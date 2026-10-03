# Red team report: `algo_efficiency` verifier (`DOMAIN.check`)

Scope: `algo_efficiency/{spec,polyexp,kv,domain}.py` and `results/certified.json`. Read and execute only; no source file was changed.
All scripts live in `algo_efficiency/analysis/redteam/`. Run them from the worktree root as `python -m algo_efficiency.analysis.redteam.<name>`.
Each script's output is saved next to it as `<name>.out`. Every script finished in under 1 minute.

## 1. Pre-mortem: "A referee tore the paper apart. Why?"

1. **A "rigorous" interval certificate isn't rigorous.** The last step in `certify_lower` and `rigorous_sup` turns the exact interval endpoint into a 53-bit float with round-to-nearest. A lower bound can be rounded up, and an upper bound can be rounded down. **This is confirmed: a false claim passes (T3/T4).**
2. **Inputs outside the model are accepted, and `describe()` prints nonsense as a verified sentence.** Examples: a negative `lambda`, a `k` that the rule ignores, and non-integer degrees or draft lengths that `int()` silently truncates. **Confirmed (T1).**
3. **"Acceptance" means different things for different rules.** For `scaled` with lambda < 1, the verifier reports P(accept flag). That is not P(emitted token = draft), which is the module's own definition of acceptance. **Confirmed (T2c).**
4. **The optimal multi-draft value is wrong** because of the set-vs-tuple reduction, `wor` handling, or zeros in q. **Refuted (T2a/b).**
5. **The draft-length argmax is wrong** at ties or because the tail certificate fails. **Refuted (T7).**
6. **KV findings are overfitted to the 20 public verifier seeds and to a scan over (n, budget).** There is no correction for multiple testing per claim, and `p = 0.0` gets printed. **Confirmed as a weakness (T5).**
7. **The "oracle is a lower bound" wording.** This is not provable (top-mass selection isn't error-optimal). It held empirically on 160/160 seed-policy pairs (T5b), but the verifier never checks it.
8. **Overstated wording.** `polymethod_rank` says the rank is "exactly C(h+d,d)". The construction only gives rank <= C(h+d,d). The verifier certifies d*, not the matrix rank.
9. **Contradiction detection is purely syntactic.** `widerspricht` compares claims with `json.dumps`, so "1/2" and "0.5" (or `B: 1` and `B: "1"`) are never compared.
10. **Upper certificates are incomplete for large B.** For B=32, d=48 (absolute error), the certified bound is 0.494 while the Remez level is 0.048. True claims fail, which limits the tables but is not a soundness problem.

## 2. Tests

### T1: malformed and out-of-model inputs (`t1_inputs.py`)
| Probe | Result | Verdict |
|---|---|---|
| `scheme_acceptance`, rule `scaled`, lambda = -1, value "-1" | PASS. The sentence "accepts with probability exactly -1" is certified | **BUG** (lambda has no range check, so a negative "probability" passes; `unbiased: true` also passes) |
| `optimal_gamma` with gamma = 8.7 | PASS. The paper sentence reads "draft length 8.7 maximises the expected speedup" | **BUG** (`int()` truncates; `describe` prints the raw value) |
| `exp_min_degree` with d = 4.99; `multidraft_optimal` with k = 2.5; `rrs_iid` with k = 2.9 or k = True | all PASS | **BUG** (same mechanism; the printed statements are false) |
| rule `standard` with k = 4, 0 or -3 | PASS, printed as "rule standard with k = 4 accepts ..." | WEAKNESS (k is ignored for standard/scaled) |
| rule `standard` with lambda = 5, `unbiased` | PASS, printed as "(k = 1, lambda = 5) is lossless" | WEAKNESS (lambda is ignored but printed) |
| `"unbiased": "false"` (a string) | `bool("false")` is True. `describe` also says "lossless", so the printed sentence is true | WEAKNESS (type coercion; check and describe agree) |
| `Tolerance` written in a different case | rejected | OK |
| mode `"WOR"` | rejected | OK |
| `wor` with k > support, zeros in q, float probabilities | correct values (float parsed via `repr`) | OK |

### T2: speculative decoding against independent code (`t2_multidraft.py`)
- (a) I checked 250 random instances in both modes (500 pairs): V = 2..5, k = 1..4, 50% with zeros, masses up to 999:1, including k > support. `optimal_multidraft` matches exactly an independent exact cut, computed by enumerating draft tuples. It also matches a HiGHS LP over tuples to within 2.1e-15. **OK**
- (b) I wrote an independent exact implementation of RRS iid and wor that enumerates draw sequences. Output distribution and acceptance match on all 500 pairs. RRS never exceeds the optimum and is always lossless. **OK**
- (c) Scaled rule with p = q = (1/2, 1/2) and lambda = 1/2: the verifier's acceptance is 1/2, but P(output = draft) is 3/4. With lambda = 0, the verifier reports 0 while P(output = draft) is 3/10. The `scaled` value is therefore not comparable with `multidraft_optimal`, which uses P(output in drafts). **WEAKNESS** (a definition mismatch; the paper must say which definition it uses)

### T3: rounding window in the interval certificates (`t3_rounding.py`)
For each case I computed three things for the verifier's own Remez polynomial:
- the exact de la Vallee Poussin endpoint m;
- the value the verifier actually uses, `lower = mpf_to_frac(mp.mpf(m))`;
- the sup S at 60 digits (dense grid plus golden-section search).

Remez levels to 1e-17 to 1e-23 relative in many cases, which is far below the rounding error of +-1.1e-16. **In 4 of 12 cases, lower > S.** Those cases are (B,d) = (3,7) relative, (5,9) relative, (2,5) absolute and (4,8) absolute. A second example is in T6: B=32, d=0 reports a lower bound of exactly 1.0, although the true minimax error tanh(32) is below 1.

### T4: a rigorously false claim passes (`t4_false_lower.py`, `t4b_min_degree.py`)
In each of the 4 cases I set eps = (S + lower)/2. Then:
- `DOMAIN.check({"typ":"exp_degree","bound":"lower",...})` **passes**, certifying "no polynomial of degree d reaches error <= eps".
- A patched `rigorous_sup` proves the opposite: the verifier's own polynomial has sup <= eps, with U - eps of about -1e-21. The patch converts interval endpoints exactly (`_mpi_`), uses 60 digits and goes down to h = 2^-60.

**BUG (soundness).** It propagates: for B=3 with relative error, `exp_min_degree` d=8 and `polymethod_rank` C(24,8)=735471 both PASS, although the true d* is 7. `upper` at d=7 fails at the same eps, because S itself also rounds above eps.
- Exploiting this needs an eps chosen to within about 1e-17 relative. The **published table is not affected**: the smallest relative margin among the 15 degree entries in `certified.json` is 0.39% (B=16, eps=1e-2, d=21).
- Fix: use exact endpoints (`mpf_to_frac` on `x._mpi_[0]` for lower bounds and `x._mpi_[1]` for upper bounds). Alternatively, round outward explicitly, or demand a relative margin such as 1e-12.
- Upper side: with eps = S(1+1e-15), the reported upper bound stayed above S in 7/7 cases, by +2.8e-16 to +9.5e-16. No sample lay above the bound. The bound is still not rigorous by construction, since round-down is possible, so this is a **WEAKNESS**. A false upper claim cannot be shown rigorously, because the Remez filter requires eps > emax >= m.

### T5: KV comparison (`t5_kv.py`)
- (a) The experiment op `kv_evaluate` with seed=1000 reproduces the verifier's raw error bit for bit. The 20 verifier seeds are public and reachable, so there is no holdout. **WEAKNESS**
- (b) "oracle" was never beaten on 160 seed-policy pairs. **OK empirically**, but the words "lower bound" are unproven.
- (c) "recent beats random" is not significant in the paper's configuration (n=256, b=32, p=0.40). Yet it passes in 7 of 24 scanned (n, budget) configurations. That allows forking paths and needs a correction for multiple testing across claims. **WEAKNESS**
- (d) `perm_test` returns p = 0.0. It should report (count+1)/(B+1) >= 5e-5. **WEAKNESS**

### T6: polynomial-method edge cases (`t6_edges.py`)
- Degree 0 matches tanh(B). L <= U held in every case where both exist. B = 1/100 behaves correctly.
- eps > 1/2 is rejected. B=32, d=48 absolute passes at eps=1/2 with a loose bound (0.49 vs 0.048).
- The B=32 lower bound reported as 1.0 is the same rounding bug as T3.

Verdict: **OK**, apart from the T3 rounding issue and incompleteness at large B.

### T7: optimal_gamma (`t7_gamma.py`)
205 cases (alpha = 0, alpha close to 1, c in [0.001, 10]) agree exactly with a brute-force Fraction search over g <= 3000, including the tie sets. **OK**

## 3. Assumptions every competing team would make that break here
1. "Interval arithmetic means rigorous": false if the final endpoint is converted with `mp.mpf` (T3/T4).
2. "A Remez-levelled error is never within 1 ulp of the alternation bound": false. Levelling reaches 1e-23.
3. "The verifier validates every field it prints": false (lambda, k, int truncation; T1).
4. "Acceptance is one well-defined number per rule": false for `scaled` (T2c).
5. "Fixed seeds equal a held-out test": false. They are reachable through `kv_evaluate` (T5a).
6. "p < 0.05 per claim is enough": false under a scan over configurations (T5c).
7. "Equal JSON means the same claim" in `widerspricht`: equivalent spellings are not recognised.
8. "The rank C(h+d,d) is the rank": it is an upper bound on the factorisation rank.
9. "`assert` protects the max-flow feasibility checks": these checks disappear under `python -O`.

## Recommended fixes (priority)
1. Use outward rounding or exact endpoints in `certify_lower` (line `lower = mpf_to_frac(mp.mpf(m))`) and in `rigorous_sup` (`ub = mpf_to_frac(mp.mpf(...b))`).
2. Validate claim fields strictly. Require integer types for k, d, gamma, h and rank (reject floats and bools). Require lambda >= 0, and allow lambda and k only for the rules that use them.
3. Define or rename the acceptance of `scaled`.
4. Hide the verifier seeds from `kv_evaluate`, report p as (c+1)/(B+1), and apply BH across all kv claims.
