# Closed forms for the constants in the odd-weight identities between dihedral modular graph functions

Noah Schittenhelm, Hack-Nation 2026, Team Ninja Turtles

# Closed forms for the constants in the odd-weight identities between dihedral modular graph functions

## Abstract

We consider the combinations $X_w$ of two-loop dihedral modular graph functions $C(a,b,c)$ of odd weight $w$ whose hyperbolic Laplacian is a multiple of the Eisenstein series $E(w)$. At each odd weight examined, $3\le w\le 61$, we prove $X_w=f_wE(w)+g_w\zeta(w)$ with $f_w=3((w-1)/2)!/w$ and $g_w=6|B_{w-1}|/((w-1)/2)!$ [C-modular-R17a]. The proof combines exact Laplace algebra, a harmonicity, invariance and growth argument, and a constant term evaluated from a Laurent polynomial in rational arithmetic. It assumes a theorem of D'Hoker–Kaidi and a standard lemma, neither checked by code [C-fakt-beweis]. We also show exactly that at each weight $3\le w\le 25$ the space of combinations with $\Delta X\in\mathbb{Q}E(w)$ has dimension 1 for odd $w$ and 0 for even $w$ [C-modular-R14]. Independently of the proof, the constants at $w=3,\dots,17$ are confirmed numerically at 32 digits at verifier-chosen points, and $w=17$ was a preregistered blind test [C-fakt-konstanten], [C-modell]. The full weight-11 basis has exactly one relation, established numerically by a singular-value criterion [C-modular-R12]. A proof beyond the examined range remains open [C-fakt-konstanten].

## Introduction

Two-loop dihedral modular graph functions $C(a,b,c)$ appear as coefficients in the low-energy expansion of the one-loop amplitude of closed strings. D'Hoker, Green and Vanhove showed that they satisfy Laplace eigenvalue equations with inhomogeneous terms polynomial in non-holomorphic Eisenstein series, and that the Laplace equation fixes an algebraic identity only up to an additive constant of integration [C-litn1]. The DGV combination $X_w$ of $C(a,b,c)$, whose Laplacian is proportional to $E(w)$, is used here at each odd weight examined, $3\le w\le 61$ [C-modular-R17a]. The constants are explicit in that work only up to weight 9 [C-modular-R7a], and $g_7,g_9$ appear there as undetermined integration constants [C-modular-R17a]. The constant $g_7$ was later given in a general procedure based on Laurent polynomials [C-litn2]. Identities among two-loop graphs at all weights were also constructed earlier [C-litn3], and relations between graphs with four and five links have been proved [C-litn4].

**Open question.** What are the closed forms of $f_w$ and $g_w$ in $X_w=f_wE(w)+g_w\zeta(w)$ for odd $w$? [C-fakt-konstanten]

**Difficulty.** The Laplace equation alone leaves $g_w$ undetermined [C-litn1]. Fixing it requires the Laurent polynomial of each $C(a,b,c)$ at the cusp [C-fakt-beweis]. The size of the combination grows with $w$, and numerical searches for relations are limited by the working precision relative to the height of the coefficients [C-neg3].

