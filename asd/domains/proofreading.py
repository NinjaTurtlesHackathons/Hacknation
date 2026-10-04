"""Domäne: thermodynamische Grenzen von Kinetic Proofreading.

Modell (verbindlich, siehe decisions.md D20):
- Netzwerk = Topologie-Spec (JSON): ungebundene Zustände (gemeinsam für R und W, z. B. "E") und gebundene Zustände
  (je eine R- und eine W-Kopie). Jede Kante hat eine Rückkante.
- Lokale detaillierte Bilanz: ln(k_vor/k_rück) = phi_u - phi_v + a_e mit a_e = fuel_e * mu + produkt_e * mu_P.
  Frei sind Vor- und Rückrate jeder Baumkante eines aufspannenden Baums und die Vorrate jeder Sehne; die Rückrate jeder
  Sehne folgt aus der Bilanz. Damit gilt für jeden Zyklus prod k_vor / prod k_rück = exp(Summe der Treibstoff-Affinitäten).
- Diskriminierung: Gebundene W-Zustände sind um Delta instabiler. Kanten gebunden -> ungebunden, die als "diskriminierend"
  markiert sind, tragen den Faktor e^Delta auf der Vorrate (Abdissoziation); bei allen anderen gebunden -> ungebunden
  Kanten folgt aus der Bilanz der Faktor e^-Delta auf der Rückrate (z. B. Rückbindung des Produkts). Sonst identisch.
- Exakt: Raten rational, e^Delta, e^mu, e^mu_P rational -> Steady State, eta, v rational (sympy); sigma als Summe
  rationaler Flüsse mal ln(rational), rigoros eingeschlossen mit arb (python-flint).
Kennzahlen: eta = J_W/J_R, sigma = Entropieproduktion/(J_R+J_W) in kT, v = J_R.
"""
import itertools, json, math
from fractions import Fraction
import numpy as np

DELTA = math.log(100.0)
L_DEFAULT = 10.0


# ------------------------------------------------------------------------------------------- Topologien
def hopfield_chain(n):
    """Lineare Hopfield-Kette mit n Proofreading-Stufen: E <-> C0 -> C1 -> ... -> Cn -> E + P, Verwerfen C_i -> E."""
    gebunden = [f"C{i}" for i in range(n + 1)]
    kanten = [{"id": "bind", "von": "C0", "nach": "E", "diskriminierend": True, "fuel": 0, "produkt": 0}]   # C0 -> E: Abdissoziation k_off
    for i in range(n):
        kanten.append({"id": f"akt{i}", "von": f"C{i}", "nach": f"C{i + 1}", "diskriminierend": False, "fuel": 1, "produkt": 0})
        kanten.append({"id": f"verw{i + 1}", "von": f"C{i + 1}", "nach": "E", "diskriminierend": True, "fuel": 0, "produkt": 0})
    kanten.append({"id": "prod", "von": f"C{n}", "nach": "E", "diskriminierend": False, "fuel": 0, "produkt": 1})
    return {"name": f"hopfield_n{n}", "ungebunden": ["E"], "gebunden": gebunden, "kanten": kanten}


def validate_spec(spec, max_states=10):
    """Modellregeln prüfen. Gibt Liste von Verstößen zurück (leer = gültig)."""
    err = []; U, Bd = spec["ungebunden"], spec["gebunden"]; S = set(U) | set(Bd)
    if len(U) + 2 * len(Bd) > max_states: err.append(f"zu viele Zustände: {len(U) + 2 * len(Bd)} > {max_states}")
    ids = [k["id"] for k in spec["kanten"]]
    if len(set(ids)) != len(ids): err.append("Kanten-IDs nicht eindeutig")
    for k in spec["kanten"]:
        if k["von"] not in S or k["nach"] not in S: err.append(f"Kante {k['id']}: unbekannter Zustand")
        if k["von"] == k["nach"]: err.append(f"Kante {k['id']}: Schleife")
        if k.get("diskriminierend") and not (k["von"] in Bd and k["nach"] in U): err.append(f"Kante {k['id']}: diskriminierend nur für gebunden -> ungebunden erlaubt")
        if k.get("produkt") and not (k["von"] in Bd and k["nach"] in U): err.append(f"Kante {k['id']}: Produktkante muss gebunden -> ungebunden sein")
    if not any(k.get("produkt") for k in spec["kanten"]): err.append("keine Produktkante")
    # Zusammenhang
    adj = {s: set() for s in S}
    for k in spec["kanten"]: adj[k["von"]].add(k["nach"]); adj[k["nach"]].add(k["von"])
    seen, stack = set(), [next(iter(S))]
    while stack:
        s = stack.pop()
        if s in seen: continue
        seen.add(s); stack += list(adj[s] - seen)
    if seen != S: err.append("Netzwerk nicht zusammenhängend")
    return err


