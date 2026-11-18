"""Second trace-driven scenario: two further public session logs and two further 4G capacity logs.

Sessions (each source is one shared link, the unit chosen by unit_choice below):
  gps   Grand Paris Sud public Wi-Fi, RADIUS accounting sessions, 29 Jul to 31 Aug 2026
        (data/raw/grandparissud_wifi_sessions/sessions.csv). start_time_session is UTC. The duration is the
        ISO-8601 field acct_session_time. donnees_recues_en_go is the volume received by the device, i.e. the
        downlink (bytes_down), and donnees_envoyees_en_go the volume the device sent, the uplink (bytes_up),
        both decimal GB converted with 1e9. The downlink reading follows the inventory and the totals of the
        file (1,455 GB received against 611 GB sent). Rows without a received volume (3,207) are dropped.
  mesa  City of Mesa (Arizona) public Wi-Fi, July 2025 (data/raw/socrata_mesa_wifi_sessions/mesa_2025_07.csv).
        Exact duplicate rows (61,125) are removed. Only ssid '@mesa' (the public network) is kept. Counter
        names are taken as written: bytes_to_user is the downlink (to the device), bytes_from_user the uplink
        (from the device). In this file the uplink counter is several times the downlink counter in every
        duration band, which is unusual for a public hotspot and is reported in the run output. The
        duration is session_duration, equal to endtime - starttime in every row. starttime carries no zone;
        it is read as Arizona local time (UTC-7, no daylight saving) and converted to UTC by adding 7 hours.

Capacity (one value per 1-second slot, Mbit/s):
  ghent  40 four-G bandwidth logs (data/raw/ghent_4g_lte/logs/report_*.log). Each line is one slot; the
         throughput is column 5 * 8 / column 6 / 1000 (bytes per ms to Mbit/s). About 99% of the lines span
         0.999 to 1.001 s, so a line is taken as one slot.
  raca   135 four-G traces (data/raw/zenodo_raca_4g_lte/extracted/Dataset/*/*.csv). DL_bitrate is in kbit/s
         (the record's maximum, 173,016, matches the published 173 Mbit/s peak), divided by 1000. Each row is
         one slot (median interval 1 s).

Pairing: gps with ghent, mesa with raca. make_trace2 follows experiments.data_real.make_real_trace: the same
tier and on/off draws, the same elastic cap rule, the same capacity scaling and the same window choice (see
pick_windows2). Two differences: the class comes from the logged traffic only (these logs have no packet
counts, so the gaming rule never applies and no session is gaming), and the meta dict has source, unit and
capacity_source in place of site.

Unit choice (unit_choice): for each candidate unit, the mean concurrency over its six busiest two-hour
windows, one per day on the source's timeline (the busiest minute-aligned 7200 s window of each of the six
busiest days, averaged). The candidate with the highest score is chosen if it reaches UNIT_MIN (25, the lower
end of "about 30"). Otherwise the smallest natural grouping that reaches UNIT_MIN is used, with
the top unit of that grouping; if none does, the whole source is one link.

Run as: python -m experiments.data_real2
"""
import functools
import glob
import os
import re

import numpy as np
import pandas as pd

from experiments.common import ROOT
from experiments.data_real import (C_FLOOR, DAY, DEFAULT_RULE, ELL_EL_CLIP, MIN_STAY, NOMINAL_GAMING,
                                   NOMINAL_VIDEO, PI_ON, P_OFF_ON, P_ON_OFF, RT_ELL, TIER_P_EST, classify_sessions)
from repay.params import F_TIER
from repay.sim import HOTSPOT_DEFAULTS, _onoff

RAW = os.path.join(ROOT, "data", "raw")
GPS_FILE = os.path.join(RAW, "grandparissud_wifi_sessions", "sessions.csv")
MESA_FILE = os.path.join(RAW, "socrata_mesa_wifi_sessions", "mesa_2025_07.csv")
GHENT_DIR = os.path.join(RAW, "ghent_4g_lte", "logs")
RACA_DIR = os.path.join(RAW, "zenodo_raca_4g_lte", "extracted", "Dataset")