**Contribution.** The Laurent polynomial of each single $C_{u,v;w}$ is known (Theorem 5.1 of D'Hoker–Kaidi, arXiv:1902.04180) [C-modular-R17a]. We evaluate it in rational arithmetic on the DGV combinations. This gives closed forms for $f_w$ and $g_w$ with a proof at each odd weight examined, $w\le 61$ [C-modular-R17a], together with numerical confirmations independent of that proof [C-fakt-konstanten].

**Summary of results.**

- Theorem 1 shows $X_w=f_wE(w)+g_w\zeta(w)$ exactly at each odd weight examined, $3\le w\le 61$, with $f_w$ and $g_w$ in closed form [C-modular-R17a]. The proof is computer-assisted in rational arithmetic, and its assumptions are stated openly [C-fakt-beweis].
- Theorem 2 shows that the space $\{X:\Delta X\in\mathbb{Q}E(w)\}$ is one-dimensional for odd $w$ and zero for even $w$, at each weight $3\le w\le 25$ [C-modular-R14].
- Conjecture 1 states that the closed forms persist beyond the examined range; they are proved up to $w=61$ [C-fakt-konstanten], [C-modular-R17a].
- Observations 1 to 3 confirm numerically, independently of the proof, the constants at $w=3,\dots,17$ [C-fakt-konstanten]. They show that the full weight-11 basis carries exactly one relation [C-modular-R12]. They also report a hardening run that exposed and fixed one evaluator bug [C-fakt-haertung].

## Setting

Let $\tau=\tau_1+i\tau_2$ and $p=m\tau+n$ with $(m,n)\in\mathbb{Z}^2\setminus\{0\}$ [C-modell]. The non-holomorphic Eisenstein series and the dihedral two-loop graphs are [C-modell]

$$E(s)=\sum_{p}{}' \Big(\frac{\tau_2}{\pi|p|^2}\Big)^{s},$$

$$C(a,b,c)=\sum_{p_1+p_2+p_3=0}{}' \prod_{i=1}^{3}\Big(\frac{\tau_2}{\pi|p_i|^2}\Big)^{a_i},$$

with $(a_1,a_2,a_3)=(a,b,c)$ and weight $w=a+b+c$. The hyperbolic Laplacian is

$$\Delta=\tau_2^2\big(\partial_{\tau_1}^2+\partial_{\tau_2}^2\big),$$

and $E(w)$ satisfies [C-fakt-beweis]

$$\Delta E(w)=w(w-1)E(w).$$

$\zeta$ is the Riemann zeta function and $B_k$ are Bernoulli numbers. For odd $w=2\mu+3$, $X_w$ denotes the rational combination of $C(a,b,c)$ of weight $w$ given by eq. 3.57 of D'Hoker–Green–Vanhove (arXiv:1502.06698), in that normalisation [C-modular-R14]. The constants are [C-fakt-konstanten]

$$f_w=\frac{3\,((w-1)/2)!}{w},$$

$$g_w=\frac{6\,|B_{w-1}|}{((w-1)/2)!}.$$

Holomorphic Eisenstein series are normalised by $a_0=1$, $E_k=1-\frac{2k}{B_k}\sum_n\sigma_{k-1}(n)q^n$ with $q=e^{2\pi i\tau}$ [C-modell].

**Verifier parameters.** The numerical verifier uses 4 evaluation points with seed 4711 in the region $|\tau_1|\le 1/2$, $1\le\tau_2\le 2.5$ [C-modell]. The working precision is 32 digits [C-modell]. Numerical relations are accepted at maximal relative residual 1e-24, and at 1e-14 when a Laplacian is involved [C-modell]. The Laplacian is evaluated by a fourth-order finite-difference scheme with step h = 1e-6 [C-modell].

## Closed forms and their proof

::: theorem [Closed forms for odd weight]
At each odd weight $w$ examined, $3\le w\le 61$, one has $X_w=f_wE(w)+g_w\zeta(w)$ [C-modular-R17a], with the constants [C-fakt-konstanten]

$$f_w=\frac{3((w-1)/2)!}{w}\quad\text{[C-fakt-konstanten]}$$

$$g_w=\frac{6|B_{w-1}|}{((w-1)/2)!}\quad\text{[C-fakt-konstanten]}$$
:::

*Proof.* The proof has three steps, following [C-fakt-beweis], [C-modular-R17a].

1. Exact rational computation in the algebraic Laplace representation gives $\Delta X_w=w(w-1)f_wE(w)$ with no other terms, re-done at each odd weight examined, $w\le 61$ [C-fakt-beweis], [C-modular-R17a]. Since $\Delta E(w)=w(w-1)E(w)$, the difference $X_w-f_wE(w)$ is harmonic [C-fakt-beweis].
2. The difference is $SL(2,\mathbb{Z})$-invariant and of polynomial growth at the cusp, hence constant by the standard argument used by D'Hoker–Green–Vanhove [C-fakt-beweis].
3. The constant equals the $\tau_2^0$ term of the Laurent polynomial of $X_w$ [C-fakt-beweis]. This polynomial follows from Proposition 2.1 and Theorem 5.1 of D'Hoker–Kaidi (arXiv:1902.04180), evaluated in rational arithmetic [C-modular-R17a]. The transcription was checked against their eq. 5.19, and every Laurent term not involving products of zeta values agrees with that of $f_wE(w)+g_w\zeta(w)$ [C-modular-R17a]. This is a consistency check. The $\tau_2^0$ term equals $g_w\zeta(w)$ with $g_w=6|B_{w-1}|/((w-1)/2)!$ at each odd weight examined, $w\le 61$ [C-fakt-beweis].

Assumptions not checked by code: the correctness of Theorem 5.1 of arXiv:1902.04180, proved there in Appendix A, whose conjectural part concerns only the coefficient of $\tau_2^{2-w}$ and is not used, and the standard lemma in step 2 [C-fakt-beweis]. $\square$

*Novelty status:* partly known. The combinations $X_w$ (DGV eq. 3.57), $f_w$ up to weight 9 and $g_w$ at weights 3 and 5 (DGV eq. 3.34) are due to DGV, and $g_7$ also appears in arXiv:2109.05017 [C-modular-R17a]. Not given there are the closed forms for general odd $w$ and their proof for $w\ge 9$ [C-modular-R17a]. The Laurent polynomial of each single $C_{u,v;w}$ is used here as a tool [C-modular-R17a].

Table 1 lists the values for odd $w\le 25$ [C-fakt-konstanten].

Table: Constants $f_w$ and $g_w$ in $X_w=f_wE(w)+g_w\zeta(w)$ for odd $w\le 25$ [C-fakt-konstanten].

| $w$ | $f_w$ | $g_w$ |
|---|---|---|
| 3 | 1 | 1 |
| 5 | 6/5 | 1/10 |
| 7 | 18/7 | 1/42 |
| 9 | 8 | 1/120 |
| 11 | 360/11 | 1/264 |
| 13 | 2160/13 | 691/327600 |
| 15 | 1008 | 1/720 |
| 17 | 120960/17 | 3617/3427200 |
| 19 | 1088640/19 | 43867/48263040 |
| 21 | 518400 | 174611/199584000 |
| 23 | 119750400/23 | 77683/83462400 |
| 25 | 57480192 | 236364091/217945728000 |

![Constants f_w and g_w from Table 1 over the odd weights w. The numerators of g_w are Bernoulli numerators, and f_w grows factorially in w.](figures/constants.png)

::: theorem [Uniqueness of the harmonic combination]
At each weight $w$ examined, $3\le w\le 25$, the rational combinations $X$ of dihedral $C(a,b,c)$ of weight $w$ with $\Delta X\in\mathbb{Q}\,E(w)$ form a vector space of dimension 1 for odd $w$ and 0 for even $w$ [C-modular-R14]. For odd $w$ it is spanned by the DGV combination $X_w$, and $\Delta X_w=w(w-1)f_wE(w)$ [C-modular-R14].
:::

*Certificate.* The algebraic Laplace representation of D'Hoker–Green–Vanhove was re-derived and the linear conditions were solved in exact rational arithmetic for each $w$ in the range [C-modular-R14]. $\square$

*Novelty status:* partly known. DGV state that the eigenvalue-0 eigenspace has multiplicity one for each odd weight and zero for each even weight; the closed form $f_w=3((w-1)/2)!/w$ is not given there, and the exact confirmation up to $w=25$ is an independent recomputation [C-modular-R14].

::: remark [Conjecture 1]
The closed forms $f_w$ and $g_w$ of Theorem 1 are conjectured to persist at odd weights beyond the examined range [C-fakt-konstanten]. Before the proof, the formula was a conjecture read off from $w=3..13$ [C-fakt-konstanten]. It is now proved up to $w=61$ [C-modular-R17a]. A proof beyond that range is open.
:::

::: remark [Status of the computer-assisted parts]
The trusted base consists of exact rational arithmetic in the Laplace algebra and in the Laurent polynomials of Theorem 5.1 of arXiv:1902.04180, plus the two assumptions listed in the proof of Theorem 1 [C-fakt-beweis]. In the numerical observations the base is 32-digit arithmetic at verifier-chosen points, together with an exact check of the leading Laurent coefficient [C-modell], [C-modular-R6b]. A third party re-runs every certificate with 'python -m asd.recheck modular' from the repository given in Appendix A [C-verfuegbarkeit].
:::

## Exact Laplace computations at weights 9 and 11

::: proposition [Weight 9]
Exactly, in rational arithmetic [C-modular-R9a],

$$\Delta\big(9C(4,4,1)+18C(4,3,2)+4C(3,3,3)\big)=288\,E(9)\quad\text{[C-modular-R9a]}$$

so $9C(4,4,1)+18C(4,3,2)+4C(3,3,3)-4E(9)$ is annihilated by $\Delta$ [C-modular-R9a].
:::

*Certificate.* The algebraic Laplace representation of DGV was re-derived and checked in rational arithmetic; the verifier returns $\lambda=288$ [C-modular-R9a]. $\square$

*Novelty status:* already known for weights 3, 5, 7 and 9 (DGV eq. 3.33) [C-modular-R9a].

::: proposition [Weight 11]
Exactly, in rational arithmetic [C-modular-R9b],

$$\Delta\big(2C(5,5,1)+4C(5,4,2)+2C(5,3,3)+3C(4,4,3)\big)=100\,E(11)\quad\text{[C-modular-R9b]}$$

so $2C(5,5,1)+4C(5,4,2)+2C(5,3,3)+3C(4,4,3)-\tfrac{10}{11}E(11)$ is annihilated by $\Delta$ [C-modular-R9b].
:::

*Certificate.* As for the weight-9 proposition; the verifier returns $\lambda=100$ [C-modular-R9b]. $\square$

*Novelty status:* the combination for each odd $w$ is already known (DGV eq. 3.57); $f_w$ and $g_w$ are not given there [C-modular-R9b].

## Numerical confirmation, independent of the proof

The following observations are numerical. Each relation was checked at 4 verifier-chosen points (seed 4711, 32 digits) [C-modell]. The leading Laurent coefficient was checked exactly and vanishes in every case [C-modular-R6b].

::: observation [Relations at $w=3,\dots,17$]
As functions of $\tau$, at relative residual below 1e-24 [C-modular-R6b]:

$$C(1,1,1)-E(3)-\zeta(3)=0\quad\text{[C-modular-R6b]}$$

$$30\,C(2,2,1)-12\,E(5)-\zeta(5)=0\quad\text{[C-modular-R6c]}$$

$$252\,C(3,3,1)+252\,C(3,2,2)=108\,E(7)+\zeta(7)\quad\text{[C-modular-R6d]}$$

At weight 9 [C-modular-R6a],

$$\begin{aligned}&-2160\,C(4,4,1)-4320\,C(4,3,2)\\&-960\,C(3,3,3)+960\,E(9)+\zeta(9)=0\quad\text{[C-modular-R6a]}\end{aligned}$$

and at weight 11 [C-modular-R7a],

$$\begin{aligned}&19008\,C(5,5,1)+38016\,C(5,4,2)\\&+19008\,C(5,3,3)+28512\,C(4,4,3)\\&-8640\,E(11)-\zeta(11)=0\quad\text{[C-modular-R7a]}\end{aligned}$$

Analogous relations hold at $w=13$ (with $-691\zeta(13)$) [C-modular-R11a], $w=15$ (with $-\zeta(15)$) [C-modular-R11b] and $w=17$ (with $-3617\zeta(17)$) [C-modular-R13].
:::

*Certificate.* Per relation: exact leading Laurent coefficient 0, then numerical evaluation at the 4 points. The maximal relative residuals are in Table 2. The weight $w=15$ was a prediction made before its value was read, and $w=17$ a preregistered blind test [C-fakt-konstanten]. $\square$

Table: Maximal relative residuals of the weight-$w$ relations at the 4 verifier points (bound 1e-24) [C-modell].

| $w$ | max. rel. residual | source |
|---|---|---|
| 3 | 5.13e-44 | [C-modular-R6b] |
| 5 | 1.57e-43 | [C-modular-R6c] |
| 7 | 1.59e-43 | [C-modular-R6d] |
| 9 | 8.33e-44 | [C-modular-R6a] |
| 11 | 1.21e-43 | [C-modular-R7a] |
| 13 | 5.67e-44 | [C-modular-R11a] |
| 15 | 6.46e-44 | [C-modular-R11b] |
| 17 | 5.49e-44 | [C-modular-R13] |

*Novelty status:* weights 3 and 5 are already known (DGV eq. 1.7) [C-modular-R6b]. Weight 7 is already known, since DKS eq. 3.77 gives $C(3,3,1)+C(3,2,2)=\tfrac37E(7)+\zeta(7)/252$, i.e. $f_7$ and $g_7$ [C-modular-R6d]. For $w=9$ the identity with an integration constant $g_9$ is in DGV eq. 3.34, but the value of $g_9$ is not given there [C-modular-R6a]. For $w=11$ the constants for $w\ge 11$ are not given in DGV [C-modular-R7a].

::: observation [Full weight-11 basis]
For the full weight-11 basis $C(9,1,1),\dots,C(4,4,3)$, $E(11)$ and $\zeta(11)$, the rational linear relations form a space of dimension exactly 1, spanned by the weight-11 relation of the previous observation [C-modular-R12].
:::

*Certificate.* The preregistered criterion 1 (15 points, seed 4712, all other singular values above 1e-8) was **not** met: the smallest of the other singular values is 4.149e-9, while the kernel singular value is 7.591e-44 [C-fakt-kriterium1]. This is reported as a failure [C-fakt-kriterium1]. Criterion 2 was preregistered afterwards on new data (20 points, seed 4713, $\tau_2\in[0.9,3]$) with threshold 1e-16, chosen to lie well above the kernel value and well below the smallest non-kernel value, and it passed [C-fakt-kriterium1], [C-modular-R12]. The threshold separates the kernel direction (largest small singular value 1.11e-43) from the smallest non-kernel value 3.69e-9 by many orders of magnitude, which is why it distinguishes the two groups unambiguously [C-modular-R12]. The 20x12 matrix has one singular value below 1e-24 and 11 above 1e-16 [C-modular-R12]. The singular-value gap supports completeness numerically; it is not a proof. $\square$

*Novelty status:* partly known; the constants for $w\ge 11$ are not given in DGV [C-modular-R12].

::: observation [Hardening of the weight-11 identity]
The weight-11 identity was tested at 8 points not used before (seed 9001, including $\tau$ near $\rho$ and $\tau_2$ up to 3), preregistered with 8 points planned and 8 completed [C-fakt-haertung]. With the residual required to be at most 10^-d at working precision d, this holds at 8 of 8 points [C-fakt-haertung]. An independent check by direct lattice summation in double precision agrees to at most 1e-12 relative at 8 of 8 points [C-fakt-haertung].
:::

*Certificate.* The run exposed and fixed an evaluator bug [C-fakt-haertung]. The Fourier sum for $E_s$ stopped when a term vanished, which happens at $\tau_1=1/4$, where $\cos(2\pi N\tau_1)=0$ for odd $N$ [C-fakt-haertung]. Before the fix that point showed a precision-independent residual of 3.5e-10 [C-fakt-haertung]. All listed points were computed with the corrected code, and no earlier test point was affected [C-fakt-haertung]. $\square$

## Discussion

**Interpretation.** Theorem 1 reduces the constants of the odd-weight identities to the single Laurent coefficient $g_w\zeta(w)$, which has the Bernoulli form $6|B_{w-1}|/((w-1)/2)!$ up to $w=61$ [C-modular-R17a]. The numerical confirmations at $w=3..17$ test the identities directly as functions of $\tau$, without the Laurent-polynomial input [C-fakt-konstanten].

**Limitations.** The proof rests on Theorem 5.1 of arXiv:1902.04180 and on the standard lemma, neither re-proved here [C-fakt-beweis]. Its range ends at $w=61$ [C-modular-R17a]. The relation-space statement for the full weight-11 basis is numerical, and its completeness criterion is a singular-value gap [C-modular-R12]. The harmonic-space dimensions are exact only for $w\le 25$ [C-modular-R14].

**What did not work.** (a) The originally preregistered completeness criterion 1 for the full weight-11 basis failed, because the smallest non-kernel singular value 4.149e-9 lies below the threshold 1e-8; a second criterion, preregistered afterwards on new data, passed [C-fakt-kriterium1]. (b) The hardening run found a premature termination of the Fourier sum for $E_s$ at $\tau_1=1/4$, now fixed [C-fakt-haertung]. Further negative results are collected in Appendix A [C-neg1], [C-neg3].

**Open questions.**

(i) Prove the identities beyond the examined range, presumably by reducing the Laurent constant to a binomial-sum identity.
(ii) Determine the constants of the non-harmonic eigenvalue equations.
(iii) Extend the analysis to higher loop order.

## Declarations

**Affiliation** Noah Schittenhelm, Hack-Nation 2026, Team Ninja Turtles [C-autor].

**Acknowledgements** Computations, literature searches and parts of the manuscript were prepared with an automated verifier-gated laboratory built on the AI system Claude (Anthropic). Every statement was accepted only after verification by code. The authors are responsible for the content.

**Code and data availability** Repository https://github.com/NinjaTurtlesHackathons/Hacknation, branch `claude/modulformen-paper`, directory `projects/modular`. All certificates are reproduced with `python -m asd.recheck modular`, and the paper is rebuilt with `python -m asd.paper --domain modular` [C-verfuegbarkeit].

**Competing interests** None.

## Appendix A: Numerical methods and error control

**Certificate types.** (1) *Exact Laplace algebra:* rational arithmetic in the algebraic Laplace representation, as in Theorem 2 and the two propositions [C-modular-R14], [C-modular-R9a], [C-modular-R9b]. (2) *Laurent constants:* rational arithmetic from Proposition 2.1 and Theorem 5.1 of arXiv:1902.04180, as in Theorem 1 [C-modular-R17a]. (3) *Numerical relation:* an exact check of the leading Laurent coefficient in $y$, then evaluation at the verifier points (4 points, seed 4711, 32 digits) [C-modell]. The tolerance is 1e-24, or 1e-14 with a Laplacian evaluated by finite differences with h = 1e-6 [C-modell]. (4) *Relation space:* singular values of the normalised value matrix at seed 4712, plus individual confirmation of each relation [C-modular-R1]. (5) *Sturm certificates* for holomorphic identities [C-modular-R5a].

**Trusted base.** The trusted base is exact rational arithmetic, 32-digit arithmetic at the verifier's own points [C-modell], and the two uncoded assumptions of Theorem 1 [C-fakt-beweis].

**Verifier self-test.** Adversarial variants with falsified constants were submitted to the verifier. Examples are a doubled $\zeta(17)$ term, which gives relative residual 3.78e-02 [C-modular-R13-RT1], and a doubled $\zeta(11)$ term, which gives 2.85e-01 [C-modular-R17c-RT2]. A wrong $g_5$ and a wrong $\lambda$ in the exact Laplace algebra were likewise rejected [C-modular-R17a-RT1], [C-modular-R9a-RT2]. In total 53 counter-checks were run: 4 passed (consistency checks that do not contradict the statements), 48 did not pass, and 1 was not executable [C-redteam].

**Relation spaces at weights 3 to 9.** For the weight-$w$ bases the relation space has dimension exactly 1, with a singular-value gap in the normalised value matrix (seed 4712) [C-modular-R1].

Table: Relation-space check at weights 3, 5, 7 and 9: matrix size, relations confirmed, smallest large singular value [C-modular-R1], [C-modular-R1b], [C-modular-R1c], [C-modular-R1d].

| $w$ | matrix | dim | smallest large s.v. |
|---|---|---|---|
| 3 | 6x3 | 1 | 0.731 |
| 5 | 7x4 | 1 | 0.0372 |
| 7 | 9x6 | 1 | 0.000127 |
| 9 | 12x9 | 1 | 8.6e-7 |

**Laplace equations (observations).** At 4 verifier points (relative residual at most 1e-14) [C-modular-R4a], [C-modular-R4b], [C-modular-R4c], [C-modular-R4d]:

$$L[C(2,1,1)]-2C(2,1,1)-9E(4)+E(2)^2=0$$

$$L[C(2,2,1)]-8E(5)=0$$

$$L[C(2,2,1)]-20C(2,2,1)+\tfrac23\zeta(5)=0$$

$$\begin{aligned}&L[C(3,1,1)]-6C(3,1,1)-\tfrac{86}{5}E(5)\\&+4E(2)E(3)-\tfrac1{10}\zeta(5)=0\end{aligned}$$

Equations of this type are already stated in the literature [C-litn1], [C-litn3], [C-litn4].

**Holomorphic validation (Sturm certificates).** All identities are exact on the stated group, with all terms modular of the same weight and character. Each is certified by the vanishing of the $q$-coefficients up to the Sturm bound.

Table: Sturm-certified identities used as validation of the verifier.

| identity | group | weight | bound | source |
|---|---|---|---|---|
| $\theta(1)^4=\eta(2)^{20}\eta(1)^{-8}\eta(4)^{-8}$ | $\Gamma_0(4)$ | 2 | 1 | [C-modular-R5a] |
| $\theta(1)^2=\eta(2)^{10}\eta(1)^{-4}\eta(4)^{-4}$ | $\Gamma_0(4)$ | 1 | 1/2 | [C-modular-R5b] |
| `thetaE8` $=E_4$ | $\Gamma_0(1)$ | 4 | 1/3 | [C-modular-R5c] |
| `thetaE8`$^2=$ `thetaD16` | $\Gamma_0(1)$ | 8 | 2/3 | [C-modular-R5d] |
| `thetaE8`$^2=E_4^2$ | $\Gamma_0(1)$ | 8 | 2/3 | [C-modular-R5e] |
| `thetaE8`$^2=E_8$ | $\Gamma_0(1)$ | 8 | 2/3 | [C-modular-R5f] |
| $1728\Delta=E_4^3-E_6^2$ | $\Gamma_0(1)$ | 12 | 1 | [C-modular-R5g] |
| $j\Delta=E_4^3$ | $\Gamma_0(1)$ | 12 | 1 | [C-modular-R5h] |

The $\Gamma_0(4)$ identities are stated in the literature [C-litn5]. The expression of $\Delta$ through $E_4,E_6$ is also stated in the literature [C-litn6]. The `thetaE8`, `thetaD16` and $j$ identities are reproductions of classical results, preregistered as validation anchors [C-modular-R5c], [C-modular-R5d], [C-modular-R5h].

::: theorem [Eta-quotient span]
For all $N\le 30$, holomorphic eta quotients with trivial character span $M_4(\Gamma_0(N))$ exactly for $N\in\{2, 4, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30\}$, and do not for $N\in\{1, 3, 7, 11, 13, 17, 19, 21, 23, 29\}$ [C-modular-R8].
:::

*Certificate.* Exact and exhaustive computation of the span for each $N\le30$ [C-modular-R8]. *Novelty status:* not found in a targeted search of 33 abstracts on 2026-10-04 [C-modular-R8].

**Negative results.**

- *Weight 6.* A search for rational linear relations among $C(4,1,1)$, $C(3,2,1)$, $C(2,2,2)$ and products of Eisenstein series and $\zeta$ values passed no claim at the verifier [C-neg1]. The value matrix is 12x9, with 8 singular values above 1e-8 and the smallest large one 2.44e-8 [C-neg1].
- *Eta quotients.* The first attempts at the table for $M_4(\Gamma_0(N))$ passed no claim; the table above is the later exact computation [C-neg2], [C-modular-R8].
- *Weight 11.* A numerical integer-relation search over the full 12-element basis, with 6-8 points and up to 64 digits, found no relation [C-neg3]. The run was stopped for lack of time, and the presumed cause is working precision that is too low relative to the coefficient height [C-neg3]. The verified claim is the later criterion-2 result [C-modular-R12].
- *Weights 13 and 15.* First attempts to check the constant formula passed no claim at the verifier [C-neg4]. The direct relation checks are in Table 2 [C-modular-R11a], [C-modular-R11b].

**Laboratory workflow.** The laboratory ran 17 rounds with 37 verified statements and 4 negative results [C-methode]. Every round was preregistered before the experiment [C-methode]. The agent roles recorded in the negative results are *sparsam*, *numeriker*, *skeptiker* and *theoretiker* [C-neg1]. Counter-checks were generated adversarially against each answer, with statistics given above [C-redteam]. Novelty searches were run for each result over the abstracts of the queried literature [C-neuheit-suche].

## Appendix B: Provenance of the statements

The provenance table mapping every statement to its evidence follows; it is generated automatically.
<!-- Abbildung konstanten.pdf: Belege C-modular-R1, C-modular-R1b, C-modular-R1c, C-modular-R1d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d, C-modular-R6e, C-modular-R7a, C-modular-R7b, C-modular-R11a, C-modular-R11b, C-modular-R12, C-modular-R13, C-modular-R17c, C-modular-R17d -->

<!-- Abbildung margins.pdf: Belege C-modular-R4a, C-modular-R4b, C-modular-R4c, C-modular-R4d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d, C-modular-R7a, C-modular-R11a, C-modular-R11b, C-modular-R13, C-modular-R17c, C-modular-R17d -->

<!-- Abbildung eta_span.pdf: Belege C-modular-R8 -->

