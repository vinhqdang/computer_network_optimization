"""E8: the hindsight slot-switching attack of exp_oracle against three allocation rules (hotspot, T=3000).

Same attack and picks as experiments/exp_oracle.py (trace, pick rule, desired declaration from the truthful
path, hold-down congestion_declaration). Each rule is attacked against its own truthful run, so the gain is
measured with respect to the truthful run under the same rule:
  repay            : Repay as is;
  repay-keep       : a device that stops declaring elastic keeps its deficits frozen and restores them on return;
  repay-keep-sticky: repay-keep plus the incumbents-first admission order.
The keep variants are defined in experiments/exp_continuity.py.

Run as: python -m experiments.exp_oracle_ablation   (writes results/oracle_ablation.json and
paper/tables/oracle_ablation.tex)
"""
import json
import os
import time

import numpy as np

from experiments.common import ROOT, RESULTS, pmap, save
from experiments.exp_continuity import RepayKeep, RepayKeepSticky
from experiments.exp_oracle import MIN_L, N_PICK, SEEDS, T, trace_of
from experiments.exp_switching import congestion_declaration, count_phases
from repay.mechanisms import Repay
from repay.params import Params
from repay.sim import run

TAUS = (1, 5, 20)
RULES = ("repay", "repay-keep", "repay-keep-sticky")
RULE_FACTORY = {
    "repay": lambda p: Repay(p),
    "repay-keep": lambda p: RepayKeep(p),
    "repay-keep-sticky": lambda p: RepayKeepSticky(p),
}


class Recorder:
    """Wrapper with the recording of experiments/exp_oracle.Recorder, around any rule."""

    def __init__(self, inner, watch):
        self.inner = inner
        self.watch = {int(i) for i in watch}
        self.rec = {}

    def reset(self):
        self.inner.reset()
        self.rec = {}

    def allocate(self, view):
        rate = np.asarray(self.inner.allocate(view), float)
        fref = self.inner.last["fluid_ref"]
        for j, (i, dk) in enumerate(zip(np.asarray(view.ids).tolist(), np.asarray(view.decl).tolist())):
            if i in self.watch and dk == 0:
                r = self.rec.setdefault(i, {"ref": np.full(T, np.nan), "rate": np.full(T, np.nan)})
                r["ref"][view.t] = fref[j, 0]
                r["rate"][view.t] = rate[j]
        return rate


def _picks(seed):
    """The same N_PICK devices per seed as exp_oracle (sojourns of at least MIN_L slots, rng 3000+seed)."""
    tr = trace_of(seed)
    elig = [d for d in tr["devices"] if d["cls"] == 0 and min(d["t_dep"], T) - d["t_arr"] >= MIN_L]
    rng = np.random.default_rng(3000 + seed)
    pick_idx = rng.choice(len(elig), size=N_PICK, replace=False)
    out = []
    for k in sorted(pick_idx):
        d = elig[int(k)]
        out.append(dict(dev=int(d["id"]), tier=int(d["tier"]), t_arr=int(d["t_arr"]),
                        tend=int(min(d["t_dep"], T))))
    return out


def _truth_job(job):
    """Truthful run of one rule on one seed, recording the fluid reference and rate of every pick."""
    rule, seed = job
    p = Params()
    tr = trace_of(seed)
    picks = _picks(seed)
    mech = Recorder(RULE_FACTORY[rule](p), [q["dev"] for q in picks])
    r = run(tr, mech, p)
    ids = np.asarray(r["dev"]["id"])
    for q in picks:
        j = int(np.flatnonzero(ids == q["dev"])[0])
        sl = slice(q["t_arr"], q["tend"])
        rec = mech.rec[q["dev"]]
        q["L"] = q["tend"] - q["t_arr"]
        q["vol_truth"] = float(r["dev"]["vol"][j])
        q["ref"] = rec["ref"][sl].tolist()
        q["rate"] = rec["rate"][sl].tolist()
        assert np.all(np.isfinite(q["ref"])) and np.all(np.isfinite(q["rate"]))
    return dict(rule=rule, seed=seed, picks=picks)


def _attack_job(job):
    """One attacked run of one rule with a single device's declaration array."""
    rule, seed, tau, dev, decl = job
    p = Params()
    tr = trace_of(seed)
    r = run(tr, RULE_FACTORY[rule](p), p, declare={int(dev): np.asarray(decl, np.int64)})
    j = int(np.flatnonzero(np.asarray(r["dev"]["id"]) == dev)[0])
    return dict(rule=rule, seed=seed, tau=tau, dev=int(dev), vol=float(r["dev"]["vol"][j]))


def _fmt(x, f):
    return "--" if x is None or x != x else format(x, f)


