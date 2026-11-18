"""Trace-driven sweep over V, the capped-priority share q and the WFQ multiplier, with unilateral deviation.

Traces are those of experiments/exp_real.py, variant main (classes from the logged traffic, tiers drawn from
TIER_P_EST): site PW0127, load 1.0, k = 0 to 5. Trace construction is reused from exp_real, so the REPAY run
at V = 20 reproduces the variant main runs in results/real_compare.json (checked and printed).

Part 1 (truthful devices): REPAY, No-debt and Plain DPP over V; capped priority over q; WFQ over its RT weight
multiplier; PF and Priority. Per-run metrics are those of exp_real Part 1, plus family, param and the bound
B_free_video = Params(V=V).B(0, 1) for the REPAY family (REPAY and No-debt).

Part 2 (unilateral static deviation): the same 20 true-elastic devices per trace as exp_real Part 2
(numpy Generator(3000 + k), stay >= 60 slots), each rerun declaring video for its whole stay. Mechanisms:
REPAY at V in (50, 100, 200) and No-debt at V in (20, 50, 100, 200). REPAY at V = 20 is not rerun; its
records are loaded from results/real_deviation.json (marked by source), and its truthful run is recomputed
only to check the stored vol_truth values.

Run as: python -m experiments.exp_real_sweep   (writes results/real_sweep.json)
"""
import time

import numpy as np

from experiments.common import LABELS, load, pmap, save
from experiments.exp_real import K_VALUES, MAIN_SITE, MIN_STAY, N_DEV, T, _by_id, _cell, _mean, _pick, _trace
from repay.mechanisms import PF, WFQ, PlainDPP, Priority, PriorityCap, Repay
from repay.params import F_TIER, Params
from repay.sim import run

VARIANT = "main"
LOAD = 1.0
PROCS = 4
V_VALUES = (5, 10, 20, 50, 100, 200, 500)
Q_VALUES = (0.05, 0.1, 0.2, 0.3, 0.5)
WFQ_MULTS = (1, 2, 4, 8)
V_FAMILIES = ("repay", "no-debt", "dpp")
BOUND_FAMILIES = ("repay", "no-debt")
DEV_CONFIGS = (("repay", 50), ("repay", 100), ("repay", 200),
               ("no-debt", 20), ("no-debt", 50), ("no-debt", 100), ("no-debt", 200))
REF_DEV = ("repay", 20)
REF_SOURCE = "results/real_deviation.json"


def _make(family, param):
    """Mechanism and parameter set of one configuration; V families use Params(V=param)."""
    p = Params(V=float(param)) if family in V_FAMILIES else Params()
    if family == "repay":
        return Repay(p), p
    if family == "no-debt":
        return Repay(p, debt_price=False), p
    if family == "dpp":
        return PlainDPP(p), p
    if family == "priority-cap":
        return PriorityCap(p, q=float(param)), p
    if family == "wfq":
        return WFQ(p, rt_mult=float(param)), p
    if family == "pf":
        return PF(p), p
    if family == "priority":
        return Priority(p), p
    raise ValueError(f"unknown family {family!r}")


def _part1_job(job):
    """One truthful run on one trace; returns the metrics stored per run in exp_real Part 1."""
    family, param, k = job
    trace, _ = _trace(VARIANT, MAIN_SITE, k, LOAD)
    mech, p = _make(family, param)
    t0 = time.perf_counter()
    r = run(trace, mech, p)
    wall = time.perf_counter() - t0
    dev = r["dev"]
    el = dev["cls"] == 0
    vid = dev["cls"] == 1
    env_el = dev["max_env"][el]
    rec = dict(
        family=family, param=param, variant=VARIANT, site=MAIN_SITE, load=LOAD, k=k,
        util_rate=r["util_rate"],
        rt_success=r["rt_success"],
        el_rate=r["el_rate"],
        jain=r["jain"],
        served_ratio=r["served_ratio"],
        free_floor_ratio=r["free_floor_ratio"],
        max_env=r["max_env"],
        cap_violations=r["cap_violations"],
        ms_per_slot=r["ms_per_slot"],
        run_s=wall,
        max_env_el_mean=float(env_el.mean()) if env_el.size else float("nan"),
        max_env_el_p95=float(np.percentile(env_el, 95)) if env_el.size else float("nan"),
        util_per_slot_video=float(dev["util"][vid].sum() / dev["L"][vid].sum())
        if dev["L"][vid].sum() > 0 else float("nan"),
        B_free_video=float(p.B(F_TIER, 1)) if family in BOUND_FAMILIES else None,
    )
    if "D_over_B_max" in r:
        rec["D_over_B_max"] = r["D_over_B_max"]
    return rec


