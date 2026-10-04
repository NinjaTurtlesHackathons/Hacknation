# Decisions

| ID | Time | Decision | Alternatives | Evidence | Reversible | Owner |
|---|---|---|---|---|---|---|
| A1 | 2026-10-04 | Isolated research/admet branch from paper-bell, projects/admet folder | main without framework | Required skills and asd absent from main, present on paper-bell | yes | Codex |
| A2 | 2026-10-04 | Full mode, module B, autonomous gates | interactive gate questions | explicit user autonomy; inherited CLAUDE precedence | yes | Codex |
| A3 | 2026-10-04 | Fixed three-endpoint representation study | claim all 22; leaderboard pursuit | interpretable endpoints, fixed before results | yes before execution | Codex |
| A4 | 2026-10-04 | ADMET MAE instead of reaction first-hit metric | reuse N_pi | user explicitly replaces research domain; reactions incompatible with ADMET supervised prediction | yes | Codex |
| A5 | 2026-10-04 | Preserve framework interfaces; add domain adapter only | change shared discovery | Domain API supports typed numerical claims | yes | Codex |
| A6 | 2026-10-04 | Median fallback for two invalid test structures | delete rows or repair charges | structural audit; amendment A | yes before scores | Codex |
| Zeit | Agent | Entscheidung | Beleg |
|---|---|---|---|
| A7 | 2026-10-04 | Harden independent scorer with source grounding and frozen prediction hashes | trust prediction artifact labels | Red-Team memory-only tamper proof; all on-disk evidence currently valid | yes | Codex |
| 2026-10-04 02:50:27 | SCOUT | 304 Quellen, 0 gesperrt, 128 Befunde mit per Code bestätigtem Zitat | research/kb/admet/wissensstand.md |
| 2026-10-04 02:50:35 | INTEGRATOR | Runde 1: [F1] Wie gross ist das numerische Validierungs-MAE-Verhaeltnis Morgan/combined fuer solubility_aqsoldb? Berichte nur das unab | F1 hat den höchsten Value of Information. Die Frage nach dem Validierungs-MAE-Verhältnis Morgan/combined für solubility_aqsoldb ist die einzige der drei Fragen, |
| 2026-10-04 02:51:34 | INTEGRATOR | Runde 2: [F4] Bleibt das Morgan/combined-MAE-Verhältnis von 1,603 für solubility_aqsoldb bestehen, wenn die Scaffold-Splits durch zufä | F4 ist die einzige Frage, die die bereits geprüfte Zahl (Morgan/combined-MAE-Verhältnis 1,603 für solubility_aqsoldb) direkt angreift: Ob dieser Wert ein Artefa |
| 2026-10-04 02:54:57 | INTEGRATOR | Runde 3: [F2] Wie gross ist das numerische Validierungs-MAE-Verhaeltnis Morgan/combined fuer lipophilicity_astrazeneca? Berichte nur d | F2 hat unter den offenen Fragen den höchsten Value of Information: Neuheit 0,7 × Machbarkeit 1,0 ergibt 0,7, während F5 (0,34), F6 (0,32) und F7 (0,27) deutlich |
