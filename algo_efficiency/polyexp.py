"""Polynomial approximation of exp on [-B, B]: the quantity behind the polynomial method for subquadratic attention.

If all attention logits satisfy |<q_i, k_j>| <= B and P is a degree-d polynomial with sup |e^x - P(x)| / e^x <= eps on [-B, B],
then exp(Q K^T) is approximated entrywise (relative error eps) by a matrix of rank <= C(h + d, d) (h = head dimension), so
attention can be computed in time ~ n * C(h + d, d) instead of n^2 (Alman & Song 2023). The minimal degree d*(B, eps) therefore
decides when this route is subquadratic; fine-grained complexity (SETH) says no route is once B grows like sqrt(log n).

Verifier side (rigorous):
  certify_upper(B, eps, d): builds its own near-minimax polynomial (Remez, mpmath), rounds it to exact rationals and bounds the
                            weighted error on [-B, B] from above with interval arithmetic (adaptive Taylor models with explicit
                            remainder). Passes only if the rigorous upper bound is <= eps.
  certify_lower(B, eps, d): de la Vallee Poussin: if some degree-d polynomial has an error that alternates in sign at d + 2
                            points with |error| >= m everywhere there, EVERY degree-d polynomial has sup error >= m. The error at
                            the points is enclosed with interval arithmetic. Passes only if m > eps.
Experiment side (numerical): Chebyshev interpolation at Chebyshev points (not Remez), errors on a grid; Taylor baseline.
All work happens in the scaled variable t = x / B in [-1, 1], f(t) = exp(B t); weight w = 1 (absolute) or exp(-B t) (relative).
"""
from fractions import Fraction
import math

import mpmath
from mpmath import mp, iv

B_MAX, D_MAX = 32, 48
from contextlib import contextmanager


@contextmanager
def _ivdps(d):
    old = iv.dps; iv.dps = d
    try: yield
    finally: iv.dps = old

MAX_BOXES = 40000


def _weight_mp(B, t, kind): return mp.mpf(1) if kind == "absolute" else mp.exp(-B * t)


def _cheb_vals(t, n):
    T = [mp.mpf(1), t]
    for _ in range(2, n + 1): T.append(2 * t * T[-1] - T[-2])
    return T[:n + 1]


def _err_mp(c, B, t, kind):
    return _weight_mp(B, t, kind) * (mp.exp(B * t) - sum(cj * Tj for cj, Tj in zip(c, _cheb_vals(t, len(c) - 1))))


def remez(B, n, kind="relative", dps=50, iters=80, tol=1e-12):
    """Weighted minimax approximation of exp(B t) by a degree-n polynomial (Chebyshev coefficients). Returns (coeffs, reference
    points, levelled error E, max grid error). Floating point (mpmath); NOT a certificate by itself."""
    with mp.workdps(dps):
        B = mp.mpf(B.numerator) / B.denominator if isinstance(B, Fraction) else mp.mpf(B)
        m = n + 2; ref = [-mp.cos(mp.pi * i / (m - 1)) for i in range(m)]
        N = max(4000, 80 * m); grid = [-mp.cos(mp.pi * g / (N - 1)) for g in range(N)]
        c = None; E = None; emax = None
        for _ in range(iters):
            A = mp.matrix(m, m); rhs = mp.matrix(m, 1)
            for i, t in enumerate(ref):
                T = _cheb_vals(t, n)
                for j in range(n + 1): A[i, j] = T[j]
                A[i, n + 1] = (-1) ** i / _weight_mp(B, t, kind); rhs[i] = mp.exp(B * t)
            sol = mp.lu_solve(A, rhs); c = [sol[j] for j in range(n + 1)]; E = abs(sol[n + 1])
            e = [_err_mp(c, B, t, kind) for t in grid]
            ext = []; g = 0                                      # one extremum per maximal run of constant sign
            while g < N:
                h = g; best = g
                while h + 1 < N and (e[h + 1] > 0) == (e[g] > 0):
                    h += 1
                    if abs(e[h]) > abs(e[best]): best = h
                lo, hi = grid[max(best - 1, 0)], grid[min(best + 1, N - 1)]
                for _r in range(60):                             # golden-section refinement of the local extremum
                    a1 = lo + (hi - lo) * mp.mpf("0.381966"); a2 = lo + (hi - lo) * mp.mpf("0.618034")
                    if abs(_err_mp(c, B, a1, kind)) > abs(_err_mp(c, B, a2, kind)): hi = a2
                    else: lo = a1
                tb = (lo + hi) / 2 if 0 < best < N - 1 else grid[best]
                ext.append(tb); g = h + 1
            while len(ext) > m:
                if abs(_err_mp(c, B, ext[0], kind)) < abs(_err_mp(c, B, ext[-1], kind)): ext.pop(0)
                else: ext.pop()
            vals = [abs(_err_mp(c, B, t, kind)) for t in ext]; emax = max(abs(x) for x in e + vals)
            if len(ext) < m: break
            ref = ext
            if (emax - min(vals)) / emax < tol: break
        return c, ref, E, emax


