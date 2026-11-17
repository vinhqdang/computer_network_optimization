"""E2: optimality gap of REPAY against the stationary benchmark U* (fixed population, i.i.d. capacity).

Run as: python -m experiments.exp_optgap   (writes results/optgap.json)
"""
import math
import time

import cvxpy as cp
import numpy as np

from experiments.common import mean_ci, pmap, save
from repay.mechanisms import PF, PlainDPP, Repay, View
from repay.params import Params

T = 20000
SEEDS = (0, 1, 2)
V_GRID = (1, 2, 5, 10, 20, 50, 100)
SUPPORT_SEED = 123
N_SUPPORT = 200
MEDIANS = (30.0, 12.0, 4.0)
SIGMA = 0.2
THETA_P, PHI = 0.5, 0.15

# (tier, declared class, demand cap); tiers F=0, P=1, Y=2; classes E=0, V=1, G=2
POP = [(0, 1, 0.0), (0, 1, 0.0), (0, 0, 8.0), (0, 0, 12.0), (0, 0, 20.0),
       (1, 1, 0.0), (1, 2, 0.0), (1, 0, 10.0), (1, 0, 25.0)]
TIER = np.array([d[0] for d in POP], np.int64)
DECL = np.array([d[1] for d in POP], np.int64)
CAP = np.array([d[2] for d in POP], float)
IDS = np.arange(len(POP), dtype=np.int64)
ARR = np.zeros(len(POP), np.int64)
EL = np.flatnonzero(DECL == 0)
GROUPS = [(0, 1), (1, 1), (1, 2)]  # RT groups (tier, class) present in the population
GN = {gk: int(np.count_nonzero((TIER == gk[0]) & (DECL == gk[1]))) for gk in GROUPS}


def make_params(V):
    return Params(V=float(V), theta_P=THETA_P, phi=PHI)


def support():
    """200 capacity support points: equal mixture of three lognormals (seed 123)."""
    rng = np.random.default_rng(SUPPORT_SEED)
    comp = rng.integers(0, len(MEDIANS), N_SUPPORT)
    return np.asarray(MEDIANS)[comp] * np.exp(SIGMA * rng.standard_normal(N_SUPPORT))


def affine(d, lo, hi):
    """Affine majorant (s, sigma) of z -> min(z, d) on [lo, hi] (design section 1)."""
    if d >= hi:
        return 1.0, 0.0
    if d <= lo:
        return 0.0, float(d)
    s = (d - lo) / (hi - lo)
    return s, (1.0 - s) * d


def _tier_constants(p):
    dem = np.where(DECL == 0, CAP, np.where(DECL == 1, p.rmax_V, p.r_G))
    com = p.committed(TIER, dem)
    return float(com[TIER == 1].sum()), float(dem[TIER == 0].sum())


def benchmark(p, envy):
    """Stationary optimum U* over the 200 scenarios; envy in {'expect', 'none', 'slot'}."""
    C = support()
    S = C.size
    com_P, dem_F = _tier_constants(p)
    floor = np.minimum(p.phi * C, dem_F)
    gt = np.array([g for g, _ in GROUPS], np.int64)
    gk = [k for _, k in GROUPS]
    gn = np.array([GN[gk_] for gk_ in GROUPS], float)
    gw = p.w_arr[gt]
    grmin = np.array([p.rmin(k) for k in gk])
    grmax = np.array([p.rmax(k) for k in gk])
    ne = EL.size
    el_tier = TIER[EL]
    el_w = p.w_arr[el_tier]

    X = cp.Variable((S, ne), nonneg=True)
    A = cp.Variable((S, len(GROUPS)), nonneg=True)
    Y = cp.Variable((S, len(GROUPS)), nonneg=True)
    cons = [
        A <= 1,
        X <= np.tile(CAP[EL], (S, 1)),
        Y >= cp.multiply(A, grmin[None, :]),
        Y <= cp.multiply(A, grmax[None, :]),
        cp.sum(X, axis=1) + Y @ gn <= C,
    ]
    rho_P = Y @ (gn * (gt == 1)) + X @ (el_tier == 1).astype(float)
    rho_F = Y @ (gn * (gt == 0)) + X @ (el_tier == 0).astype(float)
    cons.append(cp.sum(rho_P) / S >= THETA_P * com_P)  # premium: mean(theta_P com_P - rho_P) <= 0
    cons.append(cp.sum(rho_F) / S >= float(floor.mean()))  # free floor in expectation

    pairs = []
    for e in range(ne):
        for j, (g, k) in enumerate(GROUPS):
            if g == el_tier[e]:
                s, sig = affine(CAP[EL[e]], p.rmin(k), p.rmax(k))
                pairs.append((e, j, s, sig))
    if envy != "none":
        for e, j, s, sig in pairs:
            expr = float(sig) * A[:, j] + float(s) * Y[:, j] - X[:, e]
            if envy == "expect":
                cons.append(cp.sum(expr) / S <= 0)
            else:
                cons.append(expr <= 0)

    total = 0
    for j, (g, k) in enumerate(GROUPS):
        if k == 1:
            total = total + float(gn[j] * gw[j]) * (A[:, j] - cp.rel_entr(A[:, j], Y[:, j] / p.rmin_V))
        else:
            total = total + float(gn[j] * gw[j]) * A[:, j]
    for e in range(ne):
        total = total + float(el_w[e]) * cp.log1p(X[:, e])
    prob = cp.Problem(cp.Maximize(cp.sum(total) / S), cons)
    prob.solve(solver=cp.CLARABEL)
    return dict(value=float(prob.value), status=str(prob.status))


