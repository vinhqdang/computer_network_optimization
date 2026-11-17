# Referee check of the theory (model.tex, algorithm.tex, analysis.tex, appendix.tex, intro/abstract)

Scope: statement-by-statement verification of every lemma/proposition/theorem, adversarial numerical tests against the actual solver (`repay/solver.py`) and `Repay` (`repay/mechanisms.py`), and consistency with the abstract/introduction. Scratch scripts are in
`(session scratch directory)`
(`slot_test.py`, `tol_test.py`, `cvx_test.py`, `adv_path.py`, `baselines.py`, `commit_ex.py`, `dyn_gain.py`, `realdev.py`, `thin.py`).

## Summary table

| # | Item | Verdict |
|---|------|---------|
| 1 | Lemma (concavity), majorant, a=0 | CORRECT WITH FIXES (majorant is stated, not proved; the surrounding text mis-describes it; domain remarks) |
| 2 | Proposition (solver) | CORRECT WITH FIXES (complexity expression, undefined N_t, scope of strict concavity, finite-tolerance meaning) |
| 3 | Theorem (deficit bound) + Remark | CORRECT for the exact, fluid solver; CORRECT WITH FIXES as written (tolerance slack, stationarity wording, the n/(n+1) remark needs a uniform-in-t form) |
| 4 | Corollary (window envy), Lindley identity | CORRECT (small fixes: index t+1, reset on class change) |
| 5 | Price-taking, static, dynamic, commitment | Static: CORRECT. Dynamic: CORRECT WITH FIXES (count of intervals K, class-constant intervals). Commitment proposition: GAP/overstated conclusion. "Identity" is an inequality. |
| 6 | Reverse deviation | CORRECT (fluid, zero-deficit slots, exact solver); hypotheses and meaning of price-taking must be spelled out |
| 7 | Utility / violation theorem | CORRECT WITH FIXES (algebra right; benchmark mis-described; needs exogenous demand caps, fluid allocation, state-wise feasibility) |
| 8 | Baselines | CORRECT (checked numerically for C in (0.5,1)); two unstated conditions |
| 9 | Consistency with abstract/intro | Several overclaims (see list) |
| 10 | Missing assumptions / notation | Listed below |

No counterexample to Theorem 1 was found (240k slot-level checks, adversarial paths, random tier prices in [-40,40]). The issues are claim-versus-proof mismatches, not an error in the core bound.

---

## 1. Lemma (concavity of the per-slot problem)

**Majorant.** With `m_d(z) = sigma + s z`:

* `d >= rmax`: `m = z = min(z,d)` on `[rmin,rmax]`. Equality. OK.
* `d <= rmin`: `m = d = min(z,d)` for `z >= rmin >= d`. Equality. OK. (When `rmin=rmax` and `d=r_G` the two cases coincide and give the same value; gaming is covered.)
* `rmin < d < rmax`: `s=(d-rmin)/(rmax-rmin) in (0,1)`, `sigma=(1-s)d`, so `m(d) = d`. `m` is the line through the kink `(d,d)` of the concave function `z -> min(z,d)` with slope `s in [0,1]`, i.e. a supporting line, hence `m(z) >= min(z,d)` for **all** real `z`, with equality only at `z=d`. This is correct. The line is *not* the chord through `(rmin, rmin)` and `(rmax, d)` (that chord has intercept `(1-s) rmin` and is a minorant of a concave function); a reader who tries to verify "chord" will fail. The paper gives no proof at all; add one line.
* Equality for `d` outside `(rmin,rmax)`: correct, as above. Inside the interval equality holds only at `z=d`, and the gap at `rmin` is `(1-s)(d-rmin)`, at `rmax` is `s(rmax-d)`; so the debt price overcharges in the interior case. This is harmless for all proofs (they only use `r <= a m`) but it means the benchmark class of Theorem `opt` is defined through `m`, not through the true reference (see item 7).

**Concavity.** `(a,y) -> a u_k(y/a)` is the perspective of a concave function: jointly concave on `a>0`. On the feasible cone `a rmin <= y <= a rmax`, `u_k` is bounded, so the value tends to 0 as `a -> 0` and the closure (value 0 at the origin) is continuous on the feasible set, hence concave there. The debt terms are linear (`a m_d(y/a) = sigma a + s y`). Elastic terms `V w log(1+x) + (beta+D_i) x` concave. Constraints linear. Gaming: `u_G = 1` gives the linear term `a`, with `y = a r_G`. **CORRECT.**

**a = 0.** At `a=0` forced `y=0`, `z` is undefined, the reference is `a min(z,d)=0` regardless, and the term `-zeta a` vanishes. Consistent everywhere (Theorem `bound` treats `a=0` as `r=0`). One gap: groups with `n_{g,k}=0` are excluded from (slot), whereas elastic devices of that tier still carry `D_{i,k}`; in (dpp) the term `-D_{i,k}(a m - x_i)` must be read with `a=0`, giving `+D_{i,k} x_i`, which is exactly what `D_i x_i` in (slot) contains. This is correct but should be said (it matters in the appendix, where the benchmark must also set `a^pi = 0` for empty groups).

Domain remark to add: `rmin_k > 0`, `w_g > 0`, `u_k` bounded on `[rmin,rmax]` (otherwise `eta_k` is infinite and the perspective closure is not continuous at the origin).

**Verdict: CORRECT WITH FIXES.** Fix (LaTeX), to insert after (eq:maj):

```latex
For $\rmin_k<d<\rmax_k$, $m_d$ is the line through the kink $(d,d)$ of the concave function
$z\mapsto\min(z,d)$ with slope $s\in(0,1)$; a supporting line of a concave function lies above it,
so $m_d(z)\ge\min(z,d)$ for all $z$, with equality only at $z=d$.
```

## 2. Proposition (solver)

