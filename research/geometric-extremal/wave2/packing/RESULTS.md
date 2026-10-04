# Wave 2 completed: two new representations, no discovery claim

**No strict Markov-conjecture counterexample or audited current record was found.** All24 saved rational packings pass the independent exact all-pair checker; none passes its algebraic counterexample test. The published comparison remains distinct from an internal search baseline.

## Executed campaign

1. Periodic Delaunay/Voronoi cavity beam reconstruction:180 jobs,480 optimized endpoints,20.069794916998944 seconds of measured whole-campaign time. Each job removed5–7 coherent points; changes were round cavities or oriented elongated seams, followed by different largest-empty-circle insertion programs. The first120 jobs covered N14–21; subsequent wider-beam jobs concentrated on the three closest threshold ratios. The registered stagnation rule stopped after108 nonimproving jobs. There was an implementation failure before the first cavity job (NumPy RHS shape), recorded and repaired without changing the hypothesis. Initialization was repeated; no failed discovery endpoint was hidden.
2. Mixed-count closed-geodesic rows:11,736 discrete programs enumerated,11,216 optimized,520 skipped by the within-row necessary bound;104.75131162499747 seconds measured after enumeration. Rows carried2–7 uniformly spaced points,3–6 rows, six primitive integer windings, and two deterministic phase starts. This was a low-dimensional structural search, independent of the first representation. Enumeration concerns discrete programs and starts; local optimization does not exhaust their continuous realizations.
3. One unrestricted all-pair release for each of eight best row-program candidates:0.22488508300011745 seconds. No counterexample resulted. N17 andN19 improved over their restricted row values, showing a meaningful effect from releasing the row assumption. The reproducible script was saved after this equivalent inline execution; the original register remains intact.

The sum of these measured campaign clocks is about125.05 seconds of computation with one compute process at a time. It excludes source research, implementation, enumeration before the row timer, later exact rechecks, and report writing. It is not a claimed end-to-end human research duration.

## Candidate outcomes

| N | Best cavity squared separation (numerical) | Best restricted row squared separation (numerical) |
| --- | --- | --- |
| 14 |0.07627462562268994|0.0669872981076616|
| 15 |0.07555555555555553|0.0755555555555554|
| 16 |0.06698729810778027|0.0636218245269219|
| 17 |0.06008213174756866|0.056197555156638684|
| 18 |0.059073014802393485|0.0583291340222787|
| 19 |0.053878902373608706|0.05000013371386157|
| 20 |0.053316923812934784|0.05358983848622427|
| 21 |0.04959203617327806|0.04513888888881233|

The row program improved our N20 cavity value. Its independent exact witness has

`d² = 10717967697238891693049/200000000000000000000000`.

This is **an internal method comparison**, not a current record. The numerical value resembles `(2-sqrt(3))/5`; algebraic identification and historical attribution have not been certified and are not claimed. N15 only reproduces the known17/225 packing. The primary 2017 paper already contains that strong Gaussian example and warns about its numerical table's lower apparent value.

The cavity programs genuinely encountered changed periodic triangulations:323 of480 starting endpoints and365 final endpoints had both degree5 and degree7 vertices. Qhull's choice in cocircular configurations and the fact that Delaunay edges need not be shortest-distance contacts mean this diagnostic does not certify a mechanically relevant new defect family. Recorded integer triangle shifts telescope to zero. Whole-packing rational checks, rather than those graph diagnostics, establish feasibility.

## Structural lesson and next selection

The derivation in ROW_STRUCTURE.md proves that three uniform diagonal geodesic rows with five points each have `d²<=17/225`; this explains the strongest reproduced case within a precisely restricted class. It is not a global torus bound, and novelty of the mechanism remains unverified. Mixed counts frequently create short cross-row distances because tangential differences use the lcm grid. Neither of these observations justifies more identical starts.

A bounded-container alternative worth preparing next is **point separation in the right-isosceles triangle at N154–156**, using boundary/interior contact surgery and transfer between adjacent counts. The fresh [HAMSP2025 primary paper](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2025.pdf), Table2, reports distance0.06476033 for N154 and0.06432531 for N156 in its normalization; these supersede older table comparisons under the same normalization. The tiny N154 improvement is a precision-audit warning, not evidence of easy improvement. Source coordinates, exact domain normalization and unrounded objectives must be checked before a record claim; the paper contains no located code/data link. This is a grounded selection candidate, not an unexecuted result presented as research success.

Torus current openness and current N17–21 incumbents remain unconfirmed. Fresh searches on2026-10-04 found the primary2017 conjecture and newer different-assumption material, but absence of a later refutation is not proof of openness. Authorship was freshly corrected to Connelly, Funkhouser, Kuperberg and Solomonides.

## Reproduction and artifacts

From repository root:

```sh
.venv/bin/python research/geometric-extremal/wave2/packing/cavity_search.py --seconds 240
.venv/bin/python research/geometric-extremal/wave2/packing/geodesic_rows.py --seconds 180
.venv/bin/python research/geometric-extremal/wave2/packing/release_rows.py
```

Runs append new prospective/results records; do not rerun merely to increase counts. Candidate files are under `candidates/wave2_packing/`. `independent_candidate_checks.json` contains fresh exact rechecks of all24 files. `experiments.jsonl`, `row_experiments.jsonl`, and `row_release.jsonl` preserve programs, coordinates, winding data, optimizer failures/status, seeds and timing. HYPOTHESES.md and ROW_STRUCTURE.md document restrictions and structural reasoning.
