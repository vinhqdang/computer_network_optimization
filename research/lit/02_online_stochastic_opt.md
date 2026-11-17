# Literature strand 02: Stochastic network optimisation and online learning for resource allocation

Date of search and verification: 2026-11-17.
Features tracked: F1 churn / dynamic arrivals-departures; F2 heterogeneous QoS utilities incl. inelastic/real-time; F3 tier/business constraints (SLA, revenue); F4 fairness; F5 incentive compatibility / strategic users.

## 1. Search log

Tools: curl against Crossref REST API (`api.crossref.org/works?query.bibliographic=` and `/works/<DOI>`), arXiv export API (`export.arxiv.org/api/query`, title and all-field queries), JMLR / PMLR / NeurIPS proceedings pages (citation_* meta tags), arXiv PDFs read with pdftotext. DBLP was attempted but returned a bot-challenge page (HTTP 202), so it was not used. Crossref returned HTTP 429 intermittently; affected queries were retried with delays.

Queries run (title or topic, source):
- Crossref/arXiv title queries for every seminal item named in the brief: Neely-Modiano-Li fairness; Georgiadis-Neely-Tassiulas; Neely monograph; Huang-Neely delay reduction; Stolyar (gradient scheduling, greedy primal-dual); Eryilmaz-Srikant; Mahdavi-Jin-Yang; Jenatton et al.; Yu-Neely-Wei; Yu-Neely low complexity; Chen-Ling-Giannakis; Cao-Liu; Mannor-Tsitsiklis-Yu; Balseiro-Lu-Mirrokni (two papers); BwK; adversarial BwK.
- Topic searches (arXiv all-field): "Lyapunov drift-plus-penalty incentive compatible online mechanism strategic users virtual queue"; "online fair allocation dynamic arrivals departures agents envy regret"; "online convex optimization long-term constraints dynamic regret time-varying"; "reinforcement learning bandwidth allocation home Wi-Fi QoS"; "online resource allocation with strategic agents misreport type truthful dual mirror descent"; "Lyapunov optimization virtual queue fairness constraint per-user guarantee churn arrivals departures"; "online learning dynamic set of agents arrivals departures ... sleeping"; "dynamic user arrivals and departures Lyapunov drift-plus-penalty ... per-user delay guarantee" (Crossref); "Lyapunov ... online incentive mechanism truthful users arriving departing virtual queue" (Crossref, returned nothing relevant).
- Fair online allocation queries: Talebi-Proutiere; Benade et al.; Sinclair et al. (two arXiv papers); Banerjee et al.; Gkatzelis et al.; Gao-Kroer-Peysakhovich; Liao-Gao-Kroer; Procaccia-Schiffer-Zhang; Kash-Procaccia-Shah.
- Bandit/fairness queries: Li-Liu-Ji; Patil et al.; Kleinberg et al.
- Constrained OCO (post-2019): Yi et al.; Guo et al.; Sinha-Vaze; Liu-Wu-Huang-Fang; Kim-Lee; Chen-Giannakis.
- Worst-case delay and real-time QoS: Neely worst-case delay; Neely delay-based NUM; Hou-Borkar-Kumar.

Items found by search but excluded from the main list as off-target: Ekbatani-Feng-Niazadeh "Online Resource Allocation with Cancellations" (arXiv 2210.11570, read abstract: buyback/competitive-ratio model, not user churn); Grosof-Mitzenmacher "Incentive Compatible Queues Without Money" (arXiv 2202.05747, seen in search only, not read); Pulido et al. techrxiv Wi-Fi RL preprint (not peer reviewed, not read).

Note: the shared scratchpad already contained other PDFs not downloaded by this agent; they were not used.

## 2. Verified sources

Read-scope vocabulary: `metadata_only` (record confirms bibliographic data only), `abstract_only`, `full_text (sections)`. "Located passages" means I searched the PDF text for specific statements and read those passages, not the whole paper.

### neely2010stochastic
M. J. Neely, *Stochastic Network Optimization with Application to Communication and Queueing Systems*, Synthesis Lectures on Learning, Networks, and Algorithms, 2010.
- Identifier: DOI 10.1007/978-3-031-79995-2. Confirmed: Crossref record (type book, same title, author Michael J. Neely).
- Read scope: metadata_only.
- Summary: The record confirms existence only. The monograph is the standard reference for Lyapunov drift-plus-penalty and virtual queues; I did not read it here, so no claim about its content is based on reading.
- F1 no, F2 no, F3 no, F4 no, F5 no (not assessed; not read).
- Relevance: Canonical citation for the drift-plus-penalty / virtual-queue toolbox.

### georgiadis2006resource
L. Georgiadis, M. J. Neely, L. Tassiulas, "Resource Allocation and Cross-Layer Control in Wireless Networks", Foundations and Trends in Networking 1(1):1-144, 2006.
- Identifier: DOI 10.1561/1300000001. Confirmed: Crossref record (volume 1, issue 1, pp. 1-144, 2006-04-16).
- Read scope: metadata_only (Crossref abstract is a generic intro paragraph about layered wireless networks).
- Summary: Survey/monograph on cross-layer resource allocation in wireless networks, the usual reference for utility maximisation with queue stability. Contents not read.
- F1 no, F2 no, F3 no, F4 partial (utility-fairness framework per its topic, unread), F5 no.
- Relevance: Foundation reference for stochastic network utility maximisation.

### neely2008fairness
M. J. Neely, E. Modiano, C.-P. Li, "Fairness and Optimal Stochastic Control for Heterogeneous Networks", IEEE/ACM Transactions on Networking 16(2):396-409, 2008. (Conference version: IEEE INFOCOM 2005, vol. 3, pp. 1723-1734, DOI 10.1109/infocom.2005.1498453.)
- Identifier: DOI 10.1109/tnet.2007.900405. Confirmed: Crossref record (issue 2, 2008-04).
- Read scope: metadata_only.
- Summary: Record confirms title and venue. Known as the source of the fairness-plus-stochastic-control (drift-plus-penalty with a fairness utility) framework for heterogeneous networks; not read here.
- F1 no, F2 no, F3 no, F4 yes (by title, unread), F5 no.
- Relevance: Named in the brief as the fairness anchor for Lyapunov control.

### stolyar2005asymptotic
A. L. Stolyar, "On the Asymptotic Optimality of the Gradient Scheduling Algorithm for Multiuser Throughput Allocation", Operations Research 53(1):12-25, 2005.
- Identifier: DOI 10.1287/opre.1040.0156. Confirmed: Crossref record, abstract present.
- Read scope: abstract_only (Crossref abstract, first sentences: N queues served by a generalized switch with random state; scheduling of N data users in a shared time-varying wireless channel).
- Summary: Studies a gradient scheduling rule for a generalized switch with random state and shows (per the title) asymptotic optimality for throughput allocation. Details not read.
- F1 no, F2 no, F3 no, F4 yes (utility-based throughput allocation, from title/abstract scope), F5 no.
- Relevance: Gradient-rule baseline for fixed-user-set fair throughput allocation.

### stolyar2005maximizing
A. L. Stolyar, "Maximizing Queueing Network Utility subject to Stability: Greedy Primal-Dual Algorithm", Queueing Systems 50(4):401-457, 2005.
- Identifier: DOI 10.1007/s11134-005-1450-0. Confirmed: Crossref record (volume 50, issue 4, pp. 401-457, 2005-08).
- Read scope: metadata_only.
- Summary: Record confirms the title of the greedy primal-dual algorithm paper. Content not read.
- F1 no, F2 no, F3 no, F4 partial (utility maximisation, unread), F5 no.
- Relevance: The greedy primal-dual alternative to drift-plus-penalty for utility maximisation.

