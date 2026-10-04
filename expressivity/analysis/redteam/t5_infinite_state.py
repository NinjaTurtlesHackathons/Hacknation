"""T5: are the published sentences true as stated? describe() of hstar_value says 'exactly v Householder reflections per token
are necessary and sufficient for one layer' with no finite-state qualifier. Exact counterexamples with infinite state space
(exact rational arithmetic, arbitrary readout of h_t as the domain's own task definition allows):
 (1) k = 0 (A = I, B(s) = translation) solves Z3 'all': h_t = sum B(s), readout h mod 3;
 (2) a one-dimensional diagonal transition A(s) = 1/K in [0,1] (= diag_pos, = one generalized Householder with beta = 1 - 1/K)
     with B(s) = index(s) encodes the whole word injectively, so ANY group (here S3 'all', A5 'all') is tracked exactly with
     k = 1 < h*.  Verified exhaustively for all words up to a length bound."""
import itertools, json
from fractions import Fraction
from expressivity.groups import get_group, alphabet
from expressivity.algebra import pmul
from expressivity.domain import DOMAIN

def check_readout(G, S, step, h0, L):
    """True iff the map h_t -> g_t is a well-defined function on all states reached by words of length <= L."""
    seen = {}
    for n in range(L + 1):
        for w in itertools.product(range(len(S)), repeat=n):
            h = h0; g = G.e
            for i in w: h = step(h, i); g = pmul(S[i], g)
            if seen.setdefault(h, g) != g: return False, len(seen)
    return True, len(seen)

G = get_group("Z3"); S = alphabet(G, "all")
from expressivity.algebra import porder
B = [1 if pmul(s, s) != G.e and porder(s) == 3 and s == G.gens[0] else 2 for s in S]
ok, n = check_readout(G, S, lambda h, i: h + B[i], 0, 10)
print(f"(1) Z3 'all', A = I (zero reflections), B = {B}: readout well-defined on {n} states up to length 10: {ok}")

for gname, al, L in (("S3", "all", 7), ("A5", "cycles5", 4)):
    G = get_group(gname); S = alphabet(G, al); K = len(S) + 2
    ok, n = check_readout(G, S, lambda h, i: h / K + (i + 1), Fraction(0), L)
    print(f"(2) {gname} '{al}' ({len(S)} letters), 1-D diagonal A = 1/{K} in [0,1], B(s) = index+1: readout well-defined on {n} states up to length {L}: {ok}")

for p in ({"typ": "hstar_value", "group": "A5", "alphabet": "all", "value": 2},
          {"typ": "hstar_value", "group": "Z3", "alphabet": "all", "value": 2},
          {"typ": "diag_realisable", "family": "diag_pos", "group": "S3", "alphabet": "all", "value": False}):
    ok, why, _ = DOMAIN.check(p)
    print(json.dumps(p), "->", ok, "\n   PUBLISHED:", DOMAIN.describe(p))
print("hstar_value's sentence omits 'finite-state' and is false for exact real arithmetic; diag_realisable's sentence carries the qualifier.")
