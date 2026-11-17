"""E7: how the mechanisms interrupt genuine video calls (hotspot, truthful devices, T=6000, seeds 0..4).

Per slot, a recorder wrapper stores for every genuine video device whether its allocated rate is below
rmin_V (an outage slot). Per run the outage statistics are computed over all video devices. Two REPAY
variants are defined here by overriding the rounding order (served-fraction key) and the deficit
bookkeeping of a device that stops declaring elastic:
  repay-sticky : incumbents first, then arrival, then id (served-fraction key dropped);
  repay-block  : served-fraction key refreshed every 10 slots, frozen in between (new flows go last).
The rounding step lives inside one large method, so _allocate_repay is a copy of Repay.allocate with only
the served-fraction line routed through the hook _served_frac. The self-check below verifies that the copy
reproduces Repay exactly under truthful declarations.

Run as: python -m experiments.exp_continuity   (writes results/continuity.json and paper/tables/continuity.tex)
"""
import json
import os
import time

import numpy as np

from experiments.common import LABELS, MECHS, RESULTS, ROOT, pmap, save
from repay.mechanisms import PF, WFQ, Priority, PlainDPP, Repay, View, _arrays, _rmax_of
from repay.params import Params
from repay.sim import make_trace, run
from repay.solver import group_offer, solve_slot

T = 6000
SEEDS = range(5)
SCENARIO = "hotspot"
ORDER = ["repay", "repay-sticky", "repay-block", "dpp", "pf", "wfq", "priority"]
RT_VARIANTS = ["repay", "repay-sticky", "repay-block"]
OUTAGE_RUN_MIN = 5
BLOCK_SLOTS = 10


