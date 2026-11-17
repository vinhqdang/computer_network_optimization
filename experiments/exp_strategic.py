"""E4: strategic misreporting of the declared class on the hotspot trace.

(a) exact unilateral static deviation (true elastic declares video for its whole sojourn),
(b) collapse curves (fraction rho of true elastic devices misreport), and
(c) reverse deviation (true video declares elastic).

Run as: python -m experiments.exp_strategic   (writes results/strategic.json)
"""
import functools
import time

import numpy as np

from experiments.common import LABELS, MECHS, mean_ci, pmap, save
from repay.params import Params
from repay.sim import make_trace, run

T = 3000
MECH_NAMES = ["repay", "repay-e", "no-debt", "dpp", "priority", "wfq", "pf", "credit"]
REPAY_FAMILY = ("repay", "repay-e", "no-debt")
N_PICK_DEV = 30
DEV_SEEDS = (0, 1)
RHOS = (0.0, 0.25, 0.5, 0.75, 1.0)
COLL_SEEDS = (0, 1, 2, 3)
N_PICK_REV = 20
REV_MECHS = ("repay", "dpp")
REV_SEEDS = (0, 1)


@functools.lru_cache(maxsize=4)
def trace_of(seed):
    """Hotspot trace for a seed (cached per process, never pickled)."""
    return make_trace("hotspot", T, seed)


def _dev_table(tr):
    devs = tr["devices"]
    ids = np.array([d["id"] for d in devs], np.int64)
    cls = np.array([d["cls"] for d in devs], np.int64)
    tier = np.array([d["tier"] for d in devs], np.int64)
    L = np.array([min(d["t_dep"], T) - d["t_arr"] for d in devs], np.int64)
    return ids, cls, tier, L


def _worker(job):
    """One simulation run; returns the per-device record arrays (module-level for pmap)."""
    mech, seed, tag, decl_items = job
    p = Params()
    tr = trace_of(seed)
    declare = {int(k): int(v) for k, v in decl_items} if decl_items else None
    r = run(tr, MECHS[mech](p), p, declare=declare)
    dev = {k: np.asarray(v).tolist() for k, v in r["dev"].items()}
    return dict(mech=mech, seed=seed, tag=tag, util_rate=r["util_rate"], dev=dev)


def _by_id(dev):
    """Map device id -> row index in a run's per-device arrays."""
    return {int(i): j for j, i in enumerate(dev["id"])}


