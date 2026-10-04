# Representation theory paper (verifier-gated)

Short, self-contained paper on complex representations of finite groups (Maschke, Schur, orthogonality,
sum of squares, number of irreducibles = number of classes, column orthogonality), with all proofs, plus character tables
of 13 small groups certified in exact arithmetic.

| File | Content |
|---|---|
| `theorems.txt` | **Plain extraction** of all definitions, theorems, proofs and results (written by hand before the paper, not by the paper-writer agent). Source of truth for the paper. |
| `cyclo.py` | Exact arithmetic in Q(zeta_N) (standard library only, no floating point) |
| `certify.py` | Verifier: self-test (7 true + 8 false statements), then 22 certificates; writes `out/claims.csv`, `out/gates.csv`, `out/tables.json` |
| `refs_check.py` | Checks every reference against Crossref → `out/refs.json` (unverified citations block the build) |
| `build_paper.py` | Gate + build: re-runs the verifier, typesets the character tables from the verifier, refuses any theorem-like environment without a verified/proved `\claim{ID}`, checks citations, runs pdflatex |
| `paper.tex`, `paper.pdf` | The paper (8 pages) |

```bash
python3 reptheory/certify.py       # ~1 s, standard library only
python3 reptheory/refs_check.py    # needs network (Crossref)
python3 reptheory/build_paper.py   # needs pdflatex with amsmath, mathtools, booktabs, longtable, hyperref
```

## Evidence levels
- `computed_rigorous` (22 claims, IDs `E-*`): recomputed exactly by `certify.py`, status `verified`.
- `proved_text` (13 claims, general theorems): full proof in `theorems.txt` and in the paper, status `proved`; each linked to
  the certificates that test it on concrete groups. Not machine-checked.

## Deviations from the lab framework (docs/FRAMEWORK.md of the paper pipeline), on purpose for a fast paper
- No Lean: not installed here, so general proofs stay at `proved_text`. Next step: formalize Lemma 2 / Theorem 3.
- No agentic literature phase (≥1000 hits) and no novelty phase: the content is classical textbook material, stated as
  such in the paper; three textbooks cited, each checked via Crossref DOI lookup.
- No LLM paper-writer/referee pass: the paper was written directly from `theorems.txt`; the hallucination gate is
  replaced by `build_paper.py` (claim tags on every environment, tables generated from the verifier).
