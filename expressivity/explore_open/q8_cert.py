"""Explicit rational 4x4 realisation of Q8 (alphabet 'all') by quaternion multiplication; checks it with the exact verifier."""
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from expressivity.domain import DOMAIN as D
from expressivity.groups import get_group, alphabet

NAMES = ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]
UNIT = {"1": (1, 0, 0, 0), "i": (0, 1, 0, 0), "j": (0, 0, 1, 0), "k": (0, 0, 0, 1)}


def qmul(a, b):
    a0, a1, a2, a3 = a; b0, b1, b2, b3 = b
    return (a0*b0 - a1*b1 - a2*b2 - a3*b3, a0*b1 + a1*b0 + a2*b3 - a3*b2,
            a0*b2 - a1*b3 + a2*b0 + a3*b1, a0*b3 + a1*b2 - a2*b1 + a3*b0)


def quat(name):
    s = -1 if name.startswith("-") else 1
    return tuple(s * x for x in UNIT[name.lstrip("-")])


def matrix(q, side):
    basis = [UNIT[n] for n in "1ijk"]
    cols = [qmul(q, e) if side == "left" else qmul(e, q) for e in basis]
    return [[str(cols[c][r]) for c in range(4)] for r in range(4)]


G = get_group("Q8"); S = alphabet(G, "all")
for side in ("left", "right"):
    mats = [matrix(quat(NAMES[s[0]]), side) for s in S]
    claim = {"typ": "realisation_matrices", "group": "Q8", "alphabet": "all", "k": 4, "matrices": mats}
    res = D.check(claim)
    print(side, res[0], res[1])
    if res[0]:
        print(json.dumps(claim))
        break