def _allocate_repay(self, view):
    """Copy of Repay.allocate; only the served-fraction key comes from self._served_frac."""
    p, w = self.p, self.p.w_arr
    ids, tier, decl, cap, arr = _arrays(view)
    n, C = ids.size, float(view.C)
    self._sync(ids, decl)
    el = np.flatnonzero(decl == 0)
    rt = np.flatnonzero(decl > 0)
    ne = el.size
    d, tel = cap[el], tier[el]

    Dm = np.array([self.D[i] for i in ids[el].tolist()], float).reshape(ne, 2)
    s_mat = np.zeros((ne, 2))
    sig_mat = np.zeros((ne, 2))
    for kk, k in enumerate((1, 2)):
        lo, hi = p.rmin(k), p.rmax(k)
        s = np.where(d >= hi, 1.0, np.where(d <= lo, 0.0, (d - lo) / max(hi - lo, 1e-300)))
        sig = np.where(d >= hi, 0.0, np.where(d <= lo, d, (1.0 - s) * d))
        s_mat[:, kk], sig_mat[:, kk] = s, sig
    bonus = Dm.sum(1)

    beta_t = self._beta_tier(view)
    pi_gk = np.zeros((3, 2))
    ze_gk = np.zeros((3, 2))
    if self.debt_price and ne:
        for kk in range(2):
            pi_gk[:, kk] = np.bincount(tel, weights=Dm[:, kk] * s_mat[:, kk], minlength=3)
            ze_gk[:, kk] = np.bincount(tel, weights=Dm[:, kk] * sig_mat[:, kk], minlength=3)

    groups = []
    for g in range(3):
        for k in (1, 2):
            mem = rt[(tier[rt] == g) & (decl[rt] == k)]
            if mem.size:
                groups.append((g, k, mem))
    gg = np.array([g for g, _, _ in groups], dtype=np.int64)
    gk = np.array([k for _, k, _ in groups], dtype=np.int64)
    gn = np.array([m.size for _, _, m in groups], dtype=float)
    gw = w[gg] if groups else np.zeros(0)
    gb = beta_t[gg] if groups else np.zeros(0)
    gpi = pi_gk[gg, gk - 1] if groups else np.zeros(0)
    gze = ze_gk[gg, gk - 1] if groups else np.zeros(0)

    res = solve_slot(C, p.V, w[tel], d, bonus, beta_t[tel], gk, gn, gw, gb, gpi, gze, p)
    x, a, z, lam = res["x"], res["a"].copy(), res["z"].copy(), res["lam"]

    if self.recycle and lam == 0.0 and groups and bool(np.all(x >= d - 1e-12)):
        spare = C - (float(np.sum(gn * a * z)) + float(x.sum()))
        for j in np.argsort(-gw, kind="stable"):
            if spare <= 1e-12:
                break
            nj, rmn, rmx = gn[j], p.rmin(gk[j]), p.rmax(gk[j])
            cur = nj * a[j] * z[j]
            extra = min(spare, nj * rmx - cur)
            spare -= extra
            Y = cur + extra
            if Y >= nj * rmn - 1e-12:
                a[j], z[j] = 1.0, min(rmx, Y / nj)
            else:
                a[j], z[j] = Y / (nj * rmn), rmn

    fref = np.zeros((n, 2))
    if ne:
        lookup = {(g, k): j for j, (g, k, _) in enumerate(groups)}
        ref = np.zeros((ne, 2))
        for g in range(3):
            mg = tel == g
            if not mg.any():
                continue
            for kk, k in enumerate((1, 2)):
                j = lookup.get((g, k))
                if j is not None:
                    ref[mg, kk] = a[j] * np.minimum(z[j], d[mg])
                elif self.entrant:
                    ae, ze, _ = group_offer(lam, 1.0, p.V * w[g], beta_t[g],
                                            pi_gk[g, kk], ze_gk[g, kk], k, p)
                    ref[mg, kk] = float(ae) * np.minimum(float(ze), d[mg])
        fref[el] = ref

    # Rounding to whole flows (the only line that differs from Repay.allocate: the hook).
    rate = np.zeros(n)
    pool = 0.0
    inc = np.isin(ids, np.fromiter(self.incumbents, np.int64, len(self.incumbents)))
    for j, (g, k, mem) in enumerate(groups):
        na = gn[j] * a[j]
        sfrac = self._served_frac(ids[mem])
        order = mem[np.lexsort((ids[mem], arr[mem], ~inc[mem], sfrac))]
        M = min(int(np.floor(na + 1e-9)), order.size)
        rate[order[:M]] = z[j]
        frac = na - M
        if M < order.size and frac > 1e-9:
            Lr = frac * z[j]
            if Lr >= p.rmin(k) - 1e-12:
                rate[order[M]] = Lr
            else:
                pool += Lr

    xf = x.copy()
    if pool > 1e-12 and ne:
        room = d - x
        mv = p.V * w[tel] / (1.0 + x) + beta_t[tel] + bonus
        order = np.argsort(-mv, kind="stable")
        rs = room[order]
        cum = np.cumsum(rs) - rs
        xf[order] += np.clip(pool - cum, 0.0, rs)
    rate[el] = xf

    if self.deficits and ne:
        Dn = np.maximum(Dm + fref[el] - xf[:, None], 0.0)
        for e, i in enumerate(ids[el].tolist()):
            self.D[i] = Dn[e].copy()

    self.incumbents = set(ids[rt][rate[rt] > 1e-12].tolist())
    for i, r_i in zip(ids[rt].tolist(), rate[rt].tolist()):
        self.rt_present[i] = self.rt_present.get(i, 0) + 1
        if r_i > 1e-12:
            self.rt_served[i] = self.rt_served.get(i, 0) + 1

    rho = np.bincount(tier, weights=rate, minlength=3)
    dem_dev = np.where(decl == 0, cap, _rmax_of(p, decl))
    dem = np.bincount(tier, weights=dem_dev, minlength=3)
    com = np.bincount(tier, weights=p.committed(tier, dem_dev), minlength=3)
    eps = np.array([p.theta_P * com[1] - rho[1],
                    p.theta_Y * com[2] - rho[2],
                    min(p.phi * C, dem[0]) - rho[0]])
    self.Q = np.maximum(self.Q + eps, 0.0)

    Dmat = np.zeros((n, 2))
    if ne:
        Dmat[el] = np.array([self.D[i] for i in ids[el].tolist()], float).reshape(ne, 2)
    self.last = dict(
        lam=lam,
        a={(g, k): float(a[j]) for j, (g, k, _) in enumerate(groups)},
        z={(g, k): float(z[j]) for j, (g, k, _) in enumerate(groups)},
        fluid_ref=fref,
        D_max=float(Dmat.max()) if n else 0.0,
        D=self.D,
        Dmat=Dmat,
    )
    return rate


