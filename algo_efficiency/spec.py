"""Speculative decoding on a finite vocabulary: exact (verifier) and numerical (experiment) computations.

Setting: target distribution p and draft distribution q over V tokens. One verification step drafts k tokens from q and
must emit a token whose distribution is exactly p ("lossless"). A step "accepts" if the emitted token is one of the drafts.

Verifier side (exact rational arithmetic, fractions.Fraction):
  - accept_standard:      single-draft acceptance of Leviathan et al. / Chen et al. speculative sampling, sum_x min(p, q)
  - step_output:          exact output distribution and acceptance of a verification rule (standard, scaled, rrs_iid, rrs_wor)
  - optimal_multidraft:   optimal acceptance over ALL lossless couplings for k drafts, certified by an exact max-flow
                          (feasible coupling = lower bound) that equals an exact min-cut (upper bound)
  - optimal_gamma:        draft length maximising expected speedup, certified with an explicit tail bound
Experiment side (floating point, deliberately different methods): LP over draft tuples (scipy/HiGHS), Monte Carlo.
"""
from collections import deque
from fractions import Fraction
from itertools import combinations, product
import math

import numpy as np

V_MAX, K_MAX = 8, 4


# ---------- input handling ----------

def frac(x):
    """Exact rational from int, decimal string, 'a/b' string or float (floats via their decimal repr, never binary)."""
    if isinstance(x, Fraction): return x
    if isinstance(x, bool): raise ValueError("boolean is not a number")
    if isinstance(x, float): x = repr(x)
    return Fraction(str(x).strip())


def parse_dist(x, name="p"):
    if not isinstance(x, (list, tuple)): raise ValueError(f"{name} must be a list")
    d = [frac(v) for v in x]
    if not 2 <= len(d) <= V_MAX: raise ValueError(f"{name}: vocabulary size must be in [2, {V_MAX}]")
    if any(v < 0 for v in d): raise ValueError(f"{name}: negative probability")
    if sum(d) != 1: raise ValueError(f"{name}: probabilities sum to {sum(d)}, not exactly 1 (no renormalisation)")
    return d


def parse_pair(p, q):
    p, q = parse_dist(p, "p"), parse_dist(q, "q")
    if len(p) != len(q): raise ValueError("p and q need the same vocabulary size")
    return p, q


def fstr(x): return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)


# ---------- exact: single and sequential verification rules ----------

def accept_standard(p, q):
    return sum(min(a, b) for a, b in zip(p, q))


def _residual(p, q):
    r = [max(Fraction(0), a - b) for a, b in zip(p, q)]; z = sum(r)
    return [x / z for x in r] if z > 0 else None


def _scaled_step(p, q, lam):
    """Accept draft x ~ q with probability min(1, lam * p_x / q_x); on rejection sample from normalised max(0, p - q*a)."""
    a = [min(Fraction(1), lam * px / qx) if qx > 0 else Fraction(0) for px, qx in zip(p, q)]
    acc = [qx * ax for qx, ax in zip(q, a)]; A = sum(acc)
    r = [max(Fraction(0), px - c) for px, c in zip(p, acc)]; Z = sum(r)
    out = [c + ((1 - A) * rx / Z if Z > 0 else 0) for c, rx in zip(acc, r)]
    return out, A


def _sequential(p, q, k, wor):
    """Recursive rejection sampling with k drafts. iid: every draft from q. wor: drafts without replacement, i.e. from q
    restricted to unused tokens and renormalised; the residual is always taken w.r.t. the distribution actually drafted from."""
    V = len(p); out = [Fraction(0)] * V; accepted = Fraction(0)

    def rec(pc, avail, left, w):
        nonlocal accepted
        qc = [q[i] if i in avail else Fraction(0) for i in range(V)]; m = sum(qc)
        if left == 0 or m == 0 or w == 0:
            for i in range(V): out[i] += w * pc[i]
            return
        qc = [x / m for x in qc]
        res = _residual(pc, qc)
        for x in range(V):
            if qc[x] == 0: continue
            a = min(Fraction(1), pc[x] / qc[x])
            out[x] += w * qc[x] * a; accepted += w * qc[x] * a
        R = 1 - accept_standard(pc, qc)
        if R == 0 or res is None: return
        if not wor:
            rec(res, avail, left - 1, w * R); return
        for x in range(V):                       # branch on which token was rejected (it leaves the pool)
            if qc[x] == 0: continue
            rej = qc[x] * (1 - min(Fraction(1), pc[x] / qc[x]))
            if rej > 0: rec(res, avail - {x}, left - 1, w * rej)

    rec(list(p), frozenset(range(V)), k, Fraction(1))
    return out, accepted


def step_output(p, q, rule, k=1, lam=1):
    """Exact (output distribution, acceptance probability) of one verification step."""
    if rule == "standard": return _scaled_step(p, q, Fraction(1))
    if rule == "scaled": return _scaled_step(p, q, frac(lam))
    if rule in ("rrs_iid", "rrs_wor"):
        if not 1 <= int(k) <= K_MAX: raise ValueError(f"k must be in [1, {K_MAX}]")
        return _sequential(p, q, int(k), rule == "rrs_wor")
    raise ValueError(f"unknown rule {rule}")


