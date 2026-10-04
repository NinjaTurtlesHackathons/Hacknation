# Certificate-First Search for Geometric Extremal Problems
## A reproducible negative research checkpoint

AI Agent Lab · Human research direction: Laurenz Thümmler · Computation, coordination and drafting: Codex agent team · 4 October 2026

**Status:** working manuscript for review. No new geometric discovery is established. [GE-STATUS]

### Abstract

The strongest confirmed derived result of this checkpoint is a quantitative local-exclusion lemma for a known fifteen-point square-torus packing: after fixing translation, no distinct equal-or-better labelled configuration exists within a strict displacement neighborhood of radius 1/3920 in the maximum coordinate norm. An elementary cycle-sum proof and an independent exact dependency checker establish the explicit constant. The mechanism and baseline are known; novelty is not established. We also independently certify inherited area, packing and few-distance witnesses. An adaptive area campaign of 1,840 candidate trials found no certified improvement of at least 0.05% over frozen comparison witnesses. The archive retains source snapshots, seeds, negative trials and claim identifiers. No new record, global optimum, counterexample or exceptional-discovery goal is achieved. [GE-LOCAL-CYCLE; GE-BASE-TRIANGLE14; GE-BASE-CONVEX15; GE-AREA-NEGATIVE; GE-STATUS]

### 1. Confirmed results and their limits

**Main derived result: explicit local exclusion for a known torus packing.** Let
\[
p_i=\left(\frac{i}{15},\frac{4i\bmod15}{15}\right),\qquad i=0,\ldots,14,
\]
on the fixed square torus \(\mathbb R^2/\mathbb Z^2\). Its least periodic squared separation is \(17/225\). Take compatible labelled lifts \(q_i=p_i+u_i\), remove common translation so \(u_0=0\), and put \(\varepsilon=\max_i\|u_i\|_\infty\). If \(\varepsilon<1/3920\) and the least periodic squared separation of \(q\) is at least \(17/225\), then every \(u_i=0\). This excludes improved or distinct equally good packings in that explicit neighborhood, without excluding better packings elsewhere. The checker verifies graph, lift and constant identities; the elementary proof below supplies the implication. No formal proof assistant or new-mechanism claim is made. [GE-LOCAL-CYCLE; GE-BASE-TORUS15]

**Proof.** Two directed cycles use label steps one and four, each coprime to fifteen. Their constant shortest-contact lifts are
\[
z_1=(1,4)/15,\qquad z_2=(4,1)/15.
\]
For a selected edge \(i\to j\) in cycle \(s\), the original integer-period shift remains an allowed lift for \(q_j-q_i\). It need not remain the nearest lift: the assumed periodic separation lower bound applies to every lift. Consequently
\[
2z_s\cdot(u_j-u_i)+\|u_j-u_i\|_2^2\geq0.
\]
Since \(\|u_j-u_i\|_2^2\leq8\varepsilon^2\), write \(a_{ij}=z_s\cdot(u_j-u_i)\geq-4\varepsilon^2\). The sum of these fifteen quantities around each directed cycle is zero. Therefore \(a_{ij}\leq4(15-1)\varepsilon^2\), and hence \(|a_{ij}|\leq4(15-1)\varepsilon^2\). Every label is reached from zero within at most fourteen cycle edges, giving
\[
|z_s\cdot u_i|\leq4(15-1)^2\varepsilon^2\quad(s=1,2).
\]
The matrix with rows \(z_1^T,z_2^T\) has inverse
\[
Z^{-1}=\begin{pmatrix}-1&4\\4&-1\end{pmatrix},
\qquad\|Z^{-1}\|_\infty=5.
\]
Thus \(\|u_i\|_\infty\leq4\cdot14^2\cdot5\,\varepsilon^2=3920\varepsilon^2\). Taking the maximum yields \(\varepsilon\leq3920\varepsilon^2\). Either \(\varepsilon=0\) or \(\varepsilon\geq1/3920\); the strict neighborhood assumption rules out the latter. This is local isolation modulo translation, not global optimality. [GE-LOCAL-CYCLE]

