# REPAY: online capacity allocation with bounded class envy

Code, experiments and paper for *Priority Now, Payback Later: Online Capacity Allocation with
Bounded Class Envy for Tiered Internet Access*.

An Internet access point (home gateway or public Wi-Fi hotspot) serves real-time flows (video
calls, gaming) and delay-tolerant flows (downloads, mail) of free, premium and pay-as-you-go
subscribers, without knowing future arrivals, demand or capacity. REPAY grants real-time flows
priority on credit: every delay-tolerant device that is passed over accumulates a deficit that is
paid back in volume later. The deficit is provably bounded on every sample path, which makes
misdeclaring the service class unprofitable (approximately, for price-taking devices that stay long enough).

## Layout

| Path | Content |
|---|---|
| `repay/` | Library: per-slot solver (`solver.py`), REPAY and baselines (`mechanisms.py`), traces and simulator (`sim.py`), parameters (`params.py`) |
| `tests/` | Unit tests: solver against a conic solver, the deficit bound under adversarial inputs, mechanism invariants, simulator smoke tests |
| `experiments/` | One script per experiment (`exp_*.py`) and the plotting scripts (`plots_a.py`, `plots_b.py`, `plots_dev.py`) |
| `results/` | JSON output of every experiment reported in the paper |
| `paper/` | LaTeX source, figures, tables and the compiled `main.pdf` |
| `research/` | Research question, literature notes with verification status, design documents, integrity and review reports |

## Reproducing

```bash
pip install -r requirements.txt   # tested with Python 3.13
```

```bash
python -m pytest -q tests
```

Experiments (run from the repository root; each writes `results/<name>.json`):

```bash
python -m experiments.exp_bound
python -m experiments.exp_optgap
python -m experiments.exp_compare
python -m experiments.exp_variability
python -m experiments.exp_tiers
python -m experiments.exp_tiers_binding
python -m experiments.exp_strategic
python -m experiments.exp_switching
python -m experiments.exp_oracle
python -m experiments.exp_deviation   # needs results/strategic.json
python -m experiments.exp_thin_market
python -m experiments.exp_frontier
python -m experiments.exp_short_stays
python -m experiments.exp_continuity
python -m experiments.exp_oracle_ablation   # needs results/oracle.json
python -m experiments.exp_runtime
```

Figures and tables:

```bash
python -m experiments.plots_a
```

```bash
python -m experiments.plots_b
python -m experiments.plots_dev   # after plots_b: writes the deviation table and figure
python -m experiments.plots_c     # frontier figure, capped-priority and short-stay tables
```

Paper:

```bash
cd paper && latexmk -pdf main.tex
```

All experiments use fixed seeds. The complete set takes roughly two hours on four cores; the
strategic experiments (`exp_strategic`, `exp_switching`) account for most of it.

## Minimal example

```python
from repay.params import Params
from repay.mechanisms import Repay, PF
from repay.sim import make_trace, run

p = Params(V=20)
trace = make_trace("hotspot", T=3000, seed=0)
for mech in (Repay(p), PF(p)):
    r = run(trace, mech, p)
    print(type(mech).__name__, r["rt_success"]["all"], r["el_rate"], r["max_env"])
```

## Author

Quang-Vinh Dang, British University Vietnam (vinh.dq4@buv.edu.vn), ORCID 0000-0002-3877-8024.
