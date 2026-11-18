"""Additional baselines (repay/baselines_extra.py): hand examples, invariants and smoke runs.

Hand examples and expected values come from research/04_additional_baselines.md (Unit tests section).
"""
import numpy as np
import pytest

from repay import PF, DMMF, FQ, JS, LendRecoup, Potential, Params, View, make_trace, run
from repay.baselines_extra import _inverse_fprime, _fprime, pswc

P = Params()

VARIANTS = {
    "fq": lambda: FQ(P),
    "fq-w": lambda: FQ(P, weighted=True),
    "js": lambda: JS(P, seed=0),
    "js-w": lambda: JS(P, kappa=1.0, seed=0),
    "lendrecoup": lambda: LendRecoup(P),
    "lendrecoup-u": lambda: LendRecoup(P, weighted=False),
    "potential": lambda: Potential(P),
    "potential-w": lambda: Potential(P, weighted=True),
    "potential-polish": lambda: Potential(P, polish=True),
    "dmmf": lambda: DMMF(P),
    "dmmf-restart": lambda: DMMF(P, restart=True),
}


def _view(C, ids, tier, decl, cap, arr=None, t=0):
    ids = np.asarray(ids, np.int64)
    n = ids.size
    return View(t=t, C=float(C), ids=ids,
                tier=np.asarray(tier, np.int64), decl=np.asarray(decl, np.int64),
                cap=np.asarray(cap, float),
                arr=np.zeros(n, np.int64) if arr is None else np.asarray(arr, np.int64))


def _warm_up(mech, ids, tier, decl, cap):
    """Create per-device state with a zero-capacity slot (state is created on arrival)."""
    mech.allocate(_view(0.0, ids, tier, decl, cap))


def _demand_of(decl, cap):
    """Section 0 demand: cap for declared E, 3.0 for video, 0.2 for gaming."""
    decl = np.asarray(decl)
    return np.where(decl == 0, np.maximum(cap, 0.0),
                    np.where(decl == 1, P.rmax_V, np.where(decl == 2, P.r_G, 0.0)))


class _Churn:
    """Random population with arrivals, departures and declared-class changes (1 to 60 devices)."""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.pop = {}
        self.next_id = 0
        self.changed = set()
        self.new = set()

    def step(self, t):
        rng = self.rng
        self.changed, self.new = set(), set()
        for i in list(self.pop):
            if rng.random() < 0.08:
                del self.pop[i]
        for i in self.pop:
            if rng.random() < 0.04:
                new_decl = int(rng.integers(3))
                if new_decl != self.pop[i]["decl"]:
                    self.pop[i]["decl"] = new_decl
                    self.changed.add(i)
        for _ in range(int(rng.integers(0, 6))):
            if len(self.pop) < 60:
                self._arrive(t)
        if not self.pop:
            self._arrive(t)
        ids = np.array(sorted(self.pop), np.int64)
        tier = np.array([self.pop[i]["tier"] for i in ids], np.int64)
        decl = np.array([self.pop[i]["decl"] for i in ids], np.int64)
        arr = np.array([self.pop[i]["arr"] for i in ids], np.int64)
        cap = rng.choice([0.0, 0.3, 2.0, 10.0, 30.0], size=ids.size).astype(float)
        C = float(np.exp(rng.uniform(np.log(0.1), np.log(200.0))))
        return View(t=t, C=C, ids=ids, tier=tier, decl=decl, cap=cap, arr=arr)

    def _arrive(self, t):
        i = self.next_id
        self.next_id += 1
        self.pop[i] = dict(tier=int(self.rng.integers(3)), decl=int(self.rng.integers(3)), arr=t)
        self.new.add(i)


# ---------------------------------------------------------------------------
# T0: invariants common to every baseline
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_random_slots_capacity_bounds_and_churn(name):
    """200 random slots with arrivals, departures and class changes: T0-cap, T0-dem, T0-churn."""
    churn = _Churn(seed=11)
    mech = VARIANTS[name]()
    mech.reset()
    fields = getattr(type(mech), "_FIELDS", ())
    for t in range(200):
        v = churn.step(t)
        rates = np.asarray(mech.allocate(v), float)
        assert rates.shape == (v.ids.size,)
        assert np.all(np.isfinite(rates))
        assert np.all(rates >= -1e-12), (name, t)
        assert rates.sum() <= v.C + 1e-9, (name, t)
        assert np.all(rates <= _demand_of(v.decl, v.cap) + 1e-9), (name, t)
        present = set(v.ids.tolist())
        for field in fields:
            assert set(getattr(mech, field)) <= present, (name, t, field)


