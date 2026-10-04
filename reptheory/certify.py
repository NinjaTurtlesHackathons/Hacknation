"""Verifier for the representation-theory paper (verifier first, see docs/FRAMEWORK.md of the lab framework).

Every computer-checked statement of the paper is a function here that recomputes it from scratch in exact arithmetic
(fractions.Fraction and cyclo.Cyc; no floating point anywhere). The self-test runs known-true AND known-false statements
first; if any of them is judged wrongly, nothing is written and the exit code is 1.

    python reptheory/certify.py        # self-test, all certificates, writes reptheory/out/{claims,gates}.csv, tables.json
"""
import csv
import datetime as dt
import itertools
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyclo import Cyc, from_ints, identity, mat_eq, mat_key, mat_mul, trace  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# ------------------------------------------------------------------ groups

class Group:
    """Finite group given by generators and a multiplication; elements are hashable keys."""

    def __init__(self, name, gens, mul, e, N=1, key=lambda x: x):
        self.name, self.gens, self.mul, self.e, self.N, self.key = name, gens, mul, e, N, key
        # closure (breadth first), remembering for every element a word g = s * h with h found earlier
        self.elements, self.parent = [e], {key(e): None}
        frontier = [e]
        while frontier:
            new = []
            for h in frontier:
                for i, s in enumerate(gens):
                    g = mul(s, h)
                    if key(g) not in self.parent:
                        self.parent[key(g)] = (i, h)
                        self.elements.append(g); new.append(g)
            frontier = new
        self.idx = {key(g): i for i, g in enumerate(self.elements)}
        n = len(self.elements)
        self.table = [[self.idx[key(mul(a, b))] for b in self.elements] for a in self.elements]
        self.eidx = self.idx[key(e)]
        self.inv = [next(j for j in range(n) if self.table[i][j] == self.eidx) for i in range(n)]
        self.classes = self._classes()

    def __len__(self):
        return len(self.elements)

    def _classes(self):
        n, seen, cls = len(self), set(), []
        for i in range(n):
            if i in seen:
                continue
            c = sorted({self.table[self.table[g][i]][self.inv[g]] for g in range(n)})
            seen.update(c); cls.append(c)
        return cls

    def order(self, i):
        k, j = 1, i
        while j != self.eidx:
            j = self.table[j][i]; k += 1
        return k

    def centralizer_size(self, i):
        return sum(1 for g in range(len(self)) if self.table[g][i] == self.table[i][g])


def perm_mul(a, b):  # (a*b)(x) = a(b(x)): apply b first
    return tuple(a[b[x]] for x in range(len(a)))


def perm_group(name, gens, N=1):
    return Group(name, [tuple(g) for g in gens], perm_mul, tuple(range(len(gens[0]))), N=N)


def cyclic(n):
    return perm_group(f"C{n}", [[(x + 1) % n for x in range(n)]] if n > 1 else [[0]], N=n)


def S3(): return perm_group("S3", [[1, 0, 2], [1, 2, 0]])
def D4(): return perm_group("D4", [[1, 2, 3, 0], [0, 3, 2, 1]])           # rotation r, reflection s of a square
def V4(): return perm_group("V4", [[1, 0, 3, 2], [2, 3, 0, 1]])
def A4(): return perm_group("A4", [[1, 2, 0, 3], [1, 0, 3, 2]], N=3)
def S4(): return perm_group("S4", [[1, 0, 2, 3], [1, 2, 3, 0]])


def Q8():
    N = 4
    z = Cyc.zeta(N)
    i = [[z, Cyc.const(N, 0)], [Cyc.const(N, 0), z.conj()]]
    j = from_ints(N, [[0, 1], [-1, 0]])
    return Group("Q8", [i, j], mat_mul, identity(N, 2), N=N, key=mat_key)


# ------------------------------------------------------------------ representations

class Rep:
    def __init__(self, name, G, mats):
        self.name, self.G, self.mats = name, G, mats       # mats[i] = rho(elements[i])
        self.dim = len(mats[0])
        self.chi = [trace(m) for m in mats]


