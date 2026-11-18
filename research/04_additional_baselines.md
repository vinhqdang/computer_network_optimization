# 04 Additional baselines: specifications for implementation

Status: specification only (no code). Date: 18 November 2026.

This note specifies five additional baselines for the simulator in `repay/`. They are classical flow-queueing max-min fairness (A1), an adaptation of Jaramillo and Srikant (2011) (A2), and three mechanisms from papers dated 2025 or 2026 (B1 to B3). Each specification is meant to be implementable without reading the source paper. For every adapted mechanism the note states what was changed and which guarantee of the original is lost.

---

## 0. Conventions shared by all baselines

These match `repay/mechanisms.py` and `repay/sim.py`.

**Interface.** Each baseline is a class with `__init__(self, params, ...)`, `reset(self)` (clears all state) and `allocate(self, view) -> np.ndarray`. The method returns one rate (Mbit/s) per active device, in the order of `view.ids`. The view gives `t`, `C` (capacity $C_t$), `ids`, `tier` (0 free, 1 premium, 2 PAYG), `decl` (declared class: 0 elastic E, 1 video V, 2 gaming G), `cap` and `arr` (arrival slot).

**Demand.** The per-device demand $D_i$ follows the convention of `PF` and `Credit` (`_rmax_of`):
- declared E: $D_i = d_{i,t} = $ `cap[i]` (verified demand cap; 0 while the device is "off");
- declared V: $D_i = r^{\max}_V = 3.0$;
- declared G: $D_i = r_G = 0.2$.

`view.cap` is also filled for RT devices (link rate times on/off), but the existing mechanisms ignore it for RT and so do all specifications here. **No baseline may return more than $D_i$ to a declared-E device.** The simulator counts the whole rate of a declared-E device as usable (`usable = rate` when `decl == 0`), so any excess would inflate measured utility.

**Constants** (from `Params`): $r^{\min}_V=0.5$, $r^{\max}_V=3$, $r_G=0.2$; tier weights $w=(w_F,w_P,w_Y)=(1,2,1.5)$; $V=20$. Write $w_i := w_{g_i}$.

**State and churn.** Per-device state lives in dicts keyed by device id. At the start of every `allocate`:
1. delete state of ids not in `view.ids` (departures);
2. create default state for new ids (arrivals);
3. when a device's declared class differs from the previous slot, reset its per-device state to the arrival default. This follows the `Repay._sync` convention: class-dependent state does not survive a class change.

All baselines are deterministic except A2 in its default (Bernoulli) mode. A2 uses its own `numpy.random.Generator` seeded from a constructor argument and never touches the simulator's RNG.

**Numerical tolerances.** Use `1e-12` for feasibility comparisons (as in `Priority`). Every bisection should run to a relative tolerance of `1e-10` or 100 iterations. The final allocation must satisfy $\sum_i x_i \le C_t + 10^{-9}$: if rounding pushes it over, scale down the last-filled component.

**Generic helper: weighted water-filling with lower and upper bounds.** Several baselines use this. The name `PSWC` comes from Zahedi and Freeman (2026), who take it from Freeman et al. (2018).

```
PSWC(A, w, m, l):            # w_i > 0, 0 <= m_i <= l_i (l_i may be +inf)
    if A <= sum(m): return m          # cannot happen when callers respect preconditions
    if A >= sum(l): return l
    find x >= 0 such that  S(x) := sum_i clip(x * w_i, m_i, l_i) = A
    (S is continuous and nondecreasing; bisection on x in [0, x_hi],
     x_hi = max_i (finite l_i or m_i or A) / w_i, doubled until S(x_hi) >= A)
    return clip(x * w_i, m_i, l_i)
```

An exact $O(n\log n)$ version sorts the breakpoints $m_i/w_i$ and $l_i/w_i$, but bisection is enough at our sizes.

---

## A1. Flow-queueing max-min fairness (FQ)

### Source

- T. Høiland-Jørgensen, P. McKenney, D. Täht, J. Gettys, E. Dumazet, *The Flow Queue CoDel Packet Scheduler and Active Queue Management Algorithm*, RFC 8290, IETF, 2018.
- T. Høiland-Jørgensen, D. Täht, J. Morton, *Piece of CAKE: A Comprehensive Queue Management Solution for Home Gateways*, IEEE LANMAN 2018, pp. 37–42.

```bibtex
@techreport{rfc8290,
  author = {H{\o}iland-J{\o}rgensen, Toke and McKenney, Paul and T{\"a}ht, Dave and Gettys, Jim and Dumazet, Eric},
  title = {The Flow Queue {CoDel} Packet Scheduler and Active Queue Management Algorithm},
  institution = {Internet Engineering Task Force}, type = {RFC}, number = {8290}, year = {2018}, doi = {10.17487/RFC8290}
}
@inproceedings{hoiland2018cake,
  author = {H{\o}iland-J{\o}rgensen, Toke and T{\"a}ht, Dave and Morton, Jonathan},
  title = {Piece of {CAKE}: A Comprehensive Queue Management Solution for Home Gateways},
  booktitle = {IEEE International Symposium on Local and Metropolitan Area Networks (LANMAN)},
  year = {2018}, pages = {37--42}, doi = {10.1109/LANMAN.2018.8475045}
}
```

(Both entries are already in `paper/references.bib`.)

### What the originals do

FQ-CoDel hashes packets into per-flow queues and serves them by deficit round robin with an equal byte quantum per queue. A queue that has just become active goes on a "new flows" list that is served before the "old flows" list. A flow that sends below its fair share therefore never builds a queue and is served almost immediately ("sparse-flow priority"). CoDel runs on each queue and controls its delay. CAKE uses the same flow-queueing core (DRR++) and adds a shaper and per-host isolation: by default it shares first across hosts and then across each host's flows. It also has optional Diffserv "tins" that are selected from the packet's DSCP mark. Neither scheduler knows the application class of a flow. CAKE's tins use a mark that the sender or an upstream network sets.

### Adaptation (rate level, one slot = 1 s)

At time scales much longer than a packet, deficit round robin with equal quanta gives every backlogged queue the same throughput. A flow whose offered rate is below that common level gets all of its offered rate. The rate-level equivalent is **max-min fairness with demand caps (water-filling)**:

$$x_i = \min(D_i,\ \phi_i\,\theta),\qquad \theta \text{ chosen so that } \textstyle\sum_i x_i=\min\big(C_t,\sum_i D_i\big).$$

- **Unweighted (main variant, `FQ`)**: $\phi_i = 1$ for all devices. Each device is one host and one flow, so CAKE's per-host isolation and FQ-CoDel's per-flow fairness give the same result.
- **Tier-weighted (optional, `FQ-w`)**: $\phi_i = w_i$. Neither RFC 8290 nor CAKE has per-host weights. This variant is our extension, added so that FQ can be compared with tier-aware rules.

