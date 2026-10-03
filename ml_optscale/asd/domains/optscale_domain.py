"""Domäne optscale: Optimierung und Skalierungsgesetze (Adam, Muon, Shampoo, LR-Schedules, Edge of Stability, μP,
Potenzgesetze aus Daten-Spektren). Erzeugt mit `python -m asd.new_domain optscale`, Prüfer zuerst.

Prüfer-Prinzipien:
 - Toleranzen, Lernraten-Gitter, Seeds, Auflösungen und Schwellen stehen fest im Prüfer, nie in der Behauptung.
 - Unabhängige Nachrechnung: andere Seeds als die Experimente, eigenes LR-Tuning, eigene Auflösung (zwei Fenster),
   exakte Arithmetik wo möglich (Stabilität quadratischer Iterationen über rationale Zahlen).
 - Ehrliche Stufen: Fits und Simulationen sind `observed` (numerisch), Seed-Vergleiche mit Permutationstest `statistical`,
   exakte rationale Zertifikate `computed_rigorous`.
"""
import json
from fractions import Fraction
import numpy as np
from .base import Domain
from . import optscale as O
from ..stats import perm_test

# ---------------------------------------------------------------- feste Prüfer-Parameter (nie aus der Behauptung)
TOL_DET = 0.03          # Exponent, deterministische Kurven (gf, param, compute)
TOL_MC = 0.10           # Exponent, Monte-Carlo-Kurven (ridge, rf)
LR_GRID = list(range(-16, 5))                     # log2-Lernraten für das Tuning im Vergleich
TUNE_SEEDS, EVAL_SEEDS = (100, 101, 102), tuple(range(200, 210))
P_MAX, EFFEKT = 0.01, 0.9                          # Vergleich: p < 0,01 und geometr. Verlust-Verhältnis < 0,9
EOS_SEEDS, EOS_BAND, STABIL_MAX = (300, 301, 302, 303, 304), (0.85, 1.25), 0.8
MUP_GRID = {"adam": list(range(-14, -1)), "sgd": list(range(-10, 3))}
MUP_SEEDS, MUP_STEPS = (400, 401), 300

_MEMO = {}


def _memo(p, fn):
    k = json.dumps(p, sort_keys=True)
    if k not in _MEMO: _MEMO[k] = fn(p)
    return _MEMO[k]


def _num(x, lo, hi, name):
    x = float(x)
    if not (lo <= x <= hi): raise ValueError(f"{name}={x} außerhalb des Prüfbereichs [{lo}, {hi}]")
    return x


# ---------------------------------------------------------------- Prüfung 1: Skalierungsexponent
def _curve(kurve, a, b, ridge, noise, window):
    """Unabhängige Nachrechnung in zwei Fenstern; window 0/1. Gibt (xs, ys) zurück."""
    if kurve == "gf":
        lo, hi = [(3, 5), (4, 6)][window]; xs = np.logspace(lo, hi, 9)
        return xs, [O.gf_loss(a, b, t, M=1_000_000) for t in xs]
    if kurve == "param":
        lo, hi = [(3, 5), (4, 6)][window]; xs = np.unique(np.logspace(lo, hi, 9).astype(int))
        return xs, [O.param_loss(a, b, P, M=1_000_000) for P in xs]
    if kurve == "compute":
        lo, hi = [(5, 7), (6, 8)][window]; xs = np.logspace(lo, hi, 7)
        return xs, [O.compute_opt(a, b, C, M=1_000_000, nP=200)["L"] for C in xs]
    if kurve == "ridge":
        M, xs = [(3000, [64, 128, 256, 512, 1024]), (4000, [128, 256, 512, 1024, 2048])][window]
        return xs, [np.mean([O.ridge_risk(a, b, N, ridge, noise, M, seed=500 + s) for s in range(8)]) for N in xs]
    if kurve == "rf":
        M, xs = [(3000, [32, 64, 128, 256, 512]), (4000, [64, 128, 256, 512, 1024])][window]
        return xs, [np.mean([O.rf_risk(a, b, P, M, seed=600 + s) for s in range(8)]) for P in xs]
    raise ValueError(f"unbekannte kurve {kurve}; erlaubt: gf, param, compute, ridge, rf")


