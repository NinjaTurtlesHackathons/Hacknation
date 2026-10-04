"""Transactional, schema-checked Delta Lake storage for Lab API events.

Optional dependencies: ``pip install 'deltalake>=1.5,<2' 'pyarrow>=19,<24'``.
This adapter writes actual Parquet data and a Delta transaction log locally;
it does not claim a Databricks workspace connection. Each append is one
transaction. Streaming one event per transaction favours durability over speed.
Inputs are normalized event rows from :mod:`asd.delta_contract`, never raw
domain objects. Payloads remain canonical JSON strings inside SQL columns.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable, Mapping, Any

from .delta_contract import EVENT_SCHEMA, NULLABLE_FIELDS, validate_event_row


class DeltaStorageError(RuntimeError):
    """Configured persistence failed; callers must not report a saved event."""


def _dependencies():
    try:
        import pyarrow as pa
        from deltalake import DeltaTable, write_deltalake
    except ImportError as exc:
        raise DeltaStorageError(
            "Delta storage requires: pip install 'deltalake>=1.5,<2' 'pyarrow>=19,<24'"
        ) from exc
    return pa, DeltaTable, write_deltalake


def _local_path(path: str | Path) -> Path:
    text = str(path)
    if not text.strip() or "://" in text or "\x00" in text:
        raise ValueError("Delta path must be a nonempty local filesystem path")
    return Path(text).expanduser().resolve()


def arrow_schema():
    """Explicit SQL types; nullable JSON fields never become Arrow null types."""
    pa, _, _ = _dependencies()
    types = {"BIGINT": pa.int64(), "STRING": pa.string(),
             "DOUBLE": pa.float64(), "BOOLEAN": pa.bool_(),
             "TIMESTAMP": pa.timestamp("us", tz="UTC")}
    return pa.schema([
        pa.field(name, types[kind], nullable=name in NULLABLE_FIELDS)
        for name, kind in EVENT_SCHEMA.items()
    ])


def _check_schema(table) -> None:
    pa, _, _ = _dependencies()
    actual = pa.schema(table.schema().to_arrow())
    if not actual.equals(arrow_schema(), check_metadata=False):
        raise DeltaStorageError("Existing Delta table schema differs from Lab event contract")


def _open_table(path: str | Path, version: int | None = None):
    _, DeltaTable, _ = _dependencies()
    root = _local_path(path)
    if version is not None and (isinstance(version, bool) or not isinstance(version, int) or version < 0):
        raise ValueError("Delta version must be a nonnegative integer")
    try:
        table = DeltaTable(str(root), version=version)
        _check_schema(table)
    except DeltaStorageError:
        raise
    except Exception as exc:
        # Error messages from storage providers can include sensitive values.
        raise DeltaStorageError("Cannot open a compatible Delta event table") from exc
    return table


def _validate_destination(root: Path) -> None:
    """Catch existing schema/path mistakes before executing a Lab operation."""
    _, DeltaTable, _ = _dependencies()
    try:
        if (root / "_delta_log").exists():
            _check_schema(DeltaTable(str(root)))
        elif root.exists() and (not root.is_dir() or any(root.iterdir())):
            raise DeltaStorageError("Refusing a nonempty non-Delta destination")
    except DeltaStorageError:
        raise
    except Exception as exc:
        raise DeltaStorageError("Cannot configure the Delta event destination") from exc


def append_rows(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> dict:
    """Validate a complete batch before a single append transaction.

    Empty batches are no-ops and never create a table. This is append-only,
    not an upsert: ingesting the same file twice stores it twice. There is no
    silent CSV fallback, automatic schema evolution, or overwrite operation.
    """
    canonical = [validate_event_row(row) for row in rows]
    root = _local_path(path)
    if not canonical:
        return {"rows_written": 0, "version": None}
    pa, DeltaTable, write_deltalake = _dependencies()
    converted = []
    for row in canonical:
        converted.append({**row, "ts": datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))})
    data = pa.Table.from_pylist(converted, schema=arrow_schema())
    try:
        _validate_destination(root)
        write_deltalake(str(root), data, mode="append")
        table = DeltaTable(str(root))
        _check_schema(table)
        return {"rows_written": len(canonical), "version": table.version()}
    except DeltaStorageError:
        raise
    except Exception as exc:
        raise DeltaStorageError("Delta event append failed; no success is reported") from exc


def _from_arrow_row(row: dict) -> dict:
    timestamp = row["ts"]
    if not isinstance(timestamp, datetime) or timestamp.tzinfo is None:
        raise DeltaStorageError("Delta timestamp must be timezone-aware")
    canonical = {**row, "ts": timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")}
    return validate_event_row(canonical)


def read_rows(path: str | Path, version: int | None = None) -> list[dict]:
    """Read and validate one Delta snapshot. Row order is not guaranteed."""
    table = _open_table(path, version)
    try:
        return [_from_arrow_row(row) for row in table.to_pyarrow_table().to_pylist()]
    except DeltaStorageError:
        raise
    except Exception as exc:
        raise DeltaStorageError("Delta event read failed or stored rows violate the contract") from exc


def inspect_table(path: str | Path, version: int | None = None) -> dict:
    """Metadata plus independently validated snapshot row count."""
    table = _open_table(path, version)
    rows = [_from_arrow_row(row) for row in table.to_pyarrow_table().to_pylist()]
    return {"version": table.version(), "row_count": len(rows),
            "sql_schema": dict(EVENT_SCHEMA), "nullable_columns": sorted(NULLABLE_FIELDS)}


class DeltaEventSink:
    """Callable Lab event sink. Write errors propagate and abort the caller."""
    def __init__(self, path: str | Path):
        self.path = _local_path(path)
        _validate_destination(self.path)
        self.rows_written = 0
        self.last_version = None

    def __call__(self, row: Mapping[str, Any]) -> None:
        result = append_rows(self.path, [row])
        self.rows_written += result["rows_written"]
        self.last_version = result["version"]

    def append(self, row: Mapping[str, Any]) -> None:
        self(row)


class DeltaEventStore:
    """Batch-capable event store, also usable as a one-row callable Lab sink.

    ``storage_options`` is reserved for a future authenticated object-store
    adapter. This implementation accepts local paths only and rejects supplied
    provider credentials rather than suggesting they are in use.
    """
    def __init__(self, path: str | Path, storage_options: dict | None = None):
        if storage_options:
            raise ValueError("Local Delta adapter does not accept cloud storage_options")
        self.path = _local_path(path)
        _validate_destination(self.path)

    def __call__(self, row: Mapping[str, Any]) -> None:
        self.append([row])

    def append(self, rows: Iterable[Mapping[str, Any]]) -> dict:
        return append_rows(self.path, rows)

    def read(self, version: int | None = None) -> list[dict]:
        return read_rows(self.path, version)

    def inspect(self, version: int | None = None) -> dict:
        return inspect_table(self.path, version)


def _load_jsonl(path: Path) -> list[dict]:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON event field")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("Non-finite JSON literal")

    rows = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                # Contract validation handles required fields, canonical JSON,
                # hashes, timestamps, finite values, and schema version.
                rows.append(validate_event_row(json.loads(
                    line, object_pairs_hook=unique_object, parse_constant=reject_constant)))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid normalized event on JSONL line {number}") from exc
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Append normalized Lab event JSONL in one transaction")
    ingest.add_argument("--input", type=Path, required=True)
    ingest.add_argument("--path", required=True)
    inspect = commands.add_parser("inspect", help="Inspect a validated Delta snapshot")
    inspect.add_argument("--path", required=True)
    inspect.add_argument("--version", type=int)
    export = commands.add_parser("export", help="Export a validated snapshot as normalized JSONL")
    export.add_argument("--path", required=True)
    export.add_argument("--version", type=int)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            result = append_rows(args.path, _load_jsonl(args.input))
        elif args.command == "inspect":
            result = inspect_table(args.path, args.version)
        else:
            rows = read_rows(args.path, args.version)
            root = _local_path(args.path)
            if args.output.resolve().is_relative_to(root):
                raise ValueError("JSONL export destination must be outside the Delta table")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as output:
                for row in rows:
                    output.write(json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
            result = {"rows_exported": len(rows)}
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True))
        return 0
    except (DeltaStorageError, ValueError, TypeError, OSError) as exc:
        # Don't echo raw payloads, provider errors, or paths containing credentials.
        parser.exit(1, f"{type(exc).__name__}: operation failed; validate configuration and input\n")


if __name__ == "__main__":
    raise SystemExit(main())
