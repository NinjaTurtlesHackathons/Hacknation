# Adversarial novelty and selection review

Reviewed2026-10-04. Scope: primary-source packing comparisons, purported conjecture status and one mathematically grounded escalation. This review is independent of the standalone geometry checker's certification audit. Verdict: **NO geometric discovery green-light from the audited campaigns.** Exact existing constructions and explicit local search pruning are useful deliverables; neither meets the requested exceptional novelty criterion.

## Material attacks and dispositions

|Attack|Evidence and disposition|
|---|---|
|Torus N15 improved printed Markov constant4.668 to6.24009|**Rejected comparison.** Primary [Connelly et al.2017 PDF](https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf), p24, explicitly explains its numerical4.668 is inaccurate and the exact value6.24 is already shown in Fig4. Our exact17/225 configuration reproduces that known lattice. No new record.|
|Current unresolved status of M<=6.25 established by searches|**Not established.** Original conjecture is verified in the2017 primary source. [Author publication index](https://connellytensegrity.com/publications.html), retrieved2026-10-04, includes newer rigidity work through2025 but no listed resolution of this density conjecture. Search failure is not a mathematical status proof. Keep present openness as an audit gap.|
|Strict endpoint in conjecture interchangeable with nonstrict endpoint|**Rejected at equality.** Primary p27 writes M<=6.25 but then gives strict density-gap inequality. Strict M>25/4 refutes both formulations, so the search criterion is safe; equality would need interpretation.|
|2020 Isostatic theorem resolves equal-circle square-torus density|**Rejected assumption transfer.** [Primary author PDF](https://e.math.cornell.edu/classes/math7610/Isostatic.pdf), theorem8.1, needs generic radius ratios AND torus lattice. Equal radii on a fixed square torus are not those assumptions. Contact-number theorem is not a density bound.|
|2025 flexible-radii rigidity resolves equal-radius packing record|**No supporting evidence.** [Connelly–Zhang2025](https://link.springer.com/article/10.1007/s00454-025-00776-9) concerns rigidity with radius changes; it cannot silently supply fixed equal-radius extremal comparison or current M-conjecture status.|
|Contact-graph surprise alone is new geometry|**Rejected.** [2024 toroidal penny-graph primary survey](https://arxiv.org/html/2410.10673) already gives K5 andK3,3 constructions, plus known six-circle octahedral geometry. A known graph embedding or newly rendered diagram is insufficient.|
|Right-triangle N23 radius from square/cube PBTS benchmark|**Rejected attribution.** The original source is [Specht crt table](https://packomania.com/crt/crt.html), reference[6], programcrt2009–2010. Raw crt22/23/24 coordinates use legs1 and containmentx+y<=1. Our candidate provenance correctly identifies this source.|
|HAMSP2025 overwrites N22–24 right-triangle baseline|**Not supported by that paper.** [Primary HAMSP PDF](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2025.pdf), section4.2, explicitly evaluates triangle counts151..200. This rules out that specific freshness concern at22–24, while not proving no other newer source exists.|
|Rounded source-centre baselines are existence proofs at printed r|**Rejected without checking.** Our exact rational witnesses shrink source radius by1e-27 and standalone verifier checks every pair and every boundary. Published decimals are evidence, not global upper bounds.|
|60 failed local searches prove global optimality|**Rejected.** They only record failure of finite methods and starts. The analytic exclusion below is local and cannot exclude disconnected better contact geometries.|

The few-distance and area summaries were also read. Their results are below updated published lower bounds and carry explicit negative/retrospective-preregistration limitations. Nothing there warrants calling an infrastructure certificate a new extremal result. This review does not replace those teams' specialist literature audits.

## One decisive pruning escalation: explicit local exclusion at known N15

Instead of another optimizer batch, use the two-cycle contact structure to rule out **every sufficiently small nonlattice deformation**, with an explicit rational neighborhood. This is a search-selection result based on known rigidity mechanisms, **not asserted a novel geometrical theorem**.

Baseline points are p_k=(k/15,4k/15) modZ², k=0,...,14. Contact lifts for step1 have vectorv=(1,4)/15; contact lifts for step4 have vectorw=(4,1)/15. Both steps generate cycles through all15 vertices, and both vector lengths squared are17/225. Let a candidate have compatible real lifts p_k+u_k, after translation u_0=0. Define epsilon=max_k||u_k||_infinity.

**Local exclusion claim.** If epsilon<1/3920 and the candidate's periodic squared separation is at least17/225, then allu_k=0. Thus this explicit neighborhood contains no distinct equal-or-better packing. Labels/lifts are part of the neighborhood condition; the claim says nothing about distant or differently matched configurations.

**Derivation.** For each oriented contact edgei→j with constant baseline lift vectorz=v orw, feasibility implies

`2 z·(u_j-u_i)+||u_j-u_i||² >=0`.

Since each coordinate difference has absolute value<=2epsilon, its squared norm is<=8epsilon². Therefore each a_i=z·(u_j-u_i)>=-4epsilon². Sum a_i around its15-cycle is exactly0. Consequently every a_i<=14*4epsilon²=56epsilon², and |a_i|<=56epsilon². Any vertex is reached from0 in at most14 edges of either cycle, so

`|v·u_k|<=784epsilon²` and `|w·u_k|<=784epsilon²`.

The matrix with rowsv,w is `(1/15)[[1,4],[4,1]]`; its inverse is `[[-1,4],[4,-1]]`, whose absolute row sums equal5. Hence ||u_k||_infinity<=3920epsilon² for everyk. Taking maxima gives epsilon<=3920epsilon². Either epsilon=0 or epsilon>=1/3920, proving the stated strict-neighborhood exclusion.

This argument uses all-periodic-copy feasibility, so even if a different lift were nearest, the selected contact lift must still meet the distance bound. No smoothness, assumed retained contacts, numerical rank or global optimality is used in the derivation.

**Executable structural support.** `search/contact_graph/n15_exclusion.py` independently constructs the30 contact lifts, checks integer wrap offsets, verifies both15-cycles, computes exact rational rigidity-matrix rank28 and checks uniform equilibrium stress exactly. Its prospective analytic question and measured execution are logged in `search/contact_graph/experiments.jsonl`; certificate is `candidates/contact_graph/n15_local_exclusion.json`. The graph arithmetic passes; the displayed analytic proof still requires independent reviewer approval before a lab claim enters the paper. It is not a globally optimality certificate.

**Decision.** No compute should be allocated to tiny modulation or symmetry jitter inside this neighborhood. A serious next torus attempt must cross a contact-graph barrier: construct a different periodic triangulation/defect arrangement or expand to a differentN. The prior remove3/reinsert reconstruction batch already crossed large barriers without improvement, so do not repeat it unchanged. A novel broad theorem or record would require more than this known local mechanism.

## Presentation gate

### Generalized pruning follow-up

`search/contact_graph/general_cycle_lemma.md` generalizes the15-point argument to any n-point fixed-torus packing with two independent constant contact-lift vectors along two Hamiltonian cycles. The explicit neighborhood is epsilon<1/[4(n-1)²||Z^{-1}||_infinity], with translation fixed and compatible labelled lifts. Cycle sums plus the elementary quadratic bound prove the exclusion; this is conditional local geometry, not global density.

`gaussian_family_certificate.py` certifies hypotheses exactly for known N15,209,2911 members. Their neighborhood radii are1/3920,1/3288064,1/2404940400. Every nonzero modular difference is tested; translational invariance proves these imply all pair checks. Critical second-cycle steps are4,56,780. No large approximate rank matrix or float geometry is used. General first-order rank follows2n-2 from the two spanning cycles. Conditional proof review remains pending, and novelty remains unverified. No broader family assumption is inferred from the three checked shortest-vector cases.

- Allowed: independently certified reproduction; negative research campaign; exact graph/rank audit; reviewed local exclusion as a pruning lemma with no novelty claim.
- Not allowed: new packing record, solved conjecture, global optimum, latest worldwide incumbent guaranteed by an old table, discovery of Gaussian continued-fraction family, or exceptional-result completion.
- Before any future record claim: freeze fresh primary comparator and coordinate witness, certify strict improvement, rerun citation-forward novelty search, and obtain independent geometry/proof review.
