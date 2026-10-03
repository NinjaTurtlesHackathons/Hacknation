"""Numerik und Zertifikate für bipartite Bell-Ungleichungen mit zwei Ausgängen (±1-Observablen).

Eine Ungleichung ist in Korrelatorform gegeben:
    I = konst + sum_x a_x <A_x> + sum_y b_y <B_y> + sum_xy c_xy <A_x B_y>
(Collins-Gisin-Form und benannte Familien werden in diese Form übersetzt, exakt in rationalen Zahlen).

Drei Werkzeuge, alle mit exakter (rationaler) Endprüfung:
  lokal()        klassische Schranke durch Aufzählung aller deterministischen Strategien, exakt.
  seesaw()       explizite Quantenstrategie (reelle QM, Dimension d pro Seite) -> untere Schranke. Das Zertifikat
                 rundet die Strategie auf rationale Zahlen: A = I - 2 V (V^T V)^-1 V^T ist exakt eine ±1-Observable,
                 der Zustand wird exakt normiert, der Bell-Wert ist dann eine rationale Zahl.
  npa()          NPA-Hierarchie (Navascués-Pironio-Acín) als SDP -> obere Schranke. Das Zertifikat ist eine rationale
                 duale Matrix Z mit exakt erfüllten Gleichungen und exakt geprüfter Positivität von Z + eps*I (LDL^T in
                 rationalen Zahlen). Reelle Momentmatrizen genügen: Re(Gamma) einer komplexen Lösung ist zulässig.
"""
import hashlib, itertools, json, math, os, re
from fractions import Fraction as F
import numpy as np

STRAT_DIR = os.environ.get("ASD_BELL_STRAT", "projects/bell/strategien")
_STRAT = {}


# ---------------------------------------------------------------- Ungleichungen

def _q(v):
    """Zahl, Dezimal-String oder 'p/q' -> Fraction (exakt; Gleitkomma über seine Dezimaldarstellung)."""
    if isinstance(v, F): return v
    if isinstance(v, bool): raise ValueError("bool ist kein Koeffizient")
    if isinstance(v, int): return F(v)
    if isinstance(v, float):
        if not math.isfinite(v): raise ValueError("nicht endlich")
        return F(repr(v))
    if isinstance(v, str): return F(v.strip())
    raise ValueError(f"Koeffizient nicht lesbar: {v!r}")


def _family(name):
    n = name.strip().lower()
    if n == "chsh": return {"korrelator": {"a": [0, 0], "b": [0, 0], "c": [[1, 1], [1, -1]]}}
    if n == "i3322":   # Collins-Gisin 2004, Form p(A=+1), p(B=+1), p(+1,+1)
        return {"cg": {"pa": [-1, 0, 0], "pb": [-2, -1, 0], "pab": [[1, 1, 1], [1, 1, -1], [1, -1, 0]]}}
    m = re.fullmatch(r"(?:chained|kette):(\d+)", n)
    if m:   # Braunstein-Caves: sum_k <A_k B_k> + <A_{k+1} B_k>, A_{m+1} = -A_1
        k = int(m.group(1))
        if not 2 <= k <= 12: raise ValueError("kette:m braucht 2 <= m <= 12")
        c = [[0] * k for _ in range(k)]
        for j in range(k):
            c[j][j] += 1
            if j + 1 < k: c[j + 1][j] += 1
            else: c[0][j] -= 1
        return {"korrelator": {"a": [0] * k, "b": [0] * k, "c": c}}
    m = re.fullmatch(r"(?:tilted|gekippt):([0-9./+-]+)", n)
    if m:   # beta <A_1> + CHSH
        return {"korrelator": {"a": [m.group(1), 0], "b": [0, 0], "c": [[1, 1], [1, -1]]}}
    raise ValueError(f"unbekannte benannte Ungleichung {name!r} (chsh, i3322, kette:m, gekippt:beta)")


