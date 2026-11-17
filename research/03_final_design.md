# Final design: REPAY (REal-time Priority with elAstic paYback)

This file is the authoritative design. `02_algorithm_design.md` (algorithm "TEDS") is an earlier
independent draft; its Lemma 1–2, the perspective form, the affine majorant, the per-unit tier
constraints and the T4 proof technique are adopted here. Differences from that draft are listed in §8.

Units: time slot = 1 s, rates in Mbps (so volume per slot in Mb).

## 1. Model

- Slots $t=1,2,\dots$. At the start of slot $t$ the operator observes capacity $C_t>0$, the active
  devices and their data. Nothing about the future is known.
- Tiers $g\in\{F,P,Y\}$ (free, premium, pay-as-you-go): billing identity, verified.
- Declared class $\in\{E\}\cup\mathcal K$, $\mathcal K=\{V,G\}$ (video, gaming); may be false.
- **RT flows** of class $k$: per-slot utility $u_k(z)$ for rate $z\in[r^{\min}_k,r^{\max}_k]$, zero below
  $r^{\min}_k$, nothing gained above $r^{\max}_k$. $u_V(z)=1+\log(z/r^{\min}_V)$; $u_G\equiv 1$ at $r_G$
  ($r^{\min}_G=r^{\max}_G=r_G$). $\eta_k=\max_z u_k(z)/z$ ($=1/r^{\min}_k$ for both).
  Group $(g,k)$ with $n_{g,k}\ge1$ flows: admission fraction $a\in[0,1]$, common rate $z$; $y=az$.
- **Elastic devices** $i$: verified demand cap $d_{i,t}=\min(\ell_{i,t},b_{i,t})$ (link rate, AP-side
  backlog; $b=\infty$ if saturated). Allocation $x_{i,t}\in[0,d_{i,t}]$. True preference: any
  nondecreasing function of cumulative volume. Operator surrogate $w_g u(x)$, $u(x)=\log(1+x)$
  (or $((1+x)^{1-\alpha}-1)/(1-\alpha)$), $u'\le1$.
- Capacity: $\sum_{g,k}n_{g,k}y_{g,k}+\sum_i x_i\le C_t$. Tier rate $\rho_g=\sum_k n_{g,k}y_{g,k}+\sum_{i:g_i=g}x_i$.
- Tier demand $\mathrm{dem}_g=\sum_k n_{g,k}r^{\max}_k+\sum_{i:g_i=g}d_i$.

**Business constraints** (long-run averages, all linear in tier rates):

| name | meaning | $e_{j,t}$ (want average $\le0$) | per-unit price |
|---|---|---|---|
| PS | premium served ratio $\ge\theta_P$ | $\theta_P\mathrm{dem}_P-\rho_P$ | $\beta_P=Q_{PS}$ |
| YS | PAYG served ratio $\ge\theta_Y$ (revenue $=p\rho_Y$) | $\theta_Y\mathrm{dem}_Y-\rho_Y$ | $\beta_Y=Q_{YS}+V\varpi p$ |
| FF | free floor | $\min(\phi C_t,\mathrm{dem}_F)-\rho_F$ | $\beta_F=Q_{FF}$ |

$Q_j(t+1)=\max(Q_j(t)+e_{j,t},0)$; these persist through churn. $\varpi\ge0$: optional revenue weight
(default 0). Tier weights $w_g$ (default $w_P=2$, $w_Y=1.5$, $w_F=1$), same weight for E and RT in a tier.

**Class-envy deficits.** For elastic $i$ of tier $g$ and RT class $k$, created at arrival with value 0:
$$r_{i,k,t}=a_{g,k,t}\min(z_{g,k,t},d_{i,t}),\qquad D_{i,k}(t+1)=\max\big(D_{i,k}(t)+r_{i,k,t}-x_{i,t},\,0\big).$$
$r_{i,k,t}$ is the expected usable volume device $i$ would have received in slot $t$ as a class-$k$ flow of
its tier, at the realised offer. If $n_{g,k,t}=0$ the reference is $0$ (default), or the *entrant offer*
(variant REPAY-E, §5).

