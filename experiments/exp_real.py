"""Real-trace scenario: truthful comparison and unilateral deviation on traces built from public data.

Traces come from experiments.data_real (Paris Wi-Fi sessions for PW0127 and PW0232, HSDPA capacity logs).
Each trace is a 7200-slot day window, k = 0 to 5. Three variants differ in how classes and tiers are set:
  main:   classes from the logged traffic (classify_sessions, default rule), tiers drawn from the estimated
          split of experiments.data_real.TIER_P_EST.
          Part 1 at PW0127 loads 0.7, 1.0, 1.5 and at PW0232 load 1.0.
  strict: as main, with the strict rule (sym in [0.5, 2], up_min 0.2). Part 1 at PW0127 load 1.0.
  tiers:  as main, with every device on the free tier (as in the logged network).
          Part 1 at PW0127 load 1.0.

Part 1 (truthful devices): REPAY, no-debt, plain DPP, PF, WFQ, Priority, capped priority with q = 0.3, and
Credit. Per-run metrics are those of experiments/exp_compare.py.

Part 2 (unilateral static deviation, variant main, site PW0127, load 1.0): per trace, 20 true-elastic devices
whose stay in the window is at least 60 slots (numpy Generator(3000 + k); all of them if fewer) each rerun with
declare={id: 1} for the whole stay. Mechanisms: REPAY, plain DPP, Priority, WFQ, PF, capped priority (q = 0.3).

Run as: python -m experiments.exp_real   (writes results/real_compare.json and results/real_deviation.json)
"""
import functools
import time

import numpy as np

from experiments.common import LABELS, MECHS, pmap, save
from experiments.data_real import RULE_SETS, STRICT_RULE, class_shares, make_real_trace, print_class_shares
from repay.mechanisms import PriorityCap
from repay.params import Params
from repay.sim import run

T = 7200
MAIN_SITE, SECOND_SITE = "PW0127", "PW0232"
SITES = (MAIN_SITE, SECOND_SITE)
K_VALUES = tuple(range(6))
MECH_ORDER = ["repay", "no-debt", "dpp", "pf", "wfq", "priority", "priority-cap", "credit"]
DEV_MECHS = ["repay", "dpp", "priority", "wfq", "pf", "priority-cap"]
Q_CAP = 0.3
N_DEV = 20
MIN_STAY = 60
PROCS = 4
REPAY_MECHS = ("repay",)
DEV_VARIANT = "main"

VARIANTS = {
    "main": dict(classes="log", tiers="estimated", rule=None,
                 part1=[(MAIN_SITE, 0.7), (MAIN_SITE, 1.0), (MAIN_SITE, 1.5), (SECOND_SITE, 1.0)]),
    "strict": dict(classes="log", tiers="estimated", rule=STRICT_RULE, part1=[(MAIN_SITE, 1.0)]),
    "tiers": dict(classes="log", tiers="free", rule=None, part1=[(MAIN_SITE, 1.0)]),
}


def _mech(name, p):
    """Mechanism constructor; capped priority uses q = 0.3 as in experiments/exp_frontier.py."""
    if name == "priority-cap":
        return PriorityCap(p, q=Q_CAP)
    return MECHS[name](p)


@functools.lru_cache(maxsize=None)
def _trace(variant, site, k, load):
    """Trace and metadata for one (variant, site, k, load), cached per process."""
    v = VARIANTS[variant]
    return make_real_trace(site, k, T, load=load, classes=v["classes"], tiers=v["tiers"], rule=v["rule"])


def _finite(vals):
    return [v for v in vals if v is not None and np.isfinite(v)]


def _mean(vals):
    """Mean of the finite values (None and NaN skipped), NaN if there are none."""
    v = _finite(vals)
    return float(np.mean(v)) if v else float("nan")


def _cell(x, width, fmt):
    """Right-justified number, or '--' when the value is None or NaN (an absent tier)."""
    s = "--" if x is None or not np.isfinite(x) else format(x, fmt)
    return f"{s:>{width}s}"


