"""Benjamini-Hochberg über alle `vergleich`-Prüfungen der Domäne optscale (präregistriert, q = 0,1, m = alle durchgeführten
Vergleiche einschließlich Red-Team). Liest nur die Prüfer-Begründungen aus state.json und schreibt projects/optscale/zusatz_claims.json.
  python -m asd.bh_optscale"""
import json, re
from .stats import bh
from .domains.base import get_domain

D = get_domain("optscale")

S = "projects/optscale/state.json"
PAT = re.compile(r"Prüfer: (\S+) \(beste LR 2\^(-?\d+)\) vs (\S+) \(beste LR 2\^(-?\d+)\).*?Verhältnis ([\d.]+).*?p = ([\d.]+)")


def main():
    s = json.load(open(S)); tests = {}
    for c in s["claims"]:
        quellen = [(c["id"], c["grund"])]
        for j, r in enumerate(c.get("red_team", [])):                     # Red-Team-Begründungen sind in state.json gekürzt:
            g = r["grund"]                                                # vollständige Begründung durch erneute (deterministische) Prüfung
            if r["pruefung"].get("typ") == "vergleich" and "p = " not in g: g = D.check(r["pruefung"])[1]
            quellen.append((f"{c['id']}-RT{j + 1}", g))
        for cid, g in quellen:
            for part in g.split(" | "):
                m = PAT.search(part)
                if m: tests.setdefault(part, {"quelle": cid, "a": m.group(1), "b": m.group(3), "ratio": float(m.group(5)), "p": float(m.group(6))})
    T = list(tests.values()); rej, adj = bh([t["p"] for t in T], q=0.1)
    for t, r, a in zip(T, rej, adj): t.update(bh_signifikant=bool(r), p_adj=round(float(a), 4))
    n_sig = sum(t["bh_signifikant"] and t["ratio"] < 0.9 for t in T)
    zeilen = "; ".join(f"{t['quelle']}: {t['a']} vs {t['b']}, Verhältnis {t['ratio']}, p = {t['p']}, p_adj = {t['p_adj']}" for t in T)
    C = [{"claim_id": "C-bh", "level": "statistical", "status": "bestätigt",
          "text": (f"Benjamini-Hochberg (präregistriert, q = 0.1) über alle m = {len(T)} durchgeführten Optimierer-Vergleiche des Prüfers "
                   f"(Hauptprüfungen und Red-Team, eindeutige Tests; Prüfungen mit Lernraten-Optimum am Gitterrand gelten als nicht entscheidbar und zählen nicht als Test): {n_sig} davon bleiben nach Korrektur signifikant mit Verhältnis unter 0.9. "
                   f"Einzeln: {zeilen}.")}]
    json.dump(C, open("projects/optscale/zusatz_claims.json", "w"), ensure_ascii=False, indent=1)
    print(C[0]["text"])


if __name__ == "__main__":
    main()
