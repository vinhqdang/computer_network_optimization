# Stage 2: Algorithm Design and Theory

**TEDS: Twin-Envy Deficit Scheduling for class-screened, tier-constrained online capacity allocation**

Status: design document. Every lemma and theorem below was checked numerically on small instances (Section 5). Labels:
**PROVED** (complete proof given), **SKETCH** (the proof is routine and only outlined), **CONJECTURE** (not proved, with the evidence we have), **REFUTED** (a claim from the original design sketch that is false; a counterexample is given).

---

## 0. Summary of changes to the original sketch

| # | Original sketch | Change | Reason |
|---|---|---|---|
| C1 | RT group variables $(a,z)$ with value $n\,a\,u_k(z)$ | Use the perspective variables $(a,y)$ with $y=az$ and value $n\,a\,u_k(y/a)$ | $a\,u_k(z)$ is not jointly concave in $(a,z)$ (its Hessian is indefinite), but the perspective is jointly concave (Lemma 1). |
| C2 | Reference $\min(m_{g,k},d_i)$ with $m=az$ inside the per-slot objective | Reference $r_{i,k}=a\,\min(z,c_{i,k})$ in the queue update; in the objective an **affine majorant** $a\,\ell_{i,k}(z)\ge r_{i,k}$ | $-D\min(y,d)$ is convex, so the sketched per-slot objective is **not concave** (Lemma 2, REFUTED). With the majorant the objective is concave and solved exactly, and the proof of T1 is unchanged. $a\min(z,c)$ is also the correct expected usable RT volume, while $\min(az,d)$ is not. |
| C3 | Lindley deficit $D=\max(D+\cdot,0)$ | Default: **signed cumulative deficit** $\Delta_{i,k}=R_{i,k}-X_i$ with bonus $\Delta^+$. Lindley is kept as variant V-L | Elastic utility depends only on cumulative volume, so cumulative envy is the right object. Combined with C4, this makes credit impossible to bank beyond the device's real backlog (T3). |
| C4 | Demand cap $d_{i,t}$ declared by the device | Demand cap is **AP-verified**: $d_{i,t}=\min(\ell_{i,t},b_{i,t})$ (link rate and AP-side backlog), and the reference is capped by the **twin backlog** $c_{i,k}=\min(\ell_i,(b_i-\Delta_{i,k})^+)$ | With self-reported caps, the sketch can be gamed by credit banking: the gain was about 100x in a 2-device example (T3a, REFUTED). With the twin cap, cumulative reference never exceeds cumulative real arrivals, and credit never exceeds the backlog the device is actually holding. |
| C5 | Premium SLA unspecified; $\kappa$ includes $Q_{\max}$ terms | All main tier constraints are written **per unit of rate** (premium satisfaction ratio, PAYG revenue, free floor/cap) | Per-unit tier prices cancel inside a tier, so $B=Vw\eta_k+r^{\max}_k$ does not depend on $Q$ and no projection of $Q$ is needed. A per-flow RT-admission SLA is variant V-S, and it puts $Q_{\max}/r^{\min}$ back into $B$. |
| C6 | Deficit vs. $m_{g,k}$ even when tier $g$ has no class-$k$ flow | The reference is $0$ when $n_{g,k}=0$ (standard envy-freeness). The phantom-entrant reference is optional | A phantom term that is not part of the optimisation breaks the $O(1/V)$ argument (T4). T1 and T2 survive the phantom. |
| C7 | Strict IC claim against "any dynamic re-declaration" | Exact within-trajectory envy (T2a), price-taking IC for **static** declaration (T2b), an exact deviation identity with an explicit externality term (T2c). Mixed E/RT switching is a CONJECTURE | What is provable without price-taking is the within-trajectory statement. |
| C8 | $\kappa=w\,u_{\max}/r^{\min}$ | $\Theta_{g,k}=V\,w_{g,k}\,\eta_k$ with $\eta_k=\max_{z\in[r^{\min}_k,r^{\max}_k]}u_k(z)/z$, refined to $\Theta\,n/(n+1)$ | Tighter. Numerically, the refined bound is asymptotically tight. |

---

## 1. Model and notation

**Slots.** $t=1,2,\dots$. At the start of slot $t$ the operator observes $\omega_t$, which contains the capacity $C_t>0$, the active device set $\mathcal N_t$, and the per-device data below. Nothing about $\omega_{t+1},\omega_{t+2},\dots$ is known.

**Tiers** $g\in\mathcal G=\{F,P,Y\}$ (free, premium, pay-as-you-go). The tier is the billing identity: it is verified and cannot be misreported. **RT classes** $k\in\mathcal K$, e.g. $V$ (video) with $[r^{\min}_V,r^{\max}_V]$ and $G$ (gaming) with $r^{\min}_G=r^{\max}_G=r_G$. **Declared class** $\hat c_i\in\{E\}\cup\mathcal K$, which may be false.

**RT flows.** $n_{g,k,t}$ is the number of active flows declared $(g,k)$. Each flow's per-slot utility is $u_k(z)$ for a rate $z\in[r^{\min}_k,r^{\max}_k]$. A rate below $r^{\min}_k$ is worthless and a rate above $r^{\max}_k$ is useless. $u_k$ is concave, nondecreasing and $\ge 0$ on $[r^{\min}_k,r^{\max}_k]$. Define $\eta_k:=\max_{z\in[r^{\min}_k,r^{\max}_k]}u_k(z)/z$ (if $u_k(z)/z$ is decreasing, $\eta_k=u_k(r^{\min}_k)/r^{\min}_k$).

**RT decision (group, perspective form).** For every group with $n_{g,k}\ge1$, choose an admission fraction $a_{g,k}\in[0,1]$ and a common rate $z_{g,k}\in[r^{\min}_k,r^{\max}_k]$, written as $y_{g,k}=a_{g,k}z_{g,k}\in[a\,r^{\min}_k,a\,r^{\max}_k]$. The group uses capacity $n_{g,k}y_{g,k}$ and earns expected utility $n_{g,k}\,a\,u_k(y/a)$ (defined as $0$ at $a=0$). Section 3.4 explains how a fractional $a$ is implemented.

