-- Core-only exact arithmetic anchor; no numerical ML claim follows from this.
def totalAbsoluteError (xs : List Int) : Nat := (xs.map Int.natAbs).sum

theorem totalAbsoluteError_nil : totalAbsoluteError [] = 0 := rfl

theorem totalAbsoluteError_cons (x : Int) (xs : List Int) :
    totalAbsoluteError (x :: xs) = x.natAbs + totalAbsoluteError xs := rfl

theorem totalAbsoluteError_zero_iff (xs : List Int) :
    totalAbsoluteError xs = 0 ↔ ∀ x ∈ xs, x = 0 := by
  induction xs with
  | nil => simp [totalAbsoluteError]
  | cons x xs ih =>
    simp only [totalAbsoluteError_cons, Nat.add_eq_zero_iff, Int.natAbs_eq_zero]
    constructor
    · intro h y hy
      rcases List.mem_cons.mp hy with hxy | hys
      · exact hxy ▸ h.1
      · exact ih.mp h.2 y hys
    · intro h
      exact ⟨h x (by simp), ih.mpr (fun y hy => h y (by simp [hy]))⟩
#print axioms totalAbsoluteError_zero_iff
