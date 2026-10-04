"""Omnigent-Policies, die ZUSTAND aus dem Projekt-/Laufverzeichnis lesen (sitzungsübergreifend wirksam). In omni/config.yaml eingebunden als
  function: {path: asd.omni_policies.<fabrik>, arguments: {...}}
Voraussetzung: das Paket ist in der Omnigent-Umgebung installiert (`uv pip install -e . --no-deps` im Omnigent-venv).

- loop_guard: eigener Schleifenschutz; ignoriert sys_read_inbox (der eingebaute detect_loop blockiert Headless-Läufe beim dritten leeren Inbox-Abruf)
- allowlist: pro Agent erlaubte asd.cli-Befehle (Rollentrennung); alles andere DENY
- publish_requires_votes: DENY für asd.paper, solange nicht jeder bestätigte Claim ein Verifier-PASS UND ein Red-Team-Votum hat
- no_resubmission: DENY für asd.cli pruefe mit einer Behauptung, die der Verifier schon abgelehnt hat (gleicher Claim-Hash)
- claim_phrases_ask: ASK bei Formulierungen mit Geltungsanspruch ("proved for all", "novel", "first", ...) in Texten, die das Labor schreibt"""
import hashlib, json, os, re, shlex
from pathlib import Path

REPO = Path(os.environ.get("ASD_REPO") or Path(__file__).resolve().parent.parent)
CLI = re.compile(r"asd\.cli\s+([a-zäöü]+)")


def claim_hash(pruefungen):
    """Kanonischer Hash einer Behauptung (Liste der Prüfungen), unabhängig von Schlüsselreihenfolge und Leerzeichen."""
    return hashlib.sha256(json.dumps(pruefungen, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:16]


def _cmd(event):
    if event.get("type") != "tool_call": return None
    d = event.get("data") or {}
    if d.get("name") != "sys_os_shell": return None
    return (d.get("arguments") or {}).get("command") or ""


def _projekt(cmd):
    m = re.search(r"--projekt\s+(\S+)", cmd); return m.group(1).strip("'\"") if m else None


def _state(projekt):
    p = REPO / "projects" / projekt / "state.json"
    return json.loads(p.read_text()) if p.exists() else None


def loop_guard(max_wiederholungen: int = 5, ignoriere: tuple = ("sys_read_inbox",)):
    def pol(event):
        if event.get("type") != "tool_call": return None
        d = event.get("data") or {}; name = d.get("name")
        if name in ignoriere: return None
        sig = hashlib.sha256((str(name) + json.dumps(d.get("arguments"), sort_keys=True, default=str)).encode()).hexdigest()[:16]
        st = event.get("session_state") or {}
        if st.get("loop_guard_sig") == sig:
            n = int(st.get("loop_guard_n", 1)) + 1
            if n >= max_wiederholungen:
                return {"result": "DENY", "reason": f"loop_guard: identical call repeated {n}x ({name}); change the approach"}
            return {"result": "ALLOW", "state_updates": [{"key": "loop_guard_n", "action": "set", "value": n}]}
        return {"result": "ALLOW", "state_updates": [{"key": "loop_guard_sig", "action": "set", "value": sig}, {"key": "loop_guard_n", "action": "set", "value": 1}]}
    return pol


def allowlist(befehle: list = (), paper: bool = False, rolle: str = "agent"):
    erlaubt = set(befehle)
    def pol(event):
        cmd = _cmd(event)
        if cmd is None: return None
        if "asd.paper" in cmd:
            return None if paper else {"result": "DENY", "reason": f"allowlist[{rolle}]: building the paper is the scribe's job"}
        m = CLI.search(cmd)
        if m and m.group(1) not in erlaubt:
            return {"result": "DENY", "reason": f"allowlist[{rolle}]: 'asd.cli {m.group(1)}' is not among the tools of this role ({sorted(erlaubt)})"}
        return None
    return pol


def publish_requires_votes():
    def pol(event):
        cmd = _cmd(event)
        if not cmd or "asd.paper" not in cmd: return None
        pj = _projekt(cmd); st = _state(pj) if pj else None
        if st is None: return {"result": "DENY", "reason": "publish_requires_votes: project state not found (pass --projekt)"}
        neu = [c for c in st.get("claims", []) if str(c.get("quelle", "")).startswith("omnigent:")]
        fehlt = [c["id"] for c in neu if c.get("status") == "bestätigt" and not c.get("red_team")]
        if fehlt:
            return {"result": "DENY", "reason": f"publish_requires_votes: claims without red-team vote: {fehlt}; run the red team first"}
        return None
    return pol


def no_resubmission():
    def pol(event):
        cmd = _cmd(event)
        if not cmd or not re.search(r"asd\.cli\s+(pruefe|prüfe)\b", cmd): return None
        pj = _projekt(cmd); st = _state(pj) if pj else None
        if not st: return None
        try:
            arg = shlex.split(cmd)[shlex.split(cmd).index("--claim-json") + 1]
            c = json.loads(arg) if arg.strip()[:1] in "{[" else json.loads((REPO / arg).read_text())
        except Exception: return None
        ps = c.get("pruefungen") or ([c["pruefung"]] if isinstance(c.get("pruefung"), dict) else [])
        h = claim_hash(ps)
        if h in {w.get("claim_hash") for w in st.get("widerlegt", []) if isinstance(w, dict)}:
            return {"result": "DENY", "reason": f"no_resubmission: this exact claim (hash {h}) was already rejected by the verifier; refine it instead"}
        return None
    return pol


PHRASEN = re.compile(r"proved for all|holds for all|\bnovel\b|\bfirst (?:time|proof|result)|for the first time|erstmals|neuartig|bewiesen für alle", re.I)


def claim_phrases_ask():
    def pol(event):
        if event.get("type") != "tool_call": return None
        d = event.get("data") or {}; a = d.get("arguments") or {}
        txt = a.get("content") if d.get("name") in ("sys_os_write", "sys_os_edit") else (a.get("command") if d.get("name") == "sys_os_shell" else None)
        if not txt or (d.get("name") == "sys_os_shell" and "asd.cli" in txt and "--json" not in txt and "--add-json" not in txt): return None
        m = PHRASEN.search(txt)
        return {"result": "ASK", "reason": f"claim_phrases: wording with a scope claim ('{m.group(0)}') needs human approval"} if m else None
    return pol
