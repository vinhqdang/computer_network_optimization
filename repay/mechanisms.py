"""Allocation mechanisms: the REPAY family and the baselines (PF, WFQ, Priority, Credit).

Every mechanism exposes allocate(view) -> rates (one per active device, view order) and reset().
"""
from dataclasses import dataclass

import numpy as np

from .params import Params
from .solver import group_offer, solve_pf, solve_slot


@dataclass
class View:
    """Per-slot observation handed to a mechanism (arrays in device order)."""

    t: int
    C: float
    ids: np.ndarray
    tier: np.ndarray
    decl: np.ndarray
    cap: np.ndarray
    arr: np.ndarray


def _arrays(view):
    """Cast a view's arrays to canonical dtypes."""
    return (np.asarray(view.ids, np.int64), np.asarray(view.tier, np.int64),
            np.asarray(view.decl, np.int64), np.asarray(view.cap, float),
            np.asarray(view.arr, np.int64))


def _rmax_of(p: Params, decl):
    """Per-device RT maximum rate from declared class (0 for elastic)."""
    decl = np.asarray(decl)
    return np.where(decl == 1, p.rmax_V, np.where(decl == 2, p.r_G, 0.0))


class Repay:
    """REPAY: per-slot exact optimisation with class-envy deficits and tier queues.

    Options: entrant (REPAY-E entrant offer for empty groups), recycle (REPAY-WC slack recycling),
    debt_price (use pi, zeta), deficits (use the bonus D_i), beta_override (callable t -> 3 tier prices,
    indexed F, P, Y, used instead of the queues).
    """

    def __init__(self, params: Params, entrant=False, recycle=False, debt_price=True,
                 deficits=True, beta_override=None):
        self.p = params
        self.entrant = entrant
        self.recycle = recycle
        self.debt_price = debt_price
        self.deficits = deficits
        self.beta_override = beta_override
        self.reset()

    def reset(self):
        """Clear all state (queues, deficits, incumbents)."""
        self.Q = np.zeros(3)  # order [PS, YS, FF]
        self.D = {}
        self.prev_decl = {}
        self.incumbents = set()
        self.last = {}

    def bound(self, g, k):
        """Deficit bound B_{g,k}."""
        return self.p.B(g, k)

    def _sync(self, ids, decl):
        """Drop state of absent devices and handle declared-class changes."""
        present = set(ids.tolist())
        for i in [i for i in self.D if i not in present]:
            del self.D[i]
        for i in [i for i in self.prev_decl if i not in present]:
            del self.prev_decl[i]
        self.incumbents &= present
        for i, dk in zip(ids.tolist(), decl.tolist()):
            if dk == 0:
                if i not in self.D or self.prev_decl.get(i) != 0:
                    self.D[i] = np.zeros(2)
            else:
                self.D.pop(i, None)
            self.prev_decl[i] = dk

    def _beta_tier(self, view):
        """Tier prices indexed by tier (F, P, Y)."""
        p = self.p
        if self.beta_override is not None:
            return np.asarray(self.beta_override(view.t), float).reshape(3)
        return np.array([self.Q[2], self.Q[0], self.Q[1] + p.V * p.varpi * p.price])

    def allocate(self, view):
        """Allocate rates for one slot and update the state."""
        p, w = self.p, self.p.w_arr
        ids, tier, decl, cap, arr = _arrays(view)
        n, C = ids.size, float(view.C)
        self._sync(ids, decl)
        el = np.flatnonzero(decl == 0)
        rt = np.flatnonzero(decl > 0)
        ne = el.size
        d, tel = cap[el], tier[el]

        Dm = np.array([self.D[i] for i in ids[el].tolist()], float).reshape(ne, 2)
        s_mat = np.zeros((ne, 2))
        sig_mat = np.zeros((ne, 2))
        for kk, k in enumerate((1, 2)):
            lo, hi = p.rmin(k), p.rmax(k)
            s = np.where(d >= hi, 1.0, np.where(d <= lo, 0.0, (d - lo) / max(hi - lo, 1e-300)))
            sig = np.where(d >= hi, 0.0, np.where(d <= lo, d, (1.0 - s) * d))
            s_mat[:, kk], sig_mat[:, kk] = s, sig
        bonus = Dm.sum(1)

        beta_t = self._beta_tier(view)
        pi_gk = np.zeros((3, 2))
        ze_gk = np.zeros((3, 2))
        if self.debt_price and ne:
            for kk in range(2):
                pi_gk[:, kk] = np.bincount(tel, weights=Dm[:, kk] * s_mat[:, kk], minlength=3)
                ze_gk[:, kk] = np.bincount(tel, weights=Dm[:, kk] * sig_mat[:, kk], minlength=3)

        groups = []
        for g in range(3):
            for k in (1, 2):
                mem = rt[(tier[rt] == g) & (decl[rt] == k)]
                if mem.size:
                    groups.append((g, k, mem))
        gg = np.array([g for g, _, _ in groups], dtype=np.int64)
        gk = np.array([k for _, k, _ in groups], dtype=np.int64)
        gn = np.array([m.size for _, _, m in groups], dtype=float)
        gw = w[gg] if groups else np.zeros(0)
        gb = beta_t[gg] if groups else np.zeros(0)
        gpi = pi_gk[gg, gk - 1] if groups else np.zeros(0)
        gze = ze_gk[gg, gk - 1] if groups else np.zeros(0)

        res = solve_slot(C, p.V, w[tel], d, bonus, beta_t[tel], gk, gn, gw, gb, gpi, gze, p)
        x, a, z, lam = res["x"], res["a"].copy(), res["z"].copy(), res["lam"]

        if self.recycle and lam == 0.0 and groups:
            spare = C - (float(np.sum(gn * a * z)) + float(x.sum()))
            for j in np.argsort(-gw, kind="stable"):
                if spare <= 1e-12:
                    break
                nj, rmn, rmx = gn[j], p.rmin(gk[j]), p.rmax(gk[j])
                cur = nj * a[j] * z[j]
                extra = min(spare, nj * rmx - cur)
                spare -= extra
                Y = cur + extra
                if Y >= nj * rmn - 1e-12:
                    a[j], z[j] = 1.0, min(rmx, Y / nj)
                else:
                    a[j], z[j] = Y / (nj * rmn), rmn

        # Fluid references for deficits (per elastic device and class of its own tier).
        fref = np.zeros((n, 2))
        if ne:
            lookup = {(g, k): j for j, (g, k, _) in enumerate(groups)}
            ref = np.zeros((ne, 2))
            for g in range(3):
                mg = tel == g
                if not mg.any():
                    continue
                for kk, k in enumerate((1, 2)):
                    j = lookup.get((g, k))
                    if j is not None:
                        ref[mg, kk] = a[j] * np.minimum(z[j], d[mg])
                    elif self.entrant:
                        ae, ze, _ = group_offer(lam, 1.0, p.V * w[g], beta_t[g],
                                                pi_gk[g, kk], ze_gk[g, kk], k, p)
                        ref[mg, kk] = float(ae) * np.minimum(float(ze), d[mg])
            fref[el] = ref

        # Rounding to whole flows: incumbents first, then earlier arrival.
        rate = np.zeros(n)
        pool = 0.0
        inc = np.isin(ids, np.fromiter(self.incumbents, np.int64, len(self.incumbents)))
        for j, (g, k, mem) in enumerate(groups):
            na = gn[j] * a[j]
            order = mem[np.lexsort((ids[mem], arr[mem], ~inc[mem]))]
            M = min(int(np.floor(na + 1e-9)), order.size)
            rate[order[:M]] = z[j]
            frac = na - M
            if M < order.size and frac > 1e-9:
                Lr = frac * z[j]
                if Lr >= p.rmin(k) - 1e-12:
                    rate[order[M]] = Lr
                else:
                    pool += Lr

        xf = x.copy()
        if pool > 1e-12 and ne:
            room = d - x
            mv = p.V * w[tel] / (1.0 + x) + beta_t[tel] + bonus
            order = np.argsort(-mv, kind="stable")
            rs = room[order]
            cum = np.cumsum(rs) - rs
            xf[order] += np.clip(pool - cum, 0.0, rs)
        rate[el] = xf

        if self.deficits and ne:
            Dn = np.maximum(Dm + fref[el] - xf[:, None], 0.0)
            for e, i in enumerate(ids[el].tolist()):
                self.D[i] = Dn[e].copy()

        self.incumbents = set(ids[rt][rate[rt] > 1e-12].tolist())

        rho = np.bincount(tier, weights=rate, minlength=3)
        dem_dev = np.where(decl == 0, cap, _rmax_of(p, decl))
        dem = np.bincount(tier, weights=dem_dev, minlength=3)
        eps = np.array([p.theta_P * dem[1] - rho[1],
                        p.theta_Y * dem[2] - rho[2],
                        min(p.phi * C, dem[0]) - rho[0]])
        self.Q = np.maximum(self.Q + eps, 0.0)

        Dmat = np.zeros((n, 2))
        if ne:
            Dmat[el] = np.array([self.D[i] for i in ids[el].tolist()], float).reshape(ne, 2)
        self.last = dict(
            lam=lam,
            a={(g, k): float(a[j]) for j, (g, k, _) in enumerate(groups)},
            z={(g, k): float(z[j]) for j, (g, k, _) in enumerate(groups)},
            fluid_ref=fref,
            D_max=float(Dmat.max()) if n else 0.0,
            D=self.D,
            Dmat=Dmat,
        )
        return rate


