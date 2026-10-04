"""Red-team test of Lemma L2 (compression lemma): run the construction of the hand proof, exactly over Q, on explicit
finite-state one-layer realisations that stress the proof (singular transitions, affine input terms, matrix-valued states,
a token-dependent readout) and check every intermediate claim: psi well defined and onto G, eTe a group, Gamma' onto G,
lambda' a faithful homomorphism on the column space C, rank(lambda'(x_s) - I_C) <= rank(A(s) - I).
Run: python3 -m expressivity.analysis.redteam.t12_compression (from the repo root) or directly with python3.
"""
import itertools
import sympy as sp

# ---------------------------------------------------------------- groups as permutation tuples
def pmul(p, q):  # (p q)(i) = p(q(i)): apply q first
    return tuple(p[q[i]] for i in range(len(q)))


def pmat(p):
    n = len(p)
    return sp.Matrix(n, n, lambda i, j: 1 if p[j] == i else 0)


def key(M):
    return tuple(M)  # hashable, exact (entries are sympy Rationals)


def explore(A, B, h0, letters, gmul, gid):
    """BFS over (state, group element). Returns reachable states Q (incl. h0) and the readout table state -> g
    (None if the readout is inconsistent, i.e. the realisation is invalid)."""
    start = (key(h0), gid)
    states = {key(h0): h0}
    seen = {start}
    frontier = [(h0, gid)]
    read = {}
    ok = True
    while frontier:
        nxt = []
        for h, g in frontier:
            for s in letters:
                h2 = A[s] * h + B[s]
                g2 = gmul(s, g)
                k2 = key(h2)
                if k2 in read and read[k2] != g2:
                    ok = False
                read[k2] = g2
                if (k2, g2) not in seen:
                    seen.add((k2, g2)); states[k2] = h2; nxt.append((h2, g2))
        frontier = nxt
        if len(states) > 5000:
            raise RuntimeError("not finite-state (more than 5000 states)")
    return states, (read if ok else None)


def l2_construction(name, A, B, h0, letters, gmul, gid, gelems):
    print(f"\n=== {name} ===")
    Qd, read = explore(A, B, h0, letters, gmul, gid)
    assert read is not None, "readout inconsistent: not a realisation"
    Qk = list(Qd.keys()); idx = {k: i for i, k in enumerate(Qk)}; n = len(Qk)
    print(f"|Q| = {n}, ranks rank(A(s)-I): " + ", ".join(f"{s}:{(A[s]-sp.eye(A[s].shape[0])).rank()}" for s in letters))
    # letter maps on Q
    amap = {s: tuple(idx[key(A[s] * Qd[k] + B[s])] for k in Qk) for s in letters}
    # transformation monoid T with a representing word for each element (word = list of letters, applied left to right)
    ident = tuple(range(n))
    T = {ident: []}
    fr = [ident]
    while fr:
        nf = []
        for t in fr:
            for s in letters:
                t2 = tuple(amap[s][t[i]] for i in range(n))  # first t, then s
                if t2 not in T:
                    T[t2] = T[t] + [s]; nf.append(t2)
        fr = nf
    print(f"|T| = {len(T)}")
    comp = lambda a, b: tuple(a[b[i]] for i in range(n))  # a after b
    h0i = idx[key(h0)]

    def g_of(word):
        g = gid
        for s in word: g = gmul(s, g)
        return g
    # psi well defined: elements are distinct maps, so check psi(t) = readout of t(h0) for nonempty words and
    # homomorphism property psi(a b) = psi(a) psi(b)
    psi = {t: g_of(w) for t, w in T.items()}
    for t, w in T.items():
        if w: assert read[Qk[t[h0i]]] == psi[t], "psi disagrees with readout"
    for a in T:
        for b in T:
            assert psi[comp(a, b)] == gmul(psi[a], psi[b]), "psi not a homomorphism"
    assert set(psi.values()) == set(gelems), "psi not onto G"
    # minimal ideal: K = T k T for k of minimal image size
    k = min(T, key=lambda t: len(set(t)))
    K = {comp(comp(a, k), b) for a in T for b in T}
    e = next(t for t in K if comp(t, t) == t)
    Gam = {comp(comp(e, t), e) for t in T}
    # group check
    for a in Gam:
        assert comp(a, e) == a == comp(e, a)
        assert any(comp(a, b) == e for b in Gam), "eTe not a group"
    print(f"|K| = {len(K)}, |eTe| = {len(Gam)}, rank(e) = {len(set(e))}, psi(e) = identity: {psi[e] == gid}")
    assert {psi[t] for t in Gam} == set(gelems), "psi|Gamma not onto G"
    u = T[e]
    def Aw(word):
        M = sp.eye(A[letters[0]].shape[0])
        for s in word: M = A[s] * M
        return M
    Au = Aw(u)
    # Q_e, W, U, C
    Qe = sorted({e[i] for i in range(n)})
    base = Qd[Qk[Qe[0]]]
    diffs = [Qd[Qk[i]] - base for i in Qe[1:]]
    m = base.shape[1]; d = base.shape[0]
    cols = [D[:, j] for D in diffs for j in range(m)]
    Cmat = sp.Matrix.hstack(*cols) if cols else sp.zeros(d, 0)
    Cb = Cmat.columnspace()
    dimC = len(Cb)
    print(f"|Q_e| = {len(Qe)}, dim U = {sp.Matrix.hstack(*[D.reshape(d*m, 1) for D in diffs]).rank() if diffs else 0}, dim C = {dimC}")
    if dimC == 0:
        assert len(set(gelems)) == 1; return
    Cb = sp.Matrix.hstack(*Cb)
    assert (Au * Cb - Cb).is_zero_matrix, "A(u) not identity on C"
    pinv = (Cb.T * Cb).inv() * Cb.T

    def lam(word):  # linear part restricted to C, in the basis Cb
        M = Aw(word)
        img = M * Cb
        coords = pinv * img
        assert (Cb * coords - img).is_zero_matrix, "C not invariant"
        return coords
    lamG = {t: lam(u + T[t] + u) for t in Gam}
    # homomorphism + faithful
    for a in Gam:
        for b in Gam:
            assert lamG[comp(a, b)] == lamG[a] * lamG[b], "lambda' not a homomorphism"
    assert len({key(M) for M in lamG.values()}) == len(Gam), "lambda' not faithful on Gamma"
    # generators x_s, Gamma', ranks
    xs = {s: comp(comp(e, amap[s]), e) for s in letters}
    Gp = {e}; fr = [e]
    while fr:
        nf = []
        for t in fr:
            for s in letters:
                t2 = comp(xs[s], t)
                if t2 not in Gp: Gp.add(t2); nf.append(t2)
        fr = nf
    assert {psi[t] for t in Gp} == set(gelems), "Gamma' not onto G"
    for s in letters:
        assert psi[xs[s]] == s
        r = (lamG[xs[s]] - sp.eye(dimC)).rank(); r0 = (A[s] - sp.eye(d)).rank()
        print(f"  letter {s}: rank(lambda'(x_s) - I_C) = {r} <= rank(A(s) - I) = {r0}: {r <= r0}")
        assert r <= r0
    print(f"|Gamma'| = {len(Gp)}; all claims of L2 hold on this instance.")


