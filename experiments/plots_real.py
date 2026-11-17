"""Tables for the real-trace experiment (reads results/real_compare.json and results/real_deviation.json).

Run as: python -m experiments.plots_real
Writes paper/tables/real_traces.tex, real_compare.tex, real_load.tex and real_deviation.tex.
"""
import os

import numpy as np

from experiments.common import LABELS, ROOT, load, mean_ci

TABLES = os.path.join(ROOT, "paper", "tables")
LAB = {**LABELS, "priority-cap": r"Capped priority ($q=0.3$)"}
MECH_ORDER = ["repay", "no-debt", "dpp", "pf", "wfq", "priority", "priority-cap", "credit"]
DEV_ORDER = ["repay", "dpp", "priority", "wfq", "pf", "priority-cap"]
LOADS = (0.7, 1.0, 1.5)


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def traces_table(d):
    metas = [m for m in d["meta"] if m["load"] == 1.0]
    main = sorted([m for m in metas if m["site"] == "PW0127"], key=lambda m: m["k"])
    sec = [m for m in metas if m["site"] == "PW0232"]
    lines = [
        "% Source: results/real_compare.json (experiments/data_real.py); PW0127 windows, and PW0232 averaged over its six windows.",
        r"\begin{tabular}{lllrrrrrr}",
        r"\toprule",
        r"Trace & Date & Devices & Mean conc. & Median stay (s) & Median elastic cap (Mbit/s) & "
        r"90th pct.\ elastic cap (Mbit/s) & Mean capacity (Mbit/s) & CV of capacity \\",
        r"\midrule",
    ]
    for m in main:
        lines.append(
            f"PW0127, $k={m['k']}$ & {m['date']} & {m['n_devices']} & {m['mean_conc']:.1f} & "
            f"{m['median_stay_s']:.0f} & {m['ell_el_q50']:.2f} & {m['ell_el_q90']:.2f} & "
            f"{m['C_mean']:.1f} & {m['C_cv']:.2f} \\\\")
    lines.append(r"\midrule")
    avg = lambda key: float(np.mean([m[key] for m in sec]))
    lines.append(
        f"PW0232, mean of $k=0,\\dots,5$ & -- & {avg('n_devices'):.1f} & {avg('mean_conc'):.1f} & "
        f"{avg('median_stay_s'):.0f} & {avg('ell_el_q50'):.2f} & {avg('ell_el_q90'):.2f} & "
        f"{avg('C_mean'):.1f} & {avg('C_cv'):.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_traces.tex"), lines)


def _runs(d, mech, load):
    return [r for r in d["runs"] if r["site"] == "PW0127" and r["load"] == load and r["mech"] == mech]


def compare_table(d):
    lines = [
        "% Source: results/real_compare.json (experiments/exp_real.py); site PW0127, load 1.0; "
        "mean $\\pm$ 95% Student-t half-width over six traces.",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Mechanism & Utility & RT success (\%) & Video success (\%) & Elastic rate (Mbit/s) & "
        r"Max class envy (Mbit) \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        rs = _runs(d, m, 1.0)
        cells = []
        for vals, fmt in (
            ([r["util_rate"] for r in rs], "{:.2f}"),
            ([100 * r["rt_success"]["all"] for r in rs], "{:.1f}"),
            ([100 * r["rt_success"]["V"] for r in rs], "{:.1f}"),
            ([r["el_rate"] for r in rs], "{:.2f}"),
            ([r["max_env"] for r in rs], "{:.2f}"),
        ):
            mu, hw = mean_ci(vals)
            cells.append(f"{fmt.format(mu)} $\\pm$ {fmt.format(hw)}")
        lines.append(f"{LAB[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_compare.tex"), lines)


def load_table(d):
    lines = [
        "% Source: results/real_compare.json (experiments/exp_real.py); site PW0127, means over six traces.",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r" & \multicolumn{3}{c}{RT success (\%)} & \multicolumn{3}{c}{Elastic rate (Mbit/s)} \\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
        r"Mechanism & 0.7 & 1.0 & 1.5 & 0.7 & 1.0 & 1.5 \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        rt = [100 * np.mean([r["rt_success"]["all"] for r in _runs(d, m, l)]) for l in LOADS]
        el = [np.mean([r["el_rate"] for r in _runs(d, m, l)]) for l in LOADS]
        lines.append(f"{LAB[m]} & " + " & ".join(f"{x:.1f}" for x in rt) + " & "
                     + " & ".join(f"{x:.2f}" for x in el) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_load.tex"), lines)


def deviation_table(d):
    S = d["summary"]
    lines = [
        f"% Source: results/real_deviation.json (experiments/exp_real.py); site PW0127, load 1.0, six traces, "
        f"{d['n_per_trace']} true-elastic devices per trace.",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Mechanism & $n$ & Median rel.\ gain (\%) & Pooled volume gain (\%) & Devices gaining (\%) & "
        r"95th pct.\ gain (Mbit/s) \\",
        r"\midrule",
    ]
    for m in DEV_ORDER:
        s = S[m]
        lines.append(f"{LAB[m]} & {s['n']} & {s['median_rel_gain_pct']:.2f} & {s['pooled_gain_pct']:.2f} & "
                     f"{s['share_gaining_pct']:.1f} & {s['p95_gain_per_slot']:.4f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_deviation.tex"), lines)


def main():
    c = load("real_compare")
    d = load("real_deviation")
    for path in (traces_table(c), compare_table(c), load_table(c), deviation_table(d)):
        print("wrote", path)


if __name__ == "__main__":
    main()
