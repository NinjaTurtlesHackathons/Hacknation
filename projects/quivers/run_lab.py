"""Labor-Lauf der Köcher-Domäne: arbeitet die präregistrierten Fragen F1–F5 (projects/quivers/prereg.md) ab.

Rollen wie im Framework (docs/FRAMEWORK.md), hier ohne LLM-Agenten im Labor:
  Forscher   = diese Datei (Experimente über DOMAIN.run_op, daraus getypte Behauptungen), vorgeschlagen in der Claude-Code-Sitzung
  Prüfer     = DOMAIN.check (exakt), Selbsttest muss vorher bestehen
  Red-Team   = je Aussage eine Gegen-Prüfung, die bestehen müsste, wenn die Aussage falsch wäre (muss durchfallen)
  Scout      = Crossref-Abruf jeder Referenz (DOI als Tool-Beleg, Titel per Code mit der Erwartung verglichen)
Schreibt projects/quivers/{state.json, runde<k>.json, lab_report.md, decisions.md}.
  python projects/quivers/run_lab.py
"""
import copy, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from asd.domains.quivers_domain import DOMAIN as D
from asd import selftest

OUT = os.path.dirname(os.path.abspath(__file__))
L1 = lambda v: [[v[0]], [v[1]]]                        # Gerade im k^2 als 2x1-Matrix


def star4_rep(lines):
    return {"dims": [2, 1, 1, 1, 1], "maps": {str(i): L1(l) for i, l in enumerate(lines)}}


def star_rep(lines):
    return {"dims": [2] + [1] * len(lines), "maps": {str(i): L1(l) for i, l in enumerate(lines)}}


def cyc(n, vals):
    return {"dims": [1] * n, "maps": {str(i): [[v]] for i, v in enumerate(vals)}}


def d4_delta_list(p):
    """Kandidatenliste für star4, delta, über F_p: V_t (t != 0, 1) und die 6 Konfigurationen mit genau einem Paar gleicher Geraden."""
    R = [star4_rep([(1, 0), (0, 1), (1, 1), (1, t)]) for t in range(2, p)]
    for i in range(4):
        for j in range(i + 1, 4):
            rest = [k for k in range(4) if k not in (i, j)]; L = [None] * 4
            L[i] = L[j] = (1, 0); L[rest[0]] = (0, 1); L[rest[1]] = (1, 1); R.append(star4_rep(L))
    return R


def cycle_delta_list(name, n, p):
    """Orientierte/azyklische Zykel, delta = (1,...,1): Skalare (1, ..., 1, lam) mit lam != 0 und genau ein Pfeil null."""
    R = [cyc(n, [1] * (n - 1) + [lam]) for lam in range(1, p)]
    for k in range(n):
        v = [1] * n; v[k] = 0; R.append(cyc(n, v))
    return R


FRAGEN = {
    "F1": "Gabriel: Welche der betrachteten Köcher sind von endlichem Typ, und hat D4 = star3 genau eine Unzerlegbare je positiver Wurzel?",
    "F2": "Vier-Unterraum-Problem (star4 = D~4): Wie sehen alle Unzerlegbaren mit Dimensionsvektor delta aus, und wie viele gibt es über F_q?",
    "F3": "Wilde Sterne (star n, n >= 5): Wie wachsen Parameterzahl und Anzahl der Unzerlegbaren, gibt es eine geschlossene Formel für alpha_n = (2;1^n)?",
    "F4": "3- und 4-Zykel: Klassifikation der Unzerlegbaren (orientiert und azyklisch), Unabhängigkeit von der Orientierung.",
    "F5": "Vielfache von delta: Wie viele Unzerlegbare hat 2 delta, und ist A_{2 delta} = A_delta?",
}

STAR = lambda n: "((q+1)**%d - 1 - %d*q)/(q*(q-1))" % (n - 1, 2 ** (n - 1) - 1)


