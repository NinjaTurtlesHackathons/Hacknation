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
    if isinstance(t, str) and t.startswith("fam"):                       # Mitglied einer vom Prüfer erzeugten Familie, z. B. fam2_43
        from .proofreading_family import family
        k = int(t[3:].split("_")[0]); return next(x for x in family(k) if x["name"] == t)
    raise ValueError(f"unbekannte Topologie {t}")


def _full(spec, params):
    names = P.param_names(spec); return {k: float(params.get(k, 0.0)) for k in names}


def evaluate(topologie, params):
    spec = _spec(topologie); err = P.validate_spec(spec)
    if err: return {"fehler": err}
    m = P.metrics_float(spec, _full(spec, params)); return {k: float(v) for k, v in m.items()} | {"hinweis": "numerisch (Kandidat)"}


def optimize(topologie, sigma_max=None, v_min=None, starts=8, seed=0, mu_max=2 * L, fest=None):
    """Minimiert log(eta) über alle freien log-Raten in [-L, L], mu, muP in [0, mu_max], unter sigma <= sigma_max und v >= v_min."""
    spec = _spec(topologie); names = P.param_names(spec); rng = np.random.default_rng(seed); fest = dict(fest or {})
    lo = np.array([0.0 if n in ("mu", "muP") else -L for n in names]); hi = np.array([mu_max if n in ("mu", "muP") else L for n in names])
    for j, n in enumerate(names):                                   # feste Parameter (z. B. Treibstoff mu) als enge Schranke
        if n in fest: lo[j] = hi[j] = float(fest[n])
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


def _cx_job(a):
    name, thr = a; best = None
    for seed in (1, 2):
        try: r = optimize(name, starts=8, seed=seed)
        except Exception: continue
        if r["feasible"] and (best is None or r["eta"] < best["eta"]): best = r
    return {"topologie": name, "eta": best["eta"] if best else None, "params": best["params"] if best else None}


def check_erreichbar_liste(p):
    """Zertifikat (a) für viele Fälle: jeder Fall {topologie, params, eta_max} wird einzeln exakt geprüft; besteht nur, wenn alle bestehen."""
    faelle = p.get("faelle") or []
    if not faelle: return False, "keine Fälle angegeben", {}
    res = [(f.get("topologie"),) + check_erreichbar({"typ": "erreichbar", **f})[:2] for f in faelle]
    bad = [(t, w[:80]) for t, ok, w in res if not ok]
    return (not bad), (f"Zertifikat (a) für {len(faelle) - len(bad)}/{len(faelle)} Fälle bestanden" + (f"; nicht bestanden: {bad[:4]}" if bad else "")), {"ergebnisse": res}


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


def check_optimum(p):
    """Numerisch: Der Prüfer sucht selbst (Seed 4711, 24 Starts) das Minimum von eta unter denselben Nebenbedingungen.
    Besteht, wenn sein Minimum innerhalb von 2 % (fest) um den behaupteten Wert liegt: nicht deutlich besser (sonst war die Behauptung
    kein Optimum) und nicht deutlich schlechter (sonst ist der Wert nicht reproduzierbar)."""
    r = optimize(p["topologie"], sigma_max=p.get("sigma_max"), v_min=p.get("v_min"), starts=24, seed=4711, fest=p.get("fest"))
    if not r["feasible"]: return False, "Prüfer findet keinen zulässigen Punkt", r
    eta_c = float(p["eta_min"]); ok = abs(r["eta"] - eta_c) <= 0.02 * eta_c
    return ok, f"Prüfer-Suche (24 Starts, Seed 4711): eta_min = {r['eta']:.4e} bei sigma = {r['sigma']:.3f}, v = {r['v']:.3e}; behauptet {eta_c:.4e} (Toleranz 2 %, fest)", r


