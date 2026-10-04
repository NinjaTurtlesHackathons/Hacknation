# Manual baseline (measured with a stopwatch, not estimated)

One JSON object per line in `manual.jsonl`, one line per measurement:

```json
{"schritt": "ergebnis_zu_entscheidung", "sekunden": 240, "person": "AS", "datum": "2026-10-04", "notiz": "read verifier output of O14, decide next question"}
```

Step types (same steps the lab is timed on by `python -m asd.metrics`):
- `ergebnis_zu_entscheidung`: read one verifier result, check it, decide and write down the next question.
- `zertifikat_nachrechnen`: recompute one exact certificate by hand / with a CAS.
- `frage_zu_claim`: from a question to a checked, typed claim.

At least 3 measurements per step type before a speedup is reported; `asd.metrics` labels it "measured, n=…, k person(s)".
