"""E6: hindsight ("oracle") slot-switching attacker against REPAY, hold-down sweep on the hotspot trace.

Step 1: a truthful REPAY run per seed (Recorder wrapper) stores, for each picked device, the fluid video
reference and the allocated rate in every slot of its sojourn.
Step 2: the oracle desire declares video (1) in slot t iff reference_t > rate_t + 1e-9 on the truthful path,
elastic (0) otherwise; the hold-down tau (as in exp_switching) limits how often the declaration may change.
The attacked run is compared against the truthful run.

Run as: python -m experiments.exp_oracle   (writes results/oracle.json and paper/tables/oracle.tex)
"""
import functools
import os
import time

import numpy as np

from experiments.common import ROOT, pmap, save
from experiments.exp_switching import congestion_declaration, count_phases
from repay.mechanisms import Repay
from repay.params import Params
from repay.sim import make_trace, run

T = 3000
SEEDS = (0, 1, 2, 3, 4, 5)
N_PICK = 20
MIN_L = 200
TAUS = (1, 5, 20, 60)


@functools.lru_cache(maxsize=4)
def trace_of(seed):
    """Hotspot trace for a seed (cached per process, never pickled)."""
    return make_trace("hotspot", T, seed)


class Recorder(Repay):
    """REPAY that records, for watched elastic devices, the fluid video reference and the rate per slot."""

    def __init__(self, params, watch):
        super().__init__(params)
        self.watch = {int(i) for i in watch}
        self.rec = {}

    def allocate(self, view):
        rate = super().allocate(view)
        fref = self.last["fluid_ref"]
        for j, (i, dk) in enumerate(zip(np.asarray(view.ids).tolist(), np.asarray(view.decl).tolist())):
            if i in self.watch and dk == 0:
                r = self.rec.setdefault(i, {"ref": np.full(T, np.nan), "rate": np.full(T, np.nan)})
                r["ref"][view.t] = fref[j, 0]
                r["rate"][view.t] = rate[j]
        return rate


def _truth_job(seed):
    """Build the trace, pick the devices as in exp_switching, and run the recorded truthful path."""
    p = Params()
    tr = trace_of(seed)
    elig = [d for d in tr["devices"] if d["cls"] == 0 and min(d["t_dep"], T) - d["t_arr"] >= MIN_L]
    rng = np.random.default_rng(3000 + seed)
    pick_idx = rng.choice(len(elig), size=N_PICK, replace=False)
    picks = []
    for k in sorted(pick_idx):
        d = elig[int(k)]
        picks.append(dict(dev=int(d["id"]), tier=int(d["tier"]), t_arr=int(d["t_arr"]),
                          tend=int(min(d["t_dep"], T))))
    mech = Recorder(p, [q["dev"] for q in picks])
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
    return dict(seed=seed, picks=picks)


def _attack_job(job):
    """One attacked run with a single device's declaration array."""
    seed, tau, dev, decl = job
    p = Params()
    tr = trace_of(seed)
    r = run(tr, Repay(p), p, declare={int(dev): np.asarray(decl, np.int64)})
    j = int(np.flatnonzero(np.asarray(r["dev"]["id"]) == dev)[0])
    return dict(seed=seed, tau=tau, dev=int(dev), vol=float(r["dev"]["vol"][j]))


