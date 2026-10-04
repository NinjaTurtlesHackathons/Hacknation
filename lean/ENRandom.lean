/-!
# E[N_random] = (n+1)/(k+1) — combinatorial core (Lean 4 core only, no Mathlib)

Setting: an urn with `n` items, `k` of which are "hits" (`1 ≤ k ≤ n` for the
probabilistic reading; the identities below hold for all `k ≤ n`). We draw
without replacement in uniformly random order; `N` is the position (1-based)
of the first hit, so `N ∈ {1, …, n-k+1}`.

All `choose n k` arrangements (sets of hit positions) are equally likely.
The event `N ≥ t` means "the first `t-1` draws are misses", i.e. all `k` hits
lie among the last `n-t+1` positions, so
  `#{N ≥ t} = choose (n-t+1) k`,  `P(N ≥ t) = choose (n-t+1) k / choose n k`.
Since `N ≥ 1` takes positive integer values, `E[N] = Σ_{t=1}^{n-k+1} P(N ≥ t)`.
Hence
  `E[N] = (n+1)/(k+1)`
  ⟺ `Σ_{t=1}^{n-k+1} choose (n-t+1) k / choose n k = (n+1)/(k+1)`
  ⟺ `(k+1) * Σ_{t=1}^{n-k+1} choose (n-t+1) k = (n+1) * choose n k`
(cross-multiplying, `choose n k > 0` for `k ≤ n`). The last line is exactly
theorem `expected_first_hit_cross` below, stated over `Nat`.
-/

namespace ENRandom

/-- Binomial coefficient via Pascal's recursion. -/
def choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => choose n k + choose n (k + 1)

@[simp] theorem choose_zero_right (n : Nat) : choose n 0 = 1 := by
  cases n <;> rfl

@[simp] theorem choose_zero_succ (k : Nat) : choose 0 (k + 1) = 0 := rfl

theorem choose_succ_succ (n k : Nat) :
    choose (n + 1) (k + 1) = choose n k + choose n (k + 1) := rfl

theorem choose_eq_zero_of_lt : ∀ {n k : Nat}, n < k → choose n k = 0
  | 0, 0, h => absurd h (by omega)
  | 0, _ + 1, _ => rfl
  | _ + 1, 0, h => absurd h (by omega)
  | n + 1, k + 1, h => by
      rw [choose_succ_succ, choose_eq_zero_of_lt (n := n) (k := k) (by omega),
        choose_eq_zero_of_lt (n := n) (k := k + 1) (by omega)]

/-- `sumLt f M = Σ_{m < M} f m`. -/
def sumLt (f : Nat → Nat) : Nat → Nat
  | 0 => 0
  | M + 1 => sumLt f M + f M

/-- `sumTo f n = Σ_{m=0}^{n} f m`. -/
def sumTo (f : Nat → Nat) (n : Nat) : Nat := sumLt f (n + 1)

/-- `sum1 g T = Σ_{t=1}^{T} g t`. -/
def sum1 (g : Nat → Nat) (T : Nat) : Nat := sumLt (fun i => g (i + 1)) T

theorem sumLt_congr (f g : Nat → Nat) :
    ∀ M, (∀ i, i < M → f i = g i) → sumLt f M = sumLt g M
  | 0, _ => rfl
  | M + 1, h => by
      simp only [sumLt]
      rw [sumLt_congr f g M (fun i hi => h i (by omega)), h M (by omega)]

/-- Hockey-stick identity: `Σ_{m=0}^{n} choose m k = choose (n+1) (k+1)`. -/
theorem hockey_stick (k : Nat) :
    ∀ n, sumTo (fun m => choose m k) n = choose (n + 1) (k + 1)
  | 0 => by
      simp [sumTo, sumLt, choose_succ_succ]
  | n + 1 => by
      have ih := hockey_stick k n
      simp only [sumTo, sumLt] at ih ⊢
      rw [ih, choose_succ_succ (n + 1) k]
      omega

/-- Absorption identity: `(k+1) * choose (n+1) (k+1) = (n+1) * choose n k`. -/
theorem absorption : ∀ n k, (k + 1) * choose (n + 1) (k + 1) = (n + 1) * choose n k
  | 0, 0 => rfl
  | 0, k + 1 => by simp [choose_succ_succ]
  | n + 1, 0 => by
      have ih := absorption n 0
      rw [choose_succ_succ (n + 1) 0]
      simp only [choose_zero_right, Nat.mul_one] at ih ⊢
      omega
  | n + 1, j + 1 => by
      have ih1 := absorption n j
      have ih2 := absorption n (j + 1)
      rw [choose_succ_succ (n + 1) (j + 1)]
      rw [choose_succ_succ n j] at ih1 ⊢
      generalize choose n j = A at ih1 ih2 ⊢
      generalize choose n (j + 1) = B at ih1 ih2 ⊢
      generalize choose (n + 1) (j + 2) = C at ih1 ih2 ⊢
      simp only [Nat.add_mul, Nat.mul_add, Nat.one_mul] at ih1 ih2 ⊢
      omega

