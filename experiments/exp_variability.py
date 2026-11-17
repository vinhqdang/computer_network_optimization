"""E6: capacity variability sweep on the hotspot scenario.

The three-state capacity multipliers are scaled by s (C_cv_scale): m_j(s) = max(0.05, 1 + s (m_j - 1)).
C_mean is chosen so that the mean scaled multiplier times C_mean equals 90 Mbit/s (the three
states are equally likely in the long run, the modulating chain is doubly stochastic).
Writes results/variability.json.
Run from the repository root: python -m experiments.exp_variability
"""
import time

import numpy as np

from experiments.common import MECHS, pmap, save
from repay.params import Params
from repay.sim import C_MULTS, make_trace, run

T = 6000
SCALES = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
SEEDS = range(5)
MECH_NAMES = ["repay", "dpp", "pf", "wfq", "priority", "credit"]
TARGET_MEAN_CAP = 90.0


def c_mean_for(scale):
    """C_mean such that E[scaled multiplier] * C_mean = TARGET_MEAN_CAP."""
    mults = np.array([max(0.05, 1.0 + scale * (m - 1.0)) for m in C_MULTS])
    return TARGET_MEAN_CAP / mults.mean()


def _job(job):
    """One run for (scale, mechanism, seed)."""
    scale, name, seed = job
    p = Params()
    trace = make_trace("hotspot", T, seed, C_cv_scale=float(scale), C_mean=c_mean_for(scale))
    r = run(trace, MECHS[name](p), p)
    return dict(
        scale=scale, mech=name, seed=seed, C_mean=c_mean_for(scale),
        util_rate=r["util_rate"], rt_success_all=r["rt_success"]["all"],
        rt_success_V=r["rt_success"]["V"], el_rate=r["el_rate"], max_env=r["max_env"],
        jain=r["jain"],
    )


def main():
    jobs = [(s, m, seed) for s in SCALES for m in MECH_NAMES for seed in SEEDS]
    t0 = time.time()
    runs = pmap(_job, jobs)
    elapsed = time.time() - t0
    print(f"E6 variability: {len(runs)} runs, T={T}, {elapsed:.0f} s wall time")
    print("C_mean per scale: " + ", ".join(f"{s}:{c_mean_for(s):.2f}" for s in SCALES))
    print(f"{'scale':>6s}{'mech':>10s}{'util':>8s}{'RT%':>7s}{'RT_V%':>7s}{'el_rate':>9s}"
          f"{'maxEnv':>9s}{'jain':>7s}")
    for s in SCALES:
        for m in MECH_NAMES:
            rs = [r for r in runs if r["scale"] == s and r["mech"] == m]
            print(f"{s:6.2f}{m:>10s}{np.mean([r['util_rate'] for r in rs]):8.2f}"
                  f"{100 * np.mean([r['rt_success_all'] for r in rs]):7.1f}"
                  f"{100 * np.mean([r['rt_success_V'] for r in rs]):7.1f}"
                  f"{np.nanmean([r['el_rate'] for r in rs]):9.2f}"
                  f"{np.mean([r['max_env'] for r in rs]):9.2f}"
                  f"{np.nanmean([r['jain'] for r in rs]):7.3f}")
    path = save("variability", dict(T=T, scales=SCALES, seeds=list(SEEDS), mechanisms=MECH_NAMES,
                                    target_mean_capacity=TARGET_MEAN_CAP, elapsed_s=elapsed,
                                    runs=runs))
    print("wrote", path)


if __name__ == "__main__":
    main()