# ---------- exact: optimal multi-draft acceptance (max-flow = min-cut) ----------

def draft_set_masses(q, k, mode):
    """Probability that the set of distinct drafted tokens equals T, for every T (dict frozenset -> Fraction)."""
    V = len(q); S = [i for i in range(V) if q[i] > 0]; mass = {}
    if mode == "iid":
        for r in range(1, len(S) + 1):
            for T in combinations(S, r):
                v = Fraction(0)
                for s in range(1, r + 1):                         # inclusion-exclusion over subsets U of T
                    for U in combinations(T, s): v += (-1) ** (r - s) * sum(q[i] for i in U) ** k
                if v: mass[frozenset(T)] = v
        return mass
    if mode == "wor":
        def rec(used, w, left):
            rest = sum(q[i] for i in S if i not in used)
            if left == 0 or rest == 0:
                mass[frozenset(used)] = mass.get(frozenset(used), Fraction(0)) + w; return
            for i in S:
                if i not in used: rec(used | {i}, w * q[i] / rest, left - 1)
        rec(frozenset(), Fraction(1), k); return mass
    raise ValueError(f"unknown mode {mode}")


def _prob_avoid(q, k, mode, H):
    """P(no drafted token lies in H), computed directly (independent of draft_set_masses)."""
    if mode == "iid": return (1 - sum(q[i] for i in H)) ** k
    S = [i for i in range(len(q)) if q[i] > 0]

    def rec(used, left):
        rest = sum(q[i] for i in S if i not in used)
        if left == 0 or rest == 0: return Fraction(1)
        return sum(q[i] / rest * rec(used | {i}, left - 1) for i in S if i not in used and i not in H)
    return rec(frozenset(), k)


def _maxflow(cap, s, t, n):
    """Edmonds-Karp on exact rationals. cap: dict (u, v) -> capacity (None = infinite)."""
    INF = None; adj = [[] for _ in range(n)]; res = {}
    for (u, v), c in cap.items():
        res[(u, v)] = c; res.setdefault((v, u), Fraction(0)); adj[u].append(v); adj[v].append(u)
    flow = Fraction(0)
    while True:
        prev = [-1] * n; prev[s] = s; dq = deque([s])
        while dq and prev[t] < 0:
            u = dq.popleft()
            for v in adj[u]:
                c = res[(u, v)]
                if prev[v] < 0 and (c is INF or c > 0): prev[v] = u; dq.append(v)
        if prev[t] < 0: return flow, res
        b, v = None, t
        while v != s:
            c = res[(prev[v], v)]; b = c if b is None or (c is not INF and c < b) else b; v = prev[v]
        v = t
        while v != s:
            u = prev[v]
            if res[(u, v)] is not INF: res[(u, v)] -= b
            if res[(v, u)] is not INF: res[(v, u)] += b
            v = u
        flow += b


def optimal_multidraft(p, q, k, mode="iid"):
    """Optimal acceptance over all lossless couplings of (k drafts) and (output ~ p). Returns (value, certificate).
    Lower bound: an explicit exact max-flow (a partial coupling with mass only on 'output in draft set', extendable to a full
    coupling). Upper bound: min over token sets H of p(V minus H) + P(draft set meets H), a cut. Equality certifies optimality."""
    if not 1 <= int(k) <= K_MAX: raise ValueError(f"k must be in [1, {K_MAX}]")
    k = int(k); V = len(p); mass = draft_set_masses(q, k, mode)
    if sum(mass.values()) != 1: raise AssertionError("draft set masses do not sum to 1")
    Ts = sorted(mass, key=lambda T: (len(T), sorted(T))); s, t = 0, 1; node = {T: 2 + j for j, T in enumerate(Ts)}
    tok = {y: 2 + len(Ts) + y for y in range(V)}; n = 2 + len(Ts) + V; cap = {}
    for T in Ts:
        cap[(s, node[T])] = mass[T]
        for y in T: cap[(node[T], tok[y])] = None
    for y in range(V): cap[(tok[y], t)] = p[y]
    flow, res = _maxflow(cap, s, t, n)
    # feasibility of the flow, re-derived from residuals: 0 <= f <= capacity and conservation at every node
    f = {e: (c - res[e]) if c is not None else res[(e[1], e[0])] for e, c in cap.items()}
    assert all(v >= 0 for v in f.values()) and all(c is None or f[e] <= c for e, c in cap.items())
    for T in Ts: assert f[(s, node[T])] == sum(f[(node[T], tok[y])] for y in T)
    for y in range(V): assert f[(tok[y], t)] == sum(f[(node[T], tok[y])] for T in Ts if y in T)
    best, argH = None, None
    for r in range(V + 1):
        for H in combinations(range(V), r):
            c = (1 - sum(p[i] for i in H)) + (1 - _prob_avoid(q, k, mode, set(H)))
            if best is None or c < best: best, argH = c, H
    return flow, {"flow": flow, "cut": best, "cut_set": list(argH), "certified": flow == best}


# ---------- exact: optimal draft length ----------

