"""Exakte q-Entwicklungen holomorpher (und schwach holomorpher) Modulformen auf Gamma_0(N) und Sturm-Zertifikate.

Bausteine (Faktoren eines Monoms, mit '*' verbunden, Potenz mit '^', z. B. "E4^3*eta(1)^-24" oder "eta(2)^20*eta(1)^-8*eta(4)^-8"):
  E<k>, E<k>(d)     Eisenstein-Reihe E_k(d tau), k >= 4 gerade, Normierung a_0 = 1      Gewicht k, Level d
  F2(d)             E_2(tau) - d E_2(d tau), d >= 2                                     Gewicht 2, Level d
  eta(d)            Dedekind eta(d tau)                                                 Gewicht 1/2
  Delta, Delta(d)   eta(d tau)^24                                                       Gewicht 12
  theta, theta(d)   sum_n q^{d n^2}  (= eta(2d)^5 / (eta(d)^2 eta(4d)^2))                Gewicht 1/2
  thetaE8, thetaD16 Thetareihen der geraden unimodularen Gitter E8 und D16+ (durch Abzaehlen der Gittervektoren)
  j                 E4^3 / Delta                                                         Gewicht 0
Alle Koeffizienten sind exakte rationale Zahlen (fractions.Fraction); keine Gleitkommazahl.
"""
import math, re
from fractions import Fraction as Fr
from functools import lru_cache


# ---------------- Reihenarithmetik ----------------

class Q:
    """Reihe q^off * sum_j c[j] q^j mit rationalem off; gueltig bis zum absoluten Exponenten off + len(c) (exklusiv)."""
    def __init__(self, off, c): self.off, self.c = Fr(off), list(c)
    @property
    def top(self): return self.off + len(self.c)
    def __mul__(self, o):
        top = min(self.top + o.off, o.top + self.off); n = int(math.floor(top - self.off - o.off))
        r = [0] * max(n, 0)
        for i, x in enumerate(self.c[:n]):
            if x == 0: continue
            for j, y in enumerate(o.c[:n - i]): r[i + j] += x * y
        return Q(self.off + o.off, r)
    def scale(self, a): return Q(self.off, [a * x for x in self.c])
    def __add__(self, o):
        d = o.off - self.off
        if d.denominator != 1: raise ValueError("Summe von Reihen mit verschiedenen Exponentenklassen")
        lo = min(self.off, o.off); top = min(self.top, o.top); n = int(top - lo)
        r = [0] * n
        for s in (self, o):
            sh = int(s.off - lo)
            for i, x in enumerate(s.c):
                if sh + i < n: r[sh + i] += x
        return Q(lo, r)
    def coeff(self, e):
        k = Fr(e) - self.off
        if k.denominator != 1 or k < 0: return 0
        if e >= self.top: raise ValueError("Exponent jenseits der berechneten Genauigkeit")
        return self.c[int(k)]


def _pow(c, r, n):
    """(Potenzreihe c mit c[0] = 1)^r bis q^{n-1}, r ganz (auch negativ), exakt ueber die J.C.P.-Miller-Rekursion."""
    a = [Fr(0)] * n; a[0] = Fr(1)
    c = [Fr(x) for x in c[:n]] + [Fr(0)] * max(0, n - len(c))
    for k in range(1, n):
        s = Fr(0)
        for i in range(1, k + 1):
            if c[i]: s += (r * i - (k - i)) * c[i] * a[k - i]
        a[k] = s / k
    return [int(x) if x.denominator == 1 else x for x in a]


@lru_cache(maxsize=None)
def euler_prod(n):
    """prod_{m>=1} (1 - q^m) bis q^{n-1} (Pentagonalzahlensatz)."""
    c = [0] * n; k = 0
    while True:
        done = True
        for kk in ((k, -k) if k else (0,)):
            e = kk * (3 * kk - 1) // 2
            if e < n: c[e] += (-1) ** abs(kk); done = False
        if done and k > 0: break
        k += 1
    return tuple(c)


