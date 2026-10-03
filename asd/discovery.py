"""Forscher-Schleife (Bedingung B): viele unabhängige, verschieden ausgerichtete Forscher-Agenten -> Experimente
im Lab -> getypte Behauptungen -> unabhängiger Code-Prüfer -> Abstimmung nur unter geprüften Behauptungen.

Design aus research/evidence.md: externer Prüfer statt Selbstkritik (Stechly et al. 2023), viele Kandidaten +
Auswahl gegen den Prüfer (Brown et al. 2024), erzwungene Vielfalt (Si et al. 2024; FunSearch-Inseln),
lückenlose Herkunft jeder Aussage (Kosmos 2025). Kein LLM entscheidet über Wahrheit.
"""
import json, time
from concurrent.futures import ThreadPoolExecutor
from .llm import ask_json, LLMError
from .domains import lattice as L
from . import verify

STRATEGIEN = {
    "numeriker": "Du gehst systematisch numerisch vor: erst grob scannen, dann gezielt verfeinern.",
    "theoretiker": "Du denkst zuerst über Symmetrie, Grenzfälle und Asymptotik nach und testest dann gezielt die entscheidende Vorhersage.",
    "skeptiker": "Du misstraust der naheliegenden Antwort und suchst aktiv nach Gegenbeispielen und alternativen Erklärungen, bevor du dich festlegst.",
    "sparsam": "Du planst wenige, maximal informative Experimente und vermeidest Redundanz.",
}

CLAIM_DOC = """Deine Endantwort braucht eine ausführbare Prüfung ("pruefung"), die ein unabhängiger Prüfer nachrechnet. Typen:
- {"typ": "argmin2d", "nu": Zahl, "erwartet": "hexagonal"|"quadratisch"|"rechteckig"|"rhombisch"|"schief", "y": Seitenverhältnis (nur bei rechteckig)}
- {"typ": "argmin3d", "nu": Zahl, "erwartet": "bcc"|"fcc"|"sc"}
- {"typ": "vorzeichenwechsel", "groesse": "diff_hex_quadrat" (T(quadratisch)-T(hexagonal)) | "eig_min_quadrat" (kleinster Hesse-Eigenwert am quadratischen Gitter) | "bain_fcc" (Bain-Krümmung bei FCC), "nu_lo": Zahl, "nu_hi": Zahl}   (Intervallbreite <= 0,05; der Wechsel muss darin liegen)
- {"typ": "koexistenz", "nu": Zahl}   (hexagonal und quadratisch sind bei nu beide lokale Minima)
- {"typ": "grenzwert", "groesse": "y_inf"|"kappa", "erwartet": Zahl, "toleranz": Zahl}
- {"typ": "vergleich_nd", "nu": Zahl, "gitter": "<name>", "gegen": ["<name>", ...]}   (gitter hat niedrigere Energie als alle in "gegen", robust in zwei Auflösungen)
- {"typ": "argmin_nd", "d": 3|4, "nu": Zahl, "erwartet": "<name>"}   (unabhängige globale Suche des Prüfers findet nichts Besseres)
Wähle die Prüfung, die deine Antwort am direktesten belegt. Für Fragen mit mehreren Teilaussagen darfst du statt "pruefung" eine Liste "pruefungen" angeben; dann muss jede bestehen."""

MULTI_DOC = ('Deine Endantwort braucht eine ausführbare Prüfung ("pruefung"), die ein unabhängiger Prüfer nachrechnet. '
             'Für mehrere Teilaussagen darfst du statt "pruefung" eine Liste "pruefungen" angeben; dann muss jede bestehen.')

ANTWORT_SCHEMA = '{"antwort": "<Kategorie oder kurze Antwort, sonst \\"unbekannt\\">", "zahl": <Zahl oder null>, "konfidenz": <0..1>, "pruefung": {...}, "begruendung": "<2-3 Sätze>"}'


def _sys(strategie):
    return (f"Du bist ein Forscher in einem automatisierten Labor für mathematische Physik. {STRATEGIEN[strategie]} "
            "Du kennst keine Ergebnisse vorab; stütze Aussagen auf Experimente. Antworte nur mit gültigem JSON.")


def _default_domain():
    from .domains.lattice_domain import DOMAIN
    return DOMAIN


