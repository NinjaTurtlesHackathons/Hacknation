---
title: "How Many Householders Does State Tracking Need? An Exact Law for One-Layer Linear RNNs That Circuit Complexity Does Not Predict"
author: "Verifier-Gated Discovery Lab (Hack-Nation team) (Hack-Nation 2026, Challenge 3)"
date: "Preprint, 4 October 2026"
mainfont: "STIX Two Text"
mathfont: "STIX Two Math"
fontsize: 10pt
geometry: margin=2cm
linkcolor: blue
header-includes:
  - \usepackage{etoolbox}
  - \AtBeginEnvironment{longtable}{\scriptsize}
---


# How Many Householders Does State Tracking Need? An Exact Law for One-Layer Linear RNNs That Circuit Complexity Does Not Predict

## Abstract

The usual account of why architectures fail at state tracking comes from circuit complexity. Log-precision Transformers can be simulated by constant-depth threshold circuits, and SSMs "cannot express computation outside the complexity class $\mathsf{TC}^0$" [C-lit-merrill-tc0][C-lit-illusion]. We study one-layer linear RNNs whose token transitions are products of generalized Householder factors, as in DeltaNet and DeltaProduct [C-lit-deltaproduct][C-H-protocol]. Consider finite-state realisations of the word problem of a finite group G with alphabet Σ. A finite-state realisation with k factors per token exists if and only if k ≥ $h^*$(G, Σ), where $h^*$ is a group invariant (proved by hand) [C-thm1]. The lower bound combines Lean-checked rank lemmas with a reviewed hand proof [C-L1][C-L4][C-L2]. For the non-solvable group A5 with involution inputs, $h^*$(A5, involutions) = 1 [C-T-A5-involutions]. With all letters, $h^*$(A5, all) = 2 [C-T-A5-all]. The S4 and A5 formats of prior work also need only 2 factors [C-T-S4-tn][C-T-A5-c3c5]. An atlas of all 319 groups of order at most 63 determines $h^*$ exactly for 138 of them [C-atlas]. A preregistered training grid did not meet its success criteria [C-H-gates]. An exact verifier certifies every concrete instance [C-verifier][C-L3].

## Introduction

The architecture debate on state tracking is usually framed in terms of circuit classes. Transformers with logarithmic arithmetic precision "can be simulated by constant-depth logspace-uniform threshold circuits" [C-lit-merrill-tc0]. SSMs are limited "very similarly to transformers" and "cannot solve simple state-tracking problems like permutation composition" [C-lit-illusion]. Self-attention "cannot model periodic finite-state languages, nor hierarchical structure, unless the number of layers or heads increases with input length" [C-lit-hahn]. Barrington's result shows that bounded-width polynomial-size branching programs "recognize exactly those languages in NC1" [C-lit-barrington]. Empirically, Transformers can learn shortcuts to automata, and "$O(1)$-depth simulators are surprisingly common" [C-lit-liu]. LSTMs, by contrast, "can solve regular and counter-language tasks" [C-lit-deletang].

Linear RNNs with non-diagonal transitions have been proposed as a way out of this picture. Grazzi et al. prove that positive-eigenvalue transitions cannot solve parity. They also show that "LRNNs can learn any regular language when their state-transition matrices are products of identity minus vector outer product matrices" [C-lit-grazzi]. DeltaProduct uses "products of $n_h$ generalized Householder transformations", which provides a tunable expressivity–efficiency trade-off [C-lit-deltaproduct]. RWKV-7 claims to "recognize all regular languages" [C-lit-rwkv7] and to solve the problem of "tracking swaps on five elements" [C-lit-rwkv7-swaps-body]. For diagonal SSMs, single-layer DCD models "cannot express state-tracking of any non-Abelian group at finite precision" [C-lit-shakerinava].

