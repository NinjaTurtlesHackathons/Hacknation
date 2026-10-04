# Exact planar few-distance constructions with 111 and 81 points

AI Agent Lab — research draft, 4 October 2026

**Status.** Both existence statements below are exact and independently checked. The independent adversarial literature audit through 4 October 2026 is complete and found no prior equal or stronger construction in the primary sources and author code it examined. These are improvements over the named published lower bounds. This qualified literature conclusion does not assert certainty about unpublished or unindexed work, global optimality, or a new general geometric mechanism.

## Abstract

We give an explicit planar set of 111 points determining exactly 41 distances, together with an 81-point set determining exactly 31 distances. Consequently, for the unrestricted Euclidean-plane problem with at most k distinct distances, G(31) ≥ 81 and G(41) ≥ 111. The constructions exceed the corresponding published lower bounds 80 and 109 in Ahmed–Snevily (2013). The recent Bao–Yu (2025) table gives 79 at 31 and does not cover 41. Both witnesses are specified by short lists of integer half-planes and complete row intervals in the triangular lattice. A complete finite integer calculation proves their cardinalities and distance counts without relying on an optimizer, floating-point tolerance, or an optimality certificate. The 81-point witness has one reflection symmetry; the 111-point witness has threefold rotational and reflection symmetry. We document source comparisons, independently checked artifacts, discovery procedures, and the limits of the novelty claim.

## 1. Problem and statements

For a finite X ⊂ R², let D(X) = {‖x−y‖ : x,y ∈ X, x ≠ y}, and define

G(k) = max { |X| : X ⊂ R² finite, |D(X)| ≤ k }.

The plane and Euclidean metric are unrestricted. There is no bounding container, prescribed diameter, contact condition, symmetry restriction, or lattice restriction in G. A lattice witness supplies a lower bound on G; it supplies no upper bound and does not prove that optimal sets must be lattice sets.

Write φ(a,b) = (a+b/2, √3 b/2) for a,b ∈ Z, and Q(u,v)=u²+uv+v². Then

‖φ(a,b)−φ(c,d)‖² = Q(a−c,b−d).

The map φ is injective. The quadratic form Q is positive for every nonzero integer vector because 4Q(u,v)=(2u+v)²+3v². Counting nonzero squared distances is equivalent to counting distances.

**Theorem 1.** The set φ(S31) defined in Section 3 has 81 points and exactly 31 distances. Therefore G(31) ≥ 81.

**Theorem 2.** The set φ(S41) defined in Section 3 has 111 points and exactly 41 distances. Therefore G(41) ≥ 111.

These are existence statements with full certificates. Neither theorem asserts G(31)=81 or G(41)=111. Monotonicity also gives G(k)≥81 for k≥31 and G(k)≥111 for k≥41, but these consequences need not improve previously known bounds. In particular, Ahmed–Snevily already gives 115 at k=42: this manuscript claims **no improvement at 42**.

## 2. Prior work and comparison scope

Erdős and Fishburn formulated and studied maximum planar sets determining k distances [1]. Ahmed and Snevily studied symmetric lattice polygons and arbitrary orientations of attached triangular blades; their main construction figure on printed page 5 explicitly states g(31)≥80, g(41)≥109, and g(42)≥115 [2]. Their g uses exactly k distances. An exactly-k construction is valid for our at-most-k definition; historical bounds must also be propagated monotonically before comparison. The audited table through 50 retains 80 and 109 at our two target indices.

Ahmed and Wildstrom proved the boundary-difference realization property for cycle-bounded triangular-lattice sets [3]. We therefore make no claim to have discovered boundary reduction. Balaji et al. revisited lattice constructions, corrected distance tables, and compared structured arrays and lattice disks [4]. The initial preprint appeared in 2019. The six-author journal publication appeared in 2020; the seven-author 2023 arXiv revision also includes Lo Phillips and is identified separately in the references. Szöllősi and Östergård's 2020 graph/Gröbner classification work concerns, among other cases, six distances in the plane [5]; it is not a classification of our large-k cases.