* **Strong duality.** Concave objective, linear constraints, a feasible point (zero allocation) with the capacity strictly slack: duality holds with an attained `lambda* >= 0`. Fine (for linear constraints Slater is not even needed beyond feasibility).
* **Uniqueness/continuity.** `x_i(lambda)` is unique and continuous (clip of `Vw/p-1`; as `p->0+` it tends to `d`). `z*(lambda)` unique and continuous by strict concavity of `psi` in `z` (for video; the closed form `z* = clip(nVw/q)` is right, with `q = n(lambda-beta)+pi`, and `z*=rmax` for `q<=0`). For gaming `z` is fixed. **Scope issue:** the model only assumes `u_k` concave; uniqueness and continuity need *strict* concavity. State "for strictly concave `u_k`" (for non-strict `u_k` the monotone selection `z*` can jump and `S` has further discontinuities).
* **Monotonicity of `S`.** `x_i` nonincreasing. `partial^2 psi/ partial z partial lambda = -n < 0`, so by Topkis `z*` is nonincreasing. `max_z psi` is nonincreasing (envelope, `psi` decreasing in `lambda` pointwise), so `a* = 1{psi>0}` is nonincreasing. Group load `n a* z*` is a product of two nonincreasing nonnegative terms. **Correct.**
* **Marginal groups.** For lambda<lambda* the maximum of `psi` is strictly positive (derivative `-n z*<0`), for lambda>lambda* strictly negative, so `S(lambda*-)` has all marginal groups at `a=1`, `S(lambda*+)` at `a=0`; any split filling the capacity is optimal because `psi=0`. `S(infinity)=0<C`, so a finite bracket exists. Several simultaneous marginal groups are handled by the cumulative fill in the code. Correct. The statement "generically at most one" is fine but unnecessary.
* **Finite tolerance.** "returns an optimal solution as the tolerance tends to zero" is correct, but with tolerance `delta = lambda_hi - lambda_lo` the output is only `O(delta)`-suboptimal and, importantly, does *not* satisfy the KKT conditions exactly; Theorem `bound` then needs a `+delta` (item 3).
* **Complexity.** `O((N_t + |K|*3) log(1/eps))` is odd: `N_t` is not defined anywhere; `|K|*3` is the number of groups (at most 3 tiers times `|K|` classes), which is at most `N_t` if `N_t` counts all active devices (every nonempty group has a member), so the expression collapses to `O(N_t log(1/eps))`. Moreover (i) "relative tolerance" is not meaningful if `lambda*` is `0` or tiny; the code uses an absolute floor `max(1, lambda_hi)`; (ii) the bracketing phase costs `O(log lambda*)` evaluations and `lambda*` is unbounded in principle (tier prices `beta` are not bounded by any theorem), so the cost is `O(N_t (log lambda* + log(1/eps)))`; (iii) the post-processing in the implementation (`argsort` for the leftover and the rounding by `lexsort`) is `O(N_t log N_t)`. The introduction's "in time linear in the number of devices" is inaccurate by the `log(1/eps)` factor and the sort.

**Verdict: CORRECT WITH FIXES.** Replace the complexity sentence by:

```latex
One slot costs $O\big(N_t\,(\log^+\lambda^\ast+\log(1/\epsilon))\big)$ operations for $N_t$ active devices
(elastic devices and RT flows) and absolute multiplier tolerance $\epsilon$, plus $O(N_t\log N_t)$
for the rounding and for handing out the leftover.
```

and add "if $u_V$ is strictly concave" to the uniqueness sentence. I also recommend the empirical check: `cvx_test.py` compared the solver against cvxpy (CLARABEL, perspective via `rel_entr`) on 597 random slots with negative/large `beta`, marginal groups, gaming, `d` below/inside/above `[rmin,rmax]`; worst relative suboptimality `2.4e-7`, all outputs capacity-feasible.

## 3. Theorem (deficit bound) and Remark

Step by step.

1. *Case `a=0` or empty group:* `r=0 <= x`. OK.
2. *Case `x=d`:* `r = a min(z,d) <= d = x`. OK.
3. *Case `a>0`, `x<d`.* The correct rigorous form: `x_i` maximises the Lagrangian `V w u(x) + (beta + D_i - lambda) x` over `[0,d_i]`. If `x_i<d_i` the right derivative at `x_i` is `<= 0`: `V w u'(x_i) + beta + D_i - lambda <= 0`. This covers `x_i=0` (inequality) and `x_i>0` (equality). The text says "since `x_i` can be increased" which suggests a primal feasibility argument (capacity may be full); the Lagrangian argument is the correct one. Because `u'>0` and `D_i = sum_k D_{i,k} >= D_{i,k} = D` (all deficits nonnegative; this is exactly where several RT classes enter and it is fine), `lambda - beta >= V w u'(x_i) + D_i > D`. **`u'>0` is used and is essential**; `u'<=1`, advertised in model.tex as part of "the analysis only uses", is used nowhere.
4. *Homogeneity.* The group's Lagrangian term `L_g(a,y) = nVw a u_k(y/a) + (n beta - pi - n lambda) y - zeta a` is positively homogeneous of degree 1 on the cone `{a rmin <= y <= a rmax}` intersected with `a <= 1`, which is correct (the feasible set of one group is exactly a cone intersected with a half-space). The conclusion "value at a maximiser is `>= 0`" is correct, but the homogeneity argument is a detour: `(a,y)=(0,0)` is feasible with value `0`, so the maximal value is `>= 0` trivially. Ties and fractional `a` are covered: a marginal group has value exactly `0`; (pf2) is a weak inequality and (pf1) strict, so `D >= Theta` is excluded in all cases with `a>0`, `x<d`.
5. *Use of `pi, zeta >= 0`.* `pi = sum D s >= 0` since `D>=0` and `s in [0,1]`; `zeta = sum D sigma >= 0` since `sigma >= 0` (`sigma = d` or `(1-s)d` or 0, with `d>=0`). So `pi z + zeta >= 0` and `n V w u_k(z) >= n(lambda-beta) z` follows, then division by `n z > 0` (`rmin_k>0` needed, not stated) gives `lambda-beta <= V w u_k(z)/z <= V w eta_k = Theta`. No sign assumption on `lambda - beta` is used. **Arbitrary real tier prices:** `beta` enters only through `lambda - beta`, once for the elastic device and once for its own tier's group (same `beta_g` multiplying the rate of both), so it cancels. Correct for any real `beta_{g,t}` (even adaptively chosen).
6. *Induction.* If `D(t) < Theta`: `D(t+1) <= D(t) + r < Theta + rmax` (`r <= a min(z,d) <= rmax`). If `Theta <= D(t) <= B`: `r <= x`, so `D(t+1) <= D(t) <= B`. Correct. Note it also proves `D(t+1) <= B` for the last slot of the sojourn (needed in the Corollary, which uses `D(t+1)`; the theorem statement only says "every slot `t` of its sojourn"; state "for every `t` up to and including the slot after the last").
7. *Rounding.* The deficit update uses the fluid reference `a min(z,d)` and the realised `x_f >= x_fluid` (the leftover pool is only added to elastic devices, clipped at `d`). Since `r <= x_fluid` is what is proved, `r <= x_f` and the recursion is unchanged. Also checked for the variants: REPAY-WC (capacity recycled only if `lambda=0` and all `x=d`, so `r <= d = x`), REPAY-E (entrant offer: `psi(z;lambda,n=1) > 0` gives the same chain (pf2) because `pi,zeta>=0`), No-debt (`pi=zeta=0`, still `>=0`). So the sentence "the deterministic guarantees hold for all three" is correct.
8. *Bisection tolerance (GAP in the statement "we assume exactly solved").* With the implemented procedure the elastic device has `x_h = x(lambda_hi)`, so (pf1) holds at `lambda_hi`, but a *marginal* group (admitted at `lambda_lo`, blocked at `lambda_hi`, given a fraction) satisfies `psi >= 0` only at `lambda_lo`. Hence `lambda_hi - beta > D` and `lambda_lo - beta <= Theta` give `D < Theta + delta`, `delta = lambda_hi - lambda_lo`. The deficit bound is `B + delta` for the implemented solver (numerically `delta <= 1e-10 max(1,lambda_hi)`). Experiment `tol_test.py` (one elastic device, one video flow, bisection tolerance widened from `1e-10` to `1`) shows the largest deficit at which `r > x` still occurs moves from 13.33 to 16.6, i.e. slack enters exactly as predicted (still below `Theta=40` there).

