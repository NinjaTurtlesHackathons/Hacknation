# ADMET research project

Scope: three preregistered regression endpoints, all 22 ADMET endpoints audited. Work is isolated under `projects/admet`, plus the required `asd/domains/admet_domain.py` adapter. Original domain implementations unchanged.

Reproduction from repository root (Python 3.12):

```bash
uv venv --python 3.12 .venv-admet
uv pip install --python .venv-admet/bin/python -r projects/admet/requirements.lock.txt --no-deps
.venv-admet/bin/python -m asd.selftest admet
.venv-admet/bin/python projects/admet/engine.py audit
.venv-admet/bin/python projects/admet/validate.py
.venv-admet/bin/python projects/admet/engine.py valid
ASD_LLM_CACHE=projects/admet/llm_cache .venv-admet/bin/python -m asd.lab_loop --domain admet --recherche --runden 3 --budget-usd 100000 --fragen projects/admet/startfragen.json
```

Final-test commands and paper generation are documented in the run report after method freeze. Use a fresh artifact directory/branch for reruns; do not overwrite sealed evidence. Raw data and fitted models are downloaded/rebuilt locally. `provenance.json` pins raw CSV hashes and package versions. Rebuilt models require the same pinned environment; numerical reproducibility can still depend on CPU/compiler.

Twenty repeated training splits are not twenty independent biological datasets. Test reporting uses fixed original TDC test rows and all models were frozen before scoring. This is not an official leaderboard submission or a clinical validation study. See `prereg.md` for the failed pre-commit initialization and the invalid-SMILES fallback amendment.

The shared writer's numeric-token gate is insufficient to guarantee semantic truth. The ADMET release uses a stricter local evidence export and independent review; no output gets a theorem label for floating-point experiments.

For a fresh numerical replication preserving the release artifacts:

```bash
.venv-admet/bin/python projects/admet/reproduce.py
```

It downloads the same source snapshot, runs the matrix in a new timestamped directory, freezes before test scoring and compares final scores at absolute tolerance 1e-8. It fails explicitly on changed raw data or numerical drift. To rebuild the released manuscript/demo from existing verified state and tables, run `render_release.py`; this does not call an LLM.

Released files: paper.pdf (five-page manuscript), paper.tex (standalone editable source), paper.md (canonical text), paper_belege.json (paragraph support), demo.html (tables only). The original framework writer output is retained under agent_draft/ and is not the released manuscript.
