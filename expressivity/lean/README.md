# Lean 4 proof of the rank lemma (lemma L1, level proved_lean)

`Hhlemma/Rank.lean` proves, with Lean 4 (v4.35.0-rc3) and Mathlib (pinned in `lake-manifest.json`):
- `rank_prod_sub_one_le`: if every `R_i` has rank at most one, then `rank (∏ (1 + R_i) - 1) ≤ k` (over any field).
- `householder_perturbation_rank_le`: a generalized Householder factor `1 - β u uᵀ` is `1 + R` with `rank R ≤ 1`.
- `deltaproduct_rank_le`: a DeltaProduct transition with `k` Householder factors satisfies `rank (A - 1) ≤ k`.

`Hhlemma/Check.lean` is the negative control (skill module F): `strengthened_bound_false` refutes the bound `≤ k - 1`, and
`#print axioms` shows that all three theorems use only `propext`, `Classical.choice`, `Quot.sound` (no `sorry`); output in `check.out`.

Reproduce:
```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
cp -r expressivity/lean /tmp/hhlemma && cd /tmp/hhlemma && lake exe cache get && lake build Hhlemma.Rank && lake env lean Hhlemma/Check.lean
```
