# Stage 1 / Phase 1 — Research Question Brief and Methodology Blueprint

Status: **draft, awaiting author confirmation** (no literature search has been run yet;
novelty statements below are hypotheses to be tested in Phase 2).

## 1. Research Question Brief

### 1.1 Setting

An Internet service provider operates a shared bottleneck (a home gateway, or a public
Wi-Fi hotspot in a cafe, metro station, airport or railway station). In each time slot:

- the **set of active devices changes** (arrivals, departures, churn) and is not known in advance;
- each device's **demand** and the **available capacity** (backhaul, airtime, channel quality) vary and are unknown ahead of time;
- flows belong to **QoS classes** with different utility shapes:
  delay-tolerant elastic (email, backup), real-time rate-adaptive (video call: hard latency, degradable rate),
  latency-critical low-rate (online gaming);
- subscribers belong to **commercial tiers** (free, premium, pay-as-you-go) that impose
  business constraints: premium service-level guarantees, caps on the capacity share given to
  free users, revenue targets, per-user PAYG budgets;
- the operator wants **fairness** within and across tiers;
- devices or applications may **strategically misdeclare** their class or demand to obtain priority.

### 1.2 Primary research question

> **RQ.** How should an ISP allocate a shared, uncertain capacity online among a churning
> population of flows with heterogeneous QoS classes and commercial tiers, so that long-run
> fair utility is maximised subject to tier-level business constraints, while strategic
> misreporting of class or demand is not profitable — and what regret, constraint-violation
> and incentive guarantees can such an algorithm provide?

### 1.3 Sub-questions

- **SQ1 (state of the art).** Which existing frameworks — network utility maximisation and
  alpha-fairness, Lyapunov drift-plus-penalty, online convex optimisation with long-term
  constraints, (distributionally) robust optimisation, smart data pricing, Stackelberg and
  mechanism-design models — cover which of the five features
  {population churn, heterogeneous QoS utilities, tier/business constraints, fairness, incentive compatibility},
  and which combinations remain uncovered?
- **SQ2 (algorithm and theory).** Can a single online algorithm handle all five features, and
  what bounds hold for (a) regret against a suitable benchmark, (b) cumulative violation of
  long-term business/SLA constraints, (c) fairness, and (d) the gain obtainable from misreporting?
- **SQ3 (evidence).** On synthetic and trace-driven workloads, how does the algorithm compare
  with static NUM, proportional-fair and weighted-fair scheduling, drift-plus-penalty, and
  generic constrained online learning, in utility, fairness, SLA violation, revenue and robustness?

### 1.4 Scope

| In scope | Out of scope |
|---|---|
| Single bottleneck link / access point (extension to a small tree of APs sharing backhaul as a secondary experiment) | Multi-hop routing, topology design, network upgrade planning |
| Slot-level rate/airtime allocation and admission | PHY/MAC protocol design, packet-level implementation in a real router |
| Unknown non-stationary arrivals, demand and capacity | Learning application classes from packets (traffic classification) |
| Tier constraints, fairness, misreport-proofness without requiring per-slot payments | Long-term pricing/plan design, competition between ISPs, regulation |
| Theory + simulation (synthetic + public traces) | Field deployment, user studies |

### 1.5 FINER assessment (provisional)

| Criterion | Score (1–5) | Note |
|---|---|---|
| Feasible | 4 | Theory + simulation only; all sources reachable from this environment (optimization-online, arXiv, Crossref tested). Real hotspot traces may need registration. |
| Interesting | 4 | Matches an operator's actual decision; combines optimisation and game theory. |
| Novel | 3 (to be verified) | Each ingredient is mature; novelty must come from the *combination with guarantees*, especially incentive compatibility under churn with long-term constraints. Phase 2 must confirm the gap. |
| Ethical | 5 | No human subjects, no personal data; public or synthetic traces only. |
| Relevant | 4 | Public Wi-Fi and tiered broadband are widely deployed; net-neutrality-compatible because differentiation is by declared class and tier, not by content provider. |

## 2. Methodology Blueprint

- **Paradigm.** Analytical / design-science: mathematical model → algorithm → proofs → computational evaluation.
- **Model.** Slotted time; active set N_t; class-dependent concave utilities with latency
  expressed through a minimum-rate/deadline structure; long-term constraints for tier SLAs,
  free-tier share and revenue; alpha-fair objective over time-averaged utilities.
- **Candidate algorithmic direction (hypothesis, to be finalised after the gap analysis).**
  An online primal–dual allocation in which dual variables for business and fairness
  constraints are shared across the churning population (so new arrivals inherit prices
  rather than starting cold), and each slot's allocation is offered as a *menu of
  class bundles* (rate, latency priority, deferral) constructed to be envy-free across
  classes, which makes truthful class declaration a dominant strategy without per-slot payments.
- **Theory targets.** Sub-linear dynamic regret and sub-linear constraint violation that scale
  with the churn rate rather than with the total number of users ever seen; an explicit
  bound on the utility a flow can gain by misreporting; a price-of-fairness/price-of-incentive bound.
- **Evaluation.** Simulator in Python; workloads: (i) synthetic Markov-modulated arrivals and
  demand, (ii) public Wi-Fi / broadband traces if retrievable. Baselines: static NUM oracle,
  proportional fair, weighted fair queueing, strict priority, drift-plus-penalty, generic
  OCO with long-term constraints. Metrics: time-average utility, Jain and alpha-fairness,
  SLA violation, revenue, regret versus hindsight optimum, misreport gain, runtime.
  Multiple seeds, confidence intervals, ablations of each component.
- **Validity.** Internal: hindsight optimum computed by a convex solver as ground truth; unit
  tests on the solver and on the menu's envy-freeness. External: sensitivity to churn rate,
  capacity volatility, tier mix and misreport fraction; stated limits of simulation-only evidence.
- **Reproducibility.** All code, seeds, configurations and figure scripts in this repository.

## 3. Devil's Advocate — Checkpoint 1

| # | Challenge | Severity | Response |
|---|---|---|---|
| 1 | Scope is too broad: home and public networks, every kind of uncertainty, pricing and fairness at once. | Major | Narrowed to one bottleneck and slot-level allocation; pricing-plan design and multi-hop are excluded (§1.4). Home and hotspot differ only in churn rate and tier mix, so they are two parameter regimes of one model. |
| 2 | "New algorithm" may be a bolt-together of drift-plus-penalty, alpha-fairness and a VCG-style payment. | Major | The contribution must be a result that fails for the naive composition, e.g. guarantees that depend on churn rate, or incentive compatibility that survives the coupling through shared dual prices. Phase 2 must check that this is open; if it is not, the RQ is revised before any implementation. |
| 3 | Strategic misreporting may be unrealistic if the operator classifies traffic by inspection. | Minor | Encrypted traffic and client-side marking (DSCP, application APIs) make self-declaration common; the incentive part is still an ablation that can be switched off. |
| 4 | Simulation-only evidence will not convince a networking venue. | Major | Target an optimisation / OR / performance-evaluation venue where theory plus trace-driven simulation is the norm; state the limitation explicitly. |
| 5 | No real operator data. | Minor | Use public traces where available; report which were not retrievable. |

**Verdict: PASS with conditions** — conditions 2 and 4 are carried into Phase 2 as explicit checks.
No Critical-severity issue.
