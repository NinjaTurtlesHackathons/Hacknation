"""Die sechs Demo-Beats des Briefings automatisch aus einem aufgezeichneten Lauf: Question, Agent handoffs, Experiment, Result,
What the lab learned, Next experiment. Jeder Beat mit Zeitstempel, IDs, Kurztext AUS DEM PROTOKOLL und Beleg-Links.

  python -m asd.beats runs/omnigent/<datum>      -> <run>/beats.json, web/tour.html (Guided tour), docs/VIDEO_SCRIPT.md"""
import datetime, glob, html, json, os, re, sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Zurich")


def _z(ts):
    if isinstance(ts, (int, float)): return datetime.datetime.fromtimestamp(ts, TZ)
    return datetime.datetime.fromisoformat(ts).replace(tzinfo=datetime.timezone.utc).astimezone(TZ)


def _txt(it): return " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict))


def beats(run):
    rec = [json.loads(l) for l in open(f"{run}/record.jsonl")]
    lead_f = glob.glob(f"{run}/sessions/lead__*.jsonl")[0]; lead = [json.loads(l) for l in open(lead_f)][1:]
    st = json.load(open(f"{run}/state.json")); fr = {q["id"]: q for q in st.get("fragen", [])}
    B = []
    # 1 Question
    q0 = next(i for i in lead if i.get("type") == "message" and i.get("role") == "user")
    start_q = next((q for q in st["fragen"] if q.get("quelle") == "omnigent-start" and q["status"] != "zurückgestellt"), None) or \
              next((fr[r["eingabe_ids"]["frage"]] for r in rec if r["befehl"] in ("waehle", "wähle") and r["eingabe_ids"].get("frage") in fr), {})
    B.append({"beat": "Question", "zeit": _z(q0["created_at"]), "ids": [start_q.get("id")], "text": f"Task: {_txt(q0)[:220]} | Question {start_q.get('id')}: {start_q.get('frage', '')[:260]}",
              "beleg": [f"{os.path.basename(lead_f)}", "prereg.md"], "bildschirm": "Omnigent terminal with the start prompt; prereg.md"})
    # 2 Agent handoffs (erster Zug mit >= 2 Dispatches)
    by = {}
    for i in lead:
        if i.get("type") == "function_call" and i.get("name") == "sys_session_send":
            a = json.loads(i["arguments"]); by.setdefault(i.get("response_id"), []).append((i["created_at"], a.get("agent"), a.get("args")))
    par = next((v for v in by.values() if len({x[1] for x in v}) >= 2), None) or next(iter(by.values()))
    w = next((r for r in rec if r["befehl"] in ("waehle", "wähle") and r["eingabe_ids"].get("option")), None)
    B.append({"beat": "Agent handoffs", "zeit": _z(min(x[0] for x in par)), "ids": [w["eingabe_ids"]["option"]] if w else [],
              "text": "Lead dispatches in parallel: " + " + ".join(sorted({f"{x[1]} ({x[2]})" for x in par})) +
                      (f". Planner chooses {w['eingabe_ids']['option']} for {w['eingabe_ids']['frage']}: {str(w.get('ergebnis'))[:200]}" if w else ""),
              "beleg": ["record.jsonl", "decisions.md", "HIGHLIGHTS.md"], "bildschirm": "HIGHLIGHTS.md rows 'Parallel dispatch' and 'Choice between options'; decisions.md"})
    # 3 Experiment (längstes/erstes nichttriviales Experiment)
    ok0 = next((r for r in rec if r["befehl"] == "pruefe" and (r.get("ergebnis") or {}).get("bestanden")), None)
    ex = [r for r in rec if r["befehl"] == "experiment" and r["ausgabe_ids"].get("op") not in ("param_names", "family", "doku")
          and (ok0 is None or r["ts"] <= ok0["ts"])]
    e = ex[-1] if ex else None                                   # das Experiment, dessen Daten in den ersten zertifizierten Claim gingen
    if e: B.append({"beat": "Experiment", "zeit": _z(e["ts"]), "ids": [e["ausgabe_ids"].get("experiment")],
                    "text": f"{e['agent']} runs {e['ausgabe_ids'].get('op')} ({e['ausgabe_ids'].get('experiment')}, option {e['eingabe_ids'].get('option')}): {str(e.get('ergebnis'))[:240]}",
                    "beleg": ["record.jsonl"], "bildschirm": "researcher session: asd.cli experiment call and its result"})
    # 4 Result (erster bestandener Claim)
    ok = next((r for r in rec if r["befehl"] == "pruefe" and (r.get("ergebnis") or {}).get("bestanden")), None)
    if ok: B.append({"beat": "Result", "zeit": _z(ok["ts"]), "ids": [ok["ausgabe_ids"].get("claim")],
                     "text": f"Verifier accepts {ok['ausgabe_ids'].get('claim')} ({ok['ergebnis'].get('level')}): {ok['ergebnis'].get('grund', '')[:200]}",
                     "beleg": ["record.jsonl", "state.json"], "bildschirm": "RESULT line of asd.cli pruefe"})
    # 5 What the lab learned (abgelehnter Claim, Überraschung, Reopen)
    ab = next((r for r in rec if r["befehl"] == "pruefe" and r.get("ergebnis") and not r["ergebnis"].get("bestanden")), None)
    ub = next((r for r in rec if r["befehl"] == "pruefe" and (r.get("ergebnis") or {}).get("ueberraschung")), None)
    ro = next((r for r in rec if r["befehl"] == "reopen"), None)
    teile = []
    if ab: teile.append(f"Rejected by the verifier: {ab['ergebnis'].get('grund', '')[:160]}")
    if ub: teile.append(f"Surprise against assumption {ub['ergebnis'].get('widerspricht_annahme')}: {ub['ergebnis'].get('ueberraschung_grund', '')[:160]}")
    if ro: teile.append(f"Planner reopens {ro['eingabe_ids'].get('annahme')} -> new question(s) {ro['ausgabe_ids'].get('fragen')}")
    zs = [r["ts"] for r in (ab, ub, ro) if r]
    if teile: B.append({"beat": "What the lab learned", "zeit": _z(min(zs)), "ids": [x for x in [(ub or {}).get("ausgabe_ids", {}).get("claim"), (ro or {}).get("eingabe_ids", {}).get("annahme")] if x],
                        "text": " | ".join(teile), "beleg": ["record.jsonl", "decisions.md (REOPEN)"], "bildschirm": "decisions.md REOPEN row; RESULT with ueberraschung: true"})
    # 6 Next experiment (letzte Lead-Entscheidung mit Begründung)
    dec = [i for i in lead if i.get("type") == "message" and i.get("role") == "assistant" and re.search(r"next|round [23]", _txt(i), re.I)]
    if dec:
        d = dec[-1] if not re.search(r"paper|scribe", _txt(dec[-1]), re.I) else (dec[-2] if len(dec) > 1 else dec[-1])
        B.append({"beat": "Next experiment", "zeit": _z(d["created_at"]), "ids": [], "text": _txt(d)[:420].replace("\n", " "),
                  "beleg": [os.path.basename(lead_f)], "bildschirm": "lead summary in the Omnigent session"})
    for b in B: b["zeit"] = b["zeit"].strftime("%H:%M:%S")
    return B


