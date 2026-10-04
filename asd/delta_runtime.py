"""Optional event sinks; normalizing the Lab API never needs optional dependencies."""
import json
import os
import threading
from pathlib import Path
from .delta_contract import validate_event_row


class JsonlEventSink:
    """Append normalized rows for later Delta ingestion; no silent write failure."""
    def __init__(self, path):
        import fcntl
        self._fcntl = fcntl
        self.path = Path(path); self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, row):
        row = validate_event_row(row)
        data = (json.dumps(row, ensure_ascii=False, allow_nan=False, sort_keys=True) + "\n").encode("utf-8")
        # Advisory lock also protects independent POSIX worker processes.
        fcntl = self._fcntl
        with self._lock, self.path.open("ab") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def configured_event_sink():
    """Explicit settings fail closed; no configured sink means in-memory records."""
    delta_path = os.environ.get("ASD_DELTA_PATH")
    jsonl_path = os.environ.get("ASD_RECORD_JSONL")
    if delta_path and jsonl_path:
        raise ValueError("Choose ASD_DELTA_PATH or ASD_RECORD_JSONL, not both")
    if delta_path:
        from .delta_store import DeltaEventStore
        return DeltaEventStore(delta_path)
    if jsonl_path: return JsonlEventSink(jsonl_path)
    return None
