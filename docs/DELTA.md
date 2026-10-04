# Delta Lake at the Lab API boundary

The Lab validates inputs before invoking the domain and validates results before returning or caching them. An explicit SQL schema prevents inferred nested types, null-only columns and schema drift. The optional backend writes actual Parquet files and `_delta_log` transactions through delta-rs. This release verifies local Delta Lake; it does not claim a Databricks workspace deployment or MLflow integration.

## Install and run

Normalization and JSONL recording use the Python standard library. NumPy values require NumPy when decoded. Actual Delta storage needs Python 3.10+ and:

```sh
python -m pip install -r requirements-delta.txt
python -m asd.delta_demo --output work/delta-demo
python -m asd.delta_store inspect --path work/delta-demo/events
```

The demo performs **new exact verification calls** for the existing 81/31 and111/41 witnesses and records a cache hit. It does not rerun discovery or pretend that historical search jobs originally ran on Delta. `report.json` distinguishes domain computation time from total normalization/storage time. These small timings are a demonstration, not a performance benchmark or evidence of discovery acceleration.

Use the real lab with either direct Delta commits or deferred JSONL ingestion:

```sh
ASD_DELTA_PATH=work/delta/events python -m asd.lab_loop --domain geometric_extremal --runden 1
ASD_RECORD_JSONL=work/record.jsonl python -m asd.lab_loop --domain geometric_extremal --runden 1
python -m asd.delta_store ingest --input work/record.jsonl --path work/delta/events
```

The lab-loop commands invoke the existing LLM backend and may generate new research artifacts. Setting both variables is an error. With neither set, normalized events stay in `lab.events`; no storage dependency is loaded. Alternatively pass `event_sink=DeltaEventStore(path)` or `event_sink=JsonlEventSink(path)` to either Lab constructor. `run_id` groups domain Lab events; the original measurement Lab retains its supplied run ID.

## Contract

Fixed columns: `schema_version BIGINT`, `event_id STRING`, `run_id STRING`, `domain STRING`, `operation STRING`, `status STRING`, `args_json STRING`, `result_json STRING`, `error_json STRING`, `args_sha256 STRING`, `result_sha256 STRING`, `ts TIMESTAMP`, `elapsed_seconds DOUBLE`, `cached BOOLEAN`. Only result/error/result-hash columns are nullable. Timestamps are timezone-aware UTC, microsecond precision. `status=success` means the API operation returned compatible data; it does **not** assert that a mathematical candidate passed the verifier. Inspect the verifier's `passed` field in `result_json` separately.

Payloads use canonical strict JSON. Ordinary JSON stays ordinary JSON; tuples become lists. Large integers, fractions, Decimal values, complex values, bytes, dates, datetimes and supported NumPy arrays/scalars use reversible, collision-safe `$asd` tags. `decode_json` restores native values before the domain sees them. Extended precision and structured/date NumPy dtypes are explicitly unsupported. SQL consumers can parse ordinary fields with `get_json_object`/`from_json`; tagged exact quantities must be decoded according to the contract, never cast blindly to DOUBLE.

Reject nonfinite numbers, cycles, nonstring mapping keys, unsupported types, invalid UTF-8, duplicate JSON keys, malformed tags, changed payload hashes and unsupported row fields. No automatic schema evolution or silent CSV fallback. Invalid inputs do not execute the domain. Invalid outputs produce an error event and raise a normalization error; no successful result is returned or cached. Domain exceptions become the existing `fehler` response shape. Errors are not cached. Storage failures propagate; no in-memory success record is accepted after a failed write. Commit acknowledgements can be ambiguous after underlying I/O failures; callers must inspect event IDs before retrying rather than assuming exactly-once execution.

Snapshots isolate caller arguments, domain mutations and returned objects from cache/history. Identical concurrent requests use a per-key lock; different requests can still execute concurrently. Reads from a Delta table have no guaranteed order; use `ORDER BY ts,event_id` for display. Re-ingesting a JSONL file appends duplicates: this is append-only storage, not an upsert.

The existing `experiments`, `claims`, `gates` CSV tables are also validated at write time by `asd.sql_tables.SQL_SCHEMA`. Seed and x_index are STRING identifiers because the algorithm-efficiency domain contains seed ranges, rational parameters and question IDs; step remains BIGINT, y DOUBLE, passed BOOLEAN. Numeric identifiers retain their textual value, without truncation. The column names remain unchanged. Existing historical CSVs can still be read. New timestamp writes require an explicit timezone; the exporter uses actual file times in UTC and does not invent a timezone for old strings. Extra fields and wrong-width list rows are rejected instead of silently dropped. These authoritative CSV tables are not automatically copied to the event Delta table.

## SQL and Databricks

In a Databricks Spark session, copy/upload the **complete Delta directory**, including `_delta_log`, into a permitted Volume/storage location. Then read it as Delta:

```python
frame = spark.read.format("delta").load(delta_path)
frame.createOrReplaceTempView("lab_events")
spark.sql("""
SELECT domain, operation, status, count(*) AS events,
       sum(CASE WHEN cached THEN 1 ELSE 0 END) AS cache_hits
FROM lab_events GROUP BY domain, operation, status
""").show()
```

Here `delta_path` is a trusted Python value, not interpolated SQL. The local adapter deliberately rejects cloud URIs/provider options. Workspace permissions, actual upload, catalog registration and live Databricks execution need separate verification. Local SQL testing reads the actual Delta snapshot via PyArrow and queries it with DuckDB; no Databricks execution is implied.

## Checks

```sh
python -m pip install -r requirements-delta-test.txt
python -m unittest discover -s tests -v
python -m asd.selftest geometric_extremal
```

Tests cover precision, invalid boundaries, cache races and mutation, storage failure, actual Delta transactions, SQL queries, historical versions, invalid-batch atomicity and schema drift. The JSONL sink additionally passed independent POSIX multiprocess/thread stress. Its advisory filesystem lock uses `fcntl`; this JSONL sink is currently POSIX-only. Direct Delta storage has no `fcntl` dependency.

Primary references: [delta-rs writing](https://delta-io.github.io/delta-rs/latest/usage/writing/), [Delta protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md), [Databricks SQL types](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datatypes).
