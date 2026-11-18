"""Five additional baseline mechanisms (FQ-w, JS, LendRecoup, Potential, DMMF) and FQ on the scenarios of
exp_compare, exp_strategic (part a) and exp_real (variant main).

The new mechanisms run with the default constructors of the registry in experiments/common.py, on the same traces
and with the same metrics as the existing experiments, so that their rows can be placed next to the stored ones.
  Part 1  synthetic hotspot, truthful devices, as experiments/exp_compare.py (T, seeds, per-run metric dict).
          Reproduction check: PF and REPAY on seed 0 against results/compare.json.
  Part 2  unilateral static deviation on the synthetic hotspot as experiments/exp_strategic.py part (a): seeds
          0 and 1, the same picked devices (checked against results/strategic.json). FQ is not in Part 2.
  Part 3  trace-driven scenario, variant main of experiments/exp_real.py (site PW0127, load 1.0, k = 0..5).
          Reproduction check: PF on k = 0 against results/real_compare.json.
  Part 4  trace-driven unilateral deviation as experiments/exp_real.py Part 2, for the five new mechanisms
          (same picked devices, checked against results/real_deviation.json).

Writes results/baselines.json. Run from the repository root: python -m experiments.exp_baselines
"""
import time

import numpy as np

from experiments.common import LABELS, MECHS, load, pmap, save
from experiments.exp_compare import SEEDS, T as T_SYN, _job as compare_job
from experiments.exp_real import K_VALUES, MAIN_SITE, T as T_REAL, _mech, _pick, _trace, _dev_job
from experiments.exp_strategic import DEV_SEEDS, N_PICK_DEV, T as T_STRAT, _dev_table, trace_of
from repay.params import Params
from repay.sim import run

PROCS = 2
NEW_SYN = ("fq", "fq-w", "js", "lendrecoup", "potential", "dmmf")  # Parts 1 and 3
NEW_DEV = ("fq-w", "js", "lendrecoup", "potential", "dmmf")         # Parts 2 and 4
MAIN_VARIANT = "main"
TIMING_KEYS = ("ms_per_slot", "run_s")  # wall-clock measurements, excluded from the reproduction checks


def _by_id(dev):
    return {int(i): j for j, i in enumerate(dev["id"])}


