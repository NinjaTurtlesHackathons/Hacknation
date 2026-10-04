"""Databricks-Export: Tabellen aus den Protokollen und das SQL für Unity Catalog (gegen eine Attrappe der SQL-Verbindung, ohne Netz)."""
import sys, types


def test_tabellen_schema():
    from asd.databricks_export import tabellen
    T = tabellen()
    assert set(T) == {"ledger", "claims", "gates", "experiments", "frozen"}
    assert set(T["experiments"][0]) == {"run_id", "seed", "policy", "dataset", "step", "x_index", "y", "mlflow_run_id", "ts"}   # Schema aus CLAUDE.md
    assert all(r["chain_hash"] for r in T["ledger"]) and T["claims"] and T["frozen"]


def test_unity_sql(monkeypatch):
    log = []
    class Cur:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def execute(self, q): log.append(q)
        def executemany(self, q, rows): log.append((q, len(rows)))
    class Con(Cur):
        def cursor(self): return Cur()
    fake = types.ModuleType("databricks.sql"); fake.connect = lambda **kw: Con()
    monkeypatch.setitem(sys.modules, "databricks.sql", fake); monkeypatch.setitem(sys.modules, "databricks", types.SimpleNamespace(sql=fake))
    monkeypatch.setenv("DATABRICKS_HOST", "https://example.cloud.databricks.com"); monkeypatch.setenv("DATABRICKS_TOKEN", "x"); monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "w")
    from asd.databricks_export import tabellen, delta_unity
    T = tabellen(); delta_unity(T, "main", "probatum")
    assert log[0] == "CREATE SCHEMA IF NOT EXISTS main.probatum"
    assert any(isinstance(q, str) and q.startswith("CREATE OR REPLACE TABLE main.probatum.experiments (`run_id` STRING, `seed` BIGINT") for q in log)
    assert sum(n for q, n in (x for x in log if isinstance(x, tuple)) if "experiments" in q) == len(T["experiments"])


def test_llm_databricks_endpoint(monkeypatch):
    """ASD_LLM=databricks ruft den Model-Serving-Endpoint im OpenAI-Chat-Format (Attrappe statt Netz)."""
    import io, json, urllib.request
    import asd.llm as L
    seen = {}
    def fake(req, timeout=0):
        seen["url"] = req.full_url; seen["body"] = json.loads(req.data); seen["auth"] = req.headers["Authorization"]
        return io.BytesIO(json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode())
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    monkeypatch.setenv("DATABRICKS_HOST", "adb-1.azuredatabricks.net"); monkeypatch.setenv("DATABRICKS_TOKEN", "t"); monkeypatch.setenv("ASD_DBX_ENDPOINT", "databricks-claude-sonnet")
    text, cost, used = L._databricks("sys", "frage", "sonnet", 10)
    assert text == "ok" and used == "databricks:databricks-claude-sonnet"
    assert seen["url"] == "https://adb-1.azuredatabricks.net/serving-endpoints/databricks-claude-sonnet/invocations" and seen["auth"] == "Bearer t"
    assert seen["body"]["messages"][0] == {"role": "system", "content": "sys"}
