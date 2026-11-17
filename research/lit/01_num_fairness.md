# Strand 01: Network utility maximisation (NUM) and fairness

Date of search/verification: 2026-11-17.

Features tracked: F1 churn/dynamic arrivals-departures; F2 heterogeneous QoS utilities incl. inelastic/real-time; F3 tier/business constraints (SLA, revenue); F4 fairness; F5 incentive compatibility/strategic users. Coverage codes: y = yes, p = partial, n = no.

Read-scope key. `abstract_only`: I read the abstract in the primary record (Crossref or arXiv API). `full_text (sections)`: I read the named sections. `metadata_only`: I confirmed title/authors/venue/year/pages only. For `metadata_only` entries the summary is labelled "from title/metadata", reflects what the title states plus the paper's standard role in the literature, and claims no result I did not read. Feature codes for these entries are judgements from the title and should be re-checked before the paper makes any claim about them. Only Lan et al. was read beyond the abstract.

## 1. Search log

Tools: Bash+curl to the Crossref REST API (`/works?query.bibliographic=...` and `/works/<DOI>`), the arXiv export API (`id_list` and `search_query`), the Semantic Scholar graph API (abstract lookups), and WebSearch and WebFetch for discovery. DBLP was queried once (Høiland-Jørgensen) and the call failed. The proxy dropped several connections, so that item was not confirmed through DBLP.

Queries run (condensed):
- Crossref, seminal items by title+authors: Kelly/Maulloo/Tan; Kelly 1997 charging; Mo-Walrand; Lan-Kao-Chiang-Sabharwal; Bertsimas-Farias-Trichakis; Lee-Mazumdar-Shroff; Hande-Zhang-Chiang; Fazel-Chiang; Shi-Prasad-Onur-Niemegeers; Demers-Keshav-Shenker; Shreedhar-Varghese (DRR); Parekh-Gallager (GPS); Bennett-Zhang (WF2Q); Shenker 1995; Heusse et al. (802.11 anomaly); Massoulie-Roberts; Bonald-Massoulie; de Veciana-Lee-Konstantopoulos; Kushner-Whiting; Stolyar; Viswanath-Tse-Laroia; Johari-Tsitsiklis; Yang-Hajek; Palomar-Chiang; Chiang et al. layering; Mazumdar-Mason-Douligeris; Hou-Borkar-Kumar; Jiang-Sekar-Zhang (FESTIVE).
- Crossref/arXiv, recent items: Ogryczak et al. survey; Vardi-Psomas-Friedman; Kash-Procaccia-Shah; Fikioris-Agarwal-Tardos; Cayci-Gupta-Eryilmaz; Si-Salem-Iosifidis-Neglia; Sinha et al.; Liao-Gao-Kroer; Cookson-Ebadian-Shah; ElAzzouni-Ekici-Shroff; Hossfeld et al. (QoE fairness); Belmoukadam et al.; Caballero et al.; Fossati et al.; Tun et al.; Zheng-Banchs-de Veciana.
- WebSearch for discovery: "alpha-fairness survey", "QoE fairness video bandwidth allocation", "online fair allocation arrivals departures incentive compatible", "online alpha-fair regret", "network slicing sigmoidal QoE", "Wi-Fi 6 OFDMA airtime fairness", "temporal fair division", "Kelly mechanism slicing".
- arXiv API `search_query` runs with strict phrase syntax mostly returned nothing relevant. Discovery came from WebSearch, and every item was then confirmed via Crossref or the arXiv API.
- WebFetch of ar5iv for Lan et al. (full-text structure). Fetches of a Princeton PDF and IEEE Xplore returned 404/empty. Semantic Scholar returned abstracts for few IEEE items (publisher-elided).

## 2. Verified sources

### kelly1998rate
- Citation: F. P. Kelly, A. K. Maulloo, D. K. H. Tan. "Rate control for communication networks: shadow prices, proportional fairness and stability." Journal of the Operational Research Society 49(3):237-252, 1998.
- ID: DOI 10.1057/palgrave.jors.2600523 (Crossref also lists 10.1038/sj.jors.2600523 as the same record). Confirmed by Crossref bibliographic search; authors/title/venue/pages copied from the record.
- Read scope: metadata_only.
- Summary (from title/metadata): The title names the paper's topic: rate control via shadow prices, proportional fairness and stability. This is the canonical NUM/proportional-fairness reference.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Anchor citation for NUM and proportional fairness as the elastic baseline.

### kelly1997charging
- Citation: F. Kelly. "Charging and rate control for elastic traffic." European Transactions on Telecommunications 8(1):33-37, 1997.
- ID: DOI 10.1002/ett.4460080106. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): The title indicates it ties charging (pricing) to rate control for elastic traffic, which is the origin of the user-willingness-to-pay framing.
- Features: F1 n, F2 n, F3 p, F4 p, F5 p. All from the title; to be checked.
- Relevance: Early link between pricing and fair rate allocation. This is the root of our tier/revenue story.

### mo2000fair
- Citation: J. Mo, J. Walrand. "Fair end-to-end window-based congestion control." IEEE/ACM Transactions on Networking 8(5):556-567, 2000.
- ID: DOI 10.1109/90.879343. Confirmed by Crossref search and direct `/works/<DOI>` lookup.
- Read scope: metadata_only.
- Summary (from title/metadata): Title only. This is the standard reference for the (weighted) alpha-fair family that interpolates between proportional and max-min fairness; the paper's content was not read here.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Source for the alpha-fairness family we use to parametrise fairness.

### mazumdar1991fairness
- Citation: R. Mazumdar, L. G. Mason, C. Douligeris. "Fairness in network optimal flow control: optimality of product forms." IEEE Transactions on Communications 39(5):775-782, 1991.
- ID: DOI 10.1109/26.87140. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): The title indicates an analysis of fairness in optimal flow control, with product-form optimality results. It predates Kelly's work.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Early formal fairness-in-flow-control reference; historical context only.

### lan2010axiomatic
- Citation: T. Lan, D. Kao, M. Chiang, A. Sabharwal. "An Axiomatic Theory of Fairness in Network Resource Allocation." IEEE INFOCOM 2010, pp. 1-9.
- ID: DOI 10.1109/INFCOM.2010.5461911 (Crossref search hit); arXiv 0906.0557v4 (arXiv API record read).
- Read scope: abstract_only for the arXiv record, plus full_text structure via ar5iv: I saw the section headings and the axiom list/main theorem (first ~100k characters; appendix proofs not read).
- Summary: Five axioms (continuity, homogeneity, asymptotic saturation, irrelevance of partition, monotonicity) define a one-parameter family of fairness measures that contains Jain's index, entropy and the max/min ratios as special cases. The paper also factorises the alpha-fair utility into a fairness part and an efficiency part, and interprets "larger alpha is more fair". An alternative axiom set covers efficiency.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Gives a principled way to choose and report a fairness measure and to justify an alpha.

