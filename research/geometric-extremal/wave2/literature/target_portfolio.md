# Wave2: independently selected geometric targets

Retrieved2026-10-04. Six concrete directions below have downloadable witnesses and established problem definitions. Numerical comparator values are construction bounds, not global optima. Ranking is based on certification and structural search opportunities, not a promise of improvement. **None is certified newly discovered.** Primary source bytes/hashes are in `sources.json`; Kamp API tree and commit snapshot are separate. No discovery code was copied. External code/data licenses must be checked before redistributing; the downloaded sources here retain origin and attribution.

## 1. Variable-radius circle packing, unit square N32 (priorityA)

Maximize S=sum_i r_i subject to r_i>=0, r_i<=x_i,y_i<=1-r_i and squared pair distance >=(r_i+r_j)^2. No equal-radius constraint. [Specht current table](https://packomania.com/csqv/csqv.html), updated30Sep2026, gives S32=2.939572771205, S26=2.635983084919, S33=2.987285008592, S34=3.029799271186. Downloaded [N32 coordinates](https://packomania.com/csqv/txt/csqv32.txt), centered frame[-1/2,1/2]^2; add1/2 to each coordinate.

The [May2026 primary paper](https://arxiv.org/html/2605.04850) and [Kamp author supplement](https://github.com/DominikKamp/Packing) have numerical N32=2.939572726664292, which is weaker. Repo commit27f71632d8655ae4b6a049410a401976748b94e3 dated16Apr2026 was the current API head. Current comparator must use stronger Specht precision, not rounded five-decimal results.dat. Independent Fraction checks can certify walls/pairs/S exactly after a conservative rational radius shrink. Search: cavity insertion with radius reallocation, deletion/reinsertion, contact-topology mutation, LP radii for fixed centers followed by joint optimization. Family prospect: neighbor N26..40 topology transfer; every N requires its own certified improvement.

Novelty attack: [Numaro3Jul2026](https://numaro.tech/research/circle-packing-unit-square-2026/) claims N26,33–40 improvements and41–42 extensions. Its visible N33/40 scores agree with current Specht, N36/41/42 are weaker; N26 difference is printed rounding scale. The page exposes no linked raw coordinate download. Do not call that tiny rounding difference a record.

## 2. Twelve unit-circumradius equilateral triangles in a square (priorityA reserve)

Minimize circumradiusR of a regular4-gon containing12 freely translated/rotated regular3-gons of circumradius1 with disjoint interiors. Square orientation can be fixed by rigid rotation; triangle rotations remain unrestricted. Current numerical [Kamp witness](https://raw.githubusercontent.com/DominikKamp/Packing/main/polygon/l4/m3/n12/polygon_n12_m3_l4.txt) has R=3.134022702061933 (May2026 paper; source snapshot saved). This already supersedes older Cantrell comparison, so reproducing it is not discovery.

Search: discrete triangle orientation motifs plus continuous separating-axis constraints; remove a triangle pair, change contact graph, reinsert; compare outside apparent two-orientation clusters. Certificate: encode orientations by rational tangent half-angle, algebraic sqrt3 vertices, exact separating axes and containment. Numerical angles alone require rigorous intervals and enlargedR. Success is an R strictly below independently certified current witness with safe separation margin. Neighbor N11/13 attacks may yield family, but a restricted orientation improvement is not the unrestricted record until it beats this comparator.

## 3. Twenty-nine equal circles in regular octagon (priorityB)

Maximize common r with centers inside the inward-offset regular octagon of circumradius1 and pair distances>=2r. [Primary table](https://packomania.com/coc/coc.html) itself is updated23Sep2026, newer than homepage29Jul2026; N29 r=.154929849312, N32=.147297380425, N39=.134962830726 and N47=.123222835031 are fresh Zorcic2026 entries. [N29 coordinates](https://packomania.com/coc/txt/coc29.txt) downloaded.

Attack octagonal boundary shells versus displaced triangular bulk: free rattlers do not themselves improve r, but identify sites for contact-network surgery. Try neighboringN28..33 using source seeds, plus symmetry-breaking insertion. Certificate: rational centers/r with exact octagon support inequalities over Q(sqrt2), or rigorous intervals for cos(pi/8). Note the table's new entries list boundary0 despite visible boundary points: metadata may be missing, not proof of a special interior configuration. Current fresh search makes naive multistart less promising; stop repeated recovery after a diversified batch. Existing2023 Amore constructions must be cited.

## 4. Twenty-three circles with prescribed radii proportional to sqrt(i) in unit disk (priorityB)

Maximize scale lambda for radii r_i=lambda sqrt(i), i1..23, centers satisfying ||c_i||+r_i<=1 and pair distances>=r_i+r_j. [Specht primary table](https://packomania.com/ccir/ccir.html), updated5Jul2026, N23 lists largest-circle radius .265697255130495150463644942363 and reciprocal first-circle scale18.0499852019821733077302951903. Thus lambda=largest/sqrt23; **largest radius is not lambda**. [Coordinates](https://packomania.com/ccir/txt/ccir23.txt) downloaded, pointindex determinesradius. N24 has seven rattlers; alternative reserve.

Search mixed-scale radial assignment, swap large-circle positions and solve small-circle cavities; discrete permutation search differs from fixed-label local polishing. Certificate algebraic radicals with outward interval bounds, or exact number-field inequalities; for rational center/lambda, conservative upper bounds on sqrt(i) suffice. Must retain prescribed radii ratios; allowing arbitrary radii changes the problem. Better integer-radius versions are easier to certify but separate established family, not equivalent comparator.

## 5. Unrestricted spherical code N100 on S² (priorityC ambitious)

Minimize t=max_i<j p_i·p_j with ||p_i||=1. Current maintained [Cohn table](https://spherical-codes.org/) entry(3,100) is t=.933385128903 and links [coordinates](https://spherical-codes.org/data/3/100), downloaded. Archive to cite: [MIT data set](https://hdl.handle.net/1721.1/153543). The table lacks an optimality marker here, which is evidence of its reported status, not proof no later theorem exists. The witness is old Hardin–Sloane–Smith; current table ingestion and a2023 search paper yielding42 newer records must be crosschecked before a claim.

Search defect moves in spherical Delaunay triangulation, patch replacement and continuationN99/101; preserve independent global starts. Certificate uses rational stereographic coordinates: p=(2u,2v,1-u²-v²)/(1+u²+v²), exact unit norms and rational pair dots. Must improve beyond full source-coordinate objective rather than twelve-digit roundedt. This avoids a numerical sphere-normalization residual. Known strongly optimized lowN15/16 algebraic configurations are less attractive discovery targets. Visual: contact graph on rotatable sphere. Complete evaluator4950pairs is fast, optimization basin difficulty high.

## 6. Heilbronn square N20, September2026 D2 arrangement (priorityA area reserve)

Maximize min absolute triangle determinant/2 among20 points in[0,1]^2. [Current witness](https://math.tejstead.com/heilbronn/square/20/), credited Fable5.1 with ShengtongZhangSeptember2026, has exact coordinate-literal objective .0129381967147270176121146278205. [Full coordinates](https://math.tejstead.com/heilbronn/square/20/points.json) downloaded and independently checked: all1140triples give25876393429454035224229255641/2000000000000000000000000000000. D2 symmetry,42approximately minimaltriangles,6orbits (4+4+4+4+2+2). The currently credited search already used symmetry-reduced basin hopping, ruin/recreate, softminwarmup and trust-regionSLP. Repeating that unchanged is a weak target.

**Cache/source attack resolved:** first webfetch of detailHTML returned stale JulyShanleyC4 reconstruction .01291155568394185…, while refreshed page and actual downloadedJSON both contain SeptemberFableD2 replacement. The changelog still contains the oldJulyalgebraicpolynomial/value, which is not the current witness. The initial recommendation was corrected before discovery; compare exact downloadedgeometry, not cachedcaption or historicalchangelog. Independent verifier agrees with currentJSONclaimedvalue.

Search unrestricted symmetry-breaking of D2, boundary reassignment, critical-triple graph swaps and N19/21continuation; exact rational enumeration is immediate. Preserve externalAI/humancontributor attribution. No claim that the arrangement is globally optimal. Recent2026 squareMINLPpaper handles n<=9 only and does not certify these larger cases.

## Rejected/deferred suggestions

Hemisphere center-separation and spherical caps wholly contained in a hemisphere are different definitions (the latter includes distance-to-equator). Targeted searches found no adequately current primary coordinate benchmark for a concrete instance. Do not fabricate a hemisphere record from unrestricted Tammes data.

Spherical covering N20 has historical1994 radius29.6230959degrees and downloadable cov3-20 in [Cohn's preserved Sloane tables](https://cohn.mit.edu/sloane/), but current-record freshness was not established; two direct page fetches failed. A sphere mesh maximum is not a covering certificate: enumerate spherical Voronoi vertices and degeneracies with interval bounds. Reserve until fresh comparator is audited.

Hexagons-in-hexagonN12..17/23 are already directly attacked by [ImprovEvolve2026](https://arxiv.org/html/2602.10233), and N25..30 extensions are reported. Do not use olderFriedman table to claim those discoveries. Its paper includes evolved code; code license and exact benchmark normalization need audit before reuse.

TorusN14..21 current numerical coordinate source not found in this pass. Markov threshold exceedance would be a conjecture counterexample; merely beating a lab baseline cannot establish a torus record. SmallN optimal-torus papers and nonperiodic square circle tables are not these comparators.

## Escalation and source queue gate

[Packomania pending requests30Sep2026](https://packomania.com/pending-requests.html) contains4666 candidates labelledmany, plus other queues. It explicitly defers Octobercsqv processing untilNovember. Thus a stronger table witness establishes improvement over a dated public construction but cannot justify latest worldwide/first record without pending-source and author-repository review. No messages were sent to external authors. Initial discovery should proceed on A targets; promising witnesses trigger renewed citation-forward search and independent certification before strong public claims.

## Independent sum-of-radii certification supplement

`independent_sum_radii.py` clears all coordinate/radius denominators into integers and checks every wall and every squared pair clearance. It imports neither director checker nor discovery implementation. 18controls pass, including malformed dimensions/types, rational denominator0, overlap, boundary, zero radius, exact equality and sub-floating-resolution improvement thresholds. Witness-supplied comparison metadata is explicitly untrusted; the CLI's optional second argument supplies a separately frozen threshold.

Snapshot `sum_radii_snapshot.json` independently checks678source/search witnesses currently exported by wave2director: zero disagreements with director acceptance/objectives, zero strict improvements against exact sums of the full frozen source radius literals. All witness and source files are SHA256 bound. Director comparison fields round to12decimal places; this supplement uses full literal precision. The finite snapshot does not include future files. A minor input-validation weakness was reported: director n=True compares equal to1; it does not change geometric feasibility, but strict integer typing is preferable.

Reproduce controls: `.venv/bin/python research/geometric-extremal/wave2/literature/independent_sum_radii.py --selftest`. Check one candidate with frozen threshold: append itsJSONpath and a rational threshold as two arguments. Positive feasibility alone does not certify a record.

`few_distance_k24_50.json` consolidates established lower bounds for an exact-discrete fallback. Thresholds at k25/31 include the stronger2013constructions; no claims about k51+freshness are made.
