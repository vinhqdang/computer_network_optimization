"""Trace-driven scenario built from two public datasets.

(A) Paris Wi-Fi session logs (City of Paris open data, ODbL) for two hotspots, PW0127 and PW0232.
    Each row is one session: start time (UTC, minute resolution), duration (s), bytes downloaded and
    uploaded by the device, and packets received and sent by the device.
(B) HSDPA 3G downlink logs from commuting routes in Oslo (Riiser et al., MMSys 2013). Each log line is
    one slot whose throughput is bytes * 8 / ms / 1000 Mbit/s.

The session logs carry no service class or tier. With classes="log" the class of a device is the class
that classify_sessions assigns to its session from the session's own logged traffic; with classes="random"
it is drawn with the probabilities of the synthetic hotspot. Tiers are all free (tiers="free") or drawn at
random (tiers="random" with the synthetic split, tiers="estimated" with TIER_P_EST). Draws are made in a fixed documented order (see make_real_trace).

classify_sessions is a heuristic on session averages (two-way traffic at call-like rates is video, two-way
traffic at low rates with small downlink packets is gaming). It is not a validated classifier.

Run as: python -m experiments.data_real   (downloads missing raw files, prints class shares and the day windows)
"""
import functools
import os
import re
import urllib.request

import numpy as np
import pandas as pd

from experiments.common import ROOT
from repay.params import F_TIER
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
             "?select=code_site,datetime,duration,device_portal_format,device_constructor_name,"
             "device_operating_system_name_version,userlanguage,bytesin,bytesout,packetsin,packetsout"
             "&where=code_site%3D%22{site}%22&delimiter=%3B")
HSDPA_URL = "https://skulddata.cs.umass.edu/traces/mmsys/2013/pathbandwidth/{route}/"
START_DATE = "2025-01-01"
SESSION_SINCE = "2025-01-01"
N_DAYS = 6
MIN_STAY = 5
DAY = 86400
TIER_P = HOTSPOT_DEFAULTS["tier_p"]
CLS_P = HOTSPOT_DEFAULTS["cls_p"]
ELL_LO, ELL_HI = HOTSPOT_DEFAULTS["ell_lo"], HOTSPOT_DEFAULTS["ell_hi"]
P_ON_OFF, P_OFF_ON = HOTSPOT_DEFAULTS["p_on_off"], HOTSPOT_DEFAULTS["p_off_on"]
PI_ON = P_OFF_ON / (P_ON_OFF + P_OFF_ON)
ELL_EL_CLIP = (0.05, 30.0)
RT_ELL = 30.0         # demand cap of RT devices in classes="log" (irrelevant: RT flows are capped at rmax)
NOMINAL_VIDEO = 1.5   # mean demand of a video device (Mbit/s), as in the design notes
NOMINAL_GAMING = 0.2  # demand of a gaming device (Mbit/s)
C_FLOOR = 0.01
CLASS_MODES = ("log", "random")
# Estimated tier split: 11.6% of users pay (connectivity take rate, Gogo Inc. Form 10-K for 2018); of those,
# 8% are pay-as-you-go (share of prepaid users, ARCEP mobile observatory, Q3 2026) and 92% subscribers.
TIER_P_EST = (0.884, 0.107, 0.009)
TIER_MODES = ("free", "random", "estimated")

DEFAULT_RULE = dict(sym_lo=1 / 3, sym_hi=3.0, up_min=0.1, game_up_min=0.01, game_pkt_max=700.0)
STRICT_RULE = dict(sym_lo=0.5, sym_hi=2.0, up_min=0.2)
RULE_SETS = {"default": {}, "strict": STRICT_RULE}


def _paris_path(site):
    return os.path.join(PARIS_DIR, f"{site}_full.csv")


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
        path = _paris_path(site)
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


def _column(df, name):
    """A numeric column as a float array; NaN everywhere if the column is absent."""
    if name not in df.columns:
        return np.full(len(df), np.nan)
    return pd.to_numeric(df[name], errors="coerce").to_numpy(float)


