# How Many Householders Does State Tracking Need? A Representation-Theoretic Characterisation for One-Layer Linear RNNs, and Where Training Falls Short

Team Ninja Turtles, Hack-Nation 2026, Challenge 3 (Agentic Scientific Discovery)

# How Many Householders Does State Tracking Need? A Representation-Theoretic Characterisation for One-Layer Linear RNNs, and Where Training Falls Short

## Abstract

Why do architectures fail at state tracking? Circuit complexity places log-precision Transformers and diagonal state-space models in $\mathsf{TC}^0$ [C-lit-merrill-tc0][C-lit-illusion]. Bounded-width branching programs, by contrast, recognise exactly NC1 [C-lit-barrington]. We study one-layer linear RNNs whose transitions are products of Householder factors, as in DeltaNet and DeltaProduct. We assume real states, finitely many reachable states and token-local transitions, and we allow $\beta = 2$. Under these assumptions, $k$ factors per token suffice if and only if $k \ge h^*(G,\Sigma)$, an invariant defined over covering groups [C-thm1]. This gives the first lower bound on factors per token for general groups and alphabets [C-novelty]. $A_5$ with involution inputs needs one reflection. $A_5$ with all inputs needs two, and so do the $S_4$/$A_5$ formats of the closest prior work [C-T-A5-involutions][C-T-A5-all][C-T-S4-tn][C-T-A5-c3c5]. An atlas covers all groups of order at most 63 [C-atlas]. Upper bounds are exact certificates. Lower bounds combine Lean-checked lemmas with a compression lemma proved by hand [C-L1][C-L4][C-L2].

Training falls short of the theory. On the preregistered H-EX1 grid our predictor matched 47 of 61 cells [C-H-accuracy]. The representation baselines matched 50 and 48 [C-H-accuracy]. The H-EX2 criterion was not met [C-X-result]. hh1 did not learn $A_5$/involutions, and no architecture learned $A_5$/all [C-G-hh1-A5-involutions][C-G-hh4-A5-all]. One cell succeeded in 18 of 20 seeds on the GPU and in 0 of 20 on the CPU [C-H-replication].

## Introduction

**The architecture debate.** Transformers with logarithmic precision can be simulated by constant-depth threshold circuits [C-lit-merrill-tc0]. State-space models "cannot express computation outside the complexity class $\mathsf{TC}^0$", so they "cannot solve simple state-tracking problems like permutation composition" [C-lit-illusion]. Bounded-width polynomial-size branching programs recognise exactly the languages in NC1 [C-lit-barrington]. Under standard complexity conjectures, this separates $\mathsf{TC}^0$ architectures from state tracking [C-lit-rwkv7].

Self-attention has further limits on periodic finite-state languages [C-lit-hahn]. In experiments, LSTMs solve regular and counter-language tasks, while RNNs and Transformers fail to generalise on non-regular ones [C-lit-deletang]. Transformers find shallow shortcuts to automata, and Krohn–Rhodes theory helps explain them [C-lit-liu]. Chain of thought increases the expressive power of Transformers [C-lit-cot][C-lit-li-cot].

**The gap.** Several constructions show that linear RNNs can track state:
- Linear RNNs whose transitions are products of identity-minus-outer-product matrices "can learn any regular language". With only positive eigenvalues they cannot solve parity [C-lit-grazzi].
- RWKV-7 recognises all regular languages [C-lit-rwkv7] and can track swaps on five elements [C-lit-rwkv7-swaps-body].
- DeltaProduct uses products of $n_h$ generalized Householder transformations, and its state tracking improves as $n_h$ grows [C-lit-deltaproduct].

These constructions give upper bounds. DeltaProduct also reports an unexpected result: "$S_4$ and $A_5$ can extrapolate robustly using only $n_h = 2$ despite the theorem suggesting 3 and 4, respectively" [C-lit-deltaproduct-body].

Howe states a representation law: "the minimal $n_h$ that length-generalizes equals the maximal generator reflection length $\operatorname{rank}(I-P)$ in the representation pinned by the task format (parity 1, $S_4$ 3, $A_5$ / $S_5$ 4)" [C-lit-howe-law-body]. The formats are "$S_4$ (transposition + 4-cycle), $A_5$ (3-cycle + 5-cycle; all-even), $S_5$ (transposition + 5-cycle; non-solvable)" [C-lit-howe-format-body]. This law is empirical and concerns learning. It is stated for an architecture without the additive input pathway, where input acts only through the orthogonal transitions [C-lit-howe]. Our realisation with a zero initial state uses exactly that additive term [C-L3]. So a gap between our expressivity values and Howe's learned values is not a contradiction.

Complex KDA (arXiv:2609.24797) proves a lower bound [C-lit-ckda-thm4-body]. It rules out one-layer $S_5$ tracking for DeltaProduct with at most three factors, assuming non-expansive transitions and finite reachability [C-lit-ckda-thm4-body]. Under those assumptions, four factors are the minimum for $S_5$ [C-lit-ckda-four-body]. Its compression starts from a word of minimum Frobenius norm [C-lit-ckda-compression-body], and the paper notes that tracking does not require a faithful representation [C-lit-ckda-decoder-body]. Our compression is different. It uses the minimal ideal of the transition monoid, needs no norm bound, and transfers the rank bound. Neither result contains the other [C-ckda-relation]:
- Complex KDA covers scalar gates, its own parameterisation, and several heads.
- Our result covers expansive transitions and every finite group and alphabet.