### bertsimas2011price
- Citation: D. Bertsimas, V. F. Farias, N. Trichakis. "The Price of Fairness." Operations Research 59(1):17-31, 2011.
- ID: DOI 10.1287/opre.1100.0865. Confirmed by Crossref search and the Crossref record's abstract.
- Read scope: abstract_only (first ~500 characters).
- Summary: Defines the price of fairness as the relative efficiency loss of a fair allocation versus the sum-of-utilities maximiser. Focuses on proportional fairness and max-min fairness (abstract states the focus; the bounds themselves were not read).
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: The metric for the efficiency cost of our fairness constraints.

### shenker1995fundamental
- Citation: S. Shenker. "Fundamental design issues for the future Internet." IEEE Journal on Selected Areas in Communications 13(7):1176-1188, 1995.
- ID: DOI 10.1109/49.414637. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title only. This is the standard reference for the elastic versus real-time (inelastic) traffic distinction and the utility-based service model; the argument was not read here.
- Features: F1 n, F2 p, F3 n, F4 n, F5 n.
- Relevance: Foundation for our class taxonomy (elastic vs real-time).

### lee2005nonconvex
- Citation: J.-W. Lee, R. R. Mazumdar, N. B. Shroff. "Non-convex optimization and rate control for multi-class services in the Internet." IEEE/ACM Transactions on Networking 13(4):827-840, 2005.
- ID: DOI 10.1109/TNET.2005.852876. Confirmed by Crossref search. Semantic Scholar confirms title/authors/year; abstract is publisher-elided.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates non-convex NUM with multi-class services (elastic plus non-concave utilities). Method and results were not read.
- Features: F1 n, F2 y, F3 n, F4 p, F5 n. From the title.
- Relevance: Core reference for mixed elastic/inelastic utilities with non-concave sigmoidal shapes.

### hande2007distributed
- Citation: P. Hande, S. Zhang, M. Chiang. "Distributed Rate Allocation for Inelastic Flows." IEEE/ACM Transactions on Networking 15(6):1240-1253, 2007.
- ID: DOI 10.1109/TNET.2007.896507. Confirmed by Crossref search. Semantic Scholar confirms the record; abstract elided.
- Read scope: metadata_only.
- Summary (from title/metadata): Title only. It addresses distributed rate allocation for inelastic flows. The conference version has the longer title "Distributed rate allocation for inelastic flows: optimization frameworks, optimality conditions, and optimal algorithms" (INFOCOM 2005, DOI 10.1109/INFOCOM.2005.1498551, seen in the Crossref record but not separately added).
- Features: F1 n, F2 y, F3 n, F4 p, F5 n. From the title.
- Relevance: Inelastic-flow NUM benchmark.

### fazel2005network
- Citation: M. Fazel, M. Chiang. "Network Utility Maximization With Nonconcave Utilities Using Sum-of-Squares Method." Proc. 44th IEEE Conference on Decision and Control, 2005, pp. 1867-1874.
- ID: DOI 10.1109/CDC.2005.1582432. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): The title states NUM with nonconcave utilities solved via the sum-of-squares method.
- Features: F1 n, F2 y, F3 n, F4 p, F5 n. From the title.
- Relevance: A route to solve non-concave class utilities (sigmoid/step) in the static allocation problem.

### chiang2007layering
- Citation: M. Chiang, S. H. Low, A. R. Calderbank, J. C. Doyle. "Layering as Optimization Decomposition: A Mathematical Theory of Network Architectures." Proceedings of the IEEE 95(1):255-312, 2007.
- ID: DOI 10.1109/JPROC.2006.887322. Confirmed by direct Crossref `/works/<DOI>` lookup.
- Read scope: metadata_only.
- Summary (from title/metadata): Title only. It is the standard survey-level reference for NUM and decomposition across protocol layers.
- Features: F1 n, F2 p, F3 n, F4 p, F5 n. From the title.
- Relevance: Umbrella reference for NUM as architecture.

### palomar2006tutorial
- Citation: D. P. Palomar, M. Chiang. "A tutorial on decomposition methods for network utility maximization." IEEE Journal on Selected Areas in Communications 24(8):1439-1451, 2006.
- ID: DOI 10.1109/JSAC.2006.879350. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Tutorial on decomposition (dual, primal, penalty-based) for NUM.
- Features: F1 n, F2 n, F3 n, F4 p, F5 n.
- Relevance: Algorithmic toolbox for the offline (static) benchmark.

### massoulie2002bandwidth
- Citation: L. Massoulie, J. W. Roberts. "Bandwidth sharing: objectives and algorithms." IEEE/ACM Transactions on Networking 10(3):320-328, 2002.
- ID: DOI 10.1109/TNET.2002.1012364. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says objectives and algorithms for bandwidth sharing. The same authors' "Bandwidth sharing and admission control for elastic traffic" (Telecommunication Systems 15(1-2):185-201, 2000, DOI 10.1023/A:1019138827659) also appeared in the Crossref search but is not separately added.
- Features: F1 p, F2 n, F3 n, F4 y, F5 n. From the title and its flow-level setting.
- Relevance: Flow-level view of fair sharing with arrivals; pointer into the churn literature.

### bonald2001impact
- Citation: T. Bonald, L. Massoulie. "Impact of fairness on Internet performance." ACM SIGMETRICS 2001, pp. 82-91.
- ID: DOI 10.1145/378420.378438 (also 10.1145/384268.378438 in SIGMETRICS PER 29(1)). Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says it studies how the fairness criterion affects Internet performance.
- Features: F1 p, F2 n, F3 n, F4 y, F5 n. From the title.
- Relevance: Flow-level performance under alpha-fair sharing with dynamic flows.

### deveciana2001stability
- Citation: G. de Veciana, T.-J. Lee, T. Konstantopoulos. "Stability and performance analysis of networks supporting elastic services." IEEE/ACM Transactions on Networking 9(1):2-14, 2001.
- ID: DOI 10.1109/90.909020. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates stability and performance analysis with elastic services; the foundational stochastic-stability result for flow-level churn under fair allocation.
- Features: F1 y, F2 n, F3 n, F4 y, F5 n. From the title.
- Relevance: Churn-aware stability baseline for elastic traffic.

### shi2014fairness
- Citation: H. Shi, R. V. Prasad, E. Onur, I. G. M. M. Niemegeers. "Fairness in Wireless Networks: Issues, Measures and Challenges." IEEE Communications Surveys & Tutorials 16(1):5-24, 2014.
- ID: DOI 10.1109/SURV.2013.050113.00015. Confirmed by Crossref search.
- Read scope: abstract_only (Semantic Scholar abstract, read via a summariser).
- Summary: Survey of fairness in wireless networks across energy, QoS and spectrum. It compares fairness models and reviews fairness work in power/topology control, scheduling, channel assignment, rate allocation, congestion control and routing. It also separates fairness from utility and from resource allocation, and lists open challenges.
- Features: F1 n, F2 p, F3 n, F4 y, F5 n.
- Relevance: The survey to cite for fairness measures and taxonomy in wireless settings.