### eryilmaz2007fair
A. Eryilmaz, R. Srikant, "Fair Resource Allocation in Wireless Networks Using Queue-Length-Based Scheduling and Congestion Control", IEEE/ACM Transactions on Networking 15(6):1333-1344, 2007. (Conference version: IEEE INFOCOM 2005, vol. 3, pp. 1794-1803, DOI 10.1109/infocom.2005.1498459.)
- Identifier: DOI 10.1109/tnet.2007.897944. Confirmed: Crossref record (issue 6, 2007-12).
- Read scope: metadata_only.
- Summary: Record confirms the title (fair allocation via queue-length-based scheduling plus congestion control). Not read.
- F1 no, F2 no, F3 no, F4 yes (by title), F5 no.
- Relevance: Classic alpha-fair allocation with queue-based control, fixed flow set.

### huang2011delay
L. Huang, M. J. Neely, "Delay Reduction via Lagrange Multipliers in Stochastic Network Optimization", IEEE Transactions on Automatic Control 56(4):842-857, 2011. (Conference version: WiOpt 2009, DOI 10.1109/wiopt.2009.5291609.)
- Identifier: DOI 10.1109/tac.2010.2067371. Confirmed: Crossref record (volume 56, issue 4, pp. 842-857, 2011-04).
- Read scope: metadata_only.
- Summary: Record confirms the title. Not read.
- F1 no, F2 partial (delay), F3 no, F4 no, F5 no.
- Relevance: Named in the brief for delay behaviour of drift-plus-penalty; relevant to the O(V) queue vs O(1/V) optimality gap trade-off.

### neely2011worstcase
M. J. Neely, "Opportunistic Scheduling with Worst Case Delay Guarantees in Single and Multi-Hop Networks", Proceedings IEEE INFOCOM 2011, pp. 1728-1736.
- Identifier: DOI 10.1109/infcom.2011.5934971 (spelling as in Crossref). Confirmed: Crossref record.
- Read scope: metadata_only.
- Summary: Record confirms the title. By title it concerns deterministic worst-case delay guarantees within a Lyapunov framework; not read.
- F1 no, F2 partial (delay guarantees), F3 no, F4 no, F5 no.
- Relevance: The nearest drift-plus-penalty-style deterministic per-item delay bound; a possible template for a per-agent sojourn guarantee (items are packets, not agents).

### neely2013delaybased
M. J. Neely, "Delay-Based Network Utility Maximization", IEEE/ACM Transactions on Networking 21(1):41-54, 2013. (INFOCOM 2010 version: DOI 10.1109/infcom.2010.5462097.)
- Identifier: DOI 10.1109/tnet.2012.2191157. Confirmed: Crossref record (volume 21, pp. 41-54, 2013-02).
- Read scope: metadata_only.
- Summary: Record confirms the title (utility maximisation with delay in the objective). Not read.
- F1 no, F2 partial (delay-sensitive utility), F3 no, F4 partial (NUM), F5 no.
- Relevance: Delay-dependent utilities inside a Lyapunov framework, relevant to latency-critical classes.

### hou2009theory
I.-H. Hou, V. Borkar, P. R. Kumar, "A Theory of QoS for Wireless", IEEE INFOCOM 2009, pp. 486-494.
- Identifier: DOI 10.1109/infocom.2009.5061954. Confirmed: Crossref search record (the direct /works/<DOI> lookup returned 404 for this DOI, but the search record matched exactly).
- Read scope: metadata_only.
- Summary: Record confirms the title. By its known scope it models per-client QoS requirements (delay-bounded delivery ratios) on a wireless channel; not read here.
- F1 no, F2 yes (real-time / deadline QoS, from title scope, unread), F3 partial, F4 no, F5 no.
- Relevance: Real-time (inelastic) QoS in a shared wireless channel with a fixed client set.

### mahdavi2012trading
M. Mahdavi, R. Jin, T. Yang, "Trading Regret for Efficiency: Online Convex Optimization with Long Term Constraints", Journal of Machine Learning Research 13(81):2503-2528, 2012.
- Identifier: jmlr.org/papers/v13/mahdavi12a.html (citation meta tags: JMLR vol 13, issue 81, pp. 2503-2528, 2012); arXiv 1111.6082. Confirmed: both records fetched.
- Read scope: abstract_only (arXiv abstract). Yu-Neely (below) states the guarantees: O(sqrt T) regret with O(T^{3/4}) violation in general, O(T^{2/3}) for both for linear constraints.
- Summary: Introduces OCO where functional constraints need only hold in the long run, avoiding projection. The rates above are as restated in Yu-Neely's abstract, which I read, not from this paper's text.
- F1 no, F2 no, F3 partial (long-term constraints), F4 no, F5 no.
- Relevance: Origin of the long-term-constraint OCO line.

### jenatton2016adaptive
R. Jenatton, J. Huang, C. Archambeau, "Adaptive Algorithms for Online Convex Optimization with Long-term Constraints", Proceedings of ICML 2016, PMLR 48:402-411.
- Identifier: proceedings.mlr.press/v48/jenatton16.html (meta: ICML, 2016/06/11, pp. 402-411); arXiv 1512.07422. Confirmed: both fetched.
- Read scope: abstract_only (arXiv).
- Summary: Adaptive online gradient method with trade-off parameter beta in (0,1): regret O(T^{max{beta,1-beta}}) and constraint violation O(T^{1-beta/2}); no knowledge of T needed.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Intermediate point between Mahdavi et al. and Yu-Neely.

### mannor2009online
S. Mannor, J. N. Tsitsiklis, J. Y. Yu, "Online Learning with Sample Path Constraints", Journal of Machine Learning Research 10(20):569-590, 2009.
- Identifier: jmlr.org/papers/v10/mannor09a.html (meta tags confirm authors, volume, pp.). Confirmed.
- Read scope: metadata_only.
- Summary: Record confirms existence. Yu-Neely-Wei's introduction (which I read) says Mannor et al. extend OCO to arbitrarily varying constraint functions revealed after each decision; the Neely-Yu abstract says the goal for time-varying constraints "is generally impossible". Attributing the impossibility result specifically to this paper rests on that reading and on general knowledge; I did not read the paper itself.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Explains why constrained-OCO guarantees need i.i.d./Slater-type structure.

### yu2017online
H. Yu, M. J. Neely, X. Wei, "Online Convex Optimization with Stochastic Constraints", Advances in Neural Information Processing Systems 30, 2017.
- Identifier: arXiv 1708.03741; proceedings.neurips.cc/paper_files/paper/2017/hash/da0d1111d2dc5d489242e60ebcbaf988-Abstract.html (meta: NeurIPS vol. 30, 2017, authors Yu, Neely, Wei). Confirmed: both fetched.
- Read scope: full_text of arXiv v1: abstract, introduction, problem setup, Assumption 2, Theorems 1-2 statements.
- Summary: Constraints g_k(x; omega(t)) are i.i.d. and revealed after the decision; a drift-plus-penalty algorithm (virtual queues Q_k) achieves O(sqrt T) expected regret and expected constraint violation, and O(sqrt T log T) with high probability. Assumes a stochastic Slater condition (exists eps>0 and x_hat with E[g_k(x_hat; omega)] <= -eps); explicitly allows individual realisations to be infeasible. Convex losses arbitrary; regret against best fixed x in the expected-feasible set. Real data-center scheduling experiments.
- F1 no, F2 no, F3 partial (long-term average constraints), F4 no, F5 no.
- Relevance: Cleanest "virtual queue on average constraint" guarantee; the guarantee is on time-averaged aggregate constraints, not per-agent.

### yu2019low
H. Yu, M. J. Neely, "A Low Complexity Algorithm with O(sqrt T) Regret and O(1) Constraint Violations for Online Convex Optimization with Long Term Constraints", Journal of Machine Learning Research 20 (2019), pp. 1-25 (submitted 10/16, revised 8/18, published 7/19).
- Identifier: arXiv 1604.02218 (v3, 18 May 2020). Confirmed: arXiv record and the JMLR header printed on the PDF ("Journal of Machine Learning Research 20 (2019) 1-25 ... Published 7/19", citing jmlr.org/papers/v20/16-494.html). The jmlr.org page itself returned 404 through the proxy, so the JMLR volume/page data come from the PDF header only.
- Read scope: full_text: abstract, introduction, Assumptions 1-4, Theorems 1-2 and surrounding discussion.
- Summary: Fixed (known-form) constraints g_k(x) <= 0 that may be violated per round but must hold long-term. With step parameters gamma = T^{1/4}-type scaling and a virtual-queue/penalty update, regret O(sqrt T) and constraint violation O(1), under bounded gradients (Assumption 1), bounded constraint values, bounded diameter, and a Slater point with margin epsilon (Assumption 4). Compares to Mahdavi et al. (O(T^{3/4})) and Jenatton et al.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Best-known fixed-constraint rate; contrast with our setting where the constraint set changes with the population.

