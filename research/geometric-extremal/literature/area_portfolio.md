# Area-extremal scout portfolio

Audit date: 2026-10-04, Europe/Zurich. Role: independent literature scout / selection critic. These are research targets, not novelty claims. Repository `CLAUDE.md`, `rigorous-innovation/SKILL.md`, and the verifier-gated-lab workflow were consulted. No contact with authors was made. Source frontiers below were observed with browser tools; exact witnesses must still be recomputed by our independent verifier.

## Common definitions and gates

For planar points P=(p1,...,pn), let m(P)=min_{i<j<k}|det(pj-pi,pk-pi)|/2. Square objective is m(P) with all points in [0,1]^2. Triangle objective is m(P)/area(T). Use the rational right triangle T={(x,y): x,y>=0, x+y<=1}, so its objective is min |det|, NOT min |det|/2. Any invertible affine map transports a triangular container and multiplies every area by the same determinant: normalized triangle results are shape independent. Disk radius-one objective is m(P), whereas unit-area disk values equal m(P)/pi. Free-convex objective is m(P)/area(conv P), with nonzero hull area. Do not impose that every point is a hull vertex.

Each Heilbronn score needs C(n,3) determinants; changing one point needs only C(n-1,2). Exact rational containment, distinctness, all determinants, and an exact monotone-chain hull plus shoelace suffice for witness certification. Search costs below are operation counts, not measured timings. The min objective is nonsmooth; active-triangle epigraph SQP / sequential LP, annealing, discrete changes of order type, and boundary-count continuation are distinct avenues. A stationary residual never proves existence or global optimality. Novelty requires a strict margin over authoritative incumbent coordinates, not merely a truncated table row.

## Six concrete questions

### A1. Can twelve points in the square beat the Comellas–Yebra configuration?

