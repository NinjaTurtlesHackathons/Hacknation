"""probatum: das Verifier-Gated Lab als MCP-Server (stdio). Das Claude des Nutzers ist der Forscher; dieser Server liefert Experimente
und ist der EINZIGE, der Claims akzeptiert (über Domain.check). Keine LLM-Aufrufe, kein API-Key, keine Shell, kein Netz.

  probatum-mcp                      # nach `pip install` / `uvx --from <repo> probatum-mcp`
  python -m asd.mcp_server          # aus dem Repo

Umgebung: PROBATUM_HOME (Default ~/.probatum), PROBATUM_TIMEOUT (Sekunden pro Rechnung, Default 120),
PROBATUM_SELFTEST_TIMEOUT (Default 900), PROBATUM_OFFLINE (ohne Wirkung: der Server greift nie aufs Netz zu)."""
import json, multiprocessing as mp, os, time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import mcp_schemas as S

NAME = "probatum"
DOMAINS = {"lattice": "Three-body power-law energy of Bravais lattices (2D/3D/4D): minimisers, sign changes, asymptotics. Numerical verifier with fixed tolerances.",
           "proofreading": "Kinetic proofreading networks (Hopfield): error rate eta, dissipation sigma, speed v. Exact rational certificates and symbolic proofs."}
TIMEOUT = float(os.environ.get("PROBATUM_TIMEOUT", "120"))
SELFTEST_TIMEOUT = float(os.environ.get("PROBATUM_SELFTEST_TIMEOUT", "900"))
REGELN = ("Rules: (1) Only submit_claim can confirm a result; it calls the domain's code verifier. (2) Tolerances belong to the verifier: "
          "tolerance fields in a claim are removed and reported. (3) Unknown fields are rejected. (4) Every call is logged to record.jsonl. "
          "(5) A rejected claim is a result too: report it openly. (6) Every number in a write-up must come from a confirmed claim.")

mcp = FastMCP(NAME, log_level="WARNING", instructions=(
    "probatum is a verifier-gated research lab. You (the assistant) propose experiments and claims; probatum runs experiments and is the ONLY "
    "authority that accepts claims (submit_claim -> code verifier). Start with list_domains, selftest(domain), describe(domain). " + REGELN))
_SELFTEST_OK: dict[str, dict] = {}


# ---------------------------------------------------------------- Speicherung ----------------------------------------------------
def _home(domain):
    d = Path(os.environ.get("PROBATUM_HOME", Path.home() / ".probatum")) / domain; d.mkdir(parents=True, exist_ok=True); return d


def _state(domain):
    p = _home(domain) / "state.json"
    return json.loads(p.read_text()) if p.exists() else {"domain": domain, "claims": [], "abgelehnt": [], "experimente": []}


def _save(domain, s): (_home(domain) / "state.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str))


def _record(domain, tool, ein, aus):
    with open(_home(domain) / "record.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": tool, "eingabe": ein, "ausgabe": aus}, ensure_ascii=False, default=str) + "\n")


# ---------------------------------------------------------------- Rechnen im Subprozess mit Timeout ------------------------------
def _worker(domain, kind, payload, q):
    os.dup2(2, 1)                                                    # stdout des Kindes nach stderr: stdio-Kanal des MCP sauber halten
    try:
        from .domains.base import get_domain
        from .discovery import _jsonfest
        D = get_domain(domain)
        if kind == "run_op": q.put(("ok", _jsonfest(D.run_op(payload["op"], payload["args"]))))
        elif kind == "check":
            ok, why, _ = D.check(payload)
            indep = None
            if ok and hasattr(D, "check_independent"): indep = bool(D.check_independent(payload)[0])
            q.put(("ok", {"bestanden": bool(ok) and indep is not False, "grund": str(why)[:600], "level": D.level(payload) if ok else "hypothesis",
                          "unabhaengig": indep, "text": D.describe(payload) if ok else None}))
        elif kind == "selftest":
            rows = []
            for p, want in D.selftest():
                ok, why, _ = D.check(p); rows.append({"erwartet": bool(want), "ergebnis": bool(ok), "korrekt": bool(ok) == bool(want), "grund": str(why)[:120]})
            q.put(("ok", rows))
        elif kind == "widerspricht": q.put(("ok", bool(D.widerspricht(payload[0], payload[1]))))
    except Exception as e:
        q.put(("fehler", f"{type(e).__name__}: {e}"[:400]))


