"""Domäne: Bell-Ungleichungen und Quantenkorrelationen (bipartit, zwei Ausgänge).

Prüfer mit ZWEISEITIGEN exakten Zertifikaten:
  untere Schranke  = explizite Quantenstrategie, auf rationale Zahlen gerundet, Bell-Wert exakt rational (bell.exact_value)
  obere Schranke   = rationales Dualzertifikat der NPA-Hierarchie, Positivität exakt per LDL^T (bell.npa_certified)
  klassisch        = vollständige Aufzählung deterministischer Strategien in rationaler Arithmetik (bell.local_bound)
Liegen untere und obere Schranke innerhalb der festen Toleranz 1e-6 beieinander, ist der Quantenwert bewiesen
(bis auf diese Breite). Toleranzen, Seeds, Dimensionen und Stufen des Prüfers stehen hier fest, nie in der Behauptung.
"""
import hashlib, json, math
from fractions import Fraction as F
import sympy as sp
from .base import Domain
from . import bell as B

TOL = F(1, 10 ** 6)                       # feste Breite für zweiseitige Aussagen
PRUEF_DIMS = (2, 3, 4)                    # eigene See-saw-Suche des Prüfers
PRUEF_STARTS = 12
PRUEF_SEED = 977_000                      # verschieden von allen Seeds, die Agenten wählen können (< 10^5)
PRUEF_STUFEN = ("1+AB", "2", "2+AAB")
P = sp.Symbol("p")


def _subst(obj, val):
    """Ersetzt in einer Ungleichungs-Vorlage jeden String mit 'p' durch den exakten Wert (rational)."""
    if isinstance(obj, dict): return {k: _subst(v, val) for k, v in obj.items()}
    if isinstance(obj, list): return [_subst(v, val) for v in obj]
    if isinstance(obj, str) and "p" in obj:
        if ":" in obj:
            pre, rest = obj.split(":", 1)
            if "p" not in rest: return obj
            e = sp.sympify(rest, locals={"p": P}).subs(P, sp.Rational(str(val)))
            if not e.is_Rational: raise ValueError(f"{obj} bei p={val} nicht rational")
            return f"{pre}:{e.p}/{e.q}"
        e = sp.sympify(obj, locals={"p": P}).subs(P, sp.Rational(str(val)))
        if not e.is_Rational: raise ValueError(f"Koeffizient {obj} bei p={val} nicht rational")
        return f"{e.p}/{e.q}"
    return obj


def _fmt(x, k=12): return f"{float(x):.{k}g}"


def own_lower(I):
    """Eigene untere Schranke des Prüfers: See-saw in mehreren Dimensionen, beste Strategie exakt bewertet."""
    best = None
    for d in PRUEF_DIMS:
        if d ** 2 * max(I["mA"], I["mB"]) > 200: break
        v, sid, _ = B.seesaw(I, d=d, starts=PRUEF_STARTS, seed=PRUEF_SEED + d)
        ex, _ = B.exact_value(I, B.load(sid))
        if best is None or ex > best[0]: best = (ex, sid, d)
    return best


def own_upper(I, stop_at=None):
    """Eigene obere Schranke: NPA-Stufen aufsteigend, beste zertifizierte Schranke. stop_at: abbrechen, sobald U <= stop_at."""
    best = None; log = []
    for st in PRUEF_STUFEN:
        if len(B.npa_words(I["mA"], I["mB"], st)) > 80: break
        try:
            U, fv, dg = B.npa_certified(I, st); log.append(f"{st}: {_fmt(U)}")
            if best is None or U < best[0]: best = (U, st)
            if stop_at is not None and U <= stop_at: break
        except ValueError as e:
            log.append(f"{st}: {e}")
    return best, log


def two_sided(I):
    lo = own_lower(I)
    up, log = own_upper(I, stop_at=lo[0] + TOL)
    return lo, up, log


