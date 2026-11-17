# 05 Closest prior art / novelty attack

Date of search: 2026-11-17. Role: adversarial novelty examiner. Targets the claim: Lyapunov drift-plus-penalty (DPP) / primal-dual online allocator for an ISP access point or home gateway with (i) persistent tier-level virtual queues (premium SLA, revenue, free floor/cap) and (ii) per-device deficit queues created at arrival that record how much a delay-tolerant device was short-changed relative to its tier's real-time bundle, with a deterministic sample-path bound on each deficit, envy-freeness up to a constant across QoS classes, approximate class-declaration incentive compatibility without payments, an O(1/V) gap / O(V) deficit trade-off, and per-device guarantees over a finite sojourn under churn.

Read-scope vocabulary: `full_text` (parts named) = PDF downloaded and text-extracted and read; `abstract_only` = abstract from the primary record (arXiv API or Crossref plus publisher/search snippet); `metadata_only` = bibliographic record verified, content known only from secondary snippets (flagged as such). Web pages are treated as data.

## 1. Search log

Tools: arXiv API (export.arxiv.org), Crossref REST API, WebSearch, WebFetch, curl + pdftotext. About 45 queries. Several PDF/HTML hosts returned 403 or connection reset (HKU, Illinois IDEALS, core.ac.uk); see section 5.

| # | Query theme | Result |
|---|---|---|
| 1 | "virtual queue" + "envy-free" / Lyapunov + incentive compatible / drift-plus-penalty + truthful (arXiv API, WebSearch) | No paper combines Lyapunov/virtual queues with envy-freeness. Lyapunov + truthfulness exists only with payments or randomized auctions (Li-Wu-Li 2015). Fairness virtual queues exist without incentives (Huang et al. 2020, 2011.01783; Kasgari-Saad 2018). |
| 2 | credit / debt / deficit fair scheduling with theory (Hou-Borkar-Kumar, DRR, Karma, BoPF, "borrow and repay") | Found Karma (OSDI'23), Credit Fairness (2026), BoPF (SIGMETRICS'19), DRR network calculus, Hou-Kumar debt papers, Elokda karma economies. |
| 3 | mixed real-time / elastic scheduling with fairness (Jaramillo-Srikant, Hou-Kumar, ElAzzouni, Anand URLLC/eMBB, Ewaisha) | Found; deficit counters here protect the real-time side, the reverse of our direction. |
| 4 | dynamic / online fair division with arrivals and departures (Kash, Friedman, Li-Li-Li, Benade, Zeng-Psomas, Aleksandrov-Walsh, Sinclair, Banerjee) | Found; fixed or abstract agents, indivisible/homogeneous goods, no Lyapunov, no QoS classes, no IC. |
| 5 | incentive-aware online allocation without money (Balseiro-Gurkan-Sun, Gorokh, Banerjee-Fikioris-Tardos, Fikioris, Dai-Golrezaei-Jaillet, Kandasamy) | Found; strongest incentive guarantees available, but one homogeneous good, no classes/tiers, no network churn model. |
| 6 | strategic class marking / IC DiffServ / IC slicing / home gateway tiers / Wi-Fi freemium | IC class choice via scheduler design: Karsten-Lin-Larson 2005 (outside window). Priority bidding with payments: Shnayder et al. 2014. Gateway credits: Wong et al. 2013/2015. Slicing IC papers are payment-based or Nash-equilibrium analyses. Freemium Wi-Fi papers are pricing games (Yu et al. 2016), no allocation guarantees. |
| 7 | tiered-SLA Lyapunov slicing with fairness | Virtual queues for slice SLAs are standard (Kasgari-Saad 2018 and others); none has envy/IC or per-device deficits. |
| 8 | "Lyapunov" + "finite sojourn" + per-user guarantee; "deferred service repaid later" | No hit combining these. |

Negative-result honesty: absence of a hit is not proof of absence. The unread items (Hou-Borkar-Kumar 2009, Li-Wu-Li 2015 full text, Karsten et al. 2005) are the main residual risks.

## 2. Per-source entries (ordered roughly by closeness)

### vuppalapati2023karma
Vuppalapati, Fikioris, Agarwal, Cidon, Khandelwal, Tardos. "Karma: Resource Allocation for Dynamic Demands." USENIX OSDI 2023.
- Identifier: arXiv:2305.17222 (confirmed via arXiv API, 2023-05-26, v2); OSDI'23 pages 645-662 taken from the USENIX presentation page seen in search (not independently confirmed via Crossref/DBLP).
- Read scope: full_text of arXiv PDF (model, algorithm, Theorems 1-4, churn paragraph, related work).
- Model/guarantees: one pooled resource in quanta; users have fair share and a guaranteed fraction alpha; users donate unused slices and earn credits, borrow and spend credits; priority goes to users with more credits (lower cumulative allocation). Theorem 1 Pareto efficiency; Theorem 2 online strategy-proofness (assuming honesty in past quanta, a user cannot raise current allocation by lying about current demand); Theorem 4 maximizes the minimum total allocation given fixed past allocations; Theorem 3 no gain for colluding groups. Churn: new user is bootstrapped with the average credit balance, described as heuristic; weights supported.
- Overlap: HIGH on the idea "long-term repayment by credit without money, online, strategy-proof, with churn".
- Difference: single homogeneous resource, one user type (demands, not QoS classes), no commercial tiers, no latency-critical vs elastic distinction, no Lyapunov/DPP, no O(1/V) gap, no per-device sojourn-wise bound; churn handled by a heuristic initial balance, not a guarantee. Strategy-proofness is one-shot (current-quantum, past honest), not class declaration. Does not subsume our claim but is the main benchmark.

### zahedi2026credit
Zahedi, Freeman. "Credit Fairness: Online Fairness in Shared Resource Pools." arXiv 2026.
- Identifier: arXiv:2601.17944 (arXiv API, v2 dated 2026-08-16 in PDF header).
- Read scope: full_text (abstract, intro, definitions, Theorems 2, 3, 5, 6 statements; algorithm LendRecoup).
- Model/guarantees: fixed set of agents with endowments and time-varying capped-linear demands. Credit fairness (CF): agents who lend in early rounds get priority to recoup; credit-adjusted endowments; agents "in debt" have their guaranteed minimum reduced. Theorem 3: no mechanism is anonymous, strategy-proof, credit fair and Pareto efficient simultaneously. LendRecoup is CF and PE (Theorems 5), online strategy-proof (Theorem 6). States all earlier PE mechanisms, including Karma, violate CF.
- Overlap: HIGH on formalizing "repay deferred agents later".
- Difference: fixed agent set, homogeneous resource, no real-time vs elastic classes, no tiers, no Lyapunov, no sojourn/churn. Importantly it contains an impossibility result (anonymity + SP + CF + PE) that our IC claim must be scoped against; our "approximate / constant-slack" notion is weaker and class-declaration based, which is the open niche.