**Affine majorant** of $z\mapsto\min(z,d)$ on $[r^{\min},r^{\max}]$: $m_d(z)=\sigma+sz$ with
$(s,\sigma)=(1,0)$ if $d\ge r^{\max}$; $(0,d)$ if $d\le r^{\min}$; else $s=\frac{d-r^{\min}}{r^{\max}-r^{\min}}$,
$\sigma=(1-s)d$. Then $m_d(z)\ge\min(z,d)$, with equality when $d\notin(r^{\min},r^{\max})$.
Debt coefficients $\pi_{g,k}=\sum_{i:g_i=g}D_{i,k}s_{i,k}$, $\zeta_{g,k}=\sum_{i:g_i=g}D_{i,k}\sigma_{i,k}$.
Bonus $D_i=\sum_kD_{i,k}$.

## 2. Per-slot problem and exact solver

$$\max_{a,y,x}\ \sum_{(g,k):n\ge1}\Big[Vw_gn\,a\,u_k(y/a)+(n\beta_g-\pi_{g,k})y-\zeta_{g,k}a\Big]
+\sum_i\Big[Vw_{g_i}u(x_i)+(\beta_{g_i}+D_i)x_i\Big]$$
s.t. capacity, $0\le a\le1$, $ar^{\min}_k\le y\le ar^{\max}_k$, $0\le x_i\le d_i$.
This is $VU-\sum_jQ_je_j-\sum_{i,k}D_{i,k}\,(a\,m_{d_i}(z)-x_i)$ up to constants; it is concave
(perspective + linear terms).

**Solver (bisection on the capacity price $\lambda\ge0$).**
- Elastic: $p_i=\lambda-\beta_{g_i}-D_i$; $x_i=d_i$ if $p_i\le0$, else $\min\{d_i,\max(0,(Vw_{g_i}/p_i)^{1/\alpha}-1)\}$.
- RT group: $q=n(\lambda-\beta_g)+\pi$. Video: $z^*=r^{\max}$ if $q\le0$ else $\mathrm{clip}(nVw_g/q,r^{\min},r^{\max})$;
  gaming: $z^*=r_G$. $\psi=n[Vw_gu_k(z^*)+(\beta_g-\lambda)z^*]-\pi z^*-\zeta$; $a^*=\mathbb 1\{\psi>0\}$.
- Load $S(\lambda)=\sum na^*z^*+\sum x_i$ is nonincreasing. If $S(0)\le C$: done with $\lambda=0$.
  Else bisect to $S(\lambda_{lo})>C\ge S(\lambda_{hi})$, $\lambda_{hi}-\lambda_{lo}\le10^{-10}\max(1,\lambda_{hi})$;
  take the allocation at $\lambda_{hi}$; groups that are on at $\lambda_{lo}$ and off at $\lambda_{hi}$ are
  marginal and receive fractional $a=\min(1,\text{residual}/(nz^*(\lambda_{hi})))$ in sequence; any
  remaining residual (from the tolerance) is given to elastic devices below their cap.

**Rounding to whole flows.** A group with $a<1$ admits $M=\lfloor na\rfloor$ flows at rate $z$
(flows served in the smallest fraction of their slots as real-time first, then incumbents, then arrival order; this rotation replaced an incumbents-first rule, which let a device in a three-device market gain volume linearly in its stay); the leftover $(na-M)z$ goes to one more flow if it is
$\ge r^{\min}$, otherwise to elastic devices below their cap (largest marginal value first). Elastic
allocations are never reduced by rounding, so Theorem 1 holds for the implemented allocation. The
deficit update uses the fluid reference $a\min(z,d_i)$, which is at least the realised average.

## 3. Algorithm (per slot)

1. Observe $C_t$, groups, elastic data; compute $d_i$, $(s,\sigma)_{i,k}$, $\pi,\zeta,D_i,\beta_g$.
2. Solve the per-slot problem (§2); round; serve.
3. $D_{i,k}\leftarrow\max(D_{i,k}+a_{g_i,k}\min(z_{g_i,k},d_i)-x_i,0)$; $Q_j\leftarrow\max(Q_j+e_j,0)$.
4. Churn: departing devices drop their deficits; arriving devices start at 0. A device that changes its
   declared class must keep the new class for at least $\tau$ slots (hold-down), enforced by the AP per
   subscriber identity.

Parameters: $V$ (utility vs. envy trade-off), $w_g$, $\theta_P,\theta_Y,\phi$, $\tau$.

## 4. Theorems (statements; proofs go in the paper)

Let $\Theta_{g,k}=Vw_g\eta_k$ and $B_{g,k}=\Theta_{g,k}+r^{\max}_k$.