The declared class is used only to set the demand: $D_i=r^{\max}_V$ for video and $D_i=r_G$ for gaming. That demand is what an RT application offers. Because the scheduler does not otherwise look at the class, the rule is class-blind in the same sense as the originals. A gaming flow (0.2 Mbit/s) or a video flow whose 3 Mbit/s is below the water level $\theta$ is served in full. This is the rate-level counterpart of sparse-flow priority. When $\theta < r^{\min}_V$, a video flow gets $\theta$ and fails, since nothing reserves its minimum. CAKE's Diffserv tins are **not** modelled, because they would make the rule depend on a declaration (the DSCP mark), which is exactly what this baseline is meant to avoid.

### State

None.

### Per-slot steps

1. Build $D_i$ (Section 0) and $\phi_i$.
2. If $\sum_i D_i \le C_t$, return $x=D$.
3. Otherwise return `PSWC(A=C_t, w=phi, m=0, l=D)`. For $\phi\equiv1$ this is exactly `_waterfill(C_t, D)` in `mechanisms.py`.

Arrivals and departures need no handling.

### Parameters

- `weighted=False` by default.

### Relation to existing baselines (important)

The repository's `PF` maximises $\sum_i w_i\log(1+x_i)$ with caps, which gives $x_i=\min(D_i,\max(0,w_i/\mu-1))$. When all weights are equal this is the same as unweighted water-filling. **Unweighted FQ therefore coincides with PF in any scenario where all devices share one tier**, including the default `home` scenario, where `tier_p=(0,1,0)`. FQ differs from PF only when tiers are mixed, as in the hotspot. FQ-w differs from PF whenever weights differ, because $x\propto w$ is not the same as $1+x\propto w$. This should be stated in the paper or the home results should omit FQ.

### Changes from the originals and guarantees lost

Packet-level behaviour is not modelled: no per-packet delay, CoDel drop or ECN dynamics, and no hashing collisions. The guarantee that is lost is the low *queueing delay* for sparse flows. The rate-level max-min share is kept.

### One-sentence description for the paper

"FQ is a rate-level model of flow-queueing schedulers such as FQ-CoDel and CAKE: class-blind max-min (water-filling) sharing across devices, each capped at its demand (its demand cap for elastic devices, $r^{\max}_k$ for real-time flows); it models their long-run throughput sharing, not their packet-level delay control."

---

## A2. Jaramillo–Srikant elastic/inelastic scheduling (JS)

### Source (read in full from arXiv:0907.5402v8, Sections II–V)

J. J. Jaramillo, R. Srikant, *Optimal Scheduling for Fair Resource Allocation in Ad Hoc Networks With Elastic and Inelastic Traffic*, IEEE/ACM Transactions on Networking 19(4):1125–1136, 2011 (DOI and pages confirmed via Crossref).

```bibtex
@article{jaramillo2011elastic,
  author  = {Jaramillo, Juan Jose and Srikant, R.},
  title   = {Optimal Scheduling for Fair Resource Allocation in Ad Hoc Networks With Elastic and Inelastic Traffic},
  journal = {IEEE/ACM Transactions on Networking},
  volume  = {19}, number = {4}, pages = {1125--1136}, year = {2011},
  doi     = {10.1109/tnet.2010.2100083}, eprint = {0907.5402}, archivePrefix = {arXiv}
}
```

### The original mechanism

Time is divided into frames of $T$ slots. Each link $l$ carries both inelastic and elastic traffic. Inelastic packets arrive at the start of a frame ($a_{il}$ of them), must be served within that frame, and are dropped otherwise. The loss probability from missed deadlines must be at most $p_l$, i.e. the delivery ratio must be at least $1-p_l$. Elastic traffic has a concave utility $U_l(x_l)$ of its admitted rate $x_l$. The static problem maximises $\sum_l U_l(x_l)+w_l\,\mu_{il}$ subject to $\mu_{il}\ge\lambda_l(1-p_l)$, where $w_l\ge0$ optionally rewards inelastic service beyond the requirement. The online algorithm comes from dual decomposition. In frame $k$:

- **Congestion control (elastic):** $\tilde x_l(k)\in\arg\max_{0\le x\le X_{\max}} \frac1\epsilon U_l(x)-q_l(k)\,x$, where $q_l(k)$ is the elastic queue at link $l$. Elastic arrivals with mean $\tilde x_l(k)$ enter the queue.
- **Scheduling (max-weight):** choose a feasible schedule $s$ maximising $\sum_l\big[(\tfrac{w_l}{\epsilon}+d_l(k))\sum_t s_{il,t}+q_l(k)\sum_t s_{el,t}\big]$, where $s_{il,t}$ and $s_{el,t}$ are inelastic and elastic packets sent in slot $t$ of the frame.
- **Deficit counter:** $d_l(k+1)=[d_l(k)+\tilde a_{il}(k)-I_{il}(k)]^+$. Here $I_{il}$ is the number of inelastic packets served in the frame and $\tilde a_{il}(k)\sim\mathrm{Binomial}(a_{il}(k),1-p_l)$: one coin with heads-probability $1-p_l$ per arriving inelastic packet. Elastic queue: $q_l(k+1)=[q_l(k)+\tilde a_{el}(k)-I_{el}(k)]^+$.

Guarantees (Lemma 1, Corollaries 1–2, Theorem 1): $(d,q)$ is positive recurrent; $\limsup E[\sum_l d_l+q_l]\le B_4+B_5/\epsilon$; utility is within $B\epsilon$ of the optimum; every link's delivery-ratio requirement is met in the long run. All of this assumes a fixed set of links, i.i.d. arrivals and channels, and a feasible requirement vector.

### Mapping to our model

| JS | Our model |
|---|---|
| frame | one 1-s slot ($T$ = 1 frame per slot) |
| link $l$ with inelastic traffic | declared-RT device $i$ (video or gaming) |
| one inelastic packet per frame ($a_{il}=1$), served or dropped | the flow's slot requirement: rate $r^{\min}_k$ in this slot; "delivered" iff it receives $\ge r^{\min}_k$ |
| required delivery ratio $1-p_l$ | target $q$ (default 0.9), common to all RT flows |
| link with elastic traffic | declared-E device $e$ (queue $Q_e$, in Mbit) |
| elastic part of an RT link | the video top-up $y\in[0,r^{\max}_V-r^{\min}_V]$ above $r^{\min}_V$ (its own virtual queue $Q^{v}_i$) |
| $U_l$ | $w_e\log(1+x)$ for elastic devices; $w_i\log(1+y/r^{\min}_V)=w_i\,[u_V(r^{\min}_V+y)-u_V(r^{\min}_V)]$ for the video top-up |
| $w_l$ (extra reward for inelastic service) | $\omega_i=\kappa\,w_i\,u_k(r^{\min}_k)=\kappa\,w_i$ with $\kappa\in\{0,1\}$ |
| $1/\epsilon$ | $V=20$ (same as `PlainDPP`/`Repay`) |
| interference constraint | single link: $\sum_i x_i\le C_t$ |
| packet sizes | one inelastic "packet" of flow $i$ has size $r^{\min}_k$ Mbit; elastic queues are measured in Mbit, so one elastic "packet" = 1 Mbit |