These works leave a quantitative gap. The DeltaProduct authors report: "Unexpectedly, S 4 and A 5 can extrapolate robustly using only n h = 2 despite the theorem suggesting 3 and 4, respectively" [C-lit-deltaproduct-body]. They attribute the efficiency to "isomorphism to subgroups of SO ⁡ ( 3 , ℝ )" [C-lit-deltaproduct-so3-body]. The closest prior work states a representation law: "the minimal n h that length-generalizes equals the maximal generator reflection length rank ⁡ ( I − P ) in the representation pinned by the task format (parity 1, S 4 3, A 5 / S 5 4)" [C-lit-howe-law-body]. We ask which number of Householder factors per token is necessary and sufficient. Our answer does not depend on a chosen representation.

Contributions:

- We prove an exact law: a finite-state one-layer realisation with k Householder factors per token exists if and only if k ≥ $h^*$(G, Σ). The proof is by hand and is not machine-checked [C-thm1].
- We give a lower bound on Householder factors per token. It rests on two Lean-checked lemmas [C-L1][C-L4] and a compression lemma that is proved by hand and was reviewed by a red-team agent [C-L2].
- We certify instances. Non-solvable A5 with involution inputs needs exactly 1 factor [C-T-A5-involutions]. A5 with all letters needs exactly 2 [C-T-A5-all]. The S4 and A5 formats of prior work need exactly 2 [C-T-S4-tn][C-T-A5-c3c5].
- We build an atlas over all 319 groups of order at most 63 [C-atlas]. Our own character tables agree with GAP for every group [C-atlas].
- We ran a preregistered training grid. Its predictors and outcome are reported in full, including the learnability failures [C-H-protocol][C-H-gates].
- We describe an agentic lab with an exact verifier and a red team, and we document the loopholes it found and closed [C-lab][C-loophole1][C-redteam].

## Setting and definitions

**Word problem and one-layer realisation.** Fix a finite group G and a generating alphabet Σ. We consider the one-layer recurrence h_t = A(s_t) h_{t-1} + B(s_t) with an arbitrary readout [C-L2]. It *realises the word problem* of (G, Σ) if it outputs the group element of every prefix, for every length [C-L2]. The realisation is *finite-state* if only finitely many states are reachable [C-L2]. In the constructions, the readout maps rho(x) h_0 to pi(x) [C-L3].

**Transition families.** We compare four families:

- diag_pos: diagonal transitions with entries in [0, 1] [C-L5].
- diag_pm: real diagonal transitions with entries in [-1, 1] [C-L5].
- cdiag: complex diagonal transitions [C-L5].
- Householder products: each token applies k generalized Householder factors I - beta u u^T, i.e. DeltaNet or DeltaProduct with beta in [0, 2] [C-L1][C-H-protocol].

**The invariants h and h\*.** $h^*$(G, Σ) is the least k with the following property [C-thm1]. There exist a finite group H, a surjection pi: H -> G, generating lifts t_s of the letters, and a faithful real representation rho of H, such that rank(rho(t_s) - I) <= k for every letter. The invariant h(G, Σ) is the same minimum restricted to H = G [C-thm1]. h can be computed from the real character table [C-L6]. The fixed-space codimension is codim Fix rho(g) = dim rho - (1/|g|) sum_j chi_rho(g^j) [C-L6]. Codimensions add over direct sums [C-L6]. A sum of real irreducible representations is faithful iff the kernels of the summands intersect trivially [C-L6].

## Results I: theory

**Lemma L1 (machine-checked).** Suppose R_1, ..., R_k have rank at most one. Then rank(prod_i (I + R_i) - I) <= k [C-L1]. In particular, a token transition made of k generalized Householder factors differs from the identity by rank at most k [C-L1]. The lemma is checked in Lean 4 with Mathlib as rank_prod_sub_one_le and deltaproduct_rank_le [C-L1]. As a negative control, Lean refutes the strengthened bound k - 1 (strengthened_bound_false) [C-L1]. All theorems use only the standard axioms propext, Classical.choice and Quot.sound [C-L1].