class BellDomain(Domain):
    name = "bell"
    recherche_ziel = ("Maximale Quantenverletzung bipartiter Bell-Ungleichungen (Tsirelson-Schranken), NPA-Hierarchie, I3322, gekippte "
                      "CHSH-Ungleichungen, Kettenungleichungen (chained Bell), Selbsttest, Dimensionszeugen, Lücke zwischen NPA-Stufen.")
    recherche_sperre = []
    kontext = ("Bipartites Bell-Szenario: Alice und Bob wählen je eine von mA bzw. mB Messungen mit Ausgängen ±1. Eine Bell-Ungleichung ist "
               "in Korrelatorform I = konst + sum_x a_x <A_x> + sum_y b_y <B_y> + sum_xy c_xy <A_x B_y> gegeben (Koeffizienten rational) oder in "
               "Collins-Gisin-Form über p(A_x=+1), p(B_y=+1), p(+1,+1|x,y). Drei Werte sind interessant: die klassische (lokale) Schranke L, der "
               "maximale Quantenwert Q (Tsirelson-Schranke der Ungleichung) und das Verhältnis Q/L. Das Labor kann L exakt aufzählen, Q von unten "
               "durch explizite Quantenstrategien (See-saw in reeller QM, Dimension d pro Seite) und von oben durch die NPA-Hierarchie (SDP, "
               "Stufen 1, 1+AB, 2, 2+AAB) eingrenzen. Beide Schranken werden vom Prüfer exakt in rationalen Zahlen zertifiziert. Fällt die "
               "Lücke zwischen unten und oben unter 1e-6, gilt Q als bewiesen. Benannte Ungleichungen: 'chsh', 'i3322', 'kette:m' "
               "(Braunstein-Caves-Kette mit m Einstellungen), 'gekippt:beta' (beta*<A_1> + CHSH). Eigene Ungleichungen als JSON "
               "{'korrelator': {'a': [...], 'b': [...], 'c': [[...]], 'konst': 0}} oder {'cg': {'pa': [...], 'pb': [...], 'pab': [[...]]}}. "
               "Parameterfamilien: in Koeffizienten darf der String 'p' bzw. ein Ausdruck in p stehen (z. B. '1-p', '2*p'), bei 'gekippt:p' "
               "auch der Name.")
    primitive_doc = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}):
- beschreibe {ungleichung}: Korrelatorform, Zahl der Einstellungen.
- lokal {ungleichung}: exakte klassische Schranke und eine optimale deterministische Strategie.
- seesaw {ungleichung, d (2..6), starts (<=40), seed (< 100000)}: beste gefundene Quantenstrategie (numerisch, Kandidat), ihre
  strategie_id und die besten Werte aller Starts. Mehrere d vergleichen zeigt, ob Qubits reichen.
- npa {ungleichung, stufe ("1"|"1+AB"|"2"|"2+AAB")}: obere Schranke der NPA-Hierarchie (numerisch und rational zertifiziert).
- strategie {strategie_id}: exakter Wert der gespeicherten Strategie nach rationaler Rundung.
- scan {vorlage, werte: [...], d?, stufe?}: für jedes p in werte: L exakt, See-saw-Wert (d, Standard 2) und NPA-Schranke (Standard 1+AB).
  vorlage ist eine Ungleichung mit p in Koeffizienten oder 'gekippt:p'. Höchstens 12 Werte."""
    claim_doc = """Prüfungstypen (der Prüfer rechnet alles selbst nach; Toleranzen, Seeds und Stufen legt er fest):
- {"typ": "klassische_schranke", "ungleichung": ..., "wert": Zahl oder "p/q"}: L ist exakt gleich wert.
- {"typ": "quanten_untere_schranke", "ungleichung": ..., "wert": Zahl, "strategie_id": "S..." (optional)}: es gibt eine Quantenstrategie
  mit Bell-Wert >= wert (exakt rational geprüft; ohne strategie_id sucht der Prüfer selbst).
- {"typ": "quanten_obere_schranke", "ungleichung": ..., "wert": Zahl}: Q <= wert für alle Quantenstrategien jeder Dimension
  (rationales NPA-Dualzertifikat, Prüfer probiert seine Stufen).
