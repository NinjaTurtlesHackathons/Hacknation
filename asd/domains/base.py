"""Domänen-Schnittstelle. Eine neue Wissenschaftsdomäne = eine Unterklasse von Domain. Alles andere (Forscher-Schleife,
Kaskade, Recherche, Labor-Schleife, Paper-Schreiber, Tabellen) ist domänenunabhängig.

Pflicht für jede Domäne:
  kontext          Was die Agenten über das Problem wissen (ohne Antworten!).
  primitive_doc    Liste der Experimente {"op", "args"}, die das Lab ausführen kann.
  claim_doc        Liste der Prüfungstypen {"typ", ...}, die der Prüfer nachrechnen kann.
  run_op(op, args) Führt ein Experiment aus -> JSON-fähiges dict (Fehler als {"fehler": ...}, nie Exception).
  check(p)         Prüfer: (bestanden, Begründung, Belege). Unabhängig nachrechnen, eigene Auflösung/Genauigkeit.
                   Toleranzen und Genauigkeiten kommen NIE aus der Behauptung des Agenten.
  selftest()       Liste (prüfung, erwartet_bool): bekannte wahre UND bekannte falsche Aussagen. Der Selbsttest muss
                   bestehen, bevor die Domäne benutzt werden darf (asd/selftest.py).
Optional:
  consistent(antwort, p)  Passt der Antworttext zur geprüften Behauptung?
  level(p)         Evidenzstufe einer bestandenen Prüfung: proved_lean | computed_rigorous | statistical | observed
"""


class Domain:
    name = "basis"
    kontext = ""
    primitive_doc = ""
    claim_doc = ""

    def run_op(self, op, args):
        raise NotImplementedError

    def check(self, p):
        raise NotImplementedError

    def selftest(self):
        raise NotImplementedError

    def consistent(self, antwort, p):
        return True

    def level(self, p):
        return "observed"


def get_domain(name):
    """Domänen-Registry: name -> Instanz. Neue Domänen hier eintragen (oder per python -m asd.new_domain erzeugen)."""
    import importlib
    mod = importlib.import_module(f"asd.domains.{name}_domain")
    return mod.DOMAIN