**Lemma L4 (machine-checked).** A real matrix of finite order with rank(M - I) <= 1 is an involution [C-L4]. Hence, if rho is a faithful real representation of a finite group H and pi(t) = s with s of order at least 3, then rank(rho(t) - I) > 1 [C-L4]. It follows that $h^*$(G, Σ) >= 2 whenever the alphabet contains a letter of order at least 3. This holds even when a larger covering group is used [C-L4]. The Lean theorems are sq_eq_one_of_rank_le_one_of_pow_eq_one and no_single_householder_lift [C-L4].

**Lemma L2 (compression lemma; proved by hand, not machine-checked).** Suppose a one-layer recurrence with an arbitrary readout solves the word problem of (G, Σ) for every length, has finitely many reachable states, and satisfies rank(A(s) - I) <= k for every letter. Then $h^*$(G, Σ) <= k [C-L2].

The proof idea has three steps [C-L2]:

1. The reachable states form a finite transformation monoid that maps onto G.
2. An idempotent e of its minimal ideal gives a group eTe that maps onto G.
3. The compressed maps A(u)A(s), restricted to the column space of the affine span of e(Q), form a faithful representation of a covering group whose generators satisfy rank(A(u)(A(s) - I)) <= k.

An independent red-team agent reviewed the proof. It found the proof valid for finite-state realisations, including affine input terms, beta in [0, 2], matrix-valued states and singular transitions [C-L2]. Lemmas L1 and L2 together give the lower bound for Householder products. A realisation with k factors per token has rank(A(s) - I) <= k [C-L1], so k >= $h^*$(G, Σ) [C-L2].

**Lemma L3 (sufficiency; proved by hand, re-verified per instance).** Suppose a finite group H maps onto G with generating lifts t_s, and rho is a faithful real representation of H with rank(rho(t_s) - I) <= k. Then an exact finite-state one-layer realisation with k Householder reflections per token (beta in {0, 2}) exists in dimension dim rho [C-L3]. The construction has three steps [C-L3]:

1. An H-invariant inner product makes rho orthogonal.
2. Cartan–Dieudonné factors each rho(t_s) into rank(rho(t_s) - I) reflections.
3. A generic initial state separates H.

The prior work cites the coarser form of Cartan–Dieudonné, that "every n × n orthogonal matrix can be written as a product of n reflections" [C-lit-grazzi-cd-body]. Our verifier re-checks Lemma L3 on every concrete instance [C-L3].

**Theorem 1 (proved by hand, not machine-checked).** Lemmas L2 and L3 together give the following statement [C-thm1]. For every finite group G and generating alphabet Σ, a finite-state one-layer realisation of the word problem with k Householder factors per token exists if and only if k >= $h^*$(G, Σ) [C-thm1]. In each instance, the parts of the proof have different status:

- The step from Householder factors to a rank bound is machine-checked [C-L1].
- The involution obstruction is machine-checked [C-L4].
- The compression step is a reviewed hand proof [C-L2].
- The constructions are certified exactly [C-L3].

**Diagonal families (Lemma L5, proved by hand via the compression lemma).** Finite-state one-layer realisations exist as follows [C-L5]:

- diag_pos (entries in [0, 1]): only for the trivial group.
- diag_pm (real entries in [-1, 1]): exactly for elementary abelian 2-groups.
- cdiag (complex entries): exactly for abelian groups.

This is consistent with prior theorems on diagonal SSMs [C-L5][C-lit-shakerinava][C-lit-grazzi].

**Abelian groups (Lemma L7, proved by hand; instances certified).** For an abelian group, $h^*$(G, Σ) is 1 if every letter is an involution, and 2 otherwise [C-L7]. The upper bound uses a count cover that tracks each letter's count modulo its order [C-L7]. Its dimension is the number of involution letters plus twice the number of other letters [C-L7].

## Results II: certified instances

Table 1 lists every certified instance with its lower bound, best certified realisation, faithful h and permutation-representation cost [C-T-Z2-all][C-T-A5-all][C-T-S5-all]. Each lower bound has one of two sources. It is either the trivial bound for a nontrivial group, or Lemma L4 (Lean-checked) combined with Lemma L2 (hand proof) [C-T-A5-all][C-T-A5-involutions].

