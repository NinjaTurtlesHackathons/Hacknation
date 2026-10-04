# Joint shape and palette search: provisional findings

The strongest candidate is 81 triangular-lattice points with exactly 31 nonzero Euclidean distances. Discovery artifact: `../../../candidates/wave2_joint_palette/k31_n81_r6_seed42102.json`; SHA256 a85a2a990531ebd5b40165eacb0f23c84bac6676404cb858f7b5c2c63b83d94c. Ahmed–Snevily 2013 explicitly publishes 80 at31; Bao–Yu 2025 displays 79. The parent director reports agreement of two independent integer checkers on all 3240 pairs. This report supplies discovery evidence; comprehensive novelty review remains separate.

The witness is all lattice sites inside an exact convex decagon, with only one reflection symmetry among the lattice dihedral transformations. Its squared-distance palette is

`1,3,4,7,9,12,13,16,19,21,25,27,28,31,36,37,39,43,48,49,52,57,61,63,64,67,73,75,76,79,91`.

It exchanges the shortest 31st lattice norm 81 for norm 91; norm 84 is also absent. Thus it lies outside a search restricted to the 31 shortest norms. This demonstrates a failure of that search restriction to reproduce our witness, not a new counterexample to a conjecture of global maximality. Its ten supporting inequalities and lattice saturation are in `k31_structure.json`. The necessary one-layer Pa-plus-unit-triangle-blades test in `bladed_membership.py` found no matching core within the parameter ranges explicitly examined by Ahmed–Snevily 2013. This is not a complete proof of nonmembership in all conceivable bladed constructions.

## Discovery and continuation

The joint model chooses a Boolean variable for every lattice site and every squared norm. A pair of selected sites forces its norm variable, and the sum of norms is bounded byk. Maximizing selected sites allows simultaneous changes of shape and distance alphabet. Matching and explicit disjoint triangle/edge covers add necessary conditional inequalities. Their validity follows from checking the graph edges, without trusting a numerical optimizer.

Seed 42102, r6 hexagonal window, k31, target81: HiGHS recovered 81 in 4.143 seconds and 9 nodes. No other r6 selected target gained a point. Neighbor batch43300 tested29,30,32,33,35,36,38,39,41,42,44,45 with origin free, and found no new gain. These are finite-window solver observations; no exclusion theorem is claimed. A radius7 CP-SAT continuation with the 37-site radius3 interior fixed and hint 81 returned 81 after 89.812 seconds. Larger k50 searches reproduced the published 141-point construction. A 91-site fixed core constrained its local search to 141; a free larger radius9 search retained 141 after 180 seconds, with an unresolved finite bound 166.

All prospective methods, seeds, solver limits, observations, interrupted work, and timings are in `experiments.jsonl` and batch logs. Four weak regular-hex 127 hints were replaced by independently counted source hints129/135/135/141. Cover-cut low-k disk runs reached limits without incumbents and were adaptively stopped. Source warmhint translations, complete pair counts, and minimal fitting radii are recorded in `source_hint_validation.json`. Full CP-SAT models are archived as text. Exact known 61/23 and141/50 positive controls are labelled baseline reconstructions, including their synthetic success thresholds.

## Accounting correction and limits

A compacted handoff mistakenly summarized the first r6 batch as entirely negative. A fresh raw-register status audit detected the successful 81/31 artifact. `candidate_gain_audit.json` mechanically checks every candidate cardinality and all norms against the consolidated published table, preventing recurrence of a prose-summary omission. No code or witness was fabricated by this correction. Current scan status and primary PDF hash are in `source_status.json`.

The mirror of arXiv2510.09800 still hosts a paper whose official arXiv v2 was withdrawn 9 September 2026 for an error in the asymptotic proof. It is not used as an established theorem. Source files retain author attribution; PDF reuse rights were not independently resolved.

Reproduction:

```
.venv/bin/python research/geometric-extremal/wave2/literature/joint_palette/search.py --radius 6 --targets 31 --seconds 180 --seed 42102
```

The solver version, single thread, and heuristic tie-breaking can change the particular witness. Verify the frozen JSON directly for deterministic mathematical reproduction. Search-side exact counting is not an independent certificate. Source novelty, independent certification, scientific significance, and global optimality are distinct questions.