### ogryczak2014fair
- Citation: W. Ogryczak, H. Luss, M. Pioro, D. Nace, A. Tomaszewski. "Fair Optimization and Networks: A Survey." Journal of Applied Mathematics 2014, article 612018, pp. 1-25.
- ID: DOI 10.1155/2014/612018. Confirmed by Crossref search and abstract.
- Read scope: abstract_only.
- Summary: Surveys fair optimisation for resource allocation in communication networks. The abstract says fair treatment does not mean equal shares because of system constraints.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n (abstract-level judgement).
- Relevance: Broad optimisation-side fairness survey for the related work.

### demers1989analysis
- Citation: A. Demers, S. Keshav, S. Shenker. "Analysis and simulation of a fair queueing algorithm." ACM SIGCOMM Computer Communication Review 19(4):1-12, 1989.
- ID: DOI 10.1145/75247.75248. Confirmed by Crossref search; abstract read from Crossref.
- Read scope: abstract_only.
- Summary: Proposes a fair queueing algorithm based on Nagle's suggestion and compares it with other congestion control by analysis and simulation. The abstract claims fair allocation of bandwidth and lower delay for sources using less than their full share.
- Features: F1 n, F2 p, F3 n, F4 y, F5 p. F5 from the abstract's incentive remark on sources; check.
- Relevance: Practical packet-level fair baseline.

### shreedhar1996efficient
- Citation: M. Shreedhar, G. Varghese. "Efficient fair queuing using deficit round-robin." IEEE/ACM Transactions on Networking 4(3):375-385, 1996.
- ID: DOI 10.1109/90.502236. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates a low-complexity fair queueing scheme (DRR).
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Implementable weighted-share baseline against which an online allocator is compared.

### parekh1993generalized
- Citation: A. K. Parekh, R. G. Gallager. "A generalized processor sharing approach to flow control in integrated services networks: the single-node case." IEEE/ACM Transactions on Networking 1(3):344-357, 1993.
- ID: DOI 10.1109/90.234856. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title: GPS for flow control in integrated-services networks, single node. Defines the ideal fluid model that WFQ approximates.
- Features: F1 n, F2 p, F3 n, F4 y, F5 n. From the title.
- Relevance: The weighted-share ideal for class/tier weights.

### heusse2003performance
- Citation: M. Heusse, F. Rousseau, G. Berger-Sabbatel, A. Duda. "Performance anomaly of 802.11b." IEEE INFOCOM 2003, vol. 2, pp. 836-843.
- ID: DOI 10.1109/INFCOM.2003.1208921. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title names the 802.11b performance anomaly, which motivates airtime-based rather than throughput-based fairness in Wi-Fi.
- Features: F1 n, F2 n, F3 n, F4 p, F5 n.
- Relevance: Explains why the shared capacity in Wi-Fi is airtime, not bits.

### hoiland2017ending
- Citation: T. Høiland-Jørgensen, M. Kazior, D. Täht, P. Hurtig, A. Brunstrom. "Ending the Anomaly: Achieving Low Latency and Airtime Fairness in WiFi." arXiv:1703.00064 (v2), 2017.
- ID: arXiv 1703.00064. Confirmed by arXiv API. The USENIX venue was not confirmed (DBLP call failed), so the entry is cited as an arXiv preprint.
- Read scope: abstract_only.
- Summary: Designs a queueing scheme that removes bufferbloat at the WiFi hop and an access-point airtime fairness scheduler that needs no client changes. The abstract says it is evaluated experimentally.
- Features: F1 n, F2 p, F3 n, F4 y, F5 n.
- Relevance: A deployed Wi-Fi airtime-fairness and low-latency baseline.

### kushner2004convergence
- Citation: H. J. Kushner, P. A. Whiting. "Convergence of Proportional-Fair Sharing Algorithms Under General Conditions." IEEE Transactions on Wireless Communications 3(4):1250-1259, 2004.
- ID: DOI 10.1109/TWC.2004.830826. Confirmed by direct Crossref lookup.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says convergence of PF sharing algorithms in cellular scheduling.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Theory for the PF scheduler used as the cellular baseline.

### stolyar2005asymptotic
- Citation: A. L. Stolyar. "On the Asymptotic Optimality of the Gradient Scheduling Algorithm for Multiuser Throughput Allocation." Operations Research 53(1):12-25, 2005.
- ID: DOI 10.1287/opre.1040.0156. Confirmed by Crossref search; abstract read.
- Read scope: abstract_only.
- Summary: N queues served by a generalized switch with random state, motivated by scheduling transmissions of data users in a time-varying wireless channel. The abstract continues to an optimality objective that I did not read.
- Features: F1 n, F2 n, F3 n, F4 y, F5 n. F4 is a judgement from the title.
- Relevance: Gradient/PF scheduler optimality for a random, uncertain channel.

### hou2009theory
- Citation: I.-H. Hou, V. Borkar, P. R. Kumar. "A Theory of QoS for Wireless." IEEE INFOCOM 2009, pp. 486-494.
- ID: DOI 10.1109/INFOCOM.2009.5061954. Confirmed by the Crossref search record (the direct `/works/<DOI>` lookup failed with a service error).
- Read scope: metadata_only.
- Summary (from title/metadata): Title only. It is the standard reference for QoS modelling with deadlines in wireless downlinks.
- Features: F1 p, F2 y, F3 n, F4 p, F5 n. From the title.
- Relevance: Delay/deadline QoS for real-time classes.

### elazzouni2020deadline
- Citation: S. ElAzzouni, E. Ekici, N. Shroff. "Is Deadline Oblivious Scheduling Efficient for Controlling Real-Time Traffic in Cellular Downlink Systems?" IEEE INFOCOM 2020, pp. 49-58.
- ID: DOI 10.1109/INFOCOM41043.2020.9155523; arXiv 2002.06474 (arXiv API abstract read).
- Read scope: abstract_only (first ~700 characters).
- Summary: Studies resource allocation for flows with hard deadlines (e.g. VR in 5G). Flow arrival and channel are unknown to the base station, so allocation is online. Reward-maximising algorithms are likely unfair, and the paper models the problem as online convex optimisation and proposes a primal-dual Deadline-Oblivious algorithm (the abstract is cut off after this).
- Features: F1 y, F2 y, F3 n, F4 p, F5 n.
- Relevance: Closest recent networking paper to online, deadline-aware, fair allocation with latency-critical flows.

