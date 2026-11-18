"""Five additional baselines specified in research/04_additional_baselines.md.

FQ (flow-queueing max-min fairness), JS (Jaramillo-Srikant elastic/inelastic scheduler),
LendRecoup (credit-fair mechanism of Zahedi and Freeman), Potential (p-potential rule of
Kahana, Segal-Halevi and Hazon) and DMMF (dynamic max-min fairness of Fikioris, Banerjee and
Tardos). Each class follows the conventions of repay/mechanisms.py: __init__(params, ...),
reset(), and allocate(view) returning one rate (Mbit/s) per active device in view order.
"""
import numpy as np

from .mechanisms import _arrays, _rmax_of, _waterfill
from .params import Params

FEAS_TOL = 1e-12     # feasibility tolerance for comparisons (as in Priority)
BISECT_REL = 1e-12   # relative tolerance of every bisection (the spec asks for 1e-10; tighter here)
BISECT_MAX = 200     # iteration cap of every bisection


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _rmin_of(p: Params, decl):
    """Per-device RT minimum rate from declared class (0 for elastic)."""
    decl = np.asarray(decl)
    return np.where(decl == 1, p.rmin_V, np.where(decl == 2, p.r_G, 0.0))


def _demand(p: Params, decl, cap):
    """Demand D_i of research/04 Section 0: cap for declared E, r^max_k for declared RT."""
    return np.where(np.asarray(decl) == 0, np.maximum(np.asarray(cap, float), 0.0), _rmax_of(p, decl))


def _bisect_feasible(S, target, lo, hi):
    """Bisection for a nondecreasing S with S(lo) <= target < S(hi); returns the feasible end lo."""
    for _ in range(BISECT_MAX):
        if hi - lo <= BISECT_REL * max(1.0, abs(hi)):
            break
        mid = 0.5 * (lo + hi)
        if S(mid) > target:
            hi = mid
        else:
            lo = mid
    return lo


def pswc(A, w, m, l):
    """PSWC(A, w, m, l): x_i = clip(x w_i, m_i, l_i) with sum x_i = A (feasible side: sum <= A).

    Requires w > 0 and 0 <= m <= l (l may be +inf). Returns m if A <= sum(m) and l if A >= sum(l).
    """
    w = np.asarray(w, float)
    m = np.asarray(m, float)
    l = np.asarray(l, float)
    if w.size == 0:
        return np.zeros(0)
    if A <= m.sum():
        return m.copy()
    if A >= l.sum():
        return l.copy()

    def S(x):
        return np.clip(x * w, m, l).sum()

    cand = np.where(np.isfinite(l), l, np.maximum(m, A)) / w
    hi = max(float(cand.max()), 1e-12)
    for _ in range(BISECT_MAX):
        if S(hi) >= A:
            break
        hi *= 2.0
    x = _bisect_feasible(S, A, 0.0, hi)
    return np.clip(x * w, m, l)


def _trim(x, C):
    """Remove any rounding excess above C, taking it from the last-filled (largest index) positive rates."""
    excess = float(x.sum()) - C
    if excess > 0.0:
        for j in np.flatnonzero(x > 0.0)[::-1]:
            take = min(excess, float(x[j]))
            x[j] -= take
            excess -= take
            if excess <= 0.0:
                break
    return x


class _DeviceState:
    """Per-device state dicts (names in _FIELDS) with the churn rules of research/04 Section 0.

    At the start of each allocate: state of departed ids is deleted; a new id, or an id whose
    declared class differs from the previous slot, gets the arrival default from _new_device.
    """

    _FIELDS = ()

    def _init_state(self):
        for name in self._FIELDS:
            setattr(self, name, {})
        self._prev_decl = {}

    def _churn(self, ids, decl):
        ids_l, decl_l = ids.tolist(), np.asarray(decl).tolist()
        present = set(ids_l)
        for name in self._FIELDS:
            d = getattr(self, name)
            for i in [i for i in d if i not in present]:
                del d[i]
        prev = self._prev_decl
        for i in [i for i in prev if i not in present]:
            del prev[i]
        for i, dk in zip(ids_l, decl_l):
            if prev.get(i) != dk:
                for name in self._FIELDS:
                    getattr(self, name).pop(i, None)
                self._new_device(i, dk)
            prev[i] = dk

    def _new_device(self, i, dk):  # pragma: no cover - overridden
        raise NotImplementedError


