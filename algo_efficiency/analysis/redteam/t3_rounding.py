"""Red team T3: the final conversion interval -> mp.mpf (53-bit, round-to-nearest) in certify_lower / rigorous_sup.

certify_lower: lower = mpf_to_frac(mp.mpf(m)) rounds the rigorous lower endpoint m to 53 bits -- possibly UP.
rigorous_sup:  ub = mpf_to_frac(mp.mpf(interval.b)) rounds the rigorous upper endpoint to 53 bits -- possibly DOWN.
Question: is the Remez polynomial levelled tightly enough (sup S vs min alternation value m) that the 1e-16 relative rounding
window opens a gap where BOTH 'upper' and 'lower' claims pass at the same eps (a logical contradiction => a false claim passes)?
For each (B, d, kind): m_exact (exact lower endpoint), lower (what the verifier uses), S = high-precision sup of the same Remez
polynomial (dense grid + local refinement at 60 digits). Window exists iff lower > S. If so, try the verifier on eps in (S, lower).
"""
from fractions import Fraction as F
import mpmath
from mpmath import mp, iv

from algo_efficiency import polyexp as PE
from algo_efficiency.domain import DOMAIN as D


def exact_lo(x):  # exact lower endpoint of an ivmpf
    s, man, ex, _ = x._mpi_[0]; v = F(int(man)) * F(2) ** ex; return -v if s else v


def analyse(B, n, kind):
    B = F(B); c, ref, E, emax = PE.remez(B, n, kind)
    pm = PE.cheb_to_monomial([PE.mpf_to_frac(x) for x in c]); pts = [PE.mpf_to_frac(t) for t in ref]
    with PE._ivdps(40):
        Bi = PE._ivq(B); errs = []
        for t in pts:
            ti = PE._ivq(t); w = iv.mpf(1) if kind == "absolute" else iv.exp(-Bi * ti)
            errs.append(w * (iv.exp(Bi * ti) - PE._ivq(PE._poly_exact(pm, t))))
        m_iv = min((abs(e) for e in errs), key=lambda e: exact_lo(e))
        m_exact = exact_lo(m_iv)
        m = min(min(abs(e.a), abs(e.b)) for e in errs)
        lower = PE.mpf_to_frac(mp.mpf(m))            # exactly what certify_lower does
    with mp.workdps(60):
        Bm = mp.mpf(B.numerator) / B.denominator
        pmm = [mp.mpf(a.numerator) / a.denominator for a in pm]
        def err(t):
            pv = mp.polyval(pmm[::-1], t); w = 1 if kind == "absolute" else mp.exp(-Bm * t)
            return abs(w * (mp.exp(Bm * t) - pv))
        N = 20000; grid = [-1 + mp.mpf(2) * i / N for i in range(N + 1)]; vals = [err(t) for t in grid]
        S = max(vals)
        for i in range(1, N):                        # golden-section refinement at every local max
            if vals[i] >= vals[i - 1] and vals[i] >= vals[i + 1]:
                lo, hi = grid[i - 1], grid[i + 1]
                for _ in range(120):
                    a1, a2 = lo + (hi - lo) * mp.mpf("0.381966011250105"), lo + (hi - lo) * mp.mpf("0.618033988749895")
                    if err(a1) > err(a2): hi = a2
                    else: lo = a1
                S = max(S, err((lo + hi) / 2))
        S = max(S, err(mp.mpf(-1)), err(mp.mpf(1)))
        Sf = F(mpmath.nstr(S, 55))                    # decimal at 55 digits; ~1e-50 relative accuracy
    return dict(m_exact=m_exact, lower=lower, S=Sf, levelling=float((Sf - m_exact) / Sf), round_up=float((lower - m_exact) / m_exact))


if __name__ == "__main__":
  cases = [(1, 3, "relative"), (1, 4, "relative"), (1, 5, "relative"), (2, 6, "relative"), (4, 10, "relative"), (4, 8, "absolute"),
           (3, 7, "relative"), (8, 16, "relative"), (1, 6, "absolute"), (2, 5, "absolute"), (16, 30, "relative"), (5, 9, "relative")]
  for B, n, kind in cases:
      r = analyse(B, n, kind)
      window = r["lower"] > r["S"]
      print(f"B={B:>2} d={n:>2} {kind:8s}: (S - m)/S = {r['levelling']:.2e}; rounding of m = {r['round_up']:+.2e}; window lower > S: {window}")
      if window:
          eps = (r["lower"] + r["S"]) / 2; es = f"{eps.numerator}/{eps.denominator}"
          lo = D.check({"typ": "exp_degree", "B": B, "eps": es, "error": kind, "bound": "lower", "d": n})
          up = D.check({"typ": "exp_degree", "B": B, "eps": es, "error": kind, "bound": "upper", "d": n})
          print(f"      eps = S + (lower - S)/2: lower claim passes={lo[0]}, upper claim passes={up[0]}  <- both True = contradiction")
          print(f"      lower reason: {lo[1][:160]}\n      upper reason: {up[1][:160]}")
