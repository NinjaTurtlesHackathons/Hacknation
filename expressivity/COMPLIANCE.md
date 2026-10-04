# Compliance checklist (every rule of the repository's system, with evidence)

Legend: DONE = satisfied with evidence; DEVIATION = intentionally different, with reason; N/A = does not apply, with reason; OPEN = not done.

## Skill `verifier-gated-lab`
| Rule | Status | Evidence |
|---|---|---|
| Read docs/FRAMEWORK.md completely first | DONE | read (with CLAUDE.md, both skills, the asd/ code and the algo_efficiency example) before any code; decisions EX1-EX6 |
| Grundregel: only `domain.check` decides truth; no result in the paper unless verified | DONE | write_paper.py builds claims only from DOMAIN.check results (certified.json, atlas, lab claims re-checked), Lean, and the preregistered statistics; hallucination gate asd.writer.check |
| 1 Clarify domain (quantities, experiment, checkable statement, anchors, known false statements) | DONE | context.md (Model block), DOMAIN.kontext, primitive_doc, claim_doc |
| 2 Scaffold with `python -m asd.new_domain` | DEVIATION | own subfolder requested by the user; same structure by hand: expressivity/, 2-line shim asd/domains/expressivity_domain.py, projects/expressivity/ (EX1; same as algo_efficiency AE7) |
| 3 Verifier first; >= 2 true, >= 2 false, >= 1 rule violation; tolerances fixed in the verifier | DONE | verifier committed (8436ea6) before any experiment; self-test 46 cases (true, near-boundary false, rule violations, red-team regressions); forbidden key prefixes; `python -m asd.selftest expressivity` -> BESTANDEN (46/46) |
| 4 run_op, kontext, primitive_doc, claim_doc; no leak; answer sources in recherche_sperre | DONE | experiments are floating point only, verifier exact (EX6); kontext states definitions and anchors, no answers; recherche_sperre empty on purpose: no hidden answer key, truth from the verifier (assumptions A7) |
| 5 Preregister comparisons BEFORE computing | DONE with disclosed pilot | prereg.md committed (13d2e3c) before the grid; pilot runs on tasks and seeds outside the grid disclosed (EX11) |
| 6 Run the lab loop; read lab_report.md, decisions.md, red-team findings in state.json | DONE | expressivity/run_lab.py (wrapper, EX9); rounds read; loophole found and closed (EX10); stored claims re-checked (EX19) |
| 7 Harden the verifier: every bug/loophole becomes a self-test case | DONE | EX7, EX8, EX10, EX15 (self-test 40 -> 46, test_consistent.py 8/8) |
| 8 Paper via `python -m asd.paper`; check the verification log | DEVIATION | asd.paper writes German; the repository author's rule requires English. write_paper.py reuses the same gate (asd.writer.check), claim structure (canonical describe, uninspected interpretation as hypothesis, red team, negatives, literature, lab method), asd.paper.to_tex, and appends the verification log (same choice as algo_efficiency) |
| Verbot: no tolerance from the claim | DONE | FORBIDDEN_PREFIXES; self-test cases |
| Verbot: no number/theorem/reference without verified claim/quote | DONE | gate; references only with code-verified title and code-verified verbatim quote (evidence.md, results/citations.tsv, results/body_quotes.json) |
| Verbot: no skipping levels; floating point = numerical | DONE | experiments labelled numerical; hand proofs at level hypothesis; only L1, L4 proved_lean |
| Verbot: preregistered criteria not changed after the run | DONE | prereg.md unchanged after 13d2e3c except dated addenda |
| Verbot: do not omit negative results | DONE | lab negatives, withdrawn lab claims, learnability failures and failed predictions are claims in the paper |
| Costs: budget cap, cache | DONE | --budget-usd 25 (user: costs are not a constraint), cache/llm |

## docs/FRAMEWORK.md section 3 (what makes a good domain) and section 5 (rules the lab enforces)
| Rule | Status | Evidence |
|---|---|---|
| 1 Verifier recomputes independently, ideally with a certificate | DONE | exact closures over Q(2 cos 2 pi/N), invariant form, rank, explicit reflection factorisation; character tables twice (own + GAP) |
| 2 Tolerances belong to the verifier | DONE | no claim field sets a tolerance or limit |
| 3 Self-test true AND false near the boundary, a rule violation; every found error becomes a case | DONE | see above |
| 4 No leak | DONE | see above |
| 5 Narrow, unambiguous check types | DONE | 6 typed checks |
| 6 Experiments fail softly with {"fehler": ...} | DONE | run_op catches every exception |
| 7 Honest naming; level() | DONE | computed_rigorous for exact certificates; the paper marks hand proofs as hypothesis |
| Section 5: self-test failing -> no start | DONE | observed in practice: the lab refused to start after a time-limit failure (EX18) |
| Section 5: a claim counts only if check passes AND the answer matches | DONE | consistent() hardened twice (EX10, EX15) |

