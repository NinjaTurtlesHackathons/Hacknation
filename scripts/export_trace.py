"""Nachweisbare Omnigent-Spur eines Laufs: runs/<lauf>/trace.json mit Session-ID, jedem Handoff (Sender, Empfänger, Zeit, sha256 von Nachricht
und Inbox-Eintrag), jeder Verifier-Quittung (claim_id, Ergebnis, Zertifikats-Hash), Policy-Ereignissen (DENY/ASK + Freigabe) und am Ende
verification.passed mit der Liste der Fehlschläge.

  python scripts/export_trace.py runs/omnigent/<datum>

Geprüft wird u. a.: jeder Handoff hat ein Ergebnis in der Inbox; jede Bestätigung hat eine Verifier-Quittung mit Zertifikat; die Hash-Kette
ist intakt; eine spätere Runde stützt sich auf eine dokumentierte Entscheidung der früheren (Fragen-ID aus reopen/folgefragen/waehle)."""
import glob, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asd.chain import verify  # noqa: E402

H = lambda t: hashlib.sha256(str(t).encode()).hexdigest()


def main(run):
    lead_f = glob.glob(f"{run}/sessions/lead__*.jsonl")[0]; L = [json.loads(l) for l in open(lead_f)]; meta, items = L[0], L[1:]
    rec = [json.loads(l) for l in open(f"{run}/record.jsonl")]; st = json.load(open(f"{run}/state.json"))
    fehler = []
    # Handoffs: sys_session_send (dedupliziert über conversation_id) + passende Inbox-Ergebnisse
    sends, seen = [], set()
    for i, it in enumerate(items):
        if it.get("type") == "function_call_output" and '"conversation_id"' in str(it.get("output", "")):
            try: o = json.loads(it["output"])
            except Exception: continue
            if o.get("kind") != "sub_agent" or o["conversation_id"] in seen: continue
            seen.add(o["conversation_id"])
            call = next((x for x in reversed(items[:i]) if x.get("type") == "function_call" and x.get("name") == "sys_session_send"), {})
            sends.append({"sender": meta.get("agent_name"), "empfaenger": o.get("agent"), "titel": o.get("title"), "zeit": it.get("created_at"),
                          "conversation_id": o["conversation_id"], "nachricht_sha256": H(call.get("arguments", "")), "inbox_sha256": None})
    inbox = [it for it in items if it.get("type") == "function_call_output" and "completed" in str(it.get("output", "")) and "sub-agent task" in str(it.get("output", ""))]
    for s in sends:
        e = next((x for x in inbox if s["conversation_id"] in str(x.get("output"))), None)
        if e: s["inbox_sha256"] = H(e["output"]); s["inbox_zeit"] = e.get("created_at")
        else: fehler.append(f"Handoff an {s['empfaenger']} ({s['titel']}) ohne Inbox-Ergebnis")
    # Verifier-Quittungen
    claims = {c["id"]: c for c in st.get("claims", [])}; quitt = []
    for r in rec:
        if r["befehl"] not in ("pruefe", "prüfe"): continue
        e = r.get("ergebnis") or {}; cid = (r.get("ausgabe_ids") or {}).get("claim")
        c = claims.get(cid) if cid else None
        quitt.append({"zeit": r["ts"], "claim_id": cid, "bestanden": e.get("bestanden"), "level": e.get("level"),
                      "zertifikat_sha256": H(json.dumps(c["pruefung"], sort_keys=True) + c.get("grund", "")) if c else None, "claim_hash": e.get("claim_hash")})
        if e.get("bestanden") and not c: fehler.append(f"Bestätigung {cid} ohne Claim im Zustand")
    vorher = st.get("runden_vor_omnigent", 0)                     # Claims, die nur aus einem früheren Lauf übernommen wurden, nicht prüfen
    for cid, c in claims.items():
        if (c.get("runde") or 0) <= vorher: continue
        if str(c.get("quelle", "")).startswith("omnigent:") and c.get("status") == "bestätigt" and not any(q["claim_id"] == cid for q in quitt):
            fehler.append(f"Claim {cid} bestätigt, aber ohne Verifier-Quittung")
    # Policy-Ereignisse aus allen Sessions
    pol = []
    for f in sorted(glob.glob(f"{run}/sessions/*.jsonl")):
        for it in (json.loads(l) for l in open(f)):
            out = str(it.get("output", "")); txt = " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict)) if isinstance(it.get("content"), list) else ""
            if "Denied by policy" in out: pol.append({"art": "DENY", "session": os.path.basename(f), "zeit": it.get("created_at"), "grund": json.loads(out).get("error", "")[:160] if out.startswith("{") else out[:160]})
            if "awaiting human approval" in txt: pol.append({"art": "ASK", "session": os.path.basename(f), "zeit": it.get("created_at"), "grund": txt[:160]})
            if "approval has been resolved" in txt: pol.append({"art": "ASK_FREIGEGEBEN" if "accept" in txt else "ASK_ABGELEHNT", "session": os.path.basename(f), "zeit": it.get("created_at")})
    pol = [dict(t) for t in {json.dumps(p, sort_keys=True): p for p in pol}.values()]
    # Runde 2 stützt sich auf Entscheidung von Runde 1
    entsch = [(r["ts"], set((r.get("ausgabe_ids") or {}).get("fragen") or []) | ({r["eingabe_ids"].get("frage")} if r["befehl"] in ("waehle", "wähle") else set()))
              for r in rec if r["befehl"] in ("reopen", "folgefragen", "waehle", "wähle")]
    research = [s for s in sends if s["empfaenger"] == "researcher"]
    gestuetzt = []
    for s in research:
        m = re.search(r"question=(F\d+)", json.dumps(s)); q = m.group(1) if m else None
        call = next((json.loads(x["arguments"]).get("args") for x in items if x.get("type") == "function_call" and x.get("name") == "sys_session_send" and H(x.get("arguments", "")) == s["nachricht_sha256"]), "")
        m = re.search(r"question=(F\d+)", str(call)); q = m.group(1) if m else q
        frueher = [t for t, fr in entsch if q in fr and t <= __import__("datetime").datetime.utcfromtimestamp(s["zeit"]).strftime("%Y-%m-%dT%H:%M:%S")]
        gestuetzt.append({"researcher": s["titel"], "frage": q, "gestuetzt_auf_entscheidung": bool(frueher)})
    if len(research) >= 2 and not all(g["gestuetzt_auf_entscheidung"] for g in gestuetzt[1:]):
        fehler.append("eine spätere Runde stützt sich nicht auf eine dokumentierte Entscheidung")
    ch, chg = verify(run)
    if ch is False: fehler.append(f"Hash-Kette gebrochen: {chg}")
    trace = {"omnigent_session_id": meta.get("id"), "agent": meta.get("agent_name"), "kosten_usd": meta.get("total_cost_usd"),
             "handoffs": sends, "verifier_quittungen": quitt, "policy_ereignisse": sorted(pol, key=lambda p: p.get("zeit") or 0),
             "runden_stuetzen_sich_auf_entscheidungen": gestuetzt, "hash_kette": chg,
             "verification": {"passed": not fehler, "fehlschlaege": fehler, "handoffs": len(sends), "quittungen": len(quitt),
                              "deny": sum(p["art"] == "DENY" for p in pol), "ask": sum(p["art"] == "ASK" for p in pol), "ask_freigegeben": sum(p["art"] == "ASK_FREIGEGEBEN" for p in pol)}}
    json.dump(trace, open(f"{run}/trace.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(trace["verification"], ensure_ascii=False))
    return 0 if not fehler else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1].rstrip("/")))
