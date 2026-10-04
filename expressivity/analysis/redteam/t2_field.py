"""T2: soundness of the exact real cyclotomic field K_N = Q(2cos(2pi/N)).
(a) minimal polynomial vs an exact integer construction from the cyclotomic polynomial (Dickson substitution), N <= 999
    (Z<n> admits n <= 999; count covers use N = lcm of letter orders);
(b) random arithmetic identities: x * x^-1 = 1, (a+b)c = ac+bc, numeric agreement with mpmath, equality vs numeric zero;
(c) canonical keys: the same number reached by different routes must give the same mkey (closure dictionary key);
    and the same mkey must never denote two different numbers inside one field;
(d) two_cos / embed / sqrt5 against mpmath;  (e) sign() on tiny nonzero elements."""
import random, time
from fractions import Fraction
import mpmath, sympy
from expressivity.algebra import Field, Elt, minpoly_2cos, embed, mkey

random.seed(1)
x = sympy.symbols("x")

def exact_minpoly(N):
    cyc = sympy.Poly(sympy.cyclotomic_poly(N, x), x).all_coeffs()[::-1]   # low -> high
    deg = len(cyc) - 1; d = deg // 2
    D = [[2], [0, 1]]
    def addp(a, b, s=1):
        n = max(len(a), len(b)); return [(a[i] if i < len(a) else 0) + s * (b[i] if i < len(b) else 0) for i in range(n)]
    for k in range(2, d + 1): D.append(addp([0] + D[-1], D[-2], -1))
    psi = [cyc[d]]
    for k in range(1, d + 1): psi = addp(psi, [cyc[d + k] * c for c in D[k]])
    while len(psi) > 1 and psi[-1] == 0: psi.pop()
    return tuple(int(c) for c in psi)

print("(a) minimal polynomials")
wrong = []; refused = []; t0 = time.time()
for N in range(3, 1000):  # (slow part)
    want = exact_minpoly(N)
    try: got = minpoly_2cos(N)
    except ArithmeticError: refused.append(N); continue
    if got != want: wrong.append(N)
print(f"  N in 3..999: wrong (silently accepted) = {wrong[:20]}{' ...' if len(wrong) > 20 else ''} (count {len(wrong)}); refused = {refused[:10]}{'...' if len(refused) > 10 else ''} (count {len(refused)}); {time.time()-t0:.0f}s")
if wrong:
    N = wrong[0]; want = exact_minpoly(N)
    print(f"  first wrong N = {N}: degree {len(want)-1}, max |coeff| = {max(abs(c) for c in want):.3e}")

def rnd(F):
    return Elt(F, [Fraction(random.randint(-9, 9), random.randint(1, 5)) for _ in range(F.deg)])

def num(e): return e.F.numeric(e, 50)

print("(b) random arithmetic")
bad = 0; tests = 0
for N in (5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 20, 24, 30, 60):
    F = Field(N)
    for _ in range(30):
        a, b, c = rnd(F), rnd(F), rnd(F); tests += 1
        if not a.is_zero():
            if not (a * a.inv()) == F.one: bad += 1; print("  inv fail", N, a)
        if (a + b) * c != a * c + b * c: bad += 1; print("  distributivity fail", N)
        if abs(num(a * b) - num(a) * num(b)) > mpmath.mpf(10) ** -30: bad += 1; print("  numeric mul fail", N)
        if not a.is_zero() and abs(num(a / b if not b.is_zero() else a) ) == 0: bad += 1
        if (a == b) != (abs(num(a) - num(b)) < mpmath.mpf(10) ** -30): bad += 1; print("  eq fail", N)
print(f"  {tests} random triples, failures: {bad}")

print("(c) canonical keys")
kfail = 0
for N in (5, 8, 12, 15, 20):
    F = Field(N); c = F.gen()
    for j in range(1, 3 * N):
        a = F.two_cos(j)
        b = c * F.two_cos(j - 1) - F.two_cos(j - 2)          # Chebyshev step in another association
        b2 = (F.two_cos(j) * F.two_cos(1) * 3) / (F.two_cos(1) * 3) if not F.two_cos(1).is_zero() else a
        if not (a.c == b.c == b2.c): kfail += 1
        # keys must coincide with equality
        if (mkey(((a,),)) == mkey(((b,),))) != (a == b): kfail += 1
# same mkey, different fields of equal degree (K_5 and K_8 / K_10 / K_12 are all degree 2): keys collide across fields
F5, F8, F10 = Field(5), Field(8), Field(10)
e5, e8, e10 = F5.gen(), F8.gen(), F10.gen()
print(f"  route-dependence failures: {kfail}")
print(f"  cross-field: mkey(c_5)==mkey(c_8): {mkey(((e5,),)) == mkey(((e8,),))}, numerically {float(e5):.4f} vs {float(e8):.4f}; c_5 == c_8 -> {e5 == e8}")
try:
    print("  c_5 + c_8 =", e5 + e8)
except TypeError as ex: print("  c_5 + c_8 raises TypeError (mixing is refused):", ex)
print("  embed(c_5 -> K_10) == two_cos(2) in K_10:", embed(e5, F10) == F10.two_cos(2), "; c_5 == embed(c_5) ->", e5 == embed(e5, F10), "(same number, compares False)")

print("(d) two_cos / sqrt5")
dfail = 0
for N in (5, 7, 9, 12, 16, 20, 30):
    F = Field(N)
    for j in range(N):
        if abs(num(F.two_cos(j)) - 2 * mpmath.cos(2 * mpmath.pi * j / N)) > mpmath.mpf(10) ** -30: dfail += 1
for N in (5, 10, 15, 20, 30, 60):
    s = Field(N).sqrt5()
    if s * s != 5 or s.sign() != 1: dfail += 1
print(f"  failures: {dfail}")

print("(e) sign() on tiny nonzero elements")
F = Field(60); c = F.gen()
# 2cos(2pi/60) - rational approximation: tiny but nonzero
for den in (10**6, 10**12, 10**20, 10**38, 10**45):
    mpmath.mp.dps = 200
    q = Fraction(int(mpmath.nint(mpmath.mpf(2) * mpmath.cos(2 * mpmath.pi / 60) * den)), den)
    e = c - q
    mpmath.mp.dps = 200; tv = 2*mpmath.cos(2*mpmath.pi/60) - mpmath.mpf(q.numerator)/q.denominator
    try: print(f"  den 1e{len(str(den))-1}: sign = {e.sign()}, true sign = {int(mpmath.sign(tv))} (|value| = {mpmath.nstr(abs(tv), 3)})")
    except ArithmeticError as ex: print(f"  den 1e{len(str(den))-1}: refused ({ex})")
