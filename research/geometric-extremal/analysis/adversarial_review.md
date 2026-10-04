# Independent certification and adversarial review

Reviewed 2026-10-04. **No new geometric discovery is certified.** The accepted numerical witnesses reproduce known constructions or remain below frozen comparators. The quantitative local-exclusion lemma below is sound within its explicit hypotheses, but novelty has not been established.

## Independent computation

`certification/independent_audit.py` imports neither discovery code nor `certification/verify.py`. It clears all rational denominators into integers, computes triangle determinants, builds convex hulls by gift wrapping rather than the primary verifier's monotone chain, expands triangular-lattice Cartesian squared distances, checks all nine neighboring torus copies and shortest self-copy, and tests right-isosceles-triangle packing constraints exactly. Floats, tolerances, duplicate points, invalid domains and false asserted bounds are rejected. Triangle-container objectives divide physical triangle area by container area; square/disk areas are physical areas and convex objectives divide by the exact hull area. Disk convention is radius one.

The latest frozen comparison (`analysis/adversarial_snapshot.json`) records SHA256 of every input: **1690 tagged witnesses, zero acceptance or exact-objective disagreements**, measured 21.302 seconds. Counts: 975 convex-area, 675 triangle-area, 25 torus, 12 few-distance and 3 circle-packing witnesses. Metadata objects were skipped (548). Twenty accepted lab cases separately agree across evidence SHA256, explicitly typed canonical import, exact gate result, and rationally normalized demonstration coordinates. Two original archived area-source files omit a problem tag; the import explicitly supplies triangle/convex type. This was checked against domain and source assumptions, rather than interpreted as an invalid geometric construction.

Three empty area attempts are rejected by both checkers: `triangle14_anneal_1668.json`, `triangle14_local_1003.json`, `triangle14_local_1011.json`. They are not among accepted claims. The snapshot is finite: ongoing discovery can create later files. No finite failed search proves a global bound.

Independent controls: **23/23 pass**, and their accept/reject decisions agree with the corrected primary verifier. Controls cover forbidden distance classes, Euclidean-versus-triangular interpretation, boundary excess smaller than floating precision, periodic wraparound, collinearity, malformed scalar types, duplicate points, denominator zero, arbitrary bound inflation and agent-provided tolerances. CLI returns nonzero for any rejected file. `--tree` returns nonzero when archived negative controls/invalid attempts are present, intentionally.

## Material attacks and repairs

1. The original torus checker would label the two-point configuration `(0,0),(1/2,1/2)` a Markov counterexample. This is false attribution: Connelly et al. Conjecture2 explicitly assumes **N>=6** ([2017 primary PDF](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf), PDF page28). The exact algebraic excess is positive (23/625), but the conjecture does not apply. The root checker now enforces applicability and rejects the counterexample assertion; independent regression agrees. Ordinary N2 objective computation remains valid.
2. Nonstring `problem` caused an uncaught `startswith` error. Root added a type guard; independent malformed control rejects it.
3. Packing claims originally linked the circle-in-circle table while their witnesses were right-triangle packings. Root corrected each to its exact `https://packomania.com/crt/txt/crt{n}.txt` provenance. All three current claim URLs agree with evidence. This was a source-attribution defect, not a feasibility failure.

No remaining false acceptance was found in this snapshot. Exact feasibility is not a novelty or global-optimality certificate. Bound fields are independently recomputed and cannot inflate geometric objectives. Auxiliary metadata alone cannot establish a result.

## Local exclusion proof and family audit

The argument in `search/contact_graph/general_cycle_lemma.md` is **sound conditional local exclusion**. Two directed Hamiltonian cycles must have constant linearly independent lift vectors z1,z2, both of the actual shortest-contact length. After translation fixes u0=0, epsilon is the maximum labelled displacement supnorm. Pair feasibility applies to every periodic copy, including the selected original contact lift even if that lift stops being nearest. No assumed retained contact, differentiability or optimizer stationarity is needed.

For each contact, z·(uj-ui)>=-4epsilon². Its cycle projections sum to zero, so each is <=4(n-1)epsilon². A path of at most n-1 edges bounds each projection by4(n-1)²epsilon². With K=||Z inverse||infinity, epsilon<=4(n-1)²K epsilon². Thus strict epsilon<1/[4(n-1)²K] forces epsilon=0. Equality is deliberately excluded. Independent directions and Hamiltonicity cannot be dropped. Compatible labelled lifts and translation gauge are explicit, not silently supplied by arbitrary nearest-neighbor matching.

`analysis/local_exclusion_independent.json` reconstructs every N15 contact offset, both cycles, actual minimum17/225, matrix inverse and constants4,56,784,5,3920. It does not merely repeat rank28. Common translations are removed by gauge; continuous Euclidean rotations generally change the fixed square torus period geometry and do not invalidate the proof.

`analysis/gaussian_family_independent.json` independently checks every nonzero modular difference using all nine integer-period images, scans second-cycle congruences, and reconstructs inverses by determinant. It confirms:

|N|squared separation|second cycle|K|strict supnorm radius|
|---|---|---|---|---|
|15|17/225|4|5|1/3920|
|209|241/43681|56|19|1/3288064|
|2911|3361/8473921|780|71|1/2404940400|

N2911 required2910 differences and0.166 seconds. Translation invariance justifies this compact reduction only for the explicitly prescribed cyclic family; it is not permission to bypass arbitrary-witness checks. The lemma does not claim global optimality, all coprime Gaussian parameters having these shortest contacts, or a new family. Its role is a rigorous local search-pruning mechanism.

## Novelty and comparator attacks

The 2025/2026 Bao–Yu few-distance table is not uniformly strongest. [Ahmed–Snevily2013 primary paper](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i4p33/pdf/) gives stronger lower bounds at k25 (64) and k31 (80). Its exactly-k convention implies at-most-k lower bounds by monotonicity; it does not imply those are global maxima. [Ahmed–Wildstrom2015 primary preprint](https://tanbir.github.io/files/preprints/ahmed_wildstrom_distance_sets.pdf) already supplies a boundary-difference mechanism for cycle-bounded triangular sets. Neither that mechanism nor bladed hexagon families should be claimed new. Bao prose side4 count63 conflicts with exact count61 and its own k23 table; comparisons use the verified table/construction.

The [September2026 unit-distance22 project](https://artwaste.land/strata/the-sixty-first-distance/) claims u22=60 via complete48-slice enumeration. We have not independently audited its exhaustive package. Therefore22=61 cannot be described as the first established open target, and the claimed resolution is a literature-status gap requiring package review, not a theorem endorsed by this report. Current unrestricted torus conjecture status also remains a citation-forward audit gap despite the confirmed2017 formulation. Old tables are not proof of latest-worldwide records.

## Reproduction

From repository root:

```sh
.venv/bin/python research/geometric-extremal/certification/independent_audit.py --selftest
.venv/bin/python research/geometric-extremal/certification/independent_audit.py --local-proof
.venv/bin/python research/geometric-extremal/certification/independent_audit.py --tree research/geometric-extremal/candidates > /tmp/geometric-independent-current.json
```

The last command checks the current archive independently and reports all input hashes; expected negative attempts make its exit status1. For a single accepted canonical geometry, pass its JSON path directly. Raw archived source files lacking type tags must be supplied via the lab's explicitly typed canonical import. Snapshot hashes bind the finite comparison; later CLI-only additions are recorded separately. No human mathematical hint was used in this audit; root/other agents supplied the candidates and proposed lemma, and this agent reconstructed the constraints and proof dependencies independently.