class Lab:
    """Führt Experimente der Domäne aus, cached identische Anfragen und protokolliert alles (Herkunft)."""
    def __init__(self, domain=None): self.domain = domain or _default_domain(); self.memo = {}; self.log = []
    def run(self, op, args, who):
        key = json.dumps([op, args], sort_keys=True)
        if key not in self.memo:
            t0 = time.time(); self.memo[key] = self.domain.run_op(op, args); dt = time.time() - t0
        else: dt = 0.0
        self.log.append({"id": len(self.log), "wer": who, "op": op, "args": args, "ergebnis": self.memo[key], "sek": round(dt, 2)})
        return self.log[-1]


def _fmt(entries):
    return "\n".join(f"[E{e['id']}] {e['op']} {json.dumps(e['args'])} -> {json.dumps(e['ergebnis'])[:700]}" for e in entries)


def forscher(kontext, frage, strategie, lab, salt, max_ops=8, model=None):
    who = f"forscher-{strategie}"; D = lab.domain
    cdoc = CLAIM_DOC if D.name == "lattice" else D.claim_doc + "\n" + MULTI_DOC
    base = f"{kontext}\n\nFRAGE: {frage}\n\n{D.primitive_doc}\n\n{cdoc}"
    trace = {"strategie": strategie, "runden": []}
    p1 = base + f'\n\nRunde 1: Plane bis zu {max_ops} Experimente. Antworte als JSON: {{"ueberlegung": "...", "plan": [{{"op": "...", "args": {{...}}}}]}}'
    r1 = ask_json(p1, _sys(strategie), salt=f"{salt}-{strategie}-r1", model=model); trace["runden"].append(r1)
    ex = [lab.run(s["op"], s.get("args", {}), who) for s in (r1.get("plan") or [])[:max_ops] if isinstance(s, dict) and "op" in s]
    p2 = (base + f"\n\nDeine Experimente und Ergebnisse:\n{_fmt(ex)}\n\nRunde 2: Entweder du brauchst noch Experimente "
          f'(dann JSON {{"plan": [...]}} mit bis zu 6 Einträgen) oder du antwortest final als JSON: {ANTWORT_SCHEMA}')
    r2 = ask_json(p2, _sys(strategie), salt=f"{salt}-{strategie}-r2", model=model); trace["runden"].append(r2)
    if "antwort" not in r2 and r2.get("plan"):
        ex += [lab.run(s["op"], s.get("args", {}), who) for s in r2["plan"][:6] if isinstance(s, dict) and "op" in s]
        p3 = base + f"\n\nAlle Experimente und Ergebnisse:\n{_fmt(ex)}\n\nRunde 3 (final): Antworte als JSON: {ANTWORT_SCHEMA}"
        r2 = ask_json(p3, _sys(strategie), salt=f"{salt}-{strategie}-r3", model=model); trace["runden"].append(r2)
    trace["experimente"] = [e["id"] for e in ex]; trace["final"] = r2
    return trace


def _clusterkey(a):
    if a.get("zahl") is not None:
        try: return ("zahl", round(float(a["zahl"]), 3), str(a.get("antwort", "")).lower()[:12])
        except (TypeError, ValueError): pass
    return ("kat", str(a.get("antwort", "")).strip().lower())


def solve(kontext, frage, salt=0, strategien=tuple(STRATEGIEN), domain=None):
    lab = Lab(domain); t0 = time.time(); D = lab.domain
    with ThreadPoolExecutor(len(strategien)) as ex:
        futs = {s: ex.submit(forscher, kontext, frage, s, lab, salt) for s in strategien}
        traces = []
        for s, f in futs.items():
            try: traces.append(f.result())
            except (LLMError, json.JSONDecodeError, KeyError, TypeError) as e: traces.append({"strategie": s, "fehler": str(e)[:300]})
    checks = {}
    for tr in traces:
        a = tr.get("final") or {}; ps = a.get("pruefungen") or ([a["pruefung"]] if isinstance(a.get("pruefung"), dict) else [])
        ps = [p for p in ps if isinstance(p, dict)]
        if not ps: tr["pruefung"] = {"bestanden": False, "grund": "keine Prüfung angegeben"}; continue
        res = []
        for p in ps:
            k = json.dumps(p, sort_keys=True)
            if k not in checks: checks[k] = D.check(p)[:2]
            res.append(checks[k])
        tr["pruefung"] = {"bestanden": all(bool(o) for o, _ in res), "grund": " | ".join(w for _, w in res)}
    verified = [tr for tr in traces if tr.get("pruefung", {}).get("bestanden")]
    if verified:
        groups = {}
        for tr in verified: groups.setdefault(_clusterkey(tr["final"]), []).append(tr)
        best = max(groups.values(), key=len); ans = dict(best[0]["final"]); ans["stimmen"] = f"{len(best)}/{len(traces)} (geprüft: {len(verified)})"
        level = "computed (Code-Prüfer bestanden)"
    else:
        ans = {"antwort": "unbekannt", "zahl": None, "konfidenz": 0.0, "stimmen": f"0/{len(traces)} geprüft"}; level = "keine geprüfte Behauptung"
    return {"antwort": ans, "level": level, "forscher": traces, "experimente": lab.log, "sek": round(time.time() - t0, 1)}