**Elastic devices** $i\in\mathcal E_t$ with tier $g_i$. The AP observes
- the backlog $b_{i,t}$ (bytes queued for $i$ after this slot's arrivals $A_{i,t}$: AP-side downlink queue, or uplink buffer reports with grant accounting, Section 6), and
- the link-rate cap $\ell_{i,t}$ (PHY rate).

Demand cap $d_{i,t}=\min(\ell_{i,t},b_{i,t})$. Allocation $x_{i,t}\in[0,d_{i,t}]$, and $b_{i,t+1}=b_{i,t}-x_{i,t}+A_{i,t+1}$. In the **saturated** (full-buffer) special case $b\equiv\infty$ and $d_{i,t}=\ell_{i,t}$. True elastic preference: any nondecreasing function of cumulative delivered volume $X_i=\sum_t x_{i,t}$ over the sojourn $[\alpha_i,\beta_i]$. The operator's surrogate is $w_{g,E}\,u(x)$ with $u(x)=\frac{(1+x)^{1-\alpha}-1}{1-\alpha}$ ($\log(1+x)$ for $\alpha=1$), so $u'(x)=(1+x)^{-\alpha}\le1$.

**Capacity:** $\sum_{g,k}n_{g,k}y_{g,k}+\sum_{i\in\mathcal E_t}x_i\le C_t$.

**Tier rate.** $\rho_{g,t}:=\sum_k n_{g,k}y_{g,k}+\sum_{i\in\mathcal E_t:g_i=g}x_i$.

**Tier constraints (time-average $\le 0$ of $e_j$).** Every constraint is linear in the tier rates, i.e. **per unit of rate**:

| $j$ | meaning | $e_{j,t}$ |
|---|---|---|
| PS | premium satisfaction ratio $\ge\theta_P$ | $\theta_P\,\mathrm{dem}_{P,t}-\rho_{P,t}$, with $\mathrm{dem}_{P}=\sum_k n_{P,k}r^{\max}_k+\sum_{i\in P}d_i$ |
| RV | PAYG revenue rate $\ge\varrho$ at unit price $p$ | $\varrho-p\,\rho_{Y,t}$ |
| FF | free floor | $\min(\phi_{lo}C_t,\mathrm{dem}_{F,t})-\rho_{F,t}$ |
| FC | free cap | $\rho_{F,t}-\phi_{hi}C_t$ |

Each constraint has a virtual queue $Q_j(t+1)=\max(Q_j(t)+e_{j,t},0)$. These queues persist through churn. The induced per-unit **tier price** is
$$\beta_{g,t}=Q_{PS}\mathbb 1_{g=P}+p\,(Q_{RV}+V\varpi)\mathbb 1_{g=Y}+(Q_{FF}-Q_{FC})\mathbb 1_{g=F},$$
where $\varpi\ge0$ is an optional operator weight on revenue. $\beta_g$ can be negative.

**Twin-envy deficit.** For every elastic $i$ and RT class $k$:
$$c_{i,k,t}=\min\big(\ell_{i,t},(b_{i,t}-\Delta_{i,k}(t))^+\big),\qquad r_{i,k,t}=a_{g_i,k,t}\,\min(z_{g_i,k,t},c_{i,k,t}),$$
$$\Delta_{i,k}(t+1)=\Delta_{i,k}(t)+r_{i,k,t}-x_{i,t},\qquad \Delta_{i,k}(\alpha_i)=0 .$$
Take $r=0$ if $n_{g_i,k,t}=0$. In the saturated case $c_{i,k,t}=\ell_{i,t}$.

**Interpretation (fluid twin).** Let $R_{i,k}(s,t)=\sum_{\tau=s}^t r_{i,k,\tau}$ and $X_i(s,t)=\sum_{\tau=s}^t x_{i,\tau}$. Then $\Delta_{i,k}(t+1)=R_{i,k}(\alpha_i,t)-X_i(\alpha_i,t)$, and $b_{i,t}-\Delta_{i,k}(t)=A^{\rm cum}_i(t)-R_{i,k}(\alpha_i,t-1)$ is exactly the backlog of a *fluid twin*: a class-$k$ RT flow of the same tier that has the same arrivals, faces the realised offers $(a,z)$, and receives in expectation $a\min(z,\ell,\text{its backlog})$. So $R_{i,k}$ is the expected volume that device $i$ would have received in this trajectory had it declared $k$. No extra state is needed beyond $(b_i,\Delta_{i,k})$.

**Affine majorant.** For $c\ge0$ define $\ell_{c}(z)\ge\min(z,c)$ on $[r^{\min},r^{\max}]$:
$$\ell_c(z)=\begin{cases}z,&c\ge r^{\max}\\ c,&c\le r^{\min}\\ (1-s)c+sz,\ s=\frac{c-r^{\min}}{r^{\max}-r^{\min}},&\text{otherwise.}\end{cases}$$
It is exact when $c\notin(r^{\min},r^{\max})$, and the gap is at most $(c-r^{\min})(r^{\max}-c)/(r^{\max}-r^{\min})\le(r^{\max}-r^{\min})/4$. Write $\ell_{i,k}:=\ell_{c_{i,k}}$ with coefficients $(s_{i,k},(1-s_{i,k})c_{i,k})$, i.e. $\ell_{i,k}(z)=\sigma_{i,k}+s_{i,k}z$.

**Debt coefficients** of group $(g,k)$:
$$\pi_{g,k}=\sum_{i\in\mathcal E,g_i=g}\Delta^+_{i,k}s_{i,k},\qquad \zeta_{g,k}=\sum_{i\in\mathcal E,g_i=g}\Delta^+_{i,k}\sigma_{i,k}.$$
**Bonus** of elastic $i$: $D_i=\sum_k\Delta^+_{i,k}$.

---

## 2. Benchmark problem (P)

Rewards: $U_t=\sum_{g,k}w_{g,k}n_{g,k}a_{g,k}u_k(z_{g,k})+\sum_{i\in\mathcal E_t}w_{g_i,E}u(x_{i,t})$ (optionally $+\varpi\,p\,\rho_{Y,t}$).

**Assumption A-T4.**
- (i) Saturated elastic devices ($d_{i,t}=\ell_{i,t}$, AP-measured).
- (ii) The population process $\{\mathcal N_t\}$ is exogenous: it does not depend on the operator's actions. Each $\mathcal N_t$ contains at most $N_{\max}$ devices, each with a tier and a class.
- (iii) Given $\mathcal N_t=\mathcal N$ and the whole past, the slot noise $(C_t,\ell_t)$ is drawn independently from a distribution $F_{\mathcal N}$.
- (iv) Boundedness: $|e_{j,t}|\le e^{\max}_j$, $\ell_{i,t}\le\ell^{\max}$, $U_t\le U^{\max}$.

**Population-conditional benchmark.** For a population state $\mathcal N$, let $\Pi(\mathcal N)$ be the set of randomized maps $\pi:(C,\ell)\mapsto(a,y,x)$ that are feasible slot by slot and satisfy
$$\mathbb E_{F_{\mathcal N}}[e_j]\le0\ \ \forall j,\qquad \mathbb E_{F_{\mathcal N}}\big[a_{g_i,k}\,\ell_{i,k}(z_{g_i,k})-x_i\big]\le0\ \ \forall i\in\mathcal E(\mathcal N),\ k\ \text{with}\ n_{g_i,k}\ge1. \tag{EF}$$
$$\text{(P)}\qquad U^*(\mathcal N)=\sup_{\pi\in\Pi(\mathcal N)}\mathbb E_{F_{\mathcal N}}[U(\pi)] .$$

(EF) is **stationary class-envy-freeness**: in expectation, each elastic device receives at least what a same-tier RT twin is offered. With the majorant it is slightly stronger than true envy-freeness, and identical when no $\ell_{i}$ falls in $(r^{\min}_k,r^{\max}_k)$, which is the typical case: elastic link rates are far above video rates. Because every per-slot problem is concave, a deterministic map attains the supremum, and no randomisation is needed in the fluid model.

**Honest note.** (P) imposes the tier constraints conditionally on each population state. An unconditional benchmark could trade tier constraints across population states and would be at least as large; see Conjecture 3.

---

## 3. Algorithm TEDS

### 3.1 Per-slot problem (concave)

$$\max_{a,y,x}\ \sum_{(g,k):n_{g,k}\ge1}\Big[V w_{g,k}n_{g,k}\,a\,u_k(y/a)+(n_{g,k}\beta_g-\pi_{g,k})\,y-\zeta_{g,k}\,a\Big]+\sum_{i\in\mathcal E}\Big[Vw_{g_i,E}\,u(x_i)+(\beta_{g_i}+D_i)\,x_i\Big]$$
$$\text{s.t. } \sum n_{g,k}y_{g,k}+\sum_i x_i\le C,\quad 0\le a\le1,\ a r^{\min}_k\le y\le a r^{\max}_k,\quad 0\le x_i\le d_i .$$

This is the drift-plus-penalty expression
$$V U+\sum_j Q_j(-e_j)+\sum_{i,k}\Delta^+_{i,k}\big(x_i-a\,\ell_{i,k}(z)\big),$$
up to terms that do not depend on the decision.

**Lemma 1 (concavity). PROVED.** The per-slot objective is jointly concave and the feasible set is convex.

*Proof.* $(a,y)\mapsto a\,u_k(y/a)$ is the perspective of a concave function, hence concave. The debt term $-\Delta^+a\,\ell_{i,k}(y/a)=-\Delta^+(\sigma_{i,k}a+s_{i,k}y)$ is linear. Everything else is concave (the $u$ terms) or linear (the $\beta$ and $D$ terms). The constraints are linear. $\square$

**Lemma 2 (sketch's objective is non-concave). PROVED; it REFUTES the implicit claim in the sketch.**
- (a) $a\,u_k(z)$ has Hessian $\begin{psmallmatrix}0&u_k'\\u_k'&a u_k''\end{psmallmatrix}$, with determinant $-u_k'^2<0$, so it is indefinite in $(a,z)$.
- (b) $-D\min(y,d)$ is convex in $y$: at $D=d=1$, $f(1)=-1<\tfrac12(f(0)+f(2))=-\tfrac12$.

So the original per-slot objective is not concave, and a KKT/bisection solver would not be exact for it. C1 and C2 repair both problems.

### 3.2 Exact solver (bisection on the capacity price $\lambda$)

Lagrangian decomposition at price $\lambda\ge0$.

**Elastic devices** (closed form):
$$x_i(\lambda)=\begin{cases}d_i,&\lambda\le\beta_{g_i}+D_i\\ \mathrm{clip}\Big(\big(\tfrac{\lambda-\beta_{g_i}-D_i}{Vw_{g_i,E}}\big)^{-1/\alpha}-1,\ 0,\ d_i\Big),&\text{else.}\end{cases}$$

**RT groups.** For fixed $z$ the group's Lagrangian is linear in $a$: $a\,\psi_{g,k}(z;\lambda)$, where
$$\psi_{g,k}(z;\lambda)=n_{g,k}\big[Vw_{g,k}u_k(z)+(\beta_g-\lambda)z\big]-\pi_{g,k}z-\zeta_{g,k}.$$
- $\psi$ is concave in $z$, so $z^*(\lambda)=\arg\max_{[r^{\min},r^{\max}]}\psi$ is a one-dimensional concave problem. For $u_V=1+\log(z/r^{\min})$ it is closed form: $z^*=\mathrm{clip}\big(nVw/(n(\lambda-\beta)+\pi)\big)$, and $r^{\max}$ if the denominator is $\le0$.
- $a^*(\lambda)=\mathbb 1\{\psi(z^*;\lambda)>0\}$.

**Monotonicity.** The capacity used, $S(\lambda)=\sum n\,a^*z^*+\sum x_i$, is nonincreasing in $\lambda$:
- $x_i(\lambda)$ is nonincreasing;
- $z^*(\lambda)$ is nonincreasing because $\psi$ has decreasing differences in $(z,\lambda)$;
- $a^*$ is nonincreasing because $\max_z\psi(z;\lambda)$ decreases in $\lambda$.

**Algorithm SOLVE.**
1. If $S(0)\le C$, return the allocation at $\lambda=0$.
2. Otherwise set $\lambda_{lo}=0$ and $\lambda_{hi}=\max\{\max_i(Vw_{g_i,E}+\beta_{g_i}+D_i),\ \max_{g,k}(Vw_{g,k}\eta_k+\beta_g)\}^+$; then $S(\lambda_{hi})=0$.
3. Bisect until $\lambda_{hi}-\lambda_{lo}\le\epsilon$, keeping $S(\lambda_{lo})>C\ge S(\lambda_{hi})$.
4. Take the allocation at $\lambda_{hi}$. Let $\mathcal M=\{(g,k):a^*(\lambda_{lo})=1,a^*(\lambda_{hi})=0\}$ (the marginal groups). Fill the residual $C-S(\lambda_{hi})$ by giving the groups in $\mathcal M$ fractional $a=\min\big(1,\mathrm{res}/(n z^*(\lambda_{hi}))\big)$, in sequence.

**Theorem 6 (solver exactness). PROVED.** As $\epsilon\to0$, SOLVE returns an optimal solution of the per-slot problem. The cost is $O\big((N+|\mathcal G||\mathcal K|)\log_2(\lambda_{hi}/\epsilon)\big)$ operations, plus $O(N|\mathcal K|)$ to build $(\pi,\zeta,D)$.

*Proof.* The problem is concave (Lemma 1), and Slater holds because $x=0,a=0$ leaves slack $C>0$. So strong duality holds with some optimal $\lambda^*$. Any primal point that maximises the Lagrangian at $\lambda^*$ and satisfies complementary slackness is optimal. At $\lambda^*$:
- the maximisers $x_i$ and $z^*$ are unique ($u,u_k$ strictly concave; for a constant-rate class $z$ is fixed);
- $a$ is free in $[0,1]$ exactly for groups with $\psi(z^*;\lambda^*)=0$.

$S(\lambda^*{-})\ge C\ge S(\lambda^*{+})$ by monotonicity, so the marginal groups can be given fractional $a$ that make capacity tight, or $\lambda^*=0$ with slack. Step 4 is this construction at $\lambda_{hi}\downarrow\lambda^*$. Continuity of $x_i$ and $z^*$ in $\lambda$ gives convergence. $\square$

Numerically, the gap to CLARABEL is $\le 3.4\times10^{-8}$ on 300 random instances (Section 5, check N1). Only the marginal group(s) are fractional, so generically at most one group per slot has $0<a<1$.

### 3.3 TEDS pseudocode (per slot $t$)

```
input: C_t; RT counts n[g,k]; elastic devices i with tier g_i, backlog b_i, link rate ell_i;
       state Q_j, Delta[i,k]
1  for each elastic i:  d_i = min(ell_i, b_i);  D_i = sum_k max(Delta[i,k],0)
       for k: c[i,k] = min(ell_i, max(b_i - Delta[i,k], 0)); (s,sigma)[i,k] = majorant(c[i,k], rmin_k, rmax_k)
2  beta_g from Q (Section 1);  pi[g,k] = sum_i Delta+ s;  zeta[g,k] = sum_i Delta+ sigma
3  (lambda, a, z, x) = SOLVE(C_t, V, n, w, beta, pi, zeta, {d_i, D_i})
4  implement: ROUND(a) -> admitted RT flows (incumbents first), rates z; elastic rates x (Section 3.4)
5  for each elastic i, k:  Delta[i,k] += a[g_i,k] * min(z[g_i,k], c[i,k]) - x_i      # ex-ante reference
   b_i -= x_i (delivered bytes)
6  for each j: Q_j = max(Q_j + e_j(t), 0)
7  churn: departing i -> drop Delta (store min(Delta,0) for tau_mem slots, keyed by subscriber id);
          arriving i -> Delta = restored negative part or 0
```

About 250 lines of numpy. The reference implementation used for the checks is `core.py` (90 lines) plus a 40-line driver.

**Parameters and recommended defaults**

| parameter | role | default |
|---|---|---|
| $V$ | utility vs. queue weight; also scales the envy bound $B$ | choose $V=(\varepsilon_{\rm vol}-r^{\max}_V)/(w\,\eta_V)$, where $\varepsilon_{\rm vol}$ is the tolerated envy in volume (e.g. 10 s of video at $r^{\max}$); in normalised units $V\in[10,100]$ |
| $w_{g,c}$ | tier/class weights | $w_{P,\cdot}=1.5$, $w_{F,\cdot}=w_{Y,\cdot}=1$; same weight for E and RT within a tier (this satisfies the calibration (Cal), Prop. 2) |
| $\alpha$ | elastic fairness | $1$ (proportional fair) |
| $u_V$ | video utility | $1+\log(z/r^{\min}_V)$ on $[r^{\min}_V,r^{\max}_V]$ ($u(z)/z$ decreasing, $\eta_V=1/r^{\min}_V$) |
| $u_G$ | gaming | $1$ at $r_G$ |
| $\theta_P,\varrho,\phi_{lo},\phi_{hi}$ | tier targets | operator input; check Slater feasibility (Section 4.4) |
| $\varpi$ | revenue weight | $0$ (revenue is enforced only as a constraint) |
| $\epsilon$ | bisection tolerance | $10^{-9}\lambda_{hi}$ (about 35 iterations) |
| $\tau_{\rm mem}$ | surplus memory after departure | 1 hour |
| optional $\gamma_k\in(0,1]$ | envy slack (V-γ) | $1$ |

### 3.4 Implementing a fractional $a$, and what the reference means

For a group with fractional $a$ (generically only the marginal one):
- Admit $M=\lfloor na\rfloor+\mathrm{Bernoulli}(na-\lfloor na\rfloor)$ flows at rate $z$, **incumbents first**: ongoing calls keep their slot, so call-admission semantics are preserved, and blocked new calls are retried each slot.
- **Rounding rule ROUND.** The extra (Bernoulli) flow's capacity, at most $z\le r^{\max}_k$, is taken from elastic devices in increasing order of marginal value $Vw u'(x_i)+\beta+D_i$. It is never taken from a *protected* device, i.e. one with some $k'$ such that $\Delta_{i,k'}\ge\Theta_{g_i,k'}$ and $a_{g_i,k'}>0$. If this is impossible, the extra flow is not admitted.

The deficit update uses the **ex-ante** reference $a\min(z,c)$. With incumbents-first, a new entrant (which is what a misreporting elastic device would be) is admitted with probability at most $a$. The reference therefore overstates the deviant's RT outcome, which is conservative in favour of elastic devices. ROUND never lowers $x_i$ for protected devices, so T1 holds exactly for the implemented allocation.

### 3.5 Variants
- **V-L (Lindley).** $\Delta\leftarrow\max(\Delta+a\min(z,d)-x,0)$, without the twin cap. T1 holds with the same $B$ and gives *every-window* envy, but it allows backlog-sitting credit (T3).
- **V-S (per-flow RT-admission SLA for premium).** Adds $n_{P,k}Q_{\rm adm}a$ to the group objective. The queue must be capped at $Q_{\max}$, and $\Theta_{P,k}$ becomes $Vw\eta_k+Q_{\max}/r^{\min}_k$.
- **V-M (single per-device deficit against the best class).** Reference $\max_k a_k\min(z_k,c)$; the majorant term $-\Delta^+\max_k(\cdot)$ is still concave. The per-tier subproblem couples the classes, so use cvxpy or enumerate the $|\mathcal K|$ argmax cases. This is needed for dynamic RT-class switching (T2d).
- **V-γ (envy slack).** Reference $\gamma_k a\min(z,c)$. This gives RT more protection in overload, and the price-taking IC gain grows by $(1-\gamma_k)R$.
- **V-Φ (phantom entrant).** For an empty group, a reference computed post hoc as the offer that a single debt-paying entrant would get at the realised $\lambda$. T1 and T2 still hold; T4 is not covered.
- **V-R (robust capacity).** Plan RT on a lower quantile $\hat C_t$, and let elastic devices absorb the realised surplus. A shortfall is cut first from non-protected elastic devices. T1 holds in every slot where the shortfall is at most the non-protected elastic allocation.

---

## 4. Theorems

Throughout, SOLVE is exact (Theorem 6), ROUND is used, and
$$\Theta_{g,k}:=V\,w_{g,k}\,\eta_k,\qquad B_{g,k}:=\Theta_{g,k}+r^{\max}_k .$$

### 4.1 T1: deterministic deficit bound

**Theorem 1. PROVED.** For **every** sequence of capacities, arrivals, departures, backlogs, link rates and **arbitrary** tier prices $\beta_{g,t}\in\mathbb R$ (so for any $Q$, capped or not), every elastic device $i$, every RT class $k$ and every slot in its sojourn:
$$\Delta_{i,k}(t)\le B_{g_i,k}.$$
Moreover $\Delta_{i,k}(t+1)\le b_{i,t}-x_{i,t}$: credit never exceeds the backlog held after service.

*Proof.* Fix $i$, $k$, $g=g_i$ and a slot $t$. Write $\Delta=\Delta_{i,k}(t)$.

*Step 1: $\Delta\ge\Theta_{g,k}$ implies the increment is $\le0$.* If $a_{g,k}=0$ then $r_{i,k}=0$ and the increment $-x_i\le0$. Suppose instead $a_{g,k}>0$ and $x_i<d_i$. KKT (strong duality, Theorem 6) gives two facts:
- (a) since $x_i<d_i$: $Vw_{g,E}u'(x_i)+\beta_g+D_i\le\lambda$, so $\lambda-\beta_g\ge D_i\ge\Delta^+$;
- (b) since $a>0$: $\psi_{g,k}(z;\lambda)\ge0$ at the chosen $z$, so
$n Vw_{g,k}u_k(z)\ge n(\lambda-\beta_g)z+\pi z+\zeta\ge n(\lambda-\beta_g)z$, using $\pi,\zeta\ge0$.

Combining, $n\Delta^+z\le nVw_{g,k}u_k(z)$, i.e. $\Delta^+\le Vw_{g,k}u_k(z)/z\le\Theta_{g,k}$. Strict inequality holds unless all of these hold with equality; the generic tie at equality only lowers the bound. So if $\Delta>\Theta$, either $a=0$ or $x_i=d_i$. In the latter case, $\Delta\ge0$ gives $c_{i,k}\le\min(\ell_i,b_i)=d_i$, so $r_{i,k}=a\min(z,c)\le d_i=x_i$. ROUND does not reduce $x_i$ for such a device.

*Step 2: induction.* The increment is $r-x\le r\le r^{\max}_k$. If $\Delta(t)\le\Theta$ then $\Delta(t+1)\le\Theta+r^{\max}$. If $\Delta(t)>\Theta$ then $\Delta(t+1)\le\Delta(t)$. Since $\Delta(\alpha_i)\le0$, the bound follows.

*Backlog claim.* $r\le c\le(b-\Delta)^+$. If $\Delta\ge0$ this is $b-\Delta$. If $\Delta<0$ then $b-\Delta>0$ and $c\le b-\Delta$. Either way $\Delta+r-x\le b-x$. $\square$

**Remark (refinement). PROVED.** Keep the debt term in (b). If $c_{i,k}\ge z$ (e.g. $\ell_i\ge r^{\max}$), then $\Delta^+(nz+z)\le nVwu(z)$, so $\Delta\le\Theta_{g,k}\,\bar n/(\bar n+1)+r^{\max}_k$, where $\bar n$ is the largest group size. The tier prices $\beta_g$ cancel because they are per unit and identical for E and RT inside a tier; this is why C5 matters.

**Why T1 does not need the debt price.** Step 1 only uses the bonus $D_i$. The debt price $\pi,\zeta$ is needed for T4 (optimality), not for T1.

### 4.2 T2: incentive properties of class declaration

**Theorem 2a (within-trajectory class-envy-freeness). PROVED.** On every sample path, for every elastic $i$, $k$ and $t\le\beta_i$:
$$X_i(\alpha_i,t)\ \ge\ R_{i,k}(\alpha_i,t)-B_{g_i,k},$$
where $R_{i,k}$ is the expected volume of the fluid twin (Section 1). Over a sojourn of length $L$, the average-rate envy is $\le B/L$.

For variant V-L the stronger window statement holds: $X_i(s,t)\ge\sum_{\tau=s}^t a\min(z,d_i)-B$ for all $\alpha_i\le s\le t$.

*Proof.* The identity $\Delta(t+1)=R-X$ plus T1. For V-L, $D(t+1)=\max_s\sum_{s}^{t}(r-x)$ (Lindley), plus T1. $\square$

**Price-taking hypothesis (H-PT).** A single device's declaration does not change the offers $\{(a_{g,k,t},z_{g,k,t})\}$, and a deviant to class $k$ receives the twin volume $R_{i,k}$. This is the large-market idealisation used in strategy-proofness in the large; the exact externality is measured by T2c.

**Theorem 2b (static ε-IC for elastic devices). PROVED under H-PT.** Let $f$ be any nondecreasing elastic preference. Consider declaring a single class $k$ for the whole sojourn instead of $E$. The volume gain is at most $B_{g,k}$, i.e. $f(X^{\rm truth})\ge f(R_{i,k}-B_{g,k})$ while the deviation yields $f(R_{i,k})$. Per slot this is $\varepsilon=B_{g,k}/L$.

*Proof.* Theorem 2a on the truthful trajectory, plus H-PT for the deviation. $\square$

**Theorem 2c (exact deviation identity). PROVED, no H-PT.** Let $R^{\rm dev}_{i,k}$ be the expected volume that $i$ receives as a class-$k$ flow in the **deviation** trajectory, and $R^{\rm tr}_{i,k}$ its twin reference in the truthful trajectory. Then
$$X^{\rm dev}_i-X^{\rm tr}_i\ \le\ B_{g,k}+\underbrace{\big(R^{\rm dev}_{i,k}-R^{\rm tr}_{i,k}\big)}_{\text{externality / feedback term}} .$$
*Proof.* $X^{\rm dev}=R^{\rm dev}$ by definition, and $X^{\rm tr}\ge R^{\rm tr}-B$ by T2a. $\square$

The externality term combines two effects: the deviant raises $n_{g,k}$ by one, and it removes its own bonus and debt, so the deficits evolve differently. We have no general bound on it; experiment E3 measures it. In the examples of Section 5 it is $\le0.001$ per slot.

**T2d (dynamic re-declaration).**
- *RT-only switching* (the device chooses $k_t\in\mathcal K$ per slot), with variant V-M: $X^{\rm tr}\ge\sum_t\max_k r_{i,k,t}-B$, which is at least the volume of any RT switching sequence under H-PT. **SKETCH** (same proof as T1 with $\max_k$; the KKT step uses the active $k$).
- With per-$(i,k)$ deficits, only $X^{\rm tr}\ge\max_k R_{i,k}-B$ holds, so the dynamic RT-switching gain can be up to about $(|\mathcal K|-1)\max_kR_k$.
- *Mixed E/RT switching* (re-associating with a different class): **CONJECTURE 1**. Under H-PT the gain over truthful E is $O(B\cdot\#\text{switches})$. Each switch forfeits positive credit; with $\tau_{\rm mem}$, surplus is not reset. Not proved, because the analysis gives no upper bound on an elastic allocation in uncongested slots.

**Proposition 2 (reverse direction: RT declaring E, zero debts). PROVED under H-PT.** Assume the calibration condition (Cal) on $[r^{\min}_k,r^{\max}_k]$:
- (i) $w_{g,k}u_k'(z)\ge w_{g,E}u'(z)$, and
- (ii) $w_{g,k}u_k(r^{\min}_k)>r^{\min}_k\,w_{g,E}u'(r^{\min}_k)$.

Suppose all deficits in tier $g$ are $\le0$ in slot $t$. Then the class-$k$ offer gives the true RT device at least the per-slot true utility it would obtain as E, namely $\tilde u_k(x)=u_k(\min(x,r^{\max}))\mathbb 1\{x\ge r^{\min}\}$.

*Proof.* Let $\lambda'=\lambda-\beta_g$. As E the device gets $x\le\hat x$, where $Vw_Eu'(\hat x)=\lambda'$ ($\hat x=\infty$ if $\lambda'\le0$). $\tilde u$ is nondecreasing, so it suffices to compare with $\hat x$. If $\hat x<r^{\min}$ then $\tilde u=0$. Otherwise let $\bar x=\min(\hat x,r^{\max})$. By (i), $Vw_ku_k'(\bar x)\ge Vw_Eu'(\bar x)\ge Vw_Eu'(\hat x)=\lambda'$, so $\psi$ (with no debts) is nondecreasing on $[r^{\min},\bar x]$ and $z^*\ge\bar x$. By (ii) and $\lambda'\le Vw_Eu'(r^{\min})$: $\max_z\psi\ge n[Vw_ku_k(r^{\min})-\lambda'r^{\min}]>0$, so $a=1$. Hence the RT utility is $u_k(z^*)\ge u_k(\bar x)=\tilde u(\hat x)$. $\square$

**Indebted case: CONJECTURE 2.** When tier-mates are indebted, the debt price lowers the RT offer, and a device posing as E collects a bonus of its own. A gain is then conceivable. The fact that works against it: E service is bursty, and for $u_k(z)/z$ nonincreasing, $\sum_t\tilde u_k(x_t)\le\eta_k\sum_tx_t$, so bursts are worth less to an RT device than a steady rate. Numerically (check N7): over 54 configurations, no gain whenever (Cal) holds. A gain of $+0.037$ appears only with $w_E=2w_V$, where (Cal-i) is violated for $z>1$.

### 4.3 T3: demand-cap manipulation

**T3a. REFUTED (sketch with self-reported caps).** "Over-reporting $d_i$ yields no usable gain" is false. Counterexample (check N5):
- Setup: $C=1$, one same-tier video flow, an honest saturated elastic device H, and an elastic device A whose true demand is 5 in one slot out of 40 and 0 otherwise. $V=10$.
- Banking strategy for A: in idle slots, report $\hat d=5$ while its deficit is below $\tau$, then report $0$ to *hold* the credit (the increment is $\min(m,0)-0=0$), and cash the credit in the on-slot.
- Result: A's useful volume rises from $8\times10^{-5}$ to $8.25\times10^{-3}$ per slot ($\approx100\times$; per on-slot from $0.003$ to $0.33$). H's volume drops from $0.499$ to $0.333$.
- The same happens with a signed deficit. The cause is the self-reported cap, not the Lindley form.

**Theorem 3b (verified backlog + twin reference). PROVED.** With $d=\min(\ell,b)$ AP-measured and $c_{i,k}=\min(\ell,(b-\Delta)^+)$:
1. $R_{i,k}(\alpha_i,t)\le A^{\rm cum}_i(t)$: the cumulative reference never exceeds the bytes that actually arrived.
2. $\Delta_{i,k}(t+1)\le b_{i,t}-x_{i,t}$: to hold credit $\Delta$, the device must keep $\Delta$ real bytes queued (use-it-or-lose-it).
3. Under H-PT, injecting $J$ junk bytes raises $R_{i,k}$ by at most $J$, so the guaranteed volume $R-B$ rises by at most $J$. Under per-device FIFO those $J$ bytes are delivered ahead of later real data.

*Proof.*
1. $R=A^{\rm cum}-(\text{twin backlog})$, and twin backlog $=b-\Delta\ge0$.
2. This is T1's backlog claim.
3. With the offers fixed, the twin is a fluid queue with service capacity $s_t=a_t\min(z_t,\ell_t)$, and $R(t)=\min_{s\le t}\big(A^{\rm cum}(s)+\sum_{\tau=s}^{t}s_\tau\big)$-type Skorokhod output. That output is nondecreasing and 1-Lipschitz in the cumulative arrival process. $\square$

**T3c (realised junk gain): exact non-profitability REFUTED numerically; approximate version CONJECTURE 4.**
- Check N6 (FIFO, file 10 units / 40 slots, $C=1$): junk $J=2$ raises A's useful rate from $0.2495$ to $0.2497$ (+0.1%) and lowers H from $0.375$ to $0.350$. Larger $J$ strictly hurts A ($J=20$: $0.112$).
- Conjecture: the useful-volume gain from junk is $O(B)$ per sojourn. Junk is mainly a spite and waste channel: it harms others by consuming capacity. For PAYG it costs $p$ per byte. For the free tier it is bounded by $\phi_{hi}$.

**Under-reporting.** With AP-verified $d$, it is impossible. With self-reported caps it is not analysed, because self-reported caps are excluded by design (C4).

### 4.4 T4: utility optimality and tier constraints

Let $B_0=\tfrac12\sum_j(e^{\max}_j)^2+\tfrac12N_{\max}|\mathcal K|(\ell^{\max})^2$ and $\bar U^*_T=\frac1T\sum_{t<T}\mathbb E[U^*(\mathcal N_t)]$.

**Theorem 4. PROVED.** Under A-T4, if $\Pi(\mathcal N)\neq\emptyset$ for all reachable $\mathcal N$, then TEDS (fluid allocation, no phantom) satisfies for all $T$:
$$\frac1T\sum_{t<T}\mathbb E[U_t]\ \ge\ \bar U^*_T-\frac{B_0}{V},\qquad \frac1T\sum_{t<T}\mathbb E[e_{j,t}]\le\frac{\mathbb E[Q_j(T)]}{T}\le\sqrt{\frac{2(B_0+2VU^{\max})}{T}} .$$

*Proof.*

*Lyapunov function over active devices.* $L(t)=\tfrac12\sum_jQ_j(t)^2+\tfrac12\sum_{i\in\mathcal E_t}\sum_k(\Delta^+_{i,k}(t))^2$.

*Churn.* A departure removes a nonnegative term. An arrival adds $(\Delta^+)^2=0$; a restored surplus is $\le0$, so it adds 0 too. Therefore $L(t+1)\le\hat L(t+1)$, the same sum taken over $\mathcal E_t$.

*Per-term inequality.* For any $\Delta$ and $\delta$: $\tfrac12((\Delta+\delta)^+)^2\le\tfrac12(\Delta^+)^2+\Delta^+\delta+\tfrac12\delta^2$. (Check $\Delta\ge0$ and $\Delta<0$ separately.) Similarly for $Q$. Increments are bounded by $\ell^{\max}$ and $e^{\max}$.

*Drift-plus-penalty bound.*
$$\hat L(t+1)-L(t)-VU_t\le B_0+\sum_jQ_je_j+\sum\Delta^+(r-x)-VU_t\le B_0+\sum_jQ_je_j+\sum\Delta^+(a\ell_{i,k}(z)-x)-VU_t .$$
The right-hand side is minus the per-slot objective plus $B_0$. TEDS maximises that objective, so for every $\pi\in\Pi(\mathcal N_t)$ the right-hand side is at most the same expression evaluated at $\pi(\omega_t)$.

*Comparison with the benchmark.* Condition on $\mathcal H_t=(Q(t),\Delta(t),\mathcal N_t)$. By A-T4(iii), $(C_t,\ell_t)$ is independent of $(Q,\Delta)$ given $\mathcal N_t$, and $\pi$ depends only on $(\mathcal N_t,C_t,\ell_t)$. Hence
$$\mathbb E[\sum Q_je_j^\pi+\sum\Delta^+(a^\pi\ell(z^\pi)-x^\pi)\mid\mathcal H_t]=\sum Q_j\mathbb E[e^\pi_j\mid\mathcal N_t]+\sum\Delta^+\mathbb E[\cdot\mid\mathcal N_t]\le0$$
by (EF) and the tier constraints. Taking $\pi$ optimal (or $\epsilon$-optimal) for (P) at $\mathcal N_t$:
$$\mathbb E[L(t+1)-L(t)\mid\mathcal H_t]-V\mathbb E[U_t\mid\mathcal H_t]\le B_0-VU^*(\mathcal N_t).$$

*Telescoping.* Sum over $t<T$, use $L(0)=0$ and $L\ge0$, and divide by $VT$ to get the utility bound. For the constraints, $Q_j(T)\ge\sum_{t<T}e_{j,t}$, $\mathbb E[Q_j(T)]\le\sqrt{2\mathbb E[L(T)]}$, and $\mathbb E[L(T)]\le T(B_0+2VU^{\max})$ from the same telescoped inequality. $\square$

**Corollary 4' ($O(V/T)$ violation). SKETCH.** Assume uniform Slater: some $\pi\in\Pi(\mathcal N)$ has $\mathbb E[e_j\mid\mathcal N]\le-\varepsilon$ and (EF) holds with slack $\varepsilon$, for all $\mathcal N$. Then the drift is $\le B_0+2VU^{\max}-\varepsilon\sum_jQ_j$. With bounded increments, a Hajek-type argument gives $\sup_t\mathbb E[Q_j(t)]=O(V/\varepsilon)$, so the average violation is $O(V/(\varepsilon T))$. The deficits are bounded deterministically by T1 in any case.

**CONJECTURE 3 (unconditional benchmark).** Assume $\{\mathcal N_t\}$ is an ergodic Markov chain with mixing time $\tau_{\rm mix}$. Then TEDS achieves $U^{\rm unc}-O(1/V)-O(\tau_{\rm mix}\cdot\text{const}/V)$ against the benchmark whose tier constraints hold only on average over population states. The expected route is a $T$-slot drift (Neely). Per-device (EF) constraints cannot be pooled across states, because devices live across many states, and this is the delicate part.

**Scope notes.** T4 covers the saturated model. With backlog dynamics the reference cap $c=b-\Delta$ is an endogenous state, and the stationary benchmark must include the backlog process; not done. Phantom mode (V-Φ) adds an uncontrolled term $\sum\Delta^+r^{\rm ph}=O(V)$ per slot, which voids the $O(1/V)$ rate.

### 4.5 T5: baselines fail (two-device examples)

Setup for the examples: one tier, video $u_V=1+\log(z/0.5)$ on $[0.5,2]$, one saturated elastic device with $\log(1+x)$ and link rate 5, $V=10$.

**Proposition 5a (strict priority to declared RT). PROVED.** With $C\equiv0.9$:
- *Truthful:* the video gets $0.9$ and the elastic device gets 0, so envy grows by $0.9$ per slot (unbounded).
- *Elastic declares V:* there are two RT flows. With an equal split, both get $0.45<r^{\min}$, so the video has zero utility in every slot. With rotation-based admission control, the video is served in 50% of slots and the fake flow gets 0.45 per slot.
- So misreporting is strictly profitable and RT protection collapses.

**Proposition 5b (class-blind PF / equal-weight WFQ). PROVED.** With $C\equiv0.9$, both devices get $0.45<r^{\min}_V$, so the video has zero utility in every slot: no RT protection.

**Proposition 5c (plain drift-plus-penalty without deficits). PROVED (numerically verified).** With $C\equiv0.9$, the video gets $0.9$ and the elastic device 0 forever; declaring V gives the elastic device $0.45$. With $C_t$ alternating $0.6/3.0$:
- truthful elastic gets $0.5$ per slot, misreporting gets $0.9$ per slot;
- in the resulting pooling outcome the video is served in only $80\%$ of slots.

**TEDS on the same instances.**
- $C\equiv0.9$: elastic $0.449$ vs. $0.450$ if it misreports (gain $0.001$ per slot); the video is served at $r^{\min}$ in 90% of slots, which is the envy-free outcome.
- Alternating $C$: elastic $0.900$, the same as misreporting, while the video is served in **100%** of slots (vs. 80% under pooling) and its utility is $1.53$ vs. $1.35$.

The value of truthful screening is **time-shifting**: elastic volume moves to high-capacity slots. **Inherent cost:** in persistent overload, envy-freeness forces RT rationing, because per-flow RT volume cannot exceed elastic volume in the same tier. V-γ trades this off against IC slack.

### 4.6 Other design decisions
- **Fairness inside a class.** Elastic: weighted α-fair through $u$, with tier weights. RT: a common rate $z$ per $(g,k)$ and admission rotation among non-incumbents.
- **Per-(device, class) vs. per-device deficit.** The default is per $(i,k)$: the problem stays separable and the solver above is exact. Use V-M if dynamic RT-class switching is a concern.
- **PAYG price.** Enters only through the per-unit price $\beta_Y=p(Q_{RV}+V\varpi)$, so T1 is unaffected.
- **Sybil and re-arrival.**
  - Key the utilities and deficits by subscriber, i.e. billing identity. Splitting one subscriber's elastic traffic into several flows then gains nothing.
  - Cap RT flows per subscriber per class (e.g. one video flow).
  - Rejoining resets positive credit, which only hurts the device itself. The negative part (surplus) is restored within $\tau_{\rm mem}$; without memory, a device could erase its surplus by rejoining.
  - Several *billing* identities (free-tier Sybils) each obtain their own share. The total harm is bounded by the free cap $\phi_{hi}$.

---

## 5. Numerical sanity checks run

The scripts are numpy plus cvxpy/CLARABEL. Utilities as in Section 3.3, $r^{\min}_V=0.5$, $r^{\max}_V=2$, $r_G=0.1$.

| ID | What | Result |
|---|---|---|
| N1 | SOLVE vs. CLARABEL on 300 random instances ($\alpha\in\{0.5,1,2\}$, $V\in[1,50]$, random $\beta\in[-5,5]$, debts, 0–3 flows per group, 0–7 elastic devices) | relative objective gap in $[-1.4\times10^{-8},\,3.4\times10^{-8}]$; capacity never exceeded |
| N2 | Lemma 2 non-concavity; majorant property on 20 000 random $(r^{\min},r^{\max},c,z)$ | Hessian of $a(1+\log z)$ has eigenvalues $\{-1.28,0.78\}$; midpoint test $-1<-0.5$; majorant always $\ge\min(z,c)$, max gap $0.2496(r^{\max}-r^{\min})$ |
| N3 | T1 stress: 60 runs × 400 slots; random churn, bursty arrivals, link rates; capacity random or on/off adversarial; **arbitrary tier prices $\beta\in[-40,40]$** (any $Q$); $V\in\{1,10,100\}$; $\alpha\in\{0.5,1,2\}$; random weights | $\max_t\Delta/B=0.459$ (mean 0.22); the assertion $\Delta(t+1)\le b-x$ never failed |
| N4 | T1 tightness: $n$ video flows, $C=n\,r^{\min}$, one elastic device with $w_E=10^{-3}$, $V=10$, $\Theta=20$, $B=22$ | $\max\Delta$ = 10.0 ($n=1$), 17.0 ($n=5$), 20.05 ($n=50$); matches the refinement $\Theta\bar n/(\bar n+1)+r^{\max}$ and is asymptotically tight |
| N5 | T3a banking counterexample (sketch, self-reported caps) | A: $8\times10^{-5}\to8.25\times10^{-3}$ per slot; H: $0.499\to0.333$ (Lindley and signed alike) |
| N6 | Junk injection under TEDS (verified backlog, twin, FIFO), $J\in\{0,2,5,20\}$, files of 10 or 20 units / 40 slots | file 10: A $0.2495$ ($J=0$), $0.2497$ ($J=2$), $0.222$ ($J=5$), $0.112$ ($J=20$); file 20: monotone decrease $0.333\to0.167$; H always weakly hurt |
| N7 | RT device declaring E: 54 configurations ($n_{RT}\in\{0,2,6\}$, honest elastic $\in\{0,1,4\}$, i.i.d./on-off $C$, $w_E\in\{0.5,1,2\}$) | gain $\le0$ in all cases satisfying (Cal); max gain $+0.037$, only at $w_E=2$ (Cal-i violated) |
| N8 | T5 examples (Section 4.5) | numbers as reported there |
| N9 | T4: fixed population (2 V + 2 E free, 1 V + 1 E premium; $w_P=1.5$), $C\sim U[1.5,7]$ (300-point SAA), free cap 0.45, premium share 0.40, $T=2\times10^4$; benchmark (P) solved exactly with CLARABEL ($U^*=6.537$) | gap $U^*-\bar U$: 0.525 / 0.056 / 0.025 / 0.019 / 0.015 for $V=1/3/10/30/100$; free-cap violation $+0.0013$ at $V=100$ ($=Q(T)/T$, $Q=25$); premium constraint slack; $\max\Delta\le0.2B$ throughout |

---

## 6. Honest limitations

1. **IC is price-taking or within-trajectory.** The exact deviation bound (T2c) contains an externality term that we do not bound. Small markets, e.g. one RT flow per tier, are where it matters most.
2. **Empty groups.** By default, an elastic device in a tier with no class-$k$ flow has no class-$k$ reference, so a lone deviant may gain. V-Φ fixes this at the cost of the $O(1/V)$ guarantee.
3. **The envy bound is $O(V)$.** The utility gap is $O(1/V)$ but the envy bound is $B=\Theta(V)$: the usual $[O(1/V),O(V)]$ trade-off. For the IC slack to be small, sojourns must be long relative to $V\eta$. Short-lived devices on a busy hotspot get weak guarantees.
4. **Envy-freeness rations RT in overload.** If elastic tier-mates outnumber RT flows and capacity is short, video admission drops. This is a property of the objective, not a bug. V-γ and premium weights are the levers.
5. **The verified-demand assumption is essential.** It is easy for downlink, where the AP holds the queue. Uplink needs buffer reports with grant accounting (reported backlog only decreases through grants), which makes uplink misreporting equivalent to junk injection. Junk is not provably unprofitable (Conjecture 4).
6. **T4 scope.** T4 assumes saturated elastic devices, a population-conditional benchmark, and a fluid allocation (expected RT utility). Backlog dynamics and the unconditional benchmark are open (Conjecture 3).
7. **Slot model.** The model ignores intra-slot latency (gaming benefits beyond the rate are not modelled). $\eta_G=u_G/r_G$ is large for tiny $r_G$, so $B_{g,G}$ is loose; the G deficit is in effect an envy bound in *rate* only.
8. **Bisection tolerance.** It perturbs KKT by $O(\epsilon)$, and T1 then holds with $\Theta+O(\epsilon)$.

---

## 7. Experiment wish-list

**Baselines.**
- (B1) Weighted proportional fair, class-blind.
- (B2) Strict priority for declared RT, with admission control.
- (B3) WFQ with per-class weights.
- (B4) Plain drift-plus-penalty with the same tier queues but no deficits.
- (B5) TEDS-Lindley (V-L).
- (B6) Offline optimum: per-slot oracle and the stationary (P) via CLARABEL/SAA, plus the hindsight optimum with known future for small instances.

**Experiments.**

| ID | Demonstrates | Design | Metrics |
|---|---|---|---|
| E1 | T1 / T2a | Adversarial and trace-driven capacity (Wi-Fi airtime traces), heavy churn; sweep $V$ | $\max\Delta/B$, the envy CDF $\max_k(R_k-X)/L$ per device, and the refined bound vs. $\bar n$ |
| E2 | T4 | Fixed populations with i.i.d. $C$; then Markov churn (tests Conjecture 3) | $U^*-\bar U$ vs. $V$ (log–log, slope $-1$ expected); violation vs. $T$ for each tier constraint; the $V$–envy Pareto curve |
| E3 | **Strategic best response** (T2b/c, Prop. 2, Conj. 1–2) | Agent-based simulation. Each device runs a best-response or no-regret learner over {truthful, declare V, declare G, mixed switching}, plus a backlog-junk strategy. Iterate to a fixed point under every scheduler | Fraction misreporting at equilibrium; the realised externality term $R^{\rm dev}-R^{\rm tr}$; RT slot-success rate and social welfare at equilibrium (TEDS vs. B2/B4, where collapse to pooling is expected) |
| E4 | T5 and the value of screening | Capacity variability sweep (coefficient of variation from 0 to 1); compare TEDS-truthful vs. TEDS-pooled vs. B1–B4 | RT slot-success, elastic throughput, gap to OPT; show that the TEDS advantage grows with capacity variability (time-shifting) |
| E5 | T3 | Credit-banking attack against V-L with self-reported caps vs. TEDS with verified backlog; junk injection sweep | Attacker useful gain and the harm to honest devices |
| E6 | T6 | Runtime of SOLVE vs. $N\in\{10,\dots,10^4\}$ against cvxpy | ms per slot (target $<1$ ms at $N=200$) |
| E7 | Tier constraints | Premium/free/PAYG targets near the Slater boundary; PAYG price sweep | Revenue rate vs. $\varrho$; premium satisfaction; the effect on T1 (should be none) and with V-S (should grow by $Q_{\max}/r^{\min}$) |
| E8 | Robustness (V-R) | $\hat C$ with estimation error | RT drops; how often T1 is violated |
| E9 | Ablations | No debt price; $\min(az,d)$ reference; no twin cap; no surplus memory; V-M | Each against T1/T4 and the attack metrics |
