"""Tables for the real-trace experiment (reads results/real_compare.json and results/real_deviation.json).

Run as: python -m experiments.plots_real
Writes paper/tables/real_traces.tex, real_compare.tex, real_load.tex, real_deviation.tex, real_variants.tex
and real_classes.tex. Variant main is used for the trace, comparison, load and deviation tables.
"""
import os

import numpy as np

from experiments.common import LABELS, ROOT, load, mean_ci

TABLES = os.path.join(ROOT, "paper", "tables")
LAB = {**LABELS, "priority-cap": r"Capped priority ($q=0.3$)"}
MECH_ORDER = ["repay", "no-debt", "dpp", "pf", "wfq", "priority", "priority-cap", "credit"]
DEV_ORDER = ["repay", "dpp", "priority", "wfq", "pf", "priority-cap"]
LOADS = (0.7, 1.0, 1.5)
MAIN_VARIANT, STRICT_VARIANT, TIERS_VARIANT = "main", "strict", "tiers"
MAIN_SITE, SECOND_SITE = "PW0127", "PW0232"


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _runs(d, variant, mech, load_, site=MAIN_SITE):
    return [r for r in d["runs"] if r["variant"] == variant and r["site"] == site
            and r["load"] == load_ and r["mech"] == mech]


def _ci(vals, fmt):
    """Mean $\\pm$ 95% half-width over the finite values, or -- if there are none."""
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return "--"
    mu, hw = mean_ci(vals)
    return f"{fmt.format(mu)} $\\pm$ {fmt.format(hw)}"


def traces_table(c):
    metas = [m for m in c["meta"] if m["variant"] == MAIN_VARIANT and m["load"] == 1.0]
    main = sorted([m for m in metas if m["site"] == MAIN_SITE], key=lambda m: m["k"])
    sec = [m for m in metas if m["site"] == SECOND_SITE]
    lines = [
        f"% Source: results/real_compare.json, variant {MAIN_VARIANT} (experiments/data_real.py); "
        f"{MAIN_SITE} windows, and {SECOND_SITE} averaged over its six windows.",
        r"\begin{tabular}{llrrrrrrrrr}",
        r"\toprule",
        r"Trace & Date & Devices & Video & Gaming & Mean conc. & Median stay (s) & "
        r"Median elastic cap (Mbit/s) & 90th pct.\ elastic cap (Mbit/s) & Mean capacity (Mbit/s) & "
        r"CV of capacity \\",
        r"\midrule",
    ]
    for m in main:
        lines.append(
            f"{MAIN_SITE}, $k={m['k']}$ & {m['date']} & {m['n_devices']} & {m['n_video']} & {m['n_gaming']} & "
            f"{m['mean_conc']:.1f} & {m['median_stay_s']:.0f} & {m['ell_el_q50']:.2f} & {m['ell_el_q90']:.2f} & "
            f"{m['C_mean']:.1f} & {m['C_cv']:.2f} \\\\")
    lines.append(r"\midrule")
    avg = lambda key: float(np.mean([m[key] for m in sec]))
    lines.append(
        f"{SECOND_SITE}, mean of $k=0,\\dots,5$ & -- & {avg('n_devices'):.1f} & {avg('n_video'):.1f} & "
        f"{avg('n_gaming'):.1f} & {avg('mean_conc'):.1f} & {avg('median_stay_s'):.0f} & "
        f"{avg('ell_el_q50'):.2f} & {avg('ell_el_q90'):.2f} & {avg('C_mean'):.1f} & {avg('C_cv'):.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_traces.tex"), lines)


def compare_table(c):
    lines = [
        f"% Source: results/real_compare.json, variant {MAIN_VARIANT} (experiments/exp_real.py); "
        f"site {MAIN_SITE}, load 1.0; mean $\\pm$ 95% Student-t half-width over six traces.",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Mechanism & Utility & RT success (\%) & Video success (\%) & Elastic rate (Mbit/s) & "
        r"Max class envy (Mbit) \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        rs = _runs(c, MAIN_VARIANT, m, 1.0)
        cells = [
            _ci([r["util_rate"] for r in rs], "{:.2f}"),
            _ci([100 * r["rt_success"]["all"] for r in rs], "{:.1f}"),
            _ci([100 * r["rt_success"]["V"] for r in rs], "{:.1f}"),
            _ci([r["el_rate"] for r in rs], "{:.2f}"),
            _ci([r["max_env"] for r in rs], "{:.2f}"),
        ]
        lines.append(f"{LAB[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_compare.tex"), lines)