**Numerical attempts to break it.**
* `slot_test.py`: 40,000 random slots (V in {1,5,20,100}; 1-5 elastic devices; random groups with n up to 4; `d` in {0,...,30} including below/inside/above `[rmin,rmax]`; `beta` drawn from {-30,-5,0,1,5,30,N(0,10)} per tier; `D` drawn up to `2 Theta`; C from 0.05 to 60). 240,252 (device,class) checks, 9,436 slots with a fractional marginal group. Violations of "`D >= Theta` implies `r <= x`": **0**; worst `r - x` for `D >= Theta` is exactly 0.0.
* Same test for the Remark (`d >= rmax`, `D >= Theta n/(n+1)`): **0** violations.
* `adv_path.py`: greedy adversary choosing (C, uniform tier price in {-20,...,20}) each slot to maximise the next maximal deficit, 150 slots, 1-3 video flows, 1-3 elastic devices, `d` in {0.4,1.5,30}. Maximal deficit reached / B (B=43 at V=20): default variant at most 0.40, No-debt at most 0.62. So the bound holds with a factor 1.6-3 of slack on these paths; the constant is not tight.
* The repository's own `tests/test_bound.py` covers churn and class changes every slot with tier prices in [-40,40] and the E/WC/No-debt variants.

**The Remark (n/(n+1)).** Derivation: `d >= rmax` gives `s=1`, `pi >= D`, (pf1) strict, so `n V w u_k(z) >= n(lambda-beta)z + Dz > (n+1) D z`, hence `D < Theta n/(n+1)`: correct *slot-wise*. As stated it is incomplete as a bound: `n=n_{g,k,t}` and `d_{i,t}` vary in time, so the uniform bound is `Theta n_max/(n_max+1) + rmax` and only if `d_{i,t} >= rmax` in every slot of the sojourn. As written ("growth stops already at ...") it is valid only as a statement about the threshold in one slot. On the instance of `tol_test.py` the true largest deficit at which the elastic device is still passed over is `Theta/3` (13.33 for `Theta=40`, `n=1`), below the remark's `Theta/2`, so the remark is also not tight.

**Verdict: CORRECT (exact fluid solver).** Corrected theorem/proof:

```latex
\begin{theorem}[Deficit bound]\label{thm:bound}
Let the per-slot problem be solved exactly with the fluid references used in \eqref{eq:D}
(if bisection stops with bracket width $\delta_t$, replace $B_{g,k}$ by $B_{g,k}+\sup_t\delta_t$).
For every sequence of capacities $C_t>0$, arrivals, departures and demand caps, and every real
tier prices $\beta_{g,t}$, $D_{i,k}(t)\le B_{g_i,k}$ for every elastic $i$, class $k$ and every
slot $t$ from its arrival up to the slot after its last.
\end{theorem}
\begin{proof}
Fix $i,k,t$; $g=g_i$, $D=D_{i,k}(t)$, $\lambda\ge0$ an optimal multiplier. Claim: $D\ge\Theta_{g,k}$
implies $r_{i,k,t}\le x_{i,t}$. If the group is empty or $a_{g,k}=0$ then $r=0$; if $x_i=d_i$ then
$r\le d_i=x_i$. Let $a>0$ and $x_i<d_i$. As $x_i$ maximises the Lagrangian
$Vw_g u(x)+(\beta_g+D_i-\lambda)x$ on $[0,d_i]$ and $x_i<d_i$, its right derivative is nonpositive:
$Vw_gu'(x_i)+\beta_g+D_i-\lambda\le0$. Since $u'>0$ and $D_i\ge D$, $\lambda-\beta_g>D$.
The group maximises $L_g(a,y)=nVw_g\,a\,u_k(y/a)+(n\beta_g-\pi-n\lambda)y-\zeta a$ over its feasible
set, which contains $(0,0)$ with $L_g=0$; hence $L_g(a,y)\ge0$, i.e. with $z=y/a$,
$nVw_gu_k(z)\ge n(\lambda-\beta_g)z+\pi z+\zeta\ge n(\lambda-\beta_g)z$ ($\pi,\zeta\ge0$), so
$\lambda-\beta_g\le Vw_gu_k(z)/z\le\Theta_{g,k}$. Thus $D<\Theta_{g,k}$: contradiction.
Rounding never lowers an elastic allocation, so $r\le x$ also holds for the realised $x$.
Induction: $D(1)=0$ (arrival); if $D(t)<\Theta$ then $D(t+1)\le D(t)+r<\Theta+\rmax_k$; if
$\Theta\le D(t)\le B$ then $r\le x$ and $D(t+1)\le D(t)$.
\end{proof}
\begin{remark}[Sharper constant]
If $d_{i,t}\ge\rmax_k$ and $n_{g,k,t}\le\bar n$ in every slot, then $\pi_{g,k}\ge D$, the chain gives
$nVw_gu_k(z)>(n+1)Dz$, and the same induction yields
$D_{i,k}(t)\le\Theta_{g,k}\,\bar n/(\bar n+1)+\rmax_k$.
\end{remark}
```

## 4. Corollary (window envy) and the Lindley claim

`D(tau+1) >= D(tau) + r - x` and telescoping give `sum_{tau=s}^t (r-x) <= D(t+1) - D(s) <= B - D(s) <= B`. Correct (the intermediate bound could carry `-D(s)`). `B = max B_{g,k}` and "envy per slot at most `B/L`" are trivial consequences.

