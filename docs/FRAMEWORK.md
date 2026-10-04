# Verifier-Gated Discovery Lab: Anleitung

Ein agentisches Forschungslabor, das in **jeder** Domäne funktioniert, in der sich Aussagen durch Rechnung, Simulation oder
Messung prüfen lassen. Kernidee: **Agenten schlagen vor, Code prüft.** Kein LLM entscheidet, was wahr ist.

Belegt im Projekt selbst (präregistriert, `prereg.md`):
- **H3:** Auf 12 Fragen aus einem Paper, das nach dem Trainingsstand erschien, kam das Framework auf 36/36 richtig und 0 falsch.
  Claude pur: 50 % richtig, 36 % falsch. Claude mit eigenem Python: 72 % richtig, 22 % falsch.
- **H4:** Die Kaskade (kleines Modell zuerst) kam auf 35/36 richtig. Der eine Fehler deckte ein Schlupfloch im
  Prüfer auf (Agent setzte seine Toleranz selbst). Es ist inzwischen geschlossen und im Selbsttest abgesichert.

## 1. Architektur

```
            literature/ (eigene PDFs/MD)    arXiv + Europe PMC
                          \                 /
SCOUT (asd/research.py) ── Zitat-Prüfer (Code) ── Leck-Filter ──> Wissensstand (nur Befunde mit bestätigtem Wortzitat)
                                                                     │
INTEGRATOR (asd/lab_loop.py) wählt die nächste Frage (Value of Information) ── PRÄREGISTRIERUNG (projects/<d>/prereg.md)
                                                                     │
FORSCHER-KASKADE (asd/discovery.py): Haiku -> Haiku -> Sonnet -> Sonnet, stoppt bei erster geprüfter Behauptung,
   danach STÄRKE-MAXIMIERUNG: bis zu 2 Versuche für eine strengere/allgemeinere Aussage (Domain.staerke entscheidet)
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
| `asd/phases.py` | Phasen-Gates 0-7 im Code (Labor verlangt 1-4, Paper 1-6) | nein |
| `asd/verifier_redteam.py` | Fallen für den Prüfer (plausible Falschaussagen), Urteile → Selbsttest | nein |
| `asd/novelty.py` | Neuheitsprüfung je Claim mit Wortzitat-Nachweis | nein |
| `asd/domains/experimental.py` | Basisklasse für Nasslabor-Domänen: Versuchsaufträge, statistischer Prüfer | nein |
| `asd/stats.py`, `prereg.md` | Permutationstest, Bootstrap, Benjamini-Hochberg, Präregistrierung | nein |

Beispiel-Domänen: `lattice_domain.py` (numerische Prüfer, Suleman 2026) und `proofreading_domain.py` (exakte Zertifikate in
rationaler Arithmetik plus rigorose Intervalle).

## 2. Eigenes Paper in einem anderen Fach

**Verbindlicher Ablauf mit Abnahmenachweisen: [`docs/WORKFLOW_PROMPT.md`](WORKFLOW_PROMPT.md)** (als erste Nachricht in Claude Code
einfügen). Kurzfassung in 6 Schritten:

```bash
git clone <repo> && cd HackNation-Ninja-Turtles
pip install numpy scipy pandas scikit-learn sympy python-flint networkx mpmath
claude --version              # Claude Code muss eingeloggt sein (Pro-Plan reicht)

