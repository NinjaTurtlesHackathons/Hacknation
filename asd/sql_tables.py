"""Explicit SQL types for the existing authoritative tables; no schema inference."""
from datetime import datetime, timezone
import math
import numbers
from fractions import Fraction
from .delta_contract import BIGINT_MIN, BIGINT_MAX, NormalizationError

SQL_SCHEMA = {
    "experiments": {"run_id": "STRING", "seed": "STRING", "policy": "STRING", "dataset": "STRING",
        "step": "BIGINT", "x_index": "STRING", "y": "DOUBLE", "mlflow_run_id": "STRING", "ts": "TIMESTAMP"},
    "claims": {"claim_id": "STRING", "text": "STRING", "level": "STRING", "evidence_run_ids": "STRING", "status": "STRING"},
    "gates": {"gate": "STRING", "passed": "BOOLEAN", "reason": "STRING", "ts": "TIMESTAMP"},
}


def normalize_row(name, row):
    schema = SQL_SCHEMA[name]
    if isinstance(row, (list, tuple)):
        if len(row) != len(schema): raise NormalizationError(f"{name}: row width differs from SQL schema")
        row = dict(zip(schema, row))
    if not isinstance(row, dict) or set(row) != set(schema):
        raise NormalizationError(f"{name}: row fields differ from SQL schema")
    out = {}
    for key, kind in schema.items():
        value = row[key]; path = f"{name}.{key}"
        if type(value).__module__.split('.')[0] == 'numpy' and hasattr(value, 'item'): value = value.item()
        if kind == 'STRING':
            if name == 'experiments' and key in ('seed', 'x_index') and isinstance(value, numbers.Real) and not isinstance(value, bool):
                if not math.isfinite(value): raise NormalizationError(f"{path}: nonfinite identifier")
                value = str(value)
            if not isinstance(value, str): raise NormalizationError(f"{path}: expected STRING")
            try: value.encode('utf-8')
            except UnicodeEncodeError as exc: raise NormalizationError(f"{path}: invalid UTF-8") from exc
        elif kind == 'BIGINT':
            if isinstance(value, bool) or not isinstance(value, numbers.Integral) or not BIGINT_MIN <= value <= BIGINT_MAX:
                raise NormalizationError(f"{path}: expected signed SQL BIGINT")
            value = int(value)
        elif kind == 'DOUBLE':
            if isinstance(value, bool) or not isinstance(value, numbers.Real): raise NormalizationError(f"{path}: expected DOUBLE")
            original = value
            value = float(value)
            if isinstance(original, numbers.Rational) and math.isfinite(value) and Fraction.from_float(value) != original: raise NormalizationError(f"{path}: lossy DOUBLE")
            if not math.isfinite(value): raise NormalizationError(f"{path}: nonfinite DOUBLE")
        elif kind == 'BOOLEAN':
            if type(value) is not bool: raise NormalizationError(f"{path}: expected BOOLEAN")
        elif kind == 'TIMESTAMP':
            if isinstance(value, str):
                try: value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError as exc: raise NormalizationError(f"{path}: invalid timestamp") from exc
            if not isinstance(value, datetime): raise NormalizationError(f"{path}: expected TIMESTAMP")
            # Historical CSV timestamps have no offset and are retained as text;
            # new writes must have a timezone to avoid inventing a historical zone.
            if value.tzinfo is None or value.utcoffset() is None: raise NormalizationError(f"{path}: timezone required")
            value = value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        out[key] = value
    return out