Before this work, no general minimum was known for an arbitrary finite group and input alphabet [C-novelty][C-ckda-relation].

**Contributions.**
- *An exact law, proved by hand.* For every finite group $G$ and generating alphabet $\Sigma$, a finite-state one-layer realisation with $k$ Householder factors per token exists if and only if $k \ge h^*(G,\Sigma)$ [C-thm1]. Here $h^*$ minimises over covering groups and their faithful real representations. We did not find this invariant in prior work; the closest notion, generation in codimension $k$, has no alphabet [C-novelty][C-lit-martino-singh-body]. The necessity half rests on a compression lemma that needs no norm bound and is proved by hand [C-L2]. The compression idea appears for $S_5$ in Complex KDA [C-novelty].
- *Machine-checked rank lemmas* in Lean 4 [C-L1][C-L4].
- *Certified instances.*
  - One reflection suffices for $A_5$ with involution inputs [C-T-A5-involutions]. Complex KDA does not state this [C-ckda-relation].
  - $A_5$ with all inputs needs exactly two [C-T-A5-all].
  - The generator formats of prior work need two [C-T-S4-tn][C-T-A5-c3c5]. The upper bound of two comes from DeltaProduct's SO(3) construction [C-lit-deltaproduct-so3-body][C-lit-deltaproduct-body]. We add the matching lower bound, from L4 and L2.
- *$S_5$, from a hand step plus a cited theorem, building on Complex KDA.* We obtain $h^*(S_5,\text{all}) = 4$, but this is not a certified instance [C-S5][C-T-S5-all].
- *An atlas* over all groups of order at most 63 [C-atlas]. We did not find a comparable atlas in prior work [C-novelty].
- *A preregistered training grid and addendum.* On both, our invariant largely fails as a predictor of learnability [C-H-gates][C-X-result].

## Setting and definitions

Let $\Sigma$ be an alphabet of letters that generate a finite group $G$. A word over $\Sigma$ is read token by token. Solving the word problem means outputting the group element of every prefix, for every length [C-L2][C-thm1].

A *one-layer realisation* is a real recurrence $z_t = A(s_t) z_{t-1} + B(s_t)$ with an arbitrary readout. The transition $A$ and the input term $B$ depend only on the current token $s_t$ [C-L2]. So transitions are token-local, with no short convolution [C-thm1]. The realisation is *finite-state* if only finitely many states are reachable [C-L2][C-thm1].

**Transition families.**
- A Householder family with $k$ factors per token uses $A(s) = \prod_{i=1}^k (I - \beta_i u_i u_i^\top)$ [C-L1]. The models hh1–hh4 are DeltaNet/DeltaProduct with $\beta \in [0,2]$ [C-H-protocol].
- diag_pos has diagonal transitions with entries in $[0,1]$ [C-L5].
- diag_pm has real diagonal entries in $[-1,1]$ [C-L5].
- cdiag has complex diagonal entries of modulus at most $1$ [C-L5].

**The invariants.** $h^*(G,\Sigma)$ is the least $k$ for which all of the following exist [C-thm1]:
- a finite group $H$,
- a surjection $\pi: H \to G$,
- generating lifts $t_s$ of the letters,
- a faithful real representation $\rho$ of $H$ with $\operatorname{rank}(\rho(t_s) - I) \le k$ for every letter $s$.

$h(G,\Sigma)$ is the same minimum with $H = G$ [C-thm1]. Requiring the lifts to generate $H$ does not change $h^*$ [C-thm1].

The definitions and all written proofs of the lemmas and of Theorem 1 are in the companion ledger [C-ledger].

## Results I: theory

**Lemma L1 (machine-checked).** If $R_1,\dots,R_k$ have rank at most one, then $\operatorname{rank}\big(\prod_i (I+R_i) - I\big) \le k$. In particular, a token transition made of $k$ factors $I - \beta u u^\top$ differs from the identity by a matrix of rank at most $k$ [C-L1]. The proof is in Lean 4 with Mathlib and uses only the standard axioms. As a negative control, Lean refutes the strengthened bound $k-1$ [C-L1].

**Lemma L4 (machine-checked).** A real matrix of finite order with $\operatorname{rank}(M-I) \le 1$ is an involution. Hence, if $\rho$ is a faithful real representation of $H$, $\pi: H \to G$, and $\pi(t) = s$ with $s$ of order at least $3$, then $\operatorname{rank}(\rho(t) - I) > 1$. So $h^*(G,\Sigma) \ge 2$ whenever $\Sigma$ contains a letter of order at least $3$, even when a larger covering group is used [C-L4]. That a real reflection has order two is classical [C-novelty].

**Lemma L2 (compression; proved by hand, not machine-checked).** Suppose a one-layer real recurrence with arbitrary readout has three properties: it solves the word problem of $(G,\Sigma)$ for every length, it has finitely many reachable states, and $\operatorname{rank}(A(s)-I) \le k$ for every letter. Then $h^*(G,\Sigma) \le k$ [C-L2].

The proof has three steps [C-L2]:
1. The reachable states form a finite transformation monoid that maps onto $G$.
2. An idempotent $e$ of its minimal ideal gives a group $eTe$ that maps onto $G$.
3. Restrict the compressed maps $A(u)A(s)$ to the column space of the affine span of $e(Q)$. They form a faithful representation of a covering group and satisfy $\operatorname{rank}(A(u)(A(s)-I)) \le k$.

