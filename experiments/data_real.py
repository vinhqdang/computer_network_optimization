"""Trace-driven scenario built from two public datasets.

(A) Paris Wi-Fi session logs (City of Paris open data, ODbL) for two hotspots, PW0127 and PW0232.
    Each row is one session: start time (UTC, minute resolution), duration (s), bytes downloaded.
(B) HSDPA 3G downlink logs from commuting routes in Oslo (Riiser et al., MMSys 2013). Each log line is
    one slot whose throughput is bytes * 8 / ms / 1000 Mbit/s.

The data carry no device class or tier. Tier and class are therefore drawn at random, with the
probabilities of the synthetic hotspot (repay.sim.HOTSPOT_DEFAULTS), and an elastic session's demand cap is
derived from its observed mean rate. Draws are made in a fixed documented order (see make_real_trace).

Run as: python -m experiments.data_real   (downloads missing raw files, then prints the day windows of k = 0)
"""
import functools
import os
import re
import urllib.request

import numpy as np
import pandas as pd

from experiments.common import ROOT
from repay.sim import HOTSPOT_DEFAULTS, _onoff

RAW = os.path.join(ROOT, "data", "raw")
PARIS_DIR = os.path.join(RAW, "paris")
HSDPA_DIR = os.path.join(RAW, "hsdpa")
SITES = ("PW0127", "PW0232")
ROUTES = (
    "bus.ljansbakken-oslo", "metro.kalbakken-jernbanetorget", "tram.ljabru-jernbanetorget",
    "tram.jernbanetorget-ljabru", "ferry.nesoddtangen-oslo", "train.oslo-vestby", "train.vestby-oslo",
)
PARIS_URL = ("https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
             "paris-wi-fi-utilisation-des-hotspots-paris-wi-fi/exports/csv"
             "?select=code_site,datetime,endtime_or_dash,duration,device_portal_format,bytesin,bytesout"
             "&where=code_site%3D%22{site}%22&delimiter=%3B")
HSDPA_URL = "https://skulddata.cs.umass.edu/traces/mmsys/2013/pathbandwidth/{route}/"
START_DATE = "2025-01-01"
N_DAYS = 6
MIN_STAY = 5
DAY = 86400
TIER_P = HOTSPOT_DEFAULTS["tier_p"]
CLS_P = HOTSPOT_DEFAULTS["cls_p"]
ELL_LO, ELL_HI = HOTSPOT_DEFAULTS["ell_lo"], HOTSPOT_DEFAULTS["ell_hi"]
P_ON_OFF, P_OFF_ON = HOTSPOT_DEFAULTS["p_on_off"], HOTSPOT_DEFAULTS["p_off_on"]
PI_ON = P_OFF_ON / (P_ON_OFF + P_OFF_ON)
ELL_EL_CLIP = (0.05, 30.0)
NOMINAL_VIDEO = 1.5   # mean demand of a video device (Mbit/s), as in the design notes
NOMINAL_GAMING = 0.2  # demand of a gaming device (Mbit/s)
C_FLOOR = 0.01


def _fetch(url, path):
    """Download url to path through a temporary file, so that an interrupted fetch leaves no partial file."""
    req = urllib.request.Request(url, headers={"User-Agent": "trace-download"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def download():
    """Fetch the raw files that are missing; existing files are never re-downloaded."""
    os.makedirs(PARIS_DIR, exist_ok=True)
    for site in SITES:
        path = os.path.join(PARIS_DIR, f"{site}.csv")
        if not os.path.exists(path):
            print("fetching", path, flush=True)
            _fetch(PARIS_URL.format(site=site), path)
    for route in ROUTES:
        d = os.path.join(HSDPA_DIR, route)
        os.makedirs(d, exist_ok=True)
        url = HSDPA_URL.format(route=route)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "trace-download"}),
                                        timeout=120) as r:
                listing = r.read().decode("utf-8", "replace")
        except OSError as exc:
            if any(n.endswith(".log") for n in os.listdir(d)):
                print(f"listing of {route} unavailable ({exc}); keeping local files", flush=True)
                continue
            raise
        for name in sorted(set(re.findall(r'href="([^"/?]+\.log)"', listing))):
            path = os.path.join(d, name)
            if not os.path.exists(path):
                print("fetching", path, flush=True)
                _fetch(url + name, path)


