"""Hochpräzise Auswertung zweischleifiger (dihedraler) Modulgraphfunktionen C_{a,b,c}(tau) und nicht-holomorpher
Eisenstein-Reihen E_s(tau) in der Normierung von D'Hoker-Green-Vanhove:

    E_s(tau)       = sum'_{p in Lambda}            (tau2 / (pi |p|^2))^s
    C_{a,b,c}(tau) = sum'_{p1+p2+p3=0, p_i != 0}  prod_i (tau2 / (pi |p_i|^2))^{a_i},   p = m tau + n.

Methode (keine Abschneide-Extrapolation in zwei Dimensionen):
 1. Poisson-Summation über n: fuer festes m ist h_{a,m}(x) = sum_n (tau2/pi)^a |m tau + n|^{-2a} e^{2 pi i n x} in
    geschlossener Form bekannt (Bernoulli-Polynom fuer m = 0, sonst Exponential-Polynome mit Polylogarithmen Li_{-i}).
    Die Faltung ueber n1+n2+n3 = 0 ist S(m) = int_0^1 h1 h2 h3 dx und wird exakt integriert.
 2. S(m) = R(m) + D(m): R ist der fuehrende, rein rationale Anteil (Randpunkte x = 0 und x = 1), D faellt
    exponentiell in min |m_i|. sum R ueber das ganze Gitter ist eine Summe von Tornheim-Reihen und wird exakt auf
    Doppel-Zeta-Werte zurueckgefuehrt; D wird auf den Geraden {|m_i| <= K} summiert (Inklusion-Exklusion), entlang
    jeder Geraden mit Richardson-Extrapolation (Summand dort rational in t plus exponentiell klein).
Ergebnis: numerisch, typischerweise 25-35 gueltige Stellen (wird gegen C_{1,1,1} = E_3 + zeta(3) und gegen die
Bessel-Darstellung von E_s geprueft).
"""
import functools
import mpmath as mp
from math import comb, factorial


def c_coef(a, j):
    """Fourier-Transformierte von (t^2+v^2)^{-a}:  (pi / v^{2a-1}) e^{-w} sum_j c_{a,j} w^j,  w = 2 pi v |xi|."""
    return mp.mpf(factorial(2 * a - 2 - j)) / (factorial(j) * factorial(a - 1 - j) * factorial(a - 1) * 2 ** (2 * a - 2 - j))


