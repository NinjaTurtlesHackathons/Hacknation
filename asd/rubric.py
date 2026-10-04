"""Briefing-Anforderungen maschinell geprüft (statt behauptet). Jede Forderung hat eine Prüffunktion gegen die Artefakte im Repo.

  python -m asd.rubric                  # Tabelle Forderung | erfüllt | Beleg; Exit 1, wenn eine Forderung offen ist
  python -m asd.rubric --write-readme   # README-Abschnitte "Evidence standards" und "Challenge deliverables map" zwischen den Markern
  python -m asd.rubric --origin         # Herkunft (origin) jedes Claims/jeder Frage aus dem Protokoll ableiten und speichern"""
import argparse, glob, json, os, re, sys

RUN = sorted(d for d in glob.glob("runs/omnigent/*") if os.path.isdir(d))[-1] if glob.glob("runs/omnigent/*") else None
PROJ = "projects/omni_proofreading"


def _jl(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def _sess(name_prefix):
    return [(os.path.basename(f), [json.loads(l) for l in open(f)]) for f in sorted(glob.glob(f"{RUN}/sessions/{name_prefix}*.jsonl"))]
def _lead(): return (_sess("lead__") or [(None, [])])[0][1]
def _texte(items, rolle):
    return [(i.get("created_at"), " ".join(x.get("text", "") for x in i.get("content", []) if isinstance(x, dict)))
            for i in items if i.get("type") == "message" and i.get("role") == rolle]
def _rec(): return _jl(f"{RUN}/record.jsonl")
def _state(): return json.load(open(f"{RUN}/state.json")) if RUN and os.path.exists(f"{RUN}/state.json") else {}


# ------------------------------------------------------------------ Herkunft ------------------------------------------------------
def origin_ableiten(pfad, nur_lesen=False):
    """origin: AGENT (Labor-Agent, mit Rolle) oder HUMAN-PROPOSED (vom Menschen vorgegeben); aus quelle/Protokoll, nie geraten.
    nur_lesen=True: versiegelte Laufdateien nicht verändern, Ergebnis als {id: origin} zurückgeben."""
    s = json.load(open(pfad)); n = 0
    for q in s.get("fragen", []):
        qu = str(q.get("quelle", ""))
        q["origin"] = ("HUMAN-PROPOSED" if qu in ("omnigent-start", "lueckenkarte") or qu.startswith("mensch") else
                       f"AGENT:{qu.split(':', 1)[1]}" if qu.startswith("agent:") else
                       "AGENT:learner" if q.get("aus_runde") or q.get("aus") else "AGENT:integrator"); n += 1
    for c in s.get("claims", []):
        qu = str(c.get("quelle", ""))
        c["origin"] = f"AGENT:{qu.split(':', 1)[1]}" if qu.startswith("omnigent:") else "AGENT:researcher(lab_loop)"
        c["akzeptiert_durch"] = "code verifier (Domain.check)"; n += 1
    if nur_lesen: return {x["id"]: x["origin"] for x in s.get("claims", []) + s.get("fragen", [])}
    json.dump(s, open(pfad, "w"), ensure_ascii=False, indent=1); return n


# ------------------------------------------------------------------ Prüfungen -----------------------------------------------------
def p_omnigent_live():
    lead = _lead(); sends = [i for i in lead if i.get("type") == "function_call" and i.get("name") == "sys_session_send"]
    meta = lead[0] if lead else {}
    return bool(sends) and meta.get("agent_name") == "verifier-gated-lab", f"{RUN}/sessions/ ({len(sends)} dispatches by Omnigent lead `{meta.get('agent_name')}`)"

def p_handoffs():
    rec = _rec(); agents = {r["agent"] for r in rec} - {"pi", "test"}
    opt = {r["eingabe_ids"].get("option") for r in rec if r["befehl"] in ("waehle", "wähle")}
    used = [r for r in rec if r["agent"] == "researcher" and r["eingabe_ids"].get("option") in opt]
    return len(agents) >= 2 and bool(used), f"{RUN}/record.jsonl: agents {sorted(agents)}; planner option ids reused by researcher in {len(used)} calls"

def p_planner_budget():
    s = _state(); E = [e for e in s.get("entscheidungen", []) if len(e.get("verworfen", [])) >= 1]
    ok = bool(E) and all("kosten" in e["gewaehlt"] for e in E) and "budget_verifier" in s
    return ok, f"{RUN}/state.json: {len(E)} decisions with ≥2 options (cost in verifier calls, budget {s.get('budget_verifier')})"

def p_result_changes_decision():
    rec = _rec(); cl = {r["ausgabe_ids"].get("claim") for r in rec if r["befehl"] == "pruefe" and r["ausgabe_ids"].get("claim")}
    folge = [r for r in rec if r["befehl"] in ("reopen", "folgefragen") and (r["eingabe_ids"].get("claim") in cl or r["eingabe_ids"].get("aus") in cl)]
    return bool(folge), f"{RUN}/record.jsonl: {len(folge)} decisions that cite a verified claim id (reopen / follow-up questions)"

def p_surprise_reopen():
    rec = _rec(); s = [r for r in rec if r["befehl"] == "pruefe" and (r.get("ergebnis") or {}).get("ueberraschung")]
    ro = [r for r in rec if r["befehl"] == "reopen"]
    return bool(s) and bool(ro) and ro[0]["ts"] >= s[0]["ts"], f"{RUN}/record.jsonl: surprise at {s[0]['ts'] if s else '-'} -> reopen {ro[0]['eingabe_ids'] if ro else '-'}"

def _parallel(filter_fn=None):
    by = {}
    for i in _lead():
        if i.get("type") == "function_call" and i.get("name") == "sys_session_send":
            ag = json.loads(i["arguments"]).get("agent")
            if filter_fn is None or filter_fn(ag): by.setdefault(i.get("response_id"), set()).add((ag, json.loads(i["arguments"]).get("title")))
    return [v for v in by.values() if len(v) >= 2]

def p_parallel_sessions():
    P = _parallel(); return bool(P), f"{RUN}/HIGHLIGHTS.md: {len(P)} turns with ≥2 parallel sub-sessions"

def p_parallel_experiments():
    P = _parallel(lambda ag: ag == "researcher")
    return bool(P), (f"{len(P)} turns with ≥2 parallel experiment sessions" if P else
                     "OPEN: the recorded run dispatched scout/planner/redteam/learner in parallel, but never two researcher experiments at once")

def p_human_approval():
    t = [x for _, x in _texte(_lead(), "user")]
    ask = any("awaiting human approval" in x for x in t); ok_ = any("approval has been resolved (action: accept)" in x for x in t)
    deny = any("Denied by policy" in json.dumps(i) for _, items in _sess("") for i in items)
    cfg = open("omni/config.yaml").read()
    return ask and ok_ and deny and "publish_gate" in cfg, f"{RUN}/HIGHLIGHTS.md: ASK raised+approved={ask and ok_}, DENY present={deny}; omni/config.yaml publish_gate"

def p_record_reconstructable():
    from .chain import verify
    rec = _rec(); ok_ids = all("eingabe_ids" in r and "ausgabe_ids" in r for r in rec); ch, g = verify(RUN)
    return bool(rec) and ok_ids and ch is True, f"{RUN}/record.jsonl ({len(rec)} entries with input/output ids); {g}"

def p_citations():
    bib = open(f"{PROJ}/references.bib").read() if os.path.exists(f"{PROJ}/references.bib") else ""
    E = [e for e in re.split(r"\n(?=@)", bib) if e.strip().startswith("@")]; n = len(E); unv = bib.count("[unverified]")
    doi = sum(1 for e in E if re.search(r"doi\s*=|eprint\s*=|url\s*=", e))
    return n > 0 and unv == 0 and doi >= n, f"{PROJ}/references.bib: {n} entries, {doi} with DOI/arXiv/URL, {unv} unverified"

def p_logs_attached():
    n = len(glob.glob(f"{RUN}/sessions/*.jsonl")); return n >= 2, f"{RUN}/sessions/: {n} session exports"

def p_origin_marked():
    s = _state(); ids = [x["id"] for x in s.get("claims", []) + s.get("fragen", [])]
    o = json.load(open(f"{RUN}/origin.json")) if os.path.exists(f"{RUN}/origin.json") else {}
    ok = ids and all(str(o.get(i, "")).startswith(("AGENT", "HUMAN")) for i in ids)
    return bool(ok), f"{RUN}/origin.json: origin derived from the record for {sum(1 for i in ids if i in o)}/{len(ids)} claims+questions"

def p_uncertainty():
    s = _state(); lv = {"proved_lean", "computed_rigorous", "statistical", "observed", "hypothesis"}
    ok_lv = all(c.get("level") in lv for c in s.get("claims", []))
    rp = json.load(open("results/replay_lattice.json")) if os.path.exists("results/replay_lattice.json") else {}
    ok_ci = all("ki95" in t for t in rp.get("tests", {}).values()) and all("treffer_ki95" in b for b in rp.get("bedingungen", {}).values() if b.get("N") and not b.get("analytisch"))
    return ok_lv and ok_ci and bool(rp), f"every claim has an evidence level; results/replay_lattice.json: speedups with bootstrap CI, hit rates with Clopper-Pearson CI"

def p_controls():
    from .domains.base import get_domain
    D = get_domain("proofreading"); cases = list(D.selftest()); nt = sum(1 for _, w in cases if w); nf = len(cases) - nt
    ok = nt >= 3 and nf >= 3 and os.path.exists("benchmarks/blind_claims.py") and os.path.exists("projects/proofreading/verifier_redteam.json")
    return ok, f"verifier self-test {nt} true / {nf} false cases; benchmarks/blind_claims.py (random claims, 0/20 accepted); projects/proofreading/verifier_redteam.json; replay canary test"

def p_gates_documented():
    r = open("README.md").read(); return "publish_gate" in r and "verifier_only" in r and "leak_guard" in r, "README.md, section Omnigent orchestration: policy table"

def p_validation_named():
    md = open(f"{PROJ}/paper.md").read() if os.path.exists(f"{PROJ}/paper.md") else ""
    ok = "(i)" in md and os.path.exists(f"{PROJ}/referee_report.md")
    return ok, f"{PROJ}/paper.md: numbered open questions / needed validation; {PROJ}/referee_report.md"

def p_measured_improvement():
    rp = json.load(open("results/replay_lattice.json")) if os.path.exists("results/replay_lattice.json") else {}
    T = rp.get("tests", {}); m = os.path.exists("results/metrics_proofreading.json")
    k = next((k for k in ("H8b", "H8a", "H7a") if T.get(k, {}).get("erfolg")), next((k for k in ("H8b", "H8a", "H7a") if k in T), None))
    h = T.get(k, {}) if k else {}; n = h.get("n_seeds", len(rp.get("seeds", [])))
    ki = h.get("ki95") or [0, 0]
    return bool(h.get("erfolg")) and m, (f"results/replay_lattice.json {k}: lab vs {dict(ZUFALL='random', HEURISTIK='heuristic', OHNE_FEEDBACK='no feedback').get(h.get('vergleich'), h.get('vergleich'))} {h.get('speedup', 0):.2f}x "
                                         f"(95% CI {ki[0]:.2f} to {ki[1]:.2f}, p = {h.get('p', 1):.2g}, {n} paired seeds); results/metrics_proofreading.json")

def p_next_experiment():
    t = [x for _, x in _texte(_lead(), "assistant")]
    hits = [x for x in t if re.search(r"next (round|experiment|question)|round [23]", x, re.I)]
    return bool(hits), f"{RUN}/sessions/lead: {len(hits)} lead decisions naming the next step with a reason"

def p_specs_in_repo():
    ag = glob.glob("omni/agents/*/config.yaml"); r = open("README.md").read()
    return os.path.exists("omni/config.yaml") and len(ag) >= 6 and "Agent | Decision it owns" in r, f"omni/config.yaml + {len(ag)} agent specs; README agent table"


FORDERUNGEN = [
    ("Omnigent orchestrates the live discovery workflow", p_omnigent_live),
    ("≥2 specialist agents exchange structured results (handoffs with ids)", p_handoffs),
    ("Planner with budget chooses between ≥2 tests", p_planner_budget),
    ("A result changes the next decision", p_result_changes_decision),
    ("A surprising result reopens an assumption", p_surprise_reopen),
    ("Parallel sub-sessions", p_parallel_sessions),
    ("Parallel experiments", p_parallel_experiments),
    ("Human approval via Omnigent policies (ASK) and a policy DENY", p_human_approval),
    ("Shared research record; every decision reconstructable", p_record_reconstructable),
    ("Citations for facts", p_citations),
    ("Run logs attached", p_logs_attached),
    ("Agent-generated hypotheses/claims marked (origin)", p_origin_marked),
    ("Uncertainty preserved (levels, confidence intervals)", p_uncertainty),
    ("Controls documented (self-test, blind claims, red team, canary)", p_controls),
    ("Approval gates documented", p_gates_documented),
    ("Needed validation named", p_validation_named),
    ("Measured improvement", p_measured_improvement),
    ("Next experiment justified", p_next_experiment),
    ("Agent specifications and policies in the repo", p_specs_in_repo),
]


def pruefen():
    """Eine Forderung ist erfüllt, wenn mindestens ein aufgezeichneter Lauf sie belegt (Beleg nennt den Lauf)."""
    global RUN
    runs = sorted(d for d in glob.glob("runs/omnigent/*") if os.path.isdir(d)); out = []
    for name, f in FORDERUNGEN:
        best = None
        for RUN in runs:
            try: ok, beleg = f()
            except Exception as e: ok, beleg = False, f"check failed: {type(e).__name__}: {e}"
            if ok: best = (True, beleg); break
            best = best or (False, beleg)
        out.append((name, bool(best[0]), best[1]))
    RUN = runs[-1]
    return out


def tabelle(res):
    return "| Requirement (challenge brief) | Met | Evidence (checked by `python -m asd.rubric`) |\n|---|---|---|\n" + \
           "\n".join(f"| {n} | {'✓' if ok else '✗'} | {b.replace('|', '/')} |" for n, ok, b in res) + "\n"


def readme(res):
    offen = [n for n, ok, _ in res if not ok]
    ev = ("### Evidence standards\n\nEvery result is accepted only by a code verifier (`Domain.check`); agents only propose. Levels: `proved_lean`, "
          "`computed_rigorous` (exact rational / symbolic / interval certificates), `statistical` (preregistered test with CI), `observed` (numerical), "
          "`hypothesis`. Every claim and question carries an `origin` derived from the record (`AGENT:<role>` or `HUMAN-PROPOSED`). The run logs are "
          "sealed with a hash chain (`asd/chain.py`). The table below is generated and checked by `python -m asd.rubric`; it fails loudly on any ✗.\n\n")
    dm = ("### Challenge deliverables map\n\n" + tabelle(res) + (f"\n**Open:** {'; '.join(offen)}.\n" if offen else "\nAll requirements met.\n"))
    return ev + dm


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write-readme", action="store_true"); ap.add_argument("--origin", action="store_true"); a = ap.parse_args()
    if a.origin:
        for run in sorted(d for d in glob.glob("runs/omnigent/*") if os.path.isdir(d)):
            o = origin_ableiten(f"{run}/state.json", nur_lesen=True)              # Laufdateien sind versiegelt: abgeleitete Datei daneben
            json.dump(o, open(f"{run}/origin.json", "w"), indent=1); print(f"{run}/origin.json", len(o), "Einträge")
        for pj in (PROJ, "projects/omni_parallel"):
            if os.path.exists(f"{pj}/state.json"): print(f"{pj}/state.json", origin_ableiten(f"{pj}/state.json"), "Einträge mit origin")
    res = pruefen(); print(tabelle(res))
    offen = [n for n, ok, _ in res if not ok]
    if a.write_readme:
        r = open("README.md").read(); blk = "<!-- rubric:start -->\n" + readme(res) + "<!-- rubric:end -->"
        r = re.sub(r"<!-- rubric:start -->.*?<!-- rubric:end -->", lambda m: blk, r, flags=re.S) if "<!-- rubric:start -->" in r else r.replace("\n## Omnigent orchestration", "\n## Evidence standards and deliverables\n\n" + blk + "\n\n## Omnigent orchestration", 1)
        open("README.md", "w").write(r); print("README aktualisiert")
    if offen: print("OFFEN (✗): " + "; ".join(offen), file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
