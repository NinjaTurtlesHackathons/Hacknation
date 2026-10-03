"""Red team T2: exact speculative-decoding quantities against independent implementations.

(a) optimal_multidraft vs an LP over draft TUPLES (scipy HiGHS, tight tolerances) and vs an independent exact upper bound
    computed by tuple enumeration (min over H of p(V\\H) + P(tuple meets H)) -- if the verifier's value exceeded this, it'd be wrong.
(b) RRS (iid / wor) acceptance and output distribution vs an independent exact tuple-level simulation of the algorithm.
(c) scaled rule: the verifier's 'acceptance' (P(accept flag)) vs P(emitted token == drafted token), the definition used in
    the module docstring ('a step accepts if the emitted token is one of the drafts').
Instances: random with zeros, extreme masses, k > support, V up to 6.
"""
from fractions import Fraction as F
from itertools import product, combinations
import random

import numpy as np
from scipy.optimize import linprog

from algo_efficiency import spec as S


def rand_dist(rng, V, zeros):
    w = [0 if (zeros and rng.random() < 0.35) else rng.choice([1, 1, 2, 5, 50, 999]) for _ in range(V)]
    if sum(w) == 0: w[rng.randrange(V)] = 1
    t = sum(w); return [F(x, t) for x in w]


def tuples(q, k, mode):
    V = len(q); out = {}
    for t in product(range(V), repeat=k):
        if mode == "iid":
            w = F(1)
            for i in t: w *= q[i]
        else:
            w, used = F(1), set()
            for i in t:
                rest = 1 - sum(q[j] for j in used)
                if rest == 0: w = F(0) if i not in used or True else w; break
                if i in used: w = F(0); break
                w *= q[i] / rest; used.add(i)
            # if support exhausted early the tuple is padded: normalise by recording the prefix set only
        if w: out[t] = w
    if mode == "wor":   # rebuild with explicit early stop (support exhausted): enumerate sequences recursively instead
        out = {}
        S_ = [i for i in range(V) if q[i] > 0]
        def rec(seq, w):
            rest = sum(q[i] for i in S_ if i not in seq)
            if len(seq) == k or rest == 0: out[tuple(seq)] = out.get(tuple(seq), F(0)) + w; return
            for i in S_:
                if i not in seq: rec(seq + [i], w * q[i] / rest)
        rec([], F(1))
    return out


def lp_value(p, T):
    V = len(p); keys = list(T); nT = len(keys)
    cost = -np.array([1.0 if y in t else 0.0 for t in keys for y in range(V)])
    A = np.zeros((nT + V, nT * V)); b = np.concatenate([[float(T[t]) for t in keys], [float(x) for x in p]])
    for i in range(nT): A[i, i * V:(i + 1) * V] = 1
    for y in range(V): A[nT + y, y::V] = 1
    r = linprog(cost, A_ub=A, b_ub=b,  # <= rows: the partial coupling (mass on accepted pairs) extends to a full lossless one
                bounds=(0, None), method="highs",
                options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
    return -r.fun


def exact_cut(p, T):
    V = len(p); best = None
    for r in range(V + 1):
        for H in combinations(range(V), r):
            c = 1 - sum(p[i] for i in H) + sum(w for t, w in T.items() if set(t) & set(H))
            best = c if best is None or c < best else best
    return best


def rrs_tuple(p, q, k, wor):
    """Exact RRS by explicit enumeration of the random draw sequence (independent code path)."""
    V = len(p); out = [F(0)] * V; acc = [F(0)]
    def go(pc, used, j, w):
        if w == 0: return
        avail = [i for i in range(V) if q[i] > 0 and (not wor or i not in used)]
        m = sum(q[i] for i in avail)
        if j == k or m == 0:
            for i in range(V): out[i] += w * pc[i]
            return
        qc = [q[i] / m if i in avail else F(0) for i in range(V)]
        for x in avail:
            px = qc[x]; a = min(F(1), pc[x] / qc[x])
            out[x] += w * px * a; acc[0] += w * px * a
            if a < 1:
                r = [max(F(0), pc[i] - qc[i]) for i in range(V)]; z = sum(r)
                if z == 0: continue
                go([v / z for v in r], used | {x}, j + 1, w * px * (1 - a))
    go(list(p), frozenset(), 0, F(1))
    return out, acc[0]


rng = random.Random(7); worst_lp = 0; n = 0; bugs = []
for trial in range(250):
    V = rng.randint(2, 5); k = rng.randint(1, 4 if V <= 4 else 3); zeros = trial % 2 == 0
    p, q = rand_dist(rng, V, zeros), rand_dist(rng, V, zeros)
    for mode in ("iid", "wor"):
        v, cert = S.optimal_multidraft(p, q, k, mode)
        T = tuples(q, k, mode); assert sum(T.values()) == 1
        ub = exact_cut(p, T)
        if v != ub: bugs.append(("cut mismatch", p, q, k, mode, v, ub))
        lv = lp_value(p, T); worst_lp = max(worst_lp, abs(lv - float(v)))
        if not cert["certified"]: bugs.append(("uncertified", p, q, k, mode))
        out, a = S.step_output(p, q, "rrs_" + mode, k=k); out2, a2 = rrs_tuple(p, q, k, mode == "wor")
        if out != out2 or a != a2: bugs.append(("rrs mismatch", p, q, k, mode, a, a2))
        if a > v: bugs.append(("rrs above optimum", p, q, k, mode, a, v))
        if out != p: bugs.append(("rrs not lossless", p, q, k, mode))
        n += 1
print(f"(a,b) {n} instance/mode pairs; max |LP - exact| = {worst_lp:.2e}; problems: {len(bugs)}")
for b in bugs[:10]: print("   ", b)

# (c) scaled rule semantics
print("(c) scaled rule: verifier acceptance vs P(emitted == drafted)")
for p, q, lam in [([F(1, 2), F(1, 2)], [F(1, 2), F(1, 2)], F(1, 2)), ([F(1, 2), F(1, 4), F(1, 4)], [F(1, 5), F(3, 5), F(1, 5)], F(1, 2)),
                  ([F(1, 2), F(1, 4), F(1, 4)], [F(1, 5), F(3, 5), F(1, 5)], F(0))]:
    out, A = S.step_output(p, q, "scaled", lam=lam)
    acc = [min(F(1), lam * p[x] / q[x]) for x in range(len(p))]
    r = [max(F(0), p[x] - q[x] * acc[x]) for x in range(len(p))]; Z = sum(r)
    same = sum(q[x] * (acc[x] + (1 - acc[x]) * r[x] / Z) for x in range(len(p)))
    print(f"   p={[str(x) for x in p]} q={[str(x) for x in q]} lambda={lam}: verifier acceptance {A}, P(output == draft) {same}, lossless {out == p}")
