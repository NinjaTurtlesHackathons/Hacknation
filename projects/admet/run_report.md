# ADMET run report

## Boundary
This is a completed reproducible pilot manuscript, not evidence of publication-level novelty, clinical efficacy or a leaderboard record. Three regression endpoints were modeled; all 22 source datasets were audited. Existing reaction/Bell/proofreading work remains untouched.

## Protocol compliance
- Required skills discovered on paper-bell, fully read with framework/API; isolated research/admet branch.
- Full mode/module B chosen autonomously, as explicitly authorized. No human gate questions or outreach.
- Scout, Analogist and independent Red-Team have separate artifacts.
- Domain scaffold created via asd.new_domain; verifier selftest precedes successful model fitting.
- Protocol written before training; failed pre-commit initialization and row-index correction disclosed in prereg.md. No model fit or score was produced by the failed initialization.
- Source provenance, units, coverage, duplicate/scaffold audits and fixed naive/learned baselines recorded.
- Training and descriptor/fingerprint ablations run at fixed 20 seeds; source-grounded independent MAE calculation.
- Test artifacts/models frozen before first score; two invalid-SMILES fallbacks fixed before fit.
- Paired intervals/permutations, primary BH family and expanded family over controls; inference is fixed-dataset sensitivity.
- Negative controls and neutral identifier exposure check recorded, with their limits.
- Lean arithmetic anchor verified; ML claims remain observed/statistical.
- All release manuscript paragraphs generated from confirmed domain.check records in state.json; no qualitative scientific conclusion inferred from the weak shared numerical-token gate.
- One demo path reads experiments/claims/gates only.
- Databricks integration is an unexecuted template, not provisioned. Expert review, independent assays and the full jury rubric remain absent. Videos have scripts only; user asked for a paper, not recording or upload.

## Reproduction after validation-only agent loop
On a fresh run without a pre-existing seal:

```bash
.venv-admet/bin/python projects/admet/freeze.py
.venv-admet/bin/python projects/admet/engine.py test
.venv-admet/bin/python projects/admet/record_test_hashes.py
.venv-admet/bin/python projects/admet/analyze.py
.venv-admet/bin/python projects/admet/validate.py --release
.venv-admet/bin/python projects/admet/enrich_release.py
ASD_LLM_CACHE=projects/admet/llm_cache .venv-admet/bin/python -m asd.paper --domain admet --titel "Physicochemical Descriptors Improve Fixed Fingerprint Baselines Across Three ADMET Endpoints" --autoren "NinjaTurtlesHackathons" --affiliation "Research draft" --lang en
# preserve this raw agent draft, then deterministic release:
.venv-admet/bin/python projects/admet/render_release.py
```

The original seal is retained. Post-score changes to scorer grounding and mutable round preregistration are documented. frozen_protocol.md reconstructs the exact originally hashed protocol; release_hashes records current hardened scoring code and unchanged predictions. A seal is an audit trail, not protection against a malicious process with filesystem access.

## Impact and publication gate
The pilot demonstrates reductions relative to a fixed Morgan/LightGBM baseline and gives reproducible ablations. It does not show a new discovery mechanism or beat strong tuned competitors. The final scientific-impact gate therefore remains open. Publish or submit only with proper human authorship, stronger competitive baselines and independent replication.

## Completed numerical replication
A fresh download, full refit and frozen final-test evaluation passed: all 15 endpoint/method mean MAEs reproduced within 1e-8. See reproduction.json. The released standalone LaTeX source also compiled successfully with the built-in editor compiler; all five PDF pages were visually inspected.
