"""Systematic certified table for the named tasks: every entry is a claim that passed DOMAIN.check (exact verifier).
  python -m expressivity.certify   -> expressivity/results/certified.json
For each (group, alphabet): lower bound (hstar_lower), the verifier's own best realisation (hstar_value search), faithful h
(h_faithful, own + GAP), the permutation-representation cost, and the diagonal-family statements."""
import json, time
from .domain import DOMAIN as D, lower_bound, search_upper
from .groups import get_group, alphabet
from .algebra import cycle_type
from .chartab import faithful_h

PAIRS = [("Z2", "all"), ("Z3", "all"), ("Z5", "all"), ("Z6", "all"), ("Z2^2", "all"), ("Z2^3", "all"),
         ("S3", "transpositions"), ("S3", "all"), ("D4", "all"), ("D5", "all"), ("Q8", "all"), ("A4", "all"), ("S4", "transpositions"),
         ("S4", "all"), ("S4", "tn"), ("A5", "c3c5"), ("S5", "tn"), ("A5", "involutions"), ("A5", "cycles3"), ("A5", "cycles5"), ("A5", "all"), ("S5", "transpositions"), ("S5", "all")]


def run():
    rows = []
    for g, a in PAIRS:
        t0 = time.time(); G = get_group(g); S = alphabet(G, a)
        lb, why = lower_bound(G, S); ub, rep, tw, ev = search_upper(G, S, stop_at=lb)
        hf, _, _ = faithful_h(G, S)
        perm_law = max(G.n - len(cycle_type(s)) for s in S)
        claims = []
        claims.append({"typ": "hstar_lower", "group": g, "alphabet": a, "k": lb})
        if ub is not None:
            claims.append({"typ": "realisation", "group": g, "alphabet": a, "k": ub, "construction": rep, "twist": tw})
            if lb == ub: claims.append({"typ": "hstar_value", "group": g, "alphabet": a, "value": ub})
        claims.append({"typ": "h_faithful", "group": g, "alphabet": a, "value": hf})
        for fam in ("diag_pos", "diag_pm", "cdiag"):
            truth = {"diag_pos": G.order == 1, "diag_pm": G.is_abelian() and G.exponent() <= 2, "cdiag": G.is_abelian()}[fam]
            claims.append({"typ": "diag_realisable", "family": fam, "group": g, "alphabet": a, "value": truth})
        checked = []
        for c in claims:
            ok, reason, evd = D.check(c, timeout=3600)        # batch run: generous wall-clock limit (load from the training grid)
            checked.append({"claim": c, "passed": bool(ok), "statement": D.describe(c) if ok else None, "reason": reason})
        rows.append({"group": g, "alphabet": a, "order": G.order, "letters": len(S), "solvable": G.is_solvable(), "abelian": G.is_abelian(),
                     "lower": lb, "upper": ub, "upper_construction": f"{rep}/{tw}", "upper_H_order": ev["H_order"] if ev else None,
                     "upper_dim": ev["dim"] if ev else None, "h_faithful": hf, "perm_law": perm_law, "exact": lb == ub,
                     "all_passed": all(x["passed"] for x in checked), "checks": checked, "sec": round(time.time() - t0, 1)})
        print(g, a, "lower", lb, "upper", ub, f"({rep}/{tw})", "h", hf, "perm", perm_law, "all passed", rows[-1]["all_passed"], flush=True)
    json.dump({"rows": rows, "selftest_cases": len(D.selftest())}, open("expressivity/results/certified.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    run()
