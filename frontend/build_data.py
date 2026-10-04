"""Erzeugt frontend/data/ aus den Protokollen (keine handgeschriebene Zahl auf der Webseite).

  python frontend/build_data.py

Quellen: runs/omnigent/<lauf>/ (record.jsonl, trace.json, CHAIN.json, state.json, sessions/), results/*.json,
projects/<projekt>/certificates/. Ausgabe: frontend/data/site.json, runs/<lauf>.json, raw/<lauf>/ (Eingaben der Hash-Kette,
damit der Browser sie nachrechnen kann), certs/<claim>/ (certificate.json + check.py), results.json.
Deutsche Verifier-Texte werden über feste Muster ins Englische übertragen; was kein Muster trifft, bleibt im Original (lang=de)."""
import ast, datetime as dt, glob, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "frontend", "data")
AGENTS = ["lead", "scout", "planner", "researcher", "redteam", "learner", "scribe"]


def rel(p): return os.path.relpath(p, ROOT)


def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def utc(ts):
    if isinstance(ts, (int, float)): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).replace(tzinfo=None)
    return dt.datetime.fromisoformat(ts)


# ---------- Übertragung der Verifier-Texte ----------
def _fall_en(t):
    t = re.sub(r"Rate außerhalb \[e\^-10, e\^10\] \(\|log k\| = ([\d.]+); auch abgeleitete Rückraten zählen\)?", r"rate outside [e^-10, e^10] (|log k| = \1, derived reverse rates included)", t)
    return t


def en(s):
    """-> (text, lang)."""
    if s is None: return "", "en"
    s = str(s); o = s
    m = re.match(r"Zertifikat \((\w)\) für (\d+)/(\d+) Fälle bestanden(?:; nicht bestanden: (\[.*)$)?", s)
    if m:
        out = f"Certificate ({m[1]}) passed for {m[2]} of {m[3]} cases"
        if m[4]:
            try: faelle = ast.literal_eval(m[4] if m[4].endswith("]") else m[4] + "')]")
            except Exception: faelle = re.findall(r"\('([^']+)', '([^']+)", m[4])
            out += "; failed: " + "; ".join(f"{a}: {_fall_en(b)}" for a, b in faelle)
        return out, "en"
    m = re.match(r"Zertifikat \(b\) Familie (\S+): Schranke (.+?) für (\d+)/(\d+) Mitglieder bewiesen(?:; nicht bewiesen: (.*))?$", s)
    if m:
        fam = "at most two bound states" if m[1] == "gebunden<=2" else m[1]
        out = f"Certificate (b), family with {fam}: bound {m[2]} proved for {m[3]} of {m[4]} members"
        rest = re.sub(r"[\[\]']", "", m[5] or "")
        return out + (f"; not proved: {rest}" if rest else ""), "en"
    m = re.match(r"Zertifikat \(a\): eta = (\S+) \(exakt rational\); sigma in (\[[^\]]+\]) kT; v = (\S+)", s)
    if m: return f"Certificate (a): eta = {m[1]} (exact rational); sigma in {m[2]} kT; v = {m[3]}", "en"
    m = re.match(r"Prüfung nicht ausführbar: (.*)", s)
    if m: return f"Check could not be run: {m[1]}", "en"
    m = re.match(r"neue zertifizierte Verletzung\(en\) (\[[^\]]*\]) ausserhalb der angenommenen Menge (\[[^\]]*\])", s)
    if m: return f"New certified violation(s) {m[1].replace(chr(39), '')} outside the assumed set {m[2].replace(chr(39), '')}", "en"
    rep = {"beste offene Frage (lit_offen, Machbarkeit)": "best open question (open in the literature, feasibility)",
           "im Faden F21 bleiben (Fortschritt oder < 2 Runden)": "stay on thread F21 (progress, or fewer than 2 rounds)",
           "bestätigt": "confirmed", "widerlegt": "refuted"}
    if s in rep: return rep[s], "en"
    m = re.match(r"(\d+) Zeichen", s)
    if m: return f"{m[1]} characters", "en"
    return o, "de" if re.search(r"[äöüß]|\b(der|die|und|für|nicht)\b", o) else "en"


