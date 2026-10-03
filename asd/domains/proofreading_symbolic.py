"""Zertifikat (b), symbolisch: untere Schranke eta >= c * e^(-k*Delta) für ALLE positiven Raten und jeden Treibstoff mu, mu_P >= 0.

Methode: eta wird in sympy exakt als rationale Funktion der Raten berechnet (Steady State per LU in rationalen Funktionen).
Mit e^mu = 1 + g_mu, e^mu_P = 1 + g_muP, e^Delta = 1 + d (alle g, d >= 0, Raten > 0) wird eta - c*e^(-k*Delta) = N/Dn gebildet.
Haben N und Dn nur nichtnegative Koeffizienten (und ist Dn nicht null), ist die Ungleichung für alle zulässigen Werte bewiesen.
Scheitert das Kriterium, ist die Aussage NICHT widerlegt, nur nicht zertifiziert (hinreichende, nicht notwendige Bedingung).
Läuft als eigener Prozess mit Zeitlimit: python -m asd.domains.proofreading_symbolic '<json>'
"""
import json, sys, time
import sympy as sp
from . import proofreading as P


def _arborescences(states, out_edges, root):
    """Alle aufspannenden Bäume, die zur Wurzel hin gerichtet sind (jeder Nicht-Wurzel-Knoten wählt genau eine ausgehende Kante)."""
    others = [s for s in states if s != root]
    for choice in __import__("itertools").product(*[out_edges[s] for s in others]):
        parent = {s: c[0] for s, c in zip(others, choice)}
        ok = True
        for s in others:                                   # zykelfrei: jeder Pfad endet an der Wurzel
            seen, x = set(), s
            while x != root:
                if x in seen: ok = False; break
                seen.add(x); x = parent[x]
            if not ok: break
        if ok: yield [c[1] for c in choice]


def symbolic_eta(spec):
    """eta exakt über das Matrix-Tree-Theorem: pi_i ~ Summe über Bäume zur Wurzel i des Produkts der Raten (nur positive Terme)."""
    names = P.param_names(spec); syms = {}
    for n in names:
        syms[n] = 1 + sp.Symbol("g_" + n, nonnegative=True) if n in ("mu", "muP") else sp.Symbol("k_" + n.replace("+", "f").replace("-", "b"), positive=True)
    D = sp.Symbol("D", positive=True)
    states, edges = P.build_rates(spec, syms, None, D, num=lambda x: sp.Integer(x))
    out = {s: [] for s in states}
    for e in edges: out[e["u"]].append((e["v"], e["f"])); out[e["v"]].append((e["u"], e["b"]))
    w = {}
    for r in states:
        w[r] = sp.Add(*[sp.Mul(*rs) for rs in _arborescences(states, out, r)])
    J = {"R": 0, "W": 0}
    for e in edges:
        if e["produkt"]: J[e["zweig"]] += w[e["u"]] * e["f"] - w[e["v"]] * e["b"]     # Normierung kürzt sich in eta heraus
    return sp.cancel(sp.together(J["W"] / J["R"])), D


ALLOWED = {"D", "G", "GP"}


def parse_bound(expr):
    """Schranke als sympy-Ausdruck in D = e^Delta, G = e^mu, GP = e^mu_P (nur diese Symbole, nur rationale Arithmetik)."""
    loc = {n: sp.Symbol(n, positive=True) for n in ALLOWED}
    e = sp.sympify(expr, locals=loc, rational=True)
    if not e.free_symbols <= set(loc.values()) or e.has(sp.exp, sp.log, sp.Function): raise ValueError("nur D, G, GP und rationale Arithmetik erlaubt")
    return e, loc


def prove_lower_bound(spec, c, k, ausdruck=None):
    t0 = time.time(); eta, D = symbolic_eta(spec); d = sp.Symbol("d", nonnegative=True)
    if ausdruck:
        e, loc = parse_bound(ausdruck); g, gp = sp.Symbol("g_mu", nonnegative=True), sp.Symbol("g_muP", nonnegative=True)
        bound = e.subs({loc["D"]: D, loc["G"]: 1 + g, loc["GP"]: 1 + gp})
    else:
        bound = sp.Rational(c) * D ** (-k)
    num, den = sp.fraction(sp.together(eta - bound))
    num, den = sp.expand(num.subs(D, 1 + d)), sp.expand(den.subs(D, 1 + d))
    gens = sorted((num.free_symbols | den.free_symbols), key=str)
    cn = sp.Poly(num, *gens).coeffs(); cd = sp.Poly(den, *gens).coeffs()
    sn = all(x >= 0 for x in cn) and any(x > 0 for x in cn); sd = all(x >= 0 for x in cd) and any(x > 0 for x in cd)
    sn2 = all(x <= 0 for x in cn) and any(x < 0 for x in cn); sd2 = all(x <= 0 for x in cd) and any(x < 0 for x in cd)
    ok = (sn and sd) or (sn2 and sd2)
    return {"bewiesen": bool(ok), "terme_zaehler": len(cn), "terme_nenner": len(cd), "min_koeff_zaehler": str(min(cn)), "min_koeff_nenner": str(min(cd)),
            "sek": round(time.time() - t0, 1), "methode": "Positivität aller Koeffizienten nach Substitution e^Delta = 1 + d, e^mu = 1 + g"}


if __name__ == "__main__":
    a = json.loads(sys.argv[1]); spec = P.hopfield_chain(int(a["topologie"].split("n")[-1])) if isinstance(a["topologie"], str) else a["topologie"]
    print(json.dumps(prove_lower_bound(spec, a.get("c", "1"), int(a.get("k", 0)), a.get("ausdruck"))))
