"""Rechenkern der Köcher-Domäne (Darstellungstheorie von Köchern). Alles exakt: rationale Arithmetik (Fraction),
Arithmetik in F_p und symbolische Elimination (sympy) mit protokollierten Pivots.

Konventionen
  Köcher Q = (n, pfeile) mit pfeile = [(s, t), ...]. Darstellung V = {"dims": [d_0, ..., d_{n-1}], "maps": {"a": Matrix}},
  wobei "a" der Index des Pfeils ist und Matrix eine d_t x d_s Liste von Zeilen (Einträge int, "p/q" oder Ausdruck in t).
  Tits-Form q(x) = sum x_i^2 - sum_{(s,t)} x_s x_t, symmetrische Form (x, y) = q(x+y) - q(x) - q(y).
"""
import itertools, math
from fractions import Fraction as Fr


# ----------------------------------------------------------------------------------------------------------- Köcher
def quiver(name):
    """Benannte Köcher. star<n>: Zentrum 0, Blätter 1..n, Pfeile Blatt -> Zentrum (Unterraum-Orientierung)."""
    if isinstance(name, dict): return int(name["n"]), [tuple(a) for a in name["pfeile"]]
    if name == "A2": return 2, [(0, 1)]
    if name == "A3": return 3, [(0, 1), (1, 2)]
    if name == "kronecker": return 2, [(0, 1), (0, 1)]
    if name.startswith("star"):
        n = int(name[4:]); return n + 1, [(i, 0) for i in range(1, n + 1)]
    if name == "cycle3_oriented": return 3, [(0, 1), (1, 2), (2, 0)]
    if name == "cycle3_acyclic": return 3, [(0, 1), (1, 2), (0, 2)]
    if name == "cycle4_oriented": return 4, [(0, 1), (1, 2), (2, 3), (3, 0)]
    if name == "cycle4_acyclic31": return 4, [(0, 1), (1, 2), (2, 3), (0, 3)]
    if name == "cycle4_acyclic22": return 4, [(0, 1), (1, 2), (0, 3), (3, 2)]
    raise ValueError(f"unbekannter Köcher {name}")


def gram(Q):
    n, A = Q; G = [[0] * n for _ in range(n)]
    for i in range(n): G[i][i] = 2
    for s, t in A: G[s][t] -= 1; G[t][s] -= 1
    return G


def tits(Q, x):
    n, A = Q; return sum(v * v for v in x) - sum(x[s] * x[t] for s, t in A)


def bil(Q, x, y):
    G = gram(Q); return sum(x[i] * G[i][j] * y[j] for i in range(len(x)) for j in range(len(y)))


