"""Gitter-Domäne (Suleman 2026) als Domain-Implementierung. Referenzbeispiel für numerische Prüfer."""
import numpy as np
from .base import Domain
from . import lattice as L
from .. import verify


class LatticeDomain(Domain):
    name = "lattice"
    kontext = ("Betrachtet wird die Dreikörper-Energie T_nu(L) = Summe über alle Paare verschiedener Gittervektoren x != y, beide ungleich 0, "
               "von (|x| |y| |x-y|)^(-nu), für Bravais-Gitter L mit Kovolumen 1. In 2D: tau = x + i y im Fundamentalbereich.")

    @property
    def primitive_doc(self): return L.PRIMITIVE_DOC

    @property
    def claim_doc(self):
        from ..discovery import CLAIM_DOC
        return CLAIM_DOC

    def run_op(self, op, args): return L.run_op(op, args)

    def check(self, p): return verify.check(p)

    def consistent(self, antwort, p):
        from ..discovery import consistent
        return consistent(antwort, p)

    def selftest(self):
        return [({"typ": "argmin2d", "nu": 5, "erwartet": "quadratisch"}, True),
                ({"typ": "argmin2d", "nu": 5, "erwartet": "hexagonal"}, False),
                ({"typ": "vorzeichenwechsel", "groesse": "diff_hex_quadrat", "nu_lo": 3.915, "nu_hi": 3.92}, True),
                ({"typ": "vorzeichenwechsel", "groesse": "diff_hex_quadrat", "nu_lo": 3.90, "nu_hi": 3.91}, False),
                ({"typ": "grenzwert", "groesse": "y_inf", "erwartet": 1.249621}, True),
                ({"typ": "grenzwert", "groesse": "y_inf", "erwartet": 1.24869, "toleranz": 0.005}, False),   # Schlupfloch aus H4
                ({"typ": "argmin3d", "nu": 5, "erwartet": "fcc"}, False)]


    def describe(self, p):
        t = p.get("typ")
        if t == "argmin2d": return f"Bei nu = {p['nu']} findet die unabhängige globale Suche des Prüfers als 2D-Minimierer: {p['erwartet']}" + (f" mit y = {p['y']}" if p.get("y") else "") + " (numerisch)."
        if t == "argmin3d": return f"Bei nu = {p['nu']} hat {p['erwartet']} unter BCC, FCC, SC und dem Bain-Pfad die niedrigste Energie (numerisch)."
        if t == "argmin_nd": return f"Bei nu = {p['nu']} findet die unabhängige Suche des Prüfers (d = {p['d']}) nichts Besseres als {p['erwartet']} (numerisch)."
        if t == "vorzeichenwechsel": return f"{p['groesse']} wechselt das Vorzeichen zwischen nu = {p['nu_lo']} und nu = {p['nu_hi']} (numerisch, Fehlerschätzung)."
        if t == "koexistenz": return f"Bei nu = {p['nu']} sind hexagonales und quadratisches Gitter beide lokale Minima (numerisch)."
        if t == "grenzwert": return f"Fit des Prüfers: {p['groesse']} = {p['erwartet']} innerhalb der festen Toleranz (numerisch)."
        if t == "vergleich_nd": return f"Bei nu = {p['nu']} hat {p['gitter']} eine niedrigere Energie als {', '.join(p.get('gegen') or [])} (numerisch, zwei Auflösungen)."
        return super().describe(p)


DOMAIN = LatticeDomain()
