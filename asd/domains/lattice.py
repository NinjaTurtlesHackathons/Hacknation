"""Gitter-Labor: Dreikörper-Potenzenergie T_nu(L) = sum'_{x != y in L\\{0}} (|x||y||x-y|)^(-nu)
für Bravais-Gitter mit Kovolumen 1 (Suleman 2026, Gl. (1)). Die "Experimente" sind Berechnungen:
die Wahrheit wird gerechnet, nicht nachgeschlagen.

Numerik wie in Suleman 2026, Anhang A: freie Ecken x, y über den Würfel [-R,R]^d der Gitterkoordinaten,
Kern der dritten Seite über [-2R,2R]^d, Faltung per FFT, Richardson-Extrapolation in R mit dem bekannten
Abfall des Abschneidefehlers (R^(d-2nu) für nu > d, R^(2d-3nu) für 2d/3 < nu < d).
"""
import numpy as np
from scipy.signal import fftconvolve

SQ3 = np.sqrt(3.0)
RHO = complex(0.5, SQ3 / 2)          # hexagonaler Punkt
I = complex(0.0, 1.0)                # quadratischer Punkt


def basis_from_tau(tau: complex) -> np.ndarray:
    """2D-Gitter (Z + tau Z)/sqrt(Im tau), Spalten = Basisvektoren, Kovolumen 1."""
    s = 1 / np.sqrt(tau.imag)
    return np.array([[s, tau.real * s], [0.0, tau.imag * s]])


def normalize(B):
    B = np.asarray(B, float); return B / abs(np.linalg.det(B)) ** (1 / B.shape[0])


BCC = normalize(np.array([[1, 1, -1], [1, -1, 1], [-1, 1, 1]]).T * 0.5)
FCC = normalize(np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]]).T * 0.5)
SC = np.eye(3)


def _f(B, R, nu):
    d = B.shape[0]; ax = np.arange(-R, R + 1)
    K = np.stack(np.meshgrid(*[ax] * d, indexing="ij"), -1).reshape(-1, d)
    r2 = np.einsum("ij,nj->ni", B, K); r2 = (r2 ** 2).sum(1)
    with np.errstate(divide="ignore"):
        f = np.where(r2 > 0, r2 ** (-nu / 2), 0.0)
    return f.reshape([2 * R + 1] * d)


def T_trunc(B, nu, R):
    """Abgeschnittene Summe über x, y in [-R,R]^d (Gitterkoordinaten); x - y beliebig in [-2R,2R]^d."""
    f = _f(B, R, nu); F = _f(B, 2 * R, nu)
    conv = fftconvolve(f, F[tuple(slice(None, None, -1) for _ in range(f.ndim))], mode="valid")  # sum_y f(y) F(x-y)
    # 'valid' liefert die Korrelation über Verschiebungen in [-R,R]^d; wir brauchen sum_y f(y) F(x-y) mit x in [-R,R]^d
    return float((f * conv[tuple(slice(None, None, -1) for _ in range(f.ndim))]).sum())


def T_direct(B, nu, R):
    """Direkte Summe über x, y in [-R,R]^d. Für große nu nötig: dort löscht die FFT-Faltung Terme der
    Größe |x|^-nu >> T aus, und ihr absoluter Rundungsfehler übersteigt T."""
    d = B.shape[0]; ax = np.arange(-R, R + 1)
    K = np.stack(np.meshgrid(*[ax] * d, indexing="ij"), -1).reshape(-1, d); K = K[np.any(K != 0, 1)]
    X = K @ B.T; lx = np.log(np.linalg.norm(X, axis=1))
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2); np.fill_diagonal(D, 1.0)
    with np.errstate(divide="ignore"):
        L = lx[:, None] + lx[None, :] + np.log(D)
    np.fill_diagonal(L, np.inf)
    return float(np.exp(-nu * L).sum())


NU_DIRECT = 12.0


