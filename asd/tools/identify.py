"""Formel-Finder für zertifizierte Zahlen (Experiment-Primitive für Domänen mit zertifizierten Einschlüssen).

Eingabe: Punkte [(p, lo, hi)] mit zertifizierten Intervallen lo <= Q(p) <= hi (rational oder als Dezimalstring).
Suche (mpmath, hohe Präzision): ganzzahlige Relation P(Q, p) = sum c_ij Q^i p^j = 0 mit kleinem Grad und kleinen Koeffizienten, gefittet NUR
an den Fit-Punkten (Nullraum per SVD, dann Rationalisierung). Prüfung (exakt, Fractions): an mindestens zwei ZURÜCKGEHALTENEN Punkten muss
P(lo, p) und P(hi, p) verschiedene Vorzeichen haben -> eine Wurzel des Kandidaten liegt im zertifizierten Intervall. Kandidaten mit mehr freien
Koeffizienten als Fit-Punkten werden abgelehnt. Ergebnis höchstens "computed_rigorous (an k Punkten)", nie ein allgemeiner Satz."""
from fractions import Fraction
import itertools, json
import mpmath as mp


def _monome(grad_q, grad_p):
    return [(i, j) for i in range(grad_q + 1) for j in range(grad_p + 1) if (i, j) != (0, 0) or True]


def _wert(c, mon, Q, p):
    return sum(ci * Q ** i * p ** j for ci, (i, j) in zip(c, mon))


def fit(fitpunkte, grad_q=2, grad_p=1, max_koeff=50, dps=50):
    """-> (koeffizienten als ints, monome) oder None. Nullraumvektor der Matrix [Q^i p^j] an den Fit-Punkten, auf kleine ganze Zahlen gebracht."""
    mp.mp.dps = dps
    mon = _monome(grad_q, grad_p)
    if len(mon) - 1 > len(fitpunkte): return None                      # mehr freie Koeffizienten (bis auf Skalierung) als Stützstellen
    A = mp.matrix([[mp.mpf(p) ** j * ((mp.mpf(lo) + mp.mpf(hi)) / 2) ** i for (i, j) in mon] for p, lo, hi in fitpunkte])
    U, S, V = mp.svd_r(A, full_matrices=True)
    v = [V[V.rows - 1, k] for k in range(V.cols)]                       # Richtung zum kleinsten (ggf. impliziten) Singulärwert
    if A.rows >= A.cols and S[len(S) - 1] > mp.mpf(10) ** (-dps // 3) * max(S): return None   # überbestimmt: echte Relation nötig
    big = max(abs(x) for x in v); v = [x / big for x in v]
    for skala in range(1, max_koeff + 1):                                # kleinste ganzzahlige Skalierung
        c = [int(mp.nint(x * skala)) for x in v]
        if any(c) and all(abs(x * skala - ci) < mp.mpf(10) ** (-dps // 4) for x, ci in zip(v, c)) and max(abs(ci) for ci in c) <= max_koeff:
            return c, mon
    return None


def pruefe(kandidat, holdout):
    """Exakte Prüfung an zurückgehaltenen Punkten: Vorzeichenwechsel von P(., p) über [lo, hi] (Fractions)."""
    c, mon = kandidat; res = []
    for p, lo, hi in holdout:
        p, lo, hi = Fraction(str(p)), Fraction(str(lo)), Fraction(str(hi))
        a, b = _wert(c, mon, lo, p), _wert(c, mon, hi, p)
        res.append({"p": str(p), "P(lo)": str(a), "P(hi)": str(b), "wurzel_im_intervall": (a == 0 or b == 0 or (a > 0) != (b > 0))})
    return all(r["wurzel_im_intervall"] for r in res), res


def identify(punkte, n_holdout=2, grade=((1, 1), (2, 1), (2, 2), (3, 1), (4, 0)), max_koeff=50):
    """Sucht über kleine Grade; Fit an allen außer den letzten n_holdout Punkten, Prüfung an diesen. Erster bestätigter Kandidat gewinnt."""
    if len(punkte) < n_holdout + 2: return {"bestanden": False, "grund": "zu wenige Punkte für Fit + mindestens zwei zurückgehaltene"}
    fitp, hold = punkte[:-n_holdout], punkte[-n_holdout:]
    versuche = []
    for gq, gp in grade:
        k = fit(fitp, gq, gp, max_koeff)
        if not k: versuche.append({"grad": [gq, gp], "ergebnis": "kein Kandidat (oder zu viele freie Koeffizienten)"}); continue
        ok, det = pruefe(k, hold)
        poly = " + ".join(f"{ci}*Q^{i}*p^{j}" for ci, (i, j) in zip(*k) if ci)
        versuche.append({"grad": [gq, gp], "kandidat": poly, "holdout_bestanden": ok, "details": det})
        if ok:
            return {"bestanden": True, "level": f"computed_rigorous (an {len(hold)} zurückgehaltenen Punkten)", "relation": poly + " = 0",
                    "fit_punkte": len(fitp), "holdout_punkte": len(hold), "versuche": versuche,
                    "hinweis": "nur an den geprüften Punkten zertifiziert; kein allgemeiner Satz"}
    return {"bestanden": False, "grund": "kein Kandidat bestand die zurückgehaltenen Punkte", "versuche": versuche}


if __name__ == "__main__":
    import sys
    print(json.dumps(identify(json.load(open(sys.argv[1]))), indent=1, ensure_ascii=False))
