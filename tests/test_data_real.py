"""Tests of the trace built from the public Paris Wi-Fi and HSDPA datasets.

Tests that need the raw data are skipped when data/raw is absent. The classifier test uses synthetic sessions.
"""
import os

import numpy as np
import pandas as pd
import pytest

from experiments.data_real import PARIS_DIR, SITES, class_shares, classify_sessions, make_real_trace

HAVE_DATA = all(os.path.exists(os.path.join(PARIS_DIR, f"{s}_full.csv")) for s in SITES) and os.path.isdir(
    os.path.join(os.path.dirname(PARIS_DIR), "hsdpa"))
needs_data = pytest.mark.skipif(not HAVE_DATA, reason="data/raw is absent")
T = 600


def _session_frame(rows):
    """Synthetic sessions: rows of (duration, bytesin, bytesout, packetsin)."""
    cols = ["duration", "bytesin", "bytesout", "packetsin"]
    return pd.DataFrame(rows, columns=cols, dtype=float)


def test_classify_sessions_rules():
    """Video: two-way at call rates. Gaming: two-way, low rate, small downlink packets. Else elastic."""
    df = _session_frame([
        (100, 10e6, 5e6, 7000),        # video: rin 0.8, rout 0.4, sym 0.5
        (100, 1e6, 5e5, 10000),        # gaming: rout 0.04 < 0.1, sym 0.5, psin 100 bytes
        (100, 1e6, 0, 10000),          # one-way download: sym 0, elastic
        (100, 1e6, np.nan, 10000),     # missing uplink bytes: elastic
        (100, 1e6, 5e5, 0),            # no downlink packets: elastic
        (100, 1.5e6, 5e5, 1000),       # large downlink packets (psin 1500): elastic
        (0, 1e6, 5e5, 10000),          # zero duration: elastic
        (100, 10e6, 4e6, 7000),        # video at sym 0.4: below the strict sym_lo of 0.5
    ])
    assert classify_sessions(df).tolist() == [1, 2, 0, 0, 0, 0, 0, 1]
    assert classify_sessions(df, sym_lo=0.5, sym_hi=2.0, up_min=0.2).tolist() == [1, 2, 0, 0, 0, 0, 0, 0]


@needs_data
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


@needs_data
def test_random_attributes_are_repeatable():
    """classes='random', tiers='random' gives the same tier, cls, t_arr and ell lists on every call."""
    a, _ = make_real_trace("PW0127", 0, T, classes="random", tiers="random")
    b, _ = make_real_trace("PW0127", 0, T, classes="random", tiers="random")
    for key in ("tier", "cls", "t_arr", "ell"):
        assert [d[key] for d in a["devices"]] == [d[key] for d in b["devices"]]


@needs_data
def test_log_classes_video_share_and_meta():
    """With classes='log' the video share is between 1% and 30%, free tiers, and RT devices are always on."""
    tr, meta = make_real_trace("PW0127", 0, 7200, classes="log", tiers="free")
    assert 0.01 <= meta["share_video"] <= 0.30
    assert meta["n_elastic"] + meta["n_video"] + meta["n_gaming"] == meta["n_devices"]
    assert meta["classes"] == "log" and meta["tiers"] == "free"
    assert set(meta["rule"]) == {"sym_lo", "sym_hi", "up_min", "game_up_min", "game_pkt_max"}
    assert all(d["tier"] == 0 for d in tr["devices"])
    for d in tr["devices"]:
        if d["cls"] > 0:
            assert d["ell"] == 30.0 and d["on"].all()


@needs_data
def test_devices_are_well_formed():
    """Every device has t_dep > t_arr >= 0 and an on-array of length t_dep - t_arr."""
    tr, _ = make_real_trace("PW0232", 1, T, load=1.0)
    assert len(tr["C"]) == T
    for d in tr["devices"]:
        assert d["t_dep"] > d["t_arr"] >= 0
        assert d["t_dep"] <= T
        assert len(d["on"]) == d["t_dep"] - d["t_arr"]


@needs_data
def test_class_shares_are_fractions():
    """Shares lie in [0, 1] and the video-like sessions have a higher uplink rate than the elastic ones."""
    cs = class_shares("PW0127")
    assert 0.0 <= cs["share_video"] <= 1.0 and 0.0 <= cs["share_gaming"] <= 1.0
    assert cs["median_rout"]["video"] > cs["median_rout"]["elastic"]