def parse(spec):
    """-> dict(a, b, c, konst) mit Fractions, mA, mB. Fehler als ValueError."""
    if isinstance(spec, str): spec = _family(spec)
    if not isinstance(spec, dict): raise ValueError("Ungleichung muss Name oder Objekt sein")
    if "name" in spec and len(spec) == 1: spec = _family(spec["name"])
    if "korrelator" in spec:
        k = spec["korrelator"]; c = [[_q(v) for v in row] for row in k["c"]]
        mA, mB = len(c), len(c[0]) if c else 0
        a = [_q(v) for v in k.get("a", [0] * mA)]; b = [_q(v) for v in k.get("b", [0] * mB)]; konst = _q(k.get("konst", 0))
    elif "cg" in spec:
        g = spec["cg"]; pab = [[_q(v) for v in row] for row in g["pab"]]
        mA, mB = len(pab), len(pab[0]) if pab else 0
        pa = [_q(v) for v in g.get("pa", [0] * mA)]; pb = [_q(v) for v in g.get("pb", [0] * mB)]
        konst = _q(g.get("konst", 0)) + sum(pa) / 2 + sum(pb) / 2 + sum(sum(r) for r in pab) / 4
        a = [pa[x] / 2 + sum(pab[x]) / 4 for x in range(mA)]
        b = [pb[y] / 2 + sum(pab[x][y] for x in range(mA)) / 4 for y in range(mB)]
        c = [[pab[x][y] / 4 for y in range(mB)] for x in range(mA)]
    else:
        raise ValueError("Ungleichung braucht 'korrelator' oder 'cg' (oder einen Namen)")
    if not (1 <= mA <= 10 and 1 <= mB <= 10): raise ValueError("1 bis 10 Einstellungen pro Seite")
    if len(a) != mA or len(b) != mB or any(len(r) != mB for r in c): raise ValueError("Dimensionen von a, b, c passen nicht zusammen")
    return {"a": a, "b": b, "c": c, "konst": konst, "mA": mA, "mB": mB}


def key(I):
    s = json.dumps([[str(v) for v in I["a"]], [str(v) for v in I["b"]], [[str(v) for v in r] for r in I["c"]], str(I["konst"])])
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def show(I):
    t = [str(I["konst"])] if I["konst"] else []
    t += [f"{v}*A{x+1}" for x, v in enumerate(I["a"]) if v] + [f"{v}*B{y+1}" for y, v in enumerate(I["b"]) if v]
    t += [f"{v}*A{x+1}B{y+1}" for x, r in enumerate(I["c"]) for y, v in enumerate(r) if v]
    return " + ".join(t).replace("+ -", "- ") or "0"


def fl(I):
    return {"a": np.array([float(v) for v in I["a"]]), "b": np.array([float(v) for v in I["b"]]),
            "c": np.array([[float(v) for v in r] for r in I["c"]]), "konst": float(I["konst"])}


# ---------------------------------------------------------------- klassisch (exakt)

def local_bound(I):
    """Exakte klassische Schranke: max über a in {±1}^mA von konst + a.alpha + sum_y |b_y + sum_x c_xy a_x|."""
    a, b, c, mA, mB = I["a"], I["b"], I["c"], I["mA"], I["mB"]
    best, arg = None, None
    for s in itertools.product((1, -1), repeat=mA):
        v = I["konst"] + sum(a[x] * s[x] for x in range(mA))
        ys = []
        for y in range(mB):
            t = b[y] + sum(c[x][y] * s[x] for x in range(mA)); v += abs(t); ys.append(1 if t >= 0 else -1)
        if best is None or v > best: best, arg = v, (s, tuple(ys))
    return best, arg


# ---------------------------------------------------------------- Quantenstrategien (reelle QM)

def _obs_from(M):
    """beste ±1-Observable für tr(A M): A = sign(M_sym)."""
    w, U = np.linalg.eigh((M + M.T) / 2)
    return (U * np.where(w >= 0, 1.0, -1.0)) @ U.T


def _random_obs(d, rng):
    Q, _ = np.linalg.qr(rng.normal(size=(d, d))); s = rng.choice([1.0, -1.0], size=d)
    if np.all(s == s[0]): s[rng.integers(d)] *= -1
    return (Q * s) @ Q.T


def bell_value(If, Psi, A, B):
    """<psi| W |psi> mit psi = vec(Psi) (d x d, ||Psi||_F = 1): <A x B> = tr(Psi^T A Psi B)."""
    v = If["konst"]
    PPt, PtP = Psi @ Psi.T, Psi.T @ Psi
    v += sum(If["a"][x] * np.trace(A[x] @ PPt) for x in range(len(A)))
    v += sum(If["b"][y] * np.trace(B[y] @ PtP) for y in range(len(B)))
    v += sum(If["c"][x, y] * np.trace(Psi.T @ A[x] @ Psi @ B[y]) for x in range(len(A)) for y in range(len(B)))
    return float(v)


def bell_operator(If, A, B):
    d = A[0].shape[0]; I_ = np.eye(d); W = If["konst"] * np.eye(d * d)
    for x in range(len(A)): W += If["a"][x] * np.kron(A[x], I_)
    for y in range(len(B)): W += If["b"][y] * np.kron(I_, B[y])
    for x in range(len(A)):
        for y in range(len(B)): W += If["c"][x, y] * np.kron(A[x], B[y])
    return W


