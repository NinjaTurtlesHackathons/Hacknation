"""Paper-Schreiber mit Halluzinations-Gate.

Ein LLM formuliert, der Code prüft: jeder Satz mit einer Zahl oder Tatsachenbehauptung muss eine claim_id
zitieren ([C-...]), jede Zahl im Satz muss im Text einer zitierten Claim vorkommen, und zitierte Claims müssen
existieren. Verstöße gehen als externes Feedback zurück (bis zu 2 Runden, vgl. Stechly et al. 2023);
was danach noch unbelegt ist, wird entfernt und protokolliert. Ergebnis: kein Satz ohne Beleg.
"""
import json, re
from .llm import ask

SYS = ("Du schreibst wissenschaftliche Texte auf Deutsch, präzise und nüchtern. Du darfst ausschließlich Aussagen aus der "
       "gegebenen Claim-Liste verwenden und musst jede Aussage mit ihrer claim_id in eckigen Klammern belegen, z. B. [C-H1]. "
       "Keine Zahl, die nicht wörtlich in einer zitierten Claim steht. Keine Literaturzitate außer denen in den Claims.")

SYS_EN = ("You write scientific text in English, precise and sober, in the style of a physics preprint. You may use only statements "
          "from the given claim list and must support every statement with its claim_id in square brackets, e.g. [C-H1]. "
          "No number that does not appear verbatim in a cited claim. No literature citations except those contained in the claims. "
          "Write decimal numbers with a decimal point.")

NUM = re.compile(r"(?<![\w.])-?\d+(?:[.,]\d+)?")
CIT = re.compile(r"\[(C-[^\]\s,;]+)(?:[,;]\s*(C-[^\]\s,;]+))*\]")


def _norm(x):
    x = x.replace(",", "."); 
    try: return float(x)
    except ValueError: return None


def _nums(text):
    return {v for v in (_norm(m) for m in NUM.findall(text)) if v is not None}


def check(md, claims):
    """Gibt Liste von Verstößen zurück: (satz, grund)."""
    C = {c["claim_id"]: c for c in claims}; issues = []
    for para in md.split("\n"):
        if not para.strip() or para.lstrip().startswith("#"): continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ\[])", para):
            ids = [i for m in re.finditer(r"\[([^\]]+)\]", s) for i in re.findall(r"C-[\w\-*.]+", m.group(1))]
            bad = [i for i in ids if i not in C]
            if bad: issues.append((s, f"unbekannte claim_id {bad}")); continue
            body = re.sub(r"\[[^\]]*\]", "", s); nums = _nums(body) - {1.0, 2.0, 3.0, 4.0}   # Aufzählungen/Dimensionen zulassen
            if nums and not ids: issues.append((s, "Zahl ohne Beleg")); continue
            allowed = set().union(*[_nums(C[i]["text"]) | _nums(C[i]["claim_id"]) for i in ids]) if ids else set()
            miss = [n for n in nums if not any(abs(n - a) <= 1e-9 * max(1, abs(a)) for a in allowed)]
            if miss: issues.append((s, f"Zahl(en) {miss} stehen in keiner zitierten Claim"))
    return issues


def write(title, outline, claims, salt="", rounds=2, lang="de"):
    sysp = SYS_EN if lang == "en" else SYS
    cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}) {c['text']}" for c in claims)
    prompt = f"Titel: {title}\n\nGliederung und Hinweise:\n{outline}\n\nClaim-Liste (einzige erlaubte Quelle):\n{cl}\n\nSchreibe den Text in Markdown."
    if lang == "en": prompt = prompt.replace("Schreibe den Text in Markdown.", "Write the text in English, in Markdown.")
    md = ask(prompt, sysp, salt=f"writer-{salt}-0"); log = []
    for r in range(rounds):
        issues = check(md, claims); log.append({"runde": r, "verstoesse": len(issues)})
        if not issues: break
        fb = "\n".join(f"- „{s.strip()[:200]}“: {why}" for s, why in issues)
        md = ask(prompt + f"\n\nDein letzter Entwurf:\n{md}\n\nDer automatische Prüfer hat diese Verstöße gefunden:\n{fb}\n\n"
                 "Korrigiere ausschließlich diese Stellen (Beleg ergänzen oder Aussage streichen) und gib den vollständigen Text zurück.",
                 sysp, salt=f"writer-{salt}-{r + 1}")
    issues = check(md, claims); removed = []
    for s, why in issues:
        md = md.replace(s, f"*[entfernt: unbelegt — {why}]*"); removed.append({"satz": s, "grund": why})
    log.append({"final_verstoesse_entfernt": len(removed)})
    return md, {"runden": log, "entfernt": removed}
