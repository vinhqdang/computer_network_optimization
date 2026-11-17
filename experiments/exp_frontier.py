"""Efficiency-versus-RT-success frontier on the hotspot scenario, and unilateral deviation for capped priority.

Part 1 (truthful devices, T = 6000, seeds 0 to 4): REPAY and plain DPP over V, WFQ over its RT weight
multiplier, capped priority over the RT share q, and the PF and Priority baselines. Per-run metrics are those
of experiments/exp_compare.py.

Part 2: unilateral static deviation (a true elastic device declares video for its whole sojourn) for capped
priority with q in (0.2, 0.3, 0.5). Same protocol and helpers as part (a) of experiments/exp_strategic.py:
T = 3000, seeds 0 and 1, the same 30 devices per seed (numpy Generator(1000 + seed), sojourn >= 60 slots).

Run as: python -m experiments.exp_frontier   (writes results/frontier.json)
"""
import time

import numpy as np

from experiments.common import LABELS, pmap, save
from experiments.exp_strategic import N_PICK_DEV, T as T_DEV, _by_id, _dev_table, trace_of
from repay.mechanisms import PF, WFQ, PlainDPP, Priority, PriorityCap, Repay
from repay.params import Params
from repay.sim import make_trace, run

T = 6000
SEEDS = range(5)
PROCS = 2
V_VALUES = (5, 10, 20, 50, 100)
WFQ_MULTS = (1, 2, 4, 8, 16)
Q_VALUES = (0.1, 0.2, 0.3, 0.5, 1.0)
DEV_Q = (0.2, 0.3, 0.5)
DEV_SEEDS = (0, 1)
MIN_SOJOURN = 60
FAMILY_ORDER = ("repay", "dpp", "wfq", "priority-cap", "pf", "priority")


def _mech_of(family, param):
    """Mechanism and parameter set of one part-1 configuration."""
    if family == "repay":
        p = Params(V=float(param))
        return Repay(p), p
    if family == "dpp":
        p = Params(V=float(param))
        return PlainDPP(p), p
    p = Params()
    if family == "wfq":
        return WFQ(p, rt_mult=float(param)), p
    if family == "priority-cap":
        return PriorityCap(p, q=float(param)), p
    if family == "pf":
        return PF(p), p
    if family == "priority":
        return Priority(p), p
    raise ValueError(family)


def _front_job(job):
    """One truthful hotspot run; returns the metrics stored per run in exp_compare."""
    family, param, seed = job
    mech, p = _mech_of(family, param)
    r = run(make_trace("hotspot", T, seed), mech, p)
    return dict(family=family, param=param, seed=seed,
                rt_success_all=r["rt_success"]["all"], rt_success_V=r["rt_success"]["V"],
                el_rate=r["el_rate"], util_rate=r["util_rate"], max_env=r["max_env"], jain=r["jain"])


def front_jobs():
    jobs = []
    for s in SEEDS:
        jobs += [("repay", v, s) for v in V_VALUES]
        jobs += [("dpp", v, s) for v in V_VALUES]
        jobs += [("wfq", m, s) for m in WFQ_MULTS]
        jobs += [("priority-cap", q, s) for q in Q_VALUES]
        jobs += [("pf", None, s), ("priority", None, s)]
    return jobs


def _dev_worker(job):
    """One run of capped priority on a deviation-protocol trace (module-level for pmap)."""
    q, seed, tag, decl_items = job
    p = Params()
    declare = {int(k): int(v) for k, v in decl_items} if decl_items else None
    r = run(trace_of(seed), PriorityCap(p, q=q), p, declare=declare)
    dev = {k: np.asarray(v).tolist() for k, v in r["dev"].items()}
    return dict(q=q, seed=seed, tag=tag, dev=dev)


def pick_devices(seed, table):
    """Deviation sample of exp_strategic part (a): 30 true-elastic devices with at least 60 slots."""
    ids, cls, tier, L = table
    elig = ids[(cls == 0) & (L >= MIN_SOJOURN)]
    rng = np.random.default_rng(1000 + seed)
    return sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))


def _deviation_record(*, q, seed, dev, tier, L, vol_truth, vol_dev):
    gain = vol_dev - vol_truth
    return dict(mech="priority-cap", q=q, seed=seed, dev=dev, tier=tier, L=L, vol_truth=vol_truth,
                vol_dev=vol_dev, gain=gain, gain_per_slot=gain / L,
                rel_gain=(gain / vol_truth) if vol_truth > 0 else None)