python -m asd.new_domain meinthema               # 1. Gerüst asd/domains/meinthema_domain.py
#   2. check() + selftest() ausfüllen  (VERIFIZIERER ZUERST)
python -m asd.selftest meinthema                 # 3. muss BESTANDEN melden, sonst startet nichts
#   4. run_op(), kontext, primitive_doc, claim_doc ausfüllen; eigene PDFs/Notizen nach literature/
python -m asd.lab_loop --domain meinthema --recherche --runden 0              # 5a. große Recherche (Phase 1)
#   Lückenkarte projects/meinthema/lueckenkarte.md + fragen.json, prereg.md committen (Phasen 2, 4)
python -m asd.verifier_redteam meinthema         # Prüfer gegen Fallen testen (Phase 3)
python -m asd.phases meinthema                   # zeigt, welche Phase offen ist; Labor startet erst bei 1-4 OK
python -m asd.lab_loop --domain meinthema --fragen projects/meinthema/fragen.json --runden 6   # 5b. Labor
python -m asd.novelty meinthema                  # Neuheitsprüfung (Phase 6)
python -m asd.paper --domain meinthema --autoren "A, B" --affiliation "ETH Zürich"   # 6. Paper (en, Titel aus Story-Plan)
python -m asd.recheck meinthema                  # alle Zertifikate mit einem Befehl reproduzieren
```
Ergebnis unter `projects/meinthema/`: `state.json`, `prereg.md`, `decisions.md`, `lab_report.md`, `runde*.json`,
`paper.md/.tex/.pdf`, `references.bib`, `pruefprotokoll.json`, `referee_report.md`.

## 2c. Experimentelle Fächer (Nasslabor): das Framework plant und wertet aus, Menschen messen

Für Domänen, in denen das Experiment nicht im Rechner läuft, von `ExperimentalDomain` erben (Vorlage: `asd/domains/assay_demo_domain.py`).
Man deklariert nur Faktoren, Messgröße, Kontrollen und Mindest-Replikate. Ablauf:
1. Der Forscher-Agent schlägt eine Hypothese vor; der Code prüft das Design (Kontrollen vorhanden, Replikate ≥ Minimum, nur erlaubte Faktorstufen).
2. Es entsteht ein **präregistrierter Versuchsauftrag** `projects/<d>/auftraege/A<n>`: `_protokoll.md` (Anleitung), `_messung.csv`
   (randomisierte Laufreihenfolge, nur verblindete Probencodes), `_schluessel.json` (nicht an die messende Person geben).
3. Das Labor hält an. Menschen messen und tragen die Werte in die CSV ein.
4. Beim nächsten Start von `asd.lab_loop` wird ausgewertet: Daten-Hash beim ersten Lesen (spätere Änderung = Verstoß), fest vorab
   definierte Analyse: einseitiger Permutationstest (20 000 Permutationen, Seed 12345), Bootstrap-95-%-KI, Kontrollen-Check,
   Benjamini-Hochberg über ALLE Tests des Projekts (`tests.json`). Stufe `statistical`, nie „Theorem“.
5. Der Selbsttest des statistischen Prüfers läuft mit simulierten Daten (echte Effekte, Null-Effekte, kaputte Kontrollen) und
   kalibriert die Falsch-Positiv-Rate (muss ≤ 0,08 sein).
Zum Testen ohne Labor: `python -m asd.simulate_messung <projekt> A1 '{"gruppe": mittel, ...}'` (markiert alle Werte als SIMULIERT).

## 2d. Verbindliche Struktur im Code

Damit jeder ein hochwertiges Ergebnis bekommt, sind die Phasen nicht nur Text, sondern Code (`asd/phases.py`):
| Phase | Abnahme (automatisch geprüft) |
|---|---|
| 1 Recherche | ≥ 1000 Treffer, ≥ 100 gesichtet, ≥ 60 geprüfte Zitate, ≥ 8 Klassiker |
| 2 Lückenkarte | ≥ 5 Zeilen, davon ≥ 3 prüfbar |
| 3 Prüfer | Selbsttest bestanden (≥ 3 wahr / ≥ 3 falsch) und Prüfer-Red-Team ohne blockierenden Befund |
| 4 Präregistrierung | `prereg.md` committet |
| 5 Labor | jede Lückenfrage beantwortet oder als negatives Ergebnis mit Grund protokolliert |
| 6 Neuheit | jeder bestätigte Claim hat einen Neuheitsstatus |
| 7 Paper | PDF existiert, Prüfprotokoll mit 0 Verstößen |
`asd.lab_loop` verweigert den Start ohne Phasen 1-4, `asd.paper` ohne 1-6. `--ohne-gates` umgeht das nur mit Eintrag als
ABWEICHUNG in `decisions.md`.

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

## 2b. Form des Papers

Jedes Paper folgt der Form von Suleman, „Optimal lattices for a three-body power-law energy“ (2026). Sie ist in `asd/paper.py` als `SULEMAN_FORM` verbindlich hinterlegt:
- informativer Titel und dichtes Abstract mit den Zahlen
- „Summary of results“ als Liste am Ende der Einleitung
- nummerierte Theorem-, Proposition- und Lemma-Umgebungen, jeweils mit einem „Proof.“- bzw. „Certificate.“-Absatz
- eine Remark zur trusted base der computergestützten Teile
- Tabellen zertifizierter Daten
- Abbildungen, wo sie helfen (über `Domain.figures`, etwa Phasendiagramm, Front oder Klassifikation)
- nummerierte offene Fragen, Declarations, Anhang mit Methoden und Beweisdetails
Jede Domäne sollte in `figures()` mindestens eine aussagekräftige Abbildung aus geprüften Aussagen liefern.

Gliederung (fest): Abstract, Introduction, Model and assumptions (alle Parameter aus `Domain.parameter()`), Method, Results,
Negative results (mit Grund), Discussion, Declarations, **Appendix A: Agentic laboratory** (nur hier dürfen Agenten genannt werden),
**Appendix B: Provenance** (Tabelle Aussage → Prüfung → Stufe → Neuheit), **Appendix C: Verifier self-test**.
Weitere Pässe: Story-Plan (Kernfrage, Kernaussage, Titel), Editor-Pass mit Diff-Wächter (darf keine Zahl/Umgebung ändern),
Referee-Pass → `referee_report.md`. Sprache Standard Englisch (`--sprache de` möglich). Literatur als BibTeX, Metadaten
über Crossref/arXiv; nicht auflösbare Einträge werden als `[unverified]` markiert.

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

## 4. Praktisch auf dem Pro-Plan

- `asd/llm.py` ruft `claude -p` ohne Tools in einem leeren Verzeichnis auf und nutzt damit das eigene Abo, ohne API-Key.
- `ASD_MODEL=sonnet` ist der Standard, mit API-Key `ASD_LLM=api`.
- Alle Antworten liegen unter `cache/llm/`; `ASD_LLM=replay` erzwingt reines Abspielen.
- Bei Rate-Limits `--runden` klein halten und später fortsetzen: Der Zustand liegt in `state.json`.
- Inhaltliches Abbruchkriterium: `--stopp-ohne-fortschritt 3` beendet die Schleife nach 3 Runden ohne neuen bestätigten Claim.

## 5. Regeln, die das Labor erzwingt

- Selbsttest nicht bestanden → kein Start.
- Jede Runde wird vor dem Experiment präregistriert (`prereg.md`). Negative Ergebnisse werden genauso protokolliert.
- Eine Aussage gilt nur, wenn `domain.check` besteht **und** die Antwort zur Prüfung passt (`consistent`).
- Red-Team: Besteht eine Gegen-Prüfung, die der Aussage logisch widerspricht (`Domain.widerspricht`), wird sie „angefochten“
  und nicht als Resultat geführt. Nicht ausführbare Gegen-Prüfungen werden nur gezählt, nie als Claim berichtet.
- Faden-Logik: Der Integrator bleibt bei einer Fragenkette, solange sie in den letzten 2 Runden einen neuen Claim brachte,
  und bevorzugt offene Literaturfragen (`lit_offen`). Jede Entscheidung steht in `decisions.md`.
- Neuheit je Claim: bekannt / offen_laut_literatur / nicht_gefunden, nur mit per Code geprüftem Wortzitat.
- Literatur nur mit per Code bestätigtem Wortzitat; Paper-Sätze nur mit `claim_id`; Zahlen nur, wenn sie in der zitierten
  Aussage stehen.
