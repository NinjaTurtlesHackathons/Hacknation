"""Eigenständige Zertifikate: für jeden Claim mit level computed_rigorous, dessen Zertifikat ohne Computeralgebra nachrechenbar ist
(erreichbar / erreichbar_liste: exakte rationale Raten), nach projects/<projekt>/certificates/<claim_id>/:
  certificate.json  alle exakten Daten (Zustände, Kanten mit rationalen Raten, Potential-Faktoren, Zweig, Produktkanten, e^Delta, eta_max)
  check.py          eigenständig (nur Standardbibliothek, importiert nichts aus asd/), druckt PASS/FAIL
  README.txt        die Aussage in einem Satz
Symbolische Beweise (untere_schranke, schranke_familie) brauchen Computeralgebra und werden im Bericht als "nicht eigenständig" geführt.

  python -m asd.certificates <domain> [--projekt P] [--verfaelschen]   -> certificates_report.md"""
import argparse, json, os, shutil, subprocess, sys
from fractions import Fraction

from .domains.base import get_domain
from .domains import proofreading as P
from .domains.proofreading_domain import _spec, _full

VORLAGE = os.path.join(os.path.dirname(__file__), "templates", "check_erreichbar.py")


def _fall(f):
    spec = _spec(f["topologie"]); r = P.rationalize(_full(spec, f["params"]))
    states, edges = P.build_rates(spec, r, None, Fraction(100), num=Fraction)
    disk = {k["id"]: bool(k.get("diskriminierend")) for k in spec["kanten"]}
    s = lambda x: f"{x.numerator}/{x.denominator}"
    return {"topologie": f["topologie"] if isinstance(f["topologie"], str) else "eigene Spec", "zustaende": states, "gebunden": list(spec["gebunden"]),
            "e_delta": "100", "eta_max": str(f["eta_max"]), "v_min": str(f["v_min"]) if f.get("v_min") is not None else None,
            "kanten": [{"id": e["id"], "u": e["u"], "v": e["v"], "f": s(e["f"]), "b": s(e["b"]), "a": s(e["a"]), "zweig": e["zweig"],
                        "produkt": e["produkt"], "disk": disk[e["id"]]} for e in edges]}


def exportieren(domain, projekt):
    D = get_domain(domain); st = json.load(open(f"projects/{projekt}/state.json")); out = f"projects/{projekt}/certificates"
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out); zeilen = []
    for c in st["claims"]:
        if c.get("level") != "computed_rigorous" or c.get("status") != "bestätigt": continue
        p = c["pruefung"]; t = p.get("typ")
        if t not in ("erreichbar", "erreichbar_liste"):
            zeilen.append((c["id"], t, "nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck)", None)); continue
        if t == "erreichbar" and p.get("sigma_max") is not None:
            zeilen.append((c["id"], t, "nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb)", None)); continue
        faelle = p["faelle"] if t == "erreichbar_liste" else [p]
        d = f"{out}/{c['id']}"; os.makedirs(d)
        json.dump({"claim_id": c["id"], "aussage": D.describe(p, lang="en") if "lang" in D.describe.__code__.co_varnames else c["text"], "typ": t,
                   "faelle": [_fall(f) for f in faelle]}, open(f"{d}/certificate.json", "w"), indent=1, ensure_ascii=False)
        shutil.copy(VORLAGE, f"{d}/check.py")
        open(f"{d}/README.txt", "w").write(f"{c['id']}: {D.describe(p, lang='en')}\nRun: python3 check.py   (standard library only; prints PASS or FAIL)\n")
        zeilen.append((c["id"], t, "exportiert", d))
    return zeilen


def ausfuehren(d):
    r = subprocess.run([sys.executable, "-I", "check.py"], cwd=d, capture_output=True, text=True, timeout=600)   # -I: isoliert, kein asd im Pfad
    return (r.stdout.strip() or r.stderr.strip()[-200:]).splitlines()[-1] if (r.stdout or r.stderr) else "FAIL: keine Ausgabe"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("domain"); ap.add_argument("--projekt", default=""); ap.add_argument("--verfaelschen", action="store_true")
    a = ap.parse_args(); pj = a.projekt or a.domain
    zeilen = exportieren(a.domain, pj); L = [f"# Certificates report ({pj})", "", "| Claim | Type | Export | check.py (fresh process, `python -I`) |", "|---|---|---|---|"]
    ergebnisse = []
    for cid, t, status, d in zeilen:
        res = ausfuehren(d) if d else "–"; ergebnisse.append(res); L.append(f"| {cid} | {t} | {status} | {res[:120]} |")
    if a.verfaelschen:                                               # Gegenprobe: ein verändertes Zertifikat muss FAIL liefern
        d = next(d for _, _, _, d in zeilen if d); tmp = d + "_verfaelscht"; shutil.copytree(d, tmp)
        cert = json.load(open(f"{tmp}/certificate.json")); k = cert["faelle"][0]["kanten"][0]; f = Fraction(k["f"]) * Fraction(1001, 1000); k["f"] = f"{f.numerator}/{f.denominator}"
        json.dump(cert, open(f"{tmp}/certificate.json", "w"), indent=1); res = ausfuehren(tmp); shutil.rmtree(tmp)
        L += ["", f"Tamper test (one rate of {os.path.basename(d)} multiplied by 1.001): **{res[:160]}**"]
        print("verfälscht:", res[:160])
    n_ex = sum(1 for z in zeilen if z[3]); n_ok = sum(1 for r in ergebnisse if r == "PASS")
    L += ["", f"Exported {n_ex}, PASS {n_ok}, not standalone {len(zeilen) - n_ex}."]
    open(f"projects/{pj}/certificates_report.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[-3:]))
    sys.exit(0 if n_ok == n_ex else 1)


if __name__ == "__main__":
    main()