The lemma covers affine input terms, $\beta \in [0,2]$ including singular transitions, matrix-valued states, and arbitrary readouts. Two independent red-team agents reviewed it. The second checked the construction exactly on adversarial instances and found it valid after wording fixes [C-L2].

**Lemma L3 (sufficiency; proved by hand, re-verified on every concrete instance by the exact verifier).** Suppose $H$ maps onto $G$ with generating lifts $t_s$ and a faithful real representation $\rho$ with $\operatorname{rank}(\rho(t_s)-I) \le k$. Then an exact finite-state realisation with $k$ reflections per token exists in dimension $\dim\rho$, with each $\beta$ equal to either $0$ or $2$ [C-L3]. The construction has four steps:
1. An $H$-invariant inner product makes $\rho$ orthogonal.
2. Cartan–Dieudonné factors each $\rho(t_s)$ into $\operatorname{rank}(\rho(t_s)-I)$ reflections.
3. A generic initial state separates the elements of $H$.
4. The readout maps $\rho(x) z_0$ to $\pi(x)$.

The construction needs $\beta = 2$ exactly, with unit keys. With a zero initial state, as in DeltaNet, the input term $v = -ck$ supplies the offset [C-L3]. Prior work uses the classical fact that an $n\times n$ orthogonal matrix is a product of $n$ reflections to obtain upper bounds [C-lit-grazzi-cd-body].

**Theorem 1 (proved by hand from Lemmas L2 and L3; proof in the companion ledger [C-ledger]).** For every finite group $G$ and generating alphabet $\Sigma$, a finite-state one-layer realisation of the word problem with $k$ Householder factors per token exists if and only if $k \ge h^*(G,\Sigma)$. The hypotheses are [C-thm1]:
- real states;
- finitely many reachable states;
- transitions that depend only on the current token;
- one layer;
- $\beta$ allowed to equal $2$.

**What is proved how.**
- *Machine-checked:* L1 and L4 [C-L1][C-L4].
- *Hand proofs, not machine-checked* [C-L2][C-L3][C-thm1][C-L5][C-L7][C-open-beta][C-complex][C-S5][C-Q8-lower]:
  - Lemmas L2, L3, L5 and L7;
  - Theorem 1;
  - the open-$\beta$ corollary;
  - the complex-state remark;
  - the $S_5$ lower-bound step;
  - the $Q_8$ lower bound.
- *Exact verifier:* it re-checks every concrete upper bound [C-L3][C-verifier].

**Computing $h$.** By standard character theory, $\operatorname{codim}\operatorname{Fix}\rho(g) = \dim\rho - \frac{1}{|g|}\sum_j \chi_\rho(g^j)$. Codimensions add over direct sums. A sum of real irreducible representations is faithful if and only if their kernels intersect trivially. So $h(G,\Sigma)$ is a finite optimisation over the real character table [C-L6].

**Diagonal families (Lemma L5; proved by hand via the compression lemma, not machine-checked).** A finite-state one-layer realisation exists [C-L5]:
- with entries in $[0,1]$, only for the trivial group;
- with real entries in $[-1,1]$, exactly for elementary abelian $2$-groups;
- with complex entries of modulus at most $1$, exactly for abelian groups.

This agrees with prior theorems on diagonal SSMs [C-L5]. For example, single-layer DCD SSMs cannot track any non-abelian group [C-lit-shakerinava].

**Abelian groups (Lemma L7; proved by hand, instances certified).** For a nontrivial abelian group, $h^*(G,\Sigma)$ is $1$ if every letter is an involution and $2$ otherwise [C-L7]. The upper bound uses a count cover, which tracks each letter's count modulo its order. Its dimension is the number of involution letters plus twice the number of other letters. This is an upper bound on the dimension, not the minimum [C-L7].

**Boundary remarks (proved by hand; found by the theory red team).**
- If $\beta$ is confined to $[0, 2)$, as with a sigmoid parameterisation, no nontrivial group is exactly realisable for any number of factors [C-open-beta]. Likewise, open intervals for diagonal entries admit only the trivial group [C-open-beta].
- A complex realisation of complex rank $k$ only gives $h^* \le 2k$ [C-complex].

## Results II: certified instances

Table 1 lists every certified instance. The two bounds in each row have different status:
- *Upper bound:* an exact certificate.
- *Lower bound:* the hand-proved Lemma L2, combined with either Lemma L4 (machine-checked) or the nontriviality of $G$ [C-T-A5-all][C-T-Z3-all][C-T-Z2-all].

**$A_5$ with involution inputs: one reflection.** In the SO(3) construction, every involution letter is lifted to its negative. This gives an exact realisation with one reflection per token, through a covering group of order 120 in dimension 3 [C-T-A5-involutions]. So $h^*(A_5,\text{involutions}) = 1$, although the faithful value is $h = 2$ [C-T-A5-involutions]. By Lemma L4, no such lift exists for letters of order at least three [C-L4].

**$A_5$ with all inputs: two.** $h^*(A_5,\text{all}) = 2$, via the SO(3) construction in dimension 3. The permutation representation costs 4 [C-T-A5-all]. The same value holds for the 3-cycle and 5-cycle alphabets [C-T-A5-cycles3][C-T-A5-cycles5].

**Generator formats of prior work.**
- $h^*(S_4,\text{tn}) = 2$, via so3 in dimension 3 [C-T-S4-tn].
- $h^*(A_5,\text{c3c5}) = 2$, via so3 [C-T-A5-c3c5].