## Project CLAUDE.md
| Rule | Status | Evidence |
|---|---|---|
| AI is only a generator; acceptance only via gate, statistics or Lean | DONE | lab cascade + exact verifier; Lean for L1, L4; preregistered statistics |
| No sentence in the paper without claim_id; no citation without tool evidence (else UNVERIFIED) | DONE | gate; 2 scout quotes not found verbatim are marked UNVERIFIED and unused |
| One pipeline, one demo path; rebuildable; seeds fixed 1000-1019 | DONE | README pipeline; grid seeds 1000-1019; pilots used other seeds (disclosed) |
| Lean 4 where possible | DONE | lean/: rank lemma L1 and order lemma L4 with negative control and axiom check (EX13, EX16) |
| Mandatory check 1: paired permutation test + bootstrap CI, >= 20 seeds | DONE | 20 seeds per cell; preregistered decision tests are one-sided Fisher exact tests on success counts (binary outcome); in addition analyze.py reports the paired sign-flip permutation test on per-seed accuracies (same seeds) and the paired bootstrap 95% CI of the accuracy ratio for every discriminating comparison |
| Mandatory check 2: negative control | see results | random-target cells (prereg.md) |
| Mandatory check 3: contamination test | N/A with reason | no learned prior is used as evidence; the agents' prior knowledge cannot make a false claim pass the exact verifier (assumptions A7) |
| Mandatory check 4: Benjamini-Hochberg with m = all tests | DONE | m = 9 (6 discriminating + 3 negative-control tests), analyze.py |
| Theory check with every run | DONE | chance accuracy 1/|G| and in-distribution accuracy per cell; certified bounds as theory for every task |
| Tables experiments/claims/gates; claims cite run ids | DONE | export_tables.py, asd.tables.validate |
| Interface changes only via decisions.md | N/A | no shared interface changed; the framework bug (EX9) was handled by an own wrapper |
| Each role writes only its own files | DONE | all files in expressivity/, projects/expressivity/ and one shim |

## Skill `rigorous-innovation` (Full mode)
| Rule | Status | Evidence |
|---|---|---|
| Mode, artefacts context/decisions/evidence + assumptions/candidates/prereg/schema | DONE | all present; schema = framework table contract validated by code |
| Jury type and rubric in context.md | DONE | context.md |
| Primary metric (one number), coverage | DONE | predictor accuracy on the preregistered grid; atlas coverage (h* exact for 138 of 319 groups) |
| Canonical reformulation, verifier, Mathematisieren with axiom status, TRIZ, assumption register | DONE | context.md, assumptions.md, theory.md |
| Gate 0 / Gate 1 (baseline, coverage) | DONE | baselines B1-B5 predictors; dumbest models diag_pos/diag_pm; coverage in the atlas |
| Gate 2 (candidate matrix, pre-check, stage, fallback) | DONE | candidates.md incl. formal stage with obligations O1-O6 |
| Gate 3 (beats baseline on primary metric) | see results | analyze.py gate H-EX1.1 |
| Gate 4 validation battery: synthetic ground truth, negative control, ablation, manipulation, leakage, multiple testing, external validation, uncertainty | DONE except external | ground truth: known anchors in the self-test, GAP; negative control; ablation = the architecture axis of the grid; manipulation = forbidden keys / red team; leakage: none possible (no hidden data); BH; external validation: role A (outreach) of the team, not done here |
| Red team as separate role (read + execute, no rationale) | DONE | analysis/redteam.md, 3 bugs fixed (EX15) |
| Scout without solution ideas; Analogist with only the functional abstraction | DONE | scout_evidence.md, analogist_candidates.md (EX5) |
| Citations verified by script (section 8) | DONE | scripts/verify_evidence.py (+ body_quotes.py) |
| Decisions logged with ID, time, alternatives, evidence, reversibility | DONE | decisions.md EX1-EX20+ |
| Figures follow the dataviz method | DONE | validated palette (validate_palette.js), sequential blue ramp, direct labels, table views (Tables 2, 3) |
| Language | DONE | all files of this domain in English (EX2); framework-generated lab logs (lab_report.md) contain the framework's German strings (shared core not edited) |