def check_exponent(p):
    kurve = p.get("kurve"); a = _num(p["a"], 0.3, 3, "a"); b = _num(p["b"], 1.1, 4, "b"); e = float(p["exponent"])
    ridge = _num(p.get("ridge", 0.0), 0, 1, "ridge"); noise = _num(p.get("noise", 0.0), 0, 1, "noise")
    tol = TOL_MC if kurve in ("ridge", "rf") else TOL_DET
    fits = []
    for w in (0, 1):
        xs, ys = _curve(kurve, a, b, ridge, noise, w)
        if not np.all(np.isfinite(ys)) or np.any(np.asarray(ys) <= 0): return False, f"Kurve nicht auswertbar (Fenster {w})", {}
        fits.append(O.slope(xs, ys))
    ok = all(abs(f - e) <= tol for f in fits)
    return ok, (f"Prüfer-Fit {kurve} (a={a}, b={b}" + (f", ridge={ridge}, noise={noise}" if kurve == "ridge" else "") +
                f"): Exponent {fits[0]:.4f} (Fenster 1) und {fits[1]:.4f} (Fenster 2), behauptet {e}, feste Toleranz {tol}"), {"fits": fits}


# ---------------------------------------------------------------- Prüfung 2: Optimierer-/Schedule-Vergleich
def _problem(cfg):
    cfg = dict(cfg or {}); typ = cfg.get("typ", "quadratisch")
    if typ not in ("quadratisch", "mlp"): raise ValueError(f"unbekanntes Problem {typ}")
    nz = cfg.get("noise")
    if nz:
        _num(nz.get("sigma", 0), 0, 1, "noise.sigma")
        if nz.get("typ", "gauss") == "student": _num(nz.get("df", 3), 1, 30, "noise.df")
    for k in ("a_L", "a_R"):
        if k in cfg: _num(cfg[k], 0, 3, k)
    return cfg


def _arm(spec):
    o = spec.get("optimizer"); s = spec.get("schedule", "const"); w = _num(spec.get("warmup", 0.0), 0, 0.2, "warmup")
    if o not in O.OPTIMIZERS: raise ValueError(f"unbekannter Optimierer {o}")
    if s not in ("const", "cosine", "linear", "wsd"): raise ValueError(f"unbekannter Schedule {s}")
    return o, s, w


def _tune(prob, arm, steps):
    o, s, w = arm; tab = {}
    for e in LR_GRID:
        tab[e] = float(np.mean([np.log(O.train(prob, o, 2.0 ** e, steps, sd, s, w)["rel_verlust"]) for sd in TUNE_SEEDS]))
    return min(tab, key=tab.get), tab


def check_vergleich(p):
    prob = _problem(p.get("problem")); steps = int(p.get("steps", 500))
    if not (50 <= steps <= 2000): raise ValueError("steps in [50, 2000]")
    A, B = _arm(p["a"]), _arm(p["b"])
    ea, _ = _tune(prob, A, steps); eb, _ = _tune(prob, B, steps)
    edge = [n for n, e in (("a", ea), ("b", eb)) if e in (LR_GRID[0], LR_GRID[-1])]
    if edge: return False, f"Optimum der Lernrate für {edge} am Rand des Prüfer-Gitters 2^{LR_GRID[0]}..2^{LR_GRID[-1]}: nicht entscheidbar", {}
    la = [np.log(O.train(prob, A[0], 2.0 ** ea, steps, sd, A[1], A[2])["rel_verlust"]) for sd in EVAL_SEEDS]
    lb = [np.log(O.train(prob, B[0], 2.0 ** eb, steps, sd, B[1], B[2])["rel_verlust"]) for sd in EVAL_SEEDS]
    pv = perm_test(la, lb); ratio = float(np.exp(np.mean(la) - np.mean(lb)))
    ok = pv < P_MAX and ratio < EFFEKT
    na, nb = "/".join(A[:2]), "/".join(B[:2])
    return ok, (f"Prüfer: {na} (beste LR 2^{ea}) vs {nb} (beste LR 2^{eb}), je eigenes Tuning auf Seeds {TUNE_SEEDS}, Bewertung auf "
                f"{len(EVAL_SEEDS)} frischen Seeds: geometr. Mittel rel. Endverlust {np.exp(np.mean(la)):.3e} vs {np.exp(np.mean(lb)):.3e}, "
                f"Verhältnis {ratio:.3f} (Schwelle < {EFFEKT}), gepaarter Permutationstest p = {pv:.4f} (Schwelle < {P_MAX})"), \
        {"lr_a": ea, "lr_b": eb, "ratio": ratio, "p": pv}


