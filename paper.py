"""Paper-Gerüst aus der Tabelle claims: jeder Ergebnissatz trägt seine claim_id. Nichts ohne Beleg.
  python paper.py [tables] -> paper/results.md
"""
import os, sys
from asd import tables as T

src = sys.argv[1] if len(sys.argv) > 1 else "tables"
C = T.read("claims", src).set_index("claim_id"); G = T.read("gates", src)
def s(cid): return f"{C.loc[cid, 'text']} [{cid}, {C.loc[cid, 'level']}, {C.loc[cid, 'status']}]" if cid in C.index else ""
sec = [("Theorie", ["C-lemma", "C-theorie-echt", "C-repro"]),
       ("Bayes'sche Optimierung als Baseline", ["C-mean-random", "C-mean-gp_ei", "C-gp"]),
       ("KI-Vorwissen (Hybrid), präregistrierte Hypothese H1", ["C-mean-hybrid", "C-hybrid-zufall", "C-H1"]),
       ("Kontaminationstest (H2)", ["C-mean-hybrid_neutral", "C-H2"]),
       ("Negativkontrollen", ["C-theorie-negativkontrolle_je_seed", "C-neg", "C-neg-seed7"] + [c for c in C.index if c.startswith("C-neg-seed7-")])]
out = ["# Ergebnisse (automatisch aus `claims` erzeugt)", "",
       f"Gates: {int(G.passed.astype(str).eq('True').sum())}/{len(G)} grün. Jede Aussage nennt ihre claim_id, ihr Evidenzlevel und ihren Status.", ""]
for title, ids in sec:
    lines = [f"- {s(c)}" for c in ids if c in C.index]
    if lines: out += [f"## {title}", ""] + lines + [""]
hyp = [c for c in C.index if c.startswith("C-hyp-")]
if hyp:
    out += ["## Hypothesen der KI (Status nach Benjamini-Hochberg, q = 0,1)", ""] + [f"- {s(c)}" for c in hyp] + [""]
os.makedirs("paper", exist_ok=True); open("paper/results.md", "w").write("\n".join(out)); print("paper/results.md")
