# Integrity verification, pre-review: Phases C-E and 7-mode failure checklist

Paper: `paper/main.tex` (sections, tables, figures). Code: `repay/*.py`, `experiments/*.py`, `tests/`. Results: `results/*.json`.
Scratch scripts (all re-runnable): `/tmp/claude-0/-home-user-computer-network-optimization/11232ee3-33c1-51be-8f70-9872c1f5a077/scratchpad/integrity/` (`v_compare.py`, `v_strat.py`, `repro.py`, `optgap_check.py`, `devfirst.py`, `oracle_abl.py`, `wfq_slot.py`).
No git command was run. Nothing in the paper, code or results was edited.

## 1. Summary and verdict

**Verdict for Phases C-E: FAIL (correctable by text edits only; no CRITICAL finding).**

- No fabricated or irreproducible result was found. All six paper tables match the JSON files cell by cell (mean and CI), 0 mismatches. A fresh run of hotspot seed 0 (T=6000) for REPAY, PF and Priority, and of one unilateral-deviation case, reproduces the stored numbers to 9 digits. `pytest -q tests`: 48 passed.
- No code bug that invalidates a claim was found. Baselines are fair and metrics are computed by the same code for every mechanism.
- Problems are in what the text says about the numbers: one wrong descriptive number (mean capacity), one wrong ratio ("a third"), an abstract headline on misreporting that is stated in a way the data do not support (mean of per-device ratios, CI for REPAY includes zero), an optimality-gap experiment in which the business constraints are slack, an algorithm box that lists a hold-down the code does not enforce, and several undisclosed limitations (2 traces for the strategic experiments, a WC variant that never triggers, no CI in the deviation table).
- CRITICAL: none. MAJOR: 6 (M1-M6). MINOR: 16 (m1-m16).

## 2. Table of numbers (location | paper value | recomputed | status)

OK = matches within rounding. All recomputation is from `results/*.json` by script.

### 2.1 Abstract and Setup

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| Abstract, hotspot size | about 75 devices | 75.1 / 75.0 / 74.4 mean active (seeds 0-2, T=6000, warm-up included); analytic 0.3167 x 240 = 76 | OK |
| Abstract, RT success REPAY vs PF | 90% vs 82% | 89.89% vs 81.89% | OK |
| Abstract, "same delay-tolerant throughput" | same | 1.75 vs 1.78 Mbit/s; paired difference -0.029 +- 0.004 (-1.7%) | WORDING (small but significant, see M4) |
| Abstract / Sec. 6.4, gain under Priority | +320% | 320.0% (mean of 60 per-device ratios); median +164%; pooled volume +106%; bootstrap 95% CI [199, 470]; per-seed 201% / 439% | NUMBER OK, CLAIM MISLEADING (M1) |
| same, WFQ | +272% | 271.8%; median +142%; pooled +100%; CI [178, 388] | same (M1) |
| same, plain DPP | +57% | 57.2%; median +59%; pooled +26%; CI [44, 71] | same (M1) |
| same, REPAY | -3% | -3.3% (mean), median -0.8%, pooled -8.1%; bootstrap 95% CI [-6.7, +0.1] | NUMBER OK, "loses" NOT SUPPORTED (M1) |
| Setup, arrivals 0.25/slot, batch Poisson(12) every 180, mean stay 240 | as stated | `HOTSPOT_DEFAULTS`: identical (also min sojourn 5, not stated) | OK |
| Setup, tier probs (0.6,0.25,0.15), class probs (0.65,0.25,0.10), link rate U[5,30] | as stated | identical | OK |
| Setup, on/off durations 50 and 20 | 50, 20 | p_on_off=0.02, p_off_on=0.05 -> 50, 20 | OK |
| Setup, capacity 150 x (1,0.6,0.2), mean hold 33 | as stated | C_MULTS, C_STAY=0.97 -> 33.3 | OK |
| **Setup, "the mean is about 96 Mbit/s"** | **96** | **90.9 (mean over 10 traces; analytic 150 x 0.6 x e^{0.15^2/2} = 91.0)** | **MISMATCH (M2)** |
| Setup, fair share 2 to 0.4 Mbit/s | 2 to 0.4 | 150/75 = 2.0, 30/75 = 0.4 | OK |
| Setup, home: 10 premium devices, 25 Mbit/s | as stated | `HOME_DEFAULTS`: 10 devices, tier (0,1,0), C_mean 25; only ~6 are elastic, RT devices cycle in sessions | OK |
| Setup, utilities, weights, c_P, c_Y, theta, phi, V=20 | as stated | `params.py` defaults identical | OK |

### 2.2 Section 6.2 (bound)

| Location | Paper | Recomputed (`bound.json`) | Status |
|---|---|---|---|
| 5 seeds x 6000 slots, adversarial 150/15 every 60 | as stated | `exp_bound.py` identical | OK |
| max D/B ratio | never above 0.43 | 0.426 (adversarial, V=10) | OK |
| DPP class envy | 270 to 900 Mbit | hotspot means 269.5 (V=2) to 901.3 (V=100); adversarial 110 to 518 | OK for hotspot (Fig. 1b is hotspot only) |
| REPAY class envy | 2 to 52 Mbit | hotspot means 1.9 to 52.4 | OK |
| V=100: RT success REPAY vs DPP | 93.8 vs 94.9 | 93.80 vs 94.89 | OK |
| V=20: RT success | 89.3 vs 92.0 | 89.28 vs 91.97 | OK |
| V=20: elastic rate | 1.67 vs 1.47 | 1.670 vs 1.468 | OK |