### le2019bopf
Le, Sun, Chowdhury, Liu. "BoPF: Mitigating the Burstiness-Fairness Tradeoff in Multi-Resource Clusters." ACM SIGMETRICS Performance Evaluation Review 46(2):77-78, 2019 (extended abstract); full version arXiv.
- Identifier: Crossref DOI 10.1145/3305218.3305246; arXiv:1912.03523 (arXiv API, 2019-12-07).
- Read scope: full_text (abstract, intro, properties section, admission/allocation algorithm, strategyproofness statement; proofs in appendix only skimmed).
- Model/guarantees: latency-sensitive queues (LQ) and throughput-sensitive queues (TQ) in a multi-resource cluster. Bounded priority: LQ bursts get guaranteed resources only if the safety and fairness conditions (demand within long-term fair share) hold, so TQs keep long-term fairness; three classes (hard guarantee, soft guarantee, elastic) via admission control; leftover by DRF. Claims "first scheduler with long-term fairness, burst guarantee, Pareto efficiency, strategyproof"; strategyproofness is "weak" (limited incentive to lie about demand), proof in appendix.
- Overlap: HIGH structurally: real-time/bursty class gets priority now, batch class protected long-term, no money, strategyproof-ish, class admission.
- Difference: admission-control and static fair-share caps, not deficit queues repaid over time; no Lyapunov; no per-device finite-sojourn bound; no commercial tiers or revenue; cluster jobs not access-network flows; weak SP is about demand reports, not class declaration. Mentions BVT (borrowed virtual time) as the analogous scheduler idea.

### banerjee2023pseudo
Banerjee, Fikioris, Tardos. "Robust Pseudo-Markets for Reusable Public Resources." ACM EC 2023, p. 241.
- Identifier: Crossref DOI 10.1145/3580507.3597723; arXiv:2302.09127 (v4, DOI listed on arXiv record).
- Read scope: full_text (abstract, intro, Theorems 5.2, 5.4, 6.1, 7.2 statements; proofs not read).
- Model/guarantees: fixed agent set with fair-share budgets of artificial credits; each round a first-price pseudo-auction with selective reserve; Bayesian setting; each agent has a strategy guaranteeing 1/2 of ideal utility in expectation regardless of others; tight. Multi-round (reusable) demands.
- Overlap: MEDIUM (non-monetary, per-agent guarantee, strategic robustness).
- Difference: guarantee is a fraction of ideal utility in expectation, not sample-path; no arrivals/departures, no QoS classes, no Lyapunov, no tiers; incentives via equilibrium bidding, not class declaration.

### fikioris2025dmmf
Fikioris, Banerjee, Tardos. "Beyond Worst-Case Online Allocation via Dynamic Max-min Fairness." arXiv 2023 (DOI 10.1145/3736252.3742501 listed on the arXiv record; venue not independently confirmed).
- Identifier: arXiv:2310.08881 (arXiv API, v4).
- Read scope: abstract + introduction/main-results skim (full PDF extracted, theorems not read).
- Model/guarantees: DMMF gives each round's item to the requesting agent with fewest allocations so far; in large markets with i.i.d. values each agent can realize 1-o(1) of ideal utility under arbitrary behavior of others; extension to reusable resources.
- Overlap: MEDIUM (history-dependent fairness, large-market approximate incentive guarantees, per-agent).
- Difference: fixed agents, indivisible items, i.i.d. values, asymptotic guarantee; no churn, no classes, no queues/Lyapunov.

### dai2025iapd
Dai, Golrezaei, Jaillet. "Efficiency, Feasibility, and Incentive-Awareness in Constrained Online Resource Allocation." arXiv 2025 (v2 July 2026).
- Identifier: arXiv:2507.09473 (arXiv API).
- Read scope: abstract and introduction (full PDF extracted; algorithm sections not read).
- Model/guarantees: indivisible resources to strategic agents under long-term constraints. Shows vanilla online primal-dual is fragile: agents manipulate reports to distort dual variables. Proposes IAPD: VCG-based payment, epoch-based lazy dual updates, random exploration, optimistic dual learner; O~(sqrt T) welfare regret, constraints satisfied, near-truthful equilibrium.
- Overlap: MEDIUM-HIGH as a threat. It is the closest published statement that primal-dual / virtual-queue style dual variables are manipulable by misreports.
- Difference: uses payments (VCG) and sqrt(T) regret, no per-agent sojourn guarantees, no classes/tiers or envy bounds. But it directly warns that our per-device deficit queues, if fed by declared classes, are dual-like state that strategic devices can try to distort; our IC claim must address this.

### jaramillo2011elastic
Jaramillo, Srikant. "Optimal Scheduling for Fair Resource Allocation in Ad Hoc Networks With Elastic and Inelastic Traffic." IEEE/ACM Trans. Netw. 19(4):1125-1136, 2011 (INFOCOM 2010 version pp. 1-9).
- Identifier: Crossref DOI 10.1109/tnet.2010.2100083 (and INFOCOM DOI 10.1109/infocom.2010.5462048); arXiv:0907.5402 (v8).
- Read scope: full_text of arXiv (model, algorithm, Lemma 1 Lyapunov, Theorem 1, simulation discussion).
- Model/guarantees: best-effort (elastic, utility) and real-time (per-packet deadline, required delivery ratio) flows in an ad hoc network; dual decomposition gives joint congestion control + max-weight scheduling; deficit counters/virtual queues enforce the inelastic delivery ratio; positive recurrence and O(1/epsilon) expected deficit+queue bound.
- Overlap: MEDIUM-HIGH: mixed elastic/real-time, Lyapunov, deficit queues, 1/epsilon-type trade-off.
- Difference: the deficit queue belongs to the real-time flow (protecting its QoS), the opposite of ours (debt owed to the elastic flow); fixed set of flows, expected-value bounds not sample-path, no strategic behavior, no tiers, no envy notion.

### hou2009theory
Hou, Borkar, Kumar. "A Theory of QoS for Wireless." IEEE INFOCOM 2009, pp. 486-494.
- Identifier: Crossref DOI 10.1109/infcom.2009.5061954.
- Read scope: metadata_only. Content (largest-debt-first policies are feasibility-optimal; debt = target share minus received) from secondary summaries only (ergodicity.net conference summary, P. R. Kumar slides). Primary PDF (Illinois IDEALS) returned 403.
- Overlap: MEDIUM (the canonical "debt" scheduling theory).
- Difference (per secondary info, unverified): debt is per real-time client over a fixed set, for timely-throughput feasibility; no elastic-class repayment, no incentives, no churn.

