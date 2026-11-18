"""Second real-trace scenario: truthful comparison and unilateral deviation on two further public traces.

Scenarios (experiments.data_real2): gps with ghent and mesa with raca. Each is a 7200-slot day window, k = 0 to 5,
at load 1.0. Traces are built once per (source, k) and cached; the parallel workers inherit the cache.

Part 1 (truthful devices): REPAY (V = 20), No-debt (V = 5), plain DPP, PF, WFQ, Priority, capped priority
(q = 0.3), Credit, FQ-w, JS, LendRecoup, Potential and DMMF. Metrics as experiments.exp_real Part 1, with the
REPAY-family bound ratio D_over_B_max where the mechanism reports it.

Part 2 (unilateral static deviation): per trace, 20 true-elastic devices whose stay in the window is at least
60 slots (numpy Generator(4000 + 100 * source_index + k); all of them if fewer), each rerun with declare={id: 1}
for its whole stay. Mechanisms: REPAY (V = 20), No-debt (V = 5), plain DPP, Priority, capped priority (q = 0.3)
and PF. The bound B is Params(V).B(tier, 1) for the two REPAY-family mechanisms.

Run as: python -m experiments.exp_real2   (writes results/real2_compare.json and results/real2_deviation.json)
"""
import functools
import time

import numpy as np

from experiments.common import LABELS, MECHS, pmap, save
from experiments.data_real2 import SOURCE_INDEX, SOURCES, make_trace2, source_summary
from repay.mechanisms import PriorityCap
from repay.params import Params
from repay.sim import run

T = 7200
K_VALUES = tuple(range(6))
LOAD = 1.0
PROCS = 4
V_REPAY = 20.0
V_NODEBT = 5.0
Q_CAP = 0.3
MECH_ORDER = ["repay", "no-debt-v5", "dpp", "pf", "wfq", "priority", "priority-cap", "credit",
              "fq-w", "js", "lendrecoup", "potential", "dmmf"]
DEV_MECHS = ["repay", "no-debt-v5", "dpp", "priority", "priority-cap", "pf"]
BOUND_MECHS = ("repay", "no-debt-v5")
N_DEV = 20
DEV_MIN_STAY = 60
LAB = {**LABELS, "no-debt-v5": "No-debt ($V=5$)", "priority-cap": "Capped priority ($q=0.3$)"}


def _make(mech):
    """Mechanism and parameters of one configuration (REPAY family at V = 20 and V = 5)."""
    if mech == "repay":
        p = Params(V=V_REPAY)
        return MECHS["repay"](p), p
    if mech == "no-debt-v5":
        p = Params(V=V_NODEBT)
        return MECHS["no-debt"](p), p
    p = Params()
    if mech == "priority-cap":
        return PriorityCap(p, q=Q_CAP), p
    return MECHS[mech](p), p


@functools.lru_cache(maxsize=None)
def _trace(source, k):
    """Trace and metadata for one (source, k) at load 1.0, cached per process."""
    return make_trace2(source, k, T, load=LOAD, classes="log", tiers="estimated")


def _finite(vals):
    return [v for v in vals if v is not None and np.isfinite(v)]


def _mean(vals):
    v = _finite(vals)
    return float(np.mean(v)) if v else float("nan")


def _cell(x, width, fmt):
    s = "--" if x is None or not np.isfinite(x) else format(x, fmt)
    return f"{s:>{width}s}"


def _part1_job(job):
    """One truthful run; returns the metrics of exp_real Part 1 and the total volume of the devices."""
    source, mech, k = job
    trace, _ = _trace(source, k)
    m, p = _make(mech)
    t0 = time.perf_counter()
    r = run(trace, m, p)
    wall = time.perf_counter() - t0
    dev = r["dev"]
    env_el = dev["max_env"][dev["cls"] == 0]
    rec = dict(
        source=source, mech=mech, k=k,
        util_rate=r["util_rate"], rt_success=r["rt_success"], el_rate=r["el_rate"], jain=r["jain"],
        served_ratio=r["served_ratio"], free_floor_ratio=r["free_floor_ratio"], max_env=r["max_env"],
        cap_violations=r["cap_violations"], ms_per_slot=r["ms_per_slot"], run_s=wall,
        max_env_el_p95=float(np.percentile(env_el, 95)) if env_el.size else float("nan"),
        vol_total=float(np.sum(dev["vol"])),
    )
    if "D_over_B_max" in r:
        rec["D_over_B_max"] = r["D_over_B_max"]
    return rec


def _dev_job(job):
    """One run on the trace of (source, k) at load 1.0, with the devices in decl declaring video."""
    source, mech, k, tag, decl = job
    trace, _ = _trace(source, k)
    m, p = _make(mech)
    declare = {int(i): 1 for i in decl} if decl else None
    r = run(trace, m, p, declare=declare)
    dev = r["dev"]
    out = dict(source=source, mech=mech, k=k, tag=tag, util_rate=r["util_rate"],
               cap_violations=r["cap_violations"],
               dev_id=np.asarray(dev["id"]).tolist(), dev_tier=np.asarray(dev["tier"]).tolist(),
               dev_L=np.asarray(dev["L"]).tolist(), dev_vol=np.asarray(dev["vol"], float).tolist())
    if "D_over_B_max" in r:
        out["D_over_B_max"] = r["D_over_B_max"]
    return out


