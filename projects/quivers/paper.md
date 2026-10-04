# Indecomposable representations of non-Dynkin quivers: stars, cycles and Kac polynomials

Verifier-Gated Discovery Lab, Hack-Nation, Challenge 3

# Indecomposable representations of non-Dynkin quivers: stars, cycles and Kac polynomials

**Author:** noah@schittenhelm.dev

## Abstract

We study indecomposable representations of quivers that are not of Dynkin type, with emphasis on star quivers (a centre with leaves attached, no edges between leaves) and on 3-cycles and 4-cycles, and we try to describe the infinitely many indecomposables. A verifier-gated computational lab checked every claim below with exact arithmetic. For the stars we confirm the classification of Tits types [C-quivers-R1-4, C-quivers-R1-5], the four-subspace problem with its one-parameter family of bricks [C-quivers-R2-19], and a counting formula for $\alpha_n$ (Theorem 1, proof in the companion ledger). For the cycles we report Kac-polynomial counts independent of orientation and a classification of the oriented cycle (Theorem 2, proof in the companion ledger). The results reproduce classical facts; the contribution is their exact computational certification and an honest account of what is and is not certified.

## 1 Introduction

**Question.** Gabriel's theorem [C-lit1] describes quivers with finitely many indecomposables. What happens beyond the Dynkin case? We examine stars and cycles and ask for dimension vectors, parameter counts, explicit families and counts over $\mathbb F_q$.

**Contribution.** Every statement in the results sections is a typed claim decided by an exact code verifier [C-methode]. We distinguish certified instances from general proofs that are written but not machine-checked.

**Results.**

- The Tits forms of star1, star2, star3 are positive definite, that of star4 is semidefinite, and those of star5, star6, star7 are indefinite [C-quivers-R1-1, C-quivers-R1-2, C-quivers-R1-3, C-quivers-R1-4, C-quivers-R1-5, C-quivers-R1-6, C-quivers-R1-7].
- star3 has exactly twelve positive roots [C-quivers-R1-11]. Exhaustive counts over $\mathbb F_2$ and $\mathbb F_3$ confirm Gabriel's picture [C-quivers-R1-12, C-quivers-R1-13].
- For star4 the number of absolutely indecomposables with dimension vector $\delta$ is $q+4$ [C-quivers-R2-18]. Complete lists over $\mathbb F_2$, $\mathbb F_3$, $\mathbb F_5$ are certified [C-quivers-R2-20, C-quivers-R2-21, C-quivers-R2-22].
- The family $V_t$ of four lines consists of pairwise non-isomorphic bricks [C-quivers-R2-19].
- Theorem 1: a closed formula for $A_{\alpha_n}(q)$ [C-quivers-R6-77, C-quivers-R3-36]. Certified instances: [C-quivers-R6-77, C-quivers-R6-78, C-quivers-R6-79, C-quivers-R6-80, C-quivers-R6-81, C-quivers-R6-82, C-quivers-R3-35, C-quivers-R3-36, C-quivers-R3-37, C-quivers-R3-38, C-quivers-R3-39].
- Wild stars: the parameter number grows [C-quivers-R3-29, C-quivers-R3-30, C-quivers-R3-31, C-quivers-R3-32].
- Cycles: $A_\delta(q)$ equals $q+2$ for the 3-cycle and $q+3$ for the 4-cycle in every orientation tested [C-quivers-R4-45, C-quivers-R4-48, C-quivers-R4-51, C-quivers-R4-54, C-quivers-R4-57]. Theorem 2 classifies the oriented cycle, with exhaustive checks [C-quivers-R4-63, C-quivers-R4-64, C-quivers-R4-65].
- Counts for $2\delta$ are given below [C-quivers-R5-67, C-quivers-R5-68, C-quivers-R5-69, C-quivers-R5-73, C-quivers-R5-74].

## 2 Definitions