class RepayCopy(Repay):
    """Repay with the rounding order copied from Repay.allocate (rotation by served fraction)."""

    def allocate(self, view):
        return _allocate_repay(self, view)

    def _served_frac(self, ids_mem):
        return np.array([self.rt_served.get(i, 0) / max(self.rt_present.get(i, 0), 1)
                         for i in ids_mem.tolist()])


class RepaySticky(RepayCopy):
    """Incumbents first, then arrival, then id: the served-fraction key is dropped."""

    def _served_frac(self, ids_mem):
        return np.zeros(ids_mem.size)


class RepayBlock(RepayCopy):
    """Served-fraction key refreshed every BLOCK_SLOTS slots and frozen in between; new flows last."""

    def reset(self):
        super().reset()
        self._snap = {}

    def allocate(self, view):
        if int(view.t) % BLOCK_SLOTS == 0:
            self._snap = {i: self.rt_served.get(i, 0) / max(self.rt_present.get(i, 0), 1)
                          for i in self.rt_present}
        return _allocate_repay(self, view)

    def _served_frac(self, ids_mem):
        return np.array([self._snap.get(i, 2.0) for i in ids_mem.tolist()], float)


class RepayKeep(RepayCopy):
    """A device that stops declaring elastic keeps its deficits frozen and restores them on return."""

    def reset(self):
        super().reset()
        self.stash = {}

    def _sync(self, ids, decl):
        present = set(ids.tolist())
        for i in [i for i in self.D if i not in present]:
            del self.D[i]
        for i in [i for i in self.stash if i not in present]:
            del self.stash[i]
        for i in [i for i in self.prev_decl if i not in present]:
            del self.prev_decl[i]
        self.incumbents &= present
        rt_now = {i for i, dk in zip(ids.tolist(), decl.tolist()) if dk != 0}
        for i in [i for i in self.rt_present if i not in rt_now]:
            del self.rt_present[i]
            self.rt_served.pop(i, None)
        for i, dk in zip(ids.tolist(), decl.tolist()):
            if dk == 0:
                if i in self.D and self.prev_decl.get(i) == 0:
                    pass
                elif i in self.stash:
                    self.D[i] = self.stash.pop(i)
                else:
                    self.D[i] = np.zeros(2)
            elif i in self.D:
                self.stash[i] = self.D.pop(i)
            self.prev_decl[i] = dk


class RepayKeepSticky(RepayKeep):
    """RepayKeep with the incumbents-first admission order."""

    def _served_frac(self, ids_mem):
        return np.zeros(ids_mem.size)


# Mechanism factories (names travel through the job tuples, factories are looked up in the worker).
CONT_FACTORY = {
    "repay": lambda p: Repay(p),
    "repay-sticky": lambda p: RepaySticky(p),
    "repay-block": lambda p: RepayBlock(p),
    "dpp": MECHS["dpp"],
    "pf": MECHS["pf"],
    "wfq": MECHS["wfq"],
    "priority": MECHS["priority"],
}
LAB = {**LABELS, "repay-sticky": "REPAY-sticky", "repay-block": "REPAY-block"}


class OutageRecorder:
    """Thin wrapper: forwards allocate/reset and records outage flags of declared-video devices."""

    def __init__(self, inner, rmin_video):
        self.inner = inner
        self.rmin = float(rmin_video)
        self.rec = {}

    def reset(self):
        self.inner.reset()
        self.rec = {}

    def allocate(self, view):
        rate = np.asarray(self.inner.allocate(view), float).reshape(len(view.ids))
        for i, dk, r in zip(np.asarray(view.ids).tolist(), np.asarray(view.decl).tolist(), rate.tolist()):
            if dk == 1:
                self.rec.setdefault(i, []).append(r < self.rmin - 1e-9)
        return rate


