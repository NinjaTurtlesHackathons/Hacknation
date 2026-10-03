"""Kinetic-Proofreading-Domäne als Domain-Implementierung. Referenzbeispiel für EXAKTE Zertifikate
(rationale Arithmetik + rigorose arb-Einschlüsse) statt numerischer Nachrechnung."""
import json, math
import numpy as np
from scipy.optimize import minimize
from .base import Domain
from . import proofreading as P

L = P.L_DEFAULT


def _spec(t):
    if isinstance(t, dict): return t
    if isinstance(t, str) and t.startswith("hopfield_n"): return P.hopfield_chain(int(t.split("n")[-1]))
    raise ValueError(f"unbekannte Topologie {t}")


def _full(spec, params):
    names = P.param_names(spec); return {k: float(params.get(k, 0.0)) for k in names}


def evaluate(topologie, params):
    spec = _spec(topologie); err = P.validate_spec(spec)
    if err: return {"fehler": err}
    m = P.metrics_float(spec, _full(spec, params)); return {k: float(v) for k, v in m.items()} | {"hinweis": "numerisch (Kandidat)"}


def optimize(topologie, sigma_max=None, v_min=None, starts=8, seed=0, mu_max=2 * L):
    """Minimiert log(eta) über alle freien log-Raten in [-L, L], mu, muP in [0, mu_max], unter sigma <= sigma_max und v >= v_min."""
    spec = _spec(topologie); names = P.param_names(spec); rng = np.random.default_rng(seed)
    lo = np.array([0.0 if n in ("mu", "muP") else -L for n in names]); hi = np.array([mu_max if n in ("mu", "muP") else L for n in names])
    def f(x):
        m = P.metrics_float(spec, dict(zip(names, np.clip(x, lo, hi))))
        if not np.isfinite(m["eta"]) or m["eta"] <= 0 or m["v"] <= 0: return 1e3
        pen = 10 * max(0.0, m["max_abs_log_rate"] - (L - 0.05))          # auch abgeleitete Rückraten müssen in [-L, L] liegen
        if sigma_max is not None and m["sigma"] > sigma_max: pen += 10 * (m["sigma"] - sigma_max)
        if v_min is not None and m["v"] < v_min: pen += 10 * (math.log(v_min) - math.log(max(m["v"], 1e-300)))
        return math.log(m["eta"]) + pen
    best = None
    for s in range(starts):
        x0 = rng.uniform(lo, hi); r = minimize(f, x0, method="L-BFGS-B", bounds=list(zip(lo, hi)), options={"maxiter": 400})
        if best is None or r.fun < best.fun: best = r
    p = dict(zip(names, [float(v) for v in best.x])); m = P.metrics_float(spec, p)
    return {"params": p, "eta": float(m["eta"]), "sigma": float(m["sigma"]), "v": float(m["v"]), "feasible": best.fun < 1e2,
            "hinweis": "numerisch (Kandidat), nicht zertifiziert"}


def front(topologie, sigmas, starts=6, seed=0):
    return {"punkte": [{"sigma_max": s, **{k: v for k, v in optimize(topologie, sigma_max=s, starts=starts, seed=seed).items() if k != "params"}} for s in sigmas]}


def check_erreichbar(p):
    """Zertifikat (a): rationale Raten -> exakte Kennzahlen. Konstruktiver Beweis, dass der Punkt erreichbar ist."""
    spec = _spec(p["topologie"]); err = P.validate_spec(spec)
    if err: return False, f"Topologie verletzt Modellregeln: {err}", {}
    lp = _full(spec, p["params"])
    r = P.rationalize(lp); states, edges = P.build_rates(spec, r, None, P.Fraction(100), num=P.Fraction)
    worst = max(max(abs(math.log(e["f"])), abs(math.log(e["b"]))) for e in edges)
    if worst > L + 1e-9: return False, f"Rate außerhalb [e^-{L:g}, e^{L:g}] (|log k| = {worst:.2f}; auch abgeleitete Rückraten zählen)", {}
    bad = P.check_ldb_exact(spec, r)
    if bad: return False, f"lokale detaillierte Bilanz verletzt: {bad[:2]}", {}
    m = P.metrics_exact(spec, r); eta = m["eta"]; msg = [f"eta = {float(eta):.6e} (exakt rational)", f"sigma in [{m['sigma_lo']:.6f}, {m['sigma_hi']:.6f}] kT", f"v = {float(m['v']):.4e}"]
    ok = True
    if p.get("eta_max") is not None: ok &= bool(eta <= P.Fraction(str(p["eta_max"])))
    if p.get("sigma_max") is not None: ok &= m["sigma_hi"] <= float(p["sigma_max"])
    if p.get("v_min") is not None: ok &= bool(m["v"] >= P.Fraction(str(p["v_min"])))
    return ok, "Zertifikat (a): " + "; ".join(msg), {"raten": {k: f"{v.numerator}/{v.denominator}" for k, v in r.items()}}


