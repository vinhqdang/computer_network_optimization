# Strand 03: Game theory, pricing and mechanism design for network/resource allocation

Search date: 2026-11-17. Features tracked: F1 churn/dynamic arrivals-departures; F2 heterogeneous QoS utilities incl. inelastic/real-time; F3 tier/business constraints (SLA, revenue); F4 fairness; F5 incentive compatibility / strategic users.

Coverage legend: yes / partial / no / n.r. (not read; metadata only, so not assessed). Read scopes: `full_text` (with sections stated), `abstract_only`, `metadata_only`.

## 1. Search log

Tools: curl to Crossref REST API (`api.crossref.org/works?query.bibliographic=...` and `/works/<DOI>`), arXiv export API (`export.arxiv.org/api/query`), USENIX pages (citation meta tags), arXiv/JAIR/NBER/Duke PDFs via curl + pdftotext, WebSearch (one query). DBLP API was unusable: it returned a "Making sure you're not a bot" challenge page (HTTP 202), so no DBLP confirmation was used anywhere.

Queries run (all 2026-11-17):
- Crossref bibliographic queries, one per hinted title: Kelly-Maulloo-Tan; Johari-Tsitsiklis; Chau-Wang-Chiu PMP; Sen et al. SDP survey; Mendelson-Whang; Afeche strategic delay; Odlyzko PMP; Joe-Wong/Ha/Chiang TUBE; Yu et al. Wi-Fi advertising; Musacchio-Walrand; DRF; Parkes-Procaccia-Shah; Kash-Procaccia-Shah; Friedman-Psomas-Vardi; Freeman et al.; Cole-Gkatzelis-Goel; Gorokh et al.; Elokda karma; Azevedo-Budish; Basar-Srikant; Acemoglu-Ozdaglar; Cocchi et al.; Shenker 1995; Gibbens et al.; Njoroge et al.; Economides-Hermalin; Choi-Kim; Iosifidis et al.; Joe-Wong multi-resource; Bonald-Roberts; Budish ACEEI; Bergemann-Valimaki; Pavan-Segal-Toikka; Prendergast; Afeche-Mendelson 2004; Benade et al.; Sinclair et al.; Elokda CARMA; Yang-Hajek; Marbach; Hande et al.; Jain-Walrand; Kelly 1997; Zhou-Zheng TRUST; Ma et al. crowdsourced Wi-Fi.
- arXiv API: Karma (OSDI), Elokda karma economy, DRF, dynamic fair division, online fair division, strategyproof Wi-Fi, network slicing Stackelberg pricing, crowdsourced Wi-Fi pricing game, paid prioritization, non-monetary mechanisms with credits, artificial currencies.
- Full-text retrieval: arXiv 2305.17222, 2207.00495, 2208.07113, 1212.1522, 2505.13824; JAIR article 10917 (Kash et al.); Duke PDF (Freeman et al.); NBER w23771 (Azevedo-Budish).
- WebSearch: Afeche 2013 PDF (only publisher page and supplement found; no open full text).

Not retrievable as full text (paywalled): Mendelson-Whang 1990, Afeche 2013, Afeche-Mendelson 2004, Chau et al. 2014, Sen et al. 2013, Ha et al. 2012 and the other INFORMS/ACM/IEEE items. These are `abstract_only` or `metadata_only` below.

Note: the Kelly-Maulloo-Tan paper appears in Crossref under two DOIs (10.1038/sj.jors.2600523 and 10.1057/palgrave.jors.2600523); the Palgrave DOI is used.

## 2. Sources

### A. Network pricing, ISP economics, service differentiation

### kelly1998rate
Kelly, F. P., Maulloo, A. K., Tan, D. K. H. (1998). Rate control for communication networks: shadow prices, proportional fairness and stability. *Journal of the Operational Research Society* 49(3):237-252.
- Identifier: DOI 10.1057/palgrave.jors.2600523; confirmed via Crossref record.
- Read scope: metadata_only.
- Summary: Not read here. Canonical source for utility-based, price-driven rate control and proportional fairness (title only; no claims made beyond that).
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Foundational reference for the pricing view of fairness (shadow prices); cite as background.

### kelly1997charging
Kelly, F. (1997). Charging and rate control for elastic traffic. *European Transactions on Telecommunications* 8(1):33-37.
- Identifier: DOI 10.1002/ett.4460080106; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates charging and rate control for elastic traffic.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Background for the elastic (delay-tolerant) class; companion to kelly1998rate.

### johari2004efficiency
Johari, R., Tsitsiklis, J. N. (2004). Efficiency loss in a network resource allocation game. *Mathematics of Operations Research* 29(3):407-435.
- Identifier: DOI 10.1287/moor.1040.0091; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates a game-theoretic analysis of efficiency loss under a network resource allocation (price-based) mechanism.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Standard citation for strategic users in a Kelly-type mechanism; quantifies cost of strategic behaviour (verify claims against the paper before citing results).

### cocchi1993pricing
Cocchi, R., Shenker, S., Estrin, D., Zhang, L. (1993). Pricing in computer networks: motivation, formulation, and example. *IEEE/ACM Transactions on Networking* 1(6):614-627.
- Identifier: DOI 10.1109/90.266050; confirmed via Crossref. A related SIGCOMM 1991 paper "A study of priority pricing in multiple service class networks" (DOI 10.1145/115994.116005) also exists in Crossref but is not listed separately.
- Read scope: metadata_only.
- Summary: Not read here. Early work on pricing in computer networks including priority/multi-class service (from titles only).
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Historical anchor for priority pricing across service classes.

### shenker1995fundamental
Shenker, S. (1995). Fundamental design issues for the future Internet. *IEEE Journal on Selected Areas in Communications* 13(7):1176-1188.
- Identifier: DOI 10.1109/49.414637; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Commonly cited for the distinction between elastic and real-time (inelastic) application utilities; this characterisation comes from background knowledge, not from reading, so verify before citing.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Candidate source for F2 (utility shapes of elastic vs real-time traffic).

### gibbens2000internet
Gibbens, R., Mason, R., Steinberg, R. (2000). Internet service classes under competition. *IEEE Journal on Selected Areas in Communications* 18(12):2490-2498.
- Identifier: DOI 10.1109/49.898732; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates analysis of multiple Internet service classes under competition.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Service-class/price differentiation under competing providers.

### marbach2003priority
Marbach, P. (2003). Priority service and max-min fairness. *IEEE/ACM Transactions on Networking* 11(5):733-746.
- Identifier: DOI 10.1109/tnet.2003.818196; confirmed via Crossref (INFOCOM 2002 version: DOI 10.1109/infcom.2002.1019268).
- Read scope: metadata_only.
- Summary: Not read here. Title links priority service classes with max-min fairness.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Potential bridge between priority tiers and fairness; read before relying.