**Inherited area certificates.** The independently recomputed values are

\[
A_{\triangle,14}\geq
\frac{11887886553786386257916512167}{500000000000000000000000000000},
\qquad
A_{\mathrm{convex},15}\geq
\frac{49128111226460317685888607941}{1999999999999999257563094398721}.
\]

These lower bounds certify external constructions. The triangle coordinates come from David Cantrell's arrangement, as provided through the current Tej Stead author table; the free-convex coordinates come from Tej Stead's construction. The rational literals, rather than an idealized numerical limit, are the certified objects. The free-convex witness has eleven hull vertices. Neither value is presented as a new bound. [GE-BASE-TRIANGLE14; GE-BASE-CONVEX15; GE-PROVENANCE]

| Certified object | Exact witness property | Interpretation | Claim |
|---|---|---|---|
| Triangle, 14 points | Normalized least area \(\approx\)0.023775773107572774 | External baseline reproduced | GE-BASE-TRIANGLE14 |
| Free convex hull, 15 points | Normalized least area \(\approx\)0.02456405561323017 | External baseline reproduced | GE-BASE-CONVEX15 |
| Square torus, 15 points | Squared periodic separation 17/225 | Known lattice seed reproduced | GE-BASE-TORUS15 |
| Square torus, 209 points | Squared periodic separation 241/43681 | Known lattice seed reproduced | GE-BASE-TORUS209 |
| Right-triangle packing, 22 circles | Radius \(\approx\)0.07289508087527324 | Existing packing made into a rational witness | GE-BASE-PACK22 |
| Triangular lattice, 27 points | Exactly 11 squared-distance values | Inherited few-distance witness | GE-BASE-FD12-27 |
| Triangular lattice, 61 points | Exactly 23 squared-distance values | Inherited few-distance witness | GE-BASE-FD23-61 |

Approximate displays in this table are not the certificates. The exact fractions, coordinates, complete comparison sets and checksums are stored in `tables/claims.json` and are recomputed by `certification/verify.py`. The few-distance properties are properties of the stored witnesses, not claims that these rows are the strongest published cardinality bounds. [GE-PROVENANCE; GE-STATUS]

### 2. Problem definitions and normalization

For distinct points \(P=(p_1,\ldots,p_n)\), define

\[
D_{ijk}=\det(p_j-p_i,p_k-p_i),\qquad
m(P)=\frac12\min_{i<j<k}|D_{ijk}|.
\]

The fixed-triangle objective is \(m(P)/\operatorname{area}(T)\), where the rational reference triangle is \(T=\{(x,y):x\geq0,\ y\geq0,\ x+y\leq1\}\). Since its area is one half, the normalized objective is **the minimum absolute determinant**, with no further division by two. The free-convex objective is \(m(P)/\operatorname{area}(\operatorname{conv}P)\), requiring a nondegenerate hull and permitting interior points. An invertible affine map multiplies all areas by the same positive factor and therefore preserves both normalized ratios. This is a standard invariance argument, not a claimed new geometric theorem. [GE-BASE-TRIANGLE14; GE-BASE-CONVEX15]

On the square flat torus, representatives lie in \([0,1)^2\). Set \(\delta_x=\min(|x_i-x_j|,1-|x_i-x_j|)\), and similarly for \(\delta_y\); the objective is the least \(\delta_x^2+\delta_y^2\), capped by the self-translate squared separation one. A corresponding packing radius is half the square root of this objective. Conjecture tests must separately validate their domain of applicability; a witness outside the stated range cannot be a counterexample. [GE-BASE-TORUS15; GE-BASE-TORUS209]

Equal-circle packing in the reference right triangle requires radius \(r>0\), center coordinates \(x_i,y_i\geq r\), diagonal distance \((1-x_i-y_i)/\sqrt2\geq r\), and squared pair separations at least \(4r^2\). The irrational diagonal constraint is checked rationally by first testing nonnegative slack, then \((1-x_i-y_i)^2\geq2r^2\). [GE-BASE-PACK22; GE-BASE-PACK23; GE-BASE-PACK24]