@functools.lru_cache(maxsize=None)
def _sessions(site):
    """Valid sessions of a site, cached per process (callers receive copies).

    Columns: start, duration, bytesin, bytesout, packetsin. The last two are NaN where the file has no value.
    """
    if site not in SITES:
        raise ValueError(f"unknown site {site!r}")
    df = pd.read_csv(_paris_path(site), sep=";", encoding="utf-8-sig", dtype=str)
    if "code_site" in df.columns:
        df = df[df["code_site"].str.strip() == site]
    start = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    dur = pd.to_numeric(df["duration"], errors="coerce")
    byt = pd.to_numeric(df["bytesin"], errors="coerce")
    ok = (start.notna() & np.isfinite(dur) & np.isfinite(byt)
          & (dur >= MIN_STAY) & (byt >= 0)).to_numpy()
    out = pd.DataFrame({"start": start[ok].to_numpy(), "duration": dur[ok].to_numpy(float),
                        "bytesin": byt[ok].to_numpy(float),
                        "bytesout": _column(df, "bytesout")[ok],
                        "packetsin": _column(df, "packetsin")[ok]})
    out = out.sort_values(["start", "duration", "bytesin"], kind="mergesort").reset_index(drop=True)
    return out


def load_sessions(site):
    """Sessions of a site as a DataFrame with columns start (UTC timestamp), duration (s, >= 5), bytesin,
    bytesout and packetsin.

    Rows with a missing or unparsable start, duration or downlink byte count, a negative byte count or a
    duration below 5 s are dropped. Uplink bytes and packets may be missing (NaN).
    """
    return _sessions(site).copy()


