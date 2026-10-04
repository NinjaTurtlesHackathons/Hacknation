"""Named finite groups (as permutation groups) and named input alphabets for word problems."""
import re
from functools import lru_cache
from .algebra import PermGroup, from_cycles, porder, cycle_type, pid, pmul


def _cyclic(n): return [from_cycles(n, list(range(n)))] if n > 1 else [pid(1)]


EXPECTED_ORDER = [(r"Z(\d+)", lambda m: int(m[1])), (r"Z2\^(\d+)", lambda m: 2 ** int(m[1])), (r"Z(\d+)xZ(\d+)", lambda m: int(m[1]) * int(m[2])),
                  (r"S(\d+)", lambda m: __import__("math").factorial(int(m[1]))), (r"A(\d+)", lambda m: __import__("math").factorial(int(m[1])) // 2),
                  (r"D(\d+)", lambda m: 2 * int(m[1])), (r"Q8", lambda m: 8)]


@lru_cache(maxsize=None)
def get_group(name):
    """Named group with a size check: the order of the constructed permutation group must equal the order the name denotes
    (red-team bug 1: S1, D1, D2 were built as the wrong groups)."""
    G = _build(name)
    for pat, order in EXPECTED_ORDER:
        m = re.fullmatch(pat, name)
        if m and G.order != order(m): raise ValueError(f"{name}: constructed order {G.order} != {order(m)}")
    return G


def _build(name):
    """Z<n>, Z2^<k>, Z<a>xZ<b>, S<n>, A<n>, D<n> (dihedral of order 2n), Q8, SG<n>_<i> (GAP SmallGroup, needs results/smallgroups.json)."""
    m = re.fullmatch(r"Z(\d+)", name)
    if m:
        if int(m.group(1)) < 2: raise ValueError("Z<n> needs n >= 2")
        return PermGroup(name, _cyclic(int(m.group(1))))
    m = re.fullmatch(r"Z2\^(\d+)", name)
    if m:
        k = int(m.group(1)); n = 2 * k
        return PermGroup(name, [from_cycles(n, [2 * i, 2 * i + 1]) for i in range(k)])
    m = re.fullmatch(r"Z(\d+)xZ(\d+)", name)
    if m:
        a, b = int(m.group(1)), int(m.group(2)); n = a + b
        return PermGroup(name, [from_cycles(n, list(range(a))), from_cycles(n, list(range(a, a + b)))])
    m = re.fullmatch(r"S(\d+)", name)
    if m:
        n = int(m.group(1))
        if n < 3: raise ValueError("S<n> needs n >= 3 (use Z2)")
        return PermGroup(name, [from_cycles(n, [0, 1]), from_cycles(n, list(range(n)))])
    m = re.fullmatch(r"A(\d+)", name)
    if m:
        n = int(m.group(1))
        if n < 3: raise ValueError("A<n> needs n >= 3")
        return PermGroup(name, [from_cycles(n, [0, 1, i]) for i in range(2, n)])
    m = re.fullmatch(r"D(\d+)", name)
    if m:
        n = int(m.group(1))
        if n < 3: raise ValueError("D<n> needs n >= 3")
        refl = tuple((-i) % n for i in range(n))
        return PermGroup(name, [from_cycles(n, list(range(n))), refl])
    if name == "Q8":
        # regular representation of the quaternion group on 8 points: elements ±1, ±i, ±j, ±k
        mult = _quat_table()
        gi = tuple(mult[2][x] for x in range(8)); gj = tuple(mult[4][x] for x in range(8))
        return PermGroup(name, [gi, gj])
    m = re.fullmatch(r"SG(\d+)_(\d+)", name)
    if m:
        import json, os
        path = os.path.join(os.path.dirname(__file__), "results", "smallgroups.json")
        sg = json.load(open(path))[f"{m.group(1)}_{m.group(2)}"]
        return PermGroup(name, [tuple(g) for g in sg["gens"]], sg["degree"])
    raise ValueError(f"unknown group {name}")


def _quat_table():
    # index: 0:1 1:-1 2:i 3:-i 4:j 5:-j 6:k 7:-k ; mult[a][b] = a*b (left multiplication table)
    base = {("1", x): x for x in "1ijk"}
    t = {("i", "i"): "-1", ("j", "j"): "-1", ("k", "k"): "-1", ("i", "j"): "k", ("j", "k"): "i", ("k", "i"): "j",
         ("j", "i"): "-k", ("k", "j"): "-i", ("i", "k"): "-j"}
    names = ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]
    def mul(a, b):
        sa = -1 if a.startswith("-") else 1; sb = -1 if b.startswith("-") else 1
        a, b = a.lstrip("-"), b.lstrip("-")
        r = base.get((a, b)) or base.get((b, a)) if "1" in (a, b) else t[(a, b)]
        if a == "1": r = b
        elif b == "1": r = a
        sr = -1 if r.startswith("-") else 1; r = r.lstrip("-")
        s = sa * sb * sr
        return ("-" if s < 0 else "") + r if r != "1" else ("-1" if s < 0 else "1")
    return [[names.index(mul(a, b)) for b in names] for a in names]


def alphabet(G, name):
    """Named generating alphabets: all (every non-identity element), involutions, transpositions, gens (the stored generators),
    cycles3, cycles5, or 'list:<i>,<j>,...' (indices into G.elements)."""
    E = [g for g in G.elements if g != G.e]
    if name == "all": S = E
    elif name == "involutions": S = [g for g in E if porder(g) == 2]
    elif name == "transpositions":
        if not re.fullmatch(r"S\d+", G.name): raise ValueError("alphabet 'transpositions' is defined only for S<n> (it depends on the permutation action)")
        S = [g for g in E if cycle_type(g)[:2] == (2, 1) or cycle_type(g) == (2,)]
    elif name == "gens": S = sorted(set(G.gens) - {G.e})
    elif name in ("cycles3", "cycles5") and not re.fullmatch(r"[AS]\d+", G.name):
        raise ValueError(f"alphabet '{name}' is defined only for A<n>, S<n>")
    elif name == "cycles3": S = [g for g in E if cycle_type(g)[0] == 3 and sum(x for x in cycle_type(g) if x > 1) == 3]
    elif name == "cycles5": S = [g for g in E if cycle_type(g)[0] == 5]
    elif name == "tn":                      # S<n>: one transposition and one n-cycle (the generator format of Howe 2026)
        if not re.fullmatch(r"S\d+", G.name): raise ValueError("alphabet 'tn' is defined only for S<n>")
        S = [from_cycles(G.n, [0, 1]), from_cycles(G.n, list(range(G.n)))]
    elif name == "c3c5":                    # A5: one 3-cycle and one 5-cycle (the generator format of Howe 2026)
        if G.name != "A5": raise ValueError("alphabet 'c3c5' is defined only for A5")
        S = [from_cycles(5, [0, 1, 2]), from_cycles(5, [0, 1, 2, 3, 4])]
    elif name.startswith("list:"): S = [G.elements[int(i)] for i in name[5:].split(",")]
    else: raise ValueError(f"unknown alphabet {name}")
    if not S: raise ValueError(f"empty alphabet {name} for {G.name}")
    from .algebra import closure
    if len(closure(S, G.n)) != G.order: raise ValueError(f"alphabet {name} does not generate {G.name}")
    return S
