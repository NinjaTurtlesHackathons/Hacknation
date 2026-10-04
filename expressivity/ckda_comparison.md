# Comparison with Complex KDA (arXiv:2609.24797)

Scout note, literature only. Source: https://arxiv.org/html/2609.24797 (v1), fetched 2026-10-04 with curl and
converted to text (math kept as LaTeX alt-text). Every quote below was copied from that fetched HTML, and each is marked
"verified verbatim in fetched HTML". The paper is licensed CC BY 4.0, so attributed quotation is permitted. Two
statements (Theorem 8 and the head-count line of Proposition 21) were cut off in our text conversion where the alt-text
contains a `<` sign. They are quoted only up to the cut and paraphrased after it.

## 1. Bibliographic data and abstract

- **Title:** Complex KDA: Understanding and Enhancing the Expressivity of Kimi Delta Attention
- **Authors (in the order given):** Julien Siems, Riccardo Grazzi, Korbinian Pöppel, Jaisidh Singh, Arber Zela, Timur
  Carstensen, Jenia Jitsev, Frank Hutter, Volkan Cevher, Antonio Orvieto, Aaron Klein (with an equal-contribution mark).
- **Identifier:** arXiv:2609.24797v1 [cs.LG], 21 Sep 2026, CC BY 4.0.
- **Abstract (excerpt):** "A single CKDA layer can track every finite group isomorphic to a subgroup of $\mathrm{SO}(3)$ ,
  and many state-tracking results use one fewer layer for CKDA compared to other diagonal-plus-rank-one Linear RNNs."
  (Abstract; verified verbatim in fetched HTML.) Another abstract sentence describes the CKDA transitions as remaining
  "diagonal-plus-rank-one and non-expansive, while reaching the state-tracking expressivity of DeltaProduct2" (verified
  verbatim in fetched HTML).
- **The S5 contribution, as the introduction states it:** "We rule out one-layer $S_{5}$ tracking for CKDA and
  DeltaProductk ( $k\leq 3$ ) with non-expansive transitions and finite reachability (Theorem 4)." (Sec. 1; verified
  verbatim in fetched HTML.)

## 2. Their relevant results and the assumptions behind them

