# Exact two-sided certificates for maximal quantum Bell violations: an agentic laboratory study of the doubly tilted CHSH family

Team Ninja Turtles, Hack-Nation 2026, Challenge 3 (Agentic Scientific Discovery)

## Abstract

We study the doubly tilted CHSH family with correlator coefficients a = b = [p, 0] and c = [[1, 1], [1, -1]]. An automated laboratory computed lower bounds on the maximal quantum value Q(p) from explicit strategies and upper bounds from the NPA hierarchy. A verifier certified both bounds in exact rational arithmetic. Q is certified to within 1e-6 at p = 0.3 [C-bell-R4], at p = 1/2 [C-bell-R1] and at p = 131/200 [C-bell-R6]. At p = 0.95 and p = 0.99 the explicit strategies violate the classical bound L = 2+2p, but the two-sided gap is not closed [C-bell-R2, C-bell-R2-RT2]. At p = 131/200, NPA level 1+AB is strictly not tight, while level 2 is [C-kombi1]. No closed formula for Q(p) was established. The preregistered anchor hypothesis H6a failed [C-H6a], and no novelty is claimed [C-H6b].

## 1 Introduction

**Question.** How does the maximal quantum value Q(p) behave for the doubly tilted CHSH family with a = b = [p, 0]? Do qubits suffice? Where does the NPA level 1+AB cease to be tight? [C-bell-R1, C-bell-R5]

**Contribution.** The study reports individually certified values and gap bounds. It also lists claims that could not be established.

**Results.**
- Two-sided certificates for Q at three parameter values: p = 0.3 [C-bell-R4], p = 1/2 [C-bell-R1] and p = 131/200 [C-bell-R6].
- A rigorous quantum violation of L at p = 0.95 and p = 0.99, without a closed two-sided gap [C-bell-R2, C-bell-R2-RT2].
- Strict non-tightness of NPA level 1+AB at p = 131/200 [C-kombi1].
- Verifier lower bounds on the gap between the 1+AB optimum and the best certified strategy at six parameter values [C-kombi2].
- A list of negative results, red-team outcomes and unmet preregistered hypotheses, given in the section on negative results [C-neg1, C-H6a].

## 2 Setting and certificates

The Bell inequality is given in correlator form with coefficients a = [p, 0], b = [p, 0], c = [[1, 1], [1, -1]] and constant 0 [C-bell-R1]. The classical bound is L = 2+2p, and at p = 1/2 it is L = 3 [C-bell-R2].

Lower bounds on Q come from explicit quantum strategies of dimension d per side, found by see-saw optimisation. The verifier evaluates their Bell value exactly in rational arithmetic [C-bell-R1-RT1]. Upper bounds come from NPA levels 1+AB, 2 and 2+AAB, certified by rational dual certificates [C-bell-R1, C-bell-R2-RT1]. Q counts as proved when the gap between lower and upper bound is below 1e-6 [C-bell-R1]. Rational feasible moment matrices give lower bounds on the NPA optimum, and the verifier compares these with the best exact strategy [C-bell-R5].

## 3 Method: the agentic laboratory

The laboratory ran 8 rounds, with 7 checked statements and 1 negative result, at a cost of 4.31 USD [C-methode]. Each round was preregistered before the experiment [C-methode]. Researcher agents proposed claims, and a code verifier certified or rejected them. A red team attacked each claim with counter-checks. Agent interpretations are labelled as unverified hypotheses and are not used here [C-bell-R1-I].

Before the run, the verifier passed a self-test with 22/22 cases correct (10 true, 12 false statements or rule violations) [C-selbsttest]. The anchors were CHSH (classical bound 2, quantum value 2.828427125), the chain with 4 settings (classical bound 6), I3322 (classical bound 0, upper bound 0.2509 at NPA level 2+AAB) and tilted CHSH with formula sqrt(8+2*p**2) [C-selbsttest].

## 4 Results

**Proposition A (computed_rigorous).** For p = 1/2, Q = 3.13693731 up to 1e-6 [C-bell-R1]. The verifier certified 3.13693731130907 ≤ Q ≤ 3.13693732592937 (gap 1.46e-08; strategy d=2, NPA 1+AB) [C-bell-R1, C-bell-R3]. The level 2+AAB upper bound is 3.13693731768845 [C-bell-R3-RT2]. An independent see-saw strategy gave the exact rational Bell value 3.13693731130907 with d=2 [C-bell-R1-RT1].

