"""Demo einer experimentellen Domäne (Vorlage für Labore): Enzymaktivität unter verschiedenen Bedingungen.
Nur ein Beispiel für die Struktur; die Messungen kommen vom Menschen (CSV). Für Tests gibt es asd/simulate_messung.py."""
from .experimental import ExperimentalDomain


class AssayDemo(ExperimentalDomain):
    name = "assay_demo"
    kontext = ("Ein Enzym wird unter verschiedenen Bedingungen auf seine Aktivität getestet (Umsatz pro Minute, Fluoreszenz-Assay). "
               "Faktoren: Temperatur und Zusatz eines Kofaktors. Negativkontrolle: ohne Enzym. Positivkontrolle: Referenzbedingung mit bekanntem Umsatz.")
    faktoren = {"temperatur": ["25C", "30C", "37C", "42C"], "kofaktor": ["ohne", "mit"]}
    messgroesse = "Aktivität"; einheit = "RFU/min"
    kontrollen = {"negativ": "ohne_enzym", "positiv": "referenz"}
    erwartung_kontrollen = "groesser"
    min_replikate = 4
    recherche_ziel = "Temperaturabhängigkeit und Kofaktor-Effekte auf die Enzymaktivität in Fluoreszenz-Assays."
    recherche_klassiker = []

    def parameter(self):
        return {"alpha": ("0.05", "significance level after Benjamini-Hochberg over all tests of the project"),
                "min_replicates": ("4", "minimal replicates per group"), "permutations": ("20000", "permutation test draws, seed 12345")}


DOMAIN = AssayDemo()
