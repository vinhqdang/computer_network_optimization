"""E1: deficit bound and class envy versus V (REPAY and plain DPP), hotspot and adversarial capacity.

Adversarial scenario: the hotspot trace with its capacity replaced by a square wave alternating
150 and 15 Mbit/s every 60 slots (starting at 150). Writes results/bound.json.
Run from the repository root: python -m experiments.exp_bound
"""
import time

import numpy as np

from experiments.common import mean_ci, pmap, save
from repay.mechanisms import PlainDPP, Repay
from repay.params import Params
from repay.sim import make_trace, run

T = 6000
VS = [2, 5, 10, 20, 50, 100]
SEEDS = range(5)
SCENARIOS = ["hotspot", "adversarial"]
MECHS = ["repay", "dpp"]


def _trace(scen, seed):
    """Hotspot trace for seed; the adversarial variant swaps in the square-wave capacity."""
    tr = make_trace("hotspot", T, seed)
    if scen == "adversarial":
        slots = np.arange(T)
        tr["C"] = np.where((slots // 60) % 2 == 0, 150.0, 15.0)
    return tr


def _job(job):
    """One simulation run; returns the metrics and the theoretical bounds for this V."""
    scen, V, seed, mech = job
    p = Params(V=float(V))
    m = Repay(p) if mech == "repay" else PlainDPP(p)
    r = run(_trace(scen, seed), m, p)
    B_all = max(p.B(g, k) for g in range(3) for k in (1, 2))
    B_vid = max(p.B(g, 1) for g in range(3))
    return dict(
        scen=scen, V=V, seed=seed, mech=mech,
        D_over_B_max=r["D_over_B_max"], max_env=r["max_env"], util_rate=r["util_rate"],
        rt_success_all=r["rt_success"]["all"], rt_success_V=r["rt_success"]["V"],
        el_rate=r["el_rate"], jain=r["jain"], B_max=B_all, B_video_max=B_vid,
    )


def main():
    jobs = [(s, V, seed, m) for s in SCENARIOS for V in VS for seed in SEEDS for m in MECHS]
    t0 = time.time()
    runs = pmap(_job, jobs)
    elapsed = time.time() - t0

    print(f"E1 bound sweep: {len(runs)} runs, T={T}, {elapsed:.0f} s wall time")
    hdr = f"{'scen':12s}{'V':>5s}{'mech':>7s}{'D/B max':>10s}{'maxEnv':>10s}{'+-CI':>8s}{'util':>8s}{'RT_V':>7s}{'B_vid':>8s}"
    print(hdr)
    for s in SCENARIOS:
        for V in VS:
            for m in MECHS:
                rs = [r for r in runs if r["scen"] == s and r["V"] == V and r["mech"] == m]
                db = max(r["D_over_B_max"] for r in rs)
                env, ci = mean_ci([r["max_env"] for r in rs])
                util = np.mean([r["util_rate"] for r in rs])
                rtv = np.mean([r["rt_success_V"] for r in rs])
                print(f"{s:12s}{V:5d}{m:>7s}{db:10.3f}{env:10.2f}{ci:8.2f}{util:8.2f}{rtv:7.3f}"
                      f"{rs[0]['B_video_max']:8.1f}")

    path = save("bound", dict(T=T, V_values=VS, seeds=list(SEEDS), scenarios=SCENARIOS,
                              mechanisms=MECHS, elapsed_s=elapsed, runs=runs))
    print("wrote", path)


if __name__ == "__main__":
    main()