@functools.lru_cache(maxsize=None)
def _sessions(site):
    """Valid sessions of a site, cached per process (callers receive copies)."""
    if site not in SITES:
        raise ValueError(f"unknown site {site!r}")
    df = pd.read_csv(os.path.join(PARIS_DIR, f"{site}.csv"), sep=";", encoding="utf-8-sig", dtype=str)
    if "code_site" in df.columns:
        df = df[df["code_site"].str.strip() == site]
    start = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    dur = pd.to_numeric(df["duration"], errors="coerce")
    byt = pd.to_numeric(df["bytesin"], errors="coerce")
    ok = (start.notna() & np.isfinite(dur) & np.isfinite(byt)
          & (dur >= MIN_STAY) & (byt >= 0)).to_numpy()
    out = pd.DataFrame({"start": start[ok].to_numpy(), "duration": dur[ok].to_numpy(float),
                        "bytesin": byt[ok].to_numpy(float)})
    out = out.sort_values(["start", "duration", "bytesin"], kind="mergesort").reset_index(drop=True)
    return out


def load_sessions(site):
    """Sessions of a site as a DataFrame with columns start (UTC timestamp), duration (s, >= 5), bytesin.

    Rows with a missing or unparsable start, duration or byte count, a negative byte count or a
    duration below 5 s are dropped.
    """
    return _sessions(site).copy()