In the permutation representation these formats cost 3 and 4 [C-T-S4-tn][C-T-A5-c3c5], which are the values of Howe's law [C-lit-howe-law-body]. Howe's law is an empirical statement about length generalisation without the additive input pathway [C-lit-howe]. Our values are exact expressivity values for a realisation that may use the additive term [C-L3]. The lower values here therefore do not contradict that law.

The SO(3) upper-bound constructions for $S_4$ and $A_5$ are due to DeltaProduct, which attributes their efficiency to "their isomorphism to subgroups of $\mathrm{SO}(3,\mathbb{R})$" [C-lit-deltaproduct-so3-body]. Complex KDA states a related one-head result for subgroups of SO(3) [C-lit-ckda-so3-body]. For these formats we contribute the matching lower bound [C-T-S4-tn][C-T-A5-c3c5]. Under our hypotheses, this explains DeltaProduct's unexpected $n_h = 2$ observation as exact optimality [C-lit-deltaproduct-body].

**Transposition alphabets.** $S_3$, $S_4$ and $S_5$ with transposition alphabets each need exactly one reflection [C-T-S3-transpositions][C-T-S4-transpositions][C-T-S5-transpositions].

**$\mathbb{Z}_2^3$: below the faithful value.** $h^*(\mathbb{Z}_2^3,\text{all}) = 1$, via a count cover of order 128 in dimension 7, while the faithful value is $h = 3$ [C-T-Z2p3-all]. Among the diagonal families, diag_pm and cdiag realise it and diag_pos does not [C-T-Z2p3-all].

**$Q_8$.**
- The faithful value is $h = 4$, and the certified lower bound is $2$ [C-T-Q8-all].
- The covering group C4:C4 of order 16, with a rational 4-dimensional representation, certifies $h^*(Q_8,\text{all}) \le 3$ [C-T-Q8-cover].
- A hand argument, not machine-checked, gives $h^*(Q_8,\text{all}) \ge 3$ [C-Q8-lower].

**$S_5$, kept separate.** For both alphabets all and tn, the certified bounds are $[2,4]$ and the faithful value is $h = 4$ [C-T-S5-all][C-T-S5-tn]. The value $h^*(S_5,\text{all}) = 4$, under exact finite reachability, rests on a hand step combined with a published theorem [C-S5]:
1. A cover with rank at most $3$ can be made orthogonal by averaging.
2. It is then a single-head, orthogonal, finite-state tracker of the kind excluded by Theorem 4 of arXiv:2609.24797 [C-S5][C-lit-ckda-thm4-body].

Our argument only needs an alphabet that contains a 5-cycle and a transposition [C-S5]. This extension is our own observation, proved by hand; it is not stated in arXiv:2609.24797 [C-S5].

An independent hand argument gives $h^*(S_5,\text{all}) \ge 3$ and $h^*(S_5,\text{tn}) \ge 3$ unconditionally. Combined with the classification of arXiv:1509.06922, it gives $4$ for every alphabet that contains a 5-cycle [C-S5-hand3][C-lit-lange-mikhailova-body]. For $S_5$ the value $4$ matches Howe's law [C-lit-howe-law-body]. Here the two agree, whereas on $S_4$ and $A_5$ they differ.

**Contrast with circuit complexity.** The non-solvable $A_5$ with all inputs costs exactly as much as the solvable $S_3$ [C-T-A5-all][C-T-S3-all], the cyclic $\mathbb{Z}_3$ [C-T-Z3-all], or $A_4$ [C-T-A4-all]. With involution inputs, $A_5$ costs as much as parity [C-T-A5-involutions][C-T-Z2-all]. Within this architecture class, the alphabet and the representation theory set the Householder budget, not solvability [C-thm1].

## Results III: the atlas

The atlas covers all 319 groups of order at most 63 in the GAP SmallGroups library, with the full alphabet [C-atlas]. Figure 2 and Table 3 summarise it.
- Our numerical character tables and GAP's exact tables give the same faithful $h$ for every group (0 disagreements) [C-atlas].
- $h^*$ is determined exactly for 138 of the 319 groups [C-atlas]. These are 32 of the 213 non-abelian groups, plus every abelian group by Lemma L7 [C-atlas].
- Over the non-abelian groups, the faithful $h$ is distributed as 2: 32, 3: 8, 4: 115, 5: 11, 6: 41, 8: 5, 10: 1 [C-atlas-dist].
- Sign lifts to $G \times \mathbb{Z}_2$ push the certified upper bound below $h$ for 37 of the 213 non-abelian groups [C-atlas-twist].
- Covers of twice the group order lowered 17 further upper bounds [C-atlas-improved]. Their lower bounds stay at 2, so these groups remain undetermined [C-atlas-improved].

**Non-monotonicity.** The only non-solvable group in the atlas is $A_5$, with $h = h^* = 2$ [C-atlas-nonsolvable]. 181 of the 212 solvable non-abelian groups have faithful $h \ge 3$ [C-atlas-monotone]. The largest faithful value is 10 [C-atlas-monotone]. So, in faithful representations, many solvable groups need more Householder factors per token than $A_5$. For $h^*$, however, these groups only have certified bounds $[2,\text{upper}]$, so we claim no strict separation in $h^*$ [C-atlas-monotone].

## Results IV: preregistered experiments

### H-EX1 grid

