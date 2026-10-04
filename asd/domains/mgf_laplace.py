"""Exakter Laplace-Operator auf dihedralen Modulgraphfunktionen C_{a,b,c} (rationale Linearalgebra, keine Numerik).

Herleitung (termweise auf den Gittersummen, f_a(p) = (tau2/(pi |p|^2))^a, p = m tau + n, Delta = 4 tau2^2 d d-bar):
  Delta f_a = a(a-1) f_a,   d f_a = a f_a pbar/(2i tau2 p),   dbar f_a = -a f_a p/(2i tau2 pbar),
  Delta(f_a(p1) f_b(p2)) = [a(a-1)+b(b-1)] f f + a b f f (z + zbar),  z = pbar1 p2/(p1 pbar2),
  und mit x_i = |p_i|^2, p3 = -p1-p2:  z + zbar = x1/x2 + x2/x1 + x3^2/(x1 x2) - 2 x3/x2 - 2 x3/x1.
Für jedes Paar (i,j) mit drittem Index k folgt
  Delta C_{a} = sum_i a_i(a_i-1) C_a + sum_{i<j} a_i a_j [C(a_i-1,a_j+1) + C(a_i+1,a_j-1) + C(a_i+1,a_j+1,a_k-2)
                                                         - 2 C(a_j+1,a_k-1) - 2 C(a_i+1,a_k-1)].
Randterme:  C_{a,b,0} = E_a E_b - E_{a+b},   C_{a,b,-1} = E_{a-1} E_b + E_a E_{b-1}   (f_{-1}(0) = 0; der Mischterm
Re(p1 pbar2) summiert sich bei p1 -> -p1 weg). E_1 und E_0 sind divergent und erscheinen nur formal; sie müssen sich aufheben
(wird geprüft). Dieselbe Formel steht (in anderer Notation) in D'Hoker-Green-Gurdogan-Vanhove; hier wird sie zusätzlich
gegen die numerische Laplace-Auswertung geprüft (asd/domains/mgf.py)."""
from fractions import Fraction as Fr
from itertools import combinations


def _C(a):
    return ("C", tuple(sorted(a, reverse=True)))


def _E(*s):
    return ("E", tuple(sorted(s, reverse=True)))


def reduce_C(a, coef, out):
    """C mit Index 0 oder -1 in Eisenstein-Produkte auflösen; sonst als C-Symbol eintragen."""
    a = list(a)
    if min(a) >= 1:
        k = _C(a); out[k] = out.get(k, 0) + coef; return
    if min(a) < -1: raise ValueError(f"Index < -1 in C{tuple(a)}")
    if sorted(a).count(0) + sorted(a).count(-1) > 1: raise ValueError(f"zwei Randindizes in C{tuple(a)}")
    i = a.index(min(a)); x, y = [a[j] for j in range(3) if j != i]
    if a[i] == 0:
        for k, c in ((_E(x, y), 1), (_E(x + y), -1)): out[k] = out.get(k, 0) + coef * c
    else:
        for k, c in ((_E(x - 1, y), 1), (_E(x, y - 1), 1)): out[k] = out.get(k, 0) + coef * c


def laplace_C(a3):
    """Delta C_{a,b,c} als dict {Symbol: rationaler Koeffizient}."""
    a3 = list(a3); out = {}
    reduce_C(a3, Fr(sum(x * (x - 1) for x in a3)), out)
    for i, j in combinations(range(3), 2):
        k = 3 - i - j; ai, aj = a3[i], a3[j]; c = Fr(ai * aj)
        def sh(di, dj, dk):
            v = list(a3); v[i] += di; v[j] += dj; v[k] += dk; return v
        reduce_C(sh(-1, 1, 0), c, out); reduce_C(sh(1, -1, 0), c, out); reduce_C(sh(1, 1, -2), c, out)
        reduce_C(sh(0, 1, -1), -2 * c, out); reduce_C(sh(1, 0, -1), -2 * c, out)
    return {k: v for k, v in out.items() if v != 0}


def dihedral(w):
    return [(a, b, c) for a in range(w, 0, -1) for b in range(a, 0, -1) for c in range(b, 0, -1) if a + b + c == w]


def fmt(sym):
    t, a = sym
    return ("C(%d,%d,%d)" % a) if t == "C" else "*".join(f"E({s})" for s in a)


def laplace_combo(vec):
    """Delta von sum_i vec[a_i] C_{a_i} (vec: {(a,b,c): Fr})."""
    out = {}
    for a, c in vec.items():
        for k, v in laplace_C(a).items(): out[k] = out.get(k, 0) + c * v
    return {k: v for k, v in out.items() if v != 0}


def harmonic_space(w):
    """Alle rationalen Kombinationen X = sum c_abc C_abc vom Gewicht w mit Delta X in Q * E_w (exakt).
    Rückgabe: Basis als Liste von (vec, lambda) mit Delta X = lambda * E_w."""
    Cs = dihedral(w); rows = [laplace_C(a) for a in Cs]
    syms = sorted({k for r in rows for k in r} - {_E(w)})
    # Bedingung: sum_i c_i rows[i][s] = 0 für alle s != E_w
    A = [[Fr(rows[i].get(s, 0)) for i in range(len(Cs))] for s in syms]
    ker = _kernel(A, len(Cs))
    out = []
    for v in ker:
        vec = {Cs[i]: v[i] for i in range(len(Cs)) if v[i] != 0}
        lam = sum(v[i] * Fr(rows[i].get(_E(w), 0)) for i in range(len(Cs)))
        out.append((vec, lam))
    return out


def _kernel(A, n):
    import math
    M = [row[:] for row in A]; piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]; out = []
    for f in free:
        v = [Fr(0)] * n; v[f] = Fr(1)
        for i, c in enumerate(piv): v[c] = -M[i][f]
        den = math.lcm(*[x.denominator for x in v]); v = [x * den for x in v]
        g = 0
        for x in v: g = math.gcd(g, int(x))
        out.append([x / g for x in v])
    return out
