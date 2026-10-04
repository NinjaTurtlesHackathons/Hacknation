"""Predictions for the preregistered grid, computed by code from certified quantities (written BEFORE any confirmatory run).

Our predictor (ALG): one-layer success iff the architecture's algebraic budget covers the task:
  diag_pos: G trivial; diag_pm: G elementary abelian 2-group; hhK: K >= h*(G, Sigma) (undetermined if lower < K < upper);
  lstm: always (nonlinear RNN, positive control).
Baselines (dumbest working predictors from the current debate):
  B1 circuit class: success iff G is solvable (non-solvable word problems are NC1-complete), for every architecture
  B2 abelian:       success iff G is abelian
  B3 size:          success iff |G| <= 24
  B4 representation law in the task's own (permutation) representation (closest prior work, Howe 2026, arXiv:2609.18966):
                    hhK succeeds iff K >= max_s rank(P(s) - I) for the permutation matrices P of G's defining action;
                    diagonal and lstm cells as ALG (B4 makes no statement about them)
  B5 faithful-only: hhK succeeds iff K >= h(G, Sigma) (minimum over faithful representations of G, no covering group);
                    other cells as ALG
"""
import json, sys
from .groups import get_group, alphabet
from .domain import DOMAIN, lower_bound, search_upper
from .algebra import cycle_type
from .chartab import faithful_h

TASKS = [("Z2", "all"), ("Z3", "all"), ("Z2^3", "all"), ("S3", "transpositions"), ("S3", "all"),
         ("A5", "involutions"), ("A5", "all"), ("S5", "transpositions"), ("S5", "all")]
ARCHS = ["diag_pos", "diag_pm", "hh1", "hh2", "hh3", "hh4", "lstm"]


def task_facts(g, a):
    G = get_group(g); S = alphabet(G, a)
    lb, why = lower_bound(G, S); ub, rep, tw, ev = search_upper(G, S)
    hf, _, _ = faithful_h(G, S)
    perm_law = max(G.n - len(cycle_type(s)) for s in S)            # rank(P(s) - I) = n - #cycles
    return {"group": g, "alphabet": a, "order": G.order, "letters": len(S), "abelian": G.is_abelian(), "solvable": G.is_solvable(),
            "exp2_abelian": G.is_abelian() and G.exponent() <= 2, "hstar_lower": lb, "hstar_upper": ub, "upper_construction": f"{rep}/{tw}",
            "upper_H_order": ev["H_order"] if ev else None, "upper_dim": ev["dim"] if ev else None, "h_faithful": hf, "perm_law": perm_law}


def predict(f, arch):
    """Returns dict predictor -> True/False/None (None = undetermined)."""
    out = {}
    if arch == "diag_pos": alg = f["order"] == 1
    elif arch == "diag_pm": alg = f["exp2_abelian"]
    elif arch == "lstm": alg = True
    else:
        K = int(arch[2:])
        alg = True if K >= f["hstar_upper"] else (False if K < f["hstar_lower"] else None)
    out["ALG"] = alg
    out["B1_circuit"] = f["solvable"]
    out["B2_abelian"] = f["abelian"]
    out["B3_size"] = f["order"] <= 24
    if arch.startswith("hh"):
        K = int(arch[2:]); out["B4_perm_law"] = K >= f["perm_law"]; out["B5_faithful"] = K >= f["h_faithful"]
    else:
        out["B4_perm_law"] = alg; out["B5_faithful"] = alg
    return out


def main(path="expressivity/results/predictions.json"):
    facts = [task_facts(g, a) for g, a in TASKS]
    cells = [{"arch": arch, **{k: f[k] for k in ("group", "alphabet")}, "pred": predict(f, arch)} for f in facts for arch in ARCHS]
    json.dump({"tasks": facts, "archs": ARCHS, "cells": cells}, open(path, "w"), indent=1)
    for f in facts: print(json.dumps(f))
    print("undetermined ALG cells:", [(c["arch"], c["group"], c["alphabet"]) for c in cells if c["pred"]["ALG"] is None])


if __name__ == "__main__":
    main(*sys.argv[1:])