def seesaw_once(If, d, rng, iters=500, tol=1e-12):
    mA, mB = If["c"].shape
    A = [_random_obs(d, rng) for _ in range(mA)]; B = [_random_obs(d, rng) for _ in range(mB)]
    Psi = rng.normal(size=(d, d)); Psi /= np.linalg.norm(Psi); last = -np.inf
    for _ in range(iters):
        w, V = np.linalg.eigh(bell_operator(If, A, B)); Psi = V[:, -1].reshape(d, d)
        A = [_obs_from(If["a"][x] * Psi @ Psi.T + sum(If["c"][x, y] * Psi @ B[y] @ Psi.T for y in range(mB))) for x in range(mA)]
        B = [_obs_from(If["b"][y] * Psi.T @ Psi + sum(If["c"][x, y] * Psi.T @ A[x] @ Psi for x in range(mA))) for y in range(mB)]
        val = bell_value(If, Psi, A, B)
        if val - last < tol: break
        last = val
    w, V = np.linalg.eigh(bell_operator(If, A, B)); Psi = V[:, -1].reshape(d, d)
    return bell_value(If, Psi, A, B), Psi, A, B


def store(I, d, Psi, A, B, value):
    rec = {"ungleichung_key": key(I), "ungleichung": show(I), "d": d, "psi": Psi.tolist(), "A": [x.tolist() for x in A],
           "B": [y.tolist() for y in B], "wert_numerisch": value}
    sid = "S" + hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:12]
    rec["id"] = sid; _STRAT[sid] = rec
    try:
        os.makedirs(STRAT_DIR, exist_ok=True)
        with open(f"{STRAT_DIR}/{sid}.json", "w") as f: json.dump(rec, f)
    except OSError:
        pass
    return sid


def load(sid):
    if sid in _STRAT: return _STRAT[sid]
    p = f"{STRAT_DIR}/{sid}.json"
    if re.fullmatch(r"S[0-9a-f]{12}", str(sid)) and os.path.exists(p):
        _STRAT[sid] = json.load(open(p)); return _STRAT[sid]
    return None


def seesaw(I, d=2, starts=10, seed=0, iters=500):
    If = fl(I); rng = np.random.default_rng(seed); vals = []; best = None
    for _ in range(starts):
        r = seesaw_once(If, d, rng, iters); vals.append(r[0])
        if best is None or r[0] > best[0]: best = r
    sid = store(I, d, best[1], best[2], best[3], best[0])
    return best[0], sid, sorted(vals, reverse=True)


# ---------------------------------------------------------------- Zertifikat: untere Schranke (exakt rational)

DEN = 10 ** 10


def _rat(x): return F(int(round(float(x) * DEN)), DEN)


def _matmul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]


def _T(X): return [list(r) for r in zip(*X)]


def _inv(M):
    n = len(M); A = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for k in range(n):
        p = next((i for i in range(k, n) if A[i][k] != 0), None)
        if p is None: raise ValueError("singulär")
        A[k], A[p] = A[p], A[k]; piv = A[k][k]; A[k] = [v / piv for v in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]; A[i] = [vi - f * vk for vi, vk in zip(A[i], A[k])]
    return [r[n:] for r in A]


def exact_observable(Afl):
    """Rationale ±1-Observable nahe Afl: A = I - 2 P, P = V (V^T V)^-1 V^T, V = gerundete Eigenvektoren zu -1."""
    Afl = np.array(Afl, dtype=float); d = Afl.shape[0]
    w, U = np.linalg.eigh((Afl + Afl.T) / 2)
    idx = [i for i in range(d) if w[i] < 0]
    I_ = [[F(int(i == j)) for j in range(d)] for i in range(d)]
    if not idx: return I_, 0.0
    V = [[_rat(U[i, j]) for j in idx] for i in range(d)]
    P = _matmul(_matmul(V, _inv(_matmul(_T(V), V))), _T(V))
    A = [[I_[i][j] - 2 * P[i][j] for j in range(d)] for i in range(d)]
    return A, float(np.max(np.abs(np.abs(w) - 1)))


