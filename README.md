# Verifier-Gated Discovery Lab (Hack-Nation, Challenge #3)

**Agenten schlagen vor, Code prüft.** Ein agentisches Forschungslabor für jede Domäne, in der sich Aussagen durch Rechnung,
Simulation oder Messung prüfen lassen. Vollständige Anleitung: **[docs/FRAMEWORK.md](docs/FRAMEWORK.md)**. In Claude Code lädt der
Skill `verifier-gated-lab` (`.claude/skills/`) die Anleitung automatisch.

```bash
python -m asd.new_domain meinthema                    # neue Domäne anlegen
python -m asd.selftest meinthema                      # Prüfer muss bestehen
python -m asd.lab_loop --domain meinthema --recherche --runden 0   # große Recherche
python -m asd.phases meinthema                        # welche Phase fehlt noch? (Labor startet erst bei 1-4 OK)
python -m asd.lab_loop --domain meinthema --fragen projects/meinthema/fragen.json --runden 6
python -m asd.novelty meinthema
python -m asd.paper --domain meinthema --autoren "..." --affiliation "ETH Zürich"
```
Experimentelle Fächer (Nasslabor): Domäne von `ExperimentalDomain` erben (Vorlage `asd/domains/assay_demo_domain.py`); das Labor
erzeugt präregistrierte, randomisierte, verblindete Versuchsaufträge, wartet auf die Messdaten und wertet sie mit fester Statistik aus.

Präregistrierte Ergebnisse (`prereg.md`, Rohdaten in `results/`):
| Bedingung (12 Fragen aus Suleman 2026, je 3 Läufe) | richtig | falsch |
|---|---|---|
| Claude pur | 50 % | 36 % |
| Claude mit eigenem Python | 72 % | 22 % |
| Framework (4 Forscher + Code-Prüfer) | 100 % | 0 % |
| Framework, Kaskade (Haiku zuerst) | 97 % | 3 % |

Weitere Befunde: KI- und Literatur-Vorwissen als GP-Prior helfen der Bayes'schen Optimierung nicht (H1, H5, beide präregistriert);
fünf geprüfte numerische Befunde zu offenen Fragen aus Suleman 2026 (`results/explore/`).



## Omnigent orchestration

**Agents propose, Omnigent orchestrates, only the code verifier accepts.** The lab (`asd/`) stays the source of truth (verifier
`Domain.check`, self-test, `state.json`, `prereg.md`); Omnigent (`omni/`, tested with omnigent 0.16.0) orchestrates the live discovery
workflow. Agents act only through the frozen harness `python -m asd.cli <command>`; every call is appended to
`projects/<project>/record.jsonl` (time, agent, command, input ids, output ids, result), so every decision can be reconstructed.

| Agent | Decision it owns | Tools (asd.cli) | Input | Output |
|---|---|---|---|---|
| `verifier-gated-lab` (lead, PI) | what runs next; when to stop or switch thread; reacts to surprises | `status`, `plan`, `fragen`; `sys_session_send`, `sys_read_inbox` | research goal | round decisions, final summary |
| `scout` (haiku, read-only) | which evidence is relevant | `wissen`, `fragen` | domain, project | evidence / claim ids, open question ids |
| `planner` (sonnet, read-only + `waehle`) | which of ≥2 code-generated rival experiments to run (cost in verifier calls vs. expected gain, budget); re-planning after a surprise | `options`, `waehle`, `reopen`, `plan`, `status` | question id / reopen request | chosen option id + rejected ids |
| `researcher` (sonnet) | experiments and the claim; **only agent allowed to call the verifier** | `doku`, `fragen`, `experiment`, `pruefe` | question id + option id | experiment ids, claim id (+ surprise flag) |
| `redteam` (**opus**, different model, read-only) | counter-checks that would pass if the claim were false | `status`, `doku`, `redteam` | claim id | counter-check ids, claim status |
| `learner` (haiku) | follow-up questions (generalisation > edge case > counterexample) | `wissen`, `folgefragen` | claim / round id | new question ids |
| `scribe` (sonnet) | building the paper — only after human approval | `python -m asd.paper` | domain, project | paper path |