# ---------- Fragen ----------
FRAGE_MUSTER = [
    (r"Welche der (\d+) noch offenen Topologien der Familie mit höchstens zwei gebundenen Zuständen \(fam2_\*\) erreichen eta < e\^\{-2 Delta\} = 1e-4 \(exaktes Zertifikat erreichbar_liste\), und für welche lässt sich die Schranke eta >= 1/D\*\*2 beweisen\?",
     r"Which of the \1 still open topologies of the family with at most two bound states (fam2_*) reach $\\eta < e^{-2\\Delta} = 10^{-4}$ (exact certificate), and for which can the bound $\\eta \\ge 1/D^2$ be proved?"),
    (r"Gibt es unter den (\d+) offenen Topologien der Familie mit höchstens zwei gebundenen Zuständen \(fam2_\*\) weitere, die eta <= e\^\{-2 Delta\} = 1e-4 erreichen \(exaktes Zertifikat erreichbar_liste\), oder lässt sich die Schranke für weitere Mitglieder beweisen\?",
     r"Among the \1 open topologies of the family with at most two bound states (fam2_*), do more reach $\\eta \\le e^{-2\\Delta} = 10^{-4}$ (exact certificate), or can the bound be proved for further members?"),
    (r"Ist die Klassifikation der Familie \(bewiesen / Gegenbeispiel / offen\) mit allen bisher zertifizierten Aussagen konsistent und vollständig gezählt\?",
     "Is the classification of the family (proved / counterexample / open) consistent with every certified statement so far, and completely counted?"),
    (r"Wie verallgemeinern sich die thermodynamischen Unsicherheitsrelationen auf Proofreading-Systeme mit unvollständiger Information oder partieller Beobachtbarkeit der molekularen Zustände\?",
     "How do thermodynamic uncertainty relations generalize to proofreading systems with incomplete information or partial observability of the molecular states?"),
]


def frage_en(t):
    for p, r in FRAGE_MUSTER:
        if re.fullmatch(p, t or ""): return re.sub(p, r, t), "en"
    return t or "", "de" if re.search(r"[äöüß]|\b(der|die|und|für|wie)\b", t or "") else "en"


# ---------- Ereignisse ----------
def _ids(d): return ", ".join(str(x) for v in (d or {}).values() for x in (v if isinstance(v, list) else [v]) if x)


def ereignis_text(e):
    b = e["befehl"]; ei = e.get("eingabe_ids") or {}; ao = e.get("ausgabe_ids") or {}; r = e.get("ergebnis")
    q = ei.get("frage")
    if b == "options": return f"Lists options {', '.join(ao.get('optionen', []))} for {q}", "tool"
    if b == "status": return "Reads the lab status", "tool"
    if b in ("waehle", "wähle"): return f"Chooses {ei.get('option')} for {q}: {r}", "tool"
    if b == "wissen": return f"Reads the knowledge base ({en(r)[0]})", "tool"
    if b == "fragen": return f"Lists open questions: {', '.join(ao.get('offen', [])) or 'none'}", "tool"
    if b == "doku": return "Reads the harness documentation", "tool"
    if b == "plan": return f"Plans the next step: recommends {ao.get('empfehlung')} ({en(r)[0]})", "tool"
    if b == "experiment": return f"Runs experiment {ao.get('experiment')} ({ao.get('op')}) for {q}, option {ei.get('option')}", "tool"
    if b == "folgefragen": return f"Proposes follow-up questions {', '.join(ao.get('fragen', []))} from {ei.get('aus')}", "tool"
    if b == "reopen": return f"Reopens assumption {ei.get('annahme')} because of {ei.get('claim')}: {r}", "policy"
    if b == "redteam":
        st = en((r or {}).get("status"))[0] if isinstance(r, dict) else ""
        return f"Red-team vote on {ei.get('claim')}: {len(ao.get('gegenpruefungen', []))} counter-checks, claim stays {st}", "tool"
    if b in ("pruefe", "prüfe") and isinstance(r, dict):
        g = en(r.get("grund"))[0]
        if r.get("bestanden"): return f"Verifier confirms {r.get('claim_id')} ({r.get('level')}): {g}", "ok"
        return f"Verifier rejects the claim: {g}", "no"
    return f"{b} {_ids(ei)}".strip(), "tool"