### neely2017time
M. J. Neely, H. Yu, "Online Convex Optimization with Time-Varying Constraints", arXiv:1702.04783 (v2, 17 Feb 2017), technical report.
- Identifier: arXiv 1702.04783. Confirmed: arXiv listing and PDF. Preprint only; no journal version confirmed.
- Read scope: full_text: abstract, introduction, Assumption 1, Theorems 1 and 3 statements (located passages).
- Summary: Objective f_t and constraints g_{t,i} revealed after the decision. States up front that the general goal is impossible; gives an algorithm with O(1/eps^2) convergence time when all constraints are nonpositive over a common subset (deterministic Slater condition). If constraints are i.i.d., similar performance in expectation, and the Slater condition is replaced by a Lagrange-multiplier assumption; when both objective and constraints are i.i.d., within eps of the best causal policy that knows the distribution.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Shows what survives with time-varying constraints; the conditions (common feasible subset, or i.i.d.) are not met by an adversarial or churning population.

### chen2017online
T. Chen, Q. Ling, G. B. Giannakis, "An Online Convex Optimization Approach to Proactive Network Resource Allocation", IEEE Transactions on Signal Processing 65(24):6350-6364, 2017.
- Identifier: DOI 10.1109/tsp.2017.2750109. Confirmed: Crossref record.
- Read scope: metadata_only.
- Summary: Record confirms title and venue. Not read.
- F1 no, F2 no, F3 no, F4 no, F5 no (not assessed).
- Relevance: Named in brief; OCO for network resource allocation with predictions/proactive control.

### chen2019bandit
T. Chen, G. B. Giannakis, "Bandit Convex Optimization for Scalable and Dynamic IoT Management", IEEE Internet of Things Journal 6(1):1276-1286, 2019.
- Identifier: DOI 10.1109/jiot.2018.2839563; arXiv 1707.09060. Confirmed: Crossref record and arXiv record (journal_ref and DOI match).
- Read scope: abstract_only (arXiv).
- Summary: OCO with time-varying losses and time-varying constraints that may be violated instantaneously but hold in the long run, with only bandit (function-value) feedback; bandit online saddle-point schemes. Motivated by fog computing in IoT with changing user preferences and unpredictable resource availability.
- F1 partial (time-varying resource availability and preferences, not agent churn), F2 no, F3 partial, F4 no, F5 no.
- Relevance: Dynamic-regret style long-term constraint OCO in a network setting.

### cao2019online
X. Cao, K. J. R. Liu, "Online Convex Optimization With Time-Varying Constraints and Bandit Feedback", IEEE Transactions on Automatic Control 64(7):2665-2680, 2019. (ICC 2018 version: DOI 10.1109/icc.2018.8422559.)
- Identifier: DOI 10.1109/tac.2018.2884653. Confirmed: Crossref record.
- Read scope: metadata_only.
- Summary: Record confirms title and venue. Not read.
- F1 no, F2 no, F3 no, F4 no, F5 no (not assessed).
- Relevance: Named in brief for time-varying constraints with bandit feedback.

### yi2021regret
X. Yi, X. Li, T. Yang, L. Xie, T. Chai, K. Johansson, "Regret and Cumulative Constraint Violation Analysis for Online Convex Optimization with Long Term Constraints", Proceedings of ICML 2021, PMLR 139:11998-12008.
- Identifier: proceedings.mlr.press/v139/yi21b.html; arXiv 2106.05135. Confirmed: both fetched.
- Read scope: abstract_only (arXiv).
- Summary: Uses cumulative constraint violation (no compensation of violated by strictly feasible rounds). Static regret O(T^{max{c,1-c}}) and CCV O(T^{(1-c)/2}); both O(log T) for strongly convex losses.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Stricter violation metric (no netting), closer to hard SLA-style requirements.

### liu2021simultaneously
Q. Liu, W. Wu, L. Huang, Z. Fang, "Simultaneously Achieving Sublinear Regret and Constraint Violations for Online Convex Optimization with Time-varying Constraints", Performance Evaluation 152:102240, 2021 (also Performance 2021).
- Identifier: DOI 10.1016/j.peva.2021.102240; arXiv 2111.07707. Confirmed: Crossref search record and arXiv record.
- Read scope: abstract_only (arXiv abstract and first page).
- Summary: Virtual-queue algorithm for OCO with long-term, time-varying constraints; analysed w.r.t. dynamic regret and constraint violation; claimed first parameter-free algorithm with simultaneously sublinear dynamic regret and violation; no Slater condition required; O(1) violation if consecutive constraints vary smoothly; unknown-horizon extension. Keywords include online network resource allocation.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Closest constrained-OCO result to non-stationary allocation (dynamic regret, no Slater).

### guo2022online
H. Guo, X. Liu, H. Wei, L. Ying, "Online Convex Optimization with Hard Constraints: Towards the Best of Two Worlds and Beyond", Advances in Neural Information Processing Systems 35, 2022, pp. 36426-36439.
- Identifier: DOI 10.52202/068431-2639. Confirmed: Crossref record. (An arXiv search by title did not return it.)
- Read scope: metadata_only.
- Summary: Record confirms existence. Content not read.
- F1 no, F2 no, F3 partial (hard constraints, by title), F4 no, F5 no.
- Relevance: Hard (per-round) constraints variant of constrained OCO.

### sinha2024optimal
A. Sinha, R. Vaze, "Optimal Algorithms for Online Convex Optimization with Adversarial Constraints", Advances in Neural Information Processing Systems 37, 2024, pp. 41274-41302.
- Identifier: arXiv 2310.18955; DOI 10.52202/079017-1306. Confirmed: arXiv record and Crossref record.
- Read scope: abstract_only (arXiv).
- Summary: Constrained OCO against an adaptive adversary choosing both cost and constraint; answers an open question by giving a first-order policy with O(sqrt T) regret and O~(sqrt T) cumulative constraint violation without restrictive assumptions (no Slater).
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Removes the i.i.d./Slater assumptions that limit drift-plus-penalty guarantees.

### kim2023zero
Y. Kim, D. Lee, "Online Convex Optimization with Stochastic Constraints: Zero Constraint Violation and Bandit Feedback", arXiv:2301.11267 (v2).
- Identifier: arXiv 2301.11267. Confirmed: arXiv record. Preprint; published version not checked.
- Read scope: abstract_only.
- Summary: Variant of drift-plus-penalty with O(sqrt T) expected regret and zero constraint violation after a fixed number of iterations, oblivious to T, through a new drift lemma giving time-varying bounds on virtual queue length; extends to two-point bandit feedback.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Shows virtual queues can be tuned to give zero (not just sublinear) violation, relevant to SLA constraints.

### balseiro2023best
S. R. Balseiro, H. Lu, V. Mirrokni, "The Best of Many Worlds: Dual Mirror Descent for Online Allocation Problems", Operations Research 71(1):101-119, 2023.
- Identifier: DOI 10.1287/opre.2021.2242; arXiv 2011.10124. Confirmed: Crossref record and arXiv search record.
- Read scope: abstract_only (Crossref abstract: data-driven algorithms for network revenue management and advertising; text truncated in record).
- Summary: Dual mirror descent for online allocation with resource constraints, robust to i.i.d. and adversarial inputs per the Crossref blurb. Rates not read.
- F1 partial (requests arrive online), F2 no, F3 partial (budget/resource constraints), F4 no, F5 no.
- Relevance: Base algorithm that the regularized variant below extends.

