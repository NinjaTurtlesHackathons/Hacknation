"""T10: named alphabets that depend on the hidden permutation representation, not on the abstract group.
'transpositions', 'cycles3', 'cycles5' are defined by cycle type in the stored action, 'gens' by the stored generators.
For groups other than S_n/A_n the published sentence 'h*(G, transpositions)' has no representation-free meaning, and
isomorphic names (Z2^2, Z2xZ2, SG4_2) can carry different alphabets and different certified values."""
from expressivity.groups import get_group, alphabet
from expressivity.algebra import porder, cycle_type
from expressivity.chartab import faithful_h
names = ["Z2^2", "Z2xZ2", "SG4_2", "Z6", "Z2xZ3", "SG6_2", "D4", "SG8_3", "Q8", "SG8_4", "Z3", "D3", "SG6_1", "A4", "SG12_3"]
for nm in names:
    G = get_group(nm); row = []
    for a in ("gens", "transpositions", "cycles3", "involutions"):
        try:
            S = alphabet(G, a); h, _, _ = faithful_h(G, S)
            row.append(f"{a}: {len(S)} letters, orders {sorted(porder(s) for s in S)}, h={h}")
        except ValueError as e: row.append(f"{a}: refused")
    print(f"{nm:7} (|G|={G.order}, degree {G.n}): " + " | ".join(row))