### hou2010utility
Hou, Kumar. "Utility Maximization for Delay Constrained QoS in Wireless." IEEE INFOCOM 2010, pp. 1-9.
- Identifier: Crossref DOI 10.1109/infcom.2010.5462070; arXiv:0908.0362.
- Read scope: abstract + intro + theorem list (partial full_text).
- Content: utility maximization over delivery ratios; decomposition into a client problem and an access-point problem forming a bidding game in which selfish clients bid for service time and the equilibrium maximizes total utility; weighted-transmission policy achieving proportional fairness; relates to largest time-based-debt-first.
- Overlap: MEDIUM (selfish clients + AP, debt policy, fairness).
- Difference: payments-like bids (price game), real-time clients only, fixed client set, no classes of different QoS type, no Lyapunov deficit toward elastic users.

### hou2014heterogeneous
Hou, Kumar. "Scheduling Heterogeneous Real-Time Traffic over Fading Wireless Channels." INFOCOM 2010 pp. 1-9; IEEE/ACM ToN 22(5):1631-1644, 2014.
- Identifier: Crossref DOIs 10.1109/infcom.2010.5462090 and 10.1109/tnet.2013.2280846; arXiv:0908.0587.
- Read scope: abstract_only. Feasibility-optimal policies for heterogeneous deadlines, time-varying channels, rate adaptation.
- Overlap: LOW-MEDIUM (rate-adaptive real-time class). Difference: no elastic/tier/IC component.

### elazzouni2020deadline
ElAzzouni, Ekici, Shroff. "Is Deadline Oblivious Scheduling Efficient for Controlling Real-Time Traffic in Cellular Downlink Systems?" IEEE INFOCOM 2020, pp. 49-58.
- Identifier: Crossref DOI 10.1109/infocom41043.2020.9155523; arXiv:2002.06474.
- Read scope: abstract + intro (partial full_text).
- Content: latency-critical (VR, cloud gaming) flows with hard deadlines and concave partial-reward; online primal-dual DO algorithm (about 3.6-competitive); LFDO combines the Lyapunov framework with the primal-dual analysis to guarantee long-term per-user timely throughput.
- Overlap: MEDIUM (gaming/video latency-critical class, online primal-dual + Lyapunov, per-user long-term guarantee).
- Difference: only real-time traffic; guarantee is each user's timely throughput, not envy toward other classes; no elastic users' deficit, no tiers, no IC.

### wong2013myob
Wong, Joe-Wong, Ha, Liu, Chiang. "Mind Your Own Bandwidth: An Edge Solution to Peak-hour Broadband Congestion." arXiv 2013; extended in Wong et al., "Improving user QoE for residential broadband: Adaptive traffic management at the network edge," IEEE IWQoS 2015; chapter in "Fog for 5G and IoT" (2017, DOI 10.1002/9781119187202.ch2).
- Identifier: arXiv:1312.7844; Crossref DOI 10.1109/iwqos.2015.7404720 (IWQoS) and 10.1002/9781119187202.ch2 (chapter).
- Read scope: full_text partial (abstract, intro, credit distribution section, Lemma 1, Proposition 3; second level only skimmed).
- Content: ISP-home gateway two-level allocation. Level 1: gateways buy guaranteed bandwidth with virtual credits (fixed total, recirculated, budget caps against hoarding); two traffic tiers (credit-bought guaranteed vs free best-effort lowest priority). Level 2: gateway splits among apps/devices by user-set relative priorities; implemented on commodity routers.
- Overlap: MEDIUM: same domain (ISP + home gateway), credits, tiers, non-monetary fairness across gateways.
- Difference: credits operate across gateways at peak hours, not per-device deficits within a gateway; device priorities are user-declared with no incentive analysis; no Lyapunov, no sample-path bound, no churn guarantees, no revenue/SLA queues.

### shnayder2014truthful
Shnayder, Parkes, Kawadia, Hoon. "Truthful Prioritization for Dynamic Bandwidth Sharing." ACM MobiHoc 2014, pp. 235-244.
- Identifier: Crossref DOI 10.1145/2632951.2632956; arXiv:1408.1492 (as "Truthful Prioritization Schemes for Spectrum Sharing").
- Read scope: abstract + intro + model (partial full_text).
- Content: users bid values; strict priority queue by bid; payments via Babaioff-Kleinberg-Slivkins style scheme; incentive compatible given monotone stochastic demand; revenue pooling for sellers.
- Overlap: LOW-MEDIUM (incentive-compatible priority classes on shared bandwidth).
- Difference: IC obtained with payments and bids; our setting is money-free for class declaration and gives bounded envy rather than DSIC.

### li2015spectrum
Li, Wu, Li. "Socially-Optimal Online Spectrum Auctions for Secondary Wireless Communication." IEEE INFOCOM 2015, pp. 2047-2055.
- Identifier: Crossref DOI 10.1109/infocom.2015.7218589; DBLP key conf/infocom/LiWL15 (via search).
- Read scope: metadata_only (PDF host connection reset). Content from search abstracts: Lyapunov optimization for online channel evaluation, randomized winner determination, truthful in expectation, near offline optimum.
- Overlap: MEDIUM as proof that Lyapunov + truthfulness has been combined. Difference: auction (payments), randomization, social-welfare benchmark, secondary spectrum rather than per-device fairness/envy.

### benade2018envy
Benade, Kazachkov, Procaccia, Psomas. "How to Make Envy Vanish Over Time." ACM EC 2018, pp. 593-610.
- Identifier: Crossref DOI 10.1145/3219166.3219179.
- Read scope: abstract + intro (full_text PDF skimmed).
- Content: T indivisible items arrive online, n agents; deterministic algorithm with Envy_T in O~(sqrt(T/n)); tight; batches.
- Overlap: LOW-MEDIUM: deterministic envy bound over time. Difference: fixed agents, indivisible goods, bound grows with T (vanishing average), no churn, no classes, no queues.

### vardi2022dynamic (with friedman2015minimal, friedman2017controlled)
Vardi, Psomas, Friedman. "Dynamic Fair Resource Division." Math. Oper. Res. 47(2):945-968, 2022. Friedman, Psomas, Vardi. "Dynamic Fair Division with Minimal Disruptions." ACM EC 2015, pp. 697-713. "Controlled Dynamic Fair Division." ACM EC 2017, pp. 461-478.
- Identifier: Crossref DOIs 10.1287/moor.2021.1155, 10.1145/2764468.2764495, 10.1145/3033274.3085123.
- Read scope: vardi2022 abstract + intro (full_text PDF skimmed); the two EC papers metadata_only (+ search summaries).
- Content: one homogeneous divisible resource, users arrive and depart; limit on disruptions per arrival; fairness ratio (min share / ideal share); near-complete trade-off characterization and optimal algorithm.
- Overlap: MEDIUM: arrivals/departures with per-user guarantee. Difference: guarantee is a share ratio under a reallocation budget; no heterogeneous QoS, no incentives, no Lyapunov, no history/debt.

