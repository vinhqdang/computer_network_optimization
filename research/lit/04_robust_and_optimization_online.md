# Strand 04: Robust / DRO / stochastic optimisation for networks, with an Optimization Online sweep

Date of search: 2026-11-17. Read-scope vocabulary: `abstract_only` (abstract/metadata on the primary record read), `metadata_only` (bibliographic record only; content NOT read). Summaries never go beyond the stated scope. For `metadata_only` items the F1-F5 column is marked "not assessed" or flagged "inferred from title".

## 1. Search log

Optimization Online (OO), fetched with curl, all dated 2026-11-17.
- Seed page https://optimization-online.org/2026/10/robust-network-enhancement-formulations-and-approximations/ fetched: confirmed (see section 2).
- Category listings (10 posts/page), pages 1-8 each: /category/network-optimization/ (p1 = 2026-11 back to p8 = 2021-10), /category/robust-optimization/ (p1-p8; p1 = 2026-11, p5 reaches 2026-02), /category/stochastic-programming/ (p1-p8), /category/applications-science-and-engineering/ (p1-p8). Several later pages came back with few or no entries in my parser, so coverage of the older tail of the category lists is incomplete. Listings are dominated by combinatorial network design, routing, generic DRO theory and power systems; almost nothing on communication-network allocation.
- Site search `?s=` queries run: bandwidth allocation; resource allocation fairness; telecommunication; network utility maximization; online allocation; fair allocation; congestion pricing; wireless; distributionally robust resource allocation; mechanism design; Stackelberg network; online convex optimization constraints; price of fairness; network slicing (0 hits); alpha-fairness (0 hits); capacity allocation uncertain demand; bandwidth; fairness; internet; TCP rate; quality of service; robust network design; hose model; Wasserstein; chance constrained; fair; online; incentive compatible; auction; price of robustness; multicommodity; satellite; 5G; stochastic network utility; Nash bargaining; proportional fairness; max-min fair.
- Every OO item below had its own page fetched (title, authors, date, abstract, PDF link read from the page). PDFs were not opened.

Published literature: Crossref API (`query.bibliographic`), arXiv export API (id_list), plus WebSearch for discovery of robust-NUM and slicing papers (search results were used only to find candidates; every record below was re-confirmed in Crossref or arXiv).

## 2. Optimization Online items (read scope: `abstract_only`, from the OO page)

