# Entscheidungen

| ID | Zeit | Entscheidung | Alternativen | Evidenz | reversibel? | Owner |
|---|---|---|---|---|---|---|
| D1 | Sa 20:50 | Benchmark: Buchwald-Hartwig-Ausbeuten (`doylelab/rxnpredict`), Top-1 % als Treffer | GB1-Protein, eigene Gitter-Rechnungen | vollständig gemessen, lädt in 1 min, klassischer BO-Testfall | ja | A |
| D2 | Sa 21:00 | Baseline: Zufall + GP-EI; RF-EI verworfen | RF-EI | RF-EI schlechter als Zufall (0,70×, $p=0{,}85$) | ja | D |
| D3 | Sa 21:16 | 1 Person Outreach an Forscher, 3 Personen Framework | 4 Personen Framework | externe Bewertung = externe Validierung | ja | A |
| D4 | Sa 21:31 | Vier Pflicht-Prüfungen; e-Werte, Conformal, EVPI, Sobol, Pooling bewusst weggelassen | alles einbauen | nur Methoden mit sicherem Nutzen | ja | D |
| D5 | Sa 21:33 | Bau in Claude Code lokal, gemeinsames Repo | Bau im Cloud-Chat | Lean, Databricks und APIs sind dort blockiert | ja | A |
