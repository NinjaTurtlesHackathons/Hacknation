"""T3: soundness and completeness of realisation.verify against an independent re-implementation.
(a) every construction x twist the library offers, on every small group/alphabet, recomputed independently in floating point
    (numpy closure with rounded keys, label consistency, onto, SVD rank) and compared with verify();
(b) exhaustive differential test on adversarial matrices: all assignments of signed permutation matrices (dim <= 3) to the
    letters of small (G, Sigma), via the claim type realisation_matrices; independent exact integer closure + sympy rank;
(c) hand-crafted adversarial matrices (singular, unipotent, wrong order, non-orthogonal finite groups)."""
import itertools, json, time
import numpy as np, sympy
from expressivity.domain import DOMAIN, CONSTRUCTIONS, TWISTS
from expressivity.groups import get_group, alphabet
from expressivity.algebra import pmul, porder
from expressivity import reps as REPS
from expressivity.realisation import verify

def indep(G, S, mats, cap=20000):
    """mats: list of numpy arrays (alphabet order). Returns (ok_consistent_onto, H, max_rank) or reason string."""
    d = mats[0].shape[0]; I = np.eye(d)
    key = lambda M: tuple(np.round(M, 8).ravel() + 0.0)
    lab = {key(I): G.e}; store = {key(I): I}; fr = [key(I)]
    while fr:
        nx = []
        for k in fr:
            M = store[k]; g = lab[k]
            for s, A in zip(S, mats):
                Y = A @ M; ky = key(Y); gy = pmul(s, g)
                if ky in lab:
                    if lab[ky] != gy: return "inconsistent"
                else:
                    lab[ky] = gy; store[ky] = Y; nx.append(ky)
                    if len(lab) > cap: return "cap"
        fr = nx
    if len(set(lab.values())) != G.order: return "not onto"
    P = sum(M.T @ M for M in store.values())
    if any(np.abs(A.T @ P @ A - P).max() > 1e-6 for A in mats): return "not orthogonal"
    r = max(int((np.linalg.svd(A - I, compute_uv=False) > 1e-8).sum()) for A in mats)
    return ("ok", len(lab), r)

print("(a) library constructions vs independent recomputation")
cases = [("Z2","all"),("Z3","all"),("Z4","all"),("Z5","all"),("Z6","all"),("Z6","gens"),("Z8","gens"),("Z12","gens"),
         ("Z2^2","all"),("Z2^3","all"),("Z2xZ4","gens"),("Z3xZ3","gens"),("S3","all"),("S3","transpositions"),("S3","gens"),
         ("D4","all"),("D4","involutions"),("D5","all"),("D6","involutions"),("Q8","all"),("Q8","gens"),("A4","all"),("A4","cycles3"),
         ("S4","transpositions"),("S4","gens"),("A5","involutions"),("A5","cycles3"),("A5","cycles5")]
disagree = []; n = 0; t0 = time.time()
for g, a in cases:
    G = get_group(g); S = alphabet(G, a)
    for rep in CONSTRUCTIONS:
        for tw in TWISTS:
            try: R = REPS.construct(G, S, rep, tw)
            except (ValueError, OverflowError): continue
            mats = [np.array([[float(x) for x in r] for r in R[s]]) for s in S]
            if mats[0].shape[0] > 40: continue
            ind = indep(G, S, mats); n += 1
            for k in (0, 1, 2, 3, 4):
                ok, why, ev = verify(G, S, R, k)
                want = isinstance(ind, tuple) and ind[2] <= k
                if bool(ok) != want or (ok and (ev["H_order"] != ind[1] or ev["max_rank"] != ind[2])):
                    disagree.append((g, a, rep, tw, k, ok, why[:80], ind))
            print(f"  {g:6} {a:15} {rep:6} {tw:12} indep: {ind}")
print(f"  {n} constructions, disagreements: {len(disagree)}  ({time.time()-t0:.0f}s)")
for d in disagree: print("   DISAGREE", d)

print("(b) exhaustive signed-permutation matrices via realisation_matrices")
def signed_perms(d):
    out = []
    for p in itertools.permutations(range(d)):
        for sg in itertools.product((1, -1), repeat=d):
            M = np.zeros((d, d), dtype=int)
            for i, j in enumerate(p): M[j, i] = sg[i]
            out.append(M)
    return out
tot = 0; bad = []; acc = 0; t0 = time.time()
for g, a, d in [("Z2","all",1),("Z2","all",2),("Z3","all",2),("Z4","gens",2),("Z2^2","gens",2),("S3","gens",2),("S3","transpositions",2),
                ("Z3","gens",3),("Z4","gens",3),("Z2^2","gens",3),("S3","gens",3),("Z6","gens",3),("D4","gens",3)]:
    G = get_group(g); S = alphabet(G, a); SP = signed_perms(d)
    for combo in itertools.product(SP, repeat=len(S)):
        mats = list(combo); ind = indep(G, S, [m.astype(float) for m in mats])
        for k in (1, 2):
            p = {"typ": "realisation_matrices", "group": g, "alphabet": a, "k": k, "matrices": [m.tolist() for m in mats]}
            ok, why, _ = DOMAIN.check(p); tot += 1
            want = isinstance(ind, tuple) and ind[2] <= k
            if ok: acc += 1
            if bool(ok) != want: bad.append((p, ok, why[:100], ind))
print(f"  {tot} claims, accepted {acc}, disagreements with independent check: {len(bad)}  ({time.time()-t0:.0f}s)")
for b in bad[:10]: print("   DISAGREE", json.dumps(b[0]), b[1], b[2], b[3])

print("(c) hand-crafted adversarial matrices")
hc = [
    ("singular idempotent for Z2", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["0"]]]}),
    ("projection for Z2", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["1", "0"], ["0", "0"]]]}),
    ("unipotent (infinite order) for Z2", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["1", "1"], ["0", "1"]]]}),
    ("order-2 matrix for Z4 generator", {"typ": "realisation_matrices", "group": "Z4", "alphabet": "gens", "k": 1, "matrices": [[["-1"]]]}),
    ("non-orthogonal finite: oblique reflection for Z2", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["1", "3"], ["0", "-1"]]]}),
    ("oblique order-3 (similar to rotation) for Z3 gens, k=2", {"typ": "realisation_matrices", "group": "Z3", "alphabet": "gens", "k": 2, "matrices": [[["0", "-1"], ["1", "-1"]]]}),
    ("same, k=1 (must fail)", {"typ": "realisation_matrices", "group": "Z3", "alphabet": "gens", "k": 1, "matrices": [[["0", "-1"], ["1", "-1"]]]}),
    ("scaling 1/2 for Z2 (infinite)", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["1/2"]]]}),
    ("decimal strings", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["-1.0"]]]}),
    ("nan", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["nan"]]]}),
    ("empty matrix", {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[]]}),
]
for name, p in hc:
    t0 = time.time(); ok, why, _ = DOMAIN.check(p)
    print(f"  {name:55} -> {ok!s:5} {why[:110]} ({time.time()-t0:.1f}s)")
print("  note: 'realisation_matrices' is accepted by check() but is NOT documented in claim_doc.")
