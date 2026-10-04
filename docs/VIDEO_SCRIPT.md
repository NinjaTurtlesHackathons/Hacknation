# Video script (generated from beats.json by `python -m asd.beats`)

Source run: `runs/omnigent/2026-10-04`. Texts in column 4 are drafts; every fact in them comes from the run's logs.

| Time (video) | Beat | Screen | Narration draft |
|---|---|---|---|
| 0:00–0:15 | Trailer (before) | *placeholder: title card, team* | *placeholder* |
| 0:15–0:30 | Question (04:20:36) | Omnigent terminal with the start prompt; prereg.md | Task: Domain proofreading, project omni_proofreading, start question F20, 3 rounds. Goal: decide more of the 35 open topologies of the two-bound-state family (exact counterexample certificate or proof), within the verifier bud / Question F20: Gibt es unter den |
| 0:30–0:45 | Agent handoffs (04:20:49) | HIGHLIGHTS.md rows 'Parallel dispatch' and 'Choice between options'; decisions.md | Lead dispatches in parallel: planner (proofreading omni_proofreading question=F20) + scout (proofreading omni_proofreading). Planner chooses O2 for F20: O2 has the higher expected gain (0.65 vs 0.35) at 1 verifier call versus 3 for O1; the budget is ample (40  |
| 0:45–1:00 | Experiment (04:25:09) | researcher session: asd.cli experiment call and its result | researcher runs search_counterexamples (E3, option O2): {'unter_schwelle': [{'topologie': 'fam2_9', 'eta': 2.000855568147094e-05, 'params': {'verw_C0_E+': 4.748790448167281, 'verw_C0_E-': 5.974755498486219, 'bind_C1_E+': 0.17888541085133824, 'bind_C1_E-': 7.14 |
| 1:00–1:15 | Result (04:25:45) | RESULT line of asd.cli pruefe | Verifier accepts proofreading-O14 (computed_rigorous): Zertifikat (a) für 10/10 Fälle bestanden |
| 1:15–1:30 | What the lab learned (04:25:30) | decisions.md REOPEN row; RESULT with ueberraschung: true | Rejected by the verifier: Zertifikat (a) für 10/11 Fälle bestanden; nicht bestanden: [('fam2_13', 'Rate außerhalb [e^-10, e^10] (/log k/ = 10.06; auch abgeleitete Rückraten zählen')] / Surprise against assumption A1: neue zertifizierte Verletzung(en) ['fam2_35 |
| 1:30–1:45 | Next experiment (04:28:26) | lead summary in the Omnigent session | The planner picked F24 with option O2 (tiefe_rechnung) and rejected O1. The round 3 researcher is dispatched on that. Redteam on O15 is still outstanding. I'm waiting on both. |
| 1:45–2:00 | Trailer (after) | *placeholder: key numbers from results/FROZEN.json* | *placeholder* |