def _dev_job(job):
    """One run on the trace of trace k (PW0127, load 1.0) with an optional declaration."""
    family, V, k, tag, decl_items = job
    trace, _ = _trace(VARIANT, MAIN_SITE, k, LOAD)
    mech, p = _make(family, V)
    declare = {int(i): int(v) for i, v in decl_items} if decl_items else None
    r = run(trace, mech, p, declare=declare)
    dev = r["dev"]
    out = dict(family=family, V=V, k=k, tag=tag, util_rate=r["util_rate"],
               rt_success_all=r["rt_success"]["all"], cap_violations=r["cap_violations"],
               dev=dict(id=np.asarray(dev["id"]).tolist(), tier=np.asarray(dev["tier"]).tolist(),
                        L=np.asarray(dev["L"]).tolist(), vol=np.asarray(dev["vol"]).tolist()))
    if "D_over_B_max" in r:
        out["D_over_B_max"] = r["D_over_B_max"]
    return out


def part1(t0):
    jobs = []
    for k in K_VALUES:
        for fam in V_FAMILIES:
            jobs += [(fam, V, k) for V in V_VALUES]
        jobs += [("priority-cap", q, k) for q in Q_VALUES]
        jobs += [("wfq", m, k) for m in WFQ_MULTS]
        jobs += [("pf", None, k), ("priority", None, k)]
    print(f"part 1: {len(jobs)} runs ({len(K_VALUES)} traces)", flush=True)
    runs = pmap(_part1_job, jobs, procs=PROCS)
    print(f"part 1 done in {time.time() - t0:.0f}s", flush=True)
    return runs


ORDER1 = [("repay", V) for V in V_VALUES] + [("no-debt", V) for V in V_VALUES] + \
         [("dpp", V) for V in V_VALUES] + [("priority-cap", q) for q in Q_VALUES] + \
         [("wfq", m) for m in WFQ_MULTS] + [("pf", None), ("priority", None)]


def print_part1(runs):
    print(f"\nTruthful devices, variant {VARIANT}, site {MAIN_SITE}, load {LOAD}, means over {len(K_VALUES)} traces")
    print(f"{'family':14s}{'param':>7s}{'RT%':>7s}{'RT_V%':>7s}{'el_rate':>9s}{'util':>8s}{'maxEnv':>9s}"
          f"{'env95':>8s}{'P_ratio':>9s}{'D/B max':>9s}{'B_fV':>8s}")
    for fam, prm in ORDER1:
        rs = [r for r in runs if r["family"] == fam and r["param"] == prm]
        has_db = any("D_over_B_max" in r for r in rs)
        line = (f"{LABELS[fam]:14s}" + f"{'--' if prm is None else format(prm, 'g'):>7s}"
                + _cell(100 * _mean([r["rt_success"]["all"] for r in rs]), 7, ".1f")
                + _cell(100 * _mean([r["rt_success"]["V"] for r in rs]), 7, ".1f")
                + _cell(_mean([r["el_rate"] for r in rs]), 9, ".2f")
                + _cell(_mean([r["util_rate"] for r in rs]), 8, ".2f")
                + _cell(_mean([r["max_env"] for r in rs]), 9, ".2f")
                + _cell(_mean([r["max_env_el_p95"] for r in rs]), 8, ".2f")
                + _cell(_mean([(r["served_ratio"] or {}).get("P") for r in rs]), 9, ".3f")
                + _cell(_mean([r.get("D_over_B_max") for r in rs]) if has_db else None, 9, ".4f")
                + _cell(_mean([r["B_free_video"] for r in rs]), 8, ".1f"))
        print(line)
    print(f"capacity violations (part 1): {sum(r['cap_violations'] for r in runs)}")


def reproduction(runs):
    """Part 1 runs at the exp_real parameters against results/real_compare.json (variant main, load 1.0)."""
    rc = load("real_compare")
    ref = {(r["mech"], r["k"]): r for r in rc["runs"]
           if r["variant"] == VARIANT and r["site"] == MAIN_SITE and r["load"] == LOAD}
    mine = {(r["family"], r["param"], r["k"]): r for r in runs}
    mapping = {"repay": ("repay", 20), "no-debt": ("no-debt", 20), "dpp": ("dpp", 20), "pf": ("pf", None),
               "wfq": ("wfq", 4), "priority": ("priority", None), "priority-cap": ("priority-cap", 0.3)}
    out = {}
    print("\nreproduction of results/real_compare.json (variant main, PW0127, load 1.0; max over traces)")
    print(f"{'mechanism':14s}{'max |d util|':>16s}{'max |d RT|':>16s}{'max |d el_rate|':>18s}")
    for m, (fam, prm) in mapping.items():
        du = dr = de = 0.0
        for k in K_VALUES:
            a, b = mine[(fam, prm, k)], ref[(m, k)]
            du = max(du, abs(a["util_rate"] - b["util_rate"]))
            dr = max(dr, abs(a["rt_success"]["all"] - b["rt_success"]["all"]))
            de = max(de, abs(a["el_rate"] - b["el_rate"]))
        out[m] = dict(max_abs_util_rate=du, max_abs_rt_success=dr, max_abs_el_rate=de)
        print(f"{LABELS[m]:14s}{du:16.2e}{dr:16.2e}{de:18.2e}")
    return out