**A5 with involution inputs.** Over faithful representations of A5 alone, h(A5, involutions) = 2 [C-T-A5-involutions]. Nevertheless, $h^*$(A5, involutions) = 1 [C-T-A5-involutions]. The certificate is the so3 construction with every involution letter lifted to its negative. Its covering group has order 120 and dimension 3 [C-T-A5-involutions]. A single reflection per token therefore tracks a non-solvable group exactly, provided the inputs are involutions and a covering group is used [C-T-A5-involutions].

**A5 with all letters.** $h^*$(A5, all) = 2 [C-T-A5-all]. The lower bound uses a letter of order at least 3 [C-T-A5-all]. The upper bound is the so3 construction with a covering group of order 60 in dimension 3 [C-T-A5-all]. The permutation representation costs 4 [C-T-A5-all]. The alphabets cycles3 and cycles5 also give $h^*$ = 2 [C-T-A5-cycles3][C-T-A5-cycles5].

**The generator formats of prior work.** The closest prior work uses the formats "S 4 (transposition + 4-cycle), A 5 (3-cycle + 5-cycle; all-even), S 5 (transposition + 5-cycle; non-solvable)" [C-lit-howe-format-body]. We encode these as the two-letter alphabets tn and c3c5 [C-T-S4-tn][C-T-A5-c3c5][C-T-S5-tn]. For S4, $h^*$(S4, tn) = 2 via so3 in dimension 3, while the permutation representation costs 3 [C-T-S4-tn]. For A5, $h^*$(A5, c3c5) = 2 via so3 in dimension 3, while the permutation representation costs 4 [C-T-A5-c3c5]. The permutation costs coincide with the values of the representation law, "S 4 3, A 5 / S 5 4" [C-lit-howe-law-body]. The exact minimum $h^*$ is lower in both cases [C-T-S4-tn][C-T-A5-c3c5]. This explains the observation that "S 4 and A 5 can extrapolate robustly using only n h = 2" [C-lit-deltaproduct-body]. It is also consistent with the SO(3) explanation offered there [C-lit-deltaproduct-so3-body]. With the full alphabet, S4 likewise has $h^*$(S4, all) = 2 [C-T-S4-all].

**S5.** For the format and for the full alphabet, the certified bounds are 2 and 4, so $h^*$ is not determined [C-T-S5-tn][C-T-S5-all]. In both cases h = 4 over faithful representations [C-T-S5-tn][C-T-S5-all]. With transposition inputs, $h^*$(S5, transpositions) = 1 [C-T-S5-transpositions].

**Abelian groups and Q8.** For Z2^3, h(Z2^3, all) = 3 over faithful representations [C-T-Z2p3-all]. Nevertheless $h^*$(Z2^3, all) = 1, via a count cover of order 128 in dimension 7 [C-T-Z2p3-all][C-L7]. Similarly, h(Z2^2, all) = 2 while $h^*$(Z2^2, all) = 1 [C-T-Z2p2-all]. For Q8, h(Q8, all) = 4, and the certified bounds on $h^*$ are 2 and 6 [C-T-Q8-all].

**Contrast with circuit complexity.** The solvable, abelian group Z3 requires $h^*$(Z3, all) = 2 [C-T-Z3-all]. The non-solvable group A5 with involution inputs requires $h^*$(A5, involutions) = 1 [C-T-A5-involutions]. Within one fixed group, the alphabet changes $h^*$: A5 has the values 1 and 2 [C-T-A5-involutions][C-T-A5-all], and S3 has the values 1 and 2 [C-T-S3-transpositions][C-T-S3-all]. The diagonal families separate differently. diag_pm realises Z2 but not Z3, while cdiag realises Z3 [C-T-Z2-all][C-T-Z3-all]. None of the three diagonal families realises S3 [C-T-S3-transpositions].

## Results III: the atlas

The atlas covers all 319 groups of order at most 63 from the GAP SmallGroups library, each with the full alphabet [C-atlas]. Our own numerical character tables and GAP's exact tables give the same faithful h for every group, with 0 disagreements [C-atlas]. $h^*$ is determined exactly for 138 of 319 groups [C-atlas]. These comprise 32 of the 213 non-abelian groups and every abelian group, the latter by Lemma L7 [C-atlas][C-L7]. The only non-solvable group in the atlas is A5. It has faithful h = 2 and $h^*$ = 2, determined exactly [C-atlas-nonsolvable].

