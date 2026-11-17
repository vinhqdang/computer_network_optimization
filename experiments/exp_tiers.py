"""E4: running tier constraints (premium, PAYG, free floor) over time, and a theta_P sweep.

repay.sim.run does not expose per-tier rates or committed demands, so this script runs its own slot
loop that builds the View exactly as repay.sim.run does (truthful declarations) and accumulates
the tier quantities. A cross-check against run() is made for one configuration.
Writes results/tiers.json.
Run from the repository root: python -m experiments.exp_tiers
"""
import time

import numpy as np

from experiments.common import mean_ci, pmap, save
from repay.mechanisms import PF, PlainDPP, Repay, View
from repay.params import Params
from repay.sim import _rmax_of_decl, make_trace, run

T_SERIES = 12000
T_SWEEP = 6000
SEEDS = range(3)
EVERY = 100
SERIES_CONFIGS = [("repay", 5), ("repay", 20), ("repay", 100), ("pf", 20), ("dpp", 20)]
THETA_P_VALUES = [0.6, 0.8, 1.0, 1.2]


def _mech(name, p):
    if name == "repay":
        return Repay(p)
    if name == "dpp":
        return PlainDPP(p)
    if name == "pf":
        return PF(p)
    raise ValueError(name)


def tier_loop(trace, mech, p, every=EVERY):
    """Slot loop (as in repay.sim.run, truthful declarations) with cumulative tier ratios.

    Returns the sampled cumulative ratios (premium, PAYG, free floor) every `every` slots and the
    final values, plus the final cumulative sums.
    """
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

    rho_c = np.zeros(3)
    com_c = np.zeros(3)
    floor_c = 0.0
    samples = dict(t=[], premium=[], payg=[], free=[])
    mech.reset()
    for t in range(T):
        act = np.flatnonzero((t_arr <= t) & (t < tend))
        if act.size:
            pos = off[act] + (t - t_arr[act])
            on = ON[pos].astype(float)
            decl = DECL[pos]
            cap = ell[act] * on
        else:
            decl = np.zeros(0, np.int64)
            cap = np.zeros(0)
        C_t = float(Cs[t])
        view = View(t=t, C=C_t, ids=ids[act], tier=tier[act], decl=decl, cap=cap, arr=t_arr[act])
        rate = np.asarray(mech.allocate(view), float).reshape(act.size)
        tr = tier[act]
        dem_dev = np.where(decl == 0, cap, _rmax_of_decl(p, decl))
        rho = np.bincount(tr, weights=rate, minlength=3)
        dem = np.bincount(tr, weights=dem_dev, minlength=3)
        com = np.bincount(tr, weights=p.committed(tr, dem_dev), minlength=3)
        rho_c += rho
        com_c += com
        floor_c += min(p.phi * C_t, dem[0])
        if (t + 1) % every == 0:
            samples["t"].append(t + 1)
            samples["premium"].append(float(rho_c[1] / com_c[1]) if com_c[1] > 0 else float("nan"))
            samples["payg"].append(float(rho_c[2] / com_c[2]) if com_c[2] > 0 else float("nan"))
            samples["free"].append(float(rho_c[0] / floor_c) if floor_c > 0 else float("nan"))
    final = dict(premium=samples["premium"][-1], payg=samples["payg"][-1], free=samples["free"][-1])
    return dict(samples=samples, final=final)


def _series_job(job):
    """One seed of a series configuration (REPAY with its V, PF or plain DPP at V=20)."""
    name, V, seed = job
    p = Params(V=float(V))
    trace = make_trace("hotspot", T_SERIES, seed)
    out = tier_loop(trace, _mech(name, p), p)
    res = dict(name=name, V=V, seed=seed, **out)
    if name == "repay" and V == 20 and seed == 0:
        # cross-check: the loop's final ratios must agree with repay.sim.run on the same trace
        r = run(make_trace("hotspot", T_SERIES, seed), Repay(p), p)
        res["check_run"] = dict(premium=r["served_ratio"]["P"], payg=r["served_ratio"]["Y"],
                                free=r["free_floor_ratio"])
    return res


def _sweep_job(job):
    """One (theta_P, seed) run of REPAY with V=20 on T=6000 slots, final values from run()."""
    th, seed = job
    p = Params(V=20.0, theta_P=float(th))
    r = run(make_trace("hotspot", T_SWEEP, seed), Repay(p), p)
    return dict(theta_P=th, seed=seed, premium=r["served_ratio"]["P"], payg=r["served_ratio"]["Y"],
                free=r["free_floor_ratio"], util_rate=r["util_rate"],
                rt_success_all=r["rt_success"]["all"], D_over_B_max=r["D_over_B_max"])


def main():
    t0 = time.time()
    series_runs = pmap(_series_job, [(n, V, s) for n, V in SERIES_CONFIGS for s in SEEDS])
    sweep_runs = pmap(_sweep_job, [(th, s) for th in THETA_P_VALUES for s in SEEDS])
    elapsed = time.time() - t0

    print(f"E4 tiers: {len(series_runs)} series runs (T={T_SERIES}), "
          f"{len(sweep_runs)} sweep runs (T={T_SWEEP}), {elapsed:.0f} s wall time")
    print("targets: theta_P = 0.8, theta_Y = 0.6, free floor = 1.0")
    print(f"{'config':16s}{'premium':>9s}{'payg':>9s}{'free':>9s}")
    for n, V in SERIES_CONFIGS:
        rs = [r for r in series_runs if r["name"] == n and r["V"] == V]
        vals = {k: [r["final"][k] for r in rs] for k in ("premium", "payg", "free")}
        label = f"{n} V={V}"
        print(f"{label:16s}" + "".join(f"{mean_ci(vals[k])[0]:9.3f}" for k in ("premium", "payg", "free")))
    chk = [r for r in series_runs if "check_run" in r][0]
    print(f"cross-check (REPAY V=20, seed 0): loop premium {chk['final']['premium']:.6f} vs run "
          f"{chk['check_run']['premium']:.6f}; payg {chk['final']['payg']:.6f} vs "
          f"{chk['check_run']['payg']:.6f}; free {chk['final']['free']:.6f} vs "
          f"{chk['check_run']['free']:.6f}")

    print(f"\ntheta_P sweep (REPAY V=20, T={T_SWEEP}, mean over seeds)")
    print(f"{'theta_P':>8s}{'premium':>9s}{'payg':>9s}{'free':>9s}{'util':>8s}{'RT%':>7s}{'D/B':>8s}")
    for th in THETA_P_VALUES:
        rs = [r for r in sweep_runs if r["theta_P"] == th]
        print(f"{th:8.2f}" + "".join(f"{np.nanmean([r[k] for r in rs]):9.3f}" for k in ("premium", "payg", "free"))
              + f"{np.mean([r['util_rate'] for r in rs]):8.2f}"
              + f"{100 * np.mean([r['rt_success_all'] for r in rs]):7.1f}"
              + f"{np.max([r['D_over_B_max'] for r in rs]):8.3f}")

    path = save("tiers", dict(T_series=T_SERIES, T_sweep=T_SWEEP, seeds=list(SEEDS), every=EVERY,
                              targets=dict(theta_P=0.8, theta_Y=0.6, free=1.0), elapsed_s=elapsed,
                              series_runs=series_runs, sweep_runs=sweep_runs))
    print("wrote", path)


if __name__ == "__main__":
    main()
