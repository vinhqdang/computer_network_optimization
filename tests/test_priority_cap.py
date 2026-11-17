"""Capped priority: capacity and RT budget invariants, and equivalence with Priority at q = 1."""
import numpy as np
import pytest

from repay.mechanisms import Priority, PriorityCap, View
from repay.params import Params

P = Params()


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


@pytest.mark.parametrize("q", [0.1, 0.3, 0.7, 1.0])
def test_capacity_never_exceeded_and_rt_total_bounded(q):
    """300 random slots: total rate <= C and declared-RT total <= q * C."""
    rng = np.random.default_rng(17)
    mech = PriorityCap(P, q=q)
    for t in range(300):
        view = _random_view(rng, t)
        rates = np.asarray(mech.allocate(view), float)
        assert np.all(rates >= -1e-12)
        assert rates.sum() <= view.C + 1e-9, (q, t)
        rt_total = rates[view.decl > 0].sum()
        assert rt_total <= q * view.C + 1e-9, (q, t)


def test_q_one_equals_priority():
    """With q = 1 the RT budget is the whole slot, so every slot matches Priority."""
    rng = np.random.default_rng(91)
    capped, plain = PriorityCap(P, q=1.0), Priority(P)
    for t in range(300):
        view = _random_view(rng, t)
        np.testing.assert_allclose(capped.allocate(view), plain.allocate(view), rtol=0, atol=1e-12)


def test_budget_binds_for_video_flows():
    """Many video flows: exactly q * C is admitted, the rest of C goes to the elastic device."""
    n_vid = 50
    view = View(t=0, C=10.0, ids=np.arange(n_vid + 1, dtype=np.int64),
                tier=np.zeros(n_vid + 1, dtype=np.int64),
                decl=np.array([1] * n_vid + [0], dtype=np.int64),
                cap=np.array([0.0] * n_vid + [30.0]),
                arr=np.zeros(n_vid + 1, dtype=np.int64))
    rates = PriorityCap(P, q=0.3).allocate(view)
    assert rates[:n_vid].sum() == pytest.approx(3.0, abs=1e-9)
    assert rates[-1] == pytest.approx(7.0, abs=1e-9)
