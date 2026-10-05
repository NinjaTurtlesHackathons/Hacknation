# Closed forms for the constants in the odd-weight identities between dihedral modular graph functions

Noah Schittenhelm, Hack-Nation 2026, Team Ninja Turtles

# Closed forms for the constants in the odd-weight identities between dihedral modular graph functions

**Noah Schittenhelm** (Hack-Nation, Team Ninja Turtles)

## Abstract

Dihedral modular graph functions $C(a,b,c)$ of weight $w=a+b+c$ are the coefficients of the low-energy expansion of the one-loop closed-string amplitude. For each odd weight there is a combination $X_w$ whose Laplacian is a multiple of $E(w)$ [C-fakt-beweis]. We determine the constants in $X_w = f_w E(w) + g_w \zeta(w)$. Theorem 1 gives $f_w = 3((w-1)/2)!/w$ and $g_w = 6|B_{w-1}|/((w-1)/2)!$ for the odd weights $3 \le w \le 61$ examined [C-modular-R17a]. The proof combines exact rational Laplace algebra, a harmonicity argument and the Laurent constant term evaluated in rational arithmetic. It rests on two assumptions that were not machine-checked: a published theorem on Laurent polynomials and a standard lemma [C-fakt-beweis]. Theorem 2 shows exactly, for the weights $3 \le w \le 25$ examined, that the space of combinations with $\Delta X \in \mathbb{Q}\,E(w)$ has dimension 1 for odd $w$ and 0 for even $w$ [C-modular-R14]. Independent numerical confirmation at 32 digits [C-modell] covers $w = 3, 5, 7, 9, 11, 13, 15, 17$, with $w = 15$ a prediction and $w = 17$ a preregistered blind test [C-fakt-konstanten]. The full weight-11 basis has exactly one relation numerically [C-modular-R12]. A proof beyond the examined range is stated as a conjecture and remains open.

## Introduction

Two-loop modular graph functions $C(a,b,c)$ satisfy Laplace eigenvalue equations with inhomogeneous terms that are polynomial in non-holomorphic Eisenstein series [C-litn1]. D'Hoker, Green and Vanhove (DGV) obtained, for each odd weight, a combination $X_w$ that is annihilated by the Laplacian after subtracting a multiple of $E(w)$. The remaining additive constant of integration is fixed by the asymptotics at the cusp [C-litn1]. DGV give $f_w$ for $w\le 9$ and $g_w$ for $w=3$ and $w=5$, while $g_7$ and $g_9$ remain undetermined there [C-modular-R17a]. The value of $g_7$ appears explicitly in later work [C-litn2].

**Open question.** What are the exact closed forms of $f_w$ and $g_w$ for general odd $w$?

**Why it is hard.** The constant is the $\tau_2^0$ term of a Laurent polynomial [C-fakt-beweis]. That polynomial is known for each single $C_{u,v;w}$ [C-modular-R17a], but evaluating it for the DGV combination requires exact bookkeeping of growing coefficient lists. Numerical relation searches are limited by the coefficient height; for the full weight-11 basis the originally preregistered completeness criterion was failed [C-fakt-kriterium1].

**Contribution.** We evaluate the Laurent constant of $X_w$ exactly for the odd weights $3 \le w \le 61$ examined, obtain closed forms, and confirm them independently by numerics [C-modular-R17a].

**Summary of results.**

- Theorem 1 shows $X_w = f_w E(w) + g_w \zeta(w)$ with $f_w = 3((w-1)/2)!/w$ and $g_w = 6|B_{w-1}|/((w-1)/2)!$ for the odd weights $3 \le w \le 61$ examined (exact Laplace algebra plus Laurent constant in rational arithmetic) [C-modular-R17a].
- Theorem 2 shows that the space $\{X : \Delta X \in \mathbb{Q}E(w)\}$ has dimension 1 for odd $w$ and 0 for even $w$, for the weights $3\le w\le 25$ examined [C-modular-R14].

- Numerical results, independent of the proof, confirm the constants at $w = 3, 5, 7, 9, 11, 13, 15, 17$ and show that the full weight-11 basis has exactly one relation [C-fakt-konstanten, C-modular-R12].

## Setting

Let $\tau=\tau_1+i\tau_2$, $q=e^{2\pi i\tau}$ and $p=m\tau+n$ [C-modell]. The lattice sums use the normalisation $(\tau_2/(\pi|p|^2))^a$ [C-modell]:

Here $(a_1,a_2,a_3)=(a,b,c)$ and $w=a+b+c$ [C-modell]. $\zeta(k)$ is the Riemann zeta value and $B_n$ are Bernoulli numbers. The Laplacian is $\Delta=\tau_2^2(\partial_{\tau_1}^2+\partial_{\tau_2}^2)$. $E(w)$ is an eigenfunction, $\Delta E(w)=w(w-1)E(w)$ [C-fakt-beweis]. For odd $w$, $X_w$ is the DGV combination (eq. 3.57), normalised so that $\Delta X_w=w(w-1)f_wE(w)$ [C-modular-R14].

Numerical parameters of the verifier [C-modell]:

- four random points, seed 4711, with $|\tau_1|\le 1/2$ and $1\le\tau_2\le 2.5$ [C-modell];
- working precision of 32 digits [C-modell];
- tolerance 1e-24 for relative residuals, and 1e-14 when a Laplacian is involved [C-modell];
- fourth-order finite-difference Laplacian with step $h=$ 1e-6 [C-modell].

## Closed forms for odd weight

::: theorem [Closed forms, $w\le 61$]
For the odd weights $3\le w\le 61$ examined [C-modular-R17a],
$$X_w=f_wE(w)+g_w\zeta(w),\quad f_w=\frac{3((w-1)/2)!}{w},\quad g_w=\frac{6|B_{w-1}|}{((w-1)/2)!}\quad\text{[C-modular-R17a]}$$
:::

*Proof.* The proof has three steps and a fourth that supplies the constant [C-fakt-beweis].

1. Exact rational computation in the algebraic Laplace representation gives $\Delta X_w=w(w-1)f_wE(w)$ with no other terms. Since $\Delta E(w)=w(w-1)E(w)$, it follows that $\Delta(X_w-f_wE(w))=0$ [C-fakt-beweis].
2. $X_w-f_wE(w)$ is $SL(2,\mathbb{Z})$-invariant and of polynomial growth at the cusp. By the standard argument used by DGV it is therefore constant [C-fakt-beweis].
3. The constant is the $\tau_2^0$ term of the Laurent polynomial of $X_w$ [C-fakt-beweis]. It was computed in rational arithmetic from Proposition 2.1 and Theorem 5.1 of D'Hoker-Kaidi, with the transcription checked against their eq. 5.19 [C-modular-R17a]. All Laurent terms not involving products of zeta values agree with those of $f_wE(w)+g_w\zeta(w)$ (consistency check) [C-modular-R17a]. The constant equals $g_w\zeta(w)$ with $g_w=6|B_{w-1}|/((w-1)/2)!$ for the odd weights $3\le w\le 61$ examined [C-modular-R17a].

Assumptions not checked by code are the correctness of Theorem 5.1 of D'Hoker-Kaidi and the standard lemma in step 2 [C-fakt-beweis]. Theorem 5.1 is proved there in its Appendix A; its conjectural part concerns only the coefficient of $\tau_2^{2-w}$ and is not used [C-fakt-beweis]. Examples are $g_3=1$, $g_5=1/10$, $g_7=1/42$, $g_9=1/120$ [C-modular-R17a].

Novelty status: partly known.  Closed forms of $f_w$ and $g_w$ for general odd $w$ and their proof for $w\ge 9$ are not given there [C-modular-R17a].

Table: Constants $f_w$ and $g_w$ in $X_w=f_wE(w)+g_w\zeta(w)$ (DGV normalisation of $X_w$), exact for odd $3\le w\le 25$ [C-fakt-konstanten].

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

## Uniqueness of the harmonic combination

::: theorem [Dimension of the harmonic space]
 For odd $w$ it is spanned by the DGV combination, with $\Delta X=w(w-1)f_wE(w)$ and $f_w=3((w-1)/2)!/w$ [C-modular-R14].
:::

*Certificate.* The statement was verified exactly for the weights $3\le w\le 25$ examined, with the algebraic Laplace representation of DGV, re-derived and evaluated in rational arithmetic [C-modular-R14]. Novelty status: partly known. The one-dimensionality of the eigenspace for odd weight, its vanishing for even weight and the combination $X_w$ are known. 

::: proposition [Laplace equations at $w=9$ and $w=11$]
$\Delta\big(9C(4,4,1)+18C(4,3,2)+4C(3,3,3)\big)=288\,E(9)$ and $\Delta\big(2C(5,5,1)+4C(5,4,2)+2C(5,3,3)+3C(4,4,3)\big)=100\,E(11)$ [C-modular-R9a, C-modular-R9b].
:::