# ---------------------------------------------------------------------------
# A1. Flow-queueing max-min fairness (FQ / FQ-w)
# ---------------------------------------------------------------------------

class FQ:
    """Rate-level flow queueing: water-filling of capacity over demand caps, weights phi_i.

    weighted=False gives FQ (phi = 1); weighted=True gives FQ-w (phi = tier weight). Stateless.
    """

    def __init__(self, params: Params, weighted=False):
        self.p = params
        self.weighted = bool(weighted)

    def reset(self):
        """Stateless."""

    def allocate(self, view):
        """x = min(D, phi * theta) with theta set so that sum x = min(C, sum D)."""
        ids, tier, decl, cap, arr = _arrays(view)
        n, C = ids.size, float(view.C)
        if n == 0:
            return np.zeros(0)
        D = _demand(self.p, decl, cap)
        if D.sum() <= C:
            return D.copy()
        phi = self.p.w_arr[tier] if self.weighted else np.ones(n)
        return pswc(C, phi, np.zeros(n), D)


# ---------------------------------------------------------------------------
# A2. Jaramillo-Srikant elastic/inelastic scheduling (JS / JS-w)
# ---------------------------------------------------------------------------

class JS(_DeviceState):
    """Single-link, per-slot adaptation of the Jaramillo-Srikant (2011) scheduler.

    RT devices carry a deficit counter d_i (slots owed) and video devices a top-up queue Qv_i;
    elastic devices carry a virtual queue Qe_i. kappa = 0 gives JS, kappa = 1 gives JS-w.
    The Bernoulli deficit arrivals come from a Generator seeded with `seed`; reset() reseeds it.
    """

    _FIELDS = ("deficit", "Qe", "Qv")

    def __init__(self, params: Params, q=0.9, V=20.0, kappa=0.0, deterministic=False, seed=0):
        self.p = params
        self.q = float(q)
        self.V = float(V)
        self.kappa = float(kappa)
        self.deterministic = bool(deterministic)
        self.seed = int(seed)
        self.reset()

    def reset(self):
        """Clear all queues and deficits and reseed the arrival generator."""
        self._init_state()
        self.rng = np.random.default_rng(self.seed)

    def _new_device(self, i, dk):
        if dk == 0:
            self.Qe[i] = 0.0
        else:
            self.deficit[i] = 0.0
            if dk == 1:
                self.Qv[i] = 0.0

    def allocate(self, view):
        """One JS slot: arrivals, congestion control, greedy max-weight schedule, updates."""
        p, V = self.p, self.V
        ids, tier, decl, cap, arr = _arrays(view)
        self._churn(ids, decl)
        n, C = ids.size, float(view.C)
        x = np.zeros(n)
        if n == 0:
            return x
        ids_l = ids.tolist()
        rt = decl > 0
        el = decl == 0
        vid = decl == 1
        rmn = _rmin_of(p, decl)
        w = p.w_arr[tier]
        dfc = np.array([self.deficit.get(i, 0.0) for i in ids_l], float)
        Qe = np.array([self.Qe.get(i, 0.0) for i in ids_l], float)
        Qv = np.array([self.Qv.get(i, 0.0) for i in ids_l], float)

        # 1. Deficit arrivals (Bernoulli(q) per RT device, or the fluid value q).
        a = np.zeros(n)
        n_rt = int(rt.sum())
        if n_rt:
            if self.deterministic:
                a[rt] = self.q
            else:
                a[rt] = (self.rng.random(n_rt) < self.q).astype(float)

        # 2. Elastic congestion control: x~ = argmax V w log(1+x) - Qe x on [0, d], d = cap.
        d_e = np.where(el, np.maximum(cap, 0.0), 0.0)
        Qe_pos = Qe > 0
        xt = np.where(Qe_pos,
                      np.clip(V * w / np.where(Qe_pos, Qe, 1.0) - 1.0, 0.0, d_e),
                      d_e)
        xt = np.where(el, xt, 0.0)
        sbar = np.where(el, np.minimum(d_e, Qe + xt), 0.0)

        # 3. Video top-up congestion control on [0, Delta]: argmax V w log(1+y/rmin) - Qv y.
        Delta = p.rmax_V - p.rmin_V
        Qv_pos = Qv > 0
        yt = np.where(vid,
                      np.where(Qv_pos,
                               np.clip(V * w / np.where(Qv_pos, Qv, 1.0) - p.rmin_V, 0.0, Delta),
                               Delta),
                      0.0)
        ybar = np.where(vid, np.minimum(Delta, Qv + yt), 0.0)

        # 4. Max-weight schedule: items sorted by key, greedy walk with left = C.
        rho = np.where(rt, (self.kappa * w * V + dfc) / np.where(rt, rmn, 1.0), 0.0)
        i_rt = np.flatnonzero(rt)
        i_el = np.flatnonzero(el)
        i_vi = np.flatnonzero(vid)
        dev = np.concatenate([i_rt, i_el, i_vi]).astype(np.int64)
        typ = np.concatenate([np.zeros(i_rt.size, np.int64), np.ones(i_el.size, np.int64),
                              np.full(i_vi.size, 2, np.int64)])
        key = np.concatenate([rho[i_rt], Qe[i_el], np.minimum(Qv[i_vi], rho[i_vi])])
        size = np.concatenate([rmn[i_rt], sbar[i_el], ybar[i_vi]])
        order = np.lexsort((ids[dev], arr[dev], typ, -key))
        dev_l, typ_l, size_l = dev[order].tolist(), typ[order].tolist(), size[order].tolist()
        admitted = [False] * n
        xl = [0.0] * n
        left = C
        for j, t, s in zip(dev_l, typ_l, size_l):
            if t == 0:
                if s <= left + FEAS_TOL:
                    admitted[j] = True
                    xl[j] = s
                    left = max(left - s, 0.0)
            elif t == 1:
                g = min(s, left)
                xl[j] += g
                left -= g
            elif admitted[j]:
                g = min(s, left)
                xl[j] += g
                left -= g
        x = np.array(xl, float)
        adm = np.array(admitted, bool)

        # 5. Updates (no clipping on Q is needed: service never exceeds queue plus arrivals).
        I = adm & rt & (x >= rmn - 1e-12)
        new_def = np.maximum(dfc + a - I.astype(float), 0.0)
        new_Qe = np.maximum(Qe + xt - x, 0.0)
        new_Qv = np.maximum(Qv + yt - np.maximum(x - p.rmin_V, 0.0), 0.0)
        for k, i in enumerate(ids_l):
            if rt[k]:
                self.deficit[i] = float(new_def[k])
            elif el[k]:
                self.Qe[i] = float(new_Qe[k])
            if vid[k]:
                self.Qv[i] = float(new_Qv[k])
        return x