SOURCES = ("gps", "mesa")
SOURCE_INDEX = {"gps": 0, "mesa": 1}
PAIRS = {"gps": "ghent", "mesa": "raca"}
SOURCE_LABEL = {"gps": "Grand Paris Sud", "mesa": "City of Mesa"}
CAP_LABEL = {"ghent": "Ghent 4G logs", "raca": "RACA 4G traces"}
N_WIN = 6
WIN_T = 7200
UNIT_TARGET = 30.0
UNIT_MIN = 25.0  # "about 30": a unit reaches the target when its score is at least this value
MESA_PUBLIC_SSID = "@mesa"
MESA_UTC_OFFSET_H = 7
TIER_MODES = ("free", "random", "estimated")
TIER_P = HOTSPOT_DEFAULTS["tier_p"]
CAP_SEED = 7000
PER_UNIT_DIMS = {
    # single-unit candidates: (dimension, session column)
    "gps": (("site", "site"), ("venue", "venue")),
    # SSID is not a candidate: after the public-SSID filter it is one value covering the whole network.
    "mesa": (("site", "site"), ("ap", "ap")),
}
AGGREGATE_DIMS = {
    # natural groupings used when no single unit reaches UNIT_MIN, finest first
    "gps": (("commune", "commune"), ("perimetre", "perimetre")),
    "mesa": (),
}
_TZ0 = pd.Timestamp("1970-01-01", tz="UTC")
_ISO = re.compile(r"^P(?:(?P<d>\d+)D)?T?(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+(?:\.\d+)?)S)?$")


def _epoch(ts):
    """Whole epoch seconds of tz-aware timestamps (scalar or Series), without the int64 representation."""
    return (ts - _TZ0) // pd.Timedelta("1s")


def _iso_seconds(series):
    """ISO-8601 durations such as P0DT00H02M12S as seconds (NaN where unparsable)."""
    ext = series.astype(str).str.strip().str.extract(_ISO)
    ok = ext[["d", "h", "m", "s"]].notna().any(axis=1)
    num = lambda c: pd.to_numeric(ext[c], errors="coerce").fillna(0.0)
    secs = num("d") * DAY + num("h") * 3600.0 + num("m") * 60.0 + num("s")
    return secs.where(ok)


def _frame(start, duration, bytes_down, bytes_up, keys):
    """Valid sessions as a DataFrame sorted by start (keys are extra candidate-unit columns)."""
    ok = (start.notna() & duration.notna() & (duration >= MIN_STAY)
          & bytes_down.notna() & (bytes_down >= 0) & bytes_up.notna() & (bytes_up >= 0))
    cols = {"start": start, "duration": duration.astype(float), "bytes_down": bytes_down.astype(float),
            "bytes_up": bytes_up.astype(float), **keys}
    out = pd.DataFrame(cols)[ok].reset_index(drop=True)
    return out.sort_values(["start", "duration", "bytes_down"], kind="mergesort").reset_index(drop=True)


@functools.lru_cache(maxsize=None)
def _read_gps():
    df = pd.read_csv(GPS_FILE, encoding="utf-8-sig", dtype=str)
    start = pd.to_datetime(df["start_time_session"], utc=True, errors="coerce")
    dur = _iso_seconds(df["acct_session_time"])
    down = pd.to_numeric(df["donnees_recues_en_go"], errors="coerce") * 1e9
    up = pd.to_numeric(df["donnees_envoyees_en_go"], errors="coerce") * 1e9
    keys = dict(site=df["hotspot_name"].fillna("(none)").str.strip(),
                venue=df["type_site"].fillna("(none)").str.strip(),
                commune=df["commune"].fillna("(none)").str.strip(),
                perimetre=df["perimetre"].fillna("(none)").str.strip())
    return _frame(start, dur, down, up, keys)


