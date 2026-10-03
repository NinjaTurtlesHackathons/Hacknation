"""Numerik der Domäne optscale: Optimierer (SGD, Momentum, Adam, Signum, Clipping, Muon, Shampoo), LR-Schedules,
Edge of Stability, μP-Hyperparameter-Transfer und Skalierungsgesetze in linearen/Random-Feature-Modellen.
Nur numpy/scipy. Alles deterministisch bei festem Seed. Ergebnisse sind numerisch (Gleitkomma)."""
import math
import numpy as np
from scipy import integrate

# ----------------------------------------------------------------------------------------------------------------
# 1. Skalierungsgesetze: lineares Modell mit Potenzgesetz-Spektrum
#    Kovarianz-Eigenwerte lambda_k = k^-a, Zielgewichte mit lambda_k * w_k^2 = k^-b (b > 1: endliche Varianz).
# ----------------------------------------------------------------------------------------------------------------

def _tail(b, M, a=0.0, t=0.0):
    """Restsumme sum_{k>M} k^-b exp(-2 k^-a t) als Integral ab M+1/2 (Mittelpunktregel), in u = ln x integriert."""
    if t == 0: return (M + 0.5) ** (1 - b) / (b - 1)
    f = lambda u: math.exp(u * (1 - b) - 2 * t * math.exp(-a * u))
    v, _ = integrate.quad(f, math.log(M + 0.5), np.inf, limit=400, epsabs=0, epsrel=1e-10)
    return v


def gf_loss(a, b, t, M=100_000, tail=True):
    """Populationsverlust des Gradientenflusses ab w=0 nach Zeit t: L(t) = 1/2 sum_k k^-b exp(-2 k^-a t)."""
    k = np.arange(1, M + 1, dtype=float)
    s = 0.5 * np.sum(k ** -b * np.exp(-2 * k ** -a * t))
    if tail: s += 0.5 * _tail(b, M, a, t)
    return float(s)


def param_loss(a, b, P, M=100_000, tail=True):
    """Approximationsfehler mit den ersten P Eigenrichtungen und unendlich vielen Daten: 1/2 sum_{k>P} k^-b."""
    P = int(P); k = np.arange(P + 1, max(M, P + 1) + 1, dtype=float)
    s = 0.5 * np.sum(k ** -b)
    if tail: s += 0.5 * _tail(b, max(M, P + 1))
    return float(s)


def pt_loss(a, b, P, t, M=100_000):
    """Modell mit P Merkmalen, Gradientenfluss für Zeit t: gelernter Teil + nicht darstellbarer Rest."""
    P = int(P); k = np.arange(1, P + 1, dtype=float)
    return float(0.5 * np.sum(k ** -b * np.exp(-2 * k ** -a * t)) + param_loss(a, b, P, M))


def compute_opt(a, b, C, M=100_000, nP=120):
    """Rechenoptimaler Verlust bei Budget C = P * t: min_P L(P, C/P) über ein log-Gitter in P."""
    Ps = np.unique(np.round(np.logspace(0, math.log10(min(C, M)), nP)).astype(int))
    vals = [pt_loss(a, b, P, C / P, M) for P in Ps]
    j = int(np.argmin(vals))
    return {"C": float(C), "L": float(vals[j]), "P_opt": int(Ps[j]), "t_opt": float(C / Ps[j])}


def ridge_risk(a, b, N, ridge=0.0, noise=0.0, M=2000, seed=0):
    """Ridge-Regression mit N Stichproben x ~ N(0, Lambda). Rückgabe: Exzess-Risiko 1/2 (w_hat - w)^T Lambda (w_hat - w)."""
    rng = np.random.default_rng(seed); k = np.arange(1, M + 1, dtype=float)
    lam = k ** -a; w = rng.choice([-1, 1], M) * np.sqrt(k ** -b / lam)
    X = rng.standard_normal((N, M)) * np.sqrt(lam); y = X @ w + noise * rng.standard_normal(N)
    K = X @ X.T
    alpha = np.linalg.lstsq(K + ridge * N * np.eye(N), y, rcond=None)[0] if ridge > 0 else np.linalg.pinv(K, rcond=1e-12) @ y
    d = X.T @ alpha - w
    return float(0.5 * np.sum(lam * d * d))


