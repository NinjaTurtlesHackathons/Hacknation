"""Frozen harness: Laborschritte und Verifier als CLI, aufrufbar von Agenten (z. B. unter Omnigent).

  python -m asd.cli <befehl> --domain <d> [--projekt <p>] [--agent <name>] ...

Befehle: selftest | wissen | fragen [--add-json f] | plan | options --frage <id> | waehle (wähle) --option <id> --grund "..."
         | experiment --spec-json <datei|json> (oder --op/--args) | pruefe (prüfe) --claim-json <datei|json>
         | redteam --claim <id> --gegen-json <datei|json> | folgefragen --aus <runde|claim|frage> --json <datei|json>
         | reopen --annahme <id> --claim <id> --grund "..." | doku | status

Nur `prüfe` schreibt bestätigte Claims in state.json. Jede Aktion wird nach projects/<p>/record.jsonl angehängt.
Der Verifier selbst (Domain.check) bleibt unverändert; die CLI ruft ihn nur auf."""
import argparse, json, os, sys, time

from .domains.base import get_domain
from .lab_loop import Project, wissen_text, faden_of, faden_fortschritt, now
from . import planner

LEAK_CFG = os.environ.get("ASD_LEAK_GUARD", "omni/leak_guard.json")


def leak_terms(D):
    t = [s.lower() for s in getattr(D, "recherche_sperre", [])]
    if os.path.exists(LEAK_CFG):
        cfg = json.load(open(LEAK_CFG)); t += [s.lower() for s in cfg.get("begriffe", [])]
    return t


def wissen_gefiltert(P, D):
    """wissen_text ohne gesperrte Quellen (Leckschutz für Replay-Läufe)."""
    terms = leak_terms(D)
    if not terms: return wissen_text(P)
    alt = P.s["wissen"]
    P.s["wissen"] = [w for w in alt if not any(x in (str(w.get("quelle", "")) + " " + str(w.get("text", "")) + " " + str(w.get("url", ""))).lower() for x in terms)]
    try: return wissen_text(P)
    finally: P.s["wissen"] = alt


def lade_json(x):
    """Datei ODER inline-JSON (Agenten brauchen so keine Schreibrechte)."""
    x = (x or "").strip()
    return json.loads(x) if x[:1] in "{[" else json.load(open(x))