def cmd_of(e):
    b = e["befehl"]; ei = e.get("eingabe_ids") or {}
    arg = " ".join(f"--{k} {v}" for k, v in ei.items() if v and k in ("frage", "option", "claim", "annahme", "aus"))
    return f"python -m asd.cli {b} {arg}".strip()


def lead_events(run):
    f = glob.glob(f"{run}/sessions/lead__*.jsonl")
    if not f: return [], None, None
    rows = jl(f[0]); meta = rows[0]; items = rows[1:]; ev = []; task = None
    txt = lambda it: " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict)).strip()
    for it in items:
        if it.get("type") != "message": continue
        t = txt(it)
        if not t: continue
        if it.get("role") == "user" and task is None: task = t; continue
        if it.get("role") == "assistant":
            t = re.sub(r"[`*#_]{1,3}(?=\S)|(?<=\S)[`*_]{1,3}", "", t)          # Markdown-Zeichen der Lead-Notizen entfernen
            ev.append({"ts": utc(it["created_at"]), "agent": "lead", "kind": "lead", "text": re.sub(r"\s+", " ", t)[:240]})
    return ev, task, meta


def agent_of_session(s):
    a = s.split("-")[0].split("__")[0]
    return a if a in AGENTS else "lead"


def build_run(run):
    rid = os.path.basename(run); rec = jl(f"{run}/record.jsonl"); trace = json.load(open(f"{run}/trace.json"))
    state = json.load(open(f"{run}/state.json")); chain = json.load(open(f"{run}/CHAIN.json"))
    lev, task, meta = lead_events(run)
    projekt = (re.search(r"project (\S+?),", (meta or {}).get("title", "") or task or "") or [None, None])[1]
    ev = []
    for i, e in enumerate(rec):
        if e["befehl"] == "selftest": continue
        t, k = ereignis_text(e)
        if i == 0 and isinstance(e.get("ergebnis"), dict) and e["ergebnis"].get("prereg_sha256"): t = "Preregistration sealed as the first ledger entry"
        x = {"ts": utc(e["ts"]), "agent": e.get("agent") if e.get("agent") in AGENTS else ("planner" if e.get("agent") == "pi" else (e.get("agent") or "lead")),
             "kind": k, "text": t, "cmd": cmd_of(e), "frage": (e.get("eingabe_ids") or {}).get("frage"), "line": i, "dauer_s": e.get("dauer_s")}
        r = e.get("ergebnis")
        if e["befehl"] in ("pruefe", "prüfe") and isinstance(r, dict):
            x["claim"] = r.get("claim_id"); x["verdict"] = bool(r.get("bestanden"))
            if r.get("ueberraschung"): x["surprise"] = en(r.get("ueberraschung_grund"))[0]
        if e["befehl"] == "redteam": x["claim"] = (e.get("eingabe_ids") or {}).get("claim")
        ev.append(x)
    for p in trace.get("policy_ereignisse", []):
        art = p["art"]; k = {"DENY": "deny", "ASK": "ask", "ASK_FREIGEGEBEN": "allow"}.get(art, "policy")
        grund = re.sub(r"^Denied by policy: ", "", p.get("grund", ""))
        label = {"DENY": "Policy denies", "ASK": "Policy asks a human", "ASK_FREIGEGEBEN": "Human approves"}.get(art, art)
        ev.append({"ts": utc(p["zeit"]), "agent": agent_of_session(p.get("session", "")), "kind": k, "text": f"{label}: {grund}"})
    for h in trace.get("handoffs", []):
        to = agent_of_session(h.get("empfaenger", "")) if h.get("empfaenger") else "lead"
        ev.append({"ts": utc(h["zeit"]), "agent": "lead", "to": to, "kind": "handoff", "text": f"Dispatches {h.get('empfaenger')}: {h.get('titel')}",
                   "hash": h.get("nachricht_sha256")})
    ev += lev
    ev.sort(key=lambda x: (x["ts"], 0 if x["kind"] == "handoff" else 1))
    t0 = ev[0]["ts"]; aktuell = None
    for x in ev:
        if x.get("frage"): aktuell = x["frage"]
        x["round"] = aktuell; x["t"] = x["ts"].strftime("%H:%M:%S"); x["s"] = round((x["ts"] - t0).total_seconds(), 1); x["ts"] = x["ts"].isoformat()
    # Runden = Fragen in Reihenfolge des ersten Auftretens
    fr = {f["id"]: f for f in state.get("fragen", []) if f.get("id")}
    rounds = []
    for x in ev:
        q = x.get("frage")
        if q and q not in [r["id"] for r in rounds]:
            txt, lang = frage_en(fr.get(q, {}).get("frage", ""))
            rounds.append({"id": q, "text": txt, "lang": lang, "source": fr.get(q, {}).get("quelle"), "start": x["s"], "start_t": x["t"]})
    for r in rounds:
        mine = [x for x in ev if x["round"] == r["id"]]
        r["end"] = mine[-1]["s"]; r["end_t"] = mine[-1]["t"]
        r["experiments"] = sum(1 for x in mine if x["text"].startswith("Runs experiment"))
        r["confirmed"] = sum(1 for x in mine if x["kind"] == "ok"); r["rejected"] = sum(1 for x in mine if x["kind"] == "no")
    # Claims dieses Laufs
    from asd.domains.base import get_domain
    D = get_domain(state.get("domain", "proofreading"))
    cl = {c["id"]: c for c in state.get("claims", [])}; claims = []; n_rej = 0
    for x in ev:
        if x["kind"] not in ("ok", "no"): continue
        if x["kind"] == "ok":
            c = cl.get(x["claim"], {}); p = c.get("pruefung") or {}
            try: text = D.describe(p, lang="en")
            except Exception: text = en(c.get("text"))[0]
            rt = [{"text": en(v.get("grund"))[0], "passed": v.get("bestanden"), "contradiction": v.get("widerspruch")} for v in (c.get("red_team") or [])]
            cdir = f"{ROOT}/projects/{projekt}/certificates/{x['claim']}"
            claims.append({"id": x["claim"], "verdict": True, "level": c.get("level"), "text": text, "reason": en(x["text"].split(": ", 1)[-1])[0],
                           "event_s": x["s"], "t": x["t"], "red_team": rt, "surprise": x.get("surprise"),
                           "certificate": x["claim"] if os.path.exists(f"{cdir}/certificate.json") else None,
                           "standalone_note": None if os.path.exists(f"{cdir}/certificate.json") else "Symbolic proof or rigorous logarithms: re-checked with python -m asd.recheck, not standalone in the browser"})
        else:
            n_rej += 1
            m = re.search(r"for \d+ of (\d+) cases", x["text"])
            claims.append({"id": f"rejected-{n_rej}", "verdict": False, "level": "hypothesis",
                           "text": f"Exact reachability certificate for {m[1]} topologies, submitted by the {x['agent']}" if m else f"Claim submitted by the {x['agent']}",
                           "reason": x["text"].split(": ", 1)[-1], "event_s": x["s"], "t": x["t"]})
        x["claim_ref"] = claims[-1]["id"]
    ver = trace.get("verification", {})
    raw = os.path.join(OUT, "raw", rid); shutil.rmtree(raw, ignore_errors=True); os.makedirs(f"{raw}/sessions")
    files = []
    for name, _ in chain["kette"]:
        src = name.split("#")[0]
        if src not in files: files.append(src)
    for f in files: shutil.copy(f"{run}/{f}", f"{raw}/{f}")
    shutil.copy(f"{run}/CHAIN.json", f"{raw}/CHAIN.json")
    dauer = (utc(ev[-1]["ts"]) - utc(ev[0]["ts"])).total_seconds()
    meta_out = {"id": rid, "project": projekt, "task": task, "started": ev[0]["ts"], "ended": ev[-1]["ts"], "duration_min": round(dauer / 60),
                "events": len(ev), "confirmed": sum(1 for c in claims if c["verdict"]), "rejected": n_rej,
                "deny": ver.get("deny"), "ask": ver.get("ask"), "ask_approved": ver.get("ask_freigegeben"), "handoffs": ver.get("handoffs"),
                "cost_usd": round(trace.get("kosten_usd") or 0, 2), "session": trace.get("omnigent_session_id"),
                "chain": {"links": chain["glieder"], "head": chain["kopf"], "sealed": chain["versiegelt"], "files": files},
                "trace_passed": ver.get("passed"), "agents": [a for a in AGENTS if any(x["agent"] == a or x.get("to") == a for x in ev)],
                "sources": [rel(f"{run}/record.jsonl"), rel(f"{run}/trace.json"), rel(f"{run}/CHAIN.json")]}
    return {"meta": meta_out, "rounds": rounds, "events": ev, "claims": claims}