### 2.3 Section 6.3 (optimality gap, `optgap.json`)

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| U* | 18.13 | 18.1325 | OK |
| U* without envy constraints | 18.22 | 18.2213 | OK |
| U* with slot-wise EF | 17.78 | 17.7782 | OK |
| value of time-shifting | 0.35 | 0.354 | OK |
| cost of EF with time-shifting | 0.09 | 0.0888 | OK |
| gap at V=5, 20, 100 | 0.49, 0.098, 0.031 | 0.4886, 0.0980, 0.0308 | OK |
| gap x V for V>=5 | between 2 and 3.1 | 2.44, 2.14, **1.96**, 2.27, 3.08 (V=5,10,20,50,100) | OK at rounding (1.96); but not constant, see M3 |
| "above slot-wise EF optimum already at V=10" | V=10 | util 17.918 > 17.778 (V=5: 17.644 < 17.778) | OK |
| DPP above U* | slightly more | 18.19 to 18.20 (+0.06) | OK |
| PF | 17.52 | 17.525 | OK |
| max deficit / bound | 0.21 | 0.2149 (max over runs), 0.214 (max of means) | OK |
| 20 000 slots | 20 000 | T=20000 (3 seeds; seeds not stated) | OK (m11) |
| Premium and free-floor constraints in the benchmark | implied active | average slack e_PS = -5.9, e_FF = -4.7 Mbit/s: both **slack**; theta_P = 0.5 not 0.8 | UNDISCLOSED (M3) |

### 2.4 Section 6.4 (truthful comparison)

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| Table 1 (hotspot), 9 mechanisms x 10 columns, mean and CI | as printed | `v_compare.py`: 0 mismatches | OK |
| Table 2 (home) | as printed | 0 mismatches | OK |
| elastic rate WFQ/Priority | "falls to 1.26" | 1.27 / 1.26 | OK |
| class envy WFQ/Priority | "about 2000" | 1981 / 2212 | OK (say 2000-2200) |
| PF, Credit RT success | 82%, 76-80% video | 81.9 / 82.6; video 79.8 / 75.7 | OK |
| REPAY RT 89.9; elastic 1.75 vs 1.78; envy 19 | as stated | 89.89; 1.75 vs 1.78; 18.9 | OK |
| "closes roughly 45% of the gap" | 45% | (89.89-81.89)/(100-81.89) = 44.2% | OK at rounding (say 44%) |
| "at no cost to elastic devices" | none | elastic rate -0.029 +- 0.004 (-1.7%, significant); utility +2.0 +- 0.4 vs PF | WORDING (M4) |
| No-debt: RT +1 point, envy 19 -> 28 | as stated | 91.0 vs 89.9; 18.9 -> 28.4 | OK |
| three variants "almost identical" | almost | REPAY-WC is **bit-identical** to REPAY in hotspot and home (util diff 0.0); REPAY-E differs at the 3rd decimal | WORDING (m7) |
| Home: all rules >= 97% RT | 97% | Credit 97.0%, others >= 99.3% | OK |
| Home envy 10 / 165 / 460 | as stated | 10.3 / 164.5 / 459.4 | OK |
| Home: WFQ = Priority "because RT flows never have to be rationed" | claim | verified: per-seed |difference| 1e-14 in util; in 2000 slots of seed 0, sum(rmin) never exceeds C and max |rate_WFQ - rate_Priority| = 6.5e-13 | SUPPORTED (genuine, analytic) |
| Table 2 caption "10 seeds" | 10 | 10 | OK |
| Table 1 caption "Ratios relative to the targets" | relative | columns are rho/committed demand (raw ratios, compare with 0.8, 0.6, 1.0) | WORDING (m1) |

### 2.5 Capacity variability (`variability.json`, Fig. 4)

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| REPAY within three points of DPP | <= 3 | max difference 2.7 (s=1.00: 89.3 vs 92.0) | OK |
| at deepest shortage REPAY, DPP, PF "about 71%" | 71% | 71.8, 72.4, 70.5 (Credit 71.7) | OK (say 70-72%) |
| "constant capacity: every rule serves the RT flows" | all | PF 99.1, Credit 99.9, rest 100 | OK, loose (m13) |
| only Priority above 90%; envy above 1500 | as stated | 92.6%; 1531 | OK |
| holding mean at 90 | 90 | `c_mean_for`: nominal mean 90 (before lognormal factor 1.011) | OK |
| 5 seeds | not stated in text | 5 | OK (m11) |

