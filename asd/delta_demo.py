"""Execute the existing exact geometry verifier through the normalized Lab into Delta."""
import argparse
import json
from pathlib import Path
import time
from .delta_contract import decode_json
from .delta_store import DeltaEventStore
from .discovery import Lab
from .domains.geometric_extremal_domain import DOMAIN


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    base = root / "research/geometric-extremal"
    args.output.mkdir(parents=True, exist_ok=True)
    store = DeltaEventStore(args.output / "events")
    lab = Lab(DOMAIN, event_sink=store)
    start = time.perf_counter()
    for record in json.loads((base / "results/records.json").read_text())["records"]:
        candidate = json.loads((base / record["candidate"]).read_text())
        entry = lab.run("evaluate", {"spec": candidate}, "delta-demo")
        if not entry["ergebnis"]["passed"]: raise RuntimeError("Exact witness verification failed")
    # Exercise a real cache hit without relabelling old search jobs as new discoveries.
    lab.run("evaluate", {"spec": candidate}, "delta-demo")
    stored = store.read()
    expected = {row["event_id"]: row for row in lab.events}
    found = {row["event_id"]: row for row in stored}
    if not all(found.get(k) == v for k,v in expected.items()): raise RuntimeError("Delta event replay mismatch")
    for row in lab.events:
        if not decode_json(row["result_json"])["passed"]: raise RuntimeError("Stored proof failed")
    (args.output / "record.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in lab.events))
    report = {"passed": True, "scope": "New exact verification calls for existing frozen witnesses; not new discovery or historical search reruns",
        "run_id": lab.run_id, "events_this_run": len(lab.events), "cache_hits_this_run": sum(r["cached"] for r in lab.events),
        "domain_seconds": sum(r["elapsed_seconds"] for r in lab.events),
        "total_seconds_including_normalization_and_storage": time.perf_counter() - start,
        "delta": store.inspect(), "local_delta_only": True, "databricks_workspace_run": False}
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
