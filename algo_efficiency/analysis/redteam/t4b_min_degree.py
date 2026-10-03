"""Red team T4b: the T4 window propagates to exp_min_degree and polymethod_rank (false minimal degree / rank)."""
import math
from algo_efficiency.domain import DOMAIN as D
from algo_efficiency.analysis.redteam.t3_rounding import analyse

r = analyse(3, 7, "relative"); eps = (r["lower"] + r["S"]) / 2; es = f"{eps.numerator}/{eps.denominator}"
for c in [{"typ": "exp_min_degree", "B": 3, "eps": es, "error": "relative", "d": 8},
          {"typ": "exp_min_degree", "B": 3, "eps": es, "error": "relative", "d": 7},
          {"typ": "polymethod_rank", "h": 16, "B": 3, "eps": es, "error": "relative", "rank": math.comb(24, 8)},
          {"typ": "polymethod_rank", "h": 16, "B": 3, "eps": es, "error": "relative", "rank": math.comb(23, 7)}]:
    ok, why, _ = D.check(c); print(f"{'PASS' if ok else 'fail'} d/rank={c.get('d', c.get('rank'))}: {why[:170]}")
print("true d* = 7 (T4 proves a degree-7 polynomial reaches <= eps).")
