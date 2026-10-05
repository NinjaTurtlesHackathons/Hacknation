"""Domäne: modular — Modulformen und Stringtheorie-Identitäten.

Zwei Prüfer-Familien:
 (1) Holomorph (exakt, Zertifikat): Identitäten zwischen Modulformen auf Gamma_0(N) (Eisenstein-Reihen, Eta-Quotienten,
     Thetareihen gerader unimodularer Gitter, j). Exakte rationale q-Koeffizienten; Beweis über die Sturm-Schranke
     (nach Multiplikation mit Delta^h auch für schwach holomorphe Formen). Familien: alle holomorphen Eta-Quotienten
     eines Gewichts/Levels und die Dimension ihres Spanns (exakter Rang bis zur Sturm-Schranke).
 (2) Nicht-holomorph (numerisch): Modulgraphfunktionen C_{a,b,c} und Eisenstein-Reihen E_s aus der Niederenergie-Entwicklung
     der Torus-Amplitude geschlossener Strings. Der Prüfer wertet an EIGENEN Zufallspunkten (Seed 4711) mit ~32 Stellen aus
     (asd/domains/mgf.py) und verlangt |Residuum| <= 1e-24 (bzw. 1e-14 mit Laplace-Termen). Stufe: numerisch (observed).
"""
import json, math
from fractions import Fraction as Fr
from .base import Domain
from . import qforms as QF

PRUEF_SEED = 4711
DPS = 32
TOL = 24          # Stellen für Relationen ohne Laplace-Term
TOL_LAP = 14      # Stellen mit Laplace-Term (finite Differenzen 4. Ordnung)
N_PUNKTE = 4


def _fr(x):
    if isinstance(x, float): raise ValueError("Koeffizienten als exakte rationale Zahl (String '7/30' oder ganze Zahl), nicht als Gleitkomma")
    return Fr(str(x))


def _terme(p, key="terme"):
    t = p.get(key)
    if not isinstance(t, list) or not t: raise ValueError(f"'{key}' fehlt oder ist leer")
    out = []
    for e in t:
        if not (isinstance(e, (list, tuple)) and len(e) == 2): raise ValueError("Term muss [koeffizient, ausdruck] sein")
        out.append((_fr(e[0]), str(e[1])))
    return out


def _fmt(terme):
    s = []
    for c, m in terme:
        c = Fr(c); sign = "-" if c < 0 else "+"; a = abs(c)
        s.append(f"{sign} {'' if a == 1 else str(a) + '·'}{m}")
    out = " ".join(s).strip()
    if out.startswith("+ "): out = out[2:]
    elif out.startswith("- "): out = "-" + out[2:]
    return out


# ---------------- holomorphe Prüfungen ----------------

def check_identitaet(p):
    terme = _terme(p)
    ok, why, bel = QF.certify_identity(terme, int(p["level"]))
    return ok, why, bel


def check_koeffizient(p):
    mon = QF.parse_monom(p["monom"]); n = Fr(str(p["n"])); want = _fr(p["wert"])
    if n.denominator != 1 or abs(n) > 2000: return False, "n muss ganz sein, |n| <= 2000", {}
    s = QF.series(mon, int(n) + 2)
    got = s.coeff(int(n))
    return got == want, f"exakter Koeffizient von q^{n} in {p['monom']}: {got}", {"wert": str(got)}


def check_eta_span(p):
    N, k = int(p["level"]), int(p["gewicht"])
    if not (1 <= N <= 64 and 2 <= k <= 12 and k % 2 == 0): return False, "nur 1 <= N <= 64, k gerade in 2..12", {}
    n, r, d, qs = QF.eta_span(N, k)
    ok = (int(p["anzahl"]) == n and int(p["dim_span"]) == r and int(p["dim_raum"]) == d)
    return ok, (f"Prüfer zählt {n} holomorphe Eta-Quotienten (trivialer Charakter) vom Gewicht {k} auf Gamma_0({N}); exakter Rang bis zur "
                f"Sturm-Schranke {QF.sturm_bound(k, N)}: {r}; dim M_{k}(Gamma_0({N})) = {d}"), {"anzahl": n, "dim_span": r, "dim_raum": d}


def check_eta_span_tabelle(p):
    k, Nmax = int(p["gewicht"]), int(p["level_bis"])
    if not (2 <= k <= 12 and k % 2 == 0 and 1 <= Nmax <= 40): return False, "nur k gerade in 2..12 und level_bis <= 40", {}
    voll, nicht = [], []
    for N in range(1, Nmax + 1):
        n, r, d, _ = QF.eta_span(N, k)
        (voll if r == d else nicht).append(N)
    ok = sorted(int(x) for x in p.get("voll", [])) == voll and sorted(int(x) for x in p.get("nicht_voll", [])) == nicht
    return ok, f"Prüfer: Eta-Quotienten spannen M_{k}(Gamma_0(N)) für N in {voll}; nicht für N in {nicht} (N <= {Nmax}, exakt)", {"voll": voll, "nicht_voll": nicht}


# ---------------- nicht-holomorphe Prüfungen (numerisch) ----------------

def _mgf_residuen(terme, pts, dps=DPS):
    from . import mgf
    import mpmath as mp
    parsed = [(c, mgf.parse(m)) for c, m in terme]
    out = []
    with mp.workdps(dps + 10):
        for t1, t2 in pts:
            vals = [mp.mpf(c.numerator) / c.denominator * mgf.value(pm, t1, t2, dps) for c, pm in parsed]
            res = abs(mp.fsum(vals)); scale = max(mp.mpf(1), max(abs(v) for v in vals))
            out.append((t1, t2, res / scale))
    return out, parsed


def check_mgf_relation(p):
    from . import mgf
    terme = _terme(p)
    if len(terme) < 2: return False, "Relation braucht mindestens zwei Terme", {}
    anw, lead_ok, lead_txt = mgf.lead_check(terme)               # exakte notwendige Bedingung (Laurent-Leitkoeffizient)
    if anw and not lead_ok: return False, f"exakt widerlegt: {lead_txt} != 0", {"leitkoeffizient": lead_txt}
    pts = mgf.punkte(PRUEF_SEED, N_PUNKTE)
    res, parsed = _mgf_residuen(terme, pts)
    lap = any(pm[0] == "L" for _, pm in parsed)
    tol = 10.0 ** (-(TOL_LAP if lap else TOL))
    worst = max(float(r) for _, _, r in res)
    ok = worst <= tol
    return ok, (f"{lead_txt if anw else 'Leitkoeffizient: ' + lead_txt}; numerisch an {len(pts)} Prüfer-Punkten (Seed {PRUEF_SEED}, {DPS} Stellen): "
                f"max. relatives Residuum {worst:.2e} (Schranke {tol:.0e}{', Laplace per finiten Differenzen' if lap else ''})"), {
               "punkte": pts, "residuen": [f"{float(r):.3e}" for _, _, r in res], "leitkoeffizient": lead_txt}


