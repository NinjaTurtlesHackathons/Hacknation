# Verifier-Gated Discovery Lab: Anleitung

Ein agentisches Forschungslabor, das in **jeder** Domäne funktioniert, in der sich Aussagen durch Rechnung, Simulation oder
Messung prüfen lassen. Kernidee: **Agenten schlagen vor, Code prüft.** Kein LLM entscheidet, was wahr ist.

Belegt im Projekt selbst (präregistriert, `prereg.md`):
- **H3:** Auf 12 Fragen aus einem Paper, das nach dem Trainingsstand erschien, kam das Framework auf 36/36 richtig und 0 falsch.
  Claude pur: 50 % richtig, 36 % falsch. Claude mit eigenem Python: 72 % richtig, 22 % falsch.
- **H4:** Die kostenoptimierte Kaskade kam auf 35/36 richtig bei 37 % der Kosten. Der eine Fehler deckte ein Schlupfloch im
  Prüfer auf (Agent setzte seine Toleranz selbst). Es ist inzwischen geschlossen und im Selbsttest abgesichert.

## 1. Architektur

```
            literature/ (eigene PDFs/MD)    arXiv + Europe PMC
                          \                 /
SCOUT (asd/research.py) ── Zitat-Prüfer (Code) ── Leck-Filter ──> Wissensstand (nur Befunde mit bestätigtem Wortzitat)
                                                                     │
INTEGRATOR (asd/lab_loop.py) wählt die nächste Frage (Value of Information) ── PRÄREGISTRIERUNG (projects/<d>/prereg.md)
                                                                     │
FORSCHER-KASKADE (asd/discovery.py): Haiku -> Haiku -> Sonnet -> Sonnet, stoppt bei erster geprüfter Behauptung
   plant Experimente ── LAB = domain.run_op() ── stellt getypte, ausführbare Behauptung auf
                                                                     │
PRÜFER = domain.check() (Code, unabhängige Nachrechnung, feste Toleranzen) ── Selbsttest muss vorher bestanden sein
                                                                     │
RED-TEAM: Gegen-Prüfungen, die bestehen müssten, wenn die Aussage falsch wäre ── LERN-AGENT: Folgefragen
                                                                     │
PAPER (asd/paper.py): Halluzinations-Gate (jede Zahl muss in einer zitierten, geprüften Aussage stehen)
```

| Datei | Rolle | domänenspezifisch? |
|---|---|---|
| `asd/domains/base.py` | Schnittstelle `Domain` | definiert sie |
| `asd/domains/<name>_domain.py` | **deine Domäne**: Experimente, Prüfer, Selbsttest | **ja, nur hier** |
| `asd/selftest.py` | Pflicht-Selbsttest des Prüfers | nein |
| `asd/lab_loop.py` | Labor-Schleife: Scout, Integrator, Kaskade, Red-Team, Lernen | nein |
| `asd/discovery.py` | Forscher-Agenten, Kaskade, Abstimmung | nein |
| `asd/research.py` | Scout: Suche, Sichtung, Extraktion, Zitat-Prüfer, Leck-Filter | nein |
| `asd/writer.py`, `asd/paper.py` | Paper mit Halluzinations-Gate, LaTeX/PDF | nein |
| `asd/llm.py` | LLM über `claude -p` (Pro/Max-Abo) oder API, mit Cache | nein |
| `asd/stats.py`, `prereg.md` | Permutationstest, Bootstrap, Benjamini-Hochberg, Präregistrierung | nein |

Beispiel-Domänen: `lattice_domain.py` (numerische Prüfer, Suleman 2026) und `proofreading_domain.py` (exakte Zertifikate in
rationaler Arithmetik plus rigorose Intervalle).

## 2. Eigenes Paper in einem anderen Fach: 6 Schritte

```bash
git clone <repo> && cd HackNation-Ninja-Turtles
pip install numpy scipy pandas scikit-learn sympy python-flint networkx mpmath
claude --version              # Claude Code muss eingeloggt sein (Pro-Plan reicht)

python -m asd.new_domain meinthema               # 1. Gerüst asd/domains/meinthema_domain.py
#   2. check() + selftest() ausfüllen  (VERIFIZIERER ZUERST)
python -m asd.selftest meinthema                 # 3. muss BESTANDEN melden, sonst startet nichts
#   4. run_op(), kontext, primitive_doc, claim_doc ausfüllen; eigene PDFs/Notizen nach literature/
python -m asd.lab_loop --domain meinthema --recherche --runden 4 --budget-usd 2   # 5. Labor laufen lassen
python -m asd.paper --domain meinthema --titel "..." --autoren "A, B" --affiliation "ETH Zürich"  # 6. Paper
```
Ergebnis unter `projects/meinthema/`: `state.json`, `prereg.md`, `decisions.md`, `lab_report.md`, `runde*.json`, `paper.md/.tex/.pdf`.

