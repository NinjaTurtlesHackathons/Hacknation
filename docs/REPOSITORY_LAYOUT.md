# Repository layout

The repository intentionally contains the reproducible research record and selected challenge/demo artifacts.

The following paths are generated local/runtime data and are not part of version control:

- `cache/` — LLM response cache
- `mlruns/` — local MLflow tracking data
- `delta/` — locally exported Delta/Parquet tables
- `frontend/data/raw/` — raw frontend export duplicated from canonical run data

Canonical evidence remains versioned under `results/`, `projects/`, `runs/`, `research/`, and the relevant benchmark directories.

The Hackathon/Challenge history is intentionally retained where it provides provenance or explains design decisions.