*Certificate.* Both equations were obtained in the algebraic Laplace representation and checked in exact rational arithmetic. The verifier returns a single value of $\lambda$ in $\Delta X=\lambda E(w)$ [C-modular-R9a, C-modular-R9b]. Novelty status: the $w=9$ equation is already known [C-modular-R9a]. For $w=11$ the combination is known, but $f_w$ and $g_w$ are not given there [C-modular-R9b].

::: conjecture [Beyond the examined range]
The identity $X_w=f_wE(w)+g_w\zeta(w)$ with the closed forms of Theorem 1 holds beyond the examined range of odd weights [C-fakt-konstanten].
:::

Before the proof, this was a conjecture read off from $w = 3..13$ [C-fakt-konstanten]. 

## Numerical confirmation, independent of the proof

The statements in this section are numerical (32 digits, four verifier-chosen points) combined with the exact vanishing of the leading Laurent coefficient [C-modular-R6b]. They do not use the proof of Theorem 1.

::: example [Weight 3]
$C(1,1,1)-E(3)-\zeta(3)=0$ as functions of $\tau$ [C-modular-R6b].
:::

*Certificate.* The exact leading Laurent coefficient in $y^3$ vanishes, and at the four verifier points the maximal relative residual is 5.13e-44 against the bound 1e-24 [C-modular-R6b]. This identity is already known [C-litn1].

::: example [Weight 5]
$30\,C(2,2,1)-12\,E(5)-\zeta(5)=0$ as functions of $\tau$ [C-modular-R6c].
:::

*Certificate.* The leading coefficient in $y^5$ vanishes exactly, and the maximal relative residual is 1.57e-43 [C-modular-R6c]. This identity is already known [C-litn1].

::: example [Weight 7]
$252\,C(3,3,1)+252\,C(3,2,2)-108\,E(7)-\zeta(7)=0$ as functions of $\tau$ [C-modular-R6d].
:::

*Certificate.* The leading coefficient in $y^7$ vanishes exactly, and the maximal relative residual is 1.59e-43 [C-modular-R6d]. This is $f_7$ and $g_7$ in the notation above, already known [C-litn2].

::: observation [Weight 9]
$960\,E(9)+\zeta(9)-2160\,C(4,4,1)-4320\,C(4,3,2)-960\,C(3,3,3)=0$ as functions of $\tau$ [C-modular-R6a].
:::

*Certificate.* The leading coefficient in $y^9$ vanishes exactly, and the maximal relative residual is 8.33e-44 [C-modular-R6a]. Novelty status: partly known. DGV give the identity with an undetermined constant $g_9$, whose value is not given there [C-modular-R6a].

Here $E(w)$ is the lattice sum of the Setting and $\zeta(w)$ the Riemann zeta value at $w$.

Table: Numerical checks of the integer-normalised relations at weights 11, 13, 15, 17; the third column is the maximal relative residual at the four verifier points (bound 1e-24) [C-modular-R7a, C-modular-R11a, C-modular-R11b, C-modular-R13].

| $w$ | coefficients of $E(w)$ and $\zeta(w)$ | residual | claim |
|---|---|---|---|
| 11 | $-8640\,E(11)$, $-\zeta(11)$ | 1.21e-43 | [C-modular-R7a] |
| 13 | $-54432000\,E(13)$, $-691\,\zeta(13)$ | 5.67e-44 | [C-modular-R11a] |
| 15 | $-725760\,E(15)$, $-\zeta(15)$ | 6.46e-44 | [C-modular-R11b] |
| 17 | $-24385536000\,E(17)$, $-3617\,\zeta(17)$ | 5.49e-44 | [C-modular-R13] |

Each of the four relations has vanishing exact leading Laurent coefficient (in $y^{11}$, $y^{13}$, $y^{15}$, $y^{17}$) [C-modular-R7a, C-modular-R11a, C-modular-R11b, C-modular-R13]. The value at $w = 15$ was a prediction made before its value was read, and $w = 17$ was a preregistered blind test [C-fakt-konstanten]. Novelty status: partly known. Existence and combination for each odd $w$ are known, but $f_w$ and $g_w$ for $w\ge 11$ are not given there [C-modular-R7a].