def _features(df):
    """Session averages: rin, rout (Mbit/s, down and up to the device), sym = bytesout / bytesin,
    psin = bytesin / packetsin (mean downlink packet size, bytes)."""
    dur = np.asarray(df["duration"], float)
    bi = np.asarray(df["bytesin"], float)
    bo = np.asarray(df["bytesout"], float)
    pk = np.asarray(df["packetsin"], float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return dict(duration=dur, bytesin=bi, packetsin=pk,
                    rin=8.0 * bi / dur / 1e6, rout=8.0 * bo / dur / 1e6,
                    sym=bo / bi, psin=bi / pk)


def classify_sessions(df, sym_lo=1 / 3, sym_hi=3.0, up_min=0.1, game_up_min=0.01, game_pkt_max=700.0):
    """Service class of each session (0 elastic, 1 video, 2 gaming) from its session averages.

    df needs columns duration (s), bytesin, bytesout and packetsin. With rin = 8*bytesin/duration/1e6,
    rout = 8*bytesout/duration/1e6, sym = bytesout/bytesin and psin = bytesin/packetsin:
      video (1):   bytesin > 0, sym_lo <= sym <= sym_hi and rout >= up_min (sustained two-way call-like rates);
      gaming (2):  not video, bytesin > 0, packetsin > 0, sym_lo <= sym <= sym_hi, rout >= game_up_min
                   and psin < game_pkt_max (two-way, low rate, small downlink packets);
      elastic (0): everything else, including sessions with a missing or zero field.
    This is a heuristic on session averages, not a validated classifier: it has not been checked against
    labelled traffic, and the thresholds are chosen by hand (see the strict rule in STRICT_RULE).
    Returns an int64 array with one entry per row of df.
    """
    with np.errstate(invalid="ignore"):
        f = _features(df)
        base = (np.isfinite(f["duration"]) & (f["duration"] > 0)
                & np.isfinite(f["bytesin"]) & (f["bytesin"] > 0)
                & (f["sym"] >= sym_lo) & (f["sym"] <= sym_hi))
        video = base & (f["rout"] >= up_min)
        gaming = (base & ~video & (f["packetsin"] > 0) & (f["rout"] >= game_up_min)
                  & (f["psin"] < game_pkt_max))
    return np.where(video, 1, np.where(gaming, 2, 0)).astype(np.int64)


def _effective_rule(rule):
    """The rule actually applied: DEFAULT_RULE with the overrides in rule."""
    return {**DEFAULT_RULE, **(rule or {})}


def _rule_key(rule):
    """Hashable form of a rule override dict (validated against DEFAULT_RULE)."""
    rule = dict(rule or {})
    unknown = set(rule) - set(DEFAULT_RULE)
    if unknown:
        raise ValueError(f"unknown rule keys {sorted(unknown)}")
    return tuple(sorted(rule.items()))


@functools.lru_cache(maxsize=None)
def _session_classes(site, rule_key):
    """Class of every session of a site under the rule (aligned with _sessions(site))."""
    return classify_sessions(_sessions(site), **dict(rule_key))


@functools.lru_cache(maxsize=None)
def _arrays(site):
    """Session start (epoch seconds), duration (whole seconds) and bytesin, as arrays."""
    s = _sessions(site)
    st = s["start"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy()
    st_s = st.astype("datetime64[s]").astype(np.int64)
    return st_s, np.rint(s["duration"].to_numpy(float)).astype(np.int64), s["bytesin"].to_numpy(float)


def class_shares(site, since=SESSION_SINCE, **rule):
    """Shares of video and gaming sessions and medians of rin and rout per class.

    Sessions are those with duration >= 5 s starting on or after `since` (UTC date). rule holds
    classify_sessions keyword overrides. Returns a dict with n_sessions, share_video, share_gaming (fractions),
    and median_rin / median_rout (Mbit/s) keyed by 'elastic', 'video' and 'gaming' (NaN if a class is empty).
    """
    s = _sessions(site)
    keep = (s["start"] >= pd.Timestamp(since, tz="UTC")).to_numpy()
    cls = _session_classes(site, _rule_key(rule))[keep]
    f = _features(s)
    rin, rout = f["rin"][keep], f["rout"][keep]
    names = {0: "elastic", 1: "video", 2: "gaming"}
    med = lambda x: float(np.median(x)) if x.size else float("nan")
    n = int(keep.sum())
    return dict(
        site=site, since=since, rule=_effective_rule(rule), n_sessions=n,
        share_video=float(np.mean(cls == 1)) if n else float("nan"),
        share_gaming=float(np.mean(cls == 2)) if n else float("nan"),
        median_rin={names[c]: med(rin[cls == c]) for c in names},
        median_rout={names[c]: med(rout[cls == c]) for c in names},
    )


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


def make_real_trace(site, k, T, load=1.0, seed=None, classes="log", tiers="free", rule=None):
    """Trace of the k-th day window of a site (k indexes pick_windows(site, 6, T)).

    Devices are the sessions overlapping the window: t_arr = max(0, start - w0), t_dep = min(T, end - w0),
    end = start + duration; sessions with t_dep - t_arr < 5 are dropped. Devices are processed in order of
    session start. For each device, random draws come from numpy Generator(5000 + 100 * site_index + k) in
    this fixed order:
      1. tier: with tiers="random", drawn with probabilities (0.6, 0.25, 0.15); with tiers="free", no draw
         and tier 0 (free) for every device;
      2. class: with classes="random", drawn with probabilities (0.65, 0.25, 0.10); with classes="log", no
         draw and the class is classify_sessions(session) under rule (overrides of DEFAULT_RULE);
      3. elastic: the on/off sequence of length t_dep - t_arr (repay.sim._onoff with p_on_off, p_off_on);
         RT (video or gaming): with classes="random", demand cap ell uniform on [ell_lo, ell_hi] (always on);
         with classes="log", ell = RT_ELL = 30 and no draw (always on).
    An elastic device's demand cap is clip(rbar / pi_on, 0.05, 30), where rbar = 8 * bytesin / duration / 1e6 is
    the session's observed mean downlink rate (whole session) and pi_on = p_off_on / (p_on_off + p_off_on).
    With classes="random" and tiers="random" the draws are those of the earlier random-attribute version.

    Capacity is C = raw series from capacity_series(T, seed), seed defaulting to 7000 + k, scaled by a constant
    so that mean(C) = load * Dbar, then floored at 0.01 Mbit/s. Dbar is the time average over the window of
    nominal demand: elastic ell * pi_on, video 1.5, gaming 0.2 Mbit/s per present device.

    Returns (trace, meta). trace is a dict with T, C, devices and scenario, as repay.sim.make_trace.
    """
    if classes not in CLASS_MODES:
        raise ValueError(f"classes must be one of {CLASS_MODES}, not {classes!r}")
    if tiers not in TIER_MODES:
        raise ValueError(f"tiers must be one of {TIER_MODES}, not {tiers!r}")
    site_index = SITES.index(site)
    if seed is None:
        seed = 7000 + k
    rule_key = _rule_key(rule)
    day, w0 = pick_windows(site, N_DAYS, T)[k]
    st_s, dur, byt = _arrays(site)
    cls_all = _session_classes(site, rule_key)
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
        if tiers == "random":
            tier = int(rng.choice(3, p=TIER_P))
        elif tiers == "estimated":
            tier = int(rng.choice(3, p=TIER_P_EST))
        else:
            tier = F_TIER
        if classes == "random":
            cls = int(rng.choice(3, p=CLS_P))
        else:
            cls = int(cls_all[j])
        L = int(t_dep[j] - t_arr[j])
        if cls == 0:
            rbar = 8.0 * byt[j] / dur[j] / 1e6
            ell = float(np.clip(rbar / PI_ON, *ELL_EL_CLIP))
            on = _onoff(rng, L, P_ON_OFF, P_OFF_ON)
        elif classes == "random":
            ell = float(rng.uniform(ELL_LO, ELL_HI))
            on = np.ones(L, dtype=bool)
        else:
            ell = RT_ELL
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
    n_dev = len(devices)
    n_video = int(np.sum(cls_arr == 1))
    n_gaming = int(np.sum(cls_arr == 2))
    meta = dict(
        site=site, k=int(k), load=float(load), seed=int(seed), T=int(T),
        date=str(day), window_start=w0.isoformat(),
        n_devices=n_dev,
        n_elastic=int(np.sum(cls_arr == 0)), n_video=n_video, n_gaming=n_gaming,
        share_video=n_video / n_dev, share_gaming=n_gaming / n_dev,
        classes=classes, tiers=tiers, rule=_effective_rule(rule),
        mean_conc=float(Ls.sum() / T), max_conc=int(conc.max()),
        median_stay_s=float(np.median(Ls)),
        ell_el_q50=float(np.percentile(el_ell, 50)), ell_el_q90=float(np.percentile(el_ell, 90)),
        ell_el_q99=float(np.percentile(el_ell, 99)),
        Dbar=Dbar, C_mean=float(C.mean()), C_cv=float(C.std() / C.mean()),
        frac_C_low=float(np.mean(C < 0.3 * C.mean())),
    )
    trace = dict(T=T, C=C, devices=devices, scenario=f"real:{site}")
    return trace, meta


def print_class_shares(rows):
    head = (f"{'site':8s}{'rule':9s}{'sessions':>10s}{'video %':>9s}{'gaming %':>10s}"
            f"{'el rin':>8s}{'el rout':>9s}{'vid rin':>9s}{'vid rout':>10s}{'gam rin':>9s}{'gam rout':>10s}")
    print(head)
    for r in rows:
        mi, mo = r["median_rin"], r["median_rout"]
        print(f"{r['site']:8s}{r['rule_name']:9s}{r['n_sessions']:10d}{100 * r['share_video']:9.2f}"
              f"{100 * r['share_gaming']:10.2f}{mi['elastic']:8.4f}{mo['elastic']:9.4f}"
              f"{mi['video']:9.4f}{mo['video']:10.4f}{mi['gaming']:9.4f}{mo['gaming']:10.4f}")


def main():
    download()
    for site in SITES:
        for k, (day, w0) in enumerate(pick_windows(site, N_DAYS, 7200)):
            print(f"{site} k={k} date={day} window_start={w0.isoformat()}")
    rows = [dict(class_shares(site, **rule), rule_name=name) for site in SITES for name, rule in RULE_SETS.items()]
    print(f"\nclass shares (sessions with duration >= {MIN_STAY} s starting on or after {SESSION_SINCE}; "
          "rin, rout in Mbit/s, medians per class)")
    print_class_shares(rows)
    tr, meta = make_real_trace("PW0127", 0, 7200, classes="log", tiers="free")
    print("PW0127 k=0 meta:", meta)


if __name__ == "__main__":
    main()
