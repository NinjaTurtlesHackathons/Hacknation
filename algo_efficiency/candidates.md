# Candidate approaches (Phase 2) and selection matrix

Scores 1-5 (* = knock-out at 1). Criteria: verifiable*, expected gain vs baseline, data situation*, effort within timebox, jury fit, hard to copy, explainable in 30 s.

| Candidate | verifiable | gain | data | effort | jury fit | hard to copy | 30 s | Decision |
|---|---|---|---|---|---|---|---|---|
| C1 Exact multi-draft optimum via max-flow = min-cut on draft SETS (not tuples) | 5 | 4 | 5 | 5 | 5 | 3 | 4 | **chosen** |
| C2 Certified d*(B, eps) via Remez + interval Taylor models + de la Vallee Poussin | 5 | 4 | 5 | 3 | 5 | 4 | 4 | **chosen** |
| C3 Lean proof of opt_wor >= opt_iid | 5 | 3 | 5 | 1 (no Lean, Mathlib needed) | 5 | 5 | 3 | deferred (needs Lean install; asked the user) |
| C4 KV eviction on real LLM traces | 3 | 4 | 1* | 2 | 4 | 3 | 4 | rejected (no weights/traces offline) |
| C5 KV eviction on explicit synthetic model with negative control | 3 | 2 | 5 | 5 | 3 | 2 | 4 | chosen, labelled synthetic |
| C6 Quantization error bounds (worst-case TV of softmax under logit perturbation = tanh(eps/2)) | 4 | 2 | 5 | 3 | 3 | 2 | 4 | open question for the paper (not verified, not claimed) |
| C7 Sketching / low-rank: Eckart-Young spectra of exp(QK^T) | 2 (floating point) | 2 | 5 | 5 | 3 | 1 | 4 | experiment op only (observed), no claims |

Formal stage (5.2): no method is transferred from another domain, so the default stage (empty, infinity) applies; the max-flow formulation is a reformulation within the same problem, re-verified in the target (flow and cut both computed for every instance).
Fallback: if a certificate fails, report the cell as "not certified" (never as a value).