Bao and Yu use first-distance palettes and equiangular hexagons [6]. Their displayed table at m=31 gives 79; comparison solely to that recent table would understate the older 80-point construction. Their first-31-distance restricted computation does not imply an upper bound on arbitrary triangular-lattice palettes. Allowing larger distances, observing multiplicities, and deleting points to remove distance classes are all prior ideas: the numerical witnesses here are not evidence of a newly discovered palette-exchange mechanism.

| k | Ahmed–Snevily 2013, exactly-k witness | Bao–Yu 2025 displayed lower bound | this manuscript, exactly-k witness | improvement over audited comparison |
|---:|---:|---:|---:|---:|
| 31 | 80 | 79 | 81 | +1 |
| 41 | 109 | not tabulated | 111 | +2 |
| 42 | 115 | not tabulated | no improved witness claimed | none |

The literature review includes author-hosted sources and code, rather than treating the newest table as complete. No source found in the currently audited set supersedes these two comparisons. The completed independent review supports the wording: “Two exact constructions improve the lower bounds in Ahmed–Snevily (2013); our literature audit through 4 October 2026 found no prior equal or stronger construction.” Its archive is `wave2/packing/few_distance_novelty/VERDICT.md`. It is not a proof of exhaustive literature coverage. The withdrawn September 2026 revision of arXiv:2510.09800 is excluded as a source of established asymptotic theorems; its old mirror PDF remains accessible [7].

## 3. Explicit constructions

For each column below, define S = {(a,b) ∈ Z² : Aa+Bb ≤ C for every listed row}. Thus the following ten inequalities alone define each witness, including every interior lattice site.

| A | B | C for S31 | C for S41 |
|---:|---:|---:|---:|
| -2 | -1 | 9 | 10 |
| -1 | -2 | 9 | 11 |
| 1 | -1 | 9 | 11 |
| 1 | 0 | 5 | 7 |
| 2 | 1 | 8 | 10 |
| 1 | 1 | 5 | 6 |
| 1 | 2 | 8 | 9 |
| 0 | 1 | 5 | 6 |
| -1 | 1 | 8 | 9 |
| -1 | 0 | 5 | 6 |

For S31, −5≤a≤5 and a−b≤9 imply b≥−14, while b≤5. For S41, −6≤a≤7 and a−b≤11 imply b≥−17, while b≤6. Hence each polygon's complete integer enumeration is contained in [−20,20]². There are no unexamined points beyond the enumeration box.

Equivalently, for each listed a, choose every integer b between the row's minimum and maximum, inclusive; choose no other rows. The following intervals are obtained directly by substituting a into the ten inequalities.

### S31

| a | minimum b | maximum b | sites |
|---:|---:|---:|---:|
| -5 | 1 | 3 | 3 |
| -4 | -1 | 4 | 6 |
| -3 | -3 | 5 | 9 |
| -2 | -3 | 5 | 9 |
| -1 | -4 | 4 | 9 |
| 0 | -4 | 4 | 9 |
| 1 | -5 | 3 | 9 |
| 2 | -5 | 3 | 9 |
| 3 | -6 | 2 | 9 |
| 4 | -5 | 0 | 6 |
| 5 | -4 | -2 | 3 |

The row lengths are 3,6,9,9,9,9,9,9,9,6,3, summing to 81. All sites inside the ten-facet polygon are selected.

### S41

| a | minimum b | maximum b | sites |
|---:|---:|---:|---:|
| -6 | 2 | 3 | 2 |
| -5 | 0 | 4 | 5 |
| -4 | -2 | 5 | 8 |
| -3 | -4 | 6 | 11 |
| -2 | -4 | 5 | 10 |
| -1 | -5 | 5 | 11 |
| 0 | -5 | 4 | 10 |
| 1 | -6 | 4 | 11 |
| 2 | -6 | 3 | 10 |
| 3 | -7 | 3 | 11 |
| 4 | -7 | 2 | 10 |
| 5 | -6 | 0 | 7 |
| 6 | -5 | -2 | 4 |
| 7 | -4 | -4 | 1 |

