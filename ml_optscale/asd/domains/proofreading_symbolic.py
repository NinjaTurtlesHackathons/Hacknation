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


def symbolic_eta(spec):
    names = P.param_names(spec); syms = {}
    for n in names:
        syms[n] = 1 + sp.Symbol("g_" + n, nonnegative=True) if n in ("mu", "muP") else sp.Symbol("k_" + n.replace("+", "f").replace("-", "b"), positive=True)
    D = sp.Symbol("D", positive=True)
    states, edges = P.build_rates(spec, syms, None, D, num=lambda x: sp.Integer(x))
    n = len(states); idx = {s: i for i, s in enumerate(states)}; Q = sp.zeros(n, n)
    for e in edges: Q[idx[e["u"]], idx[e["v"]]] += e["f"]; Q[idx[e["v"]], idx[e["u"]]] += e["b"]
    for i in range(n): Q[i, i] = -sum(Q[i, j] for j in range(n) if j != i)
    M = Q.T.copy(); M[n - 1, :] = sp.ones(1, n); rhs = sp.zeros(n, 1); rhs[n - 1] = 1
    pv = M.LUsolve(rhs); pi = {s: pv[idx[s]] for s in states}; J = {"R": 0, "W": 0}
    for e in edges:
        if e["produkt"]: J[e["zweig"]] += pi[e["u"]] * e["f"] - pi[e["v"]] * e["b"]
    return sp.cancel(sp.together(J["W"] / J["R"])), D


def prove_lower_bound(spec, c, k):
    t0 = time.time(); eta, D = symbolic_eta(spec); d = sp.Symbol("d", nonnegative=True)
    num, den = sp.fraction(sp.together(eta - sp.Rational(c) * D ** (-k)))
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
    print(json.dumps(prove_lower_bound(spec, a.get("c", "1"), int(a["k"]))))
