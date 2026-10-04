# Red-team report: hand proofs in `expressivity/theory.md`

Scope: L2 (compression), L3 (sufficiency), Theorem 1, L5 (diagonal families), L7 (abelian groups). L1 and L4 are
checked only for whether their Lean statements match the text. No existing file was modified.
New scripts (run from the repo root as `python3 -m expressivity.analysis.redteam.<name>`; output saved next to each one as `.out`):

- `t12_compression.py`: runs the L2 construction exactly over Q on four adversarial realisations. All intermediate claims
  are asserted.
- `t13_counterexample_search.py`: exhaustive search for a rank-1 affine realisation of Z3. Also runs the complex control.
- `t14_zero_init.py`: tests L3 under the trained architecture's convention S_0 = 0.

## 1 Verdicts

| item | verdict | one-line reason |
|---|---|---|
| L1 (Lean) | VALID; the statement matches | `rank_prod_sub_one_le` works over any field and any list; `deltaproduct_rank_le` holds for any beta and any u (stronger than the text). The axioms are only propext, Classical.choice and Quot.sound (`check.out`); there is no `sorry`. |
| L4 (Lean) | VALID; the statement matches; **the status label is wrong** | `no_single_householder_lift`: an injective `rho : H →* Matrix n n ℝ` with H finite, any hom pi, and pi t = s with ord s ≥ 3 gives ¬ rank(rho t − 1) ≤ 1. theory.md still tags L4 `[hand]`; it should be `[Lean]`. |
| L2 | VALID WITH FIX (wording only) | The core argument is correct, including for singular A, affine B, matrix states and arbitrary readout. Fixes needed: h_0 ∈ Q, the empty word, the field (real versus complex rank), and that G is finite in the "onto" step. |
| L3 | VALID WITH FIX | Correct as stated (generic h_0, B = 0). It does not apply verbatim to the implemented convention S_0 = 0; a token-local fix exists and was verified (§2.3). |
| Theorem 1 | VALID WITH FIX | The "iff" is exactly right. It needs: real states, beta allowed to reach 2, and the hypotheses of L3 and L2 stated together. Whether the lifts generate H does not matter (§2.4). |
| L5 | VALID WITH FIX | The proofs are right for the *closed* families [0,1], [−1,1] and \|lambda\| ≤ 1. The cdiag case needs L2 over C. All three statements fail for open parameterisations such as tanh (§2.5). |
| L7 | VALID WITH FIX | pi is a homomorphism and the dimension count is right. Two fixes: exclude G = 1, and the paper's "needs a dimension" must read "uses". |

## 2 Details per lemma

### 2.1 L2 (compression)

I checked every step and found each of them correct:

- psi is a well-defined homomorphism.
- K is the minimal ideal, and eTe is a group for an idempotent e ∈ K.
- psi(e) = 1, so psi maps Gamma onto G, and Gamma' maps onto G.
- Gamma acts bijectively on Q_e. The restriction to W = aff(Q_e) is well defined and faithful, because t = ete is determined on Q_e.
- The linear part is faithful, because a translation of finite order is trivial in characteristic 0.
- A(u) = I on U. The rank bound holds because rank(A(u)(A(s) − I)|_U) ≤ rank(A(s) − I).
- The column-space reduction to C is valid: C is invariant, A(u) = I on C, and an element acts trivially on U iff it acts trivially on C.

The column-space reduction is genuinely needed. On U the operator I_m ⊗ (A(s) − I) can have rank up to k·m. t12 E2
(3x2 matrix state) has dim U = 4 and dim C = 2, and the rank bound on U alone would be twice as large.

Numerical stress test (t12, exact): the construction succeeded with every assertion passing on all four instances:

- E1: S3/transpositions with an extra singular block (A = 0, B one-hot), a beta = 1 projection block, and affine terms. T is not a group (|T| = 19, |eTe| = 6).
- E2: matrix state, where no single column determines the state.
- E3: Z3 with an affine term, so W does not pass through 0.
- E4: a cover S3 × Z2 lifting each transposition to −P, plus a singular row. Compressed rank 2 ≤ 3.

Required wording fixes:

1. Define Q = {h_0} ∪ {reachable states}. The step "h_0 ∈ Q" uses this.
2. The readout is only required for t ≥ 1, so phi(h_0) is unconstrained. Either work with the semigroup of *nonempty*
   words (the minimal-ideal argument is unchanged, and u is then nonempty), or note this: if alpha_w|Q = id for a nonempty w,
   then for every nonempty v the word "w then v" has alpha = alpha_v on Q. So g(v)g(w) = g(v), and therefore g(w) = e. Hence psi(id) = e is consistent.
3. "onto G": positive words suffice only because G is finite. Say so.
4. Field. The proof works verbatim over C, with rank taken over C. But Theorem 1 and h* are about real states. With
   complex states, Z3 is realised by the 1x1 rotation e^{2πi/3}, whose complex rank(A − I) is 1, while h*(Z3) = 2 (t13).
   Realification gives h* ≤ 2k for complex-valued realisations. Add a remark: "(iv) The proof holds over C with complex
   rank; for complex states it gives the analogous complex invariant, and realification yields h* ≤ 2k."
5. Optional strengthening: the readout may also depend on the current token, phi(h_t, s_t). psi stays well defined:
   if alpha_w|Q = alpha_{w'}|Q, then for every nonempty v, g(v)g(w) = g(v)g(w'), so the elements cancel in G. This
   matters for the paper because the real models read out S_t q_t, where q_t depends on x_t.
6. Add a one-line edge case: if G ≠ 1 then dim C ≥ 1. If G = 1 the claim h* = 0 is trivial.

### 2.2 Lean statements (L1, L4)

They match theory.md and are slightly stronger: L1 holds over any field, and the hom pi in L4 need not be surjective.
L4's Lean statement does not mention h*, because h* is not defined in Lean. The step from "no rank-≤1 lift" to h* ≥ 2
also needs that rank 0 is impossible, which is trivial (t_s = 1 ⇒ s = e). Fix: change the theory.md heading
`## L4 (order lemma) [hand]` to `[Lean]`, and name the theorems.

### 2.3 L3 (sufficiency)

The proof is correct: averaging gives an invariant inner product; Scherk's theorem gives *exactly* rank(M − I) reflections
for an orthogonal M on a definite space; padding uses beta = 0; a generic h_0 avoids the finitely many proper subspaces
Fix rho(x). Generation of H by the t_s is not used.

Gap with respect to the architecture that is actually trained: `train.py` uses S_0 = 0 and a right action
S ← S(I − βkk^T) + βvk^T. With h_0 = 0 and B = 0, L3's realisation is constant.

Fix, which stays token-local: pick a generic row c and set v_j = −(c k_j) for every factor. Then S_t + c = c·rho(x_t), so S_t
determines x_t. t14 verified this exactly for S5/transpositions with one reflection per token: 120 reachable states, and the
readout is consistent.

Also state that the reflections require beta = 2 exactly and unit keys.

### 2.4 Theorem 1

- (⇒) L2 applies to the rank class, which contains DeltaProduct_k by L1. (⇐) L3 produces DeltaProduct_k with beta ∈ {0, 2}.
  So the iff holds simultaneously for "rank(A(s) − I) ≤ k" and for "k Householder factors with beta ∈ [0, 2]".
- **Generating lifts.** Sufficiency does not need them. Necessity produces them: the t_s = x_s generate Gamma' by
  definition. Any cover can also be replaced by the subgroup generated by the lifts; rho stays faithful, and pi stays onto
  because Sigma generates G. So h* is the same with or without "generating". The word "surjective" in the definition is
  likewise redundant (it follows from pi(t_s) = s). The definition is consistent with the iff.
- **Counterexample attempts** (§3) found nothing.
- **Hypotheses the statement must carry:**
  - real state space;
  - finite reachable set;
  - transitions depend on the current token only (no short convolution);
  - one layer;
  - readout a function of h_t (or of (h_t, s_t), see §2.1 item 5);
  - beta allowed to equal 2.