def main():
    t0 = time.time()
    p = Params()
    picks_dev, picks_rev = {}, {}
    tables = {}
    for s in sorted(set(DEV_SEEDS) | set(COLL_SEEDS) | set(REV_SEEDS)):
        tables[s] = _dev_table(trace_of(s))
    for s in DEV_SEEDS:
        ids, cls, tier, L = tables[s]
        elig = ids[(cls == 0) & (L >= 60)]
        rng = np.random.default_rng(1000 + s)
        picks_dev[s] = sorted(int(i) for i in rng.choice(elig, size=N_PICK_DEV, replace=False))
    for s in REV_SEEDS:
        ids, cls, tier, L = tables[s]
        elig = ids[(cls == 1) & (L >= 60)]
        rng = np.random.default_rng(4000 + s)
        picks_rev[s] = sorted(int(i) for i in rng.choice(elig, size=N_PICK_REV, replace=False))
    # nested misreporter sets for the collapse curves (fixed permutation of true elastic ids per seed)
    perm, mis_sets = {}, {}
    for s in COLL_SEEDS:
        ids, cls, tier, L = tables[s]
        el = ids[cls == 0]
        rng = np.random.default_rng(2000 + s)
        perm[s] = rng.permutation(el)
        for rho in RHOS:
            k = int(round(rho * el.size))
            mis_sets[(rho, s)] = sorted(int(i) for i in perm[s][:k])

    jobs = []
    truth_seeds = sorted(set(DEV_SEEDS) | set(COLL_SEEDS) | set(REV_SEEDS))
    for m in MECH_NAMES:
        for s in truth_seeds:
            jobs.append((m, s, "truth", ()))
    for m in MECH_NAMES:
        for s in DEV_SEEDS:
            for i in picks_dev[s]:
                jobs.append((m, s, f"dev:{i}", ((i, 1),)))
    for m in MECH_NAMES:
        for rho in RHOS[1:]:
            for s in COLL_SEEDS:
                items = tuple((i, 1) for i in mis_sets[(rho, s)])
                jobs.append((m, s, f"coll:{rho}", items))
    for m in REV_MECHS:
        for s in REV_SEEDS:
            for i in picks_rev[s]:
                jobs.append((m, s, f"rev:{i}", ((i, 0),)))
    print(f"{len(jobs)} runs queued", flush=True)
    res = pmap(_worker, jobs, procs=4)
    print(f"runs done in {time.time() - t0:.0f}s", flush=True)

    truth = {(r["mech"], r["seed"]): r for r in res if r["tag"] == "truth"}

    # (a) exact unilateral static deviation
    dev_rows = []
    for m in MECH_NAMES:
        for s in DEV_SEEDS:
            T0 = truth[(m, s)]
            idx0 = _by_id(T0["dev"])
            for i in picks_dev[s]:
                r = next(r for r in res if r["mech"] == m and r["seed"] == s and r["tag"] == f"dev:{i}")
                j0 = idx0[i]
                jd = _by_id(r["dev"])[i]
                Li = int(T0["dev"]["L"][j0])
                vt = float(T0["dev"]["vol"][j0])
                vd = float(r["dev"]["vol"][jd])
                gain = vd - vt
                row = dict(mech=m, seed=s, dev=i, tier=int(T0["dev"]["tier"][j0]), L=Li,
                           vol_truth=vt, vol_dev=vd, gain=gain, gain_per_slot=gain / Li,
                           rel_gain=(gain / vt) if vt > 0 else None,
                           max_env_truth=float(T0["dev"]["max_env"][j0]))
                if m in REPAY_FAMILY:
                    row["B"] = p.B(row["tier"], 1)
                dev_rows.append(row)

    def _dev_summary(m):
        g = np.array([r["gain_per_slot"] for r in dev_rows if r["mech"] == m])
        rel = [r["rel_gain"] for r in dev_rows if r["mech"] == m and r["rel_gain"] is not None]
        return dict(n=int(g.size), mean_gain_per_slot=float(g.mean()), median_gain_per_slot=float(np.median(g)),
                    p95_gain_per_slot=float(np.percentile(g, 95)), share_positive=float(np.mean(g > 0)),
                    mean_rel_gain=float(np.mean(rel)) if rel else None)

    dev_summary = {m: _dev_summary(m) for m in MECH_NAMES}
    print("\n(a) unilateral static deviation, gain per slot (Mbit/s)")
    print(f"{'mech':10s} {'mean':>9s} {'median':>9s} {'p95':>9s} {'share>0':>8s} {'rel%':>8s}")
    for m in MECH_NAMES:
        d = dev_summary[m]
        print(f"{LABELS[m]:10s} {d['mean_gain_per_slot']:9.4f} {d['median_gain_per_slot']:9.4f} "
              f"{d['p95_gain_per_slot']:9.4f} {100 * d['share_positive']:8.1f} "
              f"{100 * (d['mean_rel_gain'] or 0):8.2f}")
    rep = [r for r in dev_rows if r["mech"] in REPAY_FAMILY]
    viol = [r for r in rep if r["gain"] > r["B"] + 1e-9]
    print(f"REPAY-family gains above B(g,1): {len(viol)} of {len(rep)}; max gain/B = "
          f"{max(r['gain'] / r['B'] for r in rep):.3f}")

    # (b) collapse curves
    coll_rows = []
    for m in MECH_NAMES:
        for s in COLL_SEEDS:
            for rho in RHOS:
                if rho == 0.0:
                    r = truth[(m, s)]
                    mis = set()
                else:
                    r = next(r for r in res if r["mech"] == m and r["seed"] == s and r["tag"] == f"coll:{rho}")
                    mis = set(mis_sets[(rho, s)])
                d = r["dev"]
                ids = np.asarray(d["id"])
                cls = np.asarray(d["cls"])
                L = np.asarray(d["L"], float)
                vol = np.asarray(d["vol"], float)
                util = np.asarray(d["util"], float)
                rts, rtr = np.asarray(d["rt_served"], float), np.asarray(d["rt_slots"], float)
                is_mis = np.isin(ids, list(mis)) if mis else np.zeros(ids.size, bool)
                tE = (cls == 0) & ~is_mis
                mE = (cls == 0) & is_mis
                rtm = cls > 0
                vm = cls == 1

                def ratio(a, b):
                    return float(a / b) if b > 0 else None

                coll_rows.append(dict(
                    mech=m, seed=s, rho=rho, n_mis=int(mE.sum()), n_truth_E=int(tE.sum()),
                    succ_true_RT=ratio(rts[rtm].sum(), rtr[rtm].sum()),
                    succ_true_V=ratio(rts[vm].sum(), rtr[vm].sum()),
                    util_true_V_per_slot=ratio(util[vm].sum(), L[vm].sum()),
                    vol_truth_E_per_slot=ratio(vol[tE].sum(), L[tE].sum()),
                    vol_mis_E_per_slot=ratio(vol[mE].sum(), L[mE].sum()),
                    util_rate=float(r["util_rate"]),
                ))

    coll_summary = {}
    print("\n(b) collapse: true-RT success at rho=0 and rho=1, misreporter advantage at rho=0.25")
    for m in MECH_NAMES:
        rows = [c for c in coll_rows if c["mech"] == m]
        def get(rho, key):
            vals = [c[key] for c in rows if c["rho"] == rho and c[key] is not None]
            return mean_ci(vals)[0] if vals else None
        adv = {}
        for rho in RHOS:
            a = [c["vol_mis_E_per_slot"] - c["vol_truth_E_per_slot"] for c in rows
                 if c["rho"] == rho and c["vol_mis_E_per_slot"] is not None and c["vol_truth_E_per_slot"] is not None]
            adv[str(rho)] = mean_ci(a)[0] if a else None
        coll_summary[m] = dict(
            succ_true_RT={str(rho): get(rho, "succ_true_RT") for rho in RHOS},
            succ_true_V={str(rho): get(rho, "succ_true_V") for rho in RHOS},
            util_rate={str(rho): get(rho, "util_rate") for rho in RHOS},
            mis_advantage={k: v for k, v in adv.items()},
        )
        cs = coll_summary[m]
        print(f"{LABELS[m]:10s} succ(rho=0)={cs['succ_true_RT']['0.0']:.4f} "
              f"succ(rho=1)={cs['succ_true_RT']['1.0']:.4f} "
              f"mis-adv(0.25)={cs['mis_advantage']['0.25']:.4f} Mbit/s")

    # (c) reverse deviation: true video declares elastic
    rev_rows = []
    for m in REV_MECHS:
        for s in REV_SEEDS:
            T0 = truth[(m, s)]
            idx0 = _by_id(T0["dev"])
            for i in picks_rev[s]:
                r = next(r for r in res if r["mech"] == m and r["seed"] == s and r["tag"] == f"rev:{i}")
                j0 = idx0[i]
                jd = _by_id(r["dev"])[i]
                ut = float(T0["dev"]["util"][j0])
                ud = float(r["dev"]["util"][jd])
                rev_rows.append(dict(mech=m, seed=s, dev=i, L=int(T0["dev"]["L"][j0]),
                                     util_truth=ut, util_dev=ud, gain=ud - ut))
    rev_summary = {}
    print("\n(c) reverse deviation (true video declares elastic): utility gain over the sojourn")
    for m in REV_MECHS:
        g = np.array([r["gain"] for r in rev_rows if r["mech"] == m])
        rev_summary[m] = dict(n=int(g.size), mean_gain=float(g.mean()), median_gain=float(np.median(g)),
                              max_gain=float(g.max()), min_gain=float(g.min()),
                              share_positive=float(np.mean(g > 0)))
        print(f"{LABELS[m]:10s} n={g.size} mean={g.mean():.3f} median={np.median(g):.3f} "
              f"min={g.min():.3f} max={g.max():.3f} share>0={100 * np.mean(g > 0):.0f}%")

    save("strategic", dict(
        T=T, scenario="hotspot", mechanisms=MECH_NAMES,
        picks_deviation=picks_dev, picks_reverse=picks_rev,
        misreporter_sets={f"{rho}|{s}": v for (rho, s), v in mis_sets.items()},
        deviation=dev_rows, deviation_summary=dev_summary,
        collapse=coll_rows, collapse_summary=coll_summary,
        reverse=rev_rows, reverse_summary=rev_summary,
    ))
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