### balseiro2025regularized
S. R. Balseiro, H. Lu, V. Mirrokni, "Regularized Online Allocation Problems: Fairness and Beyond", Manufacturing & Service Operations Management 27(3):720-735, 2025. (Preprint: arXiv 2007.00514 v4, 5 Nov 2021.)
- Identifier: DOI 10.1287/msom.2022.0212; arXiv 2007.00514. Confirmed: Crossref record and arXiv PDF.
- Read scope: full_text: abstract, introduction, model and Assumptions 1-2, Theorem 1 statement and comments, competitive-ratio discussion (located passages).
- Summary: Adds a non-separable concave regularizer r on total resource consumption to online allocation with resource constraints (examples include fairness and load balancing). Dual mirror descent: with step size eta ~ T^{-1/2} the regret is O(sqrt T) for stochastic i.i.d. requests (Theorem 1: Regret <= C1 + C2 eta T + C3/eta, constants depending on bounds f_bar, b_bar, regularizer), and a fixed regularizer-dependent competitive ratio for adversarial input. No convexity of reward/consumption needed. A void action (x=0) is assumed available. Regret lower bound cited from Arlotto-Gurvich.
- F1 partial (requests/agents arrive sequentially; resources deplete, no departures), F2 partial (arbitrary reward/consumption functions), F3 partial (resource budgets), F4 yes (regularizer-based fairness across agents), F5 no.
- Relevance: Most directly reusable online fairness-regularised allocation guarantee; fairness is aggregate (regularizer on totals), not a per-agent finite-lifetime guarantee.

### badanidiyuru2018bandits
A. Badanidiyuru, R. Kleinberg, A. Slivkins, "Bandits with Knapsacks", Journal of the ACM 65(3), 2018, pp. 1-55. (FOCS 2013 version: DOI 10.1109/focs.2013.30, pp. 207-216.)
- Identifier: DOI 10.1145/3164539; arXiv 1305.2545. Confirmed: Crossref record (abstract present) and arXiv record.
- Read scope: abstract_only.
- Summary: Introduces bandits with knapsacks: bandit learning with supply/budget limits in addition to time horizon; optimal policy may beat the best fixed arm, so sublinear regret is harder; two algorithms near the information-theoretic optimum (abstract).
- F1 no, F2 no, F3 partial (budget constraints), F4 no, F5 no.
- Relevance: Template for learning under consumable budgets (revenue/SLA budgets).

### immorlica2022adversarial
N. Immorlica, K. A. Sankararaman, R. Schapire, A. Slivkins, "Adversarial Bandits with Knapsacks", Journal of the ACM 69(6), 2022, pp. 1-47. (FOCS 2019: DOI 10.1109/focs.2019.00022, pp. 202-219.)
- Identifier: DOI 10.1145/3557045; arXiv 1811.11881. Confirmed: Crossref record (abstract present) and arXiv record.
- Read scope: abstract_only.
- Summary: BwK with adversarial outcomes; regret minimisation is infeasible, so the goal is competitive ratio: O(log T) relative to the best fixed distribution over actions, with a matching lower bound.
- F1 no, F2 no, F3 partial, F4 no, F5 no.
- Relevance: Shows the price of dropping stochastic assumptions under budget constraints.

### talebi2018learning
M. S. Talebi, A. Proutiere, "Learning Proportionally Fair Allocations with Low Regret", Proceedings of the ACM on Measurement and Analysis of Computing Systems 2(2), 2018, pp. 1-31.
- Identifier: DOI 10.1145/3224431. Confirmed: Crossref record with abstract (a 3-page SIGMETRICS abstract version also exists: DOI 10.1145/3219617.3219638).
- Read scope: abstract_only (Crossref abstract, partial).
- Summary: Sequential allocation of servers to tasks of many jobs with unknown success probabilities theta_ij, formulated as a bandit problem; the aim is rapid convergence to the proportionally fair allocation (or similar fairness-efficiency trade-offs) with low regret; a restricted-PF allocation is analysed and a learning algorithm ES-RPF is proposed (abstract; regret rates not read).
- F1 no, F2 no, F3 no, F4 yes (proportional fairness), F5 no.
- Relevance: Learning an unknown-utility proportional-fair allocation with regret guarantees.

