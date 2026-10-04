"""Red-team counterexample search for Theorem 1 / Lemma L2 + L4: a finite-state one-layer realisation of Z3 (one letter of
order 3) with a single rank-1 affine transition h -> (I + v w^T) h + b would contradict h*(Z3) = 2.
Exhaustive over small integer/half-integer data in dimensions 2 and 3; also checks the complex-diagonal case, where a
1x1 complex rotation has complex rank(A - I) = 1, i.e. the real invariant h* does not bound the complex rank.
Run: python3 -m expressivity.analysis.redteam.t13_counterexample_search
"""
import itertools
from fractions import Fraction as F
import cmath


def orbit_ok(A, b, h0, maxlen=60):
    """Return True if h_t (t >= 1) is eventually periodic with a consistent readout of t mod 3, i.e. a realisation."""
    d = len(h0)
    seen = {}
    h = tuple(h0)
    for t in range(1, maxlen + 1):
        h = tuple(sum(A[i][j] * h[j] for j in range(d)) + b[i] for i in range(d))
        if any(abs(x) > 10 ** 6 for x in h):
            return False
        if h in seen:
            t0 = seen[h]
            return (t - t0) % 3 == 0  # period divisible by 3 <=> states determine t mod 3 consistently
        seen[h] = t
    return False


def search(d, vals):
    hits = 0; tried = 0
    vecs = list(itertools.product(vals, repeat=d))
    for v in vecs:
        if all(x == 0 for x in v): continue
        for w in vecs:
            if all(x == 0 for x in w): continue
            A = [[(1 if i == j else 0) + v[i] * w[j] for j in range(d)] for i in range(d)]
            for b in vecs:
                for h0 in itertools.product([0, 1], repeat=d):
                    tried += 1
                    if orbit_ok(A, b, h0):
                        hits += 1
                        print("HIT", v, w, b, h0)
    return tried, hits


if __name__ == "__main__":
    vals = [F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2)]
    for d in (2,):
        tried, hits = search(d, vals)
        print(f"d={d}: tried {tried} rank-1 affine letters, realisations of Z3 found: {hits}")
    vals3 = [F(-1), F(0), F(1)]
    tried, hits = search(3, vals3)
    print(f"d=3: tried {tried} rank-1 affine letters, realisations of Z3 found: {hits}")
    # complex diagonal: 1x1 state, A = exp(2 pi i / 3), complex rank(A - 1) = 1; orbit of h0 = 1 has period 3
    a = cmath.exp(2j * cmath.pi / 3)
    hs = [a ** t for t in range(1, 7)]
    distinct = len({(round(z.real, 9), round(z.imag, 9)) for z in hs})
    print(f"complex 1x1 rotation: complex rank(A-1) = 1, orbit period = {distinct} -> Z3 realised with complex rank 1 < h*(Z3) = 2;"
          " its real 2x2 form has rank(A-I) = 2")
