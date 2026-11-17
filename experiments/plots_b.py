"""Figures and the deviation table for experiments E2, E4 and E5 (reads results/*.json).

Run as: python -m experiments.plots_b   (writes paper/figures/*.pdf and paper/tables/deviation.tex)
"""
import os

import numpy as np

from experiments.common import COLORS, LABELS, MARKERS, ROOT, load, mean_ci, style

SINGLE, DOUBLE = 3.4, 7.0
TABLES = os.path.join(ROOT, "paper", "tables")
MECHS_ORDER = ["repay", "repay-e", "no-debt", "dpp", "priority", "wfq", "pf", "credit"]
TIER_NAMES = ["Free", "Premium", "PAYG"]


def fig_optgap(plt, d, out):
    rep, dpp = d["summary"]["repay"], d["summary"]["dpp"]
    V = np.array([r["V"] for r in rep])
    gap = np.array([r["gap"] for r in rep])
    gci = np.array([r["gap_ci"] for r in rep])
    util = np.array([r["util"] for r in rep])
    uci = np.array([r["util_ci"] for r in rep])
    c = float(np.mean([r["gapV"] for r in rep]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE, 2.8))
    ax1.errorbar(V, gap, yerr=gci, fmt="o-", color=COLORS["repay"], capsize=2, label="REPAY")
    Vg = np.geomspace(V.min(), V.max(), 60)
    ax1.plot(Vg, c / Vg, "--", color="0.4", lw=1)
    ax1.text(Vg[-1], c / Vg[-1], r" $\propto 1/V$", va="bottom", ha="right", color="0.3", fontsize=8)
    ax1.set_xscale("log")
    if np.all(gap > 0):
        ax1.set_yscale("log")
    ax1.set_xlabel("Utility weight $V$")
    ax1.set_ylabel("Gap $U^*-\\bar U$ (utility per slot)")

    ax2.errorbar(V, util, yerr=uci, fmt="o-", color=COLORS["repay"], capsize=2, label="REPAY")
    ax2.axhline(d["U_star"], color="k", lw=1, label=r"$U^*$")
    ax2.axhline(d["U_star_noEF"], color="k", lw=1, ls="--", label=r"$U^*_{\mathrm{noEF}}$")
    ax2.axhline(d["U_star_slotEF"], color="k", lw=1, ls=":", label=r"$U^*_{\mathrm{slotEF}}$")
    ax2.axhline(d["pf_util"]["mean"], color=COLORS["pf"], lw=1.2, label="PF")
    dpp20 = [r for r in dpp if r["V"] == 20.0][0]
    ax2.axhline(dpp20["util"], color=COLORS["dpp"], lw=1.2, ls="-.", label="Plain DPP ($V{=}20$)")
    ax2.set_xscale("log")
    ax2.set_xlabel("Utility weight $V$")
    ax2.set_ylabel("Time-average utility per slot")
    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.2, 1, 1))
    fig.savefig(os.path.join(out, "fig_optgap.pdf"))
    plt.close(fig)


def fig_deviation(plt, d, out):
    recs = d["deviation"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE, 2.8), gridspec_kw=dict(width_ratios=[1.7, 1]))
    data = [[r["gain_per_slot"] for r in recs if r["mech"] == m] for m in MECHS_ORDER]
    ax1.boxplot(data, widths=0.6, flierprops=dict(markersize=2.5))
    ax1.set_xticks(range(1, len(MECHS_ORDER) + 1))
    ax1.set_xticklabels([LABELS[m] for m in MECHS_ORDER], rotation=40, ha="right")
    ax1.axhline(0, color="k", lw=0.8)
    ax1.set_ylabel("Unilateral gain per slot (Mbit/s)")

    rep = [r for r in recs if r["mech"] == "repay"]
    rng = np.random.default_rng(0)
    for g in range(3):
        rs = [r for r in rep if r["tier"] == g]
        xs = g + rng.uniform(-0.15, 0.15, len(rs))
        ax2.scatter(xs, [r["gain"] for r in rs], s=10, color=COLORS["repay"], alpha=0.8, lw=0)
        if rs:
            B = rs[0]["B"]
            ax2.hlines(B, g - 0.35, g + 0.35, linestyles="--", color="k", lw=1,
                       label=r"bound $B_{g,V}$" if g == 0 else None)
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(TIER_NAMES)
    ax2.set_xlim(-0.6, 2.6)
    ax2.set_ylabel("Gain in volume (Mbit)")
    ax2.set_xlabel("Tier (REPAY)")
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_deviation.pdf"))
    plt.close(fig)


