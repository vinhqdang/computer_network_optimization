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
| `experiments/` | One script per experiment (`exp_*.py`), the trace builders (`data_real.py`, `data_real2.py`) and the plotting scripts (`plots_*.py`) |
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
python -m experiments.data_real    # downloads the public traces into data/raw (not in the repository)
python -m experiments.exp_real     # trace-driven comparison and deviations
python -m experiments.exp_real_sweep   # sweep of V, cap and weight on the trace-driven scenario (needs results/real_*.json)
python -m experiments.exp_mix        # real-time share and population sweeps, deviation at a 10% real-time share
python -m experiments.exp_baselines  # six additional baselines (FQ, FQ-w, JS, LendRecoup, Potential, DMMF); needs results/compare.json, strategic.json, real_compare.json, real_deviation.json
python -m experiments.data_real2     # prints the windows of the two further trace-driven scenarios (data must be in data/raw, see Data)
python -m experiments.exp_real2      # Grand Paris Sud and Mesa scenarios: comparison and deviations
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
python -m experiments.plots_real  # tables of the trace-driven scenario
python -m experiments.plots_real_sweep  # frontier figure and sweep tables of the trace-driven scenario
python -m experiments.plots_mix        # figure and tables of the traffic-mix and population sweeps
python -m experiments.plots_baselines  # tables of the additional baselines
python -m experiments.plots_real2      # tables of the Grand Paris Sud and Mesa scenarios
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

## Data

The trace-driven experiments use two public datasets that are downloaded by `experiments/data_real.py` and are not redistributed here: the session logs of the Paris public Wi-Fi network (City of Paris open data portal, dataset `paris-wi-fi-utilisation-des-hotspots-paris-wi-fi`, Open Database License) and the HSDPA commute-path bandwidth logs of Riiser, Vigmostad, Griwodz and Halvorsen (MMSys 2013). Service classes of the trace-driven devices are inferred from session traffic features, and tiers are drawn from an estimated split (see `experiments/data_real.py`). The Paris dataset is updated by its publisher, so a later download can contain more sessions; the windows used in the paper are the six busiest days between January 2025 and July 2026.

The two further trace-driven scenarios (`experiments/data_real2.py`, `experiments/exp_real2.py`) use four more public datasets. They are not downloaded by the code and are not redistributed here; place them under `data/raw/` as follows.

| Directory | Dataset | Where | Licence |
|---|---|---|---|
| `data/raw/grandparissud_wifi_sessions/sessions.csv` | Grand Paris Sud public Wi-Fi, RADIUS accounting sessions, 29 July to 31 August 2026 ("[Nouveaux Flux / Wifi territorial] Table des sessions utilisateurs") | https://data.grandparissud.fr/explore/dataset/nouveaux-flux-wifi-territorial-table-sessions-utilisateurs/ | not stated (licence fields empty in the portal metadata) |
| `data/raw/socrata_mesa_wifi_sessions/mesa_2025_07.csv` | City of Mesa (Arizona), "Wifi Activity - City Owned Access Points", records of July 2025 | https://citydata.mesaaz.gov/d/2vtm-mpvz (Socrata API `https://citydata.mesaaz.gov/resource/2vtm-mpvz`) | "See Terms of Use"; the terms page could not be retrieved |
| `data/raw/ghent_4g_lte/logs/` | Ghent University 4G/LTE bandwidth logs (40 logs, 2015-16), file `logs/logs_all.zip`, extracted | https://users.ugent.be/~jvdrhoof/dataset-4g/ | not stated; the page asks to cite van der Hooft et al., IEEE Communications Letters 20(11), 2016 |
| `data/raw/zenodo_raca_4g_lte/extracted/Dataset/` | Raca et al. 4G/LTE dataset (135 traces, Cork, 2017-18), `LTE_Dataset.zip`, extracted | https://doi.org/10.5281/zenodo.1219679 | CC BY 4.0; cite Raca et al., MMSys 2018 |

Caveats, documented in `experiments/data_real2.py` and in the paper: the Grand Paris Sud unit is the whole intercommunal network, not one site; in the Mesa file the uplink counter is about ten times the downlink counter, its start times carry no time zone (read as Arizona local time, UTC-7), and its elastic demand is almost entirely at the floor of the demand-cap rule; neither log has packet counts, so no device is classified as gaming. `research/05_additional_datasets.md` records the provenance of each dataset.