**T1 (deterministic deficit bound).** For every sequence of capacities, populations, demands and any
tier prices $\beta_{g,t}\in\mathbb R$: $D_{i,k}(t)\le B_{g_i,k}$ for all $i,k,t$.
*Proof idea.* If $a_{g,k}>0$ and $x_i<d_i$: KKT for $x_i$ gives $\lambda-\beta_g\ge D_i\ge D_{i,k}$; $\psi\ge0$
gives $Vw_gu_k(z)\ge(\lambda-\beta_g)z$. So $D_{i,k}\le Vw_gu_k(z)/z\le\Theta$. Hence $D_{i,k}>\Theta$ implies
$a=0$ or $x_i=d_i\ge r_{i,k}$: no growth. Growth per slot $\le r^{\max}_k$.

**T2 (window class-envy-freeness, every sample path).** For all $s\le t$ in the sojourn of $i$:
$\sum_{\tau=s}^t x_{i,\tau}\ \ge\ \sum_{\tau=s}^t r_{i,k,\tau}-\big(D_{i,k}(t+1)-D_{i,k}(s)\big)\ \ge\ \sum_{\tau=s}^t r_{i,k,\tau}-B_{g_i,k}$.

**L3 (credit monotonicity) — REFUTED.** The conjecture "an elastic device that starts with less
deficit never receives more cumulative volume in the same environment" is false: near the threshold
$\lambda-\beta=D$ the elastic response is arbitrarily sensitive to $D$, so a copy with slightly more
credit can be served up to its cap, lose the excess by reflection, and end up behind (random search:
difference up to 34 Mb with $d\le50$). What does hold is the identity
$X^q-X^p=(D^p-D^q)(t)-(D^p-D^q)(0)+Y^q(t)-Y^p(t)$, where $Y$ is the cumulative reflection.

**T4 (dynamic declarations, price-taking).** Under the price-taking hypothesis, consider any declaration
strategy of a saturated elastic device with $K$ maximal RT-declared phases $J_1,\dots,J_K$. In each
phase the deviant receives at most $\sum_{t\in J}r_{i,k,t}$, while truthful declaration yields in the
same slots at least $\sum_{t\in J}r_{i,k,t}-B$ (T2). So the volume advantage collected during
RT-declared phases is at most $KB_{\max}$; with hold-down $\tau$, $K\le\lceil L/(2\tau)\rceil$. A static
misreport ($K=1$, whole sojourn) gains at most $B$, i.e. $B/L$ per slot. The theorem does not bound the
difference in the E-declared phases (the deviant re-enters with zero deficit; by the refuted L3 this
can go either way); experiment E5 measures the total.

**P5 (hold-down is necessary).** For any mechanism, a device allowed to re-declare every slot obtains
$\sum_t\max(x_{i,t},r_{i,k,t})$ under price-taking, i.e. gains $\sum_t(r_{i,k,t}-x_{i,t})^+$ over
truthful; this is not controlled by any bound on windowed envy (example: alternating slots).

**P6 (reverse direction, zero debts).** Under the calibration $w_gu_k'(z)\ge w_gu'(z)$ on
$[r^{\min}_k,r^{\max}_k]$ and $u_k(r^{\min}_k)>r^{\min}_ku'(r^{\min}_k)$ (true for our utilities), when all
deficits of the tier are zero an RT device cannot gain by declaring E (price-taking).

**T7 (utility and constraints).** Fixed-population-state conditional i.i.d. model (A-T4 of the draft) with
exogenous demand caps: time-average utility $\ge\bar U^*-B_0/V$, where $U^*(\mathcal N)$ is the optimum over
stationary policies satisfying the tier constraints and class-envy-freeness *in expectation*
($\mathbb E[a\,m_{d_i}(z)-x_i]\le0$); tier-constraint violation $\le\sqrt{2(B_0+2VU^{\max})/T}$.
$B_0=\tfrac12\sum_j(e_j^{\max})^2+\tfrac12N_{\max}|\mathcal K|(\ell^{\max})^2$.

**P8 (baselines).** Strict priority and plain drift-plus-penalty have unbounded class envy; class-blind
proportional fairness gives no RT protection (two-device examples).

**T9 (solver).** The bisection solver is exact; cost $O((N+|\mathcal G||\mathcal K|)\log(1/\epsilon))$.

