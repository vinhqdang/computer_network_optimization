"""Figures and LaTeX tables for experiments E1, E3, E4 (bound, compare, variability), E4 tiers and E8 runtime.

Reads results/{bound,compare,variability,tiers,runtime}.json. A figure or table whose input file is
missing (or still being written) is skipped with a printed note, so the script can be re-run later.

Run from the repository root: python -m experiments.plots_a
Writes paper/figures/fig_{bound,tradeoff,compare,variability,tiers,runtime}.pdf and
paper/tables/{compare,compare_home,variability}.tex.
"""
import json
import os

import numpy as np
from matplotlib.ticker import NullLocator

from experiments.common import COLORS, FIGURES, LABELS, MARKERS, ROOT, load, mean_ci, style

SINGLE, DOUBLE, ROW = 3.4, 7.0, 2.3
TABLES = os.path.join(ROOT, "paper", "tables")
ENVY_FLOOR = 0.1  # class envy is plotted as max(value, 0.1) on log axes
COMPARE_ORDER = ["repay", "repay-wc", "repay-e", "no-debt", "dpp", "pf", "wfq", "priority", "credit"]
VARIABILITY_ORDER = ["repay", "dpp", "pf", "wfq", "priority", "credit"]
TIER_TARGETS = dict(theta_P=0.8, theta_Y=0.6, free=1.0)


# --------------------------------------------------------------------------- helpers

def _load_or_none(name):
    """Return results/<name>.json, or None if it is missing or still being written."""
    try:
        return load(name)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _select(runs, **kw):
    return [r for r in runs if all(r.get(k) == v for k, v in kw.items())]


def _yerr(m, hw, floor=None):
    """Asymmetric error bars that stay above `floor` (needed on log axes)."""
    m, hw = np.asarray(m, float), np.asarray(hw, float)
    lo = hw if floor is None else np.minimum(hw, np.maximum(m - floor, 0.0))
    return np.vstack([lo, hw])


def _floor(v):
    return np.maximum(np.asarray(v, float), ENVY_FLOOR)


def _legend_below(ax, ncol):
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=ncol, handlelength=1.8)


def _fig_legend(fig, handles, labels, ncol, height):
    """Shared legend under all panels; reserves the strip at the bottom of the figure."""
    rows = int(np.ceil(len(labels) / ncol))
    strip = (0.26 * rows + 0.12) / height
    fig.legend(handles, labels, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.8, columnspacing=1.2)
    fig.tight_layout(rect=(0, strip, 1, 1))


def _set_vticks(ax, xs):
    ax.set_xticks(xs)
    ax.set_xticklabels([str(x) for x in xs])
    ax.xaxis.set_minor_locator(NullLocator())


# --------------------------------------------------------------------------- figures

def fig_bound(plt, d):
    """(a) peak D/B vs V for hotspot and adversarial; (b) max class envy vs V with B_video_max."""
    runs, Vs = d["runs"], d["V_values"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE, ROW + 0.5))

    for scen, mk, col in [("hotspot", "o", COLORS["repay"]), ("adversarial", "s", COLORS["dpp"])]:
        ys = [max(r["D_over_B_max"] for r in _select(runs, scen=scen, mech="repay", V=V)) for V in Vs]
        ax1.plot(Vs, ys, marker=mk, color=col, label=scen.capitalize())
    ax1.axhline(1.0, color="k", ls="--", lw=1)
    ax1.text(0.98, 1.0, "bound", transform=ax1.get_yaxis_transform(), ha="right", va="bottom", fontsize=8)
    ax1.set_xscale("log")
    _set_vticks(ax1, Vs)
    ax1.set_ylim(0, 1.1)
    ax1.set_xlabel("Utility weight $V$")
    ax1.set_ylabel(r"Peak $D/B$ (max over seeds)")
    ax1.set_title("(a)", loc="left")
    _legend_below(ax1, 2)

    for mech, mk, col in [("repay", "o", COLORS["repay"]), ("dpp", "s", COLORS["dpp"])]:
        m, hw = zip(*[mean_ci([r["max_env"] for r in _select(runs, scen="hotspot", mech=mech, V=V)])
                      for V in Vs])
        ax2.errorbar(Vs, m, yerr=_yerr(m, hw, floor=ENVY_FLOOR), marker=mk, color=col, capsize=2,
                     label=LABELS[mech])
    bvid = [_select(runs, scen="hotspot", mech="repay", V=V)[0]["B_video_max"] for V in Vs]
    ax2.plot(Vs, bvid, ls="--", color="0.3", lw=1.2, label=r"$B^{\max}_{\mathrm{video}}$")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    _set_vticks(ax2, Vs)
    ax2.set_xlabel("Utility weight $V$")
    ax2.set_ylabel("Max class envy (Mbit)")
    ax2.set_title("(b)", loc="left")
    _legend_below(ax2, 3)
    fig.tight_layout()
    return fig