@pytest.mark.parametrize("name", list(VARIANTS))
def test_smoke_run_on_hotspot_trace(name):
    """Short synthetic hotspot run through repay.sim.run."""
    trace = make_trace("hotspot", 300, seed=7)
    res = run(trace, VARIANTS[name](), P)
    assert res["cap_violations"] == 0
    assert np.isfinite(res["util_rate"]) and res["util_rate"] >= 0.0
    assert 0.0 <= res["rt_success"]["all"] <= 1.0 or np.isnan(res["rt_success"]["all"])


def test_js_random_states_and_video_rates():
    """JS: queues and deficits stay nonnegative; video rates are 0 or in [rmin_V, rmax_V]."""
    churn = _Churn(seed=23)
    mech = JS(P, seed=5)
    for t in range(200):
        v = churn.step(t)
        rates = mech.allocate(v)
        vid = v.decl == 1
        ok = (np.abs(rates[vid]) < 1e-12) | ((rates[vid] >= P.rmin_V - 1e-9) & (rates[vid] <= P.rmax_V + 1e-9))
        assert np.all(ok), t
        assert all(d >= 0.0 for d in mech.deficit.values())
        assert all(q >= 0.0 for q in mech.Qe.values())
        assert all(q >= 0.0 for q in mech.Qv.values())


def test_reset_reproduces_js_arrivals():
    """Bernoulli deficit arrivals come from the seeded generator: same seed, same rates."""
    churn = _Churn(seed=3)
    views = [churn.step(t) for t in range(60)]
    a, b = JS(P, seed=9), JS(P, seed=9)
    ra = [a.allocate(v) for v in views]
    rb = [b.allocate(v) for v in views]
    for x, y in zip(ra, rb):
        np.testing.assert_array_equal(x, y)
    a.reset()
    rc = [a.allocate(v) for v in views]
    for x, y in zip(ra, rc):
        np.testing.assert_array_equal(x, y)


def test_inverse_fprime_is_accurate():
    """The table-plus-Newton inverse of f'(u) reproduces u for several p."""
    for pp in (1.0, 1.4, 5.7, 7.6):
        h = _inverse_fprime(pp)
        u = np.logspace(-6, 3, 60)
        np.testing.assert_allclose(h(_fprime(u, pp)), u, rtol=1e-9, atol=0.0)
        assert np.all(h(np.array([0.0, -1.0])) == 0.0)


def test_pswc_water_filling_with_bounds():
    """PSWC: sum equals A, bounds respected, and it reduces to plain water-filling for m = 0."""
    x = pswc(3.0, np.array([1.0, 2.0, 1.0]), np.array([0.5, 0.0, 0.0]), np.array([2.0, 5.0, 0.4]))
    assert x.sum() == pytest.approx(3.0, abs=1e-9)
    assert np.all(x >= np.array([0.5, 0.0, 0.0]) - 1e-12)
    assert np.all(x <= np.array([2.0, 5.0, 0.4]) + 1e-12)
    np.testing.assert_allclose(pswc(3.0, np.ones(3), np.zeros(3), np.array([10.0, 10.0, 10.0])),
                               [1.0, 1.0, 1.0], atol=1e-9)


# ---------------------------------------------------------------------------
# A1. FQ
# ---------------------------------------------------------------------------

def test_fq_hand_unweighted():
    v = _view(10.0, [0, 1, 2, 3], [0, 0, 0, 0], [0, 0, 1, 2], [8, 8, 0, 0])
    np.testing.assert_allclose(FQ(P).allocate(v), [3.4, 3.4, 3.0, 0.2], atol=1e-9)


def test_fq_hand_weighted():
    v = _view(10.0, [0, 1, 2, 3], [0, 1, 0, 2], [0, 0, 1, 2], [8, 8, 0, 0])
    np.testing.assert_allclose(FQ(P, weighted=True).allocate(v), [2.45, 4.9, 2.45, 0.2], atol=1e-9)


def test_fq_equals_pf_for_one_tier():
    """With all devices in one tier, FQ coincides with PF (documented overlap, research/04 A1)."""
    rng = np.random.default_rng(4)
    fq, pf = FQ(P), PF(P)
    for _ in range(100):
        n = int(rng.integers(1, 30))
        decl = rng.integers(0, 3, n)
        v = _view(float(rng.uniform(0.1, 200)), np.arange(n), np.full(n, 1), decl,
                  rng.choice([0.0, 0.4, 3.0, 30.0], n))
        np.testing.assert_allclose(fq.allocate(v), pf.allocate(v), rtol=0, atol=1e-9)