# ---------------------------------------------------------------------------
# B1. LendRecoup (Zahedi and Freeman, 2026), adapted to time-varying capacity and churn
# ---------------------------------------------------------------------------

class LendRecoup(_DeviceState):
    """Credit-fair allocation: endowments e_i = C w_i / sum w (or C / n), credits, cumulative history.

    weighted=True gives the tier-weighted endowment (main variant); weighted=False the equal one.
    """

    _FIELDS = ("credit", "cum", "Ehat")

    def __init__(self, params: Params, weighted=True):
        self.p = params
        self.weighted = bool(weighted)
        self.reset()

    def reset(self):
        """Clear credits, cumulative allocations and cumulative endowments."""
        self._init_state()

    def _new_device(self, i, dk):
        self.credit[i] = 0.0
        self.cum[i] = 0.0
        self.Ehat[i] = 0.0

    def allocate(self, view):
        """Steps 1 to 4 of the per-slot LendRecoup rule (no-shortage, branches 3a and 3b)."""
        p = self.p
        ids, tier, decl, cap, arr = _arrays(view)
        self._churn(ids, decl)
        n, C = ids.size, float(view.C)
        if n == 0:
            return np.zeros(0)
        ids_l = ids.tolist()
        c = np.array([self.credit[i] for i in ids_l], float)
        cum = np.array([self.cum[i] for i in ids_l], float)
        Eh = np.array([self.Ehat[i] for i in ids_l], float)
        D = _demand(p, decl, cap)
        w = p.w_arr[tier] if self.weighted else np.ones(n)
        e = C * w / w.sum()
        Eh = Eh + e

        if C <= 0.0:
            x = np.zeros(n)
            at = np.zeros(n)
        elif D.sum() <= C:
            at = pswc(C, e, D, np.full(n, np.inf))   # uncapped output, used for the books
            x = D.copy()
        else:
            dbar = np.minimum(D, np.maximum(0.0, e + c))
            if dbar.sum() >= C:
                at = pswc(C, e, np.zeros(n), dbar)
            else:
                def S(y):
                    return np.clip(y * Eh - cum, dbar, D).sum()

                lo = float(np.min((dbar + cum) / Eh))
                hi = float(np.max((D + cum) / Eh))
                y = _bisect_feasible(S, C, lo, hi)
                at = np.clip(y * Eh - cum, dbar, D)
            x = np.minimum(at, D)

        c_new = c + e - at
        cum_new = cum + at
        for k, i in enumerate(ids_l):
            self.credit[i] = float(c_new[k])
            self.cum[i] = float(cum_new[k])
            self.Ehat[i] = float(Eh[k])
        return x


