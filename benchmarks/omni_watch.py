"""Beobachtet eine Omnigent-Session: Status, offene Freigaben (ASK), letzte Tool-Aufrufe, record.jsonl.
  python benchmarks/omni_watch.py <session_id> [projekt]"""
import json, sys, urllib.request

BASE = "http://127.0.0.1:6767/v1"
sid = sys.argv[1]; proj = sys.argv[2] if len(sys.argv) > 2 else "omni_proofreading"
d = json.load(urllib.request.urlopen(f"{BASE}/sessions/{sid}"))
print("status:", d["status"], "| kosten_usd:", d.get("total_cost_usd"), "| offene Freigaben:",
      [(e.get("elicitation_id"), (e.get("params") or {}).get("message", "")[:80], (e.get("params") or {}).get("target_session_id")) for e in d.get("pending_elicitations") or []])
for it in d["items"][-8:]:
    t = it.get("type"); c = it.get("content")
    txt = it.get("arguments") or it.get("output") or (" ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else c)
    print(f"  [{t}] {it.get('name') or it.get('role') or ''} {str(txt)[:200]}")
try:
    for l in open(f"projects/{proj}/record.jsonl").readlines()[-12:]:
        r = json.loads(l); print(f"  rec {r['ts'][11:]} {r['agent']:10s} {r['befehl']:11s} ein={r['eingabe_ids']} aus={r['ausgabe_ids']}")
except FileNotFoundError: print("  (noch kein record.jsonl)")
