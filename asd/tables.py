"""Die drei Tabellen (einzige Quelle für Dashboard und Paper): experiments, claims, gates.
Lokal als CSV unter tables/. Auf Databricks schreibt C dieselben Spalten als Delta-Tabellen."""
import os
import pandas as pd

SCHEMA = {
    "experiments": ["run_id", "seed", "policy", "dataset", "step", "x_index", "y", "mlflow_run_id", "ts"],
    "claims": ["claim_id", "text", "level", "evidence_run_ids", "status"],
    "gates": ["gate", "passed", "reason", "ts"],
}


def write(name, rows, out="tables"):
    os.makedirs(out, exist_ok=True)
    df = pd.DataFrame(rows, columns=SCHEMA[name]); df.to_csv(f"{out}/{name}.csv", index=False); return df


def read(name, out="tables"):
    return pd.read_csv(f"{out}/{name}.csv")


def validate(out="tables"):
    """Prüft Spalten und Claim-Belege: jeder evidence_run_id muss in experiments vorkommen."""
    errs = []
    for name, cols in SCHEMA.items():
        df = read(name, out)
        if list(df.columns) != cols: errs.append(f"{name}: Spalten {list(df.columns)} != {cols}")
    runs = set(read("experiments", out)["run_id"]); cl = read("claims", out)
    for _, c in cl.iterrows():
        for rid in str(c["evidence_run_ids"]).split(";") if isinstance(c["evidence_run_ids"], str) else []:
            if rid not in runs: errs.append(f"{c['claim_id']}: Beleg {rid} fehlt in experiments")
    bad = set(cl["level"]) - {"proved_lean", "computed_rigorous", "statistical", "observed", "hypothesis"}
    if bad: errs.append(f"unbekannte level: {bad}")
    return errs
