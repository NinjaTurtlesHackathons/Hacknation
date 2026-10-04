"""Phasen-Gates (Workflow Phase 0-8) im Code. Labor und Paper prüfen sie und verweigern den Start, wenn eine Pflichtphase fehlt.
Damit bekommt jede Gruppe dieselbe Mindestqualität, egal wie gut der Prompt ist.

  python -m asd.phases <projekt> [--domain <domain>]          # Status aller Phasen
Ausnahme nur bewusst: --ohne-gates in lab_loop/paper, wird in decisions.md als Abweichung protokolliert.
"""
import json, os, re, subprocess, sys

SCHWELLEN = {"abgerufen": 1000, "gesichtet": 100, "verifiziert": 60, "klassiker": 8}


def _git_committed(path):
    r = subprocess.run(["git", "log", "-1", "--format=%h %ci", "--", path], capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", path], capture_output=True, text=True).stdout.strip()
    return (r.stdout.strip() or None), bool(dirty)


def check(projekt, domain=None):
    """Gibt [(phase, bestanden, grund)] zurück."""
    from .domains.base import get_domain
    domain = domain or projekt; d = f"projects/{projekt}"; out = []
    try: D = get_domain(domain); out.append((0, True, f"Domäne {domain} geladen"))
    except Exception as e: return [(0, False, f"Domäne {domain} nicht ladbar: {type(e).__name__}")]
    kb = f"research/kb/{domain}/kb.json"
    if os.path.exists(kb):
        st = json.load(open(kb))["stats"]
        fehl = [f"{k} {st.get(k, 0)} < {v}" for k, v in SCHWELLEN.items() if k != "klassiker" and st.get(k, 0) < v]
        if st.get("klassiker_gesamt", 0) < SCHWELLEN["klassiker"]: fehl.append(f"Klassiker-Suchen {st.get('klassiker_gesamt', 0)} < {SCHWELLEN['klassiker']}")
        if not os.path.exists(f"research/kb/{domain}/known_results.md"): fehl.append("known_results.md fehlt")
        out.append((1, not fehl, "; ".join(fehl) or f"{st['abgerufen']} Quellen, {st['verifiziert']} geprüfte Zitate, {st.get('klassiker_gesamt')} Klassiker"))
    else: out.append((1, False, "keine Recherche (research/kb/<domain>/kb.json fehlt)"))
    lk = f"{d}/lueckenkarte.md"
    if os.path.exists(lk):
        rows = [l for l in open(lk) if re.match(r"^\|\s*L\d", l)]
        pruefbar = [l for l in rows if "Prüfer fehlt" not in l and "verifier missing" not in l.lower()]
        out.append((2, len(rows) >= 5 and len(pruefbar) >= 3, f"{len(rows)} Lücken, {len(pruefbar)} prüfbar (Soll: >= 5 und >= 3)"))
    else: out.append((2, False, "lueckenkarte.md fehlt"))
    from . import selftest
    ok, rows = selftest.run(domain, log=lambda m: None)
    rt = f"{d}/verifier_redteam.json"; rt_ok, rt_txt = False, "Prüfer-Red-Team fehlt (python -m asd.verifier_redteam <domain>)"
    if os.path.exists(rt):
        from .verifier_redteam import offen
        o = offen(json.load(open(rt))); rt_ok = not o; rt_txt = f"Prüfer-Red-Team: {len(o)} blockierend"
    out.append((3, ok and rt_ok, f"Selbsttest {'bestanden' if ok else 'NICHT bestanden'} ({sum(r['korrekt'] for r in rows)}/{len(rows)}); {rt_txt}"))
    pre = [f for f in (f"{d}/prereg.md", "prereg.md") if os.path.exists(f)]
    pc = [(f,) + _git_committed(f) for f in pre]
    ok4 = any(h and not dirty for f, h, dirty in pc)
    out.append((4, ok4, "; ".join(f"{f}: {'committet ' + h if h else 'nicht committet'}{' (uncommittete Änderungen)' if dirty else ''}" for f, h, dirty in pc) or "keine prereg.md"))
    sp = f"{d}/state.json"
    if os.path.exists(sp):
        s = json.load(open(sp)); lk_q = [q for q in s["fragen"] if q.get("quelle") == "lueckenkarte"]
        offen_q = [q["id"] for q in lk_q if q["status"] == "offen"]
        n_ok = sum(c["status"] == "bestätigt" for c in s["claims"])
        out.append((5, n_ok >= 1 and not offen_q, f"{n_ok} bestätigte Aussagen, {len(s['widerlegt'])} negative; offene Lückenfragen: {offen_q or 'keine'}"))
        ohne = [c["id"] for c in s["claims"] if c["status"] == "bestätigt" and not (c.get("neuheit") or {}).get("status")]
        out.append((6, n_ok >= 1 and not ohne, f"Neuheitsstatus fehlt bei: {ohne}" if ohne else "alle bestätigten Aussagen haben einen Neuheitsstatus"))
    else: out += [(5, False, "kein Laborlauf"), (6, False, "kein Laborlauf")]
    pp = f"{d}/pruefprotokoll.json"
    if os.path.exists(pp) and os.path.exists(f"{d}/paper.pdf"):
        n = len(json.load(open(pp)).get("verbleibende_verstoesse", []))
        out.append((7, n == 0, f"paper.pdf vorhanden, verbleibende Verstöße: {n}"))
    else: out.append((7, False, "paper.pdf oder pruefprotokoll.json fehlt"))
    return out


def require(projekt, phasen, domain=None, log=print):
    """Bricht ab, wenn eine der Phasen nicht bestanden ist."""
    res = {p: (ok, g) for p, ok, g in check(projekt, domain)}
    fehl = [(p, res[p][1]) for p in phasen if p in res and not res[p][0]]
    if fehl:
        for p, g in fehl: log(f"Phase {p} nicht bestanden: {g}")
        raise SystemExit(f"Abbruch: Pflichtphasen {[p for p, _ in fehl]} nicht bestanden (siehe docs/WORKFLOW_PROMPT.md). Ausnahme nur mit --ohne-gates.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("projekt"); ap.add_argument("--domain", default=""); a = ap.parse_args()
    for p, ok, g in check(a.projekt, a.domain or None): print(f"Phase {p}: {'OK    ' if ok else 'OFFEN '} {g}")
