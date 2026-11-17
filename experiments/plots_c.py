"""Frontier figure and tables for the capped-priority, frontier and short-stay experiments.

Reads results/frontier.json and results/short_stays.json. Writes paper/figures/fig_frontier.pdf,
paper/tables/priority_cap.tex (from frontier.json) and paper/tables/short_stays.tex (from short_stays.json).
Run from the repository root: python -m experiments.plots_c
"""
import os

import numpy as np

from experiments.common import COLORS, FIGURES, LABELS, MARKERS, ROOT, load, mean_ci, style
from experiments.plots_a import _legend_below, _num, _pm, _tabular

FIG_W, FIG_H = 5.0, 3.6
TABLES = os.path.join(ROOT, "paper", "tables")
SHORT_ORDER = ["repay", "dpp", "priority", "wfq", "pf"]


def _vals(runs, family, key, param=None):
    """Per-seed values of one metric for one family (and parameter, when given)."""
    return [r[key] for r in runs if r["family"] == family and (param is None or r["param"] == param)]


def fig_frontier(plt, fr):
    """RT success against mean elastic rate for each family, parameter values annotated."""
    runs, grids = fr["runs"], fr["grids"]
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    swept = [
        ("repay", grids["repay_V"], lambda v: f"$V$={v:g}", "o"),
        ("dpp", grids["dpp_V"], lambda v: f"$V$={v:g}", "s"),
        ("wfq", grids["wfq_mult"], lambda v: f"$\\times${v:g}", "P"),
        ("priority-cap", grids["priority_cap_q"], lambda v: f"$q$={v:g}", "p"),
    ]
    for fam, values, text, _ in swept:
        xs, ys = [], []
        for v in values:
            xs.append(mean_ci(_vals(runs, fam, "el_rate", v))[0])
            ys.append(100 * mean_ci(_vals(runs, fam, "rt_success_all", v))[0])
        col = COLORS[fam]
        ax.plot(xs, ys, color=col, marker=MARKERS[fam], lw=1.2, label=LABELS[fam])
        for v, x, y in zip(values, xs, ys):
            ax.annotate(text(v), (x, y), xytext=(4, 3), textcoords="offset points", fontsize=6.5,
                        color=col, ha="left")
    for fam in ("pf", "priority"):
        x = mean_ci(_vals(runs, fam, "el_rate"))[0]
        y = 100 * mean_ci(_vals(runs, fam, "rt_success_all"))[0]
        ax.plot([x], [y], color=COLORS[fam], marker=MARKERS[fam], ls="none", markersize=6,
                label=LABELS[fam])
    ax.set_xlabel("Mean elastic rate (Mbit/s)")
    ax.set_ylabel("RT success (%)")
    _legend_below(ax, 3)
    fig.tight_layout()
    return fig


def table_priority_cap(fr):
    """Capped priority over q: truthful performance and unilateral deviation summary."""
    runs = fr["runs"]
    dev = fr["deviation"]["summary"]
    header = ["$q$", "RT success (\\%)", "Elastic rate (Mbit/s)", "Max class envy (Mbit)",
              "Median rel.\\ gain of misreport (\\%)", "Pooled volume gain (\\%)", "Devices gaining (\\%)"]
    rows = []
    for q in fr["grids"]["priority_cap_q"]:
        rt = mean_ci([100 * x for x in _vals(runs, "priority-cap", "rt_success_all", q)])
        el = mean_ci(_vals(runs, "priority-cap", "el_rate", q))
        env = mean_ci(_vals(runs, "priority-cap", "max_env", q))
        d = dev.get(str(q))
        cells = [f"{q:g}", _pm(*rt, 1), _pm(*el, 2), _pm(*env, 2)]
        if d is None:
            cells += ["--", "--", "--"]
        else:
            cells += [_num(d["median_rel_gain_pct"], 2), _num(d["pooled_gain_pct"], 2),
                      _num(d["share_gaining_pct"], 1)]
        rows.append(cells)
    return ("% Source: results/frontier.json; truthful columns mean $\\pm$ 95% CI half-width over seeds "
            "(hotspot, T=6000); deviation columns from the unilateral static deviation (T=3000, seeds 0 and 1)\n"
            + _tabular("r" * len(header), header, rows))


def table_short_stays(ss):
    """Unilateral static deviation of short-stay true-elastic devices, per mechanism."""
    header = ["Mechanism", "n", "Median rel.\\ gain (\\%)", "Pooled volume gain (\\%)",
              "Devices gaining (\\%)", "Max gain (Mbit)"]
    rows = []
    for m in SHORT_ORDER:
        d = ss["summary"][m]
        rows.append([LABELS[m], str(d["n"]), _num(d["median_rel_gain_pct"], 2),
                     _num(d["pooled_gain_pct"], 2), _num(d["share_gaining_pct"], 1),
                     _num(d["max_gain_mbit"], 3)])
    lo, hi = ss["length_range"]
    return (f"% Source: results/short_stays.json; true-elastic devices with {lo} to {hi} slots, "
            f"T={ss['T']}, seeds {ss['seeds']}\n" + _tabular("lrrrrr", header, rows))


def main():
    plt = style()
    os.makedirs(TABLES, exist_ok=True)

    fr = load("frontier")
    fig = fig_frontier(plt, fr)
    path = os.path.join(FIGURES, "fig_frontier.pdf")
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)

    path = os.path.join(TABLES, "priority_cap.tex")
    with open(path, "w") as f:
        f.write(table_priority_cap(fr))
    print("wrote", path)

    ss = load("short_stays")
    path = os.path.join(TABLES, "short_stays.tex")
    with open(path, "w") as f:
        f.write(table_short_stays(ss))
    print("wrote", path)


if __name__ == "__main__":
    main()