The row lengths are 2,5,8,11,10,11,10,11,10,11,10,7,4,1, summing to 111. All sites inside the corresponding polygon are selected.

## 4. Complete elementary certificate

Let a row-interval set S have rows R_a=[L_a,U_a]∩Z. For an integer difference vector (u,v), its ordered-pair multiplicity is

N(u,v) = ∑_a max(0, min(U_a,U_{a−u}+v) − max(L_a,L_{a−u}+v) + 1),

where a term is zero if either row does not exist. This formula counts the integers b for which both (a,b) and (a−u,b−v) lie in S: their intervals intersect exactly as shown. For q>0 the number of **unordered** pairs at squared distance q is

C(q) = (1/2) ∑_{u²+uv+v²=q} N(u,v).

Only |u|≤a_max−a_min and |v|≤b_max−b_min can contribute. These are finite integer ranges. Negating (u,v) reverses each pair, explaining the factor 1/2. Zero differences are omitted. This proves the counting formula without a solver or a floating-point operation.

For S31 use u∈[−10,10], v∈[−11,11]. For S41 use u,v∈[−13,13]. Substitution of the row intervals gives exactly the positive multiplicities below; all other q have multiplicity zero.

| squared distance q | unordered pairs in S31 | unordered pairs in S41 |
|---:|---:|---:|
| 1 | 208 | 291 |
| 3 | 189 | 270 |
| 4 | 175 | 252 |
| 7 | 314 | 462 |
| 9 | 144 | 216 |
| 12 | 135 | 207 |
| 13 | 254 | 390 |
| 16 | 115 | 180 |
| 19 | 212 | 342 |
| 21 | 198 | 324 |
| 25 | 88 | 147 |
| 27 | 81 | 144 |
| 28 | 158 | 276 |
| 31 | 146 | 258 |
| 36 | 63 | 117 |
| 37 | 112 | 222 |
| 39 | 108 | 216 |
| 43 | 98 | 198 |
| 48 | 36 | 81 |
| 49 | 110 | 249 |
| 52 | 64 | 156 |
| 57 | 54 | 144 |
| 61 | 40 | 114 |
| 63 | 36 | 108 |
| 64 | 19 | 60 |
| 67 | 28 | 102 |
| 73 | 16 | 90 |
| 75 | 9 | 36 |
| 76 | 16 | 72 |
| 79 | 10 | 66 |
| 81 | 0 | 36 |
| 84 | 0 | 54 |
| 91 | 4 | 84 |
| 93 | 0 | 36 |
| 97 | 0 | 30 |
| 100 | 0 | 12 |
| 103 | 0 | 18 |
| 108 | 0 | 9 |
| 109 | 0 | 18 |
| 112 | 0 | 12 |
| 127 | 0 | 6 |

There are 31 positive entries in the S31 column and 41 in the S41 column. Their sums are respectively 3240=81·80/2 and 6105=111·110/2. The finite difference ranges cover every possible pair, so the table is complete. Every listed positive value is realized; no other value occurs. The injectivity of φ and the positivity identity for Q now prove both theorems.

A second computation enumerates unordered point pairs and uses the Cartesian numerator (2(a−c)+b−d)²+3(b−d)², dividing by 4. Agreement with the row-correlation calculation is archived in `wave2/paper/evidence.json`. This cross-check is manuscript reproducibility; the independent certification reported below uses separately implemented checkers.

The full squared-distance set for S31 is

`1,3,4,7,9,12,13,16,19,21,25,27,28,31,36,37,39,43,48,49,52,57,61,63,64,67,73,75,76,79,91`.

For S41 it is

`1,3,4,7,9,12,13,16,19,21,25,27,28,31,36,37,39,43,48,49,52,57,61,63,64,67,73,75,76,79,81,84,91,93,97,100,103,108,109,112,127`.

## 5. Geometry and limitations of the structural interpretation

S31 is a filled convex decagon. Among lattice rotations and reflections followed by translation, its only symmetries are identity and (a,b)↦(−a,a+b), a Euclidean reflection. This follows by transforming the complete finite set under the twelve triangular-lattice dihedral maps and checking the only possible aligning translations. A single asymmetric witness does not contradict a conjecture about the symmetry of a globally optimal configuration: no global optimality is proved.

