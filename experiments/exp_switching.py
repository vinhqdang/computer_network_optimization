"""E5: dynamic declarations (switching attack) against the hold-down tau on the hotspot trace.

Attacker: a true elastic device wants to declare video in slots where C_t is below the 40th percentile of
the trace's capacity and elastic otherwise; it may change its declaration only if at least tau slots have
passed since its last change. Static 'always video' is included for comparison.

Run as: python -m experiments.exp_switching   (writes results/switching.json)
"""
import functools
import time

import numpy as np

from experiments.common import LABELS, MECHS, mean_ci, pmap, save
from repay.params import Params
from repay.sim import make_trace, run

T = 3000
SEEDS = (0, 1)
MECH_NAMES = ("repay", "dpp")
N_PICK = 20
MIN_L = 200
TAUS = (1, 5, 20, 60, 200)
STRATS = [f"tau={t}" for t in TAUS] + ["always-video"]


@functools.lru_cache(maxsize=4)
def trace_of(seed):
    """Hotspot trace for a seed (cached per process, never pickled)."""
    return make_trace("hotspot", T, seed)


def congestion_declaration(desired, tau):
    """Declared classes for a sojourn given the desired class per slot and hold-down tau."""
    out = np.empty(desired.size, np.int64)
    cur, last = int(desired[0]), 0
    out[0] = cur
    for k in range(1, desired.size):
        if desired[k] != cur and k - last >= tau:
            cur, last = int(desired[k]), k
        out[k] = cur
    return out


def count_phases(decl):
    """Number of maximal video-declared (1) phases."""
    on = (np.asarray(decl) == 1).astype(np.int64)
    return int(np.sum(np.diff(np.concatenate([[0], on])) == 1))


def _worker(job):
    """One run with optional per-device declaration arrays (module-level for pmap)."""
    mech, seed, tag, dev_id, decl = job
    p = Params()
    tr = trace_of(seed)
    declare = None if dev_id is None else {int(dev_id): np.asarray(decl, np.int64)}
    r = run(tr, MECHS[mech](p), p, declare=declare)
    dev = {k: np.asarray(v).tolist() for k, v in r["dev"].items()}
    return dict(mech=mech, seed=seed, tag=tag, dev_id=dev_id, util_rate=r["util_rate"], dev=dev)


def main():
    t0 = time.time()
    p = Params()
    picks, sojourn = {}, {}
    plan = []
    for s in SEEDS:
        tr = trace_of(s)
        C = np.asarray(tr["C"], float)
        p40 = float(np.percentile(C, 40))
        elig = []
        for d in tr["devices"]:
            tend = min(d["t_dep"], T)
            if d["cls"] == 0 and tend - d["t_arr"] >= MIN_L:
                elig.append(d)
        rng = np.random.default_rng(3000 + s)
        pick_idx = rng.choice(len(elig), size=N_PICK, replace=False)
        picks[s] = []
        for k in sorted(pick_idx):
            d = elig[int(k)]
            tend = min(d["t_dep"], T)
            t_arr = d["t_arr"]
            L = tend - t_arr
            desired = (C[t_arr:tend] < p40).astype(np.int64)  # 1 = video when congestion
            picks[s].append(dict(dev=int(d["id"]), tier=int(d["tier"]), L=int(L)))
            strategies = {f"tau={tau}": congestion_declaration(desired, tau) for tau in TAUS}
            strategies["always-video"] = np.ones(L, np.int64)
            sojourn[(s, int(d["id"]))] = strategies
            for m in MECH_NAMES:
                for name, decl in strategies.items():
                    plan.append((m, s, name, int(d["id"]), decl))
        for m in MECH_NAMES:
            plan.append((m, s, "truth", None, None))
    print(f"{len(plan)} runs queued", flush=True)
    res = pmap(_worker, plan, procs=4)
    print(f"runs done in {time.time() - t0:.0f}s", flush=True)

    truth = {(r["mech"], r["seed"]): r for r in res if r["tag"] == "truth"}
    rows = []
    for r in res:
        if r["tag"] == "truth":
            continue
        m, s, name, dev_id = r["mech"], r["seed"], r["tag"], r["dev_id"]
        T0 = truth[(m, s)]["dev"]
        j0 = next(j for j, i in enumerate(T0["id"]) if i == dev_id)
        jd = next(j for j, i in enumerate(r["dev"]["id"]) if i == dev_id)
        decl = sojourn[(s, dev_id)][name]
        L = int(T0["L"][j0])
        tier = int(T0["tier"][j0])
        gain = float(r["dev"]["vol"][jd]) - float(T0["vol"][j0])
        K = count_phases(decl)
        row = dict(mech=m, seed=s, dev=dev_id, tier=tier, strategy=name, L=L, K=K,
                   vol_truth=float(T0["vol"][j0]), vol_dev=float(r["dev"]["vol"][jd]),
                   gain=gain, gain_per_slot=gain / L, share_video=float(np.mean(decl == 1)))
        if m == "repay":
            row["B"] = p.B(tier, 1)
            row["KB"] = K * p.B(tier, 1)
        rows.append(row)

    summary = {}
    print("\nswitching attack: gain per slot (Mbit/s) over truthful; K = video phases; bound K*B for REPAY")
    print(f"{'mech':10s} {'strategy':14s} {'mean':>9s} {'max':>9s} {'mean K':>7s} {'max K':>6s} {'K*B viol':>9s}")
    for m in MECH_NAMES:
        summary[m] = {}
        for name in STRATS:
            rs = [r for r in rows if r["mech"] == m and r["strategy"] == name]
            g = np.array([r["gain_per_slot"] for r in rs])
            Ks = np.array([r["K"] for r in rs])
            gm = [float(np.mean([r["gain_per_slot"] for r in rs if r["seed"] == s])) for s in SEEDS]
            entry = dict(n=len(rs), mean_gain_per_slot=float(g.mean()), max_gain_per_slot=float(g.max()),
                         mean_gain=float(np.mean([r["gain"] for r in rs])),
                         max_gain=float(np.max([r["gain"] for r in rs])),
                         seed_means=gm, mean_K=float(Ks.mean()), max_K=int(Ks.max()))
            if m == "repay":
                viol = sum(1 for r in rs if r["gain"] > r["KB"] + 1e-9)
                entry["KB_violations"] = int(viol)
                entry["max_gain_over_KB"] = float(max(r["gain"] / r["KB"] for r in rs if r["KB"] > 0))
            summary[m][name] = entry
            extra = f"{entry.get('KB_violations', '-'):>9}" if m == "repay" else f"{'-':>9s}"
            print(f"{LABELS[m]:10s} {name:14s} {entry['mean_gain_per_slot']:9.4f} {entry['max_gain_per_slot']:9.4f} "
                  f"{entry['mean_K']:7.2f} {entry['max_K']:6d} {extra}")

    print("\nper-seed mean gain per slot (CI over seeds):")
    for m in MECH_NAMES:
        for name in STRATS:
            mu, hw = mean_ci(summary[m][name]["seed_means"])
            print(f"  {LABELS[m]:10s} {name:14s} {mu:9.4f} +- {hw:.4f}")

    save("switching", dict(
        T=T, scenario="hotspot", seeds=list(SEEDS), mechanisms=list(MECH_NAMES), taus=list(TAUS),
        strategies=STRATS, quantile_C=0.4, picks=picks, records=rows, summary=summary,
    ))
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