def rep_from_generators(name, G, images):
    """Extend generator images along the words found by the closure. Whether this is a homomorphism is NOT assumed;
    it is checked separately by is_homomorphism (a wrong set of images fails there)."""
    mats = {}
    d = len(images[0])
    for g in G.elements:
        k = G.key(g)
        if G.parent[k] is None:
            mats[k] = identity(images[0][0][0].N, d)
        else:
            s, h = G.parent[k]
            mats[k] = mat_mul(images[s], mats[G.key(h)])
    return Rep(name, G, [mats[G.key(g)] for g in G.elements])


def rep_from_function(name, G, f):
    return Rep(name, G, [f(g) for g in G.elements])


def is_homomorphism(R):
    G = R.G
    n = len(G)
    for a in range(n):
        for b in range(n):
            if not mat_eq(mat_mul(R.mats[a], R.mats[b]), R.mats[G.table[a][b]]):
                return False, f"rho({a})rho({b}) != rho({a}*{b})"
    return True, f"rho(gh)=rho(g)rho(h) for all {n*n} pairs"


def sign(p):
    s, seen = 1, set()
    for i in range(len(p)):
        if i in seen:
            continue
        j, L = i, 0
        while j not in seen:
            seen.add(j); j = p[j]; L += 1
        s *= (-1) ** (L - 1)
    return s


def permmat(N, p):
    n = len(p)
    return from_ints(N, [[1 if p[c] == r else 0 for c in range(n)] for r in range(n)])  # e_c -> e_{p(c)}


def stdmat(N, p):
    """Standard representation on {x : sum x = 0}, basis f_i = e_i - e_{n-1}, i < n-1."""
    n = len(p); m = n - 1
    M = [[0] * m for _ in range(m)]
    for i in range(m):
        if p[i] != m: M[p[i]][i] += 1
        if p[m] != m: M[p[m]][i] -= 1
    return from_ints(N, M)


def scal(N, x):
    return [[x if isinstance(x, Cyc) else Cyc.const(N, x)]]


PAIRINGS = [frozenset({frozenset({0, 1}), frozenset({2, 3})}), frozenset({frozenset({0, 2}), frozenset({1, 3})}),
            frozenset({frozenset({0, 3}), frozenset({1, 2})})]


def s4_to_s3(p):
    img = [frozenset(frozenset(p[x] for x in pair) for pair in P) for P in PAIRINGS]
    return tuple(PAIRINGS.index(Q) for Q in img)


def reps_of(G):
    """The claimed complete lists of irreducible representations (these are the 'claims'; the certificates judge them)."""
    N, nm = G.N, G.name
    if nm.startswith("C"):
        n = len(G)
        return [rep_from_function(f"chi_{j}", G, lambda g, j=j: scal(N, Cyc.zeta(N, j * g[0]))) for j in range(n)]
    if nm == "S3":
        return [rep_from_function("trivial", G, lambda g: scal(N, 1)), rep_from_function("sign", G, lambda g: scal(N, sign(g))),
                rep_from_function("standard", G, lambda g: stdmat(N, g))]
    if nm == "D4":
        out = [rep_from_generators(f"({a:+d},{b:+d})", G, [scal(N, a), scal(N, b)]) for a in (1, -1) for b in (1, -1)]
        return out + [rep_from_generators("rotation", G, [from_ints(N, [[0, -1], [1, 0]]), from_ints(N, [[1, 0], [0, -1]])])]
    if nm == "Q8":
        out = [rep_from_generators(f"({a:+d},{b:+d})", G, [scal(N, a), scal(N, b)]) for a in (1, -1) for b in (1, -1)]
        return out + [rep_from_function("quaternion", G, lambda g: g)]
    if nm == "A4":
        w = Cyc.zeta(3)
        out = [rep_from_generators(f"omega^{j}", G, [scal(N, [Cyc.const(N, 1), w, w * w][j]), scal(N, 1)])
               for j in range(3)]
        return out + [rep_from_function("standard", G, lambda g: stdmat(N, g))]
    if nm == "S4":
        return [rep_from_function("trivial", G, lambda g: scal(N, 1)), rep_from_function("sign", G, lambda g: scal(N, sign(g))),
                rep_from_function("2-dim (via S4->S3)", G, lambda g: stdmat(N, s4_to_s3(g))),
                rep_from_function("standard", G, lambda g: stdmat(N, g)),
                rep_from_function("standard x sign", G, lambda g: [[x * sign(g) for x in r] for r in stdmat(N, g)])]
    raise KeyError(nm)


