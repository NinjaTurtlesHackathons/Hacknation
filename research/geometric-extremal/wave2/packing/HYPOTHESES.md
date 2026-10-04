# Wave 2: periodic cavity programs

## Structural decision

The verified two-spanning-cycle mechanism excludes small improvements near the Gaussian baseline. Previous increment-3 forcing did reach a different contact requirement but only in a restricted small patch. This wave removes five to seven points simultaneously, leaving a true periodic cavity, and reconstructs it through periodic Voronoi vertices. Round cavities and elongated seams probe different patch boundaries. Beam branching selects different insertion programs and is followed by full pairwise geometric relaxation. The representation is the discrete sequence of hole choices, rather than independent coordinate jitter.

Periodic Delaunay triangles supply a diagnostic of changed topology. Degree-5 and degree-7 vertices may appear; their presence is measured, never presumed from the name of the method. Qhull may choose different diagonals in cocircular cases, so degree changes alone cannot certify a mechanically relevant dislocation. Integer shifts belong to the periodic copies used to construct each triangle and telescope around its boundary. Every accepted packing is independently checked over all periodic pairs using rational coordinates.

## Allowed assumptions and success

The unit square flat torus, equal circles/point separation, and N≥6 are the published conjecture setting. For N points, a strict counterexample has squared minimum separation

`d² > 2/(sqrt(3) N) - 8/(25 N²)`.

The verifier tests this algebraically by writing `t=d²+8/(25N²)` and checking `3N²t²>4`, with positive t. The campaign covers N14–21. The known Gaussian N15 value `17/225` is an exact reproduced comparison. Baselines for other N are cyclic subgroups followed by numerical relaxation; they are **search baselines**, not current published records. A gain over them is not a discovery claim.

Primary source: Robert Connelly, Matthew Funkhouser, Vivian Zieve Kuperberg and Evan Solomonides, *Packings of equal disks in a square torus*, Discrete & Computational Geometry 58 (2017), 614–642, [author PDF](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf), [arXiv1512.08762](https://arxiv.org/abs/1512.08762). Authorship was checked against fresh primary metadata on 2026-10-04. Its N15 figure already contains the high-Markov Gaussian construction; its conflicting numerical table does not establish a weaker incumbent. Current openness remains subject to literature audit.

## Prospectively logged adaptation and stopping

Seeds4000–4999 are reserved. One compute worker and a 240-second wall cap apply. First120 jobs rotate N14–21, cavity sizes5–7 and beam width2. Later jobs concentrate on the three largest baseline/threshold ratios, use seven-point cavities and beam width4. A stage-2 streak of80 nonimproving jobs after job180 stops this representation. Exact candidates and all failures remain registered. Substantial changes in representation require a new prospective protocol; an unchanged extension is prohibited.

The implemented stop branch records a stop and performs no further pivot. The executed register governs interpretation. An initial pre-search implementation failure (NumPy batched-solve RHS shape) is recorded; the repair does not change the hypothesis or parameters.
