---
name: verifier-gated-lab
description: "Agentisches Forschungslabor mit Code-Prüfer (Verifier-Gated Discovery Lab) aus diesem Repo nutzen, um in einem beliebigen Fachgebiet geprüfte Resultate zu finden und ein Paper zu schreiben. Verwenden, wenn jemand eine neue Forschungsdomäne anlegen, das Labor laufen lassen, Ergebnisse zertifizieren oder ein Paper aus Labor-Ergebnissen erzeugen will. Nicht für reine Literaturfragen ohne Rechnung oder Experiment."
---

# Verifier-Gated Discovery Lab

Lies zuerst `docs/FRAMEWORK.md` vollständig. Diese Datei sagt dir, wie du es benutzt. Halte dich an die Reihenfolge.

## Grundregel
Agenten (auch du) schlagen nur vor. Wahr ist nur, was `domain.check()` (Code) bestätigt. Du formulierst nie selbst ein
Resultat ins Paper, das nicht als geprüfte Aussage in `projects/<domain>/state.json` steht.

## Ablauf
1. **Domäne klären.** Frage, falls unklar: Welche Größen? Was ist ein Experiment (Simulation, Rechnung, Daten)? Was ist eine
   prüfbare Aussage? Gibt es bekannte Anker (wahre Werte) und bekannte Falschaussagen für den Selbsttest?
2. **Gerüst:** `python -m asd.new_domain <name>`. Arbeite in `asd/domains/<name>_domain.py`. Vorbilder:
   `proofreading_domain.py` (exakte Zertifikate) und `lattice_domain.py` (numerische Nachrechnung).
3. **Prüfer zuerst:** `check()` und `selftest()` schreiben, dann `python -m asd.selftest <name>`. Nicht weitermachen, bevor
   BESTANDEN dasteht. Mindestens 2 wahre, 2 falsche Aussagen, dazu eine Regelverletzung. Toleranzen fest im Prüfer.
4. **Experimente und Kontext:** `run_op`, `kontext`, `primitive_doc`, `claim_doc`. Kein Leck: keine Antworten im Kontext.
   Quellen, die die Antwort enthalten, in `recherche_sperre`.
5. **Präregistrieren**, falls ihr einen Vergleich oder Benchmark macht: Abschnitt in `prereg.md` committen, BEVOR gerechnet wird.
6. **Labor:** `python -m asd.lab_loop --domain <name> --recherche --runden 4 --budget-usd 2`. Lies danach `lab_report.md`,
   `decisions.md` und die Red-Team-Befunde in `state.json`.
7. **Prüfer härten:** Jeder Fehler und jedes Schlupfloch, das du findest, wird ein neuer Selbsttest-Fall. Dann erneut laufen lassen.
8. **Paper:** `python -m asd.paper --domain <name> --titel "..." --autoren "..." --affiliation "..."`. Das Halluzinations-Gate
   entfernt unbelegte Sätze. Prüfe das Prüfprotokoll am Ende von `paper.md`.

## Verbote
- Keine Toleranz, Genauigkeit oder Auflösung aus der Behauptung des Agenten übernehmen.
- Keine Zahl, kein Theorem und keine Referenz im Paper ohne geprüfte Aussage bzw. Zitat-Beleg.
- Keine Stufe überspringen: `observed` → `computed_rigorous` (Zertifikat) → `proved_lean`. Gleitkomma = „numerisch“.
- Präregistrierte Kriterien nach dem Lauf nicht ändern. Abweichungen kommen als datierter Nachtrag in `prereg.md`.
- Negative Ergebnisse nicht weglassen.

## Kosten (Pro-Plan)
`claude -p` nutzt das Abo. Die Kaskade beginnt mit Haiku. `--budget-usd` setzt eine Obergrenze, `cache/llm/` macht
Wiederholungen kostenlos. Bei Rate-Limit: später mit demselben Befehl fortsetzen.
