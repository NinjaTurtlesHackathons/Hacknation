"""Klassifikation der Familie (<= 2 gebundene Zustände) aus den BESTÄTIGTEN Claims eines Projekts neu berechnen und als Fakten ablegen.
Jede Verletzung wird erneut exakt geprüft (check_erreichbar) und nur gezählt, wenn eta STRIKT unter e^{-2 Delta} = 1e-4 liegt.
  python -m asd.klassifikation --projekt omni_proofreading"""
import argparse, json, re
from fractions import Fraction
from .domains.proofreading_family import family
from .domains.proofreading_domain import check_erreichbar

ap = argparse.ArgumentParser(); ap.add_argument("--projekt", default="omni_proofreading"); a = ap.parse_args()
d = f"projects/{a.projekt}"; s = json.load(open(f"{d}/state.json")); alle = [x["name"] for x in family(2)]
bew, verl = set(), {}
for c in s["claims"]:
    if c.get("status") != "bestätigt": continue
    p = c["pruefung"]
    if p.get("typ") == "schranke_familie": bew |= set(p.get("mitglieder") or [])
    faelle = p.get("faelle", []) if p.get("typ") == "erreichbar_liste" else ([p] if p.get("typ") == "erreichbar" else [])
    for f in faelle:
        t = f.get("topologie")
        if not (isinstance(t, str) and t.startswith("fam2_")) or t in verl: continue
        ok, why, ev = check_erreichbar({"typ": "erreichbar", **f})
        m = re.search(r"eta = ([0-9.eE+-]+)", why)
        if ok and m and float(m.group(1)) < 1e-4: verl[t] = (float(m.group(1)), c["id"])
assert not (bew & set(verl)), f"Widerspruch: {bew & set(verl)}"
offen = [n for n in alle if n not in bew and n not in verl]
fk = json.load(open(f"{d}/fakten.json")); fk = [x for x in fk if x["id"] not in ("fakt-klassifikation", "fakt-verletzungen-eta")]
fk.append({"id": "fakt-klassifikation", "level": "computed_rigorous",
           "text": f"Klassifikation der {len(alle)} Topologien mit zwei gebundenen Zuständen (aus den bestätigten Claims neu berechnet, asd/klassifikation.py): "
                   f"{len(bew)} mit bewiesener Schranke eta >= e^-2Delta (Zertifikat b), {len(verl)} mit exakt zertifizierter Verletzung eta < e^-2Delta "
                   f"({', '.join(sorted(verl, key=lambda x: int(x.split('_')[1])))}), {len(offen)} offen."})
fk.append({"id": "fakt-verletzungen-eta", "level": "computed_rigorous",
           "text": "Exakte Fehlerraten der zertifizierten Verletzungen (rationale Raten, exakte Arithmetik; alle strikt unter e^-2Delta = 1e-4): " +
                   "; ".join(f"{t}: eta = {e:.6e} ({cid})" for t, (e, cid) in sorted(verl.items(), key=lambda x: int(x[0].split('_')[1])))})
json.dump(fk, open(f"{d}/fakten.json", "w"), ensure_ascii=False, indent=1)
erg = {"familie": "gebunden<=2", "topologien": len(alle), "bewiesen": len(bew), "verletzt": len(verl), "offen": len(offen),
       "verletzungen": sorted(verl, key=lambda x: int(x.split('_')[1])), "eta_min": min(e for e, _ in verl.values()) if verl else None, "projekt": a.projekt}
json.dump(erg, open(f"{d}/klassifikation.json", "w"), indent=1); print(json.dumps(erg, ensure_ascii=False))