### li2018dynamic
Li, Li, Li. "Dynamic Fair Division Problem with General Valuations." IJCAI 2018, pp. 375-381.
- Identifier: Crossref DOI 10.24963/ijcai.2018/52; arXiv:1802.05294.
- Read scope: abstract_only (PDF extracted; not read beyond abstract).
- Content: divisible resource, players arrive/depart, general valuations; O(n)-envy-free and O(log n)-proportional algorithms with near-matching lower bounds.
- Overlap: MEDIUM (envy-freeness bound with arrivals/departures). Difference: envy factor grows with n and is multiplicative; ours claims additive constant between classes under a queueing model.

### kash2014noagent
Kash, Procaccia, Shah. "No Agent Left Behind: Dynamic Fair Division of Multiple Resources." J. Artif. Intell. Res. 51:579-603, 2014 (outside window).
- Identifier: Crossref DOI 10.1613/jair.4405.
- Read scope: metadata_only + search summary. Dynamic DRF with arrivals, envy-freeness and sharing incentives, no reallocation. Overlap LOW-MEDIUM. Difference: no departures with queues, no classes/IC via Lyapunov.

### zeng2020dynamic
Zeng, Psomas. "Fairness-Efficiency Tradeoffs in Dynamic Fair Division." ACM EC 2020, pp. 911-912.
- Identifier: Crossref DOI 10.1145/3391403.3399467; arXiv:1907.11672 (arXiv API).
- Read scope: abstract_only. Items arrive online to n fixed agents; envy/efficiency trade-offs under random vs adversarial values. Overlap LOW. Difference: indivisible items, fixed agents.

### sinclair2023sequential
Sinclair, Jain, Banerjee, Yu. "Sequential Fair Allocation: Achieving the Optimal Envy-Efficiency Trade-off Curve." Operations Research 71(5):1689-1705, 2023.
- Identifier: Crossref DOI 10.1287/opre.2022.2397; arXiv:2105.05308.
- Read scope: abstract_only. Counterfactual envy vs efficiency; GUARDED-HOPE. Overlap LOW-MEDIUM (explicit envy-efficiency frontier like ours O(1/V) vs O(V)). Difference: stochastic individuals over T rounds, no queues, no IC.

### banerjee2026perishable
Banerjee, Hssaine, Sinclair. "Online Fair Allocation of Perishable Resources." Operations Research 74(5):2748-2771, 2026.
- Identifier: Crossref DOI 10.1287/opre.2024.0847; arXiv:2406.02402.
- Read scope: abstract_only (PDF extracted). Budget of perishable resources, random arrivals per round, envy-efficiency lower bounds, algorithm with predictions. Overlap LOW. Difference: no per-agent sojourn, no queues, no IC, no classes.

### balseiro2019nomoney
Balseiro, Gurkan, Sun. "Multiagent Mechanism Design Without Money." Operations Research 67(5):1417-1436, 2019.
- Identifier: Crossref DOI 10.1287/opre.2018.1820.
- Read scope: metadata_only + abstract-level summary (search). A single resource each period among agents with private values, no payments; future allocations tied to reports; asymptotically first-best as patience grows; optimal convergence rate for two agents.
- Overlap: MEDIUM (money-free incentive via future allocation, i.e., repayment). Difference: infinite-horizon discounted, fixed agents, no queueing/QoS classes/churn, Bayesian private values.

### gorokh2021fisher
Gorokh, Banerjee, Iyer. "The Remarkable Robustness of the Repeated Fisher Market." ACM EC 2021, p. 562.
- Identifier: Crossref DOI 10.1145/3465456.3467560 (also SSRN 3411444).
- Read scope: metadata_only + abstract summary (search): artificial credits, repeated first-price auctions, each agent can secure about half of ideal utility regardless of others. Overlap LOW-MEDIUM. Difference: as banerjee2023pseudo.

### kandasamy2020maxmin
Kandasamy, Sela, Gonzalez, Jordan, Stoica. "Online Learning Demands in Max-min Fairness." arXiv 2020.
- Identifier: arXiv:2012.08648 (arXiv API).
- Read scope: abstract_only. Repeated max-min mechanism with demand feedback; efficient, fair, strategy-proof with learning; notes IC definitions are asymptotic/with high probability in multi-round settings. Overlap LOW-MEDIUM. Difference: compute-cluster users, no queues, no classes.

### li2026dynmech
Li, Chen. "Dynamic Mechanism Design without Monetary Transfers: A Queueing Theory Approach." arXiv 2026.
- Identifier: arXiv:2601.20728 (arXiv API; PDF download failed).
- Read scope: abstract_only. Agents and goods arrive stochastically and queue; no transfers; costly verification; optimal steady-state dynamic threshold mechanism. Overlap LOW-MEDIUM (money-free mechanism with queues and arrivals). Difference: principal-payoff optimal mechanism with verification, not fairness/envy, no QoS classes.

### balseiro2025regularized
Balseiro, Lu, Mirrokni. "Regularized Online Allocation Problems: Fairness and Beyond." ICML 2021 (PMLR 139:630-639); extended in Manufacturing & Service Operations Management 27(3):720-735, 2025.
- Identifier: Crossref DOI 10.1287/msom.2022.0212; arXiv:2007.00514.
- Read scope: abstract_only (+ search summary). Dual mirror descent with a regularizer (max-min fairness, load balancing) on cumulative consumption; sublinear regret. Overlap LOW-MEDIUM (primal-dual online fairness). Difference: aggregate fairness on groups/consumption, no per-agent guarantee, no incentives, no churn.

### gao2021onlinemarket
Gao, Kroer, Peysakhovich. "Online Market Equilibrium with Application to Fair Division." NeurIPS 2021.
- Identifier: arXiv:2103.12936 (arXiv API; NeurIPS proceedings not matched in Crossref).
- Read scope: abstract_only. Online Fisher market, PACE dynamics, asymptotic envy-freeness and Pareto optimality with O(log t / t) rates under i.i.d. items. Overlap LOW-MEDIUM. Difference: fixed buyers, i.i.d. goods, asymptotic.

### aleksandrov2020survey
Aleksandrov, Walsh. "Online Fair Division: A Survey." AAAI 2020 (34(9):13557-13562).
- Identifier: Crossref DOI 10.1609/aaai.v34i09.7081; arXiv:1911.09488.
- Read scope: abstract_only. Survey of online fair division. Overlap LOW; use for positioning (the literature largely treats indivisible goods, fixed agents, no queueing/Lyapunov).

### azevedo2019spl
Azevedo, Budish. "Strategy-proofness in the Large." Review of Economic Studies, 2019 (DOI 10.1093/restud/rdy042; NBER w23771).
- Identifier: Crossref DOI 10.1093/restud/rdy042 and 10.3386/w23771.
- Read scope: abstract-level (search summary). SP-L: truthfulness is approximately dominant for price-taking agents in large markets, evaluated against full-support i.i.d. play. Overlap LOW (tool for our IC definition). Use to scope "strategy-proof-in-the-large" claim: SP-L is ex-interim against i.i.d. play, a different notion from a sample-path envy bound.

