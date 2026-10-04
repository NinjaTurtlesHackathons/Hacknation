"""Atlas: Householder complexity of the word problem with the full alphabet for every group of order <= N (GAP SmallGroups).

Per group G (alphabet Sigma = G minus identity, the standard state-tracking task):
  lower  certified lower bound on h*: 1 if G is nontrivial, 2 if G has an element of order >= 3 (lemma L4)
  h      min over faithful real representations of max codim Fix: own character table AND GAP (exact); must agree
  twist  upper bound from lifts to G x Z2: each letter may be multiplied by -1, cost min(codim Fix, codim of the -1 eigenspace),
         subject to faithfulness of the twisted group (no (z, -1) in H with rho(z) = -I)
  upper  min(h, twist) for non-abelian G; for abelian G lemma L7 (count cover): 1 if exponent 2, else 2
  exact  lower == upper  (then h* is determined)
  python -m expressivity.atlas 63      -> expressivity/results/smallgroups.json, expressivity/results/atlas.json
"""
import json, os, subprocess, sys, tempfile, time

from .algebra import PermGroup, pmul, porder
from .chartab import codim_table, minimise
from .gap_oracle import GAP, _gap_perm

EXPORT = r"""
SizeScreen([60000, 1000]);;
Print("BEGIN\n");
for n in [1..%d] do
  for i in [1..NrSmallGroups(n)] do
    S := SmallGroup(n, i);
    P := Image(IsomorphismPermGroup(S));
    P := Image(SmallerDegreePermutationRepresentation(P));
    d := Maximum(1, LargestMovedPoint(P));
    gens := SmallGeneratingSet(P);
    if Length(gens) = 0 then gens := [()]; fi;
    Print("GROUP ", n, " ", i, " ", d, " ", List(gens, g -> ListPerm(g, d)), " ", ReplacedString(StructureDescription(S), " ", ""), "\n");
  od;
od;
Print("END\n");
QUIT;
"""


def export_smallgroups(N, path="expressivity/results/smallgroups.json"):
    with tempfile.NamedTemporaryFile("w", suffix=".g", delete=False) as f:
        f.write(EXPORT % N); p = f.name
    out = subprocess.run([GAP, "-q", "-b", p], capture_output=True, text=True, timeout=3600).stdout
    os.unlink(p); res = {}
    for line in out[out.index("BEGIN"):out.index("END")].splitlines()[1:]:
        _, n, i, d, rest = line.split(" ", 4)
        gens_s, name = rest.rsplit(" ", 1)
        gens = [[x - 1 for x in g] for g in json.loads(gens_s)]
        res[f"{n}_{i}"] = {"order": int(n), "id": int(i), "degree": int(d), "gens": gens, "name": name}
    json.dump(res, open(path, "w"))
    return res