def fig_collapse(plt, d, out):
    rows = d["collapse"]
    rhos = sorted({r["rho"] for r in rows})
    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE, 2.7))
    panels = [
        ("success", "True RT success rate"),
        ("adv", "Misreporter minus truthful\nvolume rate (Mbit/s)"),
        ("util", "Utility rate (per slot)"),
    ]
    handles = []
    for m in MECHS_ORDER:
        for ax, (key, ylabel) in zip(axes, panels):
            xs, ys, hs = [], [], []
            for rho in rhos:
                rs = [r for r in rows if r["mech"] == m and r["rho"] == rho]
                if key == "success":
                    vals = [r["succ_true_RT"] for r in rs]
                elif key == "util":
                    vals = [r["util_rate"] for r in rs]
                else:
                    vals = [r["vol_mis_E_per_slot"] - r["vol_truth_E_per_slot"] for r in rs
                            if r["vol_mis_E_per_slot"] is not None and r["vol_truth_E_per_slot"] is not None]
                if not vals or (key == "adv" and rho in (0.0, 1.0)):
                    continue
                mu, hw = mean_ci(vals)
                xs.append(rho)
                ys.append(mu)
                hs.append(hw)
            h = ax.errorbar(xs, ys, yerr=hs, color=COLORS[m], marker=MARKERS[m], capsize=1.5,
                            label=LABELS[m], lw=1.2, ms=3.5)
            ax.set_xlabel(r"Misreporting fraction $\rho$")
            ax.set_ylabel(ylabel)
            if key == "adv":
                ax.axhline(0, color="k", lw=0.8)
        handles.append(h)
    fig.legend(handles, [LABELS[m] for m in MECHS_ORDER], loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(os.path.join(out, "fig_collapse.pdf"))
    plt.close(fig)


def fig_switching(plt, d, out):
    summ, taus = d["summary"], d["taus"]
    static_x = 2.0 * max(taus)
    fig, ax = plt.subplots(figsize=(SINGLE, 2.6))
    handles = []
    for m in ("repay", "dpp"):
        mu, hw = zip(*[mean_ci(summ[m][f"tau={t}"]["seed_means"]) for t in taus])
        h = ax.errorbar(taus, mu, yerr=hw, color=COLORS[m], marker=MARKERS[m], capsize=2,
                        label=LABELS[m], lw=1.2)
        handles.append(h)
        ms, hs = mean_ci(summ[m]["always-video"]["seed_means"])
        ax.errorbar([static_x], [ms], yerr=[hs], fmt=MARKERS[m], mfc="white", mec=COLORS[m],
                    color=COLORS[m], capsize=2, ms=5)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xscale("log")
    ax.set_xticks(list(taus) + [static_x])
    ax.set_xticklabels([str(t) for t in taus] + ["static"])
    ax.minorticks_off()
    ax.set_xlabel(r"Hold-down $\tau$ (slots, log scale)")
    ax.set_ylabel("Mean gain per slot (Mbit/s)")
    fig.legend(handles, [LABELS[m] for m in ("repay", "dpp")], loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(os.path.join(out, "fig_switching.pdf"))
    plt.close(fig)


def write_deviation_table(d, path):
    ds = d["deviation_summary"]
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Mechanism & Mean gain (Mbit/s) & Median (Mbit/s) & 95th pct.\ (Mbit/s) & Gain $>0$ (\%) & Mean rel.\ gain (\%) \\",
        r"\midrule",
    ]
    for m in MECHS_ORDER:
        s = ds[m]
        rel = "--" if s["mean_rel_gain"] is None else f"{100 * s['mean_rel_gain']:.1f}"
        lines.append(f"{LABELS[m]} & {s['mean_gain_per_slot']:.3f} & {s['median_gain_per_slot']:.3f} & "
                     f"{s['p95_gain_per_slot']:.3f} & {100 * s['share_positive']:.1f} & {rel} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    plt = style()
    out = os.path.join(ROOT, "paper", "figures")
    os.makedirs(out, exist_ok=True)
    fig_optgap(plt, load("optgap"), out)
    strat = load("strategic")
    fig_deviation(plt, strat, out)
    fig_collapse(plt, strat, out)
    fig_switching(plt, load("switching"), out)
    write_deviation_table(strat, os.path.join(TABLES, "deviation.tex"))
    print("wrote fig_optgap.pdf, fig_deviation.pdf, fig_collapse.pdf, fig_switching.pdf, tables/deviation.tex")


if __name__ == "__main__":
    main()