def _run_lengths(flags):
    """Lengths of maximal runs of True in a boolean array."""
    f = np.concatenate([[0], flags.astype(np.int8), [0]])
    d = np.diff(f)
    return np.flatnonzero(d == -1) - np.flatnonzero(d == 1)


def outage_stats(seqs):
    """Pooled outage statistics over per-device boolean outage sequences (1 slot = 1 s)."""
    pres = sum(int(s.size) for s in seqs)
    out = sum(int(s.sum()) for s in seqs)
    lens = np.concatenate([_run_lengths(s) for s in seqs]) if seqs else np.zeros(0, int)
    never = sum(1 for s in seqs if not s.any())
    nan = float("nan")
    return dict(
        presence_slots=pres,
        outage_slots=out,
        outage_pct=100.0 * out / pres if pres else nan,
        interruptions=int(lens.size),
        interrupts_per_100=100.0 * lens.size / pres if pres else nan,
        mean_len=float(lens.mean()) if lens.size else nan,
        p95_len=float(np.percentile(lens, 95)) if lens.size else nan,
        max_len=int(lens.max()) if lens.size else 0,
        long_share_pct=100.0 * float(lens[lens >= OUTAGE_RUN_MIN].sum()) / out if out else nan,
        never_pct=100.0 * never / len(seqs) if seqs else nan,
        n_devices=len(seqs),
    )


def _job(job):
    """One (mechanism, seed) run with truthful declarations; outage statistics over video devices."""
    scen, name, seed = job
    p = Params()
    tr = make_trace(scen, T, seed)
    rec = OutageRecorder(CONT_FACTORY[name](p), p.rmin_V)
    r = run(tr, rec, p)
    vids = [d["id"] for d in tr["devices"] if d["cls"] == 1 and min(d["t_dep"], T) > d["t_arr"]]
    seqs = [np.asarray(rec.rec[i], bool) for i in vids if i in rec.rec]
    st = outage_stats(seqs)
    rt_v = float(r["rt_success"]["V"])
    return dict(
        scen=scen, mech=name, seed=seed, **st,
        rt_all=float(r["rt_success"]["all"]), rt_V=rt_v, el_rate=float(r["el_rate"]),
        check_gap=abs(st["outage_pct"] / 100.0 - (1.0 - rt_v)),
    )


def _selfcheck():
    """The copy must reproduce Repay exactly under truthful declarations (no class changes)."""
    p = Params()
    tr = make_trace(SCENARIO, 1500, 1)
    a = run(tr, Repay(p), p)
    for mech in (RepayCopy(p), RepayKeep(p)):
        b = run(tr, mech, p)
        same = (np.array_equal(a["dev"]["vol"], b["dev"]["vol"])
                and np.array_equal(a["dev"]["rt_served"], b["dev"]["rt_served"])
                and a["util_rate"] == b["util_rate"])
        if not same:
            return False
    return True


def _f(x, fmt):
    return "--" if x is None or x != x else format(x, fmt)


def _summary(runs):
    """Mean over seeds of each metric, per mechanism."""
    out = {}
    for m in ORDER:
        rs = [r for r in runs if r["mech"] == m]
        keys = ["outage_pct", "interrupts_per_100", "mean_len", "p95_len", "max_len",
                "long_share_pct", "never_pct", "rt_all", "rt_V", "el_rate", "check_gap"]
        entry = {k: float(np.nanmean([r[k] if r[k] is not None else np.nan for r in rs])) for k in keys}
        entry["max_len_mean"] = float(np.mean([r["max_len"] for r in rs]))
        entry["interruptions_total_mean"] = float(np.mean([r["interruptions"] for r in rs]))
        out[m] = entry
    return out