S41 has centroid (1/3,−2/3) in lattice coordinates. The map (a,b)↦(−a−b,a−1) is a 120-degree rotation about this centroid, and (a,b)↦(b+1,a−1) is a reflection fixing it. The corresponding six D3 maps preserve the entire set. Accordingly all nonzero-distance multiplicities in S41 are multiples of three. This observation is explanatory, not part of the existence proof.

S31 uses squared norm 91 while avoiding 81 and 84; it therefore is not restricted to the 31 shortest triangular-lattice norms. S41 similarly avoids 111,117,121 while using 112 and 127. These are concrete alphabet choices. Their value is the certified cardinality improvement at the two specified indices; the principle of trading distance classes predates this work.

The known symmetric saw-blade families B_s,r,t in [2] do not represent these two witnesses up to similarity: cardinality restricts the standard families to parameter cases whose core distances include norms absent from our witnesses. The finite arithmetic exclusion is archived separately. A necessary search for a polygonal P_a,r1,r2 core with individually attached unit-triangle sites also found no match within the tested parameter ranges. That computation is not a proof excluding every interpretation of arbitrary blades, and neither exclusion by itself establishes novelty against all prior work.

### An exact parameter construction for S41

For integers s≥1 and t≥0, let P(s,t) be the polygon with successive vertices

```
(0,0), (s,−2s), (3s,−3s), (3s+t,−3s),
(4s+t,−2s), (3s+t,0), (3s,t), (s,s+t), (0,t).
```

Define F(s,t)=P(s,t)∩Z², selecting every lattice site. For t>0 the edge vectors are

```
(s,−2s), (2s,−s), (t,0), (s,s), (−s,2s),
(−t,t), (−2s,s), (−s,−s), (0,−t).
```

They sum to zero and their Euclidean directions turn by 60°,30°,30°, repeated three times. The closed polygon is strictly convex. At t=0 the three zero edges collapse to a regular hexagon. The shoelace sum and the sum of edge-coordinate gcds are respectively

2A = 18s²+12st+t²,   B = 6s+3t.

Here A is area in lattice-coordinate space, where Z² has unit fundamental cell; it is not area in the physical φ embedding. Pick's theorem gives the following exact cardinality identity for every allowed s,t:

**Proposition 3.** |F(s,t)| = 9s²+6st+t(t+3)/2+3s+1.

**Proof.** The listed closed vertices give the displayed shoelace sum. Six edges have coordinate gcd s, and three have gcd t, giving B. Counting interior and boundary sites, Pick's theorem gives |F|=A+B/2+1. Substitution yields the identity. At t=0, the same computation applies after collapsing zero-length edges. ∎

The construction is D3-symmetric for t>0 about c=(2s+t/3,−s+t/3). The centered 120-degree rotation is (a,b)↦(−a−b,a)+(3s+t,−3s); the centered reflection is (a,b)↦(b,a)+(3s,−3s). They preserve the listed vertices and Z², so they preserve every filled lattice site. The three distinguished t-edges have Euclidean length t and the other six length s√3. These lengths are unequal for positive integers s,t, restricting any extra symmetry to that of the triangle formed by the distinguished-edge midpoints; the full group is D3.

At (s,t)=(3,1), the identity gives 111 sites: doubled coordinate area is 199 and B=21. Direct translation shows F(3,1)=S41+(6,−2). The pair certificate in Section 4 proves its 41 distances. The general cardinality identity is an algebraic consequence of the explicit polygon, not an extrapolation from a finite batch. It is not a claimed formula for the number of distances. The symbolic area and D3 identities, and the translated 111-point polygon equality, are separately checked by `wave2/paper/verify_family_proposition.py`; its result is archived in `family_proposition_certificate.json`. The executed 72-case parameter batch s∈{1,…,8},t∈{0,…,8} checked the counts; only the 111/41 case improved the audited comparison table in that batch. No new asymptotic mechanism or generally improving infinite family is claimed.

### 5.2. Why squared distance 111 disappears