We use the following standard conventions; they are not lab claims. A quiver is $Q=(Q_0,Q_1,s,t)$. A representation $V$ assigns a vector space $V_i$ to each vertex $i$ and a linear map $V_a:V_{s(a)}\to V_{t(a)}$ to each arrow $a$. Morphisms are families of linear maps commuting with the arrow maps. Direct sums and indecomposability are defined as usual. Krull–Schmidt holds, so decompositions into indecomposables are unique up to isomorphism. The dimension vector is $\dim V\in\mathbb N^{Q_0}$. The Tits form is
$$q(x)=\sum_i x_i^2-\sum_{a\in Q_1}x_{s(a)}x_{t(a)}.$$
Real and imaginary roots, the parameter number $1-q(\alpha)$ and the count $A_\alpha(q)$ of absolutely indecomposable representations over $\mathbb F_q$ are as in Kac [C-lit3, C-lit4].

## 3 Gabriel's theorem and the lab's confirmation

Gabriel: a connected quiver has finitely many isoclasses of indecomposables iff its underlying graph is Dynkin of type A, D, E; the indecomposables then correspond bijectively to positive roots via the dimension vector [C-lit1]. A proof via reflection (Coxeter) functors is due to Bernstein–Gelfand–Ponomarev [C-lit2].

**Proposition (computed_rigorous), Tits types.** The Tits forms of star1, star2 and star3 are positive definite (exact leading principal minors) [C-quivers-R1-1, C-quivers-R1-2, C-quivers-R1-3]. The Tits form of star4 is positive semidefinite, not definite [C-quivers-R1-4]. The Tits forms of star5, star6 and star7 are indefinite [C-quivers-R1-5, C-quivers-R1-6, C-quivers-R1-7]. The red-team counter-checks (tame resp. finite type) failed in each case [C-quivers-R1-1-RT1, C-quivers-R1-4-RT1, C-quivers-R1-5-RT1].

**Proposition (computed_rigorous), roots of D4.** star3 has exactly twelve positive roots, obtained as the Weyl-group orbit of the simple roots [C-quivers-R1-11].

**Proposition (computed_rigorous), exhaustive counts.** Over $\mathbb F_2$ and over $\mathbb F_3$, for all dimension vectors $0<\beta\le[2, 1, 1, 1]$ of star3, there is exactly one indecomposable for each real root and none for non-roots [C-quivers-R1-12, C-quivers-R1-13]. The same holds for A3 over $\mathbb F_2$ for all $0<\beta\le[2, 2, 2]$ [C-quivers-R1-14].

## 4 Beyond Dynkin

Kac: over an algebraically closed field, the dimension vectors of indecomposables are exactly the positive roots. Real roots carry exactly one indecomposable, imaginary roots infinitely many, with $1-q(\alpha)$ parameters [C-lit3]. $A_\alpha(q)$ is a monic integer polynomial in $q$ of degree $1-q(\alpha)$, independent of the orientation [C-lit4]. Hua gives a counting formula [C-lit7], and the coefficients are non-negative [C-lit8]. Nazarova classified the indecomposables of the Euclidean quivers, which are exactly the tame ones [C-lit5]. By Ringel their regular indecomposables fall into tubes parametrised by $\mathbb P^1$, with finitely many exceptional tubes [C-lit6]. All other connected quivers are wild.

**Proposition (computed_rigorous).** The Tits forms of kronecker, cycle3_oriented and cycle4_oriented are positive semidefinite, not definite [C-quivers-R1-8, C-quivers-R1-9, C-quivers-R1-10].

## 5 Star quivers

### 5a The four-subspace problem

**Proposition (computed_rigorous).** The radical of the Tits form of star4 is one-dimensional, generated by $\delta=[2, 1, 1, 1, 1]$ [C-quivers-R2-15]. This $\delta$ is an imaginary root with $1-q(\delta)$ equal to $1$, as is $[4, 2, 2, 2, 2]$ [C-quivers-R2-16, C-quivers-R2-17].

**Proposition (computed_rigorous), Kac polynomial.** The count of absolutely indecomposables is a Kac polynomial, certified at several primes [C-quivers-R2-18]:
$$A_\delta(q)=q+4 \qquad [\text{C-quivers-R2-18}]$$

