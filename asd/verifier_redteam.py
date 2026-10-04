"""Red-Team gegen den PRÜFER (vor dem Labor, Phase 3). Ein zweites Modell baut Fallen: Prüfungen, die FALSCH sein müssten, die ein
schwacher Prüfer aber durchlassen könnte (Toleranz-Tricks, Grenzfälle, Regelverletzungen, kaputte Eingaben, entartete Fälle).

Ergebnis je Falle: absturz (Prüfer wirft eine Exception -> sicherer Prüferfehler) | verdaechtig_bestanden (muss ein Mensch/Claude
beurteilen) | korrekt_abgelehnt. Beurteilung:  python -m asd.verifier_redteam <domain> --urteil T3=falsch T5=wahr
"falsch" heißt: die Aussage ist wirklich falsch, der Prüfer hat sie zu Unrecht bestanden -> sie wird als neuer Selbsttest-Fall
(erwartet False) in projects/<domain>/selftest_extra.json eingetragen; der Selbsttest schlägt dann fehl, bis der Prüfer repariert ist.
"""
import argparse, json, os, time
from .domains.base import get_domain
from .llm import ask_json


def run(domain, n=10, salt=""):
    D = get_domain(domain); d = f"projects/{domain}"; os.makedirs(d, exist_ok=True)
    known = json.dumps([p for p, _ in D.selftest()], ensure_ascii=False)[:4000]
    r = ask_json(f"Domain: {D.kontext}\n\n{D.primitive_doc}\n\n{D.claim_doc}\n\nExisting self-test cases: {known}\n\nYou attack the VERIFIER, not the science. "
                 f"Construct {n} checks (same JSON types as above) that are FALSE (or malformed) but that a weak verifier might wrongly accept: "
                 "tolerance tricks (extra fields like 'toleranz'), values just beyond known limits, boundary cases, rule violations (rates out of range, "
                 "inconsistent parameters), degenerate inputs, wrong types, missing fields. For each say why it must be rejected. "
                 'JSON: {"fallen": [{"pruefung": {...}, "warum_falsch": "..."}]}', "You are a security tester for scientific verifiers. Answer with valid JSON only.",
                 salt=f"verifier-redteam-{domain}-{salt}")
    out = []
    for j, f in enumerate(r.get("fallen", [])[:n], 1):
        p = f.get("pruefung")
        if not isinstance(p, dict): continue
        try:
            ok, why, _ = D.check(p); erg = "verdaechtig_bestanden" if ok else "korrekt_abgelehnt"
        except Exception as e:
            ok, why, erg = False, f"{type(e).__name__}: {e}"[:200], "absturz"
        out.append({"id": f"T{j}", "pruefung": p, "warum_falsch": f.get("warum_falsch", ""), "ergebnis": erg, "grund": str(why)[:200], "urteil": None})
    rep = {"domain": domain, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "fallen": out}
    json.dump(rep, open(f"{d}/verifier_redteam.json", "w"), ensure_ascii=False, indent=1)
    return rep


def urteil(domain, urteile):
    d = f"projects/{domain}"; rep = json.load(open(f"{d}/verifier_redteam.json")); extra_p = f"{d}/selftest_extra.json"
    extra = json.load(open(extra_p)) if os.path.exists(extra_p) else []
    for u in urteile:
        tid, val = u.split("="); f = next(x for x in rep["fallen"] if x["id"] == tid); f["urteil"] = val
        if val == "falsch" and f["ergebnis"] == "verdaechtig_bestanden":
            extra.append({"pruefung": f["pruefung"], "erwartet": False, "quelle": f"verifier_redteam {tid}", "warum": f["warum_falsch"]})
    json.dump(rep, open(f"{d}/verifier_redteam.json", "w"), ensure_ascii=False, indent=1)
    json.dump(extra, open(extra_p, "w"), ensure_ascii=False, indent=1)


def offen(rep):
    """Was blockiert Phase 3: Abstürze und unbeurteilte verdächtige Fälle."""
    return [f for f in rep["fallen"] if f["ergebnis"] == "absturz" or (f["ergebnis"] == "verdaechtig_bestanden" and not f.get("urteil"))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("domain"); ap.add_argument("--urteil", nargs="*"); ap.add_argument("-n", type=int, default=10)
    a = ap.parse_args()
    if a.urteil: urteil(a.domain, a.urteil); print("Urteile gespeichert")
    else:
        rep = run(a.domain, a.n)
        for f in rep["fallen"]: print(f"[{f['ergebnis']:22}] {f['id']} {json.dumps(f['pruefung'], ensure_ascii=False)[:110]} | {f['grund'][:90]}")
        print(f"blockierend für Phase 3: {len(offen(rep))}")
