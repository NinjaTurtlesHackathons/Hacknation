"""Confirmatory runs exactly as preregistered in algo_efficiency/prereg.md (H-AE1, negative control, T1-T3, H-AE2).
  python -m algo_efficiency.confirm  ->  algo_efficiency/results/confirmatory.json
"""
import json, math, time
from fractions import Fraction

import numpy as np

from asd.stats import bh
from . import kv, spec as S
from .domain import DOMAIN as D

OUT = "algo_efficiency/results/confirmatory.json"; N, BUD = 1024, 128


def h_ae1():
    tests = [("primary", "h2o", "sink_recent", True), ("secondary_a", "sink_recent", "recent", True), ("secondary_b", "h2o", "random", True),
             ("secondary_c", "oracle", "h2o", True), ("negctl_recent", "recent", "random", False), ("negctl_sink_recent", "sink_recent", "random", False),
             ("negctl_h2o", "h2o", "random", False)]
    rows = []
    for name, a, b, structured in tests:
        r = kv.compare(a, b, N, BUD, structured=structured); rows.append({"test": name, "a": a, "b": b, "structured": structured, **r})
        print(name, a, b, round(r["err_a"], 4), round(r["err_b"], 4), r["p_a_better"], flush=True)
    rej, adj = bh([r["p_a_better"] for r in rows], q=0.1)
    for r, rj, pa in zip(rows, rej, adj):
        r["p_bh"] = float(pa); r["success"] = bool(r["p_a_better"] < 0.05 and r["ci95"][0] > 1 and pa < 0.1)
        if r["structured"]:
            ok, why, _ = D.check({"typ": "kv_compare", "policy_a": r["a"], "policy_b": r["b"], "n": N, "budget": BUD, "better": "a"})
            r["verifier"] = {"passed": bool(ok), "reason": why}
    negctl_ok = all(r["p_a_better"] > 0.05 for r in rows if not r["structured"])
    return {"tests": rows, "m_tests": len(rows), "negative_control_passed": negctl_ok}


def t1():
    out = []
    for s in range(1000, 1020):
        x = S.random_instance(V=4, seed=s); P, Q = S.parse_pair(x["p"], x["q"])
        for rule, k in (("standard", 1), ("rrs_iid", 2), ("rrs_wor", 2)):
            exact = float(S.step_output(P, Q, rule, k=k)[1]); mc = S.mc_scheme(P, Q, rule, k=k, samples=200000, seed=s)
            z = (mc["acceptance"] - exact) / max(mc["stderr"], 1e-12)
            out.append({"seed": s, "rule": rule, "exact": exact, "mc": mc["acceptance"], "z": z, "tv_mc_to_p": mc["tv_to_target"]})
    return {"rows": out, "max_abs_z": max(abs(r["z"]) for r in out), "passed": all(abs(r["z"]) < 3 for r in out)}


def t2():
    R = json.load(open("algo_efficiency/results/certified.json")).get("degree", [])
    cells = [{"B": r["claim"]["B"], "eps": r["claim"]["eps"], "d": r["claim"]["d"], "taylor": r["taylor_degree_estimate"]} for r in R if r["passed"]]
    return {"cells": len(cells), "passed": bool(cells) and all(c["taylor"] is not None and c["d"] <= c["taylor"] for c in cells),
            "violations": [c for c in cells if c["taylor"] is None or c["d"] > c["taylor"]]}


def h_ae2_and_t3():
    cnt = {"S1": [], "S2": [], "T3": []}; tested = 0; margin = {"S1": None, "S2": None}
    for seed in range(20000, 25000):
        V = 3 + seed % 5; k = 2 + (seed // 5) % 3; conc = (0.1, 0.3, 1.0, 3.0)[(seed // 15) % 4]
        if V ** k > 1300: k = 2
        x = S.random_instance(V=V, seed=seed, family="dirichlet", conc=conc); P, Q = S.parse_pair(x["p"], x["q"])
        oi = S.optimal_multidraft(P, Q, k, "iid")[0]; ow = S.optimal_multidraft(P, Q, k, "wor")[0]
        ri = S.step_output(P, Q, "rrs_iid", k=k)[1]; rw = S.step_output(P, Q, "rrs_wor", k=k)[1]; tested += 1
        for key, d in (("S1", ow - oi), ("S2", rw - ri)):
            margin[key] = d if margin[key] is None else min(margin[key], d)
            if d < 0: cnt[key].append({"seed": seed, "p": x["p"], "q": x["q"], "k": k, "iid": S.fstr(oi if key == "S1" else ri), "wor": S.fstr(ow if key == "S1" else rw)})
        if ri > oi or rw > ow: cnt["T3"].append({"seed": seed})
    for key in ("S2",):
        for c in cnt[key][:3]:   # certify reported counterexamples through the verifier
            c["check_iid"] = D.check({"typ": "scheme_acceptance", "p": c["p"], "q": c["q"], "rule": "rrs_iid", "k": c["k"], "value": c["iid"]})[:2]
            c["check_wor"] = D.check({"typ": "scheme_acceptance", "p": c["p"], "q": c["q"], "rule": "rrs_wor", "k": c["k"], "value": c["wor"]})[:2]
    return ({"tested": tested, "counterexamples_S1": len(cnt["S1"]), "counterexamples_S2": len(cnt["S2"]), "examples_S1": cnt["S1"][:3],
             "examples_S2": cnt["S2"][:3], "min_margin": {k: S.fstr(v) for k, v in margin.items()}},
            {"instances": tested, "violations": len(cnt["T3"]), "passed": not cnt["T3"]})


if __name__ == "__main__":
    t0 = time.time(); res = {"prereg": "algo_efficiency/prereg.md", "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res["H_AE1"] = h_ae1(); res["T1"] = t1(); print("T1", res["T1"]["passed"], res["T1"]["max_abs_z"], flush=True)
    res["T2"] = t2(); print("T2", res["T2"], flush=True)
    res["H_AE2"], res["T3"] = h_ae2_and_t3(); print("H_AE2", {k: v for k, v in res["H_AE2"].items() if not k.startswith("examples")}, "T3", res["T3"], flush=True)
    res["sec"] = round(time.time() - t0); json.dump(res, open(OUT, "w"), indent=1, default=str); print("saved", OUT)
