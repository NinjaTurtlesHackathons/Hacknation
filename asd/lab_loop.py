"""Labor-Schleife (domänenunabhängig): Selbsttest -> Scout -> [Integrator plant -> Präregistrierung -> Forscher-Kaskade ->
Prüfer -> Red-Team -> Lernen] x Runden -> Tabellen, Laborbericht.

  python -m asd.lab_loop --domain proofreading --runden 4 --budget-usd 3
  python -m asd.lab_loop --domain proofreading --recherche      # mit Scout (arXiv + Europe PMC + eigene Dateien in literature/)

Alles landet unter projects/<domain>/: state.json, prereg.md, decisions.md, lab_report.md, claims.csv.
Regeln: Der Selbsttest des Prüfers muss bestehen. Jede Runde wird vor dem Experiment präregistriert. Nur der Code-Prüfer
entscheidet über Wahrheit; das Red-Team versucht, jede geprüfte Aussage mit Gegen-Prüfungen zu brechen.
"""
import argparse, json, os, time
from .domains.base import get_domain
from .llm import ask_json, COST_LOG, LLMError
from .discovery import solve_cascade
from . import selftest

SYS = "Du bist {rolle} in einem automatisierten Forschungslabor. Antworte nur mit gültigem JSON."


def now(): return time.strftime("%Y-%m-%d %H:%M:%S")


class Project:
    def __init__(self, domain):
        self.dir = f"projects/{domain}"; os.makedirs(self.dir, exist_ok=True); self.path = f"{self.dir}/state.json"
        self.s = json.load(open(self.path)) if os.path.exists(self.path) else {
            "domain": domain, "wissen": [], "fragen": [], "claims": [], "widerlegt": [], "runden": [], "kosten_usd": 0.0}
    def save(self): json.dump(self.s, open(self.path, "w"), ensure_ascii=False, indent=1, default=str)
    def append(self, fn, text):
        with open(f"{self.dir}/{fn}", "a") as f: f.write(text + "\n")


def scout(P, D, log):
    from .research import run as research_run
    ziel = getattr(D, "recherche_ziel", None) or D.kontext
    spec = {"ziel": ziel, "sperre": list(getattr(D, "recherche_sperre", [])), "klassiker": list(getattr(D, "recherche_klassiker", [])),
            "crossref": bool(getattr(D, "recherche_crossref", True))}
    ok, st = research_run(f"{D.name}", n_queries=40, per_query=30, keep=150, kette=15, spec=spec, log=log)
    P.s["wissen"] = [{"text": f["aussage"], "zitat": f["zitat"], "quelle": f["quelle"], "typ": f.get("typ"), "url": f.get("url"), "status": f.get("status")} for f in ok]
    P.append("decisions.md", f"| {now()} | SCOUT | {st['abgerufen']} Quellen, {st['gesperrt']} gesperrt, {st['verifiziert']} Befunde mit per Code bestätigtem Zitat | research/kb/{D.name}/wissensstand.md |")


def wissen_text(P, n=40):
    w = P.s["wissen"][:n]
    rank = {"bewiesen": 0, "numerisch": 1, "experimentell": 2, "vermutet": 3}
    w = sorted(P.s["wissen"], key=lambda x: rank.get(x.get("status"), 4))[:n]
    lit = "\n".join(f"- ({x.get('status', '?')}) {x['text']} [{x['quelle']}]" for x in w)
    eig = "\n".join(f"- [{c['id']}] {c['text']} (geprüft: {c['grund'][:150]})" for c in P.s["claims"] if c["status"] == "bestätigt")
    wid = "\n".join(f"- {x}" for x in P.s["widerlegt"][-10:])
    return f"Literatur (Zitate per Code geprüft):\n{lit or '-'}\n\nEigene geprüfte Ergebnisse:\n{eig or '-'}\n\nNicht bestätigt / widerlegt:\n{wid or '-'}"


def integrator_fragen(P, D, k=5, salt=""):
    r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\n{D.primitive_doc}\n\n{D.claim_doc}\n\nSchlage {k} neue Forschungsfragen vor, die (1) mit den "
                 "Experimenten beantwortbar und (2) mit den Prüfungstypen nachprüfbar sind, (3) über das Bekannte hinausgehen. Mische sichere "
                 "Anker (Bekanntes reproduzieren) und offene Fragen. "
                 'JSON: {"fragen": [{"frage": "...", "begruendung": "...", "neuheit": 0-1, "machbarkeit": 0-1}]}',
                 SYS.format(rolle="der Integrator (Forschungsleiter)"), salt=f"integrator-fragen-{salt}")
    for q in r.get("fragen", []):
        q.update(id=f"F{len(P.s['fragen']) + 1}", status="offen"); P.s["fragen"].append(q)


