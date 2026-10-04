"""Lossless scientific payloads and a fixed SQL/Delta event contract.

``normalize_payload`` produces JSON-safe values, ``restore_payload`` reverses
scientific tags, and ``canonical_json`` is deterministic storage serialization.
Ordinary tuples normalize to lists. Large integers are decimal strings in tagged
objects; SQL columns never receive heterogeneous nested data. This module has no
mandatory third-party dependencies. NumPy is imported only to restore NumPy tags.
"""
from __future__ import annotations

import base64
import binascii
from datetime import date, datetime, timezone
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import math
import uuid

TAG = "$asd"
BIGINT_MIN, BIGINT_MAX = -(2**63), 2**63 - 1
EVENT_SCHEMA = {
    "schema_version": "BIGINT", "event_id": "STRING", "run_id": "STRING",
    "domain": "STRING", "operation": "STRING", "status": "STRING",
    "args_json": "STRING", "result_json": "STRING", "error_json": "STRING",
    "args_sha256": "STRING", "result_sha256": "STRING", "ts": "TIMESTAMP",
    "elapsed_seconds": "DOUBLE", "cached": "BOOLEAN",
}
EVENT_FIELDS = tuple(EVENT_SCHEMA)
NULLABLE_FIELDS = frozenset(("result_json", "error_json", "result_sha256"))


class NormalizationError(ValueError):
    """Unsupported, lossy, cyclic or malformed input; message includes its path."""


def _fail(path, message):
    raise NormalizationError(f"{path}: {message}")


def normalize_payload(value):
    """Return JSON-safe data without silently rounding scientific values.

    Reject nonfinite numbers, nonstring mapping keys, cycles and unsupported
    objects. Shared references are allowed. Dictionaries containing the reserved
    tag key are escaped, so user data cannot be mistaken for a scientific tag.
    """
    active = set()

    def walk(v, path):
        if type(v) is str:
            try:
                v.encode('utf-8')
            except UnicodeEncodeError:
                _fail(path, 'string is not valid UTF-8')
            return v
        if v is None or type(v) is bool:
            return v
        if type(v) is int:
            return v if BIGINT_MIN <= v <= BIGINT_MAX else {TAG: "integer", "value": str(v)}
        if type(v) is float:
            if not math.isfinite(v):
                _fail(path, "nonfinite float")
            return v
        if isinstance(v, Fraction):
            return {TAG: "fraction", "numerator": str(v.numerator), "denominator": str(v.denominator)}
        if isinstance(v, Decimal):
            if not v.is_finite():
                _fail(path, "nonfinite Decimal")
            return {TAG: "decimal", "value": str(v)}
        if type(v) is complex:
            return {TAG: "complex", "real": walk(v.real, path + '.real'), "imag": walk(v.imag, path + '.imag')}
        if isinstance(v, bytes):
            return {TAG: "bytes", "value": base64.b64encode(v).decode('ascii')}
        if isinstance(v, datetime):
            return {TAG: "datetime", "value": v.isoformat(), "fold": v.fold}
        if isinstance(v, date):
            return {TAG: "date", "value": v.isoformat()}
        if type(v).__module__.split('.')[0] == 'numpy':
            import numpy as np
            if isinstance(v, (np.ndarray, np.generic)):
                if v.dtype.kind in 'fm' and v.dtype.itemsize > 8 or v.dtype.kind == 'c' and v.dtype.itemsize > 16:
                    _fail(path, "NumPy extended precision is unsupported; use exact Decimal values")
                if v.dtype.kind not in 'biufcUSO':
                    _fail(path, f"unsupported NumPy dtype {v.dtype}")
                if isinstance(v, np.ndarray):
                    ident = id(v)
                    if ident in active:
                        _fail(path, 'cycle detected')
                    active.add(ident)
                    try:
                        data = [walk(x.item() if isinstance(x, np.generic) else x, f'{path}[{i}]') for i, x in enumerate(v.flat)]
                        return {TAG: 'ndarray', 'dtype': v.dtype.str, 'shape': list(v.shape), 'values': data}
                    finally:
                        active.remove(ident)
                return {TAG: 'numpy_scalar', 'dtype': v.dtype.str, 'value': walk(v.item(), path)}
        if isinstance(v, (dict, list, tuple)):
            ident = id(v)
            if ident in active:
                _fail(path, 'cycle detected')
            active.add(ident)
            try:
                if isinstance(v, dict):
                    for key in v:
                        if not isinstance(key, str):
                            _fail(path, f'nonstring dictionary key {key!r}')
                    data = {key: walk(item, f'{path}[{key!r}]') for key, item in sorted(v.items())}
                    return {TAG: 'mapping', 'items': [[k, item] for k, item in data.items()]} if TAG in data else data
                return [walk(item, f'{path}[{i}]') for i, item in enumerate(v)]
            finally:
                active.remove(ident)
        _fail(path, f'unsupported type {type(v).__name__}')

    return walk(value, '$')