### 2.6 Strategic devices (`strategic.json`)

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| Table 3, all 8 rows x 5 columns | as printed | 0 mismatches | OK |
| setup: 30 devices x 2 traces x 3000 slots, L>=60 | as stated | `N_PICK_DEV=30`, `DEV_SEEDS=(0,1)`, L>=60 | OK |
| median -0.008; 45% gain; p95 0.05 | as stated | -0.0080; 45.0%; 0.0458 | OK |
| "roughly quadruples ... almost every device gains" | quadruples | mean of ratios 4.2x; median 2.6x; pooled 2.06x. Share gaining 93.3% / 96.7% | NOT SUPPORTED as a statement about volume (M1) |
| "No device gains more than 0.39 of its bound" | 0.39 | REPAY 0.322; REPAY-E 0.309; **No-debt 0.388**. 27/60 REPAY devices have positive gain, max 13.9 Mbit | NUMBER is the family maximum, not REPAY (m5) |
| Collapse: Priority 1.60 vs 0.63 at rho=0.25 | as stated | 1.602 vs 0.630 | OK |
| WFQ 78% = PF; DPP 84% at rho=1 | 78, 84 | 78.3 (PF 78.3), 83.9 | OK |
| utility WFQ 72.3 -> 59.8; DPP 70.7 -> 61.9 | as stated | 72.32 -> 59.82; 70.71 -> 61.92 | OK |
| Priority 95.8%; video utility 1.75 vs 2.53; elastic 0.97 | as stated | 95.8%; 1.745 vs 2.530; 0.967 | OK |
| REPAY 1.06 vs 1.24 at rho=0.25 | as stated | 1.063 vs 1.241 | OK |
| REPAY rho=0: 69.2, 1.28, 1.86; Priority rho=1: 64.9, 0.97, 1.75 | as stated | 69.23, 1.277, 1.858; 64.94, 0.967, 1.745 | OK |
| RT success 95.8 vs 89.9 | as stated | 95.8 vs 89.9 (REPAY at rho=0 in this 4-seed T=3000 run; coincides with Table 1) | OK |
| **"buys it with a third of the elastic volume"** | a third | 0.967/1.277 = 0.76: a loss of **24%** (a quarter) | **MISMATCH (M-num, m3)** |
| Reverse: 40 devices, every one loses, mean -33 | as stated | n=40, share positive 0, mean -32.9 (DPP -144.6) | OK |
| Switching: 40 devices, L>=200, 40th percentile | as stated | 20 per seed x 2, `MIN_L=200`, `quantile_C=0.4` | OK |
| DPP gains 0.15 to 0.21 for every tau | as stated | 0.148, 0.205, 0.194, 0.167, 0.180 (tau 200, 5, 20, 60, 1) | OK |
| REPAY loses 0.03 to 0.05; best device +0.04; none above KB | as stated | -0.034 to -0.050; best +0.0376; 0/40 above KB at every tau | OK |
| Oracle: price-taking prediction 25 to 43 Mbit | as stated | 25.0 (tau=60) to 42.7 (tau=1) | OK |
| Oracle: mean -0.05 to -0.07; at most 1 in 5 gain | as stated | -0.050, -0.072, -0.060, -0.053; share positive 5, 0, 5, 20% | OK |
| Table 4 (oracle), 4 rows x 5 columns | as printed | 0 mismatches vs `oracle.json` | OK |

### 2.7 Business constraints, runtime

| Location | Paper | Recomputed | Status |
|---|---|---|---|
| theta_P sweep: premium ratio 1.28, 1.33, 1.40, 1.50 | as stated | 1.281, 1.334, 1.401, 1.496 | OK |
| RT success 92% -> 79% | as stated | 92.2% -> 79.4% | OK |
| max D/B 0.33-0.34 | as stated | 0.328, 0.341, 0.340, 0.337 (max over 3 seeds) | OK |
| "settle above targets for all V" (Fig. 6) | as stated | minima after slot 1000: premium 1.23, PAYG 1.14, free 2.02 (V=5,20,100) | OK |
| default tier constraints met "by every rule including PF" | as stated | Table 1 min premium 1.15 (Priority), PAYG 1.21, floor 2.62 | OK; constraints are not binding (disclosed) |
| Table 5 (binding), 6 rows x 6 columns | as printed | 0 mismatches | OK |
| weight-based rules "55%" premium; REPAY, DPP 99%, 98% | as stated | 0.549-0.551; 0.992, 0.979 | OK |
| utility 59.4 vs 72.6; RT 76% vs 89%; envy 17 | as stated | 59.43 vs 72.61; 76.1 vs 88.5; 16.6 | OK (88.5 rounds to 88 or 89) |
| WFQ = Priority identical in Table 5 | not discussed | identical to 1e-11 in all 5 seeds; verified genuine: with equal weights and no rationing the two coincide analytically (2000 slots, max difference 5.6e-13) | GENUINE |
| Runtime: bisection 1.5 -> 2.1 ms (10 -> 3000 devices) | as stated | 1.483 -> 2.086 ms | OK |
| conic 11 -> 23 ms (10 -> 300); agreement 1e-8 | as stated | 11.05 -> 23.41 ms; max relative gap 1.07e-8 to 1.14e-8 | OK, but see m9 |
| "about fifty bisection steps" | 50 | 43 evaluations of the response per slot (min 42, max 44; in simulation mean 39.7) | MINOR (m8) |
| "three orders of magnitude of headroom" | 3 | 1000 ms / 2.1 ms = 480x (2.7 orders) | MINOR (m8) |
| Analysis: B = 43 Mbit, "fourteen seconds of full-rate video" | 43, 14 s | 20x1x2+3 = 43; 43/3 = 14.3 s | OK |