@functools.lru_cache(maxsize=None)
def _read_mesa():
    df = pd.read_csv(MESA_FILE, dtype=str).drop_duplicates()
    df = df[df["ssid"].str.strip() == MESA_PUBLIC_SSID]
    local = pd.to_datetime(df["starttime"], errors="coerce")
    start = (local + pd.Timedelta(hours=MESA_UTC_OFFSET_H)).dt.tz_localize("UTC")
    dur = pd.to_numeric(df["session_duration"], errors="coerce")
    down = pd.to_numeric(df["bytes_to_user"], errors="coerce")
    up = pd.to_numeric(df["bytes_from_user"], errors="coerce")
    ap = df["ap_name"].fillna("(none)").str.strip()
    keys = dict(site=ap.str.split("-").str[0], ap=ap, ssid=df["ssid"].str.strip())
    return _frame(start.reset_index(drop=True), dur.reset_index(drop=True), down.reset_index(drop=True),
                  up.reset_index(drop=True), {k: v.reset_index(drop=True) for k, v in keys.items()})


@functools.lru_cache(maxsize=None)
def all_sessions(source):
    """All valid sessions of a source (before the unit choice), with the candidate-unit columns."""
    if source == "gps":
        return _read_gps().copy()
    if source == "mesa":
        return _read_mesa().copy()
    raise ValueError(f"unknown source {source!r}")