::: observation [Full weight-11 basis]
The rational linear relations among $C(9,1,1)$, $C(8,2,1)$, $C(7,3,1)$, $C(7,2,2)$, $C(6,4,1)$, $C(6,3,2)$, $C(5,5,1)$, $C(5,4,2)$, $C(5,3,3)$, $C(4,4,3)$, $E(11)$, $\zeta(11)$ form a space of dimension exactly 1 (weight 11), spanned by the weight-11 relation of the table [C-modular-R12].
:::

 The threshold was chosen so as to separate the null value 1.11e-43 from the smallest large singular value 3.69e-9 [C-modular-R12]. One singular value is below 1e-24 and 11 are above 1e-16 [C-modular-R12].  Novelty status: partly known; see the weight-11 entry above [C-modular-R12].

::: observation [Hardening of the weight-11 identity]
 An independent direct lattice summation in double precision agrees to at most 1e-12 relative at 8 of 8 points [C-fakt-haertung].
:::

*Certificate.* The criterion operationalises the preregistered expectation that the residual decreases with precision; an exact 0 counts as below rounding resolution [C-fakt-haertung]. The run exposed and fixed an evaluator bug [C-fakt-haertung]. The Fourier sum for $E_s$ stopped when a term vanished, which happens at $\tau_1=1/4$ where $\cos(2\pi N\tau_1)=0$ for odd $N$ [C-fakt-haertung]. Before the fix that point showed a precision-independent residual of 3.5e-10 [C-fakt-haertung]. All listed points were computed with the corrected code, and no earlier test point was affected [C-fakt-haertung].

::: remark [Status of the computer-assisted parts]
The trusted base consists of the following.

- **Exact rational arithmetic.** It covers the Laplace algebra of Theorems 1 and 2 and the Laurent constants [C-fakt-beweis].
- **The 32-digit evaluator.** It covers the numerical observations, with the tolerances of the Setting [C-modell].

Not machine-checked are Theorem 5.1 of D'Hoker-Kaidi and the harmonic-implies-constant lemma [C-fakt-beweis]. A third party re-runs all certificates with the commands in the Declarations [C-verfuegbarkeit]. Statements marked numerical are not proofs.
:::

## Discussion

 

**Limitations.** The proof depends on two external ingredients, listed in the status remark [C-fakt-beweis]. The range $w\le 61$ is a computational bound, not a theorem beyond it [C-modular-R17a]. Numerical confirmation certifies values at sampled points together with exact leading coefficients, for the weights $w = 3, 5, 7, 9, 11, 13, 15, 17$ examined [C-fakt-konstanten].

**What did not work.**

 It was reported openly, and criterion 2, preregistered afterwards on new data, passed [C-fakt-kriterium1, C-modular-R12].
- The hardening run found an evaluator bug at $\tau_1=1/4$ (early termination of the Fourier sum when a term vanished). It was fixed, and all listed points use the corrected code [C-fakt-haertung].

Further negative results are collected in Appendix A.

**Open questions.**

(i) Is there a proof of $X_w=f_wE(w)+g_w\zeta(w)$ beyond the examined range, i.e. of Conjecture 1, presumably via a binomial-sum identity for the Laurent constant?

(ii) What are the constants in the non-harmonic Laplace eigenvalue equations for $C(a,b,c)$?

(iii) Do analogous closed forms exist at higher loop order?

## Declarations

**Affiliation** Noah Schittenhelm, Hack-Nation, Team Ninja Turtles.

**Acknowledgements** Computations, literature searches and parts of the manuscript were prepared with an automated verifier-gated laboratory built on the AI system Claude (Anthropic). Every statement was accepted only after verification by code. The authors are responsible for the content.

**Code and data availability** Repository https://github.com/NinjaTurtlesHackathons/Hacknation, branch `claude/modulformen-paper`, directory `projects/modular`. All certificates are reproduced with `python -m asd.recheck modular`, and the paper is rebuilt with `python -m asd.paper --domain modular` [C-verfuegbarkeit].

**Competing interests** None.

## Appendix A: Numerical methods and error control

**Certificate types.**

1. *Exact Laplace algebra and Laurent constants:* rational arithmetic, no floating point [C-fakt-beweis].
2. *Function relations:* the leading Laurent coefficient is checked exactly, then numerically at four verifier points (seed 4711, 32 digits, tolerance 1e-24, or 1e-14 with the finite-difference Laplacian of step 1e-6) [C-modell].
3. *Relation spaces:* completeness is shown by a singular-value gap of the normalised value matrix at independent points (seed 4712) [C-modular-R1].