# ------------------------------------------------------------------ character computations

def inner(G, chi, psi):
    """<chi, psi> = 1/|G| sum_g chi(g) conj(psi(g))."""
    return sum((chi[g] * psi[g].conj() for g in range(len(G))), Cyc(G.N)) / len(G)


def is_class_function(G, chi):
    return all(chi[i] == chi[c[0]] for c in G.classes for i in c)


def char_table(G, R):
    return [[r.chi[c[0]] for c in G.classes] for r in R]


# ------------------------------------------------------------------ certificates (each returns (passed, reason, data))

def cert_character_table(G, R):
    """Certificate for 'R is a complete list of pairwise non-isomorphic irreducible representations of G'.
    Chain: homomorphisms (exact) -> <chi_i,chi_j> = delta_ij (Cor. 2: irreducible, pairwise non-isomorphic)
    -> sum dim^2 = |G| (Prop. 3: no irreducible missing) -> #irreps = #classes (Thm. 4, consistency)
    -> column orthogonality (Thm. 5, consistency) -> chi_reg = sum d_i chi_i (Prop. 3, consistency)."""
    n = len(G)
    for r in R:
        ok, why = is_homomorphism(r)
        if not ok:
            return False, f"{r.name}: not a homomorphism ({why})", None
        if not is_class_function(G, r.chi):
            return False, f"{r.name}: character not a class function", None
    for a, b in itertools.product(range(len(R)), repeat=2):
        v = inner(G, R[a].chi, R[b].chi)
        if not v == (1 if a == b else 0):
            return False, f"<chi_{R[a].name}, chi_{R[b].name}> = {v}, expected {int(a == b)}", None
    s = sum(r.dim ** 2 for r in R)
    if s != n:
        return False, f"sum of squared dimensions = {s} != |G| = {n} (list incomplete)", None
    if len(R) != len(G.classes):
        return False, f"{len(R)} irreducibles but {len(G.classes)} classes", None
    for a, b in itertools.product(range(len(G.classes)), repeat=2):
        ga, gb = G.classes[a][0], G.classes[b][0]
        v = sum((r.chi[ga] * r.chi[gb].conj() for r in R), Cyc(G.N))
        if not v == (G.centralizer_size(ga) if a == b else 0):
            return False, f"column orthogonality fails at classes {a},{b}", None
    for g in range(n):
        if not sum((r.chi[g] * r.dim for r in R), Cyc(G.N)) == (n if g == G.eidx else 0):
            return False, "sum d_i chi_i != chi_reg", None
    data = {"group": G.name, "order": n,
            "class_reps_order": [G.order(c[0]) for c in G.classes], "class_sizes": [len(c) for c in G.classes],
            "centralizers": [G.centralizer_size(c[0]) for c in G.classes],
            "irreps": [{"name": r.name, "dim": r.dim, "values": [repr(x) for x in row]}
                       for r, row in zip(R, char_table(G, R))]}
    return True, (f"{len(R)} homomorphisms checked on all {n*n} pairs; Gram matrix = identity; sum d^2 = {n} = |G|; "
                  f"{len(R)} = #classes; column orthogonality; chi_reg = sum d_i chi_i"), data