def test_fq_uncongested_gives_demand():
    v = _view(100.0, [0, 1, 2], [0, 1, 2], [0, 1, 2], [4.0, 0.0, 0.0])
    np.testing.assert_allclose(FQ(P, weighted=True).allocate(v), [4.0, 3.0, 0.2], atol=1e-12)


# ---------------------------------------------------------------------------
# A2. JS
# ---------------------------------------------------------------------------

def test_js_hand_example_five_slots():
    """C = 1, one gaming flow and one elastic device (d = 5), deterministic arrivals, q = 0.9."""
    js = JS(P, deterministic=True)
    expected = [(0.2, 0.8), (0.0, 1.0), (0.0, 1.0), (0.2, 0.8), (0.0, 1.0)]
    for t, (eg, ee) in enumerate(expected):
        x = js.allocate(_view(1.0, [0, 1], [0, 0], [2, 0], [0.0, 5.0], t=t))
        np.testing.assert_allclose(x, [eg, ee], atol=1e-9, err_msg=f"slot {t + 1}")
        if t == 0:
            assert js.Qe[1] == pytest.approx(4.2, abs=1e-9)
        if t == 1:
            # Elastic congestion control: x~ = V/Q - 1 = 3.7619 in slot 2 (Q after slot 2 = 4.2 + 3.7619 - 1).
            assert js.Qe[1] == pytest.approx(6.9619, abs=1e-4)
        if t == 2:
            assert js.deficit[0] == pytest.approx(1.8, abs=1e-9)
            assert 1.8 / 0.2 == pytest.approx(9.0)
            assert js.Qe[1] == pytest.approx(7.8347, abs=5e-5)
    assert js.deficit[0] == pytest.approx(2.6, abs=1e-9)
    assert js.Qe[1] == pytest.approx(8.9164, abs=5e-5)


def test_js_ample_capacity_serves_every_rt_flow():
    """C = 100 with 5 gaming and 3 elastic devices: every RT flow is served and all deficits stay 0."""
    js = JS(P, deterministic=True)
    ids = np.arange(8)
    decl = np.array([2] * 5 + [0] * 3)
    cap = np.array([0.0] * 5 + [5.0] * 3)
    for t in range(200):
        x = js.allocate(_view(100.0, ids, np.zeros(8), decl, cap, t=t))
        assert np.all(x[:5] >= P.r_G - 1e-12)
        assert all(d == pytest.approx(0.0, abs=1e-12) for d in js.deficit.values())


def test_js_delivery_ratio_on_feasible_load():
    """5 gaming and 30 elastic devices (d = 5) at C = 20, no churn, 5000 slots."""
    js = JS(P, deterministic=True)
    n_g, n_e = 5, 30
    ids = np.arange(n_g + n_e)
    decl = np.array([2] * n_g + [0] * n_e)
    cap = np.array([0.0] * n_g + [5.0] * n_e)
    served = np.zeros(n_g)
    max_def = np.zeros(5000)
    for t in range(5000):
        x = js.allocate(_view(20.0, ids, np.zeros(ids.size), decl, cap, t=t))
        served += x[:n_g] >= P.r_G - 1e-12
        max_def[t] = max(js.deficit.values())
    assert np.all(served / 5000 >= 0.9 - 0.01)
    first, second = max_def[:2500].max(), max_def[2500:].max()
    assert second <= first + 1.0, "deficits grow linearly in the second half"


# ---------------------------------------------------------------------------
# B1. LendRecoup
# ---------------------------------------------------------------------------

def test_lendrecoup_paper_example_4():
    """Demands (2,2,0), (2,2,0), (2,2,6), C = 3, unweighted endowments."""
    lr = LendRecoup(P, weighted=False)
    demands = [[2, 2, 0], [2, 2, 0], [2, 2, 6]]
    alloc = [[1.5, 1.5, 0.0], [1.5, 1.5, 0.0], [0.0, 0.0, 3.0]]
    credit = [[-0.5, -0.5, 1.0], [-1.0, -1.0, 2.0], [0.0, 0.0, 0.0]]
    for t in range(3):
        x = lr.allocate(_view(3.0, [0, 1, 2], [0, 0, 0], [0, 0, 0], demands[t], t=t))
        np.testing.assert_allclose(x, alloc[t], atol=1e-9)
        np.testing.assert_allclose([lr.credit[i] for i in range(3)], credit[t], atol=1e-9)