Lindley: from `D(t+1) = max(D(t) + r_t - x_t, 0)`, `D(start)=0`, one gets `D(t+1) = max(0, max_{s<=t} sum_{tau=s}^t (r_tau - x_tau))` (empty window included). **Correct**: "the deficit is exactly the largest class envy over all windows that end now" holds, with two caveats the text should state: (i) `r` is the fluid reference and `x` the realised rate; (ii) windows must lie inside one uninterrupted stretch of E-declaration because the implementation resets `D` to 0 when a device re-declares E after being RT (`Repay._sync`), but algorithm.tex says only that deficits start at 0 on *arrival*. On the truthful path (no class change) this is moot.

**Verdict: CORRECT.** Fix: state "the deficit of a device is reset to zero whenever it re-declares class E", and "for slots `t` up to and including the last slot".

## 5. Price-taking, static misreport, dynamic declarations, commitment

**Definition (price-taking).** It is an assumption, not a derived approximation. The text says "the last clause is conservative"; that is not accurate in general:
* If the group `(g,k)` is empty on the truthful path (thin market), `r=0` by (eq:ref), so price-taking says the deviator receives at most 0; in reality a lone deviator becomes the only member of an RT group and receives an RT offer (this is the loophole REPAY-E was designed for). Not conservative for the deviator's gain, but *optimistic for the theorem*.
* The deviator's entry removes its own debt `D_i s_i` from `pi`, which raises the group's offer; and the group offers are re-optimised for `n+1` flows. Price-taking ignores both.

Numerical evidence that the hypothesis is not innocuous (`thin.py`, actual `Repay`, V=20, capacity alternating 0.9/3.0 scaled by n/3, one device deviating to "always video" for the whole sojourn, B=43):

| elastic others / video flows | truthful volume | deviation volume | gain |
|---|---|---|---|
| 1 / 1 | 1298.1 | 1485.7 | 187.6 (14%) |
| 2 / 1 | 1298.9 | 1304.2 | 5.3 |
| 4 / 2 | 1298.6 | 1304.2 | 5.6 |
| 9 / 4, 19 / 9, 39 / 19 | | | 5.3-5.6 |

In the 3-device market the gain is **linear in L** (L = 250, 500, 1000, 2000, 4000 -> 27.1, 50.1, 95.9, 187.6, 370.9), i.e. unbounded and far above `B=43`; for 4 or more devices it stays about 5.5, below `B`. REPAY-E gives the identical numbers here (the entrant offer is not what matters in this instance; the effect is the change in offers when the deviator joins). So the correction term "(R^dev - R^tr)" is not a technicality, and "price-taking" must be justified as a large-market statement (e.g. `n_{g,k}` and tier population large) or the theorem presented only as a conditional statement.

**Theorem (static).** Proof: deviation yields at most `sum_t r_{i,k,t}` by the definition (the definition says "at most"); truthful yields at least `sum r - B` by the Corollary over the window = whole sojourn. **CORRECT.** Two remarks: (a) the claim is about *volume*, and "any nondecreasing preference" yields no utility bound; for an `ell`-Lipschitz preference the utility gain is `<= ell B`; (b) both paths must have the same demand caps `d_{i,t}` (r depends on them). In model.tex `d_{i,t}` is `min(link rate, queued traffic)`, which depends on the device's own past service; comparing the two paths therefore needs demand caps exogenous to the device's allocation (open-loop traffic or permanently backlogged). Add this to the definition of price-taking / to the model.

**"Identity with explicit correction".** It is an inequality: `gain = R^dev - sum x^tr <= R^dev - R^tr + B`. Rename "bound with an explicit correction". The bound is trivial (no control of `R^dev - R^tr`).

**Theorem (dynamic).** The proof (apply the Corollary on the truthful path to each window `J_j`) is correct, and the statement is exactly what is proved: the volume received during the RT-declared slots on the deviation path (at most `sum_{J_j} r_{k_j}`) minus the truthful volume in the *same slots* (at least `sum_{J_j} r - B_{g,k_j}`). Problems:

1. The quantity bounded is the advantage during RT phases only. The E phases (the device re-enters with `D=0` while its truthful self carries `D>0`) are not compared; the paper itself says the sign is indeterminate. So the theorem does **not** bound the device's total gain, yet the abstract says "the gain from misreporting the class is at most this constant ... provided declarations cannot be changed in every slot". Tried numerically (`dyn_gain.py`: frozen prices from a REPAY run, strategies = greedy RT iff `r>x`, random subsets, periodic blocks, E-phase response computed with reset deficits): total gain / (K B) never exceeded 0.13, so no counterexample, but there is no proof.
2. "K maximal intervals" with `sum_j B_{g,k_j}`: each interval needs a single class `k_j`. A device can switch V -> G -> V with no E phase in between; those are *different* class-constant intervals, and the Corollary (single class) applies only to class-constant windows. Define `J_j` as maximal intervals of constant declared class in `{V,G}`.
3. `K <= ceil(L/(2 tau))`: with the hold-down applying to *every* change (including E), consecutive RT intervals of the same class are separated by an E interval of length `>= tau`, and all intervals except possibly the last (cut by departure) have length `>= tau`; then `L >= 2(K-1)tau + 1`, i.e. `K <= floor((L-1)/(2 tau)) + 1 = ceil(L/(2 tau))`. Correct **if** the declaration at arrival is also subject to the hold-down. If the initial declaration is free, the first interval can be short and `K <= ceil(L/(2tau)) + 1`. And with direct V<->G switches allowed (item 2) the count is `K <= ceil(L/tau)`.

**Verdict: CORRECT WITH FIXES.** Replacement:

```latex
\begin{theorem}[Dynamic declarations]
Let $i$ be price-taking and let $J_1,\dots,J_K$ be the maximal intervals of slots on which its declared
class is constant and equal to an RT class $k_j$. The volume received during $J_1\cup\dots\cup J_K$
exceeds the truthful volume in the same slots by at most $\sum_jB_{g_i,k_j}$. If every declared class
(including the one at arrival) is kept for at least $\tau$ slots, $K\le\lceil L/\tau\rceil$, and
$K\le\lceil L/(2\tau)\rceil$ if switches between two RT classes are not allowed.
This does not bound the volume received in E-declared slots.
\end{theorem}
```