/-- Reflection: `Σ_{t=1}^{T} f (M - t) + Σ_{m < M-T} f m = Σ_{m < M} f m` for `T ≤ M`. -/
theorem sum_reflect (f : Nat → Nat) (M : Nat) :
    ∀ T, T ≤ M → sumLt (fun i => f (M - (i + 1))) T + sumLt f (M - T) = sumLt f M
  | 0, _ => by simp [sumLt]
  | T + 1, h => by
      have ih := sum_reflect f M T (by omega)
      have hM : M - T = (M - (T + 1)) + 1 := by omega
      rw [hM] at ih
      simp only [sumLt] at ih ⊢
      omega

/-- Terms `m < k` of `Σ choose m k` vanish. -/
theorem sumLt_choose_below (k : Nat) : ∀ M, M ≤ k → sumLt (fun m => choose m k) M = 0
  | 0, _ => rfl
  | M + 1, h => by
      simp only [sumLt]
      rw [sumLt_choose_below k M (by omega), choose_eq_zero_of_lt (by omega)]

/-- Tail-sum reindexing:
`Σ_{t=1}^{n-k+1} choose (n-t+1) k = Σ_{m=0}^{n} choose m k` for `k ≤ n`. -/
theorem tail_sum_eq (n k : Nat) (hk : k ≤ n) :
    sum1 (fun t => choose (n - t + 1) k) (n - k + 1) = sumTo (fun m => choose m k) n := by
  unfold sum1 sumTo
  have hcongr : sumLt (fun i => choose (n - (i + 1) + 1) k) (n - k + 1)
      = sumLt (fun i => choose (n + 1 - (i + 1)) k) (n - k + 1) := by
    apply sumLt_congr
    intro i hi
    by_cases h : i + 1 ≤ n
    · have : n - (i + 1) + 1 = n + 1 - (i + 1) := by omega
      rw [this]
    · have hk0 : k = 0 := by omega
      subst hk0
      simp
  rw [hcongr]
  have hr := sum_reflect (fun m => choose m k) (n + 1) (n - k + 1) (by omega)
  have hrest : n + 1 - (n - k + 1) = k := by omega
  rw [hrest, sumLt_choose_below k k (Nat.le_refl k), Nat.add_zero] at hr
  exact hr

/-- **Main theorem** (cross-multiplied form of `E[N] = (n+1)/(k+1)`):
for `k ≤ n`,
  `(k+1) * Σ_{t=1}^{n-k+1} choose (n-t+1) k = (n+1) * choose n k`.
Here `choose (n-t+1) k = #{arrangements with N ≥ t}`, so dividing both sides by
`(k+1) * choose n k` gives `Σ_t P(N ≥ t) = E[N] = (n+1)/(k+1)`. -/
theorem expected_first_hit_cross (n k : Nat) (hk : k ≤ n) :
    (k + 1) * sum1 (fun t => choose (n - t + 1) k) (n - k + 1) = (n + 1) * choose n k := by
  rw [tail_sum_eq n k hk, hockey_stick k n, absorption n k]

/-- Positivity of the denominator: `choose n k > 0` for `k ≤ n`. -/
theorem choose_pos : ∀ {n k : Nat}, k ≤ n → 0 < choose n k
  | _, 0, _ => by simp
  | 0, _ + 1, h => absurd h (by omega)
  | n + 1, k + 1, h => by
      rw [choose_succ_succ]
      have := choose_pos (n := n) (k := k) (by omega)
      omega

/-- Small sanity checks (fully evaluated by the kernel). -/
example : choose 5 2 = 10 := by decide
example : (2 + 1) * sum1 (fun t => choose (6 - t + 1) 2) (6 - 2 + 1) = (6 + 1) * choose 6 2 := by
  decide

/-- The concrete instance n = 4132, k = 41 is a direct corollary. -/
example : (41 + 1) * sum1 (fun t => choose (4132 - t + 1) 41) (4132 - 41 + 1)
    = (4132 + 1) * choose 4132 41 :=
  expected_first_hit_cross 4132 41 (by decide)

end ENRandom

#print axioms ENRandom.expected_first_hit_cross
