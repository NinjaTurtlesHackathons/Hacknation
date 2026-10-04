# Novelty check (literature only)

Date of search: 2026-10-04. Scope: the 65 sources in `scout_evidence.md` plus new searches (arXiv API full-text abstract
search, Semantic Scholar citation lists of arXiv:2502.10297 (74 citing papers), arXiv:2411.12537 (109), arXiv:2503.14456 (154),
arXiv:2603.01959 (11), arXiv:2609.18966 (0 indexed), web search, full-text HTML/PDF of the closest hits).
Every quote below was seen verbatim in a tool result (arXiv abstract via export.arxiv.org, arXiv HTML full text, or arXiv PDF text).
Anything not seen in a tool result is marked UNVERIFIED.

Closeness scale: **anticipates** (same statement), **partially** (same statement for a special case, or same technique),
**related** (neighbouring concept), **not**.

## New source that changes the picture

**arXiv:2609.24797** - Siems, Grazzi, Pöppel et al., "Complex KDA: Understanding and Enhancing the Expressivity of Kimi Delta
Attention", v1 2026-09-21 (not in `scout_evidence.md`). Same group as DeltaProduct and Grazzi et al. It contains (i) a
one-layer lower bound for S5 with an exact minimum of four Householders, (ii) a reduction of finite-state non-expansive affine
trackers to orthogonal trackers via an idempotent word of minimum Frobenius norm, producing a finite matrix group with a
surjection onto the tracked group (i.e. a covering group), and (iii) a many-to-one-decoder construction of A5 in dimension 4.
This must be cited and positioned against C1, C2 and C4.

## C1 - lower bound via compression of the transition monoid to a covering group

| ID | Source | Verbatim quote (tool result) | Closeness |
|---|---|---|---|
| arXiv:2609.24797 | Siems et al. 2026 (CKDA), abstract | "We rule out one-layer S 5 tracking for CKDA and DeltaProduct k ( k ≤ 3 ) with non-expansive transitions and finite reachability ( Theorem 4 )." (contributions list, HTML) | **partially** (same type of result, S5 only, all-of-G alphabet) |
| arXiv:2609.24797 | CKDA, App. C.6 / B.4 | "Together with the lower bound, this proves that four is the minimum number of Householder transformations needed for single-layer Gated DeltaProduct tracking of S 5 under these assumptions." | **partially** (S5 instance of C1 + sufficiency) |
| arXiv:2609.24797 | CKDA, Prop. 20 proof | "We first choose a word whose linear part has minimum Frobenius norm and repeat it until it acts as a projection without changing the decoded value. Minimality and non-expansion then force the original matrices to act orthogonally on its image." | **partially** (same compression technique: idempotent word, restriction to its image; analytic, needs ‖A‖<=1) |
| arXiv:2609.24797 | CKDA, proof of Thm 4 | "The resulting block-diagonal matrices generate a finite group Γ , with a surjective homomorphism p : Γ → S 5 satisfying p ⁡ ( 𝑨 g ) = g ." | **partially** (covering group surjecting onto G; the bound used is spectral, "at most one non-real conjugate eigenvalue pair", not rank(ρ(t)-I)<=k) |
| arXiv:2609.18966 | Howe 2026, full text | "for S 5 the necessity is representation-independent: in every faithful representation of S 5 the 5-cycle's reflection length is 4 (checked across the irreducible representations), so n h = 4 is a true lower bound" | **partially** (informal S5 lower bound, faithful representations only, no reduction from arbitrary finite-state trackers) |
| arXiv:2411.12537 | Grazzi et al. 2024, abstract | "We prove that finite precision LRNNs with state-transition matrices having only positive eigenvalues cannot solve parity, while non-triangular matrices are needed to count modulo $3$." | related (eigenvalue-type necessary conditions, no factor count) |
| arXiv:2502.10297 | Siems et al. 2025 (DeltaProduct), full text | searched for "lower bound": 0 hits; "minimum number": 0 hits | not (constructions only) |
| arXiv:2606.01765 | Nowak, Cotterell, Boumasmoud 2026, abstract | "This account reduces expressivity to an algebraic question, e.g., whether a network's syntactic monoid divides a certain wreath product." | related (monoid-theoretic view, no Householder count) |

