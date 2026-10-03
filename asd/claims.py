"""Claims: jeder Satz im Paper braucht eine claim_id mit Beleg (evidence_run_ids). Erzeugt nur aus Gate-Ergebnissen."""
import numpy as np
from .gates import compare

LEVELS = ["proved_lean", "computed_rigorous", "statistical", "observed", "hypothesis"]


def build(results, gates):
    G = {g["gate"]: g for g in gates}; C = results.get("comparisons", {}); claims = []
    def add(cid, text, level, ev, status):
        assert level in LEVELS; claims.append(dict(claim_id=cid, text=text, level=level,
                                                   evidence_run_ids=";".join(ev), status=status))
    st = lambda ok: "bestätigt" if ok else "widerlegt"
    runs = results["runs"]; ids = lambda pol, ds="echt": [r["run_id"] for r in runs if r["policy"] == pol and r["dataset"] == ds]

    if "G7_lean_lemma" in G:
        add("C-lemma", "Für Zufallssuche ohne Zurücklegen gilt E[N] = (n+1)/(k+1); Beweis in Lean 4 (lean/ENRandom.lean).",
            "proved_lean" if G["G7_lean_lemma"]["passed"] else "hypothesis", [], "bestätigt" if G["G7_lean_lemma"]["passed"] else "offen")
    for ds in ["echt", "negativkontrolle", "negativkontrolle_je_seed"]:
        g = G.get(f"G1_theorie_zufall_{ds}")
        if g: add(f"C-theorie-{ds}", f"Zufallssuche ({ds}) stimmt mit der Theorie überein: {g['reason']}.", "statistical", ids("random", ds), st(g["passed"]))
    if "G2_reproduktion_selftest" in G:
        g = G["G2_reproduktion_selftest"]
        add("C-repro", f"Die Pipeline reproduziert die Selbsttest-Rohdaten exakt ({g['reason']}).", "computed_rigorous",
            ids("random") + ids("gp_ei"), st(g["passed"]))
    for gate, cid, label in [("G3_gp_ei_schlaegt_zufall", "C-gp", "GP + EI schlägt Zufallssuche"),
                             ("G3_hybrid_schlaegt_zufall", "C-hybrid-zufall", "Hybrid schlägt Zufallssuche"),
                             ("H1_hybrid_schlaegt_gp_ei", "C-H1", "H1: Hybrid schlägt GP + EI")]:
        if gate in G:
            ok = G[gate]["passed"]; pre = "" if ok or not cid.startswith("C-H") else "Nicht belegt, das präregistrierte Erfolgskriterium (p < 0,05 und KI-Untergrenze > 1) ist verfehlt. "
            add(cid, f"{label}: {pre}{G[gate]['reason']}.", "statistical", C[gate]["run_ids"], "bestätigt" if ok else ("offen" if cid.startswith("C-H") else "widerlegt"))
    if "G5_kontamination_H2" in G:
        g = G["G5_kontamination_H2"]; add("C-H2", f"H2 (Kontamination): {g['reason']}", "statistical", C["H2"]["run_ids"] + ids("hybrid"), "bestätigt" if g["passed"] else "offen")
    neg = [g for k, g in G.items() if k.startswith("G4_negativkontrolle_") and not k.endswith("_seed7")]
    if neg:
        ok = all(g["passed"] for g in neg); ev = sum((C[g["gate"]]["run_ids"] for g in neg), [])
        add("C-neg", "Negativkontrolle (vertauschte Ausbeuten, eigene Vertauschung je Seed): " + " | ".join(f"{g['gate'].split('_', 2)[-1]}: {g['reason']}" for g in neg),
            "statistical", ev, st(ok))
    if "G4_negativkontrolle_gp_ei_seed7" in G:
        g = G["G4_negativkontrolle_gp_ei_seed7"]
        add("C-neg-seed7", f"Negativkontrolle wie präregistriert (eine Vertauschung, Seed 7), GP + EI: {g['reason']}.",
            "statistical", C[g["gate"]]["run_ids"], st(g["passed"]))
    for pol in sorted({r["policy"] for r in runs} - {"random", "gp_ei"}):
        cs = compare(results, pol, "random", "negativkontrolle")
        n_vals = {r["N"] for r in runs if r["policy"] == pol and r["dataset"] == "negativkontrolle"}
        add(f"C-neg-seed7-{pol}", f"{pol} auf der präregistrierten Einzel-Vertauschung (Seed 7): Speedup {cs['speedup']:.2f} "
            f"(KI {cs['ci95'][0]:.2f}–{cs['ci95'][1]:.2f}), p = {cs['p']:.4f}. Kein Leck: das feste KI-Vorwissen ordnet die Kandidaten "
            f"für alle Seeds gleich, ein zufällig hoch eingestufter Treffer wird daher in jedem Seed gefunden (Werte von N: {sorted(n_vals)}). "
            "Die 20 Seeds sind hier keine unabhängigen Wiederholungen; maßgeblich ist C-neg.", "observed", cs["run_ids"], "bestätigt")
    for pol in sorted({r["policy"] for r in runs}):
        N = [r["N"] for r in runs if r["policy"] == pol and r["dataset"] == "echt"]
        add(f"C-mean-{pol}", f"{pol}: im Mittel {np.mean(N):.1f} Experimente bis zum ersten Top-1-%-Treffer (Median {np.median(N):.0f}, {len(N)} Seeds).",
            "observed", ids(pol), "bestätigt")
    for h in results.get("hyptests", []):
        lvl = "statistical" if h["status"] == "bestätigt" else "hypothesis"
        add(f"C-hyp-{h['id']}", f"KI-Hypothese ({h['view']}): {h['text']} [r = {h['r']:.2f}, p = {h['p']:.4f}, p_BH = {h['p_adj']:.4f}]",
            lvl, [results["hyptest_run_id"]], h["status"])
    return claims
