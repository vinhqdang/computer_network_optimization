# Integrity recheck: numbers in abstract, intro, experiments, discussion (post-regeneration)

Scope: abstract.tex, intro.tex, experiments.tex, discussion.tex, captions, paper/tables/*.tex against results/*.json, experiments/*.py, repay/sim.py, repay/params.py.
All values recomputed from the JSON records with Python (scratch scripts in the session scratchpad). Nothing was edited, no experiment rerun, no git command run.
Tables compare, compare_home, variability, tiers_binding and deviation were regenerated from the records cell by cell (mean, CI half-width, formatting): 0 differences. oracle.tex and thin_market.tex also match the JSON.

Verdicts: OK / MISMATCH / UNSUPPORTED / WORDING.

## 1. Claim table

### Abstract (abstract.tex)

| Line | Claim | Found | Verdict |
|---|---|---|---|
| 9 | about 75 devices | analytic (0.25+12/180) x 240 = 76; earlier check 75 | OK |
| 9 | REPAY serves 90% of RT slots vs 82% PF | 89.89% vs 81.89% | OK |
| 9 | "at the same delay-tolerant throughput" | elastic rate 1.753 vs 1.783 Mbit/s (-1.7%, experiments.tex:75 itself says 1.7% lower) | WORDING |
| 10 | 180 devices, six traces | 6 x 30 = 180 | OK |
| 10 | median gain 170% Priority, 154% WFQ, 62% plain DPP | 170.0, 153.8, 62.3 | OK |
| 10 | REPAY median change 0.2% | 0.178 (CI [-0.51, 0.24]) | OK |
| 10 | no device gains more than a third of the bound (REPAY) | max gain/B = 0.2945 (12.66 of 43 Mbit); n_above_1 = 0 | OK |

### Introduction (intro.tex)

No numeric result claims. "four minutes" = 240-slot mean stay (OK). Line 13 "we show that strict priority and standard utility-maximising schedulers both have this defect" is supported (Priority +170%, DPP +62% median).

### Experiments: setup (experiments.tex 9-33) against code

| Line | Claim | Code / data | Verdict |
|---|---|---|---|
| 10 | slot 1 s | convention | OK |
| 11 | arrivals 0.25/slot, batch Poisson(12) every 180, geometric stay mean 240 | HOTSPOT_DEFAULTS identical | OK |
| 11 | about 75 devices present | 76 analytic | OK |
| 12 | tier probs (0.6,0.25,0.15), class probs (0.65,0.25,0.10) | identical | OK |
| 13 | link rate U[5,30]; on/off mean 50 and 20 | ell_lo/hi 5/30; p_on_off 0.02, p_off_on 0.05 | OK |
| 14 | capacity 150, multipliers (1,0.6,0.2), mean hold 33 slots, lognormal noise | C_MULTS, C_STAY 0.97 (33.3) | OK |
| 14 | mean about 91 Mbit/s | 150 x 0.6 x exp(0.15^2/2) = 91.0 (stationary law is uniform on states) | OK |
| 14 | fair share between roughly 2 and 0.4 | 150/75 = 2.0; 30/75 = 0.4 (below rmin_v = 0.5) | OK |
| 15 | home: ten premium devices, 25 Mbit/s | HOME_DEFAULTS n=10, tier (0,1,0), C_mean 25 | OK |
| 16 | rmin_v 0.5, rmax_v 3, r_g 0.2, w (1,2,1.5), c_P 2, c_Y 1.5, theta 0.8/0.6, phi 0.15, V 20 | Params defaults identical | OK |
| 32 | 10 traces comparison | SEEDS range(10) | OK |
| 32 | 5 traces: bound, variability, binding table | range(5) in all three | OK |
| 32 | 3: default business constraints, optimality gap | exp_tiers range(3); optgap (0,1,2) | OK |
| 32 | 4: collapse | COLL_SEEDS 0..3 | OK |
| 32 | 6: unilateral deviations | SEEDS 0..5 | OK |
| 32 | 2: switching and oracle | SEEDS (0,1) in both | OK |
| 33 | noise sigma 0.15; sojourn at least 5 slots | C_sigma 0.15; min_sojourn 5 | OK |
| 37-38 | 5 seeds x 6000 slots; adversarial square wave 150/15 every 60 | exp_bound T=6000, SEEDS range(5), `(slots//60)%2` -> 150/15 | OK |
| 53 | optgap population: 2 tiers, 3 video, 1 gaming, 5 elastic; 200 equiprobable capacities; lognormal mixture medians 30,12,4; theta_P 0.5, phi 0.15; 3 seeds; 20 000 slots | exp_optgap POP and constants identical | OK |
| 70 | 10 seeds, 6000 slots | T=6000 | OK |
| 121 | 30 devices/trace, 6 traces of 3000 slots, at least 60 slots | N_PICK_DEV 30, T 3000, L>=60 (min L found = 60) | OK |
| 134 | thin market: saturated elastic, capacity alternating 0.3 and 1 Mbit/s per device | code: (0.9, 3.0) x n/3 = 0.3 and 1.0 per device; elastic cap 30 | OK (undisclosed: tier prices are forced to zero via beta_override) |
| 177 | 40 reverse-deviation devices | 20 x 2 seeds | OK |
| 181 | 40 elastic devices, stay >= 200; 40th percentile | N_PICK 20 x 2, MIN_L 200, quantile_C 0.4 | OK |
| 232 | "about forty bisection steps per slot" | solver loops: up to 80 steps to relative tolerance 1e-10 plus bracketing; step count is not recorded in any result file | UNSUPPORTED (plausible) |

### Experiments: results

| Line | Claim | Found | Verdict |
|---|---|---|---|
| 39 | max deficit/bound never exceeds 0.43 | 0.426 (adversarial, V=10); hotspot 0.377 | OK |
| 41 | DPP class envy 110 to 900 Mbit | hotspot means 269.5 to 901.3; adversarial 109.7 to 517.6; union 110 to 901 | OK |
| 41 | REPAY envy 2 to 52 | 1.9 to 52.3 (hotspot), 3.8 to 45.6 (adversarial) | OK |
| 42 | V=100: 93.8% vs 94.9% | 93.81 vs 94.89 | OK |
| 42 | V=20: 89.3% vs 92.0%; elastic 1.67 vs 1.47 | 89.28 vs 91.97; 1.670 vs 1.468 | OK |
| 55 | U* 18.13; 18.22 without envy; 17.78 slot-wise EF; time-shifting value 0.35; EF cost 0.09 | 18.1325; 18.2213; 17.7782; 0.354; 0.0888 | OK |
| 54 | both tier constraints slack on this instance | multipliers/slack are not stored in optgap.json | UNSUPPORTED (not checkable from results) |
| 57 | gap 0.49 (V=5), 0.098 (V=20), 0.031 (V=100) | 0.4886, 0.0980, 0.0308 | OK |
| 57 | gap x V between 1.96 and 3.08 for V>=5 | 2.443, 2.144, 1.959, 2.271, 3.076 | OK |
| 57 | above slot-wise EF optimum already at V=10 | 17.918 > 17.778 (V=5: 17.644 below) | OK |
| 58 | DPP slightly above U*; PF 17.52 | 18.19 to 18.20; 17.525 | OK |
| 59 | largest deficit 0.21 of bound | 0.2136 | OK |
| 72 | elastic rate falls from about 1.75 to 1.26 (WFQ/Priority) | 1.753 to 1.271 / 1.257 | OK |
| 72 | class envy reaches about 2000 Mbit | WFQ 1981, Priority 2212 | WORDING (minor) |
| 73 | PF, Credit: 82% of RT slots, 76 to 80% video | 81.9 / 82.6; 79.8 / 75.7 | OK |
| 74 | REPAY 89.9%; elastic 1.75 vs 1.78; envy 19 | 89.9; 1.753 vs 1.783; 18.9 | OK |
| 75 | closes 44% of PF-Priority RT gap; 1.7% lower elastic rate; higher utility than PF | (89.9-81.9)/(100-81.9) = 44.2%; 1.7%; 70.7 > 68.7 | OK |
| 76 | free tier 83% vs 70% PF | 83.3 vs 70.0 | OK |
| 76 | paid tiers served in more than 99% of slots "by every rule that uses the tier weights" | REPAY 99.9/99.07, DPP 99.9/99.4, no-debt 99.86/99.24, PF 100/99.1, WFQ/Priority 100. Credit also uses tier weights (`w = p.w_arr[tier]`, mechanisms.py:367) and serves premium 95.3%, PAYG 83.8% | WORDING (false for Credit) |
| 77 | Priority and WFQ utility 74.8 and 73.9 vs 70.7 | 74.79, 73.95, 70.73 | OK |
| 78 | REPAY-WC coincides with REPAY in every run | util/RT differences exactly 0.0 in all 20 runs (hotspot and home) | OK |
| 78 | recycling condition "never occurs in these scenarios" | inferred from identical output, no counter is stored | WORDING (state as "has no effect in any run") |
| 78 | REPAY-E differs only in third decimal | means: 1.753 vs 1.754 elastic; per-run util differs up to 0.024; PAYG ratio shown 1.31 vs 1.32, envy 18.9 vs 18.8 | OK (loose) |
| 79 | no debt price: RT +1 point, envy 19 to 28 | 91.0 vs 89.9; 28.4 vs 18.9 | OK |
| 81 | home: all rules serve at least 97% of RT slots | PF 99.3, Credit 96.97 (table 97.0); Credit worst seed 89.2% | WORDING (minor: "about 97%") |
| 81 | home envy 10 (REPAY), 165 (DPP), 460 (WFQ, Priority) | 10.3, 164.5, 459.4 | OK |
| 81 | WFQ and Priority coincide "because RT flows never have to be rationed" | identical to 1e-11; RT success exactly 100% in all seeds | OK (explanation is inference) |
| 105-108 | mean 90 Mbit/s; constant capacity all >= 99%; REPAY within three points of DPP; 70 to 72% at s=1.25; only Priority above 90% with envy above 1500 | 90 by construction; min 99.1 (PF); 89.3 vs 92.0 (2.7 pts); 71.8, 72.4, 70.5; Priority 92.6% at s=1.25, envy 1531 | OK |
| 124 | misreporting pays for more than nine in ten (Priority, WFQ) | 91.1%, 92.2% | OK |
| 124 | median 170, 154; pooled +105, +100 | 170.0, 153.8; 105.3, 99.5 | OK |
| 125 | DPP median 62, pooled 26 | 62.3, 26.4 | OK |
| 126 | REPAY median +0.2, CI [-0.5, 0.2], pooled -11 | 0.18, [-0.505, 0.243], -11.2 | OK |
| 127 | 51% gain; p95 0.05; largest gain 12.7 Mbit; no device above 0.30 of B | 51.1; 0.052; 12.66; 0.2945 | OK |
| 128 | Free: median 1.2%, 71% gain; Premium/PAYG median -12%, -3% | 1.21, 71.4; -12.2, -3.1 | OK |
| 129 | every sampled device has link rate above 3 | min ell = 5.21 | OK |
| 136 | thin market gain "about 5 Mbit", an eighth of B=43, or negative and decreasing in L | constants 4.2 to 5.6 (5.3/43 = 0.12); negative rows -75/-8.3/-12.4 decrease with L | OK |
| 162 | Priority at rho=0.25: 1.60 vs 0.63 | 1.602 vs 0.630 | OK |
| 162 | misreporter gets more than truthful "at every rho" under Priority, WFQ, DPP | positive in every seed at rho=0.25, 0.5, 0.75; undefined at rho=1 (no truthful device) and rho=0 | WORDING (minor: "at every rho in {0.25,0.5,0.75}") |
| 163 | rho=1: WFQ 78% = PF; DPP 84%; utility WFQ 72.3 to 59.8; DPP 70.7 to 61.9 | 78.3 / 78.3; 84.0; 72.32 to 59.82; 70.71 to 61.94 | OK |
| 164 | Priority 95.8% RT at rho=1; video utility 1.75 vs 2.53; elastic 0.97 | 95.83; 1.745 vs 2.530; 0.967 | OK |
| 165 | REPAY at rho=0.25: 1.06 vs 1.24 | 1.064 vs 1.241 (negative advantage in all 4 seeds, all rho) | OK |
| 166-167 | REPAY rho=0: utility 69.2, elastic 1.28, video utility 1.86; Priority rho=1: 64.9, 0.97, 1.75; RT 95.8 vs 89.9; "a quarter of the elastic rate" | 69.22, 1.277, 1.858; 64.94, 0.967, 1.745; 95.8 vs 89.9; (1.28-0.97)/1.28 = 24% | OK |
| 178 | every reverse deviator loses utility; mean -33 under REPAY | 40/40 negative (max -1.03); mean -33.2; DPP also 40/40 negative | OK |
| 183 | plain DPP switching gains 0.15 to 0.21 Mbit/s for every tau | 0.184, 0.209, 0.198, 0.169, 0.149 | OK |
| 184 | REPAY loses 0.03 to 0.05 on average; best device +0.04; no device exceeds KB | -0.045, -0.030, -0.031, -0.045, -0.048; max 0.038; KB_violations 0 for all tau, max gain/KB 0.10 | OK |
| 186 | price-taking prediction 25 to 43 Mbit | 42.7, 31.1, 26.0, 25.0 | OK |
| 187 | oracle mean change -0.05 to -0.07; at most 23% gain; largest gain 0.04 | -0.048 to -0.069; 22.5%; 0.043 | OK |
| 189 | hold-down is a restriction on the attacker, not enforced by allocation code | consistent with experiments (tau only shapes the declaration sequence) | OK |
| 207 | all rules meet the service levels with margin, incl. PF | min premium 1.15, PAYG 1.22, free-floor 2.62 vs targets 0.8/0.6/1 | OK |
| 208 | ratios settle above targets for all V | final premium 1.29 to 1.56, PAYG 1.20 to 1.36 (V=5,20,100) | OK |
| 209 | premium ratio 1.28, 1.33, 1.40, 1.50 for theta_P 0.6..1.2; RT 92% to 79% | 1.281, 1.334, 1.401, 1.495; 92.2 to 79.4 | OK |
| 210 | deficit/bound 0.33 to 0.34 throughout | max over seeds per theta: 0.328, 0.341, 0.340, 0.337 | OK |
| 213 | weight-based rules deliver 55% of committed premium demand; REPAY, DPP 99%, 98% and meet other targets | 0.549 to 0.551; 0.992, 0.979; PAYG 0.92, 0.91; free 2.0 | OK |
| 214 | utility 59.4 vs 72.6; RT 76% vs 89%; envy 17 | 59.44 vs 72.61; 76.1 vs 88.5 (0.88505); 16.6 | OK |
| 233 | solve median 1.4 to 2.0 ms for 10 to 3000; conic 11 to 27 ms for 10 to 300; relative difference 1e-8 | 1.37 to 1.98; 10.8 to 26.9; max 1.14e-8 | OK |
| 234 | 2.2 ms per slot at 75 devices; more than two orders of magnitude headroom | 2.19 (hotspot REPAY mean); 1000/2.2 = 450x | OK |

### Captions

| Caption | Claim | Found | Verdict |
|---|---|---|---|
| Fig. bound (a) | maximum over seeds | D_over_B_max max over 5 seeds | OK |
| Fig. bound (b) | dashed line max_g B_{g,v} | B_vid(V) is far above the REPAY envy at all V (max env/B_max 0.23) | OK |
| Tab. compare | mean over 10 seeds; targets 0.8, 0.6, 1 | OK | OK |
| Tab. compare-home | mean over 10 seeds | OK | OK |
| Tab. deviation | 180 devices, six traces, bootstrap over traces | n_boot 2000, resample traces | OK |
| Tab. thin | n_E, n_V, L, Mbit | matches thin_market.json | OK |
| Tab. oracle | 40 devices | 20 x 2 | OK |
| Tab. tiers-binding | mean over 5 seeds, 95% CI | OK | OK |
| Fig. variability | scale 0 constant, scale 1 default, equal mean capacity | OK | OK |

### Discussion (discussion.tex)

| Line | Claim | Found | Verdict |
|---|---|---|---|
| 26 | constant too large to be informative at simulated parameters | text on optgap (gap x V about 2 to 3 vs B_0 "far larger") | OK |
| 29 | constants chosen before the runs and not tuned; business constraints slack in comparisons, bind only in the dedicated experiment | slack confirmed (ratios 1.15 to 3.3 vs targets); "not tuned afterwards" is a process statement that cannot be verified from the repository | OK / not checkable |
| 30 | video bundle capped at 3 Mbit/s | rmax_V = 3 | OK |
| 11 | gaming class has small rate, large eta and loose B | eta_g = 5, B_{P,g} = 200.2 vs video 83 | OK |

## 2. Issues by severity

No CRITICAL and no MAJOR issue. Every numeric value in the four sections, the captions and the five regenerated tables matches the JSON. The setup text matches the code and parameters.

### MINOR (wording or reproducibility; fix recommended)

1. abstract.tex:9, "at the same delay-tolerant throughput". The elastic rate is 1.75 vs 1.78 Mbit/s (1.7% lower, and experiments.tex:75 states this). Suggested: "at a delay-tolerant throughput within 2%", or "at nearly the same delay-tolerant throughput".
2. experiments.tex:76, "the paid tiers are served in more than 99% of slots by every rule that uses the tier weights". Credit uses the tier weights and serves premium 95.3% and PAYG 83.8% of RT slots. Suggested: "by every rule except \textsc{Credit} (95% and 84%)". All other nine mechanisms satisfy the claim (lowest value: REPAY PAYG 99.07%).
3. experiments.tex:81, "all rules serve at least 97% of RT slots" in the home scenario. Credit is 96.97% (table shows 97.0); its worst seed is 89%. Suggested: "all rules serve about 97% or more of RT slots on average".
4. experiments.tex:72, "class envy reaches about 2000 Mbit". WFQ is 1981, Priority 2212. Suggested: "about 2000 to 2200 Mbit".
5. experiments.tex:162, "at every $\rho$". Gains are measured at rho in {0.25, 0.5, 0.75} (positive in every seed). At rho=0 and rho=1 there is no misreporter or no truthful device. Suggested: "at every tested interior $\rho$".
6. experiments.tex:78, "its recycling condition ... never occurs in these scenarios". The experiments show only that REPAY-WC output is identical to REPAY in all 20 runs; no counter records whether the condition was ever met. Suggested: "has no effect on any run".
7. experiments.tex:232, "about forty bisection steps per slot" is not recorded in any result file (the code runs up to 80 steps to a 1e-10 relative tolerance). Either add a step counter to exp_runtime or write "at most 80".
8. experiments.tex:54, "Both tier constraints turn out to be slack on this instance" cannot be verified from optgap.json (multipliers are not stored). Store the dual values or the tier service ratios.
9. experiments.tex:31, "95% confidence intervals" are 1.96 x SE (normal approximation, common.mean_ci) with 3 to 10 seeds. For 3 or 5 seeds the t-interval is about 2.2 to 2.5 times wider. Either say "normal-approximation" or use t quantiles. Applies to the compare, variability, tiers_binding tables and the text quoting them.
10. Setup omissions (no mismatch): the thin-market experiment forces tier prices to zero (beta_override); T for the business-constraint runs (6000, 8000, 12 000) and sigma=0.2 for the optgap capacity mixture are not stated in the text; the reverse-deviation experiment uses 2 traces (20 devices each) and is not in the list of trace counts at line 32.

### Items verified as exact and worth noting

- The REPAY deviation headline (median +0.2%, CI [-0.5, 0.2], pooled -11%) is worded in the text without a claim of a significant loss; the CI includes zero and the text says so.
- "No device gains more than a third of the bound" (abstract) holds for REPAY (max 0.2945) but not for every variant: REPAY-E max 0.305, No-debt max 0.334 (the latter is just above 1/3). The abstract refers to REPAY only, so OK.
- Deviation seeds 0 and 1 were reused from strategic.json after a reproduction check (max abs error 0.0), as recorded in deviation.json.
