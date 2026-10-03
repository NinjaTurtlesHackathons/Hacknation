# Preregistration: algo_efficiency (commit before any confirmatory run; the commit hash is the timestamp)

## Disclosure: exploratory runs before this preregistration (Sun 2026-10-04, ~01:30-01:50)
The following were computed BEFORE this file existed and are therefore **exploratory**; they may motivate hypotheses below but
are not confirmatory evidence: KV comparison at n = 512, budget = 64 (seeds 1000-1019); multi-draft table on instance seeds
0-149; counterexample search on instance seeds 10000-12999. Exact computations (degree table, gamma table) are certificates,
not hypothesis tests; their order relative to this file does not matter.

## H-AE1 (KV-cache, confirmatory, statistical)
- Model: synthetic attention model of `algo_efficiency/kv.py` (structured = True, logit scale 6), **new configuration n = 1024, budget = 128**, m = 32, h = 32.
- Seeds 1000-1019 (verifier-owned, fixed project-wide).
- Primary: h2o has lower mean relative output error than sink_recent.
- Secondary: (a) sink_recent < recent; (b) h2o < random; (c) oracle < h2o.
- Test: paired one-sided sign-flip permutation test (20,000 flips, `asd.stats.perm_test`), effect = ratio of means with paired bootstrap 95% CI (`asd.stats.ratio_ci`).
- Success per hypothesis: p < 0.05 and CI lower bound > 1, and BH-adjusted p < 0.1.
- Multiple testing: Benjamini-Hochberg with q = 0.1 over **all** KV tests in this file (primary, 3 secondary, 3 negative-control tests: m = 7).
- Reported regardless of outcome.

## Negative control for H-AE1 (mandatory check 2)
- Same configuration with structured = False (no sinks, heavy hitters, locality or shared query direction).
- Expectation: none of recent, sink_recent, h2o beats random (each p > 0.05). If one does, the generator or metric is biased and every KV claim is downgraded.

## Theory checks (run with every confirmatory run)
- T1: Monte Carlo of the standard rule must match the exact acceptance sum min(p, q): |z| < 3 on each of 20 instances (instance seeds 1000-1019, V = 4, 200,000 samples, MC seed = instance seed). Same for rrs_iid and rrs_wor with k = 2 against the exact values.
- T2: For every certified cell of the degree table, d*(B, eps) <= Taylor degree estimate (the Taylor polynomial is one admissible polynomial).
- T3: For every multi-draft instance: rrs_iid <= opt_iid and rrs_wor <= opt_wor (a lossless rule cannot beat the optimum), exactly.

## H-AE2 (multi-draft, confirmatory counterexample search, exact)
- Statements: S1 opt_wor >= opt_iid (hand proof exists); S2 rrs_wor >= rrs_iid (conjecture).
- Fresh instance seeds 20000-24999; V = 3 + seed mod 5 (3..7), k = 2 + (seed div 5) mod 3, reduced to k = 2 when V^k > 1300; Dirichlet concentration cycling through 0.1, 0.3, 1, 3; denominators 1000.
- Outcome: number of counterexamples (any counterexample is certified through DOMAIN.check and reported). Zero counterexamples is reported as support, not proof.

Changes to this file after the first confirmatory run only as a new dated section with reason.

## Addendum 2026-10-04 ~02:30 (after the confirmatory run; criteria above unchanged)
- Confirmatory run: `python -m algo_efficiency.confirm` (results/confirmatory.json), executed after commit a3b3eb6 of this file.
- **Negative control FAILED:** in the structure-free model h2o beats random (mean error 1.6237 vs 1.7359, p < 0.001); recent and sink_recent do not (p = 0.54, 0.62). As preregistered, **every KV claim is downgraded** (level observed, not statistical), although H-AE1 primary and all secondaries reached p < 0.001.
- Post-hoc explanation (hypothesis only, not tested): Gaussian keys have varying norms, so high-norm keys attract attention from all queries even without planted structure; h2o exploits these "natural heavy hitters". A control with unit-norm keys would separate this; it would need a new preregistration.
- T1, T2, T3 passed; H-AE2: 0 counterexamples to S1 and S2 in 5,000 fresh instances (support, not proof).