def blockdiag(*Ms):
    return sp.diag(*Ms)


if __name__ == "__main__":
    # S3 on {0,1,2}, transpositions
    S3 = [tuple(p) for p in itertools.permutations(range(3))]
    e3 = (0, 1, 2)
    tr = [(1, 0, 2), (0, 2, 1), (2, 1, 0)]

    # E1: S3 / transpositions, vector state = permutation rep (rank 1 per transposition) + a singular "last letter" block
    # (A = 0, B = one-hot of the letter) + a projection block (beta = 1) with B in its kernel. T is not a group.
    A, B = {}, {}
    for i, s in enumerate(tr):
        P = pmat(s)
        proj = sp.Matrix([[1, 0], [0, 0]])  # I - e2 e2^T, beta = 1
        A[s] = blockdiag(P, sp.zeros(3, 3), proj)
        b = sp.zeros(8, 1); b[3 + i] = 1; b[7] = i + 1  # B in ker of the projection block
        B[s] = b
    h0 = sp.Matrix([1, 2, 3, 0, 0, 0, 5, 7])
    l2_construction("E1 S3/transpositions, singular blocks + affine terms", A, B, h0, tr, pmul, e3, S3)

    # E2: matrix-valued state (m = 2), S3 / all non-identity elements, A = permutation matrices acting from the left,
    # h0 = [e1, e2] (one column alone does not determine the permutation), plus an affine term in the sum-zero direction
    allS = [p for p in S3 if p != e3]
    A, B = {}, {}
    for s in allS:
        A[s] = pmat(s)
        B[s] = sp.zeros(3, 2)
    h0 = sp.Matrix([[1, 0], [0, 1], [0, 0]])
    l2_construction("E2 S3/all, matrix state 3x2", A, B, h0, allS, pmul, e3, S3)

    # E3: Z3 / {1}, permutation rep of the 3-cycle with an affine term b with (I + P + P^2) b = 0 (orbit is finite);
    # W does not pass through 0.
    c = (1, 2, 0)
    Z3 = [e3, c, pmul(c, c)]
    P = pmat(c)
    A = {c: P}; B = {c: sp.Matrix([1, -1, 0])}
    h0 = sp.Matrix([4, 0, 1])
    l2_construction("E3 Z3, affine input term", A, B, h0, [c], pmul, e3, Z3)

    # E4: S3 / transpositions through a larger cover: H = S3 x Z2, t_s = (s, -1) acting by -P (rank(-P - I) = 2),
    # matrix state with a singular extra row block. Compression must still give rank <= 2 and a faithful rep.
    A, B = {}, {}
    for i, s in enumerate(tr):
        A[s] = blockdiag(-pmat(s), sp.Matrix([[0]]))
        b = sp.zeros(4, 2); b[3, 0] = i; b[3, 1] = 1
        B[s] = b
    h0 = sp.Matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    l2_construction("E4 S3/transpositions via cover S3 x Z2, matrix state with singular row", A, B, h0, tr, pmul, e3, S3)