| # | Statement (short) | Model / transition class | Alphabet | Decoder | Norm | Reachability / precision |
|---|---|---|---|---|---|---|
| Thm 1 / Thm 6 | Every orthogonal DPR1 matrix is a signed Householder $(I-2kk^\top)S$ | single matrix | n/a | n/a | orthogonal | n/a |
| Thm 8 | A CKDA matrix has at most one non-real eigenvalue pair (requires $\beta>1$ and a negative gate entry) | CKDA | n/a | n/a | n/a | n/a |
| Thm 9 | Non-expansive diagonal + rank $\le r$: at most $r$ non-real unit-circle pairs | DPLR, $\|A\|_2\le1$ | n/a | n/a | non-expansive | n/a |
| Lemma 11 | A finite-state tracker gives a group $\Gamma$ and a surjective homomorphism $p:\Gamma\to G$ | signed Householder, orthogonal, $B=0$, $S_0=I$ | all of $G$ | arbitrary | orthogonal | finite |
| Prop 13 | Axis test: a rotation of $\mathbb R^3$ (other than $0$ or $\pi$) is signed Householder iff its axis has a zero coordinate. The identity and half-turns always are. | $\mathcal{SH}_3$ | n/a | n/a | orthogonal | n/a |
| Prop 14 | $\mathbb Z_n$ and $D_n$ are realised in $d=2$ | CKDA | all | bijective | orthogonal | finite, exact |
| Prop 15 | $S_4$ and $A_4$ are realised in $d=3$ (cube rotated by $45^\circ$) | CKDA | all | bijective | orthogonal | finite, exact |
| Thm 17 | No finite-state tracker of $A_5$ in $d=3$, even with an arbitrary decoder (proof uses $\psi(Q)=\det(Q)Q$) | $\mathcal{SH}_3$ | all | arbitrary | orthogonal | finite |
| Prop 18 / Cor 19 | $A_5$ is tracked in $d=4$ with a many-to-one quadratic decoder and $\le 7200$ reachable states | CKDA, gate $\mathrm{Diag}(-1,1,1,1)$, $\beta=2$ | all | many-to-one | orthogonal | finite, exact |
| Thm 3 | One CKDA head tracks every finite subgroup of $SO(3)$ | CKDA | all | as above | orthogonal | finite, fixed exact datatype |
| Prop 20 | Removes the additive term and restricts to a common invariant subspace on which every $A_g$ is orthogonal; eigenvalue multiplicities do not increase | any affine $A_gS+B_g$ | all | arbitrary | **$\|A_g\|_2\le1$** | **finite** |
| Prop 21 | The same reduction for independent heads; joint matrices generate a finite group $\Gamma\twoheadrightarrow G$ | block-diagonal heads | all | arbitrary joint | $\le1$ per head | finite per head |
| Thm 4 / Thm 22 | No one-layer tracker of $S_5$ if every head transition has $\|A\|_2\le1$ and at most one non-real unit-circle pair | any such matrices, any number of heads, arbitrary $B$ | **all of $S_5$** | arbitrary, many-to-one | **non-expansive** | **finite under exact updates** |
| Lemma 23 | Two same-angle planar rotations of order divisible by 5 in a finite group: commutator$^{10}=I$ | $O(n)$ | n/a | n/a | orthogonal | finite group |
| C.6 "Consequences" | DeltaProduct$_k$ with $k\le3$ is excluded; $k=4$ suffices; so 4 is the minimum | Gated DeltaProduct, $\beta_j\in[0,2]$, scalar gate $\alpha\in[0,1]$ | all | arbitrary | non-expansive | finite |

Supporting quotes (each verified verbatim in fetched HTML):

- **Thm 4 (Sec. 5):** "Suppose every head transition ${\bm{A}}$ satisfies $\|{\bm{A}}\|_{2}\leq 1$ and has at most one
  non-real conjugate eigenvalue pair on the unit circle, counted with algebraic multiplicity. Then a single recurrent
  layer with any finite number of independent heads cannot track $S_{5}$ when the updates of each head reach only
  finitely many states."
- **Thm 22 (App. C.6), extra scope:** "This holds for arbitrary state dimensions, input-dependent additive matrices, and
  many-to-one joint state decoders."
- **The alphabet (App. B.1):** "Throughout our group results, inputs range over all of $G$ . Restricting inputs to a
  chosen set of generators gives a different task."
- **Decoder (App. B.1, Def. B.1):** "The decoder need not be injective, and $\mathcal{S}$ need not be finite."
- **Additive term (App. B.2):** "The $S_{5}$ lower bound allows arbitrary additive matrices ${\bm{B}}({\bm{x}}_{t})$ ,
  and therefore also covers the CKDA additive term."
- **Finite reachability versus datatype (App. B.4):** "Finitely many rounded states do not imply finitely many exact
  states, so choosing a finite datatype alone does not justify this reduction." Also: "Replacing finite reachability by
  a suitable datatype and casting assumption remains open."
- **Why the norm is needed (App. B.4):** "We assume finite reachability in the $S_{5}$ obstruction to simplify the
  analysis: together with non-expansion, it lets us remove the additive term and restrict to orthogonal transitions
  (Propositions 20 and 21)."
- **Prop 20 (App. C.5), hypothesis:** "with $\|{\bm{A}}_{g}\|_{2}\leq 1$ for every $g$ ." Conclusion: "Every eigenvalue
  of $\widehat{{\bm{A}}}_{g}$ is an eigenvalue of ${\bm{A}}_{g}$ with no increase in algebraic multiplicity. Both
  decoders may be many-to-one."
