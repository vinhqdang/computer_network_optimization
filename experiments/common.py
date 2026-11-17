"""Shared helpers for the experiment scripts: mechanism registry, parallel map, result files, plot style."""
import json
import os
from multiprocessing import Pool

import numpy as np

from repay.mechanisms import PF, WFQ, Credit, PlainDPP, Priority, Repay

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "paper", "figures")

# name -> factory(params)
MECHS = {
    "repay": lambda p: Repay(p),
    "repay-wc": lambda p: Repay(p, recycle=True),
    "repay-e": lambda p: Repay(p, entrant=True),
    "no-debt": lambda p: Repay(p, debt_price=False),
    "dpp": lambda p: PlainDPP(p),
    "pf": lambda p: PF(p),
    "wfq": lambda p: WFQ(p),
    "priority": lambda p: Priority(p),
    "credit": lambda p: Credit(p),
}

LABELS = {
    "repay": "REPAY", "repay-wc": "REPAY-WC", "repay-e": "REPAY-E", "no-debt": "No-debt",
    "dpp": "Plain DPP", "pf": "PF", "wfq": "WFQ", "priority": "Priority", "credit": "Credit",
}

# Okabe-Ito colour-blind-safe palette
COLORS = {
    "repay": "#0072B2", "repay-wc": "#56B4E9", "repay-e": "#009E73", "no-debt": "#999999",
    "dpp": "#E69F00", "pf": "#CC79A7", "wfq": "#D55E00", "priority": "#000000", "credit": "#F0E442",
}
MARKERS = {
    "repay": "o", "repay-wc": "v", "repay-e": "^", "no-debt": "x",
    "dpp": "s", "pf": "D", "wfq": "P", "priority": "*", "credit": "h",
}


def pmap(fn, jobs, procs=4):
    """Map fn over jobs in worker processes (fn must be a module-level function)."""
    if procs <= 1 or len(jobs) <= 1:
        return [fn(j) for j in jobs]
    with Pool(procs) as pool:
        return pool.map(fn, jobs, chunksize=1)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return f if np.isfinite(f) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def save(name, obj):
    """Write results/<name>.json."""
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name + ".json")
    with open(path, "w") as f:
        json.dump(_clean(obj), f, indent=1)
    return path


def load(name):
    with open(os.path.join(RESULTS, name + ".json")) as f:
        return json.load(f)


def mean_ci(values):
    """Mean and half-width of a 95% normal confidence interval over seeds."""
    v = np.asarray([x for x in values if x is not None], dtype=float)
    if v.size == 0:
        return float("nan"), float("nan")
    hw = 1.96 * v.std(ddof=1) / np.sqrt(v.size) if v.size > 1 else 0.0
    return float(v.mean()), float(hw)


def style():
    """Matplotlib style shared by all figures."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
        "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight",
        "pdf.fonttype": 42, "lines.linewidth": 1.5, "lines.markersize": 4.5,
    })
    os.makedirs(FIGURES, exist_ok=True)
    return plt