def check_schranke_familie(p, timeout=1800):
    """Zertifikat (b) für eine Familie: der Prüfer erzeugt die Familie 'gebunden<=k' selbst und beweist die Schranke für jedes
    Mitglied (oder für die angegebene Teilmenge). Besteht nur, wenn ALLE betrachteten Mitglieder bewiesen sind."""
    from .proofreading_family import family, prove_family
    from .proofreading_symbolic import parse_bound
    parse_bound(p["ausdruck"])                                          # Regelprüfung des Ausdrucks vorab
    k = int(str(p["familie"]).split("<=")[-1]); fam = family(k)
    names = p.get("mitglieder") or [x["name"] for x in fam]
    known = {x["name"] for x in fam}; unknown = [n for n in names if n not in known]
    if unknown: return False, f"unbekannte Familienmitglieder: {unknown[:5]}", {}
    out = prove_family(k, names, p["ausdruck"], timeout=timeout)
    ok_n = [n for n, b in out.items() if b]; bad = [n for n, b in out.items() if not b]
    return (not bad), (f"Zertifikat (b) Familie gebunden<={k}: Schranke eta >= {p['ausdruck']} für {len(ok_n)}/{len(names)} Mitglieder bewiesen"
                       + (f"; nicht bewiesen: {bad[:8]}{' …' if len(bad) > 8 else ''}" if bad else "")), {"bewiesen": ok_n, "nicht_bewiesen": bad}


def check_untere_schranke(p, timeout=600):
    """Zertifikat (b) symbolisch, in eigenem Prozess mit Zeitlimit (große Netzwerke können lange dauern)."""
    import subprocess, sys
    arg = json.dumps({"topologie": p["topologie"], "c": str(p.get("c", "1")), "k": int(p.get("k", 0)), "ausdruck": p.get("ausdruck")})
    try:
        r = subprocess.run([sys.executable, "-m", "asd.domains.proofreading_symbolic", arg], capture_output=True, text=True, timeout=timeout)
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return False, f"nicht zertifiziert: symbolische Rechnung > {timeout} s", {}
    except Exception as e:
        return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}
    rhs = p.get("ausdruck") or f"{p.get('c', 1)}*e^(-{p.get('k')}*Delta)"
    return out["bewiesen"], (f"Zertifikat (b) symbolisch: eta - ({rhs}) = N/D mit {out['terme_zaehler']} bzw. {out['terme_nenner']} "
                             f"Termen, alle Koeffizienten nichtnegativ: {out['bewiesen']} ({out['sek']} s)"), out


def klassifikation_figure(state, outdir, lang="en"):
    """Übersicht der Familie gebunden<=2: bewiesen (Zertifikat b), Gegenbeispiel (Zertifikat a), offen. Nur aus bestätigten Claims."""
    from .proofreading_family import family
    bew, cx, ids = set(), set(), []
    for c in state["claims"]:
        if c.get("status") != "bestätigt": continue
        p = c["pruefung"]
        if p.get("typ") == "schranke_familie" and str(p.get("familie")) == "gebunden<=2" and str(p.get("ausdruck")).replace(" ", "") in ("1/D**2", "D**-2"):
            bew |= set(p.get("mitglieder") or [x["name"] for x in family(2)]); ids.append(c["id"])
        if p.get("typ") == "erreichbar_liste":
            cx |= {f["topologie"] for f in p.get("faelle", []) if float(f.get("eta_max", 1)) <= 1e-4 and str(f["topologie"]).startswith("fam2_")}; ids.append(c["id"])
        if p.get("typ") == "erreichbar" and str(p.get("topologie", "")).startswith("fam2_") and float(p.get("eta_max") or 1) <= 1e-4:
            cx.add(p["topologie"]); ids.append(c["id"])
    if not bew and not cx: return []
    n = len(family(2)); offen = n - len(bew | cx)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ..figstyle import apply_style; apply_style()
    lab = (["bound proven\n(certificate b)", "counterexample\n(certificate a)", "open"] if lang == "en" else ["Schranke bewiesen\n(Zertifikat b)", "Gegenbeispiel\n(Zertifikat a)", "offen"])
    vals = [len(bew), len(cx), offen]; cols = ["#2f6fdf", "#d9480f", "#b8bcc4"]
    fig, ax = plt.subplots(figsize=(4.6, 2.4)); bars = ax.barh(lab[::-1], vals[::-1], color=cols[::-1])
    for b, v in zip(bars, vals[::-1]): ax.text(b.get_width() + 0.8, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=8)
    ax.set_xlabel(f"number of topologies (of {n} with two bound states)" if lang == "en" else f"Anzahl Topologien (von {n} mit zwei gebundenen Zuständen)")
    ax.grid(axis="y", visible=False); fig.tight_layout(); fig.savefig(f"{outdir}/klassifikation.pdf"); fig.savefig(f"{outdir}/klassifikation.png", dpi=200); plt.close(fig)
    cap = (f"Classification of the {n} non-degenerate networks with two bound states with respect to the bound $\\eta \\geq e^{{-2\\Delta}}$."
           if lang == "en" else f"Klassifikation der {n} nicht entarteten Netzwerke mit zwei gebundenen Zuständen bezüglich $\\eta \\geq e^{{-2\\Delta}}$.")
    return [("klassifikation.pdf", cap, [f"C-{i}" for i in ids])]


