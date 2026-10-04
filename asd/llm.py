"""LLM-Backend für alle Agenten. Reihenfolge: Cache -> claude CLI (headless, ohne Tools, leeres Arbeitsverzeichnis,
damit kein CLAUDE.md und keine Repo-Dateien sichtbar sind) -> Anthropic-API.

Jeder Aufruf wird mit Prompt, Antwort, Modell und Kosten unter cache/llm/<sha>.json abgelegt. Dadurch sind
Agenten-Läufe reproduzierbar (ASD_LLM=replay spielt nur aus dem Cache ab) und auditierbar.
"""
import hashlib, json, os, re, shutil, subprocess, tempfile, time

CACHE = os.environ.get("ASD_LLM_CACHE", "cache/llm")
MODEL = os.environ.get("ASD_MODEL", "sonnet")
COST_LOG = []


class LLMError(RuntimeError): pass


def _key(system, prompt, model, salt):
    return hashlib.sha256(json.dumps([system, prompt, model, salt], ensure_ascii=False).encode()).hexdigest()[:24]


def _cli(system, prompt, model, timeout):
    exe = shutil.which("claude")
    if not exe: raise LLMError("claude CLI nicht gefunden")
    with tempfile.TemporaryDirectory() as cwd:          # leeres Verzeichnis: kein Zugriff auf Daten oder CLAUDE.md
        cmd = [exe, "-p", prompt, "--output-format", "json", "--tools", "", "--model", model,
               "--no-session-persistence", "--system-prompt", system]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    if p.returncode != 0: raise LLMError(p.stderr[-500:] or p.stdout[-500:])
    d = json.loads(p.stdout)
    if d.get("is_error"): raise LLMError(str(d.get("result"))[:500])
    return d["result"], float(d.get("total_cost_usd") or 0), ",".join(d.get("modelUsage", {}).keys()) or model


def _api(system, prompt, model, timeout):
    import anthropic
    ids = {"sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5", "haiku": "claude-haiku-4-5-20251001"}
    m = anthropic.Anthropic().messages.create(model=ids.get(model, model), max_tokens=8000, system=system,
                                              messages=[{"role": "user", "content": prompt}], timeout=timeout)
    return "".join(b.text for b in m.content if b.type == "text"), 0.0, ids.get(model, model)


def ask(prompt, system="Du bist ein sorgfältiger Wissenschaftler.", model=None, salt="", timeout=600, retries=2):
    """salt unterscheidet bewusst unabhängige Stichproben desselben Prompts (z. B. Ensemble, Best-of-N)."""
    model = model or MODEL; os.makedirs(CACHE, exist_ok=True)
    k = _key(system, prompt, model, salt); path = f"{CACHE}/{k}.json"
    if os.path.exists(path): return json.load(open(path))["response"]
    if os.environ.get("ASD_LLM") == "replay": raise LLMError(f"nicht im Cache: {k}")
    backend = _api if os.environ.get("ASD_LLM") == "api" else _cli
    for attempt in range(retries + 1):
        try:
            t0 = time.time(); text, cost, used = backend(system, prompt, model, timeout); break
        except (LLMError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            if attempt == retries: raise LLMError(str(e))
            time.sleep(2 * (attempt + 1))
    COST_LOG.append(cost)
    json.dump({"key": k, "model": used, "salt": salt, "system": system, "prompt": prompt, "response": text,
               "cost_usd": cost, "sek": round(time.time() - t0, 1), "ts": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(path, "w"), ensure_ascii=False, indent=1)
    return text


def _parse_json(text):
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.S) or re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if not m: raise json.JSONDecodeError("keine JSON-Antwort", text[:100], 0)
    return json.loads(m.group(1))


def ask_json(prompt, system="Du bist ein sorgfältiger Wissenschaftler. Antworte nur mit gültigem JSON.", repairs=2, **kw):
    """Wie ask, aber mit JSON-Ergebnis. Fehlerhaftes JSON wird dem Modell zur Reparatur zurückgegeben (bis zu `repairs` Mal)."""
    text = ask(prompt, system, **kw); salt = kw.pop("salt", "")
    for j in range(repairs + 1):
        try: return _parse_json(text)
        except json.JSONDecodeError as e:
            if j == repairs: raise LLMError(f"ungültiges JSON nach {repairs} Reparaturen: {e}")
            text = ask(f"Dieser Text sollte gültiges JSON sein, ist es aber nicht ({e}). Gib exakt denselben Inhalt als gültiges JSON zurück, "
                       f"ohne weiteren Text:\n\n{text[:12000]}", system, salt=f"{salt}-repair{j}", **kw)
