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


DOMAIN = LatticeDomain()