def rf_risk(a, b, P, M=2000, seed=0):
    """Lineares Random-Feature-Modell f(x) = v^T F x mit Gauß-Projektion F (P x M), unendlich viele Daten:
    optimales v, Rückgabe des Populationsverlusts."""
    rng = np.random.default_rng(seed); k = np.arange(1, M + 1, dtype=float)
    lam = k ** -a; w = rng.choice([-1, 1], M) * np.sqrt(k ** -b / lam)
    F = rng.standard_normal((P, M)) / math.sqrt(M)
    A = (F * lam) @ F.T; rhs = (F * lam) @ w
    v = np.linalg.lstsq(A, rhs, rcond=None)[0]
    d = F.T @ v - w
    return float(0.5 * np.sum(lam * d * d))


def slope(xs, ys):
    """Exponent e im Fit y ~ x^-e (kleinste Quadrate in log-log)."""
    xs, ys = np.log(np.asarray(xs, float)), np.log(np.asarray(ys, float))
    return float(-np.polyfit(xs, ys, 1)[0])


# ----------------------------------------------------------------------------------------------------------------
# 2. Optimierer auf Matrix-Parametern
# ----------------------------------------------------------------------------------------------------------------

def newton_schulz(G, steps=5):
    """Näherung von msign(G) = U V^T (Muon, quintische Iteration)."""
    a, b, c = 3.4445, -4.7750, 2.0315
    X = G / (np.linalg.norm(G) + 1e-7); tr = X.shape[0] > X.shape[1]
    if tr: X = X.T
    for _ in range(steps):
        A = X @ X.T; X = a * X + (b * A + c * A @ A) @ X
    return X.T if tr else X


def _inv_root(S, p, eps):
    e, V = np.linalg.eigh(S); e = np.maximum(e, 0) + eps
    return (V * e ** (-1.0 / p)) @ V.T


OPTIMIZERS = ("sgd", "momentum", "adam", "signum", "clip_sgd", "muon", "shampoo")


class Opt:
    def __init__(self, name, shapes):
        if name not in OPTIMIZERS: raise ValueError(f"unbekannter Optimierer {name}; erlaubt: {OPTIMIZERS}")
        self.name = name; self.t = 0
        self.m = [np.zeros(s) for s in shapes]; self.v = [np.zeros(s) for s in shapes]
        self.L = [np.zeros((s[0], s[0])) for s in shapes]; self.R = [np.zeros((s[1], s[1])) for s in shapes]

    def step(self, params, grads, lr):
        self.t += 1; n = self.name
        if n == "clip_sgd":
            g = math.sqrt(sum(float(np.sum(G * G)) for G in grads)); c = min(1.0, 1.0 / (g + 1e-12))
        for i, (W, G) in enumerate(zip(params, grads)):
            if n == "sgd": W -= lr * G
            elif n == "clip_sgd": W -= lr * c * G
            elif n == "momentum":
                self.m[i] = 0.9 * self.m[i] + G; W -= lr * self.m[i]
            elif n == "signum":
                self.m[i] = 0.9 * self.m[i] + 0.1 * G; W -= lr * np.sign(self.m[i])
            elif n == "adam":
                self.m[i] = 0.9 * self.m[i] + 0.1 * G; self.v[i] = 0.999 * self.v[i] + 0.001 * G * G
                mh = self.m[i] / (1 - 0.9 ** self.t); vh = self.v[i] / (1 - 0.999 ** self.t)
                W -= lr * mh / (np.sqrt(vh) + 1e-8)
            elif n == "muon":
                self.m[i] = 0.95 * self.m[i] + G; U = newton_schulz(G + 0.95 * self.m[i])
                W -= lr * math.sqrt(max(1.0, W.shape[0] / W.shape[1])) * U
            elif n == "shampoo":
                self.L[i] += G @ G.T; self.R[i] += G.T @ G
                W -= lr * _inv_root(self.L[i], 4, 1e-6) @ G @ _inv_root(self.R[i], 4, 1e-6)


def lr_at(schedule, lr, s, steps, warmup=0.0):
    """Lernrate im Schritt s (0-basiert). const | cosine | linear | wsd (konstant, letzte 20 % linear auf 0)."""
    w = int(warmup * steps)
    if s < w: return lr * (s + 1) / w
    u = (s - w) / max(1, steps - w)
    if schedule == "const": return lr
    if schedule == "cosine": return lr * 0.5 * (1 + math.cos(math.pi * u))
    if schedule == "linear": return lr * (1 - u)
    if schedule == "wsd": return lr if u < 0.8 else lr * (1 - u) / 0.2
    raise ValueError(f"unbekannter Schedule {schedule}; erlaubt: const, cosine, linear, wsd")