def _pick2(source, k, devices):
    """Deviation sample of (source, k): true-elastic devices with a stay of at least DEV_MIN_STAY slots."""
    elig = np.array([d["id"] for d in devices if d["cls"] == 0 and d["t_dep"] - d["t_arr"] >= DEV_MIN_STAY],
                    dtype=np.int64)
    if elig.size == 0:
        raise ValueError(f"no eligible devices in {source} k={k}")
    n = min(N_DEV, elig.size)
    rng = np.random.default_rng(4000 + 100 * SOURCE_INDEX[source] + k)
    return sorted(int(i) for i in rng.choice(elig, size=n, replace=False))


def _tab1(runs, source):
    lines = [f"{'mechanism':18s}{'utility':>9s}{'RT%':>8s}{'RT_V%':>8s}{'el_rate':>9s}{'maxEnv':>9s}"
             f"{'env95':>8s}{'P_ratio':>9s}{'D/B max':>9s}{'capV':>6s}"]
    for m in MECH_ORDER:
        rs = [r for r in runs if r["source"] == source and r["mech"] == m]
        dbs = [r["D_over_B_max"] for r in rs if "D_over_B_max" in r]
        lines.append(
            f"{LAB[m]:18s}"
            + _cell(_mean([r["util_rate"] for r in rs]), 9, ".2f")
            + _cell(100 * _mean([r["rt_success"]["all"] for r in rs]), 8, ".1f")
            + _cell(100 * _mean([r["rt_success"]["V"] for r in rs]), 8, ".1f")
            + _cell(_mean([r["el_rate"] for r in rs]), 9, ".2f")
            + _cell(_mean([r["max_env"] for r in rs]), 9, ".2f")
            + _cell(_mean([r["max_env_el_p95"] for r in rs]), 8, ".2f")
            + _cell(_mean([(r["served_ratio"] or {}).get("P") for r in rs]), 9, ".3f")
            + _cell(_mean(dbs) if dbs else None, 9, ".4f")
            + f"{sum(r['cap_violations'] for r in rs):6d}")
    return "\n".join(lines)


def _summary(recs, m):
    rs = [r for r in recs if r["mech"] == m]
    gain = np.array([r["gain"] for r in rs], float)
    rel = [r["rel_gain"] for r in rs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in rs)
    vd = sum(r["vol_dev"] for r in rs)
    out = dict(n=len(rs), median_rel_gain_pct=100 * float(np.median(rel)) if rel else float("nan"),
               pooled_gain_pct=100 * (vd - vt) / vt if vt > 0 else float("nan"),
               share_gaining_pct=100 * float(np.mean(gain > 0)) if gain.size else float("nan"))
    if m in BOUND_MECHS:
        B = np.array([r["B"] for r in rs], float)
        out["n_above_bound"] = int(np.sum(gain / B > 1.0))
        out["max_gain_over_B"] = float(np.max(gain / B)) if gain.size else float("nan")
    return out


def _tab2(summ):
    lines = [f"{'mechanism':18s}{'n':>6s}{'median rel %':>14s}{'pooled vol %':>14s}{'gain>0 %':>10s}"
             f"{'above bound':>13s}{'max gain/B':>12s}"]
    for m in DEV_MECHS:
        s = summ[m]
        ab = f"{s['n_above_bound']:d}" if "n_above_bound" in s else "--"
        mb = f"{s['max_gain_over_B']:.3f}" if "max_gain_over_B" in s else "--"
        lines.append(f"{LAB[m]:18s}{s['n']:6d}{s['median_rel_gain_pct']:14.2f}{s['pooled_gain_pct']:14.2f}"
                     f"{s['share_gaining_pct']:10.1f}{ab:>13s}{mb:>12s}")
    return "\n".join(lines)


def part1(t0):
    jobs = [(s, m, k) for s in SOURCES for m in MECH_ORDER for k in K_VALUES]
    print(f"part 1: {len(jobs)} runs ({len(SOURCES)} scenarios x {len(MECH_ORDER)} mechanisms x {len(K_VALUES)} traces)",
          flush=True)
    runs = pmap(_part1_job, jobs, procs=PROCS)
    print(f"part 1 done in {time.time() - t0:.0f}s", flush=True)
    for s in SOURCES:
        print(f"\nTruthful devices, scenario {s}, load {LOAD}, means over {len(K_VALUES)} traces")
        print(_tab1(runs, s))
    return runs