### odlyzko1999paris
Odlyzko, A. (1999). Paris Metro pricing for the Internet. In *Proceedings of the 1st ACM Conference on Electronic Commerce (EC '99)*, pp. 140-147.
- Identifier: DOI 10.1145/336992.337030; confirmed via Crossref (workshop version: IWQoS 1999, DOI 10.1109/iwqos.1999.766491, pp. 159-161).
- Read scope: metadata_only.
- Summary: Not read here. Original proposal of Paris Metro Pricing (PMP): several logical networks with identical capacity but different prices (self-selection of congestion level) as understood from the title and the Chau et al. abstract.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Price-based self-selection of service class (F5/F3 baseline).

### chau2014economic
Chau, C.-K., Wang, Q., Chiu, D.-M. (2014). Economic viability of Paris Metro Pricing for digital services. *ACM Transactions on Internet Technology* 14(2-3):1-21.
- Identifier: DOI 10.1145/2663492; confirmed via Crossref (conference version: INFOCOM 2010, DOI 10.1109/infocom.2010.5461957).
- Read scope: abstract_only (Crossref abstract, partly truncated in my view).
- Summary: Studies whether PMP with multiple isolated service classes at differentiated prices is economically viable (more profit for provider, more social welfare); notes prior studies used specific models and reached conflicting conclusions, and derives unifying principles in a general setting.
- F1 no; F2 partial (classes, no explicit inelastic utilities per abstract); F3 yes (profit, welfare); F4 no; F5 partial (users self-select class).
- Relevance: Main reference on whether class-differentiated pricing pays off.

### sen2013survey
Sen, S., Joe-Wong, C., Ha, S., Chiang, M. (2013). A survey of smart data pricing: past proposals, current plans, and future trends. *ACM Computing Surveys* 46(2):Article 15, 1-37. (Title in Crossref: "A survey of smart data pricing".)
- Identifier: DOI 10.1145/2543581.2543582; confirmed via Crossref. The full title with the subtitle is from memory; the Crossref record title is "A survey of smart data pricing".
- Read scope: abstract_only.
- Summary: Surveys static and dynamic broadband pricing proposals, their realisations in consumer data plans, and open research problems as operators move from flat rate to richer pricing.
- F1 no; F2 no; F3 yes; F4 no; F5 partial.
- Relevance: Survey anchor for tiered/usage/time-dependent plans (F3).

### ha2012tube
Ha, S., Sen, S., Joe-Wong, C., Im, Y., Chiang, M. (2012). TUBE: time-dependent pricing for mobile data. *ACM SIGCOMM Computer Communication Review* 42(4):247-258. (Crossref title: "TUBE".)
- Identifier: DOI 10.1145/2377677.2377723; confirmed via Crossref. Subtitle is from memory, not from the record.
- Read scope: abstract_only.
- Summary: Presents the architecture, implementation and a user trial of an end-to-end time-dependent pricing (TDP) system: a price-based feedback loop where the ISP computes prices to balance congestion cost against discounts and users respond via a mobile GUI.
- F1 no; F2 no; F3 yes; F4 no; F5 partial (user price response, no misreport model).
- Relevance: Price-incentive load shifting of delay-tolerant traffic; monetary counterpart of deferral-with-compensation.

### mendelson1990optimal
Mendelson, H., Whang, S. (1990). Optimal incentive-compatible priority pricing for the M/M/1 queue. *Operations Research* 38(5):870-883.
- Identifier: DOI 10.1287/opre.38.5.870; confirmed via Crossref.
- Read scope: abstract_only (full text paywalled).
- Summary: M/M/1 system with multiple user classes characterised by delay cost, service time and demand function; derives a pricing mechanism that is optimal and incentive-compatible, with arrival rates and priorities chosen on a decentralised basis by users, and gives a closed-form price structure.
- F1 no (steady-state queue); F2 yes (classes differ in delay cost); F3 partial (system net value, not revenue tiers); F4 no; F5 yes (IC via payments).
- Relevance: Core precedent for delay-cost screening of classes with money; the baseline our payment-free scheme should be compared with.

### afeche2004pricing
Afèche, P., Mendelson, H. (2004). Pricing and priority auctions in queueing systems with a generalized delay cost structure. *Management Science* 50(7):869-882.
- Identifier: DOI 10.1287/mnsc.1030.0156; confirmed via Crossref.
- Read scope: abstract_only.
- Summary: Compares revenue-maximising and socially optimal equilibria under uniform pricing, preemptive and nonpreemptive priority auctions with admission price when delay cost depends on service valuation; shows the delay-cost structure can reverse classical conclusions.
- F1 no; F2 yes; F3 yes (revenue); F4 no; F5 yes (bidding equilibrium).
- Relevance: Priority auctions with heterogeneous delay costs; revenue vs welfare.

### afeche2013incentive
Afèche, P. (2013). Incentive-compatible revenue management in queueing systems: optimal strategic delay. *Manufacturing & Service Operations Management* 15(3):423-443.
- Identifier: DOI 10.1287/msom.2013.0449; confirmed via Crossref; publisher page located via search; no open full text.
- Read scope: abstract_only.
- Summary: Two-type queue with private delay-sensitivity; combines achievable-region analysis with mechanism design. Shows the work-conserving c-mu rule (delay-cost minimising, IC, socially optimal) need not maximise revenue and that artificially inflating the lead time of patient customers (strategic delay) can be revenue-optimal.
- F1 no; F2 yes; F3 yes; F4 no; F5 yes.
- Relevance: Closest known "delay as a screening device": deferral of the patient class is used to extract revenue, with payments. Our setting uses deferral plus later compensation instead of payments.

### basar2002revenue
Basar, T., Srikant, R. (2002). Revenue-maximizing pricing and capacity expansion in a many-users regime. In *Proc. IEEE INFOCOM 2002*, vol. 1, pp. 294-301.
- Identifier: DOI 10.1109/infcom.2002.1019271; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates ISP revenue-maximising pricing and capacity in a many-users regime.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Candidate for ISP-user Stackelberg framing (verify content before citing as Stackelberg).

### hande2010pricing
Hande, P., Chiang, M., Calderbank, R., Zhang, J. (2010). Pricing under constraints in access networks: revenue maximization and congestion management. In *Proc. IEEE INFOCOM 2010*, pp. 1-9.
- Identifier: DOI 10.1109/infcom.2010.5461954; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates revenue maximisation and congestion management in access-network pricing.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Candidate for F3 (revenue under constraints); read before use.

### yang2007vcg
Yang, S., Hajek, B. (2007). VCG-Kelly mechanisms for allocation of divisible goods: adapting VCG mechanisms to one-dimensional signals. *IEEE Journal on Selected Areas in Communications* 25(6):1237-1243.
- Identifier: DOI 10.1109/jsac.2007.070817; confirmed via Crossref (conference version CISS 2006, DOI 10.1109/ciss.2006.286682).
- Read scope: metadata_only.
- Summary: Not read here. Title indicates a Kelly-style one-dimensional-signal mechanism adapted from VCG for divisible goods.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Candidate for strategyproof (with payments) network allocation.

### economides2012economics
Economides, N., Hermalin, B. E. (2012). The economics of network neutrality. *RAND Journal of Economics* 43(4):602-629.
- Identifier: DOI 10.1111/1756-2171.12001; confirmed via Crossref.
- Read scope: abstract_only.
- Summary: Analyses private and social effects of fees charged to content providers for access to ISP's residential customers and for prioritisation, when the network is congested and more traffic implies longer delay; derives conditions under which such fees help or harm.
- F1 no; F2 partial; F3 yes; F4 partial (social welfare); F5 no.
- Relevance: Net-neutrality/paid-prioritisation benchmark for ISP revenue.

### njoroge2014investment
Njoroge, P., Ozdaglar, A., Stier-Moses, N. E., Weintraub, G. Y. (2014). Investment in two-sided markets and the net neutrality debate. *Review of Network Economics* 12(4).
- Identifier: DOI 10.1515/rne-2012-0017; confirmed via Crossref (no page numbers in record).
- Read scope: metadata_only.
- Summary: Not read here. Title indicates a two-sided-market model of provider investment and net neutrality.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Secondary net-neutrality reference.

### naghizadeh2020paid
Naghizadeh, P., Joe-Wong, C., Chiang, M. (2020). Paid prioritization with content competition. arXiv:2007.14574 (preprint).
- Identifier: arXiv:2007.14574v1 (arXiv API record; no journal reference listed).
- Read scope: abstract_only.
- Summary: Studies paid-prioritisation (fast lane) arrangements under content-provider competition with a monopolist ISP, with multi-purchasing users; shows ISP incentives to build extra fast lanes subsidised by high-revenue CPs and that non-prioritised CPs need not lose users.
- F1 no; F2 partial; F3 yes; F4 no; F5 no.
- Relevance: Recent ISP paid-prioritisation model (2020).

### yu2017public
Yu, H., Cheung, M. H., Gao, L., Huang, J. (2017). Public Wi-Fi monetization via advertising. *IEEE/ACM Transactions on Networking* 25(4):2110-2121.
- Identifier: DOI 10.1109/tnet.2017.2675944 (Crossref); arXiv:1609.01951 (abstract read).
- Read scope: abstract_only.
- Summary: Venue owners offer premium (paid) access or ad-sponsored free access; the interactions among ad platform, venue owners, users and advertisers are modelled as a three-stage Stackelberg game.
- F1 no; F2 no; F3 yes; F4 no; F5 partial (users choose access scheme).
- Relevance: Free vs premium tier economics of public Wi-Fi.

### musacchio2006wifi
Musacchio, J., Walrand, J. (2006). WiFi access point pricing as a dynamic game. *IEEE/ACM Transactions on Networking* 14(2):289-301.
- Identifier: DOI 10.1109/tnet.2006.872553; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here. Title indicates a dynamic-game model of Wi-Fi access-point pricing.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Hotspot pricing precedent (verify contents).

### ma2017economic
Ma, Q., Gao, L., Liu, Y.-F., Huang, J. (2017). Economic analysis of crowdsourced wireless community networks. *IEEE Transactions on Mobile Computing* 16(7):1856-1869.
- Identifier: DOI 10.1109/tmc.2016.2606390 (Crossref); arXiv:1608.08744 (abstract read).
- Read scope: abstract_only.
- Summary: Two-layer Stackelberg model: operator sets pricing, users decide Wi-Fi sharing; analyses user membership/access games in small and large networks and designs a partial price-differentiation scheme.
- F1 no; F2 no; F3 yes; F4 no; F5 partial.
- Relevance: Crowdsourced Wi-Fi pricing with differentiated plans.

### B. Fair division, mechanism design without money, dynamic allocation

### ghodsi2011dominant
Ghodsi, A., Zaharia, M., Hindman, B., Konwinski, A., Shenker, S., Stoica, I. (2011). Dominant resource fairness: fair allocation of multiple resource types. In *8th USENIX Symposium on Networked Systems Design and Implementation (NSDI 11)*.
- Identifier: USENIX page https://www.usenix.org/conference/nsdi11/dominant-resource-fairness-fair-allocation-multiple-resource-types (citation meta tags read; page numbers not in tags, omitted).
- Read scope: metadata_only.
- Summary: Not read here. Introduced DRF for multi-resource allocation (title); its fairness/strategyproofness properties are described via Kash et al. and Parkes et al. below, not from this paper.
- F1 no (static; per Kash et al.); F2 n.r.; F3 no; F4 yes; F5 yes (per Kash et al. intro, which cites DRF's game-theoretic properties).
- Relevance: Static baseline for multi-resource fairness.

### parkes2015beyond
Parkes, D. C., Procaccia, A. D., Shah, N. (2015). Beyond dominant resource fairness: extensions, limitations, and indivisibilities. *ACM Transactions on Economics and Computation* 3(1):Article 3, 1-22. (EC 2012 version: DOI 10.1145/2229012.2229075, pp. 808-825.)
- Identifier: DOI 10.1145/2739040; confirmed via Crossref.
- Read scope: abstract_only.
- Summary: Studies multi-resource allocation with Leontief preferences, extending DRF (the abstract, as retrieved, covers the motivation and DRF background; the remaining results were not read).
- F1 no; F2 partial (Leontief); F3 no; F4 yes; F5 yes (per abstract context; details not read).
- Relevance: Extensions and limits of DRF.

### bei2026fair
Bei, X., Li, Z., Luo, J. (2026). Fair and efficient multi-resource allocation for cloud computing: beyond dominant resource fairness. *Mathematics of Operations Research* (published online 2026-02-11).
- Identifier: DOI 10.1287/moor.2024.0714; confirmed via Crossref.
- Read scope: abstract_only (partial).
- Summary: Allocation of multiple resource types under Leontief preferences; introduces a "fair-ratio" measure comparing optimal welfare/utilisation among fair allocations with that of the mechanism, to bypass DRF's poor welfare approximation lower bounds.
- F1 no; F2 partial; F3 no; F4 yes; F5 partial (DRF properties stated as background).
- Relevance: Recent (2026) fairness-efficiency result in DRF family.

### joewong2013multiresource
Joe-Wong, C., Sen, S., Lan, T., Chiang, M. (2013). Multiresource allocation: fairness-efficiency tradeoffs in a unifying framework. *IEEE/ACM Transactions on Networking* 21(6):1785-1798.
- Identifier: DOI 10.1109/tnet.2012.2233213; confirmed via Crossref (INFOCOM 2012: DOI 10.1109/infcom.2012.6195481).
- Read scope: metadata_only.
- Summary: Not read here (title only).
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Networking-side multi-resource fairness.

### bonald2015multi
Bonald, T., Roberts, J. (2015). Multi-resource fairness: objectives, algorithms and performance. (Crossref title: "Multi-Resource Fairness".) In *Proc. 2015 ACM SIGMETRICS*, pp. 31-42.
- Identifier: DOI 10.1145/2745844.2745869; confirmed via Crossref. The title in the record is "Multi-Resource Fairness"; the longer subtitle is from memory.
- Read scope: metadata_only.
- Summary: Not read here.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Candidate for fairness with flow-level dynamics (check content).

### kash2014no
Kash, I., Procaccia, A. D., Shah, N. (2014). No agent left behind: dynamic fair division of multiple resources. *Journal of Artificial Intelligence Research* 51:579-603.
- Identifier: DOI 10.1613/jair.4405; JAIR article 10917 (open PDF).
- Read scope: full_text (abstract, introduction, model section 2, axioms, Theorems 3, 4, 11 statements and proof outlines; experiments not read in detail).
- Summary: Agents arrive over time (they do not depart) with Leontief demands; allocations are irrevocable and the number of agents n is known to the mechanism in advance. Properties: sharing incentives (SI), strategyproofness (SP), dynamic Pareto optimality (DPO), envy-freeness (EF), dynamic EF (DEF). Theorem 3: EF and DPO are incompatible (n >= 3, m >= 2). Theorem 4: DYNAMIC DRF satisfies SI, DEF, DPO and SP. Theorem 11: CAUTIOUS LP satisfies SI, EF, cautious DPO and SP.
- F1 partial (arrivals only, no departures, n known); F2 partial (Leontief, fixed demands); F3 no; F4 yes (SI, EF/DEF); F5 yes (SP; demands fixed at arrival).
- Relevance: Cleanest axiomatic treatment of envy-freeness versus efficiency under arrivals; the irrevocability assumption is what makes SP easy and is unavailable if we want to defer users.

### friedman2015dynamic
Friedman, E., Psomas, C.-A., Vardi, S. (2015). Dynamic fair division with minimal disruptions. In *Proc. 16th ACM Conference on Economics and Computation (EC '15)*, pp. 697-713.
- Identifier: DOI 10.1145/2764468.2764495; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read; journal version below (vardi2022dynamic) read at abstract level.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Conference version of vardi2022dynamic.

### vardi2022dynamic
Vardi, S., Psomas, A., Friedman, E. (2022). Dynamic fair resource division. *Mathematics of Operations Research* 47(2):945-968.
- Identifier: DOI 10.1287/moor.2021.1155; confirmed via Crossref. Author order and the name "Alexandros" are as in the Crossref record (EC'15 lists Christos-Alexandros Psomas first-name form).
- Read scope: abstract_only.
- Summary: A single homogeneous resource shared among users who arrive and depart; ideal allocations exist for any fixed number of users but implementing them requires adjusting everyone on each arrival. The paper limits the number of users disrupted per arrival and studies the fairness versus number-of-disruptions trade-off.
- F1 yes; F2 no (single homogeneous resource); F3 no; F4 yes; F5 no (per abstract).
- Relevance: Churn with arrivals/departures and fairness; relevant to how many devices' rates we may change per event.

### freeman2018dynamic
Freeman, R., Zahedi, S. M., Conitzer, V., Lee, B. C. (2018). Dynamic proportional sharing: a game-theoretic approach. *Proceedings of the ACM on Measurement and Analysis of Computing Systems* 2(1):Article 3, 1-36.
- Identifier: DOI 10.1145/3179406; confirmed via Crossref; PDF read from Duke site.
- Read scope: full_text (abstract, preliminaries, property definitions, theorem statements; proofs not read).
- Summary: Fixed set of n agents with endowments, R rounds; per-round utility is H per unit up to demand and L per unit beyond. Shows dynamic max-min violates sharing incentives (Thm 5) and strategyproofness (Thm 6); with L>0 no dynamic mechanism achieves SP and efficiency (Thm 10) or alpha-SI and efficiency (Thm 9). Flexible lending (FL) is SP (Thm 21), gives at least half of static utility (Thm 22/24) and an asymptotic efficiency guarantee under i.i.d. symmetric demands (Thm 25); the T-period mechanism is SP and guarantees entitlements.
- F1 no (fixed agents); F2 partial (two-level utility, single resource); F3 no; F4 partial (entitlements/sharing incentives); F5 yes (SP without money via lending/borrowing across rounds).
- Relevance: A payment-free SP mechanism where deferral is repaid later (lending); its impossibility results bound what we can promise.

### cole2013mechanism
Cole, R., Gkatzelis, V., Goel, G. (2013). Mechanism design for fair division: allocating divisible items without payments. In *Proc. 14th ACM Conference on Electronic Commerce (EC '13)*, pp. 251-268. (arXiv:1212.1522.)
- Identifier: DOI 10.1145/2482540.2482582 (Crossref); arXiv:1212.1522v3 (full text downloaded).
- Read scope: abstract and introduction read; theorem statements skimmed (sections 3.x partially); proofs not read.
- Summary: Uses proportional fairness as benchmark and designs truthful mechanisms without payments: for homogeneous valuations a truthful mechanism gives every agent at least 1/e of her proportionally fair valuation; no truthful mechanism can guarantee more than 0.5 even for additive linear valuations. Truthfulness is achieved by discarding a carefully chosen fraction of resources.
- F1 no; F2 partial (additive, Leontief and other classes); F3 no; F4 yes; F5 yes.
- Relevance: Shows the efficiency price (wasted resource) of truthful, payment-free fair division; static.

### gorokh2021monetary
Gorokh, A., Banerjee, S., Iyer, K. (2021). From monetary to nonmonetary mechanism design via artificial currencies. *Mathematics of Operations Research* 46(3):835-855. (EC 2017 abstract: DOI 10.1145/3033274.3085140.)
- Identifier: DOI 10.1287/moor.2020.1098; confirmed via Crossref.
- Read scope: abstract_only.
- Summary: For repeated allocation, gives two black-box constructions turning any one-shot monetary mechanism into a dynamic nonmonetary mechanism with an artificial currency, with vanishing gains from non-truthful reporting over time and vanishing performance loss; for two agents a particular mechanism has vanishing price of anarchy.
- F1 no (per abstract); F2 partial (general allocation setting); F3 no; F4 partial; F5 yes (asymptotic IC).
- Relevance: Theoretical template for replacing payments by a currency in a repeated game.

### budish2011combinatorial
Budish, E. (2011). The combinatorial assignment problem: approximate competitive equilibrium from equal incomes. *Journal of Political Economy* 119(6):1061-1103.
- Identifier: DOI 10.1086/664613; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here (pseudo-market with equal artificial incomes, as per title).
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Pseudo-market reference.

### prendergast2022allocation
Prendergast, C. (2022). The allocation of food to food banks. *Journal of Political Economy* 130(8):1993-2017.
- Identifier: DOI 10.1086/720332; confirmed via Crossref.
- Read scope: metadata_only.
- Summary: Not read here.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Real-world artificial-currency allocation (background only; read before use).

### azevedo2019strategy
Azevedo, E. M., Budish, E. (2019). Strategy-proofness in the large. *Review of Economic Studies* (published online 2018-08-07).
- Identifier: DOI 10.1093/restud/rdy042 (Crossref; volume/pages not in the record); full text read from NBER Working Paper w23771 (2017).
- Read scope: full_text of NBER working paper (abstract, introduction, Definition 5-6 on envy-freeness, Theorem 1 statement; proofs and later sections not read).
- Summary: Defines strategy-proofness in the large (SP-L): truthful reporting is approximately optimal in large markets, evaluated ex interim against all full-support i.i.d. distributions of others' reports. Theorem 1: if a mechanism is envy-free (or envy-free but for tie-breaking, EF-TB) then it is SP-L. Theorem 2: Bayes-Nash-implementable outcomes can be approximated by SP-L mechanisms.
- F1 no; F2 partial (general); F3 no; F4 yes (envy-freeness); F5 yes (approximate IC).
- Relevance: Justifies using envy-freeness between classes as an approximate-IC route in a population of many devices.

### vuppalapati2023karma
Vuppalapati, M., Fikioris, G., Agarwal, R., Cidon, A., Khandelwal, A., Tardos, E. (2023). Karma: resource allocation for dynamic demands. In *17th USENIX Symposium on Operating Systems Design and Implementation (OSDI 23)*. (arXiv:2305.17222.)
- Identifier: USENIX page https://www.usenix.org/conference/osdi23/presentation/vuppalapati (meta tags read; page numbers not in tags); arXiv:2305.17222v2 (full version with proofs).
- Read scope: full_text for abstract, introduction, section 2 (motivation), section 3.1-3.4 (guarantees, churn paragraph); appendix proofs only skimmed (lemma statements).
- Summary: Single elastic resource, n users with dynamic demands, per-quantum allocation. Users donate unused share and earn credits; borrowers spend credits, and prioritisation uses credits. Theorem 1: Pareto efficient per quantum. Theorem 2: online strategy-proof (a user cannot gain in quantum q by lying in q, given honest history). A user with perfect knowledge of others' future demands can still gain by a small constant factor (at most 1.5x) by under-reporting; with imprecise knowledge she can lose by Omega(n). Theorem 3: no group of colluding users gains. Theorem 4: given past allocations, Karma yields an optimally fair allocation. All theoretical results are stated for guaranteed fraction alpha = 0 (alpha > 0 left open) and assume enough initial credits that no one runs out. Churn: a joiner receives the average credit balance of existing users and the fair share is rescaled (a mechanism rule, not analysed as theorem in the portions I read).
- F1 partial (join/leave rule, theory for fixed n as far as read); F2 no (utility = useful allocation, no QoS classes); F3 no; F4 yes (long-term fairness); F5 yes (online SP, group-SP; no money).
- Relevance: Closest working example of credit-compensated deferral with IC and fairness guarantees; limited to one resource, a single user type, and alpha = 0.

### elokda2023selfcontained
Elokda, E., Bolognani, S., Censi, A., Dörfler, F., Frazzoli, E. (2023). A self-contained karma economy for the dynamic allocation of common resources. *Dynamic Games and Applications*. DOI 10.1007/s13235-023-00503-0. (arXiv:2207.00495.)
- Identifier: Crossref DOI 10.1007/s13235-023-00503-0; arXiv:2207.00495v3 (journal_ref and DOI in arXiv record).
- Read scope: abstract, introduction, model (section 3 up to assumptions) read; numerical results and proofs not read.
- Summary: Repeated allocation of a scarce resource among a large population where two random agents compete each round by bidding non-tradable karma. Modelled as a dynamic population game; existence of a stationary Nash equilibrium is guaranteed; efficiency and ex-post fairness are analysed numerically at equilibrium for homogeneous agents, with robustness to heterogeneity and redistribution remedies. The abstract lists "admitting internet content to a regulated fast channel" as an example.
- F1 partial (large-population model; continuing matching, no arrival/departure analysis read); F2 partial (time-varying urgency types); F3 no; F4 yes; F5 partial (equilibrium incentives, not dominant-strategy truthfulness).
- Relevance: Equilibrium-based payment-free priority via karma; mentions fast-channel use.

### elokda2025carma
Elokda, E., Cenedese, C., Zhang, K., Censi, A., Lygeros, J., Frazzoli, E., Dörfler, F. (2025). CARMA: fair and efficient bottleneck congestion management via nontradable karma credits. *Transportation Science* 59(2):340-359. (arXiv:2208.07113.)
- Identifier: DOI 10.1287/trsc.2023.0323 (Crossref); arXiv:2208.07113v2 (full text downloaded).
- Read scope: abstract, introduction and theorem/proposition statements located; proofs and numerics not read.
- Summary: A bottleneck split into a congestion-free fast lane and a congested slow lane; commuters with heterogeneous, dynamically varying value of time bid non-tradable karma for the fast lane, karma is redistributed each day. Modelled as a dynamic population game; Proposition 1: a stationary Nash equilibrium exists; Proposition 2: equitable w.r.t. heterogeneous income classes; Proposition 4: strong Pareto improvement over no intervention (under stated assumptions); numerically matches optimal tolling's congestion reduction.
- F1 partial (population game, day-by-day repetition); F2 yes (heterogeneous urgency/VOT); F3 no; F4 yes (equity across classes); F5 partial (equilibrium, non-tradable currency).
- Relevance: Two service lanes (priority vs delay) allocated by non-monetary credits with fairness across heterogeneous classes; structurally the closest analogue to real-time vs delay-tolerant classes.

### elokda2026dynamic
Elokda, E., Bolognani, S., Dörfler, F., Nax, H. H. (2026). Dynamic resource allocation with karma: an experimental study. *Journal of Economic Behavior & Organization* 251:107771.
- Identifier: DOI 10.1016/j.jebo.2026.107771 (Crossref); arXiv:2404.02687v5 (abstract and journal ref read).
- Read scope: abstract_only.
- Summary: MTurk experiment where subjects repeatedly bid non-tradable credits according to time-varying urgency; karma achieves an almost Pareto improvement over random allocation even though subjects deviate from the theoretical Nash bidding policy.
- F1 no; F2 partial (urgency); F3 no; F4 partial; F5 partial (behavioural evidence).
- Relevance: Empirical support that humans use credit-based priority sensibly.

### riehl2024resource
Riehl, K., Kouvelas, A., Makridis, M. (2024). Resource allocation with karma mechanisms. *Economies* 12(8):211.
- Identifier: DOI 10.3390/economies12080211; arXiv:2406.14728 (record read, journal_ref and DOI listed there). Not checked in Crossref.
- Read scope: abstract_only.
- Summary: Review of the scattered karma literature: non-tradeable, resource-inherent currency; characterised in the abstract as embodying fairness, near incentive compatibility, Pareto efficiency and robustness to population heterogeneity.
- F1 no; F2 no; F3 no; F4 yes; F5 partial.
- Relevance: Entry point to the karma literature.

### lin2025online
Lin, D. X., Hall, D., Fikioris, G., Banerjee, S., Tardos, E. (2025). Online resource sharing: better robust guarantees via randomized strategies. arXiv:2505.13824 (preprint).
- Identifier: arXiv:2505.13824v2 (arXiv API; full text downloaded).
- Read scope: abstract, introduction, model and theorem statements (1-3); proofs not read.
- Summary: Repeated allocation of a single resource to one of n agents without money, via repeated first-price auction with artificial currency (budget alpha_i T). A randomized bidding strategy guarantees each agent a (2 - sqrt 2) ~ 0.59 fraction of her ideal utility regardless of others' behaviour (Thm 1); static bidding cannot exceed 0.6 (Thm 2); an adversarial strategy bounds any agent at 1 - 1/e (Thm 3 as stated in intro). Prior 1/2 robustness holds for pseudo-markets and dynamic max-min.
- F1 no; F2 partial (value distributions); F3 no; F4 yes (fair-share-based ideal utility); F5 partial (robustness guarantees, not IC).
- Relevance: Sets the current benchmark for payment-free long-run guarantees under arbitrary strategic behaviour (about 0.59 vs 1/e hardness).

### onyeze2025dynamic
Onyeze, C., Lin, D. X., Banerjee, S., Tardos, E. (2025). Dynamic allocation of public goods with approximate core equilibria. arXiv:2511.04817 (preprint).
- Identifier: arXiv:2511.04817v1 (arXiv API).
- Read scope: abstract_only.
- Summary: Repeated online allocation of shareable public goods without money, with global constraints on selected goods (submodular cost) and i.i.d. possibly correlated values; mechanisms use an artificial currency with budgets proportional to fair share.
- F1 no; F2 partial; F3 partial (global constraints on the principal); F4 yes; F5 partial.
- Relevance: Non-monetary online mechanism with principal-side global constraints.

### benade2024fair
Benadè, G., Kazachkov, A. M., Procaccia, A. D., Psomas, A., Zeng, D. (2024). Fair and efficient online allocations. *Operations Research* 72(4):1438-1452. (Earlier: "How to make envy vanish over time", EC 2018, DOI 10.1145/3219166.3219179.)
- Identifier: DOI 10.1287/opre.2022.0332; confirmed via Crossref.
- Read scope: abstract_only (Crossref summary describes the food rescue motivation).
- Summary: Online allocation of unpredictable, perishable donations with immediate irrevocable decisions; studies trade-offs between efficiency and equitable treatment of organisations.
- F1 yes (arrivals); F2 partial; F3 no; F4 yes; F5 no.
- Relevance: Envy over time in online allocation (no strategic users).

### sinclair2023sequential
Sinclair, S. R., Jain, G., Banerjee, S., Yu, C. L. (2023). Sequential fair allocation: achieving the optimal envy-efficiency trade-off curve. *Operations Research* 71(5):1689-1705.
- Identifier: DOI 10.1287/opre.2022.2397 (Crossref); arXiv:2105.05308v3 (full text downloaded, abstract read).
- Read scope: abstract_only.
- Summary: Divides limited resources among individuals arriving over T rounds with random counts; shows envy-freeness and efficiency are in contention online: additive counterfactual envy up to LT forces efficiency loss of at least 1/LT; the Guarded-Hope threshold algorithm attains any point on this frontier.
- F1 yes; F2 partial (multiple types/resources); F3 no; F4 yes (envy); F5 no.
- Relevance: Quantifies the cost of fairness under uncertain future arrivals (shared-uncertainty analogue).

### zeng2020fairness
Zeng, D., Psomas, A. (2020). Fairness-efficiency tradeoffs in dynamic fair division. In *Proc. ACM EC 2020*. arXiv:1907.11672.
- Identifier: arXiv:1907.11672v2 (arXiv record: comment states acceptance at EC 2020; no DOI checked).
- Read scope: abstract_only.
- Summary: Indivisible items arrive over time and are allocated irrevocably to n agents; studies tradeoffs between envy and efficiency (adversarial vs i.i.d. values).
- F1 yes; F2 no; F3 no; F4 yes; F5 no.
- Relevance: Further envy-over-time bounds.

### pavan2014dynamic
Pavan, A., Segal, I., Toikka, J. (2014). Dynamic mechanism design: a Myersonian approach. *Econometrica* 82(2):601-653.
- Identifier: DOI 10.3982/ecta10269; confirmed via Crossref (author list missing in record, so authors given from the SSRN working-paper record 10.2139/ssrn.1620662).
- Read scope: metadata_only.
- Summary: Not read here.
- F1 n.r.; F2 n.r.; F3 n.r.; F4 n.r.; F5 n.r.
- Relevance: Standard reference for IC in dynamic settings with monetary transfers (contrast with payment-free scheme).

## 3. BibTeX

```bibtex
@article{kelly1998rate,
  author = {Kelly, F. P. and Maulloo, A. K. and Tan, D. K. H.},
  title = {Rate control for communication networks: shadow prices, proportional fairness and stability},
  journal = {Journal of the Operational Research Society},
  year = {1998}, volume = {49}, number = {3}, pages = {237--252},
  doi = {10.1057/palgrave.jors.2600523}
}
@article{kelly1997charging,
  author = {Kelly, Frank},
  title = {Charging and rate control for elastic traffic},
  journal = {European Transactions on Telecommunications},
  year = {1997}, volume = {8}, number = {1}, pages = {33--37},
  doi = {10.1002/ett.4460080106}
}
@article{johari2004efficiency,
  author = {Johari, Ramesh and Tsitsiklis, John N.},
  title = {Efficiency Loss in a Network Resource Allocation Game},
  journal = {Mathematics of Operations Research},
  year = {2004}, volume = {29}, number = {3}, pages = {407--435},
  doi = {10.1287/moor.1040.0091}
}
@article{cocchi1993pricing,
  author = {Cocchi, R. and Shenker, S. and Estrin, D. and Zhang, L.},
  title = {Pricing in computer networks: motivation, formulation, and example},
  journal = {IEEE/ACM Transactions on Networking},
  year = {1993}, volume = {1}, number = {6}, pages = {614--627},
  doi = {10.1109/90.266050}
}
@article{shenker1995fundamental,
  author = {Shenker, S.},
  title = {Fundamental design issues for the future {I}nternet},
  journal = {IEEE Journal on Selected Areas in Communications},
  year = {1995}, volume = {13}, number = {7}, pages = {1176--1188},
  doi = {10.1109/49.414637}
}
@article{gibbens2000internet,
  author = {Gibbens, R. and Mason, R. and Steinberg, R.},
  title = {Internet service classes under competition},
  journal = {IEEE Journal on Selected Areas in Communications},
  year = {2000}, volume = {18}, number = {12}, pages = {2490--2498},
  doi = {10.1109/49.898732}
}
@article{marbach2003priority,
  author = {Marbach, P.},
  title = {Priority service and max-min fairness},
  journal = {IEEE/ACM Transactions on Networking},
  year = {2003}, volume = {11}, number = {5}, pages = {733--746},
  doi = {10.1109/tnet.2003.818196}
}
@inproceedings{odlyzko1999paris,
  author = {Odlyzko, Andrew},
  title = {Paris Metro pricing for the {I}nternet},
  booktitle = {Proceedings of the 1st ACM Conference on Electronic Commerce},
  year = {1999}, pages = {140--147},
  doi = {10.1145/336992.337030}
}
@article{chau2014economic,
  author = {Chau, Chi-Kin and Wang, Qian and Chiu, Dah-Ming},
  title = {Economic Viability of {P}aris {M}etro {P}ricing for Digital Services},
  journal = {ACM Transactions on Internet Technology},
  year = {2014}, volume = {14}, number = {2--3}, pages = {1--21},
  doi = {10.1145/2663492}
}
@article{sen2013survey,
  author = {Sen, Soumya and Joe-Wong, Carlee and Ha, Sangtae and Chiang, Mung},
  title = {A survey of smart data pricing},
  journal = {ACM Computing Surveys},
  year = {2013}, volume = {46}, number = {2}, pages = {1--37},
  doi = {10.1145/2543581.2543582}
}
@article{ha2012tube,
  author = {Ha, Sangtae and Sen, Soumya and Joe-Wong, Carlee and Im, Youngbin and Chiang, Mung},
  title = {{TUBE}},
  journal = {ACM SIGCOMM Computer Communication Review},
  year = {2012}, volume = {42}, number = {4}, pages = {247--258},
  doi = {10.1145/2377677.2377723}
}
@article{mendelson1990optimal,
  author = {Mendelson, Haim and Whang, Seungjin},
  title = {Optimal Incentive-Compatible Priority Pricing for the {M/M/1} Queue},
  journal = {Operations Research},
  year = {1990}, volume = {38}, number = {5}, pages = {870--883},
  doi = {10.1287/opre.38.5.870}
}
@article{afeche2004pricing,
  author = {Af{\`e}che, Philipp and Mendelson, Haim},
  title = {Pricing and Priority Auctions in Queueing Systems with a Generalized Delay Cost Structure},
  journal = {Management Science},
  year = {2004}, volume = {50}, number = {7}, pages = {869--882},
  doi = {10.1287/mnsc.1030.0156}
}
@article{afeche2013incentive,
  author = {Af{\`e}che, Philipp},
  title = {Incentive-Compatible Revenue Management in Queueing Systems: Optimal Strategic Delay},
  journal = {Manufacturing \& Service Operations Management},
  year = {2013}, volume = {15}, number = {3}, pages = {423--443},
  doi = {10.1287/msom.2013.0449}
}
@inproceedings{basar2002revenue,
  author = {Basar, T. and Srikant, R.},
  title = {Revenue-maximizing pricing and capacity expansion in a many-users regime},
  booktitle = {Proceedings of IEEE INFOCOM 2002},
  year = {2002}, volume = {1}, pages = {294--301},
  doi = {10.1109/infcom.2002.1019271}
}
@inproceedings{hande2010pricing,
  author = {Hande, Prashanth and Chiang, Mung and Calderbank, Robert and Zhang, Junshan},
  title = {Pricing under Constraints in Access Networks: Revenue Maximization and Congestion Management},
  booktitle = {Proceedings of IEEE INFOCOM 2010},
  year = {2010}, pages = {1--9},
  doi = {10.1109/infcom.2010.5461954}
}
@article{yang2007vcg,
  author = {Yang, Sichao and Hajek, Bruce},
  title = {{VCG-Kelly} Mechanisms for Allocation of Divisible Goods: Adapting {VCG} Mechanisms to One-Dimensional Signals},
  journal = {IEEE Journal on Selected Areas in Communications},
  year = {2007}, volume = {25}, number = {6}, pages = {1237--1243},
  doi = {10.1109/jsac.2007.070817}
}
@article{economides2012economics,
  author = {Economides, Nicholas and Hermalin, Benjamin E.},
  title = {The economics of network neutrality},
  journal = {The RAND Journal of Economics},
  year = {2012}, volume = {43}, number = {4}, pages = {602--629},
  doi = {10.1111/1756-2171.12001}
}
@article{njoroge2014investment,
  author = {Njoroge, Paul and Ozdaglar, Asuman and Stier-Moses, Nicol{\'a}s E. and Weintraub, Gabriel Y.},
  title = {Investment in Two-Sided Markets and the Net Neutrality Debate},
  journal = {Review of Network Economics},
  year = {2014}, volume = {12}, number = {4},
  doi = {10.1515/rne-2012-0017}
}
@misc{naghizadeh2020paid,
  author = {Naghizadeh, Parinaz and Joe-Wong, Carlee and Chiang, Mung},
  title = {Paid Prioritization with Content Competition},
  year = {2020}, eprint = {2007.14574}, archivePrefix = {arXiv}
}
@article{yu2017public,
  author = {Yu, Haoran and Cheung, Man Hon and Gao, Lin and Huang, Jianwei},
  title = {Public {Wi-Fi} Monetization via Advertising},
  journal = {IEEE/ACM Transactions on Networking},
  year = {2017}, volume = {25}, number = {4}, pages = {2110--2121},
  doi = {10.1109/tnet.2017.2675944}
}
@article{musacchio2006wifi,
  author = {Musacchio, J. and Walrand, J.},
  title = {{WiFi} access point pricing as a dynamic game},
  journal = {IEEE/ACM Transactions on Networking},
  year = {2006}, volume = {14}, number = {2}, pages = {289--301},
  doi = {10.1109/tnet.2006.872553}
}
@article{ma2017economic,
  author = {Ma, Qian and Gao, Lin and Liu, Ya-Feng and Huang, Jianwei},
  title = {Economic Analysis of Crowdsourced Wireless Community Networks},
  journal = {IEEE Transactions on Mobile Computing},
  year = {2017}, volume = {16}, number = {7}, pages = {1856--1869},
  doi = {10.1109/tmc.2016.2606390}
}
@inproceedings{ghodsi2011dominant,
  author = {Ghodsi, Ali and Zaharia, Matei and Hindman, Benjamin and Konwinski, Andy and Shenker, Scott and Stoica, Ion},
  title = {Dominant Resource Fairness: Fair Allocation of Multiple Resource Types},
  booktitle = {8th USENIX Symposium on Networked Systems Design and Implementation (NSDI 11)},
  year = {2011},
  url = {https://www.usenix.org/conference/nsdi11/dominant-resource-fairness-fair-allocation-multiple-resource-types}
}
@article{parkes2015beyond,
  author = {Parkes, David C. and Procaccia, Ariel D. and Shah, Nisarg},
  title = {Beyond Dominant Resource Fairness: Extensions, Limitations, and Indivisibilities},
  journal = {ACM Transactions on Economics and Computation},
  year = {2015}, volume = {3}, number = {1}, pages = {1--22},
  doi = {10.1145/2739040}
}
@article{bei2026fair,
  author = {Bei, Xiaohui and Li, Zihao and Luo, Junjie},
  title = {Fair and Efficient Multi-resource Allocation for Cloud Computing: Beyond Dominant Resource Fairness},
  journal = {Mathematics of Operations Research},
  year = {2026}, doi = {10.1287/moor.2024.0714}
}
@article{joewong2013multiresource,
  author = {Joe-Wong, Carlee and Sen, Soumya and Lan, Tian and Chiang, Mung},
  title = {Multiresource Allocation: Fairness--Efficiency Tradeoffs in a Unifying Framework},
  journal = {IEEE/ACM Transactions on Networking},
  year = {2013}, volume = {21}, number = {6}, pages = {1785--1798},
  doi = {10.1109/tnet.2012.2233213}
}
@inproceedings{bonald2015multi,
  author = {Bonald, Thomas and Roberts, James},
  title = {Multi-Resource Fairness},
  booktitle = {Proceedings of the 2015 ACM SIGMETRICS International Conference on Measurement and Modeling of Computer Systems},
  year = {2015}, pages = {31--42},
  doi = {10.1145/2745844.2745869}
}
@article{kash2014no,
  author = {Kash, Ian and Procaccia, Ariel D. and Shah, Nisarg},
  title = {No Agent Left Behind: Dynamic Fair Division of Multiple Resources},
  journal = {Journal of Artificial Intelligence Research},
  year = {2014}, volume = {51}, pages = {579--603},
  doi = {10.1613/jair.4405}
}
@inproceedings{friedman2015dynamic,
  author = {Friedman, Eric and Psomas, Christos-Alexandros and Vardi, Shai},
  title = {Dynamic Fair Division with Minimal Disruptions},
  booktitle = {Proceedings of the 16th ACM Conference on Economics and Computation},
  year = {2015}, pages = {697--713},
  doi = {10.1145/2764468.2764495}
}
@article{vardi2022dynamic,
  author = {Vardi, Shai and Psomas, Alexandros and Friedman, Eric},
  title = {Dynamic Fair Resource Division},
  journal = {Mathematics of Operations Research},
  year = {2022}, volume = {47}, number = {2}, pages = {945--968},
  doi = {10.1287/moor.2021.1155}
}
@article{freeman2018dynamic,
  author = {Freeman, Rupert and Zahedi, Seyed Majid and Conitzer, Vincent and Lee, Benjamin C.},
  title = {Dynamic Proportional Sharing: A Game-Theoretic Approach},
  journal = {Proceedings of the ACM on Measurement and Analysis of Computing Systems},
  year = {2018}, volume = {2}, number = {1}, pages = {1--36},
  doi = {10.1145/3179406}
}
@inproceedings{cole2013mechanism,
  author = {Cole, Richard and Gkatzelis, Vasilis and Goel, Gagan},
  title = {Mechanism design for fair division: allocating divisible items without payments},
  booktitle = {Proceedings of the 14th ACM Conference on Electronic Commerce},
  year = {2013}, pages = {251--268},
  doi = {10.1145/2482540.2482582}
}
@article{gorokh2021monetary,
  author = {Gorokh, Artur and Banerjee, Siddhartha and Iyer, Krishnamurthy},
  title = {From Monetary to Nonmonetary Mechanism Design via Artificial Currencies},
  journal = {Mathematics of Operations Research},
  year = {2021}, volume = {46}, number = {3}, pages = {835--855},
  doi = {10.1287/moor.2020.1098}
}
@article{budish2011combinatorial,
  author = {Budish, Eric},
  title = {The Combinatorial Assignment Problem: Approximate Competitive Equilibrium from Equal Incomes},
  journal = {Journal of Political Economy},
  year = {2011}, volume = {119}, number = {6}, pages = {1061--1103},
  doi = {10.1086/664613}
}
@article{prendergast2022allocation,
  author = {Prendergast, Canice},
  title = {The Allocation of Food to Food Banks},
  journal = {Journal of Political Economy},
  year = {2022}, volume = {130}, number = {8}, pages = {1993--2017},
  doi = {10.1086/720332}
}
@article{azevedo2019strategy,
  author = {Azevedo, Eduardo M. and Budish, Eric},
  title = {Strategy-proofness in the Large},
  journal = {The Review of Economic Studies},
  year = {2019}, note = {Published online 2018},
  doi = {10.1093/restud/rdy042}
}
@inproceedings{vuppalapati2023karma,
  author = {Vuppalapati, Midhul and Fikioris, Giannis and Agarwal, Rachit and Cidon, Asaf and Khandelwal, Anurag and Tardos, {\'E}va},
  title = {Karma: Resource Allocation for Dynamic Demands},
  booktitle = {17th USENIX Symposium on Operating Systems Design and Implementation (OSDI 23)},
  year = {2023}, eprint = {2305.17222}, archivePrefix = {arXiv},
  url = {https://www.usenix.org/conference/osdi23/presentation/vuppalapati}
}
@article{elokda2023selfcontained,
  author = {Elokda, Ezzat and Bolognani, Saverio and Censi, Andrea and D{\"o}rfler, Florian and Frazzoli, Emilio},
  title = {A self-contained karma economy for the dynamic allocation of common resources},
  journal = {Dynamic Games and Applications},
  year = {2023}, doi = {10.1007/s13235-023-00503-0}
}
@article{elokda2025carma,
  author = {Elokda, Ezzat and Cenedese, Carlo and Zhang, Kenan and Censi, Andrea and Lygeros, John and Frazzoli, Emilio and D{\"o}rfler, Florian},
  title = {{CARMA}: Fair and Efficient Bottleneck Congestion Management via Nontradable Karma Credits},
  journal = {Transportation Science},
  year = {2025}, volume = {59}, number = {2}, pages = {340--359},
  doi = {10.1287/trsc.2023.0323}
}
@article{elokda2026dynamic,
  author = {Elokda, Ezzat and Bolognani, Saverio and D{\"o}rfler, Florian and Nax, Heinrich H.},
  title = {Dynamic resource allocation with karma: An experimental study},
  journal = {Journal of Economic Behavior \& Organization},
  year = {2026}, volume = {251}, pages = {107771},
  doi = {10.1016/j.jebo.2026.107771}
}
@article{riehl2024resource,
  author = {Riehl, Kevin and Kouvelas, Anastasios and Makridis, Michail},
  title = {Resource Allocation with Karma Mechanisms},
  journal = {Economies},
  year = {2024}, volume = {12}, number = {8}, pages = {211},
  doi = {10.3390/economies12080211}
}
@misc{lin2025online,
  author = {Lin, David X. and Hall, Daniel and Fikioris, Giannis and Banerjee, Siddhartha and Tardos, {\'E}va},
  title = {Online Resource Sharing: Better Robust Guarantees via Randomized Strategies},
  year = {2025}, eprint = {2505.13824}, archivePrefix = {arXiv}
}
@misc{onyeze2025dynamic,
  author = {Onyeze, Chido and Lin, David X. and Banerjee, Siddhartha and Tardos, {\'E}va},
  title = {Dynamic Allocation of Public Goods with Approximate Core Equilibria},
  year = {2025}, eprint = {2511.04817}, archivePrefix = {arXiv}
}
@article{benade2024fair,
  author = {Benad{\`e}, Gerdus and Kazachkov, Aleksandr M. and Procaccia, Ariel D. and Psomas, Alexandros and Zeng, David},
  title = {Fair and Efficient Online Allocations},
  journal = {Operations Research},
  year = {2024}, volume = {72}, number = {4}, pages = {1438--1452},
  doi = {10.1287/opre.2022.0332}
}
@article{sinclair2023sequential,
  author = {Sinclair, Sean R. and Jain, Gauri and Banerjee, Siddhartha and Yu, Christina Lee},
  title = {Sequential Fair Allocation: Achieving the Optimal Envy-Efficiency Trade-off Curve},
  journal = {Operations Research},
  year = {2023}, volume = {71}, number = {5}, pages = {1689--1705},
  doi = {10.1287/opre.2022.2397}
}
@misc{zeng2020fairness,
  author = {Zeng, David and Psomas, Alexandros},
  title = {Fairness-Efficiency Tradeoffs in Dynamic Fair Division},
  year = {2020}, note = {ACM EC 2020; full version},
  eprint = {1907.11672}, archivePrefix = {arXiv}
}
@article{pavan2014dynamic,
  author = {Pavan, Alessandro and Segal, Ilya and Toikka, Juuso},
  title = {Dynamic Mechanism Design: A {M}yersonian Approach},
  journal = {Econometrica},
  year = {2014}, volume = {82}, number = {2}, pages = {601--653},
  doi = {10.3982/ecta10269}
}
```

## 4. Could not verify / could not retrieve

Confirmed to exist but full text not retrievable (listed above as abstract_only/metadata_only): Mendelson-Whang 1990, Afeche 2013, Afeche-Mendelson 2004, Chau et al. 2014, Sen et al. 2013, Ha et al. 2012 (all paywalled; only Crossref abstracts read), Ghodsi et al. DRF (USENIX page metadata only; PDF not read).

Hinted or considered but NOT included (not confirmed or not searched to a primary record):
- Acemoglu and Ozdaglar, "Competition and efficiency in congested markets": Crossref returned only NBER/SSRN working-paper versions (10.3386/w11201, 10.2139/ssrn.676662); the journal version (Math. of OR 2007) was not confirmed, so excluded.
- Choi and Kim, "Net neutrality and investment incentives" (RAND J. Econ. 2010, DOI 10.1111/j.1756-2171.2010.00107.x) was confirmed in Crossref but left out for space; add if wanted.
- Jain and Walrand (Automatica 2010, DOI 10.1016/j.automatica.2010.05.013), Iosifidis et al. (IEEE Commun. Mag. 2014, DOI 10.1109/mcom.2014.6894448), Joe-Wong et al. sponsored data (INFOCOM 2015, DOI 10.1109/infocom.2015.7218528), Zhou-Zheng TRUST (INFOCOM 2009): confirmed in Crossref records but omitted (not read, peripheral).
- Bergemann-Valimaki dynamic pivot mechanism: only SSRN working papers found; not included.
- Aleksandrov-Walsh "Online fair division: a survey": Crossref lookup failed twice (tool error); not retried; arXiv has related 2006.15891 ("Monotone and Online Fair Division") which was seen but not used.
- Freemium/tiered Internet access pricing (premium vs free tier) and strategic-class-choice papers in networking, and strategyproof Wi-Fi scheduling: no confirmed source found with the queries tried (Crossref returned off-topic results). This is a gap, not evidence that none exist.
- Net-neutrality Stackelberg models other than those listed: not searched beyond the queries in the log.
- DBLP: API blocked by bot challenge; no DBLP-based verification used.

## 5. Strand synthesis

Settled. (i) Money-based incentive compatibility across delay classes in a queue is well understood: Mendelson-Whang (priority pricing, IC), Afeche (strategic delay of the patient class can be revenue-optimal), Afeche-Mendelson (priority auctions). PMP and smart-data-pricing literatures cover class self-selection and tiering (F3), but without churn or long-term guarantees. (ii) For payment-free fairness with agents arriving over time, axiomatic results exist: Kash et al. show EF and dynamic Pareto optimality are incompatible and give SP mechanisms (Dynamic DRF, Cautious LP) under irrevocable allocations and no departures; Freeman et al. give SP flexible lending with half-of-static-utility; Cole et al. show truthful payment-free allocation wastes resources (1/e vs 0.5 bounds); Sinclair et al. and Zeng-Psomas give envy-efficiency frontiers online. (iii) Envy-freeness implies strategy-proofness in the large (Azevedo-Budish, Theorem 1), which supports approximate IC in large device populations.

Open. Credit-compensated deferral is closest to Karma (Vuppalapati et al.): single resource, users differ only in demand, online SP and long-term fairness proved for alpha = 0, with a heuristic churn rule. Karma economies (Elokda et al., CARMA) give equilibrium, not dominant-strategy, guarantees; CARMA does model a fast lane vs slow lane for heterogeneous urgency, and Lin et al. give 0.59 robustness versus 1/e hardness under arbitrary behaviour. In the sources I read, none obtains IC or envy-freeness between QoS classes (real-time versus delay-tolerant, inelastic versus elastic utilities) without payments by compensating deferred users later, inside an online optimisation with long-term constraints (revenue/SLA tiers, uncertain capacity) and guarantees with churn. Not covered by any confirmed source: tier/SLA constraints combined with payment-free IC, inelastic utilities in credit mechanisms, uncertain shared capacity. This is a gap in the sources found by these queries, not a proof of absence.
