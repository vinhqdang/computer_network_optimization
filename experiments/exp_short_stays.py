"""Unilateral static deviation for short stays: true-elastic devices with 5 to 59 slots.

Same protocol as part (a) of experiments/exp_strategic.py (a true elastic device declares video for its whole
sojourn, one rerun per device, T = 3000, hotspot traces). Per seed, 30 eligible devices are drawn with
numpy Generator(2000 + seed); if fewer than 30 are eligible, all of them are used.

Run as: python -m experiments.exp_short_stays   (writes results/short_stays.json)
"""
import time

import numpy as np

from experiments.common import LABELS, pmap, save
from experiments.exp_strategic import N_PICK_DEV, T, _by_id, _dev_table, _worker, trace_of
from repay.params import Params

MECHS = ("repay", "dpp", "priority", "wfq", "pf")
REPAY_FAMILY = ("repay",)
SEEDS = (0, 1, 2, 3)
PICK_BASE = 2000
L_MIN, L_MAX = 5, 59
PROCS = 2


def pick_devices(seed, table):
    """Short-stay deviation sample for one trace (all eligible devices if there are fewer than 30)."""
    ids, cls, tier, L = table
    elig = ids[(cls == 0) & (L >= L_MIN) & (L <= L_MAX)]
    if elig.size <= N_PICK_DEV:
        return sorted(int(i) for i in elig)
    rng = np.random.default_rng(PICK_BASE + seed)
    return sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))


def _record(*, mech, seed, dev, tier, L, vol_truth, vol_dev, B):
    gain = vol_dev - vol_truth
    return dict(mech=mech, seed=seed, dev=dev, tier=tier, L=L, vol_truth=vol_truth, vol_dev=vol_dev,
                gain=gain, gain_per_slot=gain / L,
                rel_gain=(gain / vol_truth) if vol_truth > 0 else None, B=B)


def _summarise(recs, mech):
    """Per-mechanism summary; relative gains and pooled volume gain as in exp_deviation."""
    rm = [r for r in recs if r["mech"] == mech]
    rel = [r["rel_gain"] for r in rm if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in rm)
    vd = sum(r["vol_dev"] for r in rm)
    gain = np.array([r["gain"] for r in rm], float)
    out = dict(n=len(rm),
               median_rel_gain_pct=100 * float(np.median(rel)) if rel else None,
               pooled_gain_pct=100 * (vd - vt) / vt if vt > 0 else None,
               share_gaining_pct=100 * float(np.mean(gain > 0)) if rm else None,
               mean_gain_mbit=float(gain.mean()) if rm else None,
               max_gain_mbit=float(gain.max()) if rm else None)
    if mech in REPAY_FAMILY and rm:
        ratios = np.array([r["gain"] / r["B"] for r in rm])
        out["max_gain_over_B"] = float(ratios.max())
    return out


def main():
    t0 = time.time()
    P = Params()
    tables = {s: _dev_table(trace_of(s)) for s in SEEDS}
    picks = {s: pick_devices(s, tables[s]) for s in SEEDS}
    print("devices per seed: " + ", ".join(f"seed {s}: {len(picks[s])}" for s in SEEDS), flush=True)

    jobs = []
    for m in MECHS:
        for s in SEEDS:
            jobs.append((m, s, "truth", ()))
            for i in picks[s]:
                jobs.append((m, s, f"dev:{i}", ((i, 1),)))
    print(f"{len(jobs)} runs queued", flush=True)
    res = {(r["mech"], r["seed"], r["tag"]): r for r in pmap(_worker, jobs, procs=PROCS)}
    print(f"runs done in {time.time() - t0:.0f}s", flush=True)

    recs = []
    for m in MECHS:
        for s in SEEDS:
            T0 = res[(m, s, "truth")]
            idx0 = _by_id(T0["dev"])
            for i in picks[s]:
                Rd = res[(m, s, f"dev:{i}")]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                tier = int(T0["dev"]["tier"][j0])
                recs.append(_record(
                    mech=m, seed=s, dev=i, tier=tier, L=int(T0["dev"]["L"][j0]),
                    vol_truth=float(T0["dev"]["vol"][j0]), vol_dev=float(Rd["dev"]["vol"][jd]),
                    B=float(P.B(tier, 1)) if m in REPAY_FAMILY else None))

    summary = {m: _summarise(recs, m) for m in MECHS}
    print(f"\nShort stays (L in [{L_MIN}, {L_MAX}]), unilateral static deviation, T={T}, seeds {list(SEEDS)}")
    print(f"{'mechanism':<10s}{'n':>5s}{'median rel %':>14s}{'pooled vol %':>14s}{'gain>0 %':>10s}"
          f"{'mean Mbit':>11s}{'max Mbit':>10s}{'max gain/B':>12s}")
    for m in MECHS:
        d = summary[m]
        gob = f"{d['max_gain_over_B']:12.4f}" if "max_gain_over_B" in d else f"{'--':>12s}"
        print(f"{LABELS[m]:<10s}{d['n']:5d}{d['median_rel_gain_pct']:14.2f}{d['pooled_gain_pct']:14.2f}"
              f"{d['share_gaining_pct']:10.1f}{d['mean_gain_mbit']:11.4f}{d['max_gain_mbit']:10.4f}{gob}")

    path = save("short_stays", dict(
        T=T, scenario="hotspot", seeds=list(SEEDS), mechanisms=list(MECHS),
        length_range=[L_MIN, L_MAX], pick_base_seed=PICK_BASE, n_pick=N_PICK_DEV,
        picks={str(s): picks[s] for s in SEEDS}, records=recs, summary=summary,
        elapsed_s=time.time() - t0,
    ))
    print(f"\nwrote {path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
