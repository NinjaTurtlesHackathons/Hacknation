# Independent area-search checkpoint

Status: completed finite adaptive discovery campaign; NO NEW GEOMETRIC RECORD and NO GLOBAL OPTIMALITY CLAIM. Primary source snapshots reproduce current comparison witnesses exactly. All proposed candidates remain at or below the incumbent, using exact rational comparison (not tolerance).

## Methods and measured execution

Single compute worker; OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=1. Source caches frozen with URL, SHA256 and actual fetched UTC time. Prospective batches preregistered before execution. One root-reviewed independent verifier recomputed the selected best witness from each problem case; all six passed. Search-side exact checks are separate from numeric SLSQP scoring. Finite-difference Jacobian checks: triangle max error9.9504e-11, convex8.3194e-11 at step1e-6 (diagnostics, not proof).

| Method | Trials | Sum measured run wall seconds | Rejected by exact checker |
|---|---:|---:|---:|
| anneal-oriented-SLSQP | 100 | 28.545059 | 1 |
| cellflip-oriented-SLSQP | 1000 | 61.960110 | 0 |
| crossdomain-oriented-SLSQP | 100 | 9.834361 | 0 |
| local-oriented-SLSQP | 40 | 5.247009 | 2 |
| neighbor-oriented-SLSQP | 400 | 39.530845 | 0 |
| transfer-oriented-SLSQP | 200 | 16.464241 | 0 |

Wall sums are durations of sequential candidate jobs (native annealing included), exclude download/compilation/reporting, and are not total session time or CPU utilization. No speedup is claimed.

## Exact-valid witnesses vs baselines

| Variant | n | Trials | Valid | Best candidate (approx display) | Baseline (approx display) | Best seed |
|---|---:|---:|---:|---:|---:|---:|
| convex | 14 | 100 | 100 | 0.027274731889281669 | 0.027835580517553696 | 1972 |
| convex | 15 | 720 | 720 | 0.024564055613229874 | 0.024564055613230173 | 1066 |
| convex | 16 | 100 | 100 | 0.019788530332296005 | 0.022272877128981267 | 1931 |
| triangle | 13 | 100 | 100 | 0.026556528919724941 | 0.026556528919738264 | 1854 |
| triangle | 14 | 720 | 717 | 0.023775773107531803 | 0.02377577310757277 | 1012 |
| triangle | 15 | 100 | 100 | 0.019258662328399338 | 0.021090769460266688 | 1875 |

Every displayed value is only a readable approximation to the rational fractions in the candidate and source artifacts. The best triangle14 and convex15 runs rediscover the incumbent, losing small amounts through inward rational snapping/decimal truncation. The larger failure is structural: most different order cells settle into inferior local maxima; repeated exact reproduction does not make the result new.

## Adaptive chronology

1. Seeds1000–1019: local analytic epigraph SLSQP under four perturbation magnitudes, triangle14/convex15. No improvement; small perturbations return to incumbent, large ones often enter much poorer order types.
2. Seeds1020–1119: deletion from n+1 sources or insertion into n−1 sources, then polish. No improvement; neighborhood labels systematically cycled.
3. Seeds1120–1619: discrete crossing of a selected point/line orientation wall before optimization. This changes combinatorial cells, rather than simply repeating local jitter. No improvement.
4. Seeds1620–1719: native-C reheated Metropolis simulated annealing, 200000 steps per restart, followed by analytic SLSQP. No improvement. This annealer's chosen schedule yields inferior basins; no reason to replicate this schedule unchanged.
5. Seeds1720–1819: disk15→free-convex transfer. Yang's exact disk witness has free-hull ratio140079044255204807636052/5720877150824075844291349≈0.024485588584091 before polish. Perturb/optimize; no improvement beyond current convex15 incumbent.
6. Seeds1820–2019: delete/insert around original targets while comparing directly against frozen triangle13/15 and convex14/16 incumbents. No improved adjacent case.

## Corrections and limitations

Original literal triangle14/convex15 witnesses each have ONE exact minimizing triple. Website counts23/25 describe approximately tied active constraints; they are not exact rational ties. Numeric optimizer success is not a certificate: infeasible outputs were rejected, including slight boundary violations. Later triangle outputs project to the reference triangle then move inward before exact checking. Every rejection remains in JSONL and stdout logs.

Search explores finitely many order cells and has no global exclusion argument. No existence proof is inferred from floating point residuals. Historical-current baselines are source-authored witnesses from a live table, not exhaustive guarantees that no new competing record exists. Download timestamps and checksums identify exactly which data were compared. The latest source refresh should occur before any future record announcement.

## Reproduction

From repository root, use `.venv/bin/python research/geometric-extremal/search/area/discover.py --mode local --start 1000 --stop 1020 --maxiter 250`. Subsequent modes transfer(1020..1119,500 iterations), cellflip(1120..1619,500), crossdomain(1720..1819,700), neighbor(1820..2019,700). Compile native optional annealer with `cc -O3 research/geometric-extremal/search/area/triangle_anneal.c -lm -o research/geometric-extremal/search/area/triangle_anneal`; anneal mode1620..1719,maxiter500. Source snapshots are cached; replay does not require new network fetches. Remove/move previous experiment outputs before replay if duplicate registry entries are undesirable.

## Next research decisions

Stop the mature small-n square/triangle/convex local-search wave. Escalate to contact-graph program search, combinatorial order-type enumeration with certifiable relaxations, or higher-n instances showing current percent-scale progress. A general theorem needs a mathematical mechanism not contained in these negative trials. Current evidence supports infrastructure and reproducible negative research only.
