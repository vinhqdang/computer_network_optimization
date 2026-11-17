"""E3: all nine mechanisms on the hotspot and home scenarios (truthful devices, 10 seeds).

Writes results/compare.json with the scalar aggregates returned by repay.sim.run and per-device
summaries computed from the run's device records (envy over true-elastic devices, true video
utility per slot).
Run from the repository root: python -m experiments.exp_compare
"""
import time

import numpy as np

from experiments.common import LABELS, MECHS, mean_ci, pmap, save
from repay.params import Params
from repay.sim import make_trace, run

T = 6000
SEEDS = range(10)
SCENARIOS = ["hotspot", "home"]
MECH_ORDER = ["repay", "repay-wc", "repay-e", "no-debt", "dpp", "pf", "wfq", "priority", "credit"]


def _job(job):
    """One (scenario, mechanism, seed) run with truthful declarations."""
    scen, name, seed = job
    p = Params()
    trace = make_trace(scen, T, seed)
    r = run(trace, MECHS[name](p), p)
    dev = r["dev"]
    el = dev["cls"] == 0
    vid = dev["cls"] == 1
    env_el = dev["max_env"][el]
    out = dict(
        scen=scen, mech=name, seed=seed,
        util_rate=r["util_rate"],
        rt_success=r["rt_success"],
        el_rate=r["el_rate"],
        jain=r["jain"],
        served_ratio=r["served_ratio"],
        free_floor_ratio=r["free_floor_ratio"],
        max_env=r["max_env"],
        cap_violations=r["cap_violations"],
        ms_per_slot=r["ms_per_slot"],
        max_env_el_mean=float(env_el.mean()) if env_el.size else float("nan"),
        max_env_el_p95=float(np.percentile(env_el, 95)) if env_el.size else float("nan"),
        util_per_slot_video=float(dev["util"][vid].sum() / dev["L"][vid].sum())
        if dev["L"][vid].sum() > 0 else float("nan"),
    )
    if "D_over_B_max" in r:
        out["D_over_B_max"] = r["D_over_B_max"]
    return out


def _ci(rs, key):
    return mean_ci([r[key] for r in rs])


def _tab(runs, scen):
    """Plain-text summary of the mean over seeds for one scenario."""
    lines = [f"{'mechanism':12s}{'util':>8s}{'RT%':>7s}{'RT_V%':>7s}{'el_rate':>9s}{'jain':>7s}"
             f"{'maxEnv':>9s}{'env95':>8s}{'P_ratio':>9s}{'Y_ratio':>9s}{'F_floor':>9s}"]
    for m in MECH_ORDER:
        rs = [r for r in runs if r["scen"] == scen and r["mech"] == m]
        util = np.mean([r["util_rate"] for r in rs])
        rt = np.mean([r["rt_success"]["all"] for r in rs]) * 100
        rtv = np.mean([r["rt_success"]["V"] for r in rs]) * 100
        el = np.nanmean([r["el_rate"] for r in rs])
        jn = np.nanmean([r["jain"] for r in rs])
        env = np.mean([r["max_env"] for r in rs])
        env95 = np.mean([r["max_env_el_p95"] for r in rs])
        sp = lambda k: np.nanmean([np.nan if r["served_ratio"][k] is None else r["served_ratio"][k]
                                   for r in rs])
        ff = np.nanmean([np.nan if r["free_floor_ratio"] is None else r["free_floor_ratio"] for r in rs])
        lines.append(f"{LABELS[m]:12s}{util:8.2f}{rt:7.1f}{rtv:7.1f}{el:9.2f}{jn:7.3f}{env:9.2f}"
                     f"{env95:8.2f}{sp('P'):9.3f}{sp('Y'):9.3f}{ff:9.3f}")
    return "\n".join(lines)


def main():
    jobs = [(s, m, seed) for s in SCENARIOS for m in MECH_ORDER for seed in SEEDS]
    t0 = time.time()
    runs = pmap(_job, jobs)
    elapsed = time.time() - t0
    print(f"E3 comparison: {len(runs)} runs, T={T}, {elapsed:.0f} s wall time")
    for s in SCENARIOS:
        print(f"\n[{s}] means over {len(SEEDS)} seeds")
        print(_tab(runs, s))
    path = save("compare", dict(T=T, seeds=list(SEEDS), scenarios=SCENARIOS, mechanisms=MECH_ORDER,
                                elapsed_s=elapsed, runs=runs))
    print("\nwrote", path)


if __name__ == "__main__":
    main()