The class is **used**: declared RT devices get deficit counters, declared E devices get elastic queues. A misdeclaring elastic device is treated as an RT flow of its declared class (usable rate $\min(\text{rate},\text{cap})$ in the simulator).

### State per device

- RT device $i$: deficit $d_i\ge0$ (unit: slots owed). Video only: virtual top-up queue $Q^v_i\ge0$ (Mbit).
- Elastic device $e$: virtual queue $Q_e\ge0$ (Mbit).
- Arrival: all zero. Departure: discard. Class change: discard and restart at zero.

### Per-slot steps (slot $t$, capacity $C$)

1. **Deficit arrivals.** For each RT device $i$ draw $\tilde a_i\sim\mathrm{Bernoulli}(q)$ with the mechanism's own RNG. Option `deterministic=True` uses $\tilde a_i=q$ (fluid version).
2. **Elastic congestion control.** For each elastic $e$ with $d_e=$ `cap[e]`:
   $$\tilde x_e=\begin{cases} d_e & Q_e=0\\ \min\{d_e,\ \max(0,\ V w_e/Q_e-1)\}& Q_e>0\end{cases}$$
   (the maximiser of $V w_e\log(1+x)-Q_e x$ on $[0,d_e]$; $X_{\max}=d_e$). Available elastic service: $\bar s_e=\min(d_e,\ Q_e+\tilde x_e)$.
3. **Video top-up congestion control.** For each video flow $i$:
   $$\tilde y_i=\begin{cases} \Delta & Q^v_i=0\\ \min\{\Delta,\ \max(0,\ V w_i/Q^v_i-r^{\min}_V)\}& Q^v_i>0\end{cases},\qquad \Delta=r^{\max}_V-r^{\min}_V=2.5$$
   (the maximiser of $V w_i\log(1+y/r^{\min}_V)-Q^v_i\,y$). Available top-up: $\bar y_i=\min(\Delta,\ Q^v_i+\tilde y_i)$.
4. **Max-weight scheduling (single-link greedy).** Build the item list:
   - RT item $i$ (indivisible): size $r^{\min}_k$, key $\rho_i=(\kappa w_i V+d_i)/r^{\min}_k$ (weight per Mbit). This uses $d_i$ and the queues *before* this slot's update, as in JS's scheduler (6).
   - Elastic item $e$ (divisible): size $\bar s_e$, key $Q_e$.
   - Video top-up item $i$ (divisible): size $\bar y_i$, key $\min(Q^v_i,\rho_i)$. The min places it no earlier than its parent RT item.

   Sort by key, descending. Ties go in this order: RT items, then elastic items, then top-ups; within a type, earlier `arr` and then smaller id. Walk the list with `left = C`:
   - RT item: if $r^{\min}_k\le$ `left` + 1e-12, admit it ($x_i=r^{\min}_k$, `left -= r_min`); otherwise skip it.
   - Elastic item: $x_e=\min(\bar s_e,\text{left})$, `left -= x_e`.
   - Top-up item: only if its parent was admitted: $x_i \mathrel{+}= \min(\bar y_i,\text{left})$, `left` reduced accordingly.

   Zero-key items are still filled in order, so capacity is not left idle while an admitted item has room (ties in max-weight are broken towards using capacity).
5. **Updates.** With $I_i=1$ if RT flow $i$ got $x_i\ge r^{\min}_k$, and 0 otherwise:
   $$d_i\leftarrow\max(d_i+\tilde a_i-I_i,\,0),\quad Q_e\leftarrow Q_e+\tilde x_e-x_e,\quad Q^v_i\leftarrow Q^v_i+\tilde y_i-(x_i-r^{\min}_V)^+ .$$
   No $[\cdot]^+$ is needed on $Q$ because service never exceeds $Q+\text{arrivals}$.
6. Return $x$.

On a single link, sorting by weight per Mbit is the exact max-weight solution when every item is divisible. It is the standard greedy approximation when RT items are indivisible: a skipped item that does not fit leaves at most $r^{\min}_k$ of slack.

### Parameters and why

- $q=0.9$ (delivery-ratio target, as requested; equivalently $p=0.1$). For sensitivity, also run 0.95.
- $V=1/\epsilon=20$, the same value as `PlainDPP`/`Repay`, so that utility scales are comparable.
- $\kappa=0$ (main variant, `JS`). RT flows are then served **only** as far as their delivery ratio requires, and the rule maximises elastic utility subject to $\ge q$ delivery. This is the defining JS behaviour and is clearly different from strict priority.
- $\kappa=1$ (`JS-w`) adds JS's reward $w_l$ for inelastic service beyond the requirement. With $V=20$ it then behaves close to priority for RT flows.
- `deterministic=False`, `seed=0`.

### Changes from the original and guarantees lost

1. One frame equals one slot, and every RT flow has exactly one "packet" per slot, of size $r^{\min}_k$. JS's arrival process (random $a_{il}$ with $P(a=0)>0$) is replaced by a constant requirement.
2. Variable-rate inelastic service (video above $r^{\min}$) is not in JS. We model it as an elastic sub-flow of the same "link", with its own queue. JS explicitly allows a link to carry both kinds of traffic.
3. The elastic "queue" is a virtual queue of admitted traffic. The real backlog is the exogenous cap $d_e$, which also bounds the injection ($X_{\max}=d_e$) and the service.
4. Elastic and inelastic units (Mbit vs. slots) are linked by our choice of packet sizes. JS counts both in packets.
5. Devices arrive and leave, capacity follows a Markov-modulated process (not i.i.d.), and the tier weights enter via $U$ and $\omega$.
6. The greedy step is not an exact max-weight schedule with indivisible items.

**Guarantees lost:** positive recurrence, the $O(1/\epsilon)$ deficit bound and the $O(\epsilon)$ optimality gap. All are proved for a fixed set of flows under i.i.d. arrivals and channel states with a strictly feasible requirement vector. Our churn and modulated capacity violate these assumptions, so whether each flow reaches the $q$ target is an empirical question. Over a short sojourn the target can be missed even when it is feasible in the long run.

### One-sentence description for the paper

