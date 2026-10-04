"""T11: own numerical h(G, Sigma) vs GAP-exact h for every SmallGroup in results/smallgroups.json (orders <= 63), alphabets
all / gens / involutions. Any disagreement or numerical refusal is listed."""
import json, os, time
from expressivity.groups import get_group, alphabet
from expressivity.chartab import faithful_h, minimise
from expressivity.gap_oracle import codim_table_gap
sg = json.load(open(os.path.join("expressivity", "results", "smallgroups.json")))
keys = sorted(sg, key=lambda k: tuple(map(int, k.split("_"))))
dis = []; ref = []; n = 0; t0 = time.time()
for k in keys:
    G = get_group("SG" + k)
    if G.order == 1: continue
    try: Gp = codim_table_gap(G)
    except Exception as e: ref.append((k, "gap", str(e)[:60])); continue
    for a in ("all", "gens", "involutions"):
        try: S = alphabet(G, a)
        except ValueError: continue
        try: own, _, _ = faithful_h(G, S)
        except Exception as e: ref.append((k, a, f"{type(e).__name__}: {e}"[:80])); continue
        sc = sorted({Gp["class_of"](s) for s in S}); gv, _ = minimise(Gp["codim"], Gp["kernels"], sc, Gp["n_classes"], Gp["class_of"](G.e))
        n += 1
        if own != gv: dis.append((k, a, own, gv))
print(f"{n} (group, alphabet) pairs over {len(keys)} SmallGroups; disagreements own vs GAP: {dis}; own refusals: {ref}  ({time.time()-t0:.0f}s)")