def main():
    t0 = time.time()
    p = Params()
    truth = pmap(_truth_job, list(SEEDS), procs=2)
    print(f"truthful runs done in {time.time() - t0:.0f}s", flush=True)

    jobs, decls, meta = [], {}, {}
    for tr_ in truth:
        s = tr_["seed"]
        for q in tr_["picks"]:
            ref = np.asarray(q["ref"], float)
            rate = np.asarray(q["rate"], float)
            desired = (ref > rate + 1e-9).astype(np.int64)
            meta[(s, q["dev"])] = dict(q, ref=ref, rate=rate, desired=desired)
            for tau in TAUS:
                decl = congestion_declaration(desired, tau)
                decls[(s, tau, q["dev"])] = decl
                jobs.append((s, tau, q["dev"], decl))
    print(f"{len(jobs)} attacked runs queued", flush=True)
    att = pmap(_attack_job, jobs, procs=2)
    print(f"all runs done in {time.time() - t0:.0f}s", flush=True)
    vol_att = {(a["seed"], a["tau"], a["dev"]): a["vol"] for a in att}

    rows = []
    for (s, dev), m in meta.items():
        for tau in TAUS:
            decl = decls[(s, tau, dev)]
            L = m["L"]
            gain = vol_att[(s, tau, dev)] - m["vol_truth"]
            K = count_phases(decl)
            B = p.B(m["tier"], 1)
            on = decl == 1
            pt = float(np.sum(np.maximum(m["ref"] - m["rate"], 0.0)[on]))
            rows.append(dict(
                seed=s, dev=dev, tier=m["tier"], tau=tau, L=L, K=K, B=float(B), KB=float(K * B),
                vol_truth=m["vol_truth"], vol_attack=vol_att[(s, tau, dev)], gain=float(gain),
                gain_per_slot=float(gain / L),
                rel_gain_pct=float(100.0 * gain / m["vol_truth"]) if m["vol_truth"] > 0 else float("nan"),
                exceeds_KB=bool(gain > K * B + 1e-9), price_taking_pred=pt, share_video=float(on.mean()),
            ))

    summary = {}
    print("\noracle hold-down sweep (hotspot, REPAY, six traces: seeds 0 to 5, 20 devices per trace, 120 devices)")
    print(f"{'tau':>4s} {'mean g/slot':>12s} {'median':>9s} {'max':>9s} {'mean rel %':>11s} "
          f"{'pos %':>7s} {'mean K':>7s} {'#>K*B':>6s} {'PT pred':>9s}")
    for tau in TAUS:
        rs = [r for r in rows if r["tau"] == tau]
        g = np.array([r["gain_per_slot"] for r in rs])
        rel = np.array([r["rel_gain_pct"] for r in rs])
        Ks = np.array([r["K"] for r in rs], float)
        entry = dict(
            n=len(rs), mean_gain_per_slot=float(g.mean()), median_gain_per_slot=float(np.median(g)),
            max_gain_per_slot=float(g.max()), mean_rel_gain_pct=float(np.nanmean(rel)),
            share_positive_pct=float(100.0 * np.mean(g > 0)), mean_K=float(Ks.mean()),
            n_exceed_KB=int(sum(r["exceeds_KB"] for r in rs)),
            mean_price_taking_pred=float(np.mean([r["price_taking_pred"] for r in rs])),
            mean_gain=float(np.mean([r["gain"] for r in rs])),
        )
        summary[f"tau={tau}"] = entry
        print(f"{tau:4d} {entry['mean_gain_per_slot']:12.4f} {entry['median_gain_per_slot']:9.4f} "
              f"{entry['max_gain_per_slot']:9.4f} {entry['mean_rel_gain_pct']:11.2f} "
              f"{entry['share_positive_pct']:7.1f} {entry['mean_K']:7.2f} {entry['n_exceed_KB']:6d} "
              f"{entry['mean_price_taking_pred']:9.3f}")

    picks_out = {}
    for tr_ in truth:
        s = tr_["seed"]
        picks_out[str(s)] = [
            dict({k: v for k, v in q.items() if k not in ("ref", "rate")},
                 desired_video_slots=int(meta[(s, q["dev"])]["desired"].sum()))
            for q in tr_["picks"]
        ]

    tex_rows = []
    for tau in TAUS:
        e = summary[f"tau={tau}"]
        rel = "--" if np.isnan(e["mean_rel_gain_pct"]) else f"{e['mean_rel_gain_pct']:.2f}"
        tex_rows.append(f"{tau} & {e['mean_gain_per_slot']:.3f} & {e['max_gain_per_slot']:.3f} & {rel} & "
                        f"{e['share_positive_pct']:.1f} & {e['mean_K']:.2f} \\\\")
    tex = "\n".join([
        "% Source: results/oracle.json, scenario hotspot, six traces (seeds 0 to 5), 20 devices per trace, 120 devices in total",
        "\\begin{tabular}{rrrrrr}",
        "\\toprule",
        "Hold-down $\\tau$ & Mean gain per slot (Mbit/s) & Max gain per slot (Mbit/s) & "
        "Mean relative gain (\\%) & Share with positive gain (\\%) & Mean video phases \\\\",
        "\\midrule",
        *tex_rows,
        "\\bottomrule",
        "\\end{tabular}",
        "",
    ])
    tex_path = os.path.join(ROOT, "paper", "tables", "oracle.tex")
    with open(tex_path, "w") as f:
        f.write(tex)

    save("oracle", dict(
        T=T, scenario="hotspot", seeds=list(SEEDS), taus=list(TAUS), n_pick=N_PICK, min_sojourn=MIN_L,
        picks=picks_out, records=rows, summary=summary,
    ))
    print(f"\nwrote {tex_path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
