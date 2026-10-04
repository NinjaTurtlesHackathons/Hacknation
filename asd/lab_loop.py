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
    wid = "\n".join(f"- {x}" if isinstance(x, str) else f"- [{x['frage_id']}] {x['frage']}: " + "; ".join(f"{g['stufe']}: {g['grund'][:100]}" for g in x["gruende"])
                     for x in P.s["widerlegt"][-10:])
    return f"Literatur (Zitate per Code geprüft):\n{lit or '-'}\n\nEigene geprüfte Ergebnisse:\n{eig or '-'}\n\nNicht bestätigt / widerlegt:\n{wid or '-'}"


def faden_of(P, q):
    """Faden = Ausgangsfrage + ihre Folgefragen. Alte Zustände ohne Feld: über aus_runde auf die Frage der Runde zurückführen."""
    if q.get("faden_id"): return q["faden_id"]
    if q.get("aus_runde"):
        r = next((x for x in P.s["runden"] if x["runde"] == q["aus_runde"]), None)
        parent = next((x for x in P.s["fragen"] if r and x["id"] == r["frage"]), None)
        if parent and parent is not q: return faden_of(P, parent)
    return q["id"]


def faden_fortschritt(P, faden, fenster=2):
    """Hat der Faden in seinen letzten `fenster` Runden mindestens einen neuen bestätigten Claim gebracht?"""
    qid2f = {q["id"]: faden_of(P, q) for q in P.s["fragen"]}
    rs = [r for r in P.s["runden"] if qid2f.get(r["frage"]) == faden][-fenster:]
    ok_runden = {c.get("runde") for c in P.s["claims"] if c.get("status") == "bestätigt"}
    return any(r["runde"] in ok_runden for r in rs)


def integrator_fragen(P, D, k=5, salt=""):
    r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\n{D.primitive_doc}\n\n{D.claim_doc}\n\nSchlage {k} neue Forschungsfragen vor, die (1) mit den "
                 "Experimenten beantwortbar und (2) mit den Prüfungstypen nachprüfbar sind, (3) über das Bekannte hinausgehen. Mische sichere "
                 "Anker (Bekanntes reproduzieren) und offene Fragen. "
                 'JSON: {"fragen": [{"frage": "...", "begruendung": "...", "neuheit": 0-1, "machbarkeit": 0-1}]}',
                 SYS.format(rolle="der Integrator (Forschungsleiter)"), salt=f"integrator-fragen-{salt}")
    for q in r.get("fragen", []):
        qid = f"F{len(P.s['fragen']) + 1}"; q.update(id=qid, status="offen", faden_id=qid); P.s["fragen"].append(q)


def integrator_plan(P, D, runde):
    offen = [q for q in P.s["fragen"] if q["status"] == "offen"]
    if not offen: return None
    if P.s["runden"]:                                          # Tiefe statt Breite: im Faden bleiben, solange er Fortschritt bringt
        last_q = next((x for x in P.s["fragen"] if x["id"] == P.s["runden"][-1]["frage"]), None)
        faden = faden_of(P, last_q) if last_q else None
        im_faden = [q for q in offen if faden and faden_of(P, q) == faden]
        if im_faden and faden_fortschritt(P, faden):
            P.append("decisions.md", f"| {now()} | INTEGRATOR | Runde {runde}: bleibe im Faden {faden} | letzte 2 Runden des Fadens brachten einen neuen bestätigten Claim; {len(im_faden)} offene Folgefragen |")
            offen = im_faden
        elif faden:
            P.append("decisions.md", f"| {now()} | INTEGRATOR | Runde {runde}: Fadenwechsel weg von {faden} | " +
                     ("keine offenen Folgefragen im Faden" if not im_faden else "kein neuer bestätigter Claim in den letzten 2 Runden des Fadens") + " |")
    liste = "\n".join(f"[{q['id']}] {q['frage']} (Neuheit {q.get('neuheit')}, Machbarkeit {q.get('machbarkeit')})" for q in offen)
    r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\nOffene Fragen:\n{liste}\n\nWähle die EINE Frage mit dem höchsten erwarteten Erkenntnisgewinn "
                 "(Value of Information: Neuheit x Machbarkeit x Lücke zum bisher Bewiesenen). Formuliere vorab ein Erfolgskriterium und ein "
                 'Abbruchkriterium. JSON: {"id": "F..", "begruendung": "...", "erfolg": "...", "abbruch": "...", "erwartung": "..."}',
                 SYS.format(rolle="der Integrator (Forschungsleiter)"), salt=f"integrator-plan-{runde}")
    q = next((q for q in offen if q["id"] == r.get("id")), offen[0]); q.setdefault("faden_id", faden_of(P, q)); return q, r


FEHLER_MUSTER = ("nicht ausführbar", "NaN", "TypeError", "IndexError", "KeyError", "ValueError", "Traceback", "Exception",
                 "unbekannter Prüfungstyp", "unbekannte Familienmitglieder", "Zeitüberschreitung", "> 600 s", "> 1800 s")


