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
