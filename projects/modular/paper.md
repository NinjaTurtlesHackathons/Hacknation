# Rational Linear Relations and Laplace Equations for Two-Loop Dihedral Modular Graph Functions at Weights 3 to 9

Noah Schittenhelm, Hack-Nation 2026, Team Ninja Turtles

## Abstract

We study rational linear relations among two-loop dihedral modular graph functions $C(a,b,c)$ of weight $w = 3, 5, 7, 9$, the Eisenstein series $E(w)$ and $\zeta(w)$ [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. We also study Laplace equations for $C(2,1,1)$, $C(3,1,1)$ and $C(2,2,1)$ [C-modular-R4a][C-modular-R4b][C-modular-R4c]. Counting predictions for such relation spaces come from generating-series methods (arXiv:2004.05156, quoted in [C-modular-R1d]); the explicit weight-9 relation was not found there in our search. At each weight we find a relation space of dimension exactly 1, including the weight-9 relation $-2160\,C(4,4,1)-4320\,C(4,3,2)-960\,C(3,3,3)+960\,E(9)+\zeta(9)=0$ [C-modular-R1d]. The Laplace equations hold with sources built from Eisenstein series and $\zeta(5)$ [C-modular-R4a][C-modular-R4b][C-modular-R4d]. The method is exact leading Laurent coefficients, high-precision evaluation at verifier-chosen points and a singular-value gap for completeness. All statements are numerical observations, not theorems. This is a pre-release: the computation at weight eleven is still running and the results are preliminary.

## Introduction

Modular graph functions arise as coefficients of the low-energy expansion of the one-loop closed-string amplitude. The two-loop dihedral functions $C(a,b,c)$ satisfy Laplace eigenvalue equations with inhomogeneous terms polynomial in non-holomorphic Eisenstein series (arXiv:1502.06698, quoted in [C-modular-R4b]). Identities among them were proved for weight less than six (arXiv:1603.00839, quoted in [C-modular-R1]). All identities at weight six and all dihedral identities at weight seven were later obtained and proven (arXiv:1608.04393v3, quoted in [C-modular-R1c]). A counting of linearly independent modular graph forms at fixed weight, with predictions, is given in arXiv:2004.05156v2 (quoted in [C-modular-R1d]).

Open question: what is the complete space of rational linear relations among all $C(a,b,c)$ of weight $w$, $E(w)$ and $\zeta(w)$ for $w = 3, 5, 7, 9$ [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]?

Contribution: we determine the relation space numerically at each of these weights, give explicit relations, and test inhomogeneous Laplace equations. The weight-9 relation was not found explicitly in our search, but it may be implied by the generating-series counting of arXiv:2004.05156 [C-modular-R1d]. This is a pre-release. The computation at weight eleven is still running and all results are preliminary. Every modular-graph-function statement below is a numerical observation.

**Summary of results.**

- Weight-3 observation: the relation space has dimension 1 [C-modular-R1][C-modular-R6b].
- Weight-5 observation: the relation space has dimension 1 [C-modular-R1b][C-modular-R6c].
- Weight-7 observation: the relation space has dimension 1 [C-modular-R1c][C-modular-R6d].
- Weight-9 observation: the relation space has dimension 1, with an explicit relation [C-modular-R1d][C-modular-R6a][C-modular-R6e].
- Laplace-equation observations for $C(3,1,1)$, $C(2,1,1)$ and $C(2,2,1)$ [C-modular-R4a][C-modular-R4b][C-modular-R4c][C-modular-R4d].
- Negative result: the weight-6 question, for which no claim passed the verifier [C-neg1].

## Model and assumptions

Notation. $\tau=\tau_1+i\tau_2$, $p=m\tau+n$ and $q=e^{2\pi i\tau}$ [C-modell]. The lattice-sum normalisation is $(\tau_2/(\pi|m\tau+n|^2))^a$ [C-modell]. With $\sum'$ denoting the sum over nonzero lattice momenta, and for $C$ over three momenta summing to zero,
$$E(s)=\sum_{p}{}'\Big(\frac{\tau_2}{\pi|p|^2}\Big)^s,\qquad C(a,b,c)=\sum_{p_1,p_2,p_3}{}'\ \prod_{i}\Big(\frac{\tau_2}{\pi|p_i|^2}\Big)^{a_i}\quad\text{[C-modell]},$$
with weight $w=a+b+c$. $L[F]=\tau_2^2(\partial_{\tau_1}^2+\partial_{\tau_2}^2)F$ is the hyperbolic Laplacian. The Eisenstein normalisation is $a_0=1$ [C-modell].

Fixed parameters [C-modell]:

| parameter | value |
|---|---|
| verifier points | 4 random points, seed 4711, $\lvert\tau_1\rvert\le 1/2$, $1\le\tau_2\le 2.5$ [C-modell] |
| working precision | 32 digits [C-modell] |
| tolerance | 1e-24 (1e-14 with Laplacian) [C-modell] |
| Laplacian step | $h=$ 1e-6, fourth-order finite differences [C-modell] |

## Method

Trusted base: the verifier's own evaluation of $E(s)$ and $C(a,b,c)$ at 32 digits at points it chooses itself [C-modell]. Relations proposed by a search are not trusted; each is re-checked as follows.

1. *Exact leading Laurent coefficient.* For each relation reported here, the exact leading Laurent coefficient vanishes [C-modular-R1d][C-modular-R4a].
2. *Numerical residual.* The relation is evaluated at the verifier points. The maximal relative residual must be below 1e-24 for linear relations and below 1e-14 for Laplace equations, where $L$ is a finite-difference Laplacian [C-modell].
3. *Completeness.* The normalised value matrix (rows are evaluation points, columns are the functions) is decomposed by singular values, with evaluation seed 4712 [C-modular-R1]. The dimension is the number of singular values below 1e-24, and a gap to the remaining values above 1e-8 is required [C-modular-R1].

Status of the claims. Everything about $C(a,b,c)$ is a numerical observation. Exact leading coefficients are necessary conditions, not proofs. Completeness rests on a numerical singular-value gap, and the claims have `scope=punkte`. The holomorphic Sturm-bound identities (the only statements that would count as theorems) are not part of the verified claim set used here, so this article states no theorems.

A third party re-runs the certificates as described in the Declarations.

The results were produced by an automated, verifier-gated laboratory in which every statement was accepted only after code-based verification. Counter-hypotheses were tested adversarially and the proposing process had no influence on the verdicts.

## Results

### Relation spaces

The four observations share one design: the $C(a,b,c)$ of weight $w$ plus $E(w)$ and $\zeta(w)$.

::: observation [Weight 3]
Numerically, the rational linear relations among $C(1,1,1)$, $E(3)$, $\zeta(3)$ form a space of dimension exactly 1 [C-modular-R1], spanned by $C(1,1,1)-E(3)-\zeta(3)=0$ [C-modular-R1][C-modular-R6b].
:::

*Certificate.* The relation holds at the verifier points with maximal relative residual 5.13e-44 against the bound 1e-24 and exact leading coefficient 0 [C-modular-R6b]. The $6\times3$ value matrix has singular values: 1 below 1e-24, 2 above 1e-8, smallest large value 0.731 [C-modular-R1]. Novelty status: inconclusive; equivalent searches disagree, and the closest literature statement is arXiv:1603.00839, so the result may be known [C-modular-R1][C-modular-R6b].

::: observation [Weight 5]
Numerically, the rational linear relations among $C(3,1,1)$, $C(2,2,1)$, $E(5)$, $\zeta(5)$ form a space of dimension exactly 1 [C-modular-R1b], spanned by $30\,C(2,2,1)-12\,E(5)-\zeta(5)=0$ [C-modular-R1b][C-modular-R6c].
:::

*Certificate.* Maximal relative residual 1.57e-43 (bound 1e-24), exact leading coefficient 0 [C-modular-R6c]. The $7\times4$ matrix has 1 singular value below 1e-24, 3 above 1e-8, smallest large value 0.0372 [C-modular-R1b]. Novelty status: inconclusive; equivalent searches disagree, and the closest literature statement is arXiv:1603.00839v4, so the result may be known [C-modular-R1b][C-modular-R6c].

::: observation [Weight 7]
Numerically, the rational linear relations among $C(5,1,1)$, $C(4,2,1)$, $C(3,3,1)$, $C(3,2,2)$, $E(7)$, $\zeta(7)$ form a space of dimension exactly 1 [C-modular-R1c], spanned by $252\,C(3,3,1)+252\,C(3,2,2)-108\,E(7)-\zeta(7)=0$ [C-modular-R1c][C-modular-R6d].
:::

*Certificate.* Maximal relative residual 1.59e-43 (bound 1e-24) [C-modular-R6d]. The $9\times6$ matrix has 1 singular value below 1e-24, 5 above 1e-8, smallest large value 0.000127 [C-modular-R1c]. Novelty status: already stated in the literature (arXiv:1608.04393v3) [C-modular-R1c]; see also arXiv:2007.05476v2 [C-modular-R6d].

::: observation [Weight 9]
Numerically, the rational linear relations among $C(7,1,1)$, $C(6,2,1)$, $C(5,3,1)$, $C(5,2,2)$, $C(4,4,1)$, $C(4,3,2)$, $C(3,3,3)$, $E(9)$, $\zeta(9)$ form a space of dimension exactly 1 [C-modular-R1d], spanned by $-2160\,C(4,4,1)-4320\,C(4,3,2)-960\,C(3,3,3)+960\,E(9)+\zeta(9)=0$ [C-modular-R1d][C-modular-R6a][C-modular-R6e]. The four functions $C(7,1,1)$, $C(6,2,1)$, $C(5,3,1)$, $C(5,2,2)$ do not occur in it [C-modular-R6a].
:::

*Certificate.* Maximal relative residual 8.33e-44 (bound 1e-24), exact leading coefficient 0 [C-modular-R6a]. The $12\times9$ matrix has 1 singular value below 1e-24, 8 above 1e-8, smallest large value 8.6e-7 [C-modular-R1d][C-modular-R6e]. Novelty status: inconclusive. The identity was not found explicitly in our search, but may be implied by the generating-series counting of arXiv:2004.05156 [C-modular-R1d][C-modular-R6a][C-modular-R6e].

Table of certified data (numerical observations). Thresholds: "small" means below 1e-24, "large" means above 1e-8 [C-modular-R1].

| $w$ | matrix | number small | number large | smallest large | claim |
|---|---|---|---|---|---|
| 3 | $6\times3$ | 1 | 2 | 0.731 | [C-modular-R1] |
| 5 | $7\times4$ | 1 | 3 | 0.0372 | [C-modular-R1b] |
| 7 | $9\times6$ | 1 | 5 | 0.000127 | [C-modular-R1c] |
| 9 | $12\times9$ | 1 | 8 | 8.6e-7 | [C-modular-R1d] |

### Laplace equations

::: observation [Laplace equation for $C(3,1,1)$]
Numerically, as functions of $\tau$, $L[C(3,1,1)]-6\,C(3,1,1)-\tfrac{86}{5}E(5)+4\,E(2)E(3)-\tfrac1{10}\zeta(5)=0$ [C-modular-R4a].
:::

*Certificate.* Maximal relative residual 1.63e-25 against the bound 1e-14, exact leading coefficient 0 [C-modular-R4a]. Novelty status: already stated in the literature (arXiv:1608.04393v3) [C-modular-R4a].

::: observation [Laplace equation for $C(2,1,1)$]
Numerically, $L[C(2,1,1)]-2\,C(2,1,1)-9\,E(4)+E(2)E(2)=0$ [C-modular-R4b].
:::

*Certificate.* Maximal relative residual 2.39e-25 (bound 1e-14) [C-modular-R4b]. Novelty status: already stated in the literature (arXiv:1502.06698) [C-modular-R4b].

::: observation [Laplace equations for $C(2,2,1)$]
Numerically, $L[C(2,2,1)]-8\,E(5)=0$ [C-modular-R4c] and $L[C(2,2,1)]-20\,C(2,2,1)+\tfrac23\zeta(5)=0$ [C-modular-R4d].
:::

*Certificate.* Maximal relative residuals 6.99e-26 and 6.74e-26 (bound 1e-14), exact leading coefficient 0 [C-modular-R4c][C-modular-R4d]. Novelty status: already stated in the literature (doi:10.1088/0264-9381/33/23/235011 and arXiv:1502.06698) [C-modular-R4c][C-modular-R4d].

## Negative results

- *Weight 6.* We asked for rational linear relations among $C(4,1,1)$, $C(3,2,1)$, $C(2,2,2)$, $E(6)$, $E(2)E(4)$, $E(3)^2$, $E(2)^3$, $\zeta(3)E(3)$, $\zeta(3)^2$, and for the dimension of the relation space (0 would also be a result) [C-neg1]. No claim passed the verifier [C-neg1]. For three attempts the reason is that no relation was confirmed individually and the $12\times9$ matrix has 0 singular values below 1e-24, 8 above 1e-8, smallest large value 2.44e-8 [C-neg1]. The fourth attempt returned no verifiable relation [C-neg1]. We therefore state no weight-6 result [C-neg1].
- *Eta-quotient identities.* No verified claim about eta quotients is available to this article as a main statement, so no reason for a failure is asserted here. Only adversarial counter-checks are recorded, in Appendix A.

## Discussion, limitations and open questions

All $C(a,b,c)$ statements rest on 32-digit evaluations at 4 verifier points [C-modell] and on singular-value gaps [C-modular-R1], which is numerical evidence, not proof. The dimension 1 at each weight is a statement about the tested function sets [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. The computation at weight eleven is still running, so no statement beyond weight 9 is made [C-modular-R1d]. The weight-9 relation has inconclusive novelty status [C-modular-R1d].

Open questions:

(i) Is the relation at each weight provable, for example by exact reduction of the lattice sums?

(ii) Does the generating-series counting of arXiv:2004.05156 reproduce the weight-9 relation-space dimension [C-modular-R1d]?

(iii) How does the pattern continue at weight eleven?

(iv) Can the weight-6 relation space be determined [C-neg1]?

## Declarations

*AI usage.* The results were produced and checked by an automated laboratory; every statement was verified by code.

*Code and data availability.* Repository https://github.com/NinjaTurtlesHackathons/Hacknation, branch claude/modulformen-paper, directory projects/modular. Reproduce all certificates with `python -m asd.recheck modular` and rebuild the paper with `python -m asd.paper --domain modular` [C-verfuegbarkeit].

*Affiliation.* None given.

*Competing interests.* None.

## Appendix A: Agentic laboratory

The laboratory ran 6 rounds with 21 verified statements and 2 negative results; every round was preregistered before the experiment (prereg.md) [C-methode]. Agents appearing in the weight-6 record are named `sparsam`, `numeriker`, `skeptiker` and `theoretiker` [C-neg1]. Novelty searches were run per result, with abstract counts recorded [C-neuheit-suche].

Red-team statistics: 25 adversarial counter-checks in total; 2 passed, 22 did not pass, 1 was not executable [C-redteam]. Examples: replacing the $\zeta(5)$ source term $\zeta(5)/10$ in the Laplace equation of $C(3,1,1)$ [C-modular-R4a] by $\zeta(5)/5$ gives a maximal relative residual 1.04e-01 [C-modular-R4d-RT1]. Changing the coefficient of $\zeta(9)$ to 2 is refuted exactly [C-modular-R6d-RT2]. The claim that the weight-9 relation space has dimension 0 fails the singular-value test [C-modular-R6a-RT1]. A counter-check with an eta quotient whose $q^1$ coefficient is 9 fails because the exact coefficient is 8 [C-modular-R5a-RT2].

## Appendix B: Provenance

The provenance table mapping every statement to its evidence follows; it is generated automatically.

## Appendix C: Verifier self-test

The claim set supplied for this article contains no description or result of a verifier self-test, so none is reported. The only available evidence on verifier discrimination is the adversarial counter-check record in Appendix A [C-redteam].
<!-- Abbildung margins.pdf: Belege C-modular-R4a, C-modular-R4b, C-modular-R4c, C-modular-R4d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d -->

