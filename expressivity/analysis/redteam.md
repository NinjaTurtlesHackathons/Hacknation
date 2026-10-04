# Red-team report: verifier of the domain `expressivity`

Scope: `expressivity/domain.py` (`check`, `consistent`, `selftest`, `describe`), `realisation.py`, `algebra.py`, `reps.py`,
`chartab.py`, `gap_oracle.py`, `groups.py`. Read and execute only; no source file was modified.
Scripts: `expressivity/analysis/redteam/tN_*.py`. Each one's output is saved next to it as `tN_*.out`. Run them with
`python3 -m expressivity.analysis.redteam.tN_name` from the repo root.
Self-test at the start: 40/40 passed.

## 1 Pre-mortem: "a certified statement was false. Why?"

Ranked by prior likelihood before testing (the verdict after testing is in brackets).

1. **The group name does not denote the group it claims to.** `describe()` prints the claim's string (`S1`, `D2`), while
   `check()` computes on whatever `get_group` builds for that string. **[CONFIRMED: BUG 1]**
2. **The published sentence says more than the check proves.** For example "necessary for one layer" without the
   finite-state hypothesis that the lemmas need. **[CONFIRMED: BUG 2]**
3. **The answer text contradicts the certificate, but the checks pass.** `consistent()` uses keyword and regex heuristics and
   never checks whether a check is relevant to the question. **[CONFIRMED: BUG 3]**
4. **The closure can be fooled.** Possible routes: non-canonical `mkey` (one matrix with two keys, so an inconsistency is
   never seen), `mkey` collisions across fields, singular matrices, or an invariant form that only holds under right
   multiplication. **[NOT FOUND: 15,556 differential claims, 0 disagreements]**
5. **The field arithmetic is unsound.** Possible routes: a wrong minimal polynomial for large N (mpmath at 80 digits), wrong
   inverses, a wrong sign decision in the positive-definiteness check. **[NOT FOUND: wrong polynomials are refused, never
   accepted silently]**
6. **The numerical character table is wrong.** Possible routes: Frobenius–Schur pairing, kernel test, integrality margin.
   And GAP may be silently absent. **[TABLES CORRECT on 31 named + 319 SmallGroups; silent GAP fallback CONFIRMED:
   WEAKNESS]**
7. **The branch and bound in `minimise` is not exact.** **[NOT FOUND: equals brute force on every case]**
8. **Lemma L4 or L5 is false in the model actually defined** (affine input term B(s), generalised beta in [0,2], matrix
   states, non-invertible transitions). **[NOT FOUND for the finite-state model, by proof sketch below. FALSE without
   finite-state, which feeds BUG 2]**
9. **Cartan–Dieudonné proves less than claimed.** Possible routes: the factors are not genuine reflections, the factor count
   differs from the rank, or the form P is not positive definite. **[NOT FOUND]**
10. **Named alphabets depend on the hidden permutation representation**, so "h*(G, gens)" is not a statement about G.
    **[CONFIRMED: WEAKNESS]**

## 2 Tests

### T1 Group names (t1_group_names)
| probe | result | verdict |
|---|---|---|
| order and abelianness of every name GROUP_RE admits, compared with textbook formulas | `S1` has order 2 (should be 1, trivial). `D1` has order 1 (should be 2). `D2` has order 2 (should be 4, Klein four). `Z0` and `Z0xZ3` are nonsense names that are accepted. | **BUG** |
| `{"typ":"hstar_value","group":"S1","alphabet":"all","value":1}` | PASSES. Published: "h*(S1, all) = 1: exactly 1 Householder reflections per token are necessary and sufficient ..." S1 is trivial. | **BUG** |
| `{"typ":"diag_realisable","family":"diag_pos","group":"S1","alphabet":"all","value":false}` | PASSES. Published: "A one-layer diag_pos recurrence cannot realise the word problem of S1". The trivial group is realisable. | **BUG** |
| `{"typ":"h_faithful","group":"D2","alphabet":"all","value":1}` | PASSES (own = GAP = 1, because GAP gets the same wrong group). Published "h(D2, all) = 1". For D2 = V4 the true value is 2, and the verifier itself certifies `h_faithful Z2xZ2 all = 2`. The paper would contain two contradictory statements about isomorphic groups. | **BUG** |
| `{"typ":"hstar_value","group":"D2","alphabet":"all","value":1}` | Passes. True for V4 as well (count cover), so harmless by luck. | WEAKNESS |
| Q8 table, Z_n, ZaxZb, Z2^k, S3–S5, A3–A5, D3–D8 | correct | OK |

