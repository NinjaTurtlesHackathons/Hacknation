"""Reproduktion aller Zertifikate eines Projekts mit einem Befehl: Selbsttest + erneute Prüfung jeder Aussage in state.json.
  python -m asd.recheck <domain>"""
import json, sys
from .domains.base import get_domain
from . import selftest

name = sys.argv[1]; D = get_domain(name); ok_self, _ = selftest.run(name)
s = json.load(open(f"projects/{name}/state.json")); bad = 0
for c in s["claims"]:
    ok, why, _ = D.check(c["pruefung"]); bad += not ok
    print(f"[{'OK ' if ok else 'FEHLER'}] {c['id']} ({c['level']}, {c['status']}): {D.describe(c['pruefung'])[:140]}")
print(f"Selbsttest: {'bestanden' if ok_self else 'NICHT bestanden'}; Aussagen erneut geprüft: {len(s['claims']) - bad}/{len(s['claims'])} bestehen")
sys.exit(0 if ok_self and bad == 0 else 1)
