# Integrity verification, Phases A-B (references and citation context)

Paper: paper/main.tex + paper/sections/*.tex; bibliography paper/references.bib (63 entries). Mode: pre-review. Date of check: 2026-11-17.
Method: every entry re-fetched from a primary record, independent of research/lit/*.md. Sources used: Crossref API (`/works/<DOI>`, 42 DOI entries), arXiv API (`export.arxiv.org/api/query?id_list=`, 26 arXiv ids), USENIX pages (NSDI'11, OSDI'23), JMLR pages (v13 mahdavi12a, v21 16-494), Optimization Online pages (2 entries), arXiv full text (Karma 2305.17222, Credit Fairness 2601.17944, Dai et al. 2507.09473, Jaramillo-Srikant 0907.5402), NBER w23771 (Azevedo-Budish), EC'18 PDF (Benade et al.). Retrieved pages were treated as data only; none contained instructions.

## Summary counts

| Item | Count |
|---|---|
| bib entries | 63 |
| Phase A VERIFIED (exists, all fields match) | 57 |
| Phase A MINOR FIX | 6 |
| Phase A NOT FOUND / MISMATCH (fabricated or mashup) | 0 |
| Citation key occurrences in text (incl. Table 1) | 79 (63 distinct keys) |
| Phase B SUPPORTED (key occurrences) | 54 |
| Phase B PARTIALLY (key occurrences) | 18 |
| Phase B UNSUPPORTED | 0 |
| Uncited prior-work claims flagged | 3 |
| Phase B CANNOT CHECK (paywalled, generic attribution) | 7 |
| Dangling citations (cited, not in bib) | 0 |
| Orphan bib entries (never cited) | 0 |

Table 1 (6 rows, 12 key occurrences) is covered in Phase B as its own rows; two of its row-level marks are flagged. Tallies are per key occurrence (79 = 54 + 18 + 7).

---

## Phase A: bibliographic verification

All 63 entries correspond to real publications; authors (all, order, spelling), titles, venues, years, volumes/pages, DOIs and arXiv ids match the primary record except as listed. All 2025-2026 arXiv items exist under the cited id with the cited title and authors:
2611.08302 (Abdullah, Iosifidis, Elayoubi, Chahed; v1 2026-11-05; arXiv comment "Accepted at NeurIPS 2026" confirmed), 2610.25067 (Lin, Onyeze, Fikioris, Banerjee, Tardos; 2026-10-18), 2606.31480 (Yu, Lee, Lee; 2026-06-30), 2605.21107 (Sarkar, Sinha; v3 2026-07-22), 2605.19844 (Kahana, Segal-Halevi, Hazon; v1 2026-05-19, v5 2026-07-16), 2604.07246 (Elokda, Wang, Johansson, Fontan; 2026-04-08), 2601.17944 (Zahedi, Freeman; v2 2026-08-16), 2507.09473 (Dai, Golrezaei, Jaillet; v1 2025-07-13, v2 2026-07-15; arXiv comment says preliminary version accepted to NeurIPS 2025). Optimization Online: rezaei2026robust (Rezaei, Wei; posted 2026/10/26) and boyd2007dynamic (Boyd, Trichakis, Zymnis; 2007/09/30) confirmed on the repository pages.

| key | verdict | issue | corrected fields |
|---|---|---|---|
| azevedo2019strategy | MINOR FIX | Volume/issue/pages missing; Crossref issue date is online 2018, print is RES 86(1) 2019 | `volume={86}, number={1}, pages={81--116}, year={2019}` (drop the "Published online 2018" note or keep) |
| fikioris2025dmmf | MINOR FIX | Entry is typed as arXiv-only with year 2023 although the key says 2025 and the arXiv record carries DOI 10.1145/3736252.3742501; Crossref: Proc. 26th ACM Conference on Economics and Computation (EC'25), 2 Jul 2025, p. 92 | `@inproceedings`, `booktitle={Proceedings of the 26th ACM Conference on Economics and Computation}, year={2025}, pages={92}, doi={10.1145/3736252.3742501}, note={arXiv:2310.08881}` |
| yu2019low | MINOR FIX | JMLR canonical record (jmlr.org/papers/v21/16-494, BibTeX) is vol. 21, no. 1, 2020, pp. 1-24; the PDF header says "20 (2019) 1-25" (the source of the bib's volume 20). Use the JMLR index record | `volume={21}, number={1}, pages={1--24}, year={2020}` (also rename key to yu2020low or keep key) |
| le2019bopf | MINOR FIX | Crossref title is "BoPF: Mitigating the Burstiness-Fairness Tradeoff in Multi-Resource Clusters" (title "BoPF" + subtitle); bib has bare "BoPF" with the subtitle in a note | `title={{BoPF}: Mitigating the Burstiness-Fairness Tradeoff in Multi-Resource Clusters}` |
| neely2010stochastic | MINOR FIX | Book entry lacks publisher | `publisher={Morgan \& Claypool}` (series/DOI/year match Crossref) |
| vuppalapati2023karma | MINOR FIX | Pages missing (USENIX page: pp. 645-662, 978-1-939133-34-2); eprint and authors correct | `pages={645--662}` |
| abdullah2026dynamic | VERIFIED | none | |
| afeche2013incentive | VERIFIED | none | |
| balseiro2019nomoney | VERIFIED | none | |
| balseiro2023best | VERIFIED | none (arXiv 2011.10124 matches) | |
| balseiro2025regularized | VERIFIED | none (arXiv 2007.00514 matches) | |
| banerjee2023pseudo | VERIFIED | p. 241 is correct (EC'23 extended abstract) | |
| benade2018envy | VERIFIED | none | |
| benameur2005routing | VERIFIED | none | |
| bertsimas2004price | VERIFIED | none | |
| bertsimas2011price | VERIFIED | none | |
| boyd2007dynamic | VERIFIED | none | |
| cole2013mechanism | VERIFIED | full title with subtitle is the ACM title (Crossref splits it) | |
| dai2025efficiency | VERIFIED | none | |
| elazzouni2020deadline | VERIFIED | none (arXiv 2002.06474 matches) | |
| elokda2024karma | VERIFIED | vol 14(3) 2024, pp. 578-610 confirmed | |
| elokda2025carma | VERIFIED | none | |
| elokda2026ev | VERIFIED | none | |
| eryilmaz2007fair | VERIFIED | none | |
| fikioris2021incentives | VERIFIED | arXiv-only record (no later venue found in the arXiv record) | |
| freeman2018dynamic | VERIFIED | subtitle is the ACM title | |
| georgiadis2006resource | VERIFIED | none | |
| ghodsi2011dominant | VERIFIED | USENIX page confirms authors, NSDI'11 | |
| gholami2023mobile | VERIFIED | none | |
| gorokh2021monetary | VERIFIED | none | |
| hande2007distributed | VERIFIED | none | |
| hoiland2017ending | VERIFIED | arXiv-only entry; exists as cited | |
| jaramillo2011elastic | VERIFIED | none | |
| johari2004efficiency | VERIFIED | none | |
| kahana2026perpetual | VERIFIED | none | |
| kash2014no | VERIFIED | none | |
| kelly1998rate | VERIFIED | none | |
| lan2010axiomatic | VERIFIED | none | |
| lee2005nonconvex | VERIFIED | none | |
| li2020combinatorial | VERIFIED | none | |
| lin2026spec | VERIFIED | none | |
| mahdavi2012trading | VERIFIED | JMLR 13(81):2503-2528 confirmed | |
| mendelson1990optimal | VERIFIED | none | |
| mo2000fair | VERIFIED | none | |
| mohajerin2018data | VERIFIED | Crossref date 2017 is online-first; vol 171, 2018 is the print record | |
| musacchio2006wifi | VERIFIED | none | |
| neely2008fairness | VERIFIED | none | |
| neely2011worstcase | VERIFIED | none | |
| odlyzko1999paris | VERIFIED | none | |
| parekh1993generalized | VERIFIED | none | |
| rezaei2026robust | VERIFIED | none | |
| sarkar2026geometric | VERIFIED | none | |
| sen2013survey | VERIFIED | none | |
| shenker1995fundamental | VERIFIED | none | |
| shreedhar1996efficient | VERIFIED | none | |
| sinclair2021sequential | VERIFIED | arXiv-only entry; exists as cited | |
| sisalem2023enabling | VERIFIED | POMACS 6(3) Dec 2022 is correct; key says 2023 (SIGMETRICS 2023 presentation); cosmetic only | |
| stolyar2005maximizing | VERIFIED | none | |
| wong2013myob | VERIFIED | arXiv-only entry; exists as cited | |
| yu2017online | VERIFIED | none | |
| yu2017public | VERIFIED | none | |
| yu2026slater | VERIFIED | none | |
| zahedi2026credit | VERIFIED | none | |

Cross-check of similar references (Elokda x3, Fikioris x3, Yu/Neely x3, Balseiro x2): each is a distinct real publication; no mashup pattern found. Also noted: `paper/references_all.bib` (234 entries) is not what the paper compiles (`\bibliography{references}`); no action needed.

---

## Phase B: citation context

Location is file:line. "Supported" is judged on the abstract and, where noted, the full text I read.

| location | key | verdict | issue | suggested wording |
|---|---|---|---|---|
| analysis:68 | azevedo2019strategy | PARTIALLY | NBER/RES full text: "The first sufficient condition is envy-freeness"; Theorem 1: EF (and EF-but-for-tie-breaking, with anonymity/large-market conditions) implies SP-L. Sufficient condition, not "what makes" a mechanism SP-L; the paper says nothing of necessity | "who show that envy-freeness (and its tie-breaking relaxation) is a sufficient condition for strategy-proofness in the large" |
| related:33 | azevedo2019strategy | SUPPORTED | "large-market sense of" SP-L; accurate | |
| appendix:66 | neely2010stochastic | SUPPORTED | standard drift-plus-penalty O(V/eps) queue bound under slack (textbook, generic) | |
| experiments:23 | vuppalapati2023karma | SUPPORTED | "in the spirit of Karma"; adaptation disclosed as the authors' own | |
| related:4 | kelly1998rate | SUPPORTED | NUM / proportional fairness | |
| related:4 | mo2000fair | SUPPORTED | alpha-fair family attribution (abstract-level evidence thin; CANNOT CHECK full text, but a generic well-known attribution) | |
| related:4 | lan2010axiomatic | SUPPORTED | axiomatic derivation of fairness families (title/arXiv abstract) | |
| related:4 | bertsimas2011price | SUPPORTED | price of fairness, Crossref abstract | |
| related:5 | shenker1995fundamental | CANNOT CHECK | paywalled; elastic vs real-time distinction is a generic well-known attribution | none needed |
| related:5 | lee2005nonconvex | CANNOT CHECK | paywalled; non-concave multi-class rate control; generic, low risk | none needed |
| related:5 | hande2007distributed | CANNOT CHECK | paywalled; inelastic flow rate allocation by title; generic, low risk | none needed |
| related:6 | parekh1993generalized, shreedhar1996efficient | PARTIALLY | Support WFQ/GPS and DRR as approximations; they do not support "remain the deployed mechanisms" (deployment claim) | "Weighted fair queueing and its practical approximations \citep{...} are the classical mechanisms, and..." or add a deployment source |
| related:6 | hoiland2017ending | SUPPORTED | airtime fairness in the Linux mainline AP stack (abstract) | |
| related:8 | sisalem2023enabling | PARTIALLY | abstract: slot- vs horizon-fairness; "vanishing regret cannot be achieved in presence of an unrestricted adversary". Claim is right but "cannot be learned" paraphrases a regret impossibility | "show that vanishing regret is impossible against an unrestricted adversary" |
| related:8 | elazzouni2020deadline | SUPPORTED | online deadline-constrained allocation with long-term fairness (abstract) | |
| related:11 | georgiadis2006resource, neely2010stochastic | SUPPORTED | drift-plus-penalty monographs | |
| related:11 | stolyar2005maximizing | CANNOT CHECK | paywalled; primal-dual NUM; generic attribution | none needed |
| related:11 | eryilmaz2007fair | CANNOT CHECK | paywalled; queue-length-based fair scheduling; generic | none needed |
| related:11 | neely2008fairness | CANNOT CHECK | paywalled; generic | none needed |
| related:12 | neely2011worstcase | PARTIALLY | Title and secondary description confirm a worst-case delay guarantee scheme; I could not read the paper to confirm that the technique is a deterministic bound on virtual queues | keep, but "for example for worst-case delay" is fine only if the authors have checked; low risk |
| related:13 | jaramillo2011elastic | SUPPORTED | arXiv 0907.5402 full text: deficit counters (d_l(k+1) = [d_l(k) + lambda_l(1-p_l) - mu_il(k)]^+) record the service deficit of inelastic flow l against a required on-time delivery fraction (1-p_l); elastic and inelastic traffic in one dual-decomposition/Lyapunov scheme; link set L fixed. The paper's description (deficit protects the delivery ratio of real-time flows, flow set fixed) is accurate. Note the counters are per link/flow and are Lagrange multipliers | none; optionally say "per-flow (per-link) deficit counters" |
| related:14 | mahdavi2012trading, yu2017online, yu2019low | SUPPORTED | OCO with long-term constraints (abstracts) | |
| related:14 | balseiro2023best, balseiro2025regularized | PARTIALLY | dual mirror descent / regularized allocation: guarantees are regret / competitive ratio under hard resource constraints, not constraint "violation" | "give regret and competitive-ratio guarantees for aggregate resource constraints" (violation bounds come from the OCO papers) |
| related:14 | yu2026slater, sarkar2026geometric, abdullah2026dynamic | SUPPORTED | Slater-free (Yu et al.), adversarial time-varying constraints (Sarkar-Sinha), time-varying constraints with memory (Abdullah et al.), all per arXiv abstracts | |
| related:16 | sinclair2021sequential | SUPPORTED | envy-efficiency trade-off, individuals arriving online (abstract) | |
| related:16 | li2020combinatorial | SUPPORTED | virtual queues for minimum selection fraction of sleeping arms (abstract) | |
| related:16 | (none) | uncited claim | "We found no drift-plus-penalty or constrained-online-learning result with guarantees per agent over a finite sojourn..." is a negative-novelty claim about the literature | "To our knowledge, ..." and state the search scope |
| related:20 | mendelson1990optimal | SUPPORTED | incentive-compatible priority pricing (Crossref abstract) | |
| related:20 | afeche2013incentive | SUPPORTED | strategic delay of patient customers can be optimal (abstract) | |
| related:21 | odlyzko1999paris | CANNOT CHECK | paywalled; PMP is a well-known attribution; "applies the idea to networks" is generic | none needed |
| related:21 | sen2013survey | SUPPORTED | survey of time- and usage-dependent pricing (abstract) | |
| related:22 | yu2017public | PARTIALLY | title: public Wi-Fi monetization via advertising (free access funded by ads); fits "free vs paid" loosely | "the economics of public Wi-Fi, including ad-funded free access \citep{yu2017public}" |
| related:22 | musacchio2006wifi | PARTIALLY | WiFi access point pricing as a dynamic game (competition among APs); not specifically free vs paid; abstract not retrievable (paywalled) | "pricing of Wi-Fi access points is studied by ..." |
| related:22 | johari2004efficiency | SUPPORTED | efficiency loss (3/4 bound) when users anticipate prices (abstract) | |
| related:23 (no cite) | (none) | uncited claim | "All of these screen with payments." is too broad: Johari-Tsitsiklis is a price-anticipating game, Sen et al. is a survey, Yu et al. use advertising | "Most of these screen with payments or prices." |
| related:27 | ghodsi2011dominant | SUPPORTED | DRF (USENIX page) | |
| related:27 | kash2014no, freeman2018dynamic, fikioris2021incentives | SUPPORTED | dynamic fair division of multiple resources (Kash), dynamic proportional sharing (Freeman; a dynamic max-min/FBP, not strictly DRF), dynamic DRF (Fikioris) | |
| related:27 | cole2013mechanism | SUPPORTED | truthful mechanisms without payments (ACM title) | |
| related:27 | gorokh2021monetary | PARTIALLY | abstract: artificial-currency mechanisms give "vanishing gains from nontruthful reporting", i.e. approximate, asymptotic truthfulness, not exact truthfulness | "obtain (approximate) truthfulness without money; Gorokh et al. do so through artificial currencies" |
| related:29 | vuppalapati2023karma | SUPPORTED | full text: Karma is a credit-based allocation for one resource type (slices); "Theorem 2. Karma is online strategy-proof" (proof Appendix A.4); also handles churn heuristically (Sec. on user churn) | |
| related:29 | le2019bopf | SUPPORTED | BoPF: short-term (burst) guarantees to latency-sensitive jobs, long-term fairness for throughput-sensitive ones, strategy-proof (arXiv abstract). Note: this is a two-class system, relevant to the "single kind" statement at related:31 | |
| related:29 | elokda2024karma, elokda2025carma, elokda2026ev | SUPPORTED | karma economies for ride hailing/intersections/internet fast channel (2024), bottleneck road congestion with urgency-dependent value of time (2025), EV charging with urgency (2026) | |
| related:29 | wong2013myob | SUPPORTED | gateways buy guaranteed bandwidth from the ISP with virtual credits; credit allocation and redistribution (arXiv abstract) | |
| related:29 | zahedi2026credit | SUPPORTED | Theorem 3 (full text): "No mechanism is anonymous, strategyproof, credit fair, and Pareto efficient." Matches the paper's wording exactly. Setting: capped linear utilities, repeated allocation | |
| related:30 | balseiro2019nomoney | SUPPORTED | repeated allocation without money (title/Crossref) | |
| related:30 | banerjee2023pseudo | SUPPORTED | ideal-utility guarantees in non-monetary repeated allocation (abstract) | |
| related:30 | fikioris2025dmmf | SUPPORTED | ideal-utility guarantee for dynamic max-min fairness under arbitrary behaviour of others (abstract) | |
| related:30 | lin2026spec | SUPPORTED | non-monetary stochastic scheduling with robust utility guarantees (abstract) | |
| related:30 | benade2018envy | PARTIALLY | EC'18 full text: a deterministic algorithm with Envy_T in O~(sqrt(T/n)) (tight) for indivisible goods; there is no deficit mechanism ("deficit" does not occur) and the bound is on envy at horizon T, growing in T, rather than a constant anytime deficit bound | "sublinear-envy rules in \citet{benade2018envy} and deficit-based rules with anytime fairness bounds in \citet{kahana2026perpetual}" |
| related:30 | kahana2026perpetual | SUPPORTED | deficit-based, anytime guarantees (abstract: "deficits", "anytime guarantees") | |
| related:31 (no cite) | (none) | PARTIALLY | "These works assume agents of a single kind (they differ in demand or urgency, not in the shape of their utility), a fixed or heuristically handled population, and no operator-side constraints." Sweeping claim about ~12 cited papers without citation; contradicted for BoPF (latency- vs throughput-sensitive jobs), CARMA (heterogeneous income classes, dynamic VOT) and Wong et al. (priorities, ISP-side contracts) | "Most of these works assume agents of one kind or two coarse classes, ..." and name the exceptions (BoPF, CARMA) |
| related:33 | zahedi2026credit | SUPPORTED | impossibility used as consistency check; caveat that Zahedi's theorem is for capped linear utilities and anonymous mechanisms | "Consistent in spirit with ..." |
| related:34 | dai2025efficiency | PARTIALLY | abstract: standard primal-dual methods are "fragile": agents manipulate reports to distort dual variables. The remedy is VCG-based payments plus epoch-based lazy dual updates plus random exploration, not payments alone; setting is indivisible resources and near-truthful equilibrium, regret O~(sqrt T) | "show that, in primal-dual allocation rules, agents can manipulate reports to distort the dual variables, and suppress this with VCG-type payments combined with lazy dual updates and random exploration" |
| related:37 | benameur2005routing, bertsimas2004price | PARTIALLY | Ben-Ameur-Kerivin is routing under uncertain demand (fits); Bertsimas-Sim is general robust linear/discrete optimization, not network design | "robust routing under demand uncertainty \citep{benameur2005routing} and robust optimisation \citep{bertsimas2004price}" |
| related:37 | rezaei2026robust | SUPPORTED | robust network enhancement (repository page) | |
| related:37 | mohajerin2018data | SUPPORTED | distributionally robust optimisation (Wasserstein) | |
| related:37 | gholami2023mobile | SUPPORTED | stochastic programming for slicing under demand uncertainty (arXiv abstract) | |
| related:38 | boyd2007dynamic | SUPPORTED | multi-period NUM with delivery contracts coupling rates across time (repository abstract); "closest analogue" is the author's judgment | |
| Table1 row 1 (related:50) | kelly1998rate, parekh1993generalized | SUPPORTED | marks churn --, RT --, IC -- are reasonable; "tiers/constraints: partial" via weights | |
| Table1 row 2 (related:51) | lee2005nonconvex, hande2007distributed | SUPPORTED | RT check, fairness partial: reasonable | |
| Table1 row 3 (related:52) | neely2010stochastic, jaramillo2011elastic | SUPPORTED | RT check from Jaramillo-Srikant, constraints and fairness from Neely; churn "--" fixed flow set confirmed | |
| Table1 row 4 (related:53) | yu2017online, balseiro2025regularized | PARTIALLY | "churn: partial" is not supported by either source: they have request/round arrivals, not agents that join and leave with a sojourn | change churn mark to "--" |
| Table1 row 5 (related:54) | mendelson1990optimal, afeche2013incentive | SUPPORTED | IC "-- (payments)" accurate | |
| Table1 row 6 (related:55) | vuppalapati2023karma, zahedi2026credit | PARTIALLY | "IC without money: check" holds for Karma (online SP) but Zahedi's own mechanism (LendRecoup) is not SP, and Theorem 3 shows PE + credit fairness + anonymity exclude SP; "churn: partial" holds for Karma (heuristic churn handling), not for Zahedi | mark IC as "partial" for the row, or split Karma and Credit Fairness |

Other statements about prior work without citation:
- intro:7-9 "The access point usually cannot tell from encrypted packets what an application is": factual claim, no source. MINOR; add a source or phrase it as an assumption.
- intro:21 "Credit-based sharing ... underlies recent resource managers and 'karma' economies": covered by the forward reference to Section 2; acceptable.
- intro:3/4 claims that strict priority and utility-maximising schedulers have the incentive defect: supported by the paper's own analysis (analysis.tex 173-180) and simulations, not by a citation; acceptable.
- related:16 negative-novelty claim and related:31 generalisation: see table.

---

## Verdict Phases A-B: FAIL

No fabricated, mismatched or unverifiable reference was found (0 NOT FOUND). The FAIL follows from the MEDIUM items below (zero MEDIUM is required for PASS).

### Required fixes, by severity

SERIOUS: none.

MEDIUM (overstated or mischaracterised claims about prior work):
1. analysis:68 (Azevedo-Budish): replace "show that envy-freeness is what makes a mechanism strategy-proof in the large" with "show that envy-freeness (and a tie-breaking relaxation of it) is a sufficient condition for strategy-proofness in the large".
2. related:34 (Dai et al.): replace "show that the dual variables of primal-dual allocation rules are themselves a channel for manipulation and remove it with payments" with "show that agents can manipulate the dual variables of standard primal-dual allocation rules by misreporting, and suppress this with VCG-type payments together with lazy dual updates and random exploration (indivisible resources)".
3. related:30 (Benade et al.): remove it from "deficit-based rules with anytime fairness bounds"; cite it as a sublinear-envy rule (Envy_T in O~(sqrt(T/n))) and keep only Kahana et al. as deficit-based.
4. related:31 (sweeping sentence "These works assume agents of a single kind ... a fixed or heuristically handled population, and no operator-side constraints"): contradicted by BoPF (two classes), CARMA (heterogeneous classes) and Wong et al. (ISP-side contracts); soften to "most of these works" and name exceptions.
5. related:27 (Gorokh et al.): "truthfulness" -> "approximate (vanishing-gain) truthfulness".
6. Table 1, row "Credit mechanisms": IC mark should be partial (Zahedi's mechanism is not strategy-proof; Theorem 3 rules out the full combination); churn mark is partial only for Karma.

MINOR:
7. Bib metadata: azevedo2019strategy (volume 86, number 1, pages 81--116); fikioris2025dmmf (EC'25, 2025, p. 92, DOI); yu2019low (JMLR 21(1), 1--24, 2020); le2019bopf (full title); neely2010stochastic (publisher Morgan & Claypool); vuppalapati2023karma (pages 645--662). Keys sisalem2023enabling (year 2022) and fikioris2025dmmf/yu2019low are cosmetic.
8. related:8: "cannot be learned" -> "vanishing regret is impossible" (Si-Salem et al.).
9. related:14: Balseiro et al. give regret/competitive-ratio, not violation, guarantees.
10. related:37: Bertsimas-Sim is general robust optimisation, not network design.
11. related:22: Musacchio-Walrand and Yu et al. are not specifically "free versus paid"; related:23 "All of these screen with payments" -> "Most of these".
12. related:6: "remain the deployed mechanisms" needs a deployment source or softer wording.
13. related:16: negative-novelty sentence -> "To our knowledge".
14. Table 1 row "Constrained online learning": churn mark "partial" is unsupported; use "--".
15. intro: uncited claim about encrypted traffic classification.
16. Could not retrieve: abstracts/full text of paywalled items (shenker1995, lee2005, hande2007, stolyar2005, eryilmaz2007, neely2008, odlyzko1999, musacchio2006, neely2011worstcase body, mo2000); these are generic attributions and are marked CANNOT CHECK or low-risk. Semantic Scholar was rate-limited (429) and not used.