class CLI:
    def __init__(self, a):
        self.a = a; self.D = get_domain(a.domain); self.pname = a.projekt or a.domain
        self.D.projekt = self.pname; self.P = Project(self.pname)
        self.agent = a.agent or os.environ.get("OMNI_AGENT") or os.environ.get("OMNIGENT_AGENT_NAME") or "unbekannt"

    def record(self, befehl, ids=None, ergebnis=None, ein=None, aus=None):
        """Gemeinsames Forschungsprotokoll: jede Aktion mit Eingabe- und Ausgabe-IDs (daraus ist jede Entscheidung rekonstruierbar)."""
        ids = ids or {}
        with open(f"{self.P.dir}/record.jsonl", "a") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "agent": self.agent, "befehl": befehl,
                                "eingabe_ids": ein if ein is not None else {k: v for k, v in ids.items() if k in ("frage", "claim", "option", "aus", "annahme")},
                                "ausgabe_ids": aus if aus is not None else {k: v for k, v in ids.items() if k not in ("frage", "claim", "option", "aus", "annahme")},
                                "ergebnis": ergebnis}, ensure_ascii=False, default=str) + "\n")

    def frage(self, qid):
        q = next((x for x in self.P.s["fragen"] if x["id"] == qid), None)
        if not q: raise SystemExit(f"Frage {qid} nicht gefunden")
        return q

    # --- Befehle ---------------------------------------------------------------------------------------
    def selftest(self):
        from . import selftest
        ok, _ = selftest.run(self.a.domain, log=lambda m: None)
        print("PASS" if ok else "FAIL"); self.record("selftest", ergebnis="PASS" if ok else "FAIL"); return 0 if ok else 1

    def wissen(self):
        t = wissen_gefiltert(self.P, self.D); print(t[:6000]); self.record("wissen", ergebnis=f"{len(t)} Zeichen"); return 0

    def fragen(self):
        if self.a.add_json:
            neu = lade_json(self.a.add_json); neu = neu.get("fragen", neu) if isinstance(neu, dict) else neu; ids = []
            for q in neu:
                qid = f"F{len(self.P.s['fragen']) + 1}"
                parent = next((x for x in self.P.s["fragen"] if x["id"] == q.get("aus_frage")), None)
                q.update(id=qid, status="offen", faden_id=faden_of(self.P, parent) if parent else qid, quelle=f"agent:{self.agent}")
                self.P.s["fragen"].append(q); ids.append(qid)
            self.P.save(); print("NEU " + json.dumps(ids)); self.record("fragen --add-json", {"fragen": ids}); return 0
        offen = [q for q in self.P.s["fragen"] if q["status"] == "offen"]
        for q in offen: print(f"[{q['id']}] (Faden {faden_of(self.P, q)}) {q['frage'][:300]}" + (f"  lit_offen={q['lit_offen']}" if q.get("lit_offen") else ""))
        if not offen: print("(keine offenen Fragen; der learner kann mit `fragen --add-json` neue anlegen)")
        self.record("fragen", {"offen": [q["id"] for q in offen]}); return 0

    def folgefragen(self):
        """Neue Fragen aus einer Runde/einem Claim speichern (learner). --aus <runden-id|claim-id|frage-id>, --json <datei|inline>."""
        neu = lade_json(self.a.json); neu = neu.get("fragen", neu) if isinstance(neu, dict) else neu; ids = []
        quelle = next((q for q in self.P.s["fragen"] if q["id"] == self.a.aus), None)
        if quelle is None:
            c = next((c for c in self.P.s["claims"] if c["id"] == self.a.aus), None)
            r = next((r for r in self.P.s["runden"] if str(r.get("runde")) == str(self.a.aus).lstrip("R")), None) if not c else None
            fid = (c or {}).get("frage_id") or (r or {}).get("frage")
            quelle = next((q for q in self.P.s["fragen"] if q["id"] == fid), None)
        for q in neu:
            qid = f"F{len(self.P.s['fragen']) + 1}"
            q.update(id=qid, status="offen", aus=self.a.aus, faden_id=faden_of(self.P, quelle) if quelle else qid, quelle=f"agent:{self.agent}")
            self.P.s["fragen"].append(q); ids.append(qid)
        self.P.save(); print("NEU " + json.dumps(ids))
        self.record("folgefragen", ein={"aus": self.a.aus}, aus={"fragen": ids}); return 0

    def reopen(self):
        """Frühere Annahme nach einem überraschenden Ergebnis wieder öffnen; der Plan muss sich danach ändern."""
        an = next((x for x in self.P.s.get("annahmen", []) if x["id"] == self.a.annahme), None)
        if not an: raise SystemExit(f"Annahme {self.a.annahme} nicht gefunden")
        if not self.a.grund or len(self.a.grund) < 10: raise SystemExit("reopen braucht --grund")
        an["status"] = "wiedereröffnet"; an.setdefault("historie", []).append({"ts": now(), "agent": self.agent, "grund": self.a.grund, "claim": self.a.claim})
        for qid in an.get("fragen", []):
            q = next((x for x in self.P.s["fragen"] if x["id"] == qid), None)
            if q: q["status"] = "offen"
        self.P.save()
        self.P.append("decisions.md", f"| {now()} | {self.agent.upper()} | REOPEN Annahme {an['id']}: {an['text'][:120]} | {self.a.grund[:200]} (Beleg {self.a.claim}) |")
        print("REOPEN " + json.dumps({"annahme": an["id"], "status": an["status"], "wieder_offen": an.get("fragen", [])}, ensure_ascii=False))
        self.record("reopen", ein={"annahme": an["id"], "claim": self.a.claim}, aus={"fragen": an.get("fragen", [])}, ergebnis=self.a.grund); return 0

    def plan(self):
        """Offene Fragen plus Empfehlung nach Faden-Regel (im Faden bleiben, solange die letzten 2 Runden einen Claim brachten)."""
        offen = [q for q in self.P.s["fragen"] if q["status"] == "offen"]
        akt = self.P.s.get("aktive_frage"); empf, grund = None, ""
        if akt:
            fa = faden_of(self.P, self.frage(akt)); im = [q for q in offen if faden_of(self.P, q) == fa]
            runden_faden = [r for r in self.P.s["runden"] if r.get("faden_id") == fa]
            if im and (len(runden_faden) < 2 or faden_fortschritt(self.P, fa)):
                empf, grund = im[0]["id"], f"im Faden {fa} bleiben (Fortschritt oder < 2 Runden)"
            elif im: grund = f"Faden {fa}: 2 Runden ohne neuen bestätigten Claim -> Themenwechsel per `wähle --frage` mit Begründung erlaubt"
        if not empf and offen:
            empf = sorted(offen, key=lambda q: (not q.get("lit_offen"), -float(q.get("machbarkeit") or 0.5)))[0]["id"]; grund = grund or "beste offene Frage (lit_offen, Machbarkeit)"
        for q in offen: print(f"[{q['id']}] (Faden {faden_of(self.P, q)}) {q['frage'][:200]}")
        print(f"EMPFEHLUNG {json.dumps({'frage': empf, 'grund': grund}, ensure_ascii=False)}")
        self.record("plan", {"empfehlung": empf}, grund); return 0

    def options(self):
        q = self.frage(self.a.frage); O = planner.options(self.D, q, self.P.s)
        self.P.s["letzte_optionen"] = {"frage": q["id"], "optionen": O, "ts": now()}; self.P.save()
        for o in O: print(json.dumps({k: o[k] for k in ("id", "art", "beschreibung", "kosten", "erwarteter_gewinn")}, ensure_ascii=False))
        self.record("options", {"frage": q["id"], "optionen": [o["id"] for o in O]}); return 0

    def waehle(self):
        a = self.a
        if not a.grund or len(a.grund.strip()) < 10: raise SystemExit("wähle braucht --grund (mindestens 10 Zeichen)")
        if a.frage:                                               # aktive Frage setzen / Themenwechsel
            q = self.frage(a.frage); alt = self.P.s.get("aktive_frage")
            wechsel = alt and faden_of(self.P, self.frage(alt)) != faden_of(self.P, q)
            if wechsel and faden_fortschritt(self.P, faden_of(self.P, self.frage(alt))) and not a.erzwinge:
                raise SystemExit(f"Faden {faden_of(self.P, self.frage(alt))} hat Fortschritt: im Faden bleiben (oder --erzwinge mit Begründung)")
            self.P.s["aktive_frage"] = q["id"]
            self.P.append("decisions.md", f"| {now()} | {self.agent.upper()} | {'THEMENWECHSEL' if wechsel else 'Frage'} -> [{q['id']}] {q['frage'][:100]} | {a.grund[:200]} |")
        if a.option:
            lo = self.P.s.get("letzte_optionen") or {}
            O = lo.get("optionen", []); o = next((x for x in O if x["id"] == a.option), None)
            if not o: raise SystemExit(f"Option {a.option} nicht in den letzten Optionen ({[x['id'] for x in O]}); erst `options` aufrufen")
            verw = [x for x in O if x["id"] != o["id"]]
            ent = {"ts": now(), "agent": self.agent, "frage": lo["frage"], "gewaehlt": o, "verworfen": verw, "grund": a.grund}
            self.P.s.setdefault("entscheidungen", []).append(ent); self.P.s["aktive_frage"] = lo["frage"]; self.P.s["aktive_option"] = o
            q = self.frage(lo["frage"])
            self.P.append("decisions.md", f"| {now()} | {self.agent.upper()} | [{q['id']}] Option {o['id']} ({o['art']}, Kosten {o['kosten']}, Gewinn {o['erwarteter_gewinn']}); "
                          f"verworfen: {', '.join(x['id'] + ' (' + x['art'] + ')' for x in verw)} | {a.grund[:200]} |")
            self.P.append("prereg.md", f"\n## {now()}, vor dem Experiment (Omnigent, {self.agent})\n- Frage [{q['id']}]: {q['frage']}\n- Option {o['id']} ({o['art']}): {o['beschreibung']}\n"
                          f"- Erwartete Verifier-Aufrufe: {o['kosten']}\n- Verworfen: {', '.join(x['id'] + ' ' + x['art'] for x in verw)}\n- Begründung: {a.grund}")
        self.P.save(); print("OK " + json.dumps({"aktive_frage": self.P.s.get("aktive_frage"), "option": (self.P.s.get("aktive_option") or {}).get("id")}))
        self.record("waehle", {"frage": self.P.s.get("aktive_frage"), "option": a.option}, a.grund); return 0

    def experiment(self):
        if self.a.spec_json:
            sp = lade_json(self.a.spec_json); self.a.op = sp.get("op", self.a.op); args = sp.get("args", {})
        else: args = json.loads(self.a.args or "{}")
        from .discovery import _jsonfest
        r = _jsonfest(self.D.run_op(self.a.op, args))
        self.P.s.setdefault("experimente", []).append({"ts": now(), "agent": self.agent, "op": self.a.op, "args": args, "frage": self.P.s.get("aktive_frage")})
        eid = f"E{len(self.P.s['experimente'])}"; self.P.save()
        print(f"EXPERIMENT {eid} " + json.dumps(r, ensure_ascii=False)[:4000]); self.record("experiment", ergebnis=str(r)[:300], ein={"frage": self.P.s.get("aktive_frage"), "option": (self.P.s.get("aktive_option") or {}).get("id")},
                    aus={"experiment": eid, "op": self.a.op}); return 0

    def pruefe(self):
        c = lade_json(self.a.claim_json); D = self.D
        ps = c.get("pruefungen") or ([c["pruefung"]] if isinstance(c.get("pruefung"), dict) else ([c] if "typ" in c else []))
        ps = [p for p in ps if isinstance(p, dict)]
        self.P.s["verifier_aufrufe"] = self.P.s.get("verifier_aufrufe", 0) + max(1, len(ps))
        if not ps: ok, why, lvl = False, "keine Prüfung (pruefung/pruefungen) im Claim-JSON", "hypothesis"
        else:
            res = [D.check(p)[:2] for p in ps]
            ok = all(bool(o) for o, _ in res) and (("antwort" not in c and "zahl" not in c) or all(D.consistent(c, p) for p in ps))
            why = " | ".join(w for _, w in res) + ("" if ok or not all(o for o, _ in res) else " | Antwort passt nicht zur Prüfung (consistent)")
            lvl = D.level(ps[0]) if ok else "hypothesis"
        qid = c.get("frage_id") or self.P.s.get("aktive_frage"); runde = len(self.P.s["runden"]) + 1
        q = next((x for x in self.P.s["fragen"] if x["id"] == qid), None)
        ueb = None
        if ok and hasattr(D, "ueberraschung"):
            try: ueb = D.ueberraschung(ps[0], self.P.s)
            except Exception as e: ueb = None
        if ok:
            cid = f"{D.name}-O{runde}"
            self.P.s["claims"].append({"id": cid, "frage": q["frage"] if q else c.get("frage", ""), "text": D.describe(ps[0]), "pruefung": ps[0],
                                       "alle_pruefungen": ps, "grund": why, "level": lvl, "status": "bestätigt", "red_team": [], "runde": runde,
                                       "relevanz": D.relevanz(ps[0]), "quelle": f"omnigent:{self.agent}",
                                       "option": (self.P.s.get("aktive_option") or {}).get("id")})
            if q: q["status"] = "beantwortet"
        else:
            cid = None
            self.P.s["widerlegt"].append({"frage_id": qid, "frage": q["frage"] if q else "", "runde": runde,
                                          "gruende": [{"stufe": f"omnigent:{self.agent}", "pruefungstyp": ps[0].get("typ") if ps else None, "grund": why[:240]}]})
        self.P.s["runden"].append({"runde": runde, "frage": qid, "status": "beantwortet" if ok else "ungeprüft", "red_team": [], "sek": 0,
                                   "faden_id": faden_of(self.P, q) if q else None, "quelle": "omnigent"})
        self.P.save()
        out = {"bestanden": bool(ok), "level": lvl, "grund": why[:400], "claim_id": cid}
        if ueb:
            out["ueberraschung"] = True; out["widerspricht_annahme"] = ueb["annahme"]; out["ueberraschung_grund"] = ueb["grund"]
            self.P.s["claims"][-1]["ueberraschung"] = ueb; self.P.save()
        print("RESULT " + json.dumps(out, ensure_ascii=False))
        self.record("pruefe", ein={"frage": qid, "option": (self.P.s.get("aktive_option") or {}).get("id")}, aus={"claim": cid}, ergebnis=out); return 0

    def redteam(self):
        c = next((x for x in self.P.s["claims"] if x["id"] == self.a.claim), None)
        if not c: raise SystemExit(f"Claim {self.a.claim} nicht gefunden")
        g = lade_json(self.a.gegen_json); gs = g.get("gegenpruefungen", [g]) if isinstance(g, dict) else g; out = []
        for x in gs[:3]:
            p = x.get("pruefung", x) if isinstance(x, dict) else None
            if not isinstance(p, dict): continue
            ok, why = self.D.check(p)[:2]; self.P.s["verifier_aufrufe"] = self.P.s.get("verifier_aufrufe", 0) + 1
            wid = bool(ok and self.D.widerspricht(c["pruefung"], p))
            c["red_team"].append({"pruefung": p, "bestanden": bool(ok), "widerspruch": wid, "grund": why[:200], "agent": self.agent}); out.append({"bestanden": bool(ok), "widerspruch": wid, "grund": why[:200]})
            if wid: c["status"] = "angefochten"
        self.P.save()
        print("REDTEAM " + json.dumps({"claim": c["id"], "status": c["status"], "gegenpruefungen": out}, ensure_ascii=False))
        self.record("redteam", ein={"claim": c["id"]}, aus={"gegenpruefungen": [f"{c['id']}-RT{i + 1}" for i in range(len(c["red_team"]) - len(out), len(c["red_team"]))]},
                    ergebnis={"status": c["status"], "n": len(out)}); return 0

    def doku(self):
        """Experimente (run_op) und Prüfungstypen (check) der Domäne, direkt aus dem Code."""
        print(self.D.primitive_doc + "\n\n" + self.D.claim_doc); self.record("doku"); return 0

    def status(self):
        s = self.P.s; best = [c for c in s["claims"] if c["status"] == "bestätigt"]
        faeden = sorted({faden_of(self.P, q) for q in s["fragen"] if q["status"] == "offen"})
        print(json.dumps({"runden": len(s["runden"]), "claims_bestaetigt": [c["id"] for c in best], "angefochten": [c["id"] for c in s["claims"] if c["status"] == "angefochten"],
                          "negative": len(s["widerlegt"]), "offene_faeden": faeden, "aktive_frage": s.get("aktive_frage"), "verifier_aufrufe": s.get("verifier_aufrufe", 0),
                          "budget_verifier": s.get("budget_verifier", 40), "budget_rest": s.get("budget_verifier", 40) - s.get("verifier_aufrufe", 0),
                          "annahmen": [{"id": x["id"], "status": x.get("status", "aktiv")} for x in s.get("annahmen", [])]},
                         ensure_ascii=False))
        self.record("status"); return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m asd.cli", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("befehl", choices=["selftest", "wissen", "fragen", "plan", "options", "wähle", "waehle", "experiment", "prüfe", "pruefe", "redteam", "folgefragen", "reopen", "doku", "status"])
    ap.add_argument("--domain", default=os.environ.get("ASD_DOMAIN", "lattice")); ap.add_argument("--projekt", default=os.environ.get("ASD_PROJEKT", ""))
    ap.add_argument("--agent", default=""); ap.add_argument("--frage", default=""); ap.add_argument("--option", default="")
    ap.add_argument("--grund", default=""); ap.add_argument("--erzwinge", action="store_true"); ap.add_argument("--add-json", default="")
    ap.add_argument("--op", default=""); ap.add_argument("--args", default="{}"); ap.add_argument("--claim-json", default="")
    ap.add_argument("--claim", default=""); ap.add_argument("--gegen-json", default="")
    ap.add_argument("--spec-json", default=""); ap.add_argument("--aus", default=""); ap.add_argument("--json", default=""); ap.add_argument("--annahme", default="")
    a = ap.parse_args(argv)
    cmd = {"wähle": "waehle", "prüfe": "pruefe"}.get(a.befehl, a.befehl)
    return getattr(CLI(a), cmd)()


if __name__ == "__main__":
    sys.exit(main())