**Proposition (commitment is necessary).**
* First claim: under the frozen-path price-taking model (`x_t, r_t` fixed whatever the device declares) the best response is slotwise `max(x_t, r_t)`, the gain is `sum (r-x)^+`. That is immediate and rule-independent *as a statement about the frozen path*. But the definition gives "at most `r`", so the equality "obtains `sum max`" needs "receives the offer in full".
* Second claim ("paths with window envy at most 1 on which the gain grows linearly in L"): arithmetic on sequences is right (alternating `+1,-1` has max window sum 1 and positive parts `L/2`), but "for any allocation rule" is not justified: no rule is exhibited whose path has this property. I verified that actual REPAY does produce such paths (`commit_ex.py`, one elastic device, one video flow, V=20, capacity alternating): `sum (r-x)^+ / L` = 0.32 (capacities 0.9/3.0), 0.10 (0.9/1.4), 0.16 (0.7/1.5) while the maximal window envy is 4.9, 11.1, 11.6 (B=43). So the example is realisable; add it (or any explicit alternating-capacity rule).
* **Conclusion drawn afterwards is overstated.** "Deferred compensation and free slot-by-slot re-declaration are incompatible" and "any rule that gives RT flows more ... can be exploited" is shown only in the frozen-path model, where the deviator keeps the repayment `x_t > r_t` without having paid for the earlier advantage. A rule can make slot-by-slot re-declaration costly by changing what the device is owed when it re-declares: REPAY itself *discards* the deficit when the device declares RT, so a device that is RT in the bad slot and E in the good slot forfeits the repayment; the frozen model ignores this. A real rule-level impossibility would need a stated class of rules and a non-frozen equilibrium notion, and none is given. Observation: even for REPAY the effect of switching is undetermined (the paper says so itself in the next paragraph), so "incompatible" cannot be both proved here and left unresolved there. Also, in `realdev.py` (non-price-taking, 3 devices) a device declaring RT in every slot gained +14%/+14%/+27% volume over truthful on three capacity patterns, a device alternating RT/E lost (-57%..-100%): the real effect depends on the switching pattern.
* The abstract's "a condition without which no guarantee of this kind can hold" repeats this overclaim.

**Verdict: GAP / overstated.** Replacement text:

```latex
\begin{proposition}[Window envy does not control per-slot re-declaration]
For any allocation path $(x_t,r_{k,t})$, a price-taking device that may re-declare its class in every
slot and receives the offer $r_{k,t}$ in the slots in which it declares $k$ obtains
$\sum_t\max(x_t,r_{k,t})$, a gain of $\sum_t(r_{k,t}-x_t)^+$ over truthful declaration.
This gain is not bounded by the window envy: for REPAY with capacity alternating between
$0.9$ and $3$ (Appendix/Section X) the window envy stays below $B$ while the gain grows linearly in $L$.
\end{proposition}
```

and replace the paragraph by "A bound on window envy therefore controls incentives only for declarations that persist; REPAY enforces persistence by a hold-down. We do not claim that no mechanism can do without commitment."

## 6. Proposition (reverse deviation) and Appendix proof

Hypotheses: (H1) `u_k' >= u'` on `[rmin,rmax]`, (H2) `u_k(rmin) > rmin u'(rmin)`; all deficits of tier `g` zero in the slot (then `pi=zeta=0` and elastic devices of tier `g` have no bonus); exact (fluid) solution; price-taking: the RT flow assumes `lambda, beta` unchanged and that, if it declared E, it would get the unconstrained response `x_hat` (an upper bound for the elastic allocation, valid also with an unbounded cap) while it keeps the group offer.