**Proposition (computed_rigorous), the family $V_t$.** The four lines $(1, 0)$, $(0, 1)$, $(1, 1)$, $(1, t)$ in $k^2$ define a representation $V_t$ with dimension vector $\delta$ [C-quivers-R2-19]. For every $t$ we have $\mathrm{End}(V_t)=k$ (a brick, absolutely indecomposable) and $\mathrm{Hom}(V_s,V_t)=0$ for $s\ne t$, so the $V_t$ are pairwise non-isomorphic [C-quivers-R2-19]. The certificate is elimination over $\mathbb Q(s,t)$ with logged pivots [C-quivers-R2-19].

**Proposition (computed_rigorous), complete lists.** Over $\mathbb F_2$, $\mathbb F_3$ and $\mathbb F_5$ the given lists of isoclasses of indecomposables with dimension vector $\delta$ are complete, with $6$, $7$ and $9$ members respectively [C-quivers-R2-20, C-quivers-R2-21, C-quivers-R2-22]. Dropping the last element makes each list incomplete [C-quivers-R2-20-RT1, C-quivers-R2-21-RT1, C-quivers-R2-22-RT1].

**Interpretation (uncertified).** The agent's description is that each list consists of the members $V_t$ together with six configurations in which exactly one pair of lines coincides [C-quivers-R2-20-I, C-quivers-R2-21-I, C-quivers-R2-22-I]. This description is a hypothesis, not a verified result. What is certified is the completeness of the lists [C-quivers-R2-20, C-quivers-R2-21, C-quivers-R2-22] and that a configuration with two pairs of coinciding lines is decomposable [C-quivers-R2-26]. We conjecture that the extra classes sit at the degenerate cross ratios and correspond to exceptional tubes of Ringel's description [C-lit6]. This matching is not certified.

**Proposition (computed_rigorous), real roots.** The following are absolutely indecomposable:
- the representation of $[1, 1, 1, 1, 1]$ with all maps $[[1]]$ [C-quivers-R2-23];
- the representation of $[3, 1, 1, 1, 1]$ with maps $[[1], [0], [0]]$, $[[0], [1], [0]]$, $[[0], [0], [1]]$, $[[1], [1], [1]]$ [C-quivers-R2-24];
- the representation of $[2, 2, 1, 1, 1]$ with maps $[[1, 0], [0, 1]]$, $[[1], [0]]$, $[[0], [1]]$, $[[1], [1]]$ [C-quivers-R2-25].

**Proposition (computed_rigorous).** For star4 over $\mathbb F_2$ and $\mathbb F_3$ and all $0<\beta\le[3, 1, 1, 1, 1]$, each real root carries exactly one indecomposable and non-roots carry none [C-quivers-R2-27, C-quivers-R2-28]. The only imaginary root in this range has $6$ resp. $7$ indecomposables [C-quivers-R2-27, C-quivers-R2-28].

### 5b Classification for $\alpha_n$

**Theorem 1 (proof in the companion ledger results.tex).** A representation of the star with dimension vector $\alpha_n=(2;1^n)$ is a tuple of vectors in $k^2$. It is indecomposable iff all vectors are non-zero and they span at least three distinct lines. Such representations are bricks, and their isoclasses are $\mathrm{PGL}_2$-orbits of point configurations in $\mathbb P^1$ with at least three distinct points. Counting gives
$$A_{\alpha_n}(q)=\frac{(q+1)^{n-1} - 1 - (2^{n-1} - 1)\,q}{q\,(q-1)}\qquad [\text{C-quivers-R6-77, C-quivers-R3-36}]$$
of degree $1-q(\alpha_n)$, i.e. the parameter number of the imaginary root $\alpha_n$ [C-quivers-R2-16, C-quivers-R3-29, C-quivers-R3-30, C-quivers-R3-31, C-quivers-R3-32].

*Evidence.* The general proof is a written proof in the ledger, not machine-checked. The instances below are computed_rigorous.

*Proof sketch.* Zero vectors split off a simple summand. If the vectors span fewer than three distinct lines, the centre splits. With three distinct lines, an endomorphism has eigenvectors along each of them and is therefore scalar. $\mathrm{PGL}_2$ acts freely on configurations with at least three distinct points. One counts configurations and divides by $|\mathrm{PGL}_2(\mathbb F_q)|$.