# ---------- exact conversions ----------

def mpf_to_frac(x):
    s, man, ex, _ = (x if isinstance(x, mpmath.mpf) else mp.mpf(x))._mpf_      # no re-rounding to the current precision
    v = Fraction(int(man)) * (Fraction(2) ** ex)
    return -v if s else v


def cheb_to_monomial(c):
    """Exact Chebyshev -> monomial coefficients (in t)."""
    n = len(c) - 1; T = [[Fraction(1)], [Fraction(0), Fraction(1)]]
    for k in range(2, n + 1):
        a = [Fraction(0)] + [2 * x for x in T[k - 1]]
        for i, x in enumerate(T[k - 2]): a[i] -= x
        T.append(a)
    out = [Fraction(0)] * (n + 1)
    for j, cj in enumerate(c):
        for i, x in enumerate(T[j]): out[i] += cj * x
    return out


def _ivq(x): return iv.mpf(x.numerator) / iv.mpf(x.denominator)


def _raw_to_frac(t):
    s, man, ex, _ = t; v = Fraction(int(man)) * (Fraction(2) ** ex); return -v if s else v


def iv_lo(x):
    """Exact lower endpoint of an mpmath interval (no rounding to the working precision; red-team bug 1)."""
    return _raw_to_frac(x._mpi_[0])


def iv_hi(x):
    return _raw_to_frac(x._mpi_[1])


def _poly_exact(pm, t): return sum(a * t ** i for i, a in enumerate(pm))


# ---------- rigorous lower bound (de la Vallee Poussin) ----------

def certify_lower(B, eps, n, kind="relative"):
    """Certificate that EVERY polynomial of degree <= n has weighted sup error > eps on [-B, B]."""
    B, eps = Fraction(B), Fraction(eps)
    if n < 0: return (kind == "relative" and eps < 1) or (kind == "absolute" and eps < math.exp(-float(B))), {"note": "zero polynomial"}
    c, ref, E, emax = remez(B, n, kind)
    pm = cheb_to_monomial([mpf_to_frac(x) for x in c]); pts = [mpf_to_frac(t) for t in ref]
    if len(pts) != n + 2 or any(not (-1 <= t <= 1) for t in pts) or any(a >= b for a, b in zip(pts, pts[1:])):
        return False, {"reason": "no valid alternation set found"}
    with _ivdps(40):
        Bi = _ivq(B); errs = []
        for t in pts:
            ti = _ivq(t); w = iv.mpf(1) if kind == "absolute" else iv.exp(-Bi * ti)
            errs.append(w * (iv.exp(Bi * ti) - _ivq(_poly_exact(pm, t))))
        los, his = [iv_lo(e) for e in errs], [iv_hi(e) for e in errs]
        signs = [1 if lo > 0 else (-1 if hi < 0 else 0) for lo, hi in zip(los, his)]
        if 0 in signs or any(s1 == s2 for s1, s2 in zip(signs, signs[1:])):
            return False, {"reason": "error does not alternate strictly (rigorously)"}
        lower = min(lo if sg > 0 else -hi for lo, hi, sg in zip(los, his, signs))   # exact lower end of |error|
    return lower > eps, {"lower_bound": float(lower), "remez_level": float(E), "points": len(pts)}


# ---------- rigorous upper bound (adaptive Taylor models) ----------

def _taylor_shift(pi, c):
    """Coefficients b_j of P(c + s) = sum b_j s^j (interval arithmetic, repeated synthetic division)."""
    a = list(pi); n = len(a) - 1; out = []
    for j in range(n + 1):
        acc = a[n]
        for i in range(n - 1, j - 1, -1): a[i] = a[i] + c * a[i + 1]
        out.append(a[j])
    return out