Differences that remain ours (to be checked against the CKDA text by the authors): general finite group G and arbitrary input
alphabet Σ (CKDA: S5, inputs range over all of G); rank criterion rank(ρ(t)-I) <= k (CKDA: count of non-real eigenvalue pairs,
which for k Householders is <= floor(k/2) per CKDA Table 1); purely algebraic compression through the minimal ideal of the finite
transition monoid (CKDA: minimum-Frobenius-norm word, requires non-expansive transitions). Whether our C1 needs non-expansion is
not something this check can decide.

**Verdict C1: PARTIALLY KNOWN** - cite arXiv:2609.24797 (Prop. 20, Thm. 4; S5 minimum of four) and arXiv:2609.18966 (informal S5
bound). The general statement for arbitrary (G, Σ) with the rank criterion was not found.

## C2 - exact characterisation k >= h*(G, Σ) ("Householder complexity")

| ID | Source | Verbatim quote (tool result) | Closeness |
|---|---|---|---|
| arXiv:1804.05089 | Martino, Singh 2018, PDF | "An abstract group G is minimally generated in codimension k if k is the minimal integer for which there exists a faithful repres entation ρ : G → GL(V ) such that the linear group ρ(G) is strictly generated in codimension k." | **partially** (the faithful, alphabet-free analogue of h: minimum over faithful real reps of the codimension of fixed spaces of generators; no covering groups, no fixed alphabet, no RNN link) |
| arXiv:1804.05089 | Martino, Singh 2018, abstract | "We say that a group $G$ is generated (resp. strictly generated) in codimension $k$ if it is generated by its elements that fix point-wise a subspace of codimension at most $k$ (resp. precisely $k$)." | related (definition) |
| arXiv:1509.06922 | Lange, Mikhailova 2015, abstract | "We survey the existing parts of a classification of finite groups generated by orthogonal transformations in a finite-dimensional Euclidean space whose fixed point subspace has codimension one or two and extend it to a complete classification." | related (classifies faithful h <= 2 linear groups with alphabet = all such elements) |
| arXiv:1312.7780 | Brady, McCammond 2013, abstract | "Every isometry of a finite dimensional euclidean space is a product of reflections and the minimum length of a reflection factorization defines a metric on its full isometry group." | related (orthogonal reflection length; the "Scherk" ingredient) |
| arXiv:1803.03070 | delMas, Lewis 2018, abstract | "We give an intrinsic criterion to tell whether a reflection factorization in the general linear group is reduced, and give a formula for computing reflection length in the general affine group." | related (reflection length in GL, relevant for generalized, non-orthogonal Householders) |
| arXiv:2609.18966 | Howe 2026, full text | "the minimal n h that length-generalizes equals the maximal generator reflection length rank ⁡ ( I − P ) in the representation pinned by the task format" (from `evidence.md`, body quote verified there) | **partially** (empirical, representation-relative version; no minimisation over representations or covers) |
| arXiv:2609.24797 | CKDA, intro | "Tracking does not require a faithful representation: a many-to-one decoder can map distinct hidden states to the same group element, and the input transitions need not themselves form a representation." | related (states the covering phenomenon informally; no characterisation) |
| arXiv:2502.10297 | DeltaProduct, App. Thm. 4 (scout) | orthogonal-group sufficiency n_h = n for subgroups of O(n) (see `scout_evidence.md`) | related (upper bound only) |
| Scherk; Huffman-Wales | classical | Scherk's theorem on reflection length in O(V); Huffman-Wales 1975 "Linear groups of degree n containing an element with exactly n-2 equal eigenvalues" | related - **UNVERIFIED** (seen only as search-engine snippet text, not as a primary-source quote) |

**Verdict C2: NOVEL** as stated (min over finite covering groups H ->> G with generating lifts of Σ, max rank(ρ(t_s)-I), and its
equivalence with one-layer exact tracking). Must be positioned as the alphabet- and cover-aware version of Martino-Singh's
"minimally generated in codimension k" (arXiv:1804.05089) and the empirical law of Howe (arXiv:2609.18966).