For F(s,1), the listed vertices give the exact widths 0≤a≤4s+1 and 0≤2a+b≤6s+2. Every point difference therefore satisfies |a|≤4s+1 and |2a+b|≤6s+2. The D3 symmetry of the polygon and central symmetry of its difference body generate D6. Applying these symmetries gives

|a|, |b|, |a+b| ≤ 4s+1,

|2a+b|, |a+2b|, |a−b| ≤ 6s+2.

The vector (3s+1,1) violates the latter bound by one and has squared norm 9s²+9s+3=N(s,1). Its whole twelve-element dihedral orbit is excluded. Other representations of this same norm can survive: this is not a universal absence theorem for that norm.

At s=3, norm111 has precisely that excluded orbit. Completing a square bounds every representation by |a|,|b|<13; exact enumeration in that finite box proves the orbit is complete. More generally, enumerate the nonzero integer vectors satisfying the six displayed caps at s=3. There are420vectors and41norms, maximum127. Since every actual point difference belongs to this envelope, it independently proves at most41distances. The full pair histogram proves all41occur. The palette is precisely the first41positive triangular-lattice norms with111replaced by127; among the45representable norms up to127, it omits111,117,121,124. The support-width argument explains this particular improvement; the broader strategy of substituting distance classes is prior art. Independent analytic replay is `wave2/final_review/orbit_review.py`.

The shared half-plane representation suggests useful construction programs. Scaling or changing its supports produces many exact point sets, but the present evidence establishes neither a uniformly improving infinite family nor an asymptotic theorem. Cases with no audited comparator are not described as improvements.

## 6. Discovery, independent checking, and reproducibility

The 81-point witness arose from joint Boolean selection of lattice sites and distance classes in a radius-6 hexagonal window. For every pair, selecting both sites forces its squared-norm variable; at most 31 norm variables may be selected. Valid matching cuts accelerate the search. Seed 42102 returned 81 points in 4.143 seconds and nine search nodes. That runtime includes the logged finite instance, not the entire earlier research portfolio. A radius-7 continuation with a fixed 37-site interior reproduced 81, without improving it. Solver optimality in a finite or partly fixed model is never used as planar optimality.

The Family agent received the 81-point support normals and independently enumerated support offsets. Its delta-2 run evaluated 9,765,625 support tuples in 54.379 seconds and produced the 111-point witness. This is independent construction development from a shared lead, not an independent rediscovery from an untouched problem statement. A subsequent canonical search evaluated 5,764,801 tuples in 31.9019 seconds. These are recorded batch timings, not the exact time to the first 111-point observation.

The director's independent integer checker and the separate Cartesian/common-denominator verifier agreed on the original 81-point witness. For the 111-point witness, the same independent Cartesian verifier recomputed all 6105 pairs without importing the Family agent's search code. Candidate geometry, historical source values, and novelty are reviewed separately. No independent checker accepts discovery metadata as a mathematical bound.

Reproduce both frozen witnesses, their half-plane/row agreement, every pair multiplicity, and artifact hashes with standard Python:

```
python3 research/geometric-extremal/results/reproduce.py
python3 research/geometric-extremal/wave2/paper/verify_witnesses.py
```

No optimization package, internet access, numerical tolerance, or random seed is needed for this command. The verifier regenerates coordinates from the manuscript row definitions and compares them with the frozen files. The complete source-and-search archive also retains model texts, seeds, prospective registrations, interrupted experiments, negative results, and explicit baseline controls.

| witness file, relative to research/geometric-extremal | SHA256 |
|---|---|
| candidates/wave2_joint_palette/k31_n81_r6_seed42102.json | a85a2a990531ebd5b40165eacb0f23c84bac6676404cb858f7b5c2c63b83d94c |
| candidates/wave2_family/support_k41_n111_code7324998.json | 2d1216002f65a2c2cccbaa30299ea4f26c21c6f493fe3ad0e164de11ad0aa3b1 |

The mathematical definitions and integer proof do not depend on those hashes; the hashes identify the exact files used in the reported checks. A corrupted or changed file is rejected by the frozen reproduction command.