def part2(t0):
    traces = {k: _trace(VARIANT, MAIN_SITE, k, LOAD) for k in K_VALUES}
    picks = {k: _pick(k, traces[k][0]["devices"]) for k in K_VALUES}
    ref_file = load("real_deviation")
    picks_match = all(picks[k] == sorted(ref_file["picks"][str(k)]) for k in K_VALUES)
    print(f"\npart 2: picks match results/real_deviation.json: {picks_match}", flush=True)

    jobs = []
    for fam, V in DEV_CONFIGS + (REF_DEV,):
        for k in K_VALUES:
            jobs.append((fam, V, k, "truth", ()))
            if (fam, V) in DEV_CONFIGS:
                for i in picks[k]:
                    jobs.append((fam, V, k, f"dev:{i}", ((i, 1),)))
    n_dev_runs = sum(len(v) for v in picks.values())
    print(f"part 2: {len(jobs)} runs ({n_dev_runs} deviating devices per configuration, "
          f"{len(DEV_CONFIGS)} configurations)", flush=True)
    res = pmap(_dev_job, jobs, procs=PROCS)
    print(f"part 2 runs done in {time.time() - t0:.0f}s", flush=True)

    truth = {(r["family"], r["V"], r["k"]): r for r in res if r["tag"] == "truth"}
    by_tag = {(r["family"], r["V"], r["k"], r["tag"]): r for r in res}

    recs = []
    for fam, V in DEV_CONFIGS:
        B_val = float(Params(V=float(V)).B(0, 1))
        for k in K_VALUES:
            T0 = truth[(fam, V, k)]
            idx0 = _by_id(T0["dev"])
            devs = traces[k][0]["devices"]
            for i in picks[k]:
                Rd = by_tag[(fam, V, k, f"dev:{i}")]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                vt = float(T0["dev"]["vol"][j0])
                vd = float(Rd["dev"]["vol"][jd])
                gain = vd - vt
                tier = int(T0["dev"]["tier"][j0])
                L = int(T0["dev"]["L"][j0])
                recs.append(dict(
                    family=fam, V=V, source="sweep", variant=VARIANT, k=k, dev=i, tier=tier, L=L,
                    ell=float(devs[i]["ell"]), vol_truth=vt, vol_dev=vd, gain=gain, gain_per_slot=gain / L,
                    rel_gain=(gain / vt) if vt > 0 else None, B=B_val))

    # Reference records: REPAY at V = 20 from results/real_deviation.json (same picks, same protocol).
    ref_recs = [dict(family="repay", V=20, source=REF_SOURCE, variant=r["variant"], k=r["k"], dev=r["dev"],
                     tier=r["tier"], L=r["L"], ell=r["ell"], vol_truth=r["vol_truth"], vol_dev=r["vol_dev"],
                     gain=r["gain"], gain_per_slot=r["gain_per_slot"], rel_gain=r["rel_gain"], B=r["B"])
                for r in ref_file["records"] if r["mech"] == "repay"]

    # Truthful-volume check: vol_truth of every deviating device equals its volume in the truthful run
    # of the same (family, V) (the sweep's runs; for the reference, the stored vol_truth against a recomputed
    # REPAY V = 20 truthful run).
    vol_check = {}
    for fam, V in DEV_CONFIGS + (REF_DEV,):
        diffs = []
        for r in recs + ref_recs:
            if (r["family"], r["V"]) != (fam, V):
                continue
            T0 = truth[(fam, V, r["k"])]
            vol_by_id = dict(zip(T0["dev"]["id"], T0["dev"]["vol"]))
            diffs.append(abs(r["vol_truth"] - vol_by_id[r["dev"]]))
        vol_check[f"{fam}:{V}"] = max(diffs) if diffs else float("nan")

    rep_db = [r["D_over_B_max"] for r in res if r["family"] in BOUND_FAMILIES and "D_over_B_max" in r]
    viol = sum(r["cap_violations"] for r in res)
    print(f"truthful volume check (max |vol_truth - truthful run volume|): "
          + ", ".join(f"{k} {v:.2e}" for k, v in vol_check.items()), flush=True)
    return recs + ref_recs, picks, dict(vol_check=vol_check, repay_family_D_over_B_max=max(rep_db),
                                        cap_violations=viol, picks_match=picks_match)