Code-generated options: `asd/planner.py` (broad scan vs. deep certified computation, plus generalisation / edge case once a thread has a
confirmed claim). Surprises: `asd.cli pruefe` reports `ueberraschung: true` when a verified result contradicts a preregistered assumption
(`state.json: annahmen`); the planner then runs `asd.cli reopen` and re-plans.

**Policies** (`omni/config.yaml`, under `guardrails: policies:`; the lead's policies apply to every sub-agent):

| Policy | Type | Purpose |
|---|---|---|
| `cost_budget` | built-in `cost.cost_budget` | hard limit 40 USD, ASK at 10 and 20 USD |
| `spawn_bounds` | built-in `orchestration.spawn_bounds` | at most 3 `sys_session_send` dispatches per turn |
| `verifier_only` | CEL | DENY any direct write to `state.json` / `record.jsonl` / `projects/` (redirect, `tee`, `cp`, `mv`, `sed -i`, file write tools) — claims are stored only by `asd.cli pruefe` |
| `leak_guard` | CEL | DENY reading blocked sources (hold-out results, answer keys, pre-cutoff literature; paths/terms configurable, same list as `omni/leak_guard.json`) |
| `harness_only` | CEL | DENY shell commands other than the frozen harness (`python -m asd.cli`, `python -m asd.paper`) |
| `publish_gate` | CEL | ASK (human approval) before `asd.paper` or `git push` |
| `read_only` | built-in `orchestration.read_only_os` | scout, planner, redteam cannot write files |
| `no_pruefe` | CEL (per agent) | every agent except the researcher is denied `asd.cli pruefe` |
| `tool_call_cap` | built-in `safety.max_tool_calls_per_session` | researcher: at most 30 tool calls per session |

Offline check of all policy verdicts: `/root/omni-venv/bin/python benchmarks/omni_policy_check.py` (15/15).

**Run it** (Python ≥ 3.12 venv outside the repo: `pip install "omnigent>=0.16"`; the claude-sdk harness uses the local Claude login):
```bash
python -m asd.omni_setup --quelle proofreading --projekt omni_proofreading     # fresh project: copied state + assumption A1 + start question
omnigent run omni -p "Domain proofreading, project omni_proofreading, start question F20, 3 rounds."
python benchmarks/omni_watch.py <session_id>                                   # status, pending approvals, record.jsonl
```
Recorded run: [`runs/omnigent/2026-10-04/`](runs/omnigent/2026-10-04/README.md) — session logs of the lead and all 14 sub-sessions,
`record.jsonl`, `decisions.md`, and [`HIGHLIGHTS.md`](runs/omnigent/2026-10-04/HIGHLIGHTS.md) with timestamps: 12 policy DENYs (leak_guard,
verifier_only, harness_only), 4 parallel dispatches, 3 option choices, 1 verifier rejection, 3 confirmed claims, a surprise that reopened
assumption A1 and changed the plan, opus red team, and a `publish_gate` ASK approved by a human. Result of the run: 8 new exactly
certified violations of η ≥ e^(−2Δ); classification of the two-bound-state family now 50 proved / 11 violations / 27 open.

## Dauerbetrieb

`run_forever.py` lässt das Labor unbeaufsichtigt laufen: Zyklus = `asd.lab_loop --runden 5` → `asd.paper` (inkl. Referee-Durchgang)
→ Qualitätskriterium `asd/quality.py:publikationsreif`. Es stoppt erst, wenn ein bestätigtes, rigoros geprüftes Hauptresultat
existiert, das laut Literatur neu ist (offen_laut_literatur / nicht_gefunden), das Paper 0 Verstöße hat und der Referee keine schwere,
mit vorhandenen Claims behebbare Schwäche meldet; dann baut es `paper_final.pdf` und beendet sich. Sonst nach `--max-runden` (Default 200) Zyklen.
Abstürze werden mit Traceback nach `logs/<domain>/supervisor.log` geschrieben und neu gestartet (Zustand in `projects/<domain>/state.json`);
Rate-Limits/Quota werden exponentiell abgewartet (1, 2, 4 … 30 min), nie abgebrochen. Bleibt ein Faden 3 Runden ohne neuen Claim,
erzwingt das Labor einen Themenwechsel (`--themenwechsel`).

```bash
tmux new -s lab 'caffeinate -dims python run_forever.py --domain <name> --autoren "A, B" --affiliation "ETH Zürich"'
# Linux statt caffeinate:  systemd-inhibit python run_forever.py --domain <name>
tail -f logs/<name>/status.md      # eine Zeile pro Zyklus: Zeit, Zyklus, Laborrunden, bestätigte Claims, Hauptresultate, Neuheit, Referee, Kriterium
less logs/<name>/supervisor.log    # Abstürze, Neustarts, Wartezeiten
tmux attach -t lab                 # live zusehen (Ctrl-b d: wieder lösen)
```
Test der Robustheit: `python run_forever.py --domain lattice --max-runden 2 --runden-pro-zyklus 1 --ohne-gates --test-fehler`
(künstlicher Absturz, Rate-Limit im Kindprozess und 2 Rate-Limits im LLM-Aufruf; alle drei werden abgefangen).

---

## Teil 1: Buchwald-Hartwig-Validierung (ursprüngliche Pipeline)

Agenten schlagen Hypothesen und Experimente vor. Akzeptiert wird nur, was Gates, Statistik oder Lean bestätigen. Projektregeln: `CLAUDE.md`. Präregistrierung: `prereg.md`. Entscheidungen: `decisions.md`.

## Schnellstart
```bash
git clone --depth 1 https://github.com/doylelab/rxnpredict.git
pip install numpy pandas scipy scikit-learn
python run.py                 # 4 Policies × 20 Seeds × 3 Datensätze, Gates, Claims, Tabellen (~3 min auf 4 Kernen)
python dashboard.py           # dashboard/index.html, liest nur tables/*.csv
python paper.py               # paper/results.md, jeder Satz mit claim_id
lean lean/ENRandom.lean       # Lemma E[N_random] = (n+1)/(k+1), Lean 4 ohne Mathlib
```
Probelauf: `python run.py --seeds 3`. Ohne KI: `python run.py --policies random,gp_ei`.

## Aufbau
| Datei | Inhalt |
|---|---|
| `asd/data.py` | Datensatz, Treffer (Top-1 %), Sichten für die KI: `named` (Namen + SMILES) und `neutral` (Codes + Deskriptoren) |
| `asd/lab.py` | `Lab.run(i)`: einziger Zugang zu den Ausbeuten, jeder Aufruf geht in `experiments` |
| `asd/policies.py` | `random`, `gp_ei` (identisch zu `lab.py`), `hybrid`, `hybrid_neutral`; Schnittstelle `propose(history, rng)` |
| `asd/hypotheses.py` | Hypothesen-Agent: Prompt bauen, Antwort prüfen, `Hypothesis`, Vorwissen m(x) |
| `asd/hyptest.py` | eigener Test jeder KI-Hypothese auf 200 Zufallsexperimenten |
| `asd/stats.py` | gepaarter Permutationstest, Bootstrap-KI, Benjamini-Hochberg, exakte Momente von N |
| `asd/gates.py` | Gates G0–G7 inkl. H1, H2, Negativkontrollen, Lean |
| `asd/claims.py`, `asd/tables.py` | Claims aus Gate-Ergebnissen; die Tabellen `experiments`, `claims`, `gates` samt Validierung |
| `hypotheses/` | KI-Hypothesen mit Prompt, Rohantwort und Generator (Provenienz) |
| `lean/` | Lean-4-Beweis des Lemmas |
| `lab.py`, `results_selftest.json` | ursprünglicher Selbsttest (Referenz für Gate G2) |
