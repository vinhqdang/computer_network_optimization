"""E8: runtime of the exact bisection solver versus cvxpy/CLARABEL on random single-slot instances.

Instances: N devices, 65% elastic (demand caps U[5,30], tiers uniform, random deficits D_{i,k} in
[0,20] per RT class, pi and zeta built from them with the affine-majorant coefficients), 35% RT
devices spread uniformly over the six (tier, class) cells, beta_g in U[0,5], C = N, V = 20.
The bisection solver is timed on 30 instances per N (median, perf_counter). For N <= 300 the
cvxpy formulation of tests/test_solver.py is solved on the first 5 instances per N (one fresh
prob.solve() call each; median reported) and the relative objective gap is computed.
Timings run serially (procs=1) so that workers do not compete for cores.
Writes results/runtime.json.
Run from the repository root: python -m experiments.exp_runtime
"""
import time

import cvxpy as cp
import numpy as np

from experiments.common import pmap, save
from repay.params import Params
from repay.solver import solve_slot

NS = [10, 30, 100, 300, 1000, 3000]
N_TIME = 30
N_CVX = 5
CVX_MAX_N = 300
V = 20.0


def make_instance(N, seed, p):
    """Random single-slot instance with N devices (see module docstring)."""
    rng = np.random.default_rng(1000 * N + seed)
    w = p.w_arr
    ne = int(round(0.65 * N))
    nrt = N - ne
    tier_e = rng.integers(0, 3, ne)
    el_w = w[tier_e]
    d = rng.uniform(5.0, 30.0, ne)
    Dmat = rng.uniform(0.0, 20.0, (ne, 2))  # deficits per RT class (video, gaming)
    s = np.zeros((ne, 2))
    sig = np.zeros((ne, 2))
    for kk, k in enumerate((1, 2)):
        lo, hi = p.rmin(k), p.rmax(k)
        s[:, kk] = np.where(d >= hi, 1.0, np.where(d <= lo, 0.0, (d - lo) / max(hi - lo, 1e-300)))
        sig[:, kk] = np.where(d >= hi, 0.0, np.where(d <= lo, d, (1.0 - s[:, kk]) * d))
    bonus = Dmat.sum(1)
    beta_t = rng.uniform(0.0, 5.0, 3)
    el_beta = beta_t[tier_e]
    pi = np.zeros((3, 2))
    zeta = np.zeros((3, 2))
    for kk in range(2):
        pi[:, kk] = np.bincount(tier_e, weights=Dmat[:, kk] * s[:, kk], minlength=3)
        zeta[:, kk] = np.bincount(tier_e, weights=Dmat[:, kk] * sig[:, kk], minlength=3)
    cell = rng.integers(0, 6, nrt)
    grp_g, grp_k, grp_n = [], [], []
    for c in range(6):
        cnt = int(np.count_nonzero(cell == c))
        if cnt:
            grp_g.append(c // 2)
            grp_k.append(c % 2 + 1)
            grp_n.append(float(cnt))
    grp_g = np.array(grp_g, int)
    grp_k = np.array(grp_k, int)
    grp_n = np.array(grp_n, float)
    grp_w = w[grp_g]
    grp_beta = beta_t[grp_g]
    grp_pi = np.array([pi[g, k - 1] for g, k in zip(grp_g, grp_k)], float)
    grp_zeta = np.array([zeta[g, k - 1] for g, k in zip(grp_g, grp_k)], float)
    return dict(C=float(N), V=V, el_w=el_w, el_d=d, el_bonus=bonus, el_beta=el_beta,
                grp_k=grp_k, grp_n=grp_n, grp_w=grp_w, grp_beta=grp_beta, grp_pi=grp_pi,
                grp_zeta=grp_zeta)


def _solve(inst, p):
    return solve_slot(inst["C"], inst["V"], inst["el_w"], inst["el_d"], inst["el_bonus"],
                      inst["el_beta"], inst["grp_k"], inst["grp_n"], inst["grp_w"],
                      inst["grp_beta"], inst["grp_pi"], inst["grp_zeta"], p)


def objective_at(inst, res, p):
    """Objective of the per-slot problem at the solver's allocation (same form as tests/test_solver.py)."""
    x, a, z = res["x"], res["a"], res["z"]
    obj = 0.0
    for j in range(len(inst["grp_k"])):
        k, n = inst["grp_k"][j], inst["grp_n"][j]
        y = a[j] * z[j]
        if k == 1:
            term = n * inst["V"] * inst["grp_w"][j] * a[j] * (1.0 + np.log(z[j] / p.rmin_V)) if a[j] > 0 else 0.0
        else:
            term = n * inst["V"] * inst["grp_w"][j] * a[j]
        obj += term + (n * inst["grp_beta"][j] - inst["grp_pi"][j]) * y - inst["grp_zeta"][j] * a[j]
    obj += np.sum(inst["V"] * inst["el_w"] * np.log1p(x) + (inst["el_beta"] + inst["el_bonus"]) * x)
    return float(obj)


def cvxpy_problem(inst, p):
    """Perspective formulation of the per-slot problem (as in tests/test_solver.py)."""
    V, C = inst["V"], inst["C"]
    el_w, el_d, el_bonus, el_beta = inst["el_w"], inst["el_d"], inst["el_bonus"], inst["el_beta"]
    grp_k, grp_n, grp_w, grp_beta = inst["grp_k"], inst["grp_n"], inst["grp_w"], inst["grp_beta"]
    grp_pi, grp_zeta = inst["grp_pi"], inst["grp_zeta"]
    ne, ng = len(el_d), len(grp_k)
    x = cp.Variable(ne, nonneg=True)
    a = cp.Variable(ng, nonneg=True)
    y = cp.Variable(ng, nonneg=True)
    cons = [a <= 1, x <= el_d]
    obj_terms = []
    for j in range(ng):
        k, n = grp_k[j], grp_n[j]
        rmn, rmx = p.rmin(k), p.rmax(k)
        cons += [y[j] >= a[j] * rmn, y[j] <= a[j] * rmx]
        if k == 1:
            obj_terms.append(n * V * grp_w[j] * (a[j] - cp.rel_entr(a[j], y[j] / rmn)))
        else:
            obj_terms.append(n * V * grp_w[j] * a[j])
        obj_terms.append((n * grp_beta[j] - grp_pi[j]) * y[j] - grp_zeta[j] * a[j])
    if ne:
        obj_terms.append(cp.sum(cp.multiply(V * el_w, cp.log1p(x))) + cp.sum(cp.multiply(el_beta + el_bonus, x)))
    if ng:
        cons.append(cp.sum(cp.multiply(grp_n, y)) + (cp.sum(x) if ne else 0) <= C)
    elif ne:
        cons.append(cp.sum(x) <= C)
    return cp.Problem(cp.Maximize(sum(obj_terms)), cons), x, a, y


def cvx_objective_at_solution(inst, p, x, a, y):
    """Objective at the cvxpy primal point. prob.value can be -inf when a is ~1e-9 and y is 0 within
    solver tolerance (rel_entr(a, 0) = inf); the rate is then recovered as z = clip(y/a, rmin, rmax)."""
    rmn = np.array([p.rmin(k) for k in inst["grp_k"]], float)
    rmx = np.array([p.rmax(k) for k in inst["grp_k"]], float)
    z = np.clip(y / np.maximum(a, 1e-300), rmn, rmx)
    return objective_at(inst, dict(x=x, a=np.clip(a, 0.0, 1.0), z=z), p)


def _job(N):
    """All measurements for one N."""
    p = Params(V=V)
    bis_times, bis_obj, insts = [], [], []
    for seed in range(N_TIME):
        inst = make_instance(N, seed, p)
        t0 = time.perf_counter()
        res = _solve(inst, p)
        bis_times.append(time.perf_counter() - t0)
        if seed < N_CVX:
            bis_obj.append(objective_at(inst, res, p))
            insts.append(inst)
    out = dict(N=N, bisection_ms_median=1e3 * float(np.median(bis_times)),
               bisection_ms_all=[1e3 * t for t in bis_times], cvxpy_ms_median=None,
               cvxpy_ms_all=None, max_rel_gap=None, gap_instances=None)
    if N <= CVX_MAX_N:
        cv_times, gaps, raw_inf = [], [], 0
        for inst, ob in zip(insts, bis_obj):
            prob, xv, av, yv = cvxpy_problem(inst, p)
            t0 = time.perf_counter()
            prob.solve(solver=cp.CLARABEL)
            cv_times.append(time.perf_counter() - t0)
            if not np.isfinite(prob.value):
                raw_inf += 1
            oc = cvx_objective_at_solution(inst, p, xv.value, av.value, yv.value)
            gaps.append(abs(oc - ob) / max(1.0, abs(oc)))
        out.update(cvxpy_ms_median=1e3 * float(np.median(cv_times)), cvxpy_ms_all=[1e3 * t for t in cv_times],
                   max_rel_gap=float(max(gaps)), gap_instances=len(gaps),
                   cvxpy_raw_value_nonfinite=raw_inf)
    return out


def main():
    t0 = time.time()
    rows = pmap(_job, NS, procs=1)
    elapsed = time.time() - t0
    print(f"E8 runtime: N in {NS}, {N_TIME} bisection instances per N, cvxpy on {N_CVX} for N<={CVX_MAX_N}; "
          f"{elapsed:.0f} s wall time")
    print(f"{'N':>6s}{'bisect ms':>12s}{'cvxpy ms':>12s}{'speedup':>10s}{'max rel gap':>14s}")
    for r in rows:
        cv = "" if r["cvxpy_ms_median"] is None else f"{r['cvxpy_ms_median']:12.2f}"
        sp = "" if r["cvxpy_ms_median"] is None else f"{r['cvxpy_ms_median'] / r['bisection_ms_median']:10.1f}"
        gp = "" if r["max_rel_gap"] is None else f"{r['max_rel_gap']:14.2e}"
        print(f"{r['N']:6d}{r['bisection_ms_median']:12.3f}{cv:>12s}{sp:>10s}{gp:>14s}")
    path = save("runtime", dict(NS=NS, N_time=N_TIME, N_cvx=N_CVX, cvx_max_N=CVX_MAX_N, V=V,
                                elapsed_s=elapsed, rows=rows))
    print("wrote", path)


if __name__ == "__main__":
    main()
