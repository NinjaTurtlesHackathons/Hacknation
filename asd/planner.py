"""Rivalisierende Experimente aus CODE (nicht vom LLM): options(domain, frage, state) -> mindestens 2 zulässige Optionen.

Jede Option: id, art, beschreibung, kosten (erwartete Verifier-Aufrufe), erwarteter_gewinn (0..1), vorgehen (Anweisung an den
Forscher), max_ops. Der Gewinn ist eine einfache, nachvollziehbare Heuristik aus dem Zustand des Fadens:
  - viele Ablehnungen im Faden  -> breiter Scan lohnt (man weiß zu wenig)
  - bestätigte Claims im Faden  -> Verallgemeinerung / Grenzfall lohnt (Tiefe statt Breite)
  - noch nichts im Faden        -> tiefe, gezielte Rechnung an wenigen Punkten ist günstig
Domänen können `optionen(frage, state)` selbst definieren; sonst gilt dieser generische Planer."""


def _faden_stats(state, frage):
    fid = frage.get("faden_id") or frage.get("id")
    qids = {q["id"] for q in state.get("fragen", []) if (q.get("faden_id") or q["id"]) == fid}
    runden = {r["runde"] for r in state.get("runden", []) if r.get("frage") in qids}
    best = [c for c in state.get("claims", []) if c.get("status") == "bestätigt" and c.get("runde") in runden]
    abgelehnt = [w for w in state.get("widerlegt", []) if isinstance(w, dict) and w.get("frage_id") in qids]
    return fid, best, abgelehnt


def options(domain, frage, state):
    if hasattr(domain, "optionen"):
        o = domain.optionen(frage, state)
        if o and len(o) >= 2: return o
    fid, best, abgelehnt = _faden_stats(state, frage)
    n_b, n_a = len(best), len(abgelehnt)
    unsicher = n_a / (n_a + n_b + 1)                       # Anteil der Ablehnungen im Faden
    O = [
        {"id": "O1", "art": "breiter_scan",
         "beschreibung": "Breiter Scan über viele Parameterwerte mit geringer Präzision, danach bis zu 3 Kandidaten-Behauptungen prüfen.",
         "kosten": 3, "erwarteter_gewinn": round(0.35 + 0.4 * unsicher, 3), "max_ops": 12,
         "vorgehen": "Scanne zuerst grob über einen weiten Parameterbereich (viele billige Experimente), identifiziere die auffälligste "
                     "Struktur und formuliere die Behauptung, die der Scan am besten stützt."},
        {"id": "O2", "art": "tiefe_rechnung",
         "beschreibung": "Tiefe, möglichst zertifizierte Rechnung an wenigen, gezielt gewählten Punkten; genau eine Behauptung prüfen.",
         "kosten": 1, "erwarteter_gewinn": round(0.55 - 0.3 * unsicher + (0.1 if n_b == 0 else 0), 3), "max_ops": 6,
         "vorgehen": "Wähle wenige, maximal informative Punkte, rechne dort mit höchster Präzision und formuliere genau eine scharfe, "
                     "prüfbare Behauptung."},
    ]
    if n_b:
        O.append({"id": "O3", "art": "verallgemeinerung",
                  "beschreibung": f"Verallgemeinerung des bestätigten Claims {best[-1]['id']} (größere Klasse, Allaussage, Grenzwert).",
                  "kosten": 2, "erwarteter_gewinn": round(0.5 + 0.1 * min(n_b, 3), 3), "max_ops": 8,
                  "vorgehen": f"Ausgangspunkt ist der geprüfte Claim [{best[-1]['id']}]: {best[-1]['text'][:200]}. Suche die allgemeinere oder "
                              "asymptotische Aussage (alle Parameter, Grenzwert, Familie) und prüfe sie."})
        O.append({"id": "O4", "art": "grenzfall",
                  "beschreibung": f"Grenzfall/Gegenbeispielsuche zu {best[-1]['id']}: wo hört die Aussage auf zu gelten?",
                  "kosten": 2, "erwarteter_gewinn": round(0.4 + 0.05 * min(n_b, 3), 3), "max_ops": 8,
                  "vorgehen": f"Suche gezielt den Rand der Gültigkeit von [{best[-1]['id']}] (extreme Parameter, Vorzeichenwechsel) und prüfe ihn."})
    for o in O: o["faden_id"] = fid; o["frage_id"] = frage.get("id")
    return sorted(O, key=lambda o: -o["erwarteter_gewinn"] / o["kosten"] ** 0.5)
