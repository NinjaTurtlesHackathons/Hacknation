# Torus search checkpoint

2026-10-04. No counterexample and no new record. The primary conjecture is Connelly–Funkhouser–Kuperberg–Solomonides, DCG58(2017), [author PDF](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf), Conjecture2. Current unresolved status remains a literature-audit gap. Numerical separation is d²; violation requires d²>2/(sqrt(3)N)-8/(25N²), equivalently M>25/4. The cited paper already covers grid-like families; those are baselines, not discoveries.

Known n15 and209 Gaussian lattice witnesses were independently verified with exact modular integer coordinates. An initial save rounded them at scale1e12; this was feasible but lost a small amount of separation. Corrected baseline files now use scaleN and exactly attain17/225 and241/43681. This correction is logged, not concealed.

Initial prospective seeds1000–1019 generated60 optimizer calls: n14 single-disk deletion, n15 low-Fourier symmetry-release, n16 farthest-hole insertion. Sum of measured optimization times1.104seconds. Numerical best d²: n14 .07627462562268994; n15 known17/225; n16 .06698729810778054. Rounded rational candidates independently passed `certification/verify.py`; none cross the conjecture threshold. These small-N packings reproduce known-looking values; no novelty claim.

Distinct discrete search enumerated20085 cyclic-slope constructions `[(k/N,s*k/N) mod1]`, n6..200 and all slopes. Integer residue objectives are exact; Markov diagnostic ranking used doubles. Maximum occurred at n15 slope4 or11, M≈6.24009237739792. This is only that finite cyclic family, not all lattices or arbitrary packings.

Topology-change pivot seeds2000–2019 removed three discs, relaxed the n12 system, and reinserted discs one at a time in farthest holes, optimizing at n13/14/15. All20 reconstructions returned the n15 lattice objective or below. Every rebuilt rational witness is saved. First attempt hit numpy-bool JSON serialization after saving seed2000; corrected with explicit bool casts and reran the prelogged batch. No hidden successful experiment occurred.

Structural diagnostic: known n15 contact graph has30 edges and numerical rigidity rank28 (2N-2), with uniform stress in equilibrium to ~6.4e-16. This is a numerical diagnostic, not a new theorem or global-optimality claim. It explains why modest local deformations return to the lattice; a successful future attack needs different periodic contact topology.

Reproduce from repository root:

```sh
.venv/bin/python research/geometric-extremal/search/torus/search.py --seconds 90
.venv/bin/python research/geometric-extremal/search/torus/lattice_audit.py
.venv/bin/python research/geometric-extremal/search/torus/defect_rebuild.py
.venv/bin/python research/geometric-extremal/certification/verify.py research/geometric-extremal/candidates/torus/baseline_n15.json research/geometric-extremal/candidates/torus/baseline_n209.json
```

Next: stopped stagnant small-N path and pivoted to circle packing in the right triangle at root request. Future torus work should attack noncyclic, nonlattice contact graphs or larger-N defect structures, and first complete citation-forward novelty audit. Scripts append to the experiment register on rerun.