### elokda2024karma
Elokda, Bolognani, Censi, Dorfler, Frazzoli. "A Self-Contained Karma Economy for the Dynamic Allocation of Common Resources." Dynamic Games and Applications 14(3):578-610, 2024 (online 2023).
- Identifier: Crossref DOI 10.1007/s13235-023-00503-0; arXiv:2207.00495. Related: arXiv:2404.02687 (J. Econ. Behav. Organ. 251:107771, 2026), arXiv:2412.17002.
- Read scope: abstract_only. Artificial-currency (karma) dynamic population game; stationary Nash equilibrium exists; efficient and ex-post fair under homogeneous future-aware agents. Overlap LOW-MEDIUM (money-free long-run fairness). Difference: pairwise bidding, equilibrium (not sample-path), no classes/queues.

### karsten2005incentive
Karsten, Lin, Larson. "Incentive-Compatible Differentiated Scheduling." ACM HotNets-IV, 2005 (outside window).
- Identifier: not found in Crossref; project page https://cs.uwaterloo.ca/~mkarsten/papers/hotnets2005.html seen in search results (page not fetched).
- Read scope: metadata_only (search snippet). Dynamic proportional rate allocation keeps FIFO delay differentiation so that each source's best response is to pick the class matching its delay target; claimed strategy-proof under stated assumptions.
- Overlap: MEDIUM as the oldest "class-declaration is incentive compatible by scheduler design, no money" result. Difference: static scheduler design for delay classes of packet traffic, not an online allocator under capacity uncertainty with tiers/churn.

### li2013regular
Li, Eryilmaz, Li. "Throughput-Optimal Wireless Scheduling with Regulated Inter-Service Times." INFOCOM 2013, pp. 2616-2624; journal: Li, Li, Eryilmaz, IEEE/ACM ToN 23(5):1542-1552, 2015.
- Identifier: Crossref DOIs 10.1109/infcom.2013.6567069 and 10.1109/tnet.2014.2333008; arXiv:1405.0625.
- Read scope: abstract_only (search + arXiv record). Time-since-last-service counter added to max-weight; throughput-optimal with regular service. Overlap LOW (a per-user lag counter with Lyapunov). Difference: bounded service gaps, no cross-class debt, no IC.

### wu2016application
Wu, Lin, Liu, Zhang. "Application-Level Scheduling With Probabilistic Deadline Constraints." IEEE/ACM ToN 24(3):1504-1517, 2016.
- Identifier: Crossref DOI 10.1109/tnet.2015.2416256.
- Read scope: metadata_only (search summary: delay-tolerant transmissions as deadline tasks, Earliest Positive-Debt Deadline First). Overlap LOW-MEDIUM (debt-based deadline policy for delay-tolerant traffic). Difference: debt defines deadline feasibility, not cross-class repayment or IC.

### anand2020urllc
Anand, de Veciana, Shakkottai. "Joint Scheduling of URLLC and eMBB Traffic in 5G Wireless Networks." IEEE/ACM ToN 28(2):477-490, 2020 (INFOCOM 2018 pp. 1970-1978).
- Identifier: Crossref DOIs 10.1109/tnet.2020.2968373, 10.1109/infocom.2018.8486430; arXiv:1712.05344.
- Read scope: abstract_only (search). Utility-maximizing eMBB scheduling aware of puncturing losses from URLLC; fixed user set, no incentives. Overlap LOW.

### ewaisha2018rtnrt
Ewaisha, Tepedelenlioglu. "Optimal Power Control and Scheduling for Real-Time and Non-Real-Time Data." IEEE Trans. Veh. Technol. 67(3):2727-2740, 2018.
- Identifier: Crossref DOI 10.1109/tvt.2017.2773569; arXiv:1705.02398.
- Read scope: abstract_only (search). Lyapunov drift; real-time QoS constraint, maximize non-real-time throughput. Overlap LOW-MEDIUM (RT/NRT with Lyapunov). Difference: no per-device repayment, no fairness among NRT users, no IC/tiers.

### kasgari2018slicing
Kasgari, Saad. "Stochastic Optimization and Control Framework for 5G Network Slicing with Effective Isolation." arXiv 2018.
- Identifier: arXiv:1801.10282 (arXiv API).
- Read scope: abstract_only (+ search summary: long-term QoS constraints turned into virtual queues, drift-plus-penalty). Overlap LOW (tier/slice-level virtual queues are standard). Difference: slice-level, no devices, no fairness/IC.

### zahedi-adjacent: quota2026
Sivan, Paes Leme, Tiuca, McFarlane, Gkatzelis, Mehta, Hassas Yeganeh, Mirrokni, Vahdat. "Quota Marketplace: Dynamic Pricing for Efficient Allocation of ML Training Resources." arXiv 2026.
- Identifier: arXiv:2607.09802 (arXiv API, 2026-07-09).
- Read scope: abstract + intro/Karma discussion (partial full_text). States Karma-style mechanisms fail Pareto/max-min properties with heterogeneous values and gives dynamic prices; points out manipulation by misreporting for credit-based mechanisms. Overlap LOW-MEDIUM; relevant as evidence that credit mechanisms lose properties under heterogeneous classes/values, which is exactly where our contribution sits.

### tabatabaee2022drr
Tabatabaee, Le Boudec. "Deficit Round-Robin: A Second Network Calculus Analysis." IEEE/ACM ToN 30(5):2216-2230, 2022 (RTAS 2021 pp. 171-183).
- Identifier: Crossref DOI 10.1109/tnet.2022.3164772; arXiv:2106.01034.
- Read scope: abstract_only (arXiv listing). Tight DRR delay/backlog bounds via network calculus. Overlap LOW (deficit counters in scheduling theory). Difference: packet scheduling bounds, no cross-class deficit repayment, no IC.

### estrada2025lying
Estrada Rodriguez, Ibrahim, Zhan. "On Customer (Dis-)Honesty in Unobservable Queues: The Role of Lying Aversion." Management Science (Crossref lists 2024; EconPapers lists 71(1):844-860, 2025).
- Identifier: Crossref DOI 10.1287/mnsc.2022.04036.
- Read scope: metadata_only + search summary (customers misreport urgency for priority; honor-policy optimal under conditions). Overlap LOW. Difference: behavioral lying-aversion model for a single queue.

## 3. BibTeX block (copied from the records above)

