# algo_efficiency: Algorithms and Efficiency domain of the Verifier-Gated Discovery Lab

Scope (only this): (1) attention in subquadratic time (polynomial method; fine-grained limits), quantization/sketching/low-rank
with error bounds; (2) speculative decoding with optimality proofs; KV-cache compression.
Goal: a paper produced by the lab in which every statement is verified by code. Framework: `docs/FRAMEWORK.md`, skills
`verifier-gated-lab` and `rigorous-innovation`. Compliance with every rule is tracked in [COMPLIANCE.md](COMPLIANCE.md).

## Pipeline (one path, rebuildable from code)
```bash
pip install numpy scipy pandas mpmath scikit-learn
python -m asd.selftest algo_efficiency                       # verifier self-test, must say BESTANDEN (24/24)
python -m algo_efficiency.certify_tables                     # systematic certified tables -> results/certified.json (~5 min)
python -m algo_efficiency.confirm                            # preregistered confirmatory runs (prereg.md) -> results/confirmatory.json
python -m asd.lab_loop --domain algo_efficiency --recherche --runden 8 --budget-usd 5 --fragen algo_efficiency/questions.json
python -m algo_efficiency.export_tables                      # projects/algo_efficiency/tables/{experiments,claims,gates}.csv
python -m algo_efficiency.write_paper --authors "..." --affiliation "..." --review algo_efficiency/review.json --errata algo_efficiency/errata.json   # paper.md/.tex/.pdf
```

## Files
| File | Role |
|---|---|
| `domain.py` | `Domain` subclass: experiments (`run_op`), verifier (`check`), self-test, `describe`, `level`, `widerspricht` |
| `spec.py` | speculative decoding: exact rules, exact optimal multi-draft acceptance (max-flow = min-cut), optimal draft length; float LP and Monte Carlo experiments |
| `polyexp.py` | polynomial method: Remez, exact rationalisation, rigorous upper bound (interval Taylor models), de la Vallee Poussin lower bound |
| `kv.py` | KV eviction policies on an explicit synthetic attention model; paired comparisons on fixed seeds |
| `certify_tables.py`, `confirm.py`, `search_counterexample.py` | systematic certification, preregistered confirmatory runs, counterexample search |
| `export_tables.py`, `write_paper.py` | project tables + gates; English paper under the framework's hallucination gate |
| `context.md`, `assumptions.md`, `candidates.md`, `evidence.md`, `prereg.md`, `decisions.md` | rigorous-innovation artefacts (Full mode) |
| `analysis/redteam.md` | red-team report (separate agent, read + execute only) |
| `questions.json` | start questions for the lab loop |
| `../asd/domains/algo_efficiency_domain.py` | 2-line registry shim |

## Claim types and evidence levels
See `DOMAIN.claim_doc`. Exact rational and interval-certified checks are `computed_rigorous`; KV comparisons would be
`statistical`, but are downgraded to `observed` because the preregistered negative control failed (prereg.md, addendum).
Nothing here is `proved_lean` (no Lean toolchain in the sandbox).