**Protocol.** The protocol was committed before the first confirmatory run [C-H-protocol]:
- *Grid:* 9 tasks × 7 architectures (diag_pos, diag_pm, hh1–hh4 with $\beta \in [0,2]$, and an LSTM) [C-H-protocol].
- *Model:* one layer, 64-dimensional state, MLP readout [C-H-protocol].
- *Training:* 20 seeds (1000-1019), 3000 steps, a length curriculum from 8 to 64 and a final stage at 128 [C-H-protocol].
- *Seed success:* token accuracy of at least 0.9 on positions 257-512 of length-512 sequences [C-H-protocol].
- *Cell success:* at least 10 of 20 seeds succeed [C-H-protocol].

The parameterisation reaches $\beta = 0$ and $\beta = 2$ exactly [C-open-beta]. For every highlighted cell we also report the preregistered secondary outcome at 7x-8x the longest training length [C-G-diag_pm-Z2-all].

**Predictors.** We compare our algebraic predictor with five baselines [C-H-accuracy]:
- circuit class (solvable);
- abelian;
- group size;
- the representation law in the permutation representation;
- faithful representations only.

**Accuracy (primary).** Agreement with the outcomes on the determined cells [C-H-accuracy]:

| Predictor | Cells matched |
|---|---|
| Our predictor | 47 of 61 [C-H-accuracy] |
| Circuit class | 41 of 61 [C-H-accuracy] |
| Abelian | 37 of 61 [C-H-accuracy] |
| Group size | 41 of 61 [C-H-accuracy] |
| Permutation-representation law | 50 of 61 [C-H-accuracy] |
| Faithful representations only | 48 of 61 [C-H-accuracy] |

Both representation baselines matched more cells than our predictor. The preregistered criterion "accuracy beats every baseline" was therefore not met [C-H-gates]. Figure 1 and Table 2 show all cells.

**Every cell where our predictor errs.** Counts are successful seeds at 2x-4x the longest training length. The secondary outcome at 7x-8x is given in parentheses [C-G-diag_pm-Z2-all]. In all fourteen cells, our predictor predicted success and the cell failed:
- hh2 on $\mathbb{Z}_2$/all: 3 of 20 (9 of 20) [C-G-hh2-Z2-all]
- hh4 on $\mathbb{Z}_2$/all: 6 of 20 (7 of 20) [C-G-hh4-Z2-all]
- hh3 on $\mathbb{Z}_3$/all: 6 of 20 (5 of 20) [C-G-hh3-Z3-all]
- hh1 on $\mathbb{Z}_2^3$/all: 1 of 20 (1 of 20) [C-G-hh1-Z2p3-all]
- hh1 on $A_5$/involutions: 0 of 20 (0 of 20) [C-G-hh1-A5-involutions]
- hh2 on $A_5$/involutions: 0 of 20 (0 of 20) [C-G-hh2-A5-involutions]
- LSTM on $A_5$/involutions: 0 of 20 (0 of 20) [C-G-lstm-A5-involutions]
- hh2 on $A_5$/all: 0 of 20 (0 of 20) [C-G-hh2-A5-all]
- hh3 on $A_5$/all: 0 of 20 (0 of 20) [C-G-hh3-A5-all]
- hh4 on $A_5$/all: 0 of 20 (0 of 20) [C-G-hh4-A5-all]
- LSTM on $A_5$/all: 0 of 20 (0 of 20) [C-G-lstm-A5-all]
- LSTM on $S_5$/transpositions: 8 of 20 (1 of 20) [C-G-lstm-S5-transpositions]
- hh4 on $S_5$/all: 0 of 20 (0 of 20) [C-G-hh4-S5-all]
- LSTM on $S_5$/all: 0 of 20 (0 of 20) [C-G-lstm-S5-all]

For hh2 and hh3 on $S_5$/all our predictor is undetermined. Both cells had 0 of 20 [C-G-hh2-S5-all][C-G-hh3-S5-all].

hh1 did not learn the headline one-reflection instance, $A_5$/involutions. Its in-distribution accuracy there was only 0.074 [C-G-hh1-A5-involutions]. No architecture learned $A_5$/all [C-G-diag_pos-A5-all][C-G-diag_pm-A5-all][C-G-hh1-A5-all][C-G-hh2-A5-all][C-G-hh3-A5-all][C-G-hh4-A5-all][C-G-lstm-A5-all].

**Highlighted cells where the prediction matched.**
- hh1 on $S_3$/transpositions: 20 of 20 (18 of 20) [C-G-hh1-S3-transpositions].
- hh1 on $S_5$/transpositions: 20 of 20 (20 of 20) [C-G-hh1-S5-transpositions].
- hh1 on $S_3$/all fails as predicted: 0 of 20 (0 of 20) [C-G-hh1-S3-all].
- hh1 on $\mathbb{Z}_3$/all fails as predicted: 0 of 20 (0 of 20) [C-G-hh1-Z3-all].
- hh3 on $A_5$/involutions: 20 of 20 (3 of 20) [C-G-hh3-A5-involutions].
- hh4 on $A_5$/involutions: 20 of 20 (0 of 20) [C-G-hh4-A5-involutions].
- diag_pm on $\mathbb{Z}_2^3$/all: 20 of 20 (0 of 20) [C-G-diag_pm-Z2p3-all].
- diag_pm on $\mathbb{Z}_3$/all fails as predicted: 0 of 20 (0 of 20) [C-G-diag_pm-Z3-all].

