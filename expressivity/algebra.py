"""Exact algebra for the expressivity verifier: real cyclotomic fields, exact matrices, permutation groups.

Field: K_N = Q(c) with c = 2 cos(2 pi / N), elements stored as coefficient tuples (Fractions) modulo the minimal polynomial
Psi_N of c. K_N contains 2 cos(2 pi j / N) for every j (Chebyshev recursion), and K_5 contains sqrt 5 = 2 c + 1. Every number
is exact; the only floating-point step is the sign of a nonzero element, which is decided with mpmath at 60 digits and
re-checked at 120 digits (a nonzero algebraic number of bounded height cannot be that close to 0 in practice; the check
refuses if the two evaluations disagree or the value is below 1e-40).
"""
from fractions import Fraction
from functools import lru_cache
from math import gcd
import itertools

import mpmath


# ---------------------------------------------------------------- real cyclotomic fields

@lru_cache(maxsize=None)
def minpoly_2cos(N):
    """Integer coefficients (low -> high) of the minimal polynomial of 2 cos(2 pi / N) over Q.
    Built as prod over j coprime to N, 1 <= j <= N/2, of (x - 2 cos(2 pi j / N)) with exact integer rounding checked."""
    if N in (1, 2):
        return (-2, 1) if N == 1 else (2, 1)
    js = [j for j in range(1, N // 2 + 1) if gcd(j, N) == 1 and not (2 * j == N)]
    mpmath.mp.dps = 80
    coeffs = [mpmath.mpf(1)]
    for j in js:
        r = 2 * mpmath.cos(2 * mpmath.pi * j / N)
        new = [mpmath.mpf(0)] * (len(coeffs) + 1)
        for i, a in enumerate(coeffs):
            new[i + 1] += a
            new[i] -= a * r
        coeffs = new
    out = []
    for a in coeffs:
        n = int(mpmath.nint(a))
        if abs(a - n) > mpmath.mpf(10) ** -40:
            raise ArithmeticError("minimal polynomial not integral")
        out.append(n)
    return tuple(out)


class Field:
    """K_N = Q(2 cos(2 pi / N)). N = 1 gives Q."""

    def __init__(self, N=1):
        self.N = N
        self.poly = minpoly_2cos(N) if N > 2 else (0, 1)     # N <= 2: c = +-2, the field is Q
        self.deg = len(self.poly) - 1 if N > 2 else 1
        self._c_num = None

    def __eq__(self, other): return isinstance(other, Field) and other.N == self.N
    def __hash__(self): return hash(("Field", self.N))
    def __repr__(self): return f"K_{self.N}"

    def __call__(self, x):
        if isinstance(x, Elt):
            if x.F == self: return x
            if x.F.N == 1 or x.F.deg == 1: return Elt(self, (x.c[0],))
            return embed(x, self)
        return Elt(self, (Fraction(x),))

    @property
    def zero(self): return Elt(self, (Fraction(0),))
    @property
    def one(self): return Elt(self, (Fraction(1),))

    def gen(self):
        """c = 2 cos(2 pi / N)."""
        if self.deg == 1:                                  # N <= 4 or N = 6: c is rational, the root of x + a0
            return Elt(self, ({1: Fraction(2), 2: Fraction(-2)}.get(self.N, Fraction(-self.poly[0])),))
        return Elt(self, (Fraction(0), Fraction(1)))

    def two_cos(self, j):
        """2 cos(2 pi j / N) as an exact element (Chebyshev: C0 = 2, C1 = c, C_{n+1} = c C_n - C_{n-1})."""
        j = j % self.N
        c = self.gen(); a, b = self(2), c
        if j == 0: return a
        for _ in range(j - 1):
            a, b = b, c * b - a
        return b

    def sqrt5(self):
        if self.N % 5: raise ValueError("sqrt 5 needs N divisible by 5")
        # 2 cos(2 pi / 5) = (sqrt5 - 1) / 2  ->  sqrt5 = 2 * two_cos(N/5) + 1
        return self.two_cos(self.N // 5) * 2 + 1

    def numeric(self, e, dps=60):
        mpmath.mp.dps = dps
        c = 2 * mpmath.cos(2 * mpmath.pi / self.N) if self.N > 2 else None
        s = mpmath.mpf(0)
        for i, a in enumerate(e.c):
            s += mpmath.mpf(a.numerator) / a.denominator * (c ** i if i else 1)
        return s


def _polymod(c, poly):
    c = list(c)
    d = len(poly) - 1
    while len(c) > d:
        lead = c.pop()
        if lead:
            for i in range(d):
                c[len(c) - d + i] -= lead * poly[i]
    return c


class Elt:
    __slots__ = ("F", "c")

    def __init__(self, F, coeffs):
        self.F = F
        cs = [Fraction(x) for x in coeffs]
        if F.deg > 1: cs = _polymod(cs, F.poly)
        while len(cs) > 1 and cs[-1] == 0: cs.pop()
        if not cs: cs = [Fraction(0)]
        self.c = tuple(cs)

    def _co(self, o):
        if isinstance(o, Elt):
            if o.F == self.F: return o
            if o.F.deg == 1: return Elt(self.F, (o.c[0],))
            if self.F.deg == 1: return Elt(o.F, (self.c[0],))
            raise TypeError(f"field mismatch {self.F} vs {o.F}")
        return Elt(self.F, (Fraction(o),))

    def __add__(self, o):
        o = self._co(o); F = self.F if self.F.deg >= o.F.deg else o.F
        n = max(len(self.c), len(o.c))
        return Elt(F, [(self.c[i] if i < len(self.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(n)])
    __radd__ = __add__

    def __neg__(self): return Elt(self.F, [-a for a in self.c])
    def __sub__(self, o): return self + (-self._co(o))
    def __rsub__(self, o): return self._co(o) - self

    def __mul__(self, o):
        o = self._co(o); F = self.F if self.F.deg >= o.F.deg else o.F
        r = [Fraction(0)] * (len(self.c) + len(o.c) - 1)
        for i, a in enumerate(self.c):
            if a:
                for j, b in enumerate(o.c):
                    if b: r[i + j] += a * b
        return Elt(F, r)
    __rmul__ = __mul__

    def is_zero(self): return all(a == 0 for a in self.c)

    def inv(self):
        if self.is_zero(): raise ZeroDivisionError
        if self.F.deg == 1: return Elt(self.F, (1 / self.c[0],))
        # extended Euclid over Q[x] with the minimal polynomial
        a = [Fraction(x) for x in self.F.poly]; b = list(self.c)
        r0, r1 = a, b; s0, s1 = [Fraction(0)], [Fraction(1)]
        while not (len(r1) == 1 and r1[0] == 0) and len(r1) > 0:
            q, r = _pdivmod(r0, r1)
            r0, r1 = r1, r
            s0, s1 = s1, _psub(s0, _pmul(q, s1))
            if len(r1) == 1 and r1[0] == 0: break
        # r0 is a nonzero constant
        if len(r0) != 1: raise ArithmeticError("not invertible")
        return Elt(self.F, [x / r0[0] for x in s0])

    def __truediv__(self, o): return self * self._co(o).inv()
    def __rtruediv__(self, o): return self._co(o) * self.inv()

    def __eq__(self, o):
        try: return (self - o).is_zero()
        except TypeError: return False

    def __hash__(self):
        return hash(self.c) if len(self.c) > 1 else hash(self.c[0])

    def sign(self):
        if self.is_zero(): return 0
        if self.F.deg == 1: return 1 if self.c[0] > 0 else -1
        v1, v2 = self.F.numeric(self, 60), self.F.numeric(self, 120)
        if abs(v2) < mpmath.mpf(10) ** -40 or (v1 > 0) != (v2 > 0):
            raise ArithmeticError("sign undecidable at this precision")
        return 1 if v2 > 0 else -1

    def __float__(self): return float(self.F.numeric(self, 30))

    def __repr__(self):
        if self.F.deg == 1: return str(self.c[0])
        return "(" + " + ".join(f"{a}*c^{i}" for i, a in enumerate(self.c) if a) + f" in {self.F})"


def _ptrim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0: p.pop()
    return p or [Fraction(0)]


def _psub(a, b):
    n = max(len(a), len(b))
    return _ptrim([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)])


def _pmul(a, b):
    r = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] += x * y
    return _ptrim(r)


def _pdivmod(a, b):
    a = _ptrim(a); b = _ptrim(b)
    q = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    r = list(a)
    while len(r) >= len(b) and not (len(r) == 1 and r[0] == 0):
        f = r[-1] / b[-1]; s = len(r) - len(b); q[s] = f
        for i in range(len(b)): r[s + i] -= f * b[i]
        r = _ptrim(r[:-1]) if len(r) > 1 else [Fraction(0)]
        if len(r) < len(b): break
    return _ptrim(q), _ptrim(r)


def embed(x, F):
    """Embed x ∈ K_M into K_N for M | N via c_M = 2 cos(2 pi (N/M) / N)."""
    M = x.F.N
    if F.N % M: raise ValueError(f"cannot embed K_{M} into K_{F.N}")
    cM = F.two_cos(F.N // M)
    r = F.zero; p = F.one
    for a in x.c:
        r = r + p * a; p = p * cM
    return r


def common_field(*Ns):
    from math import lcm
    return Field(lcm(*[n for n in Ns if n] or [1]))


# ---------------------------------------------------------------- exact matrices (tuples of tuples of Elt)

def mat(F, rows):
    return tuple(tuple(F(x) for x in r) for r in rows)


def eye(F, n):
    return tuple(tuple(F.one if i == j else F.zero for j in range(n)) for i in range(n))


def mmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return tuple(tuple(sum((A[i][k] * B[k][j] for k in range(m)), A[0][0] * 0) for j in range(p)) for i in range(n))


def mvec(A, v):
    return tuple(sum((A[i][k] * v[k] for k in range(len(v))), A[0][0] * 0) for i in range(len(A)))


def msub(A, B):
    return tuple(tuple(a - b for a, b in zip(ra, rb)) for ra, rb in zip(A, B))


def madd(A, B):
    return tuple(tuple(a + b for a, b in zip(ra, rb)) for ra, rb in zip(A, B))


def mT(A):
    return tuple(tuple(A[i][j] for i in range(len(A))) for j in range(len(A[0])))


def mscale(A, s):
    return tuple(tuple(a * s for a in r) for r in A)


def mkey(A):
    return tuple(tuple(x.c for x in r) for r in A)


def rank(A):
    M = [list(r) for r in A]; n, m = len(M), len(M[0]); r = 0
    for col in range(m):
        piv = next((i for i in range(r, n) if not M[i][col].is_zero()), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        inv = M[r][col].inv()
        M[r] = [x * inv for x in M[r]]
        for i in range(n):
            if i != r and not M[i][col].is_zero():
                f = M[i][col]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == n: break
    return r


def det(A):
    M = [list(r) for r in A]; n = len(M); d = M[0][0] * 0 + 1
    for col in range(n):
        piv = next((i for i in range(col, n) if not M[i][col].is_zero()), None)
        if piv is None: return M[0][0] * 0
        if piv != col: M[col], M[piv] = M[piv], M[col]; d = -d
        d = d * M[col][col]; inv = M[col][col].inv()
        for i in range(col + 1, n):
            if not M[i][col].is_zero():
                f = M[i][col] * inv; M[i] = [a - f * b for a, b in zip(M[i], M[col])]
    return d


def is_pos_def(P):
    """Sylvester's criterion with exact leading principal minors (signs decided exactly in K_N)."""
    n = len(P)
    if mT(P) != P: return False
    return all(det(tuple(tuple(P[i][j] for j in range(k)) for i in range(k))).sign() > 0 for k in range(1, n + 1))


def kernel_basis(A):
    """Basis of {x : A x = 0} (exact)."""
    M = [list(r) for r in A]; n, m = len(M), len(M[0]); piv_cols = []; r = 0
    for col in range(m):
        piv = next((i for i in range(r, n) if not M[i][col].is_zero()), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = M[r][col].inv(); M[r] = [x * inv for x in M[r]]
        for i in range(n):
            if i != r and not M[i][col].is_zero():
                f = M[i][col]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv_cols.append(col); r += 1
        if r == n: break
    z = A[0][0] * 0; basis = []
    for free in (c for c in range(m) if c not in piv_cols):
        v = [z] * m; v[free] = z + 1
        for i, pc in enumerate(piv_cols): v[pc] = -M[i][free]
        basis.append(tuple(v))
    return basis


# ---------------------------------------------------------------- Householder (P-reflection) factorisation

def p_reflection(v, P):
    """R = I - 2 v v^T P / (v^T P v): the reflection across the P-orthogonal complement of v."""
    n = len(v); Pv = mvec(P, v); q = sum((v[i] * Pv[i] for i in range(n)), v[0] * 0)
    return tuple(tuple((v[0] * 0 + (1 if i == j else 0)) - v[i] * Pv[j] * 2 / q for j in range(n)) for i in range(n))


def cartan_dieudonne(M, P):
    """Factor a P-orthogonal matrix M into rank(M - I) P-reflections (exact). Returns the list of reflection vectors v_1..v_r
    with M = R(v_1) R(v_2) ... R(v_r). Algorithm: while M != I pick a basis vector x with M x != x, reflect with v = M x - x."""
    F0 = M[0][0]; n = len(M); I = eye_like(M); vs = []; cur = M
    for _ in range(n + 1):
        if cur == I: break
        x = next(tuple(F0 * 0 + (1 if i == j else 0) for i in range(n)) for j in range(n)
                 if mvec(cur, tuple(F0 * 0 + (1 if i == j else 0) for i in range(n))) != tuple(F0 * 0 + (1 if i == j else 0) for i in range(n)))
        v = tuple(a - b for a, b in zip(mvec(cur, x), x))
        R = p_reflection(v, P); cur = mmul(R, cur); vs.append(v)
    if cur != I: raise ArithmeticError("factorisation failed (matrix not P-orthogonal?)")
    return vs                      # R(v_r) ... R(v_1) M = I  =>  M = R(v_1) ... R(v_r)


def eye_like(M):
    z = M[0][0] * 0
    return tuple(tuple(z + (1 if i == j else 0) for j in range(len(M))) for i in range(len(M)))


# ---------------------------------------------------------------- permutation groups (elements = tuples of images)

def pmul(a, b):
    """(a * b)(i) = a(b(i)): apply b first, then a."""
    return tuple(a[i] for i in b)


def pinv(a):
    r = [0] * len(a)
    for i, x in enumerate(a): r[x] = i
    return tuple(r)


def pid(n): return tuple(range(n))


def closure(gens, n=None, cap=200000):
    n = n or len(gens[0]); e = pid(n); seen = {e}; frontier = [e]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = pmul(g, x)
                if y not in seen:
                    seen.add(y); nxt.append(y)
                    if len(seen) > cap: raise OverflowError("group too large")
        frontier = nxt
    return seen


def porder(a):
    e = pid(len(a)); x = a; k = 1
    while x != e: x = pmul(a, x); k += 1
    return k


def cycle_type(a):
    seen = set(); out = []
    for i in range(len(a)):
        if i in seen: continue
        L = 0; j = i
        while j not in seen: seen.add(j); j = a[j]; L += 1
        out.append(L)
    return tuple(sorted(out, reverse=True))


def from_cycles(n, *cycles):
    p = list(range(n))
    for cyc in cycles:
        for i, x in enumerate(cyc): p[x] = cyc[(i + 1) % len(cyc)]
    return tuple(p)


class PermGroup:
    """A finite group given by permutation generators; elements enumerated."""

    def __init__(self, name, gens, n=None):
        self.name = name; self.gens = [tuple(g) for g in gens]; self.n = n or len(self.gens[0])
        self.elements = sorted(closure(self.gens, self.n)); self.order = len(self.elements)
        self.e = pid(self.n); self._index = {g: i for i, g in enumerate(self.elements)}
        self._classes = None

    def __contains__(self, g): return tuple(g) in self._index

    def mul(self, a, b): return pmul(a, b)
    def inv(self, a): return pinv(a)

    def classes(self):
        if self._classes is None:
            left = set(self.elements); cl = []
            for g in self.elements:
                if g not in left: continue
                c = {pmul(pmul(x, g), pinv(x)) for x in self.elements}
                cl.append(sorted(c)); left -= c
            cl.sort(key=lambda c: (porder(c[0]), len(c), c[0]))
            self._classes = cl
        return self._classes

    def class_of(self, g):
        for i, c in enumerate(self.classes()):
            if g in c: return i
        raise KeyError(g)

    def is_abelian(self):
        return all(pmul(a, b) == pmul(b, a) for a in self.gens for b in self.gens)

    def exponent(self):
        from math import lcm
        return lcm(*[porder(g) for g in self.elements])

    def center(self):
        return [z for z in self.elements if all(pmul(z, g) == pmul(g, z) for g in self.gens)]

    def derived_subgroup(self, H=None):
        H = H or self.elements
        comms = {pmul(pmul(a, b), pmul(pinv(a), pinv(b))) for a in H for b in H}
        return sorted(closure(list(comms) or [self.e], self.n)) if comms else [self.e]

    def derived_series(self):
        series = [self.elements]
        while True:
            D = self.derived_subgroup(series[-1])
            if len(D) == len(series[-1]): break
            series.append(D)
            if len(D) == 1: break
        return [len(x) for x in series]

    def is_solvable(self):
        return self.derived_series()[-1] == 1

    def is_perfect(self):
        return len(self.derived_subgroup()) == self.order
