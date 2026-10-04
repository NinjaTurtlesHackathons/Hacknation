-- Optional integration template, NOT executed or validated against a live workspace.
-- Upload the three authoritative CSV tables to a governed Volume first.
-- Names and locations are placeholders; choose an existing authorized catalog/schema.
CREATE TABLE IF NOT EXISTS experiments (
  run_id STRING, seed BIGINT, policy STRING, dataset STRING, step BIGINT,
  x_index BIGINT, y DOUBLE, mlflow_run_id STRING, ts STRING, seconds DOUBLE
) USING DELTA;
CREATE TABLE IF NOT EXISTS claims (
  claim_id STRING, text STRING, level STRING, evidence_run_ids STRING, status STRING
) USING DELTA;
CREATE TABLE IF NOT EXISTS gates (
  gate STRING, passed BOOLEAN, reason STRING, ts STRING
) USING DELTA;
