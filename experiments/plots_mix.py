"""Figure and tables for the real-time share, population scale and deviation experiment (reads results/mix.json).

Writes paper/figures/fig_mix.pdf, paper/tables/mix_scale.tex (RT success by population scale) and
paper/tables/mix_dev.tex (unilateral deviation at rho_RT = 0.10).
Run from the repository root: python -m experiments.plots_mix
"""
import os

import numpy as np

from experiments.common import COLORS, FIGURES, LABELS, MARKERS, ROOT, load, mean_ci, style
from experiments.plots_a import _num, _pm, _tabular

DOUBLE = 7.0
TABLES = os.path.join(ROOT, "paper", "tables")


def _series(runs, mech, xkey, xs, fn):
    """Seed means and 95% half-widths of fn(run) at each value of run field xkey."""
    mus, hws = [], []
    for x in xs:
        mu, hw = mean_ci([fn(r) for r in runs if r["mech"] == mech and r[xkey] == x])
        mus.append(mu)
        hws.append(hw)
    return np.asarray(mus), np.asarray(hws)


def fig_mix(plt, mx):
    """(a) RT success against the real-time share; (b) max class envy against the real-time share (log)."""
    runs, rhos, mechs = mx["runs"], mx["rho_grid"], mx["mechanisms"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE, 3.1))
    handles = []
    for m in mechs:
        mu, hw = _series(runs, m, "rho_RT", rhos, lambda r: 100 * r["rt_success"]["all"])
        h = ax1.errorbar(rhos, mu, yerr=hw, color=COLORS[m], marker=MARKERS[m], capsize=1.5,
                         lw=1.2, ms=3.5, label=LABELS[m])
        handles.append(h)

        env, _ = _series(runs, m, "rho_RT", rhos, lambda r: r["max_env"])
        keep = env > 0
        if keep.any():
            ax2.plot(np.asarray(rhos)[keep], env[keep], color=COLORS[m], marker=MARKERS[m], lw=1.2, ms=3.5)

    ax1.set_xticks(rhos)
    ax1.set_xticklabels([f"{100 * r:.0f}" for r in rhos])
    ax1.set_xlabel(r"Real-time share of devices $\rho_{RT}$ (%)")
    ax1.set_ylabel("RT success (%)")
    ax2.set_xticks(rhos)
    ax2.set_xticklabels([f"{100 * r:.0f}" for r in rhos])
    ax2.set_xlabel(r"Real-time share of devices $\rho_{RT}$ (%)")
    ax2.set_yscale("log")
    ax2.set_ylabel("Max class envy (Mbit, log scale)")
    fig.legend(handles, [LABELS[m] for m in mechs], loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.17, 1, 1))
    return fig


def table_scale(mx):
    """RT success (%) per mechanism and population scale; columns labelled by mean active devices."""
    runs, scales, mechs = mx["scale_runs"], mx["scales"], mx["mechanisms"]
    active = mx["mean_active_by_scale"]
    header = ["Mechanism"] + [f"{active[str(s)]:.0f}" for s in scales]
    rows = []
    for m in mechs:
        cells = []
        for s in scales:
            mu, hw = mean_ci([100 * r["rt_success"]["all"] for r in runs if r["mech"] == m and r["scale"] == s])
            cells.append(_pm(mu, hw, 1))
        rows.append([LABELS[m]] + cells)
    return ("% Source: results/mix.json, part 2; hotspot default mix, truthful devices, T=6000, seeds 0 to 2; "
            "columns: mean number of active devices; cells: RT success (\\%) mean $\\pm$ 95% CI half-width\n"
            + _tabular("l" + "r" * len(scales), header, rows))


def table_dev(mx):
    """Unilateral static deviation at rho_RT = 0.10, per mechanism."""
    dev = mx["deviation"]
    header = ["Mechanism", "$n$", "Median rel.\\ gain (\\%)", "Pooled volume gain (\\%)",
              "Devices gaining (\\%)", "Devices above bound"]
    rows = []
    for m in dev["mechanisms"]:
        d = dev["summary"][m]
        above = str(d["n_above_B"]) if "n_above_B" in d else "--"
        rows.append([LABELS[m], str(d["n"]), _num(d["median_rel_gain_pct"], 2),
                     _num(d["pooled_gain_pct"], 2), _num(d["share_gaining_pct"], 1), above])
    return (f"% Source: results/mix.json, part 3; rho_RT={dev['rho_RT']}, T={dev['T']}, seeds "
            f"{dev['seeds']}, 30 true-elastic devices per seed; devices above bound counts gains above "
            f"$B_{{g,1}}$ (REPAY and no-debt only)\n"
            + _tabular("lrrrrr", header, rows))


def main():
    plt = style()
    os.makedirs(TABLES, exist_ok=True)
    mx = load("mix")

    fig = fig_mix(plt, mx)
    path = os.path.join(FIGURES, "fig_mix.pdf")
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)

    path = os.path.join(TABLES, "mix_scale.tex")
    with open(path, "w") as f:
        f.write(table_scale(mx))
    print("wrote", path)

    path = os.path.join(TABLES, "mix_dev.tex")
    with open(path, "w") as f:
        f.write(table_dev(mx))
    print("wrote", path)


if __name__ == "__main__":
    main()