# ---------------------------------------------------------------------------
# B2. Perpetual potential rule (Kahana, Segal-Halevi and Hazon, 2026), usable-volume instance
# ---------------------------------------------------------------------------

_H_CACHE = {}


def _fpot(u, p):
    """Normalised potential f(u) = (1 + u^2 / (4 p^2))^p (sigma = 1)."""
    return (1.0 + u * u / (4.0 * p * p)) ** p


def _fprime(u, p):
    """Derivative of the normalised potential: (u / (2p)) (1 + u^2 / (4p^2))^(p - 1)."""
    return u / (2.0 * p) * (1.0 + u * u / (4.0 * p * p)) ** (p - 1.0)


def _inverse_fprime(p):
    """Vectorised inverse h of _fprime on y >= 0 (h(y) = 0 for y <= 0).

    A log-spaced table gives the starting point and four Newton steps refine it. Tables are cached per p.
    """
    key = round(float(p), 12)
    cached = _H_CACHE.get(key)
    if cached is not None:
        return cached
    ls = np.linspace(-30.0, 14.0, 4401)
    s_tab = np.exp(ls)
    lg = np.log(s_tab * (1.0 + s_tab * s_tab) ** (p - 1.0))

    def _h(y):
        y = np.asarray(y, float)
        out = np.zeros(y.shape)
        pos = y > 0
        if not np.any(pos):
            return out
        yp = y[pos]
        ly = np.log(yp)
        idx = np.clip(np.searchsorted(lg, ly), 1, lg.size - 1)
        frac = (ly - lg[idx - 1]) / (lg[idx] - lg[idx - 1])
        s0 = np.exp(ls[idx - 1] + frac * (ls[idx] - ls[idx - 1]))
        for _ in range(4):
            q = 1.0 + s0 * s0
            g = s0 * q ** (p - 1.0)
            dg = q ** (p - 2.0) * (1.0 + (2.0 * p - 1.0) * s0 * s0)
            s0 = np.maximum(s0 - (g - yp) / dg, 1e-300)
        out[pos] = 2.0 * p * s0
        return out

    _H_CACHE[key] = _h
    return _h


def _potential_fill_leftover(x, adm, C, rmn, D, rt, elig, L):
    """Step (c): admit unadmitted RT flows at rmin in decreasing L while they fit, then water-fill."""
    x = x.copy()
    adm = adm.copy()
    R = C - float(x.sum())
    if R > FEAS_TOL:
        cand = np.flatnonzero(elig & ~adm)
        for j in cand[np.argsort(-L[cand], kind="stable")]:
            if rmn[j] <= R + FEAS_TOL:
                x[j] = rmn[j]
                adm[j] = True
                R -= float(rmn[j])
        room = np.where(~rt | adm, np.maximum(D - x, 0.0), 0.0)
        if R > FEAS_TOL and room.sum() > 0.0:
            x = x + _waterfill(R, room)
    return x, adm


