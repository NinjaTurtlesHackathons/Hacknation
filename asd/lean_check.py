"""Lean-Stufe für diskrete Aussagen. Die Lean-AUSSAGE wird per Vorlage aus dem Claim-JSON erzeugt (kein Agent schreibt sie); der Agent liefert nur
die Taktik. Kompiliert mit lokalem `lean` (Lean 4 Core, ohne Mathlib) im Temp-Ordner mit Zeitlimit; `#print axioms` wird mitprotokolliert.

Claim-Typ "klassische_schranke" (Bell-Ungleichung in Korrelator-Form, rationale Koeffizienten c[x][y]):
  L = max über deterministische Strategien a_x, b_y in {+1, -1} von sum_{x,y} c[x][y] a_x b_y.
  Claim {"typ": "klassische_schranke", "koeffizienten": [["1","1"],["1","-1"]], "schranke": "2"} behauptet: L = schranke
  (alle Strategien <= schranke UND eine Strategie erreicht sie). CHSH: L = 2.

  python -m asd.lean_check '<claim-json>' [--taktik decide]
Ohne Lean: Ergebnis "lean_nicht_verfuegbar", der Claim bleibt computed_rigorous (kein Fehlschlag)."""
import json, math, os, re, shutil, subprocess, sys, tempfile
from fractions import Fraction

ERLAUBTE_TAKTIK = re.compile(r"^(decide|simp|omega|rfl|by_cases\b[^;]*|decide\s*<;>\s*\w+)$")
ERLAUBTE_AXIOME = {"propext", "Quot.sound", "Classical.choice"}


def lean_bin():
    return shutil.which("lean") or (os.path.expanduser("~/.elan/bin/lean") if os.path.exists(os.path.expanduser("~/.elan/bin/lean")) else None)


def aussage_klassische_schranke(claim):
    """Lean-Quelltext (ohne Beweis-Taktik) aus dem Claim; Koeffizienten auf ganze Zahlen skaliert (Hauptnenner)."""
    C = [[Fraction(str(v)) for v in row] for row in claim["koeffizienten"]]; L = Fraction(str(claim["schranke"]))
    den = 1
    for v in [v for row in C for v in row] + [L]: den = den * v.denominator // math.gcd(den, v.denominator)
    Ci = [[int(v * den) for v in row] for row in C]; Li = int(L * den) if (L * den).denominator == 1 else None
    if Li is None: raise ValueError("Schranke nicht darstellbar")
    m, n = len(Ci), len(Ci[0]); a = [f"a{x}" for x in range(m)]; b = [f"b{y}" for y in range(n)]
    summe = " + ".join(f"({Ci[x][y]}) * s {a[x]} * s {b[y]}" for x in range(m) for y in range(n))
    quant = " ".join(a + b)
    return (f"def s (b : Bool) : Int := if b then 1 else -1\n\n"
            f"/-- generated from the claim: every deterministic strategy gives at most {L} (scaled by {den}). -/\n"
            f"theorem obere_schranke : ∀ {quant} : Bool, {summe} ≤ {Li} := by TAKTIK\n\n"
            f"/-- generated from the claim: some deterministic strategy attains {L}. -/\n"
            f"theorem erreicht : ∃ {quant} : Bool, {summe} = {Li} := by TAKTIK\n\n"
            f"#print axioms obere_schranke\n#print axioms erreicht\n")


def pruefe(claim, taktik="decide", timeout=180):
    """-> dict(bestanden, level, grund, axiome, lean_ausgabe). Lean fehlt -> bestanden None, level bleibt computed_rigorous."""
    if claim.get("typ") != "klassische_schranke": return {"bestanden": False, "grund": f"Claim-Typ {claim.get('typ')} hat keine Lean-Vorlage"}
    if not ERLAUBTE_TAKTIK.match(taktik.strip()) or re.search(r"sorry|admit|native_decide|axiom", taktik):
        return {"bestanden": False, "grund": f"Taktik nicht erlaubt: {taktik!r}"}
    lean = lean_bin()
    if not lean: return {"bestanden": None, "level": "computed_rigorous", "grund": "lean_nicht_verfuegbar: Claim bleibt computed_rigorous"}
    src = aussage_klassische_schranke(claim).replace("TAKTIK", taktik.strip())
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "Claim.lean"), "w").write(src)
        try: r = subprocess.run([lean, "Claim.lean"], cwd=d, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired: return {"bestanden": False, "grund": f"Lean-Zeitlimit {timeout} s", "lean_quelle": src}
    out = (r.stdout + r.stderr).strip()
    axiome = sorted(set(re.findall(r"\b([A-Za-z_.]+)\b", " ".join(re.findall(r"depends on axioms: \[([^\]]*)\]", out)))))
    fremd = [x for x in axiome if x not in ERLAUBTE_AXIOME]
    ok = r.returncode == 0 and "error" not in out.lower() and not fremd
    return {"bestanden": ok, "level": "proved_lean" if ok else "hypothesis", "axiome": axiome,
            "grund": ("Lean 4 bestätigt beide Sätze (obere Schranke, Erreichbarkeit)" if ok else f"Lean lehnt ab (exit {r.returncode}){'; fremde Axiome ' + str(fremd) if fremd else ''}"),
            "lean_ausgabe": out[-1500:], "lean_quelle": src}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("claim"); ap.add_argument("--taktik", default="decide"); a = ap.parse_args()
    res = pruefe(json.loads(a.claim), a.taktik); res.pop("lean_quelle", None); print(json.dumps(res, ensure_ascii=False, indent=1))
