"""Unabhängiger Scorer für den Replay-Benchmark: prüft jede als Treffer gezählte Behauptung erneut DIREKT mit dem Verifier
(asd.verify.check), ohne den Benchmark-Code (Zähler, Treffer-Logik) zu benutzen.  python benchmarks/score_independent.py"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asd import verify  # noqa: E402

ZIEL, TOL = 1.249621, 2e-4
rows = []
for f in sorted(glob.glob("results/replay_lattice/*.json")):
    r = json.load(open(f))
    if not r.get("treffer"): continue
    c = r.get("treffer_claim")
    if not c: rows.append((os.path.basename(f), "ohne protokollierte Behauptung (Lauf vor H8)", None)); continue
    ok, why, ev = verify.check(c)
    unabhaengig = bool(ok) and c.get("typ") == "grenzwert" and c.get("groesse") == "y_inf" and abs(float(c["erwartet"]) - ZIEL) <= 2 * TOL
    rows.append((os.path.basename(f), why[:90], unabhaengig))
gepr = [x for x in rows if x[2] is not None]
out = {"treffer_gesamt": len(rows), "unabhaengig_geprueft": len(gepr), "bestaetigt": sum(1 for x in gepr if x[2]),
       "abweichend": [x[0] for x in gepr if not x[2]], "ohne_behauptung": [x[0] for x in rows if x[2] is None]}
json.dump(out, open("results/score_independent.json", "w"), indent=1, ensure_ascii=False); print(json.dumps({k: v for k, v in out.items() if k != "ohne_behauptung"}, ensure_ascii=False))
