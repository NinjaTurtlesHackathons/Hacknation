# Live-demo path (rebuildable from code)

Run everything from the repository root. Every command is a line of the pipeline in `expressivity/README.md` or a one-line call of
the verifier `DOMAIN.check` (the same function the lab and the paper use). The expected outputs below were captured from real runs
on Sun 2026-10-04 between 06:48 and 06:58, on a machine under heavy load (load average about 87, H-EX1 grid running); wall-clock
times are from those runs and will be shorter on an idle machine. Outputs of the shared framework are partly German
(`BESTANDEN` = passed, `erwartet` / `bekommen` = expected / got); this is the shared core's text, not ours.

Helper used in D2-D5 (prints the verdict and the reason; `check` returns `(passed, reason, evidence)`):
```bash
chk() { python3 -c "import json,sys; from expressivity.domain import DOMAIN as D; print(D.check(json.loads(sys.argv[1])))" "$1"; }
```
Without the helper, each line is literally
`python3 -c "from expressivity.domain import DOMAIN as D; print(D.check({...}))"` with the dictionary pasted in.

## D1 Verifier self-test (the lab refuses to start if this fails)
```bash
python -m asd.selftest expressivity
```
Expected (last lines):
```
[OK ] erwartet False bekommen False {"typ": "hstar_value", "group": "Z2xZ2", "alphabet": "transpositions", "value": 1}
[OK ] erwartet False bekommen False {"typ": "hstar_value", "group": "S3", "alphabet": "cycles3", "value": 2}
Selbsttest expressivity: BESTANDEN (46/46)
```
Time: 109 s CPU; 6:07 wall under load. **Over the 2-minute budget on a loaded machine**: start it at the beginning of the demo in a
second terminal, or show the recorded output. 46 cases: true, false near the boundary, rule violations, red-team regressions
(e.g. `hstar_value S1 all 1` must be False).

## D2 The surprise, certified live: A5 with involution inputs needs ONE reflection (~2 s)
```bash
chk '{"typ":"realisation","group":"A5","alphabet":"involutions","k":1,"construction":"so3","twist":"involutions"}'
```
Expected:
```
(True, 'certified: |H| = 120, pi: H -> G onto (60 elements), consistent readout, dimension 3, field K_5, max rank(R[s] - I) = 1 <= k = 1, every letter factored into <= 1 exact reflections', {'H_order': 120, 'dim': 3, 'max_rank': 1, 'field': 'K_5', 'kernel_order': 2})
```
Say: "|H| = 120 is the icosahedral reflection group H3 = A5 x Z2; the kernel of order 2 is the sign. Exact arithmetic in
Q(2 cos 2 pi/5), no floating point."
Honest caveat (say it): this is realisable, not learned. In the preregistered grid hh1 on A5/involutions length-generalises in 0/20
seeds (hh2 0/20, hh3 20/20; `results/confirmatory.json`, `cells`). Learnability is a separate bottleneck.

## D3 The verifier REJECTS k = 1 without the sign lift (~1 s)
```bash
chk '{"typ":"realisation","group":"A5","alphabet":"involutions","k":1,"construction":"so3","twist":"none"}'
```
Expected:
```
(False, 'rank(R[s] - I) = 2 > k = 1 for a letter of order 2', {'max_rank': 2})
```
Say: "In the rotation group itself every involution is a rotation by pi, rank 2. Only the covering group makes it one reflection.
This is why h* (over covers) and h (faithful only) differ." Optional backup (~4 s):
```bash
chk '{"typ":"h_faithful","group":"A5","alphabet":"involutions","value":2}'
```
```
(True, 'h(G, Sigma) = 2 (own character table, GAP exact: 2)', {...})
```
(The trailing evidence dictionary is abbreviated here.)