### johari2004efficiency
- Citation: R. Johari, J. N. Tsitsiklis. "Efficiency Loss in a Network Resource Allocation Game." Mathematics of Operations Research 29(3):407-435, 2004.
- ID: DOI 10.1287/moor.1040.0091. Confirmed by Crossref search; abstract read.
- Read scope: abstract_only.
- Summary: Analyses a congestion game where users anticipate the effect of their actions on the price. For a single resource, aggregate utility is at least 3/4 of the maximum. It extends to a network where users pay per link and shows a related efficiency guarantee (the abstract's network statement was truncated, not read).
- Features: F1 n, F2 n, F3 p, F4 p, F5 y.
- Relevance: Strategic users and efficiency loss in Kelly-style proportional allocation.

### yang2007vcg
- Citation: S. Yang, B. Hajek. "VCG-Kelly Mechanisms for Allocation of Divisible Goods: Adapting VCG Mechanisms to One-Dimensional Signals." IEEE Journal on Selected Areas in Communications 25(6):1237-1243, 2007.
- ID: DOI 10.1109/JSAC.2007.070817. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates a mechanism for divisible-good allocation combining VCG with one-dimensional (Kelly) signalling.
- Features: F1 n, F2 n, F3 p, F4 p, F5 y. From the title.
- Relevance: Incentive-compatible-at-equilibrium allocation with scalar bids.

### jiang2014festive
- Citation: J. Jiang, V. Sekar, H. Zhang. "Improving Fairness, Efficiency, and Stability in HTTP-Based Adaptive Video Streaming With Festive." IEEE/ACM Transactions on Networking 22(1):326-340, 2014.
- ID: DOI 10.1109/TNET.2013.2291681 (conference version: CoNEXT 2012, DOI 10.1145/2413176.2413189). Confirmed by Crossref search and direct lookup.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says it improves fairness, efficiency and stability of adaptive video bitrate selection among competing players.
- Features: F1 n, F2 y, F3 n, F4 y, F5 n.
- Relevance: Fairness among adaptive video clients in a shared bottleneck.

### hossfeld2017qoe
- Citation: T. Hossfeld, L. Skorin-Kapov, P. E. Heegaard, M. Varela. "Definition of QoE Fairness in Shared Systems." IEEE Communications Letters 21(1):184-187, 2017.
- ID: DOI 10.1109/LCOMM.2016.2616342. Confirmed by Crossref search. (Crossref also lists an OSF preprint and the follow-up "A new QoE fairness index for QoE management", Quality and User Experience 3(1), 2018, DOI 10.1007/s41233-018-0017-x.)
- Read scope: metadata_only.
- Summary (from title/metadata): Title says it defines QoE fairness for shared systems.
- Features: F1 n, F2 y, F3 n, F4 y, F5 n. From the title.
- Relevance: Fairness defined on QoE rather than rate, which matches multi-class utilities.

### belmoukadam2021screen
- Citation: O. Belmoukadam, M. J. Khokhar, C. Barakat. "On accounting for screen resolution in adaptive video streaming: QoE-driven bandwidth sharing framework." International Journal of Network Management 31(1), 2021 (online 2020-07-13).
- ID: DOI 10.1002/nem.2128 (conference version CNSM 2019, DOI 10.23919/CNSM46954.2019.9012672). Confirmed by Crossref search; abstract start read.
- Read scope: abstract_only (opening lines only).
- Summary: Notes that screen resolution and network conditions drive video QoE and that earlier work linked MOS to bitrate per screen type. A web search snippet (not the paper) reports a heuristic that beats TCP-like max-min allocation by up to 20% in QoE; I did not verify that number.
- Features: F1 n, F2 y, F3 n, F4 p, F5 n.
- Relevance: QoE-driven bandwidth sharing for heterogeneous video clients.

### caballero2019network
- Citation: P. Caballero, A. Banchs, G. de Veciana, X. Costa-Perez. "Network Slicing Games: Enabling Customization in Multi-Tenant Mobile Networks." IEEE/ACM Transactions on Networking 27(2):662-675, 2019.
- ID: DOI 10.1109/TNET.2019.2895378; arXiv 1612.08446v4 (arXiv API abstract read). Confirmed by both.
- Read scope: abstract_only.
- Summary: Analyses share-constrained proportional allocation as a mechanism for network slicing so that tenants gain from sharing while customising their own users' allocation. The abstract was read only to its first sentences. A search snippet (not read in the paper) mentions price-of-anarchy and envy-freeness bounds.
- Features: F1 n, F2 p, F3 y, F4 y, F5 y.
- Relevance: Tenant/tier shares with strategic behaviour in a proportional-allocation game.

### tun2019wireless
- Citation: Y. K. Tun, N. H. Tran, D. T. Ngo, S. R. Pandey, Z. Han, C. S. Hong. "Wireless Network Slicing: Generalized Kelly Mechanism-Based Resource Allocation." IEEE Journal on Selected Areas in Communications 37(8):1794-1807, 2019.
- ID: DOI 10.1109/JSAC.2019.2927100; arXiv 1907.02182 (arXiv record: same title, authors). Confirmed by both.
- Read scope: abstract_only (opening sentences).
- Summary: Frames wireless slicing as sharing base-station resources between infrastructure providers and MVNOs, and uses a generalised Kelly mechanism. I read only the opening of the abstract.
- Features: F1 n, F2 p, F3 y, F4 p, F5 y. The F3/F5 judgements rely on the mechanism-design framing in the title; check.
- Relevance: Kelly-mechanism allocation among commercial parties.

### zheng2023constrained
- Citation: J. Zheng, A. Banchs, G. de Veciana. "Constrained Network Slicing Games: Achieving Service Guarantees and Network Efficiency." IEEE/ACM Transactions on Networking 31(6):2698-2713, 2023.
- ID: DOI 10.1109/TNET.2023.3262810. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says it combines service guarantees with efficiency in slicing games. A search snippet describes a conference version (GREET) as a Fisher-market variant with budgets and guaranteed service levels; that was not read in the paper.
- Features: F1 n, F2 p, F3 y, F4 p, F5 p.
- Relevance: Guarantee (SLA) constraints inside a market-style fair allocation.

### fossati2020multi
- Citation: F. Fossati, S. Moretti, P. Perny, S. Secci. "Multi-Resource Allocation for Network Slicing." IEEE/ACM Transactions on Networking 28(3):1311-1324, 2020.
- ID: DOI 10.1109/TNET.2020.2979667. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates multi-resource allocation for slicing. A related conference paper in the same search is "Multi-Resource Allocation for Network Slicing under Service Level Agreements" (NoF 2019, DOI 10.1109/NOF47743.2019.9014995).
- Features: F1 n, F2 p, F3 p, F4 y, F5 n. From the titles.
- Relevance: Fair multi-resource slicing with SLA flavour.

### joewong2013multi
- Citation: C. Joe-Wong, S. Sen, T. Lan, M. Chiang. "Multiresource Allocation: Fairness-Efficiency Tradeoffs in a Unifying Framework." IEEE/ACM Transactions on Networking 21(6):1785-1798, 2013.
- ID: DOI 10.1109/TNET.2012.2233213 (INFOCOM 2012 version: 10.1109/INFCOM.2012.6195481). Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title says it gives a unifying framework for the fairness-efficiency tradeoff in multi-resource allocation.
- Features: F1 n, F2 p, F3 n, F4 y, F5 n.
- Relevance: Axiomatic fairness-efficiency tradeoff in a systems setting.

### joseph2011variability
- Citation: V. Joseph, G. de Veciana. "Variability Aware Network Utility Maximization." arXiv:1111.3728v3, 2011.
- ID: arXiv 1111.3728. Confirmed by the arXiv API; abstract opening read.
- Read scope: abstract_only (opening only).
- Summary: The abstract introduces NUM as the framework for allocating among users and for understanding bandwidth allocation by protocols, and says it motivates work incorporating new constraints. The rest of the abstract (the paper's own contribution on variability) was not read. A related Allerton 2012 paper by Joseph, de Veciana and Arapostathis (DOI 10.1109/ALLERTON.2012.6483304) also appeared in Crossref but is not separately added.
- Features: F1 n, F2 n, F3 n, F4 p, F5 n.
- Relevance: Capacity or rate variability in NUM; supports the uncertain-capacity theme.

### vardi2022dynamic
- Citation: S. Vardi, A. Psomas, E. Friedman. "Dynamic Fair Resource Division." Mathematics of Operations Research 47(2):945-968, 2022.
- ID: DOI 10.1287/moor.2021.1155. Confirmed by Crossref search; abstract read.
- Read scope: abstract_only.
- Summary: A single homogeneous resource is fairly shared among users who arrive and depart. Re-adjusting every user's allocation on each arrival is impractical, so the paper limits how many users can be disrupted per arrival. The abstract's results after this were not read.
- Features: F1 y, F2 n, F3 n, F4 y, F5 n.
- Relevance: Churn with a disruption (re-allocation) limit, which matches a practical ISP rule.

### kash2014no
- Citation: I. Kash, A. D. Procaccia, N. Shah. "No Agent Left Behind: Dynamic Fair Division of Multiple Resources." Journal of Artificial Intelligence Research 51:579-603, 2014.
- ID: DOI 10.1613/jair.4405. Confirmed by Crossref search.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates dynamic fair division of multiple resources with arriving agents.
- Features: F1 y, F2 p, F3 n, F4 y, F5 p.
- Relevance: Axiomatic dynamic fair division reference.

### fikioris2021incentives
- Citation: G. Fikioris, R. Agarwal, E. Tardos. "Incentives in Dominant Resource Fair Allocation under Dynamic Demands." arXiv:2109.12401v2, 2021.
- ID: arXiv 2109.12401. Confirmed by the arXiv API. Published-venue not confirmed, so cited as a preprint.
- Read scope: abstract_only (opening). A WebSearch summary (not the paper) reported the results (dynamic DRF is (1+rho)-incentive compatible; dynamic MMF has ratio 3/2); I did not read those results in the paper.
- Summary: Notes that max-min fairness and DRF guarantee incentive compatibility, envy-freeness and Pareto efficiency only for static demands, while real demands are time-dependent. The paper studies these policies under dynamic demands.
- Features: F1 p, F2 n, F3 n, F4 y, F5 y.
- Relevance: Closest to incentive compatibility of fair allocation when demands change over time.

### sisalem2023enabling
- Citation: T. Si Salem, G. Iosifidis, G. Neglia. "Enabling Long-term Fairness in Dynamic Resource Allocation." Proc. ACM Meas. Anal. Comput. Syst. 6(3):1-36, 2022 (SIGMETRICS 2023).
- ID: DOI 10.1145/3570606; arXiv 2208.05898 (arXiv API record read). Confirmed by both.
- Read scope: abstract_only.
- Summary: Studies dynamic allocation under alpha-fairness with two objectives: slot-fairness (fair every slot) and horizon-fairness (fair across accumulated utilities). The authors argue horizon-fairness costs less welfare, show vanishing regret is impossible against an unrestricted adversary, and propose restrictions on the adversary.
- Features: F1 p, F2 n, F3 n, F4 y, F5 n.
- Relevance: Long-term (over time) fairness in an online allocator.

### sinha2023noregret
- Citation: A. Sinha, A. Joshi, R. Bhattacharjee, C. Musco, M. Hajiesmaili. "No-regret Algorithms for Fair Resource Allocation." Advances in Neural Information Processing Systems (NeurIPS 2023), pp. 48083-48109.
- ID: Crossref DOI 10.52202/075280-2086; arXiv 2303.06396v1 (arXiv API record read).
- Read scope: abstract_only.
- Summary: Considers online allocation against an unrestricted adversary with an aggregate alpha-fair objective, noting that sublinear standard regret was shown impossible earlier. Proposes a policy (called Online Proportional Fair in arXiv v1) that achieves sublinear regret against a relaxed benchmark (a c_alpha-approximation of the best static allocation).
- Features: F1 n, F2 n, F3 n, F4 y, F5 n.
- Relevance: Regret guarantees for alpha-fair online allocation.

### cayci2020group
- Citation: S. Cayci, S. Gupta, A. Eryilmaz. "Group-Fair Online Allocation in Continuous Time." arXiv:2006.06852v2, 2020.
- ID: arXiv 2006.06852. Confirmed by the arXiv API. Published venue not confirmed (a Crossref title search returned no match), so cited as a preprint.
- Read scope: abstract_only (opening).
- Summary: Considers online learning in continuous time where outcomes of an action are observed after a random, action-dependent time, with deadlines on tasks and fairness across groups in a time budget B.
- Features: F1 p, F2 n, F3 n, F4 y, F5 n.
- Relevance: Group fairness in online allocation with deadlines.

### liao2022nonstationary
- Citation: L. Liao, Y. Gao, C. Kroer. "Nonstationary Dual Averaging and Online Fair Allocation." Advances in Neural Information Processing Systems 35, pp. 37159-37172, 2022.
- ID: DOI 10.52202/068431-2693. Confirmed by Crossref search and direct DOI lookup.
- Read scope: metadata_only.
- Summary (from title/metadata): Title indicates a nonstationary dual-averaging method applied to online fair allocation.
- Features: F1 p, F2 n, F3 n, F4 y, F5 n.
- Relevance: Online fair allocation with arrivals under drift in the stream.

### cookson2025temporal
- Citation: B. Cookson, S. Ebadian, N. Shah. "Temporal Fair Division." Proceedings of the AAAI Conference on Artificial Intelligence 39(13):13727-13734, 2025.
- ID: DOI 10.1609/aaai.v39i13.33500; arXiv 2410.23416 (arXiv API record read). Confirmed by both; Crossref abstract read.
- Read scope: abstract_only.
- Summary: Agents receive a possibly different set of goods each day. The paper charts what fairness guarantees can hold both per day and over time (up to each day, or the weaker overall version).
- Features: F1 p, F2 n, F3 n, F4 y, F5 n.
- Relevance: Formal notions of fairness over time (indivisible goods, so only an analogy to divisible capacity).

### girici2007fair
- Citation: T. Girici, C. Zhu, J. R. Agre, A. Ephremides. "Fair Scheduling in OFDMA-based Wireless Systems with QoS Constraints." International OFDM Workshop (InOWo 2007), arXiv:0711.1269v1.
- ID: arXiv 0711.1269. Confirmed by the arXiv API (the workshop reference is from the arXiv journal-ref field).
- Read scope: abstract_only.
- Summary: Downlink allocation of power and bandwidth in OFDMA for proportional fairness of long-term rates of data users plus QoS rate constraints for real-time sessions. It solves the constrained problem and proposes an algorithm, with numerical results (stated in the abstract).
- Features: F1 n, F2 y, F3 n, F4 y, F5 n.
- Relevance: PF for elastic data with guaranteed rates for real-time sessions: the static analogue of our class mix.

## 3. BibTeX (verified sources)

```bibtex
@article{kelly1998rate,
  author = {Kelly, F. P. and Maulloo, A. K. and Tan, D. K. H.},
  title = {Rate control for communication networks: shadow prices, proportional fairness and stability},
  journal = {Journal of the Operational Research Society},
  volume = {49}, number = {3}, pages = {237--252}, year = {1998},
  doi = {10.1057/palgrave.jors.2600523}
}
@article{kelly1997charging,
  author = {Kelly, F.},
  title = {Charging and rate control for elastic traffic},
  journal = {European Transactions on Telecommunications},
  volume = {8}, number = {1}, pages = {33--37}, year = {1997},
  doi = {10.1002/ett.4460080106}
}
@article{mo2000fair,
  author = {Mo, J. and Walrand, J.},
  title = {Fair end-to-end window-based congestion control},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {8}, number = {5}, pages = {556--567}, year = {2000},
  doi = {10.1109/90.879343}
}
@article{mazumdar1991fairness,
  author = {Mazumdar, R. and Mason, L. G. and Douligeris, C.},
  title = {Fairness in network optimal flow control: optimality of product forms},
  journal = {IEEE Transactions on Communications},
  volume = {39}, number = {5}, pages = {775--782}, year = {1991},
  doi = {10.1109/26.87140}
}
@inproceedings{lan2010axiomatic,
  author = {Lan, T. and Kao, D. and Chiang, M. and Sabharwal, A.},
  title = {An Axiomatic Theory of Fairness in Network Resource Allocation},
  booktitle = {Proc. IEEE INFOCOM}, pages = {1--9}, year = {2010},
  doi = {10.1109/INFCOM.2010.5461911}, eprint = {0906.0557}, archivePrefix = {arXiv}
}
@article{bertsimas2011price,
  author = {Bertsimas, D. and Farias, V. F. and Trichakis, N.},
  title = {The Price of Fairness},
  journal = {Operations Research},
  volume = {59}, number = {1}, pages = {17--31}, year = {2011},
  doi = {10.1287/opre.1100.0865}
}
@article{shenker1995fundamental,
  author = {Shenker, S.},
  title = {Fundamental design issues for the future {Internet}},
  journal = {IEEE Journal on Selected Areas in Communications},
  volume = {13}, number = {7}, pages = {1176--1188}, year = {1995},
  doi = {10.1109/49.414637}
}
@article{lee2005nonconvex,
  author = {Lee, J.-W. and Mazumdar, R. R. and Shroff, N. B.},
  title = {Non-convex optimization and rate control for multi-class services in the {Internet}},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {13}, number = {4}, pages = {827--840}, year = {2005},
  doi = {10.1109/TNET.2005.852876}
}
@article{hande2007distributed,
  author = {Hande, P. and Zhang, S. and Chiang, M.},
  title = {Distributed Rate Allocation for Inelastic Flows},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {15}, number = {6}, pages = {1240--1253}, year = {2007},
  doi = {10.1109/TNET.2007.896507}
}
@inproceedings{fazel2005network,
  author = {Fazel, M. and Chiang, M.},
  title = {Network Utility Maximization With Nonconcave Utilities Using Sum-of-Squares Method},
  booktitle = {Proc. 44th IEEE Conference on Decision and Control}, pages = {1867--1874}, year = {2005},
  doi = {10.1109/CDC.2005.1582432}
}
@article{chiang2007layering,
  author = {Chiang, M. and Low, S. H. and Calderbank, A. R. and Doyle, J. C.},
  title = {Layering as Optimization Decomposition: A Mathematical Theory of Network Architectures},
  journal = {Proceedings of the IEEE},
  volume = {95}, number = {1}, pages = {255--312}, year = {2007},
  doi = {10.1109/JPROC.2006.887322}
}
@article{palomar2006tutorial,
  author = {Palomar, D. P. and Chiang, M.},
  title = {A tutorial on decomposition methods for network utility maximization},
  journal = {IEEE Journal on Selected Areas in Communications},
  volume = {24}, number = {8}, pages = {1439--1451}, year = {2006},
  doi = {10.1109/JSAC.2006.879350}
}
@article{massoulie2002bandwidth,
  author = {Massouli{\'e}, L. and Roberts, J. W.},
  title = {Bandwidth sharing: objectives and algorithms},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {10}, number = {3}, pages = {320--328}, year = {2002},
  doi = {10.1109/TNET.2002.1012364}
}
@inproceedings{bonald2001impact,
  author = {Bonald, T. and Massouli{\'e}, L.},
  title = {Impact of fairness on {Internet} performance},
  booktitle = {Proc. ACM SIGMETRICS}, pages = {82--91}, year = {2001},
  doi = {10.1145/378420.378438}
}
@article{deveciana2001stability,
  author = {de Veciana, G. and Lee, T.-J. and Konstantopoulos, T.},
  title = {Stability and performance analysis of networks supporting elastic services},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {9}, number = {1}, pages = {2--14}, year = {2001},
  doi = {10.1109/90.909020}
}
@article{shi2014fairness,
  author = {Shi, H. and Prasad, R. V. and Onur, E. and Niemegeers, I. G. M. M.},
  title = {Fairness in Wireless Networks: Issues, Measures and Challenges},
  journal = {IEEE Communications Surveys \& Tutorials},
  volume = {16}, number = {1}, pages = {5--24}, year = {2014},
  doi = {10.1109/SURV.2013.050113.00015}
}
@article{ogryczak2014fair,
  author = {Ogryczak, W. and Luss, H. and Pi{\'o}ro, M. and Nace, D. and Tomaszewski, A.},
  title = {Fair Optimization and Networks: A Survey},
  journal = {Journal of Applied Mathematics},
  volume = {2014}, pages = {1--25}, year = {2014}, note = {Article 612018},
  doi = {10.1155/2014/612018}
}
@article{demers1989analysis,
  author = {Demers, A. and Keshav, S. and Shenker, S.},
  title = {Analysis and simulation of a fair queueing algorithm},
  journal = {ACM SIGCOMM Computer Communication Review},
  volume = {19}, number = {4}, pages = {1--12}, year = {1989},
  doi = {10.1145/75247.75248}
}
@article{shreedhar1996efficient,
  author = {Shreedhar, M. and Varghese, G.},
  title = {Efficient fair queuing using deficit round-robin},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {4}, number = {3}, pages = {375--385}, year = {1996},
  doi = {10.1109/90.502236}
}
@article{parekh1993generalized,
  author = {Parekh, A. K. and Gallager, R. G.},
  title = {A generalized processor sharing approach to flow control in integrated services networks: the single-node case},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {1}, number = {3}, pages = {344--357}, year = {1993},
  doi = {10.1109/90.234856}
}
@inproceedings{heusse2003performance,
  author = {Heusse, M. and Rousseau, F. and Berger-Sabbatel, G. and Duda, A.},
  title = {Performance anomaly of 802.11b},
  booktitle = {Proc. IEEE INFOCOM}, volume = {2}, pages = {836--843}, year = {2003},
  doi = {10.1109/INFCOM.2003.1208921}
}
@misc{hoiland2017ending,
  author = {H{\o}iland-J{\o}rgensen, T. and Kazior, M. and T{\"a}ht, D. and Hurtig, P. and Brunstrom, A.},
  title = {Ending the Anomaly: Achieving Low Latency and Airtime Fairness in {WiFi}},
  year = {2017}, eprint = {1703.00064}, archivePrefix = {arXiv}
}
@article{kushner2004convergence,
  author = {Kushner, H. J. and Whiting, P. A.},
  title = {Convergence of Proportional-Fair Sharing Algorithms Under General Conditions},
  journal = {IEEE Transactions on Wireless Communications},
  volume = {3}, number = {4}, pages = {1250--1259}, year = {2004},
  doi = {10.1109/TWC.2004.830826}
}
@article{stolyar2005asymptotic,
  author = {Stolyar, A. L.},
  title = {On the Asymptotic Optimality of the Gradient Scheduling Algorithm for Multiuser Throughput Allocation},
  journal = {Operations Research},
  volume = {53}, number = {1}, pages = {12--25}, year = {2005},
  doi = {10.1287/opre.1040.0156}
}
@inproceedings{hou2009theory,
  author = {Hou, I.-H. and Borkar, V. and Kumar, P. R.},
  title = {A Theory of {QoS} for Wireless},
  booktitle = {Proc. IEEE INFOCOM}, pages = {486--494}, year = {2009},
  doi = {10.1109/INFOCOM.2009.5061954}
}
@inproceedings{elazzouni2020deadline,
  author = {ElAzzouni, S. and Ekici, E. and Shroff, N.},
  title = {Is Deadline Oblivious Scheduling Efficient for Controlling Real-Time Traffic in Cellular Downlink Systems?},
  booktitle = {Proc. IEEE INFOCOM}, pages = {49--58}, year = {2020},
  doi = {10.1109/INFOCOM41043.2020.9155523}, eprint = {2002.06474}, archivePrefix = {arXiv}
}
@article{johari2004efficiency,
  author = {Johari, R. and Tsitsiklis, J. N.},
  title = {Efficiency Loss in a Network Resource Allocation Game},
  journal = {Mathematics of Operations Research},
  volume = {29}, number = {3}, pages = {407--435}, year = {2004},
  doi = {10.1287/moor.1040.0091}
}
@article{yang2007vcg,
  author = {Yang, S. and Hajek, B.},
  title = {{VCG-Kelly} Mechanisms for Allocation of Divisible Goods: Adapting {VCG} Mechanisms to One-Dimensional Signals},
  journal = {IEEE Journal on Selected Areas in Communications},
  volume = {25}, number = {6}, pages = {1237--1243}, year = {2007},
  doi = {10.1109/JSAC.2007.070817}
}
@article{jiang2014festive,
  author = {Jiang, J. and Sekar, V. and Zhang, H.},
  title = {Improving Fairness, Efficiency, and Stability in {HTTP}-Based Adaptive Video Streaming With {Festive}},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {22}, number = {1}, pages = {326--340}, year = {2014},
  doi = {10.1109/TNET.2013.2291681}
}
@article{hossfeld2017qoe,
  author = {Ho{\ss}feld, T. and Skorin-Kapov, L. and Heegaard, P. E. and Varela, M.},
  title = {Definition of {QoE} Fairness in Shared Systems},
  journal = {IEEE Communications Letters},
  volume = {21}, number = {1}, pages = {184--187}, year = {2017},
  doi = {10.1109/LCOMM.2016.2616342}
}
@article{belmoukadam2021screen,
  author = {Belmoukadam, O. and Khokhar, M. J. and Barakat, C.},
  title = {On accounting for screen resolution in adaptive video streaming: {QoE}-driven bandwidth sharing framework},
  journal = {International Journal of Network Management},
  volume = {31}, number = {1}, year = {2021},
  doi = {10.1002/nem.2128}
}
@article{caballero2019network,
  author = {Caballero, P. and Banchs, A. and de Veciana, G. and Costa-Perez, X.},
  title = {Network Slicing Games: Enabling Customization in Multi-Tenant Mobile Networks},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {27}, number = {2}, pages = {662--675}, year = {2019},
  doi = {10.1109/TNET.2019.2895378}, eprint = {1612.08446}, archivePrefix = {arXiv}
}
@article{tun2019wireless,
  author = {Tun, Y. K. and Tran, N. H. and Ngo, D. T. and Pandey, S. R. and Han, Z. and Hong, C. S.},
  title = {Wireless Network Slicing: Generalized {Kelly} Mechanism-Based Resource Allocation},
  journal = {IEEE Journal on Selected Areas in Communications},
  volume = {37}, number = {8}, pages = {1794--1807}, year = {2019},
  doi = {10.1109/JSAC.2019.2927100}, eprint = {1907.02182}, archivePrefix = {arXiv}
}
@article{zheng2023constrained,
  author = {Zheng, J. and Banchs, A. and de Veciana, G.},
  title = {Constrained Network Slicing Games: Achieving Service Guarantees and Network Efficiency},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {31}, number = {6}, pages = {2698--2713}, year = {2023},
  doi = {10.1109/TNET.2023.3262810}
}
@article{fossati2020multi,
  author = {Fossati, F. and Moretti, S. and Perny, P. and Secci, S.},
  title = {Multi-Resource Allocation for Network Slicing},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {28}, number = {3}, pages = {1311--1324}, year = {2020},
  doi = {10.1109/TNET.2020.2979667}
}
@article{joewong2013multi,
  author = {Joe-Wong, C. and Sen, S. and Lan, T. and Chiang, M.},
  title = {Multiresource Allocation: Fairness--Efficiency Tradeoffs in a Unifying Framework},
  journal = {IEEE/ACM Transactions on Networking},
  volume = {21}, number = {6}, pages = {1785--1798}, year = {2013},
  doi = {10.1109/TNET.2012.2233213}
}
@misc{joseph2011variability,
  author = {Joseph, V. and de Veciana, G.},
  title = {Variability Aware Network Utility Maximization},
  year = {2011}, eprint = {1111.3728}, archivePrefix = {arXiv}
}
@article{vardi2022dynamic,
  author = {Vardi, S. and Psomas, A. and Friedman, E.},
  title = {Dynamic Fair Resource Division},
  journal = {Mathematics of Operations Research},
  volume = {47}, number = {2}, pages = {945--968}, year = {2022},
  doi = {10.1287/moor.2021.1155}
}
@article{kash2014no,
  author = {Kash, I. and Procaccia, A. D. and Shah, N.},
  title = {No Agent Left Behind: Dynamic Fair Division of Multiple Resources},
  journal = {Journal of Artificial Intelligence Research},
  volume = {51}, pages = {579--603}, year = {2014},
  doi = {10.1613/jair.4405}
}
@misc{fikioris2021incentives,
  author = {Fikioris, G. and Agarwal, R. and Tardos, {\'E}.},
  title = {Incentives in Dominant Resource Fair Allocation under Dynamic Demands},
  year = {2021}, eprint = {2109.12401}, archivePrefix = {arXiv}
}
@article{sisalem2023enabling,
  author = {Si Salem, T. and Iosifidis, G. and Neglia, G.},
  title = {Enabling Long-term Fairness in Dynamic Resource Allocation},
  journal = {Proc. ACM Meas. Anal. Comput. Syst.},
  volume = {6}, number = {3}, pages = {1--36}, year = {2022},
  doi = {10.1145/3570606}, eprint = {2208.05898}, archivePrefix = {arXiv}
}
@inproceedings{sinha2023noregret,
  author = {Sinha, A. and Joshi, A. and Bhattacharjee, R. and Musco, C. and Hajiesmaili, M.},
  title = {No-regret Algorithms for Fair Resource Allocation},
  booktitle = {Advances in Neural Information Processing Systems}, pages = {48083--48109}, year = {2023},
  doi = {10.52202/075280-2086}, eprint = {2303.06396}, archivePrefix = {arXiv}
}
@misc{cayci2020group,
  author = {Cayci, S. and Gupta, S. and Eryilmaz, A.},
  title = {Group-Fair Online Allocation in Continuous Time},
  year = {2020}, eprint = {2006.06852}, archivePrefix = {arXiv}
}
@inproceedings{liao2022nonstationary,
  author = {Liao, L. and Gao, Y. and Kroer, C.},
  title = {Nonstationary Dual Averaging and Online Fair Allocation},
  booktitle = {Advances in Neural Information Processing Systems}, volume = {35}, pages = {37159--37172}, year = {2022},
  doi = {10.52202/068431-2693}
}
@inproceedings{cookson2025temporal,
  author = {Cookson, B. and Ebadian, S. and Shah, N.},
  title = {Temporal Fair Division},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence}, volume = {39}, number = {13}, pages = {13727--13734}, year = {2025},
  doi = {10.1609/aaai.v39i13.33500}, eprint = {2410.23416}, archivePrefix = {arXiv}
}
@misc{girici2007fair,
  author = {Girici, T. and Zhu, C. and Agre, J. R. and Ephremides, A.},
  title = {Fair Scheduling in {OFDMA}-based Wireless Systems with {QoS} Constraints},
  year = {2007}, note = {International OFDM Workshop (InOWo 2007)},
  eprint = {0711.1269}, archivePrefix = {arXiv}
}
```

## 4. Could not verify / could not retrieve

- Jain, Chiu, Hawe, "A quantitative measure of fairness and discrimination for resource allocation in shared computer systems" (DEC technical report 301, 1984). Tried Crossref bibliographic search; it returned unrelated theses and no record for this report. No primary record fetched, so I did not include it. Lan et al. (above) cover Jain's index as a special case.
- Hemmati, University of Ottawa PhD thesis on sigmoidal-utility NUM and Social Utility Maximization. Only a WebSearch snippet (ruor.uottawa.ca/handle/10393/36626); I did not fetch or verify the record, so it is excluded.
- Datar, Altman, De Pellegrini, El Azouzi, Touati, "A Mechanism for Price Differentiation and Slicing in Wireless Networks" (WiOpt 2020). Seen only in search results (dl.ifip.org page header named different authors). Not confirmed via Crossref/DBLP. Excluded.
- Høiland-Jørgensen et al. USENIX ATC 2017 venue/pages: the DBLP query failed (proxy). The paper is included as an arXiv preprint only.
- Cayci et al. and Fikioris et al.: published venues not confirmed; cited as arXiv preprints. A Crossref title search for Cayci returned no match.
- Full texts. Everything except Lan et al. was read at abstract or metadata level. Paywalled IEEE/ACM items whose full texts matter for the paper and were not read: Lee-Mazumdar-Shroff 2005, Hande et al. 2007 (Princeton PDF 404; IEEE Xplore page returned empty; Semantic Scholar abstract elided), Kelly et al. 1998, Mo-Walrand 2000, Fazel-Chiang 2005, Hou-Borkar-Kumar 2009, Zheng et al. 2023, Fossati et al. 2020, Hossfeld et al. 2017.
- Viswanath-Tse-Laroia (IEEE Trans. Inf. Theory 48(6):1277-1294, 2002, DOI 10.1109/TIT.2002.1003822) and Bennett-Zhang WF2Q (INFOCOM 1996, DOI 10.1109/INFCOM.1996.497885) were confirmed in Crossref but not added to the main list, to keep it focused. Add them if the paper needs the opportunistic-scheduling or WF2Q references.
- No confirmed 2022-2026 networking paper on Wi-Fi 6/7 OFDMA fairness with class-dependent QoS was found. One 2025 UORA arXiv paper (2510.04731) appeared only in a search snippet and was not fetched, so it is not used.

## 5. Strand synthesis

Settled. Kelly-style NUM and the alpha-fair family give a standard way to turn utilities into allocations. Axiomatic work (Lan et al.) and the price of fairness (Bertsimas et al.) say how to pick and price a fairness level. For mixed traffic, the classic line (Shenker; Lee et al.; Hande et al.; Fazel-Chiang) shows non-concave utilities break convexity and need special treatment. Packet-level and cellular baselines (fair queueing, DRR/GPS, PF, gradient scheduling, Wi-Fi airtime fairness) are well established. Strategic behaviour in proportional (Kelly-type) allocation has efficiency guarantees (Johari-Tsitsiklis; VCG-Kelly).

Open. F1: most NUM and fairness theory is static or flow-level. Online allocation with arrivals and departures appears in fair-division (Vardi et al., Kash et al.), online-learning (Si Salem et al., Sinha et al.) and deadline-scheduling (ElAzzouni et al.) papers, but none that I read combines uncertain capacity with class-dependent non-concave utilities. F2 and F3 together: slicing games (Caballero, Zheng, Fossati) bring SLAs into fair allocation but not heterogeneous real-time utilities for individual devices under churn. F5: incentive compatibility for fair allocation under dynamic demands is only treated for DRF/MMF (Fikioris et al.), not for misreported QoS class on a shared link with tiers. F4 over time: horizon-fairness has regret impossibility results against unrestricted adversaries, so some restriction on arrivals or capacity will be needed. No source found covers all five features jointly.