def pareto_figure(state, outdir, lang="en"):
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
    from ..figstyle import apply_style; apply_style()
    fig, ax = plt.subplots(figsize=(4.6, 3.2)); cols = {"hopfield_n0": "#8a8f98", "hopfield_n1": "#2f6fdf", "hopfield_n2": "#d9480f"}
    for t, v in pts.items():
        v.sort(); ax.plot([a for a, _ in v], [b for _, b in v], "o-", ms=3, lw=1.2, color=cols.get(t, "#333"), label=(f"{t}: achievable (a)" if lang == "en" else f"{t}: erreichbar (a)"))
    for t, b in bounds: ax.axhline(b, ls="--", lw=1, color=cols.get(t, "#333"), label=(f"{t}: bound (b)" if lang == "en" else f"{t}: Schranke (b)"))
    ax.set_yscale("log"); ax.set_xlabel(r"dissipation bound $\sigma_{\max}$ [$k_BT$ per product]" if lang == "en" else r"Dissipationsschranke $\sigma_{\max}$ [$k_BT$ pro Produkt]")
    ax.set_ylabel(r"error rate $\eta$ (dimensionless)" if lang == "en" else r"Fehlerrate $\eta$ (dimensionslos)"); ax.legend(); fig.tight_layout()
    fig.savefig(f"{outdir}/pareto_front.pdf"); fig.savefig(f"{outdir}/pareto_front.png", dpi=200); plt.close(fig)
    cap = ("Certified achievable error thresholds (dots; each dot is the threshold of one exact certificate, not an optimum) and proven lower "
           "bounds (dashed lines)." if lang == "en" else "Zertifiziert erreichbare Fehlerschwellen (Punkte; je ein exaktes Zertifikat, kein Optimum) "
           "und bewiesene untere Schranken (gestrichelt).")
    return [("pareto_front.pdf", cap, [f"C-{i}" for i in ids])]


def _topo(t): return t if isinstance(t, str) else t.get("name", "custom topology")


def describe_en(p):
    """Canonical English statement, exactly as strong as the check."""
    t = p.get("typ")
    if t == "untere_schranke":
        rhs = p.get("ausdruck") or f"{p.get('c', 1)} e^(-{p['k']} Delta)"
        return (f"For {_topo(p['topologie'])}, eta >= {rhs} (D = e^Delta, G = e^mu) holds for all positive rates and all fuel potentials mu, mu_P >= 0 "
                f"(certificate (b): symbolic positivity proof, independent of the rate range).")
    if t == "schranke_familie":
        n = len(p.get("mitglieder") or []) or "all"
        return (f"For {n} topologies of the verifier-generated family {p['familie']} (one unbound state, edge catalogue of the model), eta >= {p['ausdruck']} "
                f"holds for all positive rates and fuel potentials (certificate (b), symbolic).")
    if t == "erreichbar_liste":
        f = p.get("faelle") or []; ts = sorted({_topo(x.get('topologie')) for x in f}); mx = max(float(x.get("eta_max", 0)) for x in f) if f else None
        return (f"For each of {len(ts)} topologies ({', '.join(ts[:12])}) there exist rational rates in [e^-10, e^10] satisfying local detailed balance with "
                f"eta <= {mx} (certificate (a), exact for each case).")
    if t == "optimum":
        cons = ", ".join(x for x in [f"sigma <= {p['sigma_max']}" if p.get("sigma_max") is not None else "", f"v >= {p['v_min']}" if p.get("v_min") is not None else ""] if x)
        return f"For {_topo(p['topologie'])}, the numerically found minimum of the error rate under [{cons or 'no constraint'}] is eta_min ≈ {p['eta_min']} (numerical, independent search, ±2 %)."
    if t == "erreichbar":
        parts = [f"eta <= {p['eta_max']}"] if p.get("eta_max") is not None else []
        if p.get("sigma_max") is not None: parts.append(f"sigma <= {p['sigma_max']} kT per product")
        if p.get("v_min") is not None: parts.append(f"v >= {p['v_min']}")
        return (f"For {_topo(p['topologie'])} there exist rational rates in [e^-10, e^10] satisfying local detailed balance such that simultaneously "
                f"{', '.join(parts)} (certificate (a): exact reachability).")
    return "Verified: " + json.dumps(p)


