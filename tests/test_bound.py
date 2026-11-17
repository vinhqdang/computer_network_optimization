"""Theorem 1: deficits stay below B_{g,k} for every capacity, population, demand and tier price path."""
import numpy as np
import pytest

from repay.mechanisms import Repay, View
from repay.params import Params

CAPS = [0.2, 1.0, 3.0, 10.0, 60.0]
DEMANDS = [0.0, 0.1, 0.4, 1.0, 5.0, 30.0]
VARIANTS = {
    "default": dict(),
    "entrant": dict(entrant=True),
    "recycle": dict(recycle=True),
    "no_debt_price": dict(debt_price=False),
}


class _Churn:
    """Random population with heavy churn, changing declarations and demand caps."""

    def __init__(self, rng):
        self.rng = rng
        self.devices = {}  # id -> dict(tier, arr)
        self.next_id = 0
        self.C = 1.0

    def step(self, t):
        rng = self.rng
        for i in [i for i in self.devices if rng.random() < 0.15]:
            del self.devices[i]
        for _ in range(int(rng.poisson(4.0))):
            self.devices[self.next_id] = dict(tier=int(rng.integers(3)), arr=t)
            self.next_id += 1
        if rng.random() < 0.5:
            self.C = float(rng.choice(CAPS))
        ids = np.array(sorted(self.devices), dtype=np.int64)
        tier = np.array([self.devices[i]["tier"] for i in ids], dtype=np.int64)
        arr = np.array([self.devices[i]["arr"] for i in ids], dtype=np.int64)
        decl = rng.choice(3, size=ids.size, p=[0.5, 0.25, 0.25]).astype(np.int64)
        cap = rng.choice(DEMANDS, size=ids.size).astype(float)
        return View(t=t, C=self.C, ids=ids, tier=tier, decl=decl, cap=cap, arr=arr)


def _check_slot(mech, view, rates, p, tier_of):
    """Capacity, nonnegativity, elastic caps and the deficit bound after one slot."""
    assert np.all(rates >= -1e-12)
    assert rates.sum() <= view.C + 1e-9, (view.t, rates.sum(), view.C)
    el = view.decl == 0
    assert np.all(rates[el] <= view.cap[el] + 1e-9)
    for i, dvec in mech.D.items():
        g = tier_of[i]
        for kk, k in enumerate((1, 2)):
            assert dvec[kk] <= p.B(g, k) + 1e-6, (view.t, i, g, k, dvec[kk], p.B(g, k))


@pytest.mark.parametrize("variant", sorted(VARIANTS))
@pytest.mark.parametrize("V", [1.0, 20.0, 100.0])
def test_deficit_bound_under_adversarial_prices(variant, V):
    """1500 slots of churn with random tier prices in [-40, 40]: D <= B after every slot."""
    p = Params(V=V)
    rng = np.random.default_rng(int(V) * 7 + len(variant))
    churn = _Churn(rng)
    price_rng = np.random.default_rng(99 + int(V))

    def override(t):
        return price_rng.uniform(-40.0, 40.0, size=3)

    mech = Repay(p, beta_override=override, **VARIANTS[variant])
    for t in range(1500):
        view = churn.step(t)
        tier_of = {int(i): int(g) for i, g in zip(view.ids, view.tier)}
        rates = mech.allocate(view)
        _check_slot(mech, view, rates, p, tier_of)


@pytest.mark.parametrize("V", [1.0, 20.0, 100.0])
def test_deficit_bound_with_real_queues(V):
    """Same churn with the real tier queues (no override) for the default variant."""
    p = Params(V=V)
    rng = np.random.default_rng(4242 + int(V))
    churn = _Churn(rng)
    mech = Repay(p)
    for t in range(1500):
        view = churn.step(t)
        tier_of = {int(i): int(g) for i, g in zip(view.ids, view.tier)}
        rates = mech.allocate(view)
        _check_slot(mech, view, rates, p, tier_of)