def _sim(job):
    """One REPAY / Plain DPP / PF run of T slots on the fixed population (module-level for pmap)."""
    kind, V, seed = job
    p = make_params(V)
    rng = np.random.default_rng(seed)
    Cs = support()[rng.integers(0, N_SUPPORT, T)]
    com_P, dem_F = _tier_constants(p)
    Bmat = np.array([[p.B(g, k) for k in (1, 2)] for g in range(3)])
    w_el = p.w_arr[TIER[EL]]
    # envy pairs: elastic device (view position) x RT group of its own tier
    pairs = []
    for pos in EL:
        for (g, k) in GROUPS:
            if g == TIER[pos]:
                s, sig = affine(CAP[pos], p.rmin(k), p.rmax(k))
                pairs.append((int(pos), g, k, s, sig))
    mech = {"repay": Repay(p), "dpp": PlainDPP(p), "pf": PF(p)}[kind]
    mech.reset()
    acc_u = 0.0
    acc_env = np.zeros(len(pairs))
    acc_ps = acc_ff = 0.0
    db_max = 0.0
    for t in range(T):
        C_t = float(Cs[t])
        view = View(t=t, C=C_t, ids=IDS, tier=TIER, decl=DECL, cap=CAP, arr=ARR)
        rate = np.asarray(mech.allocate(view), float)
        if kind == "pf":
            u = float(np.sum(w_el * np.log1p(rate[EL])))
            for pos in np.flatnonzero(DECL > 0):
                r, w = rate[pos], p.w_arr[TIER[pos]]
                if DECL[pos] == 1:
                    if r >= p.rmin_V - 1e-9:
                        u += w * (1.0 + math.log(min(r, p.rmax_V) / p.rmin_V))
                elif r >= p.r_G - 1e-9:
                    u += w
            acc_u += u
        else:
            last = mech.last
            u = 0.0
            for (g, k), a in last["a"].items():
                z = last["z"][(g, k)]
                n = GN[(g, k)]
                uk = 1.0 + math.log(z / p.rmin_V) if k == 1 else 1.0
                u += p.w[g] * n * a * uk
            u += float(np.sum(w_el * np.log1p(rate[EL])))
            acc_u += u
            for idx, (pos, g, k, s, sig) in enumerate(pairs):
                acc_env[idx] += last["a"][(g, k)] * (sig + s * last["z"][(g, k)]) - rate[pos]
            Dm = last["Dmat"]
            if Dm.size:
                db_max = max(db_max, float((Dm / Bmat[TIER]).max()))
        rho = np.bincount(TIER, weights=rate, minlength=3)
        acc_ps += THETA_P * com_P - rho[1]
        acc_ff += min(PHI * C_t, dem_F) - rho[0]
    env_avg = acc_env / T
    kinds = np.array([k for _, _, k, _, _ in pairs])
    out = dict(kind=kind, V=float(V), seed=int(seed), avg_util=acc_u / T,
               e_PS=acc_ps / T, e_FF=acc_ff / T,
               DB_max=None if kind == "pf" else db_max)
    if pairs:
        out["envy_max_V"] = float(env_avg[kinds == 1].max()) if (kinds == 1).any() else None
        out["envy_max_G"] = float(env_avg[kinds == 2].max()) if (kinds == 2).any() else None
        out["envy_max"] = float(env_avg.max())
    return out