def _timeline(df):
    """Epoch start and end (whole seconds), the first midnight and the number of days covering the sessions."""
    st = _epoch(df["start"]).to_numpy(np.int64)
    en = st + np.rint(df["duration"].to_numpy(float)).astype(np.int64)
    t0 = int((st.min() // DAY) * DAY)
    n_days = int(np.ceil((en.max() - t0) / DAY))
    return st, en, t0, n_days


def _peak_mean_conc(st, en, t0, n_days, T=WIN_T, n=N_WIN):
    """Mean of the n highest daily peaks of T-second mean concurrency (minute-aligned starts inside each day).

    st, en: epoch seconds of the sessions; t0: first midnight of the timeline; n_days: days in the timeline.
    Returns the score and the best window mean concurrency of every day.
    """
    L = n_days * DAY
    lo = np.clip(st - t0, 0, L)
    hi = np.clip(en - t0, 0, L)
    keep = hi > lo
    diff = (np.bincount(lo[keep], minlength=L + 1)[:L + 1]
            - np.bincount(hi[keep], minlength=L + 1)[:L + 1])
    occ = np.cumsum(diff)[:L]
    P = np.concatenate([[0], np.cumsum(occ)])
    offs = np.arange(0, DAY - T + 1, 60)
    W = (np.arange(n_days) * DAY)[:, None] + offs[None, :]
    best = (P[W + T] - P[W]).max(axis=1) / T
    return float(np.sort(best)[::-1][:min(n, n_days)].mean()), best


def _group_scores(df, col, st, en, t0, n_days):
    """Score and session count of every value of a candidate column."""
    out = {}
    for val, idx in df.groupby(col, sort=True).indices.items():
        out[val] = (_peak_mean_conc(st[idx], en[idx], t0, n_days)[0], int(len(idx)))
    return out


def _ranked(scores):
    return sorted(scores.items(), key=lambda kv: (-kv[1][0], str(kv[0])))


@functools.lru_cache(maxsize=None)
def unit_choice(source):
    """The shared-link unit of a source and the statistics behind the choice (deterministic).

    Returns a dict with dim, col, value, label, score (mean concurrency over the six busiest two-hour windows),
    n_sessions, n_units (per candidate dimension), top (the three best units per dimension), reached
    (score >= UNIT_MIN), aggregated (True when a natural grouping was used).
    """
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}")
    df = all_sessions(source)
    st, en, t0, n_days = _timeline(df)
    tables, cands = [], []
    for order, (dim, col) in enumerate(PER_UNIT_DIMS[source]):
        sc = _group_scores(df, col, st, en, t0, n_days)
        tables.append(dict(dim=dim, n_units=len(sc), top=[(v, s, n) for v, (s, n) in _ranked(sc)[:3]]))
        cands += [(s, order, str(v), dim, col, v, n) for v, (s, n) in sc.items()]
    best = sorted(cands, key=lambda c: (-c[0], c[1], c[2]))[0]
    if best[0] >= UNIT_MIN:
        score, _, _, dim, col, value, n = best
        aggregated = False
    else:
        for dim, col in AGGREGATE_DIMS[source]:
            sc = _group_scores(df, col, st, en, t0, n_days)
            tables.append(dict(dim=dim, n_units=len(sc), top=[(v, s, n) for v, (s, n) in _ranked(sc)[:3]]))
            top_v, (top_s, top_n) = _ranked(sc)[0]
            if top_s >= UNIT_MIN:
                score, dim, col, value, n, aggregated = top_s, dim, col, top_v, top_n, True
                break
        else:
            score = _peak_mean_conc(st, en, t0, n_days)[0]
            dim, col, value, n, aggregated = "all", None, "all", int(len(df)), True
    label = "all" if dim == "all" else f"{dim}={value}"
    return dict(source=source, dim=dim, col=col, value=str(value), label=label, score=float(score),
                n_sessions=int(n), n_units=tables, reached=bool(score >= UNIT_MIN),
                aggregated=aggregated)


def load_sessions(source):
    """Sessions of the chosen unit of a source as a DataFrame with columns start (UTC timestamp),
    duration (s, >= 5), bytes_down, bytes_up (both bytes) and unit (label of the chosen unit)."""
    ch = unit_choice(source)
    df = all_sessions(source)
    if ch["col"] is not None:
        df = df[df[ch["col"]].astype(str) == ch["value"]]
    out = df[["start", "duration", "bytes_down", "bytes_up"]].reset_index(drop=True).copy()
    out["unit"] = ch["label"]
    return out


def _classify(df):
    """Service class of sessions from the logged traffic. packetsin is absent in these logs (NaN), so the
    gaming rule cannot fire and only the video rule applies."""
    return classify_sessions(pd.DataFrame({
        "duration": df["duration"].to_numpy(float),
        "bytesin": df["bytes_down"].to_numpy(float),
        "bytesout": df["bytes_up"].to_numpy(float),
        "packetsin": np.full(len(df), np.nan)}))


@functools.lru_cache(maxsize=None)
def _window_list2(source, n_days, T):
    if not 0 < T <= DAY:
        raise ValueError("T must lie in (0, 86400]")
    s = load_sessions(source)
    st = _epoch(s["start"]).to_numpy(np.int64)
    en = st + np.rint(s["duration"].to_numpy(float)).astype(np.int64)
    day_id = st // DAY
    counts = pd.Series(day_id).value_counts()
    ranked = sorted(counts.index, key=lambda d: (-int(counts[d]), d))
    chosen = sorted(int(d) for d in ranked[:n_days])
    out = []
    for d in chosen:
        day0 = d * DAY
        lo = np.clip(st - day0, 0, DAY)
        hi = np.clip(en - day0, 0, DAY)
        keep = hi > lo
        diff = (np.bincount(lo[keep], minlength=DAY + 1)[:DAY + 1]
                - np.bincount(hi[keep], minlength=DAY + 1)[:DAY + 1])
        occ = np.cumsum(diff)[:DAY]
        P = np.concatenate([[0], np.cumsum(occ)])
        W = np.arange(0, DAY - T + 1, 60)
        best = int(W[int(np.argmax(P[W + T] - P[W]))])
        out.append((pd.Timestamp(day0, unit="s", tz="UTC").date(), pd.Timestamp(day0 + best, unit="s", tz="UTC")))
    return tuple(out)


def pick_windows2(source, n=N_WIN, T=WIN_T):
    """The n calendar days (UTC) of the chosen unit with the most session starts, in date order.

    For each day, the T-second window (minute-aligned start inside the day) with the highest mean number of
    concurrent sessions of the unit. Returns a list of (date, window_start) with window_start a UTC timestamp.
    """
    return list(_window_list2(source, int(n), int(T)))


@functools.lru_cache(maxsize=None)
def _unit_arrays(source):
    s = load_sessions(source)
    st = _epoch(s["start"]).to_numpy(np.int64)
    dur = np.rint(s["duration"].to_numpy(float)).astype(np.int64)
    return st, dur, s["bytes_down"].to_numpy(float), s["bytes_up"].to_numpy(float), _classify(s)


@functools.lru_cache(maxsize=None)
def _capacity_files(cap):
    if cap == "ghent":
        return tuple(sorted(glob.glob(os.path.join(GHENT_DIR, "report_*.log"))))
    if cap == "raca":
        return tuple(sorted(glob.glob(os.path.join(RACA_DIR, "*", "*.csv"))))
    raise ValueError(f"unknown capacity source {cap!r}")


def _ghent_rates(path):
    """Throughput of each valid line of one Ghent log (Mbit/s), in file order."""
    rates = []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                nbytes, ms = float(parts[4]), float(parts[5])
            except ValueError:
                continue
            if ms <= 0:
                continue
            rates.append(nbytes * 8.0 / ms / 1000.0)
    return np.asarray(rates, float)


def _raca_rates(path):
    """DL_bitrate of one RACA trace in Mbit/s (the column is kbit/s), rows with a missing value dropped."""
    x = pd.to_numeric(pd.read_csv(path, usecols=["DL_bitrate"])["DL_bitrate"], errors="coerce").to_numpy(float)
    return x[np.isfinite(x)] / 1000.0


@functools.lru_cache(maxsize=None)
def _pool(cap):
    """Per-file capacity arrays (Mbit/s) of a capacity source, in sorted file order."""
    read = _ghent_rates if cap == "ghent" else _raca_rates
    files = _capacity_files(cap)
    if not files:
        raise FileNotFoundError(f"no {cap} capacity files found")
    return tuple(read(f) for f in files)


def capacity_series2(cap, T, seed):
    """Raw capacity series (Mbit/s) of length T: the files of a capacity source concatenated in the order of a
    permutation drawn with numpy Generator(seed). Unscaled."""
    pool = _pool(cap)
    order = np.random.default_rng(seed).permutation(len(pool))
    chunks, n = [], 0
    for j in order:
        r = pool[j]
        chunks.append(r)
        n += r.size
        if n >= T:
            break
    if n < T:
        raise ValueError(f"{cap} holds {n} slots, fewer than T={T}")
    return np.concatenate(chunks)[:T].astype(float)


def capacity_stats(cap):
    """Mean (Mbit/s), coefficient of variation, share of zero slots and size of a capacity source (all files)."""
    x = np.concatenate(_pool(cap))
    mean = float(x.mean())
    return dict(capacity=cap, label=CAP_LABEL[cap], n_files=len(_pool(cap)), n_slots=int(x.size), mean=mean,
                cv=float(x.std() / mean), zero_share=float(np.mean(x == 0)))


def video_share_file(source):
    """Shares of video-like and gaming-like sessions over all valid sessions of the file (all units)."""
    cls = _classify(all_sessions(source))
    n = cls.size
    return dict(n_sessions=int(n), share_video=float(np.mean(cls == 1)) if n else float("nan"),
                share_gaming=float(np.mean(cls == 2)) if n else float("nan"))


def make_trace2(source, k, T=WIN_T, load=1.0, classes="log", tiers="estimated"):
    """Trace of the k-th day window of a source (k indexes pick_windows2(source, 6, T)), built as
    experiments.data_real.make_real_trace.

    Devices are the unit's sessions overlapping the window (t_arr = max(0, start - w0), t_dep = min(T, end - w0),
    end = start + duration), sessions with t_dep - t_arr < 5 dropped, in order of start. Random draws come from
    numpy Generator(6000 + 100 * source_index + k), in this order per device:
      1. tier: with tiers="estimated", drawn with TIER_P_EST; with "random", with the hotspot split; with "free",
         no draw and tier F_TIER;
      2. class: classes must be "log" (no draw): the video rule of classify_sessions on the session.
    Elastic devices: cap clip(rbar / pi_on, 0.05, 30), rbar = 8 * bytes_down / duration / 1e6, and the on/off
    sequence of length L. RT devices: always on, cap RT_ELL.
    Capacity: the raw series of the paired capacity source with seed 7000 + k, scaled so that
    mean(C) = load * Dbar, floored at C_FLOOR.

    Returns (trace, meta). meta has the fields of make_real_trace with site replaced by source, plus unit and
    capacity_source.
    """
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}")
    if classes != "log":
        raise ValueError("classes must be 'log': these logs carry no packet counts, so no class can be drawn")
    if tiers not in TIER_MODES:
        raise ValueError(f"tiers must be one of {TIER_MODES}, not {tiers!r}")
    cap = PAIRS[source]
    st, dur, bd, bu, cls_all = _unit_arrays(source)
    day, w0 = pick_windows2(source, N_WIN, T)[k]
    w0_s = int(_epoch(w0))
    a = st - w0_s
    b = a + dur
    t_arr = np.maximum(a, 0)
    t_dep = np.minimum(b, T)
    sel = np.flatnonzero(t_dep - t_arr >= MIN_STAY)
    if sel.size == 0:
        raise ValueError(f"no sessions in window {source} k={k}")

    rng = np.random.default_rng(6000 + 100 * SOURCE_INDEX[source] + k)
    devices = []
    for j in sel:
        if tiers == "random":
            tier = int(rng.choice(3, p=TIER_P))
        elif tiers == "estimated":
            tier = int(rng.choice(3, p=TIER_P_EST))
        else:
            tier = F_TIER
        cls = int(cls_all[j])
        L = int(t_dep[j] - t_arr[j])
        if cls == 0:
            rbar = 8.0 * bd[j] / dur[j] / 1e6
            ell = float(np.clip(rbar / PI_ON, *ELL_EL_CLIP))
            on = _onoff(rng, L, P_ON_OFF, P_OFF_ON)
        else:
            ell = RT_ELL
            on = np.ones(L, dtype=bool)
        devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=int(t_arr[j]),
                            t_dep=int(t_dep[j]), ell=ell, on=on))

    Ls = np.array([d["t_dep"] - d["t_arr"] for d in devices], float)
    nominal = np.array([d["ell"] * PI_ON if d["cls"] == 0 else (NOMINAL_VIDEO if d["cls"] == 1 else NOMINAL_GAMING)
                        for d in devices])
    Dbar = float((nominal * Ls).sum() / T)

    raw = capacity_series2(cap, T, CAP_SEED + k)
    C = np.maximum(raw * (load * Dbar / raw.mean()), C_FLOOR)

    conc = np.zeros(T + 1, np.int64)
    for d in devices:
        conc[d["t_arr"]] += 1
        conc[d["t_dep"]] -= 1
    conc = np.cumsum(conc)[:T]
    el_ell = np.array([d["ell"] for d in devices if d["cls"] == 0], float)
    cls_arr = np.array([d["cls"] for d in devices])
    n_dev = len(devices)
    n_video = int(np.sum(cls_arr == 1))
    n_gaming = int(np.sum(cls_arr == 2))
    pct = lambda q: float(np.percentile(el_ell, q)) if el_ell.size else float("nan")
    ch = unit_choice(source)
    meta = dict(
        source=source, unit=ch["label"], capacity_source=cap, k=int(k), load=float(load), seed=int(CAP_SEED + k),
        T=int(T), date=str(day), window_start=w0.isoformat(),
        n_devices=n_dev,
        n_elastic=int(np.sum(cls_arr == 0)), n_video=n_video, n_gaming=n_gaming,
        share_video=n_video / n_dev, share_gaming=n_gaming / n_dev,
        classes=classes, tiers=tiers, rule=dict(DEFAULT_RULE),
        mean_conc=float(Ls.sum() / T), max_conc=int(conc.max()),
        median_stay_s=float(np.median(Ls)),
        ell_el_q50=pct(50), ell_el_q90=pct(90), ell_el_q99=pct(99),
        Dbar=Dbar, C_mean=float(C.mean()), C_cv=float(C.std() / C.mean()),
        frac_C_low=float(np.mean(C < 0.3 * C.mean())),
    )
    trace = dict(T=T, C=C, devices=devices, scenario=f"real2:{source}")
    return trace, meta