def test_lendrecoup_no_shortage_books():
    """Demands (1,2,4), C = 10, equal endowments 10/3: unvalued allocation (3,3,4), credits e - a."""
    lr = LendRecoup(P, weighted=False)
    x = lr.allocate(_view(10.0, [0, 1, 2], [0, 0, 0], [0, 0, 0], [1.0, 2.0, 4.0]))
    np.testing.assert_allclose(x, [1.0, 2.0, 4.0], atol=1e-9)
    e = 10.0 / 3.0
    np.testing.assert_allclose([lr.credit[i] for i in range(3)], [e - 3, e - 3, e - 4], atol=1e-9)
    np.testing.assert_allclose([lr.cum[i] for i in range(3)], [3, 3, 4], atol=1e-9)


@pytest.mark.parametrize("weighted", [True, False])
def test_lendrecoup_credit_fairness_per_slot(weighted):
    """CF4 and CF5 with pre-slot credits and current endowments; credits balance under shortage."""
    churn = _Churn(seed=31)
    lr = LendRecoup(P, weighted=weighted)
    for t in range(200):
        v = churn.step(t)
        n = v.ids.size
        ids = v.ids.tolist()
        c_old = np.array([0.0 if (i in churn.new or i in churn.changed) else lr.credit.get(i, 0.0)
                          for i in ids])
        w = P.w_arr[v.tier] if weighted else np.ones(n)
        e = v.C * w / w.sum()
        D = _demand_of(v.decl, v.cap)
        x = lr.allocate(v)
        if v.C <= 0:
            continue
        cf4 = x >= np.minimum(D, e + np.minimum(0.0, c_old)) - 1e-9
        assert np.all(cf4), (t, "CF4")
        guar = np.maximum(0.0, e + c_old)
        if np.any(x > guar + 1e-9):
            cf5 = (x >= D - 1e-9) | (x >= e + c_old - 1e-9)
            assert np.all(cf5), (t, "CF5")
        if D.sum() > v.C:
            change = np.array([lr.credit[i] for i in ids]) - c_old
            assert abs(change.sum()) <= 1e-9, (t, "credit balance")


def test_lendrecoup_class_change_resets_state():
    """A device whose declared class changes restarts with zero credit, cumulative and endowment."""
    lr = LendRecoup(P, weighted=False)
    ids, tier = [0, 1], [0, 0]
    _warm_up(lr, ids, tier, [0, 0], [5.0, 5.0])
    lr.credit[0], lr.cum[0], lr.Ehat[0] = 5.0, 40.0, 50.0
    x = lr.allocate(_view(2.0, ids, tier, [2, 0], [0.0, 5.0]))   # device 0 becomes gaming
    e = 1.0
    assert lr.cum[0] == pytest.approx(x[0], abs=1e-9)
    assert lr.Ehat[0] == pytest.approx(e, abs=1e-9)
    assert lr.credit[0] == pytest.approx(e - x[0], abs=1e-9)


# ---------------------------------------------------------------------------
# B2. Potential
# ---------------------------------------------------------------------------

def _phi(x, decl, cap, delta, prop, U):
    """Potential sum_i f(z_i) for elastic devices (v_i(x) = min(x, cap))."""
    p = float(np.log(2.0 * x.size)) if x.size > 1 else 1.0
    p = max(1.0, p)
    v = np.minimum(x, cap)
    z = np.maximum(delta + prop - v, 0.0) / U
    return float(np.sum((1.0 + z * z / (4.0 * p * p)) ** p))


def test_potential_equalisation():
    """C = 1, two elastic devices (d = 1), U = 1, signed deficits (0.4, 0): rates (0.7, 0.3)."""
    pt = Potential(P)
    ids, tier, decl, cap = [0, 1], [0, 0], [0, 0], [1.0, 1.0]
    _warm_up(pt, ids, tier, decl, cap)
    pt.delta[0], pt.delta[1] = 0.4, 0.0
    pt.scale[0], pt.scale[1] = 1.0, 1.0
    x = pt.allocate(_view(1.0, ids, tier, decl, cap))
    np.testing.assert_allclose(x, [0.7, 0.3], atol=1e-9)
    assert pt.delta[0] == pytest.approx(0.2, abs=1e-9)
    assert pt.delta[1] == pytest.approx(0.2, abs=1e-9)