def speedup(alpha, c, g):
    """Expected walltime speedup with draft length g, i.i.d. acceptance alpha and draft/target cost ratio c
    (Leviathan et al. 2023, Thm 3.8 setting): (1 - alpha^(g+1)) / ((1 - alpha)(g c + 1))."""
    return (1 - alpha ** (g + 1)) / ((1 - alpha) * (g * c + 1))


def optimal_gamma(alpha, c, gmax=5000):
    """Exact argmax over g >= 0 with a tail certificate: for g > G, speedup < 1 / ((1 - alpha)(g c + 1)) <= best."""
    alpha, c = frac(alpha), frac(c)
    if not (0 <= alpha < 1 and c > 0): raise ValueError("need 0 <= alpha < 1 and c > 0")
    best, arg, pw = None, [], alpha
    for g in range(gmax + 1):
        v = (1 - pw) / ((1 - alpha) * (g * c + 1)); pw *= alpha
        if best is None or v > best: best, arg = v, [g]
        elif v == best: arg.append(g)
        if 1 / ((1 - alpha) * ((g + 1) * c + 1)) <= best:     # no larger g can beat (or tie) the current best
            return arg, best, g
    return None, best, gmax


# ---------- numerical experiments (independent methods) ----------

def lp_multidraft(p, q, k, mode="iid"):
    """Floating-point LP over draft TUPLES (not sets): maximise P(output in drafts) s.t. lossless marginals. Candidate only."""
    from scipy.optimize import linprog
    p = np.array([float(x) for x in p]); q = np.array([float(x) for x in q]); V = len(p)
    tuples = list(product(range(V), repeat=k)) if mode == "iid" else [t for t in product(range(V), repeat=k) if len(set(t)) == k]
    if len(tuples) * V > 60000: return {"error": "instance too large for the LP experiment"}
    def tprob(t):
        if mode == "iid": return float(np.prod(q[list(t)]))
        w, used = 1.0, set()
        for i in t:
            rest = 1 - sum(q[j] for j in used)
            if rest <= 0: return 0.0
            w *= q[i] / rest; used.add(i)
        return w
    w = np.array([tprob(t) for t in tuples]); nT = len(tuples)
    cost = -np.array([1.0 if y in t else 0.0 for t in tuples for y in range(V)])
    A = np.zeros((nT + V, nT * V)); b = np.concatenate([w, p])
    for i in range(nT): A[i, i * V:(i + 1) * V] = 1
    for y in range(V): A[nT + y, y::V] = 1
    r = linprog(cost, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    return {"acceptance": float(-r.fun) if r.success else None, "status": r.message, "note": "numerical (candidate)"}


def mc_scheme(p, q, rule, k=1, lam=1.0, samples=200000, seed=0):
    """Monte Carlo simulation of a verification rule: acceptance estimate with standard error and TV(empirical, p)."""
    rng = np.random.default_rng(seed); p = np.array([float(x) for x in p]); q0 = np.array([float(x) for x in q]); V = len(p)
    counts = np.zeros(V); acc = 0
    for _ in range(int(samples)):
        pc = p.copy(); avail = np.ones(V, bool); emitted = None
        steps = 1 if rule in ("standard", "scaled") else int(k)
        lam_ = float(lam) if rule == "scaled" else 1.0
        for _s in range(steps):
            qc = q0 * avail if rule == "rrs_wor" else q0.copy()
            if qc.sum() <= 0: break
            qc = qc / qc.sum(); x = rng.choice(V, p=qc)
            if rng.random() < min(1.0, lam_ * pc[x] / qc[x]): emitted = x; acc += 1; break
            r = np.maximum(pc - (np.minimum(1.0, lam_ * pc / np.where(qc > 0, qc, 1)) * qc if rule == "scaled" else qc), 0)
            if r.sum() <= 1e-15: break
            pc = r / r.sum()
            if rule == "rrs_wor": avail[x] = False
        if emitted is None: emitted = rng.choice(V, p=pc / pc.sum())
        counts[emitted] += 1
    a = acc / samples
    return {"acceptance": a, "stderr": math.sqrt(a * (1 - a) / samples), "tv_to_target": float(0.5 * np.abs(counts / samples - p).sum()),
            "samples": int(samples), "note": "Monte Carlo (statistical estimate)"}


def random_instance(V=4, seed=0, family="dirichlet", conc=1.0, denom=1000):
    """Random (p, q) with exact rational entries of denominator `denom` (sums exactly 1)."""
    rng = np.random.default_rng(seed); V = int(V)
    if not 2 <= V <= V_MAX: return {"error": f"V must be in [2, {V_MAX}]"}
    def one():
        if family == "dirichlet": x = rng.dirichlet(np.full(V, float(conc)))
        elif family == "zipf": x = 1 / np.arange(1, V + 1) ** float(conc); rng.shuffle(x); x = x / x.sum()
        else: return None
        n = np.floor(x * denom).astype(int); n[np.argmax(x)] += denom - n.sum()
        return [fstr(Fraction(int(v), denom)) for v in n]
    p, q = one(), one()
    if p is None: return {"error": f"unknown family {family}"}
    return {"p": p, "q": q}
