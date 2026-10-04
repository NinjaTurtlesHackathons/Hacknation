# Few-distance discovery log

## Source provenance

Bao–Yu, *Constructions of Large m-Distance Sets on Triangular Lattice*, arXiv:2509.00880, accessed 2026-10-04. Current HTML table lower bounds: k7=16, k10=24, k12=27, k16=37, k19=48, k23=61. They are unrestricted planar lower bounds with lattice witnesses, not optimality proofs. Source: https://arxiv.org/html/2509.00880 . Author code cloned to sibling `work/triangular-m-distance`, commit `b428a159589af30d50c3abdd3045a38c8ab9181f`, author date 2025-07-25. Three C++ files, no LICENSE file; source code was read for algorithm understanding, not copied. Our Python search is independently implemented integer norm arithmetic and greedy-color clique branching. Author acknowledges first-smallest-distance palette restriction; we search palette changes. Exact q(a,b)=a²+ab+b² corresponds to physical point (a+b/2,sqrt(3)b/2).

## Batch FD-001 — palette mutation, seed 41217

Question: improve any above lower bound through distance-palette variation. Announced to director before completion, but no persisted preregistration before execution: **retrospective registration departure**, explicitly recorded. 600 proposed experiments, max .4s clique branching each; duplicate palettes skipped. Anchors (0,0),(1,0), norms ≤100 and first k+8 norm proposals restrict completeness. Baseline first palettes reproduce n16,k7; n24,k10; n27,k12 (actually11 norms); n37,k16 (actually15 norms). Full per-attempt hypotheses (palette), seed, method, outcome and measured runtime in `search/few_distance/experiments.jsonl`. No improvement. k19 shortest palette cannot attain inherited48 baseline; this is known, because replacing48 by49 supplies the alternating hexagon. k23 first palette is below the regular-hexagon61 construction. These are source mechanism reproductions, not discoveries.

## Batch FD-002 — preregistered point-set annealing, seed 41218

Question: for n28,38,49,62 can one reach at most12,16,19,23 norms respectively? Initialize independently reconstructed baseline plus one site. Search finite triangular lattice disk q≤100, swaps preserving cardinality/injectivity. Incrementally update norm multiplicities; minimize number of distinct norms, with annealed tie-breaking based on rare norms to escape plateau. Four targets × up to250,000 proposals. Success requires exact integer witness above threshold; independent verifier decides validity later. Stop/escalate after this batch if no improvement: change to structured cut-and-paste family or abandon rather than repeat unchanged annealing. This restricted search cannot prove global optimality or nonexistence.

Outcome: all negative. Actual seeds41230/41234/41237/41241,250000 proposals each. Best counts respectively13,17,21,26; measured runtimes7.31,5.45,4.48,3.85 seconds. Exact baselines n48,k19 and n61,k23 independently reconstructed. Both methods stalled, so representation is changed again.

## Batch FD-003 — preregistered asymmetric lattice windows

Question: do asymmetric convex lattice hexagons or rounded ellipse windows improve any published bound k7..34? Deterministic enumeration of `{(a,b):0≤a≤A,0≤b≤B,L≤a+b≤U}` with A,B≤14, cardinality≤110, followed by disc/ellipse windows. No assumed reflection/equal-side symmetry. Evaluate exact norm sets; save only witnesses strictly improving current table lower bound. Success ≥1 extra point at same or lower distance count. Escalate if all negative, do not claim novelty of window search itself. Source table values for k7..34 captured directly from arXiv HTML; k19=48,k23=61,k24=63. Finite shape enumeration is not an unrestricted nonexistence proof.

Outcome:62699 evaluated windows,4.61 seconds, all negative. Subsequent literature audit strengthened k25baseline64,k31baseline80 from Ahmed–Snevily2013; negative result remains negative against the stronger bounds. No more unchanged discovery batches. Switch to independent certification/adversarial audit per director.

## Revised literature baseline and assumptions

Ahmed–Snevily, EJC20(4)P33 (2013), https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i4p33/pdf/ , lists EXACT-k bounds through50. Combining and monotonizing gives at-most-k:

`k7..50 = [16,19,21,24,27,27,31,34,37,37,42,45,48,49,55,58,61,63,64,69,72,75,75,79,80,85,88,91,96,96,102,105,108,109,109,115,115,121,124,127,129,135,135,141]`.

The2015 Ahmed–Wildstrom paper (author PDF https://tanbir.github.io/files/preprints/ahmed_wildstrom_distance_sets.pdf , publication index https://tanbir.github.io/publications.html) proves the cycle-bounded boundary-difference theorem, so that is excluded as a new discovery. Its tables concern hexagon distance enumeration rather than stronger small-k witnesses. No primary bound table k51..100 was located; missing source coverage is a limitation. Source text typo: Bao–Yu prose regular hexagon side4 has63 points, while exact count is61 and its table k23 agrees. All found current construction thresholds remain only lower bounds; upper/global optimality cannot be inferred.