def integrator_plan(P, D, runde):
    offen = [q for q in P.s["fragen"] if q["status"] == "offen"]
    if not offen: return None
    liste = "\n".join(f"[{q['id']}] {q['frage']} (Neuheit {q.get('neuheit')}, Machbarkeit {q.get('machbarkeit')})" for q in offen)
    r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\nOffene Fragen:\n{liste}\n\nWähle die EINE Frage mit dem höchsten erwarteten Erkenntnisgewinn "
                 "(Value of Information: Neuheit x Machbarkeit x Lücke zum bisher Bewiesenen). Formuliere vorab ein Erfolgskriterium und ein "
                 'Abbruchkriterium. JSON: {"id": "F..", "begruendung": "...", "erfolg": "...", "abbruch": "...", "erwartung": "..."}',
                 SYS.format(rolle="der Integrator (Forschungsleiter)"), salt=f"integrator-plan-{runde}")
    q = next((q for q in offen if q["id"] == r.get("id")), offen[0]); return q, r


def red_team(P, D, frage, ans, runde):
    """Erzeugt Gegen-Prüfungen, die FALSCH sein müssten, wenn die Aussage stimmt. Besteht eine davon, ist die Aussage angefochten."""
    try:
        r = ask_json(f"{D.kontext}\n\nFRAGE: {frage}\nGEPRÜFTE ANTWORT: {json.dumps(ans, ensure_ascii=False)}\n\n{D.claim_doc}\n\nDu bist Red-Team. Formuliere bis zu 2 "
                     "Prüfungen (gleiche Typen), die bestehen würden, wenn die Antwort FALSCH wäre (Gegenbeispiel, Randfall, Gegenteil). "
                     'JSON: {"gegenpruefungen": [{"pruefung": {...}, "idee": "..."}]}', SYS.format(rolle="das Red-Team"), salt=f"redteam-{runde}")
    except (LLMError, json.JSONDecodeError): return []
    out = []
    for g in r.get("gegenpruefungen", [])[:2]:
        p = g.get("pruefung")
        if not isinstance(p, dict): continue
        ok, why, _ = D.check(p); out.append({"pruefung": p, "idee": g.get("idee", ""), "bestanden": bool(ok), "grund": why[:200]})
    return out


