"""Exogenous traces (hotspot, home scenarios) and the slot-by-slot simulator."""
import time

import numpy as np

from .mechanisms import Repay, View
from .params import Params

HOTSPOT_DEFAULTS = dict(
    arr_rate=0.25, burst_size=12, burst_period=180, mean_sojourn=240, min_sojourn=5,
    tier_p=(0.6, 0.25, 0.15), cls_p=(0.65, 0.25, 0.10), ell_lo=5.0, ell_hi=30.0,
    p_on_off=0.02, p_off_on=0.05, C_mean=150.0, C_sigma=0.15, C_cv_scale=1.0,
)
HOME_DEFAULTS = dict(
    n_devices=10, tier_p=(0.0, 1.0, 0.0), cls_p=(0.6, 0.3, 0.1), ell_lo=5.0, ell_hi=30.0,
    p_on_off=0.02, p_off_on=0.05, call_start=0.01, call_end=0.02,
    C_mean=25.0, C_sigma=0.15, C_cv_scale=1.0,
)
C_STAY = 0.97
C_MULTS = (1.0, 0.6, 0.2)


def _onoff(rng, L, p_off, p_on, start_on=True):
    """Two-state on/off chain of length L, starting in the given state."""
    u = rng.random(L)
    s = np.empty(L, dtype=bool)
    st = start_on
    for i in range(L):
        s[i] = st
        st = (u[i] >= p_off) if st else (u[i] < p_on)
    return s


def _capacity(rng, T, C_mean, C_sigma, C_cv_scale):
    """Capacity: 3-state Markov modulation times lognormal noise."""
    m = np.array([max(0.05, 1.0 + C_cv_scale * (x - 1.0)) for x in C_MULTS])
    stay = rng.random(T) < C_STAY
    states = np.empty(T, dtype=int)
    s = 0
    for t in range(T):
        states[t] = s
        if not stay[t]:
            s = [j for j in range(3) if j != s][int(rng.integers(2))]
    noise = np.exp(rng.normal(0.0, C_sigma, T))
    return C_mean * m[states] * noise


def make_trace(scenario, T, seed, **overrides):
    """Build an exogenous trace for 'hotspot' or 'home' with optional parameter overrides."""
    rng = np.random.default_rng(seed)
    if scenario == "hotspot":
        q = {**HOTSPOT_DEFAULTS, **overrides}
        C = _capacity(rng, T, q["C_mean"], q["C_sigma"], q["C_cv_scale"])
        devices = []
        pool = []
        for t in range(T):
            n_new = int(rng.poisson(q["arr_rate"]))
            if t > 0 and t % q["burst_period"] == 0:
                n_new += int(rng.poisson(q["burst_size"]))
            pool.append(n_new)
        for t in range(T):
            for _ in range(pool[t]):
                tier = int(rng.choice(3, p=q["tier_p"]))
                cls = int(rng.choice(3, p=q["cls_p"]))
                ell = float(rng.uniform(q["ell_lo"], q["ell_hi"]))
                L = max(q["min_sojourn"], int(rng.geometric(1.0 / q["mean_sojourn"])))
                if cls == 0:
                    on = _onoff(rng, L, q["p_on_off"], q["p_off_on"])
                else:
                    on = np.ones(L, dtype=bool)
                devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=t,
                                    t_dep=t + L, ell=ell, on=on))
        return dict(T=T, C=C, devices=devices, scenario=scenario)

    if scenario == "home":
        q = {**HOME_DEFAULTS, **overrides}
        C = _capacity(rng, T, q["C_mean"], q["C_sigma"], q["C_cv_scale"])
        devices = []
        for _ in range(q["n_devices"]):
            tier = int(rng.choice(3, p=q["tier_p"]))
            cls = int(rng.choice(3, p=q["cls_p"]))
            ell = float(rng.uniform(q["ell_lo"], q["ell_hi"]))
            if cls == 0:
                on = _onoff(rng, T, q["p_on_off"], q["p_off_on"])
                devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=0, t_dep=T,
                                    ell=ell, on=on))
                continue
            # RT device: each on-call session is a separate device entry.
            u = rng.random(T)
            active, start = False, 0
            for t in range(T):
                if not active and u[t] < q["call_start"]:
                    active, start = True, t
                elif active and u[t] < q["call_end"]:
                    devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=start,
                                        t_dep=t, ell=ell, on=np.ones(t - start, dtype=bool)))
                    active = False
            if active:
                devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=start,
                                    t_dep=T, ell=ell, on=np.ones(T - start, dtype=bool)))
        return dict(T=T, C=C, devices=devices, scenario=scenario)

    raise ValueError(f"unknown scenario {scenario!r}")