def _part1_job(job):
    """All mechanisms on one trace; returns the trace metadata and one record per mechanism."""
    variant, site, load, k = job
    trace, meta = _trace(variant, site, k, load)
    runs = []
    for m in MECH_ORDER:
        p = Params()
        t0 = time.perf_counter()
        r = run(trace, _mech(m, p), p)
        wall = time.perf_counter() - t0
        dev = r["dev"]
        el = dev["cls"] == 0
        vid = dev["cls"] == 1
        env_el = dev["max_env"][el]
        rec = dict(
            variant=variant, site=site, load=load, k=k, mech=m,
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
        )
        if "D_over_B_max" in r:
            rec["D_over_B_max"] = r["D_over_B_max"]
        runs.append(rec)
    return dict(variant=variant, site=site, load=load, k=k, meta=dict(meta, variant=variant), runs=runs)


def _tab(runs, variant, site, load):
    """Plain-text means over the traces of one (variant, site, load)."""
    lines = [f"{'mechanism':16s}{'util':>8s}{'RT%':>7s}{'RT_V%':>7s}{'el_rate':>9s}{'jain':>7s}"
             f"{'maxEnv':>9s}{'env95':>8s}{'P_ratio':>9s}{'Y_ratio':>9s}{'F_floor':>9s}{'capV':>6s}"]
    for m in MECH_ORDER:
        rs = [r for r in runs if r["variant"] == variant and r["site"] == site and r["load"] == load
              and r["mech"] == m]
        sp = lambda key: _mean([r["served_ratio"][key] for r in rs])
        lines.append(
            f"{LABELS[m]:16s}"
            + _cell(_mean([r["util_rate"] for r in rs]), 8, ".2f")
            + _cell(100 * _mean([r["rt_success"]["all"] for r in rs]), 7, ".1f")
            + _cell(100 * _mean([r["rt_success"]["V"] for r in rs]), 7, ".1f")
            + _cell(_mean([r["el_rate"] for r in rs]), 9, ".2f")
            + _cell(_mean([r["jain"] for r in rs]), 7, ".3f")
            + _cell(_mean([r["max_env"] for r in rs]), 9, ".2f")
            + _cell(_mean([r["max_env_el_p95"] for r in rs]), 8, ".2f")
            + _cell(sp("P"), 9, ".3f")
            + _cell(sp("Y"), 9, ".3f")
            + _cell(_mean([r["free_floor_ratio"] for r in rs]), 9, ".3f")
            + f"{sum(r['cap_violations'] for r in rs):6d}")
    return "\n".join(lines)


def _trace_line(m):
    return (f"  k={m['k']} date={m['date']} n={m['n_devices']} video={m['n_video']} gaming={m['n_gaming']} "
            f"mean_conc={m['mean_conc']:.1f} max_conc={m['max_conc']} median_stay={m['median_stay_s']:.0f}s "
            f"Dbar={m['Dbar']:.2f} C_mean={m['C_mean']:.2f} C_cv={m['C_cv']:.3f}")


def _dev_summary(recs, m):
    rs = [r for r in recs if r["mech"] == m]
    gain = np.array([r["gain"] for r in rs], float)
    gps = np.array([r["gain_per_slot"] for r in rs], float)
    rel = [r["rel_gain"] for r in rs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in rs)
    vd = sum(r["vol_dev"] for r in rs)
    out = dict(n=len(rs), median_rel_gain_pct=100 * float(np.median(rel)) if rel else float("nan"),
               pooled_gain_pct=100 * (vd - vt) / vt if vt > 0 else float("nan"),
               share_gaining_pct=100 * float(np.mean(gain > 0)) if gain.size else float("nan"),
               p95_gain_per_slot=float(np.percentile(gps, 95)) if gps.size else float("nan"))
    if m in REPAY_MECHS:
        B = np.array([r["B"] for r in rs], float)
        out["max_gain_over_B"] = float(np.max(gain / B)) if gain.size else float("nan")
        out["n_gain_over_B_gt1"] = int(np.sum(gain / B > 1.0))
    return out


