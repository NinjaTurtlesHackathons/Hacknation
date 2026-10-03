# Compliance checklist (every rule of the repository's system, with evidence)

Legend: DONE = satisfied with evidence; DEVIATION = intentionally different, with reason; N/A = does not apply, with reason; OPEN = not yet done.

## Skill `verifier-gated-lab`
| Rule | Status | Evidence |
|---|---|---|
| Read docs/FRAMEWORK.md completely first | DONE | read before any code (decisions AE1-AE3 follow its section 3) |
| Grundregel: only `domain.check` decides truth; no result in the paper unless it is a verified claim | DONE | `write_paper.py` uses only claims from state.json and certified tables whose entries passed `DOMAIN.check`; hallucination gate `asd.writer.check` |
| 1 Clarify domain (quantities, experiment, checkable statement, anchors, known false statements) | DONE | context.md (Model block), domain.kontext |
| 2 Scaffold with `python -m asd.new_domain <name>` | DEVIATION | the scaffold writes into asd/domains/; the user asked for an own subfolder. Same structure created by hand: domain code in algo_efficiency/, 2-line shim asd/domains/algo_efficiency_domain.py, projects/algo_efficiency/ (AE7) |
| 3 Verifier first; selftest >= 2 true, >= 2 false, >= 1 rule violation; tolerances fixed in the verifier | DONE | 36 cases (true and false, near-boundary within 1-2 %, analytic ground truth tanh(B), rule violations, red-team regressions); forbidden keys tolerance/precision/seeds/...; `python -m asd.selftest algo_efficiency` -> BESTANDEN (36/36) |
| 4 run_op, kontext, primitive_doc, claim_doc; no leak; answer sources in recherche_sperre | DONE | kontext contains only model, rules and known anchors; recherche_sperre empty on purpose: there is no hidden benchmark answer key, truth comes from the verifier (assumptions A7) |
| 5 Preregister comparisons/benchmarks BEFORE computing | DONE with disclosed violation | exploratory runs before prereg are disclosed as exploratory (prereg.md, AE9); confirmatory runs after commit a3b3eb6 (gate AE_G1) |
| 6 Run the lab loop; read lab_report.md, decisions.md, red-team findings in state.json | OPEN until the loop finishes | projects/algo_efficiency/ |
| 7 Harden the verifier: every bug/loophole becomes a selftest case | DONE | AE4 (rounding) -> regression case; AE13 (eps range) -> tanh ground truth; AE14 (unknown answer counted) -> consistent(); AE15 red-team soundness bug -> 2 regression cases; AE16 field validation -> 5 regression cases; AE17 KV forking paths -> preregistered-configuration case. Self-test now 36/36; red-team exploit scripts re-run: all fail |
| 8 Paper via `python -m asd.paper`; check the verification log at the end of paper.md | DEVIATION | asd.paper writes German; the repository author's rule requires English output. `algo_efficiency/write_paper.py` reuses the same gate (`asd.writer.check`), the same claim construction (canonical `describe`, uninspected interpretation as hypothesis, red team, negatives, literature, lab method), `asd.paper.to_tex`, and appends the same verification log |
| Verbot: no tolerance from the claim | DONE | FORBIDDEN_KEYS; selftest case |
| Verbot: no number/theorem/reference without verified claim/quote | DONE | gate; references only with verified title + code-checked quote (evidence.md) |
| Verbot: no skipping levels; floating point = "numerical" | DONE | experiment outputs say "numerical (candidate)"/"Monte Carlo"; nothing is proved_lean; hand proof kept at level hypothesis |
| Verbot: preregistered criteria not changed after the run | DONE | negative-control failure handled exactly as preregistered (addendum, AE10) |
| Verbot: do not omit negative results | DONE | failed negative control, failed H-AE1 acceptance, lab negatives (C-neg*) all go into claims and paper |
| Costs: budget cap, cache | DONE | `--budget-usd 5`; cache/llm |

## docs/FRAMEWORK.md section 3 (what makes a good domain)
| Rule | Status | Evidence |
|---|---|---|
| 1 Verifier recomputes independently, ideally with a certificate | DONE | exact rationals; flow = cut; interval arithmetic + de la Vallee Poussin; experiments use different methods (AE6) |
| 2 Tolerances belong to the verifier | DONE | see above |
| 3 Selftest true AND false, near the boundary, a rule violation; every found error becomes a case | DONE | see above |
| 4 No leak | DONE | see above |
| 5 Narrow, unambiguous check types | DONE | 10 typed checks, no free text |
| 6 Experiments fail softly with {"fehler": ...} | DONE | all run_op paths return {"fehler": ...} |
| 7 Honest naming; level() states the level | DONE | `level()`: statistical for kv_compare, computed_rigorous otherwise; KV downgraded to observed in the paper |

