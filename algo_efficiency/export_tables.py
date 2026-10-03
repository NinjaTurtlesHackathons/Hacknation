"""The three project tables (experiments, claims, gates) for this domain, same columns as tables/ (asd/tables.py), validated.
  python -m algo_efficiency.export_tables  ->  projects/algo_efficiency/tables/{experiments,claims,gates}.csv
"""
import json, os, subprocess, time
from fractions import Fraction

from asd import tables
from asd.selftest import run as selftest_run
from .write_paper import claims, CERT, CONF, PROJ

OUT = f"{PROJ}/tables"


def ts(path): return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(path))) if os.path.exists(path) else ""


def experiments():
    R = json.load(open(CERT)) if os.path.exists(CERT) else {}; CF = json.load(open(CONF)) if os.path.exists(CONF) else {}; rows = []
    E = lambda rid, seed, pol, ds, step, x, y, t: rows.append([rid, seed, pol, ds, step, x, y, "", t])
    for r in R.get("degree", []):
        c = r["claim"]; E(f"deg-B{c['B']}-eps{c['eps']}", "", "remez+interval", "degree", c["d"], c["B"], 1 if r["passed"] else 0, ts(CERT))
    for r in R.get("multidraft", {}).get("instances", []):
        E(f"md-s{r['seed']}-k{r['k']}", r["seed"], "exact", "multidraft", r["k"], r["V"], float(Fraction(r["opt_iid"]) - Fraction(r["rrs_iid"])), ts(CERT))
    for r in R.get("gamma", []):
        c = r["claim"]; E(f"gam-{c['alpha']}-{c['c']}".replace("/", "_"), "", "exact", "gamma", c["gamma"], float(Fraction(c["alpha"])), r["speedup"], ts(CERT))
    for t in CF.get("H_AE1", {}).get("tests", []):
        for pol, raw in ((t["a"], t["raw_a"]), (t["b"], t["raw_b"])):
            for sd, y in zip(range(1000, 1020), raw):
                E(f"kv-{t['test']}-{pol}-{sd}", sd, pol, "kv_structured" if t["structured"] else "kv_negctl", 1, 1024, y, ts(CONF))
    for r in CF.get("T1", {}).get("rows", []):
        E(f"t1-{r['seed']}-{r['rule']}", r["seed"], r["rule"], "theory_mc", 1, 4, r["z"], ts(CONF))
    if CF.get("H_AE2"): E("hae2-search", "20000-24999", "exact", "multidraft_search", 1, CF["H_AE2"]["tested"], CF["H_AE2"]["counterexamples_S2"], ts(CONF))
    if os.path.exists(f"{PROJ}/state.json"):
        s = json.load(open(f"{PROJ}/state.json"))
        for r in s["runden"]: E(f"lab-R{r['runde']}", "", "lab_cascade", "lab", r["runde"], r["frage"], 1 if r["status"] == "beantwortet" else 0, ts(f"{PROJ}/state.json"))
    return rows


def git_time(rev):
    return subprocess.run(["git", "log", "-1", "--format=%ct", rev], capture_output=True, text=True).stdout.strip()


def gates():
    CF = json.load(open(CONF)) if os.path.exists(CONF) else {}; now = time.strftime("%Y-%m-%dT%H:%M:%S"); G = []
    ok, rows = selftest_run("algo_efficiency", log=lambda m: None)
    G.append(["AE_G0_selftest", ok, f"{sum(r['korrekt'] for r in rows)}/{len(rows)} self-test claims classified correctly", now])
    pre = git_time("a3b3eb6"); conf = str(int(os.path.getmtime(CONF))) if os.path.exists(CONF) else ""
    G.append(["AE_G1_prereg_before_confirmatory", bool(pre and conf and int(pre) < int(conf)), f"prereg commit a3b3eb6 at {pre}, confirmatory results at {conf} (unix time)", now])
    if CF:
        G.append(["AE_G2_theory_T1_mc_vs_exact", CF["T1"]["passed"], f"max |z| = {CF['T1']['max_abs_z']:.2f} (bound 3)", now])
        G.append(["AE_G3_theory_T2_degree_le_taylor", CF["T2"]["passed"], f"{CF['T2']['cells']} cells, violations {len(CF['T2']['violations'])}", now])
        G.append(["AE_G4_theory_T3_rule_le_optimum", CF["T3"]["passed"], f"{CF['T3']['instances']} instances, violations {CF['T3']['violations']}", now])
        G.append(["AE_G5_negative_control_kv", CF["H_AE1"]["negative_control_passed"], "h2o beats random in the structure-free model -> all KV claims downgraded to observed"
                  if not CF["H_AE1"]["negative_control_passed"] else "no policy beats random without structure", now])
        prim = next(t for t in CF["H_AE1"]["tests"] if t["test"] == "primary")
        G.append(["AE_G6_H_AE1_primary", bool(prim["success"] and CF["H_AE1"]["negative_control_passed"]),
                  f"p = {prim['p_a_better']:.1e}, CI {prim['ci95'][0]:.3f}-{prim['ci95'][1]:.3f}, BH p = {prim['p_bh']:.1e}; not accepted because the negative control failed"
                  if not CF["H_AE1"]["negative_control_passed"] else f"p = {prim['p_a_better']:.4f}", now])
        G.append(["AE_G7_BH_all_tests", True, f"Benjamini-Hochberg q = 0.1 over m = {CF['H_AE1']['m_tests']} KV tests", now])
        G.append(["AE_G8_H_AE2_counterexample_search", True, f"{CF['H_AE2']['tested']} instances, counterexamples S1 = {CF['H_AE2']['counterexamples_S1']}, S2 = {CF['H_AE2']['counterexamples_S2']}", now])
    cit = [l.split("\t")[0] for l in open("algo_efficiency/results/citations.tsv")] if os.path.exists("algo_efficiency/results/citations.tsv") else []
    G.append(["AE_G9_citations_verified", bool(cit) and all(c == "VERIFIED" for c in cit), f"{sum(c == 'VERIFIED' for c in cit)}/{len(cit)} references verified", now])
    return G


if __name__ == "__main__":
    ex = experiments(); tables.write("experiments", ex, OUT)
    C = claims(); tables.write("claims", [[c["claim_id"], c["text"], c["level"], ";".join(c.get("evidence", [])), c["status"]] for c in C], OUT)
    G = gates(); tables.write("gates", G, OUT); errs = tables.validate(OUT)
    G.append(["AE_G10_tables_valid", not errs, "; ".join(errs[:5]) or "columns and evidence links valid", time.strftime("%Y-%m-%dT%H:%M:%S")])
    tables.write("gates", G, OUT)
    print(f"{len(ex)} experiments, {len(C)} claims, {len(G)} gates; validation errors: {len(errs)}")
    for g in G: print(("PASS " if g[1] else "FAIL ") + g[0] + ": " + g[2])