def restore_payload(value):
    """Restore a normalized payload; malformed and unknown tags are rejected."""
    def walk(v, path):
        if isinstance(v, list):
            return [walk(item, f'{path}[{i}]') for i, item in enumerate(v)]
        if not isinstance(v, dict):
            if v is None or type(v) in (str, bool, int):
                return v
            if type(v) is float and math.isfinite(v):
                return v
            _fail(path, 'invalid normalized primitive')
        if any(not isinstance(k, str) for k in v):
            _fail(path, 'nonstring dictionary key')
        if TAG not in v:
            return {k: walk(item, f'{path}[{k!r}]') for k, item in v.items()}
        tag = v[TAG]
        fields = {
            'integer': {'value'}, 'fraction': {'numerator', 'denominator'},
            'decimal': {'value'}, 'complex': {'real', 'imag'}, 'bytes': {'value'},
            'date': {'value'}, 'datetime': {'value', 'fold'}, 'mapping': {'items'},
            'ndarray': {'dtype', 'shape', 'values'}, 'numpy_scalar': {'dtype', 'value'},
        }
        if not isinstance(tag, str) or tag not in fields or set(v) != fields.get(tag, set()) | {TAG}:
            _fail(path, 'unknown tag or invalid tag fields')
        try:
            if tag == 'integer':
                if not isinstance(v['value'], str):
                    raise ValueError('integer must be decimal text')
                return int(v['value'])
            if tag == 'fraction':
                if any(not isinstance(v[k], str) for k in ('numerator', 'denominator')):
                    raise ValueError('fraction must use integer text')
                return Fraction(int(v['numerator']), int(v['denominator']))
            if tag == 'decimal':
                if not isinstance(v['value'], str):
                    raise ValueError('decimal must be text')
                out = Decimal(v['value'])
                if not out.is_finite():
                    raise ValueError('nonfinite Decimal')
                return out
            if tag == 'complex':
                real, imag = walk(v['real'], path + '.real'), walk(v['imag'], path + '.imag')
                if type(real) not in (int, float) or type(imag) not in (int, float):
                    raise ValueError('invalid complex components')
                return complex(real, imag)
            if tag == 'bytes':
                return base64.b64decode(v['value'], validate=True)
            if tag == 'date':
                return date.fromisoformat(v['value'])
            if tag == 'datetime':
                if type(v['fold']) is not int or v['fold'] not in (0, 1):
                    raise ValueError('invalid datetime fold')
                return datetime.fromisoformat(v['value']).replace(fold=v['fold'])
            if tag == 'mapping':
                if not isinstance(v['items'], list):
                    raise ValueError('mapping items must be a list')
                out = {}
                for pair in v['items']:
                    if not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str) or pair[0] in out:
                        raise ValueError('invalid or duplicate mapping entry')
                    out[pair[0]] = walk(pair[1], f'{path}[{pair[0]!r}]')
                return out
            import numpy as np
            dtype = np.dtype(v['dtype'])
            if dtype.kind not in 'biufcUSO' or (dtype.kind == 'f' and dtype.itemsize > 8) or (dtype.kind == 'c' and dtype.itemsize > 16):
                raise ValueError('unsupported numpy dtype')
            if tag == 'numpy_scalar':
                decoded = walk(v['value'], path + '.value')
                out = np.asarray(decoded, dtype=dtype)[()]
                # Encoding again detects narrowing/overflow rather than trusting a tag.
                if normalize_payload(out) != v:
                    raise ValueError('numpy scalar tag would lose precision')
                return out
            shape = v['shape']
            if not isinstance(shape, list) or any(type(n) is not int or n < 0 for n in shape):
                raise ValueError('invalid array shape')
            if not isinstance(v['values'], list) or math.prod(shape) != len(v['values']):
                raise ValueError('array shape does not match values')
            data = walk(v['values'], path + '.values')
            out = np.empty(len(data), dtype=dtype)
            for i, item in enumerate(data):
                out[i] = item
            out = out.reshape(shape)
            if normalize_payload(out) != v:
                raise ValueError('numpy array tag would lose precision')
            return out
        except (ValueError, TypeError, OverflowError, KeyError, ImportError, binascii.Error) as exc:
            _fail(path, f'invalid {tag} tag: {exc}')
    return walk(value, '$')


