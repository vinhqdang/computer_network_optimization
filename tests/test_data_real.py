"""Tests of the trace built from the public Paris Wi-Fi and HSDPA datasets (skipped when data/raw is absent)."""
import os

import numpy as np
import pytest

from experiments.data_real import PARIS_DIR, SITES, make_real_trace

HAVE_DATA = all(os.path.exists(os.path.join(PARIS_DIR, f"{s}.csv")) for s in SITES) and os.path.isdir(
    os.path.join(os.path.dirname(PARIS_DIR), "hsdpa"))
pytestmark = pytest.mark.skipif(not HAVE_DATA, reason="data/raw is absent")
T = 600


def test_trace_is_deterministic():
    """The same site, window and load give identical capacity, devices and attributes."""
    a, ma = make_real_trace("PW0127", 0, T, load=1.0)
    b, mb = make_real_trace("PW0127", 0, T, load=1.0)
    assert np.array_equal(a["C"], b["C"])
    assert len(a["devices"]) == len(b["devices"]) > 0
    for da, db in zip(a["devices"], b["devices"]):
        assert (da["tier"], da["cls"], da["t_arr"], da["t_dep"], da["ell"]) == (
            db["tier"], db["cls"], db["t_arr"], db["t_dep"], db["ell"])
        assert np.array_equal(da["on"], db["on"])
    assert ma == mb


def test_devices_are_well_formed():
    """Every device has t_dep > t_arr >= 0 and an on-array of length t_dep - t_arr."""
    tr, _ = make_real_trace("PW0232", 1, T, load=1.0)
    assert len(tr["C"]) == T
    for d in tr["devices"]:
        assert d["t_dep"] > d["t_arr"] >= 0
        assert d["t_dep"] <= T
        assert len(d["on"]) == d["t_dep"] - d["t_arr"]