# ---------------------------------------------------------------- Prüfung 3: Edge of Stability
def check_eos(p):
    w = int(p["width"]); lr = _num(p["lr"], 1e-3, 10, "lr"); steps = int(p["steps"]); reg = p.get("regime")
    if reg not in ("eos", "stabil"): raise ValueError("regime eos|stabil")
    if not (4 <= w <= 64) or not (500 <= steps <= 4000): raise ValueError("width in [4, 64], steps in [500, 4000]")
    rows = []
    for sd in EOS_SEEDS:
        r = O.gd_eos(w, lr, steps, sd, n_checks=5, full=True)
        rows.append(None if r["divergiert"] or len(r["verlauf"]) < 2 else [x["lr_mal_schaerfe_halbe"] for x in r["verlauf"][-2:]])
    if reg == "eos": hit = [x is not None and all(EOS_BAND[0] <= v <= EOS_BAND[1] for v in x) for x in rows]
    else: hit = [x is not None and all(v < STABIL_MAX for v in x) for x in rows]
    ok = sum(hit) >= 4
    shown = ", ".join("div." if x is None else "/".join(f"{v:.3f}" for v in x) for x in rows)
    return ok, (f"Prüfer: voller Hesse-Eigenwert (Finite Differenzen) bei 80 % und 100 % der Schritte, 5 frische Seeds; "
                f"lr*lambda_max/2 = [{shown}]; Kriterium {reg}: " + (f"in {list(EOS_BAND)}" if reg == "eos" else f"< {STABIL_MAX}") +
                f" an beiden Punkten in >= 4/5 Seeds, erfüllt in {sum(hit)}/5"), {"werte": rows}


# ---------------------------------------------------------------- Prüfung 4: μP-Lernraten-Transfer
def check_transfer(p):
    par, opt = p.get("param"), p.get("optimizer"); want = p.get("transfer")
    if par not in ("sp", "mup") or opt not in ("adam", "sgd") or not isinstance(want, bool): raise ValueError("param sp|mup, optimizer adam|sgd, transfer bool")
    ws = sorted({int(x) for x in p["widths"]})
    if not (3 <= len(ws) <= 4 and ws[0] >= 32 and ws[-1] <= 512 and ws[-1] / ws[0] >= 8): raise ValueError("3-4 Breiten in [32, 512], max/min >= 8")
    grid = MUP_GRID[opt]; best = {}
    for w in ws:
        e, _ = O.best_log2_lr(par, opt, w, grid, MUP_STEPS, MUP_SEEDS)
        if e in (grid[0], grid[-1]): return False, f"optimale LR bei Breite {w} am Gitterrand: nicht entscheidbar", {}
        best[w] = e
    shift = best[ws[-1]] - best[ws[0]]; spread = max(best.values()) - min(best.values())
    ok = (abs(shift) <= 1 and spread <= 1) if want else abs(shift) >= 2
    return ok, (f"Prüfer: optimale log2-LR je Breite {best} ({par}, {opt}, {MUP_STEPS} Schritte, Seeds {MUP_SEEDS}, Gitter 2^{grid[0]}..2^{grid[-1]}); "
                f"Verschiebung kleinste->größte Breite {shift:+d} Oktaven, Spannweite {spread}; Kriterium " +
                ("Transfer: |Verschiebung| <= 1 und Spannweite <= 1" if want else "kein Transfer: |Verschiebung| >= 2")), {"best": best}


