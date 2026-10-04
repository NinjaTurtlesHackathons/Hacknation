"""Exportiert einen Omnigent-Lauf nach runs/omnigent/<datum>/ und erzeugt HIGHLIGHTS.md (Zeitstempel der Schlüsselmomente fürs Video).
  /root/omni-venv/bin/python benchmarks/omni_export.py <lead_session_id> [--projekt omni_proofreading]
Exportiert die Lead-Session und rekursiv alle Sub-Sessions (conversation_id aus sys_session_send), kopiert record.jsonl, decisions.md,
prereg.md, state.json des Projekts. Alle Zeiten in Europe/Zurich."""
import argparse, datetime, json, os, shutil, subprocess
from zoneinfo import ZoneInfo

OMNI = "/root/omni-venv/bin/omnigent"
TZ = ZoneInfo("Europe/Zurich")


def zeit(ts):
    if isinstance(ts, (int, float)): return datetime.datetime.fromtimestamp(ts, TZ).strftime("%H:%M:%S")
    return datetime.datetime.fromisoformat(ts).replace(tzinfo=datetime.timezone.utc).astimezone(TZ).strftime("%H:%M:%S")   # record.jsonl: UTC


def export(sid, out, name, seen):
    if sid in seen: return []
    seen.add(sid); fn = f"{out}/sessions/{name}__{sid[:8]}.jsonl"
    subprocess.run([OMNI, "session", "export", "--id", sid, "-o", fn], capture_output=True, text=True)
    items = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []
    rows = [(name, it) for it in items]
    for it in items:
        if it.get("type") == "function_call_output" and '"conversation_id"' in str(it.get("output", "")):
            try: o = json.loads(it["output"])
            except Exception: continue
            if o.get("kind") == "sub_agent" and o.get("conversation_id"):
                rows += export(o["conversation_id"], out, f"{o.get('agent')}-{(o.get('title') or '').replace(' ', '_')[:30]}", seen)
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("sid"); ap.add_argument("--projekt", default="omni_proofreading"); ap.add_argument("--datum", default="")
    a = ap.parse_args(); datum = a.datum or datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    out = f"runs/omnigent/{datum}"; os.makedirs(f"{out}/sessions", exist_ok=True)
    rows = export(a.sid, out, "lead", set())
    for f in ("record.jsonl", "decisions.md", "prereg.md", "state.json"):
        if os.path.exists(f"projects/{a.projekt}/{f}"): shutil.copy(f"projects/{a.projekt}/{f}", f"{out}/{f}")
    rec = [json.loads(l) for l in open(f"{out}/record.jsonl")] if os.path.exists(f"{out}/record.jsonl") else []

    H = []                                                        # (zeit, moment, beleg)
    seen_calls = set()
    for agent, it in rows:
        if it.get("type") == "function_call_output" and "Denied by policy" in str(it.get("output", "")):
            key = (agent, str(it.get("output"))[:80])
            if key in seen_calls: continue
            seen_calls.add(key); H.append((it["created_at"], "DENY (policy)", f"{agent}: {json.loads(it['output']).get('error', '')[:140]}"))
        if agent == "lead" and it.get("type") == "message" and it.get("role") == "user":
            t = " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict))
            if "awaiting human approval" in t: H.append((it["created_at"], "ASK raised (policy publish_gate)", t[:200]))
            if "approval has been resolved" in t: H.append((it["created_at"], "ASK approved by a human", t[:200]))
    # parallele Dispatches: >= 2 sys_session_send derselben Lead-Antwort (gleiche response_id) an verschiedene Agenten
    by_resp = {}
    for agent, it in rows:
        if agent == "lead" and it.get("type") == "function_call" and it.get("name") == "sys_session_send":
            try: ag = json.loads(it["arguments"]).get("agent")
            except Exception: continue
            by_resp.setdefault(it.get("response_id"), {})[ag] = it["created_at"]
    for r, d in by_resp.items():
        if len(d) >= 2: H.append((min(d.values()), "Parallel dispatch", " + ".join(sorted(d))))
    for r in rec:
        b = r["befehl"]; e = r.get("ergebnis") if isinstance(r.get("ergebnis"), dict) else {}
        if b in ("waehle", "wähle") and r["eingabe_ids"].get("option"): H.append((r["ts"], "Choice between options", f"{r['agent']}: option {r['eingabe_ids']['option']} for {r['eingabe_ids'].get('frage')}: {str(r.get('ergebnis'))[:140]}"))
        if b == "pruefe" and e.get("bestanden"): H.append((r["ts"], "Confirmed claim (verifier)", f"{e.get('claim_id')} {e.get('level')}: {e.get('grund', '')[:100]}"))
        if b == "pruefe" and e and not e.get("bestanden"): H.append((r["ts"], "Rejected claim (verifier)", e.get("grund", "")[:140]))
        if b == "pruefe" and e.get("ueberraschung"): H.append((r["ts"], "Surprise (contradicts preregistered assumption)", f"{e.get('widerspricht_annahme')}: {e.get('ueberraschung_grund', '')[:140]}"))
        if b == "reopen": H.append((r["ts"], "Reopen + re-plan", f"{r['eingabe_ids']} -> {r['ausgabe_ids']}: {str(r.get('ergebnis'))[:120]}"))
        if b == "redteam": H.append((r["ts"], "Red team (opus)", f"{r['eingabe_ids']} -> {r.get('ergebnis')}"))
        if b == "folgefragen": H.append((r["ts"], "Follow-up questions", f"{r['eingabe_ids']} -> {r['ausgabe_ids']}"))
    for agent, it in rows:                                        # Folgeentscheidungen des Leads (Textantworten nach Ergebnissen)
        if agent == "lead" and it.get("type") == "message" and it.get("role") == "assistant":
            t = " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict))
            if any(k in t.lower() for k in ("next round", "round 2", "round 3", "next experiment", "summary")): H.append((it["created_at"], "Lead decision", t[:220].replace("\n", " ")))
    H = sorted(H, key=lambda h: zeit(h[0]))
    L = [f"# Omnigent run {datum}: highlights", "", f"Lead session `{a.sid}`; {len({r[0] for r in rows})} sessions exported to `sessions/`; "
         f"{len(rec)} harness calls in `record.jsonl`. Times: Europe/Zurich.", "", "| Time | Moment | Evidence |", "|---|---|---|"]
    L += [f"| {zeit(t)} | {m} | {b.replace('|', '/')} |" for t, m, b in H]
    open(f"{out}/HIGHLIGHTS.md", "w").write("\n".join(L) + "\n")
    chain = " -> ".join(dict.fromkeys(r["agent"] for r in rec if r["agent"] not in ("pi", "test")))
    print(f"{out}: {len(rows)} items, {len(H)} highlights; agent chain in record.jsonl: {chain}")


if __name__ == "__main__":
    main()