```bibtex
@inproceedings{vuppalapati2023karma,
  author    = {Vuppalapati, Midhul and Fikioris, Giannis and Agarwal, Rachit and Cidon, Asaf and Khandelwal, Anurag and Tardos, {\'E}va},
  title     = {Karma: Resource Allocation for Dynamic Demands},
  booktitle = {17th USENIX Symposium on Operating Systems Design and Implementation (OSDI 23)},
  year      = {2023},
  pages     = {645--662},
  note      = {arXiv:2305.17222}
}
@misc{zahedi2026credit,
  author = {Zahedi, Seyed Majid and Freeman, Rupert},
  title  = {Credit Fairness: Online Fairness In Shared Resource Pools},
  year   = {2026},
  eprint = {2601.17944},
  archivePrefix = {arXiv}
}
@article{le2019bopf,
  author  = {Le, Tan N. and Sun, Xiao and Chowdhury, Mosharaf and Liu, Zhenhua},
  title   = {BoPF},
  journal = {ACM SIGMETRICS Performance Evaluation Review},
  volume  = {46}, number = {2}, pages = {77--78}, year = {2019},
  doi     = {10.1145/3305218.3305246},
  note    = {Full version: arXiv:1912.03523, ``BoPF: Mitigating the Burstiness-Fairness Tradeoff in Multi-Resource Clusters''}
}
@inproceedings{banerjee2023pseudo,
  author    = {Banerjee, Siddhartha and Fikioris, Giannis and Tardos, {\'E}va},
  title     = {Robust Pseudo-Markets for Reusable Public Resources},
  booktitle = {Proceedings of the 24th ACM Conference on Economics and Computation},
  year      = {2023}, pages = {241},
  doi       = {10.1145/3580507.3597723},
  note      = {arXiv:2302.09127}
}
@misc{fikioris2025dmmf,
  author = {Fikioris, Giannis and Banerjee, Siddhartha and Tardos, {\'E}va},
  title  = {Beyond Worst-Case Online Allocation via Dynamic Max-min Fairness},
  year   = {2023}, eprint = {2310.08881}, archivePrefix = {arXiv},
  note   = {DOI listed on arXiv record: 10.1145/3736252.3742501}
}
@misc{dai2025iapd,
  author = {Dai, Yan and Golrezaei, Negin and Jaillet, Patrick},
  title  = {Efficiency, Feasibility, and Incentive-Awareness in Constrained Online Resource Allocation},
  year   = {2025}, eprint = {2507.09473}, archivePrefix = {arXiv}
}
@article{jaramillo2011elastic,
  author  = {Jaramillo, Juan Jose and Srikant, R.},
  title   = {Optimal Scheduling for Fair Resource Allocation in Ad Hoc Networks With Elastic and Inelastic Traffic},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {19}, number = {4}, pages = {1125--1136}, year = {2011},
  doi     = {10.1109/tnet.2010.2100083}
}
@inproceedings{hou2009theory,
  author    = {Hou, I-Hong and Borkar, Vivek and Kumar, P. R.},
  title     = {A Theory of {QoS} for Wireless},
  booktitle = {IEEE INFOCOM 2009},
  year      = {2009}, pages = {486--494},
  doi       = {10.1109/infcom.2009.5061954}
}
@inproceedings{hou2010utility,
  author    = {Hou, I-Hong and Kumar, P. R.},
  title     = {Utility Maximization for Delay Constrained {QoS} in Wireless},
  booktitle = {2010 Proceedings IEEE INFOCOM},
  year      = {2010}, pages = {1--9},
  doi       = {10.1109/infcom.2010.5462070}
}
@article{hou2014heterogeneous,
  author  = {Hou, I-Hong and Kumar, P. R.},
  title   = {Scheduling Heterogeneous Real-Time Traffic Over Fading Wireless Channels},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {22}, number = {5}, pages = {1631--1644}, year = {2014},
  doi     = {10.1109/tnet.2013.2280846},
  note    = {Conference version: INFOCOM 2010, doi 10.1109/infcom.2010.5462090}
}
@inproceedings{elazzouni2020deadline,
  author    = {ElAzzouni, Sherif and Ekici, Eylem and Shroff, Ness},
  title     = {Is Deadline Oblivious Scheduling Efficient for Controlling Real-Time Traffic in Cellular Downlink Systems?},
  booktitle = {IEEE INFOCOM 2020},
  year      = {2020}, pages = {49--58},
  doi       = {10.1109/infocom41043.2020.9155523}
}
@misc{wong2013myob,
  author = {Wong, Felix Ming Fai and Joe-Wong, Carlee and Ha, Sangtae and Liu, Zhenming and Chiang, Mung},
  title  = {Mind Your Own Bandwidth: An Edge Solution to Peak-hour Broadband Congestion},
  year   = {2013}, eprint = {1312.7844}, archivePrefix = {arXiv}
}
@inproceedings{wong2015qoe,
  author    = {Wong, Felix Ming Fai and Joe-Wong, Carlee and Ha, Sangtae and Liu, Zhenming and Chiang, Mung},
  title     = {Improving user {QoE} for residential broadband: Adaptive traffic management at the network edge},
  booktitle = {2015 IEEE 23rd International Symposium on Quality of Service (IWQoS)},
  year      = {2015},
  doi       = {10.1109/iwqos.2015.7404720}
}
@inproceedings{shnayder2014truthful,
  author    = {Shnayder, Victor and Parkes, David C. and Kawadia, Vikas and Hoon, Jeremy},
  title     = {Truthful Prioritization for Dynamic Bandwidth Sharing},
  booktitle = {Proceedings of the 15th ACM International Symposium on Mobile Ad Hoc Networking and Computing (MobiHoc)},
  year      = {2014}, pages = {235--244},
  doi       = {10.1145/2632951.2632956}
}
@inproceedings{li2015spectrum,
  author    = {Li, Hongxing and Wu, Chuan and Li, Zongpeng},
  title     = {Socially-optimal online spectrum auctions for secondary wireless communication},
  booktitle = {2015 IEEE Conference on Computer Communications (INFOCOM)},
  year      = {2015}, pages = {2047--2055},
  doi       = {10.1109/infocom.2015.7218589}
}
@inproceedings{benade2018envy,
  author    = {Benade, Gerdus and Kazachkov, Aleksandr and Procaccia, Ariel D. and Psomas, Christos-Alexandros},
  title     = {How to Make Envy Vanish Over Time},
  booktitle = {Proceedings of the 2018 ACM Conference on Economics and Computation},
  year      = {2018}, pages = {593--610},
  doi       = {10.1145/3219166.3219179}
}
@article{vardi2022dynamic,
  author  = {Vardi, Shai and Psomas, Alexandros and Friedman, Eric},
  title   = {Dynamic Fair Resource Division},
  journal = {Mathematics of Operations Research},
  volume  = {47}, number = {2}, pages = {945--968}, year = {2022},
  doi     = {10.1287/moor.2021.1155}
}
@inproceedings{friedman2015minimal,
  author    = {Friedman, Eric and Psomas, Christos-Alexandros and Vardi, Shai},
  title     = {Dynamic Fair Division with Minimal Disruptions},
  booktitle = {Proceedings of the Sixteenth ACM Conference on Economics and Computation},
  year      = {2015}, pages = {697--713},
  doi       = {10.1145/2764468.2764495}
}
@inproceedings{friedman2017controlled,
  author    = {Friedman, Eric and Psomas, Christos-Alexandros and Vardi, Shai},
  title     = {Controlled Dynamic Fair Division},
  booktitle = {Proceedings of the 2017 ACM Conference on Economics and Computation},
  year      = {2017}, pages = {461--478},
  doi       = {10.1145/3033274.3085123}
}
@inproceedings{li2018dynamic,
  author    = {Li, Bo and Li, Wenyang and Li, Yingkai},
  title     = {Dynamic Fair Division Problem with General Valuations},
  booktitle = {Proceedings of the Twenty-Seventh International Joint Conference on Artificial Intelligence (IJCAI)},
  year      = {2018}, pages = {375--381},
  doi       = {10.24963/ijcai.2018/52}
}
@article{kash2014noagent,
  author  = {Kash, Ian and Procaccia, Ariel D. and Shah, Nisarg},
  title   = {No Agent Left Behind: Dynamic Fair Division of Multiple Resources},
  journal = {Journal of Artificial Intelligence Research},
  volume  = {51}, pages = {579--603}, year = {2014},
  doi     = {10.1613/jair.4405}
}
@inproceedings{zeng2020dynamic,
  author    = {Zeng, David and Psomas, Alexandros},
  title     = {Fairness-Efficiency Tradeoffs in Dynamic Fair Division},
  booktitle = {Proceedings of the 21st ACM Conference on Economics and Computation},
  year      = {2020}, pages = {911--912},
  doi       = {10.1145/3391403.3399467}
}
@article{sinclair2023sequential,
  author  = {Sinclair, Sean R. and Jain, Gauri and Banerjee, Siddhartha and Yu, Christina Lee},
  title   = {Sequential Fair Allocation: Achieving the Optimal Envy-Efficiency Trade-off Curve},
  journal = {Operations Research},
  volume  = {71}, number = {5}, pages = {1689--1705}, year = {2023},
  doi     = {10.1287/opre.2022.2397}
}
@article{banerjee2026perishable,
  author  = {Banerjee, Siddhartha and Hssaine, Chamsi and Sinclair, Sean R.},
  title   = {Online Fair Allocation of Perishable Resources},
  journal = {Operations Research},
  volume  = {74}, number = {5}, pages = {2748--2771}, year = {2026},
  doi     = {10.1287/opre.2024.0847}
}
@article{balseiro2019nomoney,
  author  = {Balseiro, Santiago R. and Gurkan, Huseyin and Sun, Peng},
  title   = {Multiagent Mechanism Design Without Money},
  journal = {Operations Research},
  volume  = {67}, number = {5}, pages = {1417--1436}, year = {2019},
  doi     = {10.1287/opre.2018.1820}
}
@inproceedings{gorokh2021fisher,
  author    = {Gorokh, Artur and Banerjee, Siddhartha and Iyer, Krishnamurthy},
  title     = {The Remarkable Robustness of the Repeated Fisher Market},
  booktitle = {Proceedings of the 22nd ACM Conference on Economics and Computation},
  year      = {2021}, pages = {562},
  doi       = {10.1145/3465456.3467560}
}
@misc{kandasamy2020maxmin,
  author = {Kandasamy, Kirthevasan and Sela, Gur-Eyal and Gonzalez, Joseph E. and Jordan, Michael I. and Stoica, Ion},
  title  = {Online Learning Demands in Max-min Fairness},
  year   = {2020}, eprint = {2012.08648}, archivePrefix = {arXiv}
}
@misc{li2026dynmech,
  author = {Li, Zihao and Chen, Xuandong},
  title  = {Dynamic Mechanism Design without Monetary Transfers: A Queueing Theory Approach},
  year   = {2026}, eprint = {2601.20728}, archivePrefix = {arXiv}
}
@article{balseiro2025regularized,
  author  = {Balseiro, Santiago and Lu, Haihao and Mirrokni, Vahab},
  title   = {Regularized Online Allocation Problems: Fairness and Beyond},
  journal = {Manufacturing \& Service Operations Management},
  volume  = {27}, number = {3}, pages = {720--735}, year = {2025},
  doi     = {10.1287/msom.2022.0212},
  note    = {Conference version: ICML 2021, PMLR 139:630--639; arXiv:2007.00514}
}
@misc{gao2021onlinemarket,
  author = {Gao, Yuan and Kroer, Christian and Peysakhovich, Alex},
  title  = {Online Market Equilibrium with Application to Fair Division},
  year   = {2021}, eprint = {2103.12936}, archivePrefix = {arXiv},
  note   = {NeurIPS 2021}
}
@inproceedings{aleksandrov2020survey,
  author    = {Aleksandrov, Martin and Walsh, Toby},
  title     = {Online Fair Division: A Survey},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume    = {34}, number = {9}, pages = {13557--13562}, year = {2020},
  doi       = {10.1609/aaai.v34i09.7081}
}
@article{azevedo2019spl,
  author  = {Azevedo, Eduardo M. and Budish, Eric},
  title   = {Strategy-proofness in the Large},
  journal = {The Review of Economic Studies},
  year    = {2019},
  doi     = {10.1093/restud/rdy042}
}
@article{elokda2024karma,
  author  = {Elokda, Ezzat and Bolognani, Saverio and Censi, Andrea and D{\"o}rfler, Florian and Frazzoli, Emilio},
  title   = {A Self-Contained Karma Economy for the Dynamic Allocation of Common Resources},
  journal = {Dynamic Games and Applications},
  volume  = {14}, number = {3}, pages = {578--610}, year = {2024},
  doi     = {10.1007/s13235-023-00503-0}
}
@article{li2015regular,
  author  = {Li, Bin and Li, Ruogu and Eryilmaz, Atilla},
  title   = {Throughput-Optimal Scheduling Design With Regular Service Guarantees in Wireless Networks},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {23}, number = {5}, pages = {1542--1552}, year = {2015},
  doi     = {10.1109/tnet.2014.2333008}
}
@article{wu2016application,
  author  = {Wu, Xiaohan and Lin, Xiaojun and Liu, Jia and Zhang, Junshan},
  title   = {Application-Level Scheduling With Probabilistic Deadline Constraints},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {24}, number = {3}, pages = {1504--1517}, year = {2016},
  doi     = {10.1109/tnet.2015.2416256}
}
@article{anand2020urllc,
  author  = {Anand, Arjun and de Veciana, Gustavo and Shakkottai, Sanjay},
  title   = {Joint Scheduling of {URLLC} and {eMBB} Traffic in 5G Wireless Networks},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {28}, number = {2}, pages = {477--490}, year = {2020},
  doi     = {10.1109/tnet.2020.2968373}
}
@article{ewaisha2018rtnrt,
  author  = {Ewaisha, Ahmed and Tepedelenlioglu, Cihan},
  title   = {Optimal Power Control and Scheduling for Real-Time and Non-Real-Time Data},
  journal = {IEEE Transactions on Vehicular Technology},
  volume  = {67}, number = {3}, pages = {2727--2740}, year = {2018},
  doi     = {10.1109/tvt.2017.2773569}
}
@misc{kasgari2018slicing,
  author = {Kasgari, Ali Taleb Zadeh and Saad, Walid},
  title  = {Stochastic Optimization and Control Framework for 5G Network Slicing with Effective Isolation},
  year   = {2018}, eprint = {1801.10282}, archivePrefix = {arXiv}
}
@misc{sivan2026quota,
  author = {Sivan, Balasubramanian and Paes Leme, Renato and Tiuca, Mihai and McFarlane, Ian and Gkatzelis, Vasilis and Mehta, Nehal and Hassas Yeganeh, Soheil and Mirrokni, Vahab and Vahdat, Amin},
  title  = {Quota Marketplace: Dynamic Pricing for Efficient Allocation of ML Training Resources},
  year   = {2026}, eprint = {2607.09802}, archivePrefix = {arXiv}
}
@article{tabatabaee2022drr,
  author  = {Tabatabaee, Seyed Mohammadhossein and Le Boudec, Jean-Yves},
  title   = {Deficit Round-Robin: A Second Network Calculus Analysis},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {30}, number = {5}, pages = {2216--2230}, year = {2022},
  doi     = {10.1109/tnet.2022.3164772}
}
@article{estrada2025lying,
  author  = {Estrada Rodriguez, Ibrahim and Zhan},
  title   = {On Customer (Dis-)Honesty in Unobservable Queues: The Role of Lying Aversion},
  journal = {Management Science},
  doi     = {10.1287/mnsc.2022.04036},
  note    = {Author list given only as surnames by Crossref (Estrada Rodriguez, Ibrahim, Zhan); verify full names before citing}
}
@inproceedings{karsten2005incentive,
  author    = {Karsten, Martin and Lin, Yunfeng and Larson, Kate},
  title     = {Incentive-Compatible Differentiated Scheduling},
  booktitle = {HotNets-IV},
  year      = {2005},
  note      = {Not found in Crossref; bibliographic data from search snippets of the author's project page. UNVERIFIED against a primary record}
}
```