def _rechne(domain, kind, payload, timeout=None):
    """Führt Domänen-Code in einem eigenen Prozess aus; bricht nach timeout Sekunden hart ab."""
    ctx = mp.get_context("spawn"); q = ctx.Queue(); p = ctx.Process(target=_worker, args=(domain, kind, payload, q))
    p.start(); t = timeout or TIMEOUT; t0 = time.time()
    import queue as _queue
    while True:
        try: status, val = q.get(timeout=1.0); break
        except _queue.Empty:
            if not p.is_alive():                                     # Kind ohne Ergebnis gestorben
                try: status, val = q.get(timeout=1.0); break
                except _queue.Empty: return {"fehler": f"Rechenprozess unerwartet beendet (exit {p.exitcode})"}
            if time.time() - t0 > t:
                p.terminate(); p.join(5)
                if p.is_alive(): p.kill()
                return {"fehler": f"Zeitlimit überschritten ({t:.0f} s); Rechnung abgebrochen"}
    p.join(5)
    return val if status == "ok" else {"fehler": val}


def _gate(domain):
    if domain not in DOMAINS: return {"fehler": f"unbekannte Domäne {domain!r}; verfügbar: {sorted(DOMAINS)}"}
    if domain not in _SELFTEST_OK: return {"fehler": f"Selbsttest der Domäne {domain} in dieser Sitzung noch nicht bestanden: zuerst selftest('{domain}') aufrufen"}
    return None


# ---------------------------------------------------------------- Tools ----------------------------------------------------------
@mcp.tool(description="List available research domains with a short description, allowed experiment types and claim types.")
def list_domains() -> dict:
    out = {d: {"beschreibung": txt, "experimente": sorted(S.ops(d)), "claim_typen": sorted(S.CLAIMS[d]), "selbsttest_bestanden": d in _SELFTEST_OK}
           for d, txt in DOMAINS.items()}
    _record("_server", "list_domains", {}, list(out)); return out


@mcp.tool(description="Run the verifier's self-test for a domain (known true and false statements must be classified correctly). "
                      "All other tools refuse a domain until its self-test has passed in this session. Takes up to a few minutes.")
def selftest(domain: str) -> dict:
    if domain not in DOMAINS: return {"fehler": f"unbekannte Domäne {domain!r}"}
    rows = _rechne(domain, "selftest", None, SELFTEST_TIMEOUT)
    if isinstance(rows, dict): _record(domain, "selftest", {}, rows); return rows
    n_true = sum(r["erwartet"] for r in rows); n_false = len(rows) - n_true; ok = all(r["korrekt"] for r in rows) and n_true >= 3 and n_false >= 3
    out = {"ergebnis": "PASS" if ok else "FAIL", "wahre_faelle": n_true, "falsche_faelle": n_false, "korrekt": sum(r["korrekt"] for r in rows),
           "fehlklassifiziert": [r for r in rows if not r["korrekt"]][:5]}
    if ok: _SELFTEST_OK[domain] = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **{k: out[k] for k in ("wahre_faelle", "falsche_faelle")}}
    _record(domain, "selftest", {}, out); return out


@mcp.tool(description="Describe a domain: context, experiment primitives (with argument schemas), claim types (with field schemas) and the rules. "
                      "Read this before proposing experiments or claims.")
