"""Frontier figure and tables for the real-trace sweep (reads results/real_sweep.json).

Writes paper/figures/fig_real_frontier.pdf, paper/tables/real_sweep.tex (truthful devices, means over the six
traces) and paper/tables/real_sweep_dev.tex (unilateral static deviation).
Run from the repository root: python -m experiments.plots_real_sweep
"""
import os

import numpy as np

from experiments.common import COLORS, FIGURES, LABELS, MARKERS, ROOT, load, style

FIG_W, FIG_H = 5.5, 3.8
TABLES = os.path.join(ROOT, "paper", "tables")
MECH_GROUPS = ("repay", "no-debt", "dpp")


def _avg(vals):
    """Mean of the finite values (None and NaN skipped), NaN if there are none."""
    v = [float(x) for x in vals if x is not None and np.isfinite(x)]
    return float(np.mean(v)) if v else float("nan")


def _num(x, d):
    return "--" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


def _runs(s, fam, param):
    return [r for r in s["part1_runs"] if r["family"] == fam and r["param"] == param]


def _booktabs(align, header, groups, source):
    """Booktabs tabular; groups is a list of row lists, with \\midrule between groups."""
    lines = [f"% Source: {source}", f"\\begin{{tabular}}{{{align}}}", "\\toprule",
             " & ".join(header) + " \\\\"]
    for rows in groups:
        lines.append("\\midrule")
        lines += [" & ".join(r) + " \\\\" for r in rows]
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(lines)


def fig_real_frontier(plt, s):
    """RT success against mean elastic rate for each family, parameter values annotated."""
    grids = s["grids"]
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    swept = [
        ("repay", grids["V"], lambda v: f"$V$={v:g}"),
        ("no-debt", grids["V"], lambda v: f"$V$={v:g}"),
        ("dpp", grids["V"], lambda v: f"$V$={v:g}"),
        ("priority-cap", grids["priority_cap_q"], lambda v: f"$q$={v:g}"),
        ("wfq", grids["wfq_mult"], lambda v: f"$\\times${v:g}"),
    ]
    for fam, values, text in swept:
        xs, ys = [], []
        for v in values:
            rs = _runs(s, fam, v)
            xs.append(_avg([r["el_rate"] for r in rs]))
            ys.append(100 * _avg([r["rt_success"]["all"] for r in rs]))
        col = COLORS[fam]
        ax.plot(xs, ys, color=col, marker=MARKERS[fam], lw=1.2, label=LABELS[fam])
        for v, x, y in zip(values, xs, ys):
            ax.annotate(text(v), (x, y), xytext=(4, 3), textcoords="offset points", fontsize=6.5,
                        color=col, ha="left")
    for fam in ("pf", "priority"):
        rs = _runs(s, fam, None)
        x = _avg([r["el_rate"] for r in rs])
        y = 100 * _avg([r["rt_success"]["all"] for r in rs])
        ax.plot([x], [y], color=COLORS[fam], marker=MARKERS[fam], ls="none", markersize=6,
                label=LABELS[fam])
    ax.set_xlabel("Mean elastic rate (Mbit/s)")
    ax.set_ylabel("RT success (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, handlelength=1.8)
    fig.tight_layout()
    return fig


def table_mechanisms(s):
    """Truthful devices: means over the six traces for REPAY, No-debt and Plain DPP at each V."""
    header = ["Mechanism", "$V$", "RT success (\\%)", "Elastic rate (Mbit/s)", "Max class envy (Mbit)",
              "Envy bound $B$ (Mbit)", "Premium served ratio"]
    groups = []
    for fam in MECH_GROUPS:
        rows = []
        for V in s["grids"]["V"]:
            rs = _runs(s, fam, V)
            rows.append([
                LABELS[fam], f"{V:g}",
                _num(100 * _avg([r["rt_success"]["all"] for r in rs]), 1),
                _num(_avg([r["el_rate"] for r in rs]), 2),
                _num(_avg([r["max_env"] for r in rs]), 2),
                _num(_avg([r["B_free_video"] for r in rs]), 1),
                _num(_avg([(r["served_ratio"] or {}).get("P") for r in rs]), 3),
            ])
        groups.append(rows)
    source = (f"results/real_sweep.json, variant {s['variant']} (experiments/exp_real_sweep.py); site "
              f"{s['site']}, load {s['load']}; means over {len(s['k_values'])} traces. Envy bound: "
              "Params(V).B(0, 1), free tier, video; -- for Plain DPP, which keeps no deficits.")
    return _booktabs("llrrrrr", header, groups, source)


def table_deviation(s):
    """Unilateral static deviation: REPAY V = 20 reference (from results/real_deviation.json) and the sweep."""
    header = ["Rule", "$V$", "Median rel.\\ gain (\\%)", "Pooled volume gain (\\%)", "Devices gaining (\\%)",
              "Devices above bound", "Max gain / bound"]
    summ = s["deviation"]["summary"]
    ref = [d for d in summ if d["source"] != "sweep"]
    groups = [[["REPAY (ref.)", "20", _num(d["median_rel_gain_pct"], 2), _num(d["pooled_gain_pct"], 2),
                _num(d["share_gaining_pct"], 1), str(d["n_above_bound"]), _num(d["max_gain_over_bound"], 3)]
               for d in ref]]
    for fam in ("repay", "no-debt"):
        rows = []
        for d in summ:
            if d["source"] == "sweep" and d["family"] == fam:
                rows.append([LABELS[fam], f"{d['V']:g}", _num(d["median_rel_gain_pct"], 2),
                             _num(d["pooled_gain_pct"], 2), _num(d["share_gaining_pct"], 1),
                             str(d["n_above_bound"]), _num(d["max_gain_over_bound"], 3)])
        groups.append(rows)
    source = (f"results/real_sweep.json and results/real_deviation.json (reference row); variant {s['variant']}, "
              f"site {s['site']}, load {s['load']}, six traces, {s['n_per_trace']} true-elastic devices per trace. "
              "Bound: Params(V).B(tier, 1) of the device's tier.")
    return _booktabs("lrrrrrr", header, groups, source)


def main():
    plt = style()
    os.makedirs(TABLES, exist_ok=True)
    s = load("real_sweep")

    fig = fig_real_frontier(plt, s)
    path = os.path.join(FIGURES, "fig_real_frontier.pdf")
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)

    path = os.path.join(TABLES, "real_sweep.tex")
    with open(path, "w") as f:
        f.write(table_mechanisms(s))
    print("wrote", path)

    path = os.path.join(TABLES, "real_sweep_dev.tex")
    with open(path, "w") as f:
        f.write(table_deviation(s))
    print("wrote", path)


if __name__ == "__main__":
    main()
