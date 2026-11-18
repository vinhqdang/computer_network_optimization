"""E9: real-time share, population size and unilateral deviation on the hotspot scenario.

Part 1 (truthful devices, T = 6000, seeds 0 to 4): the share rho_RT of real-time devices in
(0.05, 0.10, 0.20, 0.35, 0.50), split video:gaming = 5:2 (cls_p = (1 - rho, rho 5/7, rho 2/7)).
Per-run metrics are those of experiments/exp_compare.py plus rho_RT.

Part 2 (truthful devices, T = 6000, seeds 0 to 2) at the default mix: arrival rate, burst size and mean
capacity are scaled together by s in (0.25, 0.5, 1, 2, 4), so the load per device is unchanged.
Records store the scale and the mean number of active devices.

Part 3: unilateral static deviation exactly as part (a) of experiments/exp_strategic (30 true-elastic devices
with at least 60 slots per trace, numpy Generator(1000 + seed), T = 3000, seeds 0 and 1), on traces with
rho_RT = 0.10.

Run as: python -m experiments.exp_mix   (writes results/mix.json)
"""
import functools
import time

import numpy as np

from experiments.common import LABELS, MECHS, pmap, save
from experiments.exp_strategic import _by_id, _dev_table
from repay.params import Params
from repay.sim import HOTSPOT_DEFAULTS, make_trace, run

T = 6000
PROCS = 2
MECH_ORDER = ["repay", "no-debt", "dpp", "pf", "wfq", "priority", "priority-cap", "credit"]
RHO_GRID = (0.05, 0.10, 0.20, 0.35, 0.50)
SEEDS = range(5)
SCALES = (0.25, 0.5, 1.0, 2.0, 4.0)
SCALE_SEEDS = range(3)
DEFAULT_RHO = round(1.0 - HOTSPOT_DEFAULTS["cls_p"][0], 2)

DEV_T = 3000
DEV_RHO = 0.10
DEV_SEEDS = (0, 1)
DEV_MECH_ORDER = ["repay", "no-debt", "dpp", "priority", "wfq", "priority-cap", "pf"]
REPAY_FAMILY = ("repay", "no-debt")
N_PICK_DEV = 30
MIN_SOJOURN = 60


def cls_mix(rho):
    """Device class shares (elastic, video, gaming) with real-time share rho and video:gaming = 5:2."""
    return (1.0 - rho, rho * 5.0 / 7.0, rho * 2.0 / 7.0)


def scale_overrides(scale):
    """Arrival rate, burst size and mean capacity multiplied together by the population scale."""
    return dict(arr_rate=HOTSPOT_DEFAULTS["arr_rate"] * scale,
                burst_size=HOTSPOT_DEFAULTS["burst_size"] * scale,
                C_mean=HOTSPOT_DEFAULTS["C_mean"] * scale)


def _mean_active(tr):
    """Time average of the number of devices present (arrived and not departed) over the horizon."""
    Tn = tr["T"]
    diff = np.zeros(Tn + 1)
    for d in tr["devices"]:
        a, b = d["t_arr"], min(d["t_dep"], Tn)
        if b > a:
            diff[a] += 1
            diff[b] -= 1
    return float(np.cumsum(diff)[:Tn].mean())


def _metrics(r):
    """Per-run metrics of experiments/exp_compare.py."""
    dev = r["dev"]
    el = dev["cls"] == 0
    vid = dev["cls"] == 1
    env_el = dev["max_env"][el]
    out = dict(
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


def _mix_job(job):
    """One truthful run at real-time share rho (part 1)."""
    rho, name, seed = job
    p = Params()
    tr = make_trace("hotspot", T, seed, cls_p=cls_mix(rho))
    r = run(tr, MECHS[name](p), p)
    return dict(rho_RT=rho, mech=name, seed=seed, n_active_mean=_mean_active(tr), **_metrics(r))


def _scale_job(job):
    """One truthful run at the default mix and population scale s (part 2)."""
    scale, name, seed = job
    p = Params()
    tr = make_trace("hotspot", T, seed, **scale_overrides(scale))
    r = run(tr, MECHS[name](p), p)
    return dict(scale=scale, rho_RT=DEFAULT_RHO, mech=name, seed=seed, n_active_mean=_mean_active(tr),
                **_metrics(r))


@functools.lru_cache(maxsize=4)
def dev_trace_of(seed):
    """Real-time share 0.10 trace of the deviation protocol (cached per process, never pickled)."""
    return make_trace("hotspot", DEV_T, seed, cls_p=cls_mix(DEV_RHO))


def _dev_worker(job):
    """One run of a mechanism on a deviation-protocol trace (module-level for pmap)."""
    name, seed, tag, decl_items = job
    p = Params()
    declare = {int(k): int(v) for k, v in decl_items} if decl_items else None
    r = run(dev_trace_of(seed), MECHS[name](p), p, declare=declare)
    dev = {k: np.asarray(v).tolist() for k, v in r["dev"].items()}
    return dict(mech=name, seed=seed, tag=tag, dev=dev)


def pick_devices(seed, table):
    """Deviation sample of exp_strategic part (a): 30 true-elastic devices with at least 60 slots."""
    ids, cls, tier, L = table
    elig = ids[(cls == 0) & (L >= MIN_SOJOURN)]
    rng = np.random.default_rng(1000 + seed)
    return sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))


