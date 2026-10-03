"""Auswertung der Präregistrierung H6 und des Selbsttests per Code -> projects/bell/zusatz_claims.json (für asd.paper).
  python projects/bell/auswertung.py"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from asd import selftest
from asd.domains import bell as B

D = "projects/bell"
s = json.load(open(f"{D}/state.json"))
start = json.load(open(f"{D}/startfragen.json"))
anker = [q["frage"] for q in start[:3]]                          # CHSH, Kette, gekippte CHSH (laut prereg.md H6a)
benannt = {B.key(B.parse(n)) for n in ["chsh", "i3322", "kette:2", "kette:3", "kette:4", "kette:5", "kette:6"]}


def ist_benannt(p):
    u = p.get("ungleichung", p.get("vorlage"))
    if isinstance(u, str) and u.split(":")[0] in ("chsh", "i3322", "kette", "chained", "gekippt", "tilted"): return True
    try: return B.key(B.parse(u)) in benannt
    except Exception: return False


claims_anker = [c for c in s["claims"] if c["frage"] in anker and c["status"] == "bestätigt"]
anker_bearbeitet = [f for f in anker if any(r for r in s["runden"] if next(q for q in s["fragen"] if q["id"] == r["frage"])["frage"] == f)]
claims_neu = [c for c in s["claims"] if c["status"] == "bestätigt" and not ist_benannt(c["pruefung"])]
ok, rows = selftest.run("bell", log=lambda m: None)

out = [
    {"claim_id": "C-selbsttest", "level": "computed_rigorous", "status": "bestätigt",
     "text": f"Selbsttest des Bell-Prüfers vor dem Lauf: {sum(r['korrekt'] for r in rows)}/{len(rows)} Fälle korrekt "
             f"({sum(r['erwartet'] for r in rows)} wahre, {len(rows) - sum(r['erwartet'] for r in rows)} falsche Aussagen bzw. Regelverletzungen); "
             f"Ergebnis: {'bestanden' if ok else 'nicht bestanden'}. Wahre Anker: CHSH (klassische Schranke 2, Quantenwert 2.828427125), Kette mit 4 Einstellungen "
             f"(klassische Schranke 6), I3322 (klassische Schranke 0, obere Schranke 0.2509 mit NPA-Stufe 2+AAB), gekippte CHSH mit Formel sqrt(8+2*p**2)."},
    {"claim_id": "C-H6a", "level": "observed", "status": "bestätigt",
     "text": f"Präregistrierte Hypothese H6a (mindestens 2 von 3 Anker-Fragen zweiseitig bestätigt): nicht erfüllt. Der Integrator wählte "
             f"{len(anker_bearbeitet)} der 3 Anker-Fragen; bestätigte Aussagen zu Anker-Fragen: {len(claims_anker)}."},
    {"claim_id": "C-H6b", "level": "observed", "status": "bestätigt",
     "text": f"Präregistrierte Hypothese H6b (mindestens eine zertifizierte Aussage zu einer Ungleichung außerhalb der benannten Familien): "
             f"{'erfüllt' if claims_neu else 'nicht erfüllt'}; {len(claims_neu)} bestätigte Aussagen betreffen die doppelt gekippte CHSH-Familie "
             f"oder andere nicht benannte Ungleichungen. Neuheit gegenüber der Literatur wird nicht behauptet."},
]
# Abgeleitete Aussagen: nur Vergleiche von Zahlen, die der Prüfer selbst ausgegeben hat (Grund-Texte der Claims)
import re
from fractions import Fraction as Fr
C = {c["id"]: c for c in s["claims"]}
def zahl(muster, text): m = re.search(muster, text); return Fr(m.group(1)) if m else None
if "bell-R5" in C and "bell-R6" in C and C["bell-R5"]["pruefung"]["ungleichung"] == C["bell-R6"]["pruefung"]["ungleichung"]:
    N = zahl(r"erreicht >= ([0-9.]+)", C["bell-R5"]["grund"]); U = zahl(r"<= Q <= ([0-9.]+)", C["bell-R6"]["grund"])
    if N is not None and U is not None and U < N:
        out.append({"claim_id": "C-kombi1", "level": "computed_rigorous", "status": "bestätigt",
                    "text": f"Folgerung aus C-bell-R5 und C-bell-R6 (gleiche Ungleichung, a = b = [131/200, 0]): Q <= {float(U):.15g} (NPA-Stufe 2, Dualzertifikat) "
                            f"und der Optimalwert der NPA-Stufe 1+AB ist >= {float(N):.12g} (rationale zulässige Momentmatrix). Da {float(U):.15g} < {float(N):.12g}, "
                            f"ist die Stufe 1+AB an diesem Punkt streng nicht scharf: ihr Optimalwert übertrifft Q um mindestens {float(N - U - Fr(1, 10**11)):.3g} "
                            f"(Rundung der ausgegebenen Werte berücksichtigt)."})
pts = []
for c in s["claims"]:
    for pr, gr in [(c["pruefung"], c["grund"])] + [(r["pruefung"], r["grund"]) for r in c["red_team"]]:
        if pr.get("typ") == "luecke_npa" and pr.get("stufe") == "1+AB":
            g = zahl(r"Lücke >= (-?[0-9.e+-]+)", gr); p = Fr(str(pr["ungleichung"]["korrelator"]["a"][0]))
            if g is not None and (p, g) not in pts: pts.append((p, g))
if len(pts) >= 3:
    pts.sort()
    klein = [(p, g) for p, g in pts if abs(g) < Fr(1, 10**7)]; gross = [(p, g) for p, g in pts if abs(g) >= Fr(1, 10**7)]
    mono = all(g1 < g2 for (_, g1), (_, g2) in zip(gross, gross[1:])) and (not klein or not gross or max(p for p, _ in klein) < min(p for p, _ in gross))
    beschr = (f"Bis p = {float(max(p for p, _ in klein)):g} liegt die Schranke betragsmäßig unter 1e-7 (Genauigkeit der SDP-Löser), ab p = "
              f"{float(min(p for p, _ in gross)):g} ist sie positiv und wächst über die untersuchten Punkte monoton. Eine über eine feste Toleranz "
              f"(z. B. 1e-6) definierte Schwelle hängt daher von dieser Toleranz ab." if mono and klein and gross else "Kein monotones Muster.")
    tab = "; ".join(f"p = {float(p):g}: {float(g):.3e}" for p, g in pts)
    out.append({"claim_id": "C-kombi2", "level": "computed_rigorous", "status": "bestätigt",
                "text": f"Untere Schranken des Prüfers für (Optimalwert NPA 1+AB) minus (beste exakt zertifizierte Strategie), doppelt gekippte CHSH, "
                        f"aus allen luecke_npa-Prüfungen inkl. Red-Team: {tab}. {beschr}"})
if len(claims_anker) >= 2: out[1]["text"] = out[1]["text"].replace("nicht erfüllt", "erfüllt", 1)
json.dump(out, open(f"{D}/zusatz_claims.json", "w"), ensure_ascii=False, indent=1)
for c in out: print(c["claim_id"], c["text"])