def certs(runs):
    d = os.path.join(OUT, "certs"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for r in runs:
        for c in r["claims"]:
            if not c.get("certificate"): continue
            src = f"{ROOT}/projects/{r['meta']['project']}/certificates/{c['id']}"
            if not os.path.exists(f"{d}/{c['id']}"): shutil.copytree(src, f"{d}/{c['id']}")


def results():
    J = lambda p: json.load(open(f"{ROOT}/{p}")) if os.path.exists(f"{ROOT}/{p}") else None
    fz = J("results/FROZEN.json") or {}; tr = J("results/trust.json")
    fl = fz.get("flaggschiff") or {}; kl = dict(J(fl["quelle"]) or {}, **{k: fl[k] for k in ("topologien", "bewiesen", "verletzt", "offen", "eta_min") if k in fl}) if fl.get("quelle") else None
    namen = {"LAB": "Lab (verifier feedback)", "OHNE_FEEDBACK": "Same agents, no feedback", "ZUFALL": "Random proposals", "HEURISTIK": "Hand-written heuristic", "ORAKEL": "Oracle (analytic upper bound)"}
    rp = fz.get("replay"); rep = None                     # einzige Quelle: results/FROZEN.json (eingefroren von asd.freeze)
    if rp and rp.get("tests"):
        rep = {"source": "results/FROZEN.json", "prereg": rp.get("praeregistrierung"), "budget": rp["budget"], "seeds": rp["seeds"],
               "conditions": [{"key": k, "name": namen.get(k, k), "N": v["N"], "mean": v["mean_N"], "median": v["median_N"], "hits": v.get("treffer"),
                               "analytic": v.get("analytisch")} for k, v in rp["bedingungen"].items()],
               "tests": [{"id": k, "vs": namen.get(v["vergleich"], v["vergleich"]), "speedup": v["speedup"], "ci": v["ki95"], "p": v["p"], "p_bh": v["p_bh"],
                          "n": v["n_seeds"], "supported": v["supported"]} for k, v in rp["tests"].items() if v]}
    trust = {"source": "results/trust.json", "question_source": tr["quelle"],
             "conditions": [{"key": k, "name": v["name"], "n": v["n"], "right": v["richtig"], "wrong": v["falsch"], "unknown": v.get("unbekannt"),
                             "wrong_pct": v["anteil_falsch_pct"], "wrong_ci": v["falsch_ki95_pct"], "right_pct": v["anteil_richtig_pct"]}
                            for k, v in tr["bedingungen"].items()]} if tr else None
    return {"frozen_at": fz.get("zeitpunkt"), "commit": fz.get("commit"), "replay": rep, "trust": trust,
            "stress": dict(fz.get("verifier_stress", {}), source="results/FROZEN.json"), "trust_frozen": fz.get("trust"),
            "classification": dict(kl, source="results/FROZEN.json") if kl else None,
            "metrics": dict(fz.get("metrics", {}), source="results/FROZEN.json")}


def figures(res, runs):
    F = []; st = res["stress"]
    if st.get("blind_claims") is not None:
        F.append({"text": f"{st['blind_claims'] - st['blind_akzeptiert']} of {st['blind_claims']} random or constant claims sent blind to the verifier were rejected, "
                          f"and {st['redteam_fallen_abgelehnt']} of {st['redteam_fallen']} red-team traps.", "source": "results/FROZEN.json", "href": "results.html#stress"})
    T = {x["id"]: x for x in (res["replay"] or {}).get("tests", [])}
    if "H8b" in T:
        t = T["H8b"]; a = T.get("H8a")
        F.insert(0, {"text": f"The lab reached the target claim with {t['speedup']:.1f}× fewer verifier calls than a hand-written heuristic "
                             f"(95% CI {t['ci'][0]:.1f} to {t['ci'][1]:.1f}, p = {t['p']:.1g}) and {a['speedup']:.1f}× fewer than random proposals, on {t['n']} paired seeds."
                             if a else "", "source": res["replay"]["source"], "href": "results.html#acceleration"})
    tc = {c["key"]: c for c in (res["trust"] or {}).get("conditions", [])}
    if "A1" in tc and "B" in tc:
        F.append({"text": f"{tc['A1']['name']} gave a wrong answer {tc['A1']['wrong_pct']:.1f}% of the time; behind the verifier gate, {tc['B']['wrong_pct']:.1f}% "
                          f"({tc['B']['n']} answers each; 12 questions from a single paper, so a small, home-field sample).", "source": res["trust"]["source"], "href": "results.html#trust"})
    return F


def excerpt(runs):
    """Erste Ablehnung, auf die im selben Lauf eine Bestätigung folgt."""
    for r in sorted(runs, key=lambda r: r["meta"]["id"], reverse=True):
        ev = r["events"]
        for i, x in enumerate(ev):
            if x["kind"] != "no": continue
            j = next((j for j in range(i + 1, len(ev)) if ev[j]["kind"] == "ok"), None)
            if j is None: continue
            i = max(k for k in range(i, j) if ev[k]["kind"] == "no")          # die letzte Ablehnung vor der Bestätigung
            k = max(0, i - 2); sl = [y for y in ev[k:j + 1] if y["kind"] != "no" or y is ev[i]]
            ids = {y.get("claim_ref") for y in sl if y.get("claim_ref")}
            return {"run": r["meta"]["id"], "project": r["meta"]["project"], "events": sl, "claims": [c for c in r["claims"] if c["id"] in ids],
                    "source": f"runs/omnigent/{r['meta']['id']}/record.jsonl"}
    return None


def main():
    os.makedirs(f"{OUT}/runs", exist_ok=True)
    runs = [build_run(r) for r in sorted(glob.glob(f"{ROOT}/runs/omnigent/*")) if os.path.exists(f"{r}/trace.json") and os.path.exists(f"{r}/CHAIN.json")]
    for r in runs: json.dump(r, open(f"{OUT}/runs/{r['meta']['id']}.json", "w"), ensure_ascii=False, indent=0)
    certs(runs); res = results(); json.dump(res, open(f"{OUT}/results.json", "w"), ensure_ascii=False, indent=0)
    try: commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception: commit = None
    site = {"generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit": commit, "repo": "https://github.com/alizema700/Daddys-Project",
            "figures": figures(res, runs), "runs": [r["meta"] for r in runs], "excerpt": excerpt(runs)}
    json.dump(site, open(f"{OUT}/site.json", "w"), ensure_ascii=False, indent=0)
    print(f"{len(runs)} runs, {sum(len(r['events']) for r in runs)} events, {len(os.listdir(f'{OUT}/certs'))} certificates -> {rel(OUT)}")


if __name__ == "__main__":
    main()