def check_mgf_relationsraum(p):
    """Die rationalen linearen Relationen zwischen den Basis-Funktionen bilden einen Raum der Dimension genau 'dim', aufgespannt
    von 'relationen'. Jede Relation wird geprüft; dass es keine weiteren gibt, zeigt der Singulärwertabstand (numerisch)."""
    from . import mgf
    import mpmath as mp
    basis = [str(b) for b in p["basis"]]; rels = [[_fr(c) for c in r] for r in p.get("relationen", [])]; dim = int(p["dim"])
    if len(set(basis)) != len(basis) or len(basis) < 2 or len(basis) > 14: return False, "Basis: 2..14 verschiedene Elemente", {}
    if any(len(r) != len(basis) for r in rels): return False, "Relationsvektoren passen nicht zur Basis", {}
    if len(rels) != dim: return False, f"{len(rels)} Relationen angegeben, behauptete Dimension {dim}", {}
    if rels and QF.rank_exact(rels) != dim: return False, "angegebene Relationen sind linear abhängig", {}
    if any(mgf.parse(b)[0] == "L" for b in basis): return False, "Laplace-Terme im Relationsraum nicht erlaubt (Genauigkeit)", {}
    for r in rels:
        ok, why, _ = check_mgf_relation({"terme": [[str(c), b] for c, b in zip(r, basis) if c != 0]})
        if not ok: return False, f"Relation {r} nicht bestätigt: {why}", {}
    n = len(basis); pts = mgf.punkte(PRUEF_SEED + 1, n + 3)
    with mp.workdps(DPS + 10):
        M = mp.matrix([[mgf.value(mgf.parse(b), t1, t2, DPS) for b in basis] for t1, t2 in pts])
        for j in range(n):                                          # Spalten normieren
            s = max(abs(M[i, j]) for i in range(M.rows))
            for i in range(M.rows): M[i, j] /= s
        sv = sorted([abs(x) for x in mp.svd_r(M, compute_uv=False)], reverse=True)
    klein = [x for x in sv if x < mp.mpf(10) ** (-TOL)]
    gross = [x for x in sv if x > mp.mpf(10) ** -8]
    ok = len(klein) == dim and len(gross) == n - dim
    return ok, (f"{dim} Relationen einzeln bestätigt; Singulärwerte der normierten {len(pts)}x{n}-Wertematrix (Seed {PRUEF_SEED + 1}): "
                f"{len(klein)} < 1e-{TOL}, {len(gross)} > 1e-8, kleinster großer {mp.nstr(min(gross), 3) if gross else '-'}"), {
               "singulaerwerte": [mp.nstr(x, 4) for x in sv]}


def _dgv_combo(w):
    """Kombination aus D'Hoker-Green-Vanhove (arXiv:1502.06698, Gl. 3.57) für ungerades w = 2 mu + 3."""
    from math import factorial as fa
    mu = (w - 3) // 2; v = {}
    for m1 in range(mu + 1):
        for m2 in range(mu + 1 - m1):
            c = Fr(fa(mu - m1) * fa(mu - m2) * fa(m1 + m2), fa(m1) * fa(m2) * fa(mu - m1 - m2))
            k = tuple(sorted((1 + mu - m1, 1 + mu - m2, 1 + m1 + m2), reverse=True)); v[k] = v.get(k, 0) + c
    return v


def check_mgf_relationsraum_v2(p):
    """Kriterium 2 (Nachtrag 2026-10-04, vorab festgelegt nach dem Verfehlen von Kriterium 1 bei Gewicht 11): eigene Punkte
    (Seed 4713, n+8 Punkte, |tau1| <= 1/2, 0.9 <= tau2 <= 3.0), 32 Stellen; genau dim Singulärwerte < 1e-24 und alle übrigen > 1e-16
    (halbe Arbeitsgenauigkeit: eine echte Relation liegt auf Rundungsniveau, schlechte Kondition nicht). Jede Relation zusätzlich wie mgf_relation."""
    from . import mgf
    import mpmath as mp, random
    basis = [str(b) for b in p["basis"]]; rels = [[_fr(c) for c in r] for r in p.get("relationen", [])]; dim = int(p["dim"])
    if len(set(basis)) != len(basis) or len(basis) < 2 or len(basis) > 14: return False, "Basis: 2..14 verschiedene Elemente", {}
    if any(len(r) != len(basis) for r in rels) or len(rels) != dim: return False, "Relationen passen nicht zur Basis/Dimension", {}
    if rels and QF.rank_exact(rels) != dim: return False, "angegebene Relationen sind linear abhängig", {}
    if any(mgf.parse(b)[0] == "L" for b in basis): return False, "Laplace-Terme nicht erlaubt", {}
    for r in rels:
        ok, why, _ = check_mgf_relation({"terme": [[str(c), b] for c, b in zip(r, basis) if c != 0]})
        if not ok: return False, f"Relation {r} nicht bestätigt: {why}", {}
    n = len(basis); rnd = random.Random(4713)
    pts = [(f"{rnd.uniform(-0.5, 0.5):.6f}", f"{rnd.uniform(0.9, 3.0):.6f}") for _ in range(n + 8)]
    with mp.workdps(DPS + 10):
        M = mp.matrix([[mgf.value(mgf.parse(b), t1, t2, DPS) for b in basis] for t1, t2 in pts])
        for j in range(n):
            s_ = max(abs(M[i, j]) for i in range(M.rows))
            for i in range(M.rows): M[i, j] /= s_
        sv = sorted([abs(x) for x in mp.svd_r(M, compute_uv=False)], reverse=True)
    klein = [x for x in sv if x < mp.mpf(10) ** (-TOL)]; gross = [x for x in sv if x > mp.mpf(10) ** -16]
    ok = len(klein) == dim and len(gross) == n - dim
    return ok, (f"Kriterium 2: Singulärwerte der normierten {len(pts)}x{n}-Matrix (Seed 4713, tau2 in [0.9, 3]): {len(klein)} < 1e-{TOL}, "
                f"{len(gross)} > 1e-16, kleinster großer {mp.nstr(min(gross), 3) if gross else '-'}, größter kleiner {mp.nstr(max(klein), 3) if klein else '-'}"), {
               "singulaerwerte": [mp.nstr(x, 4) for x in sv]}


def check_mgf_harmonisch(p):
    """Exakt: Delta(sum c_abc C_abc) = lambda * E_w in der algebraischen Laplace-Darstellung (asd/domains/mgf_laplace.py)."""
    from .mgf_laplace import laplace_combo, fmt
    from . import mgf
    w = int(p["gewicht"]); vec = {}
    for k, c in p["kombination"].items():
        pa = mgf.parse(k)
        if pa[0] != "M" or len(pa[1]) != 1 or pa[1][0][0] != "C" or pa[1][0][2] != 1: return False, f"{k}: nur einzelne C(a,b,c)", {}
        a = pa[1][0][1]
        if sum(a) != w: return False, f"{k} hat nicht Gewicht {w}", {}
        vec[a] = vec.get(a, 0) + _fr(c)
    if not any(vec.values()): return False, "leere Kombination", {}
    lam = _fr(p["lambda"]); out = laplace_combo(vec)
    rest = {fmt(k): str(v) for k, v in out.items() if k != ("E", (w,))}
    got = out.get(("E", (w,)), 0)
    ok = not rest and got == lam
    return ok, (f"exakte Laplace-Algebra: Delta X = {got}*E({w})" + (f" + Reste {rest}" if rest else "") + f"; behauptet lambda = {lam}"), {"rest": rest, "lambda": str(got)}


