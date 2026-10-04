"""Red-team check for Lemma L3 under the trained architecture's conventions: state S in R^{dv x dk} starts at S_0 = 0 and is
updated from the right, S <- S (I - beta k k^T) + beta v k^T. L3 as written uses a generic h_0 and B = 0, which is not
available when S_0 = 0. Fix tested here: choose a generic row c and v = -(c k) for every factor; then S_t + c = c rho(x_t)
(row action), so S_t determines x_t. Instance: S5 / transpositions, rho = permutation representation (one reflection per
letter, beta = 2, k = (e_i - e_j)/sqrt 2), exact over Q(sqrt 2) avoided by using k k^T = (e_i - e_j)(e_i - e_j)^T / 2.
Run: python3 -m expressivity.analysis.redteam.t14_zero_init
"""
import itertools
import random
from fractions import Fraction as F

n = 5
letters = [(i, j) for i in range(n) for j in range(i + 1, n)]


def step(S, ij):
    i, j = ij
    kkT = [[F(0)] * n for _ in range(n)]
    for a, sa in ((i, 1), (j, -1)):
        for b, sb in ((i, 1), (j, -1)):
            kkT[a][b] = F(sa * sb, 2)
    beta = F(2)
    c = C0
    # S' = S - beta (S k - v) k^T with v = -(c k)  <=>  S' = S - beta (S + c) k k^T
    Sc = [S[a] + c[a] for a in range(n)]
    return tuple(S[b] - beta * sum(Sc[a] * kkT[a][b] for a in range(n)) for b in range(n))


def perm_of(word):
    p = list(range(n))
    for (i, j) in word:  # g_t = s_t ... s_1 as right action on the row: track the composite permutation
        p = [p[k] for k in range(n)]
        p[i], p[j] = p[j], p[i]
    return tuple(p)


random.seed(0)
C0 = [F(random.randint(1, 10 ** 6)) for _ in range(n)]
seen = {}
ok = True
S0 = tuple(F(0) for _ in range(n))
frontier = [(S0, ())]
visited = {(S0, tuple(range(n)))}
while frontier:
    nf = []
    for S, w in frontier:
        for s in letters:
            S2 = step(S, s); g2 = perm_of(w + (s,))
            if S2 in seen and seen[S2] != g2: ok = False
            seen[S2] = g2
            if (S2, g2) not in visited:
                visited.add((S2, g2)); nf.append((S2, w + (s,)))
    frontier = nf
print(f"S5/transpositions, S_0 = 0, v = -(c k): reachable states {len(seen)}, readout consistent: {ok}, |S5| = 120")