Many of these primary successes collapse at 7x-8x [C-G-diag_pm-Z2p3-all]:
- diag_pm on $\mathbb{Z}_2^3$/all falls from 20 to 0 [C-G-diag_pm-Z2p3-all].
- hh3 on $\mathbb{Z}_2^3$/all falls from 20 to 0 [C-G-hh3-Z2p3-all].
- hh4 on $A_5$/involutions falls from 20 to 0, and hh3 keeps only 3 [C-G-hh4-A5-involutions][C-G-hh3-A5-involutions].
- hh2 on $S_3$/all falls from 19 to 1 [C-G-hh2-S3-all].

Agreement on the primary outcome therefore does not imply robust length generalisation.

**Discriminating tests.** All tests are one-sided Fisher exact tests with Benjamini–Hochberg correction ($m = 9$, $q = 0.1$) [C-H-D1]. We also report BH over all 12 tests of H-EX1 and H-EX2 [C-H-D1].
- **D1:** hh1 on $A_5$/involutions vs $A_5$/all, testing one reflection for $A_5$/involutions. 0 vs 0 successes, $p = 1.000$, not significant [C-H-D1]. The supplementary paired permutation test gave $p = 0.145$ (bootstrap CI 0.99-1.03), so the project criterion was not met [C-H-D1].
- **D2:** hh2 vs hh1 on $A_5$/all, testing two factors for $A_5$/all. 0 vs 0, $p = 1.000$, not significant [C-H-D2]. Supplementary $p = 0.946$; criterion not met [C-H-D2].
- **D3:** hh1 on $\mathbb{Z}_2^3$ vs $\mathbb{Z}_3$. 1 vs 0, adjusted $p = 1.000$, not significant; BH over all 12 tests gives 0.857 [C-H-D3]. The supplementary paired permutation test ($p$ = 5.0e-05, accuracy ratio 1.98) met the project criterion [C-H-D3].
- **D4:** hh1 on $S_5$/transpositions vs $S_5$/all. 20 vs 0, significant [C-H-D4].
- **D5:** hh1 on $\mathbb{Z}_2$ vs $\mathbb{Z}_3$. 18 vs 0, significant [C-H-D5].
- **D6:** diag_pm on $\mathbb{Z}_2^3$ vs $\mathbb{Z}_3$. 20 vs 0, significant [C-H-D6].

The tests that separate our predictor from the representation baselines are D1–D3, and none of them was significant [C-H-D1][C-H-D2][C-H-D3]. D4–D6 do not separate them:
- In D4 the permutation representation costs 1 against 4, and in D5 1 against 2. This is the same split as $h^*$ [C-T-S5-transpositions][C-T-S5-all][C-T-Z2-all][C-T-Z3-all].
- D6 tests a diagonal family. Its prediction follows from Lemma L5 and agrees with prior theorems on diagonal SSMs [C-L5].

D5 needs a further caveat. Its 18 successes come from the MPS run, for which only the success count survives, so no paired test is possible [C-G-hh1-Z2-all]. The CPU replication of the same cell gave 0 of 20 [C-H-replication]. With the CPU run, D5 would compare 0 with 0 successes [C-H-replication]. H-EX1 therefore gives no evidence for our predictor over the representation baselines. The criterion "all six discriminating tests significant" was not met [C-H-gates].

**Controls.** The three random-target negative controls (hh4 and LSTM on $S_5$, hh2 on $A_5$) each had 0 successes [C-H-NC-hh4-S5][C-H-NC-lstm-S5][C-H-NC-hh2-A5]. The negative-control criterion held, but H-EX1 as a whole failed [C-H-gates]. The LSTM positive control failed on the $A_5$ and $S_5$ tasks [C-H-exploratory].

**Exploratory analysis (post hoc, not preregistered).** We restricted the comparison to the 5 tasks where the LSTM succeeded [C-H-exploratory]. There, our predictor, the permutation law and the faithful-only predictor each matched 26 of 30 cells [C-H-exploratory]. The other baselines matched 16 or fewer [C-H-exploratory]. On the remaining tasks, the cells mainly measure the training budget [C-H-exploratory].

**Device sensitivity.** Because of a runner bug, the same protocol and seeds were run once on the MPS GPU and once on the CPU. For hh1 on $\mathbb{Z}_2$/all, 18 of 20 seeds succeeded on MPS and 0 of 20 on CPU [C-H-replication]. Training outcomes can depend strongly on floating-point details of the device [C-H-replication].

### H-EX2 addendum: the generator formats of prior work

**Protocol.** The addendum was preregistered before its runs [C-X-protocol]:
- *Tasks:* $S_4$/tn and $A_5$/c3c5.
- *Architectures:* hh1, hh2 and hh3, with 20 seeds each [C-X-protocol].
- *Setup:* the H-EX1 protocol, run on the MPS GPU.
- *Predictions:* we predicted that hh1 fails while hh2 and hh3 succeed. The permutation law predicts that $S_4$/tn needs 3 factors and $A_5$/c3c5 needs 4.

There is a device confound. H-EX2 ran entirely on MPS, whereas most H-EX1 cells for hh2–hh4 ran on the CPU, and the device changed outcomes in the replication [C-X-protocol][C-H-replication]. Table 4 and Figure 3 show the results.