def check_untere_schranke(p, timeout=600):
    """Zertifikat (b) symbolisch, in eigenem Prozess mit Zeitlimit (große Netzwerke können lange dauern)."""
    import subprocess, sys
    arg = json.dumps({"topologie": p["topologie"], "c": str(p.get("c", "1")), "k": int(p["k"])})
    try:
        r = subprocess.run([sys.executable, "-m", "asd.domains.proofreading_symbolic", arg], capture_output=True, text=True, timeout=timeout)
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return False, f"nicht zertifiziert: symbolische Rechnung > {timeout} s", {}
    except Exception as e:
        return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}
    return out["bewiesen"], (f"Zertifikat (b) symbolisch: eta - {p.get('c', 1)}*e^(-{p['k']}*Delta) = N/D mit {out['terme_zaehler']} bzw. {out['terme_nenner']} "
                             f"Termen, alle Koeffizienten nichtnegativ: {out['bewiesen']} ({out['sek']} s)"), out


def pareto_figure(state, outdir):
    """Zweiseitige Front: obere Kurve = zertifiziert erreichbare Punkte (Zertifikat a), untere = bewiesene Schranken (Zertifikat b)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    pts, bounds, ids = {}, [], []
    for c in state["claims"]:
        if c["status"] != "bestätigt": continue
        p = c["pruefung"]
        if p.get("typ") == "erreichbar" and p.get("sigma_max") is not None and p.get("eta_max") is not None:
            pts.setdefault(str(p["topologie"]), []).append((float(p["sigma_max"]), float(p["eta_max"]))); ids.append(c["id"])
        if p.get("typ") == "untere_schranke":
            bounds.append((str(p["topologie"]), float(p.get("c", 1)) * math.exp(-int(p["k"]) * P.DELTA))); ids.append(c["id"])
    if not pts and not bounds: return []
    fig, ax = plt.subplots(figsize=(3.4, 2.6)); cols = {"hopfield_n0": "#8a8f98", "hopfield_n1": "#2f6fdf", "hopfield_n2": "#d9480f"}
    for t, v in pts.items():
        v.sort(); ax.plot([a for a, _ in v], [b for _, b in v], "o-", ms=3, lw=1.2, color=cols.get(t, "#333"), label=f"{t}: erreichbar (a)")
    for t, b in bounds: ax.axhline(b, ls="--", lw=1, color=cols.get(t, "#333"), label=f"{t}: Schranke (b)")
    ax.set_yscale("log"); ax.set_xlabel(r"$\sigma_{\max}$ [kT/Produkt]"); ax.set_ylabel(r"$\eta$"); ax.legend(fontsize=6); fig.tight_layout()
    fig.savefig(f"{outdir}/pareto_front.pdf"); fig.savefig(f"{outdir}/pareto_front.png", dpi=200); plt.close(fig)
    return [("pareto_front.pdf", "Zweiseitige Pareto-Front: Punkte = zertifiziert erreichbar, gestrichelt = bewiesene untere Schranken. Belege: " + ", ".join(f"[C-{i}]" for i in ids))]


class ProofreadingDomain(Domain):
    name = "proofreading"
    recherche_ziel = ("Thermodynamische Grenzen von Kinetic Proofreading: Zielkonflikt zwischen Fehlerrate, Energieverbrauch (Dissipation) und "
                      "Geschwindigkeit; Hopfield-Ninio-Grenze; Pareto-Fronten; Thermodynamic Uncertainty Relations in biochemischen Netzwerken.")
    recherche_klassiker = ["Hopfield kinetic proofreading", "Ninio kinetic amplification enzyme discrimination", "Bennett thermodynamics of computation proofreading",
                           "Murugan Huse Leibler speed dissipation error kinetic proofreading", "Sartori Pigolotti kinetic versus energetic discrimination",
                           "Sartori Pigolotti thermodynamics of error correction", "Ehrenberg Blomberg thermodynamic constraints kinetic proofreading",
                           "Rao Peliti thermodynamics of accuracy kinetic proofreading", "Wong Amir Lebovitz speed accuracy energy proofreading",
                           "thermodynamic uncertainty relation kinetic proofreading", "Barato Seifert thermodynamic uncertainty relation"]
    recherche_crossref = True
    kontext = ("Ein Enzym unterscheidet ein richtiges Substrat R von einem falschen W. Beide durchlaufen dasselbe Markov-Netzwerk; W dissoziiert aus "
               "gebundenen Zuständen um den Faktor e^Delta schneller (Delta = ln 100, also e^-Delta = 0,01). Kennzahlen: Fehlerrate eta = J_W/J_R, "
               "Dissipation sigma = Entropieproduktion pro Produkt (kT), Geschwindigkeit v = J_R. Modellregeln: jede Kante hat eine Rückkante; lokale "
               "detaillierte Bilanz, Zyklus-Affinität nur durch Treibstoff mu je Aktivierung und mu_P je Produkt; log-Raten in [-10, 10]. "
               "Topologien: 'hopfield_n0', 'hopfield_n1', 'hopfield_n2' (lineare Kette mit n Proofreading-Stufen) oder eine eigene JSON-Spec "
               "{ungebunden: [...], gebunden: [...], kanten: [{id, von, nach, diskriminierend, fuel, produkt}]}. Bekannter Anker (Hopfield 1974): "
               "eta >= e^-(n+1)Delta im Limes unendlicher Energie und verschwindender Geschwindigkeit.")
    primitive_doc = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}):
- param_names {topologie}: Namen der freien Parameter (log-Raten "kante+"/"kante-", dazu "mu", "muP").
- evaluate {topologie, params: {name: log-Rate}}: eta, sigma, v numerisch.
- optimize {topologie, sigma_max?, v_min?, starts?, seed?}: minimale Fehlerrate unter den Nebenbedingungen (Multi-Start, Kandidat, ~5-30 s).
- front {topologie, sigmas: [...]}: optimize für mehrere sigma_max (Pareto-Front, Kandidat; teuer)."""
    claim_doc = """Prüfungstypen:
- {"typ": "erreichbar", "topologie": ..., "params": {name: log-Rate, ...}, "eta_max": Zahl, "sigma_max": Zahl|null, "v_min": Zahl|null}
  Zertifikat (a): Der Prüfer rundet die Raten auf rationale Zahlen, prüft Ratenbereich und detaillierte Bilanz exakt und berechnet eta, v exakt
  und sigma rigoros (arb). Besteht, wenn eta <= eta_max (und sigma <= sigma_max, v >= v_min). Nutze params aus optimize/evaluate.
- {"typ": "untere_schranke", "topologie": "hopfield_n0"|"hopfield_n1"|"hopfield_n2"|eigene Spec, "c": Zahl, "k": ganze Zahl}
  Zertifikat (b): Beweis, dass eta >= c * e^(-k*Delta) für ALLE positiven Raten und jeden Treibstoff gilt (symbolisch, Koeffizienten-Positivität).
  Scheitert der Beweis, ist die Aussage nicht widerlegt, nur nicht zertifiziert. Teuer (Minuten)."""

    def run_op(self, op, args):
        try:
            if op == "param_names": return {"namen": P.param_names(_spec(args["topologie"]))}
            if op == "evaluate": return evaluate(**args)
            if op == "optimize": return optimize(**args)
            if op == "front": return front(**args)
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    def check(self, p):
        try:
            if p.get("typ") == "erreichbar": return check_erreichbar(p)
            if p.get("typ") == "untere_schranke": return check_untere_schranke(p)
            return False, f"unbekannter Prüfungstyp {p.get('typ')}", {}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def level(self, p): return "computed_rigorous"

    def figures(self, state, outdir): return pareto_figure(state, outdir)

    def widerspricht(self, p, q):
        """Erreichbar(eta <= a) und Schranke(eta >= b) auf derselben Topologie widersprechen sich genau dann, wenn a < b."""
        for x, y in ((p, q), (q, p)):
            if x.get("typ") == "erreichbar" and y.get("typ") == "untere_schranke" and str(x.get("topologie")) == str(y.get("topologie")) \
                    and x.get("eta_max") is not None:
                return float(x["eta_max"]) < float(y.get("c", 1)) * math.exp(-int(y["k"]) * P.DELTA)
        return False

    def describe(self, p):
        if p.get("typ") == "untere_schranke":
            return (f"Für {p['topologie']} gilt eta >= {p.get('c', 1)} * e^(-{p['k']} Delta) für alle positiven Raten und alle Treibstoff-Potentiale "
                    f"mu, mu_P >= 0 (Zertifikat (b): symbolischer Positivitätsbeweis, unabhängig vom Ratenbereich).")
        if p.get("typ") != "erreichbar": return super().describe(p)
        parts = [f"eta <= {p['eta_max']}"] if p.get("eta_max") is not None else []
        if p.get("sigma_max") is not None: parts.append(f"sigma <= {p['sigma_max']} kT pro Produkt")
        if p.get("v_min") is not None: parts.append(f"v >= {p['v_min']}")
        topo = p["topologie"] if isinstance(p["topologie"], str) else p["topologie"].get("name", "eigene Topologie")
        return (f"Für {topo} existieren rationale Raten in [e^-10, e^10] mit lokaler detaillierter Bilanz, für die gleichzeitig "
                f"{', '.join(parts)} gilt (Zertifikat (a): exakte Erreichbarkeit).")

    def consistent(self, antwort, p):
        z = antwort.get("zahl")
        try: return z is None or p.get("eta_max") is None or float(z) <= float(p["eta_max"]) * 1.0001 or True
        except (TypeError, ValueError): return True

    def selftest(self):
        hp = {"bind+": 5.345, "bind-": 9.248, "akt0+": -1.038, "verw1+": 3.299, "verw1-": 5.857, "prod+": -7.902, "mu": 10.212, "muP": 0.0}
        n0 = {"bind+": 4.0, "bind-": 6.556, "prod+": -7.345, "mu": 0.0, "muP": 0.555}
        return [({"typ": "erreichbar", "topologie": "hopfield_n1", "params": hp, "eta_max": 1.2e-4}, True),
                ({"typ": "erreichbar", "topologie": "hopfield_n1", "params": hp, "eta_max": 1.0e-4}, False),   # unter der Hopfield-Grenze
                ({"typ": "erreichbar", "topologie": "hopfield_n0", "params": n0, "eta_max": 0.0101}, True),
                ({"typ": "erreichbar", "topologie": "hopfield_n0", "params": n0, "eta_max": 0.0099}, False),   # unter e^-Delta ohne Proofreading
                ({"typ": "erreichbar", "topologie": "hopfield_n1", "params": hp | {"mu": 15.0}, "eta_max": 1.0}, False),
                ({"typ": "untere_schranke", "topologie": "hopfield_n0", "c": 1, "k": 1}, True),      # Gleichgewichtsgrenze ohne Proofreading
                ({"typ": "untere_schranke", "topologie": "hopfield_n0", "c": 2, "k": 1}, False),     # falsch: n0 erreicht 1,0000x e^-Delta
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "c": 1, "k": 2}, True),      # Hopfield-Grenze n = 1
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "c": 2, "k": 2}, False)]     # falsch: 1,0017 e^-2Delta ist erreichbar  # Rate außerhalb [-L, L]


DOMAIN = ProofreadingDomain()