**Proposition B (computed_rigorous).** For p = 0.3, Q = 2.93828832 up to 1e-6, with 2.93828833175884 ≤ Q ≤ 2.938288368081 (gap 3.63e-08; strategy d=2, NPA 1+AB) [C-bell-R4]. An independent d=2 strategy gave the exact value 2.93828833175884 [C-bell-R4-RT2].

**Proposition C (computed_rigorous).** For p = 131/200, Q = 3.35825951388 up to 1e-6, with 3.35825951388355 ≤ Q ≤ 3.35825955532047 (gap 4.14e-08; strategy d=2, NPA 2) [C-bell-R6]. An independent d=2 strategy gave the exact value 3.35825951388355 [C-bell-R6-RT2].

**Proposition D (computed_rigorous).** The classical bound is exceeded at two parameter values.
- At p = 0.99, the verifier's explicit strategy has exact value 3.98000132884628, and L = 199/50 [C-bell-R2]. The level 2+AAB upper bound is 3.98000623486376 [C-bell-R2-RT1].
- At p = 0.95, L = 3.9 [C-bell-R2-RT2]. Also 3.90016389936512 ≤ Q ≤ 3.90019981472908 (gap 3.59e-05) [C-bell-R2-RT2]. The gap is too large for certification of Q, but the lower bound exceeds L [C-bell-R2-RT2].
- At p = 1, L = 4 and the verifier's quantum strategy attains exactly 4, so no violation was found there [C-bell-R1-RT2].

**Proposition E (computed_rigorous).** At p = 131/200, Q ≤ 3.35825955532047 (NPA level 2, dual certificate), while the optimum of NPA level 1+AB is ≥ 3.35826280973 (rational feasible moment matrix) [C-kombi1]. Level 1+AB is therefore strictly not tight there: its optimum exceeds Q by at least 3.25e-06 [C-kombi1].

**Proposition F (computed_rigorous).** Lower bounds on (NPA 1+AB optimum) minus (best exactly certified strategy) are as follows [C-kombi2]:

| p | lower bound on gap | source |
|---|---|---|
| 0.5 | -1.726e-08 | [C-kombi2] |
| 0.62 | -2.336e-08 | [C-kombi2] |
| 0.652 | 1.843e-07 | [C-kombi2] |
| 0.6532 | 1.025e-06 | [C-kombi2] |
| 0.6533 | 1.120e-06 | [C-kombi2] |
| 0.655 | 3.296e-06 | [C-kombi2] |

Up to p = 0.62 the bound is below 1e-7 in magnitude, which is the accuracy of the SDP solvers [C-kombi2]. From p = 0.652 on it is positive and grows monotonically over the points examined [C-kombi2]. A threshold defined by a fixed tolerance such as 1e-6 therefore depends on that tolerance [C-kombi2]. At p = 0.62, the strategy value 3.30352972153 (d≤3) and the 1+AB value ≥ 3.30352969818 agree to within solver accuracy [C-bell-R5-RT1]. At p = 0.72, NPA level 2 reaches ≥ 3.46649094809 against a best strategy of 3.46649100491 (d≤2) [C-bell-R5-RT2].

**Summary of certified values.**

| p | Lower bound (strategy) | Upper bound (NPA) | Gap | Status | Source |
|---|---|---|---|---|---|
| 0.3 | 2.93828833175884 (d=2) | 2.938288368081 (1+AB) | 3.63e-08 | proved | [C-bell-R4] |
| 1/2 | 3.13693731130907 (d=2) | 3.13693732592937 (1+AB) | 1.46e-08 | proved | [C-bell-R1] |
| 131/200 | 3.35825951388355 (d=2) | 3.35825955532047 (2) | 4.14e-08 | proved | [C-bell-R6] |
| 0.95 | 3.90016389936512 (d=2) | 3.90019981472908 (2+AAB) | 3.59e-05 | not certified | [C-bell-R2-RT2] |
| 0.99 | 3.98000132884628 | 3.98000623486376 (2+AAB) | not stated | not certified | [C-bell-R2, C-bell-R2-RT1] |

## 5 Negative results, preregistration and red team

