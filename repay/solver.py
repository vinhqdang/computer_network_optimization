"""Exact per-slot solver (bisection on the capacity price) and weighted proportional fairness."""
import numpy as np

from .params import Params


def group_offer(lam, n, Vw, beta, pi, zeta, k, p: Params):
    """Optimal (a, z, psi) of RT groups at capacity price lam; vectorised over groups.

    z is the per-flow rate maximising the group term, a = 1{psi > 0} the admission.
    """
    k = np.asarray(k)
    rlo = np.where(k == 1, p.rmin_V, p.r_G)
    rhi = np.where(k == 1, p.rmax_V, p.r_G)
    q = n * (lam - beta) + pi
    qpos = q > 0
    z = np.where(qpos, np.clip(n * Vw / np.where(qpos, q, 1.0), rlo, rhi), rhi)
    u = np.where(k == 1, 1.0 + np.log(z / p.rmin_V), 1.0)
    psi = n * (Vw * u + (beta - lam) * z) - pi * z - zeta
    return (psi > 0).astype(float), z, psi


def solve_slot(C, V, el_w, el_d, el_bonus, el_beta, grp_k, grp_n, grp_w, grp_beta,
               grp_pi, grp_zeta, params: Params):
    """Solve the per-slot REPAY problem exactly (section 2 of the design).

    Returns dict with x (elastic rates), a and z (per group), lam (capacity price), used (load).
    """
    f = lambda v: np.asarray(v, dtype=float).ravel()
    el_w, el_d, el_bonus, el_beta = f(el_w), np.maximum(f(el_d), 0.0), f(el_bonus), f(el_beta)
    grp_k = np.asarray(grp_k, dtype=int).ravel()
    grp_n, grp_w, grp_beta, grp_pi, grp_zeta = map(f, (grp_n, grp_w, grp_beta, grp_pi, grp_zeta))
    C = float(C)
    Vw_e, Vw_g = V * el_w, V * grp_w

    def resp(lam):
        pe = lam - el_beta - el_bonus
        pos = pe > 0
        xe = np.where(pos, Vw_e / np.where(pos, pe, 1.0) - 1.0, el_d)
        xe = np.clip(xe, 0.0, el_d)
        a, z, psi = group_offer(lam, grp_n, Vw_g, grp_beta, grp_pi, grp_zeta, grp_k, params)
        load = float(np.sum(grp_n * a * z) + np.sum(xe))
        return xe, a, z, load

    x0, a0, z0, load0 = resp(0.0)
    if load0 <= C:
        return dict(x=x0, a=a0, z=z0, lam=0.0, used=load0)

    lo, hi = 0.0, 1.0
    for _ in range(200):
        if resp(hi)[3] <= C:
            break
        lo, hi = hi, 2.0 * hi
    for _ in range(80):
        if hi - lo <= 1e-10 * max(1.0, hi):
            break
        mid = 0.5 * (lo + hi)
        if resp(mid)[3] > C:
            lo = mid
        else:
            hi = mid

    xh, ah, zh, Sh = resp(hi)
    _, al, _, _ = resp(lo)
    marg = (al > 0.5) & (ah < 0.5)  # on at lo, off at hi: fractional admission

    contrib = np.where(marg, grp_n * zh, 0.0)
    before = np.cumsum(contrib) - contrib
    resid = C - Sh
    frac = np.clip((resid - before) / np.where(contrib > 0, contrib, 1.0), 0.0, 1.0)
    a_out = np.where(marg, frac, ah)
    leftover = resid - float(np.sum(contrib * frac))

    xf = xh.copy()
    if leftover > 1e-12 and el_d.size:
        room = el_d - xh
        mv = Vw_e / (1.0 + xh) + el_beta + el_bonus
        order = np.argsort(-mv, kind="stable")
        rs = room[order]
        cum = np.cumsum(rs) - rs
        xf[order] += np.clip(leftover - cum, 0.0, rs)

    used = float(np.sum(grp_n * a_out * zh) + np.sum(xf))
    return dict(x=xf, a=a_out, z=zh, lam=hi, used=used)


def solve_pf(C, w, cap):
    """Maximise sum w_i log(1+x_i) s.t. 0 <= x <= cap, sum x <= C (water-filling)."""
    w = np.asarray(w, dtype=float).ravel()
    cap = np.maximum(np.asarray(cap, dtype=float).ravel(), 0.0)
    if w.size == 0:
        return np.zeros(0)
    if cap.sum() <= C:
        return cap.copy()
    C = float(C)
    if C <= 0.0:
        return np.zeros_like(cap)

    def S(mu):
        return np.clip(w / mu - 1.0, 0.0, cap).sum()

    hi = float(w.max())
    lo = hi
    for _ in range(200):
        if S(lo) > C:
            break
        lo *= 0.5
    for _ in range(200):
        if hi - lo <= 1e-13 * hi:
            break
        mid = 0.5 * (lo + hi)
        if S(mid) > C:
            lo = mid
        else:
            hi = mid
    return np.clip(w / hi - 1.0, 0.0, cap)
