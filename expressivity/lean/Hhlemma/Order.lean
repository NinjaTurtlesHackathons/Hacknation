import Mathlib

/-!
Order lemma (expressivity domain, lemma L4): a real matrix of finite order that differs from the identity by rank at most one
is an involution. Consequence: a letter of order >= 3 can never be realised by a single Householder factor, even in a larger
covering group, so h*(G, Sigma) >= 2 whenever the alphabet contains an element of order >= 3.
-/

open Matrix Module

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- A matrix of rank at most one satisfies `R * R = τ • R` for some scalar `τ`. -/
theorem sq_eq_smul_of_rank_le_one (R : Matrix n n ℝ) (hR : R.rank ≤ 1) : ∃ τ : ℝ, R * R = τ • R := by
  have hfin : finrank ℝ (LinearMap.range R.mulVecLin) ≤ 1 := hR
  obtain ⟨w, hw⟩ := (finrank_le_one_iff (K := ℝ) (V := LinearMap.range R.mulVecLin)).mp hfin
  -- every vector in the range is a multiple of w
  have hRw : (R.mulVecLin (w : n → ℝ)) ∈ LinearMap.range R.mulVecLin := LinearMap.mem_range_self _ _
  obtain ⟨τ, hτ⟩ := hw ⟨_, hRw⟩
  refine ⟨τ, ?_⟩
  apply Matrix.toLin'.injective
  apply LinearMap.ext; intro x
  have hx : (R.mulVecLin x) ∈ LinearMap.range R.mulVecLin := LinearMap.mem_range_self _ _
  obtain ⟨c, hc⟩ := hw ⟨_, hx⟩
  have hc' : R *ᵥ x = c • (w : n → ℝ) := by
    have := congrArg Subtype.val hc; simpa [Matrix.mulVecLin_apply] using this.symm
  have hτ' : R *ᵥ (w : n → ℝ) = τ • (w : n → ℝ) := by
    have := congrArg Subtype.val hτ; simpa [Matrix.mulVecLin_apply] using this.symm
  simp only [Matrix.toLin'_apply, ← Matrix.mulVec_mulVec, hc', Matrix.mulVec_smul, hτ']
  rw [Matrix.smul_mulVec, hc', smul_comm]

/-- Powers of `1 + R` when `R * R = τ • R`. -/
theorem pow_one_add (R : Matrix n n ℝ) (τ : ℝ) (h : R * R = τ • R) (k : ℕ) :
    (1 + R) ^ k = 1 + (∑ i ∈ Finset.range k, (1 + τ) ^ i) • R := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [pow_succ, ih, Finset.sum_range_succ]
    set s := ∑ i ∈ Finset.range k, (1 + τ) ^ i with hs
    have hg : s * τ = (1 + τ) ^ k - 1 := by
      have := geom_sum_mul (1 + τ) k
      simpa [← hs] using this
    rw [add_mul, mul_add, mul_add, one_mul, mul_one, one_mul, Matrix.smul_mul, h, smul_smul, hg]
    module

/-- **Lemma L4.** A real matrix of finite order with `rank (M - 1) ≤ 1` is an involution. -/
theorem sq_eq_one_of_rank_le_one_of_pow_eq_one (M : Matrix n n ℝ) (hr : (M - 1).rank ≤ 1)
    (N : ℕ) (hN : 0 < N) (hM : M ^ N = 1) : M ^ 2 = 1 := by
  set R := M - 1 with hRdef
  have hMR : M = 1 + R := by rw [hRdef]; abel
  obtain ⟨τ, hτ⟩ := sq_eq_smul_of_rank_le_one R hr
  have hpow := pow_one_add R τ hτ
  by_cases hR0 : R = 0
  · rw [hMR, hR0]; simp
  · have hN' := hpow N
    rw [← hMR, hM] at hN'
    have h0 : (∑ i ∈ Finset.range N, (1 + τ) ^ i) • R = 0 := by
      have := congrArg (fun X => X - 1) hN'
      simpa using this.symm
    have hs : (∑ i ∈ Finset.range N, (1 + τ) ^ i) = 0 := by
      rcases smul_eq_zero.mp h0 with h | h
      · exact h
      · exact absurd h hR0
    have ha : 1 + τ = -1 := by
      rcases le_or_gt 0 (1 + τ) with hpos | hneg
      · exfalso
        have h1 : (1 : ℝ) ≤ ∑ i ∈ Finset.range N, (1 + τ) ^ i := by
          calc (1 : ℝ) = (1 + τ) ^ 0 := by simp
            _ ≤ ∑ i ∈ Finset.range N, (1 + τ) ^ i :=
              Finset.single_le_sum (fun i _ => pow_nonneg hpos i) (Finset.mem_range.mpr hN)
        linarith
      · have hg := geom_sum_mul (1 + τ) N
        rw [hs, zero_mul] at hg
        have haN : (1 + τ) ^ N = 1 := by linarith
        have habs : |1 + τ| ^ N = 1 := by rw [← abs_pow, haN, abs_one]
        have h1 : |1 + τ| = 1 := (pow_eq_one_iff_of_nonneg (abs_nonneg _) (by omega)).mp habs
        rw [abs_of_neg hneg] at h1
        linarith
    rw [hMR, hpow 2]
    simp [Finset.sum_range_succ, ha]

/-- **Corollary (order lemma for covering groups).** If `ρ` is a faithful real representation of a finite group `H`, `π : H → G`
a homomorphism and `π t = s` with `orderOf s ≥ 3`, then `ρ t` is not a single Householder-type factor: `rank (ρ t - 1) > 1`. -/
theorem no_single_householder_lift {H G : Type*} [Group H] [Finite H] [Group G]
    (ρ : H →* Matrix n n ℝ) (hρ : Function.Injective ρ) (π : H →* G) (t : H) (s : G) (hs : π t = s)
    (hord : 3 ≤ orderOf s) : ¬ (ρ t - 1).rank ≤ 1 := by
  intro hr
  have hpos : 0 < orderOf t := orderOf_pos t
  have hpowN : ρ t ^ orderOf t = 1 := by rw [← map_pow, pow_orderOf_eq_one, map_one]
  have h2 : ρ t ^ 2 = 1 := sq_eq_one_of_rank_le_one_of_pow_eq_one (ρ t) hr _ hpos hpowN
  have ht2 : t ^ 2 = 1 := hρ (by rw [map_pow, h2, map_one])
  have hs2 : s ^ 2 = 1 := by rw [← hs, ← map_pow, ht2, map_one]
  have := orderOf_le_of_pow_eq_one (by norm_num) hs2
  omega
