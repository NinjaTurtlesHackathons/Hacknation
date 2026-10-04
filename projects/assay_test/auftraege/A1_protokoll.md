# Versuchsauftrag A1

**Hypothese (präregistriert 2026-10-04T01:22:24):** Der Zusatz des Kofaktors bei 37C erhöht die Enzymaktivität [RFU/min] gegenüber 37C ohne Kofaktor.

**Messgröße:** Aktivität [RFU/min]
**Replikate je Gruppe:** 8

## Gruppen

- ohne_enzym: {"temperatur": "37C", "kofaktor": "ohne"}
- referenz: {"temperatur": "37C", "kofaktor": "ohne"}
- 37C_ohne_kofaktor: {"temperatur": "37C", "kofaktor": "ohne"}
- 37C_mit_kofaktor: {"temperatur": "37C", "kofaktor": "mit"}

## Durchführung

1. Proben in der Reihenfolge `lauf_nr` aus `A1_messung.csv` messen (randomisiert).
2. Die messende Person kennt nur die `probe_code`; den Schlüssel nicht weitergeben (Verblindung).
3. Messwert in `messwert` eintragen, Einheit wie oben. Nichts löschen; Ausfälle leer lassen und in `bemerkung` begründen.
4. Datei speichern und die Labor-Schleife erneut starten. Die Auswertung ist vorab festgelegt:

   einseitiger Permutationstest (20000 Permutationen, Seed 12345), alpha 0.05, Bootstrap-95-%-KI, Benjamini-Hochberg über alle Tests des Projekts, Kontrollen-Check {'negativ': 'ohne_enzym', 'positiv': 'referenz'}