## 3. Code audit findings (severity, file:line)

No CRITICAL finding. Items marked "checked, no issue" are included because the task asked for them.

**Baselines and metrics (checked, no issue unless noted)**
- `repay/mechanisms.py:238-262` PF and WFQ: exact water-filling (`solver.py:87-116`), RT caps at rmax, same utility log(1+x). No handicap. PF envy exactly 0 is genuine: elastic link rates (>=5) exceed RT caps (<=3) and weights are equal inside a tier.
- `mechanisms.py:286-329` Priority: admits at rmin in order (tier rank, gaming before video, arrival), raises video equally, elastic PF on the remainder. This is the strong version (the design note `03_final_design.md` §6 first planned admission at rmax). Not handicapped. WFQ x4 is untuned.
- `mechanisms.py:332-365` Credit: class-blind, credits unbounded (idle devices accumulate their whole share), no donor/borrower accounting of real Karma. Disclosed as an adaptation. Its low utility (64.4, below PF) comes from this design; it is not a bug.
- `sim.py:118-277` one loop computes all metrics for all mechanisms; the same trace is used for every mechanism and seed (`make_trace(seed)` has no dependence on the mechanism; `run` draws no randomness). Comparable.
- `sim.py:212-224` external class envy: reference = mean realised rate of declared-RT flows of the device's tier and class, capped at the device's demand, Lindley recursion, max over devices and both RT classes. Matches the paper's definition (Section 6.1) and is identical for all mechanisms.
- `sim.py:186-192` true utility: elastic log(1+usable), RT utility only if usable >= rmin. Not weighted by tier weight, while the operator objective is weighted (m12, disclosed as "true per-slot utility").

**MAJOR**
- **M5. `repay/` (no hold-down anywhere; `grep -i hold|tau` finds nothing).** `algorithm.tex` Algorithm 1, last line, states "a device that changes its declared class keeps the new class for at least tau slots" as part of the rule. The allocation code does not enforce it; the experiments impose the hold-down on the attacker (`exp_switching.py:33-42`). The theory (Thm. 3) assumes it, so the evaluation is consistent, but the text must say it is an assumption on devices. Also `mechanisms.py:77-83` (`_sync`) discards deficits when a device declares RT and restarts them at zero on return to E: this forfeiture is a rule of the implemented mechanism and it is what drives the oracle result. My ablation (seed 0, tau=5, 20 devices, `oracle_abl.py`): mean gain per slot -0.062 with forfeiture; -0.010 if deficits are kept (frozen) across RT phases; -0.007 if in addition the attacker is also served first in its group. So forfeiture accounts for about 84% of the oracle attacker's loss and incumbents-first ordering for about 5%. The paper's "two effects" explanation is supported, with forfeiture dominant. Fix: disclose (text below).
- **M6. `exp_strategic.py:21-26`, `exp_oracle.py:24`, `exp_switching.py:19`.** The deviation (Table 3), oracle and switching experiments use two traces; collapse four; tiers three; optgap three. The 60 deviators are 30 per trace and share one system, so they are not independent. Table 3 and Table 4 report no CI. The headline incentive claim rests on these. Fix: report bootstrap CIs over devices and say "two traces".