def part1(t0):
    jobs = [(name, site, load, k) for name, v in VARIANTS.items() for site, load in v["part1"] for k in K_VALUES]
    print(f"part 1: {len(jobs)} traces x {len(MECH_ORDER)} mechanisms, variants {', '.join(VARIANTS)}", flush=True)
    groups = pmap(_part1_job, jobs, procs=PROCS)
    runs = [r for g in groups for r in g["runs"]]
    metas = [g["meta"] for g in groups]
    print(f"part 1 done in {time.time() - t0:.0f}s", flush=True)
    for name, v in VARIANTS.items():
        for site, load in v["part1"]:
            print(f"\n[variant {name}, {site}, load {load}] means over {len(K_VALUES)} traces")
            print(_tab(runs, name, site, load))
    print("\ncapacity violations per variant (Part 1, all runs):")
    for name in VARIANTS:
        print(f"  {name}: {sum(r['cap_violations'] for r in runs if r['variant'] == name)}")
    print("\ntrace metadata (Part 1, by variant):")
    for name, v in VARIANTS.items():
        for site, load in v["part1"]:
            print(f"{name}, {site}, load {load}:")
            for m in sorted((m for m in metas if m["variant"] == name and m["site"] == site
                             and m["load"] == load), key=lambda m: m["k"]):
                print(_trace_line(m))
    shares = [dict(class_shares(site, **rule), rule_name=name) for site in SITES for name, rule in RULE_SETS.items()]
    print("\nclass shares (sessions with duration >= 5 s starting on or after 2025-01-01)")
    print_class_shares(shares)
    path = save("real_compare", dict(
        T=T, sites=list(SITES), k_values=list(K_VALUES), mechanisms=MECH_ORDER, priority_cap_q=Q_CAP,
        variants={name: dict(classes=v["classes"], tiers=v["tiers"], rule=v["rule"] or {},
                             part1=[[s, l] for s, l in v["part1"]]) for name, v in VARIANTS.items()},
        class_shares=shares, meta=metas, runs=runs, elapsed_s=time.time() - t0))
    print("wrote", path, flush=True)
    return runs, metas


