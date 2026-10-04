# Packing and distance portfolio — independent scout

Retrieved 2026-10-04 (Europe/Zurich). Scope: six concrete targets; source-based baselines, not claims of discovery. Author tables can lag papers. Absence of a newer search hit does not establish that a conjecture remains open. Read `CLAUDE.md`, both repository research skills, and `docs/FRAMEWORK.md`: numerical search proposes; independently checked claims alone enter the paper. Sources containing benchmark answers belong in the lab's research-block list when used for a contamination-sensitive evaluation.

## Decision summary

1. **Square flat torus: nonlattice configurations and the Markov conjecture.** Best mechanism/family prospect. Use small N=10 as a calibration target, then N near continued-fraction families; explicitly challenge the restriction to grid-like packings. A conjecture refutation has a clean witness certificate. The conjecture's current unresolved status still needs a citation-forward check.
2. **23 equal circles in the isosceles right triangle.** Small, understandable and cheaply certifiable; table remains old, so compare independently with the 2025 HAMSP paper before describing a record. Seek contact-graph changes and symmetry breaking, then n=22–26. The existing D1 symmetry is a seed hypothesis, not an imposed constraint.

Tammes N=15 is the high-significance reserve, but a baseline known for decades is unlikely to yield to routine random optimization. Sphere cube N=33 is useful for method transfer, with much stronger recent computational competition than the old table date suggests. Square N=31 should calibrate infrastructure, rather than receive the entire compute budget.

## P1 — 31 equal circles in a unit square

**Question.** Maximize r for exactly 31 centres c_i in [r,1-r]^2, with ||c_i-c_j||² >= 4r². Tangency permitted; all radii equal.