**MINOR (code / experiment)**
- **C1 `mechanisms.py:172-187` incumbents-first rounding.** Tested for bias in the deviation experiment (`devfirst.py`, seed 0, 30 deviators): putting the deviator first and treating it as an incumbent changes REPAY's mean relative gain from -3.1% to -2.4% and the share gaining from 50% to 53%; max gain/B 0.33. Not a material bias in the deviation test.
- **C2 `sim.py:186` and `params.py` rmax_V = 3.** A misreporting elastic device is capped at 3 Mbit/s while truthful elastic devices can take up to their link rate (5-30), and a declared-video device keeps a video allocation while it is idle (usable = 0). This applies to every mechanism. PF (which ignores the declaration) shows the pure cost of the cap: -7.6%. By tier, REPAY's mean relative gain is +1.4% for free-tier devices (38 of 60), -13.3% for premium (16) and -6.3% for PAYG (6): the negative mean is produced by the premium devices for which the cap binds, not by the mechanism's debt logic. See M1.
- **C3 `mechanisms.py:138-152` REPAY-WC branch.** `lam == 0 and all elastic at cap` never holds in the hotspot or home runs: REPAY-WC is bit-identical to REPAY in util, RT, envy and all seeds. The variant is not evaluated in any informative sense (m7).
- **C4 `exp_optgap.py:161-169` utility in the optimality-gap runs.** The reported "fluid" utility is fluid RT utility (a, z) plus realised elastic utility; the rounding pool is therefore counted twice (once as RT fluid, once as elastic rate). Checked (`optgap_check.py`, T=4000, V=5 and 20): paper metric 18.0810, pure fluid 18.0779, realised 18.0768 at V=20; 17.6981, 17.6917, 17.6870 at V=5. Maximum inflation 0.006 (pool active in 24 to 93 of 4000 slots). Negligible, but "fluid utility" in the text is not exactly what is computed (m10).
- **C5 `exp_optgap.py:22,99-107`.** theta_P = 0.5 and phi = 0.15, only tiers F and P, premium and free-floor constraints in expectation, envy constraints through the affine majorant (`affine`, line 48). The benchmark solves the problem of Eq. (bench): premium, free floor and majorant-envy-in-expectation, with `A<=1`, `Y in [A rmin, A rmax]`, perspective video utility, capacity per scenario. Correct and consistent with the theorem. The majorant makes the constraint stricter than Definition 1 (reference a*min(z,d) <= majorant), while the simulated REPAY updates deficits with the true reference (`mechanisms.py:165`); envy in `exp_optgap.py:169` is measured against the majorant. This is consistent with the proof (drift uses the majorant) but is not what the abstract says (see M3).
- **C6 `exp_runtime.py:140-151`.** For N=100 and 300, CLARABEL returned a non-finite `prob.value` in 5 of 5 and 4 of 5 instances (`cvxpy_raw_value_nonfinite`); the objective was recomputed at the conic primal point. The 1e-8 agreement is therefore about that recomputed objective (m9).
- **C7 `exp_strategic.py:129,135-140` summary statistic.** `rel_gain` is gain / truthful volume per device, averaged over devices: dominated by low-volume devices. See M1.
- **C8 deficit bound.** D/B max over all REPAY-family compare runs: REPAY 0.377, REPAY-E 0.377, WC 0.377, No-debt 0.592 (hotspot). All below 1; consistent with Thm. 1 and `tests/test_bound.py`.

## 4. Reproducibility check

| Run | Stored (`results/*.json`) | Re-run | Result |
|---|---|---|---|
| hotspot seed 0, T=6000, REPAY | util 72.281866146, RT 0.887478705, el 1.664728723, env 18.291297 | identical to 9 digits | exact |
| same, PF | util 70.523041561, RT 0.817795833, env 0 | identical | exact |
| same, Priority | util 76.643258538, RT 1.0, el 1.148876946, env 1635.022282 | identical | exact |
| strategic, seed 0, device 1 declares video, T=3000, REPAY | vol_truth 644.736753, vol_dev 326.469618 | identical | exact |
| same, Priority | 611.449139, 437.838892 | identical | exact |
| `pytest -q tests` | | 48 passed in 51 s | pass |
| `cap_violations` in all compare runs | 0 | | OK |

Run-to-run determinism is bit-exact, so the stored JSON can be regarded as produced by the shipped code. No run logs or exit codes are stored; determinism substitutes for them.

## 5. Phase D (originality) and Phase E (claim verification)

Phase D (not a plagiarism or literature check; citations are covered by another agent). The novelty claims are hedged and acceptable: "Credit-based sharing is not a new idea" (intro, related work); "we do not claim the technique, only its use" (virtual-queue bounds); the contribution is stated as "narrower and complementary". One unverifiable negative-existence claim remains: "We found no drift-plus-penalty or constrained-online-learning result with guarantees per agent over a finite sojourn, nor one that enforces envy constraints through virtual queues" (related.tex). Suggested: "To the best of our search (Section on related work covers X-Y), we did not find...". Status: OK with hedge; no overclaim, no "first" or "novel" wording anywhere in abstract, intro, discussion.

Phase E (high-impact claims: headline, numerical, causal, methods-critical):

| Claim | Status |
|---|---|
| Deficit <= V w eta + rmax on every path (abstract, Thm. 1) | Supported analytically; empirical D/B <= 0.59 in all runs; 48 tests incl. adversarial prices in [-40,40] |
| "no device gains more than 0.39 of its bound" | Supported for the family (0.388); REPAY 0.322 (m5) |
| REPAY serves 90% vs 82% for PF at the same throughput | Numbers OK; "same" slightly off; gain is entirely in the free tier (RT success free tier: REPAY 83.3%, PF 70.0%; premium and PAYG are 99-100% under both); Priority and WFQ serve 100% and 98.7% with higher utility (74.8 and 73.9 vs 70.7) (M4, m4) |
| Misreporting "loses 3%" under REPAY | Not supported as stated (M1) |
| "gains 320% / 272% / 57%" | Numbers are means of ratios (M1) |
| Near-optimality within O(1/V) of best policy meeting business constraints and EF on average | Theory OK; experiment checks envy only, tier constraints slack, gap x V not constant (M3) |
| "tier constraints are met 99% vs 55%" | OK, but the weight-based baselines have no mechanism to meet commitments; the fair comparison is REPAY vs plain DPP (paper says so) |
| "Experiments do not show a hold-down is needed" | Honest and supported (oracle loses -0.05 to -0.07; with forfeiture removed the loss shrinks to -0.01, still not positive) |
| "A random search over price-taking environments produced differences of either sign" (analysis.tex) | Documented only in `research/03_final_design.md` L3 and `research/02_algorithm_design.md`; no script in the repository (m14) |
| "we showed that such inflation is worth at most one envy bound of credit" | One-line argument in "Other manipulations"; repeated accumulation is not excluded; "showed" is too strong (m15) |

