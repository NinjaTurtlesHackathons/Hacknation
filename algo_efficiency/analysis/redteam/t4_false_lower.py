"""Red team T4: turn the T3 rounding window into a rigorously FALSE claim that passes the verifier, and test whether the
reported 'rigorous upper bound' can lie below the true sup error (dense high-precision sampling).

Rigorous refutation: a patched copy of rigorous_sup that converts interval endpoints EXACTLY (no 53-bit rounding) proves that
the verifier's own Remez polynomial has sup error <= eps; yet DOMAIN.check accepts 'every degree-d polynomial has error > eps'.
"""
from fractions import Fraction as F
import mpmath
from mpmath import mp, iv

from algo_efficiency import polyexp as PE
from algo_efficiency.domain import DOMAIN as D
from algo_efficiency.analysis.redteam.t3_rounding import analyse


def exact_hi(x):
    s, man, ex, _ = x._mpi_[1]; v = F(int(man)) * F(2) ** ex; return -v if s else v


def rigorous_sup_exact(pm, B, eps, kind, max_boxes=200000):
    with PE._ivdps(60):
        pi = [PE._ivq(a) for a in pm]; Bi = PE._ivq(B)
        stack = [(F(-1) + F(2 * i + 1, 32), F(1, 32)) for i in range(32)]; worst = F(0); boxes = 0
        while stack:
            c, h = stack.pop(); boxes += 1
            if boxes > max_boxes: return False, None, boxes
            ub = exact_hi(PE._box_bound(pi, Bi, c, h, kind, extra=35))
            if ub <= eps: worst = max(worst, ub); continue
            if h < F(1, 2 ** 60): return False, ub, boxes
            stack += [(c - h / 2, h / 2), (c + h / 2, h / 2)]
        return True, worst, boxes


for B, n, kind in [(3, 7, "relative"), (2, 5, "absolute"), (5, 9, "relative"), (4, 8, "absolute")]:
    r = analyse(B, n, kind); eps = (r["lower"] + r["S"]) / 2; es = f"{eps.numerator}/{eps.denominator}"
    ok_v, why, _ = D.check({"typ": "exp_degree", "B": B, "eps": es, "error": kind, "bound": "lower", "d": n})
    c, ref, E, emax = PE.remez(F(B), n, kind); pm = PE.cheb_to_monomial([PE.mpf_to_frac(x) for x in c])
    ok_r, U, boxes = rigorous_sup_exact(pm, F(B), eps, kind)
    print(f"B={B} d={n} {kind}: eps={float(eps):.17e}  verifier 'lower' (no poly reaches <= eps) passes: {ok_v}; "
          f"exact-endpoint proof that the verifier's own poly reaches <= eps: {ok_r} (U - eps = {float(U - eps) if U is not None else None:.3e}, boxes {boxes})")
    if ok_v and ok_r: print(f"   => FALSE CLAIM PASSES: {D.describe({'typ': 'exp_degree', 'B': B, 'eps': es, 'error': kind, 'bound': 'lower', 'd': n})[:120]}...")

print("\nReported upper_bound vs high-precision sup S of the verifier's polynomial (eps just above S):")
for B, n, kind in [(1, 3, "relative"), (1, 4, "relative"), (2, 6, "relative"), (4, 10, "relative"), (8, 16, "relative"), (1, 6, "absolute"), (16, 30, "relative")]:
    r = analyse(B, n, kind); S = r["S"]; eps = S * (1 + F(1, 10 ** 15)); es = f"{eps.numerator}/{eps.denominator}"
    ok, why, info = D.check({"typ": "exp_degree", "B": B, "eps": es, "error": kind, "bound": "upper", "d": n})
    ub = info.get("upper_bound")
    rel = (F(ub) - S) / S if ub is not None else None
    print(f"B={B:>2} d={n:>2} {kind}: passed={ok}; reported bound - S (relative) = {float(rel) if rel is not None else None:+.2e}"
          f"{'   <-- bound BELOW true sup' if rel is not None and rel < 0 else ''}")