For the triangular-lattice few-distance representation, coordinates are in the basis \((1,0),(1/2,\sqrt3/2)\). Squared Euclidean separation is the exact integer or rational expression \(\Delta x^2+\Delta x\Delta y+\Delta y^2\). The verifier counts its distinct values over every pair, rather than inferring a count from symmetry. [GE-BASE-FD12-27; GE-BASE-FD23-61]

### 3. Certificate method and elementary soundness argument

The acceptance checker imports no search optimizer. It parses integer or rational-string coordinates, refuses floating-point coordinates and agent-supplied tolerances, checks distinctness and region membership, and computes every required pair or triple using exact rational arithmetic. For a free hull it independently constructs the monotone-chain convex hull and computes its shoelace area. [GE-SELFTEST; GE-BASE-TRIANGLE14; GE-BASE-CONVEX15]

The soundness argument is direct. If all region constraints pass and every determinant has absolute value at least \(b\), the listed finite configuration is an existing feasible witness with normalized least area at least the appropriately normalized \(b\). For a rational free-hull ratio \(u/v\), comparing it with \(a/b\) reduces to the integer inequality \(ub\geq av\), with positive denominators. Pair-distance and circle-containment certificates follow by the same finite enumeration and algebraic inequalities. This establishes the witness property; it excludes no other configuration. No local stationarity assumption enters acceptance. [GE-BASE-TRIANGLE14; GE-BASE-CONVEX15; GE-BASE-PACK22]

The checker passes the 22 positive and negative controls recorded in the reviewed claim table. Controls include normalization, overlap, periodic wraparound, duplicates, degeneracy, malformed problem types and forbidden agent tolerances. This finite test suite is evidence of implemented behavior, not a formal proof of the Python interpreter or of absence of all software defects. [GE-SELFTEST]

### 4. Adaptive discovery and negative outcomes

Candidate generation combined analytic oriented-determinant epigraph optimization with changes of order type, deletion and insertion across neighboring point counts, native simulated annealing and transfer from a disk configuration to a free convex hull. Seeds and failed outputs were saved. The area register contains 1,840 trials; it found no certified improvement of at least 0.05% over the frozen same-normalization triangle, free-convex and adjacent-case incumbents. [GE-METHOD; GE-AREA-NEGATIVE]

The sum of recorded area candidate wall durations is 161.581625 seconds. This excludes source retrieval, compilation, reporting and director/team work; it is neither CPU time nor total research-session time. It supports no speedup claim. [GE-AREA-RUNTIME]

The strongest retained searches at the principal targets have exact values

\[
\frac{118878865537659017321655259}{5000000000000000000000000000}
\quad\text{and}\quad
\frac{1256922519001955210918702140}{51169177386367479355299145589},
\]

for triangle fourteen and free-convex fifteen respectively. Both are below their inherited comparison witnesses. They are independently checked feasible constructions, not improvements. [GE-SEARCH-TRIANGLE14; GE-SEARCH-CONVEX15]

Certified neighboring-case candidates and torus searches are retained in the same claim registry. Their existence supports replay and diagnostics; it does not establish a global upper bound or verify an open conjecture. A failed finite search cannot justify “no better construction exists.” [GE-SEARCH-CONVEX14; GE-SEARCH-CONVEX16; GE-SEARCH-TRIANGLE13; GE-SEARCH-TRIANGLE15; GE-SEARCH-TORUS14; GE-SEARCH-TORUS15; GE-SEARCH-TORUS16; GE-STATUS]

### 5. Adversarial corrections and literature provenance

Adversarial review corrected two acceptance defects: a crash on a nonstring problem field, and a false Markov-conjecture counterexample classification outside the published range \(N\geq6\). The known two-point packing is now rejected as a purported counterexample. Circle-packing provenance was also corrected from circle-in-circle attribution to the right-triangle CRT coordinate source. These corrections materially affected acceptance and attribution; they are documented defects, not hypothetical risks. [GE-AUDIT-SCOPE]