"JS is our single-link, per-slot adaptation of the elastic/inelastic scheduler of Jaramillo and Srikant (2011): utility-maximising congestion control with virtual queues for elastic devices and per-flow deficit counters that enforce a delivery ratio $q=0.9$ for declared real-time flows, combined by a max-weight rule; it is not the original multi-hop, frame-based system."

---

## B1. LendRecoup: credit fairness (Zahedi and Freeman, 2026)

### Source (read: model §3, Definition 5, §5 incl. Algorithm 1 and Example 4, Theorems 5–6 statements)

S. M. Zahedi, R. Freeman, *Credit Fairness: Online Fairness in Shared Resource Pools*, arXiv:2601.17944 (v1 25 Jan 2026, v2 16 Aug 2026). Authors and title checked against the arXiv API record.

```bibtex
@misc{zahedi2026credit,
  author = {Zahedi, Seyed Majid and Freeman, Rupert},
  title  = {Credit Fairness: Online Fairness in Shared Resource Pools},
  year   = {2026},
  note   = {arXiv preprint, v2 August 2026},
  eprint = {2601.17944}, archivePrefix = {arXiv}, primaryClass = {cs.GT}
}
```

### The original mechanism and setting

A fixed set of $n$ agents shares a pool. Agent $i$ contributes an endowment $e_i>0$ per round and the pool is $E=\sum_ie_i$. In each round agent $i$ reports a demand $d'_{i,t}$ and gets utility $\min(d_{i,t},a_{i,t})$ (capped linear), additive across rounds. Credits start at $c_{i,1}=0$. In each round of LendRecoup (Algorithm 1):