## C3 - a real finite-order matrix with rank(M-I) <= 1 is an involution (or I)

| ID | Source | Verbatim quote (tool result) | Closeness |
|---|---|---|---|
| arXiv:math/0311012 | Geck, Malle 2003, "Reflection Groups. A Contribution to the Handbook of Algebra", PDF p.1-2 | "Over ﬁelds K contained in the ﬁeld R of real numbers, reﬂections necessarily have order 2, which is the case motivating their name." | **anticipates** (in their definition a reflection is a finite-order, diagonalisable element fixing a hyperplane pointwise; in char 0 finite order implies diagonalisable, so rank(M-I) = 1 with finite order over R gives order 2) |
| arXiv:1509.06922 | Lange, Mikhailova, PDF | "Since an orthogonal pseudoreﬂection neces- sarily rotates t[he two-dimensional complement of its fixed point subspace]" (quote truncated in the tool result after "rotates t") | related (codimension-two analogue) |
| arXiv:2411.12537 / arXiv:2609.24797 | Grazzi; CKDA Table 1 | CKDA Table 1 lists "Complex pairs ... ≤ ⌊ k / 2 ⌋" for Gated DeltaProduct k | related (a single generalized Householder has real spectrum, so it cannot have order >= 3 on the unit circle; the ML papers state this spectrally) |
| Lehrer, Taylor, "Unitary Reflection Groups", CUP 2009 | book | standard reference for pseudo-reflections | **UNVERIFIED** (no quote seen) |

**Verdict C3: KNOWN** - classical; cite Geck-Malle arXiv:math/0311012 (and the corollary "order >= 3 needs >= 2 factors" follows
immediately; its spectral form is implicit in Grazzi et al. arXiv:2411.12537 and CKDA arXiv:2609.24797 Table 1).

## C4 - A5 with involution inputs and one Householder via H3 = A5 x Z2; A5/S4 with 2; abelian count covers

| ID | Source | Verbatim quote (tool result) | Closeness |
|---|---|---|---|
| arXiv:2609.24797 | CKDA, App. C.4.1 | "In three dimensions, multiplying an orientation-reversing orthogonal matrix by − 𝑰 3 makes it orientation-preserving." ... "The map identifies at most a matrix and its negative, since its kernel K is contained in { ± 𝑰 3 } ." | **partially** (exactly the O(3) -> SO(3), Q -> det(Q) Q correspondence that underlies H3 ->> A5, but used as an obstruction for CKDA, not as a one-Householder construction) |
| arXiv:2609.24797 | CKDA, Thm. 3 | "A single CKDA layer (one head) tracks every finite group isomorphic to a subgroup of S ​ O ​ ( 3 ) . Specifically, it realizes every finite cyclic ( ℤ n ) and dihedral group ( D n ) in d = 2 and A 4 , S 4 in d = 3 , and tracks A 5 in d = 4 ." | **partially** (A5 via a many-to-one decoder; all-of-G alphabet; CKDA, not one plain Householder) |
| arXiv:2609.24797 | CKDA, footnote | "If inputs are restricted to identity and swaps, one-layer DeltaNet suffices ( Grazzi et al., 2025 ) ." | related (alphabet dependence for S_n, a reflection group; nothing on A5) |
| arXiv:2609.18966 | Howe, full text | "For S 4 and A 5 , however, Siems et al. [ 10 ] report robust extrapolation at n h = 2 via their isomorphisms to rotation groups in S ​ O ​ ( 3 ) , where every element is a product of ≤ 2 reflections." | **anticipates** the "A5 and S4 with 2 in any alphabet" part (DeltaProduct via SO(3)) |
| arXiv:2502.10297 | DeltaProduct, App. Thm 7 / Thm 6 (scout) | dihedral one layer n_h >= 2; modular addition with reflections in two layers | **anticipates** abelian/cyclic with 2 in one layer (2D rotations; also CKDA Thm 3 "cyclic ( ℤ n ) ... in d = 2") |
| arXiv:1509.06922 | Lange, Mikhailova, PDF | "Lemma 15. There exists a primitive absolutely irreducible rotation g roup isomorphic to the altern- ating group A5." | related (A5 generated by codimension-2 elements in another rep) |
| Wikipedia "Icosahedral symmetry" | web | H3 has 120 elements and is isomorphic to Z2 x A5 (search-engine summary only) | related, **UNVERIFIED** as a quote; classical fact (Coxeter) |
| searches | arXiv API | 'abs:"icosahedral" AND (abs:RNN OR abs:recurrent OR abs:"state tracking")': 0 hits; "H 3"/"Coxeter"/"involution" in CKDA full text: 0 hits; "involution"/"covering"/"icosahedr" in DeltaProduct and Howe full text: 0 hits | - |

