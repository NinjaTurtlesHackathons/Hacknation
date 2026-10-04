"""Unabhängige Kontrolle: direkte Gittersummen für E_s und C_{a,b,c} in doppelter Genauigkeit (numpy), Abschneiden |m|,|n| <= L.
Völlig anderer Algorithmus als asd/domains/mgf.py (keine Poisson-Summation, keine Extrapolation); Genauigkeit ~1e-9..1e-12."""
import numpy as np


def _lattice(t1, t2, L):
    m, n = np.meshgrid(np.arange(-L, L + 1), np.arange(-L, L + 1), indexing="ij")
    m, n = m.ravel(), n.ravel(); keep = (m != 0) | (n != 0)
    return m[keep], n[keep]


def E(s, t1, t2, L=60):
    m, n = _lattice(t1, t2, L)
    x = (m * t1 + n) ** 2 + (m * t2) ** 2
    return float(np.sum((t2 / (np.pi * x)) ** s))


def C(a3, t1, t2, L=20):
    """sum_{p1,p2 != 0, p1+p2 != 0} f_a(p1) f_b(p2) f_c(p1+p2), beide Impulse im Kasten |m|,|n| <= L (p3 beliebig)."""
    a, b, c = a3; m, n = _lattice(t1, t2, L)
    f = lambda mm, nn, e: (t2 / (np.pi * ((mm * t1 + nn) ** 2 + (mm * t2) ** 2))) ** e
    fa, fb = f(m, n, a), f(m, n, b); tot = 0.0
    for i in range(len(m)):                       # p1 fest, p2 vektorisiert
        m3, n3 = m[i] + m, n[i] + n; ok = (m3 != 0) | (n3 != 0)
        tot += fa[i] * float(np.sum(fb[ok] * f(m3[ok], n3[ok], c)))
    return tot
