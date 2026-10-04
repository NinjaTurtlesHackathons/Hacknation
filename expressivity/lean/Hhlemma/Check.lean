import Hhlemma.Rank

open Matrix

/-- Negative control: the bound is tight, so the strengthened (false) statement `rank ≤ k - 1` is refuted formally
(one reflection `1 + (-2)` on a 1-dimensional space differs from the identity by rank 1). -/
theorem strengthened_bound_false :
    ¬ (∀ (L : List (Matrix (Fin 1) (Fin 1) ℚ)), (∀ R ∈ L, R.rank ≤ 1) →
        ((L.map (fun R => 1 + R)).prod - 1).rank ≤ L.length - 1) := by
  intro h
  have hR : (-2 : Matrix (Fin 1) (Fin 1) ℚ).rank ≤ 1 := by
    simpa using Matrix.rank_le_card_width (-2 : Matrix (Fin 1) (Fin 1) ℚ)
  have h1 := h [(-2 : Matrix (Fin 1) (Fin 1) ℚ)] (by simpa using hR)
  have hu : IsUnit (-2 : Matrix (Fin 1) (Fin 1) ℚ) := by
    rw [Matrix.isUnit_iff_isUnit_det, Matrix.det_unique]
    have e : (-2 : Matrix (Fin 1) (Fin 1) ℚ) default default = -2 := by
      simp [Matrix.ofNat_apply]
    rw [e]; exact isUnit_iff_ne_zero.mpr (by norm_num)
  have h2 : (-2 : Matrix (Fin 1) (Fin 1) ℚ).rank = 1 := by simpa using Matrix.rank_of_isUnit _ hu
  have h3 : ((1 + (-2 : Matrix (Fin 1) (Fin 1) ℚ)) - 1) = -2 := by abel
  simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one, List.length_cons, List.length_nil] at h1
  rw [h3, h2] at h1
  norm_num at h1

#print axioms rank_prod_sub_one_le
#print axioms deltaproduct_rank_le
#print axioms strengthened_bound_false
