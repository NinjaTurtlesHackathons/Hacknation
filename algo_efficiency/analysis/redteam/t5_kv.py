"""Red team T5: kv_compare. (a) verifier seeds reachable from the experiment op (no holdout); (b) is 'oracle' really a lower
bound per seed; (c) seed-overfitting: how many (n, budget) configurations of a weak pair pass by scanning; (d) p-value of 0."""
import numpy as np
from algo_efficiency.domain import DOMAIN as D
from algo_efficiency import kv

r = kv.compare("sink_recent", "recent", 128, 16)
e = D.run_op("kv_evaluate", {"policy": "sink_recent", "n": 128, "budget": 16, "seed": 1000})
print("(a) experiment op with seed 1000 == verifier raw_a[0]:", e["rel_error"] == r["raw_a"][0], "| p-value reported:", r["p_a_better"])
worse = 0; tot = 0
for n, b in [(128, 16), (256, 32), (256, 128), (512, 64)]:
    o = [kv.evaluate("oracle", n=n, budget=b, seed=s)["rel_error"] for s in kv.VERIFIER_SEEDS[:10]]
    for pol in ("h2o", "sink_recent", "recent", "random"):
        x = [kv.evaluate(pol, n=n, budget=b, seed=s)["rel_error"] for s in kv.VERIFIER_SEEDS[:10]]
        w = sum(xi < oi for xi, oi in zip(x, o)); worse += w; tot += len(o)
        if w: print(f"(b) n={n} budget={b}: {pol} beats 'oracle' on {w}/10 seeds (mean {np.mean(x):.4f} vs oracle {np.mean(o):.4f})")
print(f"(b) oracle beaten on {worse}/{tot} seed-policy pairs")
passed = []
for n in (64, 96, 128, 192, 256):
    for b in (8, 16, 24, 32, 48):
        if b >= n: continue
        ok, why, rr = D.check({"typ": "kv_compare", "policy_a": "recent", "policy_b": "random", "n": n, "budget": b, "better": "a"})
        if ok: passed.append((n, b, round(rr["ratio_b_over_a"], 3), rr["p_a_better"]))
print(f"(c) 'recent beats random' (not significant at n=256,b=32 in the paper's table) passes at {len(passed)} of the scanned configs: {passed}")
