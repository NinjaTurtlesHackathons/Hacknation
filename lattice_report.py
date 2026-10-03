"""Gitter-Domäne -> die drei Tabellen (experiments, claims, gates) + Paper.
  python lattice_report.py           # nach benchmarks/run_benchmark.py (A1, A2, B) und explore.py
Hängt die Zeilen an tables/*.csv an (bestehende Zeilen der Gitter-Domäne werden ersetzt)."""
import glob, json, math, os, subprocess, time
import numpy as np, pandas as pd
from asd import tables as T
from asd.domains import lattice as L

TS = time.strftime("%Y-%m-%dT%H:%M:%S")
REF = [(4, L.I, 7.58266977279, 7.58267002399), (5, L.I, 4.83802684659, 4.83802684684), (6, L.I, 3.24997431242, 3.24997431246),
       (7, L.I, 2.23344617477, 2.23344617480), (8, L.I, 1.55240121256, 1.55240121259), (3.5, L.RHO, 9.77228723809, 9.77246454156)]


def main_scalar(res):
    if not isinstance(res, dict): return float("nan")
    for k in ("T", "diff", "y", "kruemmung", "y_inf_fit"):
        if isinstance(res.get(k), (int, float)): return float(res[k])
    return float("nan")


def lab_validation():
    rows, ok_all, parts = [], True, []
    for nu, tau, lo, hi in REF:
        v, e = L.T_tau(tau, nu, (64, 96)); ok = lo - 3 * e - 1e-11 <= v <= hi + 3 * e + 1e-11; ok_all &= ok
        parts.append(f"nu={nu}: {v:.11f} in [{lo}, {hi}]: {'ja' if ok else 'NEIN'}")
    a = L.compare2d(L.I, L.RHO, 3.918364, (64, 96))["diff"]; b = L.compare2d(L.I, L.RHO, 3.918366, (64, 96))["diff"]
    ok = a > 0 > b; ok_all &= ok; parts.append(f"T(i)-T(rho): {a:.3e} bei 3,918364 und {b:.3e} bei 3,918366 (Paper: [2,31; 2,90]e-7 und [-3,46; -2,87]e-7)")
    e1 = min(L.hessian2d(L.I, 8.604, R=(48, 64))["eigenwerte"]); e2 = min(L.hessian2d(L.I, 8.608, R=(48, 64))["eigenwerte"])
    ok = e1 > 0 > e2; ok_all &= ok; parts.append(f"kleinster Hesse-Eigenwert am Quadrat: {e1:.3e} bei 8,604, {e2:.3e} bei 8,608 (Paper: nu_2 in (8,604; 8,608))")
    c1 = L.bain_curvature(np.sqrt(2), 3.75, R=(10, 14))["kruemmung"]; c2 = L.bain_curvature(np.sqrt(2), 3.755, R=(10, 14))["kruemmung"]
    ok = c1 > 0 > c2; ok_all &= ok; parts.append(f"Bain-Krümmung bei FCC: {c1:.3e} bei 3,75, {c2:.3e} bei 3,755 (Paper: nu_c = 3,7521 ± 0,0001)")
    return ok_all, parts


def main():
    exp_rows, claims, gates = [], [], []
    ok, parts = lab_validation()
    gates.append(dict(gate="G8_gitterlabor_validierung", passed=ok, reason="; ".join(parts), ts=TS))
    claims.append(dict(claim_id="C-lab-validierung", text="Das Gitter-Labor reproduziert die rigorosen Ergebnisse aus Suleman 2026: " + "; ".join(parts) + ".",
                       level="observed", evidence_run_ids="", status="bestätigt" if ok else "widerlegt"))
    # Benchmark
    for cond in ("A1", "A2", "B"):
        for f in sorted(glob.glob(f"results/benchmark/{cond}/*.json")):
            r = json.load(open(f)); rid = f"suleman2026-{cond}-{r['frage']}-{r['salt']}"
            log = r.get("experimente") or [{"id": 0, "wer": cond, "ergebnis": {}}]
            for e in log:
                exp_rows.append(dict(run_id=rid, seed=r["salt"], policy=e.get("wer", cond), dataset=f"suleman2026_{cond}", step=e["id"],
                                     x_index=e["id"], y=main_scalar(e.get("ergebnis")), mlflow_run_id="", ts=TS))
    if os.path.exists("results/benchmark/score.json"):
        S = json.load(open("results/benchmark/score.json")); summ = S["summary"]
        for c, v in summ.items():
            ids = ";".join(sorted({f"suleman2026-{c}-{os.path.basename(f).split('_')[0]}-{json.load(open(f))['salt']}" for f in glob.glob(f"results/benchmark/{c}/*.json")}))
            name = {"A1": "Claude pur (ohne Tools)", "A2": "Claude mit eigenem Python-Code", "B": "Framework (Forscher-Schleife mit Code-Prüfer)"}[c]
            claims.append(dict(claim_id=f"C-bench-{c}", text=f"{name}: {v['richtig'] * 100:.1f} % richtige und {v['falsch'] * 100:.1f} % falsche Antworten auf 12 Fragen aus Suleman 2026 (je 3 Läufe).",
                               level="observed", evidence_run_ids=ids, status="bestätigt"))
        for k, t in S.get("tests", {}).items():
            okk = t["p"] < 0.05
            gates.append(dict(gate=k, passed=okk, reason=f"gepaarter Permutationstest über 12 Fragen: p = {t['p']:.4f}, p_BH = {t['p_bh']:.4f}", ts=TS))
            claims.append(dict(claim_id=f"C-{k}", text=f"{k.replace('_', ' ')}: p = {t['p']:.4f} (BH-adjustiert {t['p_bh']:.4f}); präregistriertes Kriterium p < 0,05 {'erfüllt' if okk else 'verfehlt'}.",
                               level="statistical", evidence_run_ids="", status="bestätigt" if okk else "offen"))
    # Entdeckungsmodus
    for f in sorted(glob.glob("results/explore/*.json")):
        r = json.load(open(f)); rid = f"explore-{r['id']}"
        for e in r["experimente"]:
            exp_rows.append(dict(run_id=rid, seed=0, policy=e["wer"], dataset="explore", step=e["id"], x_index=e["id"],
                                 y=main_scalar(e.get("ergebnis")), mlflow_run_id="", ts=TS))
        a = r["antwort"]; verified = r["level"].startswith("computed")
        grund = next((tr["pruefung"]["grund"] for tr in r["forscher"] if tr.get("pruefung", {}).get("bestanden")), "")
        claims.append(dict(claim_id=f"C-{r['id']}", text=f"{r['frage']} Antwort: {a.get('antwort')} (Stimmen {a.get('stimmen')}). Prüfer: {grund}",
                           level="observed" if verified else "hypothesis", evidence_run_ids=rid, status="bestätigt" if verified else "offen"))
    for name, rows, key in [("experiments", exp_rows, "dataset"), ("claims", claims, "claim_id"), ("gates", gates, "gate")]:
        old = T.read(name) if os.path.exists(f"tables/{name}.csv") else pd.DataFrame(columns=T.SCHEMA[name])
        if name == "experiments": old = old[~old.dataset.astype(str).str.startswith(("suleman2026", "explore"))]
        else: old = old[~old[key].isin([r[key] for r in rows])]
        T.write(name, old.to_dict("records") + rows)
    print("Validierung Gitter-Labor:", ok); print(f"{len(exp_rows)} Experimente, {len(claims)} Claims, {len(gates)} Gates angehängt")
    print("Tabellen-Validierung:", T.validate() or "OK")


if __name__ == "__main__":
    main()
