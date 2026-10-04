"""NUR FÜR TESTS: füllt die Mess-CSV eines Versuchsauftrags mit simulierten Werten (wahre Mittelwerte je Gruppe angeben).
Im echten Labor trägt ein Mensch die Messwerte ein.  python -m asd.simulate_messung <projekt> <A<n>> '{"gruppe": mittel, ...}' [--sd 1]"""
import argparse, csv, json
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("projekt"); ap.add_argument("auftrag"); ap.add_argument("mittel"); ap.add_argument("--sd", type=float, default=1.0)
a = ap.parse_args(); d = f"projects/{a.projekt}/auftraege"; codes = json.load(open(f"{d}/{a.auftrag}_schluessel.json")); mu = json.loads(a.mittel)
rows = list(csv.DictReader(open(f"{d}/{a.auftrag}_messung.csv"))); rng = np.random.default_rng(7)
for r in rows: r["messwert"] = f"{rng.normal(mu.get(codes[r['probe_code']], 0.0), a.sd):.3f}"; r["bemerkung"] = "SIMULIERT (Test)"
with open(f"{d}/{a.auftrag}_messung.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["lauf_nr", "probe_code", "messwert", "bemerkung"]); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} simulierte Messwerte eingetragen")