def T(B, nu, R=(24, 32), richardson=True):
    """Richardson-extrapolierte Energie. Gibt (Wert, Fehlerschätzung) zurück.
    Für nu >= NU_DIRECT direkte Summation mit kleinem R (Terme fallen dort extrem schnell ab)."""
    d = B.shape[0]; p = 2 * nu - d if nu > d else 3 * nu - 2 * d
    if nu >= NU_DIRECT:
        r1, r2 = {2: (6, 8), 3: (3, 4)}.get(d, (2, 3))
        t1, t2 = T_direct(B, nu, r1), T_direct(B, nu, r2); return t2, abs(t2 - t1)
    r1, r2 = R; t1, t2 = T_trunc(B, nu, r1), T_trunc(B, nu, r2)
    if not richardson: return t2, abs(t2 - t1)
    if p * np.log(r2 / r1) > 30: return t2, abs(t2 - t1)      # Abfall so steil, dass Extrapolation nichts bringt
    w = (r2 / r1) ** p; t = (w * t2 - t1) / (w - 1)
    return t, abs(t - t2)


def T_tau(tau, nu, R=(24, 32)):
    return T(basis_from_tau(tau), nu, R)


def reduce_tau(tau: complex) -> complex:
    """In den Fundamentalbereich |Re| <= 1/2, |tau| >= 1, und per Spiegelung auf Re >= 0."""
    for _ in range(100):
        tau = complex(tau.real - round(tau.real), tau.imag)
        if abs(tau) < 1 - 1e-15: tau = -1 / tau
        else: break
    return complex(abs(tau.real), tau.imag)


# ---------------------------------------------------------------------------------------------
# Experiment-Primitive (das, was Agenten planen und das Lab ausführt). Jede gibt ein JSON-fähiges
# Ergebnis mit Fehlerschätzung zurück.
# ---------------------------------------------------------------------------------------------
from scipy.optimize import minimize as _minimize

FAST, ACC = (12, 16), (32, 48)


def _fd_point(x, y): return complex(x, y)


def _in_fd(x, y): return 0 <= x <= 0.5 and x * x + y * y >= 1 - 1e-12


def energy2d(tau, nu, R=ACC):
    v, e = T_tau(reduce_tau(complex(tau)), nu, R); return {"T": v, "err": e}


def compare2d(tau_a, tau_b, nu, R=ACC):
    a, ea = T_tau(reduce_tau(complex(tau_a)), nu, R); b, eb = T_tau(reduce_tau(complex(tau_b)), nu, R)
    err = ea + eb + 1e-13 * max(a, b)
    return {"T_a": a, "T_b": b, "diff": a - b, "err": err, "sicher": abs(a - b) > 3 * err}


def minimize2d(nu, grid=14, ymax=1.8, R_grid=FAST, R_fine=ACC, n_polish=4):
    """Globale Suche über den Fundamentalbereich: Gitter-Raster + Nelder-Mead-Politur der besten Startpunkte.
    Gibt das beste tau, die Energie und die gefundenen lokalen Minima zurück."""
    xs = np.linspace(0, 0.5, grid); ys = np.linspace(np.sqrt(3) / 2, ymax, grid)
    cand = [(T_tau(complex(x, y), nu, R_grid)[0], x, y) for x in xs for y in ys if _in_fd(x, y)]
    cand += [(T_tau(t, nu, R_grid)[0], t.real, t.imag) for t in (RHO, I)]
    cand.sort(); minima = []
    def obj(p):
        x, y = p
        if y <= 0.3: return 1e9
        t = reduce_tau(complex(x, y)); return T_tau(t, nu, R_fine)[0]
    for _, x, y in cand[:n_polish]:
        r = _minimize(obj, [x, y], method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-13, maxiter=300))
        t = reduce_tau(complex(*r.x)); minima.append((r.fun, t))
    minima.sort(key=lambda m: m[0]); best_T, best = minima[0]
    uniq = []
    for v, t in minima:
        if all(abs(t - u[1]) > 1e-3 for u in uniq): uniq.append((v, t))
    return {"tau": [best.real, best.imag], "T": best_T, "typ": classify(best),
            "lokale_minima": [{"tau": [t.real, t.imag], "T": v, "typ": classify(t)} for v, t in uniq]}


def classify(tau, tol=2e-3):
    tau = reduce_tau(complex(tau))
    if abs(tau - RHO) < tol: return "hexagonal"
    if abs(tau - I) < tol: return "quadratisch"
    if abs(tau.real) < tol: return f"rechteckig(y={tau.imag:.4f})"
    if abs(abs(tau) - 1) < tol: return "rhombisch"
    if abs(tau.real - 0.5) < tol: return "zentriert-rechteckig"
    return "schief"