def part2(t0, part1_runs):
    traces = {k: _trace(DEV_VARIANT, MAIN_SITE, k, 1.0)[0] for k in K_VALUES}
    metas = {k: dict(_trace(DEV_VARIANT, MAIN_SITE, k, 1.0)[1], variant=DEV_VARIANT) for k in K_VALUES}
    picks = {k: _pick(k, traces[k]["devices"]) for k in K_VALUES}
    jobs = []
    for m in DEV_MECHS:
        for k in K_VALUES:
            jobs.append((DEV_VARIANT, m, k, "truth", ()))
            for i in picks[k]:
                jobs.append((DEV_VARIANT, m, k, f"dev:{i}", ((i, 1),)))
    print(f"\npart 2: {len(jobs)} runs ({sum(len(v) for v in picks.values())} deviating devices per mechanism)",
          flush=True)
    res = pmap(_dev_job, jobs, procs=PROCS)
    print(f"part 2 runs done in {time.time() - t0:.0f}s", flush=True)

    truth = {(r["mech"], r["k"]): r for r in res if r["tag"] == "truth"}
    by_tag = {(r["mech"], r["k"], r["tag"]): r for r in res}

    # Cross-check: truthful runs of part 2 reproduce the part-1 truthful runs of the same variant at load 1.0.
    p1 = {(r["mech"], r["k"]): r for r in part1_runs
          if r["variant"] == DEV_VARIANT and r["site"] == MAIN_SITE and r["load"] == 1.0}
    mismatch = max(abs(truth[(m, k)]["util_rate"] - p1[(m, k)]["util_rate"])
                   for m in DEV_MECHS for k in K_VALUES)

    recs = []
    for m in DEV_MECHS:
        for k in K_VALUES:
            T0 = truth[(m, k)]
            idx0 = _by_id(T0["dev"])
            devs = traces[k]["devices"]
            for i in picks[k]:
                Rd = by_tag[(m, k, f"dev:{i}")]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                tier = int(T0["dev"]["tier"][j0])
                L = int(T0["dev"]["L"][j0])
                vt = float(T0["dev"]["vol"][j0])
                vd = float(Rd["dev"]["vol"][jd])
                gain = vd - vt
                recs.append(dict(
                    variant=DEV_VARIANT, mech=m, k=k, dev=i, tier=tier, L=L, ell=float(devs[i]["ell"]),
                    vol_truth=vt, vol_dev=vd, gain=gain, gain_per_slot=gain / L,
                    rel_gain=(gain / vt) if vt > 0 else None,
                    B=float(Params().B(tier, 1)) if m in REPAY_MECHS else None))

    print(f"\nunilateral static deviation (variant {DEV_VARIANT}, PW0127, load 1.0, traces k=0..5)")
    print(f"{'mechanism':16s}{'n':>6s}{'median rel %':>14s}{'pooled vol %':>14s}{'gain>0 %':>10s}"
          f"{'p95 gain/slot':>15s}{'max gain/B':>12s}")
    summary = {}
    for m in DEV_MECHS:
        s = _dev_summary(recs, m)
        summary[m] = s
        mb = f"{s['max_gain_over_B']:.3f}" if "max_gain_over_B" in s else "--"
        print(f"{LABELS[m]:16s}{s['n']:6d}{s['median_rel_gain_pct']:14.2f}{s['pooled_gain_pct']:14.2f}"
              f"{s['share_gaining_pct']:10.1f}{s['p95_gain_per_slot']:15.4f}{mb:>12s}")
    s = summary["repay"]
    print(f"REPAY: devices with gain/B > 1: {s['n_gain_over_B_gt1']} of {s['n']}")
    print(f"truthful part-2 runs vs part-1 runs: max |util_rate difference| = {mismatch:.2e}")

    rep_db = [r["D_over_B_max"] for r in res if r.get("mech") == "repay" and r.get("D_over_B_max") is not None] + \
             [r["D_over_B_max"] for r in part1_runs if r.get("mech") == "repay" and r.get("D_over_B_max") is not None]
    viol = sum(r["cap_violations"] for r in res) + sum(r["cap_violations"] for r in part1_runs)
    print(f"REPAY max D/B over all REPAY runs: {max(rep_db):.4f}; capacity violations (all runs): {viol}")

    path = save("real_deviation", dict(
        T=T, variant=DEV_VARIANT, site=MAIN_SITE, load=1.0, k_values=list(K_VALUES), mechanisms=DEV_MECHS,
        n_per_trace=N_DEV, min_stay=MIN_STAY, picks={str(k): picks[k] for k in K_VALUES},
        meta=[metas[k] for k in K_VALUES], records=recs, summary=summary,
        truth_crosscheck_max_abs_util_diff=float(mismatch),
        repay_D_over_B_max=float(max(rep_db)), cap_violations_total=int(viol),
        elapsed_s=time.time() - t0))
    print("wrote", path, flush=True)


def _by_id(dev):
    return {int(i): j for j, i in enumerate(dev["id"])}


def _pick(k, devices):
    """Deviation sample of trace k: true-elastic devices with a stay of at least MIN_STAY slots."""
    elig = np.array([d["id"] for d in devices if d["cls"] == 0 and d["t_dep"] - d["t_arr"] >= MIN_STAY],
                    dtype=np.int64)
    n = min(N_DEV, elig.size)
    rng = np.random.default_rng(3000 + k)
    return sorted(int(i) for i in rng.choice(elig, size=n, replace=False))


def _dev_job(job):
    """One run on the PW0127 trace of trace k at load 1.0 with optional declarations."""
    variant, mech, k, tag, decl_items = job
    p = Params()
    trace, _ = _trace(variant, MAIN_SITE, k, 1.0)
    declare = {int(i): int(v) for i, v in decl_items} if decl_items else None
    r = run(trace, _mech(mech, p), p, declare=declare)
    out = dict(variant=variant, mech=mech, k=k, tag=tag, util_rate=r["util_rate"], el_rate=r["el_rate"],
               rt_success_all=r["rt_success"]["all"], cap_violations=r["cap_violations"],
               dev={key: np.asarray(v).tolist() for key, v in r["dev"].items()})
    if "D_over_B_max" in r:
        out["D_over_B_max"] = r["D_over_B_max"]
    return out


def main():
    t0 = time.time()
    runs, _ = part1(t0)
    part2(t0, runs)
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
