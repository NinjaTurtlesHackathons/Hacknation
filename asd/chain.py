"""Hash-Kette über die Protokolldateien eines Laufs (manipulationssicher ab dem Zeitpunkt der Versiegelung).

  python -m asd.chain seal <run-ordner>     # schreibt <run>/CHAIN.json
  python -m asd.chain verify <run-ordner>   # Exit 1, wenn eine Datei oder Zeile verändert wurde

Jede Zeile von record.jsonl und jeder Session-Export geht in die Kette ein: h_i = sha256(h_{i-1} || Inhalt_i).
Ehrlicher Hinweis: Eine nachträglich angelegte Kette schützt nur vor Änderungen NACH dem Versiegeln."""
import hashlib, json, os, sys, time

DATEIEN = ("record.jsonl", "decisions.md", "prereg.md", "state.json")


def _glieder(run):
    teile = []
    p = os.path.join(run, "record.jsonl")
    if os.path.exists(p):
        teile += [("record.jsonl#%d" % i, l.encode()) for i, l in enumerate(open(p, encoding="utf-8").read().splitlines())]
    for f in DATEIEN[1:]:
        q = os.path.join(run, f)
        if os.path.exists(q): teile.append((f, open(q, "rb").read()))
    sd = os.path.join(run, "sessions")
    if os.path.isdir(sd):
        teile += [("sessions/" + f, open(os.path.join(sd, f), "rb").read()) for f in sorted(os.listdir(sd))]
    return teile


def kette(run):
    h = "0" * 64; out = []
    for name, data in _glieder(run):
        h = hashlib.sha256(h.encode() + data).hexdigest(); out.append([name, h])
    return out


def seal(run):
    k = kette(run)
    json.dump({"versiegelt": time.strftime("%Y-%m-%dT%H:%M:%S"), "glieder": len(k), "kopf": k[-1][1] if k else None, "kette": k},
              open(os.path.join(run, "CHAIN.json"), "w"), indent=1)
    return k[-1][1] if k else None


def verify(run):
    """-> (ok, grund). Ohne CHAIN.json: (None, 'keine Kette')."""
    p = os.path.join(run, "CHAIN.json")
    if not os.path.exists(p): return None, "no hash chain present"
    alt = json.load(open(p)); neu = kette(run)
    if len(neu) != alt["glieder"]: return False, f"Anzahl der Glieder geändert ({alt['glieder']} -> {len(neu)})"
    for (n1, h1), (n2, h2) in zip(alt["kette"], neu):
        if h1 != h2: return False, f"Kette bricht bei {n2}"
    return True, f"hash chain intact ({len(neu)} links, head {neu[-1][1][:12]})"


if __name__ == "__main__":
    cmd, run = sys.argv[1], sys.argv[2]
    if cmd == "seal": print("versiegelt, Kopf", seal(run))
    else:
        ok, g = verify(run); print(g); sys.exit(0 if ok else 1)
