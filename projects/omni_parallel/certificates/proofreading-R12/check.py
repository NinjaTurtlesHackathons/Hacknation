"""Standalone check of an exact reachability certificate (kinetic proofreading). Standard library only. Prints PASS or FAIL.
Checks: (1) every rate lies in [e^-10, e^10] (conservative rational bounds), (2) the W branch follows from the R branch
(discriminating exits x100, other bound->unbound reverse rates /100), (3) local detailed balance on a cycle basis,
(4) exact steady state: eta = J_W / J_R <= eta_max (and v = J_R >= v_min if given)."""
import json, sys
from fractions import Fraction as F
E10_LO = F("22026.4657948")                     # < e^10, so f <= E10_LO implies f <= e^10 and f >= 1/E10_LO implies f >= e^-10


def steady(states, edges):
    n = len(states); ix = {s: i for i, s in enumerate(states)}; Q = [[F(0)] * n for _ in range(n)]
    for e in edges: Q[ix[e["u"]]][ix[e["v"]]] += e["f"]; Q[ix[e["v"]]][ix[e["u"]]] += e["b"]
    for i in range(n): Q[i][i] = -sum(Q[i][j] for j in range(n) if j != i)
    M = [[Q[j][i] for j in range(n)] + [F(0)] for i in range(n)]; M[-1] = [F(1)] * n + [F(1)]
    for c in range(n):                                          # Gauss-Jordan, exakt
        p = next(r for r in range(c, n) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
        M[c] = [x / M[c][c] for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0: M[r] = [a - M[r][c] * b for a, b in zip(M[r], M[c])]
    return {s: M[ix[s]][n] for s in states}


def check_case(c):
    E = [dict(e, f=F(e["f"]), b=F(e["b"]), a=F(e["a"])) for e in c["kanten"]]; B = set(c["gebunden"]); ed = F(c["e_delta"])
    for e in E:
        for k in (e["f"], e["b"]):
            if not (1 / E10_LO <= k <= E10_LO): return f"rate {k} of {e['id']} outside [e^-10, e^10]"
    R = {e["id"]: e for e in E if e["zweig"] == "R"}
    for e in E:
        if e["zweig"] != "W": continue
        r = R[e["id"]]; u0, v0 = e["u"].rsplit("_W", 1)[0], e["v"].rsplit("_W", 1)[0]; f, b = r["f"], r["b"]
        if u0 in B and v0 not in B: f, b = (f * ed, b) if e["disk"] else (f, b / ed)
        elif v0 in B and u0 not in B: f, b = (f, b * ed) if e["disk"] else (f / ed, b)
        if (f, b) != (e["f"], e["b"]): return f"W rates of {e['id']} do not follow from the R branch"
    adj, seen, par = {}, set(), {}                              # spanning tree (BFS) of the multigraph, then one cycle per chord
    for j, e in enumerate(E): adj.setdefault(e["u"], []).append((e["v"], j)); adj.setdefault(e["v"], []).append((e["u"], j))
    tree = set()
    for s0 in adj:
        if s0 in seen: continue
        seen.add(s0); q = [s0]
        while q:
            x = q.pop(0)
            for y, j in adj[x]:
                if y not in seen: seen.add(y); par[y] = (x, j); tree.add(j); q.append(y)
    def up(x):
        out = []
        while x in par: p, j = par[x]; out.append((p, x, j)); x = p
        return out
    for j, e in enumerate(E):
        if j in tree: continue
        pk, pa = e["f"] / e["b"], e["a"]                        # cycle u -> v (chord), back v -> u along the tree
        for a_, b_, k in [(y, x, k) for (x, y, k) in up(e["v"])] + [(x, y, k) for (x, y, k) in reversed(up(e["u"]))]:
            t = E[k]
            if t["u"] == a_: pk *= t["f"] / t["b"]; pa *= t["a"]
            else: pk *= t["b"] / t["f"]; pa /= t["a"]
        if pk != pa: return f"local detailed balance violated on the cycle of {e['id']}"
    pi = steady(c["zustaende"], E); J = {"R": F(0), "W": F(0)}
    for e in E:
        if e["produkt"]: J[e["zweig"]] += pi[e["u"]] * e["f"] - pi[e["v"]] * e["b"]
    if J["R"] <= 0: return "no net production"
    eta = J["W"] / J["R"]
    if eta > F(c["eta_max"]): return f"eta = {float(eta):.6e} > eta_max = {c['eta_max']}"
    if c.get("v_min") is not None and J["R"] < F(c["v_min"]): return f"v = {float(J['R']):.4e} < v_min"
    return None


cert = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "certificate.json"))
errors = [f"{c['topologie']}: {m}" for c in cert["faelle"] for m in [check_case(c)] if m]
print("PASS" if not errors else "FAIL: " + "; ".join(errors)); sys.exit(1 if errors else 0)
