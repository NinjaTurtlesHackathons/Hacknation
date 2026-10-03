# Verifier-Gated Discovery Lab (Hack-Nation, Challenge #3)

**Agenten schlagen vor, Code prüft.** Ein agentisches Forschungslabor für jede Domäne, in der sich Aussagen durch Rechnung,
Simulation oder Messung prüfen lassen. Vollständige Anleitung: **[docs/FRAMEWORK.md](docs/FRAMEWORK.md)**. In Claude Code lädt der
Skill `verifier-gated-lab` (`.claude/skills/`) die Anleitung automatisch.

```bash
python -m asd.new_domain meinthema                    # neue Domäne anlegen
python -m asd.selftest meinthema                      # Prüfer muss bestehen
python -m asd.lab_loop --domain meinthema --recherche --runden 4 --budget-usd 2
python -m asd.paper --domain meinthema --titel "..." --autoren "..." --affiliation "ETH Zürich"
```

Präregistrierte Ergebnisse (`prereg.md`, Rohdaten in `results/`):
| Bedingung (12 Fragen aus Suleman 2026, je 3 Läufe) | richtig | falsch | Kosten/Frage |
|---|---|---|---|
| Claude pur | 50 % | 36 % | 0,02 USD |
| Claude mit eigenem Python | 72 % | 22 % | 0,03 USD |
| Framework (4 Forscher + Code-Prüfer) | 100 % | 0 % | 0,21 USD |
| Framework, Kaskade (Haiku zuerst) | 97 % | 3 % | 0,08 USD |

Weitere Befunde: KI- und Literatur-Vorwissen als GP-Prior helfen der Bayes'schen Optimierung nicht (H1, H5, beide präregistriert);
fünf geprüfte numerische Befunde zu offenen Fragen aus Suleman 2026 (`results/explore/`).

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