## 6. 7-mode AI research failure checklist

| # | Mode | Outcome | Evidence |
|---|---|---|---|
| 1 | Implementation bug passing self-review | **CLEAR** | Code read line by line (solver, mechanisms, sim, all experiments). 48 tests pass, solver agrees with CLARABEL to 1e-8, deficit bound tests with adversarial prices. Bit-exact reproduction (section 4). No suspicious constants: CIs vary across rows and conditions. The three "identical" results are explained: WFQ = Priority (home, equal-weight binding table) verified per slot, analytic; REPAY-WC = REPAY because the branch never fires (C3); REPAY vs DPP at rho=1 coincide because no elastic device remains. Residual issues are minor (C4, C6). |
| 2 | Hallucinated citation | **Covered elsewhere** | Not assessed here. |
| 3 | Hallucinated experimental result | **CLEAR** | Every number traced to JSON; all six tables reproduce with 0 mismatches; seed, slot and device counts match the scripts (10/5/5/2/2/2/4/3/3/5 seeds as listed in 2.x). Wrong or loose statements found (M2, "a third", "about fifty", "three orders") are descriptive slips, not invented runs. |
| 4 | Shortcut reliance | **SUSPECTED (mild, flag-only)** | (i) The REPAY deviation "loss" is largely the 3 Mbit/s video cap on high-rate devices (PF shows -7.6% from the cap alone; free-tier REPAY deviators gain +1.4%). (ii) No ablation isolates the elastic bonus from the debt price on RT groups (No-debt keeps the bonus; DPP drops both). (iii) No capped-priority or quota baseline, WFQ weight 4 untuned. (iv) Default tier constraints are not binding and the optgap benchmark has slack tier constraints, so the tier-queue machinery is exercised only in the equal-weight table. (v) The RT-success gain over PF comes entirely from the free tier. None of these makes a reported number wrong; they limit what the numbers show (M1, M3, M4). |
| 5 | Bug reframed as insight | **CLEAR** | The surprising results were checked: (a) oracle attacker loses although the price-taking prediction is +25 to +43 Mbit: ablation shows 84% of the loss comes from deficit forfeiture and 5% from incumbents-first ordering (section 3, M5), both implemented and disclosed; (b) REPAY misreporters "lose": ordering bias tested (-3.1% vs -2.4%), cap effect separated by PF; (c) REPAY above slot-wise EF optimum at V=10: consistent with time-shifting (0.35 range), and the double-counting check shows <= 0.006 inflation. |
| 6 | Methodology fabrication | **CLEAR with required edits** | Scenario and parameter text matches the code except the mean capacity (96 vs 91) and the hold-down, which the algorithm box presents as part of the rule but the code does not enforce (M5). Optgap parameters (theta_P=0.5, three seeds, 200 support points) are not all stated (m11). |
| 7 | Frame-lock | **CLEAR** | The framing (class envy, bounded deficits, approximate IC) is stated with its limits: permanent shortage, price-taking, downlink-only, synthetic traces. The design notes show frame changes made during work (committed demand instead of raw demand, majorant, Priority redesign, hold-down necessity as Prop. 5). Residual: V=20 and C_mean=150 were fixed in the design stage (V in [10,100] there) and not tuned after results as far as the repository shows (no history inspected, as git was not allowed); results are shown across V in Sections 6.2-6.3. |

Blocking rule (Modes 1, 3, 5, 6 must not be SUSPECTED or INSUFFICIENT): satisfied. Mode 4 is flag-only at this stage.

## 7. Findings list

**MAJOR (must fix or disclose)**
- M1. Abstract and Sec. 6.5 (strategic): misreporting gains are means of per-device ratios (n=60, 2 traces). "Roughly quadruples the volume" is false for volume (pooled +106% Priority, +100% WFQ, +26% DPP; median +164, +142, +59). "Loses 3%" under REPAY has bootstrap 95% CI [-6.7%, +0.1%], median -0.8%, pooled -8.1%, free-tier devices +1.4%. Priority per-seed 201% vs 439%.
- M2. Setup: mean capacity "about 96" is 91.
- M3. Optgap: tier constraints slack (e_PS -5.9, e_FF -4.7), theta_P = 0.5, majorant envy stricter than Definition 1; "gap x V between 2 and 3.1 ... as the B0/V bound predicts" (gap x V = 1.96 to 3.08, rising for V>=20; B0 is orders of magnitude larger, so the bound is not tested). The abstract and intro claim optimality against "the best policy that satisfies the business constraints and is envy-free between classes on average": the experiment tests only the envy constraints.
- M4. Abstract headline selective: against PF only; "at the same throughput" (-1.7%, significant); Priority/WFQ have higher RT success and utility when truthful; gain concentrated in the free tier.
- M5. Hold-down not implemented in the mechanism; forfeiture of deficits on class change is an undeclared rule in the algorithm box.
- M6. Strategic experiments: 2 traces (4 for collapse, 3 for tiers/optgap), no CIs in Tables 3-4, devices within a trace are dependent.

