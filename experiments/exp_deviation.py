"""E4(a) on six hotspot traces: unilateral static deviation (a true elastic device declares video for its whole sojourn).

Same protocol as part (a) of experiments/exp_strategic.py: per trace, 30 true-elastic devices with at least 60
slots are picked with numpy Generator(1000 + seed) and each is rerun with declare={id: 1}. Seeds 0 and 1 reuse the
per-device records stored in results/strategic.json after a fresh reproduction check on one (mechanism, device)
pair per seed; seeds 2 to 5 are run fresh. If a reproduction check fails, that seed is rerun fresh.

Run as: python -m experiments.exp_deviation   (writes results/deviation.json)
"""
import time

import numpy as np

from experiments.common import LABELS, load, pmap, save
from experiments.exp_strategic import N_PICK_DEV, T, _by_id, _dev_table, _worker, trace_of
from repay.params import Params

MECHS = ("repay", "repay-e", "no-debt", "dpp", "priority", "wfq", "pf", "credit")
REPAY_FAMILY = ("repay", "repay-e", "no-debt")
SEEDS = (0, 1, 2, 3, 4, 5)
REUSE_SEEDS = (0, 1)
TIER_NAMES = ("Free", "Premium", "PAYG")
TOL = 1e-6
N_BOOT = 2000
BOOT_SEED = 7
PROCS = 4


def pick_devices(s, table):
    """Deviation sample for a seed, identical to exp_strategic part (a)."""
    ids, cls, tier, L = table
    elig = ids[(cls == 0) & (L >= 60)]
    rng = np.random.default_rng(1000 + s)
    return sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))


def full_jobs(seeds, picks):
    """Truthful run and one deviation run per picked device, for each mechanism and seed."""
    jobs = []
    for s in seeds:
        for m in MECHS:
            jobs.append((m, s, "truth", ()))
            for i in picks[s]:
                jobs.append((m, s, f"dev:{i}", ((i, 1),)))
    return jobs


def check_jobs(s, picks):
    """Reproduction check: repay truthful run and the first picked device's deviation run."""
    i = picks[s][0]
    return [("repay", s, "truth", ()), ("repay", s, f"dev:{i}", ((i, 1),))]


def make_record(m, s, i, tier, L, ell, vt, vd, max_env, source, P):
    gain = vd - vt
    rec = dict(mech=m, seed=s, dev=i, tier=tier, L=L, ell=ell, vol_truth=vt, vol_dev=vd, gain=gain,
               gain_per_slot=gain / L, rel_gain=(gain / vt) if vt > 0 else None,
               max_env_truth=max_env, B=None, source=source)
    if m in REPAY_FAMILY:
        rec["B"] = float(P.B(tier, 1))
    return rec


def fresh_records(s, res, table, picks_s, ell_s, P):
    ids, cls, tier, L = table
    recs = []
    for m in MECHS:
        T0 = res[(m, s, "truth")]
        idx0 = _by_id(T0["dev"])
        for i in picks_s:
            Rd = res[(m, s, f"dev:{i}")]
            j0 = idx0[i]
            jd = _by_id(Rd["dev"])[i]
            recs.append(make_record(
                m, s, i, int(T0["dev"]["tier"][j0]), int(T0["dev"]["L"][j0]), ell_s[i],
                float(T0["dev"]["vol"][j0]), float(Rd["dev"]["vol"][jd]),
                float(T0["dev"]["max_env"][j0]), "fresh", P))
    return recs


def stored_records(s, stored_dev, table, ell_s, P):
    ids, cls, tier, L = table
    Lmap = {int(i): int(l) for i, l in zip(ids, L)}
    recs = []
    for r in stored_dev:
        if r["seed"] != s:
            continue
        assert Lmap[r["dev"]] == r["L"], f"slot count mismatch for seed {s}, device {r['dev']}"
        recs.append(make_record(
            r["mech"], s, r["dev"], r["tier"], r["L"], ell_s[r["dev"]], r["vol_truth"], r["vol_dev"],
            r["max_env_truth"], "stored", P))
    return recs


def check_reproduction(s, res, stored_dev, picks_s):
    i = picks_s[0]
    T0 = res[("repay", s, "truth")]
    Rd = res[("repay", s, f"dev:{i}")]
    j0 = _by_id(T0["dev"])[i]
    jd = _by_id(Rd["dev"])[i]
    st = next(r for r in stored_dev if r["mech"] == "repay" and r["seed"] == s and r["dev"] == i)
    vt = float(T0["dev"]["vol"][j0])
    vd = float(Rd["dev"]["vol"][jd])
    err = max(abs(vt - st["vol_truth"]), abs(vd - st["vol_dev"]))
    return dict(mech="repay", dev=i, vol_truth_fresh=vt, vol_truth_stored=st["vol_truth"],
                vol_dev_fresh=vd, vol_dev_stored=st["vol_dev"], max_abs_err=err, passed=bool(err <= TOL))