def exact_value(I, rec):
    """Exakter Bell-Wert einer gespeicherten Strategie nach rationaler Rundung -> (Fraction, Diagnose)."""
    d = rec["d"]; mA, mB = I["mA"], I["mB"]
    if len(rec["A"]) != mA or len(rec["B"]) != mB: raise ValueError("Strategie passt nicht zur Zahl der Einstellungen")
    A, ea = zip(*[exact_observable(x) for x in rec["A"]]); B, eb = zip(*[exact_observable(y) for y in rec["B"]])
    for M in list(A) + list(B):     # Selbstkontrolle: A symmetrisch, A^2 = I exakt
        if any(M[i][j] != M[j][i] for i in range(d) for j in range(d)): raise ValueError("Observable nicht symmetrisch")
        M2 = _matmul(M, M)
        if any(M2[i][j] != (1 if i == j else 0) for i in range(d) for j in range(d)): raise ValueError("A^2 != I")
    Psi = [[_rat(v) for v in r] for r in rec["psi"]]
    norm = sum(v * v for r in Psi for v in r)
    if norm == 0: raise ValueError("Nullzustand")
    PPt, PtP = _matmul(Psi, _T(Psi)), _matmul(_T(Psi), Psi)
    tr = lambda X, Y: sum(X[i][j] * Y[j][i] for i in range(d) for j in range(d))
    v = I["konst"] * norm
    v += sum(I["a"][x] * tr(A[x], PPt) for x in range(mA) if I["a"][x])
    v += sum(I["b"][y] * tr(B[y], PtP) for y in range(mB) if I["b"][y])
    for x in range(mA):
        if not any(I["c"][x]): continue
        APsi = _matmul(_matmul(_T(Psi), A[x]), Psi)          # Psi^T A Psi
        for y in range(mB):
            if I["c"][x][y]: v += I["c"][x][y] * tr(APsi, B[y])
    return v / norm, {"d": d, "max_eigabweichung": max(ea + eb)}


# ---------------------------------------------------------------- NPA mit rationalem Dualzertifikat

def _cancel(w):
    out = []
    for l in w:
        if out and out[-1] == l: out.pop()
        else: out.append(l)
    return tuple(out)


def _red(w):
    return _cancel([l for l in w if l[0] == "A"]) + _cancel([l for l in w if l[0] == "B"])


def _canon(w):
    r1, r2 = _red(w), _red(tuple(reversed(w)))
    return min(r1, r2)


def npa_words(mA, mB, stufe):
    As = [(("A", x),) for x in range(mA)]; Bs = [(("B", y),) for y in range(mB)]
    S = [()] + As + Bs
    if stufe in ("1+AB", "2", "2+AAB"): S += [a + b for a in As for b in Bs]
    if stufe in ("2", "2+AAB"):
        S += [a + a2 for a in As for a2 in As if a != a2] + [b + b2 for b in Bs for b2 in Bs if b != b2]
    if stufe == "2+AAB":
        S += [a + a2 + b for a in As for a2 in As if a != a2 for b in Bs] + [a + b + b2 for a in As for b in Bs for b2 in Bs if b != b2]
    if stufe not in ("1", "1+AB", "2", "2+AAB"): raise ValueError("stufe muss 1, 1+AB, 2 oder 2+AAB sein")
    seen, out = set(), []
    for s in S:
        r = _red(s)
        if r not in seen: seen.add(r); out.append(r)
    return out


def npa_structure(I, stufe):
    S = npa_words(I["mA"], I["mB"], stufe); n = len(S)
    cls = {}
    for i in range(n):
        for j in range(n):
            w = _canon(tuple(reversed(S[i])) + S[j]); cls.setdefault(w, []).append((i, j))
    obj = {(): I["konst"]}
    for x in range(I["mA"]): obj[(("A", x),)] = I["a"][x]
    for y in range(I["mB"]): obj[(("B", y),)] = I["b"][y]
    for x in range(I["mA"]):
        for y in range(I["mB"]): obj[(("A", x), ("B", y))] = I["c"][x][y]
    for w in obj:
        if w not in cls: raise ValueError(f"Wort {w} fehlt in der Momentmatrix")
    return S, cls, obj


def npa_float(I, stufe="1+AB"):
    """Löst das duale SDP min <Z, F_1> s.t. <Z, F_w> = -c_w (w != 1), Z >= 0. Rückgabe (Schranke, Z)."""
    import cvxpy as cp
    S, cls, obj = npa_structure(I, stufe); n = len(S)
    Z = cp.Variable((n, n), symmetric=True); cons = [Z >> 0]
    mask = lambda ents: np.array([[1.0 if (i, j) in ents else 0.0 for j in range(n)] for i in range(n)])
    one = None
    for w, ents in cls.items():
        if w == (): one = mask(set(ents)); continue
        cons.append(cp.sum(cp.multiply(mask(set(ents)), Z)) == -float(obj.get(w, 0)))
    prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(one, Z))), cons)
    for solver in ("CLARABEL", "SCS"):
        try:
            prob.solve(solver=solver)
            if Z.value is not None and prob.status in ("optimal", "optimal_inaccurate"): break
        except Exception:
            continue
    if Z.value is None: raise ValueError(f"SDP nicht gelöst ({prob.status})")
    return float(I["konst"]) + float(prob.value), Z.value, (S, cls, obj)


