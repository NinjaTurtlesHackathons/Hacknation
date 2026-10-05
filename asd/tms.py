"""Wahrheitspflege (truth maintenance) über das Claim-Feld "benutzt" (Liste der claim_ids, auf denen ein Claim aufbaut).

- widerrufen(state, cid, grund): Claim wird widerrufen/angefochten; alle transitiv abhängigen Claims -> "abhängig_ungültig" (protokolliert).
- bestaetigen(state, cid): Claim wieder bestätigt; abhängige Claims, deren Abhängigkeiten alle wieder gelten, erhalten ihren alten Status zurück.
- reihenfolge(claims): topologische Ordnung (Abhängigkeiten zuerst), z. B. Lemma -> Theorem im Paper.
Der Prüfer prüft eine Kombination selbst (Domain.check); "benutzt" dokumentiert nur die Herkunft, ersetzt keine Prüfung."""
import time

GUELTIG = ("bestätigt",)


def _abhaengige(state, cid):
    """Alle Claims, die (transitiv) auf cid aufbauen."""
    out, neu = set(), {cid}
    while neu:
        n = {c["id"] for c in state.get("claims", []) if set(c.get("benutzt") or []) & neu and c["id"] not in out}
        out |= n; neu = n
    return out


def _log(state, eintrag):
    state.setdefault("tms_log", []).append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **eintrag})


def widerrufen(state, cid, grund, status="widerrufen"):
    by = {c["id"]: c for c in state.get("claims", [])}
    if cid not in by: raise KeyError(cid)
    by[cid]["status_vorher"] = by[cid].get("status"); by[cid]["status"] = status
    betroffen = sorted(_abhaengige(state, cid))
    for d in betroffen:
        if by[d].get("status") != "abhängig_ungültig": by[d]["status_vorher"] = by[d].get("status")
        by[d]["status"] = "abhängig_ungültig"; by[d]["ungueltig_wegen"] = cid
    _log(state, {"aktion": status, "claim": cid, "grund": grund, "herabgestuft": betroffen})
    return betroffen


def bestaetigen(state, cid, grund="erneut bestätigt"):
    by = {c["id"]: c for c in state.get("claims", [])}
    by[cid]["status"] = "bestätigt"; wieder = []
    for _ in range(len(by)):                                         # Fixpunkt: Ketten wiederherstellen
        geaendert = False
        for c in by.values():
            if c.get("status") == "abhängig_ungültig" and all(by.get(b, {}).get("status") in GUELTIG for b in c.get("benutzt") or []):
                c["status"] = c.pop("status_vorher", "bestätigt") or "bestätigt"; c.pop("ungueltig_wegen", None); wieder.append(c["id"]); geaendert = True
        if not geaendert: break
    _log(state, {"aktion": "wiederhergestellt", "claim": cid, "grund": grund, "wiederhergestellt": wieder})
    return wieder


def reihenfolge(claims, key="id"):
    """Topologisch sortiert: jeder Claim nach den Claims, die er benutzt (stabil bezüglich der Eingabereihenfolge)."""
    by = {c[key]: c for c in claims}; fertig, out = set(), []
    def besuch(c, pfad=()):
        if c[key] in fertig or c[key] in pfad: return
        for b in c.get("benutzt") or []:
            if b in by: besuch(by[b], pfad + (c[key],))
        fertig.add(c[key]); out.append(c)
    for c in claims: besuch(c)
    return out