def _summarise_dev(recs):
    rel = [r["rel_gain"] for r in recs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in recs)
    vd = sum(r["vol_dev"] for r in recs)
    gain = np.array([r["gain"] for r in recs], float)
    return dict(n=len(recs), median_rel_gain_pct=100 * float(np.median(rel)),
                pooled_gain_pct=100 * (vd - vt) / vt, share_gaining_pct=100 * float(np.mean(gain > 0)))


def main():
    t0 = time.time()
    jobs = front_jobs()
    print(f"{len(jobs)} frontier runs queued", flush=True)
    runs = pmap(_front_job, jobs, procs=PROCS)
    print(f"frontier runs done in {time.time() - t0:.0f}s", flush=True)

    print(f"\nFrontier, hotspot, truthful devices, T={T}, means over {len(SEEDS)} seeds")
    print(f"{'mechanism':<16s}{'param':>7s}{'RT%':>8s}{'RT_V%':>8s}{'el_rate':>9s}{'util':>8s}"
          f"{'maxEnv':>9s}{'jain':>7s}")
    for fam in FAMILY_ORDER:
        params = [None] if fam in ("pf", "priority") else sorted({r["param"] for r in runs if r["family"] == fam})
        for prm in params:
            rs = [r for r in runs if r["family"] == fam and r["param"] == prm]
            mean = lambda k: float(np.nanmean([r[k] for r in rs]))
            ptxt = "--" if prm is None else f"{prm:g}"
            print(f"{LABELS[fam]:<16s}"
                  f"{ptxt:>7s}{100 * mean('rt_success_all'):8.1f}{100 * mean('rt_success_V'):8.1f}"
                  f"{mean('el_rate'):9.3f}{mean('util_rate'):8.2f}{mean('max_env'):9.2f}{mean('jain'):7.3f}")

    # Part 2: unilateral deviation for capped priority
    t1 = time.time()
    tables = {s: _dev_table(trace_of(s)) for s in DEV_SEEDS}
    picks = {s: pick_devices(s, tables[s]) for s in DEV_SEEDS}
    dev_jobs = []
    for q in DEV_Q:
        for s in DEV_SEEDS:
            dev_jobs.append((q, s, "truth", ()))
            for i in picks[s]:
                dev_jobs.append((q, s, f"dev:{i}", ((i, 1),)))
    print(f"\n{len(dev_jobs)} deviation runs queued", flush=True)
    res = {(r["q"], r["seed"], r["tag"]): r for r in pmap(_dev_worker, dev_jobs, procs=PROCS)}
    print(f"deviation runs done in {time.time() - t1:.0f}s", flush=True)

    recs = []
    for q in DEV_Q:
        for s in DEV_SEEDS:
            T0 = res[(q, s, "truth")]
            idx0 = _by_id(T0["dev"])
            for i in picks[s]:
                Rd = res[(q, s, f"dev:{i}")]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                recs.append(_deviation_record(
                    q=q, seed=s, dev=i, tier=int(T0["dev"]["tier"][j0]), L=int(T0["dev"]["L"][j0]),
                    vol_truth=float(T0["dev"]["vol"][j0]), vol_dev=float(Rd["dev"]["vol"][jd])))

    dev_summary = {}
    print("\nUnilateral static deviation, capped priority (T=3000, seeds 0 and 1, 30 devices per seed)")
    print(f"{'q':>5s}{'n':>5s}{'median rel %':>14s}{'pooled vol %':>14s}{'gain>0 %':>10s}")
    for q in DEV_Q:
        rq = [r for r in recs if r["q"] == q]
        dev_summary[str(q)] = _summarise_dev(rq)
        d = dev_summary[str(q)]
        print(f"{q:5.2f}{d['n']:5d}{d['median_rel_gain_pct']:14.2f}{d['pooled_gain_pct']:14.2f}"
              f"{d['share_gaining_pct']:10.1f}")

    path = save("frontier", dict(
        T=T, seeds=list(SEEDS), scenario="hotspot", procs=PROCS,
        grids=dict(repay_V=list(V_VALUES), dpp_V=list(V_VALUES), wfq_mult=list(WFQ_MULTS),
                   priority_cap_q=list(Q_VALUES)),
        runs=runs,
        deviation=dict(T=T_DEV, seeds=list(DEV_SEEDS), mechanism="priority-cap", q_values=list(DEV_Q),
                       picks={str(s): picks[s] for s in DEV_SEEDS}, records=recs, summary=dev_summary),
        elapsed_s=time.time() - t0,
    ))
    print(f"\nwrote {path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
