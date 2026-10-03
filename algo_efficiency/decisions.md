# Decisions: algo_efficiency domain

| ID | Time | Decision | Alternatives | Evidence | Reversible? |
|---|---|---|---|---|---|
| AE1 | Sun 00:40 | Scope limited to: subquadratic attention (polynomial method, fine-grained limits, low rank), speculative decoding (optimality), KV-cache compression | broader efficiency topics | assignment | yes |
| AE2 | Sun 00:45 | Speculative decoding on finite vocabularies (V <= 8) with exact rational arithmetic; optimal multi-draft acceptance certified by exact max-flow = min-cut | float LP as verifier | an LP optimum in floating point is a candidate, not a certificate | yes |
| AE3 | Sun 00:50 | Polynomial method: verifier runs its own Remez (mpmath, 50 digits), rounds to exact rationals, upper bound by adaptive Taylor models in interval arithmetic, lower bound by de la Vallee Poussin | trust Remez error level | Remez is floating point; only interval-enclosed bounds count | yes |
| AE4 | Sun 01:05 | Bug found by the verifier itself: coefficients were re-rounded to 15 digits when converted to fractions; the certificate refused (no false positive). Fixed; covered by the B = 4, d = 10 selftest cases | - | rigorous_sup failed at B = 16, d = 30 | - |
| AE5 | Sun 01:15 | KV-cache: synthetic attention model (sinks, heavy hitters, locality, logit scale 6), claims only statistical over the verifier's 20 fixed seeds 1000-1019 | real LLM attention traces | no model weights or traces in the sandbox; downloading is out of scope for the deadline. Results are labelled synthetic | yes |
| AE6 | Sun 01:20 | Experiments use different methods than the verifier (float LP over draft tuples, Monte Carlo, Chebyshev interpolation) | reuse verifier code in experiments | a check must be an independent recomputation (FRAMEWORK.md, section 3) | yes |
| AE7 | Sun 01:20 | Domain code in its own folder algo_efficiency/; a 2-line shim asd/domains/algo_efficiency_domain.py registers it | code directly in asd/domains | own subfolder requested; core untouched | yes |
| AE8 | Sun 01:20 | All files of this domain are written in English | German like the rest of the repo | repository language rule of the author | yes |