### benade2024fair
G. Benade, A. M. Kazachkov, A. D. Procaccia, A. Psomas, D. Zeng, "Fair and Efficient Online Allocations", Operations Research 72(4):1438-1452, 2024. (EC 2018 version: "How to Make Envy Vanish Over Time", DOI 10.1145/3219166.3219179, pp. 593-610.)
- Identifier: DOI 10.1287/opre.2022.0332. Confirmed: Crossref record (abstract/summary blurb present).
- Read scope: abstract_only (journal's summary blurb).
- Summary: Fairness-efficiency trade-offs in online allocation of unpredictable, perishable donations; against adversarial arrivals no algorithm gets non-trivial guarantees on both; with distributional values, a simultaneously fair and efficient algorithm exists (per the blurb).
- F1 partial (online arrivals of items), F2 no, F3 no, F4 yes (envy-based), F5 no.
- Relevance: Online envy-freeness benchmark; adversarial impossibility.

### banerjee2022online
S. Banerjee, V. Gkatzelis, A. Gorokh, B. Jin, "Online Nash Social Welfare Maximization with Predictions", Proceedings of ACM-SIAM SODA 2022, pp. 1-19.
- Identifier: DOI 10.1137/1.9781611977073.1; arXiv 2008.03564. Confirmed: Crossref record and arXiv record.
- Read scope: abstract_only (arXiv).
- Summary: Online allocation of divisible goods to N agents maximising Nash social welfare with adversarial values; no algorithm beats the trivial O(N) competitive ratio without extra information; with predictions of each agent's monopolist utility an improved competitive ratio is obtained (ratio not read).
- F1 partial, F2 no, F3 no, F4 yes (NSW), F5 no.
- Relevance: Online proportional-fairness objective under adversarial arrivals.

### gkatzelis2021fair
V. Gkatzelis, A. Psomas, X. Tan, "Fair and Efficient Online Allocations with Normalized Valuations", Proceedings of the AAAI Conference on Artificial Intelligence 35(6):5440-5447, 2021.
- Identifier: DOI 10.1609/aaai.v35i6.16685; arXiv 2009.12405. Confirmed: Crossref and arXiv records.
- Read scope: abstract_only.
- Summary: Divisible resources allocated irrevocably each round; with normalised values, for two agents the outcome is envy-free while guaranteeing 91.6% of optimal social welfare, with a 93.3% upper bound on any envy-free algorithm.
- F1 partial, F2 no, F3 no, F4 yes (envy-freeness), F5 no.
- Relevance: Quantifies envy-free vs efficiency in online allocation (two agents only).

### gao2021online
Y. Gao, C. Kroer, A. Peysakhovich, "Online Market Equilibrium with Application to Fair Division", arXiv:2103.12936 (v2).
- Identifier: arXiv 2103.12936. Confirmed: arXiv record. Venue (believed NeurIPS 2021) was not confirmed from a primary record, so it is cited as a preprint.
- Read scope: abstract_only.
- Summary: Online Fisher market: items arrive sequentially and must be allocated and priced irrevocably; defines online market equilibrium; PACE allocation-and-pricing dynamics converge to an online market equilibrium for i.i.d. items from an unknown distribution (per the abstract).
- F1 partial (items arrive; buyer set fixed), F2 no, F3 no, F4 yes (competitive-equilibrium fairness), F5 partial (prices/market view; no incentive claims read).
- Relevance: PACE is the online fair-allocation algorithm extended below to nonstationary inputs.

### liao2022nonstationary
L. Liao, Y. Gao, C. Kroer, "Nonstationary Dual Averaging and Online Fair Allocation", Advances in Neural Information Processing Systems 35, 2022, pp. 37159-37172.
- Identifier: arXiv 2202.11614; DOI 10.52202/068431-2693. Confirmed: arXiv record and Crossref record.
- Read scope: abstract_only plus theorem headings (Theorems 1-3 identified; statements not read in detail).
- Summary: Studies PACE for online fair allocation under non-i.i.d. inputs: adversarially corrupted stochastic, ergodic, and block-independent (including periodic) arrivals; convergence up to errors caused by nonstationarity, recovering classical i.i.d. bounds; "best of many worlds" guarantees.
- F1 partial (nonstationary item arrivals; fixed agent set), F2 no, F3 no, F4 yes, F5 no.
- Relevance: Robustness of online fair allocation to nonstationarity.

### procaccia2024honor
A. D. Procaccia, B. Schiffer, S. Zhang, "Honor Among Bandits: No-Regret Learning for Online Fair Division", Advances in Neural Information Processing Systems 37, 2024, pp. 13183-13227.
- Identifier: arXiv 2407.01795; DOI 10.52202/079017-0420. Confirmed: arXiv and Crossref records.
- Read scope: abstract_only.
- Summary: Online fair division of indivisible goods with unknown mean values reduced to a stochastic bandit variant; maximises welfare while fair in expectation (envy-freeness or proportionality in expectation); explore-then-commit with O~(T^{2/3}) regret while maintaining the fairness constraint (abstract).
- F1 partial, F2 no, F3 no, F4 yes, F5 no (values learned; truthfulness not claimed in the abstract).
- Relevance: Learning unknown values under envy/proportionality constraints with regret rates.

### sinclair2021sequential
S. R. Sinclair, G. Jain, S. Banerjee, C. L. Yu, "Sequential Fair Allocation: Achieving the Optimal Envy-Efficiency Tradeoff Curve", arXiv:2105.05308 (v3, 29 Sep 2022). A related three-page SIGMETRICS 2022 abstract exists (DOI 10.1145/3489048.3526951; its Crossref author list differs, so it is not treated as this paper).
- Identifier: arXiv 2105.05308. Confirmed: arXiv record and PDF. Full-paper venue not confirmed.
- Read scope: full_text (partial): abstract, contents, introduction, informal Theorem 1, related work, model section (3.1).
- Summary: T rounds; a random number of individuals of known types arrives each round (distribution F known, need not be i.i.d.); resources are divisible; individuals arrive and depart in the same step, and allocations cannot be revisited. Shows an envy-efficiency uncertainty principle: counterfactual envy at least ~1/sqrt T (up to logs), and any algorithm with additive counterfactual envy LT has efficiency loss at least ~min{sqrt T, 1/LT}. Guarded-Hope, an adaptive-threshold algorithm, attains Envy <= LT with Delta-efficiency ~ min{sqrt T, 1/LT} with probability 1-delta, for multiple resources and types.
- F1 partial (stochastic per-round arrivals, but each agent is served only in its arrival round, so no multi-round sojourn), F2 partial (types with linear utilities), F3 no, F4 yes (individual envy-freeness guarantee), F5 no.
- Relevance: A per-individual fairness (envy) guarantee under random arrivals, but for one-shot agents; the tradeoff curve is a template for what to expect in our setting.

### li2020combinatorial
F. Li, J. Liu, B. Ji, "Combinatorial Sleeping Bandits with Fairness Constraints", IEEE Transactions on Network Science and Engineering 7(3):1799-1813, 2020. (INFOCOM 2019: DOI 10.1109/infocom.2019.8737461, pp. 1702-1710.)
- Identifier: DOI 10.1109/tnse.2019.2954310; arXiv 1901.04891. Confirmed: Crossref record and arXiv record (authors Fengjiao Li, Jia Liu, Bo Ji).
- Read scope: abstract_only plus located passages (model assumptions, Theorem 2 statement location).
- Summary: CSMAB-F: several arms can be played per round, arms can be unavailable ("sleeping"), and each arm has a minimum selection fraction. The LFG algorithm combines UCB with virtual queues for the fairness constraints; the paper proves it is feasibility-optimal and gives a time-average regret bound with a tunable parameter eta (a term of order sqrt(log T / T) per the abstract). Arm availability is i.i.d. over time with an unknown distribution; mean rewards unknown.
- F1 partial (stochastic availability of arms, not arrivals/departures), F2 no, F3 partial (minimum-fraction guarantees act like per-arm SLAs), F4 yes (per-arm minimum selection fraction via virtual queues), F5 no.
- Relevance: Shows virtual queues enforcing per-arm (per-agent) guarantees with learning; closest drift-plus-penalty-style per-agent fairness with a varying available set.

### patil2020achieving
V. Patil, G. Ghalme, V. Nair, Y. Narahari, "Achieving Fairness in the Stochastic Multi-Armed Bandit Problem", Proceedings of the AAAI Conference on Artificial Intelligence 34(4):5379-5386, 2020.
- Identifier: DOI 10.1609/aaai.v34i04.5986; arXiv 1907.10516. Confirmed: Crossref and arXiv records.
- Read scope: abstract_only.
- Summary: Fair-SMAB: each arm must be pulled at least a given fraction of rounds; defines fairness-aware r-Regret; a class of algorithms parameterised by unfairness tolerance and a black-box learner gives a uniform-in-time fairness guarantee, and with UCB1 a regret bound (rate truncated in the record I read).
- F1 no, F2 no, F3 partial, F4 yes (minimum pull fractions), F5 no.
- Relevance: Per-arm guarantees that hold uniformly over time rather than only asymptotically.

### kleinberg2010regret
R. Kleinberg, A. Niculescu-Mizil, Y. Sharma, "Regret Bounds for Sleeping Experts and Bandits", Machine Learning 80(2-3):245-272, 2010.
- Identifier: DOI 10.1007/s10994-010-5178-7. Confirmed: Crossref record.
- Read scope: metadata_only.
- Summary: Record confirms title and venue. The paper concerns experts/actions that are available only in some rounds; not read.
- F1 partial (time-varying availability, by title), F2 no, F3 no, F4 no, F5 no.
- Relevance: Foundation for time-varying action sets, the nearest online-learning model for a changing set.

### kash2014agent
I. Kash, A. D. Procaccia, N. Shah, "No Agent Left Behind: Dynamic Fair Division of Multiple Resources", Journal of Artificial Intelligence Research 51:579-603, 2014. (AAMAS 2013: DOI 10.65109/mblc7804, pp. 351-358.)
- Identifier: DOI 10.1613/jair.4405. Confirmed: Crossref record (abstract present).
- Read scope: abstract_only.
- Summary: Notes that agents are not all present simultaneously; develops a dynamic fair-division model with axiomatic properties for dynamic allocation mechanisms, and two novel mechanisms satisfying some of them, evaluated on real data.
- F1 yes (agents arrive over time, per abstract), F2 partial (multiple resources), F3 no, F4 yes, F5 not stated in the abstract.
- Relevance: Closest fair-division work with a dynamic agent population; likely overlaps with another strand.

### yin2022online
S. Yin, S. Agrawal, A. Zeevi, "Online Allocation and Learning in the Presence of Strategic Agents", Advances in Neural Information Processing Systems 35, 2022, pp. 6333-6344.
- Identifier: arXiv 2209.12112 (v1); DOI 10.52202/068431-0458. Confirmed: arXiv PDF and Crossref record.
- Read scope: full_text (partial): abstract, introduction, problem definitions, Theorems 1-2 statements.
- Summary: T items arrive sequentially for n homogeneous agents; each agent must receive a pre-specified fraction of items; agents' values are i.i.d. with unknown distribution; no payments. Mechanism is (O(sqrt(nT log(nT/delta))), delta)-approximate Bayesian incentive compatible (Theorem 1), and when agents are truthful, with probability 1-delta every agent's individual regret is O(sqrt(nT log(nT/delta))) (Theorem 2). A detection step stops the game if deviation is suspected.
- F1 no (fixed set of n agents), F2 no (homogeneous agents), F3 partial (fraction quotas), F4 partial (guaranteed fractions per agent), F5 yes (approximate BIC without money).
- Relevance: Per-agent (individual) regret plus incentive guarantee for online allocation with learning, but with a fixed population and i.i.d. values.

### dai2025efficiency
Y. Dai, N. Golrezaei, P. Jaillet, "Efficiency, Feasibility, and Incentive-Awareness in Constrained Online Resource Allocation", arXiv:2507.09473 (v2, 15 Jul 2026). A preliminary version is noted in the paper as accepted at NeurIPS 2025 (not confirmed from a proceedings record).
- Identifier: arXiv 2507.09473. Confirmed: arXiv record and PDF.
- Read scope: full_text (partial): abstract, introduction, related-work paragraph on strategic agents, model Section 2.1, Theorem 1 statement.
- Summary: Dynamic allocation of indivisible resources to strategic agents under long-term constraints; values and consumptions are i.i.d. from unknown distributions, values private; planner sees reports and consumption vectors. Shows vanilla primal-dual is manipulable via the dual variables. Incentive-Aware Primal-Dual (IAPD): VCG-based dual-adjusted payments (non-redistributable, "money-burning"), epoch-based lazy dual updates, random exploration, and an optimistic dual learner O-FTRL-FP. Result: O~(sqrt T) social-welfare regret, all long-term constraints satisfied, near-truthful perfect Bayesian equilibrium (Theorem 1: with high probability only O~(1) large-misreport rounds per agent per epoch). Notes this nearly matches the non-strategic Omega(sqrt T) lower bound.
- F1 no (fixed set of K agents), F2 partial (multi-dimensional consumption), F3 yes (multiple long-term resource constraints), F4 partial (general long-term constraints can encode fairness-type ones; fairness not the focus), F5 yes.
- Relevance: Closest found work combining a primal-dual/virtual-queue-like dual state, long-term constraints, and strategic misreporting; shows manipulation of the dual state is the central difficulty.

### lei2016mode
L. Lei, Q. Hao, Z. Zhong, "Mode Selection and Resource Allocation in Device-to-Device Communications With User Arrivals and Departures", IEEE Access 4:5209-5222, 2016.
- Identifier: DOI 10.1109/access.2016.2577020. Confirmed: Crossref record.
- Read scope: metadata_only.
- Summary: Record confirms title and venue; by title it treats resource allocation with user arrivals and departures in D2D networks. Method and guarantees not read.
- F1 yes (by title), F2 no, F3 no, F4 no, F5 no.
- Relevance: Example of a communications paper with explicit churn; checking whether it offers per-user finite-sojourn guarantees would require reading it.

### casasnovas2026learning
M. Casasnovas, F. Wilhelmi, R. Combes, M. Wojnar, K. Kosek-Szott, S. Szott, A. Jonsson, L. Esteve-Elfau, B. Bellalta, "Learning-Based Channel Access in Wi-Fi: A Multi-Armed Bandit Approach", IEEE Access 14:125904-125922, 2026.
- Identifier: DOI 10.1109/access.2026.3721756. Confirmed: Crossref record (authors, volume, pages).
- Read scope: metadata_only.
- Summary: Record confirms title and venue. It is about channel access (MAC-layer), not bandwidth allocation among devices; content not read.
- F1 no, F2 no, F3 no, F4 no, F5 no (not assessed).
- Relevance: Single recent Wi-Fi bandit reference found; brief pointer only. No home-network bandwidth-allocation RL paper with QoS classes was verified in this strand.

## 3. BibTeX (verified entries only; keys match headings)

```bibtex
@book{neely2010stochastic,
  author = {Neely, Michael J.},
  title = {Stochastic Network Optimization with Application to Communication and Queueing Systems},
  series = {Synthesis Lectures on Learning, Networks, and Algorithms},
  year = {2010},
  doi = {10.1007/978-3-031-79995-2}
}
@article{georgiadis2006resource,
  author = {Georgiadis, Leonidas and Neely, Michael J. and Tassiulas, Leandros},
  title = {Resource Allocation and Cross-Layer Control in Wireless Networks},
  journal = {Foundations and Trends in Networking},
  volume = {1}, number = {1}, pages = {1--144}, year = {2006},
  doi = {10.1561/1300000001}
}
@article{neely2008fairness,
  author = {Neely, Michael J. and Modiano, Eytan and Li, Chih-Ping},
  title = {Fairness and Optimal Stochastic Control for Heterogeneous Networks},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {16}, number = {2}, pages = {396--409}, year = {2008},
  doi = {10.1109/TNET.2007.900405}
}
@article{stolyar2005asymptotic,
  author = {Stolyar, Alexander L.},
  title = {On the Asymptotic Optimality of the Gradient Scheduling Algorithm for Multiuser Throughput Allocation},
  journal = {Operations Research},
  volume = {53}, number = {1}, pages = {12--25}, year = {2005},
  doi = {10.1287/opre.1040.0156}
}
@article{stolyar2005maximizing,
  author = {Stolyar, Alexander L.},
  title = {Maximizing Queueing Network Utility subject to Stability: Greedy Primal-Dual Algorithm},
  journal = {Queueing Systems},
  volume = {50}, number = {4}, pages = {401--457}, year = {2005},
  doi = {10.1007/s11134-005-1450-0}
}
@article{eryilmaz2007fair,
  author = {Eryilmaz, Atilla and Srikant, R.},
  title = {Fair Resource Allocation in Wireless Networks Using Queue-Length-Based Scheduling and Congestion Control},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {15}, number = {6}, pages = {1333--1344}, year = {2007},
  doi = {10.1109/TNET.2007.897944}
}
@article{huang2011delay,
  author = {Huang, Longbo and Neely, Michael J.},
  title = {Delay Reduction via {Lagrange} Multipliers in Stochastic Network Optimization},
  journal = {IEEE Transactions on Automatic Control},
  volume = {56}, number = {4}, pages = {842--857}, year = {2011},
  doi = {10.1109/TAC.2010.2067371}
}
@inproceedings{neely2011worstcase,
  author = {Neely, Michael J.},
  title = {Opportunistic Scheduling with Worst Case Delay Guarantees in Single and Multi-Hop Networks},
  booktitle = {Proceedings IEEE INFOCOM},
  pages = {1728--1736}, year = {2011},
  doi = {10.1109/INFCOM.2011.5934971}
}
@article{neely2013delaybased,
  author = {Neely, Michael J.},
  title = {Delay-Based Network Utility Maximization},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {21}, number = {1}, pages = {41--54}, year = {2013},
  doi = {10.1109/TNET.2012.2191157}
}
@inproceedings{hou2009theory,
  author = {Hou, I-Hong and Borkar, V. and Kumar, P. R.},
  title = {A Theory of {QoS} for Wireless},
  booktitle = {IEEE INFOCOM},
  pages = {486--494}, year = {2009},
  doi = {10.1109/INFCOM.2009.5061954}
}
@article{mahdavi2012trading,
  author = {Mahdavi, Mehrdad and Jin, Rong and Yang, Tianbao},
  title = {Trading Regret for Efficiency: Online Convex Optimization with Long Term Constraints},
  journal = {Journal of Machine Learning Research},
  volume = {13}, number = {81}, pages = {2503--2528}, year = {2012},
  eprint = {1111.6082}, archiveprefix = {arXiv}
}
@inproceedings{jenatton2016adaptive,
  author = {Jenatton, Rodolphe and Huang, Jim and Archambeau, C{\'e}dric},
  title = {Adaptive Algorithms for Online Convex Optimization with Long-term Constraints},
  booktitle = {Proceedings of the 33rd International Conference on Machine Learning},
  series = {PMLR}, volume = {48}, pages = {402--411}, year = {2016},
  eprint = {1512.07422}, archiveprefix = {arXiv}
}
@article{mannor2009online,
  author = {Mannor, Shie and Tsitsiklis, John N. and Yu, Jia Yuan},
  title = {Online Learning with Sample Path Constraints},
  journal = {Journal of Machine Learning Research},
  volume = {10}, number = {20}, pages = {569--590}, year = {2009},
  url = {https://jmlr.org/papers/v10/mannor09a.html}
}
@inproceedings{yu2017online,
  author = {Yu, Hao and Neely, Michael J. and Wei, Xiaohan},
  title = {Online Convex Optimization with Stochastic Constraints},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {30}, year = {2017},
  eprint = {1708.03741}, archiveprefix = {arXiv}
}
@article{yu2019low,
  author = {Yu, Hao and Neely, Michael J.},
  title = {A Low Complexity Algorithm with {$O(\sqrt{T})$} Regret and {$O(1)$} Constraint Violations for Online Convex Optimization with Long Term Constraints},
  journal = {Journal of Machine Learning Research},
  volume = {20}, pages = {1--25}, year = {2019},
  eprint = {1604.02218}, archiveprefix = {arXiv}
}
@misc{neely2017time,
  author = {Neely, Michael J. and Yu, Hao},
  title = {Online Convex Optimization with Time-Varying Constraints},
  year = {2017},
  eprint = {1702.04783}, archiveprefix = {arXiv}
}
@article{chen2017online,
  author = {Chen, Tianyi and Ling, Qing and Giannakis, Georgios B.},
  title = {An Online Convex Optimization Approach to Proactive Network Resource Allocation},
  journal = {IEEE Transactions on Signal Processing},
  volume = {65}, number = {24}, pages = {6350--6364}, year = {2017},
  doi = {10.1109/TSP.2017.2750109}
}
@article{chen2019bandit,
  author = {Chen, Tianyi and Giannakis, Georgios B.},
  title = {Bandit Convex Optimization for Scalable and Dynamic {IoT} Management},
  journal = {IEEE Internet of Things Journal},
  volume = {6}, number = {1}, pages = {1276--1286}, year = {2019},
  doi = {10.1109/JIOT.2018.2839563}, eprint = {1707.09060}, archiveprefix = {arXiv}
}
@article{cao2019online,
  author = {Cao, Xuanyu and Liu, K. J. Ray},
  title = {Online Convex Optimization With Time-Varying Constraints and Bandit Feedback},
  journal = {IEEE Transactions on Automatic Control},
  volume = {64}, number = {7}, pages = {2665--2680}, year = {2019},
  doi = {10.1109/TAC.2018.2884653}
}
@inproceedings{yi2021regret,
  author = {Yi, Xinlei and Li, Xiuxian and Yang, Tao and Xie, Lihua and Chai, Tianyou and Johansson, Karl},
  title = {Regret and Cumulative Constraint Violation Analysis for Online Convex Optimization with Long Term Constraints},
  booktitle = {Proceedings of the 38th International Conference on Machine Learning},
  series = {PMLR}, volume = {139}, pages = {11998--12008}, year = {2021},
  eprint = {2106.05135}, archiveprefix = {arXiv}
}
@article{liu2021simultaneously,
  author = {Liu, Qingsong and Wu, Wenfei and Huang, Longbo and Fang, Zhixuan},
  title = {Simultaneously Achieving Sublinear Regret and Constraint Violations for Online Convex Optimization with Time-varying Constraints},
  journal = {Performance Evaluation},
  volume = {152}, pages = {102240}, year = {2021},
  doi = {10.1016/j.peva.2021.102240}, eprint = {2111.07707}, archiveprefix = {arXiv}
}
@inproceedings{guo2022online,
  author = {Guo, Hengquan and Liu, Xin and Wei, Honghao and Ying, Lei},
  title = {Online Convex Optimization with Hard Constraints: Towards the Best of Two Worlds and Beyond},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {35}, pages = {36426--36439}, year = {2022},
  doi = {10.52202/068431-2639}
}
@inproceedings{sinha2024optimal,
  author = {Sinha, Abhishek and Vaze, Rahul},
  title = {Optimal Algorithms for Online Convex Optimization with Adversarial Constraints},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {37}, pages = {41274--41302}, year = {2024},
  doi = {10.52202/079017-1306}, eprint = {2310.18955}, archiveprefix = {arXiv}
}
@misc{kim2023zero,
  author = {Kim, Yeongjong and Lee, Dabeen},
  title = {Online Convex Optimization with Stochastic Constraints: Zero Constraint Violation and Bandit Feedback},
  year = {2023},
  eprint = {2301.11267}, archiveprefix = {arXiv}
}
@article{balseiro2023best,
  author = {Balseiro, Santiago R. and Lu, Haihao and Mirrokni, Vahab},
  title = {The Best of Many Worlds: Dual Mirror Descent for Online Allocation Problems},
  journal = {Operations Research},
  volume = {71}, number = {1}, pages = {101--119}, year = {2023},
  doi = {10.1287/opre.2021.2242}, eprint = {2011.10124}, archiveprefix = {arXiv}
}
@article{balseiro2025regularized,
  author = {Balseiro, Santiago R. and Lu, Haihao and Mirrokni, Vahab},
  title = {Regularized Online Allocation Problems: Fairness and Beyond},
  journal = {Manufacturing \& Service Operations Management},
  volume = {27}, number = {3}, pages = {720--735}, year = {2025},
  doi = {10.1287/msom.2022.0212}, eprint = {2007.00514}, archiveprefix = {arXiv}
}
@article{badanidiyuru2018bandits,
  author = {Badanidiyuru, Ashwinkumar and Kleinberg, Robert and Slivkins, Aleksandrs},
  title = {Bandits with Knapsacks},
  journal = {Journal of the ACM},
  volume = {65}, number = {3}, pages = {1--55}, year = {2018},
  doi = {10.1145/3164539}, eprint = {1305.2545}, archiveprefix = {arXiv}
}
@article{immorlica2022adversarial,
  author = {Immorlica, Nicole and Sankararaman, Karthik Abinav and Schapire, Robert and Slivkins, Aleksandrs},
  title = {Adversarial Bandits with Knapsacks},
  journal = {Journal of the ACM},
  volume = {69}, number = {6}, pages = {1--47}, year = {2022},
  doi = {10.1145/3557045}, eprint = {1811.11881}, archiveprefix = {arXiv}
}
@article{talebi2018learning,
  author = {Talebi, Mohammad Sadegh and Proutiere, Alexandre},
  title = {Learning Proportionally Fair Allocations with Low Regret},
  journal = {Proceedings of the ACM on Measurement and Analysis of Computing Systems},
  volume = {2}, number = {2}, pages = {1--31}, year = {2018},
  doi = {10.1145/3224431}
}
@article{benade2024fair,
  author = {Benad{\`e}, Gerdus and Kazachkov, Aleksandr M. and Procaccia, Ariel D. and Psomas, Alexandros and Zeng, David},
  title = {Fair and Efficient Online Allocations},
  journal = {Operations Research},
  volume = {72}, number = {4}, pages = {1438--1452}, year = {2024},
  doi = {10.1287/opre.2022.0332}
}
@inproceedings{banerjee2022online,
  author = {Banerjee, Siddhartha and Gkatzelis, Vasilis and Gorokh, Artur and Jin, Billy},
  title = {Online {Nash} Social Welfare Maximization with Predictions},
  booktitle = {Proceedings of the 2022 Annual ACM-SIAM Symposium on Discrete Algorithms (SODA)},
  pages = {1--19}, year = {2022},
  doi = {10.1137/1.9781611977073.1}, eprint = {2008.03564}, archiveprefix = {arXiv}
}
@inproceedings{gkatzelis2021fair,
  author = {Gkatzelis, Vasilis and Psomas, Alexandros and Tan, Xizhi},
  title = {Fair and Efficient Online Allocations with Normalized Valuations},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume = {35}, number = {6}, pages = {5440--5447}, year = {2021},
  doi = {10.1609/aaai.v35i6.16685}, eprint = {2009.12405}, archiveprefix = {arXiv}
}
@misc{gao2021online,
  author = {Gao, Yuan and Kroer, Christian and Peysakhovich, Alex},
  title = {Online Market Equilibrium with Application to Fair Division},
  year = {2021},
  eprint = {2103.12936}, archiveprefix = {arXiv}
}
@inproceedings{liao2022nonstationary,
  author = {Liao, Luofeng and Gao, Yuan and Kroer, Christian},
  title = {Nonstationary Dual Averaging and Online Fair Allocation},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {35}, pages = {37159--37172}, year = {2022},
  doi = {10.52202/068431-2693}, eprint = {2202.11614}, archiveprefix = {arXiv}
}
@inproceedings{procaccia2024honor,
  author = {Procaccia, Ariel D. and Schiffer, Benjamin and Zhang, Shirley},
  title = {Honor Among Bandits: No-Regret Learning for Online Fair Division},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {37}, pages = {13183--13227}, year = {2024},
  doi = {10.52202/079017-0420}, eprint = {2407.01795}, archiveprefix = {arXiv}
}
@misc{sinclair2021sequential,
  author = {Sinclair, Sean R. and Jain, Gauri and Banerjee, Siddhartha and Yu, Christina Lee},
  title = {Sequential Fair Allocation: Achieving the Optimal Envy-Efficiency Tradeoff Curve},
  year = {2021},
  eprint = {2105.05308}, archiveprefix = {arXiv}
}
@article{li2020combinatorial,
  author = {Li, Fengjiao and Liu, Jia and Ji, Bo},
  title = {Combinatorial Sleeping Bandits With Fairness Constraints},
  journal = {IEEE Transactions on Network Science and Engineering},
  volume = {7}, number = {3}, pages = {1799--1813}, year = {2020},
  doi = {10.1109/TNSE.2019.2954310}, eprint = {1901.04891}, archiveprefix = {arXiv}
}
@inproceedings{patil2020achieving,
  author = {Patil, Vishakha and Ghalme, Ganesh and Nair, Vineet and Narahari, Y.},
  title = {Achieving Fairness in the Stochastic Multi-Armed Bandit Problem},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume = {34}, number = {4}, pages = {5379--5386}, year = {2020},
  doi = {10.1609/aaai.v34i04.5986}, eprint = {1907.10516}, archiveprefix = {arXiv}
}
@article{kleinberg2010regret,
  author = {Kleinberg, Robert and Niculescu-Mizil, Alexandru and Sharma, Yogeshwer},
  title = {Regret Bounds for Sleeping Experts and Bandits},
  journal = {Machine Learning},
  volume = {80}, number = {2--3}, pages = {245--272}, year = {2010},
  doi = {10.1007/s10994-010-5178-7}
}
@article{kash2014agent,
  author = {Kash, Ian and Procaccia, Ariel D. and Shah, Nisarg},
  title = {No Agent Left Behind: Dynamic Fair Division of Multiple Resources},
  journal = {Journal of Artificial Intelligence Research},
  volume = {51}, pages = {579--603}, year = {2014},
  doi = {10.1613/jair.4405}
}
@inproceedings{yin2022online,
  author = {Yin, Steven and Agrawal, Shipra and Zeevi, Assaf},
  title = {Online Allocation and Learning in the Presence of Strategic Agents},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {35}, pages = {6333--6344}, year = {2022},
  doi = {10.52202/068431-0458}, eprint = {2209.12112}, archiveprefix = {arXiv}
}
@misc{dai2025efficiency,
  author = {Dai, Yan and Golrezaei, Negin and Jaillet, Patrick},
  title = {Efficiency, Feasibility, and Incentive-Awareness in Constrained Online Resource Allocation},
  year = {2025},
  note = {arXiv v2, July 2026},
  eprint = {2507.09473}, archiveprefix = {arXiv}
}
@article{lei2016mode,
  author = {Lei, Lei and Hao, Qingyun and Zhong, Zhangdui},
  title = {Mode Selection and Resource Allocation in Device-to-Device Communications With User Arrivals and Departures},
  journal = {IEEE Access},
  volume = {4}, pages = {5209--5222}, year = {2016},
  doi = {10.1109/ACCESS.2016.2577020}
}
@article{casasnovas2026learning,
  author = {Casasnovas, Miguel and Wilhelmi, Francesc and Combes, Richard and Wojnar, Maksymilian and Kosek-Szott, Katarzyna and Szott, Szymon and Jonsson, Anders and Esteve-Elfau, Luis and Bellalta, Boris},
  title = {Learning-Based Channel Access in {Wi-Fi}: A Multi-Armed Bandit Approach},
  journal = {IEEE Access},
  volume = {14}, pages = {125904--125922}, year = {2026},
  doi = {10.1109/ACCESS.2026.3721756}
}
```

Note on the Casasnovas entry: the author list was taken from the Crossref DOI record (nine authors); recheck it against the publisher page before submission.

## 4. Could not verify / could not retrieve

- Full text of Neely's monograph, Georgiadis-Neely-Tassiulas, Neely-Modiano-Li, Stolyar (both), Eryilmaz-Srikant, Huang-Neely, Hou-Borkar-Kumar, Cao-Liu, Chen-Ling-Giannakis, Guo et al., Neely worst-case delay and delay-based NUM, Kleinberg et al., Lei et al., Casasnovas et al.: only Crossref/record metadata retrieved (no open full text reached). Their entries are existence-confirmed only.
- JMLR page for Yu-Neely (jmlr.org/papers/v20/16-494.html) returned 404 through the proxy; JMLR volume and pages are taken from the header of the arXiv v3 PDF.
- DBLP: blocked by bot challenge; no DBLP records used.
- Venue of Gao-Kroer-Peysakhovich (believed NeurIPS 2021) and of the full Sinclair et al. paper (believed ACM POMACS / SIGMETRICS 2022) could not be confirmed from a primary record; cited as arXiv preprints.
- Stolyar's 2006 follow-up (Queueing Systems 54:203-220, DOI 10.1007/s11134-006-0067-2) was found in Crossref but left out of the list to limit scope.
- Not found: any peer-reviewed paper on RL or bandit bandwidth allocation among devices of different QoS classes on a home/Wi-Fi link (searched Crossref and arXiv with several phrasings). Only the Wi-Fi channel-access bandit item above was found.
- Not found: any Lyapunov or constrained-OCO paper with truthful/incentive-compatible mechanism design via virtual queues (see synthesis).
- Not found: a Lyapunov/OCO paper with explicit churn (arrival and departure of agents) and per-agent finite-sojourn guarantees; Lei et al. (2016) is the only churn-titled candidate and was not read.

## 5. Strand synthesis

Settled. With a fixed set of constraints, virtual-queue (drift-plus-penalty) methods give O(sqrt T) regret with O(sqrt T) violation (Yu-Neely-Wei, i.i.d. constraints plus a stochastic Slater condition) or O(1) violation (Yu-Neely 2019, known fixed constraints plus Slater); dynamic regret without Slater is available (Liu et al. 2021), and adversarial constraints can be handled at O(sqrt T) regret and O~(sqrt T) cumulative violation (Sinha-Vaze). Online allocation with a fairness regulariser has O(sqrt T) regret for i.i.d. input and constant competitive ratios for adversarial input (Balseiro et al.). Online envy-freeness against efficiency has a quantified trade-off (Sinclair et al., Benade et al., Gkatzelis et al.), and per-arm minimum-share guarantees are enforceable with virtual queues even when arms sleep (Li-Liu-Ji).

Open with respect to our features. F1: constrained OCO and drift-plus-penalty analyses fix the set of constraints or agents; churn appears only as stochastic availability (Li-Liu-Ji) or one-round agents (Sinclair et al.). Kash et al. is the dynamic-population exception but is a fair-division axiomatic model. F2: inelastic/real-time utilities appear in Hou-Borkar-Kumar and delay-based NUM, with fixed client sets. F3: SLA/revenue appear only as generic long-term constraints. F4: fairness is aggregate (regularisers on totals) or per-arm share, not per-agent over a finite stay. F5: only Yin et al. and Dai et al. combine strategic reporting with online learning, for fixed agent sets and i.i.d. values, and neither uses a plain virtual-queue mechanism.

Direct answers. Within this search I found no drift-plus-penalty or constrained-OCO work giving per-agent finite-sojourn guarantees under churn: virtual-queue guarantees are time-averaged over the horizon or per queue of a fixed set. The nearest deterministic per-item bounds are packet delay guarantees (Neely 2011), not agent lifetimes. I also found none that handle incentive or envy constraints through virtual queues. Dai et al. show the dual state itself is the manipulation channel, which suggests that incentive constraints in a drift-plus-penalty design need separate treatment.
