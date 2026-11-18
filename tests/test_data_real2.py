"""Tests of the second real-trace scenario (public session logs and 4G capacity logs).

Tests that need the raw data are skipped when data/raw is absent.
"""
import os

import numpy as np
import pytest

from experiments.data_real import C_FLOOR, MIN_STAY
from experiments.data_real2 import GHENT_DIR, GPS_FILE, MESA_FILE, RACA_DIR, SOURCES, make_trace2, video_share_file

HAVE_DATA = (os.path.exists(GPS_FILE) and os.path.exists(MESA_FILE) and os.path.isdir(GHENT_DIR)
             and os.path.isdir(RACA_DIR))
needs_data = pytest.mark.skipif(not HAVE_DATA, reason="data/raw is absent")
T = 600


@needs_data
@pytest.mark.parametrize("src", SOURCES)
def test_trace_is_deterministic(src):
    """The same source, window and load give identical capacity, devices and attributes."""
    a, ma = make_trace2(src, 0, T)
    b, mb = make_trace2(src, 0, T)
    assert np.array_equal(a["C"], b["C"])
    assert ma == mb
    assert len(a["devices"]) == len(b["devices"]) > 0
    for da, db in zip(a["devices"], b["devices"]):
        assert (da["tier"], da["cls"], da["t_arr"], da["t_dep"], da["ell"]) == (
            db["tier"], db["cls"], db["t_arr"], db["t_dep"], db["ell"])


@needs_data
@pytest.mark.parametrize("src", SOURCES)
def test_device_fields_are_valid(src):
    """Tiers and classes lie in range, stays are inside the window and of at least MIN_STAY slots, caps are
    positive and on-sequences have the stay's length. The logs carry no packet counts, so no device is gaming."""
    trace, meta = make_trace2(src, 1, T)
    assert trace["C"].shape == (T,) and np.all(trace["C"] >= C_FLOOR)
    assert len(trace["devices"]) > 0
    assert meta["n_gaming"] == 0
    for d in trace["devices"]:
        assert d["tier"] in (0, 1, 2)
        assert d["cls"] in (0, 1, 2)
        assert 0 <= d["t_arr"] < d["t_dep"] <= T
        assert d["t_dep"] - d["t_arr"] >= MIN_STAY
        assert np.isfinite(d["ell"]) and d["ell"] > 0
        assert len(d["on"]) == d["t_dep"] - d["t_arr"]


@needs_data
@pytest.mark.parametrize("src", SOURCES)
def test_video_share_in_range(src):
    """The video-like share of the whole file lies between 0.5% and 40%."""
    share = video_share_file(src)["share_video"]
    assert 0.005 <= share <= 0.40