def fig_tradeoff(plt, d):
    """Max class envy against RT success rate along V, REPAY and plain DPP on hotspot."""
    runs, Vs = d["runs"], d["V_values"]
    fig, ax = plt.subplots(figsize=(SINGLE, ROW + 0.4))
    # label offsets (points, horizontal alignment) chosen so that the clustered points stay legible
    offsets = {
        "repay": {2: (5, -9, "left"), 5: (5, -9, "left"), 10: (5, -9, "left"), 20: (5, -9, "left"),
                  50: (5, -9, "left"), 100: (-5, 5, "right")},
        "dpp": {2: (6, -3, "left"), 5: (6, -3, "left"), 10: (6, -9, "left"), 20: (-6, -10, "right"),
                50: (-6, 4, "right"), 100: (6, -2, "left")},
    }
    for mech, mk, col in [("repay", "o", COLORS["repay"]), ("dpp", "s", COLORS["dpp"])]:
        xs, xh, ys, yh = [], [], [], []
        for V in Vs:
            rs = _select(runs, scen="hotspot", mech=mech, V=V)
            mx, mxh = mean_ci([r["max_env"] for r in rs])
            my, myh = mean_ci([100 * r["rt_success_all"] for r in rs])
            xs.append(mx)
            xh.append(mxh)
            ys.append(my)
            yh.append(myh)
        ax.errorbar(xs, ys, xerr=_yerr(xs, xh, floor=ENVY_FLOOR), yerr=yh, marker=mk, color=col,
                    capsize=2, label=LABELS[mech])
        for V, x, y in zip(Vs, xs, ys):
            dx, dy, ha = offsets[mech][V]
            ax.annotate(f"V={V}", (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7,
                        color=col, ha=ha)
    ax.set_xscale("log")
    ax.set_xlim(right=3000)
    ax.set_xlabel("Max class envy (Mbit, log scale)")
    ax.set_ylabel("RT success rate (%)")
    _legend_below(ax, 2)
    fig.tight_layout()
    return fig


def fig_compare(plt, d):
    """Four bar panels for the hotspot scenario, one bar per mechanism."""
    runs = d["runs"]
    panels = [
        (lambda r: 100 * r["rt_success"]["all"], "RT success (%)", False),
        (lambda r: r["el_rate"], "Elastic rate (Mbit/s)", False),
        (lambda r: r["util_rate"], "Utility rate (utility units/slot)", False),
        (lambda r: r["max_env"], "Max class envy (Mbit)", True),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(DOUBLE, 2 * ROW + 1.0))
    x = np.arange(len(COMPARE_ORDER))
    for i, (ax, (get, ylabel, is_log)) in enumerate(zip(axes.flat, panels)):
        stats = [mean_ci([get(r) for r in _select(runs, scen="hotspot", mech=m)]) for m in COMPARE_ORDER]
        m = np.array([s[0] for s in stats])
        hw = np.array([s[1] for s in stats])
        colors = [COLORS[k] for k in COMPARE_ORDER]
        if is_log:
            mp = _floor(m)
            ax.bar(x, mp - ENVY_FLOOR, bottom=ENVY_FLOOR, color=colors, edgecolor="0.2", linewidth=0.4,
                   yerr=_yerr(mp, hw, floor=ENVY_FLOOR), capsize=2, error_kw=dict(lw=0.8))
            ax.set_yscale("log")
            ax.set_ylim(ENVY_FLOOR, max(float(np.max(mp + hw)) * 2.5, 1.0))
        else:
            ax.bar(x, m, color=colors, edgecolor="0.2", linewidth=0.4, yerr=hw, capsize=2,
                   error_kw=dict(lw=0.8))
        ax.set_xticks(x)
        ax.set_xticklabels([LABELS[k] for k in COMPARE_ORDER], rotation=45, ha="right",
                           rotation_mode="anchor", fontsize=7.5)
        ax.set_ylabel(ylabel)
        ax.set_title(f"({'abcd'[i]})", loc="left")
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def fig_variability(plt, d):
    """RT success, elastic rate and max class envy against the capacity variability scale."""
    runs, scales = d["runs"], d["scales"]
    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE, ROW + 0.3))
    specs = [
        (lambda r: 100 * r["rt_success_all"], "RT success (%)", False),
        (lambda r: r["el_rate"], "Elastic rate (Mbit/s)", False),
        (lambda r: r["max_env"], "Max class envy (Mbit)", True),
    ]
    handles = labels = None
    for i, (ax, (get, ylabel, is_log)) in enumerate(zip(axes, specs)):
        for mech in VARIABILITY_ORDER:
            stats = [mean_ci([get(r) for r in _select(runs, mech=mech, scale=s)]) for s in scales]
            m = np.array([s[0] for s in stats])
            hw = np.array([s[1] for s in stats])
            if is_log:
                mp = _floor(m)
                ax.errorbar(scales, mp, yerr=_yerr(mp, hw, floor=ENVY_FLOOR), color=COLORS[mech],
                            marker=MARKERS[mech], capsize=2, label=LABELS[mech])
            else:
                ax.errorbar(scales, m, yerr=hw, color=COLORS[mech], marker=MARKERS[mech], capsize=2,
                            label=LABELS[mech])
        if is_log:
            ax.set_yscale("log")
            ax.set_ylim(ENVY_FLOOR, None)
        ax.set_xticks(scales)
        ax.set_xlabel("Capacity variability scale")
        ax.set_ylabel(ylabel)
        ax.set_title(f"({'abc'[i]})", loc="left")
        if i == 0:
            handles, labels = ax.get_legend_handles_labels()
    _fig_legend(fig, handles, labels, ncol=3, height=ROW + 0.3)
    return fig


