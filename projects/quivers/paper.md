# Indecomposable representations of non-Dynkin quivers: stars, cycles and Kac polynomials

Verifier-Gated Discovery Lab, Hack-Nation, Challenge 3

# Indecomposable representations of non-Dynkin quivers: stars, cycles and Kac polynomials

## Abstract

We study indecomposable representations of quivers that are not of Dynkin type. We concentrate on star quivers (a centre with n leaves, no edges between leaves) and on 3- and 4-cycles, oriented and acyclic. A verifier-gated agentic lab checked the Tits-form type of each quiver with exact principal minors. It confirmed Gabriel's theorem for D4 and A3 by exhaustive counts over small finite fields. For the four-subspace problem it certified a one-parameter family of pairwise non-isomorphic bricks and the complete lists of indecomposables for the dimension vector δ over F_2, F_3 and F_5. For wild stars it certified the growth of the parameter count 1 − q(α) and Kac polynomials for the dimension vectors (2;1^n) at several n. For cycles it certified the Kac polynomial of δ independently of the orientation, and it checked the classification of indecomposables in the oriented case against exhaustive counts. All results are computer-verified and reproduce classical facts. No claim was refuted.

## 1 Introduction

**Question.** For quivers outside the Dynkin list there are infinitely many isoclasses of indecomposable representations. We ask how to describe them: which dimension vectors occur, how many parameters appear, which explicit families exist, and how many there are over F_p.

**Contribution.** We collect exactly certified statements for stars and cycles and place them in the classical framework of Gabriel, Kac, Nazarova and Ringel [C-lit1][C-lit3][C-lit4][C-lit5][C-lit6].

**Summary of results.**

- Tits-form types: star1, star2 and star3 are positive definite, star4 is positive semidefinite, star5 to star7 are indefinite (wild), and the Kronecker quiver and the oriented 3- and 4-cycles are semidefinite (tame) [C-quivers-R1-1][C-quivers-R1-2][C-quivers-R1-3][C-quivers-R1-4][C-quivers-R1-5][C-quivers-R1-6][C-quivers-R1-7][C-quivers-R1-8][C-quivers-R1-9][C-quivers-R1-10].
- D4 = star3 has exactly 12 positive roots [C-quivers-R1-11], and the Gabriel count holds over F_2 and F_3 [C-quivers-R1-12][C-quivers-R1-13].
- Four-subspace problem: δ = [2, 1, 1, 1, 1] is an imaginary root with 1 − q(α) = 1 [C-quivers-R2-15][C-quivers-R2-16]. There is a certified family of pairwise non-isomorphic bricks [C-quivers-R2-19], complete lists over F_2, F_3 and F_5 [C-quivers-R2-20][C-quivers-R2-21][C-quivers-R2-22], and the Kac polynomial 4 q^0 + 1 q^1 [C-quivers-R2-18].
- Wild stars: for (2;1^n) the parameter count grows, with star5, star6, star7 and star8 giving 2, 3, 4, 5 [C-quivers-R3-29][C-quivers-R3-30][C-quivers-R3-31][C-quivers-R3-32]. Kac polynomials are certified for star4 up to star8 [C-quivers-R3-35][C-quivers-R3-36][C-quivers-R3-37][C-quivers-R3-38][C-quivers-R3-39].
- Cycles: δ spans the radical of the Tits form, the Kac polynomial of δ has the same form for all tested orientations [C-quivers-R4-45][C-quivers-R4-48][C-quivers-R4-51][C-quivers-R4-54][C-quivers-R4-57], and the classification of the oriented cycle is checked exhaustively in small dimension [C-quivers-R4-63][C-quivers-R4-64][C-quivers-R4-65].
- Counts for 2δ over F_2, F_3 and F_5 for the cycles [C-quivers-R5-67][C-quivers-R5-68][C-quivers-R5-69][C-quivers-R5-73][C-quivers-R5-74].

## 2 Model

Notation and definitions follow standard usage; only the roles they play in the cited claims matter here.

- A quiver is Q = (Q_0, Q_1, s, t). A representation assigns a vector space to each vertex and a linear map to each arrow, with morphisms, direct sums, indecomposables and dimension vectors in the usual sense. Krull–Schmidt holds.
- The Tits form is q(x) = Σ x_i² − Σ_a x_{s(a)} x_{t(a)}.
- Roots are real or imaginary. A real root has exactly one indecomposable and an imaginary root has infinitely many, with 1 − q(α) parameters [C-lit3].
- A_α(q) denotes the number of absolutely indecomposable representations over F_q. It is a monic polynomial with integer coefficients of degree 1 − q(α), independent of the orientation [C-lit4].
- Assumption: the lab's exact verifier works over Q, Q(t) and finite fields F_p. Absolute indecomposability is certified by dim End and the dimension of the radical J(End), and families are certified by elimination over Q(s,t) with logged pivots.