# ---------------------------------------------------------------- Prüfung 5: exakte Stabilität quadratischer Iterationen
def _pd(M):
    """Exakt: positiv definit über führende Hauptminoren (Sylvester), Bruch-Arithmetik."""
    import sympy as sp
    A = sp.Matrix(M)
    return all(A[:k, :k].det() > 0 for k in range(1, A.shape[0] + 1))


def check_stabil(p):
    H = [[Fraction(str(x)) for x in row] for row in p["H"]]; n = len(H)
    if not (1 <= n <= 6) or any(len(r) != n for r in H): raise ValueError("H quadratisch, Dimension 1..6")
    if any(H[i][j] != H[j][i] for i in range(n) for j in range(n)): return False, "H nicht symmetrisch", {}
    lr = Fraction(str(p["lr"])); beta = Fraction(str(p.get("beta", 0))); meth = p.get("methode", "gd")
    if meth not in ("gd", "heavy_ball") or lr <= 0: raise ValueError("methode gd|heavy_ball, lr > 0")
    if meth == "gd": beta = Fraction(0)
    import sympy as sp
    Hs = [[sp.Rational(x.numerator, x.denominator) for x in r] for r in H]
    c = 2 * (1 + beta) / lr; cs = sp.Rational(c.numerator, c.denominator)
    upper = [[(cs if i == j else 0) - Hs[i][j] for j in range(n)] for i in range(n)]
    stabil = abs(beta) < 1 and _pd(Hs) and _pd(upper)
    ok = stabil == bool(p.get("stabil"))
    return ok, (f"Exakt (rationale Arithmetik, Sylvester-Kriterium): Iteration {meth} mit lr={lr}, beta={beta} ist "
                f"{'stabil' if stabil else 'nicht stabil'} (Bedingung: |beta|<1, H>0 und H < 2(1+beta)/lr = {c}); behauptet stabil={p.get('stabil')}"), {}


CHECKS = {"exponent": check_exponent, "vergleich": check_vergleich, "eos": check_eos, "lr_transfer": check_transfer, "stabilitaet": check_stabil}
LEVEL = {"exponent": "observed", "vergleich": "statistical", "eos": "observed", "lr_transfer": "observed", "stabilitaet": "computed_rigorous"}


