# Second representation: mixed closed-geodesic rows

For a primitive integer direction `(h,k)`, set `S=h²+k²`. A row with m equally spaced points has coordinates

`p_l = (h,k)(phase + l/m) + (-k,h) normal/S mod Z²`, `l=0,...,m-1`.

The row closes by the **exact integer winding `(h,k)`**. Normal coordinates have period1 with a compatible tangential phase twist induced by the square lattice. No closure equation is silently discarded: the explicit points are evaluated modulo both unit square periods. Multiple rows may carry different counts m, phases and normal positions. Their common winding direction is fixed per discrete program; phases/positions are continuous variables. This is a distinct low-dimensional representation of mixed-scale configurations, not an extension of the cavity seeds.

The campaign enumerates row-count words of length3–6 with individual counts2–7 and total N14–21, identifying cyclic rotations and word reversal. Six primitive directions `(1,1),(2,1),(3,1),(3,2),(4,1),(4,3)` are searched. Two deterministic winding-compatible phase programs supply starts. All actual periodic pair constraints remain in the optimizer; neither adjacent-row constraints nor a Delaunay graph substitutes for them. Rational snapping may destroy exact uniform row spacing, so the saved witness certifies whole-packing feasibility, not membership in the exact row subclass.

## A structural obstruction explaining the strongest reproduced case

If R rows each contain m uniformly spaced points, their geodesic circumference is `sqrt(S)` and the transversal period is `1/sqrt(S)`. Some neighboring normal gap is at most `1/(R sqrt(S))`. Along those two uniform rows, some pair has tangential difference at most `sqrt(S)/(2m)`, after an integer row translation. That selected periodic copy supplies the upper bound

`d² <= 1/(S R²) + S/(4m²)`.

Additionally, copies of consecutive points on a row supply `d² <= S/m²`. These are upper bounds on the whole-packing separation, even when a different periodic copy is shorter. They do not certify attainment, a mixed-row class, or all configurations.

For the diagonal direction `(1,1)`, R=3, m=5, the first bound is exactly

`1/18 + 1/50 = 17/225`.

Thus this class cannot improve the known Gaussian N15 construction. The optimizer reproduces that value, but a local optimum elsewhere in the row enumeration has no global interpretation. Mixed row counts were included specifically to evade the equal-row restriction; allowing each row one point would make the class nearly unconstrained, so those degenerate row programs were deliberately outside this bounded campaign.

For unequal neighboring row counts m and l, their tangential differences form a grid of spacing `sqrt(S)/lcm(m,l)`, giving an adjacent-pair upper estimate with tangential component at most `sqrt(S)/(2 lcm(m,l))`. This explains why mixing coprime counts can create very short cross-row gaps rather than improving density. No completeness claim is made from this heuristic selection observation.

Baseline/conjecture source is the primary 2017 square-torus paper linked in HYPOTHESES.md. The exact generic verifier certifies candidates independently of the row derivation. The construction formulas and bound are used as a search/pruning mechanism; novelty of either is unverified.