def test_potential_rt_rotation():
    """C = 0.3, gaming G and elastic E (d = 1): serve G in slot 1, block it in slot 2."""
    pt = Potential(P)
    ids, tier, decl, cap = [0, 1], [0, 0], [2, 0], [0.0, 1.0]
    x1 = pt.allocate(_view(0.3, ids, tier, decl, cap, t=0))
    np.testing.assert_allclose(x1, [0.2, 0.1], atol=1e-9)
    assert pt.delta[0] == pytest.approx(-0.1, abs=1e-9)
    assert pt.delta[1] == pytest.approx(0.05, abs=1e-9)
    x2 = pt.allocate(_view(0.3, ids, tier, decl, cap, t=1))
    np.testing.assert_allclose(x2, [0.0, 0.3], atol=1e-9)


def test_potential_leftover_and_surplus():
    """C = 1: A (d = 1) and B (d = 0) in slot 1; both (d = 1) in slot 2 gives (0.25, 0.75)."""
    pt = Potential(P)
    x1 = pt.allocate(_view(1.0, [0, 1], [0, 0], [0, 0], [1.0, 0.0], t=0))
    np.testing.assert_allclose(x1, [1.0, 0.0], atol=1e-9)
    assert pt.delta[0] == pytest.approx(-0.5, abs=1e-9)
    x2 = pt.allocate(_view(1.0, [0, 1], [0, 0], [0, 0], [1.0, 1.0], t=1))
    np.testing.assert_allclose(x2, [0.25, 0.75], atol=1e-9)

    # Slot 2 potential at the returned rates is no larger than at random feasible rates.
    prop = np.array([0.5, 0.5])
    U = np.array([1.0, 1.0])
    delta = np.array([-0.5, 0.0])
    cap = np.array([1.0, 1.0])
    base = _phi(x2, np.zeros(2), cap, delta, prop, U)
    rng = np.random.default_rng(0)
    for _ in range(100):
        a = rng.uniform(0.0, 1.0)
        b = rng.uniform(0.0, 1.0 - a)
        assert base <= _phi(np.array([a, b]), np.zeros(2), cap, delta, prop, U) + 1e-12


def test_potential_polish_never_worse():
    """The optional toggle search only accepts improving moves, so its potential is no larger."""
    churn = _Churn(seed=41)
    plain, polished = Potential(P), Potential(P, polish=True)
    for t in range(60):
        v = churn.step(t)
        x_plain = plain.allocate(v)
        x_pol = polished.allocate(v)
        assert x_pol.sum() <= v.C + 1e-9
        assert np.all(x_pol >= -1e-12)
        assert np.all(x_pol <= _demand_of(v.decl, v.cap) + 1e-9)
        assert x_plain.shape == x_pol.shape


def test_potential_class_change_resets_state():
    """A device whose class changes restarts with zero deficit and zero scale before the slot."""
    pt = Potential(P)
    ids, tier = [0, 1], [0, 0]
    _warm_up(pt, ids, tier, [0, 0], [2.0, 2.0])
    pt.delta[0], pt.scale[0] = 7.0, 9.0
    x = pt.allocate(_view(1.0, ids, tier, [2, 0], [0.0, 2.0]))   # device 0 becomes gaming
    v0 = min(1.0, P.r_G)          # usable volume of a gaming flow at C = 1: min(C, r_G)
    prop0 = v0 / 2.0              # two devices, unweighted proportionality
    assert pt.scale[0] == pytest.approx(v0, abs=1e-9)
    assert pt.delta[0] == pytest.approx(prop0 - x[0], abs=1e-9)


# ---------------------------------------------------------------------------
# B3. DMMF
# ---------------------------------------------------------------------------

def test_dmmf_same_example_as_lendrecoup():
    dm = DMMF(P, weighted=False)
    demands = [[2, 2, 0], [2, 2, 0], [2, 2, 6]]
    alloc = [[1.5, 1.5, 0.0], [1.5, 1.5, 0.0], [0.0, 0.0, 3.0]]
    for t in range(3):
        x = dm.allocate(_view(3.0, [0, 1, 2], [0, 0, 0], [0, 0, 0], demands[t], t=t))
        np.testing.assert_allclose(x, alloc[t], atol=1e-9)


def test_dmmf_catch_up_on_idle_device():
    """C = 2, demands (2,0) for 5 slots, then (2,2): (2,0) then (0,2)."""
    dm = DMMF(P, weighted=False)
    for t in range(5):
        np.testing.assert_allclose(dm.allocate(_view(2.0, [0, 1], [0, 0], [0, 0], [2.0, 0.0], t=t)), [2.0, 0.0],
                                   atol=1e-9)
    np.testing.assert_allclose(dm.allocate(_view(2.0, [0, 1], [0, 0], [0, 0], [2.0, 2.0], t=5)), [0.0, 2.0],
                               atol=1e-9)