class OptScaleDomain(Domain):
    name = "optscale"
    recherche_ziel = ("Theorie der Optimierung und der Skalierungsgesetze im Deep Learning: Konvergenz von Adam, Muon, Shampoo und "
                      "Lernraten-Schedules unter Nicht-Konvexität, heavy-tailed Gradientenrauschen und Edge of Stability; "
                      "Hyperparameter-Transfer mit μP (Maximal Update Parametrization, Tensor Programs); Ursprung von Potenzgesetzen "
                      "und ihrer Exponenten aus Daten-Spektren, Kernel- und Random-Feature-Modellen.")
    recherche_sperre = []
    kontext = (
        "Forschungsgebiet: Warum funktionieren moderne Optimierer und Lernraten-Schedules, wann überträgt sich die Lernrate über die "
        "Modellbreite, und woher kommen Skalierungsgesetze mit ihren Exponenten? Das Labor hat vier Modellwelten, alle numerisch (numpy):\n"
        "(1) Lineares Modell mit Potenzgesetz-Spektrum: Merkmals-Kovarianz mit Eigenwerten lambda_k = k^-a, Zielfunktion mit "
        "Spektralanteilen lambda_k w_k^2 = k^-b (b > 1). Größen: Verlust des Gradientenflusses nach Zeit t; Verlust mit nur P "
        "Merkmalen; rechenoptimaler Verlust bei Budget C = P*t; Ridge-Regression mit N Stichproben; lineares Random-Feature-Modell "
        "mit P Gauß-Projektionen. Ein Skalierungsexponent e bedeutet Verlust ~ x^-e.\n"
        "(2) Optimierer sgd, momentum (0,9), adam (0,9/0,999), signum (Vorzeichen des Momentums), clip_sgd (Gradientennorm auf 1 "
        "beschnitten), muon (Momentum 0,95 + Newton-Schulz-Orthogonalisierung), shampoo (Kronecker-Vorkonditionierer L^-1/4 G R^-1/4). "
        "Probleme: 'quadratisch' = schlecht konditionierte Matrix-Quadratik 32x32 mit Kronecker-Krümmung (Spektren i^-a_L, j^-a_R, "
        "wahlweise rotiert), additives Gradientenrauschen gauss oder student (heavy-tailed, df Freiheitsgrade, df <= 2: unendliche "
        "Varianz); 'mlp' = nicht-konvexes Lehrer-Schüler-Netz (tanh) mit Minibatch-Rauschen. Lernraten-Schedules: const, cosine, "
        "linear, wsd (konstant, letzte 20 % linear auf 0), optional Warmup. Metrik: relativer Endverlust (Verlust/Anfangsverlust).\n"
        "(3) Edge of Stability: Voll-Batch-Gradientenabstieg auf einem kleinen tanh-Netz; Schärfe = größter Hesse-Eigenwert lambda_max; "
        "Kenngröße lr*lambda_max/2.\n"
        "(4) μP gegen Standard-Parametrisierung (SP): 3-Schicht-ReLU-MLP, Breiten 32 bis 512, Adam oder SGD, Online-Training; "
        "bei Basisbreite 64 sind μP und SP identisch. Frage: Verschiebt sich die optimale Lernrate mit der Breite?\n"
        "Exakte Anker gibt es für quadratische Iterationen (Gradientenabstieg, Heavy-Ball) mit rationaler Krümmungsmatrix H.\n"
        "Behauptungen gelten nur, wenn ein unabhängiger Code-Prüfer sie nachrechnet (eigene Seeds, eigenes Lernraten-Tuning, eigene Auflösung).")
    primitive_doc = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}):
- gf_kurve {a, b, ts: [...], M?}: Verlust des Gradientenflusses L(t) (M Moden, Standard 1e5, Rest als Integral).
- param_kurve {a, b, Ps: [...]}: Verlust mit den ersten P Merkmalen (unendlich viele Daten).
- compute_kurve {a, b, Cs: [...]}: rechenoptimaler Verlust bei Budget C = P*t, mit optimalem P und t.
- ridge_kurve {a, b, Ns: [...], ridge?, noise?, seeds?}: Exzess-Risiko der Ridge-Regression (N <= 1024, M = 2000, Monte Carlo).
- rf_kurve {a, b, Ps: [...], seeds?}: Verlust des linearen Random-Feature-Modells (P <= 512, M = 2000, unendlich viele Daten).
- fit_exponent {xs: [...], ys: [...]}: Exponent e in y ~ x^-e (log-log-Fit).
- trainiere {problem: {typ: "quadratisch"|"mlp", rotiert?, a_L?, a_R?, noise?: {typ: "gauss"|"student", sigma, df?}}, optimizer, lr, steps (<= 2000), seed?, schedule?, warmup?}:
  relativer Endverlust, Divergenz-Flag, Verlaufskurve.
- lr_sweep {problem, optimizer, log2_lrs: [...], steps, seeds?: [...], schedule?, warmup?}: rel. Endverlust je Lernrate (geometrisches Mittel über Seeds), beste Lernrate.
- gd_schaerfe {width (4..64), lr, steps (<= 4000), seed?}: Voll-Batch-GD; Verlust und Schärfe lambda_max (Potenzmethode) an 10 Punkten, dazu 2/lr.
- mup_sweep {param: "sp"|"mup", optimizer: "adam"|"sgd", widths: [...] (<= 512), log2_lrs: [...], steps (<= 400), seeds?: [...]}: Testverlust je Breite und Lernrate, beste log2-LR je Breite.
- stabilitaet_numerisch {H: [[...]], lr, beta?}: Spektralradius der GD- bzw. Heavy-Ball-Iteration (numerisch)."""
    claim_doc = """Prüfungstypen (Toleranzen, Seeds, LR-Gitter und Schwellen legt der Prüfer fest):