def describe(domain: str) -> dict:
    g = _gate(domain)
    if g: return g
    from .domains.base import get_domain
    D = get_domain(domain)
    out = {"kontext": D.kontext, "experimente_doku": D.primitive_doc, "claims_doku": D.claim_doc,
           "experiment_schemas": {op: {a: {"typ": t, "pflicht": r} for a, (t, r) in args.items()} for op, args in S.ops(domain).items()},
           "claim_schemas": {t: {a: {"typ": ty, "pflicht": r} for a, (ty, r) in f.items()} for t, f in S.CLAIMS[domain].items()},
           "regeln": REGELN + " Tolerance fields are ignored: " + ", ".join(sorted(S.TOLERANZ_FELDER)),
           "parameter": {k: list(v) for k, v in D.parameter().items()} if hasattr(D, "parameter") else {}}
    _record(domain, "describe", {}, "ok"); return out


@mcp.tool(description="Run one experiment. spec = {\"op\": <experiment name>, \"args\": {...}} (see describe). Returns an experiment id and a "
                      f"compact result; errors come back as {{\"fehler\": ...}}. Time limit {TIMEOUT:.0f} s per call (PROBATUM_TIMEOUT).")
def run_experiment(domain: str, spec: dict) -> dict:
    g = _gate(domain)
    if g: return g
    sp, fehler = S.validate_spec(domain, spec)
    if fehler: _record(domain, "run_experiment", spec, {"abgelehnt": fehler}); return {"fehler": "; ".join(fehler)}
    r = _rechne(domain, "run_op", sp); s = _state(domain); eid = f"E{len(s['experimente']) + 1}"
    s["experimente"].append({"id": eid, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "spec": sp, "ergebnis": r}); _save(domain, s)
    txt = json.dumps(r, ensure_ascii=False, default=str)
    out = {"experiment_id": eid, "ergebnis": r if len(txt) <= 6000 else {"gekuerzt": txt[:6000] + " …"}}
    _record(domain, "run_experiment", sp, {"experiment_id": eid, "fehler": r.get("fehler") if isinstance(r, dict) else None}); return out


@mcp.tool(description="Submit a typed claim to the domain's code verifier (the only way to confirm a result). claim = {\"typ\": ..., <fields>} "
                      "(see describe). Returns bestanden, level, grund, claim_id. Tolerance fields are removed and reported; unknown fields are rejected. "
                      "Optional 'frage' records the research question the claim answers.")
def submit_claim(domain: str, claim: dict, frage: str = "") -> dict:
    g = _gate(domain)
    if g: return g
    c, ign, fehler = S.validate_claim(domain, claim)
    if fehler:
        out = {"bestanden": False, "level": "hypothesis", "grund": "Schema: " + "; ".join(fehler), "claim_id": None, "toleranz_ignoriert": ign}
        _record(domain, "submit_claim", claim, out); return out
    r = _rechne(domain, "check", c); s = _state(domain)
    if "fehler" in r: out = {"bestanden": False, "level": "hypothesis", "grund": r["fehler"], "claim_id": None}
    elif r["bestanden"]:
        cid = f"{domain}-C{len(s['claims']) + 1}"
        s["claims"].append({"id": cid, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "frage": frage, "claim": c, "text": r["text"], "level": r["level"],
                            "grund": r["grund"], "status": "bestätigt", "gegenpruefungen": [], "unabhaengig_geprueft": r["unabhaengig"]})
        out = {"bestanden": True, "level": r["level"], "grund": r["grund"], "claim_id": cid, "aussage": r["text"]}
    else:
        s["abgelehnt"].append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "frage": frage, "claim": c, "grund": r["grund"]})
        out = {"bestanden": False, "level": "hypothesis", "grund": r["grund"], "claim_id": None}
    if ign: out["toleranz_ignoriert"] = ign
    _save(domain, s); _record(domain, "submit_claim", c, out); return out


