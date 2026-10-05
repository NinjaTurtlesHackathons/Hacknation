"""Exakte Laurent-Koeffizienten der Zweischleifen-Modulgraphfunktionen nach D'Hoker-Kaidi (arXiv:1902.04180):
Proposition 2.1 (Partialbruchzerlegung C_{a,b,c} -> C_{u,v;w}) und Theorem 5.1 (Gl. 5.4/5.5, Koeffizienten l_{2k-w+1} von
zeta(2w-2k-1)/(4 pi tau2)^{w-2k-1}). Theorem 5.1 ist dort bewiesen (Anhang A); die Vermutung 6.2 aus [11] betrifft nur l_{2-w}
und wird hier nicht benutzt. Alles in rationaler Arithmetik."""
from fractions import Fraction as Fr
from math import comb, factorial
from sympy import bernoulli as _bern


def B(n): return Fr(int(_bern(n).p), int(_bern(n).q)) if n != 1 else Fr(-1, 2)


def binom(n, k): return comb(n, k) if 0 <= k <= n and n >= 0 else 0


def Lam(k, a1, a2):
    """Gl. (2.29): Lambda_k(a1, a2) = (-1)^{a1+a2+k} binom(a1+a2-k-1, a2-1)."""
    return (-1) ** (a1 + a2 + k) * binom(a1 + a2 - k - 1, a2 - 1)


def zerlegung(a, b):
    """Prop. 2.1: C[a1 a2 a3; b1 b2 b3] (alle a1,a2,b1,b2 >= 1) als {(u, v): Koeffizient} in C_{u,v;w} = C[u 0 w-u; 0 v w-v]."""
    w = sum(a); assert w == sum(b)
    out = {}
    def add(u, v, c):
        if c: out[(u, v)] = out.get((u, v), 0) + c
    for (A, Bv) in ((a, b), ((a[1], a[0], a[2]), (b[1], b[0], b[2]))):    # Term und (1 <-> 2); Spaltentausch 1<->2 ist Umbenennung p1<->p2
        a1, a2, a3 = A; b1, b2, b3 = Bv
        for k in range(1, a1 + 1):
            for l in range(1, b1 + 1): add(w - k, w - l, Lam(k, a1, a2) * Lam(l, b1, b3))        # C[a-k 0 k; 0 b-l l]
            for l in range(1, b3 + 1): add(k, w - l, Lam(k, a1, a2) * Lam(l, b3, b1))            # C[k 0 a-k; 0 b-l l]
    return {k: v for k, v in out.items() if v}


def ell(k, u, v, w):
    """Gl. (5.5): Koeffizient l_{2k-w+1} von zeta(2w-2k-1)/(4 pi tau2)^{w-2k-1} in L_{u,v;w}."""
    t = Fr(0)
    for (x, y) in ((u, v), (v, u)):
        if x // 2 - k >= 0:
            t += 2 * Fr((-1) ** (y + 1)) * B(2 * k) / factorial(2 * k) * binom(2 * w - 2 * k - 2, w - x - 1) * binom(x + y - 1 - 2 * k, x - 2 * k)
    if (2 * w - u - v) // 2 - k >= 0:
        t += 2 * Fr((-1) ** (w + 1)) * B(2 * k) / factorial(2 * k) * binom(2 * w - 2 * k - 2, 2 * w - u - v - 2 * k) * binom(u + v - 2, v - 1)
    return t


def ell_C(abc, k):
    """l_{2k-w+1} fuer die dihedrale C_{a,b,c} (a = b in DK-Notation)."""
    w = sum(abc)
    return sum(c * ell(k, u, v, w) for (u, v), c in zerlegung(tuple(abc), tuple(abc)).items())


def konstante(combo):
    """Koeffizient von zeta(w) im Konstantterm (tau2^0) einer Kombination {(a,b,c): Koeffizient} von ungeradem Gewicht w."""
    w = sum(next(iter(combo))); assert w % 2 == 1
    return sum(Fr(c) * ell_C(abc, (w - 1) // 2) for abc, c in combo.items())