def _triple(rs):
    """(median rel gain, mean rel gain, pooled volume gain) for a list of records; NaN if undefined."""
    rel = [r["rel_gain"] for r in rs if r["rel_gain"] is not None]
    vt = sum(r["vol_truth"] for r in rs)
    vd = sum(r["vol_dev"] for r in rs)
    if not rel or vt <= 0:
        return (np.nan, np.nan, np.nan)
    return (float(np.median(rel)), float(np.mean(rel)), (vd - vt) / vt)


def stats(rs):
    """Full summary statistics for a list of records (fractions for relative gains)."""
    med, mean, pooled = _triple(rs)
    gps = np.array([r["gain_per_slot"] for r in rs], float)
    gain = np.array([r["gain"] for r in rs], float)
    return dict(n=len(rs), median_rel=med, mean_rel=mean, pooled=pooled,
                mean_gps=float(gps.mean()), median_gps=float(np.median(gps)),
                p95_gps=float(np.percentile(gps, 95)), share_gaining=float(np.mean(gain > 0)))


def boot_ci(recs_by_seed, draws):
    """95% percentile CIs from cluster bootstrap over traces (draws index into SEEDS)."""
    vals = np.array([_triple([r for k in idx for r in recs_by_seed[SEEDS[k]]]) for idx in draws], float)
    lo = np.nanpercentile(vals, 2.5, axis=0)
    hi = np.nanpercentile(vals, 97.5, axis=0)
    return {"median_rel": (float(lo[0]), float(hi[0])), "mean_rel": (float(lo[1]), float(hi[1])),
            "pooled": (float(lo[2]), float(hi[2]))}


def group_by_seed(rs):
    return {s: [r for r in rs if r["seed"] == s] for s in SEEDS}


def with_ci(rs, draws):
    st = stats(rs)
    ci = boot_ci(group_by_seed(rs), draws)
    out = dict(n=st["n"],
               median_rel_gain_pct=100 * st["median_rel"], median_rel_ci_pct=[100 * x for x in ci["median_rel"]],
               mean_rel_gain_pct=100 * st["mean_rel"], mean_rel_ci_pct=[100 * x for x in ci["mean_rel"]],
               pooled_gain_pct=100 * st["pooled"], pooled_ci_pct=[100 * x for x in ci["pooled"]],
               mean_gain_per_slot=st["mean_gps"], median_gain_per_slot=st["median_gps"],
               p95_gain_per_slot=st["p95_gps"], share_gaining_pct=100 * st["share_gaining"])
    return out


def print_summary(title, rows):
    print(f"\n{title}")
    print(f"{'mechanism':<10s} {'n':>4s} {'median rel %':>24s} {'pooled vol %':>24s} {'mean rel %':>24s} {'gain>0 %':>9s}")
    for name, s in rows:
        def ci(v, c):
            return f"{v:8.2f} [{c[0]:7.2f},{c[1]:7.2f}]"
        print(f"{name:<10s} {s['n']:4d} {ci(s['median_rel_gain_pct'], s['median_rel_ci_pct'])} "
              f"{ci(s['pooled_gain_pct'], s['pooled_ci_pct'])} {ci(s['mean_rel_gain_pct'], s['mean_rel_ci_pct'])} "
              f"{s['share_gaining_pct']:9.1f}")
    print(f"\n{'mechanism':<10s} {'mean Mbit/s':>12s} {'median Mbit/s':>14s} {'p95 Mbit/s':>12s}")
    for name, s in rows:
        print(f"{name:<10s} {s['mean_gain_per_slot']:12.4f} {s['median_gain_per_slot']:14.4f} "
              f"{s['p95_gain_per_slot']:12.4f}")


