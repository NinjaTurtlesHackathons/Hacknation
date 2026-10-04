"""Domäne: quivers — Darstellungstheorie von Köchern, unzerlegbare Darstellungen nicht-Dynkin'scher Köcher.

Prüfer (alle exakt):
  * Tits-Form: Hauptminoren in rationaler Arithmetik (endlich / zahm / wild), Radikal, Kac' Wurzel-Reduktion.
  * Unzerlegbarkeit über Q̄: dim End(V) - dim J(End V) = 1, J als Kern der Spurform (Charakteristik 0).
  * Familien V_t: Gauß-Elimination über Q(t) bzw. Q(s, t) mit protokollierten Pivots (Zertifikat für alle t außerhalb
    der genannten Ausnahmen): End(V_t) = k und Hom(V_s, V_t) = 0 für s != t.
  * Zählen über F_p: I_alpha(p) = Anzahl Isoklassen Unzerlegbarer. Der Prüfer zählt direkt (alle Darstellungen aufzählen,
    End vollständig aufzählen, Lokalität testen, Bahnformel), wenn |Rep_alpha(F_p)| <= 20000; sonst über die Burnside-Summe
    und den plethystischen Logarithmus (Krull-Schmidt). Welche Methode lief, steht in der Begründung und in describe().
Toleranzen gibt es keine (alles exakt); Felder wie "toleranz" in der Behauptung werden ignoriert.
"""
import math
from fractions import Fraction as Fr
from .base import Domain
from . import quivers as K

BRUTE_MAX = 20000
PRIMES = (2, 3, 5, 7, 11, 13, 17)


def _Q(p): return K.quiver(p["quiver"])


def _alpha(p, Q, key="alpha"):
    a = [int(x) for x in p[key]]
    if len(a) != Q[0] or any(x < 0 for x in a): raise ValueError(f"{key} muss {Q[0]} nichtnegative ganze Zahlen haben")
    return a


def _prime(p):
    q = int(p["p"])
    if q < 2 or any(q % d == 0 for d in range(2, int(q ** 0.5) + 1)): raise ValueError("p muss eine Primzahl sein")
    return q


def method_for(Q, a, q):
    return "direkt" if K.rep_space_size(Q, a, q) <= BRUTE_MAX else "burnside"


def count_I(Q, a, q):
    """Prüfer-Zählung von I_a(q) mit der in method_for festgelegten Methode."""
    if method_for(Q, a, q) == "direkt": return K.brute_indecomposables(Q, tuple(a), q), "direkt"
    I, _ = K.indecomposable_counts(Q, tuple(a), q); return I[tuple(a)], "burnside"


def _check_rep_dims(Q, V, a=None):
    n, A = Q
    if len(V["dims"]) != n: raise ValueError("dims passt nicht zum Köcher")
    if a is not None and list(V["dims"]) != list(a): raise ValueError("Dimensionsvektor der Darstellung != alpha")
    for k, (s, t) in enumerate(A):
        m = V["maps"].get(str(k))
        if m is not None and (len(m) != V["dims"][t] or any(len(r) != V["dims"][s] for r in m)):
            raise ValueError(f"Pfeil {k}: Matrix muss {V['dims'][t]}x{V['dims'][s]} sein")