def nullity_Q(rows, ncols):
    """dim of {x in Q^ncols : rows x = 0}, Gaussian elimination over Fraction."""
    A = [[Fraction(x) for x in r] for r in rows]
    rank, col = 0, 0
    while rank < len(A) and col < ncols:
        piv = next((i for i in range(rank, len(A)) if A[i][col] != 0), None)
        if piv is None:
            col += 1; continue
        A[rank], A[piv] = A[piv], A[rank]
        for i in range(len(A)):
            if i != rank and A[i][col] != 0:
                f = A[i][col] / A[rank][col]
                A[i] = [x - f * y for x, y in zip(A[i], A[rank])]
        rank += 1; col += 1
    return ncols - rank


def dim_hom_G(V, W):
    """dim Hom_G(V, W) by linear algebra: X (dim W x dim V) with rho_W(s) X = X rho_V(s) for the generators s.
    Only for representations with rational matrices (N = 1). Independent of characters."""
    G = V.G
    m, n = W.dim, V.dim
    gens = [G.idx[G.key(s)] for s in G.gens]
    rows = []
    for s in gens:
        A, B = W.mats[s], V.mats[s]
        for i in range(m):
            for j in range(n):
                row = [Fraction(0)] * (m * n)               # unknown X[k][l] at position k*n + l
                for k in range(m):                          # (A X)_{ij} = sum_k A_ik X_kj
                    row[k * n + j] += A[i][k].rational()
                for l in range(n):                          # (X B)_{ij} = sum_l X_il B_lj
                    row[i * n + l] -= B[l][j].rational()
                rows.append(row)
    return nullity_Q(rows, m * n)


def cert_orthogonality_vs_linear_algebra(G, R):
    """Theorem 3 checked independently: <chi_W, chi_V> (characters) == dim Hom_G(V, W) (Gaussian elimination)."""
    pairs = []
    for V in R:
        for W in R:
            a = inner(G, W.chi, V.chi).rational()
            b = dim_hom_G(V, W)
            pairs.append((V.name, W.name, str(a), b))
            if a is None or a != b:
                return False, f"<chi_{W.name}, chi_{V.name}> = {a} but dim Hom_G = {b}", pairs
    return True, f"{len(pairs)} ordered pairs, all equal", pairs


def orbits(G, npts):
    parent = list(range(npts))
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for g in G.elements:
        for x in range(npts):
            a, b = find(x), find(g[x])
            if a != b: parent[a] = b
    return len({find(x) for x in range(npts)})


def cert_fixed_points(G, claimed=None):
    """Lemma 2: dim V^G = 1/|G| sum chi(g), for the permutation representation (dim V^G = #orbits, counted combinatorially)."""
    npts = len(G.e)
    avg = sum(Fraction(sum(1 for x in range(npts) if g[x] == x)) for g in G.elements) / len(G)
    orb = orbits(G, npts) if claimed is None else claimed
    ok = avg == orb
    return ok, f"1/|G| sum chi_perm(g) = {avg}, number of orbits = {orb}", {"average": str(avg), "orbits": orb}


def cert_maschke_example():
    """Theorem 1 (proof by averaging) on an example: S3 on Q^3, start from the NON-invariant projection E onto
    span(1,1,1) along span(e1, e2); its average P must be an invariant idempotent with image span(1,1,1) and
    kernel {sum x = 0}."""
    G = S3(); N = 1
    P_g = [permmat(N, g) for g in G.elements]
    E = from_ints(N, [[0, 0, 1], [0, 0, 1], [0, 0, 1]])
    invariant_E = all(mat_eq(mat_mul(M, E), mat_mul(E, M)) for M in P_g)
    acc = from_ints(N, [[0] * 3 for _ in range(3)])
    for i, M in enumerate(P_g):
        T = mat_mul(mat_mul(M, E), P_g[G.inv[i]])
        acc = [[a + b for a, b in zip(r, s)] for r, s in zip(acc, T)]
    P = [[x / len(G) for x in r] for r in acc]
    checks = {
        "E is not G-equivariant": not invariant_E,
        "P^2 = P": mat_eq(mat_mul(P, P), P),
        "P rho(g) = rho(g) P for all g": all(mat_eq(mat_mul(M, P), mat_mul(P, M)) for M in P_g),
        "P(1,1,1) = (1,1,1)": mat_eq(mat_mul(P, from_ints(N, [[1], [1], [1]])), from_ints(N, [[1], [1], [1]])),
        "P kills (1,-1,0) and (0,1,-1)": all(all(x[0].is_zero() for x in mat_mul(P, from_ints(N, v)))
                                             for v in ([[1], [-1], [0]], [[0], [1], [-1]])),
    }
    return all(checks.values()), "; ".join(f"{k}: {v}" for k, v in checks.items()), {"P": [[repr(x) for x in r] for r in P]}


