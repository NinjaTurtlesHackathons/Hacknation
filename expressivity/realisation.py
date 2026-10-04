"""Exact verification of a one-layer Householder realisation certificate (sufficiency, lemma L3).

Input: group G, alphabet Sigma, budget k, matrices R[s] (exact). Checks, all in exact arithmetic:
  1. closure of the pairs (R[w], g(w)) over all words w terminates (the matrix group H is finite, |H| <= cap);
  2. consistency: every matrix of H carries exactly one group element (so a readout from the state exists and pi: H -> G is
     well defined); every element of G is reached (pi is onto);
  3. P = sum_{M in H} M^T M is positive definite and R[s]^T P R[s] = P for every letter (H is orthogonal for P);
  4. rank(R[s] - I) <= k for every letter, and an explicit factorisation of R[s] into rank(R[s] - I) <= k P-reflections
     (Cartan–Dieudonné), multiplied back exactly.
If all pass, the recurrence h_t = R[s_t] h_{t-1} (in a P-orthonormal basis: products of <= k Householder reflections, beta = 2)
with a generic initial state and the readout M h_0 -> pi(M) solves the word problem exactly for every length.
"""
from .algebra import porder, eye, mmul, mT, mkey, msub, rank, is_pos_def, madd, cartan_dieudonne, p_reflection, pmul


def verify(G, sigma, R, k, cap=60000):
    try:
        letters = list(sigma)
        if set(letters) != set(R): return False, "matrices must be given for exactly the letters of the alphabet", {}
        d = len(R[letters[0]]); F0 = R[letters[0]][0][0]
        if any(len(M) != d or any(len(r) != d for r in M) for M in R.values()): return False, "dimension mismatch", {}
        I = eye(F0.F, d)
        # 0: every letter must have finite order (cheap pre-check; red team: unbounded denominators before the closure cap)
        for s in letters:
            X = R[s]; o = 1
            while X != I:
                X = mmul(R[s], X); o += 1
                big = max(max(abs(c.denominator).bit_length(), abs(c.numerator).bit_length()) for row in X for x in row for c in x.c)
                if o > 5000 or big > 400: return False, "a letter matrix does not have finite order (powers grow): no finite group", {}
        # 1 + 2: closure with labels
        lab = {mkey(I): G.e}; mats = {mkey(I): I}; frontier = [mkey(I)]
        while frontier:
            nxt = []
            for key in frontier:
                M = mats[key]; g = lab[key]
                for s in letters:
                    Y = mmul(R[s], M); ky = mkey(Y); gy = pmul(s, g)
                    if ky in lab:
                        if lab[ky] != gy:
                            return False, "inconsistent: one state matrix carries two different group elements (no readout exists)", {"H_size_so_far": len(lab)}
                    else:
                        lab[ky] = gy; mats[ky] = Y; nxt.append(ky)
                        if len(lab) > cap: return False, f"matrix group larger than the verifier cap {cap} (finiteness not certified)", {}
            frontier = nxt
        H = len(lab); covered = len(set(lab.values()))
        if covered != G.order: return False, f"pi not onto: {covered} of {G.order} elements reached", {}
        # 3: invariant form
        P = None
        for M in mats.values():
            T = mmul(mT(M), M); P = T if P is None else madd(P, T)
        if not is_pos_def(P): return False, "averaged form not positive definite", {}
        for s in letters:
            if mmul(mmul(mT(R[s]), P), R[s]) != P: return False, "letter matrix not orthogonal for the averaged form", {}
        # 4: rank and explicit reflection factorisation
        ranks = {}; nrefl = {}
        for s in letters:
            r = rank(msub(R[s], I)); ranks[s] = r
            if r > k: return False, f"rank(R[s] - I) = {r} > k = {k} for a letter of order {porder(s)}", {"max_rank": r}
            vs = cartan_dieudonne(R[s], P)
            prod = I
            for v in vs: prod = mmul(prod, p_reflection(v, P))
            if prod != R[s] or len(vs) != r: return False, "explicit Householder factorisation failed", {}
            nrefl[s] = len(vs)
        mr = max(ranks.values())
        return True, (f"certified: |H| = {H}, pi: H -> G onto ({G.order} elements), consistent readout, dimension {d}, "
                      f"field {F0.F}, max rank(R[s] - I) = {mr} <= k = {k}, every letter factored into <= {mr} exact reflections"), \
            {"H_order": H, "dim": d, "max_rank": mr, "field": str(F0.F), "kernel_order": H // G.order}
    except Exception as e:
        return False, f"verification not executable: {type(e).__name__}: {e}"[:300], {}