Root cause, in `groups.py`: S<n> uses `_cyclic(2)` for every n <= 2. For D<n> with n <= 2, the "reflection" `(-i) % n` is the
identity.

### T2 Field arithmetic (t2_field)
| probe | result | verdict |
|---|---|---|
| `minpoly_2cos(N)` vs exact integer construction (cyclotomic polynomial plus Dickson substitution), N = 3..999 | 0 wrong. 511 values of N >= 257 are refused with "not integral". Sound, but Z<n> for n >= 257 cannot be used. | OK (WEAKNESS: refusal; and the check `abs(a-n) > 1e-40` is vacuous once coefficients exceed 10^80) |
| 420 random triples in K_N (N up to 60): inverse, distributivity, numerical agreement, `==` vs numerical zero | 0 failures | OK |
| mkey canonicality (the same number reached by different routes) | 0 failures | OK |
| cross-field: c_5 in K_5 and c_8 in K_8 have the same mkey `((0,1),)` but are different numbers. c_5 and embed(c_5, K_10) are the same number but compare unequal. | Not reachable: mixed-field arithmetic raises TypeError, and every construction uses a single field | WEAKNESS (latent) |
| `sign()` on 1e-7 ... 1e-39 | correct. Refuses at 1e-46. | OK |

### T3 Realisation verify vs an independent implementation (t3_realisation)
| probe | result | verdict |
|---|---|---|
| 189 library constructions (4 constructions x 3 twists x 28 (G, Sigma)) recomputed with numpy (closure, labels, onto, invariant form, SVD rank), k = 0..4 | 0 disagreements, including |H| and max rank | OK |
| exhaustive: every assignment of signed permutation matrices (dim <= 3) to the letters of 13 small (G, Sigma), as `realisation_matrices`, k = 1, 2 | 15,556 claims, 731 accepted, 0 disagreements | OK |
| singular idempotent, projection, order-2 matrix for a Z4 generator | refused (inconsistent) | OK |
| unipotent `[[1,1],[0,1]]` | refused at the cap (3 s) | OK |
| `{"typ":"realisation_matrices","group":"Z2","alphabet":"all","k":1,"matrices":[[["1/2"]]]}` | refused, but only after **125 s**: denominators grow to 2^60000 before the cap is reached | WEAKNESS (DoS) |
| non-orthogonal finite matrices (oblique reflection, oblique order 3) | accepted with the correct rank, because P is found by averaging | OK |
| claim type `realisation_matrices` | accepted by `check()` but **not documented** in `claim_doc` | WEAKNESS |

### T4 / T11 Character tables vs GAP, minimise vs brute force (t4_chartab, t11_chartab_sg)
| probe | result | verdict |
|---|---|---|
| 31 groups (Z2..Z12, D3..D8, S3..S5, A4, A5, Q8, Z2^2..Z2^4, Z2xZ4, Z2xZ6, Z3xZ3, Z4xZ4, Z3xZ6): element-wise multiset of (codim, mult(-1), in-kernel), irrep (deg, FS) signature, h for every alphabet | 0 mismatches | OK |
| `minimise` vs exhaustive subset search, on both the own table and the GAP table | identical on every case | OK |
| all 319 SmallGroups in results/smallgroups.json (orders <= 63), alphabets all/gens/involutions, own h vs GAP h | 708 pairs, 0 disagreements, 0 numerical refusals | OK |
| GAP unavailable (`GAP` set to a missing path): `{"typ":"h_faithful","group":"Q8","alphabet":"all","value":4}` | passes on numerics alone. `describe()` still says "(character tables, own and GAP)". | WEAKNESS |

### T5 Published sentence of hstar_value without finite-state (t5_infinite_state)
| probe | result | verdict |
|---|---|---|
| Z3 'all' with A = I (zero reflections) and B(s) in {1, 2}, readout h mod 3 | exact on every word up to length 10 | shows the sentence is false |
| S3 'all' and A5 'cycles5' with a 1-D diagonal A = 1/K in [0,1] (= diag_pos = one generalised Householder) and B(s) = index | readout is a well-defined function on 97,656 and 346,201 exact rational states, so the task is solved with k = 1 | shows the sentence is false |
| `{"typ":"hstar_value","group":"A5","alphabet":"all","value":2}` (in the self-test) | PASSES. Published: "exactly 2 Householder reflections per token are necessary and sufficient for one layer". Necessity holds only for finite-state realisations. The `diag_realisable` sentence carries "(finite-state)"; this one does not. | **BUG** (wording) |