**MINOR**
- m1. Table 1 caption: ratios are raw served/committed volumes, not "relative to targets".
- m2. Priority description omits gaming-before-video ordering.
- m3. "a third of the elastic volume" is 24%.
- m4. "closes roughly 45%": 44%; "no cost to elastic devices": -1.7%.
- m5. "0.39 of its bound" is the No-debt maximum; REPAY 0.32.
- m6. "class envy about 2000": 1981-2212.
- m7. REPAY-WC identical to REPAY in all runs; "almost identically".
- m8. "about fifty bisection steps" is 43; "three orders" is 2.7; the full allocation step (rounding, bookkeeping) costs 3.5-3.9 ms/slot in the simulator at 75 devices (compare.json `ms_per_slot`).
- m9. Conic agreement of 1e-8 is on the objective recomputed at the conic primal point (CLARABEL raw value non-finite in 9 of 20 instances).
- m10. "Fluid utility" in optgap = fluid RT utility + realised elastic utility (difference <= 0.006), weighted by tier weights, unlike the unweighted utility in Table 1.
- m11. Not stated in the text: seeds and horizons per experiment (collapse 4 seeds T=3000; tiers 3 seeds T=12000/6000; binding T=8000; variability 5 seeds; optgap 3 seeds, theta_P=0.5, phi=0.15, sigma=0.2), lognormal sigma 0.15, min sojourn 5.
- m12. Utility in Tables 1-2 is unweighted by tier; operator objective is weighted.
- m13. "constant capacity: every rule serves the RT flows": PF 99.1%.
- m14. "random search" claim: no script in the repository.
- m15. "we showed that such inflation is worth at most one envy bound": not shown for repeated accumulation.
- m16. Alpha-fair substitution is claimed ("any alpha-fair utility can be substituted") but `Params` raises NotImplementedError for alpha != 1 (untested claim).

## 8. Required corrections to the paper text (old -> suggested new)