**Published comparison.** [Specht's author table](https://packomania.com/csq/csq.html), updated 10-Sep-2026, gives r=0.089338333351 (rounded 12-place value), corresponding point-separation d=0.217547291619, D1 symmetry and four rattlers. Do not compare d with 2r: the point problem is rescaled to the full unit square, so d=2r/(1-2r). Downloadable coordinates/contact graphs are linked from the table. Latest numerical research to reconcile: [Lai et al., PBTS, 2023](https://pubsonline.informs.org/doi/10.1287/ijoc.2023.1290), with [MIT-licensed author software/data](https://github.com/INFORMSJoC/2022.0004).

**Methods and cost.** Basinhopping, thresholding and local constrained optimization compete here. Evaluation: 465 pairs plus 124 linear boundary inequalities; cheap. Rattlers expose opportunities to restructure the rigid spine, but moving rattlers alone need not improve r.

**Certificate and significance.** Rational centres and rational r allow exact integer inequalities. A decimal table is not a rigorous bound: retrieve its underlying witness, then establish a safe strict margin. A certified improvement is a classical finite packing result; a change of contact mechanism across n=30–35 matters more than a tiny decimal refinement. Visual clarity 5/5; novelty probability low without a new mechanism. Stop after structurally distinct starts stagnate; retain baseline reproduction.

## P2 — 32 equal circles in the unit disk

**Question.** Maximize r with ||c_i|| <= 1-r and pair distance >= 2r, exactly 32 circles, equal radii.

**Comparison.** [Specht table](https://www.packomania.com/cci/cci.html), dated 25-Dec-2024, row N=32: r=0.155533985422770861614341265770; normalized point separation d=0.368360556228273831682910131413. Here d=2r/(1-r). The table gives one rattler and 16 boundary circles. **Freshness warning:** [Lai et al., HAMSP, COR 181 (2025), 107099](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2025.pdf) reports improved circular-container benchmarks; the table timestamp is insufficient evidence of current priority. Its instance table/supplements must be compared before any record claim.

**Plan.** Contact-ring surgery, shell exchange and unrestricted multistart, rather than forcing concentric rings. 496 pair inequalities plus 32 quadratic containment inequalities make evaluation cheap. Certify rational coordinates/r by squared norms; intervals suffice for algebraic reconstructions. Rational coordinates are allowed and a sufficiently shrunken candidate has an exact existence certificate.

**Assessment.** Good visualization, possible ring-family mechanism; moderate significance for one case, higher for multiple cases. Lower priority until fresh baseline reconciliation; abandon a claimed improvement if only the stale 2024 table is beaten.

## P3 — 23 equal circles in an isosceles right triangle

**Question.** Container T={(x,y): x>=0,y>=0,x+y<=1}; legs have length 1. Maximize r subject to x_i>=r,y_i>=r,x_i+y_i<=1-sqrt(2)r and pair distance >=2r.

**Comparison.** [Specht author table](https://packomania.com/crt/crt.html), dated 18-Mar-2011: N=23 radius 0.071581718995599529585444225012, point separation 0.189468690981505999703046686857, D1 symmetry. Conversion is d=2r/[1-(2+sqrt(2))r], rather than a square normalization. The table attributes the row to reference [6]. [HAMSP 2025](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2025.pdf) also studies this container, including larger instances: inspect exact N coverage before accepting table priority.

**Plan/certificate.** Reflect seed, perturb unequal row lengths, split contacts near the hypotenuse, and enumerate candidate contact graphs. 253 pair constraints. Rational x,y,r can certify the irrational boundary exactly: require h=1-x-y>=0 and h²>=2r². Baseline selftests should include overlap, negative coordinate, and a circle barely crossing the hypotenuse.

**Assessment.** Cheap exact witness, excellent visual demonstration and plausible neighboring-family development. A one-case numerical change is insufficient for the ambitious objective unless substantial or revealing. Escalate if n=22–26 show a repeatable new row-defect mechanism. Stop if progress disappears under exact feasibility shrinkage or newer literature already dominates it.

## P4 — 33 equal spheres in a unit cube

**Question.** Maximize r with c_i in [r,1-r]^3 and all pair distances >=2r.

**Comparison.** [Specht table](https://packomania.com/scu/scu.html): r=0.154605431908113458803268257572, d=0.447619754885616000062572316853, ratio 1/r=6.4680780465354498015739562139. Table date is 25-Jun-2013 whereas overview lists 29-Jun-2018: freshness is ambiguous. Independent 2023 author artifact [33_CubeSol.txt](https://raw.githubusercontent.com/INFORMSJoC/2022.0004/main/results/best_solutions/PESC/33_CubeSol.txt) starts `33 6.46807804653548679`, in the radius-one/smallest-cube-side convention; it matches the old radius to numerical rounding, rather than improving this instance. [PBTS 2023](https://pubsonline.informs.org/doi/10.1287/ijoc.2023.1290) improves many other cube instances and supplies executable source.

**Plan/certificate.** Layer exchange, octahedral clusters and asymmetric boundary defects; preserve distinctions between close-packed family seeds and unrestricted search. 528 pairs and 198 boundary constraints. Exact rational certificate identical to P1 in 3D. Viewer needs rotation and transparent boundary for contact clarity.

**Assessment.** A finite improvement is meaningful; a family near close-packed counts is better. [Tatarevic 2015](https://arxiv.org/abs/1503.07933) already proves improvement mechanisms when deleting >=2 spheres from cubic close-packed counts: merely rediscovering deletion-induced relaxation is not novel. Stop repetitive multistart; pivot to contact graph/layer structure.

## P5 — Tammes problem for 15 points on S²

**Question.** For ||x_i||=1, minimize t=max_{i<j} x_i·x_j. Equivalent objective is maximal minimum angle theta=arccos(t), or chord distance sqrt(2-2t).

**Comparison.** [Henry Cohn's author table](https://cohn.mit.edu/spherical-codes/) search-indexed N=15 entry: t=0.59260590292507377809642492233276, minimal polynomial 13t^5-t^4+6t^3+2t²-3t-1. The modern [spherical-code database](https://www.spherical-codes.org/) incorporates 2023, 2024, 2025 and 2026 records for other N; direct opens failed, so the 15-point full coordinate/attribution download remains an access gap. No global optimum claim is made here. [Musin–Tarasov N=14 primary paper](https://arxiv.org/abs/1410.2536) provides contact-graph proof machinery. [IDNS 2023 author PDF](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2022.pdf) is current algorithmic competition.

**Plan/certificate.** Contact-graph enumeration and symmetry-class release; compare distinct numerical optima, not just their objective. 105 pairs, 15 sphere equations. Use rational stereographic coordinates, producing exact rational unit vectors, or algebraic points with isolating intervals. Normalizing rounded Cartesian vectors only approximately is not a sphere existence certificate.

**Assessment.** Very high significance; known incumbent is exceptionally strong. Exact global proof would require exclusions, not local KKT. Low short-run improvement chance, strong flagship reserve if an independently found different contact graph appears. Stop if only incumbent rediscovery occurs; expand to a neighboring N with a fresh downloaded baseline.

## P6 — Square flat torus, N=10 and Markov-bound family

**Question.** On R²/Z² maximize d=min_{i<j,min_{k in Z²}}||x_i-x_j+k||. Radius r=d/2; density delta=N*pi*r². Pair distances use wrapped differences, and periodic copies of the same disk must also not overlap (r<=1/2).

**Comparison.** [Connelly, Funkhouser, Kuperberg, Solomonides, author PDF](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf), published DCG 58 (2017), 614–642, DOI 10.1007/s00454-016-9843-x, table N=10: density .785, radius .158. The rotated square sublattice with generators (3,1),(-1,3), determinant 10, yields exact d=1/sqrt(10), r=1/(2sqrt(10)), delta=pi/4. This is a verified known construction; current globally best status is **unresolved in this scout pass**.

The same paper's Conjecture 2 asserts Markov constant M<=6.25 for N>=6; written gap condition is pi/(2sqrt(3))-delta > pi/(12.5N). Strict/non-strict endpoint wording should be resolved from the definition before formalizing. Its Theorem 2 proves M<6.25 for rigid **grid-like** packings, not arbitrary packings. A candidate above 6.25, rigorously separated, attacks a genuine published conjecture. Search-index queries found no resolution, which is not proof it is open.

**Methods.** Continued fractions and Gaussian-integer lattices provide exact family baselines; nonlattice defects, contact graphs and modular discrete search are independent discovery routes. [Musin–Nikitenko 2012](https://arxiv.org/abs/1212.0649) solves N=6,7,8; [Voloshinov 2018](https://arxiv.org/abs/1809.10525) reports MINLP/ParaSCIP confirmation for N=9 at numerical relative gap 1e-6, not a proof-certificate substitute. [Toroidal penny graphs 2024](https://arxiv.org/abs/2410.10673) links contact topology to geometry.

**Certificate/assessment.** For rational centres, enumerate the nine shifts {-1,0,1}² and check exact squared distances. Certify density/Markov comparison with rational enclosures of pi and sqrt(3). N=10 has 45 pairs; scaling to tens/hundreds remains feasible. Excellent mechanism/family prospects; visualize tiled 3x3 copies to show periodic contacts. Do not claim rediscovered continued-fraction families as lab discoveries. Stop or redesign if all good candidates are merely grid-like packs already covered by the theorem.

## Audit gaps and next actions

### Actionable torus seeds for the next wave

For k=0,...,N-1 use centres `((b*k % N)/N, (a*k % N)/N)` for coprime a,b and N=a²-b². These are known lattice constructions. Independent exact wrapped-distance evaluation is required before relying on the formulas. Useful cases:

| N | a,b | Known seed d² | Density | Markov M, numerical diagnostic |
|---|---|---|---|---|
| 15 | 4,1 | 17/225 | 17*pi/60 | 6.24009237739796 |
| 209 | 15,4 | 241/43681 | 241*pi/836 | 6.01662053041081 |
| 2911 | 56,15 | 3361/8473921 | 3361*pi/11644 | 6.00119024004954 |

The conjecture-violation threshold is **d² > 2/(sqrt(3)*N)-8/(25*N²)**, derived directly from M>25/4. At N=15 the known seed is close to that threshold, so this is the first symmetry-release experiment. N=14 is a useful deletion-plus-relaxation contrast, but its known source-table configuration must also be reproduced. N=209 tests a more nearly triangular periodic arrangement; N=2911 is an analytic-family reserve, not a suitable first dense all-pairs optimizer. For N=10 calibration, centres `(k/10,3*k/10) mod 1` have d²=1/10. No seed or formula in this subsection is claimed novel; diagnostic decimals were calculated locally with Python double precision.

- Obtain current original spherical-code N=15 coordinates; primary direct access failed, search-index evidence succeeded.
- Reconcile HAMSP 2025 exact instance tables against circle-circle and triangle baselines.
- Pin author-repository commit and verify downloaded PBTS coordinates with a lab-owned independent checker before reuse.
- Citation-forward check of the square-torus conjecture is mandatory before the paper calls it currently open.
- Any source decimals remain literature evidence, not certified upper bounds. Improvements need an independently certified feasible lower bound safely exceeding a freshly reproduced comparator.

No new geometric result was found in this literature pass. Recommendations are research judgments, not claims of scientific novelty.