- **Prop 20, proof idea:** "We first choose a word whose linear part has minimum Frobenius norm and repeat it until it
  acts as a projection without changing the decoded value. Minimality and non-expansion then force the original
  matrices to act orthogonally on its image."
- **Prop 21 (App. C.5):** "The joint transition matrices generate a finite group $\Gamma$ with a surjective homomorphism
  $p:\Gamma\to G$ taking the transition for each input $g$ to $g$ ."
- **Counting pairs and Householder factors (App. C.6, "Consequences"):** "Since $\alpha_{g}$ is real, at most $k$
  eigenvalues can be non-real, counted with algebraic multiplicity. They occur in conjugate pairs, so $k\leq 3$ allows
  at most one such pair per head."
- **The Householder count (App. C.6):** "Together with the lower bound, this proves that four is the minimum number of
  Householder transformations needed for single-layer Gated DeltaProduct tracking of $S_{5}$ under these assumptions."
- **Lemma 23:** "Suppose they are planar rotations through the same angle, possibly in different planes, and their
  common order is a multiple of five." Conclusion: "$({\bm{R}}_{1}{\bm{R}}_{2}{\bm{R}}_{1}^{\top}{\bm{R}}_{2}^{\top})^{10}={\bm{I}}.$"
- **The proof uses only two letters (App. C.6):** "Let $c=(12345)$ and $t=(12)$ ." Also: "But direct permutation
  composition gives $p({\bm{C}})=cbc^{-1}b^{-1}=(142)$ , so $e=p({\bm{C}}^{10})=(142)^{10}=(142)\neq e,$ a
  contradiction."
- **Thm 9 (App. A.4):** "Then ${\bm{A}}$ has at most $r$ non-real conjugate pairs of eigenvalues on the unit circle. In
  particular, a non-expansive rank-one DPLR transition has at most one such pair."
- **Thm 8 (App. A.3), quoted up to the conversion cut:** "The matrix
  ${\bm{A}}=({\bm{I}}-\beta{\bm{k}}{\bm{k}}^{\top})\operatorname{Diag}({\bm{\alpha}})$ has at most one pair
  $\lambda,\lambda^{*}$ of non-real eigenvalues, and such a pair can occur only if $\beta>1$ and $\alpha_{i}$". The
  sentence continues with a negative gate entry; Sec. 4 summarises the condition as "requiring both $\beta>1$ and a
  negative gate entry".
- **Thm 3 (Sec. 5):** "Specifically, it realizes every finite cyclic ( $\mathbb{Z}_{n}$ ) and dihedral group (
  $D_{n}$ ) in $d=2$ and $A_{4},S_{4}$ in $d=3$ , and tracks $A_{5}$ in $d=4$ . These constructions use orthogonal
  transitions and a fixed exact datatype."
- **Thm 17 (App. C.4.1):** "The group $A_{5}$ admits no finite-state signed-Householder tracking in dimension three,
  even with an arbitrary decoder."
- **The $\det(Q)Q$ map (Thm 17 proof):** "In three dimensions, multiplying an orientation-reversing orthogonal matrix by
  $-{\bm{I}}_{3}$ makes it orientation-preserving." Also: "The map identifies at most a matrix and its negative, since
  its kernel $K$ is contained in $\{\pm{\bm{I}}_{3}\}$ ."
- **Half-turn as a signed Householder (Prop 13 proof):**
  "$2{\bm{a}}{\bm{a}}^{\top}-{\bm{I}}=({\bm{I}}-2{\bm{a}}{\bm{a}}^{\top})(-{\bm{I}})={\bm{H}}_{{\bm{a}}}(-{\bm{I}}),$"