def _jain(y):
    """Jain fairness index of a 1-D array (NaN if empty)."""
    if y.size == 0:
        return float("nan")
    return float(y.sum() ** 2 / (y.size * np.sum(y ** 2))) if np.any(y) else 1.0


def _ratio(num, den):
    """num/den, NaN when den is zero."""
    return float(num / den) if den > 0 else float("nan")


def run(trace, mech, params: Params, declare=None, record_series=False):
    """Simulate a mechanism on a trace and return the metric dictionary."""
    p = params
    devs = trace["devices"]
    T = len(trace["C"])
    Cs = np.asarray(trace["C"], float)
    N = len(devs)
    ids = np.array([d["id"] for d in devs], np.int64)
    tier = np.array([d["tier"] for d in devs], np.int64)
    cls = np.array([d["cls"] for d in devs], np.int64)
    t_arr = np.array([d["t_arr"] for d in devs], np.int64)
    tend = np.minimum(np.array([d["t_dep"] for d in devs], np.int64), T)
    ell = np.array([d["ell"] for d in devs], float)
    Ls = np.maximum(tend - t_arr, 0)
    off = np.concatenate([[0], np.cumsum(Ls)[:-1]]).astype(np.int64) if N else np.zeros(0, np.int64)
    ON = np.concatenate([np.asarray(d["on"], bool)[:L] for d, L in zip(devs, Ls)]) if N else np.zeros(0, bool)
    DECL = np.repeat(cls, Ls)
    idx_of = {int(i): j for j, i in enumerate(ids.tolist())}
    for did, val in (declare or {}).items():
        j = idx_of[int(did)]
        seg = slice(off[j], off[j] + Ls[j])
        DECL[seg] = np.asarray(val)[: Ls[j]] if np.ndim(val) else int(val)

    rmin_true = np.where(cls == 1, p.rmin_V, p.r_G)
    rmax_true = np.where(cls == 1, p.rmax_V, p.r_G)
    util_acc = np.zeros(N)
    vol = np.zeros(N)
    rt_slots = np.zeros(N)
    rt_served = np.zeros(N)
    on_count = np.zeros(N)
    env_a = np.zeros((N, 2))
    env_max = np.zeros(N)
    first_decl = np.full(N, -1, np.int64)
    rho_sum = np.zeros(3)
    dem_sum = np.zeros(3)
    floor_sum = 0.0
    E_on_usable = 0.0
    E_on_count = 0.0
    cap_viol = 0
    DB_max = 0.0
    is_repay = isinstance(mech, Repay)
    series = {k: [] for k in ("C", "rt_rate", "el_rate", "lam", "max_deficit", "Q")} if record_series else None
    Bmat = np.array([[p.B(g, k) for k in (1, 2)] for g in range(3)])

    mech.reset()
    t0 = time.perf_counter()
    for t in range(T):
        act = np.flatnonzero((t_arr <= t) & (t < tend))
        if act.size:
            pos = off[act] + (t - t_arr[act])
            on = ON[pos].astype(float)
            decl = DECL[pos]
            cap = ell[act] * on
            first_decl[act] = np.where(first_decl[act] < 0, decl, first_decl[act])
        else:
            pos = np.zeros(0, np.int64)
            on = np.zeros(0)
            decl = np.zeros(0, np.int64)
            cap = np.zeros(0)
        C_t = float(Cs[t])
        view = View(t=t, C=C_t, ids=ids[act], tier=tier[act], decl=decl, cap=cap, arr=t_arr[act])
        rate = np.asarray(mech.allocate(view), float).reshape(act.size)
        if rate.size and rate.sum() > C_t + 1e-6:
            cap_viol += 1

        ca = cls[act]
        trueE = ca == 0
        trueRT = ~trueE
        usable = np.where(decl == 0, rate, np.minimum(rate, cap))
        usable = np.maximum(usable, 0.0)
        rmn, rmx = rmin_true[act], rmax_true[act]
        with np.errstate(divide="ignore", invalid="ignore"):
            u_rt = np.where(ca == 1, 1.0 + np.log(np.maximum(np.minimum(usable, rmx), 1e-300) / p.rmin_V), 1.0)
        served = trueRT & (usable >= rmn - 1e-9)
        util = np.where(trueE, np.log1p(usable), np.where(served, u_rt, 0.0))
        util_acc[act] += util
        vol[act] += usable
        rt_slots[act] += trueRT
        rt_served[act] += served
        on_count[act] += np.where(trueE, on, 0.0)
        E_on_usable += float(usable[trueE & (on > 0.5)].sum())
        E_on_count += float(np.count_nonzero(trueE & (on > 0.5)))

        # Served ratios and free floor (demand as in the queue definition).
        dem_dev = np.where(decl == 0, cap, _rmax_of_decl(p, decl))
        tr = tier[act]
        rho = np.bincount(tr, weights=rate, minlength=3)
        dem = np.bincount(tr, weights=dem_dev, minlength=3)
        com = np.bincount(tr, weights=p.committed(tr, dem_dev), minlength=3)
        dem[1:] = com[1:]  # premium and PAYG service levels are relative to committed demand
        rho_sum += rho
        dem_sum += dem
        floor_sum += min(p.phi * C_t, dem[0])

        # External class envy: reference rates per (tier, declared RT class).
        REF = np.zeros((3, 2))
        for g in range(3):
            for kk, k in enumerate((1, 2)):
                m = (tr == g) & (decl == k)
                if m.any():
                    REF[g, kk] = rate[m].mean()
        me = decl == 0
        if me.any():
            ae = act[me]
            c = np.minimum(REF[tr[me]], cap[me][:, None])
            env_a[ae] = np.maximum(env_a[ae] + c - usable[me][:, None], 0.0)
            env_max[ae] = np.maximum(env_max[ae], env_a[ae].max(1))

        if is_repay:
            Dmat = mech.last["Dmat"]
            if Dmat.size:
                DB_max = max(DB_max, float((Dmat / Bmat[tr]).max()))

        if record_series:
            series["C"].append(C_t)
            series["rt_rate"].append(float(rate[decl > 0].sum()))
            series["el_rate"].append(float(rate[decl == 0].sum()))
            series["lam"].append(float(mech.last["lam"]) if is_repay and mech.last else float("nan"))
            series["max_deficit"].append(float(mech.last["D_max"]) if is_repay and mech.last else float("nan"))
            series["Q"].append(np.array(mech.Q, float) if is_repay else np.full(3, np.nan))
    ms_per_slot = (time.perf_counter() - t0) / max(T, 1) * 1e3

    trueE_all = cls == 0
    trueRT_all = ~trueE_all
    tot_util = float(util_acc.sum())
    rt_all = rt_served.sum() / rt_slots.sum() if rt_slots.sum() > 0 else float("nan")
    rt_success = {"all": float(rt_all)}
    for name, k in (("V", 1), ("G", 2)):
        m = cls == k
        rt_success[name] = _ratio(rt_served[m].sum(), rt_slots[m].sum())
    for name, g in (("F", 0), ("P", 1), ("Y", 2)):
        m = trueRT_all & (tier == g)
        rt_success[name] = _ratio(rt_served[m].sum(), rt_slots[m].sum())

    jm = trueE_all & (on_count >= 20)
    if jm.any():
        y = (vol[jm] / on_count[jm]) / p.w_arr[tier[jm]]
        jain = _jain(y)
    else:
        jain = float("nan")

    served_ratio = {name: _ratio(rho_sum[g], dem_sum[g]) for name, g in (("F", 0), ("P", 1), ("Y", 2))}
    out = dict(
        util_rate=tot_util / T,
        rt_success=rt_success,
        el_rate=_ratio(E_on_usable, E_on_count),
        jain=jain,
        served_ratio=served_ratio,
        free_floor_ratio=_ratio(rho_sum[0], floor_sum),
        max_env=float(env_max.max()) if N else 0.0,
        cap_violations=int(cap_viol),
        ms_per_slot=ms_per_slot,
        dev=dict(id=ids, tier=tier, cls=cls, decl=first_decl, L=Ls, vol=vol, util=util_acc,
                 rt_slots=rt_slots, rt_served=rt_served, max_env=env_max),
    )
    if is_repay:
        out["D_over_B_max"] = DB_max
    if record_series:
        out["series"] = {k: np.asarray(v) for k, v in series.items()}
    return out


def _rmax_of_decl(p, decl):
    """RT maximum rate per declared class (0 for elastic)."""
    decl = np.asarray(decl)
    return np.where(decl == 1, p.rmax_V, np.where(decl == 2, p.r_G, 0.0))
