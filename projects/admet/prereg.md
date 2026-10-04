# ADMET preregistration — 2026-10-04

Committed before ADMET training. User authorizes autonomous decisions; Full scientific workflow, module B; no conformal claims (CLAUDE.md precedence).

Scope: official TDC ADMET fixed train_val/test CSVs, solubility_aqsoldb, lipophilicity_astrazeneca, caco2_wang. These three endpoints are selected before model results, for physicochemical interpretability; no claim covering all 22 tasks.

Primary H1: concatenating Morgan fingerprints with ten fixed physicochemical descriptors reduces scaffold-validation MAE relative to Morgan alone on solubility. Secondary H2/H3: same comparison on lipophilicity and Caco-2. Family m=3, one-sided paired sign-flip Monte Carlo test, 20,000 flips with plus-one correction; paired percentile bootstrap 5,000 replicates, BH q=0.1. Success requires 20 seeds, p<0.05, BH rejection and ratio-CI lower bound >1. The repeated splits overlap; seed intervals describe this fixed dataset and do not establish independent biological replication.

Seeds 1000–1019. TDC get_train_valid_split(seed, endpoint) scaffold partitions. Fixed LightGBM: 200 estimators, learning_rate=.05, num_leaves=15, max_depth=-1, min_child_samples=20, reg_lambda=1, n_jobs=2, deterministic=True, force_col_wise=True. No tuning/early stopping. Features: Morgan radius2 1024-bit; MolWt, MolLogP, TPSA, NumHDonors, NumHAcceptors, NumRotatableBonds, RingCount, FractionCSP3, HeavyAtomCount, NumAromaticRings. Ablations: descriptors-only, Morgan-only, concatenated; median baseline.

No test labels or scores to agent prompts. Freeze fixed methods before computing test scores. Final test uses the same 20 fitted scaffold-training models (not refit on train_val). Also report seeds 1000–1004 separately; these are not asserted to be the leaderboard's standard seeds or an official submission.

Negative control: concatenated features with training targets shuffled per seed, compared with train-target median. Non-significance alone is not proof of independence. Synthetic recoverability and verifier true/false/boundary/malformed/self-assigned-tolerance tests mandatory. Neutralization: all agent inputs are codes and validation summaries; identifiers cannot affect predictions. This checks name exposure, not absence of training-corpus memorization.

Audit all 22 endpoints for missing fields, valid SMILES, canonical-molecule and scaffold overlap; invalid structures block model run; no silent row dropping. Data hashes and package versions archived. Test similarities segmented below .3, [.3,.6), >=.6 against each model's training molecules, exploratory only; no segment significance claims. All failed hypotheses retained. No leaderboard, clinical, causal, 10x discovery-speed or biological-mechanism claim without independent evidence.

Stop criteria: verifier/audit fails => feature stop; hypothesis gate fails => honest negative-result paper. External validation here is measured held-out ADMET outcomes; independent new assay/temporal dataset and expert review remain absent.

## Amendment A — 2026-10-04, before completed experiment or score inspection
Structural audit (no test targets inspected) found two unparsable solubility test SMILES, rows 1159 and 1160. Preserve every row; use training-target median on invalid structures for all methods, mark invalid_structure and similarity=0. Training invalids still block. No chemical repair or row deletion. Report valid-structure-only sensitivity.

## Execution deviation
A shell working-directory error prevented the planned preregistration commit, while the following training command started. It was terminated during first split initialization before a completed seed or any score was inspected. No result informed protocol changes. The protocol document existed before this command; the commit is later. This is not a clean commit-before-first-computation claim.