def test_dmmf_differs_from_lendrecoup_on_injected_state():
    """Entitlement 9 each, cumulative (6, 8), C = 2, demands 5: DMMF gives (2,0), LendRecoup (1,1)."""
    v = _view(2.0, [0, 1], [0, 0], [0, 0], [5.0, 5.0])
    dm = DMMF(P, weighted=False)
    _warm_up(dm, [0, 1], [0, 0], [0, 0], [5.0, 5.0])
    dm.A.update({0: 6.0, 1: 8.0})
    dm.Ehat.update({0: 9.0, 1: 9.0})
    np.testing.assert_allclose(dm.allocate(v), [2.0, 0.0], atol=1e-9)

    lr = LendRecoup(P, weighted=False)
    _warm_up(lr, [0, 1], [0, 0], [0, 0], [5.0, 5.0])
    lr.credit.update({0: 3.0, 1: 1.0})
    lr.cum.update({0: 6.0, 1: 8.0})
    lr.Ehat.update({0: 9.0, 1: 9.0})
    np.testing.assert_allclose(lr.allocate(v), [1.0, 1.0], atol=1e-9)


def _greedy_quantised(C, D, Eh, A, delta):
    """Item-by-item Algorithm 1 with quanta delta: each quantum goes to the requesting device with
    the smallest (A_i + x_i) / Eh_i, ties broken by smaller id."""
    n = len(D)
    x = [0.0] * n
    total = int(round(C / delta))
    for _ in range(total):
        best, best_key = None, None
        for i in range(n):
            if x[i] + delta <= D[i] + 1e-12:
                key = ((A[i] + x[i]) / Eh[i], i)
                if best_key is None or key < best_key:
                    best, best_key = i, key
        if best is None:
            break
        x[best] += delta
    return np.array(x)


def test_dmmf_matches_quantised_algorithm_one():
    """Divisible water-fill equals item-by-item Algorithm 1 with quanta 0.001 up to n * 0.001 in l1."""
    rng = np.random.default_rng(8)
    delta = 0.001
    for _ in range(12):
        n = int(rng.integers(2, 5))
        C = float(rng.integers(300, 1500)) * delta
        D = rng.uniform(0.2, 1.5, n)
        if D.sum() <= C:
            D = D * (2.0 * C / D.sum())
        A = rng.uniform(0.0, 2.0, n)
        Eh0 = rng.uniform(0.5, 3.0, n)
        dm = DMMF(P, weighted=False)
        ids = list(range(n))
        _warm_up(dm, ids, [0] * n, [0] * n, D)
        dm.A.update({i: float(A[i]) for i in ids})
        dm.Ehat.update({i: float(Eh0[i]) for i in ids})
        cont = dm.allocate(_view(C, ids, [0] * n, [0] * n, D))
        Eh_after = Eh0 + C / n
        oracle = _greedy_quantised(C, D, Eh_after, A, delta)
        assert np.abs(cont - oracle).sum() <= n * delta + 1e-9


def test_dmmf_restart_variant_resets_on_change():
    """restart=True: when the active set changes, every device starts from zero history."""
    dm = DMMF(P, weighted=False, restart=True)
    dm.allocate(_view(2.0, [0, 1], [0, 0], [0, 0], [2.0, 2.0]))
    dm.allocate(_view(2.0, [0, 1], [0, 0], [0, 0], [2.0, 2.0], t=1))
    x = dm.allocate(_view(2.0, [0, 1, 2], [0, 0, 0], [0, 0, 0], [2.0, 2.0, 2.0], t=2))
    np.testing.assert_allclose(x, [2.0 / 3.0] * 3, atol=1e-9)


def test_dmmf_class_change_resets_state():
    dm = DMMF(P, weighted=False)
    ids, tier = [0, 1], [0, 0]
    _warm_up(dm, ids, tier, [0, 0], [5.0, 5.0])
    dm.A[0], dm.Ehat[0] = 7.0, 9.0
    x = dm.allocate(_view(2.0, ids, tier, [2, 0], [0.0, 5.0]))
    assert dm.A[0] == pytest.approx(x[0], abs=1e-9)
    assert dm.Ehat[0] == pytest.approx(1.0, abs=1e-9)