@mcp.tool(description="Red-team a confirmed claim with a counter-claim (same claim types) that should pass if the original were false. "
                      "If the counter-claim passes AND logically contradicts the original, the original becomes 'angefochten' (contested).")
def challenge_claim(domain: str, claim_id: str, counter_claim: dict) -> dict:
    g = _gate(domain)
    if g: return g
    s = _state(domain); orig = next((x for x in s["claims"] if x["id"] == claim_id), None)
    if not orig: return {"fehler": f"Claim {claim_id} nicht gefunden"}
    c, ign, fehler = S.validate_claim(domain, counter_claim)
    if fehler: return {"fehler": "Schema: " + "; ".join(fehler)}
    r = _rechne(domain, "check", c)
    if "fehler" in r: out = {"claim_id": claim_id, "status": orig["status"], "gegenpruefung_bestanden": None, "grund": r["fehler"]}
    else:
        wid = bool(r["bestanden"]) and _rechne(domain, "widerspricht", [orig["claim"], c]) is True
        orig["gegenpruefungen"].append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "claim": c, "bestanden": r["bestanden"], "widerspruch": wid, "grund": r["grund"]})
        if wid: orig["status"] = "angefochten"
        out = {"claim_id": claim_id, "status": orig["status"], "gegenpruefung_bestanden": r["bestanden"], "widerspruch": wid, "grund": r["grund"]}
        _save(domain, s)
    if ign: out["toleranz_ignoriert"] = ign
    _record(domain, "challenge_claim", {"claim_id": claim_id, "counter": c}, out); return out


@mcp.tool(description="List claims of a domain with level, status and evidence. status: 'bestätigt', 'angefochten', 'abgelehnt' or empty for confirmed+contested.")
def list_claims(domain: str, status: str = "") -> dict:
    if domain not in DOMAINS: return {"fehler": f"unbekannte Domäne {domain!r}"}
    s = _state(domain)
    if status == "abgelehnt": return {"abgelehnt": [{"frage": x["frage"], "claim": x["claim"], "grund": x["grund"][:300]} for x in s["abgelehnt"]]}
    cl = [x for x in s["claims"] if not status or x["status"] == status]
    return {"claims": [{"claim_id": x["id"], "aussage": x["text"], "level": x["level"], "status": x["status"], "beleg": x["grund"][:300],
                        "gegenpruefungen": len(x["gegenpruefungen"])} for x in cl], "abgelehnt_anzahl": len(s["abgelehnt"])}


@mcp.tool(description="Return the last entries of the research record (every tool call with inputs and outputs) for a domain.")
def research_record(domain: str, last_n: int = 20) -> dict:
    if domain not in DOMAINS: return {"fehler": f"unbekannte Domäne {domain!r}"}
    p = _home(domain) / "record.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines()[-max(1, min(last_n, 200)):]] if p.exists() else []
    return {"eintraege": rows, "datei": str(p)}


@mcp.tool(description="Prepare a paper: probatum's paper generator needs an LLM, so this returns the verified claims as a structured list "
                      "(claim_id, text, level, evidence) plus writing rules. YOU write the paper from it: every number must come from a listed claim, "
                      "cite claim ids, report rejected and contested claims honestly.")
def build_paper(domain: str, title: str = "", authors: str = "") -> dict:
    if domain not in DOMAINS: return {"fehler": f"unbekannte Domäne {domain!r}"}
    s = _state(domain)
    out = {"titel": title, "autoren": authors,
           "regeln": ["Every sentence with a result cites a claim_id.", "Every number must appear in the cited claim (no rounding beyond it).",
                      "'Theorem' only for level computed_rigorous / proved_lean; level observed/statistical = 'numerical observation'.",
                      "Report rejected claims and contested claims in a 'Negative results' section.", "Do not cite literature you have not verified."],
           "claims": [{"claim_id": x["id"], "text": x["text"], "level": x["level"], "status": x["status"], "beleg": x["grund"][:400],
                       "gegenpruefungen": [{"bestanden": g["bestanden"], "widerspruch": g["widerspruch"]} for g in x["gegenpruefungen"]]} for x in s["claims"]],
           "abgelehnt": [{"claim": x["claim"], "grund": x["grund"][:300]} for x in s["abgelehnt"]],
           "gliederung": ["Abstract", "Introduction", "Model and assumptions", "Method", "Results", "Negative results", "Discussion", "Appendix: provenance (claim_id -> evidence)"]}
    _record(domain, "build_paper", {"titel": title}, {"claims": len(out["claims"])}); return out