**Verdict C4: PARTIALLY KNOWN** - A5/S4 with 2 Householders via SO(3) and cyclic/abelian with 2 are KNOWN (arXiv:2502.10297,
arXiv:2609.24797 Thm. 3). The one-Householder A5 construction for involution alphabets via H3 = A5 x Z2 (a cover of A5 that is a
real reflection group) was not found; the ±I identification it relies on appears in CKDA's 3D obstruction proof. The H3 ≅ A5 x Z2
fact itself is classical (cite Coxeter or Humphreys; UNVERIFIED here).

## C5 - atlas of h over all groups of order <= 63 via character tables

| ID | Source | Verbatim quote (tool result) | Closeness |
|---|---|---|---|
| arXiv:1804.05089 | Martino, Singh 2018, abstract | "Further, we compute the intersection lattice of all finite subgroups of $GL_3(\mathbb{R})$, and moreover, we emphasize the groups that are \"minimally generated in real codimension two\", i.e, groups that are strictly generated in codimension two but have no real reflection representations." | related (tabulates low-codimension generation for subgroups of GL3(R) only) |
| arXiv:1509.06922 | Lange, Mikhailova 2015 | classification of codimension <= 2 generated orthogonal groups (quote under C2) | related (classification by type, not an order-indexed atlas, no alphabets) |
| arXiv:2609.12259 | Larson 2026, abstract | "On group-composition state tracking over five finite groups spanning the solvable/non-solvable divide, the recruited rank equals the group's minimal faithful real representation dimension $d_{\min}$" | not (dimension, not Householder count; empirical) |
| arXiv:2609.24797 | CKDA Table 1 | per-model expressivity table for S2, S3, S4, A5, S5 etc. (all-of-G inputs) | related (a handful of groups, not an atlas) |

**Verdict C5: NOVEL** (no atlas of reflection/Householder complexity over all small groups found).

## Summary of verdicts

- C1: PARTIALLY KNOWN (arXiv:2609.24797 Prop. 20 + Thm. 4: idempotent compression, covering surjection Γ ->> S5, minimum of four
  Householders for S5; arXiv:2609.18966 informal S5 bound).
- C2: NOVEL (closest: arXiv:1804.05089 "minimally generated in codimension k", faithful and alphabet-free; arXiv:2609.18966 empirical
  representation-pinned law).
- C3: KNOWN (arXiv:math/0311012, Geck-Malle: real reflections have order 2).
- C4: PARTIALLY KNOWN (SO(3) parts and cyclic-with-2 known: arXiv:2502.10297, arXiv:2609.24797; H3 one-Householder construction for
  A5 with involution inputs not found).
- C5: NOVEL.

## Limitations of this check

- Semantic Scholar had 0 indexed citations of arXiv:2609.18966; papers from the last ~2 weeks may be missing.
- Classical sources (Scherk 1950, Huffman-Wales 1975, Wales 1978, Lehrer-Taylor 2009, Coxeter) were not read in primary form; any
  statement attributed to them above is UNVERIFIED.
- Full text of arXiv:2609.24797 was read only through keyword windows; whether its Prop. 20 already yields a general rank-based bound
  for arbitrary (G, Σ) should be checked by reading Appendix C.5-C.6 in full before submission.