def det_frac(M):
    M = [[Fr(v) for v in r] for r in M]; n = len(M); d = Fr(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return Fr(0)
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            if f: M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return d


def connected(Q, verts=None):
    n, A = Q; verts = set(range(n)) if verts is None else set(verts)
    if not verts: return False
    seen, todo = set(), [min(verts)]
    while todo:
        v = todo.pop()
        if v in seen: continue
        seen.add(v)
        todo += [t if s == v else s for s, t in A if v in (s, t) and (t if s == v else s) in verts]
    return seen == verts


def tits_type(Q):
    """Exakt: positiv definit (endlich) / positiv semidefinit, nicht definit (zahm) / indefinit (wild), per Hauptminoren."""
    G = gram(Q); n = len(G)
    lead = [det_frac([r[:k] for r in G[:k]]) for k in range(1, n + 1)]
    if all(v > 0 for v in lead): return "endlich", {"fuehrende_hauptminoren": [str(v) for v in lead]}
    minors = {S: det_frac([[G[i][j] for j in S] for i in S]) for k in range(1, n + 1) for S in itertools.combinations(range(n), k)}
    neg = [S for S, v in minors.items() if v < 0]
    if not neg: return "zahm", {"alle_hauptminoren_nichtnegativ": len(minors), "det": str(minors[tuple(range(n))])}
    wit = next((x for x in itertools.product(range(4), repeat=n) if any(x) and tits(Q, x) < 0), None)
    return "wild", {"negativer_hauptminor": list(neg[0]), "zeuge_q_negativ": list(wit) if wit else None,
                    "q_zeuge": tits(Q, wit) if wit else None}


def nullspace_frac(M, ncols):
    M = [[Fr(v) for v in r] for r in M]; piv = []; r = 0
    for c in range(ncols):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [v / pv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
    free = [c for c in range(ncols) if c not in piv]; basis = []
    for f in free:
        v = [Fr(0)] * ncols; v[f] = Fr(1)
        for i, c in enumerate(piv): v[c] = -M[i][f]
        basis.append(v)
    return basis


def radical(Q):
    """Kern der symmetrischen Form; für euklidische Köcher eindimensional, erzeugt von delta (minimal, positiv, ganzzahlig)."""
    G = gram(Q); B = nullspace_frac(G, len(G))
    if len(B) != 1: return None, len(B)
    v = B[0]; l = math.lcm(*[x.denominator for x in v]); w = [int(x * l) for x in v]; g = math.gcd(*w); w = [x // g for x in w]
    if all(x <= 0 for x in w): w = [-x for x in w]
    return w, 1


def root_kind(Q, a):
    """Kac' Reduktionsalgorithmus. Gibt 'reell', 'imaginaer' oder 'keine' für einen Vektor a in N^n zurück."""
    a = list(a); n = len(a)
    if any(x < 0 for x in a) or not any(a): return "keine"
    G = gram(Q)
    while True:
        if sum(a) == 1: return "reell"
        for i in range(n):
            c = sum(G[i][j] * a[j] for j in range(n))
            if c > 0:
                a[i] -= c
                if a[i] < 0: return "keine"
                break
        else:
            return "imaginaer" if connected(Q, [i for i in range(n) if a[i]]) else "keine"


def positive_roots(Q, limit=10000):
    """Alle positiven Wurzeln eines Dynkin-Köchers als W-Bahn der einfachen Wurzeln (endlich, sonst None)."""
    n = Q[0]; G = gram(Q); simple = [tuple(int(i == j) for j in range(n)) for i in range(n)]
    seen = set(simple); todo = list(simple)
    while todo:
        a = todo.pop()
        for i in range(n):
            c = sum(G[i][j] * a[j] for j in range(n)); b = list(a); b[i] -= c; b = tuple(b)
            if all(x >= 0 for x in b) and any(b) and b not in seen:
                seen.add(b); todo.append(b)
                if len(seen) > limit: return None
    return sorted(seen)


# ------------------------------------------------------------------------------------------ Darstellungen über Q
def _mat(V, Q, k):
    n, A = Q; s, t = A[k]; m = V["maps"].get(str(k))
    ds, dt = V["dims"][s], V["dims"][t]
    if m is None: return [[Fr(0)] * ds for _ in range(dt)]
    M = [[Fr(x) for x in row] for row in m]
    if len(M) != dt or any(len(r) != ds for r in M): raise ValueError(f"Pfeil {k}: Matrix muss {dt}x{ds} sein")
    return M


def hom_system(Q, V, W):
    """Lineares Gleichungssystem für Hom(V, W): W_a f_s - f_t V_a = 0. Unbekannte: Einträge der f_i (zeilenweise)."""
    n, A = Q; off = [0]
    for i in range(n): off.append(off[-1] + W["dims"][i] * V["dims"][i])
    N = off[-1]; rows = []
    idx = lambda i, r, c: off[i] + r * V["dims"][i] + c
    for k, (s, t) in enumerate(A):
        Va, Wa = _mat(V, Q, k), _mat(W, Q, k)
        for r in range(W["dims"][t]):
            for c in range(V["dims"][s]):
                row = [Fr(0)] * N
                for j in range(W["dims"][s]): row[idx(s, j, c)] += Wa[r][j]          # (W_a f_s)[r][c]
                for j in range(V["dims"][t]): row[idx(t, r, j)] -= Va[j][c]          # (f_t V_a)[r][c]
                rows.append(row)
    return rows, N, off


def hom_basis(Q, V, W):
    rows, N, off = hom_system(Q, V, W); B = nullspace_frac(rows, N); n = Q[0]; out = []
    for v in B:
        out.append([[[v[off[i] + r * V["dims"][i] + c] for c in range(V["dims"][i])] for r in range(W["dims"][i])] for i in range(n)])
    return out


def _mm(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]) if Y else 0)] for i in range(len(X))]