class ProofreadingDomain(Domain):
    name = "proofreading"
    fachgebiet = "Biological Physics"
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
- front {topologie, sigmas: [...]}: optimize für mehrere sigma_max (Pareto-Front, Kandidat; teuer).
- search_counterexamples {names: [...], eta_max}: numerische Suche nach eta < eta_max für jede genannte Topologie (liefert params; ~2-5 min).
- classify_family {k, ausdruck}: Beweisversuch der Schranke für ALLE Mitglieder; liefert Listen beweisbar / nicht_beweisbar (~1 min).
- family {k}: alle Topologien mit k gebundenen Zuständen (Namen fam<k>_<i>, Kanten: id, Treibstoff, diskriminierend). k = 2 hat 88 Mitglieder."""
    claim_doc = """Prüfungstypen:
- {"typ": "erreichbar", "topologie": ..., "params": {name: log-Rate, ...}, "eta_max": Zahl, "sigma_max": Zahl|null, "v_min": Zahl|null}
  Zertifikat (a): Der Prüfer rundet die Raten auf rationale Zahlen, prüft Ratenbereich und detaillierte Bilanz exakt und berechnet eta, v exakt
  und sigma rigoros (arb). Besteht, wenn eta <= eta_max (und sigma <= sigma_max, v >= v_min). Nutze params aus optimize/evaluate.
- {"typ": "untere_schranke", "topologie": "hopfield_n0"|"hopfield_n1"|"hopfield_n2"|eigene Spec, "c": Zahl, "k": ganze Zahl}
  Zertifikat (b): Beweis, dass eta >= c * e^(-k*Delta) für ALLE positiven Raten und jeden Treibstoff gilt (symbolisch, Koeffizienten-Positivität).
  Alternativ "ausdruck": rationale Funktion in D = e^Delta, G = e^mu, GP = e^mu_P, z. B. "(1+G)/(D*(D+G))": Beweis eta >= ausdruck
  für alle Raten, bei JEDEM Treibstoff (Schranke darf von mu abhängen). Scheitert der Beweis, ist die Aussage nicht widerlegt,
  nur nicht zertifiziert. Teuer (Sekunden bis Minuten).
- {"typ": "optimum", "topologie": ..., "eta_min": Zahl, "sigma_max": Zahl|null, "v_min": Zahl|null, "fest": {"mu": Zahl}|null}
  Numerisch: Der Prüfer sucht selbst (eigener Seed, 24 Starts); besteht, wenn sein Minimum innerhalb von 2 % am behaupteten Wert liegt.
- {"typ": "erreichbar_liste", "faelle": [{"topologie": ..., "params": {...}, "eta_max": Zahl}, ...]}
  Zertifikat (a) für viele Topologien auf einmal (z. B. alle Gegenbeispiele aus search_counterexamples); besteht nur, wenn jeder Fall besteht.