class Potential(_DeviceState):
    """Minimise sum_i f(z_i(x_i)) over the feasible rates by a Lagrangian sweep over mu.

    Per device: signed deficit delta_i and scale U_i (both zero on arrival). weighted=False is the
    paper's unweighted proportionality; polish=True adds the optional toggle local search.
    """

    _FIELDS = ("delta", "scale")

    def __init__(self, params: Params, weighted=False, polish=False):
        self.p = params
        self.weighted = bool(weighted)
        self.polish = bool(polish)
        self.reset()

    def reset(self):
        """Clear all deficits and scales."""
        self._init_state()

    def _new_device(self, i, dk):
        self.delta[i] = 0.0
        self.scale[i] = 0.0

    def allocate(self, view):
        """Per-slot potential minimisation: deficit-clearing step, mu bisection, leftover fill."""
        p = self.p
        ids, tier, decl, cap, arr = _arrays(view)
        self._churn(ids, decl)
        n, C = ids.size, float(view.C)
        if n == 0:
            return np.zeros(0)
        ids_l = ids.tolist()
        delta = np.array([self.delta[i] for i in ids_l], float)
        U = np.array([self.scale[i] for i in ids_l], float)
        rt = decl > 0
        rmn = _rmin_of(p, decl)
        rmx = _rmax_of(p, decl)
        D = _demand(p, decl, cap)
        lo = np.where(rt, rmn, 0.0)

        def val(x):
            """Usable volume v_i(x): min(x, cap) for declared E; min(x, rmax) * 1{x >= rmin} for RT."""
            return np.where(rt, np.minimum(x, rmx) * (x >= rmn - FEAS_TOL), np.minimum(x, D))

        vC = val(np.full(n, C))
        w = p.w_arr[tier] if self.weighted else np.ones(n)
        prop = vC * w / w.sum()
        U = np.maximum(U, vC)
        dl = delta + prop
        pp = max(1.0, float(np.log(2.0 * n)))
        h = _inverse_fprime(pp)
        Upos = U > 0
        Us = np.where(Upos, U, 1.0)
        elig = rt & Upos & (C >= rmn - FEAS_TOL)

        def z_of(v):
            return np.where(Upos, np.maximum(dl - v, 0.0) / Us, 0.0)

        def alloc_at(mu):
            """Allocation and RT admission at multiplier mu, with the admission gains L_i(mu)."""
            xs = dl - U * h(mu * U)
            xr = np.clip(xs, rmn, rmx)
            L = _fpot(z_of(np.zeros(n)), pp) - _fpot(z_of(xr), pp) - mu * xr
            adm = elig & (L > 0.0)
            x = np.where(rt & ~adm, 0.0, np.clip(xs, lo, D))
            return x, adm, L

        x0, adm0, L0 = alloc_at(0.0)
        if x0.sum() <= C:
            x, adm, Lref = x0, adm0, L0
        else:
            mu_lo, mu_hi = 0.0, 1.0
            for _ in range(BISECT_MAX):
                if alloc_at(mu_hi)[0].sum() <= C:
                    break
                mu_lo, mu_hi = mu_hi, 2.0 * mu_hi
            for _ in range(BISECT_MAX):
                if mu_hi - mu_lo <= 1e-10 * max(1.0, mu_hi):
                    break
                mid = 0.5 * (mu_lo + mu_hi)
                if alloc_at(mid)[0].sum() > C:
                    mu_lo = mid
                else:
                    mu_hi = mid
            x, adm, _ = alloc_at(mu_hi)
            Lref = alloc_at(mu_lo)[2]
        x, adm = _potential_fill_leftover(x, adm, C, rmn, D, rt, elig, Lref)

        if self.polish:
            x, adm = self._polish(x, adm, C, val, z_of, dl, Upos, Us, pp, rmn, D, rt, elig, Lref)

        x = _trim(x, C)
        new_delta = dl - val(x)
        for k, i in enumerate(ids_l):
            self.delta[i] = float(new_delta[k])
            self.scale[i] = float(U[k])
        return x

    @staticmethod
    def _polish(x, adm, C, val, z_of, dl, Upos, Us, pp, rmn, D, rt, elig, Lref):
        """Optional local search: toggle each eligible RT flow once, keep improving toggles."""

        def potential(xx):
            return float(_fpot(z_of(val(xx)), pp).sum())

        best = potential(x)
        for j in np.flatnonzero(elig):
            x2, adm2 = x.copy(), adm.copy()
            if adm2[j]:
                x2[j] = 0.0
                adm2[j] = False
                x2, adm2 = _potential_fill_leftover(x2, adm2, C, rmn, D, rt, elig, Lref)
            else:
                need = float(rmn[j]) - (C - float(x2.sum()))
                if need > FEAS_TOL:
                    marg = np.where(~rt & Upos & (x2 > 0), _fprime(z_of(val(x2)), pp) / Us, np.inf)
                    got = 0.0
                    for e in np.argsort(marg, kind="stable"):
                        if not np.isfinite(marg[e]) or got >= need - FEAS_TOL:
                            break
                        take = min(float(x2[e]), need - got)
                        x2[e] -= take
                        got += take
                    if got < need - FEAS_TOL:
                        continue
                x2[j] = rmn[j]
                adm2[j] = True
                room = np.where(~rt | adm2, np.maximum(D - x2, 0.0), 0.0)
                R = C - float(x2.sum())
                if R > FEAS_TOL and room.sum() > 0.0:
                    x2 = x2 + _waterfill(R, room)
            v2 = potential(x2)
            if v2 < best - 1e-12:
                x, adm, best = x2, adm2, v2
        return x, adm