### T6 consistent() loopholes (t6_consistent)
Each answer below passes every check and `consistent()`, so `solve_cascade` returns it as the verified answer.

| answer (all checks pass) | contradiction | verdict |
|---|---|---|
| `{"antwort":"h*(A5, all) = 1, a single reflection suffices","pruefungen":[{"typ":"hstar_lower","group":"A5","alphabet":"all","k":2}]}` | the text contradicts its own certificate. Numbers in the text are never checked, only `zahl`. | **BUG** |
| `{"antwort":"No, DeltaNet (HH_1) cannot track S3 with transpositions","pruefungen":[{"typ":"hstar_lower","group":"S3","alphabet":"transpositions","k":0}]}` | false (h* = 1). The trivial bound k = 0 counts as an "impossibility certificate". | **BUG** |
| `{"antwort":"h*(S5, all) = 4","zahl":4,"pruefungen":[{"typ":"h_faithful","group":"S5","alphabet":"all","value":4}]}` | h is confused with h* (only 2 <= h* <= 4 is known) | **BUG** |
| `{"antwort":"Yes, A5 with all letters needs only 1 reflection","zahl":1,"pruefungen":[{"typ":"hstar_value","group":"A5","alphabet":"involutions","value":1}]}` | the check is about a different alphabet | **BUG** |
| number words ("equals one"), negation forms that the regex misses ("does not hold"), `zahl: true` coerced to 1 | accepted | WEAKNESS |

Impact: the paper sentence comes from `describe(first check)`, which stays true. The agent's answer, the vote clusters and
the discovery accuracy all use the text that was never checked.

### T7 Malformed inputs and time limits (t7_malformed)
| probe | result | verdict |
|---|---|---|
| k = 1e9, k = -1, k = 2.0, k = true, bad alphabet, `list:` alphabet, leading space, trailing newline, `Tolerance` (case) | refused cleanly | OK |
| `tol_rel`, `max_k` keys | ignored (not in FORBIDDEN_KEYS), so harmless, but the rule "claims may not carry limits" is only a name list | WEAKNESS |
| `{"typ":"hstar_value","group":"Z2^4","alphabet":"all","value":1}` | **> 90 s, killed** (search_upper builds a 15-letter count cover with a 15x15 closure of 2^15 elements) | WEAKNESS (DoS) |
| `{"typ":"realisation","group":"Z2^6","alphabet":"all","k":1,"construction":"count"}` | > 90 s, killed | WEAKNESS (DoS) |
| SIGALRM inside `check()` | swallowed by `except Exception` in verify/check. `search_upper` then continues with the next construction, so the verifier has no time limit that works. | WEAKNESS |
| `Z257` planar | refused (minpoly) | OK |
| describe text with k = 16 | true but vacuous ("at most 16") | OK |

### T8 Cartan–Dieudonné certificate (t8_cartan)
| probe | result | verdict |
|---|---|---|
| 8 certified realisations, every letter. Each factor checked for R^2 = I, rank(R-I) = 1, R^T P R = P, det = -1. Product = M. #factors = rank(M-I). In a Cholesky P-orthonormal basis, each factor is I - 2uu^T with unit u. | 0 failures. The greedy algorithm provably uses exactly rank(M-I) steps (Fix grows by x each step, since <y, Mx-x>_P = 0 for y in Fix M). P always contains I^T I, so it is positive definite. | OK |

### T9 / T10 SmallGroups and alphabets (t9_smallgroups, t10_alphabets)
| probe | result | verdict |
|---|---|---|
| IdGroup of all 319 entries in smallgroups.json (that file appeared during this session) | 319/319 correct | OK |
| `gens`, `transpositions`, `cycles3` on isomorphic groups | D4 `gens` = {order 2, order 4}, but SG8_3 (= D4) `gens` = three involutions. Z2^2 `transpositions` = 2 letters, h = 1. These alphabets are artefacts of the stored permutation action and generators, so "h*(D4, gens)" has no meaning that does not depend on the representation. | WEAKNESS |

### Lemma audit (no script; proof sketches)
* **L4** (a letter of order >= 3 forces h* >= 2). Inside the h* definition: rank(rho(t)-I) = 1 and finite order mean the only
  eigenvalue different from 1 is real, so it is -1 and t has order 2. Then pi(t) = s has order <= 2. In the operational model
  (finite state, h -> (I - beta uu^T)h + B, beta in [0,2], matrix states allowed): for beta in (0,2) minus {1}, the map is
  injective on the finite reachable set R. It is a contraction in direction u and a translation on u-perp, so it is the
  identity on R. beta = 1 is idempotent, so f_s f_s = f_s and therefore s = e. beta = 2 is an involution. So s^2 = e. **Sound
  (finite-state only).**