def twisted_upper(G, T, sigma_classes):
    """Best upper bound over faithful sums S of real irreducibles with letter-wise sign twists (lifts to G x Z2)."""
    from itertools import combinations
    R = len(T["irreps"]); deg = [r["deg"] for r in T["irreps"]]; nc = len(T["classes"]); e = T["class_index"][G.e]
    anti = [[deg[p] - T["minus"][p][c] for c in range(nc)] for p in range(R)]
    target = frozenset([e]); best = [10 ** 9, None]
    order = sorted(range(R), key=lambda p: max(min(T["codim"][p][c], anti[p][c]) for c in sigma_classes))

    def cost(S):
        eps = {}; worst = 0
        for c in sigma_classes:
            plus = sum(T["codim"][p][c] for p in S); minus = sum(anti[p][c] for p in S)
            eps[c] = -1 if minus < plus else 1; worst = max(worst, min(plus, minus))
        # faithfulness of the twisted group: central classes acting as -I in rho_S must not be reachable with sign -1
        minusI = [c for c in range(nc) if T["class_sizes"][c] == 1 and all(T["codim"][p][c] == deg[p] and T["minus"][p][c] == deg[p] for p in S)]
        if minusI and any(v == -1 for v in eps.values()):
            cls_of = T["class_index"]; letters = [g for g in G.elements if g != G.e]
            seen = {(G.e, 1)}; frontier = [(G.e, 1)]
            while frontier:
                nxt = []
                for g, s in frontier:
                    for x in letters:
                        y = (pmul(x, g), s * eps[cls_of[x]])
                        if y not in seen: seen.add(y); nxt.append(y)
                frontier = nxt
            if any((z, -1) in seen for z in G.elements if cls_of[z] in minusI):
                return max(sum(T["codim"][p][c] for p in S) for c in sigma_classes)     # fall back to the untwisted lift (always valid)
        return worst

    def rec(start, K, chosen, lb):
        if lb >= best[0]: return
        if K == target:
            c = cost(chosen)
            if c is not None and c < best[0]: best[0], best[1] = c, list(chosen)
            return
        for j in range(start, R):
            p = order[j]; K2 = K & T["kernels"][p]
            if K2 == K: continue
            lb2 = max(lb, max(min(T["codim"][p][c], anti[p][c]) for c in sigma_classes))
            rec(j + 1, K2, chosen + [p], lb2)

    rec(0, frozenset(range(nc)), [], 0)
    return best[0], best[1]


def analyse(key, sg, gap_check=True):
    G = PermGroup(f"SG{key}", [tuple(g) for g in sg["gens"]], sg["degree"])
    t0 = time.time()
    if G.order == 1:
        return {"key": key, "name": sg["name"], "order": 1, "lower": 0, "h": 0, "upper": 0, "exact": True, "hstar": 0}
    T = codim_table(G); sigma = [g for g in G.elements if g != G.e]
    sc = sorted({T["class_index"][s] for s in sigma}); e = T["class_index"][G.e]
    h, sel = minimise(T["codim"], T["kernels"], sc, len(T["classes"]), e)
    hgap = None
    if gap_check:
        from .gap_oracle import codim_table_gap
        Tg = codim_table_gap(G); scg = sorted({Tg["class_of"](s) for s in sigma})
        hgap, _ = minimise(Tg["codim"], Tg["kernels"], scg, Tg["n_classes"], Tg["class_of"](G.e))
    tw, _ = twisted_upper(G, T, sc)
    ab = G.is_abelian(); expo = G.exponent()
    lower = 2 if expo >= 3 else 1
    if ab: upper, how = (1 if expo <= 2 else 2), "lemma L7 (count cover)"
    else: upper, how = min(h, tw), ("twisted cover" if tw < h else "faithful representation")
    return {"key": key, "name": sg["name"], "order": G.order, "abelian": ab, "solvable": G.is_solvable(), "exponent": expo,
            "n_irreps_real": len(T["irreps"]), "lower": lower, "h": h, "h_gap": hgap, "agree": hgap is None or hgap == h,
            "twist": tw, "upper": upper, "upper_method": how, "exact": lower == upper, "hstar": upper if lower == upper else None,
            "sec": round(time.time() - t0, 2)}


def main(N=63):
    N = int(N); path = "expressivity/results/smallgroups.json"
    sgs = export_smallgroups(N, path)
    rows = []
    for key, sg in sorted(sgs.items(), key=lambda kv: (kv[1]["order"], kv[1]["id"])):
        r = analyse(key, sg); rows.append(r)
        print(json.dumps(r), flush=True)
    summ = {"N": N, "groups": len(rows), "exact": sum(r["exact"] for r in rows),
            "disagreements_own_vs_gap": [r["key"] for r in rows if not r.get("agree", True)],
            "nonabelian": sum(1 for r in rows if not r.get("abelian", True)),
            "nonabelian_exact": sum(1 for r in rows if not r.get("abelian", True) and r["exact"])}
    json.dump({"summary": summ, "rows": rows}, open("expressivity/results/atlas.json", "w"), indent=1)
    print(json.dumps(summ))


if __name__ == "__main__":
    main(*sys.argv[1:])
