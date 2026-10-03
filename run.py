"""Eine Pipeline, ein Demo-Pfad: Hypothesen laden -> Lab-Läufe -> Hypothesentest -> Gates -> Claims -> Tabellen.

  python run.py                       # alle Policies, 20 Seeds, Budget 400 (prereg)
  python run.py --seeds 3             # Checkpoint 23:15 (schneller Probelauf)
  python run.py --policies random,gp_ei   # ohne KI
"""
import argparse, json, time
import numpy as np
from asd.data import load, SEEDS
from asd.hypotheses import load_hypotheses
from asd import runner, hyptest, gates as G, claims as CL, tables as T

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=20); ap.add_argument("--budget", type=int, default=400)
ap.add_argument("--policies", default="random,gp_ei,hybrid,hybrid_neutral"); ap.add_argument("--workers", type=int)
ap.add_argument("--out", default="tables")
a = ap.parse_args()
policies = a.policies.split(","); seeds = SEEDS[:a.seeds]
ds = load(); t0 = time.time()
hyps = {v: load_hypotheses(v) for v in ["named", "neutral"]} if any(p.startswith("hybrid") for p in policies) else None

runs, rows = runner.run_all(policies, seeds, a.budget, hyps, a.workers)
results = {"n": ds.n, "seeds": len(seeds), "budget": a.budget, "runs": runs}
print(f"Läufe fertig nach {time.time() - t0:.0f} s", flush=True)
if hyps:
    ht, ht_rows, ht_id = hyptest.run(ds, hyps); results["hyptests"] = ht; results["hyptest_run_id"] = ht_id; rows += ht_rows

gate_rows = []
for g in G.default_gates(policies, reproducible=(a.budget == 400)):
    passed, reason = g.check(results)
    gate_rows.append(dict(gate=g.name, passed=bool(passed), reason=reason, ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
    print(f"[{'OK ' if passed else 'ROT'}] {g.name}: {reason}", flush=True)
claims = CL.build(results, gate_rows)

T.write("experiments", rows, a.out); T.write("gates", gate_rows, a.out); T.write("claims", claims, a.out)
errs = T.validate(a.out)
print("Tabellen-Validierung:", "OK" if not errs else errs)
json.dump(results, open(f"{a.out}/results.json", "w"), ensure_ascii=False, indent=1, default=float)
print(f"Fertig nach {time.time() - t0:.0f} s -> {a.out}/")