class PlainDPP(Repay):
    """Plain drift-plus-penalty: REPAY with no deficits and no debt prices."""

    def __init__(self, params: Params, **kw):
        kw.setdefault("entrant", False)
        super().__init__(params, deficits=False, debt_price=False, **kw)


class PF:
    """Class-blind weighted proportional fairness (RT caps at rmax_k)."""

    rt_mult = 1.0

    def __init__(self, params: Params):
        self.p = params

    def reset(self):
        """Stateless."""

    def allocate(self, view):
        """Weighted PF water-filling over all active devices."""
        ids, tier, decl, cap, arr = _arrays(view)
        w = self.p.w_arr[tier] * np.where(decl > 0, self.rt_mult, 1.0)
        capv = np.where(decl == 0, cap, _rmax_of(self.p, decl))
        return solve_pf(view.C, w, capv)


class WFQ(PF):
    """PF with RT weights multiplied by rt_mult (default 4)."""

    def __init__(self, params: Params, rt_mult=4.0):
        super().__init__(params)
        self.rt_mult = rt_mult


class Priority:
    """Strict priority for declared-RT flows (P, Y, F; gaming before video), then weighted PF."""

    def __init__(self, params: Params):
        self.p = params

    def reset(self):
        """Stateless."""

    def allocate(self, view):
        """Admit RT flows at rmax while capacity lasts; remaining capacity to elastic."""
        p = self.p
        ids, tier, decl, cap, arr = _arrays(view)
        n = ids.size
        rate = np.zeros(n)
        rt = np.flatnonzero(decl > 0)
        tier_rank = np.array([2, 0, 1])[tier]
        dec_rank = np.where(decl == 2, 0, 1)
        order = rt[np.lexsort((ids[rt], arr[rt], dec_rank[rt], tier_rank[rt]))]
        left = float(view.C)
        for j in order:
            rn, rx = p.rmin(decl[j]), p.rmax(decl[j])
            if left >= rx - 1e-12:
                rate[j] = rx
                left = max(left - rx, 0.0)
            elif rx > rn and left >= rn - 1e-12:
                rate[j] = left
                left = 0.0
        el = np.flatnonzero(decl == 0)
        if el.size:
            rate[el] = solve_pf(left, p.w_arr[tier[el]], cap[el])
        return rate


class Credit:
    """Karma-style class-blind credit mechanism."""

    def __init__(self, params: Params):
        self.p = params
        self.reset()

    def reset(self):
        """Clear credit balances."""
        self.credit = {}

    def allocate(self, view):
        """Fair shares, then unused capacity to borrowers in decreasing credit order."""
        p = self.p
        ids, tier, decl, cap, arr = _arrays(view)
        n, C = ids.size, float(view.C)
        present = set(ids.tolist())
        for i in [i for i in self.credit if i not in present]:
            del self.credit[i]
        if n == 0:
            return np.zeros(0)
        c = np.array([self.credit.get(i, 0.0) for i in ids.tolist()], float)
        w = p.w_arr[tier]
        f = C * w / w.sum()
        demand = np.where(decl == 0, cap, _rmax_of(p, decl))
        x = np.minimum(demand, f)
        unused = max(C - float(x.sum()), 0.0)
        room = demand - x
        order = np.lexsort((ids, arr, -c))
        rs = room[order]
        cum = np.cumsum(rs) - rs
        x[order] += np.clip(unused - cum, 0.0, rs)
        self.credit = dict(zip(ids.tolist(), (c + f - x).tolist()))
        return x
