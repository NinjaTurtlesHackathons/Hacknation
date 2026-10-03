"""Red team T6: polynomial-method edge cases: degree 0, tiny/large B, absolute error with large B, eps at the limits.
For each case: lower certificate value L and upper certificate value U of the SAME degree must satisfy L <= U (else unsound)."""
import time
from fractions import Fraction as F
from algo_efficiency import polyexp as PE
from algo_efficiency.domain import DOMAIN as D

for B, d, kind in [(F(1, 100), 0, "relative"), (F(1, 100), 3, "relative"), (1, 0, "relative"), (1, 0, "absolute"),
                   (32, 0, "relative"), (32, 20, "relative"), (32, 40, "relative"), (32, 48, "absolute"), (F(1, 3), 2, "absolute")]:
    t = time.time()
    lo_ok, li = PE.certify_lower(F(B), F(1, 10 ** 30), d, kind)
    L = li.get("lower_bound")
    up_ok, ui = PE.certify_upper(F(B), F(1, 2), d, kind) if kind == "relative" else (None, {})
    U = ui.get("upper_bound")
    # exact minimax error for degree 0 relative: (e^B - e^-B)/(e^B + e^-B) = tanh(B)
    print(f"B={str(B):>6} d={d:>2} {kind:8s}: L={L} U={U} remez={li.get('remez_level')} L<=U: {None if U is None or L is None else L <= U}  ({time.time() - t:.1f}s)")
import math
print("degree-0 relative exact minimax = tanh(B): B=1 ->", math.tanh(1), "; B=32 ->", math.tanh(32))
print(D.check({"typ": "exp_min_degree", "B": 1, "eps": "0.5", "error": "relative", "d": 0}))
print(D.check({"typ": "exp_degree", "B": 1, "eps": "0.76", "error": "relative", "bound": "upper", "d": 0}))  # eps>1/2 rejected by range
print(D.check({"typ": "exp_degree", "B": 32, "eps": "0.5", "error": "absolute", "bound": "upper", "d": 48}))