def _box_bound(pi, Bi, c, h, kind, extra=25):
    """Rigorous upper bound of the weighted error on [c - h, c + h] (c, h exact rationals)."""
    ci, hi = _ivq(c), _ivq(h); b = _taylor_shift(pi, ci); n = len(b) - 1; N = n + extra
    if kind == "absolute":
        ec = iv.exp(Bi * ci); rho = []; fact = iv.mpf(1); Bp = iv.mpf(1)
        for m in range(N + 1):
            if m: fact *= m; Bp *= Bi
            rho.append(ec * Bp / fact - (b[m] if m <= n else 0))
        Bh = Bi * hi; tail = ec * Bh ** (N + 1) / iv.factorial(N + 1) * iv.exp(Bh)
    else:   # r(c+s) = 1 - e^{-Bc} e^{-Bs} P(c+s)
        emc = iv.exp(-Bi * ci); coef = [iv.mpf(1)]
        for i in range(1, N + 1): coef.append(coef[-1] * (-Bi) / i)
        rho = []
        for m in range(N + 1):
            g = sum((b[j] * coef[m - j] for j in range(min(m, n) + 1)), iv.mpf(0))
            rho.append((1 if m == 0 else 0) - emc * g)
        Bh = Bi * hi; tail = iv.mpf(0)
        for j in range(n + 1):
            M = N - j + 1; tail += abs(b[j]) * hi ** j * Bh ** M / iv.factorial(M) * iv.exp(Bh)
        tail *= emc
    # quadratic part exactly (endpoints and vertex), higher orders by the triangle inequality
    q0, q1, q2 = rho[0], rho[1], rho[2]
    cands = [q0 + q1 * hi + q2 * hi ** 2, q0 - q1 * hi + q2 * hi ** 2]
    if not (q2.a <= 0 <= q2.b):
        sv = -q1 / (2 * q2)
        if sv.a > -hi.b and sv.b < hi.b:
            sv = iv.mpf([max(sv.a, -hi.b), min(sv.b, hi.b)]); cands.append(q0 + q1 * sv + q2 * sv ** 2)
        elif not (sv.b < -hi.a or sv.a > hi.a):
            cands.append(q0 + q1 * iv.mpf([-hi.b, hi.b]) + q2 * iv.mpf([-hi.b, hi.b]) ** 2)
    else:
        cands.append(q0 + q1 * iv.mpf([-hi.b, hi.b]) + q2 * iv.mpf([-hi.b, hi.b]) ** 2)
    quad = max(max(abs(x.a), abs(x.b)) for x in cands)
    rest = sum((abs(r) * hi ** m for m, r in enumerate(rho) if m >= 3), iv.mpf(0)) + tail
    return iv.mpf(quad) + rest


def rigorous_sup(pm, B, eps, kind, max_boxes=MAX_BOXES):
    """Adaptive bisection of [-1, 1]; returns (sup_bound <= eps?, bound, boxes)."""
    with _ivdps(40):
        pi = [_ivq(a) for a in pm]; Bi = _ivq(B); stack = [(Fraction(-1) + Fraction(2 * i + 1, 32), Fraction(1, 32)) for i in range(32)]
        worst = Fraction(0); boxes = 0
        while stack:
            c, h = stack.pop(); boxes += 1
            if boxes > max_boxes: return False, None, boxes
            ub = iv_hi(_box_bound(pi, Bi, c, h, kind))                              # exact upper endpoint
            if ub <= eps: worst = max(worst, ub); continue
            if h < Fraction(1, 2 ** 40): return False, float(ub), boxes
            stack += [(c - h / 2, h / 2), (c + h / 2, h / 2)]
        return True, float(worst), boxes


def certify_upper(B, eps, n, kind="relative"):
    """Certificate that SOME polynomial of degree <= n has weighted sup error <= eps on [-B, B] (constructed by the verifier)."""
    B, eps = Fraction(B), Fraction(eps)
    c, ref, E, emax = remez(B, n, kind)
    if emax >= mp.mpf(eps.numerator) / eps.denominator:
        return False, {"reason": f"verifier's own minimax error {mpmath.nstr(emax, 6)} is not below eps", "remez_level": float(E)}
    pm = cheb_to_monomial([mpf_to_frac(x) for x in c])
    ok, bound, boxes = rigorous_sup(pm, B, eps, kind)
    return ok, {"upper_bound": bound, "remez_level": float(E), "boxes": boxes}


# ---------- numerical experiments (independent of the verifier's method) ----------

def cheb_interp_error(B, d, kind="relative", grid=1500, dps=30):
    """Interpolate exp(B t) at d + 1 Chebyshev points; weighted max error on a grid. Near-minimax estimate (candidate)."""
    with mp.workdps(dps):
        B = mp.mpf(B); nodes = [mp.cos(mp.pi * (k + mp.mpf(1) / 2) / (d + 1)) for k in range(d + 1)]
        vals = [mp.exp(B * x) for x in nodes]
        c = [(2 if j else 1) * mp.fsum(v * mp.cos(j * mp.pi * (k + mp.mpf(1) / 2) / (d + 1)) for k, v in enumerate(vals)) / (d + 1) for j in range(d + 1)]
        err = max(abs(_err_mp(c, B, -mp.cos(mp.pi * g / (grid - 1)), kind)) for g in range(grid))
        return float(err)


def taylor_degree(B, eps, kind="relative"):
    """Smallest d such that the degree-d Taylor polynomial at 0 has weighted sup error <= eps on [-B, B] (grid estimate)."""
    with mp.workdps(30):
        B = mp.mpf(B); eps = mp.mpf(eps)
        for d in range(0, 400):
            xs = [B * (-1 + 2 * mp.mpf(g) / 400) for g in range(401)]
            e = max(abs((mp.exp(x) - mp.fsum(x ** j / mp.factorial(j) for j in range(d + 1))) * (mp.exp(-x) if kind == "relative" else 1)) for x in xs)
            if e <= eps: return d
    return None


def polymethod_rank(h, d): return math.comb(int(h) + int(d), int(d))