- {"typ": "quantenwert", "ungleichung": ..., "wert": Zahl}: Q ist zweiseitig bewiesen (Lücke unten/oben <= 1e-6) und wert liegt darin.
- {"typ": "quantenverletzung", "ungleichung": ..., "strategie_id": "S..." (optional)}: eine Quantenstrategie übertrifft L exakt.
- {"typ": "formel", "vorlage": ..., "ausdruck": "<sympy-Ausdruck in p>", "werte": [>= 3 rationale p]}: Q(p) = ausdruck, zweiseitig
  bewiesen an jedem angegebenen p und zusätzlich an 2 Stellen, die der Prüfer selbst im Bereich der Werte wählt.
- {"typ": "luecke_npa", "ungleichung": ..., "stufe": "1"|"1+AB"|"2", "mindestens": Zahl}: die NPA-Schranke dieser Stufe liegt um
  mindestens 'mindestens' über einer exakt zertifizierten Quantenstrategie (die Stufe ist also nicht scharf)."""

    # ------------------------------------------------------------ Experimente
    def run_op(self, op, args):
        try:
            if op == "beschreibe":
                I = B.parse(args["ungleichung"]); return {"korrelator": B.show(I), "mA": I["mA"], "mB": I["mB"]}
            if op == "lokal":
                I = B.parse(args["ungleichung"]); L, (sa, sb) = B.local_bound(I)
                return {"L": str(L), "L_float": float(L), "strategie_A": list(sa), "strategie_B": list(sb), "hinweis": "exakt"}
            if op == "seesaw":
                I = B.parse(args["ungleichung"]); d = int(args.get("d", 2)); starts = int(args.get("starts", 10)); seed = int(args.get("seed", 0))
                if not 2 <= d <= 6: return {"fehler": "d muss in 2..6 liegen"}
                if not 1 <= starts <= 40: return {"fehler": "starts muss in 1..40 liegen"}
                if not 0 <= seed < 100_000: return {"fehler": "seed muss in 0..99999 liegen"}
                v, sid, vals = B.seesaw(I, d=d, starts=starts, seed=seed)
                return {"wert": v, "strategie_id": sid, "beste_starts": [round(x, 9) for x in vals[:8]], "d": d, "hinweis": "numerisch (Kandidat)"}
            if op == "npa":
                I = B.parse(args["ungleichung"]); st = str(args.get("stufe", "1+AB"))
                U, fv, dg = B.npa_certified(I, st)
                return {"schranke_numerisch": fv, "schranke_zertifiziert": float(U), "stufe": st, "groesse": dg["groesse"]}
            if op == "strategie":
                rec = B.load(args["strategie_id"])
                if not rec: return {"fehler": "unbekannte strategie_id"}
                I = B.parse(args["ungleichung"]) if "ungleichung" in args else None
                if I is None: return {"ungleichung": rec["ungleichung"], "d": rec["d"], "wert_numerisch": rec["wert_numerisch"]}
                ex, dg = B.exact_value(I, rec); return {"wert_exakt_float": float(ex), "d": rec["d"]}
            if op == "scan":
                werte = list(args["werte"])[:12]; d = int(args.get("d", 2)); st = str(args.get("stufe", "1+AB")); out = []
                if not 2 <= d <= 4: return {"fehler": "d muss in 2..4 liegen"}
                for w in werte:
                    try:
                        I = B.parse(_subst(args["vorlage"], w)); L, _ = B.local_bound(I)
                        v, sid, _ = B.seesaw(I, d=d, starts=8, seed=1)
                        fv, _, _ = B.npa_float(I, st)
                        out.append({"p": w, "L": float(L), "seesaw": v, "npa": fv, "strategie_id": sid})
                    except Exception as e:
                        out.append({"p": w, "fehler": f"{type(e).__name__}: {e}"[:200]})
                return {"punkte": out, "hinweis": "numerisch (Kandidat)"}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    # ------------------------------------------------------------ Prüfer
    def check(self, p):
        try:
            t = p.get("typ")
            if t == "klassische_schranke":
                I = B.parse(p["ungleichung"]); L, _ = B.local_bound(I); w = B._q(p["wert"])
                return L == w, f"Prüfer: L = {L} exakt (Aufzählung von 2^{I['mA']} Strategien)", {"L": str(L)}
            if t == "quanten_untere_schranke":
                I = B.parse(p["ungleichung"]); w = B._q(p["wert"])
                if p.get("strategie_id"):
                    rec = B.load(p["strategie_id"])
                    if not rec: return False, "unbekannte strategie_id", {}
                    if rec["ungleichung_key"] != B.key(I): return False, "Strategie gehört zu einer anderen Ungleichung", {}
                    ex, dg = B.exact_value(I, rec); src = f"Strategie {p['strategie_id']} (d={rec['d']})"
                else:
                    ex, sid, d = own_lower(I); src = f"eigene See-saw-Strategie {sid} (d={d})"
                return ex >= w, f"Prüfer: {src}, exakter rationaler Bell-Wert = {_fmt(ex, 15)}", {"wert": float(ex)}
            if t == "quanten_obere_schranke":
                I = B.parse(p["ungleichung"]); w = B._q(p["wert"])
                up, log = own_upper(I, stop_at=w)
                if up is None: return False, f"keine NPA-Schranke zertifizierbar ({'; '.join(log)})", {}
                return up[0] <= w, f"Prüfer: NPA-Stufe {up[1]}, rational zertifizierte obere Schranke {_fmt(up[0], 15)} ({'; '.join(log)})", {"U": float(up[0])}
            if t == "quantenwert":
                I = B.parse(p["ungleichung"]); w = B._q(p["wert"])
                lo, up, log = two_sided(I)
                if up is None: return False, "obere Schranke nicht zertifizierbar", {}
                gap = up[0] - lo[0]; ok = gap <= TOL and lo[0] - TOL <= w <= up[0] + TOL
                return ok, (f"Prüfer: {_fmt(lo[0], 15)} <= Q <= {_fmt(up[0], 15)} (Lücke {float(gap):.2e}, Strategie d={lo[2]}, NPA {up[1]}); "
                            + ("bewiesen" if gap <= TOL else "Lücke zu groß, nicht zertifiziert")), {"unten": float(lo[0]), "oben": float(up[0])}
            if t == "quantenverletzung":
                I = B.parse(p["ungleichung"]); L, _ = B.local_bound(I)
                if p.get("strategie_id"):
                    rec = B.load(p["strategie_id"])
                    if not rec or rec["ungleichung_key"] != B.key(I): return False, "Strategie fehlt oder gehört zu anderer Ungleichung", {}
                    ex, _ = B.exact_value(I, rec)
                else:
                    ex, _, _ = own_lower(I)
                return ex > L, f"Prüfer: L = {L}, Quantenstrategie exakt {_fmt(ex, 15)} (Verhältnis {float(ex / L) if L else float('nan'):.6f})", {}
            if t == "formel":
                werte = [B._q(v) for v in p["werte"]]
                if len(werte) < 3: return False, "mindestens 3 Parameterwerte nötig", {}
                expr = sp.sympify(p["ausdruck"], locals={"p": P})
                if expr.free_symbols - {P}: return False, "Ausdruck darf nur p enthalten", {}
                h = int(hashlib.sha256(json.dumps([p["ausdruck"], [str(w) for w in werte]]).encode()).hexdigest(), 16)
                lo_w, hi_w = min(werte), max(werte); extra = [lo_w + (hi_w - lo_w) * F((h >> (8 * k)) % 97 + 1, 99) for k in (0, 1)]
                rows = []
                for w in werte + extra:
                    I = B.parse(_subst(p["vorlage"], w)); val = F(repr(float(expr.subs(P, sp.Rational(w.numerator, w.denominator)).evalf(30))))
                    lo, up, _ = two_sided(I)
                    if up is None: return False, f"p={w}: obere Schranke nicht zertifizierbar", {}
                    ok = up[0] - lo[0] <= TOL and lo[0] - TOL <= val <= up[0] + TOL
                    rows.append(f"p={w}: [{_fmt(lo[0], 10)}, {_fmt(up[0], 10)}] Formel {_fmt(val, 10)} {'ok' if ok else 'FALSCH'}")
                    if not ok: return False, "Prüfer: " + "; ".join(rows), {}
                return True, "Prüfer (inkl. 2 selbst gewählter Stellen): " + "; ".join(rows), {}
            if t == "luecke_npa":
                I = B.parse(p["ungleichung"]); st = str(p["stufe"]); m = B._q(p["mindestens"])
                if st not in ("1", "1+AB", "2"): return False, "stufe muss 1, 1+AB oder 2 sein", {}
                N, dg = B.npa_primal_lower(I, st)            # rigorose untere Schranke für den NPA-Optimalwert
                ex, sid, d = own_lower(I)                    # beste eigene Strategie, exakt
                gap = N - ex
                return gap >= m, (f"Prüfer: NPA-Stufe {st} erreicht >= {_fmt(N, 12)} (rationale zulässige Momentmatrix), beste eigene Strategie "
                                  f"exakt {_fmt(ex, 12)} (d<={d}); Lücke >= {float(gap):.3e}"), {}
            return False, f"unbekannter Prüfungstyp {t}", {}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def level(self, p):
        return "computed_rigorous"

    def describe(self, p):
        t = p.get("typ"); u = p.get("ungleichung")
        name = u if isinstance(u, str) else json.dumps(u, ensure_ascii=False)
        if t == "klassische_schranke": return f"Die klassische Schranke von {name} ist exakt {p['wert']} (vollständige Aufzählung, rationale Arithmetik)."
        if t == "quanten_untere_schranke": return f"Für {name} gibt es eine explizite Quantenstrategie mit Bell-Wert >= {p['wert']} (exakt rational zertifiziert)."
        if t == "quanten_obere_schranke": return f"Für {name} gilt Q <= {p['wert']} für alle Quantenstrategien (rationales NPA-Dualzertifikat)."
        if t == "quantenwert": return f"Der maximale Quantenwert von {name} ist Q = {p['wert']} bis auf 1e-6, zweiseitig zertifiziert (explizite Strategie und NPA-Dualzertifikat)."
        if t == "quantenverletzung": return f"{name} wird von einer expliziten Quantenstrategie exakt verletzt (Bell-Wert über der klassischen Schranke)."
        if t == "formel":
            v = json.dumps(p["vorlage"], ensure_ascii=False) if not isinstance(p["vorlage"], str) else p["vorlage"]
            return (f"Für die Familie {v} gilt Q(p) = {p['ausdruck']} bis auf 1e-6 an den Stellen p in {p['werte']} und zwei weiteren vom Prüfer "
                    "gewählten Stellen (jeweils zweiseitig zertifiziert). Für andere p ist die Formel eine Vermutung.")
        if t == "luecke_npa": return (f"Für {name} liegt der Optimalwert der NPA-Stufe {p['stufe']} um mindestens {p['mindestens']} über der besten Quantenstrategie, "
                                      "die der Prüfer in Dimension bis 4 findet (beide Seiten exakt zertifiziert). Ob Q selbst darunter liegt, ist damit nicht gezeigt.")
        return super().describe(p)

    def _ident(self, p):
        try:
            if p.get("typ") == "formel": return ("formel", json.dumps(p.get("vorlage"), sort_keys=True), str(p.get("ausdruck")).replace(" ", ""))
            return (p.get("typ"), B.key(B.parse(p["ungleichung"])))
        except Exception:
            return (p.get("typ"), json.dumps(p, sort_keys=True))

    def novel(self, p, frueher):
        """Gleicher Prüfungstyp für dieselbe Ungleichung (bzw. dieselbe Formel) wie eine frühere Aussage = kein neues Resultat."""
        return self._ident(p) not in {self._ident(q) for q in frueher if isinstance(q, dict)}

    def consistent(self, antwort, p):
        z = antwort.get("zahl")
        try: z = float(z) if z is not None else None
        except (TypeError, ValueError): return True
        if z is None or p.get("typ") not in ("quantenwert", "klassische_schranke"): return True
        return abs(z - float(B._q(p["wert"]))) <= 1e-4 * max(1.0, abs(z))

    def selftest(self):
        chsh_strat = self.run_op("seesaw", {"ungleichung": "chsh", "d": 2, "starts": 4, "seed": 3})["strategie_id"]
        i33_strat = self.run_op("seesaw", {"ungleichung": "i3322", "d": 2, "starts": 6, "seed": 3})["strategie_id"]
        return [
            ({"typ": "klassische_schranke", "ungleichung": "chsh", "wert": 2}, True),
            ({"typ": "klassische_schranke", "ungleichung": "chsh", "wert": "201/100"}, False),
            ({"typ": "klassische_schranke", "ungleichung": "i3322", "wert": 0}, True),             # Collins-Gisin 2004
            ({"typ": "klassische_schranke", "ungleichung": "kette:4", "wert": 6}, True),          # 2m - 2
            ({"typ": "quanten_untere_schranke", "ungleichung": "chsh", "wert": "2.8284271", "strategie_id": chsh_strat}, True),
            ({"typ": "quanten_untere_schranke", "ungleichung": "chsh", "wert": "2.8284272", "strategie_id": chsh_strat}, False),  # über 2*sqrt(2)
            ({"typ": "quanten_untere_schranke", "ungleichung": "i3322", "wert": "0.25", "strategie_id": chsh_strat}, False),     # fremde Strategie
            ({"typ": "quanten_untere_schranke", "ungleichung": "chsh", "wert": 2.8, "strategie_id": "S000000000000"}, False),    # unbekannt
            ({"typ": "quanten_obere_schranke", "ungleichung": "chsh", "wert": "2.8284272"}, True),
            ({"typ": "quanten_obere_schranke", "ungleichung": "chsh", "wert": "2.8284270"}, False),   # unter 2*sqrt(2), muss scheitern
            ({"typ": "quanten_obere_schranke", "ungleichung": "i3322", "wert": "0.2509"}, True),      # NPA 2+AAB: 0,250876
            ({"typ": "quanten_obere_schranke", "ungleichung": "i3322", "wert": "0.2508"}, False),     # unter jeder zertifizierbaren Schranke
            ({"typ": "quantenwert", "ungleichung": "chsh", "wert": "2.828427125"}, True),
            ({"typ": "quantenwert", "ungleichung": "chsh", "wert": "2.8284", "toleranz": 0.1}, False),  # Toleranz der Behauptung wird ignoriert
            ({"typ": "quantenwert", "ungleichung": "i3322", "wert": "0.25"}, False),                  # Lücke nicht geschlossen
            ({"typ": "quantenverletzung", "ungleichung": "i3322", "strategie_id": i33_strat}, True),
            ({"typ": "luecke_npa", "ungleichung": "i3322", "stufe": "2", "mindestens": "0.0009"}, True),     # 0,25094 vs. 0,25
            ({"typ": "luecke_npa", "ungleichung": "i3322", "stufe": "2", "mindestens": "0.001"}, False),
            ({"typ": "luecke_npa", "ungleichung": "chsh", "stufe": "1+AB", "mindestens": "0.000001"}, False),  # CHSH: Stufe scharf
            ({"typ": "formel", "vorlage": "gekippt:p", "ausdruck": "sqrt(8+2*p**2)", "werte": ["1/4", "1/2", "1"]}, True),   # Acín-Massar-Pironio 2012
            ({"typ": "formel", "vorlage": "gekippt:p", "ausdruck": "sqrt(8+p**2)", "werte": ["1/4", "1/2", "1"]}, False),
            ({"typ": "formel", "vorlage": "gekippt:p", "ausdruck": "sqrt(8+2*p**2)", "werte": ["1/2", "1"]}, False),          # zu wenige Stellen
        ]


DOMAIN = BellDomain()