**Proposition (computed_rigorous), exhaustive verification of the criterion.** All representations were enumerated, and no deviation from the criterion was found:
- star4: $256$ representations over $\mathbb F_2$, $6$ isoclasses; $6561$ over $\mathbb F_3$, $7$ isoclasses [C-quivers-R6-77, C-quivers-R6-78].
- star5: $1024$ over $\mathbb F_2$, $25$ isoclasses; $59049$ over $\mathbb F_3$, $35$ isoclasses [C-quivers-R6-79, C-quivers-R6-80].
- star6 over $\mathbb F_2$: $4096$ representations, $90$ isoclasses [C-quivers-R6-81].
- star7 over $\mathbb F_2$: $16384$ representations, $301$ isoclasses [C-quivers-R6-82].

**Proposition (computed_rigorous), Kac polynomials.** The counts agree with the formula of Theorem 1 at $\deg + 2$ primes [C-quivers-R3-35, C-quivers-R3-36, C-quivers-R3-37, C-quivers-R3-38, C-quivers-R3-39]:
- star4: $((q+1)^3 - 1 - 7q)/(q(q-1))$ [C-quivers-R3-35].
- star5: $((q+1)^4 - 1 - 15q)/(q(q-1))$ [C-quivers-R3-36].
- star6: $((q+1)^5 - 1 - 31q)/(q(q-1))$ [C-quivers-R3-37].
- star7: $((q+1)^6 - 1 - 63q)/(q(q-1))$ [C-quivers-R3-38].
- star8: $((q+1)^7 - 1 - 127q)/(q(q-1))$ [C-quivers-R3-39].

Shifting the constant by one fails [C-quivers-R3-35-RT1, C-quivers-R3-36-RT1]. By Kac's theorem a polynomial of the stated degree is determined by finitely many values [C-lit4].

### 5c Wild stars

**Proposition (computed_rigorous).** For star5, star6, star7, star8 the vector $(2;1^n)$ is an imaginary root with parameter number $2$, $3$, $4$, $5$ respectively [C-quivers-R3-29, C-quivers-R3-30, C-quivers-R3-31, C-quivers-R3-32]. For star5 the vectors $[4, 2, 2, 2, 2, 2]$ and $[6, 3, 3, 3, 3, 3]$ are imaginary roots with parameter numbers $5$ and $10$ [C-quivers-R3-33, C-quivers-R3-34]. The parameter number is therefore unbounded.

**Proposition (computed_rigorous), slices of a two-parameter family.** For star5 with the lines $(1, 0)$, $(0, 1)$, $(1, 1)$, $(1, s)$, $(1, t)$ [C-quivers-R3-41], the slices $s=2$, $s=3$, $s=-1$ give one-parameter families $V_t$ of pairwise non-isomorphic bricks [C-quivers-R3-41, C-quivers-R3-42, C-quivers-R3-43]. Elimination over $\mathbb Q(s,t)$ certifies $\mathrm{End}(V_t)=k$ and $\mathrm{Hom}(V_s,V_t)=0$ for $s\ne t$ [C-quivers-R3-41].

**Proposition (computed_rigorous).** Over $\mathbb F_2$ the given list of $25$ representations of star5 with dimension vector $[2, 1, 1, 1, 1, 1]$ is complete [C-quivers-R3-40].

## 6 Cycles

**Proposition (computed_rigorous), radicals.** For cycle3_oriented and cycle3_acyclic the radical of the Tits form is generated by $\delta=[1, 1, 1]$ [C-quivers-R4-44, C-quivers-R4-47]. For cycle4_oriented, cycle4_acyclic31 and cycle4_acyclic22 it is generated by $\delta=[1, 1, 1, 1]$ [C-quivers-R4-50, C-quivers-R4-53, C-quivers-R4-56].

**Proposition (computed_rigorous), orientation independence.** The Kac polynomial is independent of orientation in every case tested:
$$A_\delta(q)=q+2\ \text{(3-cycle, oriented and acyclic)}\qquad [\text{C-quivers-R4-45, C-quivers-R4-48}]$$
$$A_\delta(q)=q+3\ \text{(4-cycle, all three orientations)}\qquad [\text{C-quivers-R4-51, C-quivers-R4-54, C-quivers-R4-57}]$$
The alternative $q+n-2$ is refuted [C-quivers-R4-45-RT1, C-quivers-R4-51-RT1]. Over $\mathbb F_3$ the lists of $5$ (3-cycle) and $6$ (4-cycle) indecomposables are complete [C-quivers-R4-46, C-quivers-R4-49, C-quivers-R4-52, C-quivers-R4-55, C-quivers-R4-58].

