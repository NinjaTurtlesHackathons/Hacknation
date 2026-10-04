"""Exact arithmetic in the cyclotomic field Q(zeta_N), Python standard library only (trusted base: fractions.Fraction).

An element is stored as a vector of N rational coefficients c_k for zeta^k (k = 0..N-1), i.e. as an element of
Q[x]/(x^N - 1). Equality and hashing use the remainder modulo the cyclotomic polynomial Phi_N, which is the true
field Q(zeta_N) = Q[x]/(Phi_N). Complex conjugation is zeta^k -> zeta^(-k).
"""
from fractions import Fraction
from functools import lru_cache


def _polydiv(num, den):
    """Exact polynomial division of integer/rational coefficient lists (lowest degree first). Returns (quot, rem)."""
    num = [Fraction(c) for c in num]
    q = [Fraction(0)] * max(1, len(num) - len(den) + 1)
    while len(num) >= len(den) and any(num):
        shift = len(num) - len(den)
        f = num[-1] / den[-1]
        q[shift] = f
        for i, c in enumerate(den):
            num[i + shift] -= f * c
        while num and num[-1] == 0:
            num.pop()
    return q, num


@lru_cache(maxsize=None)
def cyclotomic(n):
    """Phi_n as a tuple of integer coefficients, lowest degree first, via x^n - 1 = prod_{d | n} Phi_d."""
    p = [-1] + [0] * (n - 1) + [1]
    for d in range(1, n):
        if n % d == 0:
            p, r = _polydiv(p, list(cyclotomic(d)))
            assert not any(r)
    assert all(c.denominator == 1 for c in p)
    return tuple(int(c) for c in p)


class Cyc:
    __slots__ = ("N", "c")

    def __init__(self, N, coeffs=None):
        self.N = N
        self.c = [Fraction(0)] * N if coeffs is None else [Fraction(x) for x in coeffs]

    @classmethod
    def const(cls, N, q):
        z = cls(N); z.c[0] = Fraction(q); return z

    @classmethod
    def zeta(cls, N, k=1):
        z = cls(N); z.c[k % N] = Fraction(1); return z

    def _lift(self, o):
        return o if isinstance(o, Cyc) else Cyc.const(self.N, o)

    def __add__(self, o):
        o = self._lift(o); return Cyc(self.N, [a + b for a, b in zip(self.c, o.c)])
    __radd__ = __add__

    def __neg__(self):
        return Cyc(self.N, [-a for a in self.c])

    def __sub__(self, o):
        return self + (-self._lift(o))

    def __rsub__(self, o):
        return self._lift(o) - self

    def __mul__(self, o):
        if not isinstance(o, Cyc):
            q = Fraction(o); return Cyc(self.N, [a * q for a in self.c])
        r = [Fraction(0)] * self.N
        for i, a in enumerate(self.c):
            if a:
                for j, b in enumerate(o.c):
                    if b:
                        r[(i + j) % self.N] += a * b
        return Cyc(self.N, r)
    __rmul__ = __mul__

    def __truediv__(self, q):
        assert not isinstance(q, Cyc), "division only by rationals is needed"
        q = Fraction(q); return Cyc(self.N, [a / q for a in self.c])

    def conj(self):
        r = [Fraction(0)] * self.N
        for k, a in enumerate(self.c):
            r[(-k) % self.N] += a
        return Cyc(self.N, r)

    def reduced(self):
        """Canonical form: remainder modulo Phi_N, padded to length deg Phi_N."""
        phi = cyclotomic(self.N)
        _, r = _polydiv(list(self.c), list(phi))
        while r and r[-1] == 0:
            r.pop()
        r = r + [Fraction(0)] * (len(phi) - 1 - len(r))
        return tuple(r)

    def __eq__(self, o):
        o = self._lift(o)
        assert o.N == self.N
        return self.reduced() == o.reduced()

    def __hash__(self):
        return hash(self.reduced())

    def is_zero(self):
        return not any(self.reduced())

    def rational(self):
        """The value as a Fraction if it lies in Q, else None."""
        r = self.reduced()
        return r[0] if not any(r[1:]) else None

    def __repr__(self):
        q = self.rational()
        if q is not None:
            return str(q)
        terms = [f"{a}*z^{k}" for k, a in enumerate(self.reduced()) if a]
        return f"({' + '.join(terms)}; N={self.N})"


# ---- matrices over Q(zeta_N) as lists of lists ----

def mat_mul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    N = A[0][0].N
    return [[sum((A[i][k] * B[k][j] for k in range(m)), Cyc(N)) for j in range(p)] for i in range(n)]


def mat_eq(A, B):
    return len(A) == len(B) and all(a == b for ra, rb in zip(A, B) for a, b in zip(ra, rb))


def mat_key(A):
    return tuple(tuple(x.reduced() for x in row) for row in A)


def identity(N, n):
    return [[Cyc.const(N, 1 if i == j else 0) for j in range(n)] for i in range(n)]


def from_ints(N, rows):
    return [[Cyc.const(N, x) if not isinstance(x, Cyc) else x for x in r] for r in rows]


def trace(A):
    return sum((A[i][i] for i in range(len(A))), Cyc(A[0][0].N))