# ---------------------------------------------------------------- Resources ------------------------------------------------------
@mcp.resource("probatum://domains/{domain}/claims", mime_type="application/json", description="All claims (confirmed, contested) and rejected attempts of a domain.")
def claims_resource(domain: str) -> str:
    return json.dumps(_state(domain) if domain in DOMAINS else {"fehler": "unbekannte Domäne"}, ensure_ascii=False, default=str)


@mcp.resource("probatum://domains/{domain}/record", mime_type="application/x-ndjson", description="Last 200 lines of the research record (JSONL).")
def record_resource(domain: str) -> str:
    p = _home(domain) / "record.jsonl"
    return "\n".join(p.read_text().splitlines()[-200:]) if domain in DOMAINS and p.exists() else ""


@mcp.resource("probatum://guide", mime_type="text/markdown", description="Short guide to probatum.")
def guide() -> str:
    return ("# probatum guide\n\n1. `list_domains`, then `selftest(domain)` (required once per session).\n2. `describe(domain)`: experiments, claim types, rules.\n"
            "3. Propose two rival experiments, pick one with a reason, `run_experiment`.\n4. Turn the result into a typed claim, `submit_claim`. "
            "Only confirmed claims count; report rejections.\n5. Try to break it: `challenge_claim` with a counter-claim.\n6. `list_claims`, `build_paper` "
            f"(you write, every number from a claim).\n\nData: {os.environ.get('PROBATUM_HOME', '~/.probatum')}/<domain>/state.json and record.jsonl.\n\n{REGELN}\n")


# ---------------------------------------------------------------- Prompts --------------------------------------------------------
@mcp.prompt(name="research_round", description="One verifier-gated research round: two rival experiments, a choice, a claim, a red-team attempt, a follow-up.")
def research_round(domain: str = "proofreading", question: str = "") -> str:
    return (f"Run one research round with the probatum tools in domain '{domain}'" + (f" on this question: {question}" if question else "") + ".\n"
            "1. If not done in this session: selftest. Then describe the domain.\n"
            "2. Propose TWO rival experiments (e.g. broad scan vs. deep precise computation), state cost and expected information gain of each, "
            "choose one and say why.\n3. run_experiment; summarise the result in one line with its experiment id.\n"
            "4. Formulate ONE typed claim exactly as strong as the evidence and call submit_claim.\n"
            "5. Try to refute it yourself: challenge_claim with a counter-claim that would pass if the claim were false.\n"
            "6. Name the next question and why.\nOnly what submit_claim confirms counts as a result. Report rejected claims openly, with the verifier's reason. "
            "Never state numbers that are not in a confirmed claim or an experiment result.")


@mcp.prompt(name="verify_my_result", description="Check one of your own statements: translate it into a claim type and let the verifier decide.")
def verify_my_result(statement: str, domain: str = "proofreading") -> str:
    return (f"The user claims: \"{statement}\"\nUse probatum in domain '{domain}': selftest if needed, describe, then translate the statement into the "
            "closest claim type WITHOUT making it weaker or stronger (say explicitly if it cannot be expressed exactly), run experiments if parameters "
            "are needed, and call submit_claim. Report the verdict, the level and the verifier's reason verbatim. If rejected, say what part failed.")


def main():
    mcp.run("stdio")


if __name__ == "__main__":
    main()