def _polymul(p, q):
    r = [mp.mpc(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        if x == 0: continue
        for j, y in enumerate(q): r[i + j] += x * y
    return r


def _li_neg(i, z):
    """sum_{l>=0} l^i z^l  (i = 0: 1/(1-z))."""
    return 1 / (1 - z) if i == 0 else mp.polylog(-i, z)


class Tau:
    def __init__(self, t1, t2, dps):
        self.dps = dps
        self.t1, self.t2 = mp.mpf(t1), mp.mpf(t2)
        self.cache = {}

    def h(self, a, m):
        """h_{a,m}(x) als Liste von Stuecken (typ, K, praefaktor, polynom in x):
        Wert = praefaktor * e^{2 pi tau2 K x} * e^{-2 pi i m tau1 x} * poly(x).  typ 'A' (Rand x=0), 'B' (Rand x=1), 'P' (m = 0)."""
        key = (a, m)
        if key in self.cache: return self.cache[key]
        t1, t2 = self.t1, self.t2; pre = (t2 / mp.pi) ** a
        if m == 0:
            bern = mp.mpf(-1) ** (a + 1) * (2 * mp.pi) ** (2 * a) / mp.factorial(2 * a)
            coeffs = [pre * bern * mp.mpf(comb(2 * a, k)) * mp.bernoulli(2 * a - k) for k in range(2 * a + 1)]   # B_{2a}(x) = sum C(2a,k) B_{2a-k} x^k
            out = [("P", 0, mp.mpf(1), [mp.mpc(c) for c in coeffs])]
        else:
            v = abs(m) * t2; u = m * t1
            lam_neg = -2j * mp.pi * u - 2 * mp.pi * v          # Lambda'
            lam_pos = 2j * mp.pi * u - 2 * mp.pi * v           # Lambda
            zn, zp = mp.exp(lam_neg), mp.exp(lam_pos)
            base = pre * mp.pi * v ** (1 - 2 * a)
            pa = [mp.mpc(0)] * a; pb = [mp.mpc(0)] * a      # Polynome in x (A) bzw. in y = 1-x (B)
            for j in range(a):
                cj = base * c_coef(a, j) * (2 * mp.pi * v) ** j
                for i in range(j + 1):
                    pa[j - i] += cj * comb(j, i) * _li_neg(i, zn)
                    pb[j - i] += cj * comb(j, i) * _li_neg(i, zp)
            pbx = [mp.mpc(0)] * a                              # (1-x)^k ausmultiplizieren
            for k, ck in enumerate(pb):
                for l in range(k + 1): pbx[l] += ck * comb(k, l) * (-1) ** l
            # A: e^{Lambda' x} = e^{-2 pi i u x} e^{-2 pi v x}           -> K = -|m|
            # B: e^{Lambda (1-x)} = e^{Lambda} e^{-2 pi i u x} e^{+2 pi v x} -> K = +|m|, Praefaktor e^{Lambda}
            out = [("A", -abs(m), mp.mpf(1), pa), ("B", abs(m), zp, pbx)]
        self.cache[key] = out
        return out

    def S(self, a3, m3):
        """S(m) = int_0^1 prod_i h_{a_i, m_i}(x) dx exakt (sum m_i = 0, daher heben sich die Phasen e^{-2 pi i m tau1 x} auf).
        Die Stuecke werden nach dem Exponenten K gesammelt und je K einmal integriert."""
        assert sum(m3) == 0
        acc = {}
        for p1 in self.h(a3[0], m3[0]):
            for p2 in self.h(a3[1], m3[1]):
                q12 = _polymul(p1[3], p2[3]); pre12 = p1[2] * p2[2]; K12 = p1[1] + p2[1]
                for p3 in self.h(a3[2], m3[2]):
                    poly = _polymul(q12, p3[3]); K = K12 + p3[1]; pre = pre12 * p3[2]
                    tgt = acc.setdefault(K, [mp.mpc(0)] * len(poly))
                    if len(tgt) < len(poly): tgt.extend([mp.mpc(0)] * (len(poly) - len(tgt)))
                    for i, c in enumerate(poly): tgt[i] += pre * c
        tot = mp.mpc(0)
        for K, poly in acc.items():
            I = self.ints(K, len(poly) - 1)
            tot += mp.fsum(c * I[k] for k, c in enumerate(poly))
        return tot

    def ints(self, K, n):
        """[int_0^1 x^k e^{2 pi tau2 K x} dx for k = 0..n], gecacht."""
        key = ("I", K)
        I = self.cache.get(key)
        if I is not None and len(I) > n: return I
        if K == 0: I = [mp.mpf(1) / (k + 1) for k in range(n + 1)]
        else:
            beta = 2 * mp.pi * self.t2 * K; eb = mp.exp(beta)
            with mp.workdps(mp.mp.dps + 3 * n + 10):           # Aufwaertsrekursion: Reserve gegen Ausloeschung
                I = [(eb - 1) / beta]
                for k in range(1, n + 1): I.append(eb / beta - k / beta * I[-1])
            I = [+x for x in I]
        self.cache[key] = I
        return I


def _int_poly_exp(poly, beta, zero):
    """int_0^1 poly(x) e^{beta x} dx exakt."""
    n = len(poly) - 1
    if zero: return sum(c / (k + 1) for k, c in enumerate(poly))
    I = [(mp.exp(beta) - 1) / beta]
    for k in range(1, n + 1): I.append(mp.exp(beta) / beta - k / beta * I[-1])
    return sum(c * I[k] for k, c in enumerate(poly))


# ---------- fuehrender rationaler Anteil R(m) und seine Gittersumme ----------

def rho(a3, ms):
    """R(m) = y^{2-w} rho(m) fuer m_i != 0 (y = pi tau2):  rho = sum_j prod c_{a_i,j_i} J! prod |m_i|^{1-2a_i+j_i} / V^{J+1}."""
    V = sum(abs(m) for m in ms); tot = mp.mpf(0)
    for j1 in range(a3[0]):
        for j2 in range(a3[1]):
            for j3 in range(a3[2]):
                J = j1 + j2 + j3
                t = c_coef(a3[0], j1) * c_coef(a3[1], j2) * c_coef(a3[2], j3) * factorial(J) / mp.mpf(V) ** (J + 1)
                for a, j, m in zip(a3, (j1, j2, j3), ms): t *= mp.mpf(abs(m)) ** (1 - 2 * a + j)
                tot += t
    return tot


@functools.lru_cache(maxsize=None)
def mzv2(a, b, dps):
    """Doppel-Zeta zeta(a,b) = sum_{n>m>=1} n^{-a} m^{-b} = sum_{m>=1} m^{-b} zeta(a, m+1)  (a >= 2)."""
    with mp.workdps(dps + 15):
        return +mp.nsum(lambda m: m ** (-b) * mp.zeta(a, m + 1), [1, mp.inf])


@functools.lru_cache(maxsize=None)
def tornheim(r, s, t, dps):
    """T(r,s,t) = sum_{p,q>=1} p^{-r} q^{-s} (p+q)^{-t} ueber Partialbruchzerlegung auf Doppel-Zeta-Werte."""
    tot = mp.mpf(0)
    for i in range(1, r + 1): tot += comb(r + s - i - 1, r - i) * mzv2(t + r + s - i, i, dps)
    for i in range(1, s + 1): tot += comb(r + s - i - 1, s - i) * mzv2(t + r + s - i, i, dps)
    return tot


def sum_R(a3, dps):
    """sum ueber alle m (m1+m2+m3 = 0, alle != 0) von rho(m): je 'grosser' Index (entgegengesetztes Vorzeichen), beide Vorzeichen."""
    tot = mp.mpf(0)
    for big in range(3):
        small = [k for k in range(3) if k != big]
        for j in (itertools_product(*[range(a) for a in a3])):
            J = sum(j)
            c = mp.mpf(1)
            for k in range(3): c *= c_coef(a3[k], j[k])
            c *= factorial(J) / mp.mpf(2) ** (J + 1)            # V = 2 (p+q)
            e = [1 - 2 * a3[k] + j[k] for k in range(3)]
            r, s = -e[small[0]], -e[small[1]]; t = J + 1 - e[big]
            tot += c * tornheim(r, s, t, dps)
    return 2 * tot


def itertools_product(*rs):
    import itertools
    return itertools.product(*rs)


# ---------- C_{a,b,c} ----------

def C(a3, t1, t2, dps=30, procs=4):
    """C_{a,b,c}(tau) numerisch auf ca. dps Stellen."""
    a3 = tuple(int(a) for a in a3); t1, t2 = str(t1), str(t2)       # tau als Dezimalstring: identisch in allen Prozessen
    if min(a3) < 1: raise ValueError("Exponenten muessen >= 1 sein")
    with mp.workdps(dps + 20):
        T = Tau(t1, t2, dps); w = sum(a3); y = mp.pi * T.t2
        K = int(mp.ceil((dps + 8) * mp.log(10) / (2 * mp.pi * T.t2))) + 2
        def D(ms):
            s = T.S(a3, ms).real
            return s - (y ** (2 - w) * rho(a3, ms) if all(ms) else 0)
        jobs = {}
        for i in range(3):
            for s in range(0, K + 1):
                key = (a3[i], tuple(sorted([a3[x] for x in range(3) if x != i])), s)
                jobs.setdefault(key, (i, s, 0))
                jobs[key] = (i, s, jobs[key][2] + (1 if s == 0 else 2))   # S(-m) = S(m)
        args = [(a3, str(t1), str(t2), dps, K, i, s) for (i, s, _) in jobs.values()]
        if procs > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(procs) as ex: vals = list(ex.map(_line_job, args, chunksize=1))
        else: vals = [_line_job(a) for a in args]
        tot = mp.fsum(mp.mpf(v) * mult for v, (_, _, mult) in zip(vals, jobs.values()))
        for m1 in range(-2 * K, 2 * K + 1):                        # Mehrfachzaehlung (Punkte auf >= 2 Geraden)
            for m2 in range(-2 * K, 2 * K + 1):
                ms = (m1, m2, -m1 - m2); c = sum(abs(x) <= K for x in ms)
                if c >= 2: tot -= (c - 1) * D(ms)
        tot += y ** (2 - w) * sum_R(a3, dps)
        return +tot


def _line_job(arg):
    """Summe von D(m) ueber die Gerade m_i = s (eigener Prozess)."""
    a3, t1, t2, dps, K, i, s = arg
    with mp.workdps(dps + 20):
        T = Tau(t1, t2, dps); w = sum(a3); y = mp.pi * T.t2
        def D(ms):
            v = T.S(a3, ms).real
            return v - (y ** (2 - w) * rho(a3, ms) if all(ms) else 0)
        j, k = [x for x in range(3) if x != i]
        def mk(t):
            ms = [0, 0, 0]; ms[i] = s; ms[j] = t; ms[k] = -s - t; return tuple(ms)
        T0 = K + abs(s) + 2
        tot = mp.fsum(D(mk(t)) for t in range(-T0, T0 + 1))
        tot += mp.nsum(lambda t: D(mk(int(t))), [T0 + 1, mp.inf], method="richardson")
        tot += mp.nsum(lambda t: D(mk(-int(t))), [T0 + 1, mp.inf], method="richardson")
        return mp.nstr(tot, dps + 15)


def E(s, t1, t2, dps=30):
    """Nicht-holomorphe Eisenstein-Reihe E_s (s ganz >= 2) ueber die Fourier-Entwicklung mit Bessel-K (exakt bis auf Abschneiden)."""
    with mp.workdps(dps + 15):
        x, y2 = mp.mpf(str(t1)), mp.mpf(str(t2)); s = int(s)
        val = 2 * mp.zeta(2 * s) * y2 ** s + 2 * mp.sqrt(mp.pi) * mp.gamma(s - mp.mpf(1) / 2) / mp.gamma(s) * mp.zeta(2 * s - 1) * y2 ** (1 - s)
        pref = 8 * mp.pi ** s * mp.sqrt(y2) / mp.gamma(s); N = 1
        while True:
            sig = mp.fsum(mp.mpf(d) ** (1 - 2 * s) for d in range(1, N + 1) if N % d == 0)
            term = pref * mp.mpf(N) ** (s - mp.mpf(1) / 2) * sig * mp.besselk(s - mp.mpf(1) / 2, 2 * mp.pi * N * y2) * mp.cos(2 * mp.pi * N * x)
            val += term
            if N > 3 and abs(term) < mp.mpf(10) ** (-(dps + 10)) * abs(val): break
            N += 1
        return +(val / mp.pi ** s)


def E_lattice(s, t1, t2, dps=30):
    """Unabhaengige Kontrolle: E_s = sum_m h_{s,m}(0) (Poisson ueber n), Summe ueber m mit Richardson."""
    with mp.workdps(dps + 15):
        T = Tau(str(t1), str(t2), dps)
        f = lambda m: sum(pc[2] * pc[3][0] for pc in T.h(s, int(m))).real if True else 0
        # h(0): nur der konstante Koeffizient des Polynoms, Exponential = 1 bei x = 0; B-Stueck: e^{Lambda} * poly(0)
        return +(f(0) + 2 * mp.nsum(f, [1, mp.inf], method="richardson"))


# ---------- Ausdruecke: Monome aus C(a,b,c), E(s), zeta(k), Laplace-Operator L[...] ----------
import re as _re, os, json
_FAK = _re.compile(r"^(C\((\d+),(\d+),(\d+)\)|E\((\d+)\)|zeta\((\d+)\))(\^(\d+))?$")
_VCACHE = {}


def parse(expr):
    """'C(2,1,1)*E(2)^2*zeta(3)' -> Liste (art, args, potenz);  'L[...]' -> ('L', inneres Monom)."""
    e = str(expr).replace(" ", "")
    if e.startswith("L[") and e.endswith("]"): return ("L", parse(e[2:-1]))
    if e in ("1", ""): return ("M", [])
    out = []
    for f in e.split("*"):
        m = _FAK.match(f)
        if not m: raise ValueError(f"unbekannter Faktor {f!r} (erlaubt: C(a,b,c), E(s), zeta(k), Potenzen ^n, Laplace L[...])")
        p = int(m.group(8) or 1)
        if p < 1 or p > 6: raise ValueError("Potenz ausserhalb 1..6")
        if m.group(2):
            a3 = tuple(sorted((int(m.group(2)), int(m.group(3)), int(m.group(4))), reverse=True))
            if min(a3) < 1 or sum(a3) > 12: raise ValueError("C(a,b,c): a,b,c >= 1 und a+b+c <= 12")
            out.append(("C", a3, p))
        elif m.group(5):
            s = int(m.group(5))
            if not 2 <= s <= 12: raise ValueError("E(s): 2 <= s <= 12")
            out.append(("E", s, p))
        else:
            k = int(m.group(6))
            if not 2 <= k <= 15: raise ValueError("zeta(k): 2 <= k <= 15")
            out.append(("z", k, p))
    return ("M", out)


def gewicht(parsed):
    if parsed[0] == "L": return gewicht(parsed[1])
    return sum((sum(a) if t == "C" else a) * p for t, a, p in parsed[1])


_DISK = os.environ.get("ASD_MGF_CACHE", "cache/mgf/werte.jsonl")     # persistente Memoisierung (übersteht Neustarts); "" schaltet ab


def _disk_load():
    if not _DISK or not os.path.exists(_DISK) or _VCACHE.get("_geladen"): return
    for line in open(_DISK):
        try: d = json.loads(line); _VCACHE[(d["t"], tuple(d["a"]) if isinstance(d["a"], list) else d["a"], d["t1"], d["t2"], d["dps"])] = mp.mpf(d["v"])
        except Exception: pass
    _VCACHE["_geladen"] = True


def _factor(t, a, t1, t2, dps, procs):
    key = (t, a, str(t1), str(t2), dps)
    _disk_load()
    if key not in _VCACHE and t == "C" and _DISK:
        v = C(a, t1, t2, dps, procs); _VCACHE[key] = v
        os.makedirs(os.path.dirname(_DISK), exist_ok=True)
        with open(_DISK, "a") as f: f.write(json.dumps({"t": t, "a": list(a), "t1": str(t1), "t2": str(t2), "dps": dps, "v": mp.nstr(v, dps + 15)}) + "\n")
    if key not in _VCACHE:
        if t == "C": v = C(a, t1, t2, dps, procs)
        elif t == "E": v = E(a, t1, t2, dps)
        else:
            with mp.workdps(dps + 10): v = +mp.zeta(a)
        _VCACHE[key] = v
    return _VCACHE[key]


def value(parsed, t1, t2, dps=30, procs=4, h=None):
    """Wert eines Monoms; fuer L[...] der hyperbolische Laplace-Operator tau2^2 (d1^2 + d2^2) per finiten Differenzen 4. Ordnung."""
    if isinstance(parsed, str): parsed = parse(parsed)
    with mp.workdps(dps + 10):
        if parsed[0] == "M":
            v = mp.mpf(1)
            for t, a, p in parsed[1]: v *= _factor(t, a, t1, t2, dps, procs) ** p
            return v
        inner = parsed[1]; h = mp.mpf(h or "1e-6"); x, y = mp.mpf(str(t1)), mp.mpf(str(t2))
        if all(t == "z" for t, _, _ in inner[1]): return mp.mpf(0)
        f = lambda a, b: value(inner, mp.nstr(a, dps + 8), mp.nstr(b, dps + 8), dps, procs)
        f0 = f(x, y)
        d11 = (-f(x + 2 * h, y) + 16 * f(x + h, y) - 30 * f0 + 16 * f(x - h, y) - f(x - 2 * h, y)) / (12 * h * h)
        d22 = (-f(x, y + 2 * h) + 16 * f(x, y + h) - 30 * f0 + 16 * f(x, y - h) - f(x, y - 2 * h)) / (12 * h * h)
        return y * y * (d11 + d22)


def punkte(seed, n):
    """Zufaellige Punkte im Streifen |tau1| <= 1/2, 1 <= tau2 <= 2.5 (Dezimalstrings mit 6 Stellen)."""
    import random
    r = random.Random(seed)
    return [(f"{r.uniform(-0.5, 0.5):.6f}", f"{r.uniform(1.0, 2.5):.6f}") for _ in range(n)]


def find_relations(basis, seed=1, n_punkte=None, dps=30, maxcoeff=10 ** 6, procs=4):
    """Ganzzahlige lineare Relationen zwischen den Basis-Funktionen (als Funktionen von tau): PSLQ auf einer zufaelligen
    Kombination der Werte an mehreren Punkten, gefundene Relation an allen Punkten pruefen, dann ein beteiligtes Element
    entfernen und weitersuchen. Kandidaten, kein Beweis."""
    import random
    P = [parse(b) for b in basis]; n = len(P); pts = punkte(seed, n_punkte or max(3, min(n, 6)))
    with mp.workdps(dps):
        M = [[value(p, t1, t2, dps, procs) for p in P] for t1, t2 in pts]
        r = random.Random(seed + 99); w = [mp.mpf(r.randint(1, 10 ** 6)) / 10 ** 6 for _ in pts]
        vec = [mp.fsum(w[i] * M[i][j] for i in range(len(pts))) for j in range(n)]
        aktiv = list(range(n)); rels = []
        lap = any(q[0] == 'L' for q in P)
        tol = mp.mpf(10) ** (-(16 if lap else dps - 6))
        while len(aktiv) >= 2:
            rel = mp.pslq([vec[j] for j in aktiv], tol=tol, maxcoeff=maxcoeff, maxsteps=10 ** 6)
            if rel is None: break
            full = [0] * n
            for j, c in zip(aktiv, rel): full[j] = int(c)
            res = max(abs(mp.fsum(full[j] * M[i][j] for j in range(n))) / max(mp.mpf(1), mp.fsum(abs(full[j] * M[i][j]) for j in range(n))) for i in range(len(pts)))
            if res > mp.mpf(10) ** (-(14 if lap else dps - 8)): break
            rels.append(full)
            drop = max((j for j in aktiv if full[j]), key=lambda j: j)      # Element mit hoechstem Index eliminieren
            aktiv.remove(drop)
    return {"basis": list(basis), "relationen": rels, "punkte": pts, "dps": dps,
            "lesart": "sum_j relation[j] * basis[j] = 0 an allen Punkten (numerisch, Kandidat)"}


# ---------- exakter Leitkoeffizient der Laurent-Entwicklung (y = pi tau2 -> unendlich) ----------
from fractions import Fraction as _Fr


def _bernpoly(n):
    """B_n(x) als Liste rationaler Koeffizienten (exakt)."""
    B = [_Fr(1)]
    for m in range(1, n + 1): B.append(-sum(comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
    return [comb(n, k) * B[n - k] for k in range(n + 1)]


def lead(parsed):
    """(Grad W, rationaler Koeffizient, Zeta-Inhalt): F = c * Z * y^W + O(y^{W-1}).
    C(a,b,c): c = 4^w prod_i (-1)^{a_i+1}/(2a_i)! * int_0^1 prod_i B_{2a_i}(x) dx  (Sektor m = 0, alle anderen Sektoren sind niedriger);
    E(s): c = (-1)^{s+1} B_{2s} 4^s / (2s)!;  zeta(k): Grad 0, Zeta-Inhalt k;  L[F]: Faktor W(W-1)."""
    if parsed[0] == "L":
        W, c, Z = lead(parsed[1]); return W, c * W * (W - 1), Z
    W, c, Z = 0, _Fr(1), []
    for t, a, p in parsed[1]:
        for _ in range(p):
            if t == "z": Z.append(a); continue
            if t == "E":
                s = a; W += s; c *= _Fr((-1) ** (s + 1)) * _bernpoly(2 * s)[0] * 4 ** s / factorial(2 * s)
                continue
            poly = [_Fr(1)]
            for ai in a:
                q = _bernpoly(2 * ai); r = [_Fr(0)] * (len(poly) + len(q) - 1)
                for i, x in enumerate(poly):
                    for j, y in enumerate(q): r[i + j] += x * y
                poly = r
                c *= _Fr((-1) ** (ai + 1), factorial(2 * ai))
            W += sum(a); c *= 4 ** sum(a) * sum(x / (k + 1) for k, x in enumerate(poly))
    return W, c, tuple(sorted(Z))


def lead_check(terme):
    """Exakte notwendige Bedingung: der Koeffizient der hoechsten y-Potenz muss verschwinden.
    Rueckgabe (anwendbar, ok, text)."""
    L = [(c, lead(parse(m))) for c, m in terme]
    W = max(l[0] for _, l in L)
    top = [(c, l) for c, l in L if l[0] == W]
    zs = {l[2] for _, l in top}
    if W == 0: return False, True, "keine y-Abhaengigkeit"
    if len(zs) > 1: return False, True, f"hoechste Potenz y^{W} mit verschiedenen Zeta-Faktoren (exakter Vergleich nicht moeglich)"
    s = sum(_Fr(c) * l[1] for c, l in top)
    return True, s == 0, f"exakter Leitkoeffizient von y^{W}: {s}"