def hessian2d(tau, nu, h=2e-3, R=ACC):
    """Hessematrix von T in (x, y) am Punkt tau (zentrale Differenzen). Eigenwerte > 0 = lokal stabil.
    Am Rand des Fundamentalbereichs wird über die Spiegelsymmetrie fortgesetzt (reduce_tau)."""
    t0 = complex(tau); f = lambda dx, dy: T_tau(reduce_tau(t0 + complex(dx, dy)), nu, R)[0]
    f0 = f(0, 0); fxx = (f(h, 0) - 2 * f0 + f(-h, 0)) / h ** 2; fyy = (f(0, h) - 2 * f0 + f(0, -h)) / h ** 2
    fxy = (f(h, h) - f(h, -h) - f(-h, h) + f(-h, -h)) / (4 * h * h)
    ev = np.linalg.eigvalsh(np.array([[fxx, fxy], [fxy, fyy]]))
    return {"eigenwerte": [float(e) for e in ev], "stabil": bool(ev.min() > 0)}


def crossing2d(tau_a, tau_b, nu_lo, nu_hi, tol=1e-6, R=ACC):
    """Bisektion auf das Vorzeichen von T(a) - T(b) zwischen nu_lo und nu_hi."""
    g = lambda nu: compare2d(tau_a, tau_b, nu, R)["diff"]
    a, b = nu_lo, nu_hi; ga, gb = g(a), g(b)
    if np.sign(ga) == np.sign(gb): return {"gefunden": False, "diff_lo": ga, "diff_hi": gb}
    while b - a > tol:
        m = (a + b) / 2; gm = g(m)
        if np.sign(gm) == np.sign(ga): a, ga = m, gm
        else: b, gb = m, gm
    return {"gefunden": True, "intervall": [a, b]}


def rect_optimum(nu, y_lo=1.0, y_hi=1.4, R=ACC):
    """Bestes Seitenverhältnis y innerhalb der Rechteckgitter tau = i*y."""
    from scipy.optimize import minimize_scalar
    r = minimize_scalar(lambda y: T_tau(complex(0, y), nu, R)[0], bounds=(y_lo, y_hi), method="bounded", options=dict(xatol=1e-7))
    return {"y": float(r.x), "T": float(r.fun)}


def bct(c_over_a):
    """Raumzentriert-tetragonal (Bain-Pfad): c/a = 1 ist BCC, c/a = sqrt(2) ist FCC. Kovolumen 1."""
    a, c = 1.0, float(c_over_a)
    return normalize(np.array([[-a / 2, a / 2, c / 2], [a / 2, -a / 2, c / 2], [a / 2, a / 2, -c / 2]]).T)


def energy3d(name_or_ca, nu, R=(8, 12)):
    B = {"bcc": BCC, "fcc": FCC, "sc": SC}.get(str(name_or_ca).lower())
    if B is None: B = bct(float(name_or_ca))
    v, e = T(B, nu, R); return {"T": v, "err": e}


def bain_curvature(ca, nu, h=1e-3, R=(8, 12)):
    f = lambda c: T(bct(c), nu, R)[0]
    return {"kruemmung": (f(ca + h) - 2 * f(ca) + f(ca - h)) / h ** 2}


PRIMITIVES = {
    "energy2d": energy2d, "compare2d": compare2d, "minimize2d": minimize2d, "hessian2d": hessian2d,
    "crossing2d": crossing2d, "rect_optimum": rect_optimum, "energy3d": energy3d, "bain_curvature": bain_curvature,
}


def asymptote(nus=(40, 60, 100, 160, 250), R=(24, 32)):
    """Optimales Seitenverhältnis y_nu für große nu und Fit y = a + b/nu + c/nu^2 (a ~ y_inf, -b ~ kappa)."""
    ys = [rect_optimum(nu, 1.1, 1.3, R)["y"] for nu in nus]
    A = np.array([[1, 1 / n, 1 / n ** 2] for n in nus]); coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    return {"nus": list(nus), "ys": ys, "y_inf_fit": float(coef[0]), "kappa_fit": float(-coef[1]), "c2": float(coef[2])}