class QuiverDomain(Domain):
    name = "quivers"
    recherche_ziel = ("Darstellungstheorie von Köchern: Gabriels Satz, euklidische (zahme) Köcher, Kac' Satz und Kac-Polynome, "
                      "Klassifikation unzerlegbarer Darstellungen von Stern-Köchern (Vier-Unterraum-Problem) und Zykeln.")
    recherche_sperre = []
    recherche_klassiker = ["Gabriel Unzerlegbare Darstellungen", "Bernstein Gelfand Ponomarev Coxeter functors",
                           "Kac infinite root systems representations of graphs", "Kac root systems representations of quivers invariant theory",
                           "Gelfand Ponomarev four subspaces", "Nazarova representations of quivers of infinite type",
                           "Donovan Freislich representation theory of finite graphs", "Ringel tame algebras integral quadratic forms",
                           "Hua counting representations of quivers over finite fields",
                           "Hausel Letellier Rodriguez-Villegas positivity Kac polynomials"]
    recherche_crossref = True
    kontext = ("Ein Köcher Q = (Q_0, Q_1, s, t); eine Darstellung V ordnet jeder Ecke i einen Vektorraum V_i und jedem Pfeil a: i -> j "
               "eine lineare Abbildung V_a: V_i -> V_j zu. Dimensionsvektor dim V in N^{Q_0}. Tits-Form q(x) = sum x_i^2 - sum_a x_s(a) x_t(a). "
               "Köcher in diesem Labor: A2, A3, star<n> (Zentrum 0, n Blätter, Pfeile Blatt -> Zentrum), cycle3_oriented, cycle3_acyclic, "
               "cycle4_oriented, cycle4_acyclic31, cycle4_acyclic22, kronecker. Ziel: die unendlich vielen Isoklassen unzerlegbarer "
               "Darstellungen nicht-Dynkin'scher Köcher beschreiben (Dimensionsvektoren, Parameterzahl, explizite Familien, Zählung über F_p).")
    primitive_doc = """Experimente (JSON {"op": ..., "args": {...}}):
- tits_typ {quiver}; radikal {quiver}; wurzel {quiver, alpha}; wurzeln {quiver, schranke}: alle Vektoren <= schranke mit Wurzelart.
- unzerlegbar {quiver, rep}: dim End, dim Radikal über Q.
- familie {quiver, rep (Einträge Polynome in t), ausnahmen}: Zertifikatsversuch für End(V_t) = k und Hom(V_s, V_t) = 0.
- anzahl {quiver, alpha, p}: I_beta(p) für alle beta <= alpha (Burnside + Krull-Schmidt).
- normalformen {quiver, alpha, p}: Vertreter aller Isoklassen Unzerlegbarer über F_p (klein!).
- interpolation {quiver, alpha, grad}: I_alpha(p) für p = 2, 3, 5, 7 und Lagrange-Polynom vom Grad grad."""
    claim_doc = """Prüfungstypen:
- {"typ": "tits_typ", "quiver", "typ_wert": "endlich"|"zahm"|"wild"}
- {"typ": "radikal", "quiver", "delta": [...]}             minimaler positiver Erzeuger des Radikals
- {"typ": "wurzel", "quiver", "alpha", "art": "reell"|"imaginaer"|"keine"}
- {"typ": "wurzelzahl", "quiver", "anzahl"}                Zahl der positiven Wurzeln (nur endlicher Typ)
- {"typ": "parameter", "quiver", "alpha", "anzahl"}         1 - q(alpha) für eine imaginäre Wurzel
- {"typ": "unzerlegbar", "quiver", "rep", "wert": bool}     absolut unzerlegbar über Q̄
- {"typ": "familie", "quiver", "rep", "ausnahmen": [...]}   für alle t außerhalb: Ziegel, paarweise nicht isomorph
- {"typ": "anzahl", "quiver", "alpha", "p", "anzahl"}       I_alpha(p)
- {"typ": "kac_polynom", "quiver", "alpha", "koeffizienten": [c0, c1, ...] | "formel": "Ausdruck in q"}  A_alpha(q) an deg + 2 Primzahlen
- {"typ": "klassifikation", "quiver", "alpha", "p", "reps": [...]}  vollständige Liste der Isoklassen Unzerlegbarer über F_p
- {"typ": "kac_box", "quiver", "schranke", "p"}             für alle 0 < beta <= schranke: I_beta(p) = 1 (reelle Wurzel), 0 (keine Wurzel)
- {"typ": "zykel_box", "quiver": "cycle<n>_oriented", "schranke", "p"}  I_beta(p) = Vorhersage (Strings + Monodromie) für alle beta <= schranke"""

    # ------------------------------------------------------------------ Experimente
    def run_op(self, op, args):
        try:
            Q = K.quiver(args["quiver"])
            if op == "tits_typ": t, w = K.tits_type(Q); return {"typ": t, "zeugen": w}
            if op == "radikal": d, k = K.radical(Q); return {"delta": d, "dim_radikal": k}
            if op == "wurzel":
                a = args["alpha"]; return {"art": K.root_kind(Q, a), "q": K.tits(Q, a), "parameter": 1 - K.tits(Q, a)}
            if op == "wurzeln":
                return {"wurzeln": [(b, K.root_kind(Q, b), K.tits(Q, b)) for b in K.box(args["schranke"]) if any(b) and K.root_kind(Q, b) != "keine"]}
            if op == "unzerlegbar":
                ok, e, j = K.abs_indecomposable_Q(Q, args["rep"]); return {"unzerlegbar": ok, "dim_end": e, "dim_radikal": j}
            if op == "familie": return K.family_certificate(Q, args["rep"], ausnahmen=args.get("ausnahmen", []))
            if op == "anzahl":
                I, M = K.indecomposable_counts(Q, tuple(args["alpha"]), int(args["p"]))
                return {"I": {str(list(b)): v for b, v in I.items() if v}, "M_alpha": M[tuple(args["alpha"])]}
            if op == "normalformen":
                R = K.normal_forms(Q, tuple(args["alpha"]), int(args["p"])); return {"anzahl": len(R), "reps": R}
            if op == "interpolation":
                vals = {q: K.indecomposable_counts(Q, tuple(args["alpha"]), q)[0][tuple(args["alpha"])] for q in PRIMES[: int(args["grad"]) + 2]}
                import sympy as sp
                x = sp.Symbol("q"); pts = list(vals.items())[: int(args["grad"]) + 1]
                poly = sp.expand(sp.interpolate([(a, b) for a, b in pts], x))
                return {"werte": vals, "polynom": str(poly), "koeffizienten": [str(poly.coeff(x, i)) for i in range(int(args["grad"]) + 1)]}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    # ------------------------------------------------------------------ Prüfer
    def check(self, p):
        try:
            return self._check(p)
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def _check(self, p):
        typ = p.get("typ"); Q = _Q(p)
        if typ == "tits_typ":
            t, w = K.tits_type(Q); return t == p["typ_wert"], f"Tits-Form ist {t} (exakt, Hauptminoren): {w}", w
        if typ == "radikal":
            d, k = K.radical(Q); return d == [int(x) for x in p["delta"]], f"Radikal: Dimension {k}, Erzeuger {d}", {"delta": d}
        if typ == "wurzel":
            a = _alpha(p, Q); r = K.root_kind(Q, a)
            return r == p["art"], f"Kac-Reduktion: {a} ist {r} (q = {K.tits(Q, a)})", {"art": r}
        if typ == "wurzelzahl":
            if K.tits_type(Q)[0] != "endlich": return False, "nur für endlichen Typ definiert", {}
            R = K.positive_roots(Q); return len(R) == int(p["anzahl"]), f"{len(R)} positive Wurzeln (W-Bahn der einfachen Wurzeln): {R}", {"wurzeln": R}
        if typ == "parameter":
            a = _alpha(p, Q); r = K.root_kind(Q, a); v = 1 - K.tits(Q, a)
            return r == "imaginaer" and v == int(p["anzahl"]), f"{a}: {r}, 1 - q = {v}", {"parameter": v}
        if typ == "unzerlegbar":
            V = p["rep"]; _check_rep_dims(Q, V); ok, e, j = K.abs_indecomposable_Q(Q, V)
            return ok == bool(p["wert"]), f"dim End = {e}, dim J(End) = {j}: {'absolut unzerlegbar' if ok else 'zerlegbar über Q̄'}", {"dim_end": e, "dim_rad": j}
        if typ == "familie":
            V = p["rep"]; _check_rep_dims(Q, V); aus = [str(x) for x in p.get("ausnahmen", [])]
            c = K.family_certificate(Q, V, ausnahmen=aus)
            ok = c["dim_end_max"] == 1 and c["dim_hom_max"] == 0
            return ok, (f"Elimination über Q(t): rang(End-System) = {c['rang_end']} von {c['N']} (dim End <= {c['dim_end_max']}), Pivot-Faktoren {c['pivots_end']}; "
                        f"Hom(V_s, V_t): rang {c['rang_hom']} (dim Hom <= {c['dim_hom_max']}), Pivot-Faktoren {c['pivots_hom']}; gültig für t, s außerhalb {aus}, s != t"), c
        if typ == "anzahl":
            a = _alpha(p, Q); q = _prime(p); v, m = count_I(Q, a, q)
            return v == int(p["anzahl"]), f"I_{a}({q}) = {v} (Methode: {m})", {"I": v, "methode": m}
        if typ == "kac_polynom":
            a = _alpha(p, Q)
            if p.get("formel") is not None:                                  # geschlossene Formel in q -> muss ein Polynom sein
                import sympy as sp
                x = sp.Symbol("q"); e = sp.cancel(sp.sympify(p["formel"], locals={"q": x}))
                if not e.is_polynomial(x): return False, f"Formel {p['formel']} ist kein Polynom in q", {}
                P_ = sp.Poly(e, x); co = [Fr(str(P_.coeff_monomial(x ** i))) for i in range(P_.degree() + 1)]
            else:
                co = [Fr(str(c)) for c in p["koeffizienten"]]
            if math.gcd(*a) != 1: return False, "alpha muss unteilbar sein (dann I_alpha = A_alpha)", {}
            deg = 1 - K.tits(Q, a)
            if len(co) - 1 != deg: return False, f"Grad {len(co) - 1} != 1 - q(alpha) = {deg} (Kac)", {}
            got = {}; prs = PRIMES[: max(4, deg + 2)]
            for q in prs:
                got[q] = count_I(Q, a, q); want = sum(c * q ** i for i, c in enumerate(co))
                if got[q][0] != want: return False, f"q = {q}: gezählt {got[q][0]}, Polynom {want}", {"werte": got}
            if len(prs) < deg + 2: return False, "zu wenige Stützstellen", {}
            return True, f"A_{a}(q) stimmt an q = {list(prs)} (Methoden {[m for _, m in got.values()]}) mit dem Polynom überein; Grad {deg} = 1 - q(alpha)", {"werte": got}
        if typ == "klassifikation":
            a = _alpha(p, Q); q = _prime(p); R = p["reps"]
            for V in R:
                _check_rep_dims(Q, V, a)
                V["maps"] = {k: [[int(x) % q for x in r] for r in m] for k, m in V["maps"].items()}
                for k in range(len(Q[1])): V["maps"].setdefault(str(k), [[0] * a[Q[1][k][0]] for _ in range(a[Q[1][k][1]])])
                if not K.local_aut(Q, V, q)[0]: return False, f"nicht unzerlegbar über F_{q}: {V['maps']}", {}
            for i in range(len(R)):
                for j in range(i):
                    if K.iso_mod(Q, R[i], R[j], q): return False, f"Liste enthält isomorphe Darstellungen ({j}, {i})", {}
            v, m = count_I(Q, a, q)
            return v == len(R), f"{len(R)} paarweise nicht isomorphe Unzerlegbare über F_{q}; Zählung I = {v} (Methode {m}) -> Liste {'vollständig' if v == len(R) else 'unvollständig'}", {"I": v}
        if typ == "kac_box":
            B = _alpha(p, Q, "schranke"); q = _prime(p); I, _ = K.indecomposable_counts(Q, tuple(B), q); bad, imag = [], {}
            for b, v in I.items():
                r = K.root_kind(Q, b)
                if r == "imaginaer": imag[str(list(b))] = v; continue
                if v != (1 if r == "reell" else 0): bad.append((b, r, v))
            return (not bad and not (K.tits_type(Q)[0] == "endlich" and imag)), (
                f"{len(I)} Vektoren <= {B} über F_{q}: reelle Wurzeln genau 1, Nicht-Wurzeln 0" + (f"; Abweichungen {bad[:5]}" if bad else "")
                + (f"; imaginäre Wurzeln: {imag}" if imag else "")), {"imaginaer": imag}
        if typ == "zykel_box":
            name = str(p["quiver"])
            if not (name.startswith("cycle") and name.endswith("_oriented")): return False, "nur orientierte Zykel", {}
            B = _alpha(p, Q, "schranke"); q = _prime(p); I, _ = K.indecomposable_counts(Q, tuple(B), q)
            bad = [(b, v, K.cycle_prediction(Q[0], b, q)) for b, v in I.items() if v != K.cycle_prediction(Q[0], b, q)]
            return not bad, f"{len(I)} Dimensionsvektoren <= {B} über F_{q}: Zählung = Vorhersage (Strings + Monodromie)" + (f"; Abweichungen {bad[:5]}" if bad else ""), {"n": len(I)}
        return False, f"unbekannter Prüfungstyp {typ}", {}

    # ------------------------------------------------------------------ kanonische Aussagen
    def describe(self, p):
        t = p.get("typ"); qn = p.get("quiver")
        if t == "tits_typ":
            m = {"endlich": "positiv definit (endlicher Typ: Dynkin)", "zahm": "positiv semidefinit, nicht definit (euklidisch, zahm)",
                 "wild": "indefinit (wild)"}[p["typ_wert"]]
            return f"Die Tits-Form von {qn} ist {m} (exakte Hauptminoren)."
        if t == "radikal": return f"Das Radikal der Tits-Form von {qn} ist eindimensional, erzeugt von delta = {p['delta']}."
        if t == "wurzel":
            return f"Für {qn} ist {p['alpha']} " + {"reell": "eine positive reelle Wurzel", "imaginaer": "eine positive imaginäre Wurzel",
                                                    "keine": "keine Wurzel"}[p["art"]] + " (Kac-Reduktion, exakt)."
        if t == "wurzelzahl": return f"{qn} hat genau {p['anzahl']} positive Wurzeln."
        if t == "parameter": return f"Für {qn} ist {p['alpha']} eine imaginäre Wurzel mit 1 - q(alpha) = {p['anzahl']}."
        if t == "unzerlegbar":
            return f"Die Darstellung von {qn} mit Dimensionsvektor {p['rep']['dims']} und Abbildungen {p['rep']['maps']} ist " + (
                "absolut unzerlegbar (End/Rad = k)." if p["wert"] else "über dem algebraischen Abschluss zerlegbar.")
        if t == "familie":
            return (f"Für {qn}: die Familie V_t mit Dimensionsvektor {p['rep']['dims']} und Abbildungen {p['rep']['maps']} erfüllt für alle t außerhalb "
                    f"{p.get('ausnahmen', [])}: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s, V_t) = 0 für s != t (paarweise nicht isomorph); "
                    "Zertifikat: Elimination über Q(s, t) mit protokollierten Pivots.")
        if t == "anzahl":
            Q = _Q(p); m = method_for(Q, [int(x) for x in p["alpha"]], int(p["p"]))
            return f"Über F_{p['p']} hat {qn} genau {p['anzahl']} Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor {p['alpha']} (exakte Zählung, Methode {m})."
        if t == "kac_polynom" and p.get("formel") is not None:
            return (f"Für {qn} und alpha = {p['alpha']} stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit "
                    f"{p['formel']} überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.")
        if t == "kac_polynom":
            poly = " + ".join(f"{c}*q^{i}" for i, c in enumerate(p["koeffizienten"]) if str(c) != "0")
            return (f"Für {qn} und alpha = {p['alpha']} ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = {', '.join(map(str, PRIMES[: max(4, len(p['koeffizienten']) + 1)]))} gleich {poly}; "
                    "da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.")
        if t == "klassifikation":
            return f"Über F_{p['p']} ist die angegebene Liste von {len(p['reps'])} Darstellungen von {qn} mit Dimensionsvektor {p['alpha']} eine vollständige Liste der Isoklassen Unzerlegbarer."
        if t == "kac_box":
            return f"Für {qn} über F_{p['p']} und alle Dimensionsvektoren 0 < beta <= {p['schranke']}: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln."
        if t == "zykel_box":
            return (f"Für {qn} über F_{p['p']} und alle 0 < beta <= {p['schranke']} stimmt die Zahl der Unzerlegbaren mit der Klassifikation "
                    "(nilpotente Strings S(i, l) und unzerlegbare Moduln über F_q[x, 1/x] für beta = m delta) überein.")
        return super().describe(p)

    def level(self, p): return "computed_rigorous"

    def widerspricht(self, p, q):
        if p.get("typ") != q.get("typ") or str(p.get("quiver")) != str(q.get("quiver")): return False
        t = p["typ"]
        if t == "tits_typ": return p["typ_wert"] != q["typ_wert"]
        if t == "radikal": return list(p["delta"]) != list(q["delta"])
        if t == "wurzel": return list(p["alpha"]) == list(q["alpha"]) and p["art"] != q["art"]
        if t == "anzahl": return list(p["alpha"]) == list(q["alpha"]) and p["p"] == q["p"] and int(p["anzahl"]) != int(q["anzahl"])
        if t == "kac_polynom": return list(p["alpha"]) == list(q["alpha"]) and [str(x) for x in p["koeffizienten"]] != [str(x) for x in q["koeffizienten"]]
        if t == "unzerlegbar": return p["rep"] == q["rep"] and p["wert"] != q["wert"]
        return False

    def selftest(self):
        V4 = lambda l4: {"dims": [2, 1, 1, 1, 1], "maps": {"0": [[1], [0]], "1": [[0], [1]], "2": [[1], [1]], "3": l4}}
        cyc = {"dims": [2, 2, 2], "maps": {"0": [[1, 0], [0, 1]], "1": [[1, 0], [0, 1]], "2": [[3, 1], [0, 3]]}}
        cyc_split = {"dims": [2, 2, 2], "maps": {"0": [[1, 0], [0, 1]], "1": [[1, 0], [0, 1]], "2": [[3, 0], [0, 3]]}}
        rot = {"dims": [2, 2], "maps": {"0": [[1, 0], [0, 1]], "1": [[0, -1], [1, 0]]}}     # Kronecker: x^2+1 über Q irreduzibel, über Q̄ zerlegbar
        return [
            ({"typ": "tits_typ", "quiver": "star3", "typ_wert": "endlich"}, True),            # D4
            ({"typ": "tits_typ", "quiver": "star4", "typ_wert": "zahm"}, True),               # D~4
            ({"typ": "tits_typ", "quiver": "star4", "typ_wert": "endlich"}, False),           # Grenzfall: semidefinit, nicht definit
            ({"typ": "tits_typ", "quiver": "star5", "typ_wert": "zahm"}, False),
            ({"typ": "radikal", "quiver": "star4", "delta": [2, 1, 1, 1, 1]}, True),
            ({"typ": "radikal", "quiver": "star4", "delta": [4, 2, 2, 2, 2]}, False),         # nicht minimal
            ({"typ": "wurzelzahl", "quiver": "star3", "anzahl": 12}, True),                   # D4 hat 12 positive Wurzeln
            ({"typ": "wurzelzahl", "quiver": "star3", "anzahl": 11}, False),
            ({"typ": "wurzelzahl", "quiver": "star4", "anzahl": 12}, False),                  # unendlich viele
            ({"typ": "wurzel", "quiver": "star4", "alpha": [3, 1, 1, 1, 1], "art": "reell"}, True),
            ({"typ": "wurzel", "quiver": "star4", "alpha": [1, 2, 0, 0, 0], "art": "keine"}, True),
            ({"typ": "wurzel", "quiver": "star4", "alpha": [4, 2, 2, 2, 2], "art": "reell"}, False),   # 2 delta ist imaginär
            ({"typ": "wurzel", "quiver": "star4", "alpha": ["x", 1, 1, 1, 1], "art": "reell"}, False),  # Regelverletzung
            ({"typ": "parameter", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "anzahl": 2}, True),
            ({"typ": "parameter", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "anzahl": 1}, False),
            ({"typ": "unzerlegbar", "quiver": "star4", "rep": V4([[1], [2]]), "wert": True}, True),
            ({"typ": "unzerlegbar", "quiver": "star4", "rep": V4([[0], [1]]), "wert": True}, True),      # L2 = L4, sonst verschieden: Ziegel (Röhre)
            ({"typ": "unzerlegbar", "quiver": "star4", "rep": {"dims": [2, 1, 1, 1, 1], "maps": {"0": [[1], [0]], "1": [[1], [0]], "2": [[0], [1]], "3": [[0], [1]]}}, "wert": False}, True),
            ({"typ": "unzerlegbar", "quiver": "cycle3_oriented", "rep": cyc, "wert": True}, True),       # Jordanblock J_2(3)
            ({"typ": "unzerlegbar", "quiver": "cycle3_oriented", "rep": cyc_split, "wert": True}, False),
            ({"typ": "unzerlegbar", "quiver": "kronecker", "rep": rot, "wert": True}, False),            # über Q unzerlegbar, über Q̄ nicht
            ({"typ": "familie", "quiver": "star4", "rep": V4([[1], ["t"]]), "ausnahmen": [0, 1]}, True),
            ({"typ": "familie", "quiver": "star4", "rep": V4([[1], ["t"]]), "ausnahmen": []}, True),     # auch t = 0, 1 sind Ziegel
            ({"typ": "familie", "quiver": "star4", "rep": V4([["t"], [0]]), "ausnahmen": [0]}, False),  # V_s ≅ V_t: keine echte Familie
            ({"typ": "anzahl", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 3, "anzahl": 7}, True),
            ({"typ": "anzahl", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 3, "anzahl": 6}, False),
            ({"typ": "anzahl", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 4, "anzahl": 8}, False),   # Regelverletzung: 4 keine Primzahl
            ({"typ": "anzahl", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 3, "anzahl": 6, "toleranz": 1}, False),  # Toleranz ignoriert
            ({"typ": "kac_polynom", "quiver": "cycle3_oriented", "alpha": [1, 1, 1], "koeffizienten": [2, 1]}, True),
            ({"typ": "kac_polynom", "quiver": "cycle3_oriented", "alpha": [1, 1, 1], "koeffizienten": [3, 1]}, False),
            ({"typ": "kac_polynom", "quiver": "cycle3_oriented", "alpha": [2, 2, 2], "koeffizienten": [2, 1]}, False),  # teilbar
            ({"typ": "kac_polynom", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "formel": "((q+1)**4 - 1 - 15*q)/(q*(q-1))"}, True),
            ({"typ": "kac_polynom", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "formel": "((q+1)**4 - 1 - 14*q)/(q*(q-1))"}, False),  # kein Polynom
            ({"typ": "kac_polynom", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "formel": "q**2 + 5*q + 12"}, False),               # um 1 daneben
            ({"typ": "kac_box", "quiver": "star3", "schranke": [2, 1, 1, 1], "p": 2}, True),             # Gabriel für D4
            ({"typ": "zykel_box", "quiver": "cycle3_oriented", "schranke": [2, 2, 1], "p": 2}, True),
            ({"typ": "zykel_box", "quiver": "cycle3_acyclic", "schranke": [1, 1, 1], "p": 2}, False),   # nur orientierte Zykel
        ]


DOMAIN = QuiverDomain()