def fig_tiers(plt, d):
    """Running premium, PAYG and free-floor ratios over time (seed 0), with their targets."""
    targets = d.get("targets", TIER_TARGETS)
    series = [("repay", 5, "#56B4E9"), ("repay", 20, COLORS["repay"]), ("repay", 100, "#003B5C"),
              ("pf", 20, COLORS["pf"])]
    panels = [("premium", "Premium ratio", targets["theta_P"], r"$\theta_P$"),
              ("payg", "PAYG ratio", targets["theta_Y"], r"$\theta_Y$"),
              ("free", "Free-floor ratio", targets["free"], "1.0")]
    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE, ROW + 0.3))
    for i, (ax, (key, ylabel, tgt, tlabel)) in enumerate(zip(axes, panels)):
        for name, V, col in series:
            rs = [r for r in d["series_runs"] if r["name"] == name and r["V"] == V and r["seed"] == 0]
            if not rs:
                continue
            s = rs[0]["samples"]
            lab = f"{LABELS[name]} $V$={V}" if name == "repay" else LABELS[name]
            ax.plot(s["t"], np.array(s[key], dtype=float), color=col, lw=1.2, label=lab)
        ax.axhline(tgt, color="k", ls="--", lw=1)
        ax.text(0.98, tgt, tlabel, transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=8)
        ax.set_ylim(0, 3)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel + " (cumulative)")
        ax.set_title(f"({'abc'[i]})", loc="left")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    _fig_legend(fig, handles, labels, ncol=4, height=ROW + 0.3)
    return fig


def fig_runtime(plt, d):
    """Median solve time against the number of devices, bisection solver versus cvxpy."""
    rows = d["rows"]
    fig, ax = plt.subplots(figsize=(SINGLE, ROW + 0.4))
    ax.plot([r["N"] for r in rows], [r["bisection_ms_median"] for r in rows], marker="o",
            color=COLORS["repay"], label="Bisection solver")
    cv = [(r["N"], r["cvxpy_ms_median"]) for r in rows if r["cvxpy_ms_median"] is not None]
    if cv:
        ax.plot([c[0] for c in cv], [c[1] for c in cv], marker="s", color=COLORS["dpp"],
                label="cvxpy (CLARABEL)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of devices $N$")
    ax.set_ylabel("Solve time (ms)")
    _legend_below(ax, 2)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- tables

def _num(m, d):
    return "--" if not np.isfinite(m) else f"{m:.{d}f}"


