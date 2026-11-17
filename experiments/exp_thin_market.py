"""Thin markets: exact gain of one elastic device that declares video for its whole stay.

One tier, capacity alternating between 0.9 and 3.0 Mbit/s per three devices, tier prices zero.
The market has one potential deviator, n_E other elastic devices and n_V genuine video flows;
all devices are present for L slots and elastic devices are saturated (cap 30 Mbit/s).
Writes results/thin_market.json and paper/tables/thin_market.tex.
Run from the repository root: python -m experiments.exp_thin_market
"""
import os

import numpy as np

from experiments.common import ROOT, save
from repay.mechanisms import Repay, View
from repay.params import Params

MARKETS = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1), (4, 2), (9, 4), (19, 9), (39, 19)]
LENGTHS = [500, 2000, 8000]
PATTERN = (0.9, 3.0)


def volumes(n_el, n_vid, deviate, L, params):
    """Cumulative volume of every device; device 0 is the potential deviator."""
    n = 1 + n_el + n_vid
    ids = np.arange(n)
    tier = np.zeros(n, int)
    arr = np.zeros(n, int)
    decl = np.array([1 if deviate else 0] + [0] * n_el + [1] * n_vid)
    cap = np.full(n, 30.0)
    mech = Repay(params, beta_override=lambda t: np.zeros(3))
    vol = np.zeros(n)
    for t in range(L):
        C = PATTERN[t % len(PATTERN)] * n / 3.0
        vol += mech.allocate(View(t, C, ids, tier, decl, cap, arr))
    return vol


def main():
    p = Params()
    B = p.B(0, 1)
    rows = []
    for n_el, n_vid in MARKETS:
        for L in LENGTHS:
            truth = volumes(n_el, n_vid, False, L, p)[0]
            dev = volumes(n_el, n_vid, True, L, p)[0]
            rows.append(dict(n_el=n_el, n_vid=n_vid, L=L, truthful=truth, deviation=dev,
                             gain=dev - truth, gain_over_B=(dev - truth) / B))
    save("thin_market", dict(pattern=PATTERN, V=p.V, B=B, rows=rows))
    print(f"B = {B:.1f} Mbit")
    print(f"{'other E':>8s}{'video':>7s}" + "".join(f"{'gain L=' + str(L):>14s}" for L in LENGTHS))
    lines = [r"\begin{tabular}{rr" + "r" * len(LENGTHS) + "}", r"\toprule",
             "$n_E$ & $n_V$ & " + " & ".join(f"$L={L}$" for L in LENGTHS) + r" \\",
             r"\midrule"]
    for n_el, n_vid in MARKETS:
        g = [next(r["gain"] for r in rows if (r["n_el"], r["n_vid"], r["L"]) == (n_el, n_vid, L))
             for L in LENGTHS]
        print(f"{n_el:8d}{n_vid:7d}" + "".join(f"{x:14.1f}" for x in g))
        lines.append(f"{n_el} & {n_vid} & " + " & ".join(f"${x:.1f}$" for x in g) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    os.makedirs(os.path.join(ROOT, "paper", "tables"), exist_ok=True)
    with open(os.path.join(ROOT, "paper", "tables", "thin_market.tex"), "w") as f:
        f.write("% Source: results/thin_market.json (gain in Mbit of the deviating device)\n")
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
