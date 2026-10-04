# An exact parameterized construction underlying the 111/41 candidate

This is a geometric derivation of the generated witness. Its novelty relative to the literature remains an independent audit question.

For integers s≥1 and t≥0, start at (0,0) in triangular-lattice coordinates and follow these nine edge vectors:

```
(s,-2s), (2s,-s), (t,0), (s,s), (-s,2s),
(-t,t), (-2s,s), (-s,-s), (0,-t).
```

Their sum is zero. For t>0 the directions turn successively by 60°,30°,30°, repeated three times in the Euclidean embedding `(a,b) -> (a+b/2, sqrt(3)b/2)`. Thus they form a strictly convex nine-gon. For t=0, zero-length edges collapse and leave a regular hexagon. Take **every integer lattice point in the closed polygon**; no boundary subset selection or numerical tolerance enters this definition.

The vertices, before returning to the origin, are:

```
(0,0), (s,-2s), (3s,-3s), (3s+t,-3s),
(4s+t,-2s), (3s+t,0), (3s,t), (s,s+t), (0,t).
```

Expansion of the shoelace sum gives doubled coordinate area
`A2 = 18s² + 12st + t²`.
The number B of integer boundary intervals is the sum of the coordinate gcds of the edge vectors:
`B = 6s + 3t`.
Pick's formula `N=A+B/2+1` therefore gives the exact number of included lattice points:

```
N(s,t) = 9s² + 6st + t(t+3)/2 + 3s + 1.
```

Coordinate area is used only to count lattice sites: it need not equal Euclidean area in this nonorthogonal embedding.

The construction has a threefold symmetry about
`c=(2s+t/3, -s+t/3)`.
Rotation by 120° in triangular coordinates is `R(a,b)=(-a-b,a)`. The centered action on the lattice has translation `c-Rc=(3s+t,-3s)`, which is integral. It sends vertices 0→3→6→0. The centered reflection `(a,b)->(b,a)` has integral translation `(3s,-3s)` and also preserves the vertex set. Both transformations preserve the polygon and the triangular lattice, so they preserve the filled construction. For s,t>0 its symmetry group is D3: the three distinguished t-edges have length t, the six others length s√3; these lengths are unequal for positive integers, so every symmetry must preserve the triangle determined by the t-edges.

At `(s,t)=(3,1)`, the construction has **111 lattice points**. It equals `support_k41_n111_code7324998.json` after translating that witness by `(6,-2)`. Exact enumeration of all 6,105 unordered pairs gives these **41 positive squared distances**:

```
1,3,4,7,9,12,13,16,19,21,25,27,28,31,36,37,39,43,
48,49,52,57,61,63,64,67,73,75,76,79,81,84,91,93,97,
100,103,108,109,112,127.
```

Each is `Δa²+ΔaΔb+Δb²`. Exact multiplicities summing to 6,105 are in `k41_n111_independent.json`. The root verifier and a separate integer-counter implementation agree; the root agent also recalculated this candidate using its independently written checker. This proves existence of a planar set with 111 points and exactly 41 distances. It exceeds the audited historical construction bound of 109, **conditional on the ongoing current-literature novelty audit**. It is not a global optimum or a Bao–Yu Conjecture 3 counterexample.

The executed parameter batch contains all 72 cases s∈{1,…,8},t∈{0,…,8}; point counts and doubled areas agree with the formulas in every case. The formulas have the algebraic derivation above, rather than being inferred from this finite test. General closed formulas for the number of distinct distances are **not claimed**. For k>50 the available comparison table has a source-coverage gap: those generated witnesses are explicit lower bounds, not established records.

Reproduce with:

```sh
.venv/bin/python research/geometric-extremal/wave2/construction_family/ninegon_family.py
```