Each inequality:
* `x_hat`: `lambda' = lambda-beta`, `x_hat = Vw/lambda' - 1` if `0 < lambda' <= Vw`, `infinity` if `lambda' <= 0`. OK.
* `lambda' <= Vw u'(x_hat)` holds with equality (finite case) or trivially (`lambda'<=0 < Vw u'`); `u'(x_hat) <= u'(xbar)` as `xbar <= x_hat` (u' decreasing); `u'(xbar) <= u'(rmin)` as `xbar >= rmin`. OK.
* Rate: for `z in [rmin, xbar]`, `Vw u_k'(z) >= Vw u_k'(xbar) >= Vw u'(xbar) >= lambda'` (concavity of `u_k`, H1 at `xbar in [rmin,rmax]`, previous bullet), so `psi` is nondecreasing on `[rmin,xbar]` and `z* >= xbar`. OK.
* Admission: `max psi >= psi(rmin) = n[Vw u_k(rmin) - lambda' rmin] > n rmin [Vw u'(rmin) - lambda'] >= 0` by H2 and the chain; strict positivity gives `a*=1` (even at a marginal-capacity multiplier, because marginality needs `psi=0`). OK.
* Conclusion `u_k(z*) >= u_k(xbar) = tilde u_k(x_hat)`. OK. The numerical hypotheses: `1/z >= 1/(1+z)`, `1 > rmin/(1+rmin)`, `1 > r_G/(1+r_G)`: true for all `rmin,r_G>0`.

Weaknesses a referee will raise: (a) it is a single-slot statement for zero-deficit tiers only; when tier-mates hold deficits the RT offer carries a debt price (this is the case in congestion, i.e. when it matters) and the paper only says it "can fail", with no characterisation; (b) it compares with `x_hat`, ignoring the leftover pool that rounding can hand to an elastic device above `x_hat`; (c) price-taking here means: `lambda, beta`, group size and offer unchanged when one flow leaves the group (n -> n-1) and joins the elastic pool; that must be written in the proposition rather than inherited from Definition `pt` (which is about elastic -> RT deviations and defines the RT receipt as `r`, not the elastic one); (d) "utility from the offer" is `a u_k(z)` with `a=1` here, fine.

**Verdict: CORRECT** (for the stated single-slot, zero-deficit, fluid, price-taking claim). Fix: restate the price-taking meaning for this direction and the conditions (exact fluid solver, `d` unconstrained).

## 7. Assumption and Theorem (utility and constraint violation), Appendix proof

Step by step:
* **Lyapunov and churn.** `L(t+1) <= sum over devices present at t of 1/2 D(t+1)^2 + 1/2 sum Q(t+1)^2` (leavers' updated values are nonnegative and dropped, arrivals contribute 0) and `L(t) = sum over present-at-t`: so the drift bound holds term by term. Correct. `L(1)=0` (devices present at slot 1 have `D=0`).
* **Drift of D.** `D(t+1)^2 <= (D + r - x)^2`; `D>=0`, `r <= a m` give `D(r-x) <= D(a m - x)`. Correct. `|r - x| <= ell_max`: `0<=r<=min(rmax,d)<=ell`, `0<=x<=d<=ell` so `r-x in [-ell,ell]`. Correct. `e_j` bounded: `|e_j| <= N_max ell_max` automatically (even the free-tier term, because `min(phi C, dem_F) <= dem_F`), provided `theta <= 1`; the explicit constant could be given.
* **Optimality used.** REPAY maximises the objective (dpp) (the concave surrogate with `m_d`) over all feasible decisions of (slot) for the realised `C_t`; a policy `pi in Pi(xi)` outputs, for each realised `C`, a feasible decision of the same problem (capacity `<=C_t`, `0<=x<=d`, `a,y` in the cone). So `(app1)` is valid. Yes, correct.
* **Conditioning.** `H_t` = past and `xi_t`; `Q(t), D(t)` are `H_t`-measurable; Assumption (ii) gives `C_t | H_t ~ F_{xi_t}`; `pi` depends on `C_t` (and `xi_t`) and independent randomisation. So `E[Q e^pi | H_t] = Q E_{F_xi}[e^pi] <= 0` and same for the `D` terms. Correct *given the assumption*. **But the assumption conflicts with the model:** `xi_t` is declared exogenous and includes the demand caps, while model.tex defines `d_{i,t} = min(link rate, traffic queued at the AP)`, which depends on past service. The theorem is true only for open-loop/exogenous caps (as in the simulator, where `d` is an exogenous on-off trace). State it in the model and in Assumption `ass:model`. Note Theorem `bound` and the Corollary hold for arbitrary caps.
* **Benchmark class `Pi(xi)`.** (1) The envy constraints in (eq:bench) use `a m_d(z)`, the *majorant*, which is `>= a min(z,d)`. So `Pi(xi)` is the set of policies envy-free in expectation with respect to the *majorant* reference; it is a subset of the truly envy-free policies whenever some `d_i in (rmin,rmax)`. The sentence "The second family of constraints is class-envy-freeness in expectation" is therefore not exactly right, and the benchmark `U*` can be strictly below the value of the best truly envy-free policy; the abstract's "best policy ... envy-free between classes on average" is not what is compared. (2) The tier constraints `E_{F_xi}[e_j] <= 0` are imposed **state by state**, not on the long-run average over states. That is a much stronger requirement than (eq:ps)-(eq:ff). A policy that serves premium more in rich states and less in poor states satisfies the long-run constraint but not the state-wise one, so `U*` may be well below the optimum of the stated problem; and REPAY (whose tier queues do shift across states) may exceed `U*`. The theorem is a one-sided lower bound `REPAY >= U* - B_0/V`, not "within O(1/V) of the best policy". (3) `Pi(xi) != emptyset` is a strong hypothesis precisely because of (2): a state with many premium devices and a capacity distribution that cannot support `theta_P` of the committed demand in expectation has `Pi(xi)=emptyset` and the theorem is silent. (4) Randomisation: allowed and harmless; `sup` over `pi` should be taken with a measurable choice `xi -> pi_xi` (a technicality if the state space is uncountable).
* **Constant `B_0`.** `B_0 = 1/2 sum_j (e_j^max)^2 + 1/2 N_max |K| ell_max^2` is right algebraically, but with `e_j^max = N_max ell_max` it is of order `N_max^2 ell_max^2`. For the hotspot (`N_max ~ 75`, `ell_max = 30`, `V=20`): `B_0 ~ 7.6e6`, `B_0/V ~ 3.8e5`, against a per-slot utility of order 100. The utility bound is vacuous at the experimental `V`; "O(1/V)" is asymptotic only. Say so.
* **Telescoping.** `L(1)=0`, `L(T+1)>=0` give the utility bound. Violation: `U*>=0` follows from `Pi` nonempty and `U>=0`; `U_t <= U^max`; so `E L(T+1) <= T(B_0 + V U^max)`. `Q_j(T+1) >= sum_{t<=T} e_{j,t}` (since `Q(t+1) >= Q(t)+e_t`, `Q(1)=0`); `E Q <= sqrt(E Q^2) <= sqrt(2 E L)`. The algebra `sqrt(2(B_0+V U^max)/T)` is correct, and `U*>=0`, `U_t<=U^max` are used in the right direction. The result is `O(sqrt(V/T))` only for `V >= B_0/U^max`.
* **Fluid allocation.** The proof needs the fluid allocation for `Q` and `U`: the tier queues use the realised `e_j`, and rounding moves capacity between tiers (leftover handed to elastic devices of other tiers) and changes `U_t`; only the `D`-drift is safe under rounding (`x_f >= x_fluid`). The paper says "the statement concerns the fluid allocation" before the theorem but the theorem statement does not, and the experiments use the rounded implementation. Also the solver tolerance adds a per-slot `V * (suboptimality)` to `B_0`. Add both to the statement.
* **Sample-path versus expectation.** Problem statement and (eq:ps)-(eq:ff) are `limsup` of sample-path averages; the theorem controls `E[(1/T) sum e_j]`. For fixed `V` this can be upgraded: `E[(Q(T)/T)^2] <= c/T`, Borel-Cantelli along `T=m^2` and the bounded increments of `Q` give `Q(T)/T -> 0` a.s. Add it, otherwise "satisfies" is not proved.
* **Remark `O(V/(eps T))`.** A uniform slack `eps` in *both* constraint families gives drift `<= B_0 + V U^max - eps(sum_j Q_j + sum D)` hence a bound on the *time average* of `E Q` of order `(B_0 + V U^max)/eps`. A bound on `E Q_j(T+1)` for the terminal `T` (needed for the violation) requires a Hajek-type uniform-in-time bound for `Y = sqrt(2L)` (bounded increments, churn only decreases `Y`); this is plausible and standard but not "the standard argument" for the time average. Without it the elementary argument over the last `m` slots gives only `O(sqrt T)` again. Also `U^max` should be replaced by `U^max - U_{pi_eps}`.

**Verdict: CORRECT WITH FIXES.** Corrected statement:

```latex
\begin{assumption}
(i) $(\xi_t)$ is exogenous (not influenced by the allocation), in particular demand caps are open-loop;
at most $N_{\max}$ devices are active. (ii) Given $\xi_t$ and the whole past, $C_t\sim F_{\xi_t}$.
(iii) $|e_{j,t}|\le e_j^{\max}$, $d_{i,t}\le\ell^{\max}$, $0\le U_t\le U^{\max}$.
\end{assumption}
For a state $\xi$ let $\Pi(\xi)$ be the set of randomised maps $C\mapsto(a,y,x)$ feasible for \eqref{eq:slot}
with $\E_{F_\xi}[e_j]\le0$ for all $j$ \emph{(state-wise tier constraints)} and
$\E_{F_\xi}[a_{g_i,k}m_{d_i}(z_{g_i,k})-x_i]\le0$ \emph{(envy in expectation with respect to the
majorant reference)}; $a^\pi:=0$ for empty groups.
\begin{theorem}
Assume $\Pi(\xi)\ne\emptyset$ for every reachable $\xi$ and that the fluid per-slot problem is solved
exactly. Then $\frac1T\sum_{t\le T}\E U_t\ge\frac1T\sum_{t\le T}\E U^\ast(\xi_t)-B_0/V$ and
$\frac1T\sum_{t\le T}\E e_{j,t}\le\sqrt{2(B_0+VU^{\max})/T}$. Moreover $Q_j(T)/T\to0$ a.s.,
so \eqref{eq:ps}--\eqref{eq:ff} hold on almost every sample path.
\end{theorem}
```

## 8. Proposition (baselines), `rmin_V=0.5`, `rmax_V=3`, `u_V=1+log(z/rmin_V)`, `u=log(1+x)`

Range: `0.5 < C < min(1,1) = 1`. Elastic device saturated means `d >= C` (state it).
* (a) Strict priority: video gets `min(C, rmax)=C >= rmin`; elastic gets `0`; reference `a min(z,d)=C`, so envy grows by `C` per slot. With two video flows `2 rmin = 1 > C`: only one is admissible. This presupposes admission control among equal-priority RT flows; if the capacity were split `C/2` each, both would be worthless. State the tie-break. CORRECT.
* (b) PF with equal weights gives `C/2 in (0.25, 0.5) < rmin`: useless. CORRECT (numerically, rates 0.275/0.275 at `C=0.55`, 0.4/0.4 at 0.8, 0.495/0.495 at 0.99).
* (c) With `a=1`: objective `Vw[1+log(z/rmin)+log(1+C-z)]`, derivative `1/z - 1/(1+C-z) > 0` iff `z < (1+C)/2`, and `(1+C)/2 > C` iff `C<1`; so `z=C`, value `Vw[1+log(C/rmin)] >= Vw > Vw log(1+C)` (blocking branch; `log(1+C)<log 2<1`). Also needed and not shown: `a=1` is optimal over fractional `a` (`partial_a [a u(y/a)] = log(z/rmin) >= 0`, so admission is increasing in `a`), and the tier price `beta` is irrelevant because total rate is `C` in both branches (saturated elastic). Numerically (PlainDPP, `beta=0`): rates `(~0, 0.55)`, `(0,0.8)`, `(~0,0.99)` at `C = 0.55, 0.8, 0.99`. CORRECT.

Final paragraph of that subsection: REPAY on this instance: the call is served for about 4 (C=0.8), 15 (C=0.55) slots, then the elastic device is served; "until the elastic device's deficit reaches the threshold of Theorem `bound`" is loose: the deficit at which service switches is about 11-13, well below `Theta=40` or `Theta/2=20` (the bound is not tight). Long-run: avg `x` = avg `r` = 0.4976 (C=0.8, V=20, t>500) and the call is admitted 60% of the time (95-96% at C=0.99, 14% at C=0.55). The sentence "gives each side the same long-run volume" is confirmed.

**Verdict: CORRECT**; add "elastic cap `d>=C`", the tie-break for (a), and "`beta` cancels" for (c).

## 9. Consistency with abstract/introduction and model.tex

Problems, with proposed wording:

1. *Abstract:* "for arbitrary arrivals, departures and capacities" is true for the exact fluid solver (Theorem `bound`); not for the utility theorem, whose capacity process must be conditionally i.i.d. given the (exogenous, open-loop) population state. Intro contribution 5 says "arbitrary exogenous population process", which is closer, but omits (i) exogenous demand caps, (ii) the conditional law of `C_t`, (iii) state-wise feasibility.
2. *Abstract:* "the gain from misreporting the class is at most this constant for price-taking devices, provided declarations cannot be changed in every slot, a condition without which no guarantee of this kind can hold." Overstated on three counts: dynamic gain is bounded only for the RT phases and by `K` times the constant, not "this constant"; "no guarantee can hold" is unproved (item 5); price-taking fails in thin markets (3-device market: linear-in-L gain, see item 5). Suggested: "the *volume* gained during the time a price-taking device poses as real-time is at most `K` times this constant, where `K` is the number of declaration changes, which a hold-down bounds".
3. *Abstract and contribution 5:* "within O(1/V) of the best policy that satisfies the business constraints and is envy-free between classes on average". The theorem is a one-sided lower bound against a state-wise, majorant-envy-free stationary benchmark, for the fluid allocation, with `B_0` of order `N_max^2 ell_max^2`. Suggested: "no worse than `B_0/V` below the best state-wise randomised policy ...".
4. *Contribution 2:* "solved exactly by bisection in time linear in the number of devices": `O(N log(1/eps))` plus `O(N log N)` sorting.
5. *Contribution 3:* "independently of the number of devices, of the churn, and of the tier prices" is correct for `B_{g,k}` (but it depends on `V, w_g, eta_k, rmax_k`); it holds for the exact fluid solver (plus `delta`).
6. *Model vs proofs:* committed demand, business constraints and `beta` enter only through `e_j` and the per-unit tier prices; the model's remark "All three are linear in the tier rates" is accurate (free-tier floor `min(phi C, dem_F)` is decision-independent). Demand caps are *queue-dependent* in the model but exogenous in Theorem `opt` and in the incentive comparison (see 5, 7). Deficits reset when a device re-declares E is in the code, not in algorithm.tex.
7. *Algorithm.tex Section "Variants":* "The deterministic guarantees hold for all three" - verified (item 3). "the optimality guarantee is proved for REPAY itself" - consistent.
8. *Discussion in analysis.tex after Theorem `opt`:* "the violation of the tier constraints vanishes as O(sqrt(V/T))" - for `V >= B_0/U^max`, in expectation; fine with the qualifier.

## 10. Missing assumptions, undefined symbols, notation clashes, other referee objections

Missing/undefined:
* `rmin_k>0`, `w_g>0`, `V>0`, `theta_P,theta_Y<=1` (for `e_j` bound), `phi in [0,1]`, `u_k` bounded and (for the solver) strictly concave; none stated.
* `N_t` (Prop. solver) undefined; `N_max` is defined later. `eps` (solver tolerance) vs `varepsilon` (slack) vs `epsilon` in the algorithm text.
* `u' <= 1` is claimed to be used; it is not used. `u' > 0` is used and not listed. The "any alpha-fair utility can be substituted" claim also requires re-deriving the closed form of `x_i(lambda)` and checking H1-H2 of the reverse deviation proposition (for `alpha<1` and `rmin>=1`, H2 can fail).
* Sojourn: devices' departure must be independent of their received volume (stated implicitly in Theorem `static`); demand caps must not depend on the device's own declaration/past service.
* Theorem `bound` is stated for deficits; the term "class-envy-free" in the Corollary relies on realised `x` and fluid `r`: say so.
* The theory does not cover REPAY-E and REPAY-WC for utility (acknowledged).

Notation clashes (a referee will notice):
* `V` is both the DPP parameter and the video class (`u_V`, `rmin_V`, `Vw_g u_V`!). Rename the parameter (e.g. `\nu`) or the class.
* `pi_{g,k}` (debt coefficient) vs `pi` (policy) in appendix, written `e^pi`, `a^pi`.
* `s` (majorant slope) vs `s` (window start). `L` (sojourn length) vs `L(t)` (Lyapunov). `K` (number of RT intervals) vs `\cK`, `|K|`. `tau` (hold-down) vs `tau` (summation index, Definition `envy`, Corollary). `B` (envy bound), `B_{g,k}`, `B_0`. `E` (class) vs `E`/`\E` (expectation) vs `\cE`. `D` (deficit) vs `d` (demand cap) vs `\dem` (demand). `p` (PAYG price) vs `p_i` (elastic price in (xresp)). `F` free tier vs `F_xi` distribution. `Theta` vs `theta_P, theta_Y`.

Other things a referee of an OR journal will object to:
* The title of the contribution "incentives" rests on price-taking; thin markets break it (item 5). An equilibrium or a regret-type statement against non-price-taking deviators is missing; the experiments are the only evidence.
* Theorem `opt` benchmark is nonstandard (state-wise, majorant, fluid); compare the usual Neely benchmark and say what is lost.
* The constants `B` and `B_0` are not tight (observed max deficit about 0.4-0.6 of `B`); fine, but the "43 Mbit, fourteen seconds of video" statement describes the bound, not the behaviour.
* A hold-down of `tau` slots is introduced in the algorithm but its effect on the utility theorem (devices that cannot re-declare) is not analysed; declared classes are exogenous in Theorem `opt`, which is consistent only if the hold-down is part of that exogenous process.

## Numerical experiments (summary)

| Script | What | Result |
|---|---|---|
| `slot_test.py` | 40k random slots, adversarial `beta` in [-30,30], `D` up to `2 Theta`, marginal groups (9,436), `d` below/inside/above interval; checks `D>=Theta => r<=x` and the remark | 0 violations / 240,252 checks; remark: 0 violations |
| `tol_test.py` | widen bisection tolerance 1e-10..1 | largest deficit still passed over: 13.33 -> 16.6 (slack ~ delta), below Theta here |
| `cvx_test.py` | solver vs cvxpy on 597 random slots | worst relative gap 2.4e-7, all feasible |
| `adv_path.py` | greedy adversary on capacity and tier price | max D / B <= 0.40 (default), <= 0.62 (No-debt) |
| `baselines.py` | PF, plain DPP, REPAY on 1 video + 1 saturated elastic | (a)-(c) confirmed; REPAY long-run `x = r`, admission 14%, 60%, 96% at C=0.55, 0.8, 0.99; switch at D ~ 11-13 |
| `commit_ex.py` | price-taking re-declaration under actual REPAY | gain `sum(r-x)^+/L` = 0.32, 0.10, 0.16 per slot with window envy 4.9, 11.1, 11.6 << B=43 |
| `dyn_gain.py` | total (RT+E phases) gain of frozen-price strategies | gain / (K B) <= 0.13: no counterexample, no proof |
| `realdev.py` | real (non-frozen) deviations, 3 devices | always-RT +14%, +14%, +27%; alternating RT/E: -57% to -100% |
| `thin.py` | static misreport vs market size | 3 devices: gain 187.6, linear in L (27 -> 371 for L 250 -> 4000), >> B=43; >= 4 devices: ~5.5 |

## Prioritised list of required changes

**CRITICAL (claim not supported by the proofs; a referee would reject the statement)**
1. Abstract, intro (contribution 4), Proposition `commit` and its following paragraph: remove "no guarantee of this kind can hold", "incompatible", "necessary". The proposition only shows that window envy on the truthful path does not control the frozen-path gain of per-slot re-declaration; rules that forfeit credit on re-declaration (REPAY itself) are not covered. Restate as in item 5.
2. Abstract/intro/Theorem `dynamic`: the dynamic result bounds only the advantage in RT-declared slots, by `sum_j B`, not the total gain; the abstract's "gain ... at most this constant" is false as written for dynamic strategies. Make the statement exact and state that the E-phase effect is unproved.
3. Abstract/intro/Theorem `opt`: the benchmark is a state-wise, majorant-envy-free stationary policy; the theorem is a one-sided bound; `Pi(xi) != emptyset` is restrictive. Rewrite the claim ("within O(1/V) of the best policy that meets the business constraints") accordingly or change the benchmark.

**MAJOR**
4. Price-taking: replace "conservative" by an honest statement; add the thin-market counterexample (3 devices, linear-in-L gain, 187.6 vs B=43 at L=2000) and give a size condition or a large-market lemma; the "identity" is an inequality.
5. Demand caps: model.tex defines `d` through the queue, but Theorem `opt` and the incentive theorems need caps exogenous to the device's own service; state it as an assumption (open-loop traffic or permanently backlogged devices).
6. Theorem `opt` is proved for the fluid, exactly solved allocation; the implemented rule (rounding, bisection tolerance) is not covered for `Q` and `U`. State this in the theorem and add the `V*suboptimality` term; also upgrade to sample-path (`Q_j(T)/T -> 0` a.s.) or weaken "satisfies (ps)-(ff)".
7. Theorem `dynamic`: use class-constant intervals; fix the interval count (`K <= ceil(L/tau)` in general, `ceil(L/(2 tau))` if V<->G switches are forbidden and the hold-down applies at arrival).
8. Theorem `bound`: add the `+delta` for the implemented bisection; rewrite the stationarity step as a Lagrangian-maximiser argument; the sharper Remark must be stated uniformly in time (`n_max`, `d>=rmax` in all slots).

**MINOR**
9. Majorant: add the one-line proof (supporting line, not chord); say gap `(1-s)(d-rmin)`.
10. Solver proposition: fix complexity expression, define `N_t`, strict concavity, `O(N log N)` sorts, tolerance meaning.
11. Remark `O(V/(eps T))`: needs both slack families and a Hajek-type uniform-in-time bound; otherwise drop.
12. `B_0` is of order `N_max^2 ell_max^2`; the bound is vacuous at V=20 in the experiments; say "asymptotic".
13. Reverse deviation: spell out price-taking for that direction, note ignored rounding pool, note it holds only for zero-deficit slots.
14. Algorithm: state that deficits reset to 0 when a device re-declares E; Theorem `bound`/Corollary: "up to and including the slot after the last"; "until the deficit reaches the threshold" in the baseline paragraph is loose (switch at ~11-13 vs Theta=40).
15. Baselines: add `d >= C`, tie-break among RT flows in (a), `beta` cancels and `a=1` optimal in (c).
16. Notation: rename `V` (parameter vs video class), `pi` (policy vs debt), `s`, `L`, `K`, `tau`; define `N_t`, `rmin>0`, `u_k` strictly concave; remove `u'<=1` or say it is unused; check the alpha-fair claim or drop it.