def _dev_record(*, mech, seed, dev, tier, L, vol_truth, vol_dev, B):
    gain = vol_dev - vol_truth
    return dict(mech=mech, rho_RT=DEV_RHO, seed=seed, dev=dev, tier=tier, L=L, vol_truth=vol_truth,
                vol_dev=vol_dev, gain=gain, gain_per_slot=gain / L,
                rel_gain=(gain / vol_truth) if vol_truth > 0 else None, B=B)


def _dev_summary(recs):
    rel = [r["rel_gain"] for r in recs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in recs)
    vd = sum(r["vol_dev"] for r in recs)
    gain = np.array([r["gain"] for r in recs], float)
    out = dict(n=len(recs), median_rel_gain_pct=100 * float(np.median(rel)),
               pooled_gain_pct=100 * (vd - vt) / vt, share_gaining_pct=100 * float(np.mean(gain > 0)))
    bounded = [r for r in recs if r["B"] is not None]
    if bounded:
        out["n_above_B"] = int(sum(r["gain"] > r["B"] + 1e-9 for r in bounded))
        out["max_gain_over_B"] = float(max(r["gain"] / r["B"] for r in bounded))
    return out


def _grid_table(title, runs, key, cols, labels, value, fmt):
    """Plain-text table of seed means: rows mechanisms, columns the values of run field `key`."""
    lines = [title, f"{'mechanism':<14s}" + "".join(f"{lab:>14s}" for lab in labels)]
    for m in MECH_ORDER:
        cells = []
        for c in cols:
            vals = [value(r) for r in runs if r["mech"] == m and r[key] == c]
            cells.append(float(np.nanmean(vals)))
        lines.append(f"{LABELS[m]:<14s}" + "".join(f"{fmt.format(x):>14s}" for x in cells))
    return "\n".join(lines)