## 7. Contributions and autonomy

Laurenz Thümmler supplied the research objective, repository, and authorization to use an agent team and computing resources. The initial human instruction supplied no coordinates or mathematical construction. The director coordinated problem selection, novelty review, trusted comparisons, and independent gates. The Structure agent researched sources, designed joint site/palette integer models, generated the 81-point witness, and wrote this draft. The Area/Family agent generalized its support representation and generated the 111-point witness. Independent certification of the 81-point discovery was performed by the director rather than its own discovery agent; the Structure agent separately certified the Family agent's 111-point witness. The Packing agent performed additional adversarial literature review.

Known constructions, mathematical ideas, and comparison tables belong to their cited original authors. Bao's author repository served as attributed prior art; its code is not presented as new lab work. General-purpose HiGHS/SciPy, OR-Tools CP-SAT, Python, and a C++ support enumerator were external computational tools. The mathematical proof is the finite exact certificate, not a model's assertion. Agent decisions, source mistakes corrected during research, and a compacted-summary omission corrected by raw-register audit are documented in the research chronology. Human authorship and final scientific review should be settled before journal submission.

## References

[1] P. Erdős and P. Fishburn. *Maximum planar sets determining k distances.* Discrete Mathematics 160 (1996), 115–125. Bibliographic details cross-checked in [4]; original paper remains the foundational problem reference.

[2] T. Ahmed and H. Snevily. [*Sparse Distance Sets in the Triangular Lattice*](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i4p33/pdf/). Electronic Journal of Combinatorics 20(4) (2013), P33. Printed page 5 gives the target lower bounds. Author publication index: https://tanbir.github.io/publications.html.

[3] T. Ahmed and D. Wildstrom. [*On Distance Sets in the Triangular Lattice*](https://tanbir.github.io/files/preprints/ahmed_wildstrom_distance_sets.pdf). Bulletin of the Institute of Combinatorics and its Applications 75 (2015), 118–127. Proposition 2.1 supplies the boundary-difference result.

[4] (a) V. Balaji, O. Edwards, A. M. Loftin, S. Mcharo, A. Rice, and B. Tsegaye. [*Lattice Configurations Determining Few Distances*](https://math.colgate.edu/~integers/u86/u86.pdf). Integers 20 (2020), A86; published 19 October 2020. This journal PDF has six authors.

(b) V. Balaji, O. Edwards, A. M. Loftin, S. Mcharo, L. Phillips, A. Rice, and B. Tsegaye. [*Lattice Configurations Determining Few Distances*](https://arxiv.org/abs/1911.11688). arXiv:1911.11688v3, 7 July 2023; initial preprint 26 November 2019. This revised preprint has seven authors. [Author-hosted current PDF](https://alexricemath.com/wp-content/uploads/2023/07/LatticeDraftRevisedNew.pdf).

[5] F. Szöllősi and P. R. J. Östergård. [*Constructions of Maximum Few-Distance Sets in Euclidean Spaces*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v27i1p23). Electronic Journal of Combinatorics 27(1) (2020), P1.23. DOI 10.37236/8565; published 24 January 2020.

[6] L.-R. Bao and W.-H. Yu. [*Constructions of Large m-Distance Sets on Triangular Lattice*](https://arxiv.org/html/2509.00880). arXiv:2509.00880v1, submitted 31 August 2025. [Author code](https://github.com/BaoCoder613/triangular-m-distance).

[7] L. Wang. [*On Few-Distance Sets in the Plane*](https://arxiv.org/abs/2510.09800). arXiv:2510.09800, v2 withdrawn 9 September 2026, with the stated reason of an error in the asymptotic proof. Cited solely to document source status, not to support a theorem.

Primary web sources were checked on 4 October 2026. The completed independent novelty review is archived at `wave2/packing/few_distance_novelty/VERDICT.md`; its frozen SHA256 is:

```
93c22b77200f6e0209fea172b6e065d7edd0f89404184947a1ac5a17c04f328a
```

Its scoped conclusion supports improvements over audited published bounds, while rejecting global-optimality and unconditional worldwide-record claims.
