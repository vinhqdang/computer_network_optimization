"""LaTeX tables for the additional baselines (experiments/exp_baselines.py), next to REPAY, PF, plain DPP and Priority.

Reference rows are recomputed from the stored results (results/compare.json, results/strategic.json,
results/real_compare.json, results/real_deviation.json); the new rows come from results/baselines.json.
Run as: python -m experiments.plots_baselines
Writes paper/tables/baselines_synth.tex, baselines_synth_dev.tex, baselines_real.tex and baselines_real_dev.tex.
"""
import os

import numpy as np

from experiments.common import LABELS, ROOT, load, mean_ci
from experiments.exp_baselines import NEW_DEV, NEW_SYN, dev_stats

TABLES = os.path.join(ROOT, "paper", "tables")
REF = ("repay", "pf", "dpp", "priority")
DEV_SEEDS = (0, 1)
MAIN_VARIANT, MAIN_SITE = "main", "PW0127"
MEAN_HEADER = ("Mechanism & Utility & RT success (\\%) & Elastic rate (Mbit/s) & Max class envy (Mbit) & "
               "Premium ratio \\\\")
DEV_HEADER = ("Mechanism & $n$ & Median rel.\\ gain (\\%) & Pooled volume gain (\\%) & "
              "Devices gaining (\\%) \\\\")
# (getter, format) for the synthetic and trace-driven mean tables
MEAN_COLS = [
    (lambda r: r["util_rate"], "{:.2f}"),
    (lambda r: 100 * r["rt_success"]["all"], "{:.1f}"),
    (lambda r: r["el_rate"], "{:.2f}"),
    (lambda r: r["max_env"], "{:.2f}"),
    (lambda r: (r["served_ratio"] or {}).get("P"), "{:.2f}"),
]


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _ci(vals, fmt):
    """Mean $\\pm$ 95% half-width over the finite values, or -- if there are none."""
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return "--"
    mu, hw = mean_ci(vals)
    return f"{fmt.format(mu)} $\\pm$ {fmt.format(hw)}"


def _mean_table(source, runs, new_runs, path):
    lines = [f"% Source: {source}; mean $\\pm$ 95% Student-t half-width over the runs.",
             r"\begin{tabular}{lrrrrr}", r"\toprule", MEAN_HEADER, r"\midrule"]
    for m in REF:
        rs = [r for r in runs if r["mech"] == m]
        cells = [_ci([get(r) for r in rs], fmt) for get, fmt in MEAN_COLS]
        lines.append(f"{LABELS[m]} & " + " & ".join(cells) + r" \\")
    lines.append(r"\midrule")
    for m in NEW_SYN:
        rs = [r for r in new_runs if r["mech"] == m]
        cells = [_ci([get(r) for r in rs], fmt) for get, fmt in MEAN_COLS]
        lines.append(f"{LABELS[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(path, lines)


def _dev_table(source, ref_recs, new_recs, path):
    lines = [f"% Source: {source}; unilateral static deviation, true-elastic devices.",
             r"\begin{tabular}{lrrrr}", r"\toprule", DEV_HEADER, r"\midrule"]
    for m in REF:
        s = dev_stats([r for r in ref_recs if r["mech"] == m])
        lines.append(f"{LABELS[m]} & {s['n']} & {s['median_rel_gain_pct']:.2f} & "
                     f"{s['pooled_gain_pct']:.2f} & {s['share_gaining_pct']:.1f} \\\\")
    lines.append(r"\midrule")
    for m in NEW_DEV:
        s = dev_stats([r for r in new_recs if r["mech"] == m])
        lines.append(f"{LABELS[m]} & {s['n']} & {s['median_rel_gain_pct']:.2f} & "
                     f"{s['pooled_gain_pct']:.2f} & {s['share_gaining_pct']:.1f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(path, lines)


def main():
    c = load("compare")
    s = load("strategic")
    rc = load("real_compare")
    rd = load("real_deviation")
    b = load("baselines")

    syn_ref = [r for r in c["runs"] if r["scen"] == "hotspot"]
    syn_dev_ref = [r for r in s["deviation"] if r["seed"] in DEV_SEEDS]
    real_ref = [r for r in rc["runs"] if r["variant"] == MAIN_VARIANT and r["site"] == MAIN_SITE
                and r["load"] == 1.0]
    real_dev_ref = rd["records"]

    paths = [
        _mean_table("results/compare.json, scenario hotspot (truthful devices, 10 seeds); new rows from "
                    "results/baselines.json part 1",
                    syn_ref, b["part1"]["runs"], os.path.join(TABLES, "baselines_synth.tex")),
        _dev_table("results/strategic.json restricted to seeds 0 and 1; new rows from results/baselines.json "
                   "part 2", syn_dev_ref, b["part2"]["records"],
                   os.path.join(TABLES, "baselines_synth_dev.tex")),
        _mean_table(f"results/real_compare.json, variant {MAIN_VARIANT}, site {MAIN_SITE}, load 1.0 (six traces); "
                    "new rows from results/baselines.json part 3",
                    real_ref, b["part3"]["runs"], os.path.join(TABLES, "baselines_real.tex")),
        _dev_table(f"results/real_deviation.json, variant {MAIN_VARIANT}, site {MAIN_SITE}, load 1.0 (six traces); "
                   "new rows from results/baselines.json part 4",
                   real_dev_ref, b["part4"]["records"], os.path.join(TABLES, "baselines_real_dev.tex")),
    ]
    for path in paths:
        print("wrote", path)


if __name__ == "__main__":
    main()
