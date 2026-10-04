# Wave 2: geometry programs and adjacent order cells

Status: candidate-generating numerical algorithms, not a global optimality proof.

Frozen author sources use `https://math.tejstead.com/heilbronn/{domain}/{n}/points.json`, with URL, UTC retrieval time, and SHA256 sidecars. Comparator values are recalculated from literal rational coordinates by `certification/verify.py`; cached HTML, rounded public table values, and polynomial values describing a previous configuration are not substituted. Attribution belongs to the source constructors, not to this search.

## Four adaptive changes

1. Full critical-line reflections and larger overshoots, then coupled sequential linear programming with active-triple constraint generation and true-score trust-region backtracking.
2. Contact-connected block reflections, changed to exact coordinate-axis linear programs. Stopped after persistent cross-block triple destruction.
3. Coordinate permutations on critical-triple-linked label sets. Stopped after repeated recovery of source values or poor cells.
4. Active-facet relaxation, then explicit single-sign inversion. Dropping constraints alone did not escape the order cell: remaining triple constraints indirectly preserve the signs. The forced version flips the sign of one triple constraint and retains all other orientation constraints in one coordinate LP. Negative coordinate-slice feasibility is not a proof of impossibility in the full geometric problem.

The final recovery stage ranks distinct successful adjacent cells and allows coupled changes of both coordinates before exact-axis refinement. This is deliberate adaptation of the search representation, not repeated SLSQP polishing of the same initial witness.

## Why the axis subproblem is linear

For a triangle `(i,j,k)`, its signed doubled area is
`D=(x_j-x_i)(y_k-y_i)-(y_j-y_i)(x_k-x_i)`.
Holding all y coordinates fixed makes every D linear in all x coordinates simultaneously. Holding x fixed gives the analogous property for y. For square witnesses the area objective is `|D|/2`; for the reference triangle with vertices (0,0),(1,0),(0,1), normalized area is `|D|`.

For free convex witnesses, the objective is `min|D|/S`, where S is the positive doubled area of the convex hull. On a fixed hull order, S is also linear in the moving coordinate axis. Fixing S=1 gives the linear-fractional (Charnes–Cooper) normalization. Translation and shear gauges fix two coordinates to zero. A numerical chart bound of [-30,30] limits this search subproblem; it is not a restriction asserted in the theorem statement for the original problem. Every output's actual hull is recomputed; the rational verifier uses the actual hull, never the optimizer's presumed one.

## Acceptance and limitations

All trial coordinates are converted to decimal rational strings. Fixed-container candidates are nudged inward before conversion. The independent stdlib verifier recomputes every determinant and hull; no solver success flag or tolerance establishes feasibility. Existing source configurations may recover within floating precision while lying strictly below the exact rational comparator. These are negative jobs, not equalities or records.

Each completed job has its seed, normalization, source exact value, method, runtime, candidate, verifier output and objective history in JSONL, with an individual candidate JSON. Interrupted jobs are not counted. Preregistered but unexecuted seeds are not counted. Search times are sums of measured job durations, excluding setup, downloads, report generation and other agents. Axis objectives are conditional optima only; local stagnation gives no global bound. The final main verifier remains external to candidate generation; root independently checks any potentially improving witness.