def abs_indecomposable_Q(Q, V):
    """Absolute Unzerlegbarkeit (über dem algebraischen Abschluss) einer über Q definierten Darstellung:
    End(V) ⊗ Q̄ ist lokal  <=>  dim End(V) - dim J(End V) = 1. In Charakteristik 0 ist J der Kern der Spurform
    (x, y) -> tr(xy) auf der treuen Darstellung V (Dickson). Rückgabe: (bool, dim End, dim J)."""
    if not any(V["dims"]): return False, 0, 0
    B = hom_basis(Q, V, V); e = len(B)
    T = [[sum(sum(_mm(B[a][i], B[b][i])[r][r] for r in range(V["dims"][i])) for i in range(Q[0]) if V["dims"][i]) for b in range(e)] for a in range(e)]
    rk = e - len(nullspace_frac(T, e)) if e else 0
    return rk == 1, e, e - rk


# ------------------------------------------------------------------------------------------ symbolische Familien
def _sym_hom_matrix(Q, V, W):
    """Wie hom_system, aber Einträge sympy-Ausdrücke (Familien mit Parameter)."""
    import sympy as sp
    n, A = Q; off = [0]
    for i in range(n): off.append(off[-1] + W["dims"][i] * V["dims"][i])
    N = off[-1]; rows = []
    def M(R, k):
        s, t = A[k]; m = R["maps"].get(str(k))
        if m is None: return [[0] * R["dims"][s] for _ in range(R["dims"][t])]
        return [[sp.sympify(x) for x in row] for row in m]
    for k, (s, t) in enumerate(A):
        Va, Wa = M(V, k), M(W, k)
        for r in range(W["dims"][t]):
            for c in range(V["dims"][s]):
                row = [sp.Integer(0)] * N
                for j in range(W["dims"][s]): row[off[s] + j * V["dims"][s] + c] += Wa[r][j]
                for j in range(V["dims"][t]): row[off[t] + r * V["dims"][t] + j] -= Va[j][c]
                rows.append(row)
    return rows, N


def certified_rank(rows, N, allowed):
    """Gauß-Elimination über Q(Parameter) mit Protokoll: es werden nur Pivots verwendet, deren irreduzible Faktoren in
    `allowed` liegen (bzw. Konstanten). Dann gilt rank >= r an JEDEM Punkt, an dem keiner dieser Faktoren verschwindet.
    Rückgabe: (r, benutzte Pivot-Faktoren)."""
    import sympy as sp
    allowed = [sp.factor(sp.sympify(a)) for a in allowed]
    def ok(expr):
        num, den = sp.fraction(sp.factor(expr))
        for f, _ in sp.factor_list(num)[1]:
            if f.free_symbols and not any(sp.simplify(f - a) == 0 or sp.simplify(f + a) == 0 for a in allowed): return False
        return True
    M = [list(r) for r in rows]; used = []; r = 0; cols = list(range(N))
    for c in cols:
        cand = [i for i in range(r, len(M)) if sp.simplify(M[i][c]) != 0]
        cand.sort(key=lambda i: (bool(sp.sympify(M[i][c]).free_symbols), sp.count_ops(M[i][c])))
        p = next((i for i in cand if ok(M[i][c])), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]
        if pv.free_symbols: used.append(str(sp.factor(pv)))
        for i in range(len(M)):
            if i != r and sp.simplify(M[i][c]) != 0:
                f = sp.cancel(M[i][c] / pv); M[i] = [sp.cancel(a - f * b) for a, b in zip(M[i], M[r])]
        r += 1
    return r, used


def family_certificate(Q, V, param="t", ausnahmen=()):
    """Für die Familie V_t (Einträge Polynome in t) wird gezeigt: für alle t außerhalb der Ausnahmen gilt dim End(V_t) = 1
    (Ziegel, absolut unzerlegbar) und Hom(V_s, V_t) = 0 für s != t (paarweise nicht isomorph)."""
    import sympy as sp
    t, s = sp.Symbol(param), sp.Symbol("s_")
    allowed_t = [t - sp.sympify(a) for a in ausnahmen]
    rows, N = _sym_hom_matrix(Q, V, V); r1, piv1 = certified_rank(rows, N, allowed_t)
    Vs = {"dims": V["dims"], "maps": {k: [[str(sp.sympify(x).subs(t, s)) for x in row] for row in m] for k, m in V["maps"].items()}}
    rows2, N2 = _sym_hom_matrix(Q, Vs, V)
    r2, piv2 = certified_rank(rows2, N2, allowed_t + [s - sp.sympify(a) for a in ausnahmen] + [s - t])
    return {"N": N, "rang_end": r1, "dim_end_max": N - r1, "pivots_end": piv1, "rang_hom": r2, "dim_hom_max": N2 - r2, "pivots_hom": piv2}


