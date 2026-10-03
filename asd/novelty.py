"""Phase 6, Neuheitsprüfung: Für jede geprüfte Aussage die ähnlichsten Befunde der Recherche (Wortüberlappung) auflisten,
damit Mensch bzw. Claude entscheidet: Reproduktion oder neu. Schreibt projects/<domain>/neuheit.md.
  python -m asd.novelty <domain>"""
import json, re, sys, time
from .domains.base import get_domain

STOP = set("der die das und oder für mit von bei ist sind ein eine einer the of and for with in on to a an is are by at as that this gilt".split())


def toks(t): return {w for w in re.findall(r"[a-zäöüß0-9]+", t.lower()) if len(w) > 2 and w not in STOP}


name = sys.argv[1]; D = get_domain(name); s = json.load(open(f"projects/{name}/state.json"))
kb = json.load(open(f"research/kb/{name}/kb.json")); facts = [f for f in kb["befunde"] if f.get("verifiziert")]
L = [f"# Neuheitsprüfung ({time.strftime('%Y-%m-%d')}, Recherche: {kb['stats'].get('abgerufen')} Quellen, {len(facts)} geprüfte Befunde)", "",
     "Label erst NACH Durchsicht setzen: Reproduktion | neu-numerisch | neu-zertifiziert. Ohne passenden Treffer: „neu laut Recherche vom <Datum>“.", "",
     "| Aussage (kanonisch) | Stufe | ähnlichste Befunde der Recherche | Label (auszufüllen) |", "|---|---|---|---|"]
for c in s["claims"]:
    a = D.describe(c["pruefung"]); ta = toks(a + " " + c.get("frage", ""))
    near = sorted(facts, key=lambda f: -len(ta & toks(f["aussage"] + " " + f["zitat"])))[:3]
    hits = "<br>".join(f"{f['quelle']}: {f['aussage'][:110]} ({len(ta & toks(f['aussage'] + ' ' + f['zitat']))} gem. Wörter)" for f in near)
    L.append(f"| [{c['id']}] {a.replace('|', '/')} | {c['level']} | {hits} | |")
open(f"projects/{name}/neuheit.md", "w").write("\n".join(L) + "\n"); print("\n".join(L[:8]))