def tree_and_chords(spec):
    """Aufspannender Baum (BFS ab dem ersten ungebundenen Zustand) über der R-Topologie; Rest = Sehnen."""
    S = spec["ungebunden"] + spec["gebunden"]; root = spec["ungebunden"][0]
    tree, seen, queue = [], {root}, [root]
    while queue:
        u = queue.pop(0)
        for k in spec["kanten"]:
            for a, b in ((k["von"], k["nach"]), (k["nach"], k["von"])):
                if a == u and b not in seen: seen.add(b); queue.append(b); tree.append(k["id"])
    chords = [k["id"] for k in spec["kanten"] if k["id"] not in tree]
    return tree, chords


def param_names(spec):
    """Freie Parameter (log-Raten): Baumkanten Vor+Rück, Sehnen nur Vor; dazu log_gamma (= mu) und log_gamma_p (= mu_P)."""
    tree, chords = tree_and_chords(spec); names = []
    for k in spec["kanten"]:
        names.append(f"{k['id']}+")
        if k["id"] in tree: names.append(f"{k['id']}-")
    return names + ["mu", "muP"]


# ------------------------------------------------------------------------------------------- Raten (generisch: float, Fraction)
def build_rates(spec, p, exp, ed, num=float):
    """p: Parameter (log-Skala, wenn exp gegeben; sonst bereits Raten bzw. p['mu'] = e^mu, p['muP'] = e^muP).
    ed: e^Delta im gleichen Zahlentyp. Gibt (Zustände, Raten {(i, j): k}) des gemeinsamen R/W-Netzwerks zurück.

    R-Zweig: Baumkanten haben freie Vor- und Rückraten, Sehnen eine freie Vorrate; die Sehnen-Rückrate folgt aus
    ln(k_vor/k_rück) = phi_u - phi_v + a_e (Potentiale phi entlang des Baums). W-Zweig: identisch bis auf Kanten
    gebunden -> ungebunden: diskriminierend -> Vorrate * e^Delta, sonst -> Rückrate * e^-Delta. Jeder Zyklus tritt gleich oft
    aus gebundenen Zuständen aus wie ein, daher bleibt die Bilanz (Zyklus-Affinität = Treibstoff) im W-Zweig erhalten."""
    X = (lambda name: exp(p[name])) if exp else (lambda name: p[name])
    G, GP = X("mu"), X("muP"); tree, chords = tree_and_chords(spec)
    Bd = set(spec["gebunden"]); U = spec["ungebunden"]
    A = {k["id"]: (G ** k.get("fuel", 0)) * (GP ** k.get("produkt", 0)) for k in spec["kanten"]}
    kR = {}
    Ephi = {U[0]: num(1)}; changed = True                      # exp(phi): f/b = Ephi_u/Ephi_v * A
    while changed:
        changed = False
        for k in spec["kanten"]:
            if k["id"] not in tree: continue
            u, v = k["von"], k["nach"]; f, b = X(f"{k['id']}+"), X(f"{k['id']}-")
            if u in Ephi and v not in Ephi: Ephi[v] = Ephi[u] * A[k["id"]] * b / f; changed = True
            elif v in Ephi and u not in Ephi: Ephi[u] = Ephi[v] * f / (A[k["id"]] * b); changed = True
    for k in spec["kanten"]:
        f = X(f"{k['id']}+")
        b = X(f"{k['id']}-") if k["id"] in tree else f * Ephi[k["nach"]] / (Ephi[k["von"]] * A[k["id"]])
        kR[k["id"]] = (f, b)
    states = list(U) + [f"{b}_R" for b in spec["gebunden"]] + [f"{b}_W" for b in spec["gebunden"]]
    edges = []
    for branch in ("R", "W"):
        nm = lambda s: s if s in U else f"{s}_{branch}"
        for k in spec["kanten"]:
            u, v = k["von"], k["nach"]; f, b = kR[k["id"]]
            if branch == "W":
                if u in Bd and v not in Bd:
                    if k.get("diskriminierend"): f = f * ed
                    else: b = b / ed
                elif v in Bd and u not in Bd:                      # Kante ungebunden -> gebunden: Regel auf die Gegenrichtung
                    if k.get("diskriminierend"): b = b * ed
                    else: f = f / ed
            if branch == "W" and u not in Bd and v not in Bd: continue   # Kanten zwischen ungebundenen Zuständen nur einmal
            edges.append({"u": nm(u), "v": nm(v), "f": f, "b": b, "id": k["id"], "zweig": branch,
                          "a": A[k["id"]], "produkt": bool(k.get("produkt"))})
    return states, edges


# ------------------------------------------------------------------------------------------- Steady State und Kennzahlen (float)
def steady_state_float(states, edges):
    n = len(states); idx = {s: i for i, s in enumerate(states)}; Q = np.zeros((n, n))
    for e in edges: Q[idx[e["u"]], idx[e["v"]]] += e["f"]; Q[idx[e["v"]], idx[e["u"]]] += e["b"]
    np.fill_diagonal(Q, 0); np.fill_diagonal(Q, -Q.sum(1)); M = Q.T.copy(); M[-1, :] = 1.0; rhs = np.zeros(n); rhs[-1] = 1.0
    return dict(zip(states, np.linalg.solve(M, rhs)))