## 3 Method: the verifier-gated agentic lab

The lab ran 5 rounds and checked 76 statements, with 0 negative results; every round was preregistered before the experiment (prereg.md) [C-methode]. Each computed claim is paired with a red-team counter-check whose failure is recorded, for example "the type would be tame" or "the list is complete without its last element" [C-quivers-R1-1-RT1][C-quivers-R2-20-RT1]. Exact certificates are principal minors, radical computation, Kac reduction, direct counting and Burnside counting over F_p, and elimination with logged pivots [C-quivers-R2-19].

## 4 Results

Items are labelled Proposition (lettered A–P) when the evidence level is computed_rigorous. Literature claims are cited as such.

### 4.1 Gabriel's theorem and its confirmation

Literature: a connected quiver has finitely many indecomposable isoclasses iff its graph is of Dynkin type A, D, E, and then indecomposables correspond bijectively to positive roots [C-lit1]. A proof by reflection (Coxeter) functors is due to Bernstein–Gelfand–Ponomarev [C-lit2].

**Proposition A (computed_rigorous).** The Tits forms of star1, star2 and star3 are positive definite, by exact leading principal minors [C-quivers-R1-1][C-quivers-R1-2][C-quivers-R1-3]. star4 is positive semidefinite and not definite [C-quivers-R1-4]. star5, star6 and star7 are indefinite [C-quivers-R1-5][C-quivers-R1-6][C-quivers-R1-7].

**Proposition B (computed_rigorous).** star3 has exactly 12 positive roots [C-quivers-R1-11].

**Proposition C (computed_rigorous).** For star3 over F_2 and over F_3, and for all 0 < β ≤ [2, 1, 1, 1], there is exactly one indecomposable for real roots and none for non-roots [C-quivers-R1-12][C-quivers-R1-13]. The same holds for A3 over F_2 with β ≤ [2, 2, 2] [C-quivers-R1-14].

### 4.2 Beyond Dynkin

Literature: for every quiver and algebraically closed field, the dimension vectors of indecomposables are exactly the positive roots; real roots have one indecomposable and imaginary roots have infinitely many [C-lit3]. A_α(q) is a polynomial [C-lit4], with a counting formula [C-lit7] and non-negative coefficients [C-lit8]. The Euclidean quivers are exactly the tame ones, and their indecomposables are classified [C-lit5]. Their regular indecomposables fall into tubes parametrised by P^1, with finitely many exceptional tubes [C-lit6].

**Proposition D (computed_rigorous).** The Kronecker quiver, cycle3_oriented and cycle4_oriented have positive semidefinite, non-definite Tits form [C-quivers-R1-8][C-quivers-R1-9][C-quivers-R1-10].

### 4.3 Star quivers

**Four-subspace problem (star4).**

**Proposition E (computed_rigorous).** The radical of the Tits form of star4 is generated by δ = [2, 1, 1, 1, 1] [C-quivers-R2-15]. δ is an imaginary root with 1 − q(α) = 1 [C-quivers-R2-16], and so is [4, 2, 2, 2, 2] [C-quivers-R2-17].

*[entfernt: unbelegt — Zahl ohne Beleg]* The V_t are therefore pairwise non-isomorphic bricks, certified by elimination over Q(s, t) [C-quivers-R2-19].

**Proposition G (computed_rigorous).** The listed representations form a complete list of isoclasses of indecomposables with dimension vector [2, 1, 1, 1, 1] over F_2 (6 classes), F_3 (7 classes) and F_5 (9 classes) [C-quivers-R2-20][C-quivers-R2-21][C-quivers-R2-22]. For q = 2, 3, 5, 7, A_δ(q) = 4 q^0 + 1 q^1, which is the Kac polynomial [C-quivers-R2-18]. A representation with two pairs of coinciding lines is decomposable over the algebraic closure [C-quivers-R2-26].

**Proposition H (computed_rigorous).** Explicit absolutely indecomposable representations exist for the real roots [1, 1, 1, 1, 1], [3, 1, 1, 1, 1] and [2, 2, 1, 1, 1] [C-quivers-R2-23][C-quivers-R2-24][C-quivers-R2-25]. Over F_2 and F_3, for all β ≤ [3, 1, 1, 1, 1], real roots have exactly one indecomposable and non-roots have none [C-quivers-R2-27][C-quivers-R2-28].

