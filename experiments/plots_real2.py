"""Tables for the second real-trace scenario (reads results/real2_compare.json and results/real2_deviation.json).

Run as: python -m experiments.plots_real2
Writes paper/tables/real2_traces.tex, real2_compare.tex and real2_deviation.tex (booktabs only).
Scenarios are gps with ghent and mesa with raca (experiments.data_real2); means of the six windows in the trace table,
mean with a 95% Student-t half-width over the six traces in the comparison table.
"""
import os

import numpy as np

from experiments.common import ROOT, load, mean_ci
from experiments.exp_real2 import DEV_MECHS, LAB, MECH_ORDER

TABLES = os.path.join(ROOT, "paper", "tables")
SCEN = ("gps", "mesa")


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _esc(s):
    return str(s).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def _ci(vals, fmt):
    """Mean $\\pm$ 95% half-width over the finite values, or -- if there are none."""
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return "--"
    mu, hw = mean_ci(vals)
    return f"{fmt.format(mu)} $\\pm$ {fmt.format(hw)}"


def _runs(c, source, mech):
    return [r for r in c["runs"] if r["source"] == source and r["mech"] == mech]


def traces_table(c):
    lines = [
        "% Source: results/real2_compare.json (experiments/data_real2.py); six day windows per scenario, "
        "load 1.0, averaged over the windows.",
        r"\begin{tabular}{llllrrrrlr}",
        r"\toprule",
        r"Source & Unit & Period & Devices per window & Video-like share (\%) & Mean concurrency & "
        r"Median stay (s) & Median elastic cap (Mbit/s) & Capacity source & CV of capacity \\",
        r"\midrule",
    ]
    for s in SCEN:
        meta = c["meta"][s]
        src = c["sources"][s]
        avg = lambda key, scale=1.0: float(np.mean([m[key] for m in meta])) * scale
        lines.append(
            f"{_esc(src['label'])} & {_esc(src['unit'])} & {_esc(src['period'])} & "
            f"{avg('n_devices'):.1f} & {avg('share_video', 100.0):.1f} & {avg('mean_conc'):.1f} & "
            f"{avg('median_stay_s'):.0f} & {avg('ell_el_q50'):.2f} & "
            f"{_esc(src['capacity']['label'])} & {avg('C_cv'):.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real2_traces.tex"), lines)


def compare_table(c):
    head = {s: f"{c['sources'][s]['label']} / {c['sources'][s]['capacity']['label']}" for s in SCEN}
    lines = [
        "% Source: results/real2_compare.json (experiments/exp_real2.py); load 1.0; mean $\\pm$ 95% Student-t "
        "half-width over six traces per scenario.",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        f" & \\multicolumn{{3}}{{c}}{{{_esc(head['gps'])}}} & \\multicolumn{{3}}{{c}}{{{_esc(head['mesa'])}}} \\\\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
        r"Mechanism & RT success (\%) & Elastic rate (Mbit/s) & Max class envy (Mbit) & "
        r"RT success (\%) & Elastic rate (Mbit/s) & Max class envy (Mbit) \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        cells = []
        for s in SCEN:
            rs = _runs(c, s, m)
            cells += [
                _ci([100 * r["rt_success"]["all"] for r in rs], "{:.1f}"),
                _ci([r["el_rate"] for r in rs], "{:.2f}"),
                _ci([r["max_env"] for r in rs], "{:.2f}"),
            ]
        lines.append(f"{LAB[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real2_compare.tex"), lines)


def deviation_table(d):
    head = {s: f"{d['sources'][s]['label']} / {d['sources'][s]['capacity']['label']}" for s in SCEN}
    lines = [
        "% Source: results/real2_deviation.json (experiments/exp_real2.py); load 1.0; six traces per scenario, "
        "20 true-elastic devices per trace (stay of at least 60 slots). Devices above bound: gain greater than "
        "B (REPAY family only).",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        f" & \\multicolumn{{3}}{{c}}{{{_esc(head['gps'])}}} & \\multicolumn{{3}}{{c}}{{{_esc(head['mesa'])}}} \\\\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
        r"Mechanism & Median rel.\ gain (\%) & Devices gaining (\%) & Devices above bound & "
        r"Median rel.\ gain (\%) & Devices gaining (\%) & Devices above bound \\",
        r"\midrule",
    ]
    for m in DEV_MECHS:
        cells = []
        for s in SCEN:
            x = d["summary"][s][m]
            ab = str(x["n_above_bound"]) if "n_above_bound" in x else "--"
            cells += [f"{x['median_rel_gain_pct']:.2f}", f"{x['share_gaining_pct']:.1f}", ab]
        lines.append(f"{LAB[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real2_deviation.tex"), lines)


def main():
    c = load("real2_compare")
    d = load("real2_deviation")
    for path in (traces_table(c), compare_table(c), deviation_table(d)):
        print("wrote", path)


if __name__ == "__main__":
    main()
