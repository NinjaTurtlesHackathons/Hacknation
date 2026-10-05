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
    lines = md.split("\n"); erbt = {}                                    # Tabellenzeilen erben die Belege ihrer Überschrift ("Table: ... [C-...]")
    for k, z in enumerate(lines):
        if z.lstrip().startswith("|"):
            cap = []
            for r in (range(k - 1, -1, -1), range(k + 1, len(lines))):
                for j in r:
                    t = lines[j].strip()
                    if not t or t.startswith("|"): continue
                    if re.match(r"^(Table|Tabelle)\s*:", t): cap += re.findall(r"C-[\w\-*.]+", t)
                    break
            erbt[k] = cap
    k = 0                                                               # Sätze in ::: Blöcken erben die Belege des Blocks und des folgenden Beweis-/Zertifikatsabsatzes
    while k < len(lines):
        if re.match(r"^:::\s*\S", lines[k].strip()):
            e = k + 1
            while e < len(lines) and lines[e].strip() != ":::": e += 1
            nxt = next((lines[j] for j in range(e + 1, len(lines)) if lines[j].strip()), "")
            ids_b = re.findall(r"C-[\w\-*.]+", " ".join(lines[k:e])) + (re.findall(r"C-[\w\-*.]+", nxt) if re.match(r"^\*?(Proof|Certificate|Beweis|Zertifikat)", nxt.strip()) else [])
            for j in range(k, e): erbt.setdefault(j, []); erbt[j] = erbt[j] + ids_b
            k = e
        k += 1
    for k, z in enumerate(lines):                                       # reine Formelzeilen ($$...$$) erben die Belege des vorangehenden Absatzes
        if re.fullmatch(r"\s*\$\$.*\$\$\s*", z) and not re.search(r"C-[\w\-*.]+", z):
            prev = next((lines[j] for j in range(k - 1, -1, -1) if lines[j].strip() and not re.fullmatch(r"\s*\$\$.*\$\$\s*", lines[j])), "")
            erbt[k] = erbt.get(k, []) + re.findall(r"C-[\w\-*.]+", prev)
    blk = {j for j in erbt if not lines[j].lstrip().startswith("|")}
    for k, para in enumerate(lines):
        if not para.strip() or para.lstrip().startswith("#"): continue
        if re.match(r"^\s*\|[\s:|-]+\|\s*$", para): continue
        for s in ([para] if k in erbt and k not in blk else re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ\[])", para)):
            ids = [i for m in re.finditer(r"\[([^\]]+)\]", s) for i in re.findall(r"C-[\w\-*.]+", m.group(1))] + erbt.get(k, [])
            bad = [i for i in ids if i not in C]
            if bad: issues.append((s, f"unbekannte claim_id {bad}")); continue
            body = re.sub(r"\[[^\]]*\]", "", s); nums = _nums(body) - {0.0, 1.0, 2.0, 3.0, 4.0}   # Aufzählungen/Dimensionen/Indizes zulassen
            if nums and not ids: issues.append((s, "Zahl ohne Beleg")); continue
            allowed = set().union(*[_nums(C[i]["text"]) | _nums(C[i]["claim_id"]) for i in ids]) if ids else set()
            miss = [n for n in nums if not any(abs(abs(n) - abs(a)) <= 1e-9 * max(1, abs(a)) for a in allowed)]   # Betrag: Vorzeichen hängt an Schreibweise ('- 12' vs '-12')
            if miss: issues.append((s, f"Zahl(en) {miss} stehen in keiner zitierten Claim"))
    return issues


QUANT = re.compile(r"\b(for all|for every|for any|universal(ly)?|always|never|monoton\w*|in general|für alle|für jede[nsr]?|universell|immer|stets|nie|allgemein)\b", re.I)
PUNKTE = re.compile(r"(at the points examined|for the cases examined|an den untersuchten (Punkten|Fällen)|in den untersuchten Fällen)", re.I)
SCHWELLE = re.compile(r"\b(threshold|cut-?off|Schwelle|Schwellwert|Grenzwert von)\b", re.I)
BEGRUENDUNG = re.compile(r"\b(because|since|chosen|so that|as it|equal to|which is|corresponding to|weil|da |gewählt|entspricht|so dass|sodass)\b", re.I)