**Outcomes.** Successful seeds, with the 7x-8x outcome in parentheses [C-X-hh2-A5-c3c5]:
- hh1 on $A_5$/c3c5: 0 of 20 (0 of 20) [C-X-hh1-A5-c3c5].
- hh2 on $A_5$/c3c5: 18 of 20 (18 of 20) [C-X-hh2-A5-c3c5].
- hh3 on $A_5$/c3c5: 18 of 20 (10 of 20) [C-X-hh3-A5-c3c5].
- hh1 on $S_4$/tn: 0 of 20 (0 of 20) [C-X-hh1-S4-tn].
- hh2 on $S_4$/tn: 6 of 20 (4 of 20) [C-X-hh2-S4-tn]. This is a failure, contrary to our prediction [C-X-hh2-S4-tn].
- hh3 on $S_4$/tn: 19 of 20 (3 of 20) [C-X-hh3-S4-tn].

E1 and E3 (on $A_5$) and E2 (on $S_4$) are significant after correction [C-X-E1][C-X-E2][C-X-E3]. Our predictor matched 5 of 6 cells and the permutation law 4 of 6 [C-X-result]. The preregistered success criterion of H-EX2 was not met [C-X-result].

**What H-EX2 supports and what it does not.**
- *Supported:* the necessity claim of the permutation law fails for $A_5$/c3c5, because under our protocol and readout two factors learn this format [C-X-hh2-A5-c3c5][C-lit-howe-law-body]. This agrees with DeltaProduct's observation [C-lit-deltaproduct-body]. Howe's law was stated without the additive input pathway [C-lit-howe], so this is a test under a different architecture variant, not a direct refutation.
- *Not supported:* that two factors are learnable for $S_4$/tn, where hh2 failed [C-X-hh2-S4-tn].
- *Scope:* our predictor is a sufficiency statement about exact expressivity [C-thm1]. H-EX2 tests it against a necessity claim of prior work, under one protocol, one device and our readout [C-X-protocol].

## The agentic lab and the verification pipeline

**Agents.** The lab had six components [C-lab]:
- a literature scout, whose quotes were checked by code;
- an integrator;
- a cascade of four researcher agents;
- an exact verifier;
- a red-team agent;
- a preregistration for each round.

**Runs and outcomes.** The lab ran 15 rounds at a cost of 10.51 USD [C-lab].
- 9 rounds produced an accepted claim [C-lab]. All 9 survive re-checking with the hardened verifier, and 0 were withdrawn [C-lab].
- 6 rounds produced a negative result: no claim passed the verifier and the consistency rule [C-lab][C-neg1][C-neg2][C-neg3][C-neg4][C-neg5][C-neg6].

The rounds on $Q_8$, $A_5$ with involutions, and $\mathbb{Z}_2^2$ carry the status "contested by red-team counter-check" [C-expressivity-R4][C-expressivity-R6][C-expressivity-R8]. "Contested" means the red team disputed the round in a counter-check. "Withdrawn" would mean the verified sentence failed re-checking, which happened for no round [C-lab]. The certified $h^*(A_5,\text{all}) = 2$ from the fifth round rests on the hand-proved L2 for its lower bound [C-expressivity-R5].

We did not inspect the agents' own interpretations, and they are not results. Several are inconsistent with the hardened consistency rule. For example, one interpretation reads "$> 1$" for $A_5$ with involutions [C-expressivity-R3-I], which contradicts the certified value $1$ [C-T-A5-involutions]. The scout kept 60 literature findings whose verbatim quote was found by code in the abstract [C-lab].

**Loophole found and closed.** In round one, an agent answered that one reflection is not enough for $A_5$ with involution inputs. It supported this with two true but weaker checks, while the verifier had itself found a certificate with $k = 1$ [C-loophole1]. The consistency rule now requires an impossibility certificate for negative answers and exact-value checks for numbers [C-loophole1].

**Verifier.** The verifier passed a mandatory self-test of 46 known true and known false claims [C-verifier]. These include near-boundary cases and a regression case for every red-team bug [C-verifier].

**Red team.** The red team found three bugs [C-redteam]:
1. The group names S1, D1 and D2 denoted the wrong groups.
2. The published $h^*$ sentence omitted the finite-state hypothesis.
3. The consistency rule accepted unchecked numbers in answer texts.

All three were fixed and became regression cases [C-redteam]. The red team also re-checked the exact core [C-redteam]:
- 189 library constructions [C-redteam];
- 15556 exhaustive explicit-matrix claims, against an independent re-implementation [C-redteam];
- the character tables of all 319 SmallGroups, against GAP [C-redteam].

All of these checks gave 0 disagreements [C-redteam]. The theory red team found the open-$\beta$ corollary and the complex-state remark [C-open-beta][C-complex].

## Limitations and open questions

- **Hypotheses of the law.** The law assumes finitely many reachable states, token-local transitions without short convolution, and one layer [C-thm1]. Its necessity half rests on a hand proof [C-L2].
- **Real states.** A complex realisation only gives $h^* \le 2k$ [C-complex].
- **Multi-layer models.** For diagonal SSMs, the number of layers needed is tied to subnormal series [C-lit-shakerinava]. A multi-layer analogue of $h^*$ for Householder products is an open question.
- **Exact arithmetic versus floating point.** The theory is exact [C-L3], while prior analyses work at finite precision [C-lit-grazzi][C-lit-deltaproduct]. Our training outcomes are device-sensitive [C-H-replication].
- **Open parameterisations.** With $\beta \in [0, 2)$, or with open intervals for diagonal entries, only approximation is possible [C-open-beta].
- **Remaining open values.**
  - $Q_8$: certified bounds $[2,3]$; the lower bound $3$ is only a hand argument [C-T-Q8-all][C-T-Q8-cover][C-Q8-lower].
  - $S_5$: the value $4$ rests on hand steps [C-S5][C-S5-hand3].
  - Most non-abelian groups in the atlas remain undetermined [C-atlas].