- **Cor 19:** "There are at most $7200$ reachable hidden matrices, and the decoder is many-to-one on this set."
- **Footnote 1 (Sec. 5):** "If inputs are restricted to identity and swaps, one-layer DeltaNet suffices (Grazzi et al., 2025)."
- **Lemma 11:** "For a finite-state signed-Householder tracker, $\mathcal{R}=\Gamma:=\langle{\bm{A}}_{h}:h\in G\rangle$ ,
  and its decoder $p:\Gamma\to G$ is a surjective homomorphism."
- **Grazzi et al. as summarised by them (App. B.4):** "Their single-layer argument also rules out tracking
  $\mathbb{Z}_{n}$ for every $n>2$ when all transition eigenvalues are real."

## 3. How their results relate to ours, point by point

### 3.1 Our L2 (compression lemma) versus their Prop 20 / Prop 21 / Lemma 11

Their argument and ours share the same skeleton: (i) finite reachability makes the word maps a finite monoid; (ii) an
idempotent word that does not change the decoded value; (iii) restriction to its image; (iv) a finite group mapping onto
$G$ through the decoder. Their Prop 21 produces exactly the data our $h^*$ is defined with: a finite group $\Gamma$, a
surjection $p:\Gamma\to G$, and generators $A_g\mapsto g$. In other words, they work implicitly with "covering groups"
but never define a complexity invariant over them.

The differences matter:

| | Ours (L2) | Theirs (Prop 20/21) |
|---|---|---|
| Norm assumption | **none** | $\|A_g\|_2\le 1$ (essential: it makes $E$ an orthogonal projection and keeps $A_g$ itself on $\mathrm{im}\,E$) |
| Choice of idempotent | idempotent in the minimal two-sided ideal $K$; group $eTe$ | word with minimal Frobenius norm, repeated $N=|\mathcal R|!$ times |
| Compressed maps | $A(u)A(s)|_U$ (a *compression*, not a restriction of $A(s)$) | $A_g|_{\mathrm{im}E}$ (a genuine *restriction* of $A_g$) |
| Invariant preserved | $\mathrm{rank}(\cdot - I)\le\mathrm{rank}(A(s)-I)$ | full spectrum: eigenvalues and algebraic multiplicities |
| Resulting rep | faithful rep of $\Gamma'$, rank bound $k$ | orthogonal rep of $\Gamma$, spectral bound per head |
| Heads | a single head with a matrix state $d\times m$ | any number of independent heads |
| Singular $A$ ($\beta=1$, zero gate) | allowed | allowed (non-expansive includes singular) |
| Additive term, decoder | arbitrary | arbitrary |

Consequence: neither result contains the other. **Our L2 is new in dropping non-expansion.** It is also the only one of
the two that yields an exact characterisation (Theorem 1) for every finite group and alphabet. Theirs is stronger in two
directions: (a) it keeps spectral information, which a gated or CKDA transition needs because its $\mathrm{rank}(A-I)$ is
not small; (b) it handles several heads, where ranks add up and our per-letter rank bound would not apply head by head.
The asymmetry has a mechanical reason. Without the norm, the compressed map $A(u)A(s)$ need not have the eigenvalues of
$A(s)$, but its rank defect from $I$ is still bounded. The rank bound survives compression; the spectral bound needs the
restriction that non-expansion provides.

### 3.2 Our L4 (a letter of order ≥ 3 needs ≥ 2 factors)

Not stated in this paper. Closest anticipations: (i) the Grazzi et al. (2025) single-layer argument as they summarise it
("rules out tracking $\mathbb{Z}_{n}$ for every $n>2$ when all transition eigenvalues are real", App. B.4). That result
is set under a finite-datatype casting convention, not finite exact reachability. (ii) Their counting remark that rank
$k$ allows at most $k$ non-real eigenvalues ($k=1$: none). Our L4 is the covering-group version: any faithful
finite-group rep with $\mathrm{rank}(\rho(t_s)-I)\le 1$ has $t_s^2=1$. Combined with L2, this gives a norm-free,
decoder-free, B-free lower bound. Overlap in spirit, so cite Grazzi et al. 2025; the exact statement is ours.