def scope_issues(md, claims):
    """Scope-Check: Quantoren/Verallgemeinerungen nur, wenn ein zitierter Claim eine Allaussage ist; sonst 'at the points examined'.
    Willkürliche Schwellen brauchen eine Begründung. Größen in Tabellenköpfen müssen direkt vor der Tabelle definiert sein."""
    C = {c["claim_id"]: c for c in claims}; issues = []
    lines = md.split("\n")
    for k, para in enumerate(lines):
        if not para.strip() or para.lstrip().startswith("#"): continue
        if para.lstrip().startswith("|") and k + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[k + 1] or ""):
            before = " ".join(lines[max(0, k - 4):k])
            for cell in [x.strip() for x in para.strip().strip("|").split("|")]:
                sym = re.findall(r"\$?([A-Za-z\\]+\([^)]*\))\$?", cell)
                for s_ in sym:
                    if s_ not in before: issues.append((para[:120], f"Tabellengröße {s_} ist nicht direkt vor der Tabelle definiert"))
            continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ\[$])", para):
            if s.lstrip().startswith("|"): continue
            ids = [i for i in re.findall(r"C-[\w\-*.]+", s) if i in C]
            if QUANT.search(re.sub(r"\[[^\]]*\]", "", s)) and ids and not PUNKTE.search(s):
                if not any(C[i].get("scope") == "alle" for i in ids) and not any(i.startswith(("C-lit", "C-modell")) for i in ids):
                    issues.append((s, "Quantor/Verallgemeinerung ohne Allaussage im zitierten Claim; sage „at the points examined (...)“ oder streiche den Quantor"))
            if SCHWELLE.search(s) and not BEGRUENDUNG.search(s) and not any(i.startswith("C-modell") for i in ids):
                issues.append((s, "Schwelle ohne Begründungs-Halbsatz"))
    return issues


SYS_EN = ("You write concise scientific prose in English in the style of a mathematical-physics preprint. You may ONLY use statements from the "
          "given claim list and must cite each statement with its claim_id in square brackets, e.g. [C-H1]. No number that does not appear "
          "verbatim in a cited claim. No literature citations except those inside the claims (cite them via their claim_id).")


def write(title, outline, claims, salt="", rounds=2, lang="de", extra_check=None):
    """extra_check(md) -> [(stelle, grund)]: zusätzliche Code-Regeln (z. B. keine Agentennamen im Haupttext), wie Zahlen-Verstöße behandelt."""
    SYS_USE = SYS_EN if lang == "en" else SYS
    full = lambda md: check(md, claims) + (extra_check(md) if extra_check else [])
    cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}" + (f", scope={c['scope']}" if c.get("scope") else "") +
                   (f", allowed environment={c['env']}" if c.get("env") else "") + (", APPENDIX ONLY" if c.get("anhang") else "") + f") {c['text']}" for c in claims)
    prompt = f"Titel: {title}\n\nGliederung und Hinweise:\n{outline}\n\nClaim-Liste (einzige erlaubte Quelle):\n{cl}\n\nSchreibe den Text in Markdown."
    md = ask(prompt, SYS_USE, salt=f"writer-{salt}-0"); log = []
    for r in range(rounds):
        issues = full(md); log.append({"runde": r, "verstoesse": len(issues)})
        if not issues: break
        fb = "\n".join(f"- „{s.strip()[:200]}“: {why}" for s, why in issues)
        md = ask(prompt + f"\n\nDein letzter Entwurf:\n{md}\n\nDer automatische Prüfer hat diese Verstöße gefunden:\n{fb}\n\n"
                 "Korrigiere ausschließlich diese Stellen (Beleg ergänzen oder Aussage streichen) und gib den vollständigen Text zurück.",
                 SYS_USE, salt=f"writer-{salt}-{r + 1}")
    issues = full(md); removed = []
    for s, why in issues:
        if s in md and len(s) > 20: md = md.replace(s, ""); removed.append({"satz": s, "grund": why})   # unbelegt -> entfernt (kein Platzhalter im Paper)
    log.append({"final_verstoesse_entfernt": len(removed)})
    return md, {"runden": log, "entfernt": removed}