@functools.lru_cache(maxsize=None)
def source_summary(source):
    """Unit, period, file-level class shares and the paired capacity statistics of a source."""
    ch = unit_choice(source)
    df = all_sessions(source)
    st = _epoch(df["start"]).to_numpy(np.int64)
    first = pd.Timestamp(int(st.min()), unit="s", tz="UTC").strftime("%Y-%m-%d")
    last = pd.Timestamp(int(st.max()), unit="s", tz="UTC").strftime("%Y-%m-%d")
    unit_n = int(load_sessions(source).shape[0])
    vs = video_share_file(source)
    return dict(source=source, label=SOURCE_LABEL[source], unit=ch["label"], unit_score=ch["score"],
                unit_sessions=unit_n, reached_target=ch["reached"], aggregated=ch["aggregated"],
                period=f"{first} to {last}", n_sessions_file=vs["n_sessions"],
                share_video_file=vs["share_video"], share_gaming_file=vs["share_gaming"],
                capacity=capacity_stats(PAIRS[source]))


def _print_unit_choice(source):
    ch = unit_choice(source)
    print(f"\n[{source}] unit choice: mean concurrency over the six busiest two-hour windows (one per busiest day)")
    for t in ch["n_units"]:
        print(f"  candidate {t['dim']:9s} units={t['n_units']:4d}  top: " + ", ".join(
            f"{v}={s:.2f} (n={n})" for v, s, n in t["top"]))
    print(f"  chosen: {ch['label']}  score={ch['score']:.2f}  sessions={ch['n_sessions']}  "
          f"reaches {UNIT_MIN:.0f}: {ch['reached']}  aggregated: {ch['aggregated']}")