Faithful h is not monotone in solvability. 181 of the 212 solvable non-abelian groups have faithful h >= 3 [C-atlas-monotone]. Every faithful representation of these groups therefore needs more Householder factors per token than the non-solvable A5 [C-atlas-monotone]. The largest faithful h in the atlas is 10, attained by C11:C5 [C-atlas-monotone]. For $h^*$, however, these groups only have certified bounds of the form [2, upper], so we do not claim a strict separation in $h^*$ [C-atlas-monotone]. Sign lifts to G x Z2 multiply a letter's matrix by -1 [C-atlas-twist]. For 37 of the 213 non-abelian groups, they lower the certified upper bound below the faithful h [C-atlas-twist].

Figure 2 and Table 3 show the distribution of faithful h over the non-abelian groups [C-atlas-dist]. The counts are 2: 32, 3: 8, 4: 115, 5: 11, 6: 41, 8: 5, 10: 1 [C-atlas-dist].

## Results IV: preregistered experiments

**Protocol.** The protocol (prereg.md) was committed before the first confirmatory run [C-H-protocol]. Its main parameters are [C-H-protocol]:

- **Models.** One-layer diag_pos, diag_pm, hh1, hh2, hh3 and hh4 (DeltaNet/DeltaProduct with beta in [0, 2]), plus an LSTM [C-H-protocol]. All use a 64-dimensional state and an MLP readout [C-H-protocol].
- **Seeds and training.** 20 seeds (1000-1019) per cell and 3000 steps, with a length curriculum from 8 to 64 and a final stage at 128 [C-H-protocol].
- **Success criteria.** A seed succeeds if its token accuracy on positions 257-512 of length-512 sequences is at least 0.9 [C-H-protocol]. A cell succeeds if at least 10 of 20 seeds succeed [C-H-protocol].
- **Grid.** 9 tasks x 7 architectures [C-H-protocol].

Figure 1 and Table 2 report the cell outcomes [C-H-protocol][C-T-A5-all].

**Cells where our predictor was correct.** In each of the following cells, our predictor said success and the cell succeeded:

- hh3 on Z2/all: 20 of 20 seeds succeed at 2x-4x the longest training length [C-G-hh3-Z2-all].
- hh4 on Z3/all: 12 of 20 [C-G-hh4-Z3-all].
- hh4 on S3/transpositions: 18 of 20 [C-G-hh4-S3-transpositions].
- hh4 on S3/all: 19 of 20 [C-G-hh4-S3-all].
- hh4 on S5/transpositions: 19 of 20 [C-G-hh4-S5-transpositions].
- hh4 on A5/involutions: 20 of 20 at 2x-4x, but 0 of 20 at 7x-8x [C-G-hh4-A5-involutions].
- hh3 and hh4 on Z2^3/all: 20 of 20 at 2x-4x [C-G-hh3-Z2p3-all][C-G-hh4-Z2p3-all], with 0 of 20 and 1 of 20 at 7x-8x [C-G-hh3-Z2p3-all][C-G-hh4-Z2p3-all].

**Learnability failures.** In each of the following cells, our predictor said success but the cell failed:

- hh4 on A5/all: 0 of 20 seeds succeed [C-G-hh4-A5-all]. Mean accuracy is 0.017 at chance 0.017, and in-distribution accuracy is 0.039 [C-G-hh4-A5-all]. The model did not fit even the training lengths, although hh4 exceeds $h^*$(A5, all) = 2 [C-T-A5-all].
- hh4 on S5/all: 0 of 20 seeds succeed, with in-distribution accuracy 0.024 [C-G-hh4-S5-all].
- hh3 on Z3/all: 6 of 20 seeds succeed [C-G-hh3-Z3-all].
- hh4 on Z2/all: 6 of 20 seeds succeed, with mean accuracy 0.515 at chance 0.500, even though its in-distribution accuracy is 1.000 [C-G-hh4-Z2-all].