def eta_series(d, r, n):
    """eta(d tau)^r bis zu n Termen nach dem Offset d r / 24."""
    m = (n + d - 1) // d + 1
    p = _pow(euler_prod(m), r, m)
    c = [0] * n
    for i, x in enumerate(p):
        if i * d < n: c[i * d] = x
    return Q(Fr(d * r, 24), c)


def sigma(n, k): return sum(d ** k for d in range(1, n + 1) if n % d == 0)


@lru_cache(maxsize=None)
def bernoulli(k):
    B = [Fr(1)]
    for m in range(1, k + 1): B.append(-sum(math.comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
    return B[k]


def eisenstein(k, d, n):
    c = [Fr(0)] * n; c[0] = Fr(1); f = Fr(-2 * k) / bernoulli(k)
    for i in range(1, (n - 1) // d + 1): c[i * d] = f * sigma(i, k - 1)
    return Q(0, c)


def lattice_theta(name, n):
    """Thetareihe sum_{x in L} q^{|x|^2/2} durch Abzaehlen: D_m bzw. D_m + (1/2,...,1/2) mit gerader Koordinatensumme."""
    dim = {"E8": 8, "D16": 16}[name]
    def count(half):
        # Zustand (2*Norm in Einheiten 1/4 bei halbzahligen Koordinaten, Paritaet der Summe)
        from collections import defaultdict
        st = {(0, 0): 1}; maxn = 8 * n  # Norm*4 <= 8 n  (|x|^2/2 < n  <=>  4|x|^2 < 8n)
        vals = [(2 * t + 1) for t in range(-n - 2, n + 2)] if half else [2 * t for t in range(-n - 2, n + 2)]   # 2x
        for _ in range(dim):
            nx = defaultdict(int)
            for (nn, par), c in st.items():
                for v in vals:
                    m = nn + v * v
                    if m < maxn: nx[(m, (par + v) % 4 if half else (par + v // 2) % 2)] += c
            st = nx
        out = [0] * n
        for (nn, par), c in st.items():
            ok = (par == 0) if not half else ((par % 4) == (0 if dim % 8 == 0 else 0))   # Summe der x_i gerade  <=> sum 2x_i == 0 mod 4
            if ok and nn % 8 == 0: out[nn // 8] += c
        return out
    a, b = count(False), count(True)
    return Q(0, [x + y for x, y in zip(a, b)])


# ---------------- Parser und Metadaten ----------------

FAKTOR = re.compile(r"^(E(\d+)|F2|eta|Delta|theta|thetaE8|thetaD16|j)(\((\d+)\))?(\^(-?\d+))?$")


def parse_monom(s):
    """-> Liste (name, k, d, exponent)."""
    out = []
    for f in str(s).replace(" ", "").split("*"):
        m = FAKTOR.match(f)
        if not m: raise ValueError(f"unbekannter Faktor {f!r}")
        name = m.group(1); k = int(m.group(2)) if m.group(2) else None; d = int(m.group(4)) if m.group(4) else 1; e = int(m.group(6)) if m.group(6) else 1
        if name.startswith("E") and name not in ("E",):
            name = "E"
            if k < 4 or k % 2: raise ValueError(f"E{k}: nur gerade k >= 4 (E2 ist nicht modular; benutze F2(d))")
        if name == "F2" and d < 2: raise ValueError("F2(d) braucht d >= 2")
        if name in ("thetaE8", "thetaD16", "j") and d != 1: raise ValueError(f"{name} ohne Argument")
        if d < 1 or d > 10000 or abs(e) > 200: raise ValueError("Argument/Exponent ausserhalb des erlaubten Bereichs")
        if name in ("E", "F2", "thetaE8", "thetaD16", "j") and e < 0: raise ValueError(f"negative Potenz von {name} nicht erlaubt (nicht holomorph kontrollierbar)")
        out.append((name, k, d, e))
    return out


def meta(monom):
    """Gewicht (Fraction), Eta-Anteil {delta: r}, Liste der Level (Teiler-Anforderungen)."""
    eta = {}; w = Fr(0); lev = [1]
    for name, k, d, e in monom:
        if name == "E": w += k * e; lev.append(d)
        elif name == "F2": w += 2 * e; lev.append(d)
        elif name == "eta": eta[d] = eta.get(d, 0) + e
        elif name == "Delta": eta[d] = eta.get(d, 0) + 24 * e
        elif name == "theta":
            for dd, rr in ((2 * d, 5), (d, -2), (4 * d, -2)): eta[dd] = eta.get(dd, 0) + rr * e
        elif name == "thetaE8": w += 4 * e
        elif name == "thetaD16": w += 8 * e
        elif name == "j": w += 0; eta[1] = eta.get(1, 0) - 24 * e; w += 12 * e   # E4^3/Delta: E4^3 holomorph (12), Delta^-1 ueber eta
    eta = {d: r for d, r in eta.items() if r}
    w += Fr(sum(eta.values()), 2)
    lev += list(eta)
    return w, eta, lev


def series(monom, n_top):
    """Exakte Reihe des Monoms, gueltig mindestens bis q^{n_top} (exklusiv)."""
    w, eta, _ = meta(monom)
    neg = sum(max(0, -Fr(d * r, 24)) for d, r in eta.items()) + sum(e for name, k, d, e in monom if name == "j")
    L = int(n_top + neg) + 3
    s = Q(0, [1] + [0] * (L - 1))
    for name, k, d, e in monom:
        if name == "E": f = eisenstein(k, d, L)
        elif name == "F2":
            a, b = eisenstein_e2(1, L), eisenstein_e2(d, L); f = a + b.scale(-d)
        elif name in ("eta", "Delta", "theta"): continue
        elif name == "thetaE8": f = lattice_theta("E8", L)
        elif name == "thetaD16": f = lattice_theta("D16", L)
        elif name == "j": f = eisenstein(4, 1, L); f = f * f * f
        for _ in range(e if name != "j" else e): s = s * f
    for d, r in sorted(eta.items()):
        s = s * eta_series(d, r, L + int(abs(Fr(d * r, 24))) + 2)
    return s


def eisenstein_e2(d, n):
    c = [Fr(0)] * n; c[0] = Fr(1)
    for i in range(1, (n - 1) // d + 1): c[i * d] = Fr(-24 * sigma(i, 1))
    return Q(0, c)


# ---------------- Gamma_0(N): Index, Spitzen, Ordnungen, Charakter, Dimension ----------------

def divisors(n): return [d for d in range(1, n + 1) if n % d == 0]


def primes(n): return [p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, int(p ** 0.5) + 1))]


def index(N):
    m = Fr(N)
    for p in primes(N): m *= Fr(p + 1, p)
    return int(m)


def eulerphi(n): return sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)


def cusp_classes(N):
    """[(d, Anzahl Spitzen mit Nenner d, Breite)]"""
    return [(d, eulerphi(math.gcd(d, N // d)), Fr(N, d * math.gcd(d, N // d))) for d in divisors(N)]


def eta_order(eta, N, d):
    """Ligozat: Ordnung des Eta-Quotienten an einer Spitze c/d von Gamma_0(N) (in der lokalen Uniformisierenden)."""
    return Fr(N, 24) * sum(Fr(math.gcd(d, delta) ** 2 * r, math.gcd(d, N // d) * d * delta) for delta, r in eta.items())


def newman_ok(eta, N):
    """Gordon-Hughes-Newman: Eta-Quotient ist modular auf Gamma_0(N) (mit Charakter)."""
    if any(N % d for d in eta): return False, "Eta-Argument teilt N nicht"
    if sum(eta.values()) % 2: return False, "halbzahliges Gewicht des Eta-Anteils"
    if sum(d * r for d, r in eta.items()) % 24: return False, "sum delta r_delta nicht durch 24 teilbar"
    if sum((N // d) * r for d, r in eta.items()) % 24: return False, "sum (N/delta) r_delta nicht durch 24 teilbar"
    return True, ""


def squarefree_kernel(fr):
    """quadratfreier Kern einer rationalen Zahl (mit Vorzeichen)."""
    x = Fr(fr); sgn = -1 if x < 0 else 1; n = abs(x.numerator) * abs(x.denominator); k = 1; p = 2
    while p * p <= n:
        e = 0
        while n % p == 0: n //= p; e += 1
        if e % 2: k *= p
        p += 1
    return sgn * k * n


def character(eta, w_eta):
    """Charakter chi(d) = ((-1)^k s / d), s = prod delta^{r_delta}; zurueckgegeben als quadratfreier Kern von (-1)^k s (1 = trivial)."""
    s = Fr(1)
    for d, r in eta.items(): s *= Fr(d) ** r
    return squarefree_kernel((-1) ** int(w_eta) * s)


def dim_M(k, N):
    """dim M_k(Gamma_0(N)), trivialer Charakter, k >= 0 gerade (Standardformel, z. B. Diamond-Shurman Kap. 3)."""
    if k < 0 or k % 2: return 0
    if k == 0: return 1
    m = index(N); ps = primes(N)
    nu2 = 0 if N % 4 == 0 else math.prod(1 + (0 if p == 2 else _leg(-1, p)) for p in ps)   # Kronecker (-4/p)
    nu3 = 0 if N % 9 == 0 else math.prod(1 + _leg(-3, p) for p in ps)
    c = sum(eulerphi(math.gcd(d, N // d)) for d in divisors(N))
    g = 1 + Fr(m, 12) - Fr(nu2, 4) - Fr(nu3, 3) - Fr(c, 2)
    if k == 2: return int(g + c - 1)
    return int((k - 1) * (g - 1) + (Fr(k, 2) - 1) * c + nu2 * (k // 4) + nu3 * (k // 3) + c)


def _leg(a, p):
    """Kronecker-Symbol (a/p) fuer Primzahl p."""
    if p == 2: return 0 if a % 2 == 0 else (1 if a % 8 in (1, 7) else -1)
    a %= p
    if a == 0: return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sturm_bound(k, N): return Fr(k * index(N), 12)


# ---------------- Zertifikat einer Identitaet ----------------

def certify_identity(terme, N, extra=10):
    """terme: [(Fraction-Koeffizient, Monom-String)]; Aussage: sum c_t f_t = 0 auf Gamma_0(N).
    Rueckgabe (bestanden, grund, belege). Beweis: alle f_t liegen in M^!_k(Gamma_0(N), chi); nach Multiplikation mit Delta^h
    (h aus den Spitzenordnungen) ist die Summe holomorph; verschwinden die Koeffizienten bis zur Sturm-Schranke, ist sie 0."""
    if len(terme) < 2: return False, "Identitaet braucht mindestens zwei Terme", {}
    N = int(N)
    if not (1 <= N <= 400): return False, "Level ausserhalb 1..400", {}
    mons = [(Fr(c), parse_monom(m), m) for c, m in terme]
    if any(c == 0 for c, _, _ in mons): return False, "Koeffizient 0 ist nicht erlaubt", {}
    infos = []
    for c, mon, s in mons:
        w, eta, lev = meta(mon)
        if any(N % d for d in lev): return False, f"{s}: Argument {[d for d in lev if N % d]} teilt N = {N} nicht", {}
        if eta:
            ok, why = newman_ok(eta, N)
            if not ok: return False, f"{s}: {why} (nicht als modular auf Gamma_0({N}) nachweisbar)", {}
        if w.denominator != 1: return False, f"{s}: halbzahliges Gewicht {w}", {}
        chi = character(eta, Fr(sum(eta.values()), 2)) if eta else 1
        ords = {d: (eta_order(eta, N, d) if eta else Fr(0)) for d, _, _ in cusp_classes(N)}
        infos.append((w, chi, ords))
    ws = {i[0] for i in infos}; chis = {i[1] for i in infos}
    if len(ws) > 1: return False, f"verschiedene Gewichte {sorted(ws)}", {}
    if len(chis) > 1: return False, f"verschiedene Charaktere {sorted(chis)}", {}
    k = int(ws.pop())
    if k < 0: return False, "negatives Gewicht nicht unterstuetzt", {}
    h = 0
    for d, _, width in cusp_classes(N):
        mn = min(i[2][d] for i in infos)
        if mn < 0: h = max(h, math.ceil(-mn / width))
    B = sturm_bound(k + 12 * h, N); nB = int(math.floor(B)) + 1 + extra
    dl = series([("Delta", None, 1, h)], nB) if h else None
    tot = None
    for c, mon, _ in mons:
        s = series(mon, nB + h + 2)
        if dl is not None: s = s * dl
        s = s.scale(c); tot = s if tot is None else tot + s
    if tot.top < nB: return False, f"interner Fehler: Genauigkeit {tot.top} < {nB}", {}
    bad = [(e, tot.coeff(e)) for e in range(0, nB) if tot.coeff(e) != 0]
    if tot.off < 0 and any(x != 0 for x in tot.c[:int(-tot.off)]): bad = [("<0", "Polterm")] + bad
    belege = {"gewicht": k, "level": N, "index": index(N), "delta_potenz": h, "sturm_schranke": str(B), "geprueft_bis": nB - 1,
              "charakter_kern": next(iter(chis))}
    if bad: return False, f"Koeffizient von q^{bad[0][0]} ist {bad[0][1]} != 0 (Identitaet falsch)", belege
    return True, (f"Sturm-Zertifikat: alle Terme in M^!_{k}(Gamma_0({N})); nach Multiplikation mit Delta^{h} holomorph vom Gewicht {k + 12 * h}; "
                  f"Koeffizienten q^0..q^{nB - 1} verschwinden exakt, Sturm-Schranke {B} (Index {index(N)})"), belege


# ---------------- Eta-Quotienten-Familie ----------------

def holomorphic_eta_quotients(N, k, trivial_char=True, limit=200000):
    """Alle holomorphen Eta-Quotienten vom Gewicht k auf Gamma_0(N) (Gordon-Hughes-Newman), ueber die Ordnungsvektoren:
    Valenzformel: sum ueber alle Spitzen der Ordnungen = k * index / 12."""
    D = divisors(N); cc = cusp_classes(N); total = Fr(k * index(N), 12)
    if total.denominator != 1: return []
    A = [[Fr(N, 24) * Fr(math.gcd(d, delta) ** 2, math.gcd(d, N // d) * d * delta) for delta in D] for d in D]
    Ainv = _inv(A); mult = [c[1] for c in cc]; out = []; cnt = [0]
    def rec(i, rest, v):
        if cnt[0] > limit: raise RuntimeError("zu viele Kandidaten")
        if i == len(D) - 1:
            if rest % mult[i]: return
            v = v + [rest // mult[i]]; cnt[0] += 1
            r = [sum(Ainv[a][b] * v[b] for b in range(len(D))) for a in range(len(D))]
            if any(x.denominator != 1 for x in r): return
            eta = {d: int(x) for d, x in zip(D, r) if x}
            if sum(eta.values()) != 2 * k: return
            ok, _ = newman_ok(eta, N)
            if not ok: return
            if trivial_char and character(eta, k) != 1: return
            out.append(eta); return
        for x in range(0, rest // mult[i] + 1): rec(i + 1, rest - x * mult[i], v + [x])
    rec(0, int(total), [])
    return out


def _inv(A):
    n = len(A); M = [row[:] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def eta_str(eta): return "*".join(f"eta({d})^{r}" for d, r in sorted(eta.items()))


def rank_exact(rows):
    """Rang einer Liste rationaler Vektoren (exakt)."""
    M = [[Fr(x) for x in r] for r in rows]; rk = 0; ncol = len(M[0]) if M else 0
    for c in range(ncol):
        p = next((r for r in range(rk, len(M)) if M[r][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(len(M)):
            if r != rk and M[r][c] != 0:
                f = M[r][c] / M[rk][c]; M[r] = [x - f * y for x, y in zip(M[r], M[rk])]
        rk += 1
    return rk


def eta_span(N, k):
    """(Anzahl holomorpher Eta-Quotienten mit trivialem Charakter, dim ihres Spanns, dim M_k(Gamma_0(N)))."""
    qs = holomorphic_eta_quotients(N, k)
    nB = int(math.floor(sturm_bound(k, N))) + 1
    rows = []
    for eta in qs:
        s = series([("eta", None, d, r) for d, r in eta.items()], nB)
        rows.append([s.coeff(e) for e in range(nB)])
    return len(qs), (rank_exact(rows) if rows else 0), dim_M(k, N), qs