### 3.3 Our Theorem 1 ($k$-Householder realisable $\iff k\ge h^*(G,\Sigma)$)

Not anticipated. They prove instances only: $S_5$ needs 4 (for non-expansive DeltaProduct), SO(3) subgroups via CKDA,
and the impossibility of 3-dimensional $A_5$ for CKDA. They have no invariant $h^*$, no sufficiency theorem for general
$(H,\pi,\rho)$ (our L3 via Cartan–Dieudonné), and no alphabet dependence beyond footnote 1.

### 3.4 $S_5$ with all inputs: does their Theorem 4 close our interval $h^*(S5,\text{all})\in[2,4]$?

**Yes. Their Theorem 22 applied to our compressed representation gives $h^*(S_5,\text{all})=4$.** The argument
[hand, needs our check]:

1. Suppose $h^*(S_5,\text{all})\le 3$: there are a finite $H$, $\pi:H\twoheadrightarrow S_5$, lifts $t_s$ generating
   $H$, and a faithful real $\rho$ with $\mathrm{rank}(\rho(t_s)-I)\le 3$.
2. Average an inner product over $H$ and change basis so that $\rho$ is orthogonal. The rank is unchanged by
   similarity.
3. Build the tracker from L3/Lemma 11: matrix state $S_0=I$, $A_s=\rho(t_s)$, $A_e=I$, $B=0$, decoder
   $S\mapsto\pi(\rho^{-1}(S))$. One head, finitely many reachable states ($|H|$), exact updates, inputs = all of
   $S_5$, $\|A_s\|_2=1$.
4. $\mathrm{rank}(A_s-I)\le 3$ means at most 3 eigenvalues differ from 1, hence at most one non-real conjugate pair.
   This is exactly the counting in their "Consequences" paragraph with $\alpha=1$.
5. Thm 22 then says no such tracker exists. Contradiction, so $h^*\ge 4$. With our $h(S_5,\text{all})=4$
   (standard 4-dimensional rep, rank of a 5-cycle = 4) we get $h^*=4$.

Which of their assumptions our setting meets:

- **Non-expansive:** the *reduced* representation from step 2 is orthogonal, so yes. The original architecture need
  not be: our L2 maps *any* finite-state realisation with $\mathrm{rank}(A(s)-I)\le 3$ (expansive, non-unit keys,
  $\beta\notin[0,2]$) to such a representation. **So L2 + their Thm 22 extends their $S_5$ lower bound to the
  norm-free rank-$k$ setting.** That extension is not in their paper. For the literal DeltaProduct with unit keys and
  $\beta\in[0,2]$, the transitions are already non-expansive and their theorem applies directly.
- **Gated:** they allow a scalar gate $\alpha\in[0,1]$; our class is ungated ($\mathrm{rank}(A-I)\le k$). We are
  covered by the $\alpha=1$ case. Our L2 does *not* cover gated transitions ($\mathrm{rank}(A-\alpha I)$ small does
  not make $\mathrm{rank}(A-I)$ small); their result does.
- **Input alphabet:** they require "inputs range over all of $S_5$" (including $e$). Our "all" is $G\setminus\{e\}$; set
  $A_e=I$. The proof itself uses only the letters $c=(12345)$ and $t=(12)$. So the argument works for any alphabet
  containing a 5-cycle and a transposition: we checked that both conjugacy types of the pair (adjacent and non-adjacent
  transposition) give a commutator of order 3. That would give $h^*(S_5,\Sigma)=4$ for, e.g., the standard generating
  pair $\{(12),(12345)\}$. **This is our observation, not their claim.** It also shows the sharp contrast with
  $h^*(S_5,\text{transpositions})=1$.