One material geometric distinction is visible directly in the exact certificates. The frozen triangle-fourteen and free-convex-fifteen coordinate literals each have **one exactly minimizing triple**. Source descriptions of twenty-three and twenty-five active triangles refer to numerical near-ties. Treating those counts as exact would change the mathematical statement. The archive preserves the distinction. [GE-EXACT-TIES]

Known torus lattice seeds are credited to Connelly and collaborators. Current Heilbronn coordinates are credited to the Tej Stead table and its named original contributors. Few-distance comparison research must combine Bao–Yu's recent work with Ahmed–Snevily's older results rather than using a recent table alone. Public constructions and external verifiers are prior art; rechecking them is not a new discovery. [GE-PROVENANCE; GE-STATUS]

Primary coordinate source snapshots have URLs and SHA256 identifiers in the claim registry. A source snapshot is a reproducible comparison object, not an assurance that every later preprint or unpublished construction has been found. Any future record claim needs a fresh comparison audit and an independently verified strict margin. [GE-PROVENANCE; GE-STATUS]

### 6. Autonomy, contribution and reproduction

The human supplied the repository, research direction, ambition and authorization for autonomous delegation. Codex selected targets and methods and coordinated a director with three concurrent agent roles through literature, discovery, independent certification and adversarial review waves. Public-source constructions were inherited openly. No external researcher endorsement, formal Lean proof, statistical speedup or cost benchmark is claimed. One palette-search batch was registered retrospectively and is disclosed rather than described as prospective. [GE-METHOD]

The canonical accepted statements live in `projects/geometric_extremal/state.json` and `tables/claims.json`; the offline demonstration reads only `tables/demo_data.json`. The geometry viewer labels floating-point calculations as illustrations and exposes the fixed exact certificate and a bound-threshold test using integer cross multiplication. Every result in this manuscript is attached to a claim identifier. [GE-METHOD]

Run the standard-library verifier with `python3 research/geometric-extremal/certification/verify.py --selftest`. Rebuild the offline visualization with `python3 research/geometric-extremal/demo/build_demo.py`. The existing lab integration, frozen witnesses and registered search scripts are described in the research README and checkpoints. Search replay requires the numerical environment; independent witness verification requires only Python's standard library. [GE-SELFTEST; GE-METHOD]

### 7. Research boundary and continuation

The current artifact is a reviewable checkpoint with exact inherited witnesses, retained negative searches and a reusable acceptance layer. It does not fulfill the exceptional-discovery ambition. Further work should change the search representation or problem portfolio, such as contact-graph program search, certified combinatorial relaxations or more recently moving higher-point frontiers, rather than repeat unsuccessful schedules unchanged. A future paper should begin with a new verified geometric result if one is obtained; this manuscript's novelty status must remain conditional until then. [GE-STATUS; GE-AREA-NEGATIVE]

### Sources

- Cantrell / Tej Stead. [Triangle n=14 coordinate source](https://math.tejstead.com/heilbronn/triangle/14/points.json). Frozen checksum in GE-BASE-TRIANGLE14.
- Tej Stead. [Free-convex n=15 coordinate source](https://math.tejstead.com/heilbronn/convex/15/points.json). Frozen checksum in GE-BASE-CONVEX15.
- Connelly and collaborators. [Original square-torus paper](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf). Provenance GE-BASE-TORUS15 / GE-BASE-TORUS209.
- Packomania. Right-triangle CRT coordinate source (see corrected provenance in GE-AUDIT-SCOPE). Provenance GE-BASE-PACK22 / GE-BASE-PACK23 / GE-BASE-PACK24.
- Bao and Yu. [arXiv:2509.00880](https://arxiv.org/abs/2509.00880). Read together with older Ahmed–Snevily comparison results, as recorded in GE-PROVENANCE.
- AI Agent Lab. `tables/claims.json`, `projects/geometric_extremal/state.json`, and the archived certificate and experiment artifacts. These are the exclusive sources of this checkpoint's computed result statements.