def consistent(ans, p):
    """Passt die Antwort zur geprüften Behauptung? (verhindert 'Prüfung bestanden, aber Antworttext etwas anderes')"""
    t = str(ans.get("antwort", "")).lower(); z = ans.get("zahl")
    try: z = float(z) if z is not None else None
    except (TypeError, ValueError): z = None
    typ = p.get("typ")
    if typ in ("argmin2d", "argmin3d"): return str(p.get("erwartet", "")).lower()[:6] in t or t.startswith(("ja", "yes"))
    if typ == "argmin_nd": return str(p.get("erwartet", "")).lower() in t or t.startswith(("ja", "yes"))
    if typ == "vorzeichenwechsel": return z is not None and float(p["nu_lo"]) - 1e-9 <= z <= float(p["nu_hi"]) + 1e-9
    if typ == "grenzwert": return z is not None and abs(z - float(p["erwartet"])) <= max(float(p.get("toleranz", 0)), 1e-3)
    return True


KASKADE = (("sparsam", "haiku"), ("numeriker", "haiku"), ("skeptiker", "sonnet"), ("theoretiker", "sonnet"))


def solve_cascade(kontext, frage, salt=0, stufen=KASKADE, domain=None, neu=None):
    """Kostenoptimiert: Forscher nacheinander, günstiges Modell zuerst; Stopp bei der ersten Behauptung, die den
    Code-Prüfer besteht und zur Antwort passt. Der Prüfer garantiert die Wahrheit, also reicht eine geprüfte Behauptung."""
    lab = Lab(domain); D = lab.domain; t0 = time.time(); traces = []; checks = {}
    for strategie, model in stufen:
        try: tr = forscher(kontext, frage, strategie, lab, f"K{salt}-{model}", model=model)
        except (LLMError, json.JSONDecodeError, KeyError, TypeError) as e: traces.append({"strategie": strategie, "modell": model, "fehler": str(e)[:300]}); continue
        tr["modell"] = model; a = tr.get("final") or {}
        ps = [p for p in (a.get("pruefungen") or ([a["pruefung"]] if isinstance(a.get("pruefung"), dict) else [])) if isinstance(p, dict)]
        res = []
        for p in ps:
            k = json.dumps(p, sort_keys=True)
            if k not in checks: checks[k] = D.check(p)[:2]
            res.append(checks[k])
        ok = bool(ps) and all(o for o, _ in res) and all(D.consistent(a, p) for p in ps)
        grund = " | ".join(w for _, w in res) or "keine Prüfung angegeben"
        if ok and neu is not None and not any(neu(p) for p in ps):     # nur schon Zertifiziertes wiederholt -> kein Fortschritt
            ok = False; grund = "bestanden, aber bereits zertifiziert (kein neues Resultat): " + grund
        tr["pruefung"] = {"bestanden": ok, "grund": grund}; traces.append(tr)
        if ok:
            ans = dict(a); ans["stimmen"] = f"Stufe {len(traces)}/{len(stufen)} ({strategie}, {model})"
            return {"antwort": ans, "level": "computed (Code-Prüfer bestanden)", "forscher": traces, "experimente": lab.log, "sek": round(time.time() - t0, 1)}
    return {"antwort": {"antwort": "unbekannt", "zahl": None, "konfidenz": 0.0, "stimmen": "keine Stufe geprüft"}, "level": "keine geprüfte Behauptung",
            "forscher": traces, "experimente": lab.log, "sek": round(time.time() - t0, 1)}