def metrics_float(spec, logp, delta=DELTA):
    states, edges = build_rates(spec, logp, math.exp, math.exp(delta))
    pi = steady_state_float(states, edges); J = {"R": 0.0, "W": 0.0}; ep = 0.0
    for e in edges:
        net = pi[e["u"]] * e["f"] - pi[e["v"]] * e["b"]; ep += net * math.log(e["f"] / e["b"])
        if e["produkt"]: J[e["zweig"]] += net
    tot = J["R"] + J["W"]; maxlog = max(max(abs(math.log(e["f"])), abs(math.log(e["b"]))) for e in edges)
    return {"eta": J["W"] / J["R"] if J["R"] > 0 else float("inf"), "sigma": ep / tot if tot > 0 else float("inf"),
            "v": J["R"], "J_W": J["W"], "ep": ep, "max_abs_log_rate": maxlog}


# ------------------------------------------------------------------------------------------- exakt (Fraction + arb)
def rationalize(logp, max_den=10 ** 6):
    """log-Parameter -> rationale Raten (Fraction), nahe exp(x). Rationale Raten sind der Zertifikats-Input."""
    return {k: Fraction(math.exp(v)).limit_denominator(max_den) if math.exp(v) < 1e6 else Fraction(round(math.exp(v))) for k, v in logp.items()}


def metrics_exact(spec, ratp, ed=Fraction(100)):
    """Exakte Kennzahlen: eta, v rational (sympy, LU in rationaler Arithmetik); sigma als rigoroser arb-Einschluss."""
    import sympy as sp
    from flint import arb, ctx
    states, edges = build_rates(spec, ratp, None, ed, num=Fraction)
    n = len(states); idx = {s: i for i, s in enumerate(states)}; R = lambda fr: sp.Rational(fr.numerator, fr.denominator)
    Q = sp.zeros(n, n)
    for e in edges: Q[idx[e["u"]], idx[e["v"]]] += R(e["f"]); Q[idx[e["v"]], idx[e["u"]]] += R(e["b"])
    for i in range(n): Q[i, i] = -sum(Q[i, j] for j in range(n) if j != i)
    M = Q.T.copy(); M[n - 1, :] = sp.ones(1, n); rhs = sp.zeros(n, 1); rhs[n - 1] = 1
    pv = M.LUsolve(rhs); pi = {s: sp.Rational(pv[idx[s]]) for s in states}
    J = {"R": sp.Integer(0), "W": sp.Integer(0)}; ctx.prec = 200; ep = arb(0); fl = []
    for e in edges:
        net = pi[e["u"]] * R(e["f"]) - pi[e["v"]] * R(e["b"]); ratio = e["f"] / e["b"]
        ep += arb(int(sp.numer(net))) / arb(int(sp.denom(net))) * (arb(ratio.numerator) / arb(ratio.denominator)).log()
        fl.append({"kante": e["id"], "zweig": e["zweig"], "netto": str(net), "k_vor/k_rück": f"{ratio.numerator}/{ratio.denominator}"})
        if e["produkt"]: J[e["zweig"]] += net
    tot = J["R"] + J["W"]; sig = ep * arb(int(sp.denom(tot))) / arb(int(sp.numer(tot)))
    return {"eta": J["W"] / J["R"], "v": J["R"], "J_W": J["W"], "sigma_arb": sig, "sigma_lo": float(sig.lower()),
            "sigma_hi": float(sig.upper()), "pi": pi, "edges": edges, "fluesse": fl}


def check_ldb_exact(spec, ratp, ed=Fraction(100)):
    """Red-Team-Prüfung: lokale detaillierte Bilanz exakt für eine Zyklusbasis des Multigraphen (inkl. Parallelkanten).
    Für jeden Basiszyklus muss prod(k_vor/k_rück) = prod(e^Affinität) gelten. Gibt die verletzten Zyklen zurück."""
    import networkx as nx
    states, edges = build_rates(spec, ratp, None, ed, num=Fraction)
    G = nx.MultiGraph()
    for j, e in enumerate(edges): G.add_edge(e["u"], e["v"], key=j)
    T = nx.minimum_spanning_tree(G); bad = []
    tree_keys = {k for _, _, k in T.edges(keys=True)}
    for j, e in enumerate(edges):
        if j in tree_keys: continue
        path = nx.shortest_path(T, e["v"], e["u"])                  # Zyklus: u -> v über Kante j, zurück über den Baum
        prod_k, prod_a = e["f"] / e["b"], e["a"]
        for x, y in zip(path[:-1], path[1:]):
            k = next(kk for kk in T[x][y]); ee = edges[k]
            if ee["u"] == x: prod_k *= ee["f"] / ee["b"]; prod_a *= ee["a"]
            else: prod_k *= ee["b"] / ee["f"]; prod_a /= ee["a"]
        if prod_k != prod_a: bad.append({"sehne": e["id"], "zweig": e["zweig"], "verhaeltnis": str(prod_k), "soll": str(prod_a)})
    return bad