# ------------------------------------------------------------------------------------------ endliche Körper F_p
def rank_mod(M, p):
    M = [[x % p for x in r] for r in M]; r = 0; ncol = len(M[0]) if M else 0
    for c in range(ncol):
        q = next((i for i in range(r, len(M)) if M[i][c]), None)
        if q is None: continue
        M[r], M[q] = M[q], M[r]; inv = pow(M[r][c], p - 2, p); M[r] = [v * inv % p for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r


def nullspace_mod(M, ncols, p):
    M = [[x % p for x in r] for r in M]; piv = []; r = 0
    for c in range(ncols):
        q = next((i for i in range(r, len(M)) if M[i][c]), None)
        if q is None: continue
        M[r], M[q] = M[q], M[r]; inv = pow(M[r][c], p - 2, p); M[r] = [v * inv % p for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
    basis = []
    for f in (c for c in range(ncols) if c not in piv):
        v = [0] * ncols; v[f] = 1
        for i, c in enumerate(piv): v[c] = (-M[i][f]) % p
        basis.append(v)
    return basis


def det_mod(M, p):
    n = len(M)
    if n == 0: return 1
    return 1 if rank_mod(M, p) == n else 0          # nur ob invertierbar


def mat_mul_mod(X, Y, p):
    return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(len(Y))) % p for j in range(len(Y[0]))) for i in range(len(X)))


_GL = {}


def gl(n, p):
    """GL_n(F_p) als Liste von Matrizen (Tupel), und Konjugationsklassen [(Vertreter, Größe)]."""
    if (n, p) in _GL: return _GL[(n, p)]
    if n == 0:
        _GL[(n, p)] = ([()], [((), 1)]); return _GL[(n, p)]
    els = [m for m in (tuple(tuple(v[i * n:(i + 1) * n]) for i in range(n)) for v in itertools.product(range(p), repeat=n * n)) if det_mod(m, p)]
    g = next(w for w in range(1, p) if len({pow(w, k, p) for k in range(1, p)}) == p - 1) if p > 2 else 1
    gens = []
    for i in range(n):
        for j in range(n):
            if i != j: gens.append(tuple(tuple(int(a == b) + (a == i and b == j) for b in range(n)) for a in range(n)))
    gens.append(tuple(tuple((g if a == 0 else 1) if a == b else 0 for b in range(n)) for a in range(n)))
    ginv = [(h, _inv_mod(h, p)) for h in gens]
    seen, classes = set(), []
    for m in els:
        if m in seen: continue
        orb = {m}; todo = [m]
        while todo:
            x = todo.pop()
            for h, hi in ginv:
                y = mat_mul_mod(mat_mul_mod(h, x, p), hi, p)
                if y not in orb: orb.add(y); todo.append(y)
        seen |= orb; classes.append((m, len(orb)))
    _GL[(n, p)] = (els, classes); return _GL[(n, p)]


def _inv_mod(m, p):
    n = len(m); A = [list(r) + [int(i == j) for j in range(n)] for i, r in enumerate(m)]
    for c in range(n):
        q = next(i for i in range(c, n) if A[i][c] % p); A[c], A[q] = A[q], A[c]; iv = pow(A[c][c], p - 2, p)
        A[c] = [x * iv % p for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]: f = A[i][c]; A[i] = [(a - f * b) % p for a, b in zip(A[i], A[c])]
    return tuple(tuple(r[n:]) for r in A)


def gl_order(n, p):
    return math.prod(p ** n - p ** i for i in range(n))


_FIX = {}


def fixdim(gs, gt, p):
    """dim {A : g_t A = A g_s} über F_p (A ist d_t x d_s)."""
    key = (gs, gt, p)
    if key in _FIX: return _FIX[key]
    ds, dt = len(gs), len(gt)
    if ds == 0 or dt == 0: _FIX[key] = 0; return 0
    rows = []
    for r in range(dt):
        for c in range(ds):
            row = [0] * (dt * ds)
            for j in range(dt): row[j * ds + c] += gt[r][j]
            for j in range(ds): row[r * ds + j] -= gs[j][c]
            rows.append(row)
    _FIX[key] = dt * ds - rank_mod(rows, p); return _FIX[key]


