# ml_optscale: Verifier-Gated Lab für Optimierung und Skalierungsgesetze

Anwendung des Frameworks (`docs/FRAMEWORK.md`, Skill `verifier-gated-lab`) auf das Thema „Optimierung und Skalierungsgesetze“
(Adam, Muon, Shampoo, LR-Schedules, heavy-tailed Noise, Edge of Stability, μP-Transfer, Exponenten aus Daten-Spektren).

**Paper:** [`projects/optscale/paper.md`](projects/optscale/paper.md) (LaTeX: `paper.tex`). Jeder Satz zitiert eine `claim_id`;
Belege in `paper_belege.json`, Prüfprotokoll am Ende des Papers. Verworfene erste Fassung: `paper_v1.md` (Grund in `decisions.md`).

## Ablauf und Stand
| Schritt | Ergebnis |
|---|---|
| Prüfer + Selbsttest (`asd/domains/optscale_domain.py`) | 18/18 bestanden (wahre, falsche, Randfälle, Regelverletzung) |
| Scout (arXiv + Europe PMC) | 328 Quellen, 89 Befunde mit per Code bestätigtem Wortzitat (`research/kb/optscale/`) |
| Labor (18 Runden, präregistriert) | 18 geprüfte Aussagen, davon 3 vom Red-Team angefochten; Kosten 8,86 USD |
| Benjamini-Hochberg (`asd/bh_optscale.py`) | m = 20 Optimierer-Vergleiche, 11 nach Korrektur signifikant |
| Paper (`asd/paper.py`) | 72 Claims zitiert, 0 verbleibende Verstöße des Halluzinations-Gates |

Steuerung durch die Forschungsleitung (Fragenauswahl, nie Prüfer-Kriterien) ist in `projects/optscale/decisions.md` und als
datierte Nachträge in `projects/optscale/prereg.md` dokumentiert.

## Reproduzieren
```bash
pip install numpy scipy pandas scikit-learn sympy mpmath
python -m asd.selftest optscale                     # Prüfer muss bestehen (~2 min)
# Laborzustand: projects/optscale/state.json, runde*.json; alle Agenten-Antworten mit Prompt in cache/llm/
python -m asd.bh_optscale                           # BH-Korrektur -> projects/optscale/zusatz_claims.json
ASD_LLM=replay python -m asd.paper --domain optscale --titel "Spektren, Rotation und Breite: ein verifikator-gesteuertes Agentenlabor zu Optimierern und Skalierungsgesetzen" --autoren "Verifier-Gated Discovery Lab, Team Ninja Turtles" --affiliation "Hack-Nation 2026, Challenge 3"
```

## Framework-Änderungen in dieser Kopie
- `asd/paper.py`: f-String-Fehler für Python < 3.12 behoben; Red-Team-Claims tragen die Evidenzstufe der Domäne statt pauschal
  `computed_rigorous`; Schreib-Regel „nicht bestandene Gegenprüfung belegt nicht das Gegenteil“; optionale `zusatz_claims.json`.
- Bekannte Schwäche (nicht geändert, im Paper berichtet): Das Red-Team markiert eine Aussage als angefochten, sobald irgendeine
  Gegenprüfung besteht, auch wenn sie mit der Aussage vereinbar ist (R15, R18).