- **Chain of thought and padding.** Prior work shows that intermediate generation increases expressive power [C-lit-cot][C-lit-li-cot]. Whether intermediate tokens act as an additional Householder budget per input symbol is an open question that we have not tested.
- **Learnability.** The theory predicts exact expressivity, not learnability. On our grid, the representation baselines predicted training outcomes at least as well as our predictor [C-H-accuracy][C-H-gates].

![Figure 1. Preregistered grid: number of seeds (out of 20) whose accuracy on positions 257-512 is at least 0.9, with the outcome predicted by the algebraic law (+ success, − failure, ? undetermined). Table 2 is the table view. Claims [C-G-*].](fig_grid.png)

*Figure 1. Preregistered grid: number of seeds (out of 20) whose accuracy on positions 257-512 is at least 0.9, with the outcome predicted by the algebraic law (+ success, − failure, ? undetermined). Table 2 is the table view. Claims [C-G-*].*


![Figure 3. Preregistered addendum H-EX2 on the generator formats of the closest prior work: successful seeds (of 20) for one, two and three Householder factors per token; solid line: minimum predicted by our law (h* = 2, certified); dotted line: the permutation-representation law (3 for S4, 4 for A5); dashed line: the cell-success threshold of 10 seeds. Evidence: claims C-X-(model)-(task) and C-X-E1 to C-X-E3, listed in Appendix C.](fig_hex2.png)

*Figure 3. Preregistered addendum H-EX2 on the generator formats of the closest prior work: successful seeds (of 20) for one, two and three Householder factors per token; solid line: minimum predicted by our law (h* = 2, certified); dotted line: the permutation-representation law (3 for S4, 4 for A5); dashed line: the cell-success threshold of 10 seeds. Evidence: claims C-X-(model)-(task) and C-X-E1 to C-X-E3, listed in Appendix C.*


![Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h against group order (dot area = number of groups with that order and h). The only non-solvable group, A5, sits at the minimum value 2 while most solvable groups need more. Claims [C-atlas-monotone], [C-atlas-nonsolvable].](fig_atlas.png)

*Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h against group order (dot area = number of groups with that order and h). The only non-solvable group, A5, sits at the minimum value 2 while most solvable groups need more. Claims [C-atlas-monotone], [C-atlas-nonsolvable].*


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
| Q8 | all | 8 | yes | 2 | 3 | cover C4:C4 (explorer) | 16 | 4 | 4 | 6 |
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
| Z2/all | 0 - | 18 + | 18 + | 3 + | 20 + | 6 + | 20 + |
| Z3/all | 0 - | 0 - | 0 - | 10 + | 6 + | 12 + | 19 + |
| Z2^3/all | 0 - | 20 + | 1 + | 20 + | 20 + | 20 + | 20 + |
| S3/transpositions | 0 - | 0 - | 20 + | 10 + | 19 + | 18 + | 20 + |
| S3/all | 0 - | 0 - | 0 - | 19 + | 20 + | 19 + | 20 + |
| A5/involutions | 0 - | 0 - | 0 + | 0 + | 20 + | 20 + | 0 + |
| A5/all | 0 - | 0 - | 0 - | 0 + | 0 + | 0 + | 0 + |
| S5/transpositions | 0 - | 0 - | 20 + | 19 + | 20 + | 19 + | 8 + |
| S5/all | 0 - | 0 - | 0 - | 0 ? | 0 ? | 0 + | 0 + |

**Table 4.** Preregistered addendum H-EX2: the generator formats of the closest prior work. Successful seeds of 20 at 2x-4x (7x-8x); predicted outcome by our law (h* = 2 for both tasks) and by the permutation-representation law. Claims [C-X-*].

| task | model | seeds 2x-4x | seeds 7x-8x | ours | permutation law |
|---|---|---|---|---|---|
| A5/c3c5 | hh1 | 0 | 0 | failure | failure |
| A5/c3c5 | hh2 | 18 | 18 | success | failure |
| A5/c3c5 | hh3 | 18 | 10 | success | failure |
| S4/tn | hh1 | 0 | 0 | failure | failure |
| S4/tn | hh2 | 6 | 4 | success | failure |
| S4/tn | hh3 | 19 | 3 | success | success |

**Table 3.** Atlas, all 319 groups of order <= 63, full alphabet. Claims [C-atlas*].

| class | groups | h* exact | faithful h = 2 | faithful h >= 3 |
|---|---|---|---|---|
| trivial | 1 | 1 | 0 | 0 |
| abelian (nontrivial) | 105 | 105 | 62 | 42 |
| solvable non-abelian | 212 | 31 | 31 | 181 |
| non-solvable | 1 | 1 | 1 | 0 |

---
Verification log: 137 claims cited, correction rounds [{"round": 0, "violations": 44}, {"round": 1, "violations": 0}, {"final_removed": 0}], 0 unsupported sentences removed, errata applied after the gate: [], remaining violations: 0. Tables and figures are generated by code from expressivity/results/.