def part2(t0, part1_runs):
    picks = {s: {k: _pick2(s, k, _trace(s, k)[0]["devices"]) for k in K_VALUES} for s in SOURCES}
    jobs = []
    for m in DEV_MECHS:
        for s in SOURCES:
            for k in K_VALUES:
                jobs.append((s, m, k, "truth", ()))
                jobs += [(s, m, k, f"dev:{i}", (i,)) for i in picks[s][k]]
    print(f"\npart 2: {len(jobs)} runs ({sum(len(v) for s in picks.values() for v in s.values())} "
          f"deviating devices per mechanism and scenario)", flush=True)
    res = pmap(_dev_job, jobs, procs=PROCS)
    print(f"part 2 runs done in {time.time() - t0:.0f}s", flush=True)

    truth = {(r["source"], r["mech"], r["k"]): r for r in res if r["tag"] == "truth"}
    by_tag = {(r["source"], r["mech"], r["k"], r["tag"]): r for r in res}
    p1 = {(r["source"], r["mech"], r["k"]): r for r in part1_runs}
    util_diff = max(abs(truth[key]["util_rate"] - p1[key]["util_rate"]) for key in truth)
    vol_diff = max(abs(sum(truth[key]["dev_vol"]) - p1[key]["vol_total"]) for key in truth)

    recs = []
    for m in DEV_MECHS:
        Bp = _make(m)[1] if m in BOUND_MECHS else None
        for s in SOURCES:
            for k in K_VALUES:
                T0 = truth[(s, m, k)]
                idx0 = {int(i): j for j, i in enumerate(T0["dev_id"])}
                cap_of = {int(d["id"]): float(d["ell"]) for d in _trace(s, k)[0]["devices"]}
                for i in picks[s][k]:
                    Rd = by_tag[(s, m, k, f"dev:{i}")]
                    idxd = {int(x): j for j, x in enumerate(Rd["dev_id"])}
                    j0, jd = idx0[i], idxd[i]
                    tier = int(T0["dev_tier"][j0])
                    L = int(T0["dev_L"][j0])
                    vt = float(T0["dev_vol"][j0])
                    vd = float(Rd["dev_vol"][jd])
                    gain = vd - vt
                    recs.append(dict(
                        source=s, mech=m, k=k, dev=i, tier=tier, L=L, ell=cap_of[i],
                        vol_truth=vt, vol_dev=vd, gain=gain, gain_per_slot=gain / L,
                        rel_gain=(gain / vt) if vt > 0 else None,
                        B=float(Bp.B(tier, 1)) if Bp is not None else None))

    print(f"\nunilateral static deviation (20 true-elastic devices per trace, stay >= {DEV_MIN_STAY} slots, "
          f"traces k=0..5, load {LOAD})")
    summ = {}
    for s in SOURCES:
        rs_s = [r for r in recs if r["source"] == s]
        summ[s] = {m: _summary(rs_s, m) for m in DEV_MECHS}
        print(f"\nscenario {s}")
        print(_tab2(summ[s]))
        bound_recs = [r for r in rs_s if r["B"] is not None]
        print(f"  bound check ({', '.join(BOUND_MECHS)}): devices with gain > B: "
              f"{sum(int(r['gain'] > r['B']) for r in bound_recs)} of {len(bound_recs)}")
    print(f"\ntruthful part-2 runs vs part-1 runs: max |util_rate difference| = {util_diff:.2e}, "
          f"max |volume difference| = {vol_diff:.2e}")

    bound_db = [r["D_over_B_max"] for r in part1_runs + res
                if r["mech"] in BOUND_MECHS and "D_over_B_max" in r]
    viol = sum(r["cap_violations"] for r in part1_runs) + sum(r["cap_violations"] for r in res)
    print(f"REPAY-family max D/B over all runs: {max(bound_db):.4f}; capacity violations (all runs): {viol}")

    path = save("real2_deviation", dict(
        T=T, sources={s: source_summary(s) for s in SOURCES}, load=LOAD, k_values=list(K_VALUES),
        mechanisms=DEV_MECHS, n_per_trace=N_DEV, min_stay=DEV_MIN_STAY,
        V={"repay": V_REPAY, "no-debt-v5": V_NODEBT}, picks={s: {str(k): picks[s][k] for k in K_VALUES} for s in SOURCES},
        records=recs, summary=summ,
        truth_crosscheck_max_abs_util_diff=float(util_diff),
        truth_crosscheck_max_abs_vol_diff=float(vol_diff),
        repay_family_D_over_B_max=float(max(bound_db)), cap_violations_total=int(viol),
        elapsed_s=time.time() - t0))
    print("wrote", path, flush=True)


def main():
    t0 = time.time()
    for s in SOURCES:
        source_summary(s)
        for k in K_VALUES:
            _trace(s, k)
    runs = part1(t0)
    path = save("real2_compare", dict(
        T=T, sources={s: source_summary(s) for s in SOURCES}, load=LOAD, k_values=list(K_VALUES),
        mechanisms=MECH_ORDER, labels=LAB, V={"repay": V_REPAY, "no-debt-v5": V_NODEBT}, priority_cap_q=Q_CAP,
        meta={s: [_trace(s, k)[1] for k in K_VALUES] for s in SOURCES}, runs=runs,
        elapsed_s=time.time() - t0))
    print("wrote", path, flush=True)
    part2(t0, runs)
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
