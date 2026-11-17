"""Solver tests: per-slot REPAY problem and weighted PF against cvxpy."""
import numpy as np
import cvxpy as cp
import pytest

from repay.params import Params
from repay.solver import solve_pf, solve_slot

P = Params()
GROUP_CELLS = [(g, k) for g in range(3) for k in (1, 2)]


def _objective(p, V, el_w, el_d, el_bonus, el_beta, grp_k, grp_n, grp_w, grp_beta, grp_pi, grp_zeta,
               x, a, z):
    """Objective of the per-slot problem evaluated at a given allocation."""
    obj = 0.0
    for j in range(len(grp_k)):
        k, n = grp_k[j], grp_n[j]
        y = a[j] * z[j]
        if k == 1:
            term = n * V * grp_w[j] * a[j] * (1.0 + np.log(z[j] / p.rmin_V)) if a[j] > 0 else 0.0
        else:
            term = n * V * grp_w[j] * a[j]
        obj += term + (n * grp_beta[j] - grp_pi[j]) * y - grp_zeta[j] * a[j]
    obj += np.sum(V * el_w * np.log1p(x) + (el_beta + el_bonus) * x)
    return float(obj)


def _cvx_objective(p, C, V, el_w, el_d, el_bonus, el_beta, grp_k, grp_n, grp_w, grp_beta, grp_pi,
                   grp_zeta):
    """Optimal value of the per-slot problem computed by cvxpy (perspective form)."""
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
    prob = cp.Problem(cp.Maximize(sum(obj_terms)), cons)
    prob.solve(solver=cp.CLARABEL)
    return float(prob.value)


def _random_instance(rng):
    """Random per-slot instance following the test specification."""
    ne = int(rng.integers(0, 9))
    ng = int(rng.integers(0, 6))
    cells = rng.choice(len(GROUP_CELLS), size=ng, replace=False)
    grp_g = np.array([GROUP_CELLS[c][0] for c in cells], int)
    grp_k = np.array([GROUP_CELLS[c][1] for c in cells], int)
    el_tier = rng.integers(0, 3, size=ne)
    el_w = np.asarray(P.w)[el_tier]
    el_d = rng.uniform(0.0, 10.0, size=ne)
    el_d[rng.random(ne) < 0.1] = 0.0
    el_bonus = rng.uniform(0.0, 5.0, size=ne) * (rng.random(ne) < 0.7)
    beta_tier = rng.uniform(-5.0, 5.0, size=3)
    el_beta = beta_tier[el_tier]
    grp_n = rng.integers(1, 6, size=ng).astype(float)
    grp_w = np.asarray(P.w)[grp_g]
    grp_beta = beta_tier[grp_g]
    grp_pi = rng.uniform(0.0, 5.0, size=ng)
    grp_zeta = rng.uniform(0.0, 5.0, size=ng)
    V = float(rng.choice([1.0, 5.0, 20.0, 100.0]))
    C = float(rng.uniform(0.3, 60.0))
    return dict(V=V, C=C, el_w=el_w, el_d=el_d, el_bonus=el_bonus, el_beta=el_beta,
                grp_k=grp_k, grp_n=grp_n, grp_w=grp_w, grp_beta=grp_beta, grp_pi=grp_pi,
                grp_zeta=grp_zeta)


def test_slot_solver_matches_cvxpy():
    """200 random per-slot instances: solver objective equals the cvxpy optimum."""
    rng = np.random.default_rng(12345)
    for trial in range(200):
        inst = _random_instance(rng)
        res = solve_slot(inst["C"], inst["V"], inst["el_w"], inst["el_d"], inst["el_bonus"],
                         inst["el_beta"], inst["grp_k"], inst["grp_n"], inst["grp_w"],
                         inst["grp_beta"], inst["grp_pi"], inst["grp_zeta"], P)
        x, a, z = res["x"], res["a"], res["z"]
        # feasibility
        assert np.all(x >= -1e-12) and np.all(x <= inst["el_d"] + 1e-9), trial
        assert np.all((a >= -1e-12) & (a <= 1 + 1e-12)), trial
        rmn = np.array([P.rmin(k) for k in inst["grp_k"]], float)
        rmx = np.array([P.rmax(k) for k in inst["grp_k"]], float)
        assert np.all(z >= rmn - 1e-9) and np.all(z <= rmx + 1e-9), trial
        load = np.sum(inst["grp_n"] * a * z) + np.sum(x)
        assert load <= inst["C"] + 1e-9, trial

        obj_s = _objective(P, inst["V"], inst["el_w"], inst["el_d"], inst["el_bonus"],
                           inst["el_beta"], inst["grp_k"], inst["grp_n"], inst["grp_w"],
                           inst["grp_beta"], inst["grp_pi"], inst["grp_zeta"], x, a, z)
        obj_c = _cvx_objective(P, inst["C"], inst["V"], inst["el_w"], inst["el_d"], inst["el_bonus"],
                               inst["el_beta"], inst["grp_k"], inst["grp_n"], inst["grp_w"],
                               inst["grp_beta"], inst["grp_pi"], inst["grp_zeta"])
        assert abs(obj_c - obj_s) <= 1e-5 * max(1.0, abs(obj_c)), (trial, obj_c, obj_s)


def test_pf_matches_cvxpy():
    """50 random weighted-PF instances: water-filling equals the cvxpy optimum."""
    rng = np.random.default_rng(777)
    for trial in range(50):
        n = int(rng.integers(0, 12))
        w = rng.uniform(0.5, 3.0, size=n)
        cap = rng.uniform(0.0, 5.0, size=n) * (rng.random(n) < 0.9)
        C = float(rng.uniform(0.3, 40.0))
        x = solve_pf(C, w, cap)
        assert np.all(x >= -1e-12) and np.all(x <= cap + 1e-9), trial
        if n == 0:
            continue
        assert x.sum() <= C + 1e-9, trial
        obj_s = float(np.sum(w * np.log1p(x)))
        xv = cp.Variable(n, nonneg=True)
        prob = cp.Problem(cp.Maximize(cp.sum(cp.multiply(w, cp.log1p(xv)))),
                          [xv <= cap, cp.sum(xv) <= C])
        prob.solve(solver=cp.CLARABEL)
        assert abs(prob.value - obj_s) <= 1e-5 * max(1.0, abs(prob.value)), (trial, prob.value, obj_s)


def test_edge_cases():
    """No elastic devices, no groups, zero caps and negative prices are handled."""
    r = solve_slot(3.0, 20.0, [], [], [], [], [], [], [], [], [], [], P)
    assert r["x"].size == 0 and r["a"].size == 0 and r["lam"] == 0.0
    r = solve_slot(2.0, 20.0, [1.0], [0.0], [0.0], [-3.0], [1], [2], [1.0], [0.0], [0.0], [0.0], P)
    assert r["x"][0] == 0.0
    r = solve_slot(0.5, 20.0, [1.0, 2.0], [4.0, 4.0], [0.0, 0.0], [-2.0, -2.0], [], [], [], [], [], [], P)
    assert np.sum(r["x"]) <= 0.5 + 1e-9
    assert np.all(r["x"] >= 0)
