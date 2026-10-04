"""Nachtrag: Teilprüfungen einer bestandenen Mehrfach-Antwort, die vor der Korrektur in lab_loop nur mit ihrer ersten Prüfung
als Claim eingetragen wurden, werden erneut geprüft (Code-Prüfer) und als eigene Claims nachgetragen (mit Red-Team und Neuheit).
  python -m asd.nachtrag_teilpruefungen <domain> <runde>"""
import json, sys
from .domains.base import get_domain
from .lab_loop import Project, red_team, now

dom, runde = sys.argv[1], int(sys.argv[2]); D = get_domain(dom); P = Project(dom); D.projekt = dom
res = json.load(open(f"{P.dir}/runde{runde}.json")); ps = [x for x in (res["antwort"].get("pruefungen") or []) if isinstance(x, dict)]
base = f"{D.name}-R{runde}"; frage = next(c["frage"] for c in P.s["claims"] if c["id"] == base)
for j, p in enumerate(ps[1:], 1):
    cid = f"{base}{'abcdefghijklmnopqrstuvwxyz'[j]}"
    if any(c["id"] == cid for c in P.s["claims"]): continue
    ok, grund, _ = D.check(p)
    print(cid, ok, grund[:200], flush=True)
    if not ok: continue
    rt = red_team(P, D, frage, dict(res["antwort"], pruefung=p, pruefungen=None), f"{runde}{j}")
    for x in rt: x["widerspruch"] = bool(x["bestanden"] and D.widerspricht(p, x["pruefung"]))
    ang = [x for x in rt if x["widerspruch"]]
    c = {"id": cid, "frage": frage, "text": D.describe(p), "interpretation_ungeprueft": str(res["antwort"].get("antwort")), "pruefung": p, "grund": grund,
         "level": D.level(p), "status": "angefochten" if ang else "bestätigt", "red_team": rt, "runde": runde, "relevanz": D.relevanz(p), "nachtrag": True}
    P.s["claims"].append(c)
    if not ang:
        from .novelty import check_claim
        try: c["neuheit"] = check_claim(D, c, salt=cid)
        except Exception as e: c["neuheit"] = {"status": "nicht_geprueft", "grund": str(e)[:120]}
    P.append("decisions.md", f"| {now()} | NACHTRAG | {cid}: Teilprüfung {j + 1} der Antwort aus Runde {runde} erneut geprüft und als eigener Claim eingetragen | Korrektur lab_loop (vorher nur erste Teilprüfung) |")
    P.save(); print(cid, c["status"], (c.get("neuheit") or {}).get("status"), flush=True)