## 4. Items verified only partially (cite with care)
- hou2009theory: DOI and venue verified via Crossref; content not read.
- li2015spectrum: DOI/venue verified via Crossref; content from search abstracts only.
- karsten2005incentive: no primary record retrieved.
- fikioris2025dmmf: publication venue for DOI 10.1145/3736252.3742501 not independently confirmed.
- vuppalapati2023karma: pages 645-662 from the USENIX presentation page snippet, not Crossref.
- estrada2025lying: year and volume differ between Crossref (2024) and EconPapers (71(1), 2025); author given names not retrieved.

## 5. Could not verify / retrieve
- Hou-Borkar-Kumar INFOCOM 2009 full text (Illinois IDEALS returned 403; no arXiv version found).
- Li-Wu-Li INFOCOM 2015 full text (hku.hk and georgetown hosts reset the connection; hub.hku.hk 403). Whether it uses explicit virtual queues is unconfirmed.
- Li and Chen 2026 (arXiv:2601.20728) PDF download failed; abstract only.
- Karsten-Lin-Larson HotNets 2005: no Crossref/DBLP record retrieved.
- Gorokh-Banerjee-Iyer and Balseiro-Gurkan-Sun: only abstracts via secondary pages.
- Azevedo-Budish full paper not read; only abstract-level summary.
- Neely, "Opportunistic scheduling with worst case delay guarantees" (INFOCOM 2011): title seen in search results only; no record retrieved. It is the likeliest source of epsilon-persistent / deficit-style virtual queues giving sample-path bounds, and should be checked before claiming a deterministic deficit bound is new as a technique.
- Searches for IC network slicing and Wi-Fi freemium returned only payment-based or game-equilibrium work; no paper retrieved that is money-free with allocation guarantees.
- Any IEEE Xplore / ACM DL paywalled pages in 2024-2026 not indexed by the search tool may exist and are not reflected here.