@functools.lru_cache(maxsize=None)
def _arrays(site):
    """Session start (epoch seconds), duration (whole seconds) and bytesin, as arrays."""
    s = _sessions(site)
    st = s["start"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy()
    st_s = st.astype("datetime64[s]").astype(np.int64)
    return st_s, np.rint(s["duration"].to_numpy(float)).astype(np.int64), s["bytesin"].to_numpy(float)


@functools.lru_cache(maxsize=None)
def _window_list(site, n_days, T):
    if not 0 < T <= DAY:
        raise ValueError("T must lie in (0, 86400]")
    st_s, dur, _ = _arrays(site)
    en_s = st_s + dur
    days = pd.to_datetime(st_s, unit="s").floor("D")
    sel = days >= pd.Timestamp(START_DATE)
    counts = pd.Series(days[sel]).value_counts()
    ranked = sorted(counts.index, key=lambda d: (-int(counts[d]), d))
    chosen = sorted(ranked[:n_days])
    out = []
    for day in chosen:
        day0 = int(day.to_datetime64().astype("datetime64[s]").astype(np.int64))
        lo = np.clip(st_s - day0, 0, DAY)
        hi = np.clip(en_s - day0, 0, DAY)
        keep = hi > lo
        diff = np.zeros(DAY + 1, np.int64)
        np.add.at(diff, lo[keep], 1)
        np.add.at(diff, hi[keep], -1)
        occ = np.cumsum(diff)[:DAY]              # sessions active in each whole second of the day
        P = np.concatenate([[0], np.cumsum(occ)])
        W = np.arange(0, DAY - T + 1, 60)         # minute-aligned window starts
        tot = P[W + T] - P[W]
        best = int(W[int(np.argmax(tot))])       # earliest window among ties
        out.append((day.date(), pd.Timestamp(day0 + best, unit="s", tz="UTC")))
    return tuple(out)


def pick_windows(site, n_days, T):
    """The n_days calendar days (UTC, from 2025-01-01) with the most sessions, in date order.

    For each day, the T-second window (minute-aligned start, inside the day) with the highest mean number
    of concurrent sessions. Returns a list of (date, window_start) with window_start a UTC timestamp.
    """
    return list(_window_list(site, int(n_days), int(T)))


@functools.lru_cache(maxsize=None)
def _log_rates(path):
    """Throughput of each valid line of one HSDPA log (Mbit/s), in file order."""
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


def _hsdpa_files():
    """All HSDPA log files over all routes, in sorted order."""
    files = []
    for route in ROUTES:
        d = os.path.join(HSDPA_DIR, route)
        if os.path.isdir(d):
            files += [os.path.join(d, n) for n in sorted(os.listdir(d)) if n.endswith(".log")]
    return files


def capacity_series(T, seed):
    """Raw capacity series (Mbit/s) of length T: HSDPA logs concatenated in a random file order.

    The order is a permutation of all log files drawn with numpy Generator(seed). Each log line is one slot.
    Lines with ms <= 0 are skipped. The series is returned unscaled.
    """
    files = _hsdpa_files()
    if not files:
        raise FileNotFoundError(f"no HSDPA logs under {HSDPA_DIR}")
    order = np.random.default_rng(seed).permutation(len(files))
    chunks, n = [], 0
    for j in order:
        r = _log_rates(files[j])
        chunks.append(r)
        n += r.size
        if n >= T:
            break
    if n < T:
        raise ValueError(f"HSDPA logs hold {n} slots, fewer than T={T}")
    return np.concatenate(chunks)[:T].astype(float)


def make_real_trace(site, k, T, load=1.0, seed=None):
    """Trace of the k-th day window of a site (k indexes pick_windows(site, 6, T)).

    Devices are the sessions overlapping the window: t_arr = max(0, start - w0), t_dep = min(T, end - w0),
    end = start + duration; sessions with t_dep - t_arr < 5 are dropped. Devices are processed in order of
    session start. For each device, random draws come from numpy Generator(5000 + 100 * site_index + k) in
    this fixed order:
      1. tier, with probabilities (0.6, 0.25, 0.15);
      2. class, with probabilities (0.65, 0.25, 0.10);
      3. elastic: the on/off sequence of length t_dep - t_arr (repay.sim._onoff with p_on_off, p_off_on);
         RT (video or gaming): demand cap ell uniform on [ell_lo, ell_hi] (hotspot range), always on.
    The data have no class or tier, so these two attributes are random by construction. An elastic
    device's demand cap is clip(rbar / pi_on, 0.05, 30), where rbar = 8 * bytesin / duration / 1e6 is the
    session's observed mean downlink rate (whole session) and pi_on = p_off_on / (p_on_off + p_off_on).

    Capacity is C = raw series from capacity_series(T, seed), seed defaulting to 7000 + k, scaled by a constant
    so that mean(C) = load * Dbar, then floored at 0.01 Mbit/s. Dbar is the time average over the window of
    nominal demand: elastic ell * pi_on, video 1.5, gaming 0.2 Mbit/s per present device.

    Returns (trace, meta). trace is a dict with T, C, devices and scenario, as repay.sim.make_trace.
    """
    site_index = SITES.index(site)
    if seed is None:
        seed = 7000 + k
    day, w0 = pick_windows(site, N_DAYS, T)[k]
    st_s, dur, byt = _arrays(site)
    w0_s = int(w0.value // 10 ** 9)
    a = st_s - w0_s
    b = a + dur
    t_arr = np.maximum(a, 0)
    t_dep = np.minimum(b, T)
    sel = np.flatnonzero(t_dep - t_arr >= MIN_STAY)
    if sel.size == 0:
        raise ValueError(f"no sessions in window {site} k={k}")

    rng = np.random.default_rng(5000 + 100 * site_index + k)
    devices = []
    for j in sel:
        tier = int(rng.choice(3, p=TIER_P))
        cls = int(rng.choice(3, p=CLS_P))
        L = int(t_dep[j] - t_arr[j])
        if cls == 0:
            rbar = 8.0 * byt[j] / dur[j] / 1e6
            ell = float(np.clip(rbar / PI_ON, *ELL_EL_CLIP))
            on = _onoff(rng, L, P_ON_OFF, P_OFF_ON)
        else:
            ell = float(rng.uniform(ELL_LO, ELL_HI))
            on = np.ones(L, dtype=bool)
        devices.append(dict(id=len(devices), tier=tier, cls=cls, t_arr=int(t_arr[j]),
                            t_dep=int(t_dep[j]), ell=ell, on=on))

    Ls = np.array([d["t_dep"] - d["t_arr"] for d in devices], float)
    nominal = np.array([d["ell"] * PI_ON if d["cls"] == 0 else (NOMINAL_VIDEO if d["cls"] == 1 else NOMINAL_GAMING)
                        for d in devices])
    Dbar = float((nominal * Ls).sum() / T)

    raw = capacity_series(T, seed)
    C = np.maximum(raw * (load * Dbar / raw.mean()), C_FLOOR)

    conc = np.zeros(T + 1, np.int64)
    for d in devices:
        conc[d["t_arr"]] += 1
        conc[d["t_dep"]] -= 1
    conc = np.cumsum(conc)[:T]
    el_ell = np.array([d["ell"] for d in devices if d["cls"] == 0], float)
    cls_arr = np.array([d["cls"] for d in devices])
    meta = dict(
        site=site, k=int(k), load=float(load), seed=int(seed), T=int(T),
        date=str(day), window_start=w0.isoformat(),
        n_devices=len(devices),
        n_elastic=int(np.sum(cls_arr == 0)), n_video=int(np.sum(cls_arr == 1)),
        n_gaming=int(np.sum(cls_arr == 2)),
        mean_conc=float(Ls.sum() / T), max_conc=int(conc.max()),
        median_stay_s=float(np.median(Ls)),
        ell_el_q50=float(np.percentile(el_ell, 50)), ell_el_q90=float(np.percentile(el_ell, 90)),
        ell_el_q99=float(np.percentile(el_ell, 99)),
        Dbar=Dbar, C_mean=float(C.mean()), C_cv=float(C.std() / C.mean()),
        frac_C_low=float(np.mean(C < 0.3 * C.mean())),
    )
    trace = dict(T=T, C=C, devices=devices, scenario=f"real:{site}")
    return trace, meta


def main():
    download()
    for site in SITES:
        for k, (day, w0) in enumerate(pick_windows(site, N_DAYS, 7200)):
            print(f"{site} k={k} date={day} window_start={w0.isoformat()}")
    tr, meta = make_real_trace("PW0127", 0, 7200)
    print("PW0127 k=0 meta:", meta)


if __name__ == "__main__":
    main()
