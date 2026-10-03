"""Red team T7: optimal_gamma vs brute force (exact Fractions over g <= 3000) on random and edge (alpha, c)."""
import random
from fractions import Fraction as F
from algo_efficiency import spec as S
rng = random.Random(3); bad = 0; n = 0
cases = [(F(0), F(1, 2)), (F(999, 1000), F(1, 1000)), (F(1, 2), F(1)), (F(1, 2), F(10)), (F(9, 10), F(1, 100))]
cases += [(F(rng.randint(0, 99), 100), F(rng.randint(1, 200), 1000)) for _ in range(200)]
for a, c in cases:
    arg, best, G = S.optimal_gamma(a, c)
    if arg is None: continue
    vals = [S.speedup(a, c, g) for g in range(min(3000, 40 * G + 50))]; m = max(vals)
    bf = [g for g, v in enumerate(vals) if v == m]; n += 1
    if bf != arg: bad += 1; print("mismatch", a, c, arg, bf)
print(f"{n} cases, {bad} mismatches")
