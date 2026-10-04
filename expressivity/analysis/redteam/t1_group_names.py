"""T1: do the group names accepted by GROUP_RE denote the groups their names claim?
Independent expectations: order and abelian/exponent from textbook formulas; then run check()/describe() on claims that
exploit any mismatch."""
import json
from math import factorial
from expressivity.domain import DOMAIN, GROUP_RE
from expressivity.groups import get_group

def expected(name):
    import re
    if m := re.fullmatch(r"Z(\d+)", name): n = int(m[1]); return n, True
    if m := re.fullmatch(r"Z2\^(\d+)", name): return 2 ** int(m[1]), True
    if m := re.fullmatch(r"Z(\d+)xZ(\d+)", name): return int(m[1]) * int(m[2]), True
    if m := re.fullmatch(r"S(\d+)", name): n = int(m[1]); return factorial(n), n <= 2
    if m := re.fullmatch(r"A(\d+)", name): n = int(m[1]); return factorial(n) // 2, n <= 3
    if m := re.fullmatch(r"D(\d+)", name): n = int(m[1]); return 2 * n, n <= 2
    if name == "Q8": return 8, False

names = ["S1", "S2", "S3", "S4", "S5", "A3", "A4", "A5", "D1", "D2", "D3", "D4", "D8", "Q8", "Z0", "Z1", "Z2", "Z12",
         "Z1xZ3", "Z2xZ2", "Z2xZ4", "Z3xZ3", "Z2^1", "Z2^3", "Z0xZ3"]
bad = []
print(f"{'name':8} {'regex':5} {'order':>6} {'expected':>8} {'abelian':>7} {'exp.ab':>6}")
for nm in names:
    G = get_group(nm); eo, ea = expected(nm)
    ok = (G.order == eo and G.is_abelian() == ea)
    print(f"{nm:8} {bool(GROUP_RE.match(nm))!s:5} {G.order:6d} {eo:8d} {G.is_abelian()!s:>7} {ea!s:>6} {'' if ok else '<-- MISMATCH'}")
    if not ok and GROUP_RE.match(nm): bad.append(nm)
# Q8 sanity: unique involution, 6 elements of order 4
from expressivity.algebra import porder
Q = get_group("Q8"); from collections import Counter
print("Q8 element orders:", dict(Counter(porder(g) for g in Q.elements)))

print("\nClaims exploiting the mismatches:")
claims = [
    {"typ": "hstar_value", "group": "S1", "alphabet": "all", "value": 1},
    {"typ": "diag_realisable", "family": "diag_pos", "group": "S1", "alphabet": "all", "value": False},
    {"typ": "h_faithful", "group": "D2", "alphabet": "all", "value": 1},
    {"typ": "hstar_value", "group": "D2", "alphabet": "all", "value": 1},
    {"typ": "realisation", "group": "D2", "alphabet": "all", "k": 1, "construction": "perm", "twist": "none"},
    {"typ": "h_faithful", "group": "Z2xZ2", "alphabet": "all", "value": 1},
    {"typ": "h_faithful", "group": "Z2xZ2", "alphabet": "all", "value": 2},
]
for p in claims:
    ok, why, _ = DOMAIN.check(p)
    print(json.dumps(p), "->", ok, "|", why[:150])
    if ok: print("   PUBLISHED:", DOMAIN.describe(p))
print("\nmismatching accepted names:", bad)
