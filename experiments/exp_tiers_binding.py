"""E5: business-constraint queues when tier weights alone do not deliver the service levels.

Hotspot trace (T=8000, seeds 0..4) with equal tier weights, committed rates (premium 3, PAYG 2),
premium target theta_P=0.8, PAYG target theta_Y=0.7 and free-floor fraction phi=0.2. The six
mechanisms of the main comparison are run with the default V, and REPAY is swept over V.
Writes results/tiers_binding.json and paper/tables/tiers_binding.tex.
Run from the repository root: python -m experiments.exp_tiers_binding
"""
import os
import time

import numpy as np

from experiments.common import LABELS, MECHS, ROOT, mean_ci, pmap, save
from repay.params import Params
from repay.sim import make_trace, run

T = 8000
SEEDS = range(5)
MECH_ORDER = ["repay", "dpp", "pf", "wfq", "priority", "credit"]
V_SWEEP = [5.0, 20.0, 100.0]
BASE = dict(w=(1.0, 1.0, 1.0), commit=(float("inf"), 3.0, 2.0), theta_P=0.8, theta_Y=0.7, phi=0.2)
TIER_NAMES = ("F", "P", "Y")
TARGETS = dict(P=0.8, Y=0.7, F=1.0)


def _params(V=None):
    """Base parameters; V is left at its default unless given."""
    kw = dict(BASE)
    if V is not None:
        kw["V"] = float(V)
    return Params(**kw)


def _job(job):
    """One (configuration, mechanism, V, seed) run; per-tier elastic rates from the device records."""
    cfg, name, V, seed = job
    p = _params(V)
    r = run(make_trace("hotspot", T, seed), MECHS[name](p), p)
    dev = r["dev"]
    el = dev["cls"] == 0
    el_tier = {}
    for g, tn in enumerate(TIER_NAMES):
        m = el & (dev["tier"] == g)
        span = dev["L"][m].sum()
        el_tier[tn] = float(dev["vol"][m].sum() / span) if span > 0 else float("nan")
    out = dict(
        cfg=cfg, mech=name, V=p.V, seed=seed,
        served_P=r["served_ratio"]["P"], served_Y=r["served_ratio"]["Y"],
        free_floor_ratio=r["free_floor_ratio"],
        util_rate=r["util_rate"],
        rt_success_all=r["rt_success"]["all"],
        el_rate=r["el_rate"],
        el_rate_F=el_tier["F"], el_rate_P=el_tier["P"], el_rate_Y=el_tier["Y"],
        max_env=r["max_env"],
    )
    if "D_over_B_max" in r:
        out["D_over_B_max"] = r["D_over_B_max"]
    return out


def _vals(rs, key):
    """Finite values of one key over runs (None or NaN entries are dropped)."""
    v = [r[key] for r in rs if r.get(key) is not None]
    return [x for x in v if np.isfinite(x)]


def _mean(rs, key):
    v = _vals(rs, key)
    return float(np.mean(v)) if v else float("nan")


def _ci(rs, key):
    return mean_ci(_vals(rs, key))


def _row_means(rs):
    """Means over seeds of the printed quantities."""
    return dict(
        P=_mean(rs, "served_P"), Y=_mean(rs, "served_Y"), F=_mean(rs, "free_floor_ratio"),
        util=_mean(rs, "util_rate"), rt=100 * _mean(rs, "rt_success_all"),
        el_F=_mean(rs, "el_rate_F"), el_P=_mean(rs, "el_rate_P"), el_Y=_mean(rs, "el_rate_Y"),
        env=_mean(rs, "max_env"),
    )


def _print_rows(label_runs):
    """Print the table rows for a list of (label, runs)."""
    head = (f"{'mechanism':12s}{'premium':>9s}{'PAYG':>9s}{'free':>9s}{'utility':>9s}{'RT%':>7s}"
            f"{'el_F':>8s}{'el_P':>8s}{'el_Y':>8s}{'maxEnv':>9s}")
    print(head)
    for label, rs in label_runs:
        m = _row_means(rs)
        print(f"{label:12s}{m['P']:9.3f}{m['Y']:9.3f}{m['F']:9.3f}{m['util']:9.2f}{m['rt']:7.1f}"
              f"{m['el_F']:8.2f}{m['el_P']:8.2f}{m['el_Y']:8.2f}{m['env']:9.2f}")


def _tex_cell(mean_hw, fmt, scale=1.0):
    mean, hw = mean_hw
    return f"${fmt % (scale * mean)}\\pm{fmt % (scale * hw)}$"


def _write_tex(main_runs, path):
    """Booktabs tabular (no table environment) with mean +- 95% CI half-width per cell."""
    lines = [
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        "Mechanism & Premium ($\\ge 0.8$) & PAYG ($\\ge 0.7$) & Free-floor ($\\ge 1.0$) & "
        "Utility & RT success (\\%) & Max envy (Mbit) \\\\",
        "\\midrule",
    ]
    for name in MECH_ORDER:
        rs = [r for r in main_runs if r["mech"] == name]
        cells = [
            _tex_cell(_ci(rs, "served_P"), "%.3f"),
            _tex_cell(_ci(rs, "served_Y"), "%.3f"),
            _tex_cell(_ci(rs, "free_floor_ratio"), "%.3f"),
            _tex_cell(_ci(rs, "util_rate"), "%.2f"),
            _tex_cell(_ci(rs, "rt_success_all"), "%.1f", scale=100.0),
            _tex_cell(_ci(rs, "max_env"), "%.2f"),
        ]
        lines.append(f"{LABELS[name]} & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def main():
    jobs = [("main", m, None, s) for m in MECH_ORDER for s in SEEDS]
    jobs += [("vsweep", "repay", V, s) for V in V_SWEEP for s in SEEDS]
    t0 = time.time()
    runs = pmap(_job, jobs, procs=2)
    elapsed = time.time() - t0

    main_runs = [r for r in runs if r["cfg"] == "main"]
    sweep_runs = [r for r in runs if r["cfg"] == "vsweep"]

    print(f"E5 binding tiers: {len(runs)} runs (T={T}, hotspot), {elapsed:.0f} s wall time")
    print("targets: premium 0.8, PAYG 0.7, free floor 1.0 (means over seeds)\n")
    _print_rows([(LABELS[m], [r for r in main_runs if r["mech"] == m]) for m in MECH_ORDER])
    print("\nREPAY V sweep")
    _print_rows([(f"REPAY V={int(V)}", [r for r in sweep_runs if r["V"] == V]) for V in V_SWEEP])

    path_json = save("tiers_binding", dict(
        T=T, seeds=list(SEEDS), base_params=BASE, targets=TARGETS, mechanisms=MECH_ORDER,
        V_sweep=V_SWEEP, elapsed_s=elapsed, runs=runs))
    path_tex = _write_tex(main_runs, os.path.join(ROOT, "paper", "tables", "tiers_binding.tex"))
    print("\nwrote", path_json)
    print("wrote", path_tex)


if __name__ == "__main__":
    main()
