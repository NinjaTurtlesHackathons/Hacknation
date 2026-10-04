"""Deterministischer Abgleich der Neuheitslabels (nach asd.novelty). Das Urteil-LLM entscheidet bei mathematisch identischen
Aussagen nicht immer gleich. Regeln (kein LLM):
 1. Aussagen mit gleichem mathematischem Inhalt (Domain.inhalt(p)) bilden eine Gruppe.
 2. Stimmen alle Labels der Gruppe überein, bleibt es dabei. Sonst: Status 'uneinheitlich' für alle Mitglieder; die Belege
    (Quelle + Wortzitat der Treffer, Zahl der Fehlsuchen) werden aufgeführt. Nie wird daraus 'neu' gemacht.
 3. Antworten auf präregistrierte Anker-Fragen (fragen.json: "anker": true) erhalten 'reproduktion_anker', falls keine
    Literaturstelle mit Zitat gefunden wurde (bei Treffer bleibt 'bekannt').
  python -m asd.novelty_abgleich <domain>"""
import json, sys, time
from .domains.base import get_domain

dom = sys.argv[1]; D = get_domain(dom); p = f"projects/{dom}/state.json"; s = json.load(open(p))
anker = {q["frage"] for q in s["fragen"] if q.get("anker")}
gruppen = {}
for c in s["claims"]:
    if c.get("status") != "bestätigt" or not c.get("neuheit"): continue
    k = D.inhalt(c["pruefung"]) if hasattr(D, "inhalt") else json.dumps(c["pruefung"], sort_keys=True)
    gruppen.setdefault(k, []).append(c)
L = [f"# Abgleich der Neuheitslabels ({time.strftime('%Y-%m-%d')})", "", "| Gruppe (Claims) | Einzellabels | Ergebnis |", "|---|---|---|"]
for k, cs in gruppen.items():
    roh = [(c["id"], (c["neuheit"].get("roh_status") or c["neuheit"]["status"])) for c in cs]
    for c in cs: c["neuheit"].setdefault("roh_status", c["neuheit"]["status"])
    st = {x for _, x in roh}
    treffer = [c["neuheit"] for c in cs if c["neuheit"]["roh_status"] != "nicht_gefunden" and c["neuheit"].get("quelle")]
    if len(st) > 1:
        fehl = sum(1 for _, x in roh if x == "nicht_gefunden")
        for c in cs:
            c["neuheit"].update(status="uneinheitlich", quelle=treffer[0]["quelle"], zitat=treffer[0]["zitat"], fehlsuchen=fehl,
                                abgleich=f"{len(cs)} gleichwertige Prüfungen; {len(treffer)} mit Literaturtreffer, {fehl} ohne")
        erg = "uneinheitlich"
    else:
        erg = st.pop()
    if any(c["frage"] in anker for c in cs) and erg == "nicht_gefunden":
        for c in cs: c["neuheit"]["status"] = "reproduktion_anker"
        erg = "reproduktion_anker"
    L.append(f"| {', '.join(c['id'] for c in cs)} | {', '.join(f'{i}: {x}' for i, x in roh)} | {erg} |")
json.dump(s, open(p, "w"), ensure_ascii=False, indent=1)
open(f"projects/{dom}/neuheit_abgleich.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
