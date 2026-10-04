"""h*(Q8, all) <= 3: cover H = C4:C4 = <a, b | a^4 = b^4 = 1, b a b^-1 = a^-1> (SmallGroup(16,4)) -> Q8, a -> i, b -> j,
kernel <a^2 b^2>. Faithful rational 4-dim representation rho1 + rho2 with rho1(a) = R (rotation by 90 degrees),
rho1(b) = F = diag(1,-1) (dihedral), rho2(a) = I, rho2(b) = R. Lifts: -1 -> a^2, +-i -> a^{+-1}, +-j -> b, b a^2, +-k -> ab, a^3 b."""
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from expressivity.domain import DOMAIN as D
from expressivity.groups import get_group, alphabet

R = [[0, -1], [1, 0]]; F = [[1, 0], [0, -1]]; I2 = [[1, 0], [0, 1]]


def mm(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]


def block(X, Y): return [X[0] + [0, 0], X[1] + [0, 0], [0, 0] + Y[0], [0, 0] + Y[1]]


A = block(R, I2); B = block(F, R)
def word(s):
    M = block(I2, I2)
    for ch in s: M = mm(M, A if ch == "a" else B)
    return M

LIFT = {"-1": "aa", "i": "a", "-i": "aaa", "j": "b", "-j": "baa", "k": "ab", "-k": "aaab"}
NAMES = ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]
G = get_group("Q8"); S = alphabet(G, "all")
mats = [[[str(x) for x in row] for row in word(LIFT[NAMES[s[0]]])] for s in S]
claim = {"typ": "realisation_matrices", "group": "Q8", "alphabet": "all", "k": 3, "matrices": mats}
res = D.check(claim); print(res[0], res[1]); print(json.dumps(claim))
claim2 = dict(claim, k=2); print("k=2 with the same matrices:", D.check(claim2)[:2])
