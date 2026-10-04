"""T4: numerical character tables (chartab) vs GAP (exact), and the branch-and-bound minimisation vs brute force.
For every group: per element g, the multiset of (codim Fix psi(g), mult of -1, g in ker psi) over real irreducibles psi must
agree between own table and GAP (matched element-wise, so class ordering cannot hide errors); FS indicators and degrees must
agree; h(G, Sigma) from both must agree for every alphabet; minimise() must equal an exhaustive search over all subsets."""
import itertools, time
from expressivity.groups import get_group, alphabet
from expressivity.chartab import codim_table, minimise, faithful_h
from expressivity.gap_oracle import codim_table_gap

def brute(codim, kernels, sc, nc, e):
    best = None; m = len(codim)
    for r in range(1, m + 1):
        for S in itertools.combinations(range(m), r):
            K = frozenset(range(nc))
            for p in S: K &= kernels[p]
            if K != frozenset([e]): continue
            v = max(sum(codim[p][c] for p in S) for c in sc)
            if best is None or v < best: best = v
    return best

groups = [f"Z{n}" for n in range(2, 13)] + [f"D{n}" for n in range(3, 9)] + ["S3", "S4", "S5", "A4", "A5", "Q8", "Z2^2", "Z2^3", "Z2^4",
          "Z2xZ4", "Z2xZ6", "Z3xZ3", "Z4xZ4", "Z3xZ6"]
ALPHS = ["all", "involutions", "transpositions", "gens", "cycles3", "cycles5"]
mism = []; t00 = time.time()
for gname in groups:
    G = get_group(gname); t0 = time.time()
    T = codim_table(G); Gp = codim_table_gap(G)
    own_sig = sorted((p["deg"], p["fs"]) for p in T["irreps"]); gap_sig = sorted((p["deg"], p["fs"]) for p in Gp["irreps"])
    issues = []
    if own_sig != gap_sig: issues.append(f"irreps differ own {own_sig} gap {gap_sig}")
    ci = T["class_index"]
    for g in G.elements:
        a = sorted((T["codim"][i][ci[g]], T["minus"][i][ci[g]], ci[g] in T["kernels"][i]) for i in range(len(T["codim"])))
        c = Gp["class_of"](g)
        b = sorted((Gp["codim"][i][c], Gp["minus"][i][c], c in Gp["kernels"][i]) for i in range(len(Gp["codim"])))
        if a != b: issues.append(f"element {g}: own {a} gap {b}"); break
    hv = {}
    for al in ALPHS:
        try: S = alphabet(G, al)
        except ValueError: continue
        own, _, _ = faithful_h(G, S)
        sc = sorted({Gp["class_of"](s) for s in S}); e = Gp["class_of"](G.e)
        gv, _ = minimise(Gp["codim"], Gp["kernels"], sc, Gp["n_classes"], e)
        bv = brute(Gp["codim"], Gp["kernels"], sc, Gp["n_classes"], e)
        sco = sorted({ci[s] for s in S}); bo = brute(T["codim"], T["kernels"], sco, len(T["classes"]), ci[G.e])
        hv[al] = (own, gv, bv, bo)
        if not (own == gv == bv == bo): issues.append(f"h mismatch {al}: own {own} gap {gv} brute(gap) {bv} brute(own) {bo}")
    print(f"{gname:6} |G|={G.order:3d} real irreps={len(T['irreps']):2d}  h(own,gap,brute,brute_own)={hv}  {'OK' if not issues else issues}  ({time.time()-t0:.1f}s)")
    if issues: mism.append((gname, issues))
print(f"\n{len(groups)} groups, mismatches: {len(mism)} ({time.time()-t00:.0f}s)")
for m in mism: print("MISMATCH", m)
