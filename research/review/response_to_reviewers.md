# Response to the simulated review (round 1)

Reports: `R1_theory.md`, `R2_experiments.md`, `R3_editor_devil.md`; numeric re-check in `../integrity/04_recheck_numbers.md`. All three recommended major revision. This note lists what was changed, what was answered by a new experiment, and what was not done.

## Changed in the text

| Concern | Action |
|---|---|
| R1-M1 fluid vs rounded allocation | Algorithm section now states which theorem holds for which allocation: the deficit bound for the rounded allocation, the utility theorem for the fluid one only. The false sentence about the fluid reference dominating the realised average rate was replaced by the correct bound. The bias that rounding introduces in the tier queues is stated as not bounded. |
| R1-M2 benchmark of the utility theorem | The text now says the benchmark allows time-shifting across capacity draws within a population state only, that it reduces to slot-wise envy-freeness under constant capacity, and that no claim is made about the best bounded-envy policy. Conclusion reworded. |
| R1-M3 capacity assumption | Stated that Markov-modulated capacity is outside the assumption unless the regime is part of the state; only the optimality-gap experiment (i.i.d. capacity) satisfies it. The referee's remark that this experiment also violates it is not correct: capacity is drawn independently in each slot there. |
| R1-M4 incentive claims | "Large-market" removed as a description of the result; Lipschitz hypothesis for utility gains stated, with the threshold-preference caveat; order of magnitude of the price-taking correction (L z / n) given; additive rmax slack under rotation stated; "costs them nothing" removed. |
| R1-M5 identity | A device is defined as an authenticated identity; multi-identity subscribers and reconnection are listed as outside the guarantees. |
| R1-M6 novelty | The deficit bound is described as a deterministic queue bound of a known kind; the specific contribution is the per-device envy queue and the cancellation of tier prices. |
| R1-M7 combined trade-off | New paragraph: the two bounds cannot both be small with the proved constants. New table of the bound against realised volume and envy. |
| R1 corrected statements 1, 3-9, 12 | Applied. |
| R2-M1, R3-1 premise | Introduction states the working assumption (class as declared) and why; new related-work paragraph on Diffserv marking, learned classification, flow queueing (FQ-CoDel, CAKE) and L4S. |
| R2-M4 statistics | Confidence intervals now use Student-t quantiles; paired differences reported for the main comparison. |
| R2-M5, R3-2 claims | Abstract now gives the RT success of plain DPP and strict priority and says that about half of the devices still gain by misreporting under REPAY. |
| Integrity re-check items 1-7, 9, 10 | Applied. |

## Answered by new experiments

| Concern | Experiment | Result |
|---|---|---|
| R2-M3 single operating point; no capped-priority baseline | `exp_frontier.py` | REPAY dominates plain DPP and WFQ on RT success vs elastic rate. Capped priority with a well-chosen cap dominates REPAY on that pair of metrics, with 20 times the class envy and incentive resistance that depends on the cap. Reported as such. |
| R2-M4, R3-3 short stays excluded | `exp_short_stays.py` | Under REPAY 83% of devices staying under a minute gain by misreporting (median +10%); far less than under the other class-aware rules, but not zero. |
| R2-M2 call continuity, rotation | `exp_continuity.py` | Outages under REPAY: 14% of slots, 3.9 s mean. Rotation is not the cause (two alternative admission orders give the same figures). |
| R3-2 ablation of forfeiture and rotation | `exp_oracle_ablation.py` | Forfeiture of deficits is what makes the oracle switching attack unprofitable; without it most devices gain a little. |
| R3-3 size of the bound | Table in the bound section | B is 17-25% of the volume of a median stay at V=20. |

## Not done

- No real traces, no packet-level (ns-3 or access-point) validation, no latency model, no airtime/PHY-rate capacity model. Stated as limitations.
- No analytical bound on the price-taking correction, and no bound on the bias that rounding introduces in the tier queues.
- No benchmark with long-run per-device envy constraints for the utility theorem.
- No noisy-classifier model, no learning or best-response adversaries, no Sybil analysis.
- No finite-transfer workload; no sweeps over class mix, load and sojourn length; no revenue comparison with priced priority.
- No class-aware credit baseline and no run of the Jaramillo-Srikant scheme.
- The paper was not shortened; it grew from 30 to 34 pages.
- Switching, oracle and reverse-deviation experiments still use two traces.

## Round 2

The verification review (`R4_rereview.md`) asked for a further, narrower revision. Its ten text-level points were applied: the capped-priority result and the short-stay result are now in the abstract, introduction and conclusion; the theorem scopes in the abstract carry their conditions; the collapse paragraph reports the PF control; the remaining overclaims and small errors it listed were corrected; dependencies are pinned in `requirements.txt`. Its list of new work (real or packet-level traces, noisy classifier and flow-queueing baselines, class-aware credit baseline, sweeps over traffic mix, a bound on the rounding bias and on the price-taking correction, more traces for the switching attacks, shortening) remains open and is listed under "Not done" above.
