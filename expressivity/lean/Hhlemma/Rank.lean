import Mathlib

/-!
Rank lemma for Householder-product transitions (expressivity domain, lemma L1).

A generalized Householder matrix is `1 + R` with `R = -β • vecMulVec u u` of rank at most one. A token transition of DeltaProduct_k
is a product of `k` such matrices. We prove: if every `R_i` has rank at most one, then `rank (∏ (1 + R_i) - 1) ≤ k`.
This is the necessity half of the Householder-complexity bound: a letter whose transition differs from the identity by rank `r`
needs at least `r` Householder factors.
-/

open Matrix Module

variable {n K : Type*} [Fintype n] [DecidableEq n] [Field K]

omit [DecidableEq n] in
theorem rank_add_le' (A B : Matrix n n K) : (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  rw [Matrix.mulVecLin_add]
  calc finrank K (LinearMap.range (A.mulVecLin + B.mulVecLin))
      ≤ finrank K ((LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin : Submodule K (n → K))) :=
        Submodule.finrank_mono (LinearMap.range_add_le _ _)
    _ ≤ finrank K (LinearMap.range A.mulVecLin) + finrank K (LinearMap.range B.mulVecLin) :=
        Submodule.finrank_add_le_finrank_add_finrank _ _

theorem rank_mul_sub_one_le (A B : Matrix n n K) :
    (A * B - 1).rank ≤ (A - 1).rank + (B - 1).rank := by
  have h : A * B - 1 = (A - 1) * B + (B - 1) := by noncomm_ring
  rw [h]
  calc ((A - 1) * B + (B - 1)).rank ≤ ((A - 1) * B).rank + (B - 1).rank := rank_add_le' _ _
    _ ≤ (A - 1).rank + (B - 1).rank := by
        gcongr
        exact Matrix.rank_mul_le_left _ _

/-- Main lemma (L1): a product of `k` rank-one perturbations of the identity differs from the identity by rank at most `k`. -/
theorem rank_prod_sub_one_le (L : List (Matrix n n K)) (hL : ∀ R ∈ L, R.rank ≤ 1) :
    ((L.map (fun R => 1 + R)).prod - 1).rank ≤ L.length := by
  induction L with
  | nil => simp
  | cons R L ih =>
    simp only [List.map_cons, List.prod_cons, List.length_cons]
    calc ((1 + R) * (L.map (fun R => 1 + R)).prod - 1).rank
        ≤ ((1 + R) - 1).rank + ((L.map (fun R => 1 + R)).prod - 1).rank := rank_mul_sub_one_le _ _
      _ ≤ 1 + L.length := by
          gcongr
          · simpa using hL R (by simp)
          · exact ih (fun R' h => hL R' (by simp [h]))
      _ = L.length + 1 := by ring

omit [DecidableEq n] in
/-- A generalized Householder factor `1 - β u uᵀ` is `1 + R` with `rank R ≤ 1`. -/
theorem householder_perturbation_rank_le (β : K) (u : n → K) : (-(β • vecMulVec u u)).rank ≤ 1 := by
  have : -(β • vecMulVec u u) = vecMulVec (-β • u) u := by
    ext i j; simp [vecMulVec_apply, mul_assoc]
  rw [this]; exact rank_vecMulVec_le _ _

/-- Corollary: a DeltaProduct transition with `k` Householder factors `1 - β u uᵀ` satisfies `rank (A - 1) ≤ k`. -/
theorem deltaproduct_rank_le (L : List (K × (n → K))) :
    (((L.map (fun (p : K × (n → K)) => -(p.1 • vecMulVec p.2 p.2))).map (fun (R : Matrix n n K) => 1 + R)).prod - 1).rank
      ≤ L.length := by
  have h := rank_prod_sub_one_le (L.map (fun (p : K × (n → K)) => -(p.1 • vecMulVec p.2 p.2))) (by
    intro R hR
    obtain ⟨p, -, rfl⟩ := List.mem_map.mp hR
    exact householder_perturbation_rank_le p.1 p.2)
  simpa using h
