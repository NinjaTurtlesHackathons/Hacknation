"""T8: does the Cartan-Dieudonne certificate prove what describe() claims ('at most k Householder reflections per token')?
For each letter of several certified realisations: recompute P, factor with cartan_dieudonne, and check independently that
every factor R is a genuine P-reflection (R^2 = I, rank(R - I) = 1, R^T P R = P, det = -1), that the product is the letter
matrix, that #factors == rank(M - I), and that in a P-orthonormal basis (Cholesky, numerically) each factor is a standard
Householder I - 2 u u^T with |u| = 1 (beta = 2)."""
import numpy as np
from expressivity.groups import get_group, alphabet
from expressivity import reps as REPS
from expressivity.algebra import (eye, mmul, mT, madd, msub, rank, det, cartan_dieudonne, p_reflection, mkey)

def closure(R):
    I = eye(next(iter(R.values()))[0][0].F, len(next(iter(R.values()))))
    seen = {mkey(I): I}; fr = [I]
    while fr:
        nx = []
        for X in fr:
            for M in R.values():
                Y = mmul(M, X)
                if mkey(Y) not in seen: seen[mkey(Y)] = Y; nx.append(Y)
        fr = nx
    return list(seen.values())

cases = [("A5", "involutions", "so3", "involutions"), ("A5", "all", "so3", "none"), ("S4", "all", "so3", "none"),
         ("S4", "transpositions", "perm", "none"), ("D5", "all", "planar", "none"), ("Z2^3", "all", "count", "none"),
         ("Z6", "all", "planar", "none"), ("Q8", "gens", "perm", "all")]
fails = 0
for g, a, rep, tw in cases:
    G = get_group(g); S = alphabet(G, a); R = REPS.construct(G, S, rep, tw)
    H = closure(R); P = None
    for M in H: T = mmul(mT(M), M); P = T if P is None else madd(P, T)
    Pn = np.array([[float(x) for x in r] for r in P]); L = np.linalg.cholesky(Pn)    # P = L L^T
    I = eye(P[0][0].F, len(P)); nf = 0; mx = 0
    for s in S:
        M = R[s]; r = rank(msub(M, I)); vs = cartan_dieudonne(M, P); prod = I
        for v in vs:
            Rf = p_reflection(v, P); prod = mmul(prod, Rf)
            ok = (mmul(Rf, Rf) == I and rank(msub(Rf, I)) == 1 and mmul(mmul(mT(Rf), P), Rf) == P and det(Rf) == -1)
            Rn = np.array([[float(x) for x in rr] for rr in Rf]); Q = L.T @ Rn @ np.linalg.inv(L.T)
            u = np.linalg.svd(np.eye(len(Q)) - Q)[0][:, 0]
            ok = ok and np.allclose(Q, np.eye(len(Q)) - 2 * np.outer(u, u), atol=1e-9)
            if not ok: fails += 1
        if prod != M or len(vs) != r: fails += 1
        mx = max(mx, len(vs))
    print(f"{g:5} {a:13} {rep:6} {tw:12} |H|={len(H):4d} dim={len(P)} max #reflections={mx}  failures so far={fails}")
print("total failures:", fails)