def nicht_ausfuehrbar(grund):
    """Gegenprüfung lief gar nicht (Fehler, unbekannter Typ, Zeitlimit) -> weder 'bestanden' noch 'nicht bestanden'."""
    return any(m in str(grund) for m in FEHLER_MUSTER)


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
        try: ok, why, _ = D.check(p)
        except Exception as e: ok, why = False, f"nicht ausführbar: {type(e).__name__}"
        na = nicht_ausfuehrbar(why) and not ok
        out.append({"pruefung": p, "idee": g.get("idee", ""), "bestanden": bool(ok), "ergebnis": "nicht_ausfuehrbar" if na else ("bestanden" if ok else "nicht_bestanden"),
                    "grund": "" if na else why[:200]})
    return out


def lernen(P, D, frage, res, runde, parent=None):
    try:
        r = ask_json(f"{D.kontext}\n\n{wissen_text(P)}\n\nZuletzt untersucht: {frage}\nErgebnis: {json.dumps(res['antwort'], ensure_ascii=False)[:600]} ({res['level']})\n\n"
                     f"{D.primitive_doc}\n\n{D.claim_doc}\n\nLeite 1-2 Folgefragen ab, die dieses Ergebnis VERTIEFEN. Bevorzuge in dieser Reihenfolge: "
                     "(1) Verallgemeinerung (größere Klasse, alle n, alle Parameter, Familie statt Einzelfall), (2) Grenzfall (wo hört es auf zu gelten?), "
                     "(3) gezielte Gegenbeispielsuche. Keine thematischen Sprünge. "
                     'JSON: {"fragen": [{"frage": "...", "begruendung": "...", "art": "verallgemeinerung|grenzfall|gegenbeispiel", "neuheit": 0-1, "machbarkeit": 0-1}]}',
                     SYS.format(rolle="der Lern-Agent"), salt=f"lernen-{runde}")
    except (LLMError, json.JSONDecodeError): return
    for q in r.get("fragen", [])[:2]:
        q.update(id=f"F{len(P.s['fragen']) + 1}", status="offen", aus_runde=runde, faden_id=faden_of(P, parent) if parent else None)
        if not q["faden_id"]: q["faden_id"] = q["id"]
        P.s["fragen"].append(q)


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
        for q in json.load(open(a.fragen)):
            qid = f"F{len(P.s['fragen']) + 1}"; q.update(id=qid, status="offen", quelle="lueckenkarte", faden_id=q.get("faden_id") or qid); P.s["fragen"].append(q)
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
                                  "level": D.level(p), "status": "angefochten" if angefochten else "bestätigt", "red_team": rt, "runde": runde,
                                  "relevanz": D.relevanz(p) if hasattr(D, "relevanz") else "stuetze"})
            log(f"  geprüft ({D.level(p)}): {D.describe(p)[:160]} | Red-Team: {len(rt)} Gegenprüfungen, {sum(x['bestanden'] for x in rt)} bestanden, {len(angefochten)} logische Widersprüche")
        else:
            gruende = []
            for tr in res.get("forscher", []):
                pr_ = tr.get("pruefung") or {}; a_ = tr.get("final") or {}
                pt = a_.get("pruefung") or (a_.get("pruefungen") or [None])[0]
                g = pr_.get("grund") or tr.get("fehler") or "keine Prüfung angegeben"
                gruende.append({"stufe": f"{tr.get('strategie')}/{tr.get('modell', '')}".strip("/"), "pruefungstyp": (pt or {}).get("typ") if isinstance(pt, dict) else None,
                                "grund": ("Prüfung nicht ausführbar" if nicht_ausfuehrbar(g) else g)[:240]})
            P.s["widerlegt"].append({"frage_id": q["id"], "frage": q["frage"], "runde": runde, "gruende": gruende})
            log("  keine geprüfte Behauptung: " + "; ".join(f"{x['stufe']}: {x['grund'][:80]}" for x in gruende)[:400])
        json.dump(res, open(f"{P.dir}/runde{runde}.json", "w"), ensure_ascii=False, indent=1, default=str)
        if not (a.fragen or a.gezielt): lernen(P, D, q["frage"], res, runde, parent=q)   # gezielter Lauf: keine frei erzeugten Folgefragen
        P.s["runden"].append({"runde": runde, "frage": q["id"], "status": q["status"], "red_team": rt, "sek": res["sek"]})
        P.s["kosten_usd"] += sum(COST_LOG); COST_LOG.clear(); P.save()
    log(f"Fertig: {len(P.s['claims'])} geprüfte Aussagen, {len(P.s['widerlegt'])} negative Ergebnisse, Kosten {P.s['kosten_usd']:.2f} USD")


if __name__ == "__main__":
    main()