def _noise(rng, shape, nz):
    if not nz or float(nz.get("sigma", 0)) == 0: return 0.0
    s = float(nz["sigma"]); typ = nz.get("typ", "gauss")
    if typ == "gauss": return s * rng.standard_normal(shape)
    if typ == "student":
        df = float(nz.get("df", 3)); z = rng.standard_t(df, shape)
        return s * (z * math.sqrt((df - 2) / df) if df > 2 else z)
    raise ValueError(f"unbekannter Rauschtyp {typ}; erlaubt: gauss, student")


# --- Problem A: Matrix-Quadratik f(W) = 1/2 tr((W-W*)^T H_L (W-W*) H_R), Gradientenrauschen ~ H_L^1/2 Z H_R^1/2
class Quadratic:
    def __init__(self, cfg, seed):
        m, n = int(cfg.get("m", 32)), int(cfg.get("n", 32))
        if not (2 <= m <= 64 and 2 <= n <= 64): raise ValueError("m, n in [2, 64]")
        rng = np.random.default_rng(10_000 + seed)
        dl = np.arange(1, m + 1, dtype=float) ** -float(cfg.get("a_L", 1.0)); dr = np.arange(1, n + 1, dtype=float) ** -float(cfg.get("a_R", 1.0))
        if cfg.get("rotiert", True):
            QL = np.linalg.qr(rng.standard_normal((m, m)))[0]; QR = np.linalg.qr(rng.standard_normal((n, n)))[0]
        else: QL, QR = np.eye(m), np.eye(n)
        self.HL, self.HR = (QL * dl) @ QL.T, (QR * dr) @ QR.T
        self.SL, self.SR = (QL * np.sqrt(dl)) @ QL.T, (QR * np.sqrt(dr)) @ QR.T
        self.Ws = rng.standard_normal((m, n)); self.noise = cfg.get("noise"); self.shapes = [(m, n)]
        self.params = [np.zeros((m, n))]; self.L0 = self.loss()

    def loss(self):
        D = self.params[0] - self.Ws; return float(0.5 * np.sum(D * (self.HL @ D @ self.HR)))

    def grads(self, rng):
        D = self.params[0] - self.Ws; G = self.HL @ D @ self.HR
        Z = _noise(rng, D.shape, self.noise)
        return [G + (self.SL @ Z @ self.SR if not np.isscalar(Z) else 0.0)]


# --- Problem B: nicht-konvex, Lehrer-Schüler-MLP (tanh, ohne Bias), Minibatch-SGD-Rauschen
def mlp_forward(Ws, X, act="tanh"):
    hs = [X]; h = X
    for W in Ws[:-1]:
        z = h @ W.T; h = np.tanh(z) if act == "tanh" else np.maximum(z, 0); hs.append(h)
    return h @ Ws[-1].T, hs


def mlp_grads(Ws, X, y, act="tanh", mult=None):
    """MSE 1/2 mean((f - y)^2). mult: Vorwärts-Multiplikatoren je Schicht (μP-Varianten), Standard 1."""
    mult = mult or [1.0] * len(Ws); hs = [X]; h = X; zs = []
    for W, c in zip(Ws[:-1], mult[:-1]):
        z = c * h @ W.T; zs.append(z); h = np.tanh(z) if act == "tanh" else np.maximum(z, 0); hs.append(h)
    f = mult[-1] * h @ Ws[-1].T; r = (f - y) / len(X); gs = [None] * len(Ws)
    d = r * mult[-1]; gs[-1] = d.T @ hs[-1]; d = d @ Ws[-1]
    for i in range(len(Ws) - 2, -1, -1):
        d = d * ((1 - np.tanh(zs[i]) ** 2) if act == "tanh" else (zs[i] > 0)) * mult[i]
        gs[i] = d.T @ hs[i]; d = d @ Ws[i]
    return gs, float(0.5 * np.mean((f - y) ** 2))