### rezaei2026robust
Rezaei, Z. and Wei, N. "Robust Network Enhancement: Formulations and Approximations." Optimization Online, published 2026-10-26.
- Confirmed: OO page (https://optimization-online.org/2026/10/robust-network-enhancement-formulations-and-approximations/, short URL ?p=37651); PDF https://optimization-online.org/wp-content/uploads/2026/10/view-3.pdf. Categories: Integer Programming, Network Optimization, Robust Optimization.
- Read scope: abstract_only.
- Summary: Robust upgrade of network components when both utilities and upgrade costs are uncertain; max-min ("lower-bound") and max-max ("upper-bound") problems, cut-generation reformulation, a box approximation of the utility uncertainty set with performance guarantees, experiments on spanning-tree instances.
- F1 no; F2 no; F3 no (costs only); F4 no; F5 no.
- Relevance: low. It is graph-structure robust optimisation (interdiction/upgrade), not allocation of shared capacity; usable only as an example of a recent robust-network paper and as a source of box-uncertainty-approximation ideas.

### beck2026wardrop
Beck, Y., Giancola, F., Ljubic, I., Mattia, S. "Modeling Network Congestion under Demand Uncertainty Using Wardrop Principles." Optimization Online, 2026-03-14.
- Confirmed: OO page .../2026/03/modeling-network-congestion-under-demand-uncertainty-using-wardrop-principles/ (?p=34014); PDF .../wp-content/uploads/2026/03/congestion-w-wardrop.pdf.
- Read scope: abstract_only.
- Summary: Worst-case congestion over demand uncertainty sets (ellipsoidal, budgeted, hose polyhedron) in a bilevel model with user-equilibrium or system-optimum followers; single-level MINLP reformulations; tests on Sioux Falls and SNDlib.
- F1 no; F2 no (single congestion cost); F3 no; F4 no; F5 partial (selfish route choice as lower level, not misreporting).
- Relevance: medium. A 2026 example of hose/budgeted uncertainty with user behaviour modelled as a lower level; vehicle for citing the hose model in the current literature.

### bao2026risk
Bao, W., Vogiatzis, C., Kontou, E. "Risk-Averse Stochastic User Equilibrium on Uncertain Transportation Networks." Optimization Online, 2026-03-04 (updated 2026-03-06).
- Confirmed: OO page .../2026/03/risk-averse-stochastic-user-equilibrium-on-uncertain-transportation-networks/ (?p=33859); PDF on site.
- Read scope: abstract_only.
- Summary: Convex truncated stochastic user equilibrium with a mean-CVaR certainty equivalent; a stochastic-programming version and a DRO version over a 1-Wasserstein ambiguity set, solved via Benders on a second-order cone reformulation.
- F1 no; F2 partial (risk attitude in travellers' cost, not QoS classes); F3 no; F4 no; F5 no.
- Relevance: low-medium. Template for coupling a Wasserstein ambiguity set with an equilibrium/allocation model on a network with uncertain supply.

### makhau2026satellite
Mak-Hau, V. and Gaudry, A. "Non-contiguous satellite channel allocation under cumulative interference: A hybrid price-and-branch approach." Optimization Online, 2026-10-31.
- Confirmed: OO page .../2026/10/non-contiguous-satellite-channel-allocation-under-cumulative-interference-a-hybrid-price-and-branch-approach/ (?p=37411); categories include Telecommunications. PDF on site.
- Read scope: abstract_only.
- Summary: Carriers with heterogeneous sub-channel demands and priorities in a multi-beam satellite system, partially satisfiable demand with a priority-weighted objective, MIP and pattern formulations, price-and-branch; synthetic instances with perturbations of interference tolerances and carrier populations.
- F1 no (static); F2 partial (heterogeneous demands, priority classes); F3 partial (priority weights); F4 no; F5 no.
- Relevance: medium as an example of priority-weighted telecom allocation in a static, offline setting.

### sun2021drfram
Sun, L., Xie, W., Witten, T. "Distributionally Robust Fair Transit Resource Allocation During a Pandemic." Optimization Online, 2021-06-26 (updated 2022-04-07); published as Transportation Science 57(4):954-978, 2023, doi 10.1287/trsc.2022.1159 (Crossref).
- Confirmed: OO page https://optimization-online.org/2021/06/8466/ (?p=17197) and Crossref record.
- Read scope: abstract_only (OO).
- Summary: Wasserstein-ambiguity distributionally robust allocation model (DrFRAM) with a fairness objective, reformulated as an MILP with strengthened formulations, scenario decomposition and an approximation algorithm.
- F1 no; F2 no; F3 no; F4 yes; F5 no.
- Relevance: high for method: one of the few DRO + fairness allocation papers found; non-communication domain.

### sun2023fairuam
Sun, L. and Xie, W. (OO page author list; the page's citation line also names Deng and Wei). "Fair and Risk-averse Urban Air Mobility Resource Allocation Under Uncertainties." Optimization Online, 2023-01-31 (updated 2024-09-30).
- Confirmed: OO page .../2023/01/fair-and-risk-averse-urban-air-mobility-resource-allocation-under-uncertainties/ (?p=21821). Author list differs between page header and citation line: check the PDF before citing.
- Read scope: abstract_only (truncated on my fetch).
- Summary: Two-stage model: first-stage resource allocation, second-stage fair and efficient assignment of delays after random capacity and demand realise; NP-hard; valid inequalities.
- F1 no; F2 no; F3 no; F4 yes; F5 no.
- Relevance: medium. Two-stage structure for fair allocation under uncertain capacity and demand.

### tang2023learning
Tang, B., Kocyigit, C., Rice, E., Vayanos, P. "Learning Optimal and Fair Policies for Online Allocation of Scarce Societal Resources from Data Collected in Deployment." Optimization Online, 2023-11-24 (updated 2025-06-19).
- Confirmed: OO page .../2023/11/learning-optimal-and-fair-policies-for-online-allocation-of-scarce-societal-resources-from-data-collected-in-deployment/ (?p=24815); PDF on site.
- Read scope: abstract_only.
- Summary: Online allocation of resources of several types to heterogeneous arrivals using dual prices of budget constraints, with asymptotic optimality and fairness constraints; reports a "price of fairness" on homelessness-housing data.
- F1 yes (online arrivals); F2 partial (heterogeneous covariates, not QoS); F3 partial (long-run budget constraints); F4 yes; F5 no.
- Relevance: medium-high: dual-price online policy plus fairness constraints is close in spirit to our online allocation, but resources are indivisible and non-network.

### chen2022simple
Chen, R., Gunluk, O., Lodi, A., Wang, G. "A Simple Algorithm for Online Decision Making." Optimization Online, 2022-11-07.
- Confirmed: OO page .../2022/11/a-simple-algorithm-for-online-decision-making/ (?p=20914); PDF on site.
- Read scope: abstract_only.
- Summary: Generalises online linear programming to online decision making with nonconvex local feasible sets and long-term goal constraints; Fenchel-dual algorithm, O(sqrt(mT)) constraint violation and O(sqrt(m log m) sqrt(T)) competitive difference under random permutation.
- F1 yes (sequential arrivals); F2 partial (general local sets); F3 partial (long-term goal constraints); F4 no; F5 no.
- Relevance: medium: online-with-constraints machinery; assumes random-order arrivals, no departures.

### sujanani2025public
Sujanani, A. "Asymptotically Fair and Truthful Allocation of Public Goods." Optimization Online, 2025-06-06.
- Confirmed: OO page .../2025/06/asymptotically-fair-and-truthful-allocation-of-public-goods/ (?p=30648); PDF on site.
- Read scope: abstract_only.
- Summary: Core (Nash-welfare) allocation of divisible items among agents with manipulable preferences; a differentially private algorithm (PPGA) attaining asymptotic truthfulness and asymptotic core with high probability; experiments on participatory budgeting.
- F1 no; F2 partial (agent-specific preferences); F3 no; F4 yes; F5 yes.
- Relevance: medium-high for the fairness + truthfulness combination via Nash welfare and privacy-based approximate IC; static and for public goods.

### lodi2021fairness
Lodi, A., Olivier, P., Pesant, G., Sankaranarayanan, S. "Fairness over Time in Dynamic Resource Allocation with an Application in Healthcare." Optimization Online, 2021-01-10.
- Confirmed: OO page .../2021/01/8203/ (?p=16904).
- Read scope: abstract_only.
- Summary: Repeated decisions by a central decision maker obliged to be fair across stakeholders; formulations for the maximum fairness attainable and for improving fairness over time; ambulance allocation case with column generation and CP.
- F1 partial (repeated rounds, fixed stakeholder set); F2 no; F3 no; F4 yes; F5 no.
- Relevance: medium for temporal fairness definitions.

### altin2005vpn
Altin, A., Amaldi, E., Belotti, P., Pinar, M. C. "Provisioning Virtual Private Networks under traffic uncertainty." Optimization Online, 2005-02-25 (DEI Politecnico di Milano Tech. Report 16, 2005).
- Confirmed: OO page https://optimization-online.org/2005/02/1072/ (?p=9702).
- Read scope: abstract_only.
- Summary: Capacity reservation for VPNs under the hose traffic model and a less conservative statistics-based robust variant, with compact MIP formulations.
- F1 no; F2 no; F3 partial (reservation cost); F4 no; F5 no.
- Relevance: medium: telecom hose-model robust provisioning (planning, not online).

### karasan2005dwdm
Karasan, O. E., Pinar, M. C., Yaman, H. "Robust DWDM Routing and Provisioning under Polyhedral Demand Uncertainty." Optimization Online, 2005-04-26 (updated 2006-08-28).
- Confirmed: OO page https://optimization-online.org/2005/04/1115/ (?p=9735).
- Read scope: abstract_only.
- Summary: MILP models robust to demands in a polyhedron (hose; restricted interval) for DWDM routing and provisioning at minimum cost, compared against Kennington et al.'s robustness model.
- F1-F5: no.
- Relevance: low-medium: same family as the hose literature.

### poss2013routing
Poss, M. "A comparison of routing sets for robust network design." Optimization Online, 2013-07-24 (Optimization Letters, to appear per OO page).
- Confirmed: OO page https://optimization-online.org/2013/07/3983/ (?p=12521). The page also lists a 2011 version (/2011/09/3145/). Final journal record not checked in Crossref: cite the OO version or verify before citing the journal.
- Read scope: abstract_only.
- Summary: Compares optimal capacity allocation costs under six routing sets (affine, volume, 2-cover and others) for designing a network that routes non-simultaneous demand vectors.
- F1-F5: no.
- Relevance: low-medium: background for robust capacity design with adjustable routing.

### boyd2007dynamic
Boyd, S., Trichakis, N., Zymnis, A. "Dynamic Network Utility Maximization with Delivery Contracts." Stanford EE report, Optimization Online 2007-09-30.
- Confirmed: OO page https://optimization-online.org/2007/09/1797/ (?p=10254).
- Read scope: abstract_only.
- Summary: Multi-period NUM with time-varying utilities, capacities and routing; "delivery contracts" coupling flow rates across time; dual decomposition when data are known and an MPC heuristic when they are not.
- F1 no (fixed flows, time-varying data); F2 partial (concave utilities per flow); F3 partial (delivery contracts act like SLA volume commitments); F4 partial (NUM utilities; not stated); F5 no.
- Relevance: medium-high: closest OO item to NUM with contract-like constraints and unknown future data.

### boyd2007interior
Boyd, S., O'Neill, D., Trichakis, N., Zymnis, A. "An Interior-Point Method for Large Scale Network Utility Maximization." Stanford report, Optimization Online 2007-09-30.
- Confirmed: OO page https://optimization-online.org/2007/09/1796/ (?p=10253).
- Read scope: abstract_only.
- Summary: Truncated-Newton primal-dual interior-point solver for large NUM with concave utilities, compared with dual decomposition, with an extension including delay.
- F1 no; F2 partial (concave utilities, delay extension); F3 no; F4 partial (NUM); F5 no.
- Relevance: low-medium: solver background for the static NUM baseline.

### bhardwaj2014bandwidth
Bhardwaj, A., Sinha, N., Vidyarthi, N. "The Multi-Hour Bandwidth Packing Problem with Queuing Delays: Bounds and Exact Solution Approach." Optimization Online, 2014-11-03.
- Confirmed: OO page https://optimization-online.org/2014/11/4624/ (?p=13130).
- Read scope: abstract_only.
- Summary: Selecting and routing messages with bandwidth demands over time-varying traffic to maximise revenue minus flow and delay cost; M/M/1 queue network, MINLP linearised to MIP, bounds and exact method.
- F1 partial (Poisson arrivals in model); F2 partial (delay cost); F3 yes (revenue/profit); F4 no; F5 no.
- Relevance: medium: revenue-driven bandwidth admission with delay.

### grothey2011topercentile
Grothey, A. and Yang, X. "Approximate Dynamic Programming with Bezier Curves/Surfaces for Top-percentile traffic routing." Optimization Online, 2011-01-05 (ERGO Technical Report 10-008).
- Confirmed: OO page https://optimization-online.org/2011/01/2877/ (?p=11404).
- Read scope: abstract_only.
- Summary: ISP multi-homing under top-percentile pricing; stochastic dynamic programming with approximate dynamic programming value functions.
- F1 partial (dynamic traffic); F2 no; F3 yes (provider charging rule); F4 no; F5 no.
- Relevance: medium: ISP-side commercial pricing under stochastic traffic.

## 3. Published and preprint literature

Read scope for every item in this section is `metadata_only` (Crossref record) unless stated otherwise. Because content was not read, "F" fields use "not assessed" and any note on scope is inferred from the title/venue and flagged.

### bertsimas2004price
Bertsimas, D. and Sim, M. "The Price of Robustness." Operations Research 52(1):35-53, 2004. doi 10.1287/opre.1030.0065. Confirmed: Crossref. Read scope: metadata_only. Summary: not read; the title names the budgeted ("Gamma") uncertainty set approach. F1-F5: not assessed. Relevance: standard citation for budgeted uncertainty used in network capacity/demand robustness.

### bertsimas2003robust
Bertsimas, D. and Sim, M. "Robust discrete optimization and network flows." Mathematical Programming 98(1-3):49-71, 2003. doi 10.1007/s10107-003-0396-4. Confirmed: Crossref. Read scope: metadata_only. F1-F5: not assessed. Relevance: robust network flows (companion to the above).

### atamturk2007two
Atamt\"urk, A. and Zhang, M. "Two-Stage Robust Network Flow and Design Under Demand Uncertainty." Operations Research 55(4):662-673, 2007. doi 10.1287/opre.1070.0428. Confirmed: Crossref. Read scope: metadata_only. F1-F5: not assessed. Relevance: two-stage robust network flow under demand uncertainty, the principal reference for the adjustable-robust network baseline.

### benameur2005routing
Ben-Ameur, W. and Kerivin, H. "Routing of Uncertain Traffic Demands." Optimization and Engineering 6(3):283-313, 2005. doi 10.1007/s11081-005-1741-7. Confirmed: Crossref. Read scope: metadata_only. F1-F5: not assessed. Relevance: robust network design under traffic uncertainty (dynamic routing, polyhedral demand), per title. Note: their CACM 2003 paper "New economical virtual private networks" appears in Crossref with a scrambled title ("Networks new economical virtual private"), doi 10.1145/777313.777314; not used.

### duffield1999hose
Duffield, N. G., Goyal, P., Greenberg, A., Mishra, P., Ramakrishnan, K. K., van der Merwe, J. E. "A flexible model for resource management in virtual private networks." Proc. ACM SIGCOMM 1999, pp. 95-108. doi 10.1145/316188.316209. Confirmed: Crossref (which spells the last author "van der Merive"; the later IEEE/ACM ToN record, doi 10.1109/TNET.2002.803918, gives "van der Merwe"). Read scope: metadata_only. Relevance: origin of the hose model, cited by name in the task brief.

### ordonez2007robust
Ord\'o\~nez, F. and Zhao, J. "Robust capacity expansion of network flows." Networks 50(2):136-145, 2007. doi 10.1002/net.20183. Confirmed: Crossref. Read scope: metadata_only. Relevance: robust capacity planning on networks.

### mohajerin2018data
Mohajerin Esfahani, P. and Kuhn, D. "Data-driven distributionally robust optimization using the Wasserstein metric: performance guarantees and tractable reformulations." Mathematical Programming 171(1-2):115-166, 2018 (online 2017). doi 10.1007/s10107-017-1172-1. Confirmed: Crossref (title truncated there at "performance guarante"; the rest of the title is from my knowledge, not the record). Read scope: metadata_only. Relevance: Wasserstein DRO foundation.

### delage2010distributionally
Delage, E. and Ye, Y. "Distributionally Robust Optimization Under Moment Uncertainty with Application to Data-Driven Problems." Operations Research 58(3):595-612, 2010. doi 10.1287/opre.1090.0741. Confirmed: Crossref. Read scope: metadata_only. Relevance: moment-based DRO foundation.

### kuhn2025distributionally
Kuhn, D., Shafiee, S., Wiesemann, W. "Distributionally robust optimization." Acta Numerica 34:579-804, 2025. doi 10.1017/S0962492924000084. Confirmed: Crossref. Read scope: metadata_only. Relevance: current survey for DRO.

### bertsimas2011theory
Bertsimas, D., Brown, D. B., Caramanis, C. "Theory and Applications of Robust Optimization." SIAM Review 53(3):464-501, 2011. doi 10.1137/080734510. Confirmed: Crossref. Read scope: metadata_only. Relevance: survey of robust optimisation.

### bertsimas2011price
Bertsimas, D., Farias, V. F., Trichakis, N. "The Price of Fairness." Operations Research 59(1):17-31, 2011. doi 10.1287/opre.1100.0865. Confirmed: Crossref. Read scope: metadata_only. Relevance: the standard "price of fairness" reference for F4 (from the title; contents not read).

### kelly1998rate
Kelly, F. P., Maulloo, A. K., Tan, D. K. H. "Rate control for communication networks: shadow prices, proportional fairness and stability." Journal of the Operational Research Society 49(3):237-252, 1998. doi 10.1057/palgrave.jors.2600523. Confirmed: Crossref (a second DOI 10.1038/sj.jors.2600523 also resolves). Read scope: metadata_only. Relevance: foundation of NUM and proportional fairness; title names F4.

### mo2000fair
Mo, J. and Walrand, J. "Fair end-to-end window-based congestion control." IEEE/ACM Transactions on Networking 8(5):556-567, 2000. doi 10.1109/90.879343. Confirmed: Crossref. Read scope: metadata_only. Relevance: fairness family for network rate allocation (F4).

### chiang2007layering
Chiang, M., Low, S. H., Calderbank, A. R., Doyle, J. C. "Layering as Optimization Decomposition: A Mathematical Theory of Network Architectures." Proceedings of the IEEE 95(1):255-312, 2007. doi 10.1109/JPROC.2006.887322. Confirmed: Crossref. Read scope: metadata_only. Relevance: NUM survey.

### parsaeefard2017robust
Parsaeefard, S., Sharafat, A. R., Mokari, N. *Robust Resource Allocation in Future Wireless Networks.* Springer, 2017. doi 10.1007/978-3-319-50389-9 (chapters 2 and 3 listed in Crossref: cooperative and noncooperative robust allocation). Confirmed: Crossref (book and chapter records). Read scope: metadata_only. Relevance: book-length treatment of robust wireless resource allocation; the nearest published match to "robust NUM", whose chapters I did not read.

### qiu2014robust
Qiu, F. and Xue, Y. "Robust Joint Congestion Control and Scheduling for Time-Varying Multi-Hop Wireless Networks With Feedback Delay" (title truncated in Crossref after "With Fee"; the ending "dback Delay" is from the 2012 SECON record's "with time delay" and a search snippet, so confirm). IEEE Transactions on Wireless Communications 13(9):5211-5222, 2014. doi 10.1109/TWC.2014.2339277. Confirmed: Crossref (partially). Read scope: metadata_only; a web search snippet describes a capacity-margin approach to fast channel fluctuations, which I did not verify. Relevance: robust congestion control with utility maximisation in wireless.

### caballero2019network
Caballero, P., Banchs, A., de Veciana, G., Costa-Perez, X. "Network Slicing Games: Enabling Customization in Multi-Tenant Mobile Networks." IEEE/ACM Transactions on Networking 27(2):662-675, 2019. doi 10.1109/TNET.2019.2895378. Confirmed: Crossref. Read scope: metadata_only. Relevance: multi-tenant slicing with game-theoretic (strategic) behaviour per title; the best match for F3/F5 in the slicing literature but not read.

### gholami2023mobile
Gholami, A., Torkzaban, N., Baras, J. S. "Mobile Network Slicing under Demand Uncertainty: A Stochastic Programming Approach." arXiv:2304.14556, 2023-04-27. Confirmed: arXiv export API record. Read scope: abstract_only (first ~600 characters). Summary: end-to-end slice orchestration across core and RAN under changing demand profiles, formulated as a two-stage stochastic mixed-integer program (the formulation detail is from a search snippet of the abstract, not checked in full). F1 partial (demand changes over time scales); F2 partial (per-slice requirements); F3 partial (slices tailored to customers; cost objective); F4 no; F5 no. Relevance: medium: slicing under demand uncertainty by stochastic programming.

### luu2020uncertainty
Luu, Q.-T., Kerboeuf, S., Kieffer, M. "Uncertainty-Aware Resource Provisioning for Network Slicing." arXiv:2006.01104, 2020-06-01. Confirmed: arXiv export API. Read scope: abstract_only. Summary: infrastructure-provider view of provisioning slice resources robustly to partly unknown demand (abstract begins "robust to a partly unknown..."; remainder not read). F1 partial; F2 partial; F3 partial; F4 no; F5 no. Relevance: medium: robust provisioning for slices.

### chatterjee2018optimal
Chatterjee, S., Abdel-Rahman, M. J., MacKenzie, A. B. "Optimal Virtualization Framework for Cellular Networks with Downlink Rate Coverage Probability Constraints." arXiv:1804.09680, 2018-04-25. Confirmed: arXiv export API. Read scope: abstract_only. Summary: wireless network virtualisation with uncertainty in UE locations and channel conditions and rate-coverage-probability constraints (chance constraints; MILP reformulation is from a search snippet). F1 no; F2 partial; F3 partial (service providers sharing resources); F4 no; F5 no. Relevance: medium: chance-constrained rate guarantees.

### li2020dra
Li, J., Liu, J., Huang, T., Liu, Y. "DRA-IG: The Balance of Performance Isolation and Resource Utilization Efficiency in Network Slicing." ICC 2020, pp. 1-6. doi 10.1109/ICC40277.2020.9149324. Confirmed: Crossref. Read scope: metadata_only (a search snippet describes a CVaR-based distributionally robust chance constraint; not verified). Relevance: DRO slicing candidate, to be read before citing.

### li2021nse
Li, J., Liu, J., Huang, T., Liu, Y. "NSE-RRS: Network Slicing Embedding With Risk-Controlled Resource Sharing." IEEE Access 9:104448-104459, 2021. doi 10.1109/ACCESS.2021.3099703. Confirmed: Crossref. Read scope: metadata_only. Relevance: risk-controlled slice sharing; read before citing.

## 4. BibTeX (verified records only)

```bibtex
@misc{rezaei2026robust,
  author = {Rezaei, Zolykha and Wei, Ningji},
  title = {Robust Network Enhancement: Formulations and Approximations},
  year = {2026}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2026/10/robust-network-enhancement-formulations-and-approximations/}}
@misc{beck2026wardrop,
  author = {Beck, Yasmine and Giancola, Francesca and Ljubi{\'c}, Ivana and Mattia, Sara},
  title = {Modeling Network Congestion under Demand Uncertainty Using {Wardrop} Principles},
  year = {2026}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2026/03/modeling-network-congestion-under-demand-uncertainty-using-wardrop-principles/}}
@misc{bao2026risk,
  author = {Bao, Wencheng and Vogiatzis, Chrysafis and Kontou, Eleftheria},
  title = {Risk-Averse Stochastic User Equilibrium on Uncertain Transportation Networks},
  year = {2026}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2026/03/risk-averse-stochastic-user-equilibrium-on-uncertain-transportation-networks/}}
@misc{makhau2026satellite,
  author = {Mak-Hau, Vicky and Gaudry, Angus},
  title = {Non-contiguous satellite channel allocation under cumulative interference: A hybrid price-and-branch approach},
  year = {2026}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2026/10/non-contiguous-satellite-channel-allocation-under-cumulative-interference-a-hybrid-price-and-branch-approach/}}
@misc{sun2021drfram,
  author = {Sun, Luying and Xie, Weijun and Witten, Tim},
  title = {Distributionally Robust Fair Transit Resource Allocation During a Pandemic},
  year = {2021}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2021/06/8466/},
  note = {Published in Transportation Science 57(4):954--978, 2023, doi:10.1287/trsc.2022.1159}}
@misc{sun2023fairuam,
  author = {Sun, Luying and Xie, Weijun},
  title = {Fair and Risk-averse Urban Air Mobility Resource Allocation Under Uncertainties},
  year = {2023}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2023/01/fair-and-risk-averse-urban-air-mobility-resource-allocation-under-uncertainties/},
  note = {Author list to be checked against the PDF; the page citation line also names Deng and Wei}}
@misc{tang2023learning,
  author = {Tang, Bill and Ko{\c c}yi{\u g}it, {\c C}a{\u g}{\i}l and Rice, Eric and Vayanos, Phebe},
  title = {Learning Optimal and Fair Policies for Online Allocation of Scarce Societal Resources from Data Collected in Deployment},
  year = {2023}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2023/11/learning-optimal-and-fair-policies-for-online-allocation-of-scarce-societal-resources-from-data-collected-in-deployment/}}
@misc{chen2022simple,
  author = {Chen, Rui and Gunluk, Oktay and Lodi, Andrea and Wang, Guanyi},
  title = {A Simple Algorithm for Online Decision Making},
  year = {2022}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2022/11/a-simple-algorithm-for-online-decision-making/}}
@misc{sujanani2025public,
  author = {Sujanani, Arnesh},
  title = {Asymptotically Fair and Truthful Allocation of Public Goods},
  year = {2025}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2025/06/asymptotically-fair-and-truthful-allocation-of-public-goods/}}
@misc{lodi2021fairness,
  author = {Lodi, Andrea and Olivier, Philippe and Pesant, Gilles and Sankaranarayanan, Sriram},
  title = {Fairness over Time in Dynamic Resource Allocation with an Application in Healthcare},
  year = {2021}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2021/01/8203/}}
@misc{altin2005vpn,
  author = {Altin, Aysegul and Amaldi, Edoardo and Belotti, Pietro and Pinar, Mustafa {\c C}.},
  title = {Provisioning Virtual Private Networks under traffic uncertainty},
  year = {2005}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2005/02/1072/}}
@misc{karasan2005dwdm,
  author = {Karasan, Oya Ekin and Pinar, Mustafa {\c C}. and Yaman, Hande},
  title = {Robust {DWDM} Routing and Provisioning under Polyhedral Demand Uncertainty},
  year = {2005}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2005/04/1115/}}
@misc{poss2013routing,
  author = {Poss, Michael},
  title = {A comparison of routing sets for robust network design},
  year = {2013}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2013/07/3983/}}
@misc{boyd2007dynamic,
  author = {Boyd, Stephen and Trichakis, Nikolaos and Zymnis, Argyrios},
  title = {Dynamic Network Utility Maximization with Delivery Contracts},
  year = {2007}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2007/09/1797/}}
@misc{boyd2007interior,
  author = {Boyd, Stephen and O'Neill, Daniel and Trichakis, Nikolaos and Zymnis, Argyrios},
  title = {An Interior-Point Method for Large Scale Network Utility Maximization},
  year = {2007}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2007/09/1796/}}
@misc{bhardwaj2014bandwidth,
  author = {Bhardwaj, Arjun and Sinha, Niraj and Vidyarthi, Navneet},
  title = {The Multi-Hour Bandwidth Packing Problem with Queuing Delays: Bounds and Exact Solution Approach},
  year = {2014}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2014/11/4624/}}
@misc{grothey2011topercentile,
  author = {Grothey, Andreas and Yang, Xinan},
  title = {Approximate Dynamic Programming with Bezier Curves/Surfaces for Top-percentile traffic routing},
  year = {2011}, howpublished = {Optimization Online},
  url = {https://optimization-online.org/2011/01/2877/}}

@article{bertsimas2004price,
  author = {Bertsimas, Dimitris and Sim, Melvyn}, title = {The Price of Robustness},
  journal = {Operations Research}, volume = {52}, number = {1}, pages = {35--53}, year = {2004}, doi = {10.1287/opre.1030.0065}}
@article{bertsimas2003robust,
  author = {Bertsimas, Dimitris and Sim, Melvyn}, title = {Robust discrete optimization and network flows},
  journal = {Mathematical Programming}, volume = {98}, number = {1--3}, pages = {49--71}, year = {2003}, doi = {10.1007/s10107-003-0396-4}}
@article{atamturk2007two,
  author = {Atamt{\"u}rk, Alper and Zhang, Muhong}, title = {Two-Stage Robust Network Flow and Design Under Demand Uncertainty},
  journal = {Operations Research}, volume = {55}, number = {4}, pages = {662--673}, year = {2007}, doi = {10.1287/opre.1070.0428}}
@article{benameur2005routing,
  author = {Ben-Ameur, Walid and Kerivin, Herv{\'e}}, title = {Routing of Uncertain Traffic Demands},
  journal = {Optimization and Engineering}, volume = {6}, number = {3}, pages = {283--313}, year = {2005}, doi = {10.1007/s11081-005-1741-7}}
@inproceedings{duffield1999hose,
  author = {Duffield, N. G. and Goyal, Pawan and Greenberg, Albert and Mishra, Partho and Ramakrishnan, K. K. and van der Merwe, Jacobus E.},
  title = {A flexible model for resource management in virtual private networks},
  booktitle = {Proc. ACM SIGCOMM}, pages = {95--108}, year = {1999}, doi = {10.1145/316188.316209}}
@article{ordonez2007robust,
  author = {Ord{\'o}{\~n}ez, Fernando and Zhao, Jiamin}, title = {Robust capacity expansion of network flows},
  journal = {Networks}, volume = {50}, number = {2}, pages = {136--145}, year = {2007}, doi = {10.1002/net.20183}}
@article{mohajerin2018data,
  author = {Mohajerin Esfahani, Peyman and Kuhn, Daniel},
  title = {Data-driven distributionally robust optimization using the {Wasserstein} metric: performance guarantees and tractable reformulations},
  journal = {Mathematical Programming}, volume = {171}, number = {1--2}, pages = {115--166}, year = {2018}, doi = {10.1007/s10107-017-1172-1}}
@article{delage2010distributionally,
  author = {Delage, Erick and Ye, Yinyu},
  title = {Distributionally Robust Optimization Under Moment Uncertainty with Application to Data-Driven Problems},
  journal = {Operations Research}, volume = {58}, number = {3}, pages = {595--612}, year = {2010}, doi = {10.1287/opre.1090.0741}}
@article{kuhn2025distributionally,
  author = {Kuhn, Daniel and Shafiee, Soroosh and Wiesemann, Wolfram}, title = {Distributionally robust optimization},
  journal = {Acta Numerica}, volume = {34}, pages = {579--804}, year = {2025}, doi = {10.1017/S0962492924000084}}
@article{bertsimas2011theory,
  author = {Bertsimas, Dimitris and Brown, David B. and Caramanis, Constantine}, title = {Theory and Applications of Robust Optimization},
  journal = {SIAM Review}, volume = {53}, number = {3}, pages = {464--501}, year = {2011}, doi = {10.1137/080734510}}
@article{bertsimas2011price,
  author = {Bertsimas, Dimitris and Farias, Vivek F. and Trichakis, Nikolaos}, title = {The Price of Fairness},
  journal = {Operations Research}, volume = {59}, number = {1}, pages = {17--31}, year = {2011}, doi = {10.1287/opre.1100.0865}}
@article{kelly1998rate,
  author = {Kelly, F. P. and Maulloo, A. K. and Tan, D. K. H.},
  title = {Rate control for communication networks: shadow prices, proportional fairness and stability},
  journal = {Journal of the Operational Research Society}, volume = {49}, number = {3}, pages = {237--252}, year = {1998}, doi = {10.1057/palgrave.jors.2600523}}
@article{mo2000fair,
  author = {Mo, J. and Walrand, J.}, title = {Fair end-to-end window-based congestion control},
  journal = {IEEE/ACM Transactions on Networking}, volume = {8}, number = {5}, pages = {556--567}, year = {2000}, doi = {10.1109/90.879343}}
@article{chiang2007layering,
  author = {Chiang, Mung and Low, Steven H. and Calderbank, A. Robert and Doyle, John C.},
  title = {Layering as Optimization Decomposition: A Mathematical Theory of Network Architectures},
  journal = {Proceedings of the IEEE}, volume = {95}, number = {1}, pages = {255--312}, year = {2007}, doi = {10.1109/JPROC.2006.887322}}
@book{parsaeefard2017robust,
  author = {Parsaeefard, Saeedeh and Sharafat, Ahmad Reza and Mokari, Nader},
  title = {Robust Resource Allocation in Future Wireless Networks},
  publisher = {Springer}, year = {2017}, doi = {10.1007/978-3-319-50389-9}}
@article{caballero2019network,
  author = {Caballero, Pablo and Banchs, Albert and de Veciana, Gustavo and Costa-P{\'e}rez, Xavier},
  title = {Network Slicing Games: Enabling Customization in Multi-Tenant Mobile Networks},
  journal = {IEEE/ACM Transactions on Networking}, volume = {27}, number = {2}, pages = {662--675}, year = {2019}, doi = {10.1109/TNET.2019.2895378}}
@misc{gholami2023mobile,
  author = {Gholami, Anousheh and Torkzaban, Nariman and Baras, John S.},
  title = {Mobile Network Slicing under Demand Uncertainty: A Stochastic Programming Approach},
  year = {2023}, eprint = {2304.14556}, archivePrefix = {arXiv}}
@misc{luu2020uncertainty,
  author = {Luu, Quang-Trung and Kerboeuf, Sylvaine and Kieffer, Michel},
  title = {Uncertainty-Aware Resource Provisioning for Network Slicing},
  year = {2020}, eprint = {2006.01104}, archivePrefix = {arXiv}}
@misc{chatterjee2018optimal,
  author = {Chatterjee, Shubhajeet and Abdel-Rahman, Mohammad J. and MacKenzie, Allen B.},
  title = {Optimal Virtualization Framework for Cellular Networks with Downlink Rate Coverage Probability Constraints},
  year = {2018}, eprint = {1804.09680}, archivePrefix = {arXiv}}
@inproceedings{li2020dra,
  author = {Li, Jieyu and Liu, Jiang and Huang, Tao and Liu, Yunjie},
  title = {{DRA-IG}: The Balance of Performance Isolation and Resource Utilization Efficiency in Network Slicing},
  booktitle = {Proc. IEEE ICC}, pages = {1--6}, year = {2020}, doi = {10.1109/ICC40277.2020.9149324}}
@article{li2021nse,
  author = {Li, Jieyu and Liu, Jiang and Huang, Tao and Liu, Yunjie},
  title = {{NSE-RRS}: Network Slicing Embedding With Risk-Controlled Resource Sharing},
  journal = {IEEE Access}, volume = {9}, pages = {104448--104459}, year = {2021}, doi = {10.1109/ACCESS.2021.3099703}}
```

Not included in BibTeX because the title was truncated in Crossref: qiu2014robust (doi 10.1109/TWC.2014.2339277, TWC 13(9):5211-5222, 2014; verify full title before citing).

## 5. Could not verify / could not retrieve

- A paper titled "robust network utility maximization" (the task's Yang et al. example): Crossref queries and one web search returned no such record. Not cited. Closest verified items: Parsaeefard et al. (book), Qiu and Xue (2014; metadata only).
- A chance-constrained 5G slicing paper "Coniglio et al." mentioned in a search summary: Crossref query returned nothing matching; unverified, not cited.
- Fendt et al., "An Efficient Model for Mobile Network Slice Embedding under Resource Uncertainty", ISWCS 2019, doi 10.1109/ISWCS.2019.8877372, appears in Crossref (metadata only, unread). Left out of the main list, available if wanted.
- Optimization Online search for "network slicing", "alpha-fairness", "bandwidth allocation": zero hits. No OO paper on ISP capacity allocation among heterogeneous QoS classes or on strategic misreporting in networks was found.
- OO category pages beyond the page ranges listed (and some pages that parsed empty) were not enumerated.
- No PDFs were opened; all published-literature items are metadata only except the three arXiv abstracts.
- Poss 2013: journal version (Optimization Letters) not verified in Crossref.

## 6. Strand synthesis

Robust and DRO approaches treat uncertainty as a property of the data: demand or capacity vectors lie in a budgeted, hose or ellipsoidal set, or the distribution lies in a moment or Wasserstein ball. The decision is then made once, ahead of time, against the worst case (or a risk measure), often with a second-stage recourse (Atamtürk-Zhang; Sun et al.; Gholami et al.). Online approaches, by contrast, treat uncertainty as sequential revelation. Decisions are made as arrivals occur, using dual prices or learned policies, and performance is measured by regret or constraint violation (Chen et al.; Tang et al.). The two are rarely combined in what I found.

Against F1-F5: churn (F1) is missing almost everywhere in the robust literature, which has a fixed demand set; only the online items treat arrivals, and none treats departures. Heterogeneous QoS (F2) appears at most as priorities or per-slice requirements; I found no treatment of inelastic or real-time utilities under robustness. Tier or business constraints (F3) show up as cost, revenue or contract terms (Boyd et al.; Bhardwaj et al.; Grothey and Yang) but not as tiers. Fairness (F4) is covered by DRO-fair allocation outside communications (Sun et al.) and by NUM fairness classics (Kelly; Mo-Walrand). Incentive compatibility (F5) appears only in Sujanani (static, public goods) and, by title, in Caballero et al.; none addresses misreporting of QoS class under uncertainty.

The author's seed paper (Rezaei and Wei) is of low relevance. It concerns robust upgrading of graph structures (spanning trees) with uncertain utilities and costs; it has none of F1-F5. Its only transferable element is the box approximation of an uncertainty set with a performance guarantee. The OO sweep as a whole confirms a gap: nothing on OO combines online allocation, churn, QoS classes, tiers, fairness and strategic users for network capacity.