- **Decoder class:** arbitrary and many-to-one in both papers. Matches.
- **Precision:** both use exact arithmetic with finite reachability of exact states. They explicitly leave finite
  datatypes with casting open, the same caveat as our L2 remark (iii).
- **Heads:** theirs allows any number of independent heads; our $h^*$ is single-head. This doesn't matter for the
  closing argument.
- **Technique vs. our covering-group definition:** the counting "rank $k\Rightarrow\le\lfloor k/2\rfloor$ non-real
  pairs" applies verbatim to $\rho(t_s)$, because $\rho(t_s)$ is a genuine matrix with $\mathrm{rank}(\rho(t_s)-I)\le
  k$. Lemma 23 needs only orthogonality and membership in a finite group, which holds for $\rho(H)$. Their passage from
  "≤ 1 pair" to "a planar rotation after raising to the power $E$" uses that the real eigenvalues are $\pm1$, which
  holds for a finite orthogonal group. So the technique applies to our definition **with $k\le 3$ only**; it does not
  bound $h^*$ for $k\ge 4$ or for other groups.

### 3.5 $A_5$

- **$h^*(A_5,\text{all})=2$ via the icosahedral rotation group in $d=3$ (ours, DeltaProduct$_2$)** versus their Thm 17
  (no 3-dimensional signed-Householder/CKDA tracker of $A_5$) and Cor 19 (4-dimensional CKDA tracker). The two do not
  conflict. A signed Householder must match the CKDA form, so that restriction (Prop 13 axis test) is stronger than
  "rank ≤ 2". In our language their 4-dimensional tracker is again a covering group: $\Gamma_{A_5}\subset SO(4)$ with
  $f:\Gamma\to A_5$, and each $g(A)$ is a rotation in a single plane, so $\mathrm{rank}(g(A)-I)\le2$. Their table lists
  DeltaProduct$_{k\ge2}$ as tracking SO(3) subgroups in one layer (from Siems et al. 2025), so our $h^*(A_5,\text{all})\le2$
  witness is anticipated as a construction. The matching lower bound $\ge2$ (our L4) and the equality $h^*=2$ in our
  framework are ours.
- **$A_5$ with involutions, using one reflection via $H_3=A_5\times\mathbb Z_2$ (ours).** Their $\psi(Q)=\det(Q)Q$ is
  precisely the homomorphism $O(3)\to SO(3)$ with kernel $\{\pm I\}$ that makes our $H_3\to A_5$ cover work. They use
  it *for an obstruction* (to push an arbitrary decoder down to $SO(3)$); we use it *for a construction* (lifting each
  involution, a half-turn $2aa^\top-I$, to the reflection $-(2aa^\top-I)=I-2aa^\top$). Their Prop 13 contains the
  identity $2aa^\top-I=H_a(-I)$, i.e. a half-turn is a reflection times $-I$. They do **not** state that
  plain DeltaNet (one reflection per token, $k=1$) tracks $A_5$ over its 15 involutions. Their only $k=1$ group result
  is footnote 1 (DeltaNet for $S_n$ with identity and swaps, citing Grazzi et al. 2025). **Our C1 ($h^*(A_5,\text{inv})=1<h(A_5,\text{inv})=2$) is new relative to this paper.**

### 3.6 Abelian and diagonal cases (our L5, L7)

They realise $\mathbb Z_n$ and $D_n$ in $d=2$ with CKDA (Prop 14) and cite Grazzi et al. for real-spectrum
impossibility. They do not determine $h^*$ for general abelian groups with the all-elements alphabet (our L7: 1 iff
every letter is an involution, else 2, via the count cover), and they have no diagonal classification like our L5.
Our L5 is consistent with their Sec. 4 claims (a non-negative gate gives a real spectrum; complex eigenvalues need both
range extensions), but is a statement about groups rather than spectra.

## 4. What is anticipated, what is new

**Anticipated by this paper (cite it):**
- Compression to a finite group with a surjection to $G$ under finite reachability with an arbitrary decoder and
  additive term: Prop 20/21 and Lemma 11, *under non-expansion*.