def _dev_stats(recs):
    gain = np.array([r["gain"] for r in recs], float)
    gps = np.array([r["gain_per_slot"] for r in recs], float)
    B = np.array([r["B"] for r in recs], float)
    rel = [r["rel_gain"] for r in recs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in recs)
    vd = sum(r["vol_dev"] for r in recs)
    return dict(
        n=len(recs),
        median_rel_gain_pct=100 * float(np.median(rel)) if rel else float("nan"),
        pooled_gain_pct=100 * (vd - vt) / vt if vt > 0 else float("nan"),
        share_gaining_pct=100 * float(np.mean(gain > 0)) if gain.size else float("nan"),
        p95_gain_per_slot=float(np.percentile(gps, 95)) if gps.size else float("nan"),
        n_above_bound=int(np.sum(gain > B)),
        max_gain_over_bound=float(np.max(gain / B)) if gain.size else float("nan"),
        max_gain_mbit=float(np.max(gain)) if gain.size else float("nan"),
    )


def dev_summary(recs):
    """Summary per (family, V), in the order of the configurations plus the REPAY V = 20 reference."""
    out = []
    for fam, V in (REF_DEV,) + DEV_CONFIGS:
        rs = [r for r in recs if r["family"] == fam and r["V"] == V]
        out.append(dict(family=fam, V=V, source=rs[0]["source"], **_dev_stats(rs)))
    return out


def print_dev(summary):
    print(f"\nUnilateral static deviation, variant {VARIANT}, PW0127, load 1.0, traces k=0..5, "
          f"{N_DEV} devices per trace")
    print(f"{'family':12s}{'V':>5s}{'n':>6s}{'med rel %':>11s}{'pool vol %':>12s}{'gain>0 %':>10s}"
          f"{'p95 g/slot':>12s}{'>B':>5s}{'max g/B':>10s}{'max gain':>10s}  source")
    for s in summary:
        print(f"{LABELS[s['family']]:12s}{s['V']:5d}{s['n']:6d}{s['median_rel_gain_pct']:11.2f}"
              f"{s['pooled_gain_pct']:12.2f}{s['share_gaining_pct']:10.1f}{s['p95_gain_per_slot']:12.4f}"
              f"{s['n_above_bound']:5d}{s['max_gain_over_bound']:10.3f}{s['max_gain_mbit']:10.3f}  {s['source']}")


def main():
    t0 = time.time()
    for k in K_VALUES:
        _trace(VARIANT, MAIN_SITE, k, LOAD)   # built in the parent, inherited by the worker processes
    runs = part1(t0)
    print_part1(runs)
    repro = reproduction(runs)
    recs, picks, checks = part2(t0)
    summary = dev_summary(recs)
    print_dev(summary)

    part1_db = [r["D_over_B_max"] for r in runs if r["family"] in BOUND_FAMILIES and "D_over_B_max" in r]
    checks["repay_family_D_over_B_max_part1"] = max(part1_db)
    checks["cap_violations_part1"] = sum(r["cap_violations"] for r in runs)
    checks["cap_violations_total"] = checks["cap_violations"] + checks["cap_violations_part1"]
    print(f"\nREPAY-family max D/B over part 1: {max(part1_db):.4f} (part 2: "
          f"{checks['repay_family_D_over_B_max']:.4f})")
    print(f"capacity violations, all runs: {checks['cap_violations_total']}")

    path = save("real_sweep", dict(
        T=T, variant=VARIANT, site=MAIN_SITE, load=LOAD, k_values=list(K_VALUES), procs=PROCS,
        grids=dict(V=list(V_VALUES), priority_cap_q=list(Q_VALUES), wfq_mult=list(WFQ_MULTS),
                   dev_configs=[[f, v] for f, v in DEV_CONFIGS], dev_reference=[REF_DEV[0], REF_DEV[1]]),
        n_per_trace=N_DEV, min_stay=MIN_STAY, picks={str(k): picks[k] for k in K_VALUES},
        meta=[dict(_trace(VARIANT, MAIN_SITE, k, LOAD)[1], variant=VARIANT) for k in K_VALUES],
        part1_runs=runs, reproduction=repro,
        deviation=dict(records=recs, summary=summary), checks=checks,
        elapsed_s=time.time() - t0))
    print("wrote", path, flush=True)
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