def _gap_stats(runs, kind, V, U):
    rs = [r for r in runs if r["kind"] == kind and r["V"] == float(V)]
    gaps = [U - r["avg_util"] for r in rs]
    util_m, util_h = mean_ci([r["avg_util"] for r in rs])
    gap_m, gap_h = mean_ci(gaps)
    return dict(V=V, util=util_m, util_ci=util_h, gap=gap_m, gap_ci=gap_h, gapV=gap_m * V,
                e_PS=mean_ci([r["e_PS"] for r in rs])[0], e_FF=mean_ci([r["e_FF"] for r in rs])[0],
                DB_max=mean_ci([r["DB_max"] for r in rs])[0] if kind != "pf" else None,
                envy_max_V=mean_ci([r["envy_max_V"] for r in rs if r.get("envy_max_V") is not None])[0]
                if kind != "pf" else None,
                envy_max_G=mean_ci([r["envy_max_G"] for r in rs if r.get("envy_max_G") is not None])[0]
                if kind != "pf" else None)


def main():
    t0 = time.time()
    pb = make_params(20.0)
    U = {}
    for envy, name in (("expect", "U_star"), ("none", "U_star_noEF"), ("slot", "U_star_slotEF")):
        t1 = time.time()
        U[name] = benchmark(pb, envy)
        print(f"{name}: {U[name]['value']:.6f} ({U[name]['status']}, {time.time() - t1:.1f}s)", flush=True)
    U_star = U["U_star"]["value"]

    jobs = [(k, V, s) for k in ("repay", "dpp") for V in V_GRID for s in SEEDS]
    jobs += [("pf", 20.0, s) for s in SEEDS]
    runs = pmap(_sim, jobs, procs=2)
    print(f"simulation runs: {len(runs)} in {time.time() - t0:.0f}s", flush=True)

    rows = {k: [_gap_stats(runs, k, V, U_star) for V in V_GRID] for k in ("repay", "dpp")}
    pf_util = mean_ci([r["avg_util"] for r in runs if r["kind"] == "pf"])
    print("\nV | avg utility | gap | gap*V | e_PS avg | e_FF avg | max D/B | envy max (V,G)")
    for kind, label in (("repay", "REPAY"), ("dpp", "Plain DPP")):
        print(f"-- {label}")
        for row in rows[kind]:
            db = "" if row["DB_max"] is None else f"{row['DB_max']:.4f}"
            print(f"{row['V']:>5} | {row['util']:.4f} +- {row['util_ci']:.4f} | {row['gap']:.4f} +- {row['gap_ci']:.4f}"
                  f" | {row['gapV']:.3f} | {row['e_PS']:+.4f} | {row['e_FF']:+.4f} | {db} | "
                  f"{row['envy_max_V']:.4f} {row['envy_max_G']:.4f}")
    print(f"-- PF (true utility, V-independent): {pf_util[0]:.4f} +- {pf_util[1]:.4f}")
    print(f"U*={U_star:.4f}  U*_noEF={U['U_star_noEF']['value']:.4f}  U*_slotEF={U['U_star_slotEF']['value']:.4f}")

    save("optgap", dict(
        params=dict(T=T, seeds=list(SEEDS), V_grid=list(V_GRID), theta_P=THETA_P, phi=PHI,
                    support_seed=SUPPORT_SEED, n_support=N_SUPPORT, medians=list(MEDIANS), sigma=SIGMA),
        population=[dict(tier=int(a), cls=int(b), cap=float(c)) for a, b, c in POP],
        U_star=U_star, U_star_noEF=U["U_star_noEF"]["value"], U_star_slotEF=U["U_star_slotEF"]["value"],
        benchmark_status={k: v["status"] for k, v in U.items()},
        pf_util=dict(mean=pf_util[0], ci=pf_util[1]),
        summary=dict(repay=rows["repay"], dpp=rows["dpp"]),
        runs=runs,
    ))
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