TOUR = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guided tour</title><style>
:root{--bg:#fafaf7;--fg:#1d1d1b;--mut:#6b6b66;--acc:#2f5d50;--card:#fff;--line:#e3e1da}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ecebe6;--mut:#a3a29c;--acc:#7fb8a4;--card:#1e1e1c;--line:#33332f}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);font-size:14px;margin-bottom:16px}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:12px 0 20px}.bar>div{height:100%;background:var(--acc);transition:width .4s}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px}
.k{font-size:13px;color:var(--acc);font-weight:600;letter-spacing:.04em;text-transform:uppercase}
.t{font-size:22px;font-weight:650;margin:4px 0 12px}.x{white-space:pre-wrap;word-break:break-word}
.meta{color:var(--mut);font-size:14px;margin-top:12px}.meta a{color:var(--acc)}
nav{display:flex;gap:8px;margin-top:16px;align-items:center}button{font:inherit;padding:8px 16px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
button.p{background:var(--acc);color:#fff;border-color:var(--acc)}
.seal{border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:14px;background:var(--card)}.seal b{color:var(--acc)}.seal.bad b{color:#b3261e}.hint{color:var(--mut);font-size:13px;margin-left:auto}
</style></head><body><main>
<h1>Guided tour: one recorded Omnigent run</h1><div class="sub">__SUB__</div>
<div class="seal" id="seal"></div>
<div class="bar"><div id="bar"></div></div>
<div class="card"><div class="k" id="k"></div><div class="t" id="t"></div><div class="x" id="x"></div><div class="meta" id="m"></div></div>
<nav><button id="prev">Back</button><button class="p" id="next">Next</button><span class="hint">keys: ← → · r = auto play</span></nav>
</main><script>
const B=__DATA__, RUN="__RUN__", T=__TRACE__;let i=0,auto=null;
(function(){const e=document.getElementById('seal');if(!T){e.style.display='none';return}const v=T.verification;
e.className='seal'+(v.passed?'':' bad');e.innerHTML=`<b>${v.passed?'✓ Verified trace':'✗ Trace check failed'}</b> · Omnigent session ${T.omnigent_session_id.slice(0,8)} · ${v.handoffs} handoffs (sha256 of message and inbox entry) · ${v.quittungen} verifier receipts · ${v.deny} policy DENY · ${v.ask_freigegeben}/${v.ask} ASK approved by a human · ${T.hash_kette} · <a href="../${RUN}/trace.json">trace.json</a>`+(v.passed?'':' · failures: '+v.fehlschlaege.join('; '))})();
function show(){const b=B[i];document.getElementById('k').textContent=`Beat ${i+1} of ${B.length} · ${b.zeit} (Zurich)`;
document.getElementById('t').textContent=b.beat;document.getElementById('x').textContent=b.text;
document.getElementById('m').innerHTML='Evidence: '+b.beleg.map(f=>`<a href="../${RUN}/${f.split(' ')[0]}">${f}</a>`).join(' · ')+(b.ids.length?' · ids: '+b.ids.join(', '):'');
document.getElementById('bar').style.width=((i+1)/B.length*100)+'%';}
function go(d){i=Math.max(0,Math.min(B.length-1,i+d));show();}
document.getElementById('next').onclick=()=>go(1);document.getElementById('prev').onclick=()=>go(-1);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1);
if(e.key==='r'){if(auto){clearInterval(auto);auto=null}else{i=0;show();auto=setInterval(()=>{if(i>=B.length-1){clearInterval(auto);auto=null}else go(1)},7000)}}});
show();</script></body></html>"""


def main():
    run = sys.argv[1].rstrip("/"); B = beats(run)
    json.dump(B, open(f"{run}/beats.json", "w"), indent=1, ensure_ascii=False)
    os.makedirs("web", exist_ok=True)
    tr = json.load(open(f"{run}/trace.json")) if os.path.exists(f"{run}/trace.json") else None
    tr_klein = {k: tr[k] for k in ("omnigent_session_id", "verification", "hash_kette")} if tr else None
    open("web/tour.html", "w").write(TOUR.replace("__DATA__", json.dumps(B, ensure_ascii=False)).replace("__TRACE__", json.dumps(tr_klein, ensure_ascii=False)).replace("__RUN__", run)
                                     .replace("__SUB__", html.escape(f"{run} · six beats extracted automatically from record.jsonl and the session logs (python -m asd.beats)")))
    L = ["# Video script (generated from beats.json by `python -m asd.beats`)", "", f"Source run: `{run}`. Texts in column 4 are drafts; every fact in them comes from the run's logs.", "",
         "| Time (video) | Beat | Screen | Narration draft |", "|---|---|---|---|", "| 0:00–0:15 | Trailer (before) | *placeholder: title card, team* | *placeholder* |"]
    t = 15
    for b in B:
        L.append(f"| {t // 60}:{t % 60:02d}–{(t + 15) // 60}:{(t + 15) % 60:02d} | {b['beat']} ({b['zeit']}) | {b['bildschirm']} | {b['text'][:260].replace('|', '/')} |"); t += 15
    L.append(f"| {t // 60}:{t % 60:02d}–{(t + 15) // 60}:{(t + 15) % 60:02d} | Trailer (after) | *placeholder: key numbers from results/FROZEN.json* | *placeholder* |")
    open("docs/VIDEO_SCRIPT.md", "w").write("\n".join(L) + "\n")
    print(json.dumps([{k: b[k] for k in ("beat", "zeit", "ids")} for b in B], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