**Definition:** maximize square m(P), n=12, no symmetry restrictions. **Audited baseline:** 0.0325988586918196982187640066235..., unique real root of 64A^3+80A^2+28A−1. The construction was found December 2001 and published [Comellas–Yebra, 2002, doi:10.37236/1623](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v9i1r6); exact seed and area are available in [current configuration page](https://math.tejstead.com/heilbronn/square/12/) and [Sudermann-Merx, March 2026](https://arxiv.org/abs/2603.11107). Proven optimality currently extends through n=9, not n=12.

**Significance / prospects:** a certified improvement of a 24-year incumbent would be highly recognizable. Cost 220 triangles; rational witness is trivial to check. Incumbent D4 symmetry, two orbits 8+4, and 20 active triangles suggest orbit perturbation or order-type jumps. But [Yang's 2026 square audit](https://github.com/SeverinVisionary/heilbronn-records) already proves local rigidity and classifies minimal rigid cores; rediscovering those is not new. Do not spend a search wave solely infinitesimally perturbing it. Visualization excellent; family potential plausible but currently unproved.

**Priority:** ambitious reserve. **Success:** rational m(P) strictly above a rigorously isolated incumbent root, preferably >=0.1% margin. **Abort/escalate:** no new contact/order structure after diversified attempts; local-only perturbations cannot disprove local rigidity. **Artifact:** exact coordinates, triangle census, certified incumbent root interval.

### A2. Can twenty-three square points improve the current asynchronous frontier?

**Definition:** square m(P), n=23. **Audited latest coordinate baseline:** 0.00975728971331477225716070200657, [Rob Gardiner configuration and provenance](https://math.tejstead.com/heilbronn/square/23/), [full JSON seed](https://math.tejstead.com/heilbronn/square/23/points.json). The site's latest change is 2026-10-01; detailed provenance says September 2026. Earlier September values are superseded. This is author-contributed computational evidence, not a peer-reviewed optimality theorem.

**Significance / prospects:** actively moving frontier with less-polished medium-n basins; evidence of recent percent-scale gains. Score 1771 triangles. Incumbent is already asymmetric, so “symmetry broken” is not novelty here. Try deletion/insertion from n=22,24,25, discrete oriented-triple constraints, continuation from rectangle aspect ratio then return to square. Certification easy. Visual clarity lower than small n; family improvement across adjacent n would strengthen story.

**Priority:** balanced high-n lane. **Success:** exact improvement >=0.5% and live-table refresh immediately before public claim. **Abort/escalate:** a tiny rounding improvement or newly posted stronger external witness. **Artifact:** witness and adjacent-n experiment registry. No global-optimality claim.

### A3. Can fourteen points in a triangle beat Cantrell's 2007 configuration?

**Definition:** normalized triangle objective, n=14. **Baseline:** 0.023775773107572772515833024334, [current page](https://math.tejstead.com/heilbronn/triangle/14/) and [rational coordinates in the right frame](https://math.tejstead.com/heilbronn/triangle/14/points.json). Cantrell's original Mathematica coordinates were received September 2026 and locally polished; prior graphical reconstructions are obsolete. 23 active triangles; incumbent is already asymmetric. [Sudermann-Merx, July 2026](https://arxiv.org/abs/2607.15021) treats certified small-n triangle optimality, not this case.

**Significance / prospects:** long-lived but accessible 364-triangle incumbent. Explicit rational seed removes a major baseline gap. Remove/insert from neighboring n, vary how many points lie on each side, then topology-changing perturbations; solve oriented determinant constraints as an epigraph. Visualization excellent, with narrow triangles showing bottlenecks. A triangle family spanning n=13..16 has meaningful potential.

**Priority:** top recommendation 2. **Success:** rational normalized value beyond incumbent with >=0.1% gain, neighboring-case sweep. **Abort/escalate:** plateau at incumbent after varying side counts and order types; avoid numerical improvements below certifiable margin. **Artifact:** right-frame rational witness, determinant enumeration, source snapshot hash.

### A4. Can fifteen points improve the free-convex Heilbronn ratio?

**Definition:** maximize m(P)/area(conv P), n=15; arbitrary planar distinct points, positive hull area. Scale, translation, rotation, and affine maps leave the ratio invariant. **Baseline:** 49128111226460317685888607941 / 1999999999999999257563094398721 = 0.0245640556132301679615750232227. [Tej Stead, July 2026](https://math.tejstead.com/heilbronn/convex/15/) supplies [exact coordinate literals](https://math.tejstead.com/heilbronn/convex/15/points.json), 11 hull vertices, 25 near-active triangles, no symmetry.

**Significance / prospects:** freeing the container permits new geometry instead of perturbing a prescribed frame; fixed hull combinatorics is smooth and admits exact objective evaluation. 455 triangles plus O(n log n) hull. Search hull vertex count 8..15, exchange hull/interior roles, use convex-hull-aware SQP, and continuation from disk/triangle seeds. Normalize affine gauge by three noncollinear points, not by forcing hull area numerically to one. An unexpected hull topology could give a general mechanism. [AlphaEvolve's primary paper](https://arxiv.org/html/2511.02864v3) already improved free-convex n=13,14, so those older baselines must not be reused.

**Priority:** top recommendation 1. **Success:** exact ratio improves by >=0.5%, then adjacent n=14,16 hull-topology sweep. **Abort/escalate:** degenerating hull or a candidate only improving unnormalized triangle area. **Artifact:** integer/rational coordinates, exact hull indices and area, min-triangle numerator, proof of strict ratio comparison by integer cross multiplication.

### A5. Can fifteen disk points beat Cantrell's historical bracket rather than merely rediscover his configuration?

**Definition:** maximize m(P), n=15, x_i^2+y_i^2<=1. **Strongest accessible exact witness:** 35019761063801201909013 / 500000000000000000000000 = 0.07003952212760241. [Yang's rational census seed](https://raw.githubusercontent.com/SeverinVisionary/heilbronn-records/main/disk/configs/circle_n15.json) explicitly says REDISCOVERY; Cantrell's primary historical printed entry is “0.0700+”. The authoritative precision is incomplete: conservatively a claimable improvement must exceed 0.0701, not just Yang's snapped witness. Original Cantrell n=15 coordinates remain a source gap. [Yang's note and audit limits](https://raw.githubusercontent.com/SeverinVisionary/heilbronn-records/main/disk/NOTE.md) must be retained in provenance.

**Significance / prospects:** disk curvature permits mixed scales and boundary/interior transitions; n=14 already has a newly known asymmetric improvement, so copying its shape or its symmetry break is not new. 455 triangle checks, quadratic rational containment. Different boundary counts and n14 insertion are concrete attacks; angle-radius parameterization and discrete interior exchange diversify search. Exact certification is simple after inward rational snapping. Neighboring n=14..17 would form a meaningful family.

**Priority:** viable alternative if free-hull plateau. **Success:** exact m(P)>0.0701 with comfortable margin and continued historical audit. **Abort/escalate:** value <=0.0701 or dependence on float containment. **Artifact:** common-scale integer coordinates and historical bracket metadata; phrase outcome “improved documented lower bound” until source gaps close.

### A6. Can a diameter-one 14-gon exceed the published maximum-area construction?

**Definition:** maximize area of a convex 14-gon, every pairwise squared distance <=1; allow no self-intersection and require 14 actual vertices. **Recent decisive source:** [Trela, arXiv:2608.15666v2, revised 2026-08-19](https://arxiv.org/abs/2608.15666), now titled *Maximum-Area Small Polygons of Even Order*, claims analytic determination for every even order, with unique optimizer and strict-concavity argument. Thus [Bingane–Mossinghoff's 2022 statement of an open n>=14 problem](https://arxiv.org/abs/2204.04547) is stale. Exact 14-gon value has not been reconstructed in this scout pass; do not quote an old numerical row as the live frontier.

**Disposition:** reject as normal discovery lane. Could independently audit Trela or search a counterexample to his claimed theorem, but that demands full paper scrutiny first. Polygon area O(n), diameter O(n^2), exact rational verification easy; theorem auditing difficult. A plotted nonregular polygon is a known phenomenon. **Success if reopened:** certified witness strictly exceeding rigorously reproduced Trela optimum, followed by detailed identification of proof flaw. **Abort:** no such concrete issue; avoid relabeling reproduction as discovery.

## Selection and novelty safeguards

Launch A4 and A3 first: different search geometries, current downloadable rational seeds, low-dimensional witnesses, and scope for adjacent-n mechanisms. Keep A2 as a medium-n escape lane and A5 as curvature lane. A1 has exceptional upside but a mature locally rigid incumbent; A6 is rejected by fresh primary-source claims.

Historical-table equality is not a record. Published decimal coordinate literals can be certified exactly without making their numerical near-ties exact. The set of all active triangles, hull graph, and boundary count should be treated as hypotheses rather than side conditions of the unrestricted problem. Current site includes October 1 and September 28 improvements: an August-only snapshot is insufficient. No global optimality or novelty has been established in this scout artifact.

## Reproducible source handoff

Seed endpoints: `https://math.tejstead.com/heilbronn/{triangle/14,convex/15,square/23}/points.json` (expand the braces) and the disk n15 raw GitHub URL above. Fetch original bytes, hash SHA256, and archive allowed data with attribution. Author repositories: [spiralulam/heilbronn](https://github.com/spiralulam/heilbronn), [TejSteadQC/heilbronn-configurations](https://github.com/TejSteadQC/heilbronn-configurations), [SeverinVisionary/heilbronn-records](https://github.com/SeverinVisionary/heilbronn-records). Third-party author claims and their verifiers are baseline evidence; our certification must compute independently from points and the definitions above.