def lernen(P, D, frage, res, runde):
    try:
        r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\nZuletzt untersucht: {frage}\nErgebnis: {json.dumps(res['antwort'], ensure_ascii=False)[:600]} ({res['level']})\n\n"
                     f"{D.primitive_doc}\n\n{D.claim_doc}\n\nLeite 1-2 Folgefragen ab, die aus diesem Ergebnis am meisten lernen (Grenzen ausloten, "
                     'Verallgemeinerung, Gegenprobe). JSON: {"fragen": [{"frage": "...", "begruendung": "...", "neuheit": 0-1, "machbarkeit": 0-1}]}',
                     SYS.format(rolle="der Lern-Agent"), salt=f"lernen-{runde}")
    except (LLMError, json.JSONDecodeError): return
    for q in r.get("fragen", [])[:2]:
        q.update(id=f"F{len(P.s['fragen']) + 1}", status="offen", aus_runde=runde); P.s["fragen"].append(q)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--domain", required=True); ap.add_argument("--runden", type=int, default=4)
    ap.add_argument("--budget-usd", type=float, default=3.0); ap.add_argument("--recherche", action="store_true"); ap.add_argument("--recherche-neu", action="store_true", help="Scout erneut ausführen")
    ap.add_argument("--fragen", default="", help="JSON-Datei mit Startfragen [{frage: ...}]")
    ap.add_argument("--gezielt", action="store_true", help="keine frei erzeugten Folgefragen (Workflow Phase 5)"); a = ap.parse_args()
    D = get_domain(a.domain); P = Project(a.domain); log = lambda m: (print(m, flush=True), P.append("lab_report.md", f"- {now()} {m}"))
    if not P.s["runden"]: P.append("decisions.md", "| Zeit | Agent | Entscheidung | Beleg |\n|---|---|---|---|")
    ok, _ = selftest.run(a.domain, log=lambda m: None)
    log(f"Selbsttest des Prüfers: {'bestanden' if ok else 'NICHT bestanden'}")
    if not ok: raise SystemExit("Abbruch: Der Prüfer besteht seinen Selbsttest nicht. Erst den Prüfer reparieren.")
    if a.recherche and (not P.s["wissen"] or a.recherche_neu): scout(P, D, log)
    if a.fragen:                                               # Startfragen aus der Lückenkarte: andere offene Fragen werden zurückgestellt
        for q in P.s["fragen"]:
            if q["status"] == "offen": q["status"] = "zurückgestellt"
        for q in json.load(open(a.fragen)): q.update(id=f"F{len(P.s['fragen']) + 1}", status="offen", quelle="lueckenkarte"); P.s["fragen"].append(q)
        P.append("decisions.md", f"| {now()} | INTEGRATOR | Startfragen aus {a.fragen} geladen, übrige offene Fragen zurückgestellt | Workflow Phase 5 |")
    if not P.s["fragen"]: integrator_fragen(P, D, salt=str(len(P.s["runden"])))
    P.save()
    for _ in range(a.runden):
        runde = len(P.s["runden"]) + 1; spent = P.s["kosten_usd"] + sum(COST_LOG)
        if spent > a.budget_usd: log(f"Budget erreicht ({spent:.2f} USD)"); break
        try: plan = integrator_plan(P, D, runde)
        except LLMError as e: log(f"Integrator-Fehler: {e}"); break
        if not plan: log("Keine offenen Fragen mehr."); break
        q, pr = plan
        P.append("prereg.md", f"\n## Runde {runde} ({now()}), vor dem Experiment\n- Frage [{q['id']}]: {q['frage']}\n- Begründung: {pr.get('begruendung')}\n"
                              f"- Erfolg: {pr.get('erfolg')}\n- Abbruch: {pr.get('abbruch')}\n- Erwartung: {pr.get('erwartung')}")
        P.append("decisions.md", f"| {now()} | INTEGRATOR | Runde {runde}: [{q['id']}] {q['frage'][:120]} | {str(pr.get('begruendung'))[:160]} |")
        log(f"Runde {runde}: {q['frage']}")
        res = solve_cascade(D.kontext + "\n\n" + wissen_text(P), q["frage"], salt=f"{D.name}-{runde}", domain=D)
        q["status"] = "beantwortet" if res["level"].startswith("computed") else "ungeprüft"
        rt = []; cid = f"{D.name}-R{runde}"
        if q["status"] == "beantwortet":
            p = (res["antwort"].get("pruefungen") or [res["antwort"].get("pruefung")])[0]
            rt = red_team(P, D, q["frage"], res["antwort"], runde)
            for x in rt: x["widerspruch"] = bool(x["bestanden"] and D.widerspricht(p, x["pruefung"]))
            angefochten = [x for x in rt if x["widerspruch"]]
            grund = next(tr["pruefung"]["grund"] for tr in res["forscher"] if tr.get("pruefung", {}).get("bestanden"))
            P.s["claims"].append({"id": cid, "frage": q["frage"], "text": D.describe(p), "interpretation_ungeprueft": str(res["antwort"].get("antwort")),
                                  "pruefung": p, "grund": grund,
                                  "level": D.level(p), "status": "angefochten" if angefochten else "bestätigt", "red_team": rt, "runde": runde})
            log(f"  geprüft ({D.level(p)}): {D.describe(p)[:160]} | Red-Team: {len(rt)} Gegenprüfungen, {sum(x['bestanden'] for x in rt)} bestanden, {len(angefochten)} logische Widersprüche")
        else:
            P.s["widerlegt"].append(f"[{q['id']}] {q['frage']}: keine Behauptung bestand die Prüfung")
            log("  keine geprüfte Behauptung (als negatives Ergebnis protokolliert)")
        json.dump(res, open(f"{P.dir}/runde{runde}.json", "w"), ensure_ascii=False, indent=1, default=str)
        if not (a.fragen or a.gezielt): lernen(P, D, q["frage"], res, runde)   # gezielter Lauf: keine frei erzeugten Folgefragen
        P.s["runden"].append({"runde": runde, "frage": q["id"], "status": q["status"], "red_team": rt, "sek": res["sek"]})
        P.s["kosten_usd"] += sum(COST_LOG); COST_LOG.clear(); P.save()
    log(f"Fertig: {len(P.s['claims'])} geprüfte Aussagen, {len(P.s['widerlegt'])} negative Ergebnisse, Kosten {P.s['kosten_usd']:.2f} USD")


if __name__ == "__main__":
    main()