- The $S_5$ lower bound "DeltaProduct$_k$, $k\le3$ fails; 4 is the minimum" for non-expansive (gated) DeltaProduct with
  all inputs: Thm 4/22 and C.6 "Consequences". This settles our open $h^*(S_5,\text{all})$, giving 4.
- Use of $\det(Q)Q$ / $\pm I$ quotients in dimension 3, and the half-turn = reflection·$(-I)$ identity.
- Constructions for cyclic, dihedral, $S_4$, $A_4$ (CKDA), and SO(3) subgroups via DeltaProduct$_2$ (as cited in their Table 1).

**New in our work (relative to this paper):**
- The invariant $h^*(G,\Sigma)$ and the exact characterisation Theorem 1 (L2 + L3) for every finite group and alphabet.
- L2 *without any norm or non-expansion assumption*, including expansive and singular transitions, via the minimal
  ideal. It inherits the rank, where their version inherits the spectrum.
- L4 (order ≥ 3 ⇒ ≥ 2 factors) in covering-group form; L7 for all abelian groups.
- Alphabet dependence: $h^*(A_5,\text{inv})=1$ with one reflection through $H_3$; $h^*(S_5,\text{transp})=1$ versus
  $h^*(S_5,\text{all})=4$; $h^*$ versus $h$ gaps ($\mathbb Z_2^k$, $A_5$/involutions), and $Q_8$, $SL(2,3)$, $S_4$ examples.
- The norm-free extension of the $S_5$ bound (L2 + their Thm 22), and the observation that their proof only needs a
  5-cycle and a transposition in the alphabet.

## 5. Recommended wording for our paper

Positioning sentences (suggested):

> "Concurrently, Siems et al. (2026, arXiv:2609.24797) show that a single layer whose head transitions are non-expansive
> and have at most one non-real unit-circle eigenvalue pair cannot track $S_5$ under finite reachability; in particular
> four Householder factors are necessary and sufficient for one-layer (gated) DeltaProduct on $S_5$. Their reduction
> (Props. 20–21) passes to a finite group mapping onto $G$ and requires non-expansion to restrict the transitions
> orthogonally. Our compression lemma (L2) removes the norm assumption, preserving the rank defect rather than the
> spectrum, which yields the exact characterisation $k\ge h^*(G,\Sigma)$ for every finite group and alphabet."

> "Combining L2 with their spectral obstruction gives $h^*(S_5, S_5\setminus\{e\})=4$: any finite-state one-layer
> realisation with $\mathrm{rank}(A(s)-I)\le 3$ for all letters, expansive or not, fails on $S_5$."

> "For $A_5$, Siems et al. use the map $Q\mapsto\det(Q)Q$ to rule out 3-dimensional signed-Householder trackers; the
> same quotient $O(3)\to SO(3)$, read in reverse, is what lets a single reflection per token track $A_5$ over its
> involutions (Corollary C1)."

**Can we cite the S5 interval as closed?** Yes, with conditions stated: $h^*(S_5,\text{all})=4$ follows from
**their Theorem 4 (= Thm 22) together with our L3/averaging argument** (the faithful rep of the cover, made orthogonal,
is a non-expansive finite-state single-head tracker with at most one non-real pair when $k\le3$). Conditions:
(i) exact arithmetic, finitely many reachable exact states; (ii) the alphabet contains all of $S_5$ (the proof needs
only a 5-cycle and a transposition, but the paper states it for all inputs); (iii) arbitrary decoder and additive term
are allowed. For the architecture-level statement (no realisation with rank ≤ 3, expansive allowed) also cite our L2.
For the gated case, cite them alone. Mark the combination step as "[hand]" until reviewed; their theorem itself is
"[cited]". Update theory.md C2 and the Open list accordingly (scout recommendation; not done here).