## Project CLAUDE.md
| Rule | Status | Evidence |
|---|---|---|
| AI is only a generator; acceptance only via gate, statistics or Lean | DONE | lab cascade + verifier; tables only via DOMAIN.check |
| No sentence in the paper without claim_id; no citation without tool evidence (else UNVERIFIED) | DONE | gate + evidence.md |
| One pipeline, one demo path; everything rebuildable from code; seeds fixed 1000-1019 | DONE | README pipeline; KV and T1 use seeds 1000-1019; instance-generation seeds are separate, documented ranges |
| Lean 4 where possible | OPEN (blocked) | the hand proof of opt_wor >= opt_iid is a Lean candidate; no Lean toolchain in the sandbox, installing it needs a download (asked the user) |
| Mandatory check 1: paired permutation test + bootstrap CI, >= 20 seeds | DONE | confirm.py, 20 seeds, 20,000 flips |
| Mandatory check 2: negative control | DONE (failed, handled) | gate AE_G5 = FAIL -> KV downgraded |
| Mandatory check 3: contamination test | N/A with reason | the agents' prior knowledge cannot make a false claim pass a code verifier; contamination could only bias which questions are asked (assumptions A7). There is no learned prior used as evidence in this domain |
| Mandatory check 4: Benjamini-Hochberg with m = all tests | DONE | m = 7 KV tests (gate AE_G7); exact checks are certificates, not tests |
| Theory check with every run | DONE | T1 (MC vs exact), T2 (d* <= Taylor), T3 (rule <= optimum) |
| Tables experiments/claims/gates with fixed columns; claims cite run ids | DONE | projects/algo_efficiency/tables/, `asd.tables.validate` -> 0 errors (gate AE_G10) |
| Interface changes only via decisions.md | N/A | no shared interface changed; only a new registry module |
| Each role writes only its own files | DONE | all files in algo_efficiency/, projects/algo_efficiency/ and one new shim; no edits to shared files |

## Skill `rigorous-innovation` (Full mode)
| Rule | Status | Evidence |
|---|---|---|
| Mode chosen; artefacts context/decisions/evidence (+ assumptions, candidates, prereg, schema) | DONE | Full: context.md, decisions.md, evidence.md, assumptions.md, candidates.md, prereg.md; schema = project table contract validated by code |
| Jury type and rubric in context.md | DONE | context.md |
| Primary metric (one number), coverage | DONE | context.md |
| Canonical reformulation, verifier, Mathematisieren block with axiom status, TRIZ contradiction, assumption register | DONE | context.md, assumptions.md |
| Gate 0 (metric + verifier + model) | DONE | context.md, selftest |
| Gate 1 (baseline end to end, coverage) | DONE | baselines Taylor / rrs_iid / recent+random in tables; coverage 15/15 degree cells, 24/24 gamma cells |
| Gate 2 (candidate matrix, pre-check, stage, fallback) | DONE | candidates.md |
| Gate 3 (beats baseline on primary metric) | DONE per area | (A) d* < Taylor degree in 15/15 cells; (B) optimum > rrs_iid on 145/150 (k = 2); (C) FAILED: not accepted (negative control) |
| Gate 4 validation battery: synthetic ground truth, negative control, ablation, manipulation, leakage, multiple testing, external validation, uncertainty | DONE except external | ground truth: tanh(B), 1 - TV, losslessness; negative control; ablation: interpolation vs Remez degree; manipulation: forbidden keys; leakage: none possible (no hidden data); BH; uncertainty: CIs; external validation: role A (outreach) of the team, not done here |
| Red team as separate role (read + execute, no rationale) | DONE | analysis/redteam.md (separate agent, got code and results only): 2 bugs (one soundness), 8 weaknesses; all bugs fixed with regression cases (AE15-AE17) |
| Citations verified by script (section 8) | DONE | scripts/verify_citations.py, results/citations.tsv (11/11) |
| Decisions logged with ID, time, alternatives, evidence, reversibility | DONE | decisions.md (times from the system clock/git, AE11) |
| Figures follow the dataviz method (validated palette, direct labels, table view) | DONE | write_paper.figure(); palette validated with validate_palette.js; Table 1 = table view |
| Language | DONE | all files of this domain in English (repository author's rule; AE8) |