def table_equivalent(G1, R1, G2, R2):
    """Are the character tables equal up to a bijection of classes (respecting class sizes) and of irreducibles?"""
    T1, T2 = char_table(G1, R1), char_table(G2, R2)
    if len(T1) != len(T2) or G1.N != G2.N:
        return False
    s1, s2 = [len(c) for c in G1.classes], [len(c) for c in G2.classes]
    k = len(s1)
    for cp in itertools.permutations(range(k)):
        if any(s1[i] != s2[cp[i]] for i in range(k)):
            continue
        A = sorted(tuple(x.reduced() for x in r) for r in T1)
        B = sorted(tuple(r[cp[i]].reduced() for i in range(k)) for r in T2)
        if A == B:
            return True
    return False


def cert_same_table_not_isomorphic():
    """Example 8: D4 and Q8 have equal character tables, but are not isomorphic (5 vs 1 elements of order 2)."""
    G1, G2 = D4(), Q8()
    # D4 lives over Q; embed its table into Q(zeta_4) for the comparison
    R1 = [Rep(r.name, G1, [[[Cyc(4, [x.rational(), 0, 0, 0]) for x in row] for row in M] for M in r.mats]) for r in reps_of(G1)]
    G1.N = 4
    same = table_equivalent(G1, R1, G2, reps_of(G2))
    G1.N = 1
    inv1 = sum(1 for i in range(len(G1)) if G1.order(i) == 2)
    inv2 = sum(1 for i in range(len(G2)) if G2.order(i) == 2)
    ok = same and inv1 != inv2
    return ok, f"tables equivalent: {same}; elements of order 2: D4 {inv1}, Q8 {inv2}", {"order2_D4": inv1, "order2_Q8": inv2}


def cert_C4_vs_V4():
    """Contrast (used as a known-false statement in the self-test): C4 and V4 do NOT have equal character tables."""
    G1, G2 = cyclic(4), V4()
    R2 = [rep_from_generators(f"({a:+d},{b:+d})", G2, [scal(1, a), scal(1, b)]) for a in (1, -1) for b in (1, -1)]
    R2 = [Rep(r.name, G2, [[[Cyc(4, [x.rational(), 0, 0, 0]) for x in row] for row in M] for M in r.mats]) for r in R2]
    G2.N = 4
    return table_equivalent(G1, reps_of(G1), G2, R2)


# ------------------------------------------------------------------ self-test: known-true and known-false statements