**Validation of the verifier on known results.**

 The singular values of the normalised matrices show one value below 1e-24; for $w = 3$ the matrix is 6x3 with smallest large value 0.731 [C-modular-R1, C-modular-R1b, C-modular-R1c, C-modular-R1d].
- Laplace equations: $\Delta C(3,1,1)-6C(3,1,1)-\tfrac{86}{5}E(5)+4E(2)E(3)-\tfrac1{10}\zeta(5)=0$ with residual 1.63e-25 [C-modular-R4a]. $\Delta C(2,1,1)-2C(2,1,1)-9E(4)+E(2)^2=0$ with 2.39e-25 [C-modular-R4b]. $\Delta C(2,2,1)-8E(5)=0$ with 6.99e-26 [C-modular-R4c]. $\Delta C(2,2,1)-20C(2,2,1)+\tfrac23\zeta(5)=0$ with 6.74e-26 [C-modular-R4d].
- Holomorphic identities (exact, Sturm certificates):
  - $\theta(1)^4=\eta(2)^{20}\eta(1)^{-8}\eta(4)^{-8}$ on $\Gamma_0(4)$, with coefficients $q^0..q^{11}$ vanishing and Sturm bound 1 [C-modular-R5a]. The weight-1 version $\theta(1)^2=\eta(2)^{10}\eta(1)^{-4}\eta(4)^{-4}$ also holds [C-modular-R5b]. The relation of eta quotients to theta functions is stated in [C-litn5].
  - $\theta_{\mathrm{E8}}=E_4$ [C-modular-R5c], $\theta_{\mathrm{E8}}^2=\theta_{\mathrm{D16}}$ [C-modular-R5d], $\theta_{\mathrm{E8}}^2=E_4^2$ [C-modular-R5e] and $\theta_{\mathrm{E8}}^2=E_8$ [C-modular-R5f].
  - $1728\,\Delta=E_4^3-E_6^2$ [C-modular-R5g], a classical fact stated in [C-litn6], and $j\Delta=E_4^3$ [C-modular-R5h].
- Eta quotients with trivial character span $M_4(\Gamma_0(N))$ exactly for $N\in\{2, 4, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30\}$ and not for $N\in\{1, 3, 7, 11, 13, 17, 19, 21, 23, 29\}$ (exact, exhaustive, $N\le 30$) [C-modular-R8].

**Negative results.**

- At weight 6, no claim passed for the relation space of $C(4,1,1)$, $C(3,2,1)$, $C(2,2,2)$ and products of Eisenstein series and zeta values; the 12x9 matrix showed 8 singular values above 1e-8 and none below 1e-24 [C-neg1].
- No claim passed for the eta-span table in the first attempts [C-neg2].
 The run was aborted, and the presumed cause is precision too low relative to the coefficient height [C-neg3].
- No claim passed in the first attempt at the weight-13 and weight-15 constants [C-neg4]. Both relations were later confirmed [C-modular-R11a, C-modular-R11b].

**Laboratory workflow.** The laboratory ran 17 rounds with 37 verified statements and 4 negative results [C-methode]. Every round was preregistered before the experiment [C-methode]. Statements were proposed by agents in the roles *sparsam*, *numeriker*, *skeptiker* and *theoretiker* [C-neg1], and accepted only if the verifier passed them. Adversarial counter-checks (red team) numbered 53 in total; 4 passed without contradicting the statement, 48 did not pass, and 1 was not executable [C-redteam]. The verifier rejected falsified variants, such as a doubled $\zeta(17)$ coefficient [C-modular-R13] or a wrong $\zeta(5)$ source term [C-modular-R4d].

## Appendix B: Provenance of the statements

The provenance table mapping every statement to its evidence follows (it is generated automatically).
<!-- Abbildung konstanten.pdf: Belege C-modular-R1, C-modular-R1b, C-modular-R1c, C-modular-R1d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d, C-modular-R6e, C-modular-R7a, C-modular-R7b, C-modular-R11a, C-modular-R11b, C-modular-R12, C-modular-R13, C-modular-R17c, C-modular-R17d -->

<!-- Abbildung margins.pdf: Belege C-modular-R4a, C-modular-R4b, C-modular-R4c, C-modular-R4d, C-modular-R6a, C-modular-R6b, C-modular-R6c, C-modular-R6d, C-modular-R7a, C-modular-R11a, C-modular-R11b, C-modular-R13, C-modular-R17c, C-modular-R17d -->

<!-- Abbildung eta_span.pdf: Belege C-modular-R8 -->