def _pm(m, hw, d):
    return "--" if not np.isfinite(m) else f"{m:.{d}f} $\\pm$ {hw:.{d}f}"


def _tabular(align, header, rows):
    lines = [f"\\begin{{tabular}}{{{align}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    lines += [" & ".join(r) + " \\\\" for r in rows]
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(lines)


# (header, getter, use CI, decimals)
COMPARE_COLS = [
    ("Utility", lambda r: r["util_rate"], True, 1),
    ("RT success (\\%)", lambda r: 100 * r["rt_success"]["all"], True, 1),
    ("Video success (\\%)", lambda r: 100 * r["rt_success"]["V"], True, 1),
    ("Elastic rate (Mbit/s)", lambda r: r["el_rate"], False, 2),
    ("Jain index", lambda r: r["jain"], False, 3),
    ("Premium ratio", lambda r: r["served_ratio"]["P"], False, 2),
    ("PAYG ratio", lambda r: r["served_ratio"]["Y"], False, 2),
    ("Free-floor ratio", lambda r: r["free_floor_ratio"], False, 2),
    ("Max class envy (Mbit)", lambda r: r["max_env"], True, 1),
    ("95th-pct.\\ device envy (Mbit)", lambda r: r["max_env_el_p95"], False, 1),
]
HOME_DROP = {"PAYG ratio", "Free-floor ratio"}


def _compare_table(d, scen, drop=()):
    runs = d["runs"]
    cols = [c for c in COMPARE_COLS if c[0] not in drop]
    header = ["Mechanism"] + [c[0] for c in cols]
    rows = []
    for m in COMPARE_ORDER:
        rs = _select(runs, scen=scen, mech=m)
        cells = [LABELS[m]]
        for _, get, use_ci, dec in cols:
            mean, hw = mean_ci([get(r) for r in rs])
            cells.append(_pm(mean, hw, dec) if use_ci else _num(mean, dec))
        rows.append(cells)
    align = "l" + "r" * len(cols)
    return ("% Source: results/compare.json, scenario " + scen + "\n" + _tabular(align, header, rows))


def table_compare(d):
    return _compare_table(d, "hotspot")


def table_compare_home(d):
    return _compare_table(d, "home", drop=HOME_DROP)


def table_variability(d):
    runs, scales = d["runs"], d["scales"]
    header = ["Mechanism"] + [f"$s={s:.2f}$" for s in scales]
    rows = []
    for m in VARIABILITY_ORDER:
        cells = [LABELS[m]]
        for s in scales:
            mean, hw = mean_ci([100 * r["rt_success_all"] for r in _select(runs, mech=m, scale=s)])
            cells.append(_pm(mean, hw, 1))
        rows.append(cells)
    return ("% Source: results/variability.json, RT success (%) mean $\\pm$ 95% CI half-width\n"
            + _tabular("l" + "r" * len(scales), header, rows))


# --------------------------------------------------------------------------- driver

FIGURE_JOBS = [
    ("fig_bound.pdf", "bound", fig_bound),
    ("fig_tradeoff.pdf", "bound", fig_tradeoff),
    ("fig_compare.pdf", "compare", fig_compare),
    ("fig_variability.pdf", "variability", fig_variability),
    ("fig_tiers.pdf", "tiers", fig_tiers),
    ("fig_runtime.pdf", "runtime", fig_runtime),
]
TABLE_JOBS = [
    ("compare.tex", "compare", table_compare),
    ("compare_home.tex", "compare", table_compare_home),
    ("variability.tex", "variability", table_variability),
]


def main():
    plt = style()
    os.makedirs(TABLES, exist_ok=True)
    cache = {}

    def get(name):
        if name not in cache:
            cache[name] = _load_or_none(name)
        return cache[name]

    for out, src, fn in FIGURE_JOBS:
        d = get(src)
        if d is None:
            print(f"skip {out}: results/{src}.json missing")
            continue
        fig = fn(plt, d)
        path = os.path.join(FIGURES, out)
        fig.savefig(path)
        plt.close(fig)
        print("wrote", path)

    for out, src, fn in TABLE_JOBS:
        d = get(src)
        if d is None:
            print(f"skip {out}: results/{src}.json missing")
            continue
        path = os.path.join(TABLES, out)
        with open(path, "w") as f:
            f.write(fn(d))
        print("wrote", path)


if __name__ == "__main__":
    main()