def _print_windows(source, T=WIN_T):
    s = load_sessions(source)
    print(f"[{source}] sessions loaded (valid, unit {unit_choice(source)['label']}): {len(s)} "
          f"of {len(all_sessions(source))} valid in the file")
    print(f"{'k':>2s}{'date':>12s}{'devices':>9s}{'video%':>8s}{'mean conc':>11s}{'max conc':>10s}"
          f"{'med stay':>10s}{'cap50':>8s}{'cap90':>8s}{'Dbar':>8s}{'CV C':>7s}")
    for k in range(N_WIN):
        _, m = make_trace2(source, k, T)
        print(f"{k:2d}{m['date']:>12s}{m['n_devices']:9d}{100 * m['share_video']:8.1f}{m['mean_conc']:11.1f}"
              f"{m['max_conc']:10d}{m['median_stay_s']:10.0f}{m['ell_el_q50']:8.2f}{m['ell_el_q90']:8.2f}"
              f"{m['Dbar']:8.2f}{m['C_cv']:7.3f}")


def main():
    for source in SOURCES:
        _print_unit_choice(source)
        _print_windows(source)
        vs = video_share_file(source)
        print(f"[{source}] video-like share over the whole file: {100 * vs['share_video']:.2f}% "
              f"of {vs['n_sessions']} sessions; gaming-like: {100 * vs['share_gaming']:.2f}%")
        up = all_sessions(source)
        print(f"[{source}] total downlink {up['bytes_down'].sum() / 1e9:.1f} GB, total uplink "
              f"{up['bytes_up'].sum() / 1e9:.1f} GB, downlink/uplink {up['bytes_down'].sum() / up['bytes_up'].sum():.3f}")
    print("\ncapacity sources (raw, Mbit/s, all files)")
    for cap in ("ghent", "raca"):
        c = capacity_stats(cap)
        print(f"  {c['label']:16s} files={c['n_files']:4d} slots={c['n_slots']:7d} mean={c['mean']:8.2f} "
              f"CV={c['cv']:.3f} zero share={100 * c['zero_share']:.2f}%")


if __name__ == "__main__":
    main()