## D4 Prior work's format: A5 as 3-cycle + 5-cycle (each ~1 s)
Permutation representation (the representation-relative law of Howe 2026 says 4):
```bash
chk '{"typ":"realisation","group":"A5","alphabet":"c3c5","k":3,"construction":"perm","twist":"none"}'
chk '{"typ":"realisation","group":"A5","alphabet":"c3c5","k":4,"construction":"perm","twist":"none"}'
```
Expected:
```
(False, 'rank(R[s] - I) = 4 > k = 3 for a letter of order 5', {'max_rank': 4})
(True, 'certified: |H| = 60, pi: H -> G onto (60 elements), consistent readout, dimension 5, field K_1, max rank(R[s] - I) = 4 <= k = 4, every letter factored into <= 4 exact reflections', {...})
```
Icosahedral rotations: two suffice, one does not.
```bash
chk '{"typ":"realisation","group":"A5","alphabet":"c3c5","k":2,"construction":"so3","twist":"none"}'
chk '{"typ":"realisation","group":"A5","alphabet":"c3c5","k":1,"construction":"so3","twist":"none"}'
chk '{"typ":"hstar_lower","group":"A5","alphabet":"c3c5","k":2}'
```
Expected:
```
(True, 'certified: |H| = 60, pi: H -> G onto (60 elements), consistent readout, dimension 3, field K_5, max rank(R[s] - I) = 2 <= k = 2, every letter factored into <= 2 exact reflections', {'H_order': 60, 'dim': 3, 'max_rank': 2, 'field': 'K_5', 'kernel_order': 1})
(False, 'rank(R[s] - I) = 2 > k = 1 for a letter of order 3', {'max_rank': 2})
(True, 'certified lower bound h* >= 2 (Lemma L4: a letter of order >= 3 cannot lift to a reflection (a rank-1 finite-order real deviation from I has order 2)); claimed >= 2', {'lower': 2})
```
Then show `projects/expressivity/fig_hex2.png`: trained models agree (hh1 0/20, hh2 18/20, Fisher p = 1.7e-9;
`results/confirmatory.json`, `H-EX2`). Also say: the preregistered H-EX2 criterion failed overall (S4/tn with 2 reflections: 6/20,
`H-EX2.success` false), and on the full H-EX1 grid our predictor (47/61) did not beat the permutation law (50/61).

## D5 The verifier refuses a wrong agent answer (~1 s and ~16 s)
The agents' wrong answer from lab rounds 3 and 6 ("more than one reflection is needed for A5/involutions"):
```bash
chk '{"typ":"hstar_lower","group":"A5","alphabet":"involutions","k":2}'
```
```
(False, 'certified lower bound h* >= 1 (nontrivial group: k = 0 means constant state); claimed >= 2', {'lower': 1})
```
And "A5 with all letters needs one reflection" (16 s under load):
```bash
chk '{"typ":"hstar_value","group":"A5","alphabet":"all","value":1}'
```
```
(False, "lower bound 2 (Lemma L4: a letter of order >= 3 cannot lift to a reflection (a rank-1 finite-order real deviation from I has order 2)); verifier's own certificate: construction so3, twist none, k = 2 (|H| = 60, dim 3); exact", {...})
```
Red-team regression (BUG 1, wrong group names): `chk '{"typ":"hstar_value","group":"S1","alphabet":"all","value":1}'` ->
`(False, "check not executable: ValueError: unknown group name 'S1'", ...)`.

## D6 Consistency-rule regressions: the lab loopholes stay closed (< 1 s)
```bash
python -m expressivity.test_consistent
```
Expected:
```
consistent() regressions: 8/8 PASS
```
The 8 cases include the round-1 loophole (answer "Nein" backed by true but weaker checks) and the red-team cases (numbers in the
answer text not certified, k = 0 as fake impossibility certificate, h used as evidence for h*); `decisions.md` EX10, EX15.

## D7 Lean: machine-checked lemmas L1 and L4
Build once beforehand (README of `expressivity/lean/`; Mathlib cache needed):
```bash
cp -r expressivity/lean /tmp/hhlemma && cd /tmp/hhlemma && lake exe cache get && lake build Hhlemma.Rank && lake env lean Hhlemma/Check.lean
```
Live (after the build): `lake env lean Hhlemma/Check.lean`. Expected (identical to `expressivity/lean/check.out`):
```
'rank_prod_sub_one_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'deltaproduct_rank_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'strengthened_bound_false' depends on axioms: [propext, Classical.choice, Quot.sound]
'sq_eq_one_of_rank_le_one_of_pow_eq_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'no_single_householder_lift' depends on axioms: [propext, Classical.choice, Quot.sound]
```
Captured by re-running `lake env lean Hhlemma/Check.lean` in an existing build of the same sources (`Rank.lean`, `Order.lean`,
`Check.lean` identical to `expressivity/lean/Hhlemma/`): 2:52 wall under load. **Over 2 minutes on a loaded machine**: if the
machine is busy, `cat expressivity/lean/check.out` and open `Order.lean` at `no_single_householder_lift` instead.
Say: "No `sorry`, only the three standard axioms; `strengthened_bound_false` is the negative control: the bound k - 1 is refuted."

## Not in the live demo (too long; show results only)
`python -m expressivity.certify`, `python -m expressivity.atlas 63`, `python -m expressivity.confirm*`, `python -m expressivity.run_lab ...`
run for minutes to hours; show `results/certified.json`, `results/atlas.json` (summary), `results/confirmatory.json` and
`projects/expressivity/lab_report.md` instead. Explorer certificates (Q8 via C4:C4, 17 lowered atlas bounds) are re-checked by
`python -m expressivity.explore_open.recheck_all` -> `results/explore_certified.json` (18/18 pass); the full re-check
`projects/expressivity/recheck.log` ends with `RECHECK PASSED`.

## Suggested order and timing (about 6 minutes with D1 and D7 pre-started)
D1 started in background -> D2 -> D3 -> D4 + fig_hex2 -> D5 -> D6 -> D1 result -> D7 output.
