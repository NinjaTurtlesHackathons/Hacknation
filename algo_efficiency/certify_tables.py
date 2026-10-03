"""Systematic certified tables for the algo_efficiency domain. Every entry is a claim that passed DOMAIN.check (the same verifier
the agents face); candidates come from cheap floating-point searches. Output: algo_efficiency/results/certified.json.

  python -m algo_efficiency.certify_tables [section ...]      sections: degree rank multidraft gamma kv
"""
import json, math, os, sys, time
from fractions import Fraction

from asd.stats import bh
from . import kv, polyexp as PE, spec as S
from .domain import DOMAIN as D

OUT = "algo_efficiency/results/certified.json"


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def save(r):
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(r, open(OUT, "w"), indent=1, default=str)


def record(p):
    t0 = time.time(); ok, why, _ = D.check(p)
    return {"claim": p, "passed": bool(ok), "reason": why, "level": D.level(p), "statement": D.describe(p) if ok else None,
            "sec": round(time.time() - t0, 1)}


def degree_table():
    rows = []
    for eps in ("1e-2", "1e-3", "1e-6"):
        for B in (1, 2, 4, 8, 16):
            d = next(d for d in range(PE.D_MAX + 1) if PE.remez(Fraction(B), d)[3] < float(eps) * 0.999)   # float candidate
            r = record({"typ": "exp_min_degree", "B": B, "eps": eps, "error": "relative", "d": d})
            r["taylor_degree_estimate"] = PE.taylor_degree(B, float(eps)); rows.append(r)
            print("degree", B, eps, d, r["passed"], r["taylor_degree_estimate"], r["sec"], flush=True)
    return rows


def rank_table(deg_rows):
    rows = []
    for r in deg_rows:
        c = r["claim"]
        if not r["passed"] or c["B"] not in (1, 4, 16) or c["eps"] != "1e-3": continue
        for h in (16, 64, 128):
            rows.append({"h": h, "B": c["B"], "eps": c["eps"], "d": c["d"], "rank": math.comb(h + c["d"], c["d"]),
                         "derived_from": c, "level": "computed_rigorous",
                         "note": "C(h+d*, d*) with d* certified in the degree table; one representative re-checked as polymethod_rank"})
    rows.append(record({"typ": "polymethod_rank", "h": 64, "B": 4, "eps": "1e-3", "error": "relative",
                        "rank": next(x["rank"] for x in rows if x["h"] == 64 and x["B"] == 4)}))
    return rows


