"""Character tables and the faithful Householder complexity h(G, Sigma) (own implementation, independent of GAP).

Burnside–Dixon: class multiplication coefficients a_ijk -> common eigenvectors of the class matrices (numerically, random
combination) -> characters. Real irreducible representations from the Frobenius–Schur indicator. For a real representation
psi and an element g of order o: codim Fix psi(g) = deg psi - (1/o) sum_j psi(g^j), an integer; the code rounds it and
refuses if the distance to the nearest integer exceeds 1e-6 (integrality margin). The minimisation over faithful sums of real
irreducibles is exact combinatorics (branch and bound) on these integers.
"""
import numpy as np
from .algebra import pmul, pinv, porder


def class_data(G):
    cls = G.classes(); r = len(cls); idx = {}
    for i, c in enumerate(cls):
        for g in c: idx[g] = i
    sizes = np.array([len(c) for c in cls], dtype=float)
    reps = [c[0] for c in cls]
    # a[i][j][k] = #{(x, y) in C_i x C_j : x y = z_k}
    a = np.zeros((r, r, r))
    for i, ci in enumerate(cls):
        for x in ci:
            for j, cj in enumerate(cls):
                for y in cj:
                    a[i, j, idx[pmul(x, y)]] += 1
    a /= sizes[None, None, :]
    # power maps: class of g^j for the representative of each class
    powers = []
    for g in reps:
        o = porder(g); x = G.e; pw = []
        for _ in range(o):
            pw.append(idx[x]); x = pmul(g, x)
        powers.append(pw)
    sq = [idx[pmul(g, g)] for g in G.elements]
    inv = [idx[pinv(g)] for g in reps]
    return cls, idx, sizes, reps, a, powers, sq, inv


def character_table(G, seed=0):
    """Rows = irreducible complex characters (values on class representatives)."""
    cls, idx, sizes, reps, a, powers, sq, inv = class_data(G)
    r = len(cls); n = G.order; rng = np.random.default_rng(seed)
    e = idx[G.e]
    for attempt in range(5):
        c = rng.normal(size=r)
        M = np.einsum("i,ijk->jk", c, a)            # M[j, k]: sum_i c_i a_ijk ; omega_j satisfies sum_k a_ijk omega_k = omega_i omega_j
        # eigenvectors of M^T? We need vectors w with sum_k a_ijk w_k = lam_i w_j for all i, i.e. A_i w = lam_i w with (A_i)_{jk} = a_ijk
        vals, vecs = np.linalg.eig(M)
        if len(set(np.round(vals, 6))) < r: continue
        chars = []
        for t in range(r):
            w = vecs[:, t] / vecs[e, t]
            deg = np.sqrt(n / np.sum(np.abs(w) ** 2 / sizes))
            chars.append(deg * w / sizes)
        X = np.array(chars)
        degs = X[:, e].real
        if abs(np.sum(degs ** 2) - n) < 1e-6 * n and np.all(np.abs(degs - np.round(degs)) < 1e-6):
            order = np.lexsort((np.round(X.real.sum(1), 6), np.round(degs)))
            return X[order], (cls, idx, sizes, reps, powers, sq, inv)
    raise ArithmeticError("character table: eigenvalues not separated")


def real_irreps(G):
    """List of real irreducible representations: dict(deg, char (values on classes), fs, complex_rows)."""
    X, data = character_table(G)
    cls, idx, sizes, reps, powers, sq, inv = data
    n = G.order; out = []; used = set()
    sq_count = np.zeros(len(cls))
    for s in sq: sq_count[s] += 1                     # number of g with g^2 in class s
    for t, chi in enumerate(X):
        if t in used: continue
        fs = np.sum(sq_count * chi) / n
        fsr = int(round(fs.real))
        if abs(fs - fsr) > 1e-6: raise ArithmeticError("Frobenius–Schur indicator not integral")
        if fsr == 1:
            out.append({"deg": int(round(chi[idx[G.e]].real)), "char": chi.real, "fs": 1, "rows": [t]}); used.add(t)
        elif fsr == -1:
            out.append({"deg": 2 * int(round(chi[idx[G.e]].real)), "char": 2 * chi.real, "fs": -1, "rows": [t]}); used.add(t)
        else:
            conj = np.conj(chi)
            t2 = next(u for u in range(len(X)) if u not in used and u != t and np.allclose(X[u], conj, atol=1e-6))
            out.append({"deg": 2 * int(round(chi[idx[G.e]].real)), "char": (chi + conj).real, "fs": 0, "rows": [t, t2]})
            used.update((t, t2))
    return out, data


def codim_table(G):
    """codim[psi][class] for every real irreducible psi, plus kernels (sets of classes acting trivially)."""
    R, data = real_irreps(G)
    cls, idx, sizes, reps, powers, sq, inv = data
    table = []; kernels = []; minus = []
    for psi in R:
        row = []; mrow = []
        for c, pw in enumerate(powers):
            o = len(pw); fix = sum(psi["char"][p] for p in pw) / o
            cd = psi["deg"] - fix
            ci = int(round(cd))
            if abs(cd - ci) > 1e-6: raise ArithmeticError(f"codim not integral: {cd}")
            row.append(ci)
            # multiplicity of eigenvalue -1: (1/o) sum_j (-1)^j psi(g^j) for even o, else 0
            if o % 2 == 0:
                m = sum(((-1) ** j) * psi["char"][p] for j, p in enumerate(pw)) / o
                mi = int(round(m))
                if abs(m - mi) > 1e-6: raise ArithmeticError("-1 multiplicity not integral")
            else:
                mi = 0
            mrow.append(mi)
        table.append(row); minus.append(mrow)
        kernels.append(frozenset(c for c in range(len(cls)) if abs(psi["char"][c] - psi["deg"]) < 1e-6))
    return {"irreps": [{"deg": p["deg"], "fs": p["fs"]} for p in R], "codim": table, "minus": minus, "kernels": kernels,
            "classes": cls, "class_index": idx, "class_sizes": [int(s) for s in sizes]}


def minimise(codim, kernels, sigma_classes, n_classes, identity_class, budget=None):
    """min over sets S of real irreducibles with intersection of kernels = {identity class} of max_{c in sigma} sum_{psi in S} codim[psi][c].
    Exact branch and bound. Returns (value, S)."""
    full = frozenset(range(n_classes)); target = frozenset([identity_class])
    m = len(codim); best = [budget if budget is not None else 10 ** 9, None]
    order = sorted(range(m), key=lambda p: max(codim[p][c] for c in sigma_classes))

    def rec(start, K, load, chosen):
        cur = max(load.values()) if load else 0
        if cur >= best[0]: return
        if K == target:
            best[0], best[1] = cur, list(chosen); return
        for j in range(start, m):
            p = order[j]
            K2 = K & kernels[p]
            if K2 == K: continue                       # does not shrink the kernel: useless
            load2 = {c: load.get(c, 0) + codim[p][c] for c in sigma_classes}
            rec(j + 1, K2, load2, chosen + [p])

    rec(0, full, {c: 0 for c in sigma_classes}, [])
    return best[0], best[1]


def faithful_h(G, sigma):
    """h(G, Sigma) from the own character table. sigma: list of group elements (the alphabet)."""
    T = codim_table(G)
    sc = sorted({T["class_index"][s] for s in sigma})
    e = T["class_index"][G.e]
    if G.order == 1: return 0, [], T
    v, S = minimise(T["codim"], T["kernels"], sc, len(T["classes"]), e)
    return v, S, T
