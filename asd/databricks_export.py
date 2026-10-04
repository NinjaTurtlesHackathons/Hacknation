"""Protokolle -> Databricks: Delta-Tabellen + MLflow. Ohne Zugangsdaten lokal (delta/, mlruns/), mit Zugangsdaten in den Workspace.

  python -m asd.databricks_export                 # lokal: delta/<tabelle>/ (Delta Lake) und mlflow.db (MLflow, SQLite)
  DATABRICKS_HOST=... DATABRICKS_TOKEN=... DATABRICKS_WAREHOUSE_ID=... python -m asd.databricks_export --catalog main --schema probatum

Tabellen (eine Quelle für Dashboard und Paper, wie in CLAUDE.md):
  ledger       jede Zeile von runs/omnigent/*/record.jsonl mit ihrem Glied der Hash-Kette
  claims       Claims der Omnigent-Projekte: Stufe, Status, wirksame Red-Team-Voten
  gates        Policy-Entscheidungen (DENY / ASK / Freigabe) aus trace.json
  experiments  Replay-Benchmark je Bedingung und Seed (run_id, seed, policy, dataset, step, x_index, y, mlflow_run_id, ts)
  frozen       results/FROZEN.json flach (key, value) -- die Zahlen, die README, Paper und Video verwenden
MLflow: ein Run je Omnigent-Lauf (Kennzahlen + record/CHAIN/trace als Artefakte), ein Run je Benchmark-Bedingung (N je Seed als Schritt)."""
import argparse, glob, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONLINE = bool(os.environ.get("DATABRICKS_HOST") and os.environ.get("DATABRICKS_TOKEN"))


def J(p): return json.load(open(os.path.join(ROOT, p)))


def _s(x): return x if isinstance(x, str) or x is None else json.dumps(x, ensure_ascii=False, default=str)