PRIMITIVES["asymptote"] = asymptote

PRIMITIVE_DOC = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}), alle für Gitter mit Kovolumen 1:
- energy2d {tau: [x, y], nu}: Energie T_nu des 2D-Gitters tau = x + i y, mit Fehlerschätzung.
- compare2d {tau_a: [x,y], tau_b: [x,y], nu}: T(a) - T(b) mit Fehler und Flag 'sicher'.
- minimize2d {nu}: globale Suche über den Fundamentalbereich (Raster + Nelder-Mead); bestes tau, Typ, lokale Minima.
- hessian2d {tau: [x,y], nu}: Eigenwerte der Hessematrix von T in (x, y); 'stabil' = beide > 0.
- crossing2d {tau_a, tau_b, nu_lo, nu_hi}: Bisektion auf den Vorzeichenwechsel von T(a) - T(b) in nu.
- rect_optimum {nu, y_lo, y_hi}: bestes Seitenverhältnis y unter Rechteckgittern tau = i y.
- asymptote {nus: [...]}: y_nu für große nu plus Fit y = a + b/nu + c/nu^2.
- energy3d {name_or_ca: "bcc"|"fcc"|"sc"|c/a-Zahl, nu}: Energie in 3D (Zahl = raumzentriert-tetragonal mit c/a; 1 = BCC, sqrt(2) = FCC).
- bain_curvature {ca, nu}: zweite Ableitung von T entlang des Bain-Pfads bei c/a = ca.
Hexagonal: tau = [0.5, 0.8660254]; quadratisch: tau = [0, 1]. Rechenzeit: minimize2d ~5 s, sonst < 3 s."""


def run_op(op, args):
    """Führt ein Experiment aus; tau-Listen werden zu komplexen Zahlen. Gibt JSON-fähiges Ergebnis zurück."""
    if op not in PRIMITIVES: return {"fehler": f"unbekannte op {op}"}
    a = dict(args or {})
    for k in ("tau", "tau_a", "tau_b"):
        if k in a and isinstance(a[k], (list, tuple)): a[k] = complex(*a[k])
    try:
        out = PRIMITIVES[op](**a)
    except Exception as e:                       # Agenten dürfen Fehler machen; das Lab bleibt stabil
        return {"fehler": f"{type(e).__name__}: {e}"[:300]}
    return json.loads(json.dumps(out, default=lambda o: float(o) if np.isscalar(o) else str(o)))


import json  # noqa: E402


# ---------------------------------------------------------------------------------------------
# Dimension 4 (offene Frage aus Suleman 2026, Abschnitt 9 / Vermutung 2)
# ---------------------------------------------------------------------------------------------
def _from_gram(G):
    return normalize(np.linalg.cholesky(np.asarray(G, float)).T)


_A4 = 2 * np.eye(4) - np.eye(4, k=1) - np.eye(4, k=-1)
LAT4 = {
    "z4": np.eye(4),
    "d4": normalize(np.array([[1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1], [0, 0, 1, 1]], float).T),
    "a4": _from_gram(_A4),
    "a4*": _from_gram(np.linalg.inv(_A4)),
}
LAT3 = {"bcc": BCC, "fcc": FCC, "sc": SC}
R4 = (4, 6)


def energy_nd(name, nu, R=None):
    """Energie benannter Gitter: 3D bcc|fcc|sc, 4D z4|d4|a4|a4*."""
    name = str(name).lower(); B = LAT4.get(name, LAT3.get(name))
    if B is None: return {"fehler": f"unbekanntes Gitter {name}"}
    R = R or (R4 if B.shape[0] == 4 else (8, 12)); v, e = T(B, nu, R); return {"T": v, "err": e}


def lll(B, delta=0.75):
    """LLL-Reduktion (Spalten = Basisvektoren). Nötig, damit der Würfel [-R,R]^d in Gitterkoordinaten
    die kurzen Vektoren enthält; sonst nutzt ein Optimierer das Abschneiden aus (T -> 0 bei schiefen Basen)."""
    B = np.array(B, float); d = B.shape[1]; k = 1
    def gs(B):
        Q = np.zeros_like(B); mu = np.zeros((d, d))
        for i in range(d):
            Q[:, i] = B[:, i]
            for j in range(i):
                mu[i, j] = B[:, i] @ Q[:, j] / (Q[:, j] @ Q[:, j]); Q[:, i] -= mu[i, j] * Q[:, j]
        return Q, mu
    Q, mu = gs(B); it = 0
    while k < d and it < 1000:
        it += 1
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q: B[:, k] -= q * B[:, j]; Q, mu = gs(B)
        if Q[:, k] @ Q[:, k] >= (delta - mu[k, k - 1] ** 2) * (Q[:, k - 1] @ Q[:, k - 1]): k += 1
        else: B[:, [k, k - 1]] = B[:, [k - 1, k]]; Q, mu = gs(B); k = max(k - 1, 1)
    return B


def _basis_from_params(p, d):
    U = np.zeros((d, d)); U[np.triu_indices(d)] = p
    U[np.diag_indices(d)] = np.abs(U[np.diag_indices(d)]) + 1e-3
    return lll(normalize(U))


def _lll_reduced_gram(B):
    """Grobe Reduktion (paarweise Größenreduktion) für eine vergleichbare Darstellung."""
    B = B.copy(); d = B.shape[1]
    for _ in range(20):
        changed = False
        for i in range(d):
            for j in range(d):
                if i != j:
                    mu = round(B[:, i] @ B[:, j] / (B[:, j] @ B[:, j]))
                    if mu: B[:, i] -= mu * B[:, j]; changed = True
        if not changed: break
    return B.T @ B


def identify(B, tol=2e-2):
    """Vergleicht ein gefundenes Gitter über die sortierten Normen kürzester Vektoren mit bekannten Gittern."""
    d = B.shape[0]; ref = LAT4 if d == 4 else LAT3
    def sig(M):
        ax = np.arange(-2, 3); K = np.stack(np.meshgrid(*[ax] * d, indexing="ij"), -1).reshape(-1, d); K = K[np.any(K != 0, 1)]
        n = np.sort(np.linalg.norm(K @ M.T, axis=1))[:24]; return n
    s = sig(B); best = min(ref, key=lambda k: np.abs(sig(ref[k]) - s).max())
    return best if np.abs(sig(ref[best]) - s).max() < tol else "unbekannt"


def minimize_nd(d, nu, starts=4, seed=0, R=None, maxiter=300):
    """Lokale Suche über alle Bravais-Gitter der Dimension d (3 oder 4) ab zufälligen Startbasen + bekannten Gittern."""
    rng = np.random.default_rng(seed); R = R or ((3, 4) if d == 4 else (4, 6)); out = []
    for s in range(starts):
        p0 = rng.normal(0, 0.3, d * (d + 1) // 2); p0[[i * (2 * d - i + 1) // 2 for i in range(d)]] += 1.0
        f = lambda p: T(_basis_from_params(p, d), nu, R)[0]
        r = _minimize(f, p0, method="BFGS", options=dict(maxiter=maxiter, gtol=1e-7))
        B = _basis_from_params(r.x, d); Rf = R4 if d == 4 else (8, 12)
        out.append({"start": s, "T_suche": float(r.fun), "T": float(T(B, nu, Rf)[0]), "gitter": identify(B), "iterationen": int(r.nit)})
    ref = {k: T(v, nu, R4 if d == 4 else (8, 12))[0] for k, v in (LAT4 if d == 4 else LAT3).items()}
    return {"laeufe": sorted(out, key=lambda o: o["T"]), "referenz_T": ref, "R": list(R)}


PRIMITIVES["energy_nd"] = energy_nd
PRIMITIVES["minimize_nd"] = minimize_nd

PRIMITIVE_DOC += """
- energy_nd {name: "bcc"|"fcc"|"sc"|"z4"|"d4"|"a4"|"a4*", nu, R?: [r1, r2]}: Energie benannter 3D/4D-Gitter (Richardson in R; R=[6,8] genauer, langsamer).
- minimize_nd {d: 3|4, nu, starts, seed}: lokale BFGS-Suche über alle Bravais-Gitter der Dimension d ab zufälligen Startbasen (LLL-reduziert); gefundene Gitter werden über kurze Vektoren identifiziert (sonst "unbekannt"). Dauer in 4D ~20-60 s pro Start."""
