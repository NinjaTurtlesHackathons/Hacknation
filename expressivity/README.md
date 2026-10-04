# expressivity: Expressivity and limits of architectures (Verifier-Gated Discovery Lab)

Scope (only this): what Transformers, SSMs (Mamba) and linear attention / linear RNNs can provably compute and what not, via
circuit complexity (TC0, NC1), formal languages (word problems of finite groups), and chain of thought as computation depth.
Result: an exact per-layer law for state tracking in linear RNNs with Householder-product transitions (DeltaNet, DeltaProduct),
the Householder complexity h*(G, Sigma), with the first lower bound on Householder factors per token (machine-checked core lemmas),
exact certificates, an atlas of all 319 groups of order <= 63, and a preregistered training grid.
Framework: `docs/FRAMEWORK.md`, skills `verifier-gated-lab` and `rigorous-innovation`. Rule compliance: [COMPLIANCE.md](COMPLIANCE.md).

## Pipeline (one path, rebuildable from code; run from the repository root)
```bash
pip install numpy scipy pandas mpmath torch matplotlib
# oracles: GAP 4 (e.g. conda create -p ~/.conda_envs/gap -c conda-forge gap-defaults) and Lean 4 + Mathlib (expressivity/lean/README.md)
python -m asd.selftest expressivity                 # verifier self-test, must say BESTANDEN
python -m expressivity.test_consistent              # consistency-rule regressions
python -m expressivity.certify                      # certified table of named tasks -> results/certified.json
python -m expressivity.atlas 63                     # all groups of order <= 63 (GAP SmallGroups) -> results/atlas.json
python -m expressivity.predict                      # predictions from certified bounds (written before the grid) -> results/predictions.json
python -m expressivity.confirm --workers 13         # preregistered grid (prereg.md), 66 cells x 20 seeds -> results/confirmatory/
python -m expressivity.confirm_mps                  # optional second runner on the MPS GPU for the same grid (EX21)
python -m expressivity.confirm_ex2                  # preregistered addendum H-EX2 (prior-work generator formats)
python -m expressivity.analyze                      # preregistered analysis -> results/confirmatory.json
python -m expressivity.run_lab --domain expressivity --recherche --runden 10 --budget-usd 25 --fragen expressivity/questions.json
python expressivity/scripts/verify_evidence.py      # titles + verbatim quotes of all 65 sources -> results/citations.tsv
python expressivity/scripts/body_quotes.py          # full-text quotes of the closest prior work -> results/body_quotes.json
python -m expressivity.write_paper                  # projects/expressivity/paper.{md,tex,pdf}, preprint form of the team (Suleman 2026 style)
python -m expressivity.export_tables                # projects/expressivity/tables/{experiments,claims,gates}.csv
python -m expressivity.recheck                      # reproduce every certificate with one command (team convention)
python expressivity/scripts/build_ledger.py         # companion proof ledger projects/expressivity/theory_ledger.pdf
```

## Files
| File | Role |
|---|---|
| `algebra.py` | exact real cyclotomic fields Q(2 cos 2 pi/N), exact matrices, Cartan–Dieudonné factorisation, permutation groups |
| `groups.py` | named groups (order-checked) and named alphabets |
| `chartab.py` | own numerical character tables (Burnside–Dixon), real irreducibles, faithful h |
| `gap_oracle.py` | independent oracle: GAP exact cyclotomic character tables |
| `reps.py`, `realisation.py` | constructions (permutation, SO(3), planar, count cover, sign twists) and the exact realisation certificate |
| `domain.py` | `Domain` subclass: experiments (floating point), verifier (exact), self-test, `describe`, `level`, `consistent` |
| `theory.md` | definitions, lemmas L1-L7, Theorem 1, proofs and their status |
| `lean/` | Lean 4 + Mathlib proofs of L1 (rank lemma) and L4 (order lemma), negative control, axiom check |
| `certify.py`, `atlas.py` | certified table, atlas |
| `train.py`, `predict.py`, `confirm.py`, `analyze.py` | models, predictions, preregistered grid, preregistered analysis |
| `run_lab.py`, `questions.json` | lab loop wrapper (robust JSON parsing, shared core untouched) and start questions |
| `write_paper.py`, `export_tables.py` | paper under the framework's hallucination gate; project tables and gates |
| `context.md`, `assumptions.md`, `candidates.md`, `evidence.md`, `prereg.md`, `decisions.md` | rigorous-innovation artefacts (Full mode) |
| `scout_evidence.md`, `analogist_candidates.md`, `analysis/redteam.md` | reports of the scout, analogist and red-team subagents |
| `../asd/domains/expressivity_domain.py` | 2-line registry shim |

## Evidence levels
`proved_lean`: L1, L4. `computed_rigorous`: exact certificates (closure over Q(2 cos 2 pi/N), consistency, invariant form, rank,
explicit reflections), character-table values where own computation and GAP agree. `statistical`: the preregistered grid.
`hypothesis`: hand proofs (L2, L3, L5, L7, Theorem 1) - reviewed by the red team, not machine-checked.