def tabellen():
    T = {"ledger": [], "claims": [], "gates": [], "experiments": [], "frozen": []}
    for run in sorted(glob.glob(f"{ROOT}/runs/omnigent/*")):
        if not os.path.exists(f"{run}/CHAIN.json"): continue
        rid = os.path.basename(run); kette = dict(json.load(open(f"{run}/CHAIN.json"))["kette"])
        for i, l in enumerate(open(f"{run}/record.jsonl", encoding="utf-8").read().splitlines()):
            e = json.loads(l)
            T["ledger"].append({"run": rid, "line": i, "ts": e.get("ts"), "agent": e.get("agent"), "command": e.get("befehl"),
                                "inputs": _s(e.get("eingabe_ids")), "outputs": _s(e.get("ausgabe_ids")), "result": _s(e.get("ergebnis")),
                                "duration_s": float(e.get("dauer_s") or 0), "chain_hash": kette.get(f"record.jsonl#{i}")})
        tr = json.load(open(f"{run}/trace.json"))
        for p in tr.get("policy_ereignisse", []):
            T["gates"].append({"run": rid, "gate": p.get("grund", "").replace("Denied by policy: ", "").split(":")[0], "decision": p["art"],
                               "passed": p["art"] != "DENY", "reason": p.get("grund"), "agent_session": p.get("session"),
                               "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(p["zeit"]))})
    from .domains.base import get_domain
    D = get_domain("proofreading")
    for pj in ("omni_proofreading", "omni_parallel"):
        st = J(f"projects/{pj}/state.json"); v = st.get("runden_vor_omnigent", 0)
        for c in st["claims"]:
            if not str(c.get("quelle", "")).startswith("omnigent:") or (c.get("runde") or 0) <= v: continue
            try: text = D.describe(c["pruefung"], lang="en")
            except Exception: text = c.get("text")
            T["claims"].append({"claim_id": c["id"], "project": pj, "text": text, "level": c.get("level"), "status": c.get("status"),
                                "red_team_effective": sum(1 for r in c.get("red_team") or [] if r.get("gueltig", True) and r.get("relevant")),
                                "red_team_contradictions": sum(1 for r in c.get("red_team") or [] if r.get("widerspruch")), "check": _s(c.get("pruefung"))})
    for f in sorted(glob.glob(f"{ROOT}/results/replay_lattice/*.json")):
        r = json.load(open(f))
        T["experiments"].append({"run_id": f"{r['bedingung']}_{r['seed']}", "seed": int(r["seed"]), "policy": r["bedingung"], "dataset": "lattice_y_inf",
                                 "step": int(r["N"]), "x_index": None, "y": 1.0 if r.get("treffer") else 0.0, "mlflow_run_id": None,
                                 "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(os.path.getmtime(f)))})
    def flach(x, pre=""):
        if isinstance(x, dict):
            for k, v in x.items(): yield from flach(v, f"{pre}.{k}" if pre else k)
        else: yield pre, _s(x)
    T["frozen"] = [{"key": k, "value": v} for k, v in flach(J("results/FROZEN.json"))]
    return T


def mlflow_log(T):
    import mlflow
    if ONLINE:
        mlflow.set_tracking_uri("databricks"); mlflow.set_experiment(os.environ.get("ASD_MLFLOW_EXPERIMENT", "/Shared/probatum"))
    else:
        mlflow.set_tracking_uri(f"sqlite:///{ROOT}/mlflow.db"); mlflow.set_experiment("probatum")
    ids = {}
    for run in sorted(glob.glob(f"{ROOT}/runs/omnigent/*")):
        if not os.path.exists(f"{run}/trace.json"): continue
        rid = os.path.basename(run); tr = json.load(open(f"{run}/trace.json")); v = tr.get("verification", {})
        rows = [r for r in T["ledger"] if r["run"] == rid]
        with mlflow.start_run(run_name=f"omnigent {rid}") as m:
            mlflow.set_tags({"kind": "omnigent_run", "omnigent_session": tr.get("omnigent_session_id"), "hash_chain": tr.get("hash_kette")})
            mlflow.log_metrics({"handoffs": v.get("handoffs", 0), "verifier_receipts": v.get("quittungen", 0), "policy_deny": v.get("deny", 0),
                                "policy_ask": v.get("ask", 0), "ledger_lines": len(rows),
                                "confirmed": sum(1 for r in rows if r["command"] in ("pruefe", "prüfe") and '"bestanden": true' in (r["result"] or "")),
                                "rejected": sum(1 for r in rows if r["command"] in ("pruefe", "prüfe") and '"bestanden": false' in (r["result"] or ""))})
            for f in ("record.jsonl", "CHAIN.json", "trace.json"): mlflow.log_artifact(f"{run}/{f}")
            ids[rid] = m.info.run_id
    fz = J("results/FROZEN.json")["replay"]
    for b in sorted({r["policy"] for r in T["experiments"]}):
        rows = sorted((r for r in T["experiments"] if r["policy"] == b), key=lambda r: r["seed"])
        with mlflow.start_run(run_name=f"replay {b}") as m:
            mlflow.set_tags({"kind": "replay_benchmark", "prereg": "prereg.md H7/H8", "condition": b})
            for r in rows: mlflow.log_metric("N_calls_to_hit", r["step"], step=r["seed"]); mlflow.log_metric("hit", r["y"], step=r["seed"])
            ns = [r["step"] for r in rows]; mlflow.log_metrics({"mean_N": sum(ns) / len(ns), "seeds": len(ns)})
            for k, t in (fz.get("tests") or {}).items():
                if t and t["vergleich"] == b: mlflow.log_metrics({f"{k}_speedup": t["speedup"], f"{k}_ci_lo": t["ki95"][0], f"{k}_ci_hi": t["ki95"][1], f"{k}_p": t["p"]})
            for r in rows: r["mlflow_run_id"] = m.info.run_id
            ids[f"replay {b}"] = m.info.run_id
    return ids


def delta_local(T, out):
    import pyarrow as pa
    from deltalake import write_deltalake
    for name, rows in T.items():
        if rows: write_deltalake(f"{out}/{name}", pa.Table.from_pylist(rows), mode="overwrite", schema_mode="overwrite")


def delta_unity(T, catalog, schema):
    """Unity Catalog über ein SQL-Warehouse (databricks-sql-connector). Jede Tabelle wird ersetzt (CREATE OR REPLACE)."""
    from databricks import sql
    host = os.environ["DATABRICKS_HOST"].replace("https://", "").rstrip("/")
    typ = lambda v: "BOOLEAN" if isinstance(v, bool) else "BIGINT" if isinstance(v, int) else "DOUBLE" if isinstance(v, float) else "STRING"
    with sql.connect(server_hostname=host, http_path=os.environ.get("DATABRICKS_HTTP_PATH") or f"/sql/1.0/warehouses/{os.environ['DATABRICKS_WAREHOUSE_ID']}",
                     access_token=os.environ["DATABRICKS_TOKEN"]) as con, con.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
        for name, rows in T.items():
            if not rows: continue
            cols = list(rows[0]); probe = {c: next((r[c] for r in rows if r[c] is not None), "") for c in cols}
            cur.execute(f"CREATE OR REPLACE TABLE {catalog}.{schema}.{name} ({', '.join(f'`{c}` {typ(probe[c])}' for c in cols)}) USING DELTA")
            q = f"INSERT INTO {catalog}.{schema}.{name} VALUES ({', '.join('?' for _ in cols)})"
            for i in range(0, len(rows), 200): cur.executemany(q, [[r[c] for c in cols] for r in rows[i:i + 200]])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--catalog", default="main"); ap.add_argument("--schema", default="probatum")
    ap.add_argument("--out", default=os.path.join(ROOT, "delta")); ap.add_argument("--ohne-mlflow", action="store_true"); a = ap.parse_args()
    T = tabellen(); ids = {} if a.ohne_mlflow else mlflow_log(T)
    delta_local(T, a.out)
    if ONLINE and (os.environ.get("DATABRICKS_WAREHOUSE_ID") or os.environ.get("DATABRICKS_HTTP_PATH")): delta_unity(T, a.catalog, a.schema); ziel = f"Unity Catalog {a.catalog}.{a.schema}"
    else: ziel = f"lokal {os.path.relpath(a.out, ROOT)}/ (Delta Lake)"
    print(json.dumps({"ziel": ziel, "mlflow": "Databricks-Workspace" if ONLINE else "lokal mlflow.db (mlflow ui --backend-store-uri sqlite:///mlflow.db)", "zeilen": {k: len(v) for k, v in T.items()},
                      "mlflow_runs": len(ids)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