## 5. Variants (ablations)

- **REPAY-E (entrant offer).** For an empty group $(g,k)$ in a tier with elastic devices, the reference
  is the offer a single entrant would get at the realised $\lambda$: $z^{e}$, $a^{e}$ from the group
  formulas with $n=1$ and the current $\pi,\zeta$. T1, T2 hold; T7 is not claimed.
- **REPAY-WC (slack recycling).** If the solution has $\lambda=0$ (spare capacity), spare capacity is
  given to RT groups (raise $a$ to 1, then $z$ to $r^{\max}$), most valuable first. T1, T2 hold
  (all elastic devices are at their caps when $\lambda=0$); T7 is not claimed.
- **No-debt-price.** $\pi=\zeta=0$ (bonus only). T1, T2 hold; T7 is not claimed.
- **Plain DPP.** $D\equiv0$ (no deficits): baseline.

## 6. Baselines

- **PF**: class-blind weighted proportional fair per slot: maximise $\sum w_g\log(1+x)$, RT flows capped at
  $r^{\max}_k$; an RT flow-slot is successful iff its rate $\ge r^{\min}_k$.
- **WFQ**: same with RT weights multiplied by 4.
- **Priority**: declared RT first (premium, PAYG, free; gaming before video): admit flows at $r^{\max}$
  while capacity lasts, the last one at $\ge r^{\min}$; remaining capacity to elastic by weighted PF.
- **Plain DPP**: REPAY with $D\equiv0$ (same tier queues).
- **Credit (Karma-style)**: weighted fair share $f_i=Cw_i/\sum w$; demand $=d_i$ (RT: $r^{\max}$);
  devices below their share donate the rest; extra capacity goes to borrowers in decreasing order of
  credit; credit $\mathrel{+}=f_i-x_i$ (initial credit 0, may be negative). Class-blind.

## 7. Experiments

E1 deficit bound and envy vs $V$; E2 optimality gap vs $V$ against the stationary benchmark (fixed
population, convex solver); E3 comparison of all mechanisms on hotspot and home scenarios (utility,
RT success, elastic volume, Jain index, tier constraints, envy); E4 strategic: exact unilateral
deviation gain (elastic declares video for its whole sojourn) and collapse curves (fraction of
misreporting elastic devices from 0 to 1); E5 switching attack vs hold-down $\tau$; E6 capacity
variability sweep; E7 ablations (REPAY-E, REPAY-WC, no debt price); E8 runtime scaling.

## 8. Differences from the TEDS draft

1. Lindley deficits (not signed cumulative with a twin backlog): gives the every-window guarantee T2,
   which is what T4 (dynamic declarations) needs; demand caps are AP-verified, so the banking attack of
   the draft (which needs self-reported caps) does not apply; any manipulation through the deficit
   state is worth at most $B$.
2. Dynamic declaration theorem T4 with hold-down and necessity P5 (new; the draft had a conjecture).
3. No free-tier cap constraint (it throttles free users when capacity is idle); PAYG revenue is expressed
   through a served-ratio constraint.
4. Deterministic rounding that never reduces elastic allocations.
5. Entrant-offer and slack-recycling variants defined and scoped (T1/T2 only).

## 9. Changes made during implementation

- Premium and PAYG service levels are relative to **committed demand**: each paid tier has a committed
  rate per device $c_g$ (defaults $c_P=2$, $c_Y=1.5$ Mbit/s) and
  $\mathrm{com}_g=\sum_k n_{g,k}\min(r^{\max}_k,c_g)+\sum_i\min(d_i,c_g)$; $e_{PS}=\theta_P\mathrm{com}_P-\rho_P$,
  $e_{YS}=\theta_Y\mathrm{com}_Y-\rho_Y$. With demand taken as the link rate of saturated devices the
  constraints were infeasible and the queues diverged. Defaults $\theta_P=0.8$, $\theta_Y=0.6$, $\phi=0.15$.
- REPAY-WC recycles spare capacity only when every elastic device is at its cap (with negative tier
  prices, $\lambda=0$ alone does not imply that, and the deficit bound failed in a test).
- Hotspot scenario: $C_{mean}=150$ with multipliers (1.0, 0.6, 0.2).
- Priority baseline: strict priority with admission control (admit RT flows at $r^{\min}$ in priority
  order, then raise video rates equally).