- {"typ": "exponent", "kurve": "gf"|"param"|"compute"|"ridge"|"rf", "a": Zahl, "b": Zahl, "exponent": Zahl, "ridge"?: Zahl, "noise"?: Zahl}
  Der Prüfer rechnet die Kurve unabhängig in zwei Fenstern mit höherer Auflösung nach (a in [0,3; 3], b in [1,1; 4]); besteht, wenn beide
  Fits nahe am behaupteten Exponenten liegen.
- {"typ": "vergleich", "problem": {...}, "steps": Zahl, "a": {"optimizer": ..., "schedule"?: ..., "warmup"?: ...}, "b": {...}}
  Behauptung: a erreicht einen kleineren Endverlust als b. Der Prüfer tunt die Lernrate beider Arme selbst und vergleicht auf frischen Seeds
  (gepaarter Permutationstest, Mindest-Effekt).
- {"typ": "eos", "width": Zahl, "lr": Zahl, "steps": Zahl (500..4000), "regime": "eos"|"stabil"}
  eos: lr*lambda_max/2 liegt am Ende nahe 1 (Edge of Stability); stabil: deutlich unter 1. Prüfer: voller Hesse-Eigenwert, 5 frische Seeds.
- {"typ": "lr_transfer", "param": "sp"|"mup", "optimizer": "adam"|"sgd", "widths": [3-4 Breiten in 32..512, max/min >= 8], "transfer": true|false}
  transfer=true: die optimale Lernrate bleibt über die Breiten (fast) gleich; false: sie verschiebt sich deutlich. Prüfer tunt selbst.
