# Preregistration: expressivity (commit before any confirmatory run; the commit hash is the timestamp)

## Disclosure: exploratory runs before this preregistration (Sun 2026-10-04, 02:20-02:45 by the system clock)
Pilot training runs on tasks that are **not** part of the confirmatory grid (D4/all, A4/all, Z2xZ2/all) with seeds 1-8 (not the
project seeds 1000-1019), files `results/pilot*/`. They were used only to choose training hyperparameters: they showed that with
beta initialised at 1 (a projection) hh2 did not learn D4/A4, and that beta saturating exactly at 2, a length curriculum and a final
stage at length 128 give the best length generalisation on A4 (7/8 seeds succeed with beta able to reach exactly 0 and 2). Two
pilot observations are disclosed because they bear on the hypotheses: hh1 learned Z2xZ2/all in 7/8 seeds (consistent with the count
cover, h* = 1 < h = 2), and hh2 learned D4/all in only 1/8 seeds under every beta variant tried (a learnability problem on a task the
theory allows). No confirmatory task or seed was trained before this file.
The certified quantities (h*, h, bounds) were computed before this file by the exact verifier; they are certificates, not tests.

## Fixed training protocol (all cells)
One layer, token-local transitions, readout = 2-layer MLP (128 hidden) of the full 64-dimensional state; architectures as in
`train.py` (diag_pos, diag_pm, hh1, hh2, hh3, hh4, lstm). Adam, lr 5e-3, 200 warm-up steps, cosine decay to 10 %, 3000 steps, batch
64 per member, per-member gradient clipping 1.0, beta_bias 2, beta_mode clamp2 (beta = 2 clip(1.5 sigmoid(z) - 0.25, 0, 1), reaches exactly 0 and 2), curriculum of
lengths 8, 16, 32, 64 in quarters of the first 85 % of steps, final 15 % at length 128. Seeds 1000-1019 (one ensemble member each;
own initialisation and data stream). Evaluation on 512 fresh sequences per member from generators seeded 900000 + seed.

## Grid
Tasks (G, Sigma): Z2/all, Z3/all, Z2^3/all, S3/transpositions, S3/all, A5/involutions, A5/all, S5/transpositions, S5/all.
Architectures: diag_pos, diag_pm, hh1, hh2, hh3, hh4, lstm. 63 cells x 20 seeds.

## Outcome definitions
- Seed success: mean token accuracy on positions 257-512 of length-512 sequences >= 0.90 (2x to 4x the longest training length 128,
  4x to 8x the main training length 64). Secondary: positions 897-1024 of length-1024 sequences, same threshold.
- Cell outcome: success iff at least 10 of 20 seeds succeed.

## Predictors (computed by code before the run: `python -m expressivity.predict` -> `results/predictions.json`)
ALG (ours: diag_pos iff G trivial, diag_pm iff G elementary abelian 2-group, hhK iff K >= h*(G, Sigma), lstm always; undetermined
when the certified bounds do not decide, i.e. hh2 and hh3 on S5/all), B1 circuit class (solvable), B2 abelian, B3 |G| <= 24,
B4 representation law in the permutation representation (Howe 2026), B5 faithful representations only (h(G, Sigma)).

## H-EX1 (primary, confirmatory)
1. **Accuracy:** ALG agrees with the cell outcomes on more determined cells (61 cells) than each of B1-B5. Reported for every predictor.
2. **Discriminating cells** (seed-level, one-sided Fisher exact test on the number of successful seeds, 20 vs 20):
   - D1: hh1 on A5/involutions > hh1 on A5/all (ALG: 1 Householder suffices for A5 with involution inputs; B4, B5: it does not)
   - D2: hh2 on A5/all > hh1 on A5/all (ALG: 2 suffice for A5; B4 predicts 4)
   - D3: hh1 on Z2^3/all > hh1 on Z3/all (ALG: count cover with 1 reflection; B4, B5 predict 3)
   - D4: hh1 on S5/transpositions > hh1 on S5/all (same group, different alphabet)
   - D5: hh1 on Z2/all > hh1 on Z3/all (necessity for an abelian, solvable group: B1, B2, B3 predict success on Z3)
   - D6: diag_pm on Z2^3/all > diag_pm on Z3/all (diagonal with negative eigenvalues: only elementary abelian 2-groups)
3. **Success of H-EX1:** (1) holds strictly for B1-B5 AND D1-D6 are significant after Benjamini–Hochberg at q = 0.1.