*Interpretation (uncertified).* The extra classes with exactly one coinciding pair of lines presumably sit in the exceptional tubes of the Euclidean case [C-lit6]. The lab did not certify this.

**Dimension vectors (2;1^n).**

**Proposition I (computed_rigorous).** The Kac polynomial for star4 is ((q+1)**3 − 1 − 7*q)/(q*(q−1)) [C-quivers-R3-35]. The Kac polynomials for star5 to star8 are

- star5: ((q+1)**4 − 1 − 15*q)/(q*(q−1)) [C-quivers-R3-36];
- star6: ((q+1)**5 − 1 − 31*q)/(q*(q−1)) [C-quivers-R3-37];
- star7: ((q+1)**6 − 1 − 63*q)/(q*(q−1)) [C-quivers-R3-38];
- star8: ((q+1)**7 − 1 − 127*q)/(q*(q−1)) [C-quivers-R3-39].

Each is certified at deg + 2 primes, together with Kac's theorem that A_α is a polynomial of degree 1 − q(α) [C-lit4].

*Classification of (2;1^n).* The classification of the representations with dimension vector (2;1^n) as configurations of points in P^1, together with the closed formula in n, is derived in a companion ledger (results.tex). That derivation is not among the claims available here, so we do not state it as a theorem. The computer verification is Proposition I, and the closed formula in n is recorded only as an uncertified interpretation [C-quivers-R3-35-I].

### 4.4 Wild stars

**Proposition J (computed_rigorous).** For star5, star6, star7 and star8 the vector (2;1^n) is an imaginary root with 1 − q(α) = 2, 3, 4, 5 respectively [C-quivers-R3-29][C-quivers-R3-30][C-quivers-R3-31][C-quivers-R3-32]. For star5, [4, 2, 2, 2, 2, 2] has 1 − q(α) = 5 and [6, 3, 3, 3, 3, 3] has 1 − q(α) = 10 [C-quivers-R3-33][C-quivers-R3-34]. The parameter count is therefore unbounded along these sequences.

**Proposition K (computed_rigorous).** For star5, the slices of the two-parameter family at s = 2, s = 3 and s = −1 (maps as in the cited claims) consist of pairwise non-isomorphic bricks [C-quivers-R3-41][C-quivers-R3-42][C-quivers-R3-43]. Over F_2 the listed 25 representations with dimension vector [2, 1, 1, 1, 1, 1] are a complete list of isoclasses of indecomposables [C-quivers-R3-40].

### 4.5 Cycles

**Proposition L (computed_rigorous).** The radical of the Tits form is generated by δ = [1, 1, 1] for cycle3_oriented and cycle3_acyclic [C-quivers-R4-44][C-quivers-R4-47]. It is generated by δ = [1, 1, 1, 1] for cycle4_oriented, cycle4_acyclic31 and cycle4_acyclic22 [C-quivers-R4-50][C-quivers-R4-53][C-quivers-R4-56].

**Proposition M (computed_rigorous).** For q = 2, 3, 5, 7, A_δ(q) = 2 q^0 + 1 q^1 for both 3-cycles [C-quivers-R4-45][C-quivers-R4-48]. A_δ(q) = 3 q^0 + 1 q^1 for the three 4-cycles [C-quivers-R4-51][C-quivers-R4-54][C-quivers-R4-57]. The polynomial is thus the same for the orientations tested, as expected from [C-lit4]. Over F_3 the lists with dimension vector δ are complete: 5 classes for each 3-cycle and 6 classes for each 4-cycle [C-quivers-R4-46][C-quivers-R4-49][C-quivers-R4-52][C-quivers-R4-55][C-quivers-R4-58].

**Proposition N (computed_rigorous).** The family of the cited claims (all maps the identity except the last, which is t ≠ 0) consists of pairwise non-isomorphic bricks on cycle3_oriented and on cycle4_acyclic22 [C-quivers-R4-59][C-quivers-R4-60]. On cycle4_oriented the representation with dimension vector [3, 3, 3, 3] whose last arrow is the Jordan block J_3(2) is absolutely indecomposable [C-quivers-R4-61]. A nilpotent string with dimension vector [2, 2, 1] on cycle3_oriented is absolutely indecomposable [C-quivers-R4-62].