- {"typ": "stabilitaet", "methode": "gd"|"heavy_ball", "H": [[rationale Zahlen als Strings, symmetrisch]], "lr": "p/q", "beta"?: "p/q", "stabil": true|false}
  Exakt: Konvergenz der Iteration auf f(x) = x^T H x / 2 (rationale Arithmetik, Zertifikat)."""

    def run_op(self, op, args):
        try:
            a = dict(args or {})
            if op == "gf_kurve": return {"ts": a["ts"], "L": [O.gf_loss(float(a["a"]), float(a["b"]), float(t), int(min(a.get("M", 100_000), 300_000))) for t in a["ts"][:30]], "hinweis": "numerisch"}
            if op == "param_kurve": return {"Ps": a["Ps"], "L": [O.param_loss(float(a["a"]), float(a["b"]), int(P)) for P in a["Ps"][:30]], "hinweis": "numerisch"}
            if op == "compute_kurve": return {"punkte": [O.compute_opt(float(a["a"]), float(a["b"]), float(C)) for C in a["Cs"][:15] if float(C) <= 1e8], "hinweis": "numerisch"}
            if op == "ridge_kurve":
                Ns = [int(N) for N in a["Ns"][:8] if int(N) <= 1024]; S = int(min(a.get("seeds", 4), 8))
                return {"Ns": Ns, "risiko": [float(np.mean([O.ridge_risk(float(a["a"]), float(a["b"]), N, float(a.get("ridge", 0)), float(a.get("noise", 0)), 2000, seed=s) for s in range(S)])) for N in Ns], "hinweis": "Monte Carlo"}
            if op == "rf_kurve":
                Ps = [int(P) for P in a["Ps"][:8] if int(P) <= 512]; S = int(min(a.get("seeds", 4), 8))
                return {"Ps": Ps, "verlust": [float(np.mean([O.rf_risk(float(a["a"]), float(a["b"]), P, 2000, seed=s) for s in range(S)])) for P in Ps], "hinweis": "Monte Carlo"}
            if op == "fit_exponent": return {"exponent": O.slope(a["xs"], a["ys"])}
            if op == "trainiere":
                r = O.train(a["problem"], a["optimizer"], float(a["lr"]), int(min(a.get("steps", 500), 2000)), int(a.get("seed", 0)),
                            a.get("schedule", "const"), float(a.get("warmup", 0)), curve_points=10)
                return r
            if op == "lr_sweep":
                seeds = [int(s) for s in a.get("seeds", [0, 1])][:3]; steps = int(min(a.get("steps", 500), 2000)); tab = {}
                for e in a["log2_lrs"][:21]:
                    tab[int(e)] = float(np.exp(np.mean([np.log(O.train(a["problem"], a["optimizer"], 2.0 ** int(e), steps, s, a.get("schedule", "const"), float(a.get("warmup", 0)))["rel_verlust"]) for s in seeds])))
                return {"rel_verlust": tab, "beste_log2_lr": min(tab, key=tab.get)}
            if op == "gd_schaerfe": return O.gd_eos(int(a["width"]), float(a["lr"]), int(a["steps"]), int(a.get("seed", 0)))
            if op == "mup_sweep":
                seeds = [int(s) for s in a.get("seeds", [0])][:2]; out = {}
                for w in [int(x) for x in a["widths"][:4] if int(x) <= 512]:
                    e, tab = O.best_log2_lr(a["param"], a["optimizer"], w, [int(x) for x in a["log2_lrs"][:15]], int(min(a.get("steps", 300), 400)), seeds)
                    out[w] = {"beste_log2_lr": e, "testverlust": tab}
                return out
            if op == "stabilitaet_numerisch":
                H = np.array(a["H"], float); lr = float(eval_frac(a["lr"])); beta = float(eval_frac(a.get("beta", 0)))
                ev = np.linalg.eigvalsh(H); rho = 0.0
                for l in ev:
                    rho = max(rho, max(abs(np.roots([1, -(1 + beta - lr * l), beta]))))
                return {"eigenwerte": ev.tolist(), "spektralradius": float(rho), "hinweis": "numerisch"}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    def check(self, p):
        try:
            fn = CHECKS.get(p.get("typ"))
            if not fn: return False, f"unbekannter Prüfungstyp {p.get('typ')}", {}
            return _memo(p, fn)
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def level(self, p): return LEVEL.get(p.get("typ"), "observed")

    def consistent(self, antwort, p):
        if p.get("typ") == "exponent" and antwort.get("zahl") is not None:
            try: return abs(float(antwort["zahl"]) - float(p["exponent"])) <= 0.05
            except (TypeError, ValueError): return False
        return True

    def describe(self, p):
        t = p.get("typ")
        if t == "exponent":
            name = {"gf": "Verlust des Gradientenflusses über die Zeit t", "param": "Verlust über die Merkmalszahl P (unendlich viele Daten)",
                    "compute": "rechenoptimaler Verlust über das Budget C = P*t", "ridge": "Exzess-Risiko der Ridge-Regression über N",
                    "rf": "Verlust des linearen Random-Feature-Modells über P"}[p["kurve"]]
            extra = f", ridge = {p.get('ridge', 0)}, noise = {p.get('noise', 0)}" if p["kurve"] == "ridge" else ""
            return (f"Im linearen Modell mit Spektrum lambda_k = k^-{p['a']} und Zielanteilen k^-{p['b']}{extra} fällt der {name} wie "
                    f"x^-{p['exponent']} (numerischer Fit des Prüfers in zwei Fenstern, Toleranz {TOL_MC if p['kurve'] in ('ridge', 'rf') else TOL_DET}).")
        if t == "vergleich":
            a, b = p["a"], p["b"]; f = lambda s: f"{s['optimizer']} ({s.get('schedule', 'const')}" + (f", Warmup {s['warmup']}" if s.get("warmup") else "") + ")"
            return (f"Auf dem Problem {json.dumps(p['problem'], ensure_ascii=False)} mit {p.get('steps', 500)} Schritten erreicht {f(a)} einen kleineren "
                    f"relativen Endverlust als {f(b)}, beide mit selbst getunter Lernrate (Prüfer: {len(EVAL_SEEDS)} frische Seeds, "
                    f"p < {P_MAX}, Verhältnis < {EFFEKT}).")
        if t == "eos":
            return (f"Voll-Batch-GD (Breite {p['width']}, lr = {p['lr']}, {p['steps']} Schritte): " +
                    (f"lr*lambda_max/2 liegt am Ende in {list(EOS_BAND)} (Edge of Stability)" if p["regime"] == "eos" else f"lr*lambda_max/2 bleibt unter {STABIL_MAX}") +
                    " in mindestens 4 von 5 Seeds (numerisch, voller Hesse-Eigenwert).")
        if t == "lr_transfer":
            return (f"{p['param'].upper()} mit {p['optimizer']} über Breiten {sorted(p['widths'])}: die optimale Lernrate " +
                    ("verschiebt sich um höchstens eine Oktave (Transfer)" if p["transfer"] else "verschiebt sich um mindestens zwei Oktaven (kein Transfer)") +
                    f" (numerisch, Prüfer-Tuning auf Gitter mit Faktor 2, {MUP_STEPS} Schritte, {len(MUP_SEEDS)} Seeds).")
        if t == "stabilitaet":
            return (f"{p.get('methode', 'gd')} mit lr = {p['lr']}" + (f", beta = {p.get('beta')}" if p.get("methode") == "heavy_ball" else "") +
                    f" auf f(x) = x^T H x / 2 mit H = {p['H']} ist {'stabil (konvergent)' if p.get('stabil') else 'nicht stabil'} "
                    "(exaktes Zertifikat, rationale Arithmetik).")
        return super().describe(p)

    def selftest(self):
        heavy = {"typ": "quadratisch", "rotiert": True, "noise": {"typ": "student", "df": 1.5, "sigma": 0.1}}
        return [
            ({"typ": "exponent", "kurve": "gf", "a": 1, "b": 2, "exponent": 1.0}, True),
            ({"typ": "exponent", "kurve": "gf", "a": 1, "b": 2, "exponent": 1.06}, False),
            ({"typ": "exponent", "kurve": "compute", "a": 1, "b": 2, "exponent": 0.5}, True),
            ({"typ": "exponent", "kurve": "compute", "a": 1, "b": 2, "exponent": 0.46}, False),
            ({"typ": "exponent", "kurve": "gf", "a": 1, "b": 2, "exponent": 1.5, "toleranz": 1.0}, False),   # Regelverletzung: eigene Toleranz
            ({"typ": "exponent", "kurve": "gf", "a": 5, "b": 2, "exponent": 0.2}, False),                    # außerhalb des Prüfbereichs
            ({"typ": "stabilitaet", "methode": "gd", "H": [["1", "0"], ["0", "2"]], "lr": "9/10", "stabil": True}, True),
            ({"typ": "stabilitaet", "methode": "gd", "H": [["1", "0"], ["0", "2"]], "lr": "1", "stabil": True}, False),   # Rand 2/lr = lambda_max
            ({"typ": "stabilitaet", "methode": "heavy_ball", "H": [["1", "0"], ["0", "2"]], "lr": "1", "beta": "1/2", "stabil": True}, True),
            ({"typ": "vergleich", "problem": heavy, "steps": 500, "a": {"optimizer": "clip_sgd"}, "b": {"optimizer": "sgd"}}, True),
            ({"typ": "vergleich", "problem": heavy, "steps": 500, "a": {"optimizer": "sgd"}, "b": {"optimizer": "clip_sgd"}}, False),
            ({"typ": "eos", "width": 16, "lr": 0.1, "steps": 2000, "regime": "stabil"}, True),
            ({"typ": "eos", "width": 16, "lr": 0.1, "steps": 2000, "regime": "eos"}, False),
            ({"typ": "eos", "width": 16, "lr": 1.0, "steps": 2000, "regime": "eos"}, True),
            ({"typ": "exponent", "kurve": "param", "a": 1, "b": 1.5, "exponent": 0.5}, True),
            ({"typ": "exponent", "kurve": "param", "a": 1, "b": 1.5, "exponent": 0.55}, False),
            ({"typ": "lr_transfer", "param": "mup", "optimizer": "adam", "widths": [32, 128, 256], "transfer": True}, True),
            ({"typ": "lr_transfer", "param": "sp", "optimizer": "sgd", "widths": [32, 128, 256], "transfer": True}, False),
        ]


def eval_frac(x): return Fraction(str(x))


DOMAIN = OptScaleDomain()