def load_table(c):
    lines = [
        f"% Source: results/real_compare.json, variant {MAIN_VARIANT} (experiments/exp_real.py); "
        f"site {MAIN_SITE}, means over six traces.",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r" & \multicolumn{3}{c}{RT success (\%)} & \multicolumn{3}{c}{Elastic rate (Mbit/s)} \\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
        r"Mechanism & 0.7 & 1.0 & 1.5 & 0.7 & 1.0 & 1.5 \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        rt = [100 * np.mean([r["rt_success"]["all"] for r in _runs(c, MAIN_VARIANT, m, l)]) for l in LOADS]
        el = [np.mean([r["el_rate"] for r in _runs(c, MAIN_VARIANT, m, l)]) for l in LOADS]
        lines.append(f"{LAB[m]} & " + " & ".join(f"{x:.1f}" for x in rt) + " & "
                     + " & ".join(f"{x:.2f}" for x in el) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_load.tex"), lines)


def deviation_table(d):
    S = d["summary"]
    lines = [
        f"% Source: results/real_deviation.json, variant {d['variant']} (experiments/exp_real.py); "
        f"site {MAIN_SITE}, load 1.0, six traces, {d['n_per_trace']} true-elastic devices per trace.",
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


def variants_table(c):
    lines = [
        f"% Source: results/real_compare.json (experiments/exp_real.py); site {MAIN_SITE}, load 1.0; "
        "mean $\\pm$ 95% Student-t half-width over six traces. Strict rule: sym in [0.5, 2], up_min 0.2. "
        "Random tiers: tiers drawn per device with probabilities (0.6, 0.25, 0.15).",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r" & \multicolumn{3}{c}{strict rule} & \multicolumn{4}{c}{random tiers} \\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-8}",
        r"Mechanism & RT success (\%) & Elastic rate (Mbit/s) & Max class envy (Mbit) & "
        r"RT success (\%) & Elastic rate (Mbit/s) & Max class envy (Mbit) & Premium served ratio \\",
        r"\midrule",
    ]
    for m in MECH_ORDER:
        rs_s = _runs(c, STRICT_VARIANT, m, 1.0)
        rs_t = _runs(c, TIERS_VARIANT, m, 1.0)
        cells = [
            _ci([100 * r["rt_success"]["all"] for r in rs_s], "{:.1f}"),
            _ci([r["el_rate"] for r in rs_s], "{:.2f}"),
            _ci([r["max_env"] for r in rs_s], "{:.2f}"),
            _ci([100 * r["rt_success"]["all"] for r in rs_t], "{:.1f}"),
            _ci([r["el_rate"] for r in rs_t], "{:.2f}"),
            _ci([r["max_env"] for r in rs_t], "{:.2f}"),
            _ci([(r["served_ratio"] or {}).get("P") for r in rs_t], "{:.3f}"),
        ]
        lines.append(f"{LAB[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_variants.tex"), lines)


def classes_table(c):
    lines = [
        "% Source: results/real_compare.json, class_shares (experiments/data_real.py): sessions of duration >= 5 s "
        "starting on or after 2025-01-01; medians of session-average rates.",
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Site & Rule & Share video (\%) & Share gaming (\%) & Video down (Mbit/s) & Video up (Mbit/s) & "
        r"Gaming down (Mbit/s) \\",
        r"\midrule",
    ]
    rows = {(r["site"], r["rule_name"]): r for r in c["class_shares"]}
    for site in (MAIN_SITE, SECOND_SITE):
        for rule in ("default", "strict"):
            r = rows[(site, rule)]
            mi, mo = r["median_rin"], r["median_rout"]
            lines.append(f"{site} & {rule} & {100 * r['share_video']:.1f} & {100 * r['share_gaming']:.1f} & "
                         f"{mi['video']:.3f} & {mo['video']:.3f} & {mi['gaming']:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return _write(os.path.join(TABLES, "real_classes.tex"), lines)


def main():
    c = load("real_compare")
    d = load("real_deviation")
    for path in (traces_table(c), compare_table(c), load_table(c), deviation_table(d),
                 variants_table(c), classes_table(c)):
        print("wrote", path)


if __name__ == "__main__":
    main()