**Proposition O (computed_rigorous).** Exhaustive counts agree with the classification into nilpotent strings S(i, l) and indecomposable modules over F_q[x, 1/x] (for β = mδ). The checks cover cycle3_oriented over F_2 and F_3 for all 0 < β ≤ [2, 2, 2], and cycle4_oriented over F_2 for all 0 < β ≤ [2, 2, 2, 2] [C-quivers-R4-63][C-quivers-R4-64][C-quivers-R4-65]. For cycle3_acyclic over F_2 and β ≤ [2, 2, 2], real roots have exactly one indecomposable and non-roots have none [C-quivers-R4-66]. The proof of the classification via Fitting's lemma lies in the companion ledger and is not part of the claims used here.

### 4.6 Multiples of δ

**Proposition P (computed_rigorous).** The number of isoclasses of indecomposables with dimension vector 2δ is as follows.

| Quiver | F_2 | F_3 | F_5 |
|---|---|---|---|
| cycle3_oriented | 5 [C-quivers-R5-67] | 8 [C-quivers-R5-68] | 17 [C-quivers-R5-69] |
| cycle3_acyclic | 5 [C-quivers-R5-70] | 8 [C-quivers-R5-71] | 17 [C-quivers-R5-72] |
| cycle4_oriented | 6 [C-quivers-R5-73] | 9 [C-quivers-R5-74] | not computed |
| cycle4_acyclic22 | 6 [C-quivers-R5-75] | 9 [C-quivers-R5-76] | not computed |

These counts coincide for the two orientations of each cycle. The identity A_{2δ} = A_δ is only an uncertified interpretation of these counts [C-quivers-R5-67-I].

## 5 Negative results and red-team findings

No claim was refuted or contested, and there were 0 negative results [C-methode]. Every red-team counter-check failed as designed. Examples: the tame-type test for star1 [C-quivers-R1-1-RT1], a second generator of the radical of star4 [C-quivers-R2-15-RT1], and a shifted constant in the Kac polynomial [C-quivers-R3-35-RT1]. Further examples are an off-by-one polynomial for the 3-cycle [C-quivers-R4-45-RT1] and a decomposition of V_5 [C-quivers-R2-19-RT1]. Removing the last list element made the lists over F_2, F_3 and F_5 incomplete, so the lists are tight [C-quivers-R2-20-RT1][C-quivers-R2-21-RT1][C-quivers-R2-22-RT1].

## 6 Limitations and open questions

- The Kac polynomials are certified only at finitely many primes, together with Kac's theorem on polynomiality and degree [C-lit4].
- The results on stars and cycles reproduce classical facts [C-lit1][C-lit3][C-lit5][C-lit6]. They are not new theorems.
- Not computed: the counts for 2δ over F_5 for the 4-cycles. The scope of the exhaustive checks is bounded by the dimension vectors stated above. See also the verifier notes referenced in [C-methode].
- The interpretation of the extra classes as exceptional tubes, the closed formula in n, the general cycle formula A_δ(q) = q + n − 1 and A_{2δ} = A_δ remain uncertified [C-quivers-R3-35-I][C-quivers-R5-67-I].
- Open: a uniform proof of the formulas from the certified instances; an extension to higher multiples of δ.

## References

- P. Gabriel (1972), "Unzerlegbare Darstellungen I", doi:10.1007/BF01298413 [C-lit1].
- I. N. Bernstein, I. M. Gelfand, V. A. Ponomarev (1973), "Coxeter functors and Gabriel's theorem", doi:10.1070/RM1973v028n02ABEH001526 [C-lit2].
- V. Kac (1980), "Infinite root systems, representations of graphs and invariant theory", doi:10.1007/BF01403155 [C-lit3].
- V. Kac (1983), "Root systems, representations of quivers and invariant theory", doi:10.1007/BFb0063236 [C-lit4].
- L. A. Nazarova (1973), "Representations of quivers of infinite type", doi:10.1070/IM1973v007n04ABEH001975 [C-lit5].
- C. M. Ringel (1984), "Tame algebras and integral quadratic forms", doi:10.1007/BFb0072870 [C-lit6].
- J. Hua (2000), "Counting representations of quivers over finite fields", doi:10.1006/jabr.1999.8220 [C-lit7].
- T. Hausel, E. Letellier, F. Rodriguez-Villegas (2013), "Positivity for Kac polynomials and DT-invariants of quivers", doi:10.4007/annals.2013.177.3.8 [C-lit8].

---
Prüfprotokoll: 95 Claims zitiert, Korrekturrunden [{"runde": 0, "verstoesse": 18}, {"runde": 1, "verstoesse": 1}, {"final_verstoesse_entfernt": 1}], 1 unbelegte Sätze entfernt, verbleibende Verstöße: 0.
