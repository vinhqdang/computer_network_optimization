"""Figure and table for the six-trace unilateral deviation experiment (reads results/deviation.json).

Run as: python -m experiments.plots_dev   (writes paper/figures/fig_deviation.pdf and paper/tables/deviation.tex)
"""
import os

import numpy as np

from experiments.common import COLORS, FIGURES, LABELS, ROOT, load, style

DOUBLE = 7.0
TABLES = os.path.join(ROOT, "paper", "tables")
ORDER = ["repay", "repay-e", "no-debt", "dpp", "priority", "wfq", "pf", "credit"]
TIER_NAMES = ["Free", "Premium", "PAYG"]


def fig_deviation(plt, d, out):
    recs = d["records"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE, 2.4), gridspec_kw=dict(width_ratios=[1.6, 1]))

    # (a) relative gain per mechanism, symlog axis so that REPAY's small values and Priority's large ones are both readable
    data = [[100 * r["rel_gain"] for r in recs if r["mech"] == m and r["rel_gain"] is not None] for m in ORDER]
    bp = ax1.boxplot(data, widths=0.6, patch_artist=True, flierprops=dict(markersize=2, markeredgewidth=0.4),
                     medianprops=dict(color="k", lw=1), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7),
                     boxprops=dict(lw=0.7))
    for patch, m in zip(bp["boxes"], ORDER):
        patch.set_facecolor(COLORS[m])
        patch.set_alpha(0.45)
    ax1.set_yscale("symlog", linthresh=10, linscale=1.0)
    ax1.axhline(0, color="k", lw=0.8)
    ax1.set_xticks(range(1, len(ORDER) + 1))
    ax1.set_xticklabels([LABELS[m] for m in ORDER], rotation=40, ha="right")
    ax1.set_ylabel("Unilateral relative gain (%)")
    ax1.set_title("(a) All mechanisms, 180 devices", fontsize=9, loc="left")

    # (b) REPAY: volume gain of every device by tier, with the bound B(g,1)
    rep = [r for r in recs if r["mech"] == "repay"]
    rng = np.random.default_rng(0)
    gains = np.array([r["gain"] for r in rep])
    lo, hi = np.percentile(gains, 1), np.percentile(gains, 99)
    Bs = [next(r["B"] for r in rep if r["tier"] == g) for g in range(3)]
    ylo = min(0.0, lo) - 0.15 * (max(Bs) - min(0.0, lo))
    yhi = max(hi, max(Bs)) + 0.12 * (max(Bs) - min(0.0, lo))
    off_below = off_above = 0
    for g in range(3):
        rs = [r for r in rep if r["tier"] == g]
        xs = g + rng.uniform(-0.18, 0.18, len(rs))
        ys = np.array([r["gain"] for r in rs])
        off_below += int(np.sum(ys < ylo))
        off_above += int(np.sum(ys > yhi))
        ax2.scatter(xs, ys, s=9, color=COLORS["repay"], alpha=0.75, lw=0, clip_on=True)
        ax2.hlines(Bs[g], g - 0.35, g + 0.35, linestyles="--", color="k", lw=1,
                   label=r"bound $B_{g,1}$" if g == 0 else None)
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_ylim(ylo, yhi)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(TIER_NAMES)
    ax2.set_xlim(-0.6, 2.6)
    ax2.set_xlabel("Tier (REPAY)")
    ax2.set_ylabel("Gain in volume (Mbit)")
    ax2.set_title("(b) REPAY, every device", fontsize=9, loc="left")
    if off_below or off_above:
        ax2.text(0.99, 0.01, f"off-axis: {off_below} below, {off_above} above", transform=ax2.transAxes,
                 ha="right", va="bottom", fontsize=6.5, color="0.3")
    ax2.legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    path = os.path.join(out, "fig_deviation.pdf")
    fig.savefig(path)
    plt.close(fig)
    return path


def _cell(v, ci):
    return f"${v:.1f}$ [${ci[0]:.1f}$, ${ci[1]:.1f}$]"


def write_table(d, path):
    S = d["summary"]
    lines = [
        f"% Source: results/deviation.json (experiments/exp_deviation.py); 180 devices, six traces. "
        "Brackets: 95% cluster-bootstrap CI over traces.",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Mechanism & Median rel.\ gain (\%) [95\% CI] & Pooled volume gain (\%) [95\% CI] & "
        r"Mean rel.\ gain (\%) [95\% CI] & Devices gaining (\%) & 95th pct.\ gain (Mbit/s) \\",
        r"\midrule",
    ]
    for m in ORDER:
        s = S[m]
        lines.append(
            f"{LABELS[m]} & {_cell(s['median_rel_gain_pct'], s['median_rel_ci_pct'])} & "
            f"{_cell(s['pooled_gain_pct'], s['pooled_ci_pct'])} & "
            f"{_cell(s['mean_rel_gain_pct'], s['mean_rel_ci_pct'])} & "
            f"{s['share_gaining_pct']:.1f} & {s['p95_gain_per_slot']:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def main():
    plt = style()
    os.makedirs(FIGURES, exist_ok=True)
    d = load("deviation")
    print("wrote", fig_deviation(plt, d, FIGURES))
    print("wrote", write_table(d, os.path.join(TABLES, "deviation.tex")))


if __name__ == "__main__":
    main()
