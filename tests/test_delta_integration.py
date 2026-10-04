"""Boundary, scientific precision and actual transactional Delta regression tests."""
import concurrent.futures
from datetime import date, datetime, timezone
from decimal import Decimal
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from asd.delta_contract import (NormalizationError, canonical_json, decode_json,
    make_event_row, validate_event_row, normalize_payload)
from asd.discovery import Lab
from asd.lab import Lab as MeasurementLab
from asd.delta_runtime import JsonlEventSink
from asd.sql_tables import normalize_row


class Echo:
    name = 'echo'
    def __init__(self): self.calls = 0
    def run_op(self, op, args): self.calls += 1; return args


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=False); self.env.start()
        os.environ.pop('ASD_DELTA_PATH', None); os.environ.pop('ASD_RECORD_JSONL', None)
    def tearDown(self): self.env.stop()

    def test_exact_scientific_roundtrip(self):
        values = [None, [], {}, True, 2**100, -(2**100), Fraction(1, 7),
            Decimal('0.123456789012345678901234567890'), complex(3, 4), b'\x00\xff',
            date(2026, 10, 4), datetime(2026, 10, 4, tzinfo=timezone.utc),
            {'$asd': 'integer', 'value': '123'}, {'nested': [2**90, Fraction(2, 3)]}]
        for value in values:
            with self.subTest(value=value): self.assertEqual(decode_json(canonical_json(value)), value)
        self.assertEqual(decode_json(canonical_json((1, 2))), [1, 2])

    def test_numpy_precision_shape_and_scalar(self):
        import numpy as np
        for value in [np.int64(4), np.bool_(True), np.array([], dtype=np.int64),
                      np.array([[1, 2], [3, 4]], dtype=np.int64), np.array([2**100], dtype=object)]:
            restored = decode_json(canonical_json(value))
            self.assertEqual(restored.dtype, value.dtype)
            np.testing.assert_array_equal(restored, value)

    def test_invalid_input_never_executes(self):
        cycle = []; cycle.append(cycle)
        d = Echo(); lab = Lab(d)
        for value in [float('nan'), float('inf'), {1: 'bad'}, cycle, object(), '\ud800']:
            with self.subTest(type=type(value)), self.assertRaises(NormalizationError): lab.run('echo', {'bad': value}, 'a')
        self.assertEqual(d.calls, 0); self.assertEqual(lab.events, [])

    def test_invalid_result_is_error_not_success_or_cache(self):
        class Bad(Echo):
            def run_op(self, op, args): self.calls += 1; return {'bad': float('nan')}
        d = Bad(); lab = Lab(d)
        with self.assertRaises(NormalizationError): lab.run('echo', {}, 'a')
        self.assertEqual(lab.memo, {}); self.assertEqual(lab.log, [])
        self.assertEqual(lab.events[0]['status'], 'error')
        self.assertIsNone(lab.events[0]['result_json'])

    def test_domain_exception_is_safe_error(self):
        class Bad(Echo):
            def run_op(self, op, args): raise ValueError('broken')
        lab = Lab(Bad()); entry = lab.run('echo', {}, 'a')
        self.assertIn('fehler', entry['ergebnis']); self.assertEqual(lab.events[0]['status'], 'error')
        self.assertEqual(lab.memo, {})

    def test_snapshot_isolated_from_all_mutations(self):
        class Mutator(Echo):
            def run_op(self, op, args): self.calls += 1; args['a'].append(2); return args
        d = Mutator(); lab = Lab(d); args = {'a': [1]}
        first = lab.run('echo', args, 'a'); first['ergebnis']['a'].append(3)
        second = lab.run('echo', args, 'b'); args['a'].append(4)
        self.assertEqual(second['ergebnis'], {'a': [1, 2]})
        self.assertEqual(lab.log[0]['args'], {'a': [1]}); self.assertEqual(d.calls, 1)
        self.assertTrue(lab.events[1]['cached'])

    def test_concurrent_cache_and_event_ids(self):
        d = Echo(); lab = Lab(d)
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            list(pool.map(lambda n: lab.run('echo', {'x': 3}, str(n)), range(40)))
        self.assertEqual(d.calls, 1); self.assertEqual(len(lab.events), 40)
        self.assertEqual(sum(r['cached'] for r in lab.events), 39)
        self.assertEqual(len(set(r['event_id'] for r in lab.events)), 40)
        self.assertEqual([r['id'] for r in lab.log], list(range(40)))

    def test_storage_failure_not_accepted(self):
        def broken(row): raise OSError('offline')
        lab = Lab(Echo(), event_sink=broken)
        with self.assertRaises(OSError): lab.run('echo', {}, 'a')
        self.assertEqual(lab.events, []); self.assertEqual(lab.log, []); self.assertEqual(lab.memo, {})
        measurement = MeasurementLab([2.5], event_sink=broken)
        with self.assertRaises(OSError): measurement.run(0)
        self.assertEqual(measurement.events, []); self.assertEqual(measurement.sink, []); self.assertEqual(measurement.log, [])

    def test_measurement_rejects_bad_indices_and_values(self):
        import numpy as np
        lab = MeasurementLab([3.5])
        for i in [True, np.bool_(True), 0.9, -1, 1]:
            with self.assertRaises(NormalizationError): lab.run(i)
        self.assertEqual(lab.run(np.int64(0)), 3.5)
        self.assertEqual(lab.events[0]['status'], 'success')
        for value in [float('inf'), 2**100+1, Fraction(1,7), Decimal('0.1')]:
            with self.subTest(value=value), self.assertRaises(NormalizationError): MeasurementLab([value]).run(0)

    def test_jsonl_environment_and_unicode(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'ASD_RECORD_JSONL': str(Path(d)/'events.jsonl')}):
            lab = Lab(Echo()); lab.run('echo', {'label': 'Zürich'}, 'a')
            rows = [json.loads(x) for x in (Path(d)/'events.jsonl').read_text().splitlines()]
            self.assertEqual(rows, lab.events); validate_event_row(rows[0])

    def test_malformed_event_and_integrity(self):
        row = make_event_row(args={'x': 1}, result={'y': 2})
        for field, value in [('cached', 1), ('schema_version', True), ('elapsed_seconds', float('nan')),
                             ('args_sha256', 'bad'), ('ts', '2026-10-04T00:00:00'), ('run_id', '\ud800'), ('unknown', 1)]:
            with self.subTest(field=field), self.assertRaises(NormalizationError): validate_event_row({**row, field: value})
        for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"$asd":"unknown"}']:
            with self.assertRaises(NormalizationError): decode_json(text)

    def test_sql_tables_preserve_heterogeneous_identifiers(self):
        from asd import tables
        row = {'run_id':'run', 'seed':'20000-24999', 'policy':'exact', 'dataset':'family',
               'step':1, 'x_index':'F3', 'y':2., 'mlflow_run_id':'', 'ts':'2026-10-04T00:00:00+00:00'}
        normalized = normalize_row('experiments', list(row.values()))
        self.assertEqual(normalized['seed'], '20000-24999'); self.assertEqual(normalized['x_index'], 'F3')
        for bad in [{**row, 'ts':'2026-10-04T00:00:00'}, {**row, 'extra':1}, {**row, 'run_id':'\ud800'}, {**row,'y':2**100+1}, {**row,'y':Fraction(1,7)}]:
            with self.assertRaises(NormalizationError): normalize_row('experiments', bad)
        with tempfile.TemporaryDirectory() as d:
            tables.write('experiments',[row],d)
            self.assertEqual(tables.read('experiments',d).iloc[0]['seed'], '20000-24999')