The theory concerns the existence of exact solutions. These cells show that gradient training under this protocol does not reliably find such solutions [C-thm1][C-G-hh4-A5-all].

**Predictor accuracy.** On the determined cells, each predictor agrees with the cell outcomes as follows [C-H-accuracy]:

| Predictor | Agreement |
|---|---|
| Our algebraic predictor | 8 of 12 [C-H-accuracy] |
| Circuit class (solvable) | 8 of 12 [C-H-accuracy] |
| Abelian | 6 of 12 [C-H-accuracy] |
| Group size | 8 of 12 [C-H-accuracy] |
| Representation law in the permutation representation | 8 of 12 [C-H-accuracy] |
| Faithful representations only | 8 of 12 [C-H-accuracy] |

Our predictor therefore does not beat the baselines on this grid [C-H-accuracy].

**Gates and controls.** The preregistered criteria give the following results [C-H-gates]:

- Accuracy beats every baseline: False.
- All six discriminating tests significant after BH: False.
- Negative control clean: True.
- The overall hypothesis H-EX1: False.

The negative control NC-hh4-S5 trains on random targets in the cell hh4, S5, all [C-H-NC-hh4-S5]. It has successful seeds [0], p = 1.000, and a Benjamini–Hochberg adjusted p = 1.000 (m = 1, q = 0.1), so it is not significant [C-H-NC-hh4-S5]. The confirmatory experiment did not confirm our predictor. The exact law is a statement about expressivity, not about learnability [C-H-gates][C-thm1].

## The agentic lab and the verification pipeline

The lab has six components [C-lab]:

- a literature scout with code-checked quotes;
- an integrator;
- a cascade of four researcher agents;
- an exact verifier;
- a red-team agent;
- a preregistration for every round.

The lab ran 9 rounds at a cost of 5.17 USD [C-lab]. 8 rounds produced an accepted claim, and all 8 survive re-checking with the hardened verifier (0 withdrawn) [C-lab]. 1 round produced a negative result [C-lab]. The scout kept 60 literature findings whose verbatim quote was found by code in the abstract [C-lab]. Before use, the verifier must pass a self-test of 46 known true and known false claims [C-verifier]. These include near-boundary cases, such as the same matrices without the sign lift and k one below the certified value [C-verifier].

**Negative rounds and loopholes.** The negative round asked whether one Householder reflection per token suffices for A5 with involution inputs. No claim from that round passed the verifier and the consistency rule [C-neg1]. Round 1 exposed a loophole [C-loophole1]. An agent answered 'no' and backed the answer with two true but weaker checks. The verifier, however, had refuted the agent's claim $h^*$ = 2 by finding a certificate with k = 1 itself [C-loophole1]. The consistency rule now requires an impossibility certificate for negative answers and exact-value checks for numbers [C-loophole1].

The agents' own interpretations were recorded but not inspected. Several are inconsistent with the hardened rule. In round 3 the agent interpreted $h^*$(A5, involutions) as "> 1" [C-expressivity-R3-I], which contradicts the certified value 1 [C-T-A5-involutions]. In round 2 the interpretation "$h^*$(Z2^3, all) <= 3" is weaker than the certified value [C-expressivity-R2-I][C-T-Z2p3-all]. The red-team counter-check contested three rounds [C-expressivity-R4][C-expressivity-R6][C-expressivity-R8].

**Red team.** An independent red-team agent with read and execute rights only found three bugs [C-redteam]:

- The group names S1, D1 and D2 denoted wrong groups, so one false sentence each could be printed.
- The published $h^*$ sentence omitted the finite-state hypothesis.
- The consistency rule accepted unchecked numbers in answer texts.

All three bugs were fixed and turned into regression cases [C-redteam]. The red team also confirmed the exact core against an independent re-implementation. 189 library constructions, 15556 exhaustive explicit-matrix claims and the character tables of all 319 SmallGroups were checked against GAP, with 0 disagreements [C-redteam].