class MLPProblem:
    def __init__(self, cfg, seed):
        rng = np.random.default_rng(20_000 + seed); d = int(cfg.get("d", 16)); h = int(cfg.get("breite", 64))
        if not (4 <= h <= 256): raise ValueError("breite in [4, 256]")
        self.T = [rng.standard_normal((8, d)) / math.sqrt(d), rng.standard_normal((1, 8)) / math.sqrt(8) * 2]
        self.d, self.batch = d, int(cfg.get("batch", 64)); self.noise = cfg.get("noise")
        self.Xte = rng.standard_normal((2048, d)); self.yte = mlp_forward(self.T, self.Xte)[0]
        self.params = [rng.standard_normal((h, d)) / math.sqrt(d), rng.standard_normal((1, h)) / math.sqrt(h)]
        self.shapes = [W.shape for W in self.params]; self.L0 = self.loss()

    def loss(self):
        return float(0.5 * np.mean((mlp_forward(self.params, self.Xte)[0] - self.yte) ** 2))

    def grads(self, rng):
        X = rng.standard_normal((self.batch, self.d)); y = mlp_forward(self.T, X)[0]
        z = _noise(rng, y.shape, self.noise); y = y + z
        return mlp_grads(self.params, X, y)[0]


def make_problem(cfg, seed):
    typ = cfg.get("typ", "quadratisch")
    if typ == "quadratisch": return Quadratic(cfg, seed)
    if typ == "mlp": return MLPProblem(cfg, seed)
    raise ValueError(f"unbekanntes Problem {typ}; erlaubt: quadratisch, mlp")


DIV = 1e3   # relativer Verlust, ab dem ein Lauf als divergiert gilt (und mit diesem Wert gewertet wird)