* **L5** (diagonal families). Coordinate maps on a finite invariant set are identity, involution or constant (diag_pm).
  Hence f_s^3 = f_s, so s^2 = e. G is a homomorphic image of the transition monoid, therefore an image of a maximal subgroup
  of a product of {id, sigma_i, constants}, therefore an elementary abelian 2-group. cdiag: maximal subgroups are finite
  subgroups of Aff(C), which are abelian. diag_pos: every map is idempotent. Non-invertible transitions and B(s) are covered.
  **Sound for finite-state.** The `describe` sentence carries "(finite-state)".

## 3 Assumptions every team makes that break here

| # | assumption | breaks? | testable |
|---|---|---|---|
| A1 | "A name the regex accepts denotes the textbook group" (S1, D1, D2) | yes (T1) | yes, broken |
| A2 | "Exact arithmetic plus passing check means the published sentence is true". The sentence also encodes a model (finite state) that the check never sees. | yes (T5) | yes, broken |
| A3 | "Checks passed means the answer is right". consistent() is a heuristic, and checks need not be about the question. | yes (T6) | yes, broken |
| A4 | "GAP cross-checks every h_faithful". The fallback is silent when GAP is missing, and the published text still cites GAP. | yes (T7) | yes, broken |
| A5 | "Alphabet names are properties of the abstract group" | yes (T10) | yes, broken |
| A6 | "The verifier always terminates fast". It has no wall-clock budget, and alarms are swallowed. | yes (T3, T7) | yes, broken |
| A7 | "Isomorphic names give the same certified values" (D2 vs Z2xZ2: h = 1 vs 2) | yes (T1) | yes, broken |
| A8 | "Numerical character tables need GAP to be trusted" | no: 0/739 disagreements | tested, holds |
| A9 | "The certified lower bound covers what is asked". It caps at 2, so h*(S5, all) or Q8-type questions with values >= 3 can never be settled. That is a limitation, not a falsehood. | n/a | yes |
| A10 | "The iff-theorem (finite-state HH_k iff k >= h*) is proven". Only sufficiency (constructive) and necessity for k <= 2 (L4) are used, and both hold. Larger-k necessity ("compression") is never exercised by a check. | holds for what is used | partly |

## 4 Recommended fixes (priority order)

1. **Group names (BUG 1).** In GROUP_RE, restrict `S[3-5]`, `A[3-5]` and `D([3-9]|1\d)`, and reject `Z0`. Or fix `get_group`:
   S1 = trivial, D1 = Z2, D2 = V4. Add a check that `G.order` equals the order the name implies before every check. Add
   self-test entries: `hstar_value S1 all 1` must be False, and `h_faithful D2 all 1` must be False.
2. **describe() for hstar_value (BUG 2).** Say "... are necessary (for finite-state one-layer realisations, Lemma L4) and
   sufficient ...". Use the same qualifier everywhere "necessary" appears.
3. **consistent() (BUG 3).** Require that every number in the answer text (digits and number words) equals a certified value.
   Ignore `hstar_lower` with k = 0 (or k below the trivial bound) as an impossibility certificate. Require the checks to name
   the group/alphabet the question is about (pass the question's (G, Sigma) in). Do not accept `h_faithful` as backing a
   statement about h*. Reject a boolean `zahl`.
4. **GAP fallback.** If GAP is unavailable, either refuse `h_faithful` or have `describe()` say "own numerical table only".
   Keep the evidence (`gap` = None) on the claim so that describe can tell.
5. **Time budget.** Run `check()` in a child process with a hard wall-clock limit. Bound fraction height in
   `realisation_matrices` (for example, refuse numerators or denominators above 10^6 and reject any matrix with a
   non-integral power). In search_upper, skip `count` when |Sigma| is large (2^|Sigma| > cap).
6. **Alphabets.** Restrict `transpositions`/`cycles3`/`cycles5` to S_n/A_n, and make `gens` print its letters (orders) in
   `describe()`. Or have describe print the alphabet as a list of element orders or class labels.
7. **Document `realisation_matrices`** in claim_doc. Add `tol_*`, `max_*` and `cap_*` prefixes to the forbidden-key rule
   (prefix match rather than an exact name list).
8. Latent: make `mkey` include the field (`x.F.N`), and make `Elt.__eq__` embed into a common field instead of returning
   False. Make the minpoly check fail if dps is not larger than the coefficient magnitude (it is vacuous once coefficients
   exceed 10^80).