class RealDeltaTests(unittest.TestCase):
    def test_real_delta_roundtrip_versions_and_sql(self):
        from asd.delta_store import DeltaEventStore
        import duckdb
        from deltalake import DeltaTable
        with tempfile.TemporaryDirectory() as d:
            store = DeltaEventStore(Path(d)/'events')
            self.assertEqual(store.append([])['rows_written'], 0)
            self.assertFalse(store.path.exists())
            lab = Lab(Echo(), event_sink=store)
            lab.run('echo', {'exact': Fraction(1,7), 'big': 2**100, 'empty': []}, 'a')
            lab.run('echo', {'exact': Fraction(1,7), 'big': 2**100, 'empty': []}, 'b')
            self.assertTrue((store.path/'_delta_log').exists()); self.assertEqual(sorted(store.read(), key=lambda r:r['event_id']), sorted(lab.events, key=lambda r:r['event_id']))
            self.assertEqual(len(store.read(version=0)), 1)
            connection = duckdb.connect(); connection.register('events', DeltaTable(str(store.path)).to_pyarrow_table())
            self.assertEqual(connection.execute("SELECT status, count(*), sum(CASE WHEN cached THEN 1 ELSE 0 END) FROM events GROUP BY status").fetchall(), [('success',2,1)])
            self.assertEqual(decode_json(next(r for r in store.read() if not r['cached'])['result_json'])['big'], 2**100)
            before = store.inspect()['version']
            with self.assertRaises(NormalizationError): store.append([lab.events[0], {**lab.events[0], 'cached': 3}])
            self.assertEqual(store.inspect()['version'], before)

    def test_refuse_schema_drift(self):
        from asd.delta_store import DeltaEventStore, DeltaStorageError
        import pyarrow as pa
        from deltalake import write_deltalake, DeltaTable
        with tempfile.TemporaryDirectory() as d:
            write_deltalake(d, pa.table({'wrong': [1]}))
            with self.assertRaises(DeltaStorageError): DeltaEventStore(d)
            self.assertEqual(DeltaTable(d).version(), 0)


if __name__ == '__main__': unittest.main()