1. experiments.tex, Setup: "the mean is about $96$~Mbit/s" -> "the mean is about $91$~Mbit/s".
2. abstract.tex: "A device that falsely declares video gains $320\%$ in volume under strict priority, $272\%$ under weighted fair queueing and $57\%$ under utility-maximising scheduling without deficits, and loses $3\%$ under \repay{}." -> "In an exact unilateral test on $60$ devices from two synthetic traces, a device that falsely declares video gains $164\%$ in volume (median) under strict priority, $142\%$ under weighted fair queueing and $59\%$ under utility-maximising scheduling without deficits, whereas under \repay{} the change is $-0.8\%$ (median; mean $-3\%$, 95\% bootstrap interval $-7\%$ to $0\%$)."
3. abstract.tex: "\repay{} serves $90\%$ of real-time slots against $82\%$ for proportional fairness at the same delay-tolerant throughput." -> "with truthful devices \repay{} serves $90\%$ of real-time slots against $82\%$ for proportional fairness, at a $2\%$ lower delay-tolerant rate; strict priority serves all real-time slots but leaves elastic devices $28\%$ less than \repay{}."
4. experiments.tex, compare: "It closes roughly $45\%$ of the gap in RT success between \textsc{PF} and \textsc{Priority} at no cost to elastic devices." -> "It closes $44\%$ of the gap in RT success between \textsc{PF} and \textsc{Priority} at a $1.7\%$ lower elastic rate (paired difference $-0.03\pm0.004$~Mbit/s) and a higher utility ($+2.0\pm0.4$); the gain is in the free tier ($83\%$ against $70\%$ of RT slots), since paid tiers are served in more than $99\%$ of slots by every weighted rule. When all devices are truthful, \textsc{Priority} has the higher utility ($74.8$ against $70.7$); its defects are envy and incentives."
5. experiments.tex: "The three variants behave almost identically here: ... so there is nothing to recycle." -> "\textsc{Repay-WC} coincides with \repay{} in every run, because its recycling condition is never met, and \textsc{Repay-E} differs only in the third decimal: ..." (keep the remaining explanation).
6. experiments.tex, Table 1 caption: "Ratios are relative to the targets $\theta_P=0.8$, $\theta_Y=0.6$ and the free-tier floor." -> "Premium and PAYG ratios are served volume over committed demand, the free-floor ratio is served volume over the floor; the targets are $\theta_P=0.8$, $\theta_Y=0.6$ and $1$."
7. experiments.tex, Baselines: "flows are admitted at $\rmin_k$ in order of tier and arrival while capacity lasts" -> "flows are admitted at $\rmin_k$ in order of tier (premium, PAYG, free), gaming before video, and arrival while capacity lasts".
8. experiments.tex, optgap: "the product of gap and $V$ stays between $2$ and $3.1$ for $V\ge5$, as the $B_0/V$ bound predicts" -> "the product of gap and $V$ is between $1.96$ and $3.08$ for $V\ge5$, of the order expected from the $O(1/V)$ bound (the constant $B_0$ of Theorem~\ref{thm:opt} is far larger, so the bound is not tight)." Add after "compute the benchmark": "(with $\theta_P=0.5$, $\phi=0.15$; both tier constraints turn out to be slack here, by $5.9$ and $4.7$~Mbit/s on average, so the gap is determined by the envy constraints, which are imposed through the affine majorant and are therefore stricter than Definition~\ref{def:envy}; three seeds)."
9. abstract.tex and intro.tex (Near-optimality item): "the best policy that satisfies the business constraints and is envy-free between classes on average" -> keep, and add in the experiments paragraph above the disclosure that the experiment exercises the envy constraints only.
10. experiments.tex, strategic: "Under \textsc{Priority} and \textsc{WFQ} misreporting roughly quadruples the volume ($+320\%$ and $+272\%$ on average), and almost every device gains." -> "Under \textsc{Priority} and \textsc{WFQ} the average device multiplies its volume by $4.2$ and $3.7$ (mean of per-device ratios; median $+164\%$ and $+142\%$, pooled volume $+106\%$ and $+100\%$), and almost every device gains."
11. experiments.tex: "Under \repay{} the deviation \emph{loses} $3\%$ on average;" -> "Under \repay{} the deviation changes the volume by $-3\%$ on average (95\% bootstrap interval $-7\%$ to $0\%$, median $-0.8\%$); free-tier devices ($38$ of the $60$) gain $1.4\%$ on average and the loss is concentrated in premium devices, for which the video cap $\rmax_V=3$~Mbit/s binds (class-blind \textsc{PF}, which pays only this cap, loses $7.6\%$);"
12. experiments.tex: "No device gains more than $0.39$ of its bound $B_{g,V}$" -> "No device gains more than $0.32$ of its bound $B_{g,V}$ ($0.39$ for the no-debt variant)".
13. experiments.tex, collapse: "it buys it with a third of the elastic volume" -> "it buys it with a quarter of the elastic rate ($0.97$ against $1.28$~Mbit/s)".
14. experiments.tex, Variability: "With constant capacity every rule serves the RT flows." -> "With constant capacity every rule serves at least $99\%$ of the RT slots." and "serve about $71\%$ of RT slots" -> "serve $70$--$72\%$ of RT slots".
15. experiments.tex, Runtime: "about fifty bisection steps per slot" -> "about forty bisection steps per slot"; "One-second slots therefore leave three orders of magnitude of headroom." -> "One-second slots therefore leave more than two orders of magnitude of headroom (the complete allocation step, with rounding, takes $3.6$~ms per slot at $75$ devices in our simulator)."; after "agrees with the bisection to a relative difference of $10^{-8}$ in the objective" add "(objective evaluated at the conic solver's primal point)".
16. algorithm.tex, Algorithm 1 last line: "a device that changes its declared class keeps the new class for at least $\tau$ slots" -> "assumption on devices: a device that changes its declared class keeps the new class for at least $\tau$ slots (enforced on the attackers of Section~\ref{sec:exp-strategic}, not by the allocation code); the allocation discards a device's deficits while it declares an RT class and restarts them at zero when it returns to $E$".
17. experiments.tex, Setup (add one sentence): "Unless stated otherwise: Section~\ref{sec:exp-bound}: 5 seeds; comparison: 10 seeds; variability: 5; business constraints: 3 seeds (default) and 5 (binding); deviation, oracle and switching experiments: 2 traces of 3000 slots; collapse: 4 traces; optimality gap: 3 seeds. Capacity noise is lognormal with $\sigma=0.15$; sojourns are at least 5 slots. All traces are synthetic."
18. experiments.tex, Strategic, Table 3 caption: add "(60 devices from two traces; devices of one trace are not independent)".
19. analysis.tex: "A random search over price-taking environments produced differences of either sign." -> "A numerical search over price-taking environments (script in \texttt{experiments/}) produced differences of either sign." and add the script to the repository, or replace by an explicit counterexample.
20. analysis.tex, Other manipulations: "since deficits never exceed $B_{g,k}$, so does the credit obtained in this way" -> "since deficits never exceed $B_{g,k}$, the credit held at any time obtained in this way is at most $B_{g,k}$; we do not bound credit that is accumulated and redeemed repeatedly". Discussion: "we showed that such inflation is worth at most one envy bound of credit" -> "the credit held at any time is at most one envy bound".
21. discussion.tex, Modelling choices: add "The main comparisons use fixed values of $V$, the tier weights and the capacity level (tier constraints are slack by default); deviation experiments use two traces, and the gain of misreporting is measured relative to a $3$~Mbit/s video cap."
22. model.tex: "any $\alpha$-fair utility ... can be substituted" -> add "(our implementation uses $\alpha=1$)".

## 9. Final verdict

Phases C-E: **FAIL** (6 MAJOR items require text correction or disclosure; 0 CRITICAL). All fixes are edits to the paper text; no experiment needs to be rerun, except that adding bootstrap CIs to Tables 3-4 (M6) can be done from the existing JSON. Re-verification after the corrections is expected to PASS: the data, code and results are consistent and reproducible.
