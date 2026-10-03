"""Domäne: {{NAME}}  —  erzeugt mit `python -m asd.new_domain {{NAME}}`.

Ausfüllen in dieser Reihenfolge (Verifizierer zuerst!):
 1. check() und selftest(): Was gilt als bewiesen/geprüft? Mindestens 2 bekannte WAHRE und 2 bekannte FALSCHE Aussagen.
    `python -m asd.selftest {{NAME}}` muss bestehen, bevor irgendein Agent läuft.
 2. run_op(): die Experimente (Simulation, Rechnung, Datenabfrage). Fehler als {"fehler": ...} zurückgeben, nie werfen.
 3. kontext, primitive_doc, claim_doc: genau das, was die Agenten sehen. KEINE Antworten, keine Testdaten.
Regeln:
 - Toleranzen, Genauigkeit, Auflösung bestimmt der Prüfer, nie die Behauptung des Agenten.
 - Der Prüfer rechnet unabhängig nach (andere Auflösung/Methode/Seed als die Experimente), idealerweise exakt oder rigoros.
 - Gleitkomma-Ergebnisse heißen „numerisch“; level() gibt die ehrliche Evidenzstufe zurück.
"""
from .base import Domain


def experiment_beispiel(x: float) -> dict:
    """Beispiel-Experiment: ersetze durch deine Simulation/Rechnung."""
    return {"y": x * x, "hinweis": "numerisch"}


class MyDomain(Domain):
    name = "{{NAME}}"
    recherche_ziel = "{{FORSCHUNGSZIEL in einem Satz, für den Scout (arXiv, Europe PMC)}}"
    recherche_sperre = []          # Wörter, deren Quellen gesperrt werden (z. B. Paper mit dem Antwortschlüssel)
    kontext = "{{Was die Agenten über das Problem wissen: Modell, Größen, Einheiten, Regeln, bekannte Anker (ohne Antworten).}}"
    primitive_doc = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}):
- quadrat {x}: berechnet y = x^2 (Beispiel)."""
    claim_doc = """Prüfungstypen:
- {"typ": "wert", "x": Zahl, "y": Zahl}: Der Prüfer rechnet y(x) unabhängig nach (feste Toleranz 1e-9)."""

    def run_op(self, op, args):
        try:
            if op == "quadrat": return experiment_beispiel(float(args["x"]))
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    def check(self, p):
        try:
            if p.get("typ") == "wert":
                y = float(p["x"]) ** 2                                   # unabhängige Nachrechnung
                ok = abs(y - float(p["y"])) <= 1e-9 * max(1.0, abs(y))   # Toleranz fest im Prüfer
                return ok, f"Prüfer: y({p['x']}) = {y}", {"y": y}
            return False, f"unbekannter Prüfungstyp {p.get('typ')}", {}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def selftest(self):
        return [({"typ": "wert", "x": 3, "y": 9}, True), ({"typ": "wert", "x": 2, "y": 4}, True),
                ({"typ": "wert", "x": 3, "y": 10}, False), ({"typ": "wert", "x": 2, "y": 4.1}, False)]

    def level(self, p):
        return "computed_rigorous"       # ehrlich: proved_lean | computed_rigorous | statistical | observed


DOMAIN = MyDomain()