def plan():
    """Präregistrierte Experimente und Behauptungen je Frage: (frage, [(op, args)], [(behauptung, interpretation, gegenprüfung, idee)])."""
    P = []
    # ---------------------------------------------------------------- F1
    ex = [("tits_typ", {"quiver": q}) for q in ["A2", "A3", "star1", "star2", "star3", "star4", "star5", "star6", "star7", "kronecker",
                                                "cycle3_oriented", "cycle3_acyclic", "cycle4_oriented", "cycle4_acyclic22"]]
    cl = []
    for q, t in [("star1", "endlich"), ("star2", "endlich"), ("star3", "endlich"), ("star4", "zahm"), ("star5", "wild"), ("star6", "wild"),
                 ("star7", "wild"), ("kronecker", "zahm"), ("cycle3_oriented", "zahm"), ("cycle4_oriented", "zahm")]:
        other = {"endlich": "zahm", "zahm": "endlich", "wild": "zahm"}[t]
        cl.append(({"typ": "tits_typ", "quiver": q, "typ_wert": t}, f"{q} hat {t}en Typ.",
                   {"typ": "tits_typ", "quiver": q, "typ_wert": other}, f"Wäre der Typ {other}, würde diese Prüfung bestehen."))
    cl.append(({"typ": "wurzelzahl", "quiver": "star3", "anzahl": 12}, "D4 hat 12 positive Wurzeln.",
               {"typ": "wurzelzahl", "quiver": "star3", "anzahl": 13}, "Eine 13. Wurzel würde die Anzahl erhöhen."))
    for p in (2, 3):
        cl.append(({"typ": "kac_box", "quiver": "star3", "schranke": [2, 1, 1, 1], "p": p},
                   "Gabriel für D4 über F_p: Unzerlegbare entsprechen genau den positiven Wurzeln.",
                   {"typ": "anzahl", "quiver": "star3", "alpha": [2, 1, 1, 1], "p": p, "anzahl": 2}, "Zwei Unzerlegbare zur maximalen Wurzel?"))
    cl.append(({"typ": "kac_box", "quiver": "A3", "schranke": [2, 2, 2], "p": 2}, "Gabriel für A3 über F_2.",
               {"typ": "anzahl", "quiver": "A3", "alpha": [1, 1, 1], "p": 2, "anzahl": 0}, "Keine Unzerlegbare zur Wurzel (1,1,1)?"))
    P.append(("F1", ex + [("wurzeln", {"quiver": "star3", "schranke": [2, 1, 1, 1]})], cl))
    # ---------------------------------------------------------------- F2
    ex = [("radikal", {"quiver": "star4"}), ("wurzeln", {"quiver": "star4", "schranke": [4, 2, 2, 2, 2]}),
          ("anzahl", {"quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 3}), ("normalformen", {"quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": 3}),
          ("familie", {"quiver": "star4", "rep": star4_rep([(1, 0), (0, 1), (1, 1), (1, "t")]), "ausnahmen": []})]
    cl = [({"typ": "radikal", "quiver": "star4", "delta": [2, 1, 1, 1, 1]}, "delta = (2;1,1,1,1).",
           {"typ": "radikal", "quiver": "star4", "delta": [1, 1, 1, 1, 1]}, "Anderer Erzeuger?"),
          ({"typ": "parameter", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "anzahl": 1}, "delta hat genau einen Parameter.",
           {"typ": "parameter", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "anzahl": 2}, "Zwei Parameter?"),
          ({"typ": "parameter", "quiver": "star4", "alpha": [4, 2, 2, 2, 2], "anzahl": 1}, "2 delta hat ebenfalls genau einen Parameter.",
           {"typ": "wurzel", "quiver": "star4", "alpha": [4, 2, 2, 2, 2], "art": "keine"}, "Ist 2 delta gar keine Wurzel?"),
          ({"typ": "kac_polynom", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "koeffizienten": [4, 1]}, "A_delta(q) = q + 4.",
           {"typ": "kac_polynom", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "koeffizienten": [3, 1]}, "q + 3 (nur P^1 plus zwei Ausnahmen)?"),
          ({"typ": "familie", "quiver": "star4", "rep": star4_rep([(1, 0), (0, 1), (1, 1), (1, "t")]), "ausnahmen": []},
           "Die Geraden-Familie V_t ist eine Ein-Parameter-Familie paarweise nicht isomorpher Ziegel (Doppelverhältnis t).",
           {"typ": "unzerlegbar", "quiver": "star4", "rep": star4_rep([(1, 0), (0, 1), (1, 1), (1, 5)]), "wert": False}, "Zerfällt V_5?")]
    for p in (2, 3, 5):
        R = d4_delta_list(p)
        cl.append(({"typ": "klassifikation", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": p, "reps": R},
                   f"Über F_{p}: V_t (t != 0, 1) und 6 Konfigurationen mit genau einem Paar gleicher Geraden sind alle {p + 4} Unzerlegbaren in delta.",
                   {"typ": "klassifikation", "quiver": "star4", "alpha": [2, 1, 1, 1, 1], "p": p, "reps": R[:-1]}, "Reicht die Liste ohne das letzte Element?"))
    for dims, lines, name in [([1, 1, 1, 1, 1], None, "(1;1,1,1,1)"), ([3, 1, 1, 1, 1], "e3", "(3;1,1,1,1)"), ([2, 2, 1, 1, 1], "id", "(2;2,1,1,1)")]:
        if lines is None: V = {"dims": dims, "maps": {str(i): [[1]] for i in range(4)}}
        elif lines == "e3": V = {"dims": dims, "maps": {"0": [[1], [0], [0]], "1": [[0], [1], [0]], "2": [[0], [0], [1]], "3": [[1], [1], [1]]}}
        else: V = {"dims": dims, "maps": {"0": [[1, 0], [0, 1]], "1": [[1], [0]], "2": [[0], [1]], "3": [[1], [1]]}}
        cl.append(({"typ": "unzerlegbar", "quiver": "star4", "rep": V, "wert": True}, f"Explizite Unzerlegbare zur reellen Wurzel {name}.",
                   {"typ": "wurzel", "quiver": "star4", "alpha": dims, "art": "imaginaer"}, "Ist der Vektor imaginär?"))
    cl.append(({"typ": "unzerlegbar", "quiver": "star4", "rep": star4_rep([(1, 0), (1, 0), (0, 1), (0, 1)]), "wert": False},
               "Zwei Paare gleicher Geraden: zerlegbar.", {"typ": "unzerlegbar", "quiver": "star4", "rep": star4_rep([(1, 0), (1, 0), (0, 1), (0, 1)]), "wert": True}, "Doch unzerlegbar?"))
    for p in (2, 3):
        cl.append(({"typ": "kac_box", "quiver": "star4", "schranke": [3, 1, 1, 1, 1], "p": p},
                   "Kac für D~4: reelle Wurzeln genau eine Unzerlegbare, Nicht-Wurzeln keine (alle Vektoren <= (3;1,1,1,1)).",
                   {"typ": "anzahl", "quiver": "star4", "alpha": [3, 1, 1, 1, 1], "p": p, "anzahl": 0}, "Keine Unzerlegbare in (3;1,1,1,1)?"))
    P.append(("F2", ex, cl))
    # ---------------------------------------------------------------- F3
    ex = [("interpolation", {"quiver": f"star{n}", "alpha": [2] + [1] * n, "grad": n - 3}) for n in (5, 6, 7)]
    cl = []
    for n in (5, 6, 7, 8):
        cl.append(({"typ": "parameter", "quiver": f"star{n}", "alpha": [2] + [1] * n, "anzahl": n - 3}, f"(2;1^{n}) hat {n - 3} Parameter.",
                   {"typ": "parameter", "quiver": f"star{n}", "alpha": [2] + [1] * n, "anzahl": n - 4}, "Einen Parameter weniger?"))
    for k in (2, 3):
        cl.append(({"typ": "parameter", "quiver": "star5", "alpha": [2 * k] + [k] * 5, "anzahl": 1 + k * k}, f"(2k;k^5) mit k = {k} hat 1 + k^2 Parameter.",
                   {"typ": "parameter", "quiver": "star5", "alpha": [2 * k] + [k] * 5, "anzahl": 2}, "Bleibt die Parameterzahl beschränkt?"))
    for n in (4, 5, 6, 7, 8):
        cl.append(({"typ": "kac_polynom", "quiver": f"star{n}", "alpha": [2] + [1] * n, "formel": STAR(n)},
                   f"A_(2;1^{n})(q) = ((q+1)^(n-1) - 1 - (2^(n-1) - 1) q)/(q(q-1)).",
                   {"typ": "kac_polynom", "quiver": f"star{n}", "alpha": [2] + [1] * n, "formel": STAR(n) + " + 1"}, "Konstante um 1 verschoben?"))
    cl.append(({"typ": "klassifikation", "quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "p": 2,
                "reps": None}, "Vollständige Liste über F_2: Konfigurationen von 5 Punkten in P^1(F_2) mit >= 3 verschiedenen Punkten modulo PGL_2.",
               None, "Liste ohne letztes Element"))
    for s in (2, 3, -1):
        cl.append(({"typ": "familie", "quiver": "star5", "rep": star_rep([(1, 0), (0, 1), (1, 1), (1, s), (1, "t")]), "ausnahmen": []},
                   f"Schnitt s = {s} der Zwei-Parameter-Familie (Geraden (1,0), (0,1), (1,1), (1,s), (1,t)): paarweise nicht isomorphe Ziegel.",
                   {"typ": "unzerlegbar", "quiver": "star5", "rep": star_rep([(1, 0), (0, 1), (1, 1), (1, s), (1, 7)]), "wert": False}, "Zerfällt ein Mitglied?"))
    P.append(("F3", ex, cl))
    # ---------------------------------------------------------------- F4
    ex = [("radikal", {"quiver": q}) for q in ("cycle3_oriented", "cycle3_acyclic", "cycle4_oriented", "cycle4_acyclic31", "cycle4_acyclic22")]
    ex += [("normalformen", {"quiver": "cycle3_oriented", "alpha": [1, 1, 1], "p": 3}), ("anzahl", {"quiver": "cycle3_oriented", "alpha": [2, 2, 2], "p": 3})]
    cl = []
    for q, n in (("cycle3_oriented", 3), ("cycle3_acyclic", 3), ("cycle4_oriented", 4), ("cycle4_acyclic31", 4), ("cycle4_acyclic22", 4)):
        cl.append(({"typ": "radikal", "quiver": q, "delta": [1] * n}, f"delta = (1,...,1) für {q}.",
                   {"typ": "radikal", "quiver": q, "delta": [2] + [1] * (n - 1)}, "Anderer Erzeuger?"))
        cl.append(({"typ": "kac_polynom", "quiver": q, "alpha": [1] * n, "koeffizienten": [n - 1, 1]}, f"A_delta(q) = q + {n - 1} für {q}.",
                   {"typ": "kac_polynom", "quiver": q, "alpha": [1] * n, "koeffizienten": [n - 2, 1]}, "q + n - 2?"))
        R = cycle_delta_list(q, n, 3)
        cl.append(({"typ": "klassifikation", "quiver": q, "alpha": [1] * n, "p": 3, "reps": R},
                   f"Über F_3: 2 Skalar-Darstellungen (Produkt der Pfeile = lambda != 0) und {n} mit genau einem Nullpfeil sind alle {n + 2} Unzerlegbaren in delta.",
                   {"typ": "klassifikation", "quiver": q, "alpha": [1] * n, "p": 3, "reps": R[:-1]}, "Liste ohne letztes Element vollständig?"))
    for q, n in (("cycle3_oriented", 3), ("cycle4_acyclic22", 4)):
        cl.append(({"typ": "familie", "quiver": q, "rep": cyc(n, [1] * (n - 1) + ["t"]), "ausnahmen": [0]},
                   f"Die Familie (1, ..., 1, t), t != 0, auf {q}: paarweise nicht isomorphe Ziegel.",
                   {"typ": "unzerlegbar", "quiver": q, "rep": cyc(n, [1] * (n - 1) + [4]), "wert": False}, "Zerfällt t = 4?"))
    J = lambda lam: {"dims": [3, 3, 3, 3], "maps": {"0": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "1": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                                                    "2": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "3": [[lam, 1, 0], [0, lam, 1], [0, 0, lam]]}}
    cl.append(({"typ": "unzerlegbar", "quiver": "cycle4_oriented", "rep": J(2), "wert": True}, "Jordanblock J_3(2) als Monodromie: unzerlegbar, Dimensionsvektor 3 delta.",
               {"typ": "unzerlegbar", "quiver": "cycle4_oriented", "rep": J(2), "wert": False}, "Zerlegbar?"))
    S = {"dims": [2, 2, 1], "maps": {"0": [[1, 0], [0, 1]], "1": [[1, 0]], "2": [[0], [1]]}}
    cl.append(({"typ": "unzerlegbar", "quiver": "cycle3_oriented", "rep": S, "wert": True}, "Nilpotenter String S(0, 5) mit Dimensionsvektor (2,2,1): unzerlegbar.",
               {"typ": "unzerlegbar", "quiver": "cycle3_oriented", "rep": S, "wert": False}, "Zerlegbar?"))
    for p, B in ((2, [2, 2, 2]), (3, [2, 2, 2]), (2, [2, 2, 2, 2])):
        q = "cycle3_oriented" if len(B) == 3 else "cycle4_oriented"
        cl.append(({"typ": "zykel_box", "quiver": q, "schranke": B, "p": p}, f"Klassifikation des orientierten Zykels für alle beta <= {B} über F_{p} bestätigt.",
                   {"typ": "anzahl", "quiver": q, "alpha": B, "p": p, "anzahl": 0}, "Keine Unzerlegbare in der Schranke?"))
    cl.append(({"typ": "kac_box", "quiver": "cycle3_acyclic", "schranke": [2, 2, 2], "p": 2}, "Kac für azyklisches Ã2: reelle Wurzeln genau eine Unzerlegbare.",
               {"typ": "anzahl", "quiver": "cycle3_acyclic", "alpha": [1, 1, 0], "p": 2, "anzahl": 2}, "Zwei Unzerlegbare in (1,1,0)?"))
    P.append(("F4", ex, cl))
    # ---------------------------------------------------------------- F5
    ex = [("anzahl", {"quiver": "cycle3_acyclic", "alpha": [2, 2, 2], "p": 5})]
    cl = []
    for q, n, ps in (("cycle3_oriented", 3, (2, 3, 5)), ("cycle3_acyclic", 3, (2, 3, 5)), ("cycle4_oriented", 4, (2, 3)), ("cycle4_acyclic22", 4, (2, 3))):
        for p in ps:
            v = (p + n - 1) + (p * p - p) // 2
            cl.append(({"typ": "anzahl", "quiver": q, "alpha": [2] * n, "p": p, "anzahl": v},
                       f"I_(2 delta)({p}) = {v} = A_delta(q) + (A_delta(q^2) - A_delta(q))/2 mit A_(2 delta) = A_delta.",
                       {"typ": "anzahl", "quiver": q, "alpha": [2] * n, "p": p, "anzahl": v + 1}, "Eine Unzerlegbare mehr?"))
    P.append(("F5", ex, cl))
    return P


def star5_f2_list():
    """Experiment: Normalformen für star5, (2;1^5), über F_2 (Kandidatenliste für die Klassifikations-Prüfung)."""
    r = D.run_op("normalformen", {"quiver": "star5", "alpha": [2, 1, 1, 1, 1, 1], "p": 2})
    return r["reps"]


REFS = [("10.1007/BF01298413", "Unzerlegbare Darstellungen I", "Gabriel",
         "Gabriel (1972): Ein zusammenhängender Köcher hat genau dann nur endlich viele Isoklassen unzerlegbarer Darstellungen, wenn der zugrunde liegende Graph ein Dynkin-Diagramm vom Typ A, D, E ist; dann entsprechen die Unzerlegbaren bijektiv den positiven Wurzeln über den Dimensionsvektor."),
        ("10.1070/RM1973v028n02ABEH001526", "COXETER FUNCTORS AND GABRIEL'S THEOREM", "Bernstein",
         "Bernstein, Gelfand, Ponomarev (1973): Beweis von Gabriels Satz mit Spiegelungsfunktoren (Coxeter-Funktoren)."),
        ("10.1007/BF01403155", "Infinite root systems, representations of graphs and invariant theory", "Kac",
         "Kac (1980): Für jeden Köcher und algebraisch abgeschlossenen Körper sind die Dimensionsvektoren Unzerlegbarer genau die positiven Wurzeln; zu reellen Wurzeln gibt es genau eine Unzerlegbare, zu imaginären unendlich viele, mit 1 - q(alpha) Parametern."),
        ("10.1007/BFb0063236", "Root systems, representations of quivers and invariant theory", "Kac",
         "Kac (1983): Die Anzahl A_alpha(q) absolut unzerlegbarer Darstellungen über F_q ist ein Polynom in q mit ganzzahligen Koeffizienten, unabhängig von der Orientierung, vom Grad 1 - q(alpha), normiert."),
        ("10.1070/IM1973v007n04ABEH001975", "REPRESENTATIONS OF QUIVERS OF INFINITE TYPE", "Nazarova",
         "Nazarova (1973): Klassifikation der Unzerlegbaren für die euklidischen (erweiterten Dynkin-) Köcher; diese sind genau die zahmen Köcher."),
        ("10.1007/BFb0072870", "Tame Algebras and Integral Quadratic Forms", "Ringel",
         "Ringel (1984): Tame Algebras and Integral Quadratic Forms; für euklidische Köcher zerfallen die regulären Unzerlegbaren in Röhren, parametrisiert durch P^1, mit endlich vielen Ausnahmeröhren."),
        ("10.1006/jabr.1999.8220", "Counting Representations of Quivers over Finite Fields", "Hua",
         "Hua (2000): Formel für die Anzahl der Isoklassen (absolut) unzerlegbarer Darstellungen eines Köchers über endlichen Körpern."),
        ("10.4007/annals.2013.177.3.8", "Positivity for Kac polynomials and DT-invariants of quivers", "Hausel",
         "Hausel, Letellier, Rodriguez-Villegas (2013): Die Koeffizienten der Kac-Polynome sind nichtnegativ.")]


def scout():
    W = []
    for doi, title, author, text in REFS:
        try:
            req = urllib.request.Request(f"https://api.crossref.org/works/{doi}", headers={"User-Agent": "asd-quivers/1.0 (mailto:noreply@example.org)"})
            m = json.load(urllib.request.urlopen(req, timeout=30))["message"]
            got = " ".join(m.get("title", [""])); auth = [a.get("family", "") for a in m.get("author", [])]
            ok = title.lower() in got.lower() and any(author.lower()[:5] in a.lower() for a in auth)
            yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        except Exception as e:
            ok, got, auth, yr = False, f"Abruf fehlgeschlagen: {e}", [], None
        W.append({"text": text, "zitat": got, "quelle": f"doi:{doi}", "typ": "literatur", "verifiziert": ok, "autoren": auth, "jahr": yr,
                  "url": f"https://doi.org/{doi}"})
        print(f"[{'OK ' if ok else 'UNVERIFIED'}] {doi}: {got[:80]} ({yr})", flush=True)
    return W


def main():
    ok, _ = selftest.run("quivers", log=lambda *_: None)
    if not ok: sys.exit("Selbsttest nicht bestanden: kein Start")
    state = {"domain": "quivers", "wissen": [w for w in scout() if w["verifiziert"]], "fragen": FRAGEN, "claims": [], "widerlegt": [], "runden": [], "kosten_usd": 0.0}
    report = ["# Laborbericht: Köcher-Domäne", "", f"Selbsttest: bestanden. Start {time.strftime('%Y-%m-%d %H:%M:%S')}.", ""]
    decisions = ["# Entscheidungen (Köcher-Domäne)", ""]
    nid = 0
    for k, (fid, ex, cl) in enumerate(plan(), 1):
        t0 = time.time(); runde = {"runde": k, "frage": fid, "text": FRAGEN[fid], "experimente": [], "pruefungen": []}
        for op, args in ex:
            te = time.time(); r = D.run_op(op, args)
            if op == "normalformen": r = {"anzahl": r.get("anzahl"), "fehler": r.get("fehler")}
            runde["experimente"].append({"op": op, "args": args, "ergebnis": r, "sek": round(time.time() - te, 2)})
        report += [f"## Runde {k} ({fid}): {FRAGEN[fid]}", ""]
        for p, interp, gegen, idee in cl:
            if p.get("typ") == "klassifikation" and p.get("reps") is None:
                p["reps"] = star5_f2_list(); gegen = copy.deepcopy(p); gegen["reps"] = p["reps"][:-1]
            okc, why, _ = D.check(copy.deepcopy(p)); nid += 1; cid = f"quivers-R{k}-{nid}"
            rt = []
            if gegen is not None:
                okg, whyg, _ = D.check(copy.deepcopy(gegen))
                rt.append({"pruefung": gegen, "idee": idee, "bestanden": okg, "widerspruch": bool(okg and D.widerspricht(p, gegen)), "grund": whyg[:400]})
            angefochten = any(r["widerspruch"] for r in rt)
            status = "angefochten" if angefochten else ("bestätigt" if okc else "widerlegt")
            entry = {"id": cid, "frage": FRAGEN[fid], "text": D.describe(p), "pruefung": p, "grund": why[:600], "level": D.level(p), "status": status,
                     "interpretation_ungeprueft": interp, "red_team": rt}
            runde["pruefungen"].append({"id": cid, "bestanden": okc, "status": status, "grund": why[:300]})
            if okc and not angefochten: state["claims"].append(entry)
            else:
                state["widerlegt"].append(f"{cid}: {D.describe(p)} -> nicht bestätigt ({why[:200]})")
                decisions.append(f"- {cid}: Präregistrierte Hypothese nicht bestätigt ({status}). Grund: {why[:300]}")
            report.append(f"- [{cid}] {'BESTÄTIGT' if status == 'bestätigt' else status.upper()}: {D.describe(p)[:260]}  \n  Prüfer: {why[:260]}"
                          + "".join(f"  \n  Red-Team: {r['idee']} -> {'bestanden (WIDERSPRUCH)' if r['widerspruch'] else ('bestanden, kein Widerspruch' if r['bestanden'] else 'durchgefallen')}" for r in rt))
            print(f"[{status}] {cid} {D.describe(p)[:120]}", flush=True)
        runde["sek"] = round(time.time() - t0, 1); state["runden"].append({"runde": k, "frage": fid, "status": "beantwortet", "sek": runde["sek"]})
        json.dump(runde, open(f"{OUT}/runde{k}.json", "w"), ensure_ascii=False, indent=1); report.append("")
    n_ok = len(state["claims"]); report += [f"Ergebnis: {n_ok} bestätigte Aussagen, {len(state['widerlegt'])} nicht bestätigt, Literatur: {len(state['wissen'])} DOIs per Crossref bestätigt."]
    json.dump(state, open(f"{OUT}/state.json", "w"), ensure_ascii=False, indent=1)
    open(f"{OUT}/lab_report.md", "w").write("\n".join(report) + "\n")
    if len(decisions) == 2: decisions.append("- Alle präregistrierten Hypothesen F1–F5 wurden bestätigt; keine Abweichung von der Präregistrierung.")
    decisions += ["- D~4 mit 2 delta über F_p wurde nicht gezählt: GL_4(F_2)-Klassen sprengen den Speicher (Lauf abgebrochen, ~4,5 GB). Ersatz: 2 delta für Ã2 und Ã3.",
                  "- (3;1^5) für star5 wurde nicht gezählt: GL_3(F_7) wird im Prüfer vollständig aufgezählt (zu teuer).",
                  "- Gelfand-Ponomarev (1972, Vier-Unterraum-Problem) und Donovan-Freislich (1973) haben keinen DOI: nicht zitiert (UNVERIFIED)."]
    open(f"{OUT}/decisions.md", "w").write("\n".join(decisions) + "\n")
    print(report[-1])


if __name__ == "__main__":
    main()