## 2a. Recherche (Scout) im Detail

`--recherche` startet die große Recherche, bevor das Labor forscht:
- 40 LLM-Suchanfragen plus die Klassiker aus `recherche_klassiker` (gezielt nach Autor und Titel)
- Abruf aus arXiv, Europe PMC und Crossref (DOI als Tool-Beleg), dazu eigene Dateien aus `literature/`
- Zitationskette: die Referenzlisten der 15 relevantesten Paper werden über Crossref aufgelöst
- Sichtung aller Treffer (Haiku), Extraktion aus den 150 relevantesten (Sonnet), jedes Wortzitat per Code im Abstract geprüft
- Evidenzstatus je Befund (bewiesen / numerisch / experimentell / vermutet) → `research/kb/<domain>/known_results.md`
- Leck-Filter: Quellen mit Wörtern aus `recherche_sperre` werden gesperrt (z. B. das Paper mit dem Antwortschlüssel)
Ergebnis: `research/kb/<domain>/wissensstand.md`, `known_results.md`, `kb.json` (Korpus, Scores, alle Befunde). Die geprüften
Befunde gehen sortiert nach Evidenzstatus in den Kontext aller Agenten. `--recherche-neu` wiederholt den Scout.

## 3. Was eine gute Domäne ausmacht (sonst wird das Framework schlecht)

1. **Der Prüfer ist das Produkt.** Er rechnet unabhängig nach: andere Auflösung, andere Methode oder exakt. Am besten liefert er
   ein Zertifikat (rationale Arithmetik, Intervallarithmetik, Lean), sonst ehrlich `observed` bzw. `statistical`.
2. **Toleranzen gehören dem Prüfer.** Lies nie `toleranz`, `genauigkeit` o. Ä. aus der Behauptung des Agenten.
3. **Der Selbsttest enthält wahre UND falsche Aussagen,** möglichst knapp an der Grenze (z. B. 1 % unter einem bekannten Wert)
   und mindestens eine Regelverletzung. Jeder gefundene Fehler wird als neuer Selbsttest-Fall eingetragen.
4. **Kein Leck.** `kontext`, `primitive_doc` und `claim_doc` enthalten keine Antworten. Quellen mit dem Antwortschlüssel gehören
   in `recherche_sperre`.
5. **Prüfungstypen sind schmal und eindeutig:** „Wert von X bei Y“, „Vorzeichenwechsel in [a, b]“, „Punkt erreichbar“,
   „Minimum ist Z“. Keine Freitext-Prüfungen.
6. **Experimente scheitern weich:** `{"fehler": ...}` statt Exception, damit die Agenten daraus lernen.
7. **Benennungen sind ehrlich:** Gleitkomma heißt „numerisch“ bzw. „Kandidat“, ein Theorem nur mit Zertifikat. `level()` gibt
   die Stufe an.

## 4. Kosten auf dem Pro-Plan

- `asd/llm.py` ruft `claude -p` ohne Tools in einem leeren Verzeichnis auf und nutzt damit das eigene Abo, ohne API-Key.
- Die Kaskade beginnt mit Haiku und nimmt Sonnet nur, wenn nötig. Eine Runde kostet typischerweise 0,05–0,20 USD.
  `--budget-usd` stoppt die Schleife.
- `ASD_MODEL=haiku` macht alles billiger, `ASD_MODEL=sonnet` ist der Standard. Mit API-Key: `ASD_LLM=api`.
- Alle Antworten liegen unter `cache/llm/`. Ein zweiter Lauf mit gleichen Prompts kostet nichts (`ASD_LLM=replay`
  erzwingt reines Abspielen).
- Bei Rate-Limits des Pro-Plans `--runden` klein halten und die Schleife später fortsetzen: Der Zustand liegt in
  `state.json`, ein neuer Aufruf macht weiter.

## 5. Regeln, die das Labor erzwingt

- Selbsttest nicht bestanden → kein Start.
- Jede Runde wird vor dem Experiment präregistriert (`prereg.md`). Negative Ergebnisse werden genauso protokolliert.
- Eine Aussage gilt nur, wenn `domain.check` besteht **und** die Antwort zur Prüfung passt (`consistent`).
- Red-Team: Besteht eine Gegen-Prüfung, wird die Aussage als „angefochten“ markiert und nicht als Resultat geführt.
- Literatur nur mit per Code bestätigtem Wortzitat; Paper-Sätze nur mit `claim_id`; Zahlen nur, wenn sie in der zitierten
  Aussage stehen.