## Limitations and open questions

- **Finite-state assumption.** Lemma L2 and Theorem 1 assume finitely many reachable states [C-L2][C-thm1]. Realisations with unboundedly many states fall outside the law.
- **Token-local transitions.** In the recurrence h_t = A(s_t) h_{t-1} + B(s_t), the transition depends only on the current letter [C-L2]. Architectures that let transitions depend on neighbouring tokens are not covered.
- **Additive input pathway.** The closest prior work reports that an additive input pathway acts as a "parasitic attractor". Without that pathway, the same architecture "learns the exact automaton" [C-lit-howe]. Our compression lemma admits affine input terms for expressivity [C-L2], but our grid does not isolate this pathway [C-H-protocol].
- **Exact versus finite-precision arithmetic.** Our realisations are exact and certified in exact arithmetic [C-L3]. The cited impossibility results are stated at finite precision [C-lit-grazzi][C-lit-shakerinava].
- **Hand proofs.** The upper-bound half of the law rests on Lemma L3, a hand proof that is re-verified on every instance [C-L3]. Lemmas L2, L5 and L7 are hand proofs and are not machine-checked [C-L2][C-L5][C-L7].
- **Open intervals.** $h^*$ remains open for S5/all, S5/tn and Q8/all [C-T-S5-all][C-T-S5-tn][C-T-Q8-all]. In the atlas, $h^*$ is determined for only 138 of 319 groups [C-atlas].
- **Multi-layer models.** For diagonal SSMs, k layers suffice if and only if the group has "a subnormal series of length $k$, with Abelian factors" [C-lit-shakerinava]. A multi-layer analogue of $h^*$ is open.
- **Intermediate generation as a Householder budget.** For Transformers, the gain from chain of thought "depends crucially on the amount of intermediate generation" [C-lit-cot]. With T steps of CoT, constant-depth Transformers can solve "any problem solvable by boolean circuits of size $T$" [C-lit-li-cot]. Whether intermediate generation or padding acts as an additional Householder budget for one-layer linear RNNs is an open question.

![Figure 1. Preregistered grid: number of seeds (out of 20) whose accuracy on positions 257-512 is at least 0.9, with the outcome predicted by the algebraic law (+ success, − failure, ? undetermined). Table 2 is the table view. Claims [C-G-*].](fig_grid.png)

*Figure 1. Preregistered grid: number of seeds (out of 20) whose accuracy on positions 257-512 is at least 0.9, with the outcome predicted by the algebraic law (+ success, − failure, ? undetermined). Table 2 is the table view. Claims [C-G-*].*


![Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h (jittered vertically) against group order. The only non-solvable group, A5, sits at the minimum value 2 while most solvable groups need more. Claims [C-atlas-monotone], [C-atlas-nonsolvable].](fig_atlas.png)

*Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h (jittered vertically) against group order. The only non-solvable group, A5, sits at the minimum value 2 while most solvable groups need more. Claims [C-atlas-monotone], [C-atlas-nonsolvable].*


## Tables

**Table 1.** Certified one-layer Householder complexity (exact verifier). lower: certified lower bound (Lemma L4 for 2); upper: best exact realisation found by the verifier (construction / sign twist, covering-group order |H|, dimension d); h: faithful representations of G only (own and GAP character tables); perm: cost in the permutation representation (the representation law of prior work). Claims [C-T-*].