def count_orbits(Q, beta, p):
    """M_beta(p) = Anzahl der Isoklassen von Darstellungen mit Dimensionsvektor beta über F_p (Burnside über Konjugationsklassen).
    Für Sterne wird über das Zentrum faktorisiert."""
    n, A = Q; cls = [gl(beta[i], p)[1] for i in range(n)]
    deg = [sum((s == i) + (t == i) for s, t in A) for i in range(n)]; c = max(range(n), key=lambda i: deg[i])
    rest = [i for i in range(n) if i != c]
    comps, left = [], set(rest)                                    # Zusammenhangskomponenten ohne c
    while left:
        v = left.pop(); comp, todo = {v}, [v]
        while todo:
            x = todo.pop()
            for s, t in A:
                for a, b in ((s, t), (t, s)):
                    if a == x and b in left: left.discard(b); comp.add(b); todo.append(b)
        comps.append(sorted(comp))
    total = 0
    for gc, zc in cls[c]:
        prod = zc
        for comp in comps:
            arrows = [(s, t) for s, t in A if s in comp or t in comp]; sub = 0
            for choice in itertools.product(*[cls[i] for i in comp]):
                g = dict(zip(comp, [x[0] for x in choice])); g[c] = gc; w = math.prod(x[1] for x in choice)
                sub += w * p ** sum(fixdim(g[s], g[t], p) for s, t in arrows)
            prod *= sub
        loops_c = [(s, t) for s, t in A if s == c and t == c]
        prod *= p ** sum(fixdim(gc, gc, p) for _ in loops_c)
        total += prod
    order = math.prod(gl_order(b, p) for b in beta); M = Fr(total, order)
    assert M.denominator == 1, "Burnside-Summe nicht ganzzahlig"
    return int(M)


def box(alpha):
    return [b for b in itertools.product(*[range(a + 1) for a in alpha])]