**Proposition (computed_rigorous), families.** On cycle3_oriented the family with arrow maps $[[1]]$, $[[1]]$, $[[t]]$, $t\neq0$, consists of pairwise non-isomorphic bricks [C-quivers-R4-59]. The analogous family $[[1]]$, $[[1]]$, $[[1]]$, $[[t]]$ on cycle4_acyclic22 does too [C-quivers-R4-60].

**Theorem 2 (proof in the companion ledger results.tex).** For the oriented cycle the indecomposables are the nilpotent strings $S(i,l)$ and the bands, i.e. representations with all spaces $k^m$, all but the last arrow the identity, and the last arrow an invertible indecomposable matrix (a Jordan block or a companion matrix) [C-quivers-R4-63, C-quivers-R4-64, C-quivers-R4-65].

*Evidence.* The general proof is a written proof in the ledger, not machine-checked. The instances are computed_rigorous.

*Proof sketch.* Fitting's lemma for the composite around the cycle splits $V$ into a nilpotent and an invertible part, compatible with the arrows. After making all but one arrow the identity, the invertible part is a $k[x,x^{-1}]$-module. The nilpotent part is a module over a Nakayama algebra, whose indecomposables are uniserial strings.

**Proposition (computed_rigorous), instances.** A Jordan-block band on cycle4_oriented with dimension vector $[3, 3, 3, 3]$ and last arrow $[[2, 1, 0], [0, 2, 1], [0, 0, 2]]$ is absolutely indecomposable [C-quivers-R4-61]. A string on cycle3_oriented with dimension vector $[2, 2, 1]$ and maps $[[1, 0], [0, 1]]$, $[[1, 0]]$, $[[0], [1]]$ is absolutely indecomposable [C-quivers-R4-62]. Exhaustive counts agree with the classification (strings plus modules over $\mathbb F_q[x,x^{-1}]$ for $\beta=m\delta$) in the following cases:
- cycle3_oriented over $\mathbb F_2$ and $\mathbb F_3$ for all $0<\beta\le[2, 2, 2]$ [C-quivers-R4-63, C-quivers-R4-64];
- cycle4_oriented over $\mathbb F_2$ for all $0<\beta\le[2, 2, 2, 2]$ [C-quivers-R4-65].

For cycle3_acyclic over $\mathbb F_2$ and $0<\beta\le[2, 2, 2]$ each real root carries exactly one indecomposable and non-roots carry none [C-quivers-R4-66].

*Acyclic orientations.* They have the same $A_\delta$ as shown above, consistent with orientation independence [C-lit4]. By Ringel the regular indecomposables of Euclidean type lie in tubes, with exceptional tubes of ranks determined by the arm lengths of the orientation [C-lit6]; this is literature, not certified here.

## 7 Multiples of $\delta$

**Proposition (computed_rigorous).** The number of isoclasses of indecomposables with dimension vector $2\delta$ is:
- cycle3_oriented: $5$, $8$, $17$ over $\mathbb F_2$, $\mathbb F_3$, $\mathbb F_5$ [C-quivers-R5-67, C-quivers-R5-68, C-quivers-R5-69];
- cycle3_acyclic: $5$, $8$, $17$ over $\mathbb F_2$, $\mathbb F_3$, $\mathbb F_5$ [C-quivers-R5-70, C-quivers-R5-71, C-quivers-R5-72];
- cycle4_oriented: $6$, $9$ over $\mathbb F_2$, $\mathbb F_3$ [C-quivers-R5-73, C-quivers-R5-74];
- cycle4_acyclic22: $6$, $9$ over $\mathbb F_2$, $\mathbb F_3$ [C-quivers-R5-75, C-quivers-R5-76].