| G | alphabet | order | solvable | lower | upper | construction | abs(H) | d | h | perm |
|---|---|---|---|---|---|---|---|---|---|---|
| Z2 | all | 2 | yes | 1 | 1 | perm/none | 2 | 2 | 1 | 1 |
| Z3 | all | 3 | yes | 2 | 2 | perm/none | 3 | 3 | 2 | 2 |
| Z5 | all | 5 | yes | 2 | 2 | planar/none | 5 | 2 | 2 | 4 |
| Z6 | all | 6 | yes | 2 | 2 | planar/none | 6 | 2 | 2 | 5 |
| Z2^2 | all | 4 | yes | 1 | 1 | count/none | 8 | 3 | 2 | 2 |
| Z2^3 | all | 8 | yes | 1 | 1 | count/none | 128 | 7 | 3 | 3 |
| S3 | transpositions | 6 | yes | 1 | 1 | perm/none | 6 | 3 | 1 | 1 |
| S3 | all | 6 | yes | 2 | 2 | perm/none | 6 | 3 | 2 | 2 |
| D4 | all | 8 | yes | 2 | 2 | planar/none | 8 | 2 | 2 | 3 |
| D5 | all | 10 | yes | 2 | 2 | planar/none | 10 | 2 | 2 | 4 |
| Q8 | all | 8 | yes | 2 | 6 | perm/none | 8 | 8 | 4 | 6 |
| A4 | all | 12 | yes | 2 | 2 | perm/none | 12 | 4 | 2 | 2 |
| S4 | transpositions | 24 | yes | 1 | 1 | perm/none | 24 | 4 | 1 | 1 |
| S4 | all | 24 | yes | 2 | 2 | so3/none | 24 | 3 | 2 | 3 |
| S4 | tn | 24 | yes | 2 | 2 | so3/none | 24 | 3 | 2 | 3 |
| A5 | c3c5 | 60 | no | 2 | 2 | so3/none | 60 | 3 | 2 | 4 |
| S5 | tn | 120 | no | 2 | 4 | perm/none | 120 | 5 | 4 | 4 |
| A5 | involutions | 60 | no | 1 | 1 | so3/involutions | 120 | 3 | 2 | 2 |
| A5 | cycles3 | 60 | no | 2 | 2 | perm/none | 60 | 5 | 2 | 2 |
| A5 | cycles5 | 60 | no | 2 | 2 | so3/none | 60 | 3 | 2 | 4 |
| A5 | all | 60 | no | 2 | 2 | so3/none | 60 | 3 | 2 | 4 |
| S5 | transpositions | 120 | no | 1 | 1 | perm/none | 120 | 5 | 1 | 1 |
| S5 | all | 120 | no | 2 | 4 | perm/none | 120 | 5 | 4 | 4 |

**Table 2.** Preregistered grid: successful seeds out of 20 (accuracy >= 0.9 on positions 257-512 of length-512 sequences); mark: predicted success (+), predicted failure (-), undetermined (?) by our predictor. Claims [C-G-*].

| task | diag_pos | diag_pm | hh1 | hh2 | hh3 | hh4 | lstm |
|---|---|---|---|---|---|---|---|
| Z2/all | n/a | n/a | n/a | n/a | 20 + | 6 + | n/a |
| Z3/all | n/a | n/a | n/a | n/a | 6 + | 12 + | n/a |
| Z2^3/all | n/a | n/a | n/a | n/a | 20 + | 20 + | n/a |
| S3/transpositions | n/a | n/a | n/a | n/a | n/a | 18 + | n/a |
| S3/all | n/a | n/a | n/a | n/a | n/a | 19 + | n/a |
| A5/involutions | n/a | n/a | n/a | n/a | n/a | 20 + | n/a |
| A5/all | n/a | n/a | n/a | n/a | n/a | 0 + | n/a |
| S5/transpositions | n/a | n/a | n/a | n/a | n/a | 19 + | n/a |
| S5/all | n/a | n/a | n/a | n/a | n/a | 0 + | n/a |

**Table 3.** Atlas, all 319 groups of order <= 63, full alphabet. Claims [C-atlas*].

| class | groups | $h^*$ exact | faithful h = 2 | faithful h >= 3 |
|---|---|---|---|---|
| abelian | 105 | 105 | 62 | 42 |
| solvable non-abelian | 212 | 31 | 31 | 181 |
| non-solvable | 1 | 1 | 1 | 0 |

---
Verification log: 76 claims cited, correction rounds [{"round": 0, "violations": 15}, {"round": 1, "violations": 0}, {"final_removed": 0}], 0 unsupported sentences removed, errata applied after the gate: [], remaining violations: 0. Tables and figures are generated by code from expressivity/results/.