def _is_pd_exact(M):
    """exakte Positiv-Definitheit über LDL^T in rationalen Zahlen."""
    n = len(M); A = [list(r) for r in M]
    for k in range(n):
        p = A[k][k]
        if p <= 0: return False
        for i in range(k + 1, n):
            if A[i][k] == 0: continue
            f = A[i][k] / p
            Ai, Ak = A[i], A[k]
            for j in range(k + 1, n): Ai[j] -= f * Ak[j]
    return True


def npa_certified(I, stufe="1+AB"):
    """Rigorose obere Schranke U (Fraction) aus einer rationalisierten dualen Lösung. Rückgabe (U, float-Wert, Diagnose)."""
    val, Zf, (S, cls, obj) = npa_float(I, stufe); n = len(S)
    Zs = (Zf + Zf.T) / 2; Z = [[_rat(Zs[i, j]) if i <= j else None for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i): Z[i][j] = Z[j][i]
    for w, ents in cls.items():          # Gleichungen <Z, F_w> = -c_w exakt herstellen (symmetrisch verteilt)
        if w == (): continue
        delta = -obj.get(w, F(0)) - sum(Z[i][j] for i, j in ents)
        if delta:
            share = delta / len(ents)
            for i, j in ents: Z[i][j] += share
    for w, ents in cls.items():
        if w != () and sum(Z[i][j] for i, j in ents) != -obj.get(w, F(0)): raise ValueError("Gleichung nicht exakt")
    if any(Z[i][j] != Z[j][i] for i in range(n) for j in range(n)): raise ValueError("Z nicht symmetrisch")
    lam = float(np.linalg.eigvalsh(np.array([[float(v) for v in r] for r in Z])).min())
    for t in (1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5):
        eps = F(repr(max(0.0, -lam) + t))
        if _is_pd_exact([[Z[i][j] + (eps if i == j else 0) for j in range(n)] for i in range(n)]):
            one = sum(Z[i][j] for i, j in cls[()]) + eps * len([1 for i, j in cls[()] if i == j])
            off_one = [(i, j) for i, j in cls[()] if i != j]
            if off_one: raise ValueError("Identitätsklasse außerhalb der Diagonale")
            U = I["konst"] + one
            return U, val, {"stufe": stufe, "groesse": n, "eps": float(eps), "lambda_min_float": lam}
    raise ValueError("Positivität nicht zertifizierbar (eps bis 1e-5)")


def npa_primal_lower(I, stufe="1+AB"):
    """Rigorose UNTERE Schranke für den Optimalwert der NPA-Stufe (nicht für Q!): rationale zulässige Momentmatrix
    Gamma_t = (1-t) Gamma_r + t I, Klassen exakt gemittelt, Positivität exakt per LDL^T. Rückgabe (Fraction, Diagnose)."""
    import cvxpy as cp
    S, cls, obj = npa_structure(I, stufe); n = len(S)
    G = cp.Variable((n, n), symmetric=True); cons = [G >> 0]
    for w, ents in cls.items():
        i0, j0 = ents[0]
        cons += [G[i, j] == (1 if w == () else G[i0, j0]) for i, j in ents[1:]] + ([G[i0, j0] == 1] if w == () else [])
    expr = sum(float(obj[w]) * G[cls[w][0]] for w in obj if w != () and obj[w] != 0)
    prob = cp.Problem(cp.Maximize(expr), cons)
    for solver in ("CLARABEL", "SCS"):
        try:
            prob.solve(solver=solver)
            if G.value is not None: break
        except Exception:
            continue
    if G.value is None: raise ValueError("primales SDP nicht gelöst")
    Gv = G.value; Gr = [[F(0)] * n for _ in range(n)]
    for w, ents in cls.items():
        m = F(1) if w == () else F(int(round(np.mean([Gv[i, j] for i, j in ents]) * DEN)), DEN)
        for i, j in ents: Gr[i][j] = m
    val = lambda M: I["konst"] + sum(obj[w] * M[cls[w][0][0]][cls[w][0][1]] for w in obj if w != ())
    for t in (0, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4):
        tt = F(repr(t))
        M = [[(1 - tt) * Gr[i][j] + (tt if i == j else 0) for j in range(n)] for i in range(n)]
        if _is_pd_exact(M): return val(M), {"stufe": stufe, "t": t, "primal_float": float(prob.value) + float(I["konst"])}
    raise ValueError("keine zulässige rationale Momentmatrix gefunden")
