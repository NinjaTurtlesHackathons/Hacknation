# Rational Linear Relations and Laplace Equations for Dihedral Modular Graph Functions up to Weight 11

Noah Schittenhelm, Hack-Nation 2026, Team Ninja Turtles

# Rational Linear Relations and Laplace Equations for Dihedral Modular Graph Functions up to Weight 11

## Abstract

We study rational linear relations among two-loop dihedral modular graph functions $C(a,b,c)$ of weight $w=a+b+c$, together with $E(w)$ and $\zeta(w)$. For the full dihedral basis at weights 3, 5, 7 and 9 the relation space is numerically of dimension exactly one per weight [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. At weight 9 it is spanned by $960E(9)+\zeta(9)-2160C(4,4,1)-4320C(4,3,2)-960C(3,3,3)=0$ [C-modular-R6a]. At weight 11 the relation space was determined only on the sub-basis $C(5,5,1),C(5,4,2),C(5,3,3),C(4,4,3),E(11),\zeta(11)$, where it is again one-dimensional [C-modular-R7b]. For the full ten-function weight-11 basis the question is undecided [C-neg3]. A counting of linearly independent modular graph forms was given in [C-litn4], and the weight-9 result may be implied there [C-modular-R1d]. We also verify inhomogeneous Laplace equations for $C(3,1,1)$, $C(2,1,1)$ and $C(2,2,1)$ [C-modular-R4a][C-modular-R4b][C-modular-R4d]. The method is PSLQ on values at random points, followed by an exact leading-Laurent-coefficient check and independent evaluation. All modular-graph-function statements are numerical observations at 4 verifier points, not theorems [C-modell].

## Introduction

Modular graph functions appear as coefficients in the low-energy expansion of the one-loop closed-string amplitude. They satisfy Laplace eigenvalue equations with inhomogeneous terms that are polynomial in non-holomorphic Eisenstein series [C-litn5]. Relations of low weight have been proved by an explicit map between graph forms [C-litn1], and all dihedral identities at weight seven are in the literature [C-litn3]. Systematic basis decompositions of two- and three-point graph forms are available [C-litn9]. A counting of linearly independent modular graph forms gives predictions for higher, hitherto unexplored weights [C-litn4].

Open question: how many independent rational linear relations exist among all $C(a,b,c)$ of weight $w$, $E(w)$ and $\zeta(w)$ for weights 3, 5, 7, 9 and 11, and which Laplace equations do the functions satisfy [C-modular-R1d][C-modular-R7b]?

Contribution: we determine the relation space numerically on the full dihedral basis at weights 3, 5, 7 and 9 [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. At weight 11 we determine it only on a six-function sub-basis [C-modular-R7b]. We verify Laplace equations for three functions [C-modular-R4a][C-modular-R4b][C-modular-R4d], and we reproduce holomorphic identities with Sturm-bound certificates [C-modular-R5a].

**Summary of results.**

- The weight-by-weight observations show that the relation space has dimension exactly one on the full dihedral basis at weights 3, 5, 7 and 9, with the novelty statuses quoted there [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d].
- A further observation gives the explicit weight-9 relation [C-modular-R6a].
- The weight-11 observation gives the relation and its one-dimensional relation space on the sub-basis only [C-modular-R7b]. The full ten-function weight-11 basis is undecided [C-neg3].
- The Laplace observations give equations for $C(3,1,1)$, $C(2,1,1)$ and $C(2,2,1)$ [C-modular-R4a][C-modular-R4b][C-modular-R4c][C-modular-R4d].
- The propositions on holomorphic identities certify string-partition-function identities [C-modular-R5a][C-modular-R5g], and a further proposition gives the eta-quotient span table [C-modular-R8].

## Model and assumptions

**Holomorphic objects.** $q=e^{2\pi i\tau}$ is the expansion variable. The Eisenstein series are normalised by $E_k=1-(2k/B_k)\sum_n\sigma_{k-1}(n)q^n$, so that $a_0=1$ [C-modell]. Further building blocks are $\eta(d)=\eta(d\tau)$ (Dedekind eta), $\Delta(d)$ (the discriminant form at $d\tau$), $\theta(d)=\sum_n q^{dn^2}$, the lattice theta series $\theta_{E8}$ and $\theta_{D16}$ obtained by lattice enumeration, and $j=E_4^3/\Delta$.

**Non-holomorphic objects.** $\tau=\tau_1+i\tau_2$ and $p=m\tau+n$. The lattice sums are normalised with weight factor $(\tau_2/(\pi|m\tau+n|^2))^a$ [C-modell]:



with weight $w=a+b+c$. $\mathcal L=\tau_2^2(\partial_{\tau_1}^2+\partial_{\tau_2}^2)$ is the hyperbolic Laplacian, and $\zeta$ is the Riemann zeta function.

**Fixed parameters** [C-modell]:

| parameter | value |
|---|---|
| verifier points | 4 points, seed 4711, $\lvert\tau_1\rvert\le 1/2$, $1\le\tau_2\le 2.5$ [C-modell] |
| working precision | 32 digits [C-modell] |
| tolerance | `1e-24` (`1e-14` with Laplacian) [C-modell] |
| finite-difference step | $h=$ `1e-6` (fourth-order Laplacian) [C-modell] |

## Method

**Relations.** Candidate rational relations are obtained by PSLQ on function values at random points. The failed weight-11 attempt on the full basis, at the points examined (6-8 points, up to 64 digits), found no relation [C-neg3]. Each candidate is then checked in two ways [C-modular-R1]:

- exact rational arithmetic on the leading Laurent coefficient [C-modular-R1];
- evaluation at the verifier's own points, with relative residual below `1e-24` [C-modell][C-modular-R1].

**Completeness.** Completeness of a relation space is judged by a singular-value gap of the normalised value matrix at an independent seed, 4712 [C-modular-R1].

**Laplace equations.** They are checked at the 4 verifier points at 32 digits, with relative residual at most `1e-14`, using a finite-difference Laplacian, together with an exact leading-coefficient check [C-modular-R4a].

**Holomorphic identities.** A Sturm-bound certificate is used. For the identity of [C-modular-R5a], the terms lie in $M^!_2(\Gamma_0(4))$ and the coefficients $q^0..q^{11}$ vanish exactly, which exceeds the Sturm bound 1 [C-modular-R5a].

**Trusted base and status.** The trusted base is exact rational arithmetic for leading coefficients and Sturm certificates, plus the verifier's 32-digit evaluation of modular graph functions [C-modell]. Everything about modular graph functions beyond the exact leading coefficient is a numerical observation at the 4 verifier points, never a theorem [C-modell]. The weight-11 sub-basis came from a human-guided exploration and was then verified by the code verifier [C-modular-R7b]. Everything is re-run with the command in the Declarations [C-verfuegbarkeit].

The work was carried out by an automated, verifier-gated laboratory in which every statement reported here was accepted only after an independent code check; its organisation is described in Appendix A.

## Results

### Relation spaces (numerical observations)

::: observation [Weight 3]
Numerically, the rational linear relations among $C(1,1,1),E(3),\zeta(3)$ form a space of dimension exactly 1, spanned by $C(1,1,1)-E(3)-\zeta(3)=0$ [C-modular-R1].
:::

*Certificate.* The relation holds to `1e-24` at verifier points with exact leading Laurent coefficient [C-modular-R1]. Completeness follows from the singular-value gap in Table 1 [C-modular-R1]. Novelty status: inconclusive; equivalent searches disagree (2 equivalent checks, 1 with a literature hit, 1 without), the closest statement being arXiv:1603.00839, and the result may be known or implied there [C-litn1][C-modular-R1].

::: observation [Weight 5]
Numerically, the relation space among $C(3,1,1),C(2,2,1),E(5),\zeta(5)$ has dimension exactly 1, spanned by $30C(2,2,1)-12E(5)-\zeta(5)=0$ [C-modular-R1b].
:::

*Certificate.* The relation holds to `1e-24` with exact leading coefficient, and the gap is given in Table 1 [C-modular-R1b]. Novelty status: inconclusive; equivalent searches disagree (2 equivalent checks, 1 with a literature hit, 1 without), closest statement arXiv:1603.00839v4, and the result may be known or implied there [C-litn2][C-modular-R1b].

::: observation [Weight 7]
Numerically, the relation space among $C(5,1,1),C(4,2,1),C(3,3,1),C(3,2,2),E(7),\zeta(7)$ has dimension exactly 1, spanned by $252C(3,3,1)+252C(3,2,2)-108E(7)-\zeta(7)=0$ [C-modular-R1c].
:::

*Certificate.* The relation holds to `1e-24` with exact leading coefficient, and the gap is given in Table 1 [C-modular-R1c]. Novelty status: already stated in the literature (arXiv:1608.04393v3) [C-litn3][C-modular-R1c].

::: observation [Weight 9, relation space]
Numerically, the relation space among $C(7,1,1),C(6,2,1),C(5,3,1),C(5,2,2),C(4,4,1),C(4,3,2),C(3,3,3),E(9),\zeta(9)$ has dimension exactly 1 [C-modular-R1d], spanned by $-2160C(4,4,1)-4320C(4,3,2)-960C(3,3,3)+960E(9)+\zeta(9)=0$ [C-modular-R1d][C-modular-R6e].
:::

*Certificate.* The relation holds to `1e-24` with exact leading coefficient [C-modular-R1d][C-modular-R6e]. The gap is given in Table 1 [C-modular-R1d]. Novelty status: inconclusive; equivalent searches disagree (3 equivalent checks, 1 with a literature hit, 2 without). The closest statement is arXiv:2004.05156v2, which counts linearly independent modular graph forms, and the result may be known or implied there [C-litn4][C-modular-R1d].

::: observation [Weight 9, explicit relation]
Numerically (32 digits, 4 verifier-chosen points, relative residual at most `1e-24`), $960E(9)+\zeta(9)-2160C(4,4,1)-4320C(4,3,2)-960C(3,3,3)=0$ as functions of $\tau$ [C-modular-R6a].
:::

*Certificate.* The exact leading coefficient of $y^9$ vanishes, and the maximal relative residual at the verifier points is 8.33e-44 [C-modular-R6a]. Novelty status: inconclusive; equivalent searches disagree (3 equivalent checks, 1 with a literature hit, 2 without), closest statement arXiv:2004.05156v2, and the result may be known or implied there [C-litn4][C-modular-R6a].

::: observation [Weight 11, sub-basis only]
Numerically, the relation space among $C(5,5,1),C(5,4,2),C(5,3,3),C(4,4,3),E(11),\zeta(11)$ has dimension exactly 1 [C-modular-R7b], spanned by $19008C(5,5,1)+38016C(5,4,2)+19008C(5,3,3)+28512C(4,4,3)-8640E(11)-\zeta(11)=0$ [C-modular-R7b]. This concerns the sub-basis only. For the full ten-function basis (ten $C(a,b,c)$, $E(11)$, $\zeta(11)$) the question is undecided: the PSLQ attempt, with up to 64 digits at the points examined, found nothing and the run was aborted [C-neg3].
:::

*Certificate.* The relation holds at 4 verifier points at 32 digits with relative residual at most `1e-24` (maximum 1.21e-43), and the exact leading coefficient of $y^{11}$ vanishes [C-modular-R7a]. Completeness on the sub-basis follows from the gap in Table 1 [C-modular-R7b]. Novelty status: not found in a targeted search of 85 abstracts on 2026-10-04 for the relation [C-modular-R7a], and not found in a targeted search of 121 abstracts on 2026-10-04 for the relation space [C-modular-R7b].

**Table 1.** Singular values of the normalised value matrices (seed 4712); one singular value is below `1e-24` in every row [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d][C-modular-R7b].

| weight [C-modular-R1] | basis | matrix | singular values $>$ `1e-8` [C-modular-R1] | smallest of these |
|---|---|---|---|---|
| 3 | full | 6x3 | 2 | 0.731 [C-modular-R1] |
| 5 | full | 7x4 | 3 | 0.0372 [C-modular-R1b] |
| 7 | full | 9x6 | 5 | 0.000127 [C-modular-R1c] |
| 9 | full | 12x9 | 8 | 8.6e-7 [C-modular-R1d] |
| 11 | sub-basis | 9x6 | 5 | 4.41e-6 [C-modular-R7b] |

### Laplace equations (numerical observations)

**Table 2.** Laplace equations at 32 digits, 4 verifier-chosen points, relative residual bound `1e-14` [C-modular-R4a][C-modular-R4b][C-modular-R4c][C-modular-R4d].

| equation (as functions of $\tau$) | max. residual |
|---|---|
| $\mathcal L[C(3,1,1)]-6C(3,1,1)-\tfrac{86}{5}E(5)+4E(2)E(3)-\tfrac1{10}\zeta(5)=0$ [C-modular-R4a] | 1.63e-25 |
| $\mathcal L[C(2,1,1)]-2C(2,1,1)-9E(4)+E(2)E(2)=0$ [C-modular-R4b] | 2.39e-25 |
| $\mathcal L[C(2,2,1)]-8E(5)=0$ [C-modular-R4c] | 6.99e-26 |
| $\mathcal L[C(2,2,1)]-20C(2,2,1)+\tfrac23\zeta(5)=0$ [C-modular-R4d] | 6.74e-26 |

::: observation [Laplace equation for $C(3,1,1)$]
$\mathcal L[C(3,1,1)]-6C(3,1,1)-\tfrac{86}{5}E(5)+4E(2)E(3)-\tfrac1{10}\zeta(5)=0$ [C-modular-R4a].
:::

*Certificate.* The exact leading coefficient of $y^5$ vanishes, with numerical residual as in Table 2 [C-modular-R4a]. Novelty status: already stated in the literature (arXiv:1608.04393v3) [C-litn3][C-modular-R4a].

::: observation [Laplace equation for $C(2,1,1)$]
$\mathcal L[C(2,1,1)]-2C(2,1,1)-9E(4)+E(2)E(2)=0$ [C-modular-R4b].
:::

*Certificate.* The exact leading coefficient of $y^4$ vanishes, with numerical residual as in Table 2 [C-modular-R4b]. Novelty status: already stated in the literature (arXiv:1502.06698) [C-litn5][C-modular-R4b].

::: observation [Source-only equation for $C(2,2,1)$]
$\mathcal L[C(2,2,1)]-8E(5)=0$ [C-modular-R4c].
:::

*Certificate.* The exact leading coefficient of $y^5$ vanishes, with numerical residual as in Table 2 [C-modular-R4c]. Novelty status: already stated in the literature (doi:10.1088/0264-9381/33/23/235011) [C-litn6][C-modular-R4c].

::: observation [Eigenvalue equation for $C(2,2,1)$]
$\mathcal L[C(2,2,1)]-20C(2,2,1)+\tfrac23\zeta(5)=0$ [C-modular-R4d].
:::

*Certificate.* The exact leading coefficient of $y^5$ vanishes, with numerical residual as in Table 2 [C-modular-R4d]. Novelty status: already stated in the literature (arXiv:1502.06698) [C-litn5][C-modular-R4d].

### Supporting statement and examples

::: observation [Weight 7, pointwise]
Numerically (32 digits, 4 verifier points, relative residual at most `1e-24`), $252C(3,3,1)+252C(3,2,2)-108E(7)-\zeta(7)=0$ as functions of $\tau$ [C-modular-R6d].
:::

*Certificate.* The exact leading coefficient of $y^7$ vanishes, and the maximal residual is 1.59e-43 [C-modular-R6d]. Status: already stated in the literature (arXiv:2007.05476v2) [C-litn9][C-modular-R6d].

::: example [Weight 3]
Numerically, $C(1,1,1)-E(3)-\zeta(3)=0$ as functions of $\tau$, with maximal relative residual 5.13e-44 and vanishing exact leading coefficient of $y^3$ [C-modular-R6b].
:::

::: example [Weight 5]
Numerically, $30C(2,2,1)-12E(5)-\zeta(5)=0$ as functions of $\tau$, with maximal relative residual 1.57e-43 and vanishing exact leading coefficient of $y^5$ [C-modular-R6c].
:::

### Holomorphic identities from string partition functions

These identities are the holomorphic building blocks of string partition functions: the Jacobi identity as an eta-quotient identity, the two heterotic lattices, and the discriminant. Each is certified exactly by a Sturm bound. They are certified statements, not numerical observations [C-modular-R5a].

::: proposition [Jacobi identity on $\Gamma_0(4)$]
(i) $\theta(1)^4-\eta(2)^{20}\eta(1)^{-8}\eta(4)^{-8}=0$ (weight 2) [C-modular-R5a].
(ii) $\theta(1)^2-\eta(2)^{10}\eta(1)^{-4}\eta(4)^{-4}=0$ (weight 1) [C-modular-R5b].
:::

::: proposition [Heterotic lattices on $\Gamma_0(1)$]
$\theta_{E8}-E_4=0$ [C-modular-R5c]; $\theta_{E8}^2-\theta_{D16}=0$ [C-modular-R5d]; $\theta_{E8}^2-E_4^2=0$ [C-modular-R5e]; $\theta_{E8}^2-E_8=0$ [C-modular-R5f].
:::

::: proposition [Discriminant and $j$ on $\Gamma_0(1)$]
$1728\,\Delta(1)-E_4^3+E_6^2=0$ [C-modular-R5g], and $j\,\Delta(1)-E_4^3=0$ [C-modular-R5h].
:::

*Certificate.* In each case all terms lie in $M^!_k(\Gamma_0(N))$ of equal weight, and the coefficients vanish exactly up to the stated order, which exceeds the Sturm bound (Table 3).

**Table 3.** Sturm certificates.

| identity | weight | index | vanishing $q$-coefficients | Sturm bound |
|---|---|---|---|---|
| $\theta(1)^4$ vs. eta quotient | 2 | 6 | $q^0..q^{11}$ | 1 [C-modular-R5a] |
| $\theta(1)^2$ vs. eta quotient | 1 | 6 | $q^0..q^{10}$ | 1/2 [C-modular-R5b] |
| $\theta_{E8}=E_4$ | 4 | 1 | $q^0..q^{10}$ | 1/3 [C-modular-R5c] |
| $\theta_{E8}^2=\theta_{D16}$, $E_4^2$, $E_8$ | 8 | 1 | $q^0..q^{10}$ | 2/3 [C-modular-R5d][C-modular-R5e][C-modular-R5f] |
| $1728\Delta=E_4^3-E_6^2$ | 12 | 1 | $q^0..q^{11}$ | 1 [C-modular-R5g] |
| $j\Delta=E_4^3$ | 12 | 1 | $q^0..q^{11}$ | 1 [C-modular-R5h] |

Novelty status: the Jacobi identities are already stated in the literature (arXiv:2607.26471v1) [C-litn7][C-modular-R5a][C-modular-R5b]. The discriminant formula is already stated in the literature (arXiv:1505.06042v1) [C-litn8][C-modular-R5g]. The lattice identities and $j\Delta=E_4^3$ are reproductions of classical results, preregistered as validation anchors without any claim of novelty [C-modular-R5c][C-modular-R5d][C-modular-R5e][C-modular-R5f][C-modular-R5h].

::: proposition [Eta-quotient span table]
For all levels $N\le 30$, holomorphic eta quotients with trivial character span $M_4(\Gamma_0(N))$ exactly for $N \in [2, 4, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30]$ and not for $N \in [1, 3, 7, 11, 13, 17, 19, 21, 23, 29]$ (exact, exhaustive) [C-modular-R8].
:::

*Certificate.* The span of eta quotients was computed exactly for each level and compared with the space dimension [C-modular-R8]. Novelty status: not found in a targeted search of 33 abstracts on 2026-10-04 [C-modular-R8].

## Negative results

- **Weight 6 (undecided).** The question concerned relations among $C(4,1,1),C(3,2,1),C(2,2,2),E(6),E(2)E(4),E(3)^2,E(2)^3,\zeta(3)E(3),\zeta(3)^2$ [C-neg1]. No claim passed the verifier. The value matrix (12x9) has no singular value below `1e-24` and a smallest large singular value of 2.44e-8 [C-neg1]. The singular-value gap criterion is therefore not met, and the dimension remains undecided [C-neg1].
- **Weight 11, first attempt with the full basis.** PSLQ over the full 12-element basis (ten $C(a,b,c)$, $E(11)$, $\zeta(11)$), at the points examined (6-8 points, up to 64 digits), found no relation [C-neg3]. The run was aborted. The suspected cause is precision that is too low relative to the coefficient height [C-neg3]. This is why the weight-11 result is restricted to the sub-basis [C-modular-R7b].
- **First eta-span run.** No claim passed the verifier [C-neg2]. The failure came from a verifier capacity limit, which was fixed, and the table above was then obtained [C-modular-R8].

## Discussion, limitations and open questions

The relation space has dimension exactly one at weights 3, 5, 7 and 9 on the full dihedral basis [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. Each relation has the form (combination of $C$) $=$ (rational) $E(w)+$ (rational) $\zeta(w)$ [C-modular-R1][C-modular-R1b][C-modular-R1c][C-modular-R1d]. The weight-11 relation has the same shape on a six-function sub-basis [C-modular-R7b]. All statements on modular graph functions are numerical observations at 4 verifier points [C-modell], with an exact check only of the leading Laurent coefficient [C-modular-R1].

Open questions:

(i) What is the relation-space dimension for the full ten-function weight-11 basis [C-neg3]? Higher precision or a different method is needed.

(ii) What is the dimension at weight 6, where the gap criterion was not met [C-neg1]?

(iii) Is the weight-9 result implied by the counting of [C-litn4] (status: inconclusive [C-modular-R1d])?

(iv) Can the numerical relations be turned into proofs, as done for low weight in [C-litn1][C-litn3]?

## Declarations

**AI usage.** The results were produced and checked by an automated laboratory; every statement was verified by code.

**Code and data availability.** Repository https://github.com/NinjaTurtlesHackathons/Hacknation, branch `claude/modulformen-paper`, directory `projects/modular`. Reproduce all certificates with `python -m asd.recheck modular` and rebuild the paper with `python -m asd.paper --domain modular` [C-verfuegbarkeit].

**Competing interests.** None.

## Appendix A: Agentic laboratory

The laboratory ran 8 rounds with 24 verified statements and 3 negative results [C-methode]. Every round was preregistered before the experiment (`prereg.md`) [C-methode]. Several agents with distinct roles proposed candidates (for example numerical, skeptical and theoretical roles, as listed in the failed attempts [C-neg1]). Only statements accepted by the code verifier were kept. Counter-checks (adversarial tests) numbered 30 in total: 2 passed, 27 did not pass, and 1 was not executable [C-redteam]. "Did not pass" means the false variant was rejected, which is the intended outcome. The two that passed did not contradict the statements [C-modular-R1c-RT1][C-modular-R5g-RT1].

## Appendix B: Provenance

The provenance table mapping every statement to its evidence follows; it is generated automatically.

## Appendix C: Verifier self-test

The verifier is tested with deliberately false variants, which it must reject. Examples:

- factor 1727 instead of 1728 in the discriminant identity [C-modular-R5a-RT1], and 1729 instead of 1728 [C-modular-R5b-RT2];
- $q^1$-coefficient 481 instead of 480 for $\theta_{D16}$ [C-modular-R5b-RT1];
- $\zeta(5)$ coefficient $1/5$ instead of $1/10$, which gives residual 1.04e-01 [C-modular-R4d-RT1];
- $\zeta(9)$ coefficient 2 instead of 1 [C-modular-R6d-RT2];
- a sign flip of the $\zeta(11)$ term, which gives residual 5.71e-01 [C-modular-R7a-RT2].

All of these were rejected, so the verifier distinguishes exact leading coefficients and tight residuals from near-misses [C-redteam].
<!-- Abbildung margins.pdf: Belege C-modular-R4a, C-modular-R4b, C-modular-R4c, C-modular-R4d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d, C-modular-R7a -->

<!-- Abbildung eta_span.pdf: Belege C-modular-R8 -->

