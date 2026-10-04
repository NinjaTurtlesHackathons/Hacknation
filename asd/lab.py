"""Ground-truth Lab with strict SQL-compatible input/output boundaries."""
import math
import operator
import numbers
import threading
import time
from datetime import datetime, timezone
from uuid import uuid4
from fractions import Fraction
from decimal import Decimal
from .delta_contract import canonical_json, decode_json, make_event_row, NormalizationError
from .delta_runtime import configured_event_sink


class Lab:
    def __init__(self, y, run_id="", seed=-1, policy="", dataset="", sink=None, *, event_sink=None):
        self._y = y; self.log = []; self.events = []; self._lock = threading.RLock()
        self.ctx = dict(run_id=run_id, seed=seed, policy=policy, dataset=dataset)
        from .sql_tables import normalize_row
        # Check metadata before measuring or indexing ground truth.
        normalize_row("experiments", {**self.ctx, "step": 0, "x_index": 0, "y": 0.0,
                      "mlflow_run_id": "", "ts": datetime.now(timezone.utc).isoformat()})
        self.sink = sink if sink is not None else []
        if not isinstance(self.sink, list): raise TypeError("Legacy sink must be a list; use event_sink for storage callbacks")
        self.event_sink = event_sink if event_sink is not None else configured_event_sink()
        self._event_run_id = run_id or str(uuid4())

    def run(self, i: int) -> float:
        # operator.index accepts integral NumPy indices without truncating floats.
        if isinstance(i, bool) or type(i).__name__ == "bool":
            raise NormalizationError("$.i: boolean is not an index")
        try: i = operator.index(i)
        except TypeError as exc: raise NormalizationError("$.i: expected an integer index") from exc
        if i < 0 or i >= len(self._y): raise NormalizationError("$.i: index out of bounds")
        args = decode_json(canonical_json({"i": i}))
        with self._lock:
            t0 = time.perf_counter(); raw_y = self._y[args["i"]]; dt = time.perf_counter() - t0
            try:
                if type(raw_y).__module__.split(".")[0] == "numpy" and hasattr(raw_y, "item"): raw_y = raw_y.item()
                if isinstance(raw_y, bool): raise NormalizationError("$.y: boolean is not a measurement")
                y = float(raw_y)
                if (isinstance(raw_y, numbers.Rational) and math.isfinite(y) and Fraction.from_float(y) != raw_y) or (isinstance(raw_y, Decimal) and math.isfinite(y) and Decimal.from_float(y) != raw_y):
                    raise NormalizationError("$.y: exact measurement cannot fit DOUBLE without precision loss")
                if not math.isfinite(y): raise NormalizationError("$.y: nonfinite measurement")
                y = decode_json(canonical_json(y))
            except (ValueError, TypeError, OverflowError) as exc:
                error = exc if isinstance(exc, NormalizationError) else NormalizationError("$.y: measurement cannot be normalized")
                event = make_event_row(run_id=self._event_run_id, domain="chemistry", operation="measure",
                    args=args, status="error", error={"fehler": str(error)}, elapsed_seconds=dt)
                if self.event_sink is not None: self.event_sink(dict(event))
                self.events.append(dict(event))
                raise error
            from .sql_tables import normalize_row
            record = normalize_row("experiments", {**self.ctx, "step": len(self.log) + 1,
                "x_index": i, "y": y, "mlflow_run_id": "", "ts": datetime.now(timezone.utc).isoformat()})
            event = make_event_row(run_id=self._event_run_id, domain="chemistry", operation="measure",
                args=args, result={"y": y}, elapsed_seconds=dt)
            self.sink.append(record)
            try:
                if self.event_sink is not None: self.event_sink(dict(event))
            except Exception:
                self.sink.pop()
                raise
            self.events.append(dict(event)); self.log.append(i)
            return y