- **Open parameterisations make the theorem vacuous.** If every factor has beta ∈ [0, 2) (for example `beta_mode=sigmoid`,
  beta = 2σ(z) ∈ (0, 2)), then *no* nontrivial G has an exact finite-state realisation, for any k.

  Proof: each factor F = I − βkk^T has ‖F‖ ≤ 1, and ‖Fy‖ = ‖y‖ iff Fy = y. On C the compressed map M = A(u)A(s) has finite
  order N, so ‖y‖ = ‖M^N y‖ ≤ ‖My‖ ≤ ‖y‖. Hence every factor along the chain fixes its input, so M|_C = I and x_s = e. This
  gives s = psi(x_s) = e, a contradiction.

  The preregistration uses `clamp2` (beta reaches 0 and 2 exactly), so it is covered. Any sigmoid-mode result must be
  described as approximate.

### 2.5 L5 (diagonal families)

- Commutation: A(u)A(s) is diagonal, so the restrictions to the common invariant subspace C commute. Gamma' ≅ lambda'(Gamma')
  is therefore abelian, and so is G. ✓
- Real entries: the restriction of a diagonalisable operator to an invariant subspace is diagonalisable, with eigenvalues
  among the diagonal entries. Finite order then forces ±1, so Gamma' is generated by commuting involutions and G is
  elementary abelian 2. ✓ Wording fix: it is the *restriction* D|_C that has finite order, not D. The entries of A(s)
  themselves are unrestricted reals here.
- [0, 1]: the eigenvalues of the restriction lie in [0, 1], and the only root of unity there is 1, so the restriction is
  the identity and G = 1. ✓
- Converse: the count cover with unit-modulus complex entries gives abelian groups, and ±1 coordinates give elementary
  abelian 2-groups. ✓ So "cdiag with |λ| ≤ 1 iff abelian" is right, because |λ| = 1 is allowed.
- Gaps:
  - (a) The cdiag necessity uses L2 over C. State this, since the Setting is real.
  - (b) The family must be **closed**. With the open sets used in `train.py` the results change: diag_pm uses
    tanh ∈ (−1, 1), cdiag with |λ| < 1 would behave the same way, and diag_pos uses sigmoid ∈ (0, 1). The compressed map on
    C is then a strict contraction and cannot have finite order unless C = 0. Only G = 1 is exactly realisable.
    The predictions in `predict.py`/`prereg.md` (diag_pm learns Z2^3) are therefore about approximation in the closed-family
    limit, not exact realisability.
  - (c) "Diagonal" means diagonal on vec(h) (Mamba-style elementwise decay). That is covered by flattening (m = 1), not
    by the left-action form. Say so.
  - (d) G = 1 has Sigma = ∅. "diag_pos iff G = 1" really says that no nontrivial group is realisable. Fine, but phrase it so.

### 2.6 L7 (abelian groups)

- pi: ∏ Z_{ord s} → G with t_s ↦ s is a homomorphism because the images commute and s^{ord s} = e, by the universal
  property of the direct product of cyclic groups. ✓
- The direct sum of faithful blocks is faithful on the product. rho(t_s) − I is supported on its own block, with rank 1
  for a reflection and 2 for a rotation by 2π/n, n ≥ 3. ✓
- Dimension = (number of involution letters) + 2·(number of others). ✓ Certified sizes: Z3/all gives |H| = 9, and Z2^3/all
  (7 letters) gives 2^7 = 128. ✓
- Fixes:
  - (a) Add "G ≠ 1". For G = 1, Sigma = ∅, the statement as written gives h* = 1 ("every letter is an involution" holds
    vacuously), but h* = 0.
  - (b) The count cover dimension is an upper bound and is not minimal. For example Z3/all has a 2-dim realisation (the rotation) against
    the cover's 4. The paper's C-L7 phrase "which needs a dimension equal to" is false as a necessity claim; change it to "uses".
- Side check of C3: h(Z2^k, all) = k holds. Any k-dim binary code has an information set, and the sum of the
  systematic generator rows has weight ≥ k; the basis characters attain k.

## 3 Counterexample attempts against Theorem 1

1. **Rank-1 affine letter for Z3** (t13, exhaustive): A = I + v wᵀ, with b and h_0 from small rational grids.
   - d = 2: 451,584 configurations.
   - d = 3: 146,016 configurations.
   - Realisations found: 0, consistent with L2 + L4.
   - Limitation: only small grids and a single letter.
2. **Singular, affine and matrix-state realisations** (t12): compression always returned a faithful representation with the rank bound.
3. **Complex states** (t13): Z3 is realised with complex rank 1 < h*(Z3) = 2. This is not a counterexample to the theorem as
   stated (real states), but it is one for any reading that uses complex rank. The paper must not apply h* to complex
   (cdiag) models with complex rank.
4. **Open beta range**: this kills the iff for every nontrivial G (§2.4). It is not a counterexample to the stated
   theorem (which assumes beta ∈ [0, 2]), but it is a scope trap for the experiments.
5. **Token-dependent readout and zero initial state**: neither breaks the theorem. See §2.1 item 5 and §2.3.

No counterexample to Theorem 1 as stated (real, finite-state, token-local, one layer, arbitrary readout, beta ∈ [0, 2]) was found.

## 4 Precise wording changes

### theory.md

1. Setting:
   - "the set Q of reachable states" → "Q = {h_0} ∪ {h_t : all words, t ≥ 1}". Add "phi(h_t) = g_t for t ≥ 1".
   - Add "all spaces are real; the field matters (see L2 remark iv)".
   - Add "Householder factors are I − βuuᵀ with ‖u‖ = 1 and β ∈ [0, 2] (closed)".
2. Definition of h*: optionally drop "surjective" and add "(requiring the t_s to generate H does not change h*: restrict to ⟨t_s⟩)".
3. L2 proof:
   - Use the semigroup of nonempty words, or add the psi(id) = e argument.
   - Add "(G finite, so positive words reach all of G)".
   - Add remark (iv): "the proof is valid over C with complex rank; for real-valued h* a complex realisation gives h* ≤ 2k".
   - Add remark (v): "the readout may depend on (h_t, s_t)".
4. L3: add "If the architecture fixes h_0 = 0 (DeltaNet S_0 = 0), take a generic c and v_j = −c k_j; then S_t + c = c·rho(x_t)".
   Also add "β = 2 exactly is required".
5. Theorem 1: "For every finite G and generating Sigma ⊆ G∖{e}, a real finite-state one-layer realisation with token-local
   transitions satisfying rank(A(s) − I) ≤ k (equivalently, by L1 + L3, a product of k Householder factors with β ∈ [0, 2])
   exists iff k ≥ h*(G, Sigma)."
   Add a corollary: "If β is confined to [0, 2), no nontrivial group is exactly realisable."
6. L4 heading: `[hand]` → `[Lean]` (`sq_eq_one_of_rank_le_one_of_pow_eq_one`, `no_single_householder_lift`).
7. L5:
   - "each compressed map is a restriction of a real diagonal matrix of finite order" → "each compressed map is the
     restriction of a real diagonal matrix to an invariant subspace, and this restriction has finite order".
   - Add "(the complex case uses L2 over C)".
   - Add "the families are the closed sets [0,1], [−1,1], |λ| ≤ 1; for open sets (sigmoid, tanh, |λ| < 1) only G = 1 is
     exactly realisable".
   - Add "diagonal acts on vec(h)".
8. L7: "For abelian G ≠ 1". Change "Upper bound (count cover)" to "... of dimension #involutions + 2·#others (not minimal in general)".

### Paper (`write_paper.py` claims)

1. C-L2:
   - Keep level `hypothesis`.
   - The sentence "reviewed by an independent red-team agent, which found it valid ..." is acceptable only with "after
     wording fixes; see expressivity/analysis/redteam_theory.md".
   - Add "real-valued states".
2. C-L3: add "beta = 2 exactly; with zero initial state the input term v = −c k supplies the generic offset".
3. C-thm1:
   - Add "real", "transitions depending only on the current token", and "beta in [0, 2] including the endpoint 2".
   - Add "requiring the lifts to generate H does not change h*".
4. C-L5:
   - Add "with closed parameter sets; under the open parameterisations used for training (sigmoid, tanh) no nontrivial
     group is exactly realisable, so the trained-model predictions concern approximation".
   - Specify "complex diagonal with |lambda| <= 1".
5. C-L7: "which needs a dimension equal to" → "which uses a dimension equal to (an upper bound, not the minimum)". Add "for G nontrivial".
6. C-L4 / ledger: present L4 as machine-checked consistently. theory.md currently says `[hand]`.
7. Any sentence that applies h* to complex (cdiag) models must state that h* counts real rank. A 1x1 complex rotation
   (complex rank 1) realises Z3, while h*(Z3) = 2.
