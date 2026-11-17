"""Interface and behaviour tests shared by all allocation mechanisms."""
import numpy as np
import pytest

from repay.mechanisms import PF, WFQ, Credit, PlainDPP, Priority, Repay, View
from repay.params import Params

P = Params()
MECHS = {
    "repay": lambda p: Repay(p),
    "repay_entrant": lambda p: Repay(p, entrant=True),
    "repay_recycle": lambda p: Repay(p, recycle=True),
    "plain_dpp": lambda p: PlainDPP(p),
    "pf": lambda p: PF(p),
    "wfq": lambda p: WFQ(p),
    "priority": lambda p: Priority(p),
    "credit": lambda p: Credit(p),
}


def _random_view(rng, t, n_max=25):
    """Random active set with random tiers, declared classes and caps."""
    n = int(rng.integers(0, n_max + 1))
    ids = rng.permutation(1000)[:n].astype(np.int64)
    tier = rng.integers(0, 3, size=n).astype(np.int64)
    decl = rng.integers(0, 3, size=n).astype(np.int64)
    cap = rng.choice([0.0, 0.1, 0.4, 1.0, 5.0, 30.0], size=n).astype(float)
    arr = rng.integers(0, max(t, 1), size=n).astype(np.int64)
    C = float(rng.choice([0.2, 1.0, 3.0, 10.0, 60.0]))
    return View(t=t, C=C, ids=ids, tier=tier, decl=decl, cap=cap, arr=arr)


def _rt_range_ok(rates, view, p):
    """Declared-RT rates are 0 or within [rmin, rmax]."""
    rt = view.decl > 0
    rmn = np.where(view.decl == 1, p.rmin_V, p.r_G)
    rmx = np.where(view.decl == 1, p.rmax_V, p.r_G)
    r = rates[rt]
    ok = (np.abs(r) <= 1e-12) | ((r >= rmn[rt] - 1e-9) & (r <= rmx[rt] + 1e-9))
    return bool(np.all(ok))


@pytest.mark.parametrize("name", sorted(MECHS))
def test_common_invariants(name):
    """300 random slots: capacity, nonnegativity, elastic caps and RT rate ranges."""
    rng = np.random.default_rng(2024)
    mech = MECHS[name](P)
    for t in range(300):
        view = _random_view(rng, t)
        rates = np.asarray(mech.allocate(view), float)
        assert rates.shape == (view.ids.size,)
        assert np.all(rates >= -1e-12), name
        assert rates.sum() <= view.C + 1e-9, (name, t)
        el = view.decl == 0
        assert np.all(rates[el] <= view.cap[el] + 1e-9), (name, t)
        if name in ("pf", "wfq", "credit"):
            # class-blind rules give RT flows continuous rates, capped at rmax
            rt = view.decl > 0
            rmx = np.where(view.decl == 1, P.rmax_V, P.r_G)
            assert np.all(rates[rt] <= rmx[rt] + 1e-9), (name, t)
        else:
            assert _rt_range_ok(rates, view, P), (name, t)


@pytest.mark.parametrize("name", ["pf", "wfq"])
def test_pf_family_exhausts_capacity(name):
    """PF and WFQ hand out min(C, total demand) up to 1e-6."""
    rng = np.random.default_rng(55)
    mech = MECHS[name](P)
    for t in range(300):
        view = _random_view(rng, t)
        rates = mech.allocate(view)
        demand = np.where(view.decl == 0, view.cap,
                          np.where(view.decl == 1, P.rmax_V, P.r_G))
        assert abs(rates.sum() - min(view.C, demand.sum())) <= 1e-6, (name, t)


def test_priority_serves_rt_before_elastic():
    """If an RT flow is left unserved, the elastic devices get less than one rmin of capacity."""
    rng = np.random.default_rng(91)
    mech = Priority(P)
    checked = 0
    for t in range(300):
        view = _random_view(rng, t)
        rates = mech.allocate(view)
        rt = np.flatnonzero(view.decl > 0)
        unserved = [j for j in rt if rates[j] <= 1e-12]
        el = view.decl == 0
        if unserved:
            checked += 1
            assert rates[el].sum() < 0.5 + 1e-9, t
    assert checked > 0


def test_repay_is_stateful_and_reset_clears_state():
    """Deficit state is created for declared-E devices and cleared by reset()."""
    rng = np.random.default_rng(3)
    mech = Repay(P)
    view = _random_view(rng, 0, n_max=20)
    mech.allocate(view)
    assert set(mech.D) == set(view.ids[view.decl == 0].tolist())
    mech.reset()
    assert mech.D == {} and np.all(mech.Q == 0)
