"""Pflicht-Selbsttest des Prüfers einer Domäne: bekannte wahre Aussagen müssen bestehen, bekannte falsche durchfallen.
Ohne bestandenen Selbsttest verweigert die Labor-Schleife den Start.  python -m asd.selftest <domain>"""
import json, sys, time
from .domains.base import get_domain


def run(name, log=print):
    d = get_domain(name); rows = []
    for p, want in d.selftest():
        t0 = time.time(); ok, why, _ = d.check(p); good = bool(ok) == want
        rows.append({"pruefung": p, "erwartet": want, "ergebnis": bool(ok), "korrekt": good, "grund": why[:200], "sek": round(time.time() - t0, 1)})
        log(f"[{'OK ' if good else 'FEHLER'}] erwartet {want!s:5} bekommen {bool(ok)!s:5} {json.dumps(p, ensure_ascii=False)[:90]}")
    n_true = sum(r["erwartet"] for r in rows); n_false = len(rows) - n_true; passed = all(r["korrekt"] for r in rows)
    if n_true == 0 or n_false == 0: passed = False; log("Selbsttest braucht mindestens eine wahre UND eine falsche Aussage.")
    log(f"Selbsttest {name}: {'BESTANDEN' if passed else 'NICHT BESTANDEN'} ({sum(r['korrekt'] for r in rows)}/{len(rows)})")
    return passed, rows


if __name__ == "__main__":
    ok, _ = run(sys.argv[1]); sys.exit(0 if ok else 1)