# ---------------------------------------------------------------------------
# B3. Dynamic max-min fairness (Fikioris, Banerjee and Tardos, 2025), divisible limit
# ---------------------------------------------------------------------------

class DMMF(_DeviceState):
    """Water-fill so that cumulative received volume / cumulative entitlement is equalised.

    Per device: A_i (Mbit received since arrival) and Ehat_i (Mbit entitled since arrival).
    weighted=True uses tier shares; restart=True resets every device whenever the active set changes.
    """

    _FIELDS = ("A", "Ehat")

    def __init__(self, params: Params, weighted=True, restart=False):
        self.p = params
        self.weighted = bool(weighted)
        self.restart = bool(restart)
        self.reset()

    def reset(self):
        """Clear all received and entitled volumes."""
        self._init_state()
        self._prev_set = None

    def _new_device(self, i, dk):
        self.A[i] = 0.0
        self.Ehat[i] = 0.0

    def allocate(self, view):
        """Entitlement update, then water-fill x = clip(theta Ehat - A, 0, D) with sum x = C."""
        p = self.p
        ids, tier, decl, cap, arr = _arrays(view)
        ids_l = ids.tolist()
        if self.restart:
            cur = frozenset(ids_l)
            if cur != self._prev_set:
                self._init_state()
            self._prev_set = cur
        self._churn(ids, decl)
        n, C = ids.size, float(view.C)
        if n == 0:
            return np.zeros(0)
        A = np.array([self.A[i] for i in ids_l], float)
        Eh = np.array([self.Ehat[i] for i in ids_l], float)
        D = _demand(p, decl, cap)
        w = p.w_arr[tier] if self.weighted else np.ones(n)
        alpha = w / w.sum()
        Eh = Eh + alpha * C

        if C <= 0.0:
            x = np.zeros(n)
        elif D.sum() <= C:
            x = D.copy()
        else:
            pos = Eh > 0
            hi = float(np.max((D[pos] + A[pos]) / Eh[pos]))

            def S(th):
                return np.clip(th * Eh - A, 0.0, D).sum()

            th = _bisect_feasible(S, C, 0.0, hi)
            x = np.clip(th * Eh - A, 0.0, D)
        A = A + x
        for k, i in enumerate(ids_l):
            self.A[i] = float(A[k])
            self.Ehat[i] = float(Eh[k])
        return x