def selftest():
    cases = []
    G = S3()
    R = reps_of(G)
    cases.append(("S3: {trivial, sign, standard} is the full list of irreducibles", cert_character_table(G, R)[0], True))
    bad = [R[0], R[1], rep_from_function("permutation", G, lambda g: permmat(1, g))]
    cases.append(("S3: {trivial, sign, permutation} is the full list (permutation rep is reducible)",
                  cert_character_table(G, bad)[0], False))
    G4 = S4(); R4 = reps_of(G4)
    cases.append(("S4: list without the 2-dimensional irreducible is complete (sum d^2 = 20)",
                  cert_character_table(G4, [r for r in R4 if r.dim != 2])[0], False))
    GD = D4()
    wrong = [rep_from_generators("fake", GD, [from_ints(1, [[0, 1], [1, 0]]), from_ints(1, [[1, 0], [0, -1]])])]
    cases.append(("D4: r -> [[0,1],[1,0]], s -> diag(1,-1) defines a representation", is_homomorphism(wrong[0])[0], False))
    C = cyclic(4)
    fake = rep_from_generators("zeta8", C, [scal(8, Cyc.zeta(8))])
    cases.append(("C4: generator -> zeta_8 defines a representation", is_homomorphism(fake)[0], False))
    cases.append(("C4: generator -> zeta_4 defines a representation",
                  is_homomorphism(rep_from_generators("zeta4", C, [scal(4, Cyc.zeta(4))]))[0], True))
    cases.append(("S4 acting on 4 points has 2 orbits (dim V^G = 2)", cert_fixed_points(G4, claimed=2)[0], False))
    cases.append(("S4 acting on 4 points: dim V^G = 1", cert_fixed_points(G4)[0], True))
    cases.append(("C4 and V4 have equal character tables", cert_C4_vs_V4(), False))
    cases.append(("D4 and Q8 have equal character tables but are not isomorphic", cert_same_table_not_isomorphic()[0], True))
    # arithmetic anchors of the trusted base
    w = Cyc.zeta(3)
    cases.append(("1 + omega + omega^2 = 0 in Q(zeta_3)", (1 + w + w * w).is_zero(), True))
    cases.append(("1 + omega = 0 in Q(zeta_3)", (1 + w).is_zero(), False))
    cases.append(("1 + i + i^2 + i^3 = 0 (regression: canonical form of an unreduced zero)", Cyc(4, [1, 1, 1, 1]) == 0, True))
    i4 = Cyc.zeta(4)
    cases.append(("i * conj(i) = 1", i4 * i4.conj() == 1, True))
    cases.append(("i^2 = 1", i4 * i4 == 1, False))
    wrong_ok = [(name, got, exp) for name, got, exp in cases if got != exp]
    n_true = sum(1 for c in cases if c[2]); n_false = len(cases) - n_true
    return not wrong_ok, cases, n_true, n_false, wrong_ok


# ------------------------------------------------------------------ main: claims table

# General theorems: full proofs in theorems.txt (level proved_text = human-readable proof, not machine-checked).
# The last field names the computed certificates that test the statement on concrete groups ("TABLES" = all
# character-table certificates). Status "proved" = text proof; it becomes REFUTED if a linked certificate fails.
TEXT_CLAIMS = [
    ("L-1", "Linear algebra: tr of an idempotent = rank; tr(f -> AfB) = trA trB; A^m = I => tr A^-1 = conj tr A.", ""),
    ("P-1", "Basic properties of characters (degree, class function, chi(g^-1) = conj chi(g), sums, Hom).", "TABLES"),
    ("T-1", "Maschke: every invariant subspace has an invariant complement; complete reducibility.", "E-M"),
    ("T-2", "Schur: G-maps between irreducibles are 0 or isomorphisms; endomorphisms are scalars.", "E-T3-"),
    ("C-1", "Irreducible representations of abelian groups have degree 1.", "E-C"),
    ("L-2", "dim V^G = 1/|G| sum chi_V(g).", "E-L2-"),
    ("T-3", "dim Hom_G(V, W) = <chi_W, chi_V>.", "E-T3-"),
    ("C-2", "Orthonormality of irreducible characters, multiplicities, irreducibility criterion <chi,chi> = 1.", "TABLES"),
    ("P-2", "Regular representation: each irreducible occurs dim V times; sum dim^2 = |G|.", "TABLES"),
    ("T-4", "Irreducible characters form an orthonormal basis of class functions; #irreducibles = #classes.", "TABLES"),
    ("L-3", "|K| |C_G(g)| = |G| for the conjugacy class K of g.", ""),
    ("T-5", "Column orthogonality: sum_i chi_i(g) conj chi_i(g') = |C_G(g)| delta_{g ~ g'}.", "TABLES"),
    ("P-3", "Irreducible representations of C_n are chi_j(c^k) = zeta^(jk), j = 0..n-1.", "E-C"),
]

