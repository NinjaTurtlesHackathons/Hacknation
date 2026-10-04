# Research chronicle: certificate-first geometric search

Checkpoint: 4 October 2026. This is an ordered research narrative, not a timing benchmark. Accepted outcome statements below refer to the canonical claim registry. No new geometric discovery is established. [GE-STATUS]

## Direction and ownership

The human provided the repository, a broad geometric-extremal direction, the ambition for an exceptional result and authorization for autonomous research. The director selected targets, allocated three concurrent agent slots, integrated role-specific files and maintained acceptance separately from discovery. Literature, discovery, certification and adversarial-review roles were used in successive waves. Public constructions were inherited openly; no external scientist was contacted or endorsed this work. [GE-METHOD]

## Turning point 1: current primary data changed the target choices

Scouts moved from familiar problem names to concrete finite instances and checked current author tables, papers and repositories. The selected area targets were a fixed triangular container and a freely varying convex hull; public coordinate literals could be frozen and independently checked. Historical tables alone were inadequate: current-coordinate provenance and comparison normalization mattered. Few-distance comparison research had to combine newer work with older bounds rather than treat the newest table as exhaustive. [GE-PROVENANCE]

Artifacts: `literature/area_portfolio.md`, other literature scouts' portfolio files, frozen source JSON, URL/SHA256/UTC provenance metadata. Those scouts' selection judgments remain hypotheses; baseline acceptance is supported by certificates.

## Turning point 2: baseline reproduction established the exact object being searched

The inherited triangle-fourteen and free-convex-fifteen witnesses were independently recomputed in rational arithmetic. The triangle's objective is normalized area, equal to the minimum absolute determinant in the reference right triangle. The free-convex denominator is exact hull area. The baseline coordinates each have only one exactly minimizing triple: larger source active-set counts are approximate clusters. Treating a near-tie as an exact equality would silently alter the research question. [GE-BASE-TRIANGLE14; GE-BASE-CONVEX15; GE-EXACT-TIES]

Artifacts: `certification/verify.py`, `tables/claims.json`, baseline source snapshots and selected witness certificates.

## Turning point 3: local rediscovery led to changes of search representation

The area team began with analytic oriented-determinant epigraph optimization. When small perturbations returned to incumbents and other perturbations found weaker configurations, it switched to deletion/insertion through neighboring point counts, discrete orientation-wall crossings, a native reheated annealer, disk-to-free-hull transfer and neighboring-case sweeps. Every output, seed, method, measured candidate duration and rejection was retained. The combined area register contains 1,840 trials and no certified improvement of at least 0.05% against the frozen comparison witnesses. [GE-METHOD; GE-AREA-NEGATIVE]

The recorded area candidate wall durations sum to 161.581625 seconds; that excludes source retrieval, compilation, reporting and director/team work. It is not CPU time, total-session time or evidence of a research speedup. [GE-AREA-RUNTIME]

Artifacts: `search/area/discover.py`, `search/area/triangle_anneal.c`, preregistration JSON, stdout logs, experiment JSONL, rational candidate files and `analysis/area_search.md`.

## Turning point 4: adversarial checks invalidated acceptance paths

An adversarial agent found a malformed-problem crash and a false Markov-conjecture counterexample classification outside the conjecture's published applicability range. The counterexample predicate was corrected to honor the range; the known two-point packing no longer passes as a counterexample. A packing-source attribution was also corrected from circle-in-circle data to the right-triangle CRT coordinates. These were material defects and corrections, not cosmetic changes. [GE-AUDIT-SCOPE]

The reviewed standalone verifier passes the controls recorded in GE-SELFTEST. Testing is finite and is not a formal guarantee that every implementation defect has been eliminated. [GE-SELFTEST]

Artifacts: `analysis/adversarial_review.md`, reviewed self-test table and independent checker results.

## Turning point 5: explain a failed local attack mathematically

The torus construction team derived a cycle-sum local-exclusion argument for the known fifteen-point packing. Its two spanning contact cycles have constant lifted vectors. Equal-or-better periodic separation forces each displacement to obey a quadratic bound. After fixing translation, strict maximum-coordinate displacement below 1/3920 implies every displacement is zero. The exact dependency checker verifies the construction, lifts and constant; independent agents reviewed the elementary proof. The mechanism is known, and novelty remains unestablished. The lemma excludes a neighborhood; it is not a global optimality result or a new packing record. [GE-LOCAL-CYCLE; GE-BASE-TORUS15]

Artifacts: `certification/local_cycle.py`, the construction team's cycle-lemma proof, `analysis/novelty_review.md`, and the complete proof in `paper/manuscript.md`.

## Reviewable presentation and next research wave

The paper begins with the strongest confirmed derived statement and states its limits. The portable demo reads only the reviewed demo table, credits public constructions, distinguishes illustrative floating-point diagrams from exact certificates, and allows readers to attack proposed witness bounds. The accepted result state, claim registry and archived sources provide a continuation boundary. [GE-METHOD; GE-STATUS]

The next wave should attack a genuinely different contact or order structure, use certified combinatorial relaxations, or revise the portfolio toward moving frontiers. Repeating the same unsuccessful annealing schedule or calling inherited witnesses discoveries would not improve the evidence. The exceptional-discovery objective remains unmet. [GE-AREA-NEGATIVE; GE-STATUS]