def _print(summary):
    print("\ncontinuity of genuine video calls (hotspot, truthful, T=6000, mean over seeds 0..4)")
    head = (f"{'mechanism':14s}{'outage%':>9s}{'int/100s':>10s}{'meanLen':>9s}{'p95Len':>8s}"
            f"{'maxLen':>8s}{'long%':>8s}{'never%':>8s}")
    print(head)
    for m in ORDER:
        e = summary[m]
        print(f"{LAB[m]:14s}{_f(e['outage_pct'], '9.2f')}{_f(e['interrupts_per_100'], '10.2f')}"
              f"{_f(e['mean_len'], '9.2f')}{_f(e['p95_len'], '8.1f')}{_f(e['max_len'], '8.1f')}"
              f"{_f(e['long_share_pct'], '8.1f')}{_f(e['never_pct'], '8.1f')}")
    print("\nRT success and elastic rate (mean over seeds)")
    print(f"{'mechanism':14s}{'RT all%':>9s}{'RT video%':>11s}{'elastic':>10s}")
    for m in RT_VARIANTS:
        e = summary[m]
        print(f"{LAB[m]:14s}{100 * e['rt_all']:9.2f}{100 * e['rt_V']:11.2f}{e['el_rate']:10.3f}")


def _tex(summary):
    rows = []
    for m in ORDER:
        e = summary[m]
        rows.append(f"{LAB[m]} & {_f(e['outage_pct'], '.2f')} & {_f(e['interrupts_per_100'], '.2f')} & "
                    f"{_f(e['mean_len'], '.2f')} & {_f(e['p95_len'], '.1f')} & "
                    f"{_f(e['long_share_pct'], '.1f')} & {_f(e['never_pct'], '.1f')} \\\\")
    lines = [
        "% Source: results/continuity.json, scenario hotspot, truthful devices, T=6000, seeds 0..4",
        "\\begin{tabular}{lrrrrrr}",
        "\\toprule",
        "Mechanism & Outage slots (\\%) & Interruptions per 100 s & Mean outage length (s) & "
        "95th pct.\\ outage length (s) & Outage in runs $\\geq 5$ s (\\%) & Calls never interrupted (\\%) \\\\",
        "\\midrule",
        *rows,
        "\\bottomrule",
        "\\end{tabular}",
        "",
    ]
    return "\n".join(lines)


def main():
    t0 = time.time()
    if not _selfcheck():
        raise SystemExit("self-check failed: _allocate_repay copy differs from Repay")
    print("self-check: rotation copy and keep variant reproduce Repay under truthful declarations", flush=True)

    jobs = [(SCENARIO, m, s) for m in ORDER for s in SEEDS]
    runs = pmap(_job, jobs, procs=2)
    print(f"{len(runs)} runs in {time.time() - t0:.0f}s", flush=True)

    summary = _summary(runs)
    _print(summary)

    # Cross-check: repay video success per seed against results/compare.json (same trace and mechanism).
    cmp_path = os.path.join(RESULTS, "compare.json")
    cross = []
    if os.path.exists(cmp_path):
        with open(cmp_path) as f:
            cmp_runs = json.load(f)["runs"]
        for r in runs:
            if r["mech"] != "repay":
                continue
            ref = [c for c in cmp_runs if c["scen"] == SCENARIO and c["mech"] == "repay" and c["seed"] == r["seed"]]
            if ref:
                cross.append(dict(seed=r["seed"], rt_V_here=r["rt_V"], rt_V_compare=ref[0]["rt_success"]["V"]))
        worst = max(abs(c["rt_V_here"] - c["rt_V_compare"]) for c in cross) if cross else float("nan")
        print(f"\ncross-check vs results/compare.json, repay video success: max |diff| = {worst:.2e}")
    max_gap = max(r["check_gap"] for r in runs)
    print(f"internal check: max |outage fraction - (1 - video success)| = {max_gap:.2e}")

    tex_path = os.path.join(ROOT, "paper", "tables", "continuity.tex")
    with open(tex_path, "w") as f:
        f.write(_tex(summary))

    path = save("continuity", dict(
        T=T, scenario=SCENARIO, seeds=list(SEEDS), mechanisms=ORDER, block_slots=BLOCK_SLOTS,
        outage_run_min=OUTAGE_RUN_MIN, summary=summary, runs=runs, cross_check=cross,
        elapsed_s=time.time() - t0,
    ))
    print(f"\nwrote {path}\nwrote {tex_path}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