def train(problem, optimizer, lr, steps, seed, schedule="const", warmup=0.0, curve_points=0):
    """Rückgabe: relativer Endverlust (Mittel der letzten 5 % der Schritte, Populationsverlust / Anfangsverlust)."""
    steps = int(steps)
    if not (10 <= steps <= 3000): raise ValueError("steps in [10, 3000]")
    P = make_problem(problem, seed); O = Opt(optimizer, P.shapes); rng = np.random.default_rng(30_000 + seed)
    tail0 = steps - max(1, steps // 20); acc = []; curve = []; every = max(1, steps // curve_points) if curve_points else 0
    with np.errstate(all="ignore"):
        for s in range(steps):
            O.step(P.params, P.grads(rng), lr_at(schedule, lr, s, steps, warmup))
            if s >= tail0 or (every and s % every == 0):
                L = P.loss() / P.L0
                if not np.isfinite(L) or L > DIV:
                    return {"rel_verlust": DIV, "divergiert": True, "kurve": curve}
                if s >= tail0: acc.append(L)
                if every and s % every == 0: curve.append([s, float(L)])
    return {"rel_verlust": float(np.mean(acc)), "divergiert": False, "kurve": curve}


# ----------------------------------------------------------------------------------------------------------------
# 3. Edge of Stability: Voll-Batch-GD auf Lehrer-Schüler-MLP, Schärfe = größter Hesse-Eigenwert
# ----------------------------------------------------------------------------------------------------------------

class EoSTask:
    def __init__(self, width, seed, n=200, d=8):
        rng = np.random.default_rng(40_000 + seed)
        T = [rng.standard_normal((6, d)) / math.sqrt(d), rng.standard_normal((1, 6))]
        self.X = rng.standard_normal((n, d)); self.y = mlp_forward(T, self.X)[0]
        self.Ws = [rng.standard_normal((width, d)) / math.sqrt(d), rng.standard_normal((1, width)) / math.sqrt(width)]
        self.shapes = [W.shape for W in self.Ws]; self.sizes = [W.size for W in self.Ws]

    def flat(self): return np.concatenate([W.ravel() for W in self.Ws])

    def unflat(self, v):
        out, i = [], 0
        for s, n in zip(self.shapes, self.sizes): out.append(v[i:i + n].reshape(s)); i += n
        return out

    def grad(self, v):
        gs, L = mlp_grads(self.unflat(v), self.X, self.y); return np.concatenate([g.ravel() for g in gs]), L

    def hvp(self, v, u, h=1e-5):
        return (self.grad(v + h * u)[0] - self.grad(v - h * u)[0]) / (2 * h)

    def sharp_power(self, v, iters=30, seed=0):
        u = np.random.default_rng(seed).standard_normal(v.size); u /= np.linalg.norm(u); lam = 0.0
        for _ in range(iters):
            w = self.hvp(v, u); lam = float(u @ w); u = w / (np.linalg.norm(w) + 1e-30)
        return lam

    def sharp_full(self, v, h=1e-5):
        n = v.size; H = np.empty((n, n)); E = np.eye(n)
        for i in range(n): H[:, i] = self.hvp(v, E[i], h)
        return float(np.linalg.eigvalsh(0.5 * (H + H.T))[-1])


def gd_eos(width, lr, steps, seed, n_checks=10, full=False):
    width, steps = int(width), int(steps)
    if not (4 <= width <= 64): raise ValueError("width in [4, 64]")
    if not (10 <= steps <= 4000): raise ValueError("steps in [10, 4000]")
    T = EoSTask(width, seed); v = T.flat(); out = []
    checks = set(np.linspace(0, steps, n_checks + 1).astype(int)[1:])
    with np.errstate(all="ignore"):
        for s in range(1, steps + 1):
            g, L = T.grad(v); v = v - lr * g
            if not np.isfinite(L) or L > 1e6: return {"divergiert": True, "verlauf": out, "zwei_durch_lr": 2 / lr}
            if s in checks:
                S = T.sharp_full(v) if full else T.sharp_power(v, seed=s)
                out.append({"schritt": s, "verlust": float(T.grad(v)[1]), "schaerfe": S, "lr_mal_schaerfe_halbe": lr * S / 2})
    return {"divergiert": False, "verlauf": out, "zwei_durch_lr": 2 / lr}


# ----------------------------------------------------------------------------------------------------------------
# 4. μP: 3-Schicht-ReLU-MLP, Standard- (SP) vs. Maximal-Update-Parametrisierung (μP), Basisbreite 64
# ----------------------------------------------------------------------------------------------------------------
BASE = 64


def mup_run(param, optimizer, width, lr, steps, seed, d=16, batch=64):
    """Online-Training (frische Stichproben) auf einem festen Lehrer; Rückgabe Testverlust am Ende.
    SP: Init-Varianz 1/fan_in, eine Lernrate. μP (Tabelle 3 in Yang et al. 2022, mit Basisbreite 64, identisch zu SP bei Breite 64):
      Adam: Eingang lr, versteckt lr*64/n, Ausgang lr*64/n, Ausgangs-Init-Varianz (1/n)*(64/n).
      SGD:  Eingang lr*n/64, versteckt lr, Ausgang lr*64/n, Ausgangs-Init-Varianz (1/n)*(64/n)."""
    n = int(width)
    if not (16 <= n <= 1024): raise ValueError("width in [16, 1024]")
    if param not in ("sp", "mup") or optimizer not in ("adam", "sgd"): raise ValueError("param sp|mup, optimizer adam|sgd")
    trng = np.random.default_rng(50_000)                                   # Lehrer: fest für alle Läufe
    T = [trng.standard_normal((32, d)) / math.sqrt(d), trng.standard_normal((32, 32)) / math.sqrt(32), trng.standard_normal((1, 32)) / math.sqrt(32)]
    rng = np.random.default_rng(60_000 + seed); r = n / BASE
    out_var = (1 / n) * (1 / r if param == "mup" else 1.0)
    Ws = [(rng.standard_normal((n, d)) / math.sqrt(d)).astype(np.float32), (rng.standard_normal((n, n)) / math.sqrt(n)).astype(np.float32),
          (rng.standard_normal((1, n)) * math.sqrt(out_var)).astype(np.float32)]
    if param == "sp": lrs = [lr, lr, lr]
    elif optimizer == "adam": lrs = [lr, lr / r, lr / r]
    else: lrs = [lr * r, lr, lr / r]
    O = [Opt(optimizer if optimizer == "adam" else "sgd", [W.shape]) for W in Ws]
    Xte = np.random.default_rng(50_001).standard_normal((1024, d)).astype(np.float32); yte = mlp_forward(T, Xte, "relu")[0]
    with np.errstate(all="ignore"):
        for s in range(int(steps)):
            X = rng.standard_normal((batch, d)).astype(np.float32); y = mlp_forward(T, X, "relu")[0]
            gs, L = mlp_grads(Ws, X, y, "relu")
            if not np.isfinite(L) or L > 1e4: return float("inf")
            for o, W, g, l in zip(O, Ws, gs, lrs): o.step([W], [g.astype(np.float32)], l)
        L = float(0.5 * np.mean((mlp_forward(Ws, Xte, "relu")[0] - yte) ** 2))
    return L if np.isfinite(L) else float("inf")


def best_log2_lr(param, optimizer, width, log2s, steps, seeds):
    """Mittlerer Testverlust (geometrisch über Seeds) je log2-Lernrate; Rückgabe argmin und Tabelle."""
    tab = {}
    for e in log2s:
        Ls = [min(mup_run(param, optimizer, width, 2.0 ** e, steps, s), 1e3) for s in seeds]
        tab[int(e)] = float(np.exp(np.mean(np.log(Ls))))
    return min(tab, key=tab.get), tab
