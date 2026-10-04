# Compliance audit: domain `expressivity` (branch `expressivity`, HEAD 03eb9f0)

Auditor role: read and execute only. Audit time: Sun 2026-10-04, about 06:50 local. The confirmatory grid was still running
(PID 73655, `python3 -m expressivity.confirm --workers 13`; the lstm cells are not finished), and so was the lab loop
(`projects/expressivity/state.json` last written 06:18).
I did not run the long self-test, training, atlas, recheck, export_tables or the paper writer.

Commands run: `git log b636a25..HEAD` (full messages), `git log -p expressivity/prereg.md`, `git status`,
`python3 -m expressivity.test_consistent` (8/8 PASS), an AST count of `DOMAIN.selftest()` cases (46), a scan of every domain file
for German words, a check of claim IDs and levels in `projects/expressivity/paper_claims.json` against `paper.md` and `paper.tex`,
and a read of the `finished`/`device` fields of all 62 files in `results/confirmatory/` against the run logs and commit times.

Legend: OK = claim verified; GAP = rule not (fully) met, or evidence missing; WRONG = COMPLIANCE.md states something that is false.

## Critical findings (summary)

1. **A preregistered cell was run twice with contradictory results, and the second run silently overwrote the first.**
   `hh1 Z2/all` on MPS (float32): 18 of 20 seeds (`results/confirm_mps_b.log`, 05:36:48). On CPU: 0 of 20 (`confirm_run.log`, 06:39:51).
   The CPU job started at about 06:12, after the MPS file already existed: `confirm.py` filters finished jobs only once, at
   start-up (line 43). Its result now sits in `results/confirmatory/hh1__Z2__all.json`. The same thing happened to
   `diag_pos__Z2__all.json` (committed MPS file overwritten by a CPU run; `git status` shows M, same outcome 0/20). The CPU pool
   will overwrite every remaining MPS cell (diag_pos, diag_pm, hh1) in the same way. This cell feeds the preregistered test
   D5 (hh1 Z2 > hh1 Z3), and the two outcomes are opposite. EX21 claims the opposite behaviour ("a cell already written is
   skipped"), and only `confirm_mps.py` actually implements it.
2. **Paper outputs contain German.** `projects/expressivity/paper.tex` (and therefore paper.pdf), lines 443 and 449, and
   `paper_claims.json` (C-expressivity-R3, R6) contain German lab-round questions ("Liegt h*(A5, involutions) bei 1 oder
   darüber ...", "Wie verhält sich ..."). The English gate in `write_paper.gate()` only scans the markdown body, not the
   claim-trace appendix.
3. **`projects/expressivity/` is entirely untracked in git** (paper, state.json, lab_report.md, round preregistrations,
   paper_claims.json, figures). The proofreading domain's project files are tracked. About 190 new `cache/llm/` entries are also
   untracked, so the paper cannot be rebuilt in replay mode from the repository.

## Audit table

| Rule | COMPLIANCE.md status | Audited status | Evidence | Required fix |
|---|---|---|---|---|
| **Git history: no Claude/Anthropic/AI mention in commit messages** (global rule) | not listed | OK | All 8 commits b636a25..HEAD: grep on full bodies for claude/anthropic/co-authored/generated/AI/LLM finds nothing; no trailers | none |
| Git history: commit messages in English | not listed | OK | all 8 subjects and bodies are English | none |
| No AI mention in code comments | not listed | OK | `git grep -i "claude\|anthropic"` over *.py/*.lean of the domain: no hits in comments | none |
| No AI mention in other repo docs (spirit of the global rule) | not listed | GAP (advisory) | `decisions.md` Owner column says "Claude" in every row (EX1-EX23) | strictly, the rule names commit messages, PR texts and code comments only; recommend changing the owner to the human role (e.g. "D (verification)") |
| Read FRAMEWORK.md first | DONE | OK (not checkable beyond documents) | decisions EX1-EX6 cite it | none |
| Grundregel: only `domain.check` decides; no unverified result in the paper | DONE | OK with caveat | `write_paper.py` builds claims from certified.json/atlas/lab re-check (EX19); 93 claims; every cited ID in paper.md exists except the family wildcards `C-G-*`, `C-T-*`, `C-atlas*` (families exist: 12, 23, 5 IDs) | make the gate expand the wildcards, or cite explicit IDs |
| Step 2 scaffold via `asd.new_domain` | DEVIATION | OK | shim `asd/domains/expressivity_domain.py` (2 lines), EX1 | none |
| Step 3 verifier first; >= 2 true, >= 2 false, a rule violation; 46 cases | DONE | OK | verifier in 8436ea6 (02:22), before prereg 13d2e3c (02:50); AST count of `selftest()`: 46 cases; `test_consistent`: 8/8 PASS (run now) | none (full self-test not re-run on purpose) |
| Step 4 no leak; recherche_sperre empty | DONE | OK | assumptions.md A7; experiments are floating point only, verifier exact | none |
| Step 5 / Verbot: preregister before computing | DONE with disclosed pilot | OK | earliest confirmatory start: hh3 Z3 at 04:15:30 - 5067 s = 02:51:03, 7 s after the 13d2e3c commit (02:50:56). H-EX2: first cells start at 04:57:31 (05:04:39 - 428 s; 05:06:32 - 541 s), 14 s after the a78ed64 commit (04:57:17). certified.json for tn/c3c5 already in 56ca504 (04:13) | none |
| Verbot: prereg not changed after the run except dated addenda | DONE | OK | `git log -p expressivity/prereg.md`: 13d2e3c creates the file; a78ed64 only appends "Addendum 2026-10-04 05:00 - H-EX2" (+15 lines, no deletions); working tree unchanged | none |
| H-EX2 addendum disclosure accuracy | not listed | WRONG (minor) | addendum says "13 hh3/hh4 cells and one negative-control cell" were seen; by 04:57:17 only 12 hh3/hh4 cells (hh3 x3, hh4 x9) plus 1 NC cell had finished (`finished` fields) | add a dated erratum line: "12 cells + 1 NC" (or list them) |
| **Protocol change for preregistered H-EX1 cells (MPS float32 device)** | DONE (EX21 in decisions) | GAP | Verbot: "Abweichungen kommen als datierter Nachtrag in prereg.md". The H-EX1 protocol (prereg 13d2e3c) does not mention MPS/float32; EX21 is only in decisions.md. The device changes the outcome (hh1 Z2/all 18/20 on MPS vs 0/20 on CPU) | dated addendum in prereg.md: which device counts per cell, written before the remaining cells finish; report the device sensitivity as a finding |
| **Integrity of confirmatory results (one run per cell, no silent overwrite)** | DONE (EX21 "a cell already written is skipped") | WRONG | `confirm.py` checks existence only at start-up; it overwrote `hh1__Z2__all.json` (MPS 18/20 -> CPU 0/20) and `diag_pos__Z2__all.json`. The MPS result survives only in `confirm_mps_b.log` | stop the CPU pool for cells the MPS runner handles, or make `job()` re-check existence before writing; recover both runs from the logs; preregister (dated addendum) which run counts; report both in the paper and in decisions.md (new EX entry); never let two runners write the same file |
| Step 6 lab loop; read lab_report, decisions, red team | DONE | OK | run_lab.py wrapper (EX9), lab_loop_run1-4.log, rounds 1-13 in projects/expressivity/ | none |
| Step 7 harden the verifier (bugs become cases) | DONE | OK | EX7, EX8, EX10, EX15, EX18; redteam.md with t1-t11 scripts and .out files; self-test 46 cases | none |
| Step 8 paper via `asd.paper` | DEVIATION | OK | write_paper.py reuses `asd.writer.check`; EX22 (pandoc) | none |
| Verbot: no tolerance from the claim | DONE | OK | `FORBIDDEN_PREFIXES` in domain.py line 16, checked line 190 | none |
| Verbot: no reference without a verified quote | DONE | OK | verify_evidence.log: 56 VERIFIED, 7 VERIFIED-ID, 2 "quote UNVERIFIED"; evidence.md marks the 2 as UNVERIFIED and unused | none |
| Verbot: no level skipping; claim types used in the paper exist | DONE | OK | levels in paper_claims.json: computed_rigorous 37, observed 26, statistical 15, hypothesis 13, proved_lean 2, all in the CLAUDE.md enum; proved_lean = L1, L4 only (lean/check.out: only propext, Classical.choice, Quot.sound; no `sorry` in Hhlemma/*.lean) | none |
| Verbot: no omitted negative results | DONE | OK (partial: grid unfinished) | lab negatives and withdrawn claims are in paper_claims (3 "contested") | after finishing, make sure both runs of the duplicated cells are reported (see above) |
| Costs: budget cap, cache | DONE | GAP | `--budget-usd 25` in README/run_lab.py OK; but about 190 new `cache/llm/*.json` files are untracked, so replay (`ASD_LLM=replay`) of the current lab/paper is impossible from git | commit the cache entries (or document that replay is not supported) |
| FRAMEWORK §3.1-3.7 (independent verifier, tolerances, self-test, no leak, narrow types, soft failure, honest naming) | DONE | OK | domain.py: 6 typed checks; run_op returns `{"fehler": ...}` (lines 171, 173; key required by the framework interface) | none |
| FRAMEWORK §5: self-test fail -> no start | DONE | OK | lab_loop_run3.log: start refused after a self-test failure (EX18) | none |
| FRAMEWORK §5: claim only if check AND consistent | DONE | OK | test_consistent 8/8 PASS | none |
| FRAMEWORK §5: every round preregistered (projects/<d>/prereg.md) | not listed separately | GAP | projects/expressivity/prereg.md exists (rounds "vor dem Experiment" with times), but the whole folder is untracked, so there is no commit timestamp | commit projects/expressivity/ (prereg.md, decisions.md, state.json, runde*.json, lab_report.md, paper*) |
| CLAUDE.md: AI only generator | DONE | OK | see Grundregel | none |
| CLAUDE.md: no sentence without claim_id; citations with tool evidence | DONE | OK with caveat | verification log at the end of paper.md: 76 claims cited, 0 removed; wildcard citations (see above) | expand the wildcards |
| CLAUDE.md: one pipeline, one demo path, rebuildable | DONE | GAP | three runners (confirm.py CPU, confirm_mps.py MPS, confirm_ex2.py) write into the same `results/confirmatory/` and collide (skill §11 anti-pattern "parallel pipelines"); paper and figures are not in git; `projects/expressivity/tables/` does not exist | one runner per cell set; commit the outputs; run export_tables |
| CLAUDE.md: seeds fixed 1000-1019 | DONE | OK | every confirmatory file has seeds 1000-1019; pilots used seeds 1-8 (disclosed) | none |
| CLAUDE.md: Lean where possible | DONE | OK | lean/check.out, Rank.lean, Order.lean, Check.lean (negative control `strengthened_bound_false`) | none |
| **Mandatory check 1: paired permutation + bootstrap; Gate 3 at >= 20 seeds, p < 0.05, CI excluding 1** | DONE | GAP | analyze.py reports the paired permutation p and the bootstrap CI (lines 65-71), but the decision rule is a one-sided Fisher test with BH q = 0.1 (prereg). CLAUDE.md fixes p < 0.05 and a CI excluding 1, and "Bei Konflikt gilt diese Datei". No decisions.md entry records this deviation | add a decisions.md entry (deviation + reason); additionally report the CLAUDE.md gate (perm p < 0.05 and CI excluding 1) per discriminating test as a secondary result |
| Mandatory check 2: negative control | see results | OK (pending) | NC hh4 S5/all (04:55) and hh2 A5/all (06:12) done; lstm S5/all still running | report after the grid ends |
| Mandatory check 3: contamination | N/A with reason | OK | prereg.md and assumptions.md A7 give the reason | none |
| **Mandatory check 4: BH with m = all tests** | DONE, "m = 9" | WRONG | since the H-EX2 addendum there are 12 tests; analyze.py corrects H-EX1 (m = 9, line 78) and H-EX2 (m = 3, line 102) separately. CLAUDE.md and skill §7 require m = the total number of tests | report BH over all 12 tests (at least as a sensitivity check; the preregistered families stay primary), document it in decisions.md, update COMPLIANCE.md (m = 12) |
| Theory check with every run | DONE | OK | analyze.py records chance 1/|G| and in-distribution accuracy per cell | none |
| Tables experiments/claims/gates, validated | DONE | GAP | `export_tables.py` exists, but `projects/expressivity/tables/` does not exist: never run (or deleted), so no validation result is on record | run `python -m expressivity.export_tables` after the grid and commit the tables plus the gate result |
| Interface changes only via decisions.md | N/A | OK | shared core unchanged (EX9 wrapper) | none |
| Each role writes only its own files | DONE | OK | `git diff --stat b636a25..HEAD` touches only expressivity/ and the shim | none |
| RI: Full-mode artefacts | DONE | OK | context, decisions, evidence, assumptions, candidates, prereg present; schema = asd.tables | none |
| RI: jury rubric verbatim in context.md | DONE | GAP (minor) | context.md has the challenge sentence and a "rubric mapping from CLAUDE.md", not the jury's official rubric verbatim | paste the official Hack-Nation judging criteria verbatim, or state that none was published |
| RI: primary metric, coverage, Mathematisieren with axiom status, TRIZ, assumptions | DONE | OK | context.md sections "Primary metric", "Model" (item 4 axioms/lemmas with status), "TRIZ"; assumptions.md | none |
| **RI: gate decisions (Gate 0-2) logged in decisions.md** | DONE | GAP | no decisions.md row records Gate 0, 1, 2 (or 3/4) as a decision ("weiter / Scope / Kandidat / Kill") with time and owner; the evidence exists in artefacts, but the gate decisions are not logged | add gate rows (time, decision, evidence, human owner) |
| RI: Gate 3 | see results | OK (pending) | analyze.py gate H-EX1.1 | none |
| RI: Gate 4 battery | DONE except external | OK | external validation openly marked as not done | none |
| RI: Red team as a separate role | DONE | OK | analysis/redteam.md ("read and execute only", 3 bugs) | none |
| RI: Scout / Analogist | DONE | OK | scout_evidence.md, analogist_candidates.md, EX5 | none |
| RI §8: citations verified by script | DONE | OK | scripts/verify_citations.py, verify_evidence.py, body_quotes.py, results/verify_evidence.log | none |
| RI: decisions with ID, time, alternatives, evidence, reversibility | DONE | GAP (minor) | format OK. Missing entries: the CPU/MPS overwrite and duplicate runs, the BH family split, the Fisher test / q = 0.1 deviation from CLAUDE.md. EX22 (05:05) appears after EX21 (05:10) | add the entries listed |
| RI: figures follow the dataviz method; "validate_palette.js" | DONE | GAP | no `validate_palette.js` and no validator output anywhere in the repository; only a docstring in write_paper.py says "validated palette" | commit the validator call and its output, or drop "validated" from the claim |
| **Language: every file of the domain in English** | DONE (exception only for lab_report.md) | WRONG | (a) paper.tex/paper.pdf appendix and paper_claims.json contain German lab questions (R3, R6); (b) tracked `expressivity/results/lab_loop_run1-4.log` contain German framework strings and German agent questions, which goes beyond the stated lab_report.md exception; (c) `run_lab.py` line 13: German default system prompt "Du bist ein sorgfältiger Wissenschaftler ..." in domain code; (d) domain.py line 315 matches German negations (functional, acceptable) | (a) make the gate scan the whole tex/appendix and claim texts, and translate or summarise lab questions in English before they enter claims; (b) extend the disclosed exception to results/lab_loop_run*.log and projects/expressivity/*.json, or translate; (c) English system prompt (this changes cache keys: note it in decisions.md) |
| Paper is current | not listed | GAP (expected, grid unfinished) | paper.md 05:03, before H-EX2 and most H-EX1 cells; Table 2 is mostly n/a | regenerate after the grid and the duplicate-run resolution |

## Required actions, in priority order
1. Stop the double-writing now (CPU pool vs MPS runner). Recover the MPS results for `hh1 Z2/all` and `diag_pos Z2/all` from the
   logs, add a dated prereg addendum fixing which run counts, add a decisions.md entry, and report both runs and the device
   sensitivity.
2. Remove German from the paper appendix and claims; extend the gate; extend or translate the lab-log exception; translate the
   run_lab.py system prompt.
3. Commit projects/expressivity/ and the new cache entries; run export_tables and commit the tables.
4. Statistics: BH over all 12 tests (sensitivity), plus a decisions.md entry for the Fisher test / q = 0.1 vs the CLAUDE.md gate
   (p < 0.05, CI excluding 1); update COMPLIANCE.md (m).
5. Minor: addendum count erratum (12 + 1), gate rows in decisions.md, verbatim rubric, palette-validator evidence, wildcard
   claim citations, optional "Claude" owner wording.