## Mandatory checks
- **Negative control:** random targets (i.i.d. uniform labels, independent of the input) for hh4 on S5/all, lstm on S5/all and hh2
  on A5/all. Expectation: 0 successful seeds in each; one-sided binomial test of "success rate > 0.05" must NOT be significant, and any
  successful seed invalidates the success criterion.
- **Positive control:** lstm on every task (expected: success).
- **Multiple testing:** Benjamini–Hochberg with q = 0.1 over all tests in this file: D1-D6 and the 3 negative-control tests (m = 9).
- **Theory check:** chance accuracy 1/|G| is reported per task; in-distribution accuracy (positions 1-64 of length 64) per cell.
- **Contamination test:** not applicable in the original sense (no learned prior used as evidence); the agents' prior knowledge
  cannot make a false claim pass the exact verifier (assumptions A7).
- Reported regardless of outcome. Cells where ALG predicts success but training fails are reported as learnability failures, not
  explained away.

Changes to this file after the first confirmatory run only as a new dated section with reason.

## Addendum 2026-10-04 05:00 - H-EX2 (new confirmatory test, preregistered before any run of these cells)
Reason: the closest prior work (Howe 2026, arXiv:2609.18966) states an empirical law for exactly two generator formats: S4 with a
transposition and a 4-cycle needs 3 Householder factors, A5 with a 3-cycle and a 5-cycle needs 4 (full-text quotes in
results/body_quotes.json). Our certified values are h*(S4, tn) = h*(A5, c3c5) = 2 (results/certified.json). H-EX1 does not contain these
formats. Partial H-EX1 results seen before this addendum (13 hh3/hh4 cells and one negative-control cell) are disclosed; none of them
uses these alphabets.
- Cells: hh1, hh2, hh3 on S4/tn and A5/c3c5 (6 cells x 20 seeds 1000-1019); protocol identical to H-EX1 (same constants in confirm.py),
  except that these cells run on the Apple-MPS GPU (float32) because the CPUs are occupied by the H-EX1 grid; device recorded per file.
- Predictions: ALG (ours): hh1 fails (Lemma L4, Lean), hh2 and hh3 succeed. B4 (representation law in the permutation representation):
  S4/tn needs 3 (hh2 fails, hh3 succeeds), A5/c3c5 needs 4 (hh2 and hh3 fail).
- Tests (one-sided Fisher exact on successful seeds, same success definition as H-EX1): E1 hh2 A5/c3c5 > hh1 A5/c3c5; E2 hh2 S4/tn > hh1 S4/tn;
  E3 hh3 A5/c3c5 > hh1 A5/c3c5. Benjamini-Hochberg with q = 0.1 over E1-E3 (m = 3).
- Success of H-EX2: E1 and E2 significant after BH AND the hh2 cells of both tasks have cell outcome success (>= 10 of 20 seeds), which B4
  predicts to be impossible. Reported regardless of outcome.

## Addendum 2026-10-04 07:00 (erratum and reporting rules after a runner bug; decision criteria above unchanged)
- **Erratum to the H-EX2 addendum:** at 05:00, 12 H-EX1 cells (hh3/hh4) and one negative-control cell had finished, not 13 plus one.
- **Runner bug (found by the compliance audit):** the CPU pool (confirm.py) checks for finished cells only at start-up and overwrote
  cells that the MPS runner (confirm_mps.py, decision EX21) had already written: hh1/Z2/all (MPS 18 of 20 successful seeds, CPU 0 of 20)
  and diag_pos/Z2/all (MPS 0 of 20, CPU 0 of 20). The per-seed MPS values of these two cells were overwritten; their success counts
  survive in the MPS runner log (results/confirmatory_mps_replication/runner_logs.txt). From 06:58 a watcher restores every MPS file
  and keeps the CPU duplicate in results/confirmatory_cpu_duplicates/; the pool is stopped once all cells exist.
- **Which run counts (rule fixed by EX21 before any of these results):** a cell already written is not recomputed, so the first
  completed run is primary (MPS for the cells the MPS runner finished first, CPU otherwise); every duplicate is reported as a replication,
  together with the device sensitivity. For hh1/Z2 and diag_pos/Z2 the primary outcome is taken from the MPS runner log (success counts
  only; no per-seed accuracies, so no paired permutation test for D5).
- **Multiple testing, additional report:** besides the preregistered families (H-EX1: m = 9; H-EX2: m = 3), Benjamini-Hochberg over all 12
  tests together is reported as well.
- **Project criterion (CLAUDE.md, mandatory check 1), additional report:** for every discriminating comparison, p < 0.05 of the paired
  permutation test AND a paired bootstrap 95% CI of the accuracy ratio that excludes 1 is reported next to the preregistered Fisher test.