## 6. NOVELTY VERDICT

**Already known (be blunt).** The following are not defensible as novel: (1) credit/debt/deficit mechanisms that let latency-sensitive users get priority now while others are repaid later, with no money and online strategy-proofness (Karma, OSDI 2023; BoPF, 2019; Credit Fairness, 2026; Balseiro-Gurkan-Sun 2019 for the money-free "pay with future allocation" idea); (2) per-flow deficit counters/virtual queues inside Lyapunov or dual schemes for mixed elastic/real-time traffic (Jaramillo-Srikant; Hou-Kumar; ElAzzouni et al. for gaming/VR); (3) slice- or tier-level virtual queues for SLA constraints (standard drift-plus-penalty practice); (4) deterministic envy bounds over time and dynamic fair division with arrivals and departures (Benade et al.; Friedman-Psomas-Vardi; Li-Li-Li); (5) credit-based home-gateway bandwidth allocation by an ISP (Wong et al.); (6) the observation that primal-dual dual variables can be gamed by strategic reports (Dai et al. 2025); (7) class-declaration incentive compatibility via scheduler design (Karsten et al. 2005) and Lyapunov plus truthfulness with payments (Li-Wu-Li 2015).

**Appears open (no hit found).** The specific combination: a Lyapunov DPP allocator in which the deficit queue is created at each device's arrival and measures shortfall relative to the real-time bundle of its own tier; a deterministic sample-path deficit bound that translates into envy-freeness up to an additive constant across heterogeneous QoS classes (elastic, rate-adaptive video, latency-critical); the resulting money-free approximate IC of class declaration; the O(1/V) gap with O(V) deficit trade-off; and guarantees stated per device over a finite sojourn under churn, together with persistent tier-level queues for revenue/SLA/free-floor. Karma and Credit Fairness handle churn heuristically or not at all and assume one homogeneous user type; BoPF uses admission control, not deficits; Jaramillo-Srikant's deficit points the other way.

**How to reposition.** Do not claim to introduce credit, debt or money-free fairness. Claim a drift-plus-penalty construction with arrival-indexed per-device deficit queues giving a sample-path bound and constant envy between QoS classes under churn, with commercial tiers. Use Karma, BoPF and Credit Fairness as baselines. State IC as approximate (constant slack, optionally strategy-proof-in-the-large) and address the Dai et al. manipulation channel and the Zahedi-Freeman impossibility. Check Neely's worst-case-delay virtual queues before calling the bounding technique new.