def canonical_json(value):
    """Serialize native payload into deterministic, strict JSON."""
    return json.dumps(normalize_payload(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def decode_json(text):
    """Read strict JSON and restore scientific values (duplicate keys rejected)."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _fail('$', f'duplicate JSON key {key!r}')
            result[key] = value
        return result
    try:
        parsed = json.loads(text, object_pairs_hook=pairs, parse_constant=lambda x: _fail('$', f'nonfinite JSON number {x}'))
    except (TypeError, ValueError) as exc:
        if isinstance(exc, NormalizationError):
            raise
        _fail('$', f'invalid JSON: {exc}')
    return restore_payload(parsed)


def _sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def make_event_row(*, run_id='', domain='', operation='', status='success', args=None,
                   result=None, error=None, event_id=None, ts=None,
                   elapsed_seconds=0.0, cached=False):
    """Build an event; status is success/error and timestamps are explicit UTC."""
    args_text = canonical_json(args)
    result_text = canonical_json(result) if status == 'success' else None
    error_text = canonical_json(error) if error is not None else None
    row = dict(schema_version=1, event_id=event_id or str(uuid.uuid4()), run_id=run_id,
               domain=domain, operation=operation, status=status, args_json=args_text,
               result_json=result_text, error_json=error_text, args_sha256=_sha(args_text),
               result_sha256=_sha(result_text) if result_text is not None else None,
               ts=ts or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
               elapsed_seconds=elapsed_seconds, cached=cached)
    return validate_event_row(row)


def validate_event_row(row):
    """Check exact SQL schema, canonical payloads, UTC timestamp and digests."""
    if not isinstance(row, dict) or set(row) != set(EVENT_FIELDS):
        _fail('$', 'event fields do not match EVENT_SCHEMA')
    for field, sql_type in EVENT_SCHEMA.items():
        item = row[field]
        if item is None and field in NULLABLE_FIELDS:
            continue
        if sql_type == 'BIGINT' and (type(item) is not int or not BIGINT_MIN <= item <= BIGINT_MAX):
            _fail(f'$.{field}', 'expected SQL BIGINT')
        if sql_type in ('STRING', 'TIMESTAMP'):
            if not isinstance(item, str):
                _fail(f'$.{field}', 'expected string')
            try:
                item.encode('utf-8')
            except UnicodeEncodeError:
                _fail(f'$.{field}', 'string is not valid UTF-8')
        if sql_type in ('STRING', 'TIMESTAMP') and isinstance(item, str):
            try: item.encode('utf-8')
            except UnicodeEncodeError: _fail(f'$.{field}', 'invalid UTF-8')
        if sql_type == 'BOOLEAN' and type(item) is not bool:
            _fail(f'$.{field}', 'expected SQL BOOLEAN')
        if sql_type == 'DOUBLE':
            try:
                valid = type(item) in (int, float) and math.isfinite(item) and item >= 0
                if type(item) is int:
                    valid = valid and int(float(item)) == item
            except (OverflowError, ValueError):
                valid = False
            if not valid:
                _fail(f'$.{field}', 'expected nonnegative finite DOUBLE without precision loss')
    if row['schema_version'] != 1 or not row['event_id'] or row['status'] not in ('success', 'error'):
        _fail('$', 'invalid event version, identifier or status')
    try:
        stamp = datetime.fromisoformat(row['ts'].replace('Z', '+00:00'))
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0 or not row['ts'].endswith('Z'):
            raise ValueError('timestamp must use UTC Z suffix')
        if stamp.isoformat().replace('+00:00', 'Z') != row['ts']:
            raise ValueError('timestamp must be canonical ISO UTC with at most microsecond precision')
    except (ValueError, AttributeError) as exc:
        _fail('$.ts', f'invalid UTC timestamp: {exc}')
    for field in ('args_json', 'result_json', 'error_json'):
        item = row[field]
        if item is not None and canonical_json(decode_json(item)) != item:
            _fail(f'$.{field}', 'payload must be canonical JSON')
    for source, digest in (('args_json', 'args_sha256'), ('result_json', 'result_sha256')):
        expected = _sha(row[source]) if row[source] is not None else None
        if row[digest] != expected:
            _fail(f'$.{digest}', 'payload hash mismatch')
    if row['status'] == 'success' and (row['result_json'] is None or row['error_json'] is not None):
        _fail('$', 'success requires result JSON and no error')
    if row['status'] == 'error' and (row['result_json'] is not None or row['error_json'] is None):
        _fail('$', 'error requires error JSON and no result')
    return {field: float(row[field]) if field == 'elapsed_seconds' else row[field] for field in EVENT_FIELDS}
