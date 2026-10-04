"""Präregistrierter Vergleich H3 (prereg.md): A1 Claude pur, A2 Claude mit Code, B Framework.
  python benchmarks/run_benchmark.py A1|A2|B [--salts 0,1,2] [--fragen Q1,Q5]
Antworten werden nur gespeichert; die Bewertung macht benchmarks/score.py gegen den Schlüssel."""
import argparse, json, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asd.llm import ask_json, MODEL

B = json.load(open("benchmarks/suleman2026.json")); OUT = "results/benchmark"
FORMAT = '{"antwort": "<Kategorie oder kurze Antwort; \\"unbekannt\\" wenn du es nicht weißt>", "zahl": <Zahl oder null>, "konfidenz": <0..1>, "begruendung": "<kurz>"}'
SYS = "Du bist ein Experte für Gitter-Energieminimierung und mathematische Physik."


def prompt(q): return f"{B['kontext']}\n\nFRAGE: {q['frage']}\n\nAntworte am Ende als JSON: {FORMAT}"


def a1(q, salt): return {"antwort": ask_json(prompt(q), SYS + " Antworte nur mit JSON.", salt=f"A1-{salt}")}


def a2(q, salt):
    """Claude Code headless mit Bash/Python in leerer Sandbox. Transkript wird auf verbotene Zugriffe geprüft."""
    extra = ("\n\nDu darfst in deinem aktuellen Arbeitsverzeichnis Python-Code schreiben und ausführen (numpy/scipy sind installiert). "
             "Kein Internet, keine Dateien außerhalb deines Arbeitsverzeichnisses. Gib als letzte Nachricht nur das JSON aus.")
    with tempfile.TemporaryDirectory() as cwd:
        cmd = [shutil.which("claude"), "-p", prompt(q) + extra, "--output-format", "stream-json", "--verbose", "--model", MODEL,
               "--no-session-persistence", "--system-prompt", SYS, "--tools", "Bash,Read,Write,Edit",
               "--allowedTools", "Bash", "Read", "Write", "Edit", "--max-budget-usd", "1"]
        t0 = time.time(); p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=cwd)
    lines = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    res = next((l for l in reversed(lines) if l.get("type") == "result"), {})
    tools = [c for l in lines if l.get("type") == "assistant" for c in l["message"].get("content", []) if c.get("type") == "tool_use"]
    blob = json.dumps(tools)
    verstoss = [w for w in ("/home/user", "HackNation", "/root/", "uploads", "curl ", "wget ", "http://", "https://", "urllib", "requests.get") if w in blob]
    text = res.get("result", ""); import re
    m = re.search(r"\{[^{}]*\"antwort\"[^{}]*\}", text, re.S)
    try: ans = json.loads(m.group(0)) if m else {"antwort": "unbekannt", "zahl": None, "konfidenz": 0, "begruendung": "kein JSON"}
    except json.JSONDecodeError: ans = {"antwort": "unbekannt", "zahl": None, "konfidenz": 0, "begruendung": "JSON fehlerhaft"}
    return {"antwort": ans, "kosten_usd": res.get("total_cost_usd"), "tool_calls": len(tools), "verstoss": verstoss,
            "sek": round(time.time() - t0, 1), "transkript_tools": tools}


def bk(q, salt):
    from asd.discovery import solve_cascade
    return solve_cascade(B["kontext"], q["frage"], salt=salt)


def b(q, salt):
    from asd.discovery import solve
    return solve(B["kontext"], q["frage"], salt=salt)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cond", choices=["A1", "A2", "B", "BK"])
    ap.add_argument("--salts", default="0,1,2"); ap.add_argument("--fragen", default=""); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(); fn = {"A1": a1, "A2": a2, "B": b, "BK": bk}[a.cond]
    qs = [q for q in B["fragen"] if not a.fragen or q["id"] in a.fragen.split(",")]
    jobs = [(q, int(s)) for s in a.salts.split(",") for q in qs]; os.makedirs(f"{OUT}/{a.cond}", exist_ok=True)
    def job(qs_):
        q, s = qs_; path = f"{OUT}/{a.cond}/{q['id']}_s{s}.json"
        if os.path.exists(path): return path
        for attempt in range(2):
            r = fn(q, s)
            if not r.get("verstoss"): break
        r.update(frage=q["id"], salt=s, bedingung=a.cond); json.dump(r, open(path, "w"), ensure_ascii=False, indent=1, default=str)
        print(a.cond, q["id"], s, json.dumps(r["antwort"], ensure_ascii=False)[:160], flush=True); return path
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(job, jobs))
