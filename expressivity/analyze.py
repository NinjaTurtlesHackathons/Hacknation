"""Preregistered analysis of the confirmatory grid (prereg.md, H-EX1). Criteria are read from prereg.md's constants below and
were fixed before the run.
  python -m expressivity.analyze   -> expressivity/results/confirmatory.json
"""
import glob, json, os
import numpy as np
from scipy.stats import fisher_exact, binomtest

from asd.stats import bh
from .confirm import OUT, path, NEG
from .predict import TASKS, ARCHS

THRESH = 0.90; MIN_SEEDS = 10
PRIMARY = "acc_T512_pos257-512"; SECONDARY = "acc_T1024_pos897-1024"; INDIST = "acc_T64_pos1-64"
DISC = [("D1", ("hh1", "A5", "involutions"), ("hh1", "A5", "all")),
        ("D2", ("hh2", "A5", "all"), ("hh1", "A5", "all")),
        ("D3", ("hh1", "Z2^3", "all"), ("hh1", "Z3", "all")),
        ("D4", ("hh1", "S5", "transpositions"), ("hh1", "S5", "all")),
        ("D5", ("hh1", "Z2", "all"), ("hh1", "Z3", "all")),
        ("D6", ("diag_pm", "Z2^3", "all"), ("diag_pm", "Z3", "all"))]
PREDICTORS = ["ALG", "B1_circuit", "B2_abelian", "B3_size", "B4_perm_law", "B5_faithful"]


def load(arch, g, a, rnd=False):
    p = path(arch, g, a, rnd)
    return json.load(open(p)) if os.path.exists(p) else None


def successes(r, key=PRIMARY):
    return int(sum(x >= THRESH for x in r[key]))


def main():
    pred = {(c["arch"], c["group"], c["alphabet"]): c["pred"] for c in json.load(open("expressivity/results/predictions.json"))["cells"]}
    cells = []; missing = []
    for g, a in TASKS:
        for arch in ARCHS:
            r = load(arch, g, a)
            if r is None: missing.append((arch, g, a)); continue
            s1 = successes(r); s2 = successes(r, SECONDARY)
            cells.append({"arch": arch, "group": g, "alphabet": a, "succ_primary": s1, "succ_secondary": s2, "n": len(r[PRIMARY]),
                          "outcome": s1 >= MIN_SEEDS, "mean_primary": float(np.mean(r[PRIMARY])), "median_primary": float(np.median(r[PRIMARY])),
                          "mean_secondary": float(np.mean(r[SECONDARY])), "mean_indist": float(np.mean(r[INDIST])),
                          "indist_success": int(sum(x >= THRESH for x in r[INDIST])), "chance": r["chance"], "pred": pred[(arch, g, a)]})
    acc = {}
    for P in PREDICTORS:
        det = [c for c in cells if c["pred"]["ALG"] is not None]
        acc[P] = {"correct": sum(c["pred"][P] == c["outcome"] for c in det), "cells": len(det)}
    tests = []
    idx = {(c["arch"], c["group"], c["alphabet"]): c for c in cells}
    for name, A, B in DISC:
        if A in idx and B in idx:
            ca, cb = idx[A], idx[B]
            table = [[ca["succ_primary"], ca["n"] - ca["succ_primary"]], [cb["succ_primary"], cb["n"] - cb["succ_primary"]]]
            p = fisher_exact(table, alternative="greater")[1]
            tests.append({"test": name, "cell": A, "control": B, "succ": [ca["succ_primary"], cb["succ_primary"]], "p": float(p)})
    neg = []
    for arch, g, a in NEG:
        r = load(arch, g, a, True)
        if r is None: continue
        s = successes(r); p = binomtest(s, len(r[PRIMARY]), 0.05, alternative="greater").pvalue
        neg.append({"cell": (arch, g, a), "succ": s, "n": len(r[PRIMARY]), "mean_primary": float(np.mean(r[PRIMARY])), "chance": r["chance"], "p": float(p)})
        tests.append({"test": f"NC-{arch}-{g}", "cell": (arch, g, a), "succ": [s], "p": float(p), "negative_control": True})
    rej, adj = bh([t["p"] for t in tests], q=0.1) if tests else ([], [])
    for t, r_, a_ in zip(tests, rej, adj): t["bh_reject"] = bool(r_); t["p_bh"] = float(a_)
    alg = acc["ALG"]["correct"]
    gate_acc = all(alg > acc[P]["correct"] for P in PREDICTORS[1:])
    disc_ok = all(t["bh_reject"] for t in tests if t["test"].startswith("D")) and len([t for t in tests if t["test"].startswith("D")]) == 6
    nc_ok = all(n["succ"] == 0 for n in neg) and all(not t["bh_reject"] for t in tests if t.get("negative_control"))
    out = {"criteria": {"threshold": THRESH, "min_seeds": MIN_SEEDS, "primary": PRIMARY, "secondary": SECONDARY},
           "cells": cells, "missing": missing, "accuracy": acc, "tests": tests, "negative_control": neg,
           "gates": {"H-EX1.1_accuracy_beats_all_baselines": gate_acc, "H-EX1.2_discriminating_tests_BH": disc_ok,
                     "negative_control_clean": nc_ok, "H-EX1_success": gate_acc and disc_ok and nc_ok}}
    json.dump(out, open("expressivity/results/confirmatory.json", "w"), indent=1, default=str)
    print(json.dumps({"accuracy": acc, "gates": out["gates"], "missing": len(missing)}, indent=1, default=str))
    for c in cells:
        print(f"{c['arch']:9s} {c['group']:5s} {c['alphabet']:15s} succ {c['succ_primary']:2d}/20 (8x {c['succ_secondary']:2d}) indist {c['mean_indist']:.2f} "
              f"mean {c['mean_primary']:.3f} ALG {c['pred']['ALG']} B4 {c['pred']['B4_perm_law']} -> {c['outcome']}")
    for t in tests: print(t)


if __name__ == "__main__":
    main()