def _finite_mean(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    return float(np.mean(v)) if v else float("nan")


def dev_stats(recs):
    """Deviation summary shared by the experiments and plots_baselines.py."""
    gain = np.array([r["gain"] for r in recs], float)
    gps = np.array([r["gain_per_slot"] for r in recs], float)
    rel = [r["rel_gain"] for r in recs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in recs)
    vd = sum(r["vol_dev"] for r in recs)
    return dict(
        n=len(recs),
        median_rel_gain_pct=100 * float(np.median(rel)) if rel else float("nan"),
        pooled_gain_pct=100 * (vd - vt) / vt if vt > 0 else float("nan"),
        share_gaining_pct=100 * float(np.mean(gain > 0)) if gain.size else float("nan"),
        p95_gain_per_slot=float(np.percentile(gps, 95)) if gps.size else float("nan"),
    )


# ----------------------------------------------------------------------------- jobs

def _real_job(job):
    """One mechanism on one trace of exp_real (same record layout as exp_real Part 1)."""
    variant, site, load_, k, name = job
    p = Params()
    trace, meta = _trace(variant, site, k, load_)
    t0 = time.perf_counter()
    r = run(trace, _mech(name, p), p)
    wall = time.perf_counter() - t0
    dev = r["dev"]
    el = dev["cls"] == 0
    vid = dev["cls"] == 1
    env_el = dev["max_env"][el]
    rec = dict(
        variant=variant, site=site, load=load_, k=k, mech=name,
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
    return rec


def _syn_dev_job(job):
    """One run on the synthetic hotspot of a seed with optional declarations (as exp_strategic._worker,
    additionally returning the capacity violation count)."""
    mech, seed, tag, decl_items = job
    p = Params()
    declare = {int(i): int(v) for i, v in decl_items} if decl_items else None
    r = run(trace_of(seed), MECHS[mech](p), p, declare=declare)
    return dict(mech=mech, seed=seed, tag=tag, util_rate=r["util_rate"], cap_violations=r["cap_violations"],
                dev={k: np.asarray(v).tolist() for k, v in r["dev"].items()})


# ----------------------------------------------------------------------------- checks

def _flat(o, prefix=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(_flat(v, f"{prefix}{k}."))
    elif isinstance(o, (list, tuple)):
        for i, v in enumerate(o):
            out.update(_flat(v, f"{prefix}{i}."))
    else:
        out[prefix[:-1]] = None if isinstance(o, float) and not np.isfinite(o) else o
    return out


def _compare_runs(new, stored):
    """Max absolute difference over all numeric fields (timing fields excluded) and count of other mismatches."""
    fn = {k: v for k, v in _flat(new).items() if not k.split(".")[0] in TIMING_KEYS}
    fs = {k: v for k, v in _flat(stored).items() if not k.split(".")[0] in TIMING_KEYS}
    max_abs, n_fields, n_mismatch = 0.0, 0, 0
    for k in fs:
        if k not in fn:
            n_mismatch += 1
            continue
        a, b = fn[k], fs[k]
        n_fields += 1
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            max_abs = max(max_abs, abs(float(a) - float(b)))
        elif a != b:
            n_mismatch += 1
    return dict(max_abs_diff=max_abs, fields=n_fields, mismatches=n_mismatch,
                cap_violations=new["cap_violations"])


# ----------------------------------------------------------------------------- printing

COLS = [
    ("Utility", lambda r: r["util_rate"], 2),
    ("RT succ %", lambda r: 100 * r["rt_success"]["all"], 1),
    ("Video succ %", lambda r: 100 * r["rt_success"]["V"], 1),
    ("El. rate", lambda r: r["el_rate"], 2),
    ("Jain", lambda r: r["jain"], 3),
    ("Max envy", lambda r: r["max_env"], 2),
    ("Env p95", lambda r: r["max_env_el_p95"], 2),
    ("Prem. ratio", lambda r: r["served_ratio"]["P"], 3),
    ("PAYG ratio", lambda r: r["served_ratio"]["Y"], 3),
    ("Free-floor", lambda r: r["free_floor_ratio"], 3),
    ("ms/slot", lambda r: r["ms_per_slot"], 2),
]


def _safe(fn, r):
    try:
        return fn(r)
    except (KeyError, TypeError):
        return None


def _print_means(title, runs, mechs, groups):
    print(f"\n{title} (means over {groups})")
    print(f"{'mechanism':12s}" + "".join(f"{c[0]:>14s}" for c in COLS))
    for m in mechs:
        rs = [r for r in runs if r["mech"] == m]
        cells = []
        for _, fn, dec in COLS:
            v = _finite_mean([_safe(fn, r) for r in rs])
            cells.append("--" if not np.isfinite(v) else f"{v:.{dec}f}")
        print(f"{LABELS[m]:12s}" + "".join(f"{c:>14s}" for c in cells))


def _print_dev(title, recs, mechs):
    print(f"\n{title}")
    print(f"{'mechanism':12s}{'n':>6s}{'median rel %':>14s}{'pooled vol %':>14s}{'gain>0 %':>11s}"
          f"{'p95 gain/slot':>15s}")
    for m in mechs:
        s = dev_stats([r for r in recs if r["mech"] == m])
        print(f"{LABELS[m]:12s}{s['n']:6d}{s['median_rel_gain_pct']:14.2f}{s['pooled_gain_pct']:14.2f}"
              f"{s['share_gaining_pct']:11.1f}{s['p95_gain_per_slot']:15.4f}")


def _deviation_records(mechs, groups, truth, dev_runs, picks, gkey):
    """Deviation records for every (mechanism, group, picked device); vol_truth from the truthful run."""
    recs, id_mismatch, L_mismatch, vol_mismatch = [], 0, 0, 0
    for m in mechs:
        for g in groups:
            T0 = truth[(m, g)]
            idx0 = _by_id(T0["dev"])
            for i in picks[g]:
                Rd = dev_runs[(m, g, i)]
                j0 = idx0[i]
                jd = _by_id(Rd["dev"])[i]
                id_mismatch += int(i not in idx0)
                L = int(T0["dev"]["L"][j0])
                L_mismatch += int(int(Rd["dev"]["L"][jd]) != L)
                vt = float(T0["dev"]["vol"][j0])
                vol_mismatch += int(vt != float(T0["dev"]["vol"][idx0[i]]))
                vd = float(Rd["dev"]["vol"][jd])
                gain = vd - vt
                recs.append(dict(mech=m, **{gkey: g}, dev=i, tier=int(T0["dev"]["tier"][j0]), L=L,
                                 vol_truth=vt, vol_dev=vd, gain=gain, gain_per_slot=gain / L,
                                 rel_gain=(gain / vt) if vt > 0 else None))
    checks = dict(device_missing_in_truth=id_mismatch, sojourn_length_mismatch=L_mismatch,
                  vol_truth_mismatch=vol_mismatch)
    return recs, checks


# ----------------------------------------------------------------------------- parts

def part1(checks):
    t0 = time.time()
    jobs = [("hotspot", m, s) for m in NEW_SYN for s in SEEDS]
    runs = pmap(compare_job, jobs, procs=PROCS)
    print(f"part 1: {len(runs)} runs, {time.time() - t0:.0f}s", flush=True)
    stored = load("compare")["runs"]
    rep = [("hotspot", "pf", 0), ("hotspot", "repay", 0)]
    rerun = pmap(compare_job, rep, procs=PROCS)
    checks["part1_reproduction"] = {}
    for job, r in zip(rep, rerun):
        s = next(x for x in stored if x["scen"] == job[0] and x["mech"] == job[1] and x["seed"] == job[2])
        cmp_ = _compare_runs(r, s)
        checks["part1_reproduction"][job[1]] = cmp_
        print(f"reproduction {job[1]} seed {job[2]} vs results/compare.json: max |diff| = "
              f"{cmp_['max_abs_diff']:.3g} over {cmp_['fields']} fields, other mismatches {cmp_['mismatches']}")
    _print_means("part 1: synthetic hotspot, truthful", runs, NEW_SYN, f"{len(list(SEEDS))} seeds")
    return dict(T=T_SYN, seeds=list(SEEDS), mechanisms=list(NEW_SYN), runs=runs,
                reproduction=checks["part1_reproduction"], elapsed_s=time.time() - t0)


def part2(checks):
    t0 = time.time()
    picks = {}
    for s in DEV_SEEDS:
        ids, cls, tier, L = _dev_table(trace_of(s))
        elig = ids[(cls == 0) & (L >= 60)]
        rng = np.random.default_rng(1000 + s)
        picks[s] = sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))
    stored = load("strategic")["picks_deviation"]
    checks["part2_picks_match_strategic"] = all(picks[s] == stored[str(s)] for s in DEV_SEEDS)

    jobs = []
    for m in NEW_DEV:
        for s in DEV_SEEDS:
            jobs.append((m, s, "truth", ()))
            for i in picks[s]:
                jobs.append((m, s, f"dev:{i}", ((i, 1),)))
    print(f"part 2: {len(jobs)} runs", flush=True)
    res = pmap(_syn_dev_job, jobs, procs=PROCS)
    truth = {(r["mech"], r["seed"]): r for r in res if r["tag"] == "truth"}
    by_tag = {(r["mech"], r["seed"], int(r["tag"].split(":")[1])): r for r in res if r["tag"] != "truth"}
    recs, dchk = _deviation_records(NEW_DEV, DEV_SEEDS, truth, by_tag, picks, "seed")
    checks["part2_device_checks"] = dchk
    checks["part2_capacity_violations"] = sum(r["cap_violations"] for r in res)
    _print_dev("part 2: unilateral static deviation, synthetic hotspot, seeds 0 and 1", recs, NEW_DEV)
    summary = {m: dev_stats([r for r in recs if r["mech"] == m]) for m in NEW_DEV}
    print(f"part 2 done in {time.time() - t0:.0f}s")
    return dict(T=T_STRAT, seeds=list(DEV_SEEDS), mechanisms=list(NEW_DEV),
                picks={str(s): picks[s] for s in DEV_SEEDS}, records=recs, summary=summary,
                cap_violations=checks["part2_capacity_violations"], elapsed_s=time.time() - t0)


def part3(checks):
    t0 = time.time()
    jobs = [(MAIN_VARIANT, MAIN_SITE, 1.0, k, m) for m in NEW_SYN for k in K_VALUES]
    runs = pmap(_real_job, jobs, procs=PROCS)
    print(f"part 3: {len(runs)} runs, {time.time() - t0:.0f}s", flush=True)
    stored = [r for r in load("real_compare")["runs"]
              if r["variant"] == MAIN_VARIANT and r["site"] == MAIN_SITE and r["load"] == 1.0]
    rerun = _real_job((MAIN_VARIANT, MAIN_SITE, 1.0, 0, "pf"))
    s = next(x for x in stored if x["k"] == 0 and x["mech"] == "pf")
    cmp_ = _compare_runs(rerun, s)
    checks["part3_reproduction"] = cmp_
    print(f"reproduction pf k=0 vs results/real_compare.json: max |diff| = {cmp_['max_abs_diff']:.3g} over "
          f"{cmp_['fields']} fields, other mismatches {cmp_['mismatches']}")
    _print_means("part 3: trace-driven, variant main, PW0127, load 1.0", runs, NEW_SYN,
                 f"{len(K_VALUES)} traces")
    metas = [_trace(MAIN_VARIANT, MAIN_SITE, k, 1.0)[1] for k in K_VALUES]
    checks["part3_capacity_violations"] = sum(r["cap_violations"] for r in runs)
    return dict(T=T_REAL, site=MAIN_SITE, load=1.0, variant=MAIN_VARIANT, k_values=list(K_VALUES),
                mechanisms=list(NEW_SYN), runs=runs, meta=metas,
                reproduction=cmp_, elapsed_s=time.time() - t0)


def part4(checks, part3_runs):
    t0 = time.time()
    traces = {k: _trace(MAIN_VARIANT, MAIN_SITE, k, 1.0)[0] for k in K_VALUES}
    picks = {k: _pick(k, traces[k]["devices"]) for k in K_VALUES}
    stored = load("real_deviation")["picks"]
    checks["part4_picks_match_real_deviation"] = all(picks[k] == stored[str(k)] for k in K_VALUES)

    jobs = []
    for m in NEW_DEV:
        for k in K_VALUES:
            jobs.append((MAIN_VARIANT, m, k, "truth", ()))
            for i in picks[k]:
                jobs.append((MAIN_VARIANT, m, k, f"dev:{i}", ((i, 1),)))
    print(f"part 4: {len(jobs)} runs", flush=True)
    res = pmap(_dev_job, jobs, procs=PROCS)
    truth = {(r["mech"], r["k"]): r for r in res if r["tag"] == "truth"}
    by_tag = {(r["mech"], r["k"], int(r["tag"].split(":")[1])): r for r in res if r["tag"] != "truth"}
    recs, dchk = _deviation_records(NEW_DEV, K_VALUES, truth, by_tag, picks, "k")
    checks["part4_device_checks"] = dchk
    checks["part4_capacity_violations"] = sum(r["cap_violations"] for r in res)
    p3 = {(r["mech"], r["k"]): r["util_rate"] for r in part3_runs}
    checks["part4_truth_vs_part3_util_max_abs_diff"] = max(
        abs(truth[(m, k)]["util_rate"] - p3[(m, k)]) for m in NEW_DEV for k in K_VALUES)
    _print_dev("part 4: unilateral static deviation, trace-driven, variant main, PW0127, load 1.0", recs, NEW_DEV)
    summary = {m: dev_stats([r for r in recs if r["mech"] == m]) for m in NEW_DEV}
    print(f"part 4 done in {time.time() - t0:.0f}s")
    return dict(T=T_REAL, variant=MAIN_VARIANT, site=MAIN_SITE, load=1.0, k_values=list(K_VALUES),
                mechanisms=list(NEW_DEV), n_per_trace=N_PICK_DEV, picks={str(k): picks[k] for k in K_VALUES},
                records=recs, summary=summary, cap_violations=checks["part4_capacity_violations"],
                elapsed_s=time.time() - t0)


def main():
    t0 = time.time()
    checks = {}
    p1 = part1(checks)
    p2 = part2(checks)
    p3 = part3(checks)
    p4 = part4(checks, p3["runs"])

    repro = list(checks["part1_reproduction"].values()) + [checks["part3_reproduction"]]
    cap = (sum(r["cap_violations"] for r in p1["runs"] + p3["runs"]) + p2["cap_violations"]
           + p4["cap_violations"] + sum(r["cap_violations"] for r in repro))
    print(f"\ncapacity violations, all runs of this script: {cap}")
    print("sanity checks:")
    for k, v in checks.items():
        print(f"  {k}: {v}")

    path = save("baselines", dict(
        part1=p1, part2=p2, part3=p3, part4=p4, checks=checks, capacity_violations_total=int(cap),
        elapsed_s=time.time() - t0))
    print(f"total {time.time() - t0:.0f}s")
    print("wrote", path)


if __name__ == "__main__":
    main()