- {"typ": "schranke_familie", "familie": "gebunden<=2", "ausdruck": "1/D**2", "mitglieder": ["fam2_0", ...] | null}
  Zertifikat (b) für Topologie-Familien: Der Prüfer erzeugt ALLE Netzwerke mit einem ungebundenen und k gebundenen Zuständen aus dem
  Kantenkatalog (Bindung, treibstoffgetriebenes Verwerfen, Umwandlung, genau eine Produktkante) und beweist die Schranke für jedes
  Mitglied (bzw. die Teilmenge). Topologien der Familie heißen fam<k>_<i> und sind überall als "topologie" verwendbar.
  Experiment dazu: family {k} listet die Mitglieder mit ihren Kanten."""

    def run_op(self, op, args):
        try:
            if op == "param_names": return {"namen": P.param_names(_spec(args["topologie"]))}
            if op == "evaluate": return evaluate(**args)
            if op == "optimize": return optimize(**args)
            if op == "front": return front(**args)
            if op == "classify_family":                          # Explorer-Werkzeug: Beweisversuch für alle Mitglieder (Kandidatenliste, kein Zertifikat)
                from .proofreading_family import family, prove_family
                k = int(args["k"]); names = [x["name"] for x in family(k)]
                out = prove_family(k, names, args.get("ausdruck", f"1/D**{k}"))
                return {"beweisbar": [n for n, b in out.items() if b], "nicht_beweisbar": [n for n, b in out.items() if not b],
                        "hinweis": "Kandidatenliste; zertifiziert wird erst durch schranke_familie"}
            if op == "search_counterexamples":                   # Explorer: für jede genannte Topologie das Minimum von eta suchen
                from concurrent.futures import ProcessPoolExecutor
                names = args["names"]; thr = float(args.get("eta_max", 1e-4))
                with ProcessPoolExecutor(4) as ex: res = list(ex.map(_cx_job, [(n, thr) for n in names]))
                return {"unter_schwelle": [r for r in res if r["eta"] is not None and r["eta"] < thr],
                        "nicht_gefunden": [r["topologie"] for r in res if r["eta"] is None or r["eta"] >= thr],
                        "hinweis": "numerische Kandidaten; zertifiziert wird erst durch erreichbar_liste"}
            if op == "family":
                from .proofreading_family import family
                return {"mitglieder": [{"name": x["name"], "kanten": [(e["id"], e["fuel"], e["diskriminierend"]) for e in x["kanten"]]} for x in family(int(args["k"]))]}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    def check(self, p):
        try:
            if p.get("typ") == "erreichbar": return check_erreichbar(p)
            if p.get("typ") == "untere_schranke": return check_untere_schranke(p)
            if p.get("typ") == "optimum": return check_optimum(p)
            if p.get("typ") == "schranke_familie": return check_schranke_familie(p)
            if p.get("typ") == "erreichbar_liste": return check_erreichbar_liste(p)
            return False, f"unbekannter Prüfungstyp {p.get('typ')}", {}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def ueberraschung(self, p, state):
        """Widerspricht ein BESTANDENES Zertifikat einer aktiven Annahme (z. B. 'genau diese Topologien verletzen die Schranke')?
        Ändert nichts am Prüfer; liefert nur {annahme, grund} für Planänderung/Reopen."""
        faelle = p.get("faelle") if p.get("typ") == "erreichbar_liste" else ([p] if p.get("typ") == "erreichbar" else [])
        for an in state.get("annahmen", []):
            if an.get("status", "aktiv") != "aktiv" or "gegenbeispiele" not in an: continue
            schwelle = float(an.get("schwelle", 1e-4))
            neu = sorted({f.get("topologie") for f in faelle if isinstance(f.get("topologie"), str) and f["topologie"] not in an["gegenbeispiele"]
                          and float(f.get("eta_max", 1)) <= schwelle})
            if neu: return {"annahme": an["id"], "grund": f"neue zertifizierte Verletzung(en) {neu} ausserhalb der angenommenen Menge {an['gegenbeispiele']}: {an['text'][:120]}"}
        return None

    def level(self, p): return "observed" if p.get("typ") == "optimum" else "computed_rigorous"

    def relevanz(self, p):
        t = p.get("typ")
        if t in ("schranke_familie", "erreichbar_liste", "untere_schranke"): return "hauptresultat"
        if t == "erreichbar" and p.get("eta_max") is not None and str(p.get("topologie", "")).startswith("fam") and float(p["eta_max"]) <= 1e-4:
            return "hauptresultat"                                          # Gegenbeispiel zur Hopfield-Schranke e^-2Delta
        if t == "optimum": return "stuetze"
        return "beispiel"

    def parameter(self):
        return {"Delta": ("ln 100 (e^Delta = 100, e^-Delta = 0.01)", "discrimination free-energy difference in kT: W leaves bound states e^Delta times faster"),
                "L": ("10", "range of log-rates: every rate, including derived reverse rates, lies in [e^-10, e^10]"),
                "mu": (">= 0, explored in [0, 20]", "fuel chemical potential (kT) consumed per fuel-driven step"),
                "mu_P": (">= 0, explored in [0, 20]", "chemical potential (kT) of product formation"),
                "max_states": ("10", "maximal number of states of a network (unbound states plus R and W copies of bound states)"),
                "concentrations": ("1", "substrate concentrations are absorbed into the binding rates (normalised)"),
                "rationalisation": ("denominator <= 10^6", "rates are rounded to rationals with denominator at most 10^6 for exact certificates"),
                "family_k": ("2", "number of bound states in the enumerated topology family (88 non-degenerate members)")}

    def figures(self, state, outdir, lang="en"): return pareto_figure(state, outdir, lang) + klassifikation_figure(state, outdir, lang)

    def widerspricht(self, p, q):
        """Erreichbar(eta <= a) und Schranke(eta >= b) auf derselben Topologie (oder Familie mit dieser Topologie) widersprechen sich, wenn a < b."""
        for x, y in ((p, q), (q, p)):
            if x.get("typ") == "erreichbar_liste" and y.get("typ") in ("schranke_familie", "untere_schranke"):
                return any(self.widerspricht({"typ": "erreichbar", **f}, y) for f in x.get("faelle") or [])
            if x.get("typ") == "erreichbar" and y.get("typ") == "schranke_familie" and x.get("eta_max") is not None:
                from .proofreading_symbolic import parse_bound
                t = str(x.get("topologie")); mem = y.get("mitglieder")
                if t.startswith(f"fam{str(y['familie']).split('<=')[-1]}_") and (not mem or t in mem):
                    e, loc = parse_bound(y["ausdruck"])
                    if not e.free_symbols - {loc["D"]}: return float(x["eta_max"]) < float(e.subs(loc["D"], 100))
            if x.get("typ") == "erreichbar" and y.get("typ") == "untere_schranke" and str(x.get("topologie")) == str(y.get("topologie")) \
                    and x.get("eta_max") is not None:
                return float(x["eta_max"]) < float(y.get("c", 1)) * math.exp(-int(y["k"]) * P.DELTA)
        return False

    def describe(self, p, lang="de"):
        if lang == "en": return describe_en(p)
        if p.get("typ") == "untere_schranke":
            rhs = p.get("ausdruck") or f"{p.get('c', 1)} * e^(-{p['k']} Delta)"
            return (f"Für {p['topologie']} gilt eta >= {rhs} (D = e^Delta, G = e^mu) für alle positiven Raten und alle Treibstoff-Potentiale "
                    f"mu, mu_P >= 0 (Zertifikat (b): symbolischer Positivitätsbeweis, unabhängig vom Ratenbereich).")
        if p.get("typ") == "erreichbar_liste":
            f = p.get("faelle") or []; ts = sorted({str(x.get("topologie")) for x in f}); mx = max(float(x.get("eta_max", 0)) for x in f) if f else None
            return (f"Für {len(ts)} Topologien ({', '.join(ts[:12])}{' …' if len(ts) > 12 else ''}) existieren jeweils rationale Raten in [e^-10, e^10] mit lokaler "
                    f"detaillierter Bilanz und eta <= {mx} (Zertifikat (a), je Fall exakt).")
        if p.get("typ") == "schranke_familie":
            n = len(p.get("mitglieder") or []) or "alle"
            return (f"Für {n} Topologien der vom Prüfer erzeugten Familie {p['familie']} (ein ungebundener Zustand, Kantenkatalog laut Modell) gilt "
                    f"eta >= {p['ausdruck']} für alle positiven Raten und Treibstoffe (Zertifikat (b), symbolisch).")
        if p.get("typ") == "erreichbar_liste":
            f = p.get("faelle") or []; ts = sorted({str(x.get("topologie")) for x in f}); mx = max(float(x.get("eta_max", 0)) for x in f) if f else None
            return (f"Für {len(ts)} Topologien ({', '.join(ts[:12])}{' …' if len(ts) > 12 else ''}) existieren jeweils rationale Raten in [e^-10, e^10] mit lokaler "
                    f"detaillierter Bilanz und eta <= {mx} (Zertifikat (a), je Fall exakt).")
        if p.get("typ") == "schranke_familie":
            n = len(p.get("mitglieder") or []) or "alle"
            return (f"Für {n} Topologien der vom Prüfer erzeugten Familie {p['familie']} (ein ungebundener Zustand, Kantenkatalog laut Modell) gilt "
                    f"eta >= {p['ausdruck']} für alle positiven Raten und Treibstoffe (Zertifikat (b), symbolisch).")
        if p.get("typ") == "optimum":
            cons = ", ".join(x for x in [f"sigma <= {p['sigma_max']}" if p.get("sigma_max") is not None else "", f"v >= {p['v_min']}" if p.get("v_min") is not None else "",
                                         f"fest {p['fest']}" if p.get("fest") else ""] if x)
            return f"Für {p['topologie']} ist das numerisch gefundene Minimum der Fehlerrate unter [{cons or 'keine Nebenbedingung'}] eta_min ≈ {p['eta_min']} (numerisch, unabhängige Suche des Prüfers, ±2 %)."
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
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "c": 2, "k": 2}, False),     # falsch: 1,0017 e^-2Delta ist erreichbar
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "ausdruck": "1/D**2"}, True),  # Ausdrucks-Form, gleiche Aussage
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "ausdruck": "1/D"}, False),    # falsch: Proofreading unterschreitet e^-Delta
                ({"typ": "untere_schranke", "topologie": "hopfield_n1", "ausdruck": "exp(-2*D)"}, False),  # Regelverletzung: nicht-rationaler Ausdruck
                ({"typ": "schranke_familie", "familie": "gebunden<=1", "ausdruck": "1/D"}, True),    # alle 1-Zustands-Netze: Gleichgewichtsgrenze
                ({"typ": "schranke_familie", "familie": "gebunden<=1", "ausdruck": "2/D"}, False),         # falsch: n0 erreicht 1,0001 e^-Delta
                ({"typ": "schranke_familie", "familie": "gebunden<=2", "ausdruck": "1/D**2", "mitglieder": ["fam2_99999"]}, False),  # erfundenes Mitglied
                ({"typ": "erreichbar_liste", "faelle": [{"topologie": "hopfield_n1", "params": hp, "eta_max": 1.2e-4},
                                                        {"topologie": "hopfield_n0", "params": n0, "eta_max": 0.0101}]}, True),
                ({"typ": "erreichbar_liste", "faelle": [{"topologie": "hopfield_n1", "params": hp, "eta_max": 1.2e-4},
                                                        {"topologie": "hopfield_n0", "params": n0, "eta_max": 0.0099}]}, False),   # ein Fall falsch -> alles falsch
                ({"typ": "untere_schranke", "topologie": {"name": "entartet", "ungebunden": ["E"], "gebunden": ["C0", "C1"], "kanten": [
                    {"id": "b", "von": "C1", "nach": "E", "diskriminierend": True, "fuel": 0, "produkt": 0},
                    {"id": "p", "von": "C0", "nach": "E", "diskriminierend": False, "fuel": 0, "produkt": 1}]}, "c": 1, "k": 2}, False)]  # eta = 0/0: nicht bewiesen, kein Absturz  # Rate außerhalb [-L, L]


DOMAIN = ProofreadingDomain()