**Negative result.** The scan for the transition at which NPA 1+AB ceases to be tight, over the points p = 0.6, 0.63, 0.65, 0.655, 0.66, 0.7, 0.8, 0.9 and 0.99, produced no claim that passed verification [C-neg1].

**Preregistration.** H6a (at least 2 of 3 anchor questions confirmed two-sided) was not met: the integrator chose 0 of the 3 anchor questions, and 0 confirmed statements concern anchor questions [C-H6a]. H6b (at least one certified statement about an inequality outside the named families) was met, with 6 confirmed statements concerning the doubly tilted CHSH family or other unnamed inequalities [C-H6b]. Novelty relative to the literature is not claimed [C-H6b].

**Red team.** Red-team checks targeting the confirmed values failed in the sense that the attacks did not succeed.
- No strategy exceeded the certified values at p = 1/2, p = 0.3 and p = 131/200 [C-bell-R1-RT1, C-bell-R4-RT2, C-bell-R6, C-bell-R6-RT2].
- The upper bounds were not undercut by any strategy [C-bell-R3-RT2, C-bell-R2-RT1].
- No violation of L was found at p = 1 [C-bell-R1-RT2].
- NPA 1+AB was not found loose at p = 1/2 or p = 0.62, and NPA level 2 was not found loose at p = 131/200 or p = 0.72 [C-bell-R4-RT1, C-bell-R5-RT1, C-bell-R6, C-bell-R6-RT1, C-bell-R5-RT2].

One claim is contested [C-bell-R8]. At p = 0.6533, the 1+AB optimum lies at least 5e-07 above the best strategy found by the verifier in dimension up to 4 [C-bell-R8]. Here the verifier reports 3.35554254508 against 3.35554142523, a gap ≥ 1.120e-06 [C-bell-R8]. This does not show that Q itself lies below the 1+AB value [C-bell-R8]. A red-team check at p = 0.6532 passed (statement contested), with a gap ≥ 1.025e-06 [C-bell-R8-RT1]. A check at p = 0.652 did not show a gap of 1e-6, with a gap ≥ 1.843e-07 [C-bell-R8-RT2]. The agent's unverified interval for the transition is not used here.

## 6 Limitations and open questions

- **Not shown:** a closed formula for Q(p). The fit attempts addressed this question [C-bell-R3, C-bell-R4], but no certified formula resulted.
- **Not shown:** that Q > L for all p < 1, or that Q = L at p = 1. The claims certify a strategy value of 4 at p = 1 and violations only at the tested points [C-bell-R1-RT2, C-bell-R2].
- **Not shown:** that qubits suffice in general. Certified strategies at the tested points have d=2 or d≤3, and the lower bounds there match the upper bounds only to the stated gaps [C-bell-R5-RT1, C-bell-R6].
- A sharp transition value for NPA 1+AB is not established. The verifier bounds are tolerance-dependent [C-kombi2], and the contested claim [C-bell-R8] is not resolved.
- Q is not certified at p = 0.95 and p = 0.99 [C-bell-R2-RT2, C-bell-R2-RT1].
- No novelty is claimed beyond what the claims support [C-H6b].

**Related work.** The NPA hierarchy yields exact bounds via an infinite series of semidefinite programs [C-lit6]. In the simplest Bell scenario, the correlations at levels 1+AB and 2 coincide under a plausible criterion [C-lit13]. Analytic criteria for the boundary of quantum correlations are hard to establish even there [C-lit14]. An iterative algorithm computes the quantum maximum of two-outcome Bell inequalities in a given Hilbert space dimension [C-lit10]. Operations on CHSH-type inequalities that preserve the Tsirelson bound but change the classical bound have been studied [C-lit5]. For I3322, finite-dimensional systems are conjectured not to attain the true quantum maximum [C-lit9]. Proposition E shows that, for a functional with marginal terms in the simplest scenario, the optima of NPA levels 1+AB and 2 differ [C-kombi1]. The coincidence of levels 1+AB and 2 reported in [C-lit13] is stated for correlations under a plausible criterion; whether its scope covers functionals with marginal terms was not checked beyond the abstract, so we do not claim a contradiction. Beyond this, we make no claim about how these results relate to the present family.

---
*Verification log (automatic):* 34 claim IDs cited; unsupported statements per writing round: 30 → 2; 0 sentences removed; remaining violations: 0. Claim texts and evidence: `paper_belege.json`.
