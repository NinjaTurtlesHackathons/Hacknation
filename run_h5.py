"""H5 (prereg.md): Literatur-Prior vs. GP + EI auf neuen Seeds 1020-1039."""
import json, time
import numpy as np
from asd.data import load
from asd.hypotheses import load_hypotheses
from asd import runner
from asd.gates import compare

seeds = list(range(1020, 1040)); ds = load()
hyps = {v: load_hypotheses(v) for v in ("named", "neutral", "literature")}
t0 = time.time()
runs, rows = runner.run_all(["random", "gp_ei", "hybrid", "hybrid_lit"], seeds, 400, hyps, dsets=("echt", "negativkontrolle_je_seed"))
res = {"n": ds.n, "runs": runs}; out = {}
for name, (a, b, d) in {"H5a_hybrid_lit_vs_gp_ei": ("hybrid_lit", "gp_ei", "echt"), "H5b_hybrid_vs_gp_ei": ("hybrid", "gp_ei", "echt"),
                        "gp_ei_vs_random": ("gp_ei", "random", "echt"), "hybrid_lit_vs_random": ("hybrid_lit", "random", "echt"),
                        "neg_hybrid_lit_vs_random": ("hybrid_lit", "random", "negativkontrolle_je_seed")}.items():
    c = compare(res, a, b, d); c["erfolg"] = bool(c["p"] < 0.05 and c["ci95"][0] > 1); out[name] = {k: v for k, v in c.items() if k != "run_ids"}
    print(f"{name}: Ø N {c['mean_better']:.1f} vs {c['mean_base']:.1f}, Speedup {c['speedup']:.2f} (KI {c['ci95'][0]:.2f}-{c['ci95'][1]:.2f}), p = {c['p']:.4f}, Kriterium erfüllt: {c['erfolg']}")
json.dump({"seeds": seeds, "tests": out, "runs": runs}, open("results/h5.json", "w"), ensure_ascii=False, indent=1, default=float)
print(f"{time.time() - t0:.0f} s")