**Numerical observation (uncertified interpretation).** The agent's reading is that these counts equal $A_\delta(q)+(A_\delta(q^2)-A_\delta(q))/2$ with $A_{2\delta}=A_\delta$ at the tested $q$ [C-quivers-R5-67-I, C-quivers-R5-68-I, C-quivers-R5-69-I, C-quivers-R5-73-I]. The counts themselves are certified; the interpretation was not decided by the verifier.

## 8 Method: the verifier-gated lab

The pipeline consisted of preregistration, typed claims, an exact code verifier, and red-team counter-checks. The lab ran $6$ rounds with $82$ verified statements and $0$ negative results, each round preregistered before the experiment (prereg.md) [C-methode].

**Factual correction regarding agents.** No autonomous researcher agents ran in this project. The questions and the typed claims were proposed by the human-directed Claude Code session, strictly following the preregistration (projects/quivers/run_lab.py). The exact code verifier decided every claim. The only LLM agent in the pipeline is the writer of this paper, whose output passes a hallucination gate that checks citations of claim ids.

The verifier works with exact arithmetic: leading principal minors for Tits types, orbit computation for roots, elimination over $\mathbb Q(s,t)$ with logged pivots for bricks, and direct enumeration or Burnside counting for isoclass numbers [C-quivers-R1-1, C-quivers-R2-19, C-quivers-R2-22]. Every claim has a red-team counter-check (an alternative statement that must fail), and all failed as intended. Statements marked as agent interpretations are not used as results and are flagged where they appear.

## 9 Negative results, red team, limitations

**Negative results.** No claim was refuted or contested [C-methode]. Each red-team counter-check, such as wrong constants, a wrong type, a missing list element, or an extra indecomposable, failed as expected, e.g. [C-quivers-R2-18-RT1, C-quivers-R3-36-RT1, C-quivers-R5-67-RT1].

**Limitations.**
- Theorems 1 and 2 are proved in the ledger but not machine-checked. Only finitely many instances are computer-verified [C-quivers-R6-77, C-quivers-R4-63].
- Kac polynomials are certified only at finitely many primes, combined with Kac's degree theorem [C-lit4, C-quivers-R3-39].
- The tube interpretation and the description of the six extra classes are uncertified [C-quivers-R2-20-I].
- The verifier's self-test and further details are not documented in the claim list and are not asserted here.
- The results on stars and cycles reproduce classical facts [C-lit1, C-lit3, C-lit5, C-lit6]. The lab certifies them computationally and does not claim new theory.

**Open questions.** Machine-check Theorems 1 and 2. Describe indecomposables for wild stars beyond $\alpha_n$, where the parameter number grows [C-quivers-R3-33, C-quivers-R3-34]. Prove $A_{2\delta}=A_\delta$ rather than observe it at tested $q$.

## References

- P. Gabriel, "Unzerlegbare Darstellungen I", doi:10.1007/BF01298413 [C-lit1].
- I. N. Bernstein, I. M. Gelfand, V. A. Ponomarev, "Coxeter functors and Gabriel's theorem", doi:10.1070/RM1973v028n02ABEH001526 [C-lit2].
- V. G. Kac, "Infinite root systems, representations of graphs and invariant theory", doi:10.1007/BF01403155 [C-lit3].
- V. G. Kac, "Root systems, representations of quivers and invariant theory", doi:10.1007/BFb0063236 [C-lit4].
- L. A. Nazarova, "Representations of quivers of infinite type", doi:10.1070/IM1973v007n04ABEH001975 [C-lit5].
- C. M. Ringel, "Tame Algebras and Integral Quadratic Forms", doi:10.1007/BFb0072870 [C-lit6].
- J. Hua, "Counting representations of quivers over finite fields", doi:10.1006/jabr.1999.8220 [C-lit7].
- T. Hausel, E. Letellier, F. Rodriguez-Villegas, "Positivity for Kac polynomials and DT-invariants of quivers", doi:10.4007/annals.2013.177.3.8 [C-lit8].

---
Prüfprotokoll: 110 Claims zitiert, Korrekturrunden [{"runde": 0, "verstoesse": 41}, {"runde": 1, "verstoesse": 1}, {"final_verstoesse_entfernt": 0}], 0 unbelegte Sätze entfernt, verbleibende Verstöße: 0.