def check_mgf_harmonisch_familie(p):
    """Exakt für alle 3 <= w <= W: der Raum der C-Kombinationen mit Delta X in Q*E_w hat Dimension 1 (w ungerade) bzw. 0 (w gerade);
    für ungerades w wird er von der DGV-Kombination (Gl. 3.57) aufgespannt und es gilt Delta X = w(w-1) f_w E_w mit f_w = 3((w-1)/2)!/w."""
    from math import factorial as fa
    from .mgf_laplace import harmonic_space
    W = int(p["gewicht_bis"])
    if not 3 <= W <= 25: return False, "gewicht_bis muss in 3..25 liegen", {}
    fehler = []
    for w in range(3, W + 1):
        H = harmonic_space(w)
        if w % 2 == 0:
            if H: fehler.append(f"w={w}: dim {len(H)} statt 0")
            continue
        if len(H) != 1: fehler.append(f"w={w}: dim {len(H)} statt 1"); continue
        (vec, lam), = H; d = _dgv_combo(w); k0 = next(iter(vec)); sc = d[k0] / vec[k0]
        if set(d) != set(vec) or any(d[k] != sc * vec[k] for k in vec): fehler.append(f"w={w}: nicht die DGV-Kombination"); continue
        if sc * lam / (w * (w - 1)) != Fr(3 * fa((w - 1) // 2), w): fehler.append(f"w={w}: f_w = {sc * lam / (w * (w - 1))}")
    return (not fehler), ("exakt für alle 3 <= w <= %d: harmonischer Raum dim 1 (ungerade, DGV-Kombination, f_w = 3((w-1)/2)!/w) bzw. 0 (gerade)" % W
                          + (f"; Abweichungen: {fehler}" if fehler else "")), {"fehler": fehler}


class ModularDomain(Domain):
    name = "modular"
    recherche_ziel = ("Modular graph functions in the low-energy expansion of genus-one closed-string amplitudes: algebraic and "
                      "differential relations among two-loop (dihedral) modular graph functions C_{a,b,c}, non-holomorphic Eisenstein "
                      "series, Laplace eigenvalue equations and Laurent polynomials; plus identities between holomorphic modular forms, "
                      "eta quotients and theta series that appear in string partition functions (Sturm bound certificates).")
    recherche_sperre = []
    recherche_klassiker = [
        "D'Hoker Green Vanhove modular structure genus-one superstring low energy expansion",
        "D'Hoker Green Gurdogan Vanhove modular graph functions",
        "D'Hoker Green Vanhove proof modular relation 1- 2- 3-loop Feynman diagrams torus",
        "D'Hoker Kaidi hierarchy of modular graph identities",
        "Green Russo Vanhove low energy expansion four-particle genus-one amplitude type II",
        "D'Hoker Green identities between modular graph forms",
        "Basu Poisson equation Mercedes diagram string theory genus one",
        "Kleinschmidt Verschinin tetrahedral modular graph functions",
        "Gerken Kleinschmidt Schlotterer generating series modular graph forms iterated Eisenstein integrals",
        "Brown class of non-holomorphic modular forms",
        "Zerbini single-valued multiple zeta values genus one superstring amplitudes",
        "Gerken basis decompositions Mathematica package modular graph forms",
        "Rouse Webb spaces of modular forms spanned by eta-quotients",
        "Sturm congruence of modular forms bound",
        "D'Hoker Green Gurdogan Vanhove Laplace eigenvalue equations length three modular graph functions",
    ]
    recherche_crossref = True
    recherche_inspire = True       # INSPIRE-HEP: Hauptquelle für Stringtheorie (arXiv-IDs, Abstracts)
    kontext = (
        "Thema: Modulformen und Identitäten aus der Stringtheorie.\n"
        "(A) Holomorph: q = e^{2 pi i tau}. Bausteine: E<k> bzw. E<k>(d) (Eisenstein E_k(d tau), k >= 4 gerade, a_0 = 1), F2(d) = E_2(tau) - d E_2(d tau), "
        "eta(d) (Dedekind eta(d tau)), Delta(d) = eta(d tau)^24, theta(d) = sum_n q^{d n^2}, thetaE8/thetaD16 (Thetareihen der Gitter E8 und D16+, "
        "durch Gitterabzählung), j = E4^3/Delta. Monome mit '*' und '^' (z. B. 'eta(2)^20*eta(1)^-8*eta(4)^-8'). Eine Identität sum c_t f_t = 0 auf "
        "Gamma_0(N) ist bewiesen, wenn alle Terme modular vom selben Gewicht und Charakter sind und die Koeffizienten bis zur Sturm-Schranke "
        "k*[SL2(Z):Gamma_0(N)]/12 verschwinden. Stringtheorie-Bezug: Zustandssummen (Bosonen: 1/eta^24; Superstring: Theta-Funktionen mit GSO-"
        "Projektion; heterotische Gitter E8+E8 und D16+), j-Funktion.\n"
        "(B) Nicht-holomorph: tau = tau1 + i tau2, p = m tau + n. E(s) = sum'_p (tau2/(pi |p|^2))^s, C(a,b,c) = sum'_{p1+p2+p3=0} prod (tau2/(pi |p_i|^2))^{a_i} "
        "(Modulgraphfunktionen zweischleifiger 'dihedraler' Graphen, Gewicht w = a+b+c). Sie treten als Koeffizienten der Niederenergie-Entwicklung "
        "der Einschleifen-Amplitude geschlossener Strings auf. zeta(k) ist die Riemannsche Zetafunktion (Konstante). L[F] ist der hyperbolische "
        "Laplace-Operator tau2^2 (d^2/dtau1^2 + d^2/dtau2^2) angewandt auf F. Gesucht: rationale lineare Relationen und Laplace-Gleichungen "
        "zwischen solchen Funktionen. Werte sind numerisch (~30 Stellen); die Prüfung erfolgt an eigenen Zufallspunkten des Prüfers.")
    primitive_doc = """Verfügbare Experimente (JSON {"op": ..., "args": {...}}):
- qexp {monom, n}: exakte q-Koeffizienten a_0..a_{n-1} (bzw. ab dem Polterm) eines Monoms, dazu Gewicht und Eta-Anteil.
- info {monom, level}: Gewicht, Charakter, Modularitätsbedingungen (Newman), Ordnungen an den Spitzen von Gamma_0(level).
- dim {gewicht, level}: dim M_k(Gamma_0(N)) und Sturm-Schranke.
- holo_relationen {level, monome: [...]}: exakter Kern der Koeffizientenmatrix bis zur Sturm-Schranke (Kandidaten-Relationen; ungleiche Gewichte -> Fehler).
- eta_quotienten {level, gewicht}: alle holomorphen Eta-Quotienten (Gordon-Hughes-Newman-Bedingungen) mit trivialem Charakter, Anzahl, Rang ihres Spanns, dim M_k (<= 64).
- eta_span_scan {gewicht, level_bis}: Tabelle Rang vs. Dimension für alle N <= level_bis (<= 40).
- mgf_wert {ausdruck, tau1, tau2, dps?}: numerischer Wert eines Monoms aus C(a,b,c), E(s), zeta(k) (auch L[...]) an einem Punkt (~5-60 s).
- mgf_laplace_exakt {kombination: {"C(a,b,c)": c, ...}}: Delta der Kombination EXAKT als Summe von C's und Eisenstein-Produkten (schnell).
- mgf_harmonisch_raum {gewicht}: exakt alle C-Kombinationen vom Gewicht w mit Delta X in Q*E(w) (schnell, w <= 25).
- mgf_leitkoeffizient {ausdruck}: exakter rationaler Leitkoeffizient der Laurent-Entwicklung in y = pi*tau2 (schnell).
- mgf_relationen {basis: [...], seed?, n_punkte? (<= 12), dps? (<= 60)}: Kandidaten für alle ganzzahligen linearen Relationen zwischen den Basis-Funktionen
  (PSLQ über mehrere Zufallspunkte). Basis-Elemente sind Monome, z. B. "C(3,1,1)", "E(2)*E(3)", "zeta(3)*E(2)", "L[C(2,1,1)]". Teuer
  (Minuten; Laplace-Terme besonders). Das Ergebnis ist ein Kandidat, kein Beweis."""
    claim_doc = """Prüfungstypen (Koeffizienten immer als exakte rationale Zahl, z. B. "7/30" oder -276; nie Gleitkomma):
- {"typ": "identitaet", "level": N, "terme": [[c1, "monom1"], [c2, "monom2"], ...]}: sum c_t * monom_t = 0 als Modulformen auf Gamma_0(N).
  Zertifikat (exakt): Modularität jedes Terms (Newman-Bedingungen, gleiches Gewicht und gleicher Charakter), Polordnungen an allen
  Spitzen (Ligozat), dann exakte Koeffizienten bis zur Sturm-Schranke. Theorem-Stufe.
- {"typ": "koeffizient", "monom": "...", "n": n, "wert": "196884"}: exakter q^n-Koeffizient.
- {"typ": "eta_span", "level": N, "gewicht": k, "anzahl": a, "dim_span": r, "dim_raum": d}: Prüfer zählt alle holomorphen Eta-Quotienten
  (trivialer Charakter) selbst, berechnet den exakten Rang ihres Spanns und dim M_k(Gamma_0(N)).
- {"typ": "eta_span_tabelle", "gewicht": k, "level_bis": Nmax, "voll": [N, ...], "nicht_voll": [N, ...]}: für alle N <= Nmax (<= 40)
  zugleich: genau für die Level in 'voll' spannen die Eta-Quotienten ganz M_k(Gamma_0(N)).
- {"typ": "mgf_relation", "terme": [[c1, "ausdruck1"], ...]}: sum c_t * ausdruck_t = 0 als Funktion von tau. Zuerst exakte notwendige
  Bedingung: der rationale Leitkoeffizient der höchsten Potenz von y = pi*tau2 (Laurent-Entwicklung) muss verschwinden; dann numerisch an
  4 eigenen Zufallspunkten mit 32 Stellen, Schranke 1e-24 relativ (1e-14, falls ein L[...]-Term vorkommt).
- {"typ": "mgf_harmonisch", "gewicht": w, "kombination": {"C(a,b,c)": c, ...}, "lambda": λ}: EXAKT in rationaler Arithmetik über die
  algebraische Laplace-Darstellung: Delta(sum c C) = λ E(w) ohne weitere Terme.
- {"typ": "mgf_harmonisch_familie", "gewicht_bis": W}: exakt für alle 3 <= w <= W (<= 25): harmonischer Raum dim 1/0, DGV-Kombination, f_w.
- {"typ": "mgf_relationsraum_v2", ...}: wie mgf_relationsraum, Kriterium 2: n+8 eigene Punkte (Seed 4713, 0.9 <= tau2 <= 3), übrige Singulärwerte > 1e-16.
- {"typ": "mgf_relationsraum", "basis": ["...", ...], "dim": r, "relationen": [[c_1, ..., c_n], ...]}: die rationalen linearen
  Relationen zwischen den Basis-Funktionen bilden GENAU einen r-dimensionalen Raum, aufgespannt von den angegebenen Vektoren
  (jede Relation geprüft wie mgf_relation; Vollständigkeit über Singulärwerte an n+3 Prüfer-Punkten; numerisch)."""

    def run_op(self, op, args):
        try:
            if op == "qexp":
                mon = QF.parse_monom(args["monom"]); n = min(int(args.get("n", 20)), 300)
                w, eta, lev = QF.meta(mon); s = QF.series(mon, n)
                return {"gewicht": str(w), "eta_anteil": eta, "offset": str(s.off), "koeffizienten": [str(x) for x in s.c[:n]]}
            if op == "info":
                mon = QF.parse_monom(args["monom"]); N = int(args["level"]); w, eta, lev = QF.meta(mon)
                ok, why = QF.newman_ok(eta, N) if eta else (True, "kein Eta-Anteil")
                return {"gewicht": str(w), "level_teilt": all(N % d == 0 for d in lev), "newman": ok, "grund": why,
                        "charakter_kern": QF.character(eta, Fr(sum(eta.values()), 2)) if eta else 1,
                        "ordnungen_eta_anteil": {str(d): str(QF.eta_order(eta, N, d)) for d, _, _ in QF.cusp_classes(N)} if eta else "holomorph (>= 0)"}
            if op == "dim":
                k, N = int(args["gewicht"]), int(args["level"])
                return {"dim_M": QF.dim_M(k, N), "sturm_schranke": str(QF.sturm_bound(k, N)), "index": QF.index(N)}
            if op == "holo_relationen": return holo_relationen(int(args["level"]), list(args["monome"]))
            if op == "eta_quotienten":
                N, k = int(args["level"]), int(args["gewicht"])
                if N > 64: return {"fehler": "level <= 64"}
                n, r, d, qs = QF.eta_span(N, k)
                return {"anzahl": n, "rang_span": r, "dim_M": d, "beispiele": [QF.eta_str(e) for e in qs[:12]]}
            if op == "eta_span_scan":
                k, Nmax = int(args["gewicht"]), min(int(args["level_bis"]), 40)
                rows = []
                for N in range(1, Nmax + 1):
                    n, r, d, _ = QF.eta_span(N, k); rows.append({"N": N, "anzahl": n, "rang": r, "dim": d})
                return {"tabelle": rows}
            if op == "mgf_wert":
                from . import mgf
                import mpmath as mp
                dps = min(int(args.get("dps", 30)), 40)
                v = mgf.value(mgf.parse(args["ausdruck"]), str(args["tau1"]), str(args["tau2"]), dps)
                return {"wert": mp.nstr(v, dps - 2), "hinweis": "numerisch"}
            if op == "mgf_leitkoeffizient":
                from . import mgf
                W, c, Z = mgf.lead(mgf.parse(args["ausdruck"]))
                return {"grad": W, "koeffizient": str(c), "zeta_faktoren": list(Z), "lesart": "F = koeffizient * prod zeta * y^grad + O(y^(grad-1)), y = pi*tau2 (exakt)"}
            if op == "mgf_laplace_exakt":
                from .mgf_laplace import laplace_combo, fmt
                from . import mgf
                vec = {}
                for k, c in args["kombination"].items():
                    pa = mgf.parse(k); vec[pa[1][0][1]] = vec.get(pa[1][0][1], 0) + Fr(str(c))
                return {"laplace": {fmt(k): str(v) for k, v in laplace_combo(vec).items()}, "hinweis": "exakt (algebraische Laplace-Darstellung)"}
            if op == "mgf_harmonisch_raum":
                from .mgf_laplace import harmonic_space
                w = int(args["gewicht"])
                if not 3 <= w <= 25: return {"fehler": "gewicht in 3..25"}
                return {"basis": [{"kombination": {"C(%d,%d,%d)" % k: str(v) for k, v in vec.items()}, "lambda": str(lam)} for vec, lam in harmonic_space(w)],
                        "lesart": "Delta(kombination) = lambda * E(w) exakt"}
            if op == "mgf_relationen":
                from . import mgf
                b = list(args["basis"])
                if len(b) > 12: return {"fehler": "höchstens 12 Basis-Elemente"}
                dps = min(int(args.get("dps", 32 if len(b) <= 6 else 45)), 60)      # große Basen brauchen mehr Stellen für PSLQ
                npk = min(int(args["n_punkte"]), 12) if args.get("n_punkte") else None          # Ressourcengrenze für Agenten-Experimente
                r = mgf.find_relations(b, seed=int(args.get("seed", 1)), n_punkte=npk, dps=dps, maxcoeff=10 ** 9)
                return r | {"hinweis": "Kandidaten; zertifiziert erst durch mgf_relation / mgf_relationsraum"}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    def check(self, p):
        try:
            t = p.get("typ")
            if t == "identitaet": return check_identitaet(p)
            if t == "koeffizient": return check_koeffizient(p)
            if t == "eta_span": return check_eta_span(p)
            if t == "eta_span_tabelle": return check_eta_span_tabelle(p)
            if t == "mgf_relation": return check_mgf_relation(p)
            if t == "mgf_relationsraum": return check_mgf_relationsraum(p)
            if t == "mgf_harmonisch": return check_mgf_harmonisch(p)
            if t == "mgf_relationsraum_v2": return check_mgf_relationsraum_v2(p)
            if t == "mgf_harmonisch_familie": return check_mgf_harmonisch_familie(p)
            return False, f"unbekannter Prüfungstyp {t}", {}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def level(self, p):
        if p.get("typ") in ("mgf_harmonisch", "mgf_harmonisch_familie"): return "computed_rigorous"
        return "observed" if str(p.get("typ", "")).startswith("mgf") else "computed_rigorous"

    def relevanz(self, p):
        t = p.get("typ")
        if t in ("eta_span_tabelle", "mgf_relationsraum", "mgf_relationsraum_v2", "mgf_harmonisch_familie"): return "hauptresultat"
        if t == "mgf_harmonisch": return "stuetze"
        if t == "mgf_relation":
            return "hauptresultat" if any("L[" in str(m) for _, m in p.get("terme", [])) or max(_w(m) for _, m in p.get("terme", [])) >= 6 else "stuetze"
        if t == "identitaet": return "stuetze"
        return "beispiel"

    def parameter(self):
        return {"q": ("e^{2 pi i tau}", "expansion variable of holomorphic forms"),
                "normalisation_E": ("a_0 = 1", "holomorphic Eisenstein series E_k = 1 - (2k/B_k) sum sigma_{k-1}(n) q^n"),
                "normalisation_MGF": ("(tau2/(pi |m tau + n|^2))^a", "lattice-sum normalisation of E_s and C_{a,b,c} (D'Hoker-Green-Vanhove)"),
                "verifier_points": (f"{N_PUNKTE} points, seed {PRUEF_SEED}, |tau1| <= 1/2, 1 <= tau2 <= 2.5", "random evaluation points chosen by the verifier"),
                "precision": (f"{DPS} digits", "working precision of the verifier for modular graph functions"),
                "tolerance": (f"1e-{TOL} (1e-{TOL_LAP} with Laplacian)", "maximal relative residual accepted for a numerical relation"),
                "laplacian_step": ("h = 1e-6", "step of the fourth-order finite-difference Laplacian")}

    def figures(self, state, outdir, lang="en"):
        out = []
        for f in (_konstanten_figure, _margins_figure, _eta_figure):
            try: out += f(state, outdir, lang)
            except Exception as e: print(f"Abbildung {f.__name__} fehlgeschlagen: {e}")
        return out

    def describe(self, p, lang="de"):
        t = p.get("typ"); en = lang == "en"
        try:
            if t == "identitaet":
                s = _fmt(_terme(p))
                return (f"On Gamma_0({p['level']}): {s} = 0 (exact; Sturm-bound certificate)." if en else
                        f"Auf Gamma_0({p['level']}) gilt {s} = 0 (exakt; Sturm-Zertifikat).")
            if t == "koeffizient":
                return (f"The coefficient of q^{p['n']} in {p['monom']} equals {p['wert']} (exact)." if en else
                        f"Der Koeffizient von q^{p['n']} in {p['monom']} ist {p['wert']} (exakt).")
            if t == "eta_span":
                return (f"There are exactly {p['anzahl']} holomorphic eta quotients of weight {p['gewicht']} with trivial character on Gamma_0({p['level']}); "
                        f"they span a space of dimension {p['dim_span']} inside M_{p['gewicht']}(Gamma_0({p['level']})), which has dimension {p['dim_raum']} (exact)." if en else
                        f"Es gibt genau {p['anzahl']} holomorphe Eta-Quotienten vom Gewicht {p['gewicht']} mit trivialem Charakter auf Gamma_0({p['level']}); "
                        f"ihr Spann hat Dimension {p['dim_span']}, dim M_{p['gewicht']}(Gamma_0({p['level']})) = {p['dim_raum']} (exakt).")
            if t == "eta_span_tabelle":
                return (f"For all N <= {p['level_bis']}: holomorphic eta quotients with trivial character span M_{p['gewicht']}(Gamma_0(N)) exactly for "
                        f"N in {sorted(p.get('voll', []))} and not for N in {sorted(p.get('nicht_voll', []))} (exact, exhaustive)." if en else
                        f"Für alle N <= {p['level_bis']}: holomorphe Eta-Quotienten mit trivialem Charakter spannen M_{p['gewicht']}(Gamma_0(N)) genau für "
                        f"N in {sorted(p.get('voll', []))}, nicht für N in {sorted(p.get('nicht_voll', []))} (exakt, vollständig).")
            if t == "mgf_relation":
                s = _fmt(_terme(p))
                return (f"Numerically (32 digits, 4 verifier-chosen points, relative residual <= 1e-{TOL_LAP if 'L[' in s else TOL}): {s} = 0 as functions of tau." if en else
                        f"Numerisch (32 Stellen, 4 Prüfer-Punkte, rel. Residuum <= 1e-{TOL_LAP if 'L[' in s else TOL}): {s} = 0 als Funktionen von tau.")
            if t == "mgf_harmonisch":
                X = _fmt([(c, k) for k, c in p["kombination"].items()])
                return (f"Exactly (algebraic Laplace representation of D'Hoker-Green-Vanhove, re-derived and checked in rational arithmetic): "
                        f"Delta({X}) = {p['lambda']}*E({p['gewicht']}); hence {X} - {Fr(str(p['lambda'])) / (int(p['gewicht']) * (int(p['gewicht']) - 1))}*E({p['gewicht']}) "
                        f"is annihilated by the Laplacian." if en else
                        f"Exakt (algebraische Laplace-Darstellung nach D'Hoker-Green-Vanhove, nachgerechnet in rationaler Arithmetik): "
                        f"Delta({X}) = {p['lambda']}*E({p['gewicht']}).")
            if t == "mgf_harmonisch_familie":
                return (f"Exactly, for every weight 3 <= w <= {p['gewicht_bis']}: the rational combinations X of dihedral C(a,b,c) of weight w with "
                        f"Delta X in Q*E(w) form a space of dimension 1 for odd w and 0 for even w; for odd w = 2mu+3 it is spanned by the combination of "
                        f"D'Hoker-Green-Vanhove (eq. 3.57 of arXiv:1502.06698), and Delta X = w(w-1) f_w E(w) with f_w = 3((w-1)/2)!/w in that normalisation." if en else
                        f"Exakt für alle 3 <= w <= {p['gewicht_bis']}: harmonischer Raum dim 1 (ungerade, DGV-Kombination, f_w = 3((w-1)/2)!/w) bzw. 0 (gerade).")
            if t == "mgf_relationsraum_v2":
                return self.describe(dict(p, typ="mgf_relationsraum"), lang).replace("completeness by a singular-value gap", "completeness by criterion 2: all other singular values above 1e-16 at 20 verifier points").replace("Vollständigkeit über Singulärwertabstand", "Vollständigkeit nach Kriterium 2 (übrige Singulärwerte > 1e-16)")
            if t == "mgf_relationsraum":
                formeln = "; ".join(_fmt([(c, b) for c, b in zip(r, p["basis"]) if Fr(str(c)) != 0]) + " = 0" for r in p.get("relationen", []))
                ws = sorted({_w(b) for b in p["basis"] if _w(b)}); wtxt = f" (weight {ws[0]})" if len(ws) == 1 else ""
                return (f"Numerically, the rational linear relations among the modular graph functions {', '.join(p['basis'])}{wtxt} form a space of dimension "
                        f"exactly {p['dim']}" + (f", spanned by the identity {formeln}" if formeln else ", i.e. there is no such relation") +
                        f" (each relation checked to 1e-{TOL} at verifier points with exact leading Laurent coefficient; completeness by a singular-value gap)." if en else
                        f"Numerisch bilden die rationalen linearen Relationen zwischen {', '.join(p['basis'])}{wtxt.replace('weight', 'Gewicht')} einen Raum der Dimension genau {p['dim']}" +
                        (f", aufgespannt von der Identität {formeln}" if formeln else ", d. h. es gibt keine solche Relation") +
                        f" (jede Relation auf 1e-{TOL} an Prüfer-Punkten geprüft, exakter Laurent-Leitkoeffizient; Vollständigkeit über Singulärwertabstand).")
        except Exception:
            pass
        return ("Verified: " if en else "Geprüft: ") + json.dumps(p, ensure_ascii=False)

    def inhaltsklasse(self, p):
        """Grobe Inhaltsklasse für Volltext-Belege: 'harmonisch:w' bzw. 'relation:w' (Gewicht-w-Identität aus C's, E(w), zeta(w))."""
        from . import mgf
        t = p.get("typ")
        if t == "mgf_harmonisch": return f"harmonisch:{int(p['gewicht'])}"
        try:
            if t == "mgf_relation": ms = [m for c, m in p["terme"] if Fr(str(c)) != 0]
            elif t in ("mgf_relationsraum", "mgf_relationsraum_v2") and int(p["dim"]) == 1:
                ms = [b for c, b in zip(p["relationen"][0], p["basis"]) if Fr(str(c)) != 0]
            else: return t
            pa = [mgf.parse(m) for m in ms]
            if any(x[0] == "L" for x in pa): return "laplace"
            ws = {mgf.gewicht(x) for x in pa}
            if len(ws) == 1 and all(len(x[1]) == 1 and x[1][0][2] == 1 for x in pa): return f"relation:{ws.pop()}"
        except Exception: pass
        return str(t)

    def inhalt(self, p):
        """Mathematischer Inhalt einer Prüfung als Schlüssel (für den Neuheits-Abgleich): Relationen als primitive, vorzeichen-
        normierte Koeffizientenvektoren über den beteiligten Monomen; ein Relationsraum der Dimension 1 ist gleichwertig zu seiner Relation."""
        t = p.get("typ")
        def norm(paare):
            from math import gcd
            d = {}
            for c, m in paare:
                c = Fr(str(c))
                if c: d[str(m).replace(" ", "")] = d.get(str(m).replace(" ", ""), 0) + c
            d = {m: c for m, c in d.items() if c}
            if not d: return "0"
            den = math.lcm(*[c.denominator for c in d.values()]); v = {m: int(c * den) for m, c in d.items()}
            g = 0
            for x in v.values(): g = gcd(g, abs(x))
            v = {m: x // g for m, x in v.items()}
            if v[sorted(v)[0]] < 0: v = {m: -x for m, x in v.items()}
            return json.dumps(sorted(v.items()))
        try:
            if t in ("mgf_relation", "identitaet"): return t[:3] + norm(p["terme"])
            if t == "mgf_relationsraum" and int(p["dim"]) == 1: return "mgf" + norm(zip(p["relationen"][0], p["basis"]))
        except Exception: pass
        return json.dumps(p, sort_keys=True)

    def widerspricht(self, p, q):
        for x, y in ((p, q), (q, p)):
            if x.get("typ") == y.get("typ") == "koeffizient" and x.get("monom") == y.get("monom") and str(x.get("n")) == str(y.get("n")):
                return Fr(str(x["wert"])) != Fr(str(y["wert"]))
            if x.get("typ") == y.get("typ") == "eta_span" and (x.get("level"), x.get("gewicht")) == (y.get("level"), y.get("gewicht")):
                return any(str(x.get(k)) != str(y.get(k)) for k in ("anzahl", "dim_span", "dim_raum"))
            if x.get("typ") == y.get("typ") == "mgf_relationsraum" and sorted(x.get("basis", [])) == sorted(y.get("basis", [])):
                return int(x["dim"]) != int(y["dim"])
            if x.get("typ") == "mgf_relationsraum" and y.get("typ") == "mgf_relation" and int(x.get("dim", 1)) == 0:
                ms = {m for _, m in y.get("terme", [])}
                return ms <= set(x.get("basis", []))
        return False

    def selftest(self):
        jac = [[1, "theta^4"], [-1, "eta(1)^8*eta(2)^-4"], [-16, "eta(4)^8*eta(2)^-4"]]
        return [
            ({"typ": "identitaet", "level": 1, "terme": [[1, "E4^3"], [-1, "E6^2"], [-1728, "Delta"]]}, True),           # Delta = (E4^3 - E6^2)/1728
            ({"typ": "identitaet", "level": 1, "terme": [[1, "E4^3"], [-1, "E6^2"], [-1727, "Delta"]]}, False),          # knapp daneben
            ({"typ": "identitaet", "level": 4, "terme": jac}, True),                                                    # Jacobi: theta3^4 = theta2^4 + theta4^4
            ({"typ": "identitaet", "level": 4, "terme": [[1, "theta^4"], [-1, "eta(1)^8*eta(2)^-4"], [-15, "eta(4)^8*eta(2)^-4"]]}, False),
            ({"typ": "identitaet", "level": 2, "terme": jac}, False),                                                   # Regelverletzung: Level 2 falsch
            ({"typ": "identitaet", "level": 1, "terme": [[1, "E2^2"], [-1, "E4"]]}, False),                              # E2 ist nicht modular
            ({"typ": "identitaet", "level": 1, "terme": [[1, "thetaE8^2"], [-1, "thetaD16"]]}, True),                    # Gitter E8+E8 vs D16+
            ({"typ": "identitaet", "level": 1, "terme": [[1, "j"], [-1, "E4^3*eta(1)^-24"]]}, True),                    # schwach holomorph
            ({"typ": "identitaet", "level": 1, "terme": [[1, "j*Delta"], [-1, "E4^3"], [1, "eta(1)^24"]]}, False),
            ({"typ": "koeffizient", "monom": "j", "n": 1, "wert": "196884"}, True),
            ({"typ": "koeffizient", "monom": "j", "n": 1, "wert": "196883"}, False),
            ({"typ": "eta_span", "level": 11, "gewicht": 2, "anzahl": 1, "dim_span": 1, "dim_raum": 2}, True),
            ({"typ": "eta_span", "level": 11, "gewicht": 2, "anzahl": 1, "dim_span": 2, "dim_raum": 2}, False),
            ({"typ": "mgf_relation", "terme": [[1, "C(1,1,1)"], [-1, "E(3)"], [-1, "zeta(3)"]]}, True),                 # Zagier / D'Hoker-Green-Vanhove
            ({"typ": "mgf_relation", "terme": [[30, "C(2,2,1)"], [-12, "E(5)"], [-1, "zeta(5)"]]}, True),                 # C221 = 2/5 E5 + zeta(5)/30
            ({"typ": "mgf_relation", "terme": [[30, "C(2,1,1)"], [-12, "E(4)"], [-1, "zeta(5)"]]}, False),               # falsche Übertragung auf w = 4
            ({"typ": "mgf_relation", "terme": [[1, "C(1,1,1)"], [-1, "E(3)"], ["-1000000000000000000001/1000000000000000000000", "zeta(3)"]]}, False),  # 1e-21 daneben
            ({"typ": "mgf_relation", "toleranz": 1.0, "terme": [[1, "C(1,1,1)"], [-1, "E(3)"]]}, False),                 # Toleranz-Lockerung wird ignoriert
            ({"typ": "mgf_relation", "terme": [[1, "C(1,1,1)"], [-1.0, "E(3)"], [-1, "zeta(3)"]]}, False),               # Regel: Gleitkomma-Koeffizient
            ({"typ": "mgf_relation", "terme": [[1, "L[C(2,1,1)]"], [-2, "C(2,1,1)"], [-9, "E(4)"], [1, "E(2)^2"]]}, True),  # D'Hoker-Green-Vanhove
            ({"typ": "mgf_relation", "terme": [[1, "L[C(2,1,1)]"], [-2, "C(2,1,1)"], [-8, "E(4)"], [1, "E(2)^2"]]}, False),
            ({"typ": "mgf_relationsraum", "basis": ["C(2,2,1)", "E(5)", "zeta(5)"], "dim": 1, "relationen": [[30, -12, -1]]}, True),
            ({"typ": "mgf_harmonisch", "gewicht": 3, "kombination": {"C(1,1,1)": 1}, "lambda": 6}, True),             # Delta C111 = 6 E3
            ({"typ": "mgf_harmonisch", "gewicht": 9, "kombination": {"C(4,4,1)": 9, "C(4,3,2)": 18, "C(3,3,3)": 4}, "lambda": 288}, True),  # DGV (3.33)
            ({"typ": "mgf_harmonisch", "gewicht": 9, "kombination": {"C(4,4,1)": 9, "C(4,3,2)": 18, "C(3,3,3)": 4}, "lambda": 287}, False),
            ({"typ": "mgf_harmonisch", "gewicht": 5, "kombination": {"C(3,1,1)": 1}, "lambda": 16}, False),          # Delta C311 hat C- und E-Produkt-Reste
            ({"typ": "mgf_harmonisch", "gewicht": 5, "kombination": {"C(2,2,2)": 1}, "lambda": 8}, False),           # falsches Gewicht
            ({"typ": "mgf_harmonisch_familie", "gewicht_bis": 15}, True),
            ({"typ": "mgf_harmonisch_familie", "gewicht_bis": 99}, False),                                            # Regelverletzung
            ({"typ": "mgf_relationsraum", "basis": ["C(1,1,1)", "E(3)", "zeta(3)", "E(2)"], "dim": 0, "relationen": []}, False),  # verschweigt eine Relation
        ]


def _margins_figure(state, outdir, lang="en"):
    """Numerische Prüfmargen: max. relatives Residuum je bestätigter MGF-Relation (aus dem Prüfer-Grund) gegen die Schranke."""
    import re
    rows = []
    for c in state["claims"]:
        if c.get("status") != "bestätigt" or c["pruefung"].get("typ") not in ("mgf_relation", "mgf_relationsraum"): continue
        m = re.findall(r"Residuum ([0-9.]+e[-+]\d+)", c.get("grund", ""))
        if m: rows.append((c["id"], max(float(x) for x in m), "L[" in json.dumps(c["pruefung"])))
    if not rows: return []
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ..figstyle import apply_style; apply_style()
    fig, ax = plt.subplots(figsize=(4.8, 0.45 * len(rows) + 1.2))
    ys = range(len(rows))
    ax.barh(list(ys), [max(r[1], 1e-45) for r in rows], color=["#d9480f" if r[2] else "#2f6fdf" for r in rows])
    ax.axvline(10.0 ** -TOL, ls="--", lw=1, color="#2f6fdf"); ax.axvline(10.0 ** -TOL_LAP, ls=":", lw=1, color="#d9480f")
    ax.set_xscale("log"); ax.set_yticks(list(ys)); ax.set_yticklabels([r[0] for r in rows], fontsize=7)
    ax.set_xlabel("max. relative residual at verifier points" if lang == "en" else "max. relatives Residuum an Prüfer-Punkten")
    fig.tight_layout(); fig.savefig(f"{outdir}/margins.pdf"); fig.savefig(f"{outdir}/margins.png", dpi=200); plt.close(fig)
    cap = (f"Numerical verification margins: largest relative residual of each confirmed relation among modular graph functions at the "
           f"verifier's own random points ({DPS} digits). Dashed: acceptance threshold $10^{{-{TOL}}}$; dotted: threshold $10^{{-{TOL_LAP}}}$ for "
           f"relations containing a Laplacian (orange)." if lang == "en" else "Numerische Prüfmargen der bestätigten Relationen.")
    return [("margins.pdf", cap, [f"C-{r[0]}" for r in rows])]


def _konstanten_figure(state, outdir, lang="en"):
    """g_w/zeta(w) nach der Vermutung (Linie) und die vom Prüfer bestätigten Gewichte (Punkte)."""
    from fractions import Fraction as F
    from math import factorial as fa, comb, log10
    def bern(n):
        B = [F(1)]
        for m in range(1, n + 1): B.append(-sum(comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
        return B[n]
    ws = list(range(3, 26, 2)); g = {w: 6 * abs(bern(w - 1)) / fa((w - 1) // 2) for w in ws}
    best, ids = set(), []
    for c in state["claims"]:
        if c.get("status") != "bestätigt": continue
        k = ModularDomain.inhaltsklasse(None, c["pruefung"])
        if k.startswith("relation:"): best.add(int(k.split(":")[1])); ids.append(c["id"])
    if not best: return []
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ..figstyle import apply_style; apply_style()
    fig, ax = plt.subplots(figsize=(4.8, 2.8))
    ax.plot(ws, [log10(float(g[w])) for w in ws], "-", color="#8a8f98", lw=1, label="conjectured $6|B_{w-1}|/((w-1)/2)!$")
    bw = sorted(w for w in best if w in g)
    ax.plot(bw, [log10(float(g[w])) for w in bw], "o", color="#2f6fdf", label="confirmed by the verifier")
    if 17 in best: ax.plot([17], [log10(float(g[17]))], "s", ms=7, mfc="none", color="#d9480f", label="preregistered blind test")
    ax.set_xlabel("weight $w$"); ax.set_ylabel(r"$\log_{10}(g_w/\zeta(w))$"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{outdir}/konstanten.pdf"); fig.savefig(f"{outdir}/konstanten.png", dpi=200); plt.close(fig)
    cap = ("Integration constants $g_w$ of the odd-weight identities in the normalisation of eq. (3.57) of D'Hoker-Green-Vanhove: conjectured closed form "
           "(line) and the weights at which the verifier confirmed the identity numerically (dots, 32 digits, 4 verifier points); the square marks the "
           "preregistered blind test at $w = 17$.")
    return [("konstanten.pdf", cap, [f"C-{i}" for i in ids])]


def _eta_figure(state, outdir, lang="en"):
    """Rang des Eta-Quotienten-Spanns gegen dim M_k(Gamma_0(N)) aus bestätigten Tabellen-Claims (vom Prüfer neu berechnet)."""
    cs = [c for c in state["claims"] if c.get("status") == "bestätigt" and c["pruefung"].get("typ") == "eta_span_tabelle"]
    if not cs: return []
    p = max(cs, key=lambda c: int(c["pruefung"]["level_bis"]))["pruefung"]; k, Nmax = int(p["gewicht"]), int(p["level_bis"])
    Ns, rk, dm = [], [], []
    for N in range(1, Nmax + 1):
        n, r, d, _ = QF.eta_span(N, k); Ns.append(N); rk.append(r); dm.append(d)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ..figstyle import apply_style; apply_style()
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    ax.bar([x - 0.2 for x in Ns], dm, width=0.4, color="#b8bcc4", label=f"dim $M_{k}(\\Gamma_0(N))$")
    ax.bar([x + 0.2 for x in Ns], rk, width=0.4, color="#2f6fdf", label="rank of eta-quotient span")
    ax.set_xlabel("level N"); ax.set_ylabel("dimension"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{outdir}/eta_span.pdf"); fig.savefig(f"{outdir}/eta_span.png", dpi=200); plt.close(fig)
    ids = [f"C-{c['id']}" for c in cs]
    return [("eta_span.pdf", f"Exact comparison, for every level $N \\le {Nmax}$, of $\\dim M_{k}(\\Gamma_0(N))$ (grey) with the rank of the span of all "
             f"holomorphic eta quotients of weight {k} with trivial character (blue).", ids)]


def _w(m):
    from . import mgf
    try: return mgf.gewicht(mgf.parse(m))
    except Exception: return 0


def holo_relationen(N, monome):
    """Exakter Kern: Relationen sum c_i f_i = 0 zwischen Monomen gleichen Gewichts auf Gamma_0(N) (bis zur Sturm-Schranke nach Delta^h)."""
    import math as _m
    if len(monome) > 40: return {"fehler": "höchstens 40 Monome"}
    infos = []
    for s in monome:
        mon = QF.parse_monom(s); w, eta, lev = QF.meta(mon)
        if any(N % d for d in lev): return {"fehler": f"{s}: Argument teilt N nicht"}
        if eta:
            ok, why = QF.newman_ok(eta, N)
            if not ok: return {"fehler": f"{s}: {why}"}
        infos.append((mon, w, {d: (QF.eta_order(eta, N, d) if eta else Fr(0)) for d, _, _ in QF.cusp_classes(N)}))
    if len({i[1] for i in infos}) > 1: return {"fehler": "verschiedene Gewichte"}
    k = int(infos[0][1]); h = 0
    for d, _, width in QF.cusp_classes(N):
        mn = min(i[2][d] for i in infos)
        if mn < 0: h = max(h, _m.ceil(-mn / width))
    nB = int(_m.floor(QF.sturm_bound(k + 12 * h, N))) + 1
    lo = min(QF.series(i[0], nB + h + 2).off for i in infos)
    rows = []
    for mon, _, _ in infos:
        s = QF.series(mon, nB + h + 2)
        if h: s = s * QF.series([("Delta", None, 1, h)], nB + 2)
        rows.append([s.coeff(e) if e >= s.off else 0 for e in range(int(min(lo, 0)), nB)])
    ker = _kernel(rows)
    return {"gewicht": k, "delta_potenz": h, "sturm_koeffizienten": nB, "relationen": [[str(c) for c in v] for v in ker],
            "lesart": "sum_i v[i] * monome[i] = 0"}


def _kernel(rows):
    """Kern von v -> sum v_i rows[i] (exakt)."""
    n = len(rows); m = len(rows[0]) if rows else 0
    A = [[Fr(rows[i][j]) for i in range(n)] for j in range(m)]       # m x n
    piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]; pv = A[r][c]; A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]; out = []
    for f in free:
        v = [Fr(0)] * n; v[f] = Fr(1)
        for i, c in enumerate(piv): v[c] = -A[i][f]
        den = math.lcm(*[x.denominator for x in v]); out.append([x * den for x in v])
    return out


DOMAIN = ModularDomain()
