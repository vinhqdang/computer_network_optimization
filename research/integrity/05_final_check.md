# Final integrity check (05)

Scope: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, paper/references.bib, results/*.json, experiments/*.py. Nothing was edited and no experiment was rerun. Numbers were recomputed from the stored records with Python. Network access worked (arXiv API, Crossref, rfc-editor.org, optimization-online.org).

## Verdicts

| Part | Verdict |
|---|---|
| A. Numbers | PASS, with one wording fix (A1) and two optional clarifications (A2, A3) |
| B. References | PASS, with one wording softening (B1) and two cosmetic notes (B2, B3) |
| C. Hygiene | PASS for paper, code, results and PDF; two non-paper files contain a scratchpad path with "claude" in it (C1) |

## Part A. Numbers

### Items that match (recomputed)

- **Table tab:bsize** (deviation.json, REPAY records, 180 devices). All 15 cells match.

| Tier | B | median vol_truth | median B/vol | median max_env_truth | max max_env_truth |
|---|---|---|---|---|---|
| Free (n=112) | 43 | 188.9 | 0.228 | 6.89 | 14.14 |
| Premium (n=41) | 83 | 494.1 | 0.168 | 3.84 | 6.66 |
| PAYG (n=27) | 63 | 247.6 | 0.254 | 6.56 | 14.15 |

  - Gaming bounds are 100.2, 200.2 and 150.2, written as 100, 200 and 150.
  - Median stay is 206 slots (text: "about 200"); minimum is 60.
  - "Between a sixth and a quarter" matches 0.17-0.25. The overall median B/vol is 0.22 ("about a fifth" in discussion.tex).
  - "Bound close to the whole volume for a 60-slot stay" matches: the median B/vol for stays of 70 slots or less is 0.88.
- **Unilateral deviations** (deviation.json), all matching recomputation from records and the stored summary:
  - Priority and WFQ: 91.1% and 92.2% of devices gain, median +170.0% and +153.8%, pooled +105.3% and +99.5%.
  - Plain DPP: median 62.3%, pooled 26.4%.
  - REPAY: median +0.18% with CI [-0.51, 0.24], pooled -11.2%, 51.1% gain, p95 0.052 Mbit/s, largest gain 12.66 Mbit, max gain/B = 0.294 ("no more than 0.30").
  - Free tier: median 1.2%, 71% gain. Premium median -12.2%, PAYG -3.1%.
  - 30 devices per trace, 6 traces, T=3000, minimum stay 60 (exp_deviation.py).
  - The elastic link-rate range of [5,30] Mbit/s supports "link rate above 3 Mbit/s".
- **Short stays** (short_stays.json, recomputed from the 600 records):
  - REPAY: n=120, 82.5% gain, median 10.07%, pooled -6.04%, max gain 10.403 Mbit, gain/B = 0.242 ("a quarter").
  - Plain DPP: median 58.9%. Priority: 141.1%. WFQ: 136.4%.
  - L is in [5,59], 4 traces, 30 per trace (script: seeds 0-3, L 5-59).
  - discussion.tex "four in five ... median 10%" matches.
- **Trade-off curves** (frontier.json, 5 seeds x 110 runs):
  - Capped priority q=0.3: RT 93.2%, elastic 1.797, envy 390.7, utility 70.09.
  - REPAY V=20: RT 89.3%, elastic 1.670, envy 19.47, utility 70.105. 390.7/19.47 = 20.06, so "twenty times" is right.
  - Misreport at q=0.2 / 0.3 / 0.5: median -55.3% / -20.3% / +68.7%, pooled -60.4% / -33.0% / +27.0%, share gaining 1.7% / 25.0% / 66.7%.
  - The 60 devices are 30 per seed on 2 seeds.
  - "REPAY lies to the right of DPP and WFQ" holds on the stored grid.
  - V=100: REPAY 93.8% vs DPP 94.9%. V=20: 89.3% vs 92.0%, with elastic 1.67 vs 1.47.
- **Call continuity** (continuity.json, mean over 5 seeds):
  - REPAY: outage 14.13%, 3.65 interruptions per 100 s, mean 3.93 s, p95 14.4 s, never interrupted 41.9%.
  - DPP is better on every count (10.64, 2.93, 3.69, 12.8, 46.9). WFQ and Priority are much better.
  - PF: 1.33 interruptions per 100 s, mean outage 17.27 s.
  - T=6000, 5 seeds.
- **Paired differences** (compare.json, hotspot, 10 seeds, t(9) half-widths):
  - REPAY minus PF: RT +8.00 ± 1.30 points, utility +2.02 ± 0.42, elastic -0.0292 ± 0.0047 Mbit/s, same sign on all 10 traces.
  - REPAY minus DPP: RT -2.30 ± 0.51 ("serves 2.3 ± 0.5 more" for DPP), utility -1.36 ± 0.13 ("higher by 1.4 ± 0.1" for DPP), elastic +0.194 ("lower by 0.19").
  - Gap closed vs Priority is 44.2%. Elastic rate is 1.64% lower than PF.
  - Per-tier statements match: free 83.3% vs 70.0%, paid tiers at least 99.1% except Credit (95.3% and 83.8%).
  - Other figures in the paragraph match: 89.9, 1.75 vs 1.78, envy 19, Priority/WFQ envy 2212/1981, utilities 74.8 and 73.9 vs 70.7. No-debt: RT 91.0%, envy 28.4. Home envy: 10.3, 164.5, 459.4.
- **Oracle and ablation** (oracle.json, oracle_ablation.json, recomputed from records):
  - Mean gain per slot by tau (1, 5, 20, 60): -0.048, -0.069, -0.059, -0.051.
  - Share with positive gain: 5, 0, 5, 22.5%. Largest gain 0.043.
  - Price-taking prediction per tau: 42.7, 31.1, 26.0, 25.0, i.e. "25 to 43".
  - Zero exceedances of KB.
  - Keep variant, tau=1: 85% gain, mean 0.0109 (1.08% of volume). Largest gain over all taus and rules in the ablation: 0.1156 ("at most 0.12"). Sticky: 77.5%, 0.0084.
  - The oracle.json and oracle_ablation.json sanity checks agree exactly.
- **Running time** (runtime.json, compare.json ms_per_slot):
  - Bisection medians are 1.37-1.98 ms for N=10..3000.
  - cvxpy medians are 10.8-26.9 ms for N=10..300. Max relative gap is 1.0-1.1e-8.
  - Solver loop is 80 steps (repay/solver.py:54).
  - REPAY ms_per_slot is 2.19 ms on hotspot, so "2.2 ms" is right. 1000/2.2 gives more than two orders of magnitude of headroom.
- **abstract.tex**: 90% vs 82% RT, throughput within 2% (1.7%), 92% DPP, 100% Priority, 170 / 154 / 62 / 0.2%, "about half gain" (51.1%), "none more than a third of the bound" (0.294). All match.
- **Thin markets**: gains are about 5.3-5.6 Mbit, i.e. an eighth of 43. The script uses capacity of 0.9 and 3.0 per three devices, i.e. 0.3 and 1 Mbit/s per device, matching the text.
- **Table files** (every file in paper/tables recomputed against its JSON):
  - compare.tex and compare_home.tex: 0 mismatches over all 9 mechanisms x all columns, including t-based CIs.
  - tiers_binding.tex, variability.tex and priority_cap.tex: 0 mismatches.
  - deviation.tex, continuity.tex, short_stays.tex, oracle.tex, oracle_ablation.tex and thin_market.tex: 0 mismatches against summaries and records.
- **Experiment descriptions vs scripts**:
  - Frontier: seeds 0-4, T=6000, V in {5,10,20,50,100}, WFQ multipliers {1,2,4,8,16}, q in {0.1,0.2,0.3,0.5,1}. Deviation: seeds 0-1, T=3000, q in {0.2,0.3,0.5}, 30 devices per seed.
  - Continuity: seeds 0-4, T=6000, outage run minimum 5, block 10.
  - Short stays: seeds 0-3, 30 per seed, L 5-59, T=3000.
  - Oracle and ablation: seeds 0-1, 20 per seed, minimum stay 200, tau {1,5,20,60} and {1,5,20}.
  - Deviation: 6 seeds. Thin market: markets and L as in Table tab:thin.
  - All match the text.

### Non-OK items

**A1 (wording; minor).** experiments.tex, "Call continuity": "give the same figures to within $0.02$" is not true of all columns of Table tab:continuity.
- p95 outage length is 14.4 / 14.2 / 14.6 s (spread 0.4 s).
- Outage in runs of at least 5 s is 65.4 / 65.7 / 65.6% (spread 0.3).
- Never-interrupted is 41.9 / 42.0 / 41.9% (spread 0.1).
- Only outage slots (14.12-14.13), interruptions per 100 s (3.63-3.65) and mean length (3.93-3.95) are within 0.02.

Exact correction: replace "give the same figures to within $0.02$" with "give the same outage share, interruption rate and mean outage length to within $0.02$ (the 95th percentile differs by at most $0.4$~s)".

**A2 (clarification; optional).** experiments.tex, "How large is the bound?": "the envy realised is three to twelve times smaller than the bound" holds for the largest realised envy (B/max: 3.0, 12.5, 4.5). For the median realised envy the ratio is 6.2 / 21.6 / 9.6. Suggested: "the largest realised envy is three to twelve times smaller than the bound".

**A3 (informational).** The "price" sentence in the bound subsection (89.3% vs 92.0%, 93.8% vs 94.9%, 1.67 vs 1.47) uses 5-trace values (frontier / bound runs). Table tab:compare uses 10 traces (89.9 / 92.2). This is consistent with the stated seed counts, but a reader may notice the difference. No correction is required.

## Part B. References

1. **Keys.** 68 distinct keys are cited in paper/sections/*.tex and 68 entries are in references.bib. Missing keys: none. Orphan entries: none.
2. **Five newest entries** (Crossref and rfc-editor.org):

| Key | Result |
|---|---|
| hoiland2018cake | OK. Crossref: Høiland-Jørgensen, Täht, Morton; "Piece of CAKE: A Comprehensive Queue Management Solution for Home Gateways"; 2018 IEEE LANMAN; pp. 37-42; DOI 10.1109/LANMAN.2018.8475045. |
| rfc8290 | OK. Høiland-Jørgensen, McKenney, Täht, Gettys, Dumazet; Jan 2018; Experimental; DOI 10.17487/RFC8290 resolves in Crossref. |
| rfc8325 | OK. Szigeti, Henry, Baker; Feb 2018; Proposed Standard; DOI 10.17487/RFC8325 resolves. |
| rfc9330 | OK. Briscoe (Ed.), De Schepper, Bagnulo, White; Jan 2023; Informational; DOI 10.17487/RFC9330 resolves. |
| rezaei2019deep | OK. Rezaei, Liu; IEEE Commun. Mag. 57(5):76-81, 2019; DOI 10.1109/MCOM.2019.1800819. |

   - related.tex sentence on RFC 8325 (Wi-Fi access categories selected from the Diffserv marking): accurate.
   - Sentence on Rezaei and Liu (learned classifiers for encrypted flows): accurate.
   - Sentence on RFC 8290 / CAKE (flow queueing and AQM isolating flows, low delay for sparse flows): accurate.
   - Sentence on RFC 9330 (L4S, flow requests low queueing delay on condition that it responds to congestion marks): accurate as a description.
3. **Spot checks** (arXiv API and Crossref), all existing with matching authors and titles:
   - abdullah2026dynamic (2611.08302, NeurIPS 2026 per arXiv comment), dai2025efficiency (2507.09473, v2 15 Jul 2026), elokda2026ev (2604.07246), kahana2026perpetual (2605.19844, v1 May, latest Jul 2026), lin2026spec (2610.25067), yu2026slater (2606.31480), zahedi2026credit (2601.17944), sarkar2026geometric (2605.21107, v3 Jul 2026).
   - rezaei2026robust: the Optimization Online page exists, Rezaei and Wei, 26 Oct 2026.
   - balseiro2025regularized: MSOM 27(3):720-735, 2025. fikioris2025dmmf: EC'25, p. 92. sisalem2023enabling: POMACS 6(3):1-36, Dec 2022.
   - elokda2025carma (Transp. Sci. 59(2):340-359) and banerjee2023pseudo (EC'23) also confirmed.

### Non-OK items

**B1 (overstatement; minor).** related.tex L13: L4S "removes the incentive to misdeclare because the low-delay queue carries no throughput advantage". RFC 9330 says the DualQ gives "no more rate advantage to unresponsive flows than a single-queue AQM" and that the service "requires self-restraint" (burst policing may later be needed). "Removes" is stronger than the RFC. Exact correction: "reduces the incentive to misdeclare, since the low-delay queue is designed to carry no throughput advantage, although the service relies on self-restraint".

**B2 (cosmetic).** The key `sisalem2023enabling` has year = {2022}, which is correct (POMACS 6(3), Dec 2022; presented at SIGMETRICS 2023). Only the key name says 2023. No change needed.

**B3 (cosmetic).** `yu2019low` has year 2020 (JMLR 21(1)), which is correct. The key names carry the arXiv year. No change needed.

## Part C. Hygiene

Searched the whole repository excluding .git (case-insensitive: claude, anthropic, chatgpt, openai, gpt, copilot, gemini, llm, generated by, AI-generated, co-authored, language model, AI, assistant, noreply), plus git history and `pdfinfo` / `strings` on the PDF.

- **paper/ (LaTeX, bib, bbl, aux, log, PDF)**: no AI-tool mention as author or generator. PDF metadata: Title, Author and Keywords are empty; Creator is "LaTeX with hyperref"; Producer is pdfTeX-1.40.25; no AI strings in the PDF.
- **Code, results, tests, README, LICENSE**: no mention of AI tools. The only hits are common-word hits: LICENSE:114 ("generated by the Derivative Works") and .gitignore:197 (the Abstra template comment).
- **Git history**: 38 commits, authors Vinh (37) and one GitHub-web commit by "Quang-Vinh Dang". No Co-Authored-By or Claude/Anthropic text. Working tree clean.
- **Hits that name an assistant tool:**

| File:line | Text | Assessment |
|---|---|---|
| research/integrity/02_data_and_claims.md:4 | scratch path `/tmp/claude-0/-home-user-computer-network-optimization/.../scratchpad/integrity/` | tool-name path (C1) |
| research/integrity/03_proofs.md:4 | scratch path `/tmp/claude-0/.../scratchpad/proofs/` | tool-name path (C1) |
| research/integrity/02_data_and_claims.md:204 | heading "7-mode AI research failure checklist" | describes an AI-failure checklist, not authorship; optional rename |

- **Topic hits, not authorship:**
  - research/lit/06_recency_2025_2026.md:283, 291, 295, 296, 545, 561 and paper/references_all.bib:1625, 1641: titles of cited works ("LLM Inference", "Agentic AI Traffic").
  - research/lit/*.md, references.bib:239 and paper/main.bbl:315: "Journal of Artificial Intelligence Research" and "AAAI Conference on Artificial Intelligence".
  - research/review/R3_editor_devil.md:95 and research/02_algorithm_design.md:111: "generated by the authors" and "indefinite".

**Author block** (paper/main.tex L35-37 and PDF page 1): Quang-Vinh Dang, ORCID 0000-0002-3877-8024 (via `\orcidlink`), British University Vietnam, Hung Yen, Vietnam, vinh.dq4@buv.edu.vn. All five required items are present and correct.

### Non-OK items

**C1 (minor).** research/integrity/02_data_and_claims.md:4 and 03_proofs.md:4 embed the tool-named scratch path `/tmp/claude-0/...`. Exact correction: replace with a neutral path such as `/tmp/integrity-scratch/`, or delete the "Scratch scripts" line, before the repository is made public.

## Summary

Every numeric claim and table in the audited passages is correct. The corrections are one overly strong sentence about the continuity variants (A1), one clarification about realised envy versus bound (A2), one softening of the L4S sentence (B1), and the scratch-path cleanup (C1).