def main():
    os.makedirs(OUT, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    gates, claims, tables = [], [], {}

    ok, cases, nt, nf, wrong = selftest()
    gates.append(("G0_selftest", ok, f"{nt} true + {nf} false statements, {len(wrong)} misjudged" +
                  (f": {wrong}" if wrong else ""), ts))
    for name, got, exp in cases:
        print(f"  selftest  {'OK ' if got == exp else 'BAD'}  expected {str(exp):5}  {name}")
    if not ok:
        print("SELF-TEST FAILED: verifier is not trusted, nothing written.")
        write(gates, claims, tables)
        sys.exit(1)

    def add(cid, text, level, res, evidence):
        passed, reason = res[0], res[1]
        claims.append((cid, text, level, evidence, "verified" if passed else "REFUTED", reason))
        print(f"  {cid:6} {'PASS' if passed else 'FAIL'}  {reason[:110]}")
        return res

    groups = [cyclic(n) for n in range(1, 9)] + [S3(), D4(), Q8(), A4(), S4()]
    for G in groups:
        res = cert_character_table(G, reps_of(G))
        tables[G.name] = res[2]
        add(f"E-{G.name}", f"The listed representations form a complete set of pairwise non-isomorphic irreducible "
                           f"representations of {G.name}; its character table is Table ({G.name}).",
            "computed_rigorous", res, "certify.cert_character_table")
    for G in (S3(), S4()):
        res = add(f"E-T3-{G.name}", f"For all pairs of irreducible representations V, W of {G.name}: "
                                    f"<chi_W, chi_V> = dim Hom_G(V, W) (dimension by Gaussian elimination).",
                  "computed_rigorous", cert_orthogonality_vs_linear_algebra(G, reps_of(G) + [
                      rep_from_function("permutation", G, lambda g: permmat(1, g))]), "certify.cert_orthogonality_vs_linear_algebra")
        tables[f"homdims_{G.name}"] = res[2]
    S3on5 = perm_group("S3 on {0..4}", [[1, 0, 2, 3, 4], [1, 2, 0, 3, 4]])
    for G in (S3(), D4(), A4(), S4(), S3on5):
        add(f"E-L2-{G.name.split()[0] + ('x' if ' ' in G.name else '')}",
            f"For the permutation representation of {G.name}: 1/|G| sum chi(g) = number of orbits = dim V^G.",
            "computed_rigorous", cert_fixed_points(G), "certify.cert_fixed_points")
    res = add("E-M", "Averaging the non-invariant projection E of Q^3 onto span(1,1,1) over S3 yields an S3-invariant "
                     "projection with kernel {x : x1+x2+x3 = 0}.", "computed_rigorous", cert_maschke_example(),
              "certify.cert_maschke_example")
    tables["maschke_P"] = res[2]
    res = add("E-DQ", "D4 and Q8 have the same character table but are not isomorphic.", "computed_rigorous",
              cert_same_table_not_isomorphic(), "certify.cert_same_table_not_isomorphic")
    gates.append(("G1_all_certificates", all(c[4] == "verified" for c in claims),
                  f"{sum(c[4] == 'verified' for c in claims)}/{len(claims)} computer-checked claims verified", ts))
    for cid, text, prefix in TEXT_CLAIMS:
        tables_ids = {"E-" + G.name for G in groups}
        ev = [c[0] for c in claims if (c[0] in tables_ids if prefix == "TABLES" else prefix and c[0].startswith(prefix))]
        claims.append((cid, text, "proved_text", "theorems.txt" + (" + " + " ".join(ev) if ev else ""),
                       "proved" if all(c[4] == "verified" for c in claims if c[0] in ev) else "REFUTED",
                       "proof in theorems.txt" + (f"; checked on {len(ev)} certificates" if ev else "")))
    write(gates, claims, tables)
    if not all(g[1] for g in gates):
        sys.exit(1)


def write(gates, claims, tables):
    with open(os.path.join(OUT, "gates.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["gate", "passed", "reason", "ts"]); w.writerows(gates)
    with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["claim_id", "text", "level", "evidence", "status", "reason"]); w.writerows(claims)
    with open(os.path.join(OUT, "tables.json"), "w") as f:
        json.dump(tables, f, indent=1)


if __name__ == "__main__":
    main()