def main():
    t0 = time.time()
    p = Params()
    truth = pmap(_truth_job, [(r, s) for r in RULES for s in SEEDS], procs=2)
    print(f"truthful runs done in {time.time() - t0:.0f}s", flush=True)

    jobs, desired_of, meta = [], {}, {}
    for tr_ in truth:
        rule, s = tr_["rule"], tr_["seed"]
        for q in tr_["picks"]:
            ref = np.asarray(q["ref"], float)
            rate = np.asarray(q["rate"], float)
            desired = (ref > rate + 1e-9).astype(np.int64)
            meta[(rule, s, q["dev"])] = dict(q, ref=ref, rate=rate, desired=desired)
            for tau in TAUS:
                decl = congestion_declaration(desired, tau)
                jobs.append((rule, s, tau, q["dev"], decl))
    print(f"{len(jobs)} attacked runs queued", flush=True)
    att = pmap(_attack_job, jobs, procs=2)
    print(f"all runs done in {time.time() - t0:.0f}s", flush=True)
    vol_att = {(a["rule"], a["seed"], a["tau"], a["dev"]): a["vol"] for a in att}
    decl_of = {(j[0], j[1], j[2], j[3]): j[4] for j in jobs}

    rows = []
    for (rule, s, dev), m in meta.items():
        for tau in TAUS:
            decl = decl_of[(rule, s, tau, dev)]
            L = m["L"]
            gain = vol_att[(rule, s, tau, dev)] - m["vol_truth"]
            B = p.B(m["tier"], 1)
            K = count_phases(decl)
            rows.append(dict(
                rule=rule, seed=s, dev=dev, tier=m["tier"], tau=tau, L=L, K=K, B=float(B),
                vol_truth=m["vol_truth"], vol_attack=vol_att[(rule, s, tau, dev)], gain=float(gain),
                gain_per_slot=float(gain / L),
                rel_gain_pct=float(100.0 * gain / m["vol_truth"]) if m["vol_truth"] > 0 else float("nan"),
                exceeds_KB=bool(gain > K * B + 1e-9), desired_video_slots=int(m["desired"].sum()),
            ))

    summary = {}
    print("\noracle hold-down sweep, allocation-rule ablation (hotspot, seeds 0 and 1, 20 devices per seed)")
    print(f"{'rule':18s}{'tau':>4s}{'mean g/slot':>13s}{'median':>10s}{'max':>10s}{'mean rel %':>12s}"
          f"{'pos %':>8s}{'mean K':>8s}{'#>K*B':>7s}")
    for rule in RULES:
        for tau in TAUS:
            rs = [r for r in rows if r["rule"] == rule and r["tau"] == tau]
            g = np.array([r["gain_per_slot"] for r in rs])
            rel = np.array([r["rel_gain_pct"] for r in rs])
            Ks = np.array([r["K"] for r in rs], float)
            e = dict(
                n=len(rs), mean_gain_per_slot=float(g.mean()), median_gain_per_slot=float(np.median(g)),
                max_gain_per_slot=float(g.max()), mean_rel_gain_pct=float(np.nanmean(rel)),
                share_positive_pct=float(100.0 * np.mean(g > 0)), mean_K=float(Ks.mean()),
                n_exceed_KB=int(sum(r["exceeds_KB"] for r in rs)),
                mean_gain=float(np.mean([r["gain"] for r in rs])),
            )
            summary[f"{rule}|tau={tau}"] = e
            print(f"{rule:18s}{tau:4d}{e['mean_gain_per_slot']:13.4f}{e['median_gain_per_slot']:10.4f}"
                  f"{e['max_gain_per_slot']:10.4f}{e['mean_rel_gain_pct']:12.2f}"
                  f"{e['share_positive_pct']:8.1f}{e['mean_K']:8.2f}{e['n_exceed_KB']:7d}")

    # Sanity: plain repay must reproduce results/oracle.json (same runs, same picks).
    print("\nsanity against results/oracle.json")
    ora_path = os.path.join(RESULTS, "oracle.json")
    checks = {}
    if os.path.exists(ora_path):
        with open(ora_path) as f:
            ora = json.load(f)
        worst_vol, worst_des, worst_mean = 0.0, 0, 0.0
        for s in SEEDS:
            ref_picks = ora["picks"][str(s)]
            for q in ref_picks:
                m = meta[("repay", s, q["dev"])]
                worst_vol = max(worst_vol, abs(m["vol_truth"] - q["vol_truth"]))
                worst_des = max(worst_des, abs(int(m["desired"].sum()) - int(q["desired_video_slots"])))
        for tau in TAUS:
            mine = summary[f"repay|tau={tau}"]["mean_gain_per_slot"]
            theirs = ora["summary"][f"tau={tau}"]["mean_gain_per_slot"]
            checks[f"tau={tau}"] = dict(ablation=mine, oracle_json=theirs)
            print(f"  tau={tau:2d}: repay mean gain per slot {mine:.4f} (oracle.json {theirs:.4f})")
        print(f"  truthful volume max |diff| = {worst_vol:.2e}; desired-video slot count max |diff| = {worst_des}")
        checks["truth_vol_max_diff"] = float(worst_vol)
        checks["desired_slots_max_diff"] = int(worst_des)

    tex_rows = []
    names = {"repay": "REPAY", "repay-keep": "REPAY-keep", "repay-keep-sticky": "REPAY-keep-sticky"}
    for rule in RULES:
        for tau in TAUS:
            e = summary[f"{rule}|tau={tau}"]
            tex_rows.append(f"{names[rule]} & {tau} & {e['mean_gain_per_slot']:.3f} & "
                            f"{e['max_gain_per_slot']:.3f} & {e['share_positive_pct']:.1f} \\\\")
        if rule != RULES[-1]:
            tex_rows.append("\\midrule")
    tex = "\n".join([
        "% Source: results/oracle_ablation.json, scenario hotspot, seeds 0 and 1, 20 devices per seed",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Rule & Hold-down $\\tau$ & Mean gain per slot (Mbit/s) & Max gain per slot (Mbit/s) & "
        "Share gaining (\\%) \\\\",
        "\\midrule",
        *tex_rows,
        "\\bottomrule",
        "\\end{tabular}",
        "",
    ])
    tex_path = os.path.join(ROOT, "paper", "tables", "oracle_ablation.tex")
    with open(tex_path, "w") as f:
        f.write(tex)

    save("oracle_ablation", dict(
        T=T, scenario="hotspot", seeds=list(SEEDS), taus=list(TAUS), rules=list(RULES), n_pick=N_PICK,
        min_sojourn=MIN_L, summary=summary, records=rows, sanity=checks,
        elapsed_s=time.time() - t0,
    ))
    print(f"\nwrote {tex_path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