def main():
    t0 = time.time()
    p = Params()

    # Part 1: real-time share sweep
    jobs1 = [(rho, m, s) for rho in RHO_GRID for m in MECH_ORDER for s in SEEDS]
    print(f"part 1: {len(jobs1)} runs queued", flush=True)
    runs = pmap(_mix_job, jobs1, procs=PROCS)
    print(f"part 1 done in {time.time() - t0:.0f}s", flush=True)
    rho_labels = [f"rho={rho:.2f}" for rho in RHO_GRID]
    print(f"\npart 1, real-time share sweep, truthful devices, T={T}, means over {len(list(SEEDS))} seeds")
    print(_grid_table("RT success (%)", runs, "rho_RT", RHO_GRID, rho_labels,
                      lambda r: 100 * r["rt_success"]["all"], "{:.1f}"))
    print(_grid_table("Elastic rate (Mbit/s)", runs, "rho_RT", RHO_GRID, rho_labels,
                      lambda r: r["el_rate"], "{:.3f}"))
    print(_grid_table("Max class envy (Mbit)", runs, "rho_RT", RHO_GRID, rho_labels,
                      lambda r: r["max_env"], "{:.2f}"))
    print(_grid_table("Utility rate (per slot)", runs, "rho_RT", RHO_GRID, rho_labels,
                      lambda r: r["util_rate"], "{:.2f}"))

    # Part 2: population scale at the default mix
    t1 = time.time()
    jobs2 = [(s, m, seed) for s in SCALES for m in MECH_ORDER for seed in SCALE_SEEDS]
    print(f"\npart 2: {len(jobs2)} runs queued", flush=True)
    scale_runs = pmap(_scale_job, jobs2, procs=PROCS)
    print(f"part 2 done in {time.time() - t1:.0f}s", flush=True)
    n_act = {s: float(np.mean([r["n_active_mean"] for r in scale_runs if r["scale"] == s])) for s in SCALES}
    scale_labels = [f"{n_act[s]:.0f} dev" for s in SCALES]
    print(f"\npart 2, population scale at the default mix, truthful devices, T={T}, means over "
          f"{len(list(SCALE_SEEDS))} seeds")
    print("mean active devices: " + ", ".join(f"s={s:g}: {n_act[s]:.1f}" for s in SCALES))
    print(_grid_table("RT success (%)", scale_runs, "scale", SCALES, scale_labels,
                      lambda r: 100 * r["rt_success"]["all"], "{:.1f}"))
    print(_grid_table("Elastic rate (Mbit/s)", scale_runs, "scale", SCALES, scale_labels,
                      lambda r: r["el_rate"], "{:.3f}"))
    print(_grid_table("Max class envy (Mbit)", scale_runs, "scale", SCALES, scale_labels,
                      lambda r: r["max_env"], "{:.2f}"))
    print(_grid_table("Utility rate (per slot)", scale_runs, "scale", SCALES, scale_labels,
                      lambda r: r["util_rate"], "{:.2f}"))

    # Part 3: unilateral static deviation at rho_RT = 0.10
    t2 = time.time()
    tables = {s: _dev_table(dev_trace_of(s)) for s in DEV_SEEDS}
    picks = {s: pick_devices(s, tables[s]) for s in DEV_SEEDS}
    dev_jobs = []
    for m in DEV_MECH_ORDER:
        for s in DEV_SEEDS:
            dev_jobs.append((m, s, "truth", ()))
            for i in picks[s]:
                dev_jobs.append((m, s, f"dev:{i}", ((i, 1),)))
    print(f"\npart 3: {len(dev_jobs)} deviation runs queued", flush=True)
    res = {(r["mech"], r["seed"], r["tag"]): r for r in pmap(_dev_worker, dev_jobs, procs=PROCS)}
    print(f"part 3 done in {time.time() - t2:.0f}s", flush=True)

    recs = []
    for m in DEV_MECH_ORDER:
        for s in DEV_SEEDS:
            T0 = res[(m, s, "truth")]
            idx0 = _by_id(T0["dev"])
            for i in picks[s]:
                Rd = res[(m, s, f"dev:{i}")]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                tier = int(T0["dev"]["tier"][j0])
                recs.append(_dev_record(
                    mech=m, seed=s, dev=i, tier=tier, L=int(T0["dev"]["L"][j0]),
                    vol_truth=float(T0["dev"]["vol"][j0]), vol_dev=float(Rd["dev"]["vol"][jd]),
                    B=p.B(tier, 1) if m in REPAY_FAMILY else None))

    dev_summary = {}
    print(f"\npart 3, unilateral static deviation at rho_RT={DEV_RHO} (T={DEV_T}, seeds 0 and 1, "
          f"30 devices per seed)")
    print(f"{'mechanism':<14s}{'n':>5s}{'median rel %':>14s}{'pooled vol %':>14s}{'gaining %':>11s}"
          f"{'n > B':>8s}{'max gain/B':>12s}")
    for m in DEV_MECH_ORDER:
        d = _dev_summary([r for r in recs if r["mech"] == m])
        dev_summary[m] = d
        above = f"{d['n_above_B']:d}" if "n_above_B" in d else "--"
        mx = f"{d['max_gain_over_B']:.3f}" if "max_gain_over_B" in d else "--"
        print(f"{LABELS[m]:<14s}{d['n']:5d}{d['median_rel_gain_pct']:14.2f}{d['pooled_gain_pct']:14.2f}"
              f"{d['share_gaining_pct']:11.1f}{above:>8s}{mx:>12s}")

    path = save("mix", dict(
        T=T, procs=PROCS, mix_rule="cls_p = (1 - rho, rho * 5/7, rho * 2/7)", default_rho=DEFAULT_RHO,
        rho_grid=list(RHO_GRID), seeds=list(SEEDS), mechanisms=MECH_ORDER,
        scales=list(SCALES), scale_seeds=list(SCALE_SEEDS), scale_overrides="arr_rate, burst_size, C_mean",
        mean_active_by_scale={str(s): n_act[s] for s in SCALES},
        runs=runs, scale_runs=scale_runs,
        deviation=dict(T=DEV_T, seeds=list(DEV_SEEDS), rho_RT=DEV_RHO, mechanisms=DEV_MECH_ORDER,
                       picks={str(s): picks[s] for s in DEV_SEEDS}, records=recs, summary=dev_summary),
        elapsed_s=time.time() - t0,
    ))
    print(f"\nwrote {path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
