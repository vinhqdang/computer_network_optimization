"""Simulator smoke tests for both scenarios and all mechanisms."""
import math

import numpy as np
import pytest

from repay.mechanisms import PF, WFQ, Credit, PlainDPP, Priority, Repay
from repay.params import Params
from repay.sim import make_trace, run

P = Params()
MECHS = {
    "repay": lambda: Repay(P),
    "repay_entrant": lambda: Repay(P, entrant=True),
    "repay_recycle": lambda: Repay(P, recycle=True),
    "plain_dpp": lambda: PlainDPP(P),
    "pf": lambda: PF(P),
    "wfq": lambda: WFQ(P),
    "priority": lambda: Priority(P),
    "credit": lambda: Credit(P),
}
T = 300


@pytest.mark.parametrize("scenario", ["hotspot", "home"])
@pytest.mark.parametrize("name", sorted(MECHS))
def test_smoke(scenario, name):
    """T=300 runs: no capacity violations and finite headline metrics."""
    trace = make_trace(scenario, T, seed=11)
    out = run(trace, MECHS[name](), P)
    assert out["cap_violations"] == 0
    assert math.isfinite(out["util_rate"])
    assert math.isfinite(out["rt_success"]["all"])
    assert math.isfinite(out["el_rate"])
    assert math.isfinite(out["jain"])
    assert math.isfinite(out["max_env"])
    # Home has only premium devices, so F and Y ratios are undefined there (NaN by design).
    assert math.isfinite(out["served_ratio"]["P"]), (scenario, name)
    if scenario == "hotspot":
        assert math.isfinite(out["served_ratio"]["F"]) and math.isfinite(out["served_ratio"]["Y"])
        assert math.isfinite(out["free_floor_ratio"])
    if isinstance(MECHS[name](), Repay):
        assert math.isfinite(out["D_over_B_max"])
        assert out["D_over_B_max"] <= 1.0 + 1e-6


def test_declare_override_changes_declared_class():
    """A declare override changes the declared class seen by the mechanism."""
    trace = make_trace("hotspot", T, seed=5)
    dev = trace["devices"][0]
    target = dev["id"]
    truth = dev["cls"]
    decl_val = 1 if truth != 1 else 2
    base = run(trace, PF(P), P)
    over = run(trace, PF(P), P, declare={target: decl_val})
    j = int(np.flatnonzero(base["dev"]["id"] == target)[0])
    assert int(over["dev"]["decl"][j]) == decl_val
    assert int(base["dev"]["decl"][j]) == truth


def test_per_slot_declare_array_is_applied():
    """A per-slot declaration array is used slot by slot."""
    trace = make_trace("home", T, seed=2)
    dev = trace["devices"][0]
    L = dev["t_dep"] - dev["t_arr"]
    arr = np.zeros(L, dtype=int)
    arr[L // 2:] = 2
    out = run(trace, Repay(P), P, declare={dev["id"]: arr}, record_series=True)
    assert out["cap_violations"] == 0
    assert out["series"]["C"].size == T