def indecomposable_counts(Q, alpha, p):
    """I_beta(p) (Anzahl Isoklassen unzerlegbarer Darstellungen über F_p) für alle 0 < beta <= alpha, aus M_beta per
    Krull-Schmidt:  sum M_beta X^beta = prod_gamma (1 - X^gamma)^(-I_gamma)  (plethystischer Logarithmus)."""
    B = [b for b in box(alpha) if any(b)]; B.sort(key=sum); M = {tuple(0 for _ in alpha): 1}
    for b in B: M[b] = count_orbits(Q, b, p)
    L = {}
    for b in B:
        h = sum(b); acc = h * Fr(M[b])
        for g in L:
            if g != b and all(x <= y for x, y in zip(g, b)):
                acc -= sum(g) * L[g] * M[tuple(y - x for x, y in zip(g, b))]
        L[b] = acc / h
    I = {}
    for b in B:
        v = L[b]; gg = math.gcd(*b)
        for k in range(2, gg + 1):
            if gg % k == 0: v -= Fr(I[tuple(x // k for x in b)], k)
        assert v.denominator == 1, f"I_{b} nicht ganzzahlig: {v}"
        I[b] = int(v)
    return I, M


# ---------------------------------------------------------------- unabhängige Methode: direkte Aufzählung über F_p
def all_reps(Q, alpha, p):
    n, A = Q; shapes = [(alpha[t], alpha[s]) for s, t in A]
    for vals in itertools.product(*[itertools.product(range(p), repeat=r * c) for r, c in shapes]):
        maps = {}
        for k, ((r, c), v) in enumerate(zip(shapes, vals)):
            maps[str(k)] = [list(v[i * c:(i + 1) * c]) for i in range(r)]
        yield {"dims": list(alpha), "maps": maps}


def _hom_mod(Q, V, W, p):
    n, A = Q; off = [0]
    for i in range(n): off.append(off[-1] + W["dims"][i] * V["dims"][i])
    N = off[-1]; rows = []
    for k, (s, t) in enumerate(A):
        Va, Wa = V["maps"][str(k)], W["maps"][str(k)]
        for r in range(W["dims"][t]):
            for c in range(V["dims"][s]):
                row = [0] * N
                for j in range(W["dims"][s]): row[off[s] + j * V["dims"][s] + c] += int(Wa[r][j])
                for j in range(V["dims"][t]): row[off[t] + r * V["dims"][t] + j] -= int(Va[j][c])
                rows.append(row)
    B = nullspace_mod(rows, N, p) if rows else [[int(i == j) for j in range(N)] for i in range(N)]
    return [[[[v[off[i] + r * V["dims"][i] + c] for c in range(V["dims"][i])] for r in range(W["dims"][i])] for i in range(n)] for v in B]


def _combos(B, p):
    for coef in itertools.product(range(p), repeat=len(B)):
        yield [[[sum(cf * b[i][r][c] for cf, b in zip(coef, B)) % p for c in range(len(B[0][i][0]) if B[0][i] else 0)]
                 for r in range(len(B[0][i]))] for i in range(len(B[0]))]


def _is_iso(f, p):
    return all(len(m) == 0 or (len(m) == len(m[0]) and rank_mod(m, p) == len(m)) for m in f)


def _is_nilpotent(f, p, N):
    for m in f:
        if not m: continue
        X = tuple(tuple(r) for r in m); P = X
        for _ in range(max(N, 1)): P = mat_mul_mod(P, X, p)
        if any(any(r) for r in P): return False
    return True


def local_aut(Q, V, p):
    """(lokal?, |Aut V|): End(V) über F_p vollständig aufgezählt; lokal <=> jedes Nicht-Unit ist nilpotent (endlicher Ring)."""
    B = _hom_mod(Q, V, V, p); N = sum(V["dims"]); units = 0; local = True
    for f in _combos(B, p):
        if _is_iso(f, p): units += 1
        elif not _is_nilpotent(f, p, N): local = False
    return local, units


def brute_indecomposables(Q, alpha, p):
    """I_alpha(p) direkt: Summe über alle unzerlegbaren x in Rep_alpha(F_p) von |Aut x| / |G_alpha| (Bahnformel)."""
    tot = 0
    for V in all_reps(Q, alpha, p):
        loc, u = local_aut(Q, V, p)
        if loc: tot += u
    order = math.prod(gl_order(b, p) for b in alpha); r = Fr(tot, order)
    assert r.denominator == 1
    return int(r)


def rep_space_size(Q, alpha, p):
    return p ** sum(alpha[s] * alpha[t] for s, t in Q[1])


def iso_mod(Q, V, W, p):
    if V["dims"] != W["dims"]: return False
    B = _hom_mod(Q, V, W, p)
    return any(_is_iso(f, p) for f in _combos(B, p)) if B else not any(V["dims"])


def normal_forms(Q, alpha, p):
    """Experiment: Vertreter aller Isoklassen unzerlegbarer Darstellungen (Bahnen unter G_alpha) über F_p."""
    n, A = Q; G = list(itertools.product(*[gl(alpha[i], p)[0] for i in range(n)])); reps, seen = [], set()
    key = lambda V: tuple(tuple(tuple(r) for r in V["maps"][str(k)]) for k in range(len(A)))
    for V in all_reps(Q, alpha, p):
        k0 = key(V)
        if k0 in seen: continue
        orb = set()
        for g in G:
            gi = [_inv_mod(x, p) if x else () for x in g]
            orb.add(tuple(tuple(tuple(r) for r in (mat_mul_mod(mat_mul_mod(g[t], V["maps"][str(k)], p), gi[s], p)
                                                      if alpha[s] and alpha[t] else V["maps"][str(k)])) for k, (s, t) in enumerate(A)))
        seen |= orb
        if local_aut(Q, V, p)[0]: reps.append(V)
    return reps


# ------------------------------------------------------------------------------- Vorhersagen aus der Klassifikation
def n_irred_nonzero(d, q):
    """Anzahl normierter irreduzibler Polynome vom Grad d über F_q mit Absolutglied != 0."""
    N = sum(_mu(d // e) * q ** e for e in range(1, d + 1) if d % e == 0) // d
    return N - (1 if d == 1 else 0)


def _mu(n):
    r, k = 1, 2
    while k * k <= n:
        if n % k == 0:
            n //= k
            if n % k == 0: return 0
            r = -r
        k += 1
    return -r if n > 1 else r


def cycle_prediction(nv, alpha, q):
    """Klassifikation des orientierten n-Zykels 0->1->...->n-1->0: Unzerlegbare sind (i) nilpotente Strings S(i, l)
    (Kopf in i, Länge l >= 1) und (ii) für alpha = m*delta: invertierbare Monodromie, unzerlegbarer F_q[x, 1/x]-Modul
    der Dimension m (Anzahl: sum_{d | m} N*_d(q)). Gibt die vorhergesagte Anzahl I_alpha(q) zurück."""
    L = sum(alpha); cnt = 0
    for i in range(nv):
        v = [0] * nv
        for j in range(L): v[(i + j) % nv] += 1
        cnt += tuple(v) == tuple(alpha)
    if len(set(alpha)) == 1 and alpha[0] > 0:
        m = alpha[0]; cnt += sum(n_irred_nonzero(d, q) for d in range(1, m + 1) if m % d == 0)
    return cnt