def summarise(recs):
    """Print and return the summaries of a list of per-device records."""
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.integers(0, len(SEEDS), size=(N_BOOT, len(SEEDS)))

    summary, tier_summary, gain_over_B = {}, {}, {}
    rows = []
    for m in MECHS:
        rm = [r for r in recs if r["mech"] == m]
        summary[m] = with_ci(rm, draws)
        rows.append((LABELS[m], summary[m]))
    print_summary("Unilateral static deviation over 180 devices (six traces); CIs are 95% cluster bootstrap",
                  rows)

    rep = [r for r in recs if r["mech"] == "repay"]
    trows = []
    for g, name in enumerate(TIER_NAMES):
        rg = [r for r in rep if r["tier"] == g]
        tier_summary[name] = with_ci(rg, draws)  # trace bootstrap restricted to this tier
        trows.append((name, tier_summary[name]))
    print_summary("REPAY by tier (devices of the tier only; CIs from trace bootstrap restricted to the tier)", trows)

    print("\nGain over bound B(g,1) (volume gain / B), per mechanism of the REPAY family")
    for m in REPAY_FAMILY:
        rm = [r for r in recs if r["mech"] == m]
        ratios = np.array([r["gain"] / r["B"] for r in rm])
        k = int(np.argmax(ratios))
        best = rm[k]
        gain_over_B[m] = dict(max_gain_over_B=float(ratios.max()), n_above_1=int(np.sum(ratios > 1.0)),
                              n=len(rm), argmax=dict(seed=best["seed"], dev=best["dev"], tier=best["tier"],
                                                     gain=best["gain"], B=best["B"]))
        print(f"{LABELS[m]:<10s} max gain/B = {ratios.max():.4f} (seed {best['seed']}, device {best['dev']}, "
              f"tier {TIER_NAMES[best['tier']]}); devices with gain > B: {int(np.sum(ratios > 1.0))} of {len(rm)}")
    return summary, tier_summary, gain_over_B


def main():
    t0 = time.time()
    P = Params()
    stored = load("strategic")
    stored_dev = stored["deviation"]
    tables = {s: _dev_table(trace_of(s)) for s in SEEDS}
    ell = {s: {int(d["id"]): float(d["ell"]) for d in trace_of(s)["devices"]} for s in SEEDS}
    picks = {s: pick_devices(s, tables[s]) for s in SEEDS}
    for s in REUSE_SEEDS:
        assert picks[s] == sorted(stored["picks_deviation"][str(s)]), f"seed {s}: picks differ from strategic.json"

    fresh_seeds = [s for s in SEEDS if s not in REUSE_SEEDS]
    jobs = []
    for s in REUSE_SEEDS:
        jobs += check_jobs(s, picks)
    jobs += full_jobs(fresh_seeds, picks)
    print(f"{len(jobs)} runs queued (reproduction checks and seeds {fresh_seeds})", flush=True)
    res = {(r["mech"], r["seed"], r["tag"]): r for r in pmap(_worker, jobs, procs=PROCS)}
    print(f"phase 1 done in {time.time() - t0:.0f}s", flush=True)

    checks = {s: check_reproduction(s, res, stored_dev, picks[s]) for s in REUSE_SEEDS}
    reused = {s for s in REUSE_SEEDS if checks[s]["passed"]}
    fallback = [s for s in REUSE_SEEDS if s not in reused]
    for s in REUSE_SEEDS:
        c = checks[s]
        print(f"reproduction check seed {s} ({c['mech']}, device {c['dev']}): "
              f"truth {c['vol_truth_fresh']:.9f} vs {c['vol_truth_stored']:.9f}, "
              f"deviation {c['vol_dev_fresh']:.9f} vs {c['vol_dev_stored']:.9f}, "
              f"max abs err {c['max_abs_err']:.2e} -> {'PASS' if c['passed'] else 'FAIL'}", flush=True)
    if fallback:
        print(f"reuse refused for seeds {fallback}; running them fresh", flush=True)
        res.update({(r["mech"], r["seed"], r["tag"]): r
                    for r in pmap(_worker, full_jobs(fallback, picks), procs=PROCS)})

    recs = []
    for s in SEEDS:
        if s in reused:
            recs += stored_records(s, stored_dev, tables[s], ell[s], P)
        else:
            recs += fresh_records(s, res, tables[s], picks[s], ell[s], P)
    print(f"{len(recs)} records; runs done in {time.time() - t0:.0f}s", flush=True)

    summary, tier_summary, gain_over_B = summarise(recs)

    print("\nReuse check (seeds reused from strategic.json):")
    for s in REUSE_SEEDS:
        print(f"  seed {s}: {'reused' if s in reused else 'fresh (check failed)'}; max abs err {checks[s]['max_abs_err']:.2e}")
    print(f"total {time.time() - t0:.0f}s")

    save("deviation", dict(
        T=T, scenario="hotspot", seeds=list(SEEDS), mechanisms=list(MECHS), tiers=list(TIER_NAMES),
        picks={str(s): picks[s] for s in SEEDS},
        reuse={str(s): dict(reused=(s in reused), check=checks[s]) for s in REUSE_SEEDS},
        bootstrap=dict(n_boot=N_BOOT, seed=BOOT_SEED, resample="traces with replacement",
                       ci="95% percentile interval"),
        records=recs, summary=summary, repay_tier_summary=tier_summary, gain_over_B=gain_over_B,
    ))


if __name__ == "__main__":
    main()