1. **No shortage** ($\sum_id'_{i,t}\le E$): $a_t=\mathrm{PSWC}(A=E,w=e,m=d'_t,l=+\infty)$.
2. **Shortage**: $\bar d_{i,t}=\min(d'_{i,t},\max(0,e_i+c_{i,t}))$ (demand capped at the *credit-adjusted endowment*).
   - (2a) If $E\le\sum_i\bar d_{i,t}$: $a_t=\mathrm{PSWC}(A=E,w=e,m=0,l=\bar d_t)$.
   - (2b) Otherwise, "re-allocate history". With $\mathrm{cum}_i=\sum_{t'<t}a_{i,t'}$, set $m=\mathrm{cum}+\bar d_t$, $l=\mathrm{cum}+d'_t$, $\tilde a=\mathrm{PSWC}(A=tE,w=e,m,l)$ and $a_t=\tilde a-\mathrm{cum}$. This gives the remaining capacity to the agents with the lowest endowment-normalised cumulative allocation.
3. Credits: $c_{t+1}=c_t+e-a_t$.

Properties: Pareto efficient (Prop. 2), credit fair (Thm 5: lenders get priority to recoup and debtors' guaranteed minimum is reduced by their debt), online strategy-proof (Thm 6). Theorem 3 shows that no anonymous mechanism is at once SP, PE and credit fair. Unlike Karma, LendRecoup does not guarantee a fixed fraction of the endowment to every agent; a debtor's guarantee shrinks by its debt.

### Adaptation to our setting

- **Endowment.** Each slot's capacity is split by tier weight among the active devices: $e_{i,t}=C_t\,w_i/\sum_{j\in\mathcal A_t}w_j$, so $E_t=C_t$. Variant `unweighted`: $e_{i,t}=C_t/n_t$. The original endowments are fixed and the pool is the sum of contributions. Here the pool is exogenous and is divided according to the operator's tier weights.
- **Demand.** $D_i$ as in Section 0. The rule is class-blind apart from setting the RT demand to $r^{\max}_k$. For elastic devices the demand is verified, so the "report" in the original is replaced by a measurement.
- **State per device:** credit $c_i$, cumulative allocation $\mathrm{cum}_i$ (Mbit since arrival), cumulative endowment $\hat E_i$ (Mbit since arrival). Arrival: all 0. Departure: discard. A departing debtor's debt and a departing lender's claim simply vanish. Class change: reset to 0, since the demand changes meaning.

**Per-slot steps:**

1. Compute $e_{i}$ for the active devices. Update $\hat E_i\leftarrow\hat E_i+e_i$, so that it includes the current slot.
2. If $\sum_iD_i\le C_t$ (no shortage): $\tilde a=\mathrm{PSWC}(A=C_t,w=e,m=D,l=+\infty)$, which gives $\tilde a_i=\max(D_i,xe_i)$. **Return $x_i=\min(\tilde a_i,D_i)=D_i$.** The part above demand has no value in the original, and in our simulator it would be counted as usable for elastic devices.
3. Otherwise compute $\bar d_i=\min(D_i,\max(0,e_i+c_i))$.
   - (a) If $\sum_i\bar d_i\ge C_t$: $\tilde a=\mathrm{PSWC}(A=C_t,w=e,m=0,l=\bar d)$, i.e. $\tilde a_i=\min(\bar d_i,\,x e_i)$.
   - (b) Else: $\tilde a_i=\mathrm{clip}(x\,\hat E_i-\mathrm{cum}_i,\ \bar d_i,\ D_i)$, with $x$ found by bisection so that $\sum_i\tilde a_i=C_t$. This is exactly line 17 of Algorithm 1 with $A=\sum_i\mathrm{cum}_i+C_t$ and $t\,e_i$ replaced by $\hat E_i$; the solution exists because $\sum\bar d<C_t<\sum D$.

   Return $x=\tilde a$, which satisfies $x\le D$ in both sub-branches.
4. Update $c_i\leftarrow c_i+e_i-\tilde a_i$ and $\mathrm{cum}_i\leftarrow\mathrm{cum}_i+\tilde a_i$, using $\tilde a$ (including the unvalued surplus in branch 2), so that the books match the original exactly.

### Parameters and why

- `weighted=True` (endowment $\propto w_g$), because tiers are the operator's statement of entitlement. Report `weighted=False` as a sensitivity check.
- No other parameters. The mechanism has none, which is part of its appeal as a baseline.

### Changes from the original and guarantees lost

Endowments vary with time (with $C_t$ and with the population) instead of being fixed. Agents arrive and leave, and their credits are created at zero and destroyed on departure. History in step 3b is normalised by the cumulative endowment over each device's own sojourn. Surplus above demand is left idle instead of handed out.

- Pareto efficiency per slot is kept: unused capacity remains only when every demand is met.
- (CF1), (CF4) and (CF5) hold slot by slot for the adapted endowments. The proofs are per round given $e_t$; we have not re-proved them for time-varying $e$.
- Online strategy-proofness (Thm 6) is about *demand* reports. Elastic demands are measured in our model, and the strategic variable is the *class*, which only changes $D_i$ to $r^{\max}_k$. The theorem says nothing about class misreporting.
- The interpretation of credits as claims on future resources is weakened by churn: a lender can leave before it recoups.

### Relation to `Credit`

The existing `Credit` baseline is Karma-style. It gives every device its full fair share $f_i$ every slot (no reduction for debtors), then gives unused capacity to borrowers in decreasing credit order. LendRecoup differs in three ways: (i) the guarantee of a debtor drops to $\max(0,e_i+c_i)$; (ii) a lender is guaranteed up to $e_i+c_i>e_i$; (iii) any further surplus is spread by equalising cumulative normalised allocations instead of a credit-ordered queue. Zahedi and Freeman state that Karma violates credit fairness.

### One-sentence description for the paper

"LendRecoup is our adaptation of the credit-fair mechanism of Zahedi and Freeman (2026) to time-varying capacity and churn, with endowments equal to tier-weighted shares of the current capacity; it is class-blind, and it is not the original fixed-pool mechanism."

---

## B2. Perpetual potential rule (Kahana, Segal-Halevi and Hazon, 2026)

### Source (read: §3 model and local balance, §4 the $p$-potential rule and Corollaries 4.5–4.6, §5.1 Case 1 with Lemma 5.1, Example 1, Lemma 5.2; §7 skimmed)

I. Kahana, E. Segal-Halevi, N. Hazon, *Perpetual Fully-Online Approximate Fairness*, arXiv:2605.19844 (v1 19 May 2026, v5 16 Jul 2026). Metadata checked against the arXiv API record.

```bibtex
@misc{kahana2026perpetual,
  author = {Kahana, Ido and Segal-Halevi, Erel and Hazon, Noam},
  title  = {Perpetual Fully-Online Approximate Fairness},
  year   = {2026},
  note   = {arXiv preprint (v1 May 2026, v5 Jul 2026)},
  eprint = {2605.19844}, archivePrefix = {arXiv}
}
```

### The original

The paper gives a general framework. In each round the decision maker sees a feasible action set $A_{t+1}$ and, for every tracked requirement $q$, the post-round deficit $z_q^{t+1}(a)\ge0$ that each action would produce. The **$p$-potential rule** picks
$$a_{t+1}\in\arg\min_{a\in A_{t+1}}\ \sum_{q} f\big(z^{t+1}_q(a)\big),\qquad f(u)=(u^2+4p^2\sigma^2)^p ,$$
with $p=\ln(2m)$ for $m$ tracked requirements. Under the "local balance" conditions (reference actions whose shifts average to $\le0$ with squared size $\le\sigma^2$), all deficits stay below $c_t=O(\sigma\ln m+\sigma\sqrt{t\ln m/n})$ at **every** $t$, without knowledge of the horizon (Cor. 4.6). In Case 1 (online items, $n$ agents) the tracked requirement of agent $i$ is the normalised proportionality deficit
$$z_i^t=\frac{[\tfrac1n v_i(G^t)-v_i(P_i^t)]^+}{U_i^t},$$
where $U_i^t$ is the largest value to $i$ of an item it did not receive, and $\sigma^2=1$ (Lemma 5.2). The deficit inside the bracket is full-history and may be negative; only the potential clips it.

### Why a direct rate-level instantiation is degenerate, and the instantiation we use

Suppose each slot's capacity is a divisible "item" with value $v_i(x)=\min(x,D_i)$. Then the proportional-share action ($x_i=\min(C_t,D_i)/n_t$) is feasible every slot and gives zero shift to every deficit. The rule then only enforces $x_i\ge \mathrm{prop}_i+(\text{past surplus})$, and the rest of its behaviour comes from tie-breaking. It becomes another fair-share-plus-ledger rule, close to `Credit`.

The instantiation becomes non-trivial, and distinct from all other baselines, once we use the **usable-volume valuation**, which says that RT service below $r^{\min}_k$ is worthless:
$$v_i(x)=\begin{cases}\min(x,D_i) & i\text{ declares }E\\ \min(x,r^{\max}_k)\cdot\mathbf 1\{x\ge r^{\min}_k\} & i\text{ declares RT class }k.\end{cases}$$
The capacity is then partly indivisible, as in the paper's item setting, and the rule decides each slot which RT flows to serve by comparing whole deficit vectors. The result is a rotation of RT service that keeps every device's normalised proportionality deficit small. The declared class is used through $v_i$, and only to measure usable volume. Tiers enter only in the optional weighted variant.

### State per device

Signed deficit $\delta_i$ (Mbit) and scale $U_i\ge0$ (Mbit). Arrival: both 0. Departure: discard. Class change: reset both, since the valuation changes.

### Per-slot steps (active set $\mathcal A$, $n=|\mathcal A|$, capacity $C$)

1. **Proportional share.** $\mathrm{prop}_i=v_i(C)/n$ (unweighted, as in the paper). Variant `weighted`: $\mathrm{prop}_i=v_i(C)\,w_i/\sum_{j\in\mathcal A}w_j$.
2. **Scale.** $U_i\leftarrow\max(U_i,\,v_i(C))$. This is our action-independent version of "largest missed item". It bounds every one-slot shift: $|\mathrm{prop}_i-v_i(x_i)|\le U_i$, which is the role $\sigma^2=1$ plays in the paper.
3. **Post-slot deficit as a function of the rate:** $\delta_i^+(x)=\delta_i+\mathrm{prop}_i-v_i(x)$, $z_i(x)=[\delta_i^+(x)]^+/U_i$, with $z_i\equiv0$ when $U_i=0$.
4. **Potential.** $p=\max(1,\ln(2n))$. Use the normalised $\tilde f(u)=(1+u^2/(4p^2))^p$, which has the same argmin as $f$ with $\sigma=1$ and avoids overflow. Its derivative is $\tilde f'(u)=\frac{u}{2p}\big(1+\frac{u^2}{4p^2}\big)^{p-1}$. This is strictly increasing on $u\ge0$ with $\tilde f'(0)=0$. Write $h(y)$ for its inverse on $y\ge0$, computed by bisection on $u\in[0,u_{hi}]$, doubling $u_{hi}$ until $\tilde f'(u_{hi})\ge y$; for $y\le0$ set $h(y)=0$.
5. **Minimise $\Phi(x)=\sum_i\tilde f(z_i(x_i))$** subject to $\sum_ix_i\le C$, $x_i\in[0,D_i]$ for E, and $x_i\in\{0\}\cup[r^{\min}_k,r^{\max}_k]$ for RT. Use a Lagrangian method with multiplier $\mu\ge0$. For a fixed $\mu$:
   - elastic $i$ (and an admitted RT $i$ with $lo_i=r^{\min}_k$; $lo_i=0$ for E, $hi_i=D_i$): $x_i(\mu)=\mathrm{clip}\big(\delta_i+\mathrm{prop}_i-U_i\,h(\mu U_i),\ lo_i,\ hi_i\big)$. This is the point where the marginal reduction $\tilde f'(z)/U_i$ equals $\mu$. For an RT flow, $v_i(x)=x$ on $[r^{\min},r^{\max}]$, so the same formula applies.
   - RT admission at $\mu$: admit $i$ iff $L_i(\mu):=\tilde f(z_i(0))-\tilde f(z_i(x_i(\mu)))-\mu\,x_i(\mu)>0$.

   Procedure:
   - (a) $\mu=0^+$ (deficit-clearing allocation). Compute $x_i(0^+)=\mathrm{clip}(\delta_i+\mathrm{prop}_i,lo_i,hi_i)$ with admission $L_i(0)>0$, i.e. admit an RT flow iff not serving it would leave a positive deficit. If $S(0^+)=\sum x_i(0^+)\le C$, keep this allocation and go to (c).
   - (b) Otherwise bisect on $\mu$ (bracket by doubling from $\mu=1$) until $S(\mu_{lo})>C\ge S(\mu_{hi})$ and $\mu_{hi}-\mu_{lo}\le10^{-10}\max(1,\mu_{hi})$. Take the allocation at $\mu_{hi}$.
   - (c) **Leftover** $R=C-\sum_ix_i$. First go through RT flows not admitted, in decreasing order of $L_i(\mu_{lo})$ (or $L_i(0)$ in case (a)), and admit at rate $r^{\min}_k$ any flow with $r^{\min}_k\le R$. Then give the remainder to admitted RT and elastic devices with room ($hi_i-x_i$) by unweighted water-filling (`_waterfill`). Raising a rate never increases $\Phi$, so step (c) only moves within (a) or near (b) the argmin set; it is the paper's "break ties arbitrarily" made work-conserving.
   - (d) Optional local search (`polish=True`): for each RT flow, evaluate $\Phi$ after toggling its admission (dropping it and refilling capacity by (c), or adding it at $r^{\min}$ by taking capacity from the elastic device with the smallest marginal $\tilde f'(z)/U$). Accept improving toggles and stop after one pass. This is off by default and is for checking how far the heuristic is from the optimum.
6. **Update:** $\delta_i\leftarrow\delta_i+\mathrm{prop}_i-v_i(x_i)$, with **no clipping**. This is the full-history signed deficit of the paper; a device that was over-served carries a surplus.

### Parameters and why

- $p=\ln(2n_t)$ recomputed each slot, the paper's choice for its $c_t$-fairness corollary (Cor. 4.6).
- `weighted=False` by default, because the paper treats unweighted proportionality. `weighted=True` is our extension for tier comparisons.
- Full history (the paper's main model). The paper also analyses discounted memory (§7: deficits multiplied by $\gamma(t)$ before each update). An optional variant with $\gamma=0.99$ per slot (memory of about 100 s) is reasonable because sojourns average 240 s; it is not needed for the main runs.

### Changes from the original and guarantees lost

1. The paper's applications are indivisible items or public decisions. Our action set is a mixed divisible/indivisible rate vector, and the tracked requirements are our own instantiation of its framework, modelled on Case 1.
2. $U_i$ is action-independent: the largest single-slot value $v_i(C_s)$ instead of the largest *missed* item.
3. The population changes. Each device's deficit exists only during its sojourn, and $n$ (hence $\mathrm{prop}_i$ and $p$) varies by slot. The paper's $m$ and $n$ are fixed.
4. The per-slot argmin is computed by a Lagrangian heuristic. It is exact for the elastic part given the admitted RT set, but the RT admission problem is combinatorial, so the selection is heuristic.
5. **Guarantees lost.** The anytime bound $c_t=O(\sigma\ln m+\sigma\sqrt{t\ln m/n})$ needs (i) the exact argmin and (ii) the local balance conditions with fixed $n$ and $m$. Local balance does hold in each slot: the $n$ reference actions "give the whole capacity to device $k$" give $\sum_k\Delta_i(k)=n\,\mathrm{prop}_i-v_i(C)=0$ and $\sum_k\Delta_i(k)^2\le1$ after normalisation. But (i) fails because of the heuristic, and with churn the bound would at best hold per device over its sojourn with a varying $n$, which we have not proved. The rule should be treated as a heuristic inspired by the paper.

### One-sentence description for the paper

"Potential is our instantiation of the fully-online $p$-potential rule of Kahana, Segal-Halevi and Hazon (2026) for a shared link: each slot it chooses rates that minimise a soft-max potential of the devices' normalised proportionality deficits in usable volume, where real-time service below $r^{\min}_k$ counts as zero; it is not the original item-allocation algorithm, and its anytime bound is not claimed here."

---

## B3. Dynamic max-min fairness (Fikioris, Banerjee and Tardos, EC 2025)

### Source (read: §2.1–2.2 incl. Algorithm 1, Remark 3.3 on dynamic populations, §4.2 Algorithm 2 for reusable resources)

G. Fikioris, S. Banerjee, É. Tardos, *Beyond Worst-Case Online Allocation via Dynamic Max-min Fairness*, Proceedings of the 26th ACM Conference on Economics and Computation (EC '25), p. 92, 2025. arXiv:2310.08881v4. DOI and venue confirmed via Crossref.

```bibtex
@inproceedings{fikioris2025dmmf,
  author    = {Fikioris, Giannis and Banerjee, Siddhartha and Tardos, {\'E}va},
  title     = {Beyond Worst-Case Online Allocation via Dynamic Max-min Fairness},
  booktitle = {Proceedings of the 26th ACM Conference on Economics and Computation (EC '25)},
  year      = {2025}, pages = {92},
  doi       = {10.1145/3736252.3742501},
  eprint    = {2310.08881}, archivePrefix = {arXiv}
}
```

### The original

In each round one indivisible item is offered to $n$ agents with exogenous fair shares $\alpha_i$ ($\sum_i\alpha_i=1$). Among the agents who request it, the item goes to one with the smallest $(A_i[t-1]+1)/\alpha_i$, where $A_i$ is the number of items won so far (Algorithm 1). Agents only say whether they want the item. The mechanism is work-conserving and needs no knowledge of distributions or horizon. Main results: under i.i.d. or Markov values, each agent has a simple ($\beta$-aggressive) request strategy that guarantees a large fraction of its *ideal utility* whatever the others do. Ideal utility is the best it could get using an $\alpha_i$ fraction of rounds without competition. The fraction is at least about 1/2 and approaches 1 in structured cases. Remark 3.3: when agents enter or leave, the mechanism can be restarted at any round at an additive loss of $O(1)$ per restart. Algorithm 2 (reusable resources, multi-round demands) uses the horizon $T$ and is not needed here.

### Adaptation

Split each slot's capacity into quanta of size $\delta$ and run Algorithm 1 quantum by quantum inside the slot. A device "requests" while its rate is below its demand $D_i$, and its counter grows by $\delta$ after each win. Each quantum then goes to the requesting device with the smallest normalised cumulative allocation. As $\delta\to0$ this is water-filling on normalised cumulative volume, which is the rule we implement. For churn we normalise each device's cumulative allocation by its **cumulative entitlement** over its own sojourn, $\hat E_i=\sum_{s}\alpha_{i,s}C_s$, rather than by a constant $\alpha_i$. In the original all agents are present in all rounds, so dividing by $\alpha_i$ and dividing by $t\alpha_i$ order the agents identically. With churn only the second is meaningful.

- **Fair share:** $\alpha_{i,t}=w_i/\sum_{j\in\mathcal A_t}w_j$ (tier-weighted, default) or $1/n_t$ (`weighted=False`).
- **Class:** class-blind apart from the demand $D_i$ (Section 0).
- **State per device:** $A_i$ (Mbit received since arrival) and $\hat E_i$ (Mbit entitled since arrival). Arrival: both 0. Departure: discard. Class change: reset.

**Per-slot steps:**
1. $\hat E_i\leftarrow\hat E_i+\alpha_{i,t}C_t$.
2. If $\sum_iD_i\le C_t$: $x=D$.
3. Else find $\theta$ by bisection with $\sum_i\mathrm{clip}(\theta\hat E_i-A_i,\,0,\,D_i)=C_t$, and set $x_i=\mathrm{clip}(\theta\hat E_i-A_i,0,D_i)$. After the slot, every device that is not at its demand has the same ratio $(A_i+x_i)/\hat E_i=\theta$, and devices above $\theta$ get nothing. This is the continuous limit of "smallest $(A_i+1)/\alpha_i$ wins".
4. $A_i\leftarrow A_i+x_i$.

An exact quantised implementation (`quantum=0.01`, item by item, ties broken by smaller id) should give the same allocation up to $\delta$ per device. It serves as a test oracle.

### Parameters and why

- `weighted=True` (fair share = tier share), so that DMMF can be compared with tier-aware rules. `weighted=False` matches the paper's equal-share examples.
- **Restart variant (`restart=True`)**, which follows Remark 3.3 literally: reset all $A_i$ and $\hat E_i$ whenever the active set changes. In the hotspot trace the active set changes every few seconds, so this variant is nearly memoryless and close to FQ. Report it only as a sensitivity check. The main variant is the per-sojourn normalisation above.

### Changes from the original and guarantees lost

The good is divisible (continuous limit of quanta) and its size $C_t$ varies. The population changes, and normalisation by cumulative entitlement replaces a fixed $\alpha_i$ (the restart variant is the paper's own remedy). Agents do not choose when to request, because elastic demand is measured. The paper's guarantees are about agents' *request strategies* under i.i.d. or Markov values, expressed as fractions of ideal utility. In our model a device's only strategic choice is its declared class, and its value is volume, so none of the paper's theorems transfers. What remains is the mechanism's defining property: it equalises cumulative normalised allocation. A device that was idle or newly arrived catches up first, and a device that has been over-served yields.

### Relation to B1 and the others

The step-3 formula equals LendRecoup's branch (b) with all lower bounds at zero. DMMF has no per-slot guarantee and no debt cap. Zahedi and Freeman also note that DMMF is Karma with $\alpha=0$. DMMF therefore separates the effect of *history-based catch-up alone* from LendRecoup (catch-up plus credit-adjusted guarantees) and from FQ (no memory).

### One-sentence description for the paper

"DMMF is our divisible-rate adaptation of the dynamic max-min fair mechanism studied by Fikioris, Banerjee and Tardos (2025): each slot it water-fills capacity so as to equalise the devices' cumulative received volume normalised by their cumulative tier-weighted entitlement since arrival; it is class-blind and is not the original single-item mechanism."

---

## Candidates considered and dropped

- **SPEC, Lin, Onyeze, Fikioris, Banerjee, Tardos (arXiv:2610.25067, Oct 2026).** Read: abstract, introduction and the structure of Algorithms 1–3. Its model is a single server that processes at most one job per period. Agents have private job values, and unserved jobs expire at random. The mechanism compensates pairwise externalities, estimated by *coupled simulations of the agents' job processes*. Our setting has a divisible link shared by many devices in each slot, and there is no stochastic job model per device for the mechanism to simulate. An adaptation would have to replace the externality estimator, which is the core of the mechanism. Not specified.
- **Karma economies, Elokda et al. (2024–2026).** The allocation outcome depends on equilibrium *bidding* of karma by agents with urgency types. A baseline would need a modelled bidding policy, and the result would measure that model more than the mechanism. A Karma-style credit rule already exists (`Credit`). Not specified; the algorithm sections were not re-read for this note.
- **Regularised online allocation, Balseiro, Lu, Mirrokni (MSOM 2025).** This is dual mirror descent on a horizon-long resource budget with a fairness regulariser. With per-slot capacity, a dual price updated by gradient steps is structurally the same family as `PlainDPP`, so it would not be a genuinely different baseline. Not specified, and its algorithm section was not read in this pass, so no fidelity claim is made.
- **Averbakh et al., FORA-IU (arXiv:2605.03436, 2026).** Read: abstract and section structure. It allocates indivisible units from a fixed budget to arriving demands, and its optimal policy needs the arrival distributions (a forward dynamic program). The model does not fit a renewable per-slot capacity. Dropped.
- **George and Joseph, adaptive bandwidth sharing for real-time video (arXiv:2506.09197, 2025).** Read: abstract and introduction. It shares bandwidth between *operators* at a semi-static time scale and has no elastic traffic. Dropped.
- **LLM-serving fair schedulers (VTC, OSDI 2024; DLPM, arXiv:2501.14312; Equinox, arXiv:2508.16646).** VTC's "counter lift" for clients that join is directly relevant to churn, but VTC dates from 2024 and the 2025 follow-ups were not read in full. They are noted as possible future baselines, not specified.
- **Kahana et al. with rate-valued (class-blind) valuations.** As explained in B2, this instantiation degenerates to a fair-share-plus-ledger rule. Only the usable-volume instantiation is specified.

---

## Unit tests (proposed)

Tests common to every baseline (parametrise over all five; random views with 1–60 devices, mixed tiers and classes, $C\in[0.1,200]$, 200 random slots with arrivals and departures):

- **T0-cap:** `rate.sum() <= C + 1e-9` and `rate >= -1e-12` in every slot.
- **T0-dem:** `rate <= D + 1e-9`, with $D$ as in Section 0. For declared E this is `cap`; it is the key guard against inflated utility.
- **T0-churn:** after a device leaves, its id is absent from every state dict. A device that changes its declared class has its per-device state reset to the arrival default.

### A1 FQ
1. **Hand example (unweighted).** $C=10$; devices E($d$=8), E($d$=8), V, G → $x=(3.4,3.4,3.0,0.2)$.
2. **Hand example (weighted).** Same devices with tiers (F, P, F, Y), so $\phi=(1,2,1,1.5)$ → $x=(2.45,4.9,2.45,0.2)$: gaming is capped at 0.2, and the remaining 9.8 is shared at level $\theta=9.8/4=2.45$.
3. **Equivalence.** With all devices in one tier, `FQ` equals `PF` to 1e-9 (documents the overlap noted in A1). With $\sum D\le C$ every device gets $D_i$.

### A2 JS (`deterministic=True`, $q=0.9$, $V=20$, $\kappa=0$)
1. **Hand example.** $C=1$, one gaming flow and one elastic device ($d=5$), both tier F. Expected rates (G, E) for slots 1–5: (0.2, 0.8), (0, 1), (0, 1), (0.2, 0.8), (0, 1). Expected states after slot 5: $d_G=2.6$, $Q_E\approx8.9164$. Intermediate values: $Q_E=4.2$ after slot 1; $\tilde x_E=3.7619$ in slot 2; $d_G=1.8$ before slot 4, where the RT key $9.0$ exceeds $Q_E=7.8347$.
2. **Delivery ratio.** With ample capacity ($C=100$) every RT flow is served every slot, and all $d_i$ stay 0. On a long stationary run with feasible load (e.g. 5 gaming and 30 elastic devices with $d$=5 at $C=20$, no churn, 5000 slots), each RT flow's served fraction is $\ge q-0.01$, and $\max_i d_i$ stays bounded (no linear trend over the second half).
3. **Invariants.** $Q_e,Q^v_i,d_i\ge0$. An RT flow's rate is 0 or $\ge r^{\min}_k$. Video top-up is positive only when the flow is admitted, and never exceeds $r^{\max}_V$.

### B1 LendRecoup (`weighted=False`, constant $C=3$, three elastic devices)
1. **Paper's Example 4.** Demands $(2,2,0)$, $(2,2,0)$, $(2,2,6)$ in slots 1–3. Expected allocations $(1.5,1.5,0)$, $(1.5,1.5,0)$, $(0,0,3)$; credits after each slot $(-0.5,-0.5,1)$, $(-1,-1,2)$, $(0,0,0)$. Slots 1–2 exercise branch 3b and slot 3 exercises branch 3a.
2. **No shortage.** If $\sum D\le C$, then $x=D$, and credits move by $e_i-\tilde a_i$ with $\tilde a$ the uncapped PSWC output.
3. **Credit-fairness checks per slot** (adapted endowments): (CF4) $x_i\ge\min(D_i,e_i+\min(0,c_i))-10^{-9}$. (CF5) if some $x_j>\max(0,e_j+c_j)+10^{-9}$, then every $i$ has $x_i\ge D_i-10^{-9}$ or $x_i\ge e_i+c_i-10^{-9}$. Under shortage, the sum of credit changes is zero.

### B2 Potential (unweighted)
1. **Equalisation.** $C=1$; two elastic devices with $d=1$, $U=1$, signed deficits $\delta=(0.4,0)$. Prop is 0.5 each, and the expected rates are $(0.7,0.3)$, leaving both post-deficits at 0.2. By symmetry of $\tilde f$ this holds for any $p$.
2. **RT rotation.** $C=0.3$; gaming G and elastic E ($d=1$), starting from zero. Slot 1: serve G → $(0.2,0.1)$, because the alternative leaves $z_G=0.5>z_E=1/6$. Slot 2, with $\delta_G=-0.1$ and $\delta_E=0.05$: block G → $(0,0.3)$, because both post-deficits are then 0, while serving G would leave $z_E=1/3$.
3. **Leftover and surplus.** $C=1$. Slot 1: A ($d=1$) and B ($d=0$) → A gets 1, so $\delta_A=-0.5$. Slot 2: both $d=1$ → deficit-clearing step gives $(0,0.5)$, and the leftover 0.5 is water-filled → $(0.25,0.75)$. Also check that $\Phi$ at the returned allocation is no larger than at 100 random feasible allocations, with RT rates restricted to $\{0\}\cup[r^{\min},r^{\max}]$.

### B3 DMMF (`weighted=False`, constant $C=3$)
1. **Same Example as B1.** Expected allocations $(1.5,1.5,0)$, $(1.5,1.5,0)$, $(0,0,3)$. In this example DMMF and LendRecoup agree.
2. **Catch-up, and where it differs from LendRecoup.** (i) Two devices, $C=2$, demands $(2,0)$ for 5 slots, then $(2,2)$ in slot 6: DMMF gives $(2,0)$ in slots 1–5 and $(0,2)$ in slot 6. LendRecoup gives the same here, because its credits equal entitlement minus allocation. (ii) Inject state directly: two devices, unweighted, $C=2$, $D=(5,5)$, entitlement before the slot $\hat E=(9,9)$, cumulative allocations $(6,8)$, so LendRecoup credits are $(3,1)$. DMMF returns $(2,0)$ ($\theta=0.8$). LendRecoup is in branch 3a ($\bar d=(4,2)$, sum $\ge C$) and returns $(1,1)$. This is the case where history-based catch-up and credit-capped proportional sharing differ.
3. **Quantised oracle.** For random small instances, the water-fill allocation matches item-by-item Algorithm 1 with quanta $\delta=0.001$ (ties broken by id) within $n\delta$ in $\ell_1$.

---

## Summary table

| Name | Source | Uses declared class? | Tier weights | Memory | Main parameters |
|---|---|---|---|---|---|
| FQ / FQ-w | RFC 8290; Høiland-Jørgensen et al. 2018 | demand only | no / $\phi=w$ | none | `weighted` |
| JS / JS-w | Jaramillo & Srikant 2011 | yes (deficits for RT) | in $U$; $\omega=\kappa w$ | deficits, virtual queues | $q=0.9$, $V=20$, $\kappa\in\{0,1\}$ |
| LendRecoup | Zahedi & Freeman 2026 | demand only | endowments $\propto w$ | credits, cumulative | `weighted` |
| Potential | Kahana, Segal-Halevi & Hazon 2026 | valuation (usable volume) | optional | signed deficits | $p=\ln 2n$, `weighted`, `polish` |
| DMMF | Fikioris, Banerjee & Tardos 2025 | demand only | fair share $\propto w$ | cumulative | `weighted`, `restart` |