def multidraft_table(n_inst=150):
    """Seeded random instances; exact optimum (iid and wor), exact rrs_iid / rrs_wor; every value passed through DOMAIN.check."""
    inst = []
    for seed in range(n_inst):
        V = 3 + seed % 3; fam = ("dirichlet", "zipf")[seed % 2]
        x = S.random_instance(V=V, seed=seed, family=fam, conc=1.0); p, q = x["p"], x["q"]; P, Q = S.parse_pair(p, q)
        for k in (2, 3):
            row = {"seed": seed, "V": V, "family": fam, "k": k, "p": p, "q": q}
            for mode, rule in (("iid", "rrs_iid"), ("wor", "rrs_wor")):
                v, cert = S.optimal_multidraft(P, Q, k, mode); _, a = S.step_output(P, Q, rule, k=k)
                ok1 = D.check({"typ": "multidraft_optimal", "p": p, "q": q, "k": k, "mode": mode, "value": S.fstr(v)})[0]
                ok2 = D.check({"typ": "scheme_acceptance", "p": p, "q": q, "rule": rule, "k": k, "value": S.fstr(a)})[0]
                assert ok1 and ok2
                row[f"opt_{mode}"] = S.fstr(v); row[rule] = S.fstr(a)
            inst.append(row)
    F = lambda s: Fraction(s); summary = {}
    for k in (2, 3):
        R = [r for r in inst if r["k"] == k]
        gi = [F(r["opt_iid"]) - F(r["rrs_iid"]) for r in R]; gw = [F(r["opt_wor"]) - F(r["rrs_wor"]) for r in R]
        summary[k] = {"instances": len(R),
                      "rrs_iid_optimal": sum(g == 0 for g in gi), "rrs_wor_optimal": sum(g == 0 for g in gw),
                      "max_gap_iid": S.fstr(max(gi)), "mean_gap_iid": float(sum(gi) / len(gi)),
                      "max_gap_wor": S.fstr(max(gw)), "mean_gap_wor": float(sum(gw) / len(gw)),
                      "opt_wor_ge_opt_iid": sum(F(r["opt_wor"]) >= F(r["opt_iid"]) for r in R),
                      "rrs_wor_ge_rrs_iid": sum(F(r["rrs_wor"]) >= F(r["rrs_iid"]) for r in R),
                      "rrs_wor_ge_opt_iid": sum(F(r["rrs_wor"]) >= F(r["opt_iid"]) for r in R)}
        worst = max(R, key=lambda r: F(r["opt_iid"]) - F(r["rrs_iid"]))
        summary[k]["worst_iid_instance"] = record({"typ": "scheme_optimal", "p": worst["p"], "q": worst["q"], "k": k, "rule": "rrs_iid", "optimal": False})
        summary[k]["worst_iid_values"] = {"opt_iid": worst["opt_iid"], "rrs_iid": worst["rrs_iid"], "seed": worst["seed"]}
        worst_w = max(R, key=lambda r: F(r["opt_wor"]) - F(r["rrs_wor"]))
        summary[k]["worst_wor_instance"] = record({"typ": "scheme_optimal", "p": worst_w["p"], "q": worst_w["q"], "k": k, "rule": "rrs_wor", "optimal": worst_w["opt_wor"] == worst_w["rrs_wor"]})
        summary[k]["worst_wor_values"] = {"opt_wor": worst_w["opt_wor"], "rrs_wor": worst_w["rrs_wor"], "seed": worst_w["seed"]}
        print("multidraft", k, {a: b for a, b in summary[k].items() if not a.startswith("worst")}, flush=True)
    return {"instances": inst, "summary": summary,
            "note": "instances: seeds 0..%d, V = 3 + seed mod 3, family alternates dirichlet/zipf, denominators 1000; all values exact" % (n_inst - 1)}


def gamma_table():
    rows = []
    for a in ("1/2", "3/5", "7/10", "4/5", "9/10", "19/20"):
        for c in ("1/100", "1/20", "1/10", "1/4"):
            arg, best, _ = S.optimal_gamma(a, c)
            r = record({"typ": "optimal_gamma", "alpha": a, "c": c, "gamma": arg[0]}); r["speedup"] = float(best); rows.append(r)
    print("gamma", [(r["claim"]["alpha"], r["claim"]["c"], r["claim"]["gamma"]) for r in rows], flush=True)
    return rows


def kv_table(n=512, budget=64):
    pols = [p for p in kv.POLICIES]; tests = []
    for i, a in enumerate(pols):
        for b in pols[i + 1:]:
            r = kv.compare(a, b, n, budget); better, worse = (a, b) if r["err_a"] < r["err_b"] else (b, a)
            r2 = kv.compare(better, worse, n, budget); tests.append({"better": better, "worse": worse, **r2})
    rej, adj = bh([t["p_a_better"] for t in tests], q=0.1)
    for t, rj, pa in zip(tests, rej, adj): t["p_bh"] = float(pa); t["bh_reject_q0.1"] = bool(rj)
    checks = [record({"typ": "kv_compare", "policy_a": t["better"], "policy_b": t["worse"], "n": n, "budget": budget, "better": "a"})
              for t in tests]
    errs = {p: kv.compare(p, "random" if p != "random" else "oracle", n, budget)["err_a"] for p in pols}
    print("kv", errs, flush=True)
    return {"tests": tests, "checks": checks, "mean_error": errs, "m_tests": len(tests)}


if __name__ == "__main__":
    secs = sys.argv[1:] or ["degree", "rank", "multidraft", "gamma", "kv"]; R = load()
    if "degree" in secs: R["degree"] = degree_table(); save(R)
    if "rank" in secs: R["rank"] = rank_table(R["degree"]); save(R)
    if "multidraft" in secs: R["multidraft"] = multidraft_table(); save(R)
    if "gamma" in secs: R["gamma"] = gamma_table(); save(R)
    if "kv" in secs: R["kv"] = kv_table(); save(R)
    print("saved", OUT)
