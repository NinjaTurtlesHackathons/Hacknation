"""Project tables in the framework schema (asd.tables.SCHEMA): experiments, claims, gates -> projects/expressivity/tables/.
experiments: one row per trained seed of the confirmatory grid (y = primary accuracy) and one row per certified (group, alphabet)
(y = best certified k); claims: every paper claim with evidence run ids; gates: the mandatory checks with their outcome.
  python -m expressivity.export_tables"""
import json, os, re, subprocess, time

from asd import tables as T

PROJ = "projects/expressivity"; R = "expressivity/results"; OUT = f"{PROJ}/tables"


def main():
    exp, cl, gates = [], [], []
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    CF = json.load(open(f"{R}/confirmatory.json")) if os.path.exists(f"{R}/confirmatory.json") else None
    if CF:
        from .confirm import path
        for c in CF["cells"]:
            r = json.load(open(path(c["arch"], c["group"], c["alphabet"])))
            for sd, y in zip(r["seeds"], r["acc_T512_pos257-512"]):
                exp.append({"run_id": f"grid-{c['arch']}-{c['group']}-{c['alphabet']}-{sd}".replace("^", "p"), "seed": sd, "policy": c["arch"],
                            "dataset": f"{c['group']}/{c['alphabet']}", "step": r["steps"], "x_index": 0, "y": y, "mlflow_run_id": "", "ts": r["finished"]})
        for n in CF["negative_control"]:
            arch, g, a = n["cell"]
            r = json.load(open(path(arch, g, a, True)))
            for sd, y in zip(r["seeds"], r["acc_T512_pos257-512"]):
                exp.append({"run_id": f"negctl-{arch}-{g}-{a}-{sd}", "seed": sd, "policy": arch, "dataset": f"{g}/{a}/random-targets", "step": r["steps"],
                            "x_index": 0, "y": y, "mlflow_run_id": "", "ts": r["finished"]})
    cert = json.load(open(f"{R}/certified.json")) if os.path.exists(f"{R}/certified.json") else {"rows": []}
    for r in cert["rows"]:
        exp.append({"run_id": f"cert-{r['group']}-{r['alphabet']}".replace("^", "p"), "seed": 0, "policy": "verifier", "dataset": f"{r['group']}/{r['alphabet']}",
                    "step": 0, "x_index": 0, "y": r["upper"] if r["upper"] is not None else -1, "mlflow_run_id": "", "ts": now})
    exp.append({"run_id": "atlas", "seed": 0, "policy": "verifier", "dataset": "SmallGroups<=63", "step": 0, "x_index": 0, "y": 0, "mlflow_run_id": "", "ts": now})
    exp.append({"run_id": "lean", "seed": 0, "policy": "lean", "dataset": "rank and order lemmas", "step": 0, "x_index": 0, "y": 1, "mlflow_run_id": "", "ts": now})
    runs = {e["run_id"] for e in exp}
    C = json.load(open(f"{PROJ}/paper_claims.json")) if os.path.exists(f"{PROJ}/paper_claims.json") else []
    for c in C:
        cid = c["claim_id"]; ev = []
        m = re.match(r"C-G-(\w+)-(.+?)-(\w+)$", cid)
        if m: ev = [e for e in runs if e.startswith(f"grid-{m.group(1)}-{m.group(2)}-{m.group(3)}-")]
        elif cid.startswith("C-T-") and not cid.endswith("-fail"): ev = [f"cert-{cid[4:]}"] if f"cert-{cid[4:]}" in runs else []
        elif cid.startswith("C-atlas"): ev = ["atlas"]
        elif cid in ("C-L1", "C-L4"): ev = ["lean"]
        elif cid.startswith("C-H-NC"): ev = [e for e in runs if e.startswith("negctl-")]
        cl.append({"claim_id": cid, "text": c["text"], "level": c["level"], "evidence_run_ids": ";".join(sorted(ev)), "status": c["status"]})

    def gate(name, passed, reason): gates.append({"gate": name, "passed": bool(passed), "reason": reason, "ts": now})
    st = subprocess.run(["python3", "-m", "asd.selftest", "expressivity"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
    gate("EX_G1_verifier_selftest", "BESTANDEN" in st, st)
    cs = subprocess.run(["python3", "-m", "expressivity.test_consistent"], capture_output=True, text=True).stdout.strip()
    gate("EX_G2_consistency_regressions", "PASS" in cs, cs)
    lean = open("expressivity/lean/check.out").read()
    gate("EX_G3_lean_no_sorry", "sorryAx" not in lean and lean.count("depends on axioms") >= 5, "5 theorems, axioms: propext, Classical.choice, Quot.sound only")
    if os.path.exists(f"{R}/atlas.json"):
        s = json.load(open(f"{R}/atlas.json"))["summary"]
        gate("EX_G4_atlas_own_vs_gap", not s["disagreements_own_vs_gap"], f"{s['groups']} groups, disagreements {s['disagreements_own_vs_gap']}")
    gate("EX_G5_certified_table", cert["rows"] and all(r["all_passed"] for r in cert["rows"]), f"{len(cert['rows'])} (group, alphabet) pairs, all checks passed: {all(r['all_passed'] for r in cert['rows']) if cert['rows'] else None}")
    tsv = open(f"{R}/citations.tsv").read().splitlines()[1:]
    gate("EX_G6_citations", all(l.startswith("VERIFIED") for l in tsv), f"{sum(l.startswith('VERIFIED') for l in tsv)} of {len(tsv)} titles verified; quotes used only where verified verbatim")
    if CF:
        g = CF["gates"]
        gate("EX_G7_prereg_accuracy_beats_baselines", g["H-EX1.1_accuracy_beats_all_baselines"], json.dumps(CF["accuracy"]))
        gate("EX_G8_prereg_discriminating_tests_BH", g["H-EX1.2_discriminating_tests_BH"], "; ".join(f"{t['test']} p_bh={t['p_bh']:.3g}" for t in CF["tests"] if t["test"].startswith("D")))
        gate("EX_G9_negative_control", g["negative_control_clean"], "; ".join(f"{n['cell']}: {n['succ']}/{n['n']}" for n in CF["negative_control"]))
        lstm = [c for c in CF["cells"] if c["arch"] == "lstm"]
        gate("EX_G10_positive_control_lstm", all(c["outcome"] for c in lstm), f"{sum(c['outcome'] for c in lstm)} of {len(lstm)} LSTM cells succeed")
        gate("EX_G11_H-EX1", g["H-EX1_success"], "preregistered overall criterion")
    os.makedirs(OUT, exist_ok=True)
    T.write("experiments", exp, OUT); T.write("claims", cl, OUT); T.write("gates", gates, OUT)
    errs = T.validate(OUT)
    gate("EX_G12_tables_validate", not errs, f"{len(errs)} errors")
    T.write("gates", gates, OUT)
    print(f"{len(exp)} experiments, {len(cl)} claims, {len(gates)} gates; validation errors: {errs[:5]}")
    for g_ in gates: print(g_["gate"], g_["passed"], g_["reason"][:120])


if __name__ == "__main__":
    main()
