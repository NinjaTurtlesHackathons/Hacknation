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
  describe(p)      Kanonische Aussage, die eine bestandene Prüfung beweist (Pflicht für ehrliche Paper-Sätze).
  parameter()      Feste Modellparameter {name: (wert, bedeutung)}; werden im Paper als Claim C-modell belegt.
  relevanz(p)      hauptresultat | stuetze | beispiel (Benennung Theorem/Proposition/Example im Paper).
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

    def parameter(self):
        """Feste Modellparameter als {name: (wert, bedeutung)}. Ohne Eintrag warnt der Paper-Bau, weil Konstanten sonst
        nicht im Paper stehen dürfen (das Halluzinations-Gate streicht jede unbelegte Zahl)."""
        return {}

    def widerspricht(self, p, q):
        """True, wenn die bestandenen Prüfungen p und q logisch nicht beide wahr sein können (Red-Team-Kriterium).
        Standard: kein bekannter Widerspruch. Domänen sollten das für ihre Prüfungstypen definieren."""
        return False

    def figures(self, state, outdir):
        """Optional: Abbildungen aus geprüften Aussagen. Gibt [(dateiname, bildunterschrift_mit_claim_ids)] zurück."""
        return []

    def describe(self, p):
        """Kanonische Aussage, die eine BESTANDENE Prüfung p beweist, erzeugt aus p selbst (nicht aus dem Text des Agenten).
        Nur diese Aussage darf als Resultat ins Paper. Der Antworttext des Agenten ist bloß Interpretation."""
        import json
        return "Prüfung bestanden: " + json.dumps(p, ensure_ascii=False)


def get_domain(name):
    """Domänen-Registry: name -> Instanz. Neue Domänen hier eintragen (oder per python -m asd.new_domain erzeugen)."""
    import importlib
    mod = importlib.import_module(f"asd.domains.{name}_domain")
    return mod.DOMAIN
