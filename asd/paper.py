"""Paper aus einem Projekt der Labor-Schleife: nur geprüfte Aussagen, jede Zahl belegt (Halluzinations-Gate).
  python -m asd.paper --domain proofreading --titel "..." --autoren "A, B, C" --affiliation "ETH Zürich"
Erzeugt projects/<domain>/paper.md, paper.tex (und paper.pdf, wenn pdflatex installiert ist)."""
import argparse, json, os, re, shutil, subprocess
from .writer import write, check, scope_issues
from .domains.base import get_domain

OUTLINE_EN = """Write a professional research article (arXiv level) in English. Structure, in this order, with these exact headings:
## Abstract
At most 180 words: the problem; why it is open (with a literature reference); the main result with its numbers; the method in half a sentence;
the most important limitation.
## Introduction
Context with citations of the literature claims; the open question; the contribution in 2-3 sentences; a bullet list of the results.
## Model and assumptions
All assumptions that carry the results and ALL fixed model parameters with their values (from the model claim); define notation exactly once.
## Method
The scientific method: which certificates are used (exact rational arithmetic, symbolic positivity proofs, interval arithmetic, independent
numerical re-computation), what the trusted base is, and what counts only as a numerical candidate. Only the LAST paragraph of this section may
mention that the work was carried out by an automated, verifier-gated laboratory, in one paragraph, without naming any of its agents or roles.
## Results
Follow the story plan: main results first, then supporting statements, then examples. Use the environments given in the story plan.
## Negative results
What was attempted and failed, with the reason for each failure.
## Discussion, limitations and open questions
## Declarations
AI usage (the results were produced and checked by an automated laboratory; every statement was verified by code), code and data availability
(use the repository/branch/command from the availability claim), competing interests (none).
## Appendix A: Agentic laboratory
Only here: the agents and roles, the workflow, preregistration, red-team statistics, computing costs.
## Appendix B: Provenance
One sentence: the provenance table mapping every statement to its evidence follows (it is generated automatically; do not write it yourself).
## Appendix C: Verifier self-test
What the verifier self-test checks and its result.

Formatting rules: mathematics as LaTeX in $...$ or $$...$$ (e.g. $e^{-2\\Delta}$, $\\eta \\geq e^{-3\\Delta}$), never Unicode math symbols and never
forms like "1 * e^-3Delta". Formal statements as fenced blocks:
::: theorem [short title]
statement
:::
(likewise ::: proposition, ::: lemma, ::: example, ::: observation, ::: remark). Cite literature only via its claim id [C-lit..]."""

OUTLINE_DE = OUTLINE_EN.replace("in English", "auf Deutsch")
OUTLINE, OUTLINE_EN_OLD = OUTLINE_DE, OUTLINE_EN
AGENT_NAMES = ["scout", "integrator", "red-team", "red team", "redteam", "lern-agent", "learning agent", "forscher-agent", "researcher agent",
               "lab loop", "lab_loop", "kaskade", "cascade", "storyteller", "explorer", "architect"]
COST_PAT = r"(\d[\d.,]*\s*(USD|US\$|\$|dollar))|((USD|\$)\s*\d)|(costs? of [\d.]+)|(Kosten von [\d.,]+)"


def main_text(md):
    """Text vor Appendix A (Haupttext)."""
    m = re.search(r"^#+\s*Appendix A", md, re.M | re.I)
    return md[:m.start()] if m else md


def rule_issues(md):
    """Code-Regeln für den Haupttext: keine Agentennamen, keine Kosten, keine internen Fehlertexte."""
    issues = []; main = main_text(md)
    for para in [p for p in main.split("\n") if p.strip()]:
        low = para.lower()
        for n in AGENT_NAMES:
            if re.search(r"(?<![a-z])" + re.escape(n) + r"(?![a-z])", low):
                issues.append((para[:200], f"Agentenname „{n}“ steht im Haupttext; nur in Appendix A erlaubt")); break
        if re.search(COST_PAT, para, re.I): issues.append((para[:200], "Kostenangabe im Haupttext; nur in Appendix A erlaubt"))
    for bad in ("TypeError", "NaN", "IndexError", "Traceback", "Exception"):
        if re.search(r"(?<![A-Za-z])" + bad + r"(?![A-Za-z])", md): issues.append((bad, f"interner Fehlertext „{bad}“ darf nicht im Paper stehen"))
    return issues


from .lab_loop import nicht_ausfuehrbar
RT_STAT = {}


def sanitize(t):
    """Interne Fehlertexte nie ins Paper."""
    t = str(t)
    for bad in ("TypeError", "IndexError", "KeyError", "ValueError", "Traceback", "Exception", "NaN", "nan comparison"):
        t = t.replace(bad, "")
    return re.sub(r"Prüfung nicht ausführbar:?", "", t).strip()


def scope_of(text, p=None):
    """'alle' = Allaussage (für alle Raten/Parameter/Mitglieder), sonst 'punkte' (endlich viele geprüfte Punkte)."""
    t = (text or "").lower()
    if any(k in t for k in ("für alle", "for all", "alle positiven", "all positive", "jedes mitglied", "every member")): return "alle"
    if p and str(p.get("typ", "")) in ("untere_schranke", "schranke_familie"): return "alle"
    return "punkte"


def env_name(c):
    """Benennung nach Relevanz UND Stufe: Theorem nur für hauptresultat + computed_rigorous/proved_lean."""
    rig = c["level"] in ("computed_rigorous", "proved_lean"); r = c.get("rolle") or c.get("relevanz")
    if c["level"] in ("statistical", "observed"): return "observation"
    if r == "hauptresultat" and rig: return "theorem"
    if r == "stuetze" and rig: return "proposition"
    if r == "beispiel": return "example"
    return "proposition" if rig else "observation"


ENV_RANK = {"theorem": 3, "proposition": 2, "lemma": 2, "example": 1, "observation": 1, "remark": 0}


def env_issues(md, C):
    """Jede ::: theorem/proposition/...-Umgebung braucht mindestens einen zitierten Claim, der diese Benennung erlaubt."""
    by = {c["claim_id"]: c for c in C}; issues = []
    for m in re.finditer(r"^:::\s*\{?\.?(\w+)[^\n]*\n(.*?)^:::\s*$", md, re.M | re.S):
        env, body = m.group(1).lower(), m.group(2)
        if env not in ENV_RANK: continue
        ids = [i for i in re.findall(r"C-[\w\-*.]+", body) if i in by]
        if not ids: issues.append((body[:150], f"Umgebung {env} ohne zitierten Claim")); continue
        if max(ENV_RANK[env_name(by[i])] for i in ids) < ENV_RANK[env]:
            issues.append((body[:150], f"„{env}“ zu stark: zitierte Claims erlauben nur {', '.join(sorted({env_name(by[i]) for i in ids}))}"))
    return issues


def modell_claim(D):
    par = D.parameter() if hasattr(D, "parameter") else {}
    if not par:
        print(f"WARNUNG: Domäne {D.name} definiert keine parameter(); feste Modellkonstanten dürfen dann nicht im Paper stehen.")
        return []
    txt = "; ".join(f"{k} = {v[0]} ({v[1]})" for k, v in par.items())
    return [{"claim_id": "C-modell", "text": f"Fixed model parameters and assumptions: {txt}.", "level": "computed_rigorous", "status": "bestätigt"}]


def claims_of(domain, lang="en"):
    RT_STAT.clear()
    s = json.load(open(f"projects/{domain}/state.json")); D = get_domain(domain); C = modell_claim(D)
    for c in s["claims"]:
        try: text = D.describe(c["pruefung"], lang=lang) if c.get("pruefung") else c["text"]   # nur was die Prüfung beweist
        except TypeError: text = D.describe(c["pruefung"])
        rel = c.get("relevanz") or (D.relevanz(c["pruefung"]) if c.get("pruefung") and hasattr(D, "relevanz") else "stuetze")
        C.append({"claim_id": f"C-{c['id']}", "text": f"Question studied: {c['frage']} Verified result: {text} Verifier: {sanitize(c['grund'])}",
                  "level": c["level"], "status": c["status"], "relevanz": rel, "scope": scope_of(text, c.get("pruefung"))})
        interp = c.get("interpretation_ungeprueft") or c["text"].split("->")[-1]
        C.append({"claim_id": f"C-{c['id']}-I", "text": f"Unverified interpretation of {c['id']} (never use as a result): {interp}",
                  "level": "hypothesis", "status": "offen", "anhang": True})
        for j, r in enumerate(c.get("red_team", [])):
            erg = r.get("ergebnis") or ("nicht_ausfuehrbar" if nicht_ausfuehrbar(r.get("grund", "")) and not r["bestanden"] else ("bestanden" if r["bestanden"] else "nicht_bestanden"))
            RT_STAT[erg] = RT_STAT.get(erg, 0) + 1
            if erg == "nicht_ausfuehrbar": continue                        # lief nie: nur als Anzahl in Appendix A
            res = ("passed and logically contradicts the statement (statement contested)" if r.get("widerspruch") else
                   "passed, but does not contradict the statement") if erg == "bestanden" else "did not pass"
            C.append({"claim_id": f"C-{c['id']}-RT{j + 1}", "text": f"Counter-check (adversarial test) of {c['id']}: {r['idee']} Result: {res}. Verifier: {sanitize(r.get('grund', ''))}",
                      "level": D.level(r["pruefung"]) if erg == "bestanden" else "observed", "status": "bestätigt", "anhang": True})
    for j, w in enumerate(s["widerlegt"]):
        if isinstance(w, str): txt = f"Negative result: {w}"
        else: txt = (f"Negative result for the question '{w['frage']}': no claim passed the verifier. Reasons per attempt: " +
                     "; ".join(f"{g['stufe']} ({g.get('pruefungstyp') or 'no check'}): {sanitize(g['grund'])}" for g in w["gruende"]))
        C.append({"claim_id": f"C-neg{j + 1}", "text": txt, "level": "observed", "status": "bestätigt"})
    for j, w in enumerate(s["wissen"][:30]):
        C.append({"claim_id": f"C-lit{j + 1}", "text": f"Literature: {w['text']} (verbatim quote: \"{w['zitat']}\", source {w['quelle']})", "level": "observed",
                  "status": "bestätigt", "quelle": w["quelle"]})
    fp = f"projects/{domain}/fakten.json"                               # per Code ermittelte Zusatzfakten (Zertifikats-Logs, Zählungen)
    if os.path.exists(fp):
        for f in json.load(open(fp)): C.append({"claim_id": f"C-{f['id']}", "text": f["text"], "level": f.get("level", "observed"), "status": "bestätigt"})
    C.append({"claim_id": "C-redteam", "text": f"Counter-checks (adversarial tests) in total: {sum(RT_STAT.values())}; passed: {RT_STAT.get('bestanden', 0)}, "
              f"did not pass: {RT_STAT.get('nicht_bestanden', 0)}, not executable: {RT_STAT.get('nicht_ausfuehrbar', 0)}.", "level": "observed", "status": "bestätigt", "anhang": True})
    C.append({"claim_id": "C-methode", "text": f"Das Labor lief {len(s['runden'])} Runden, {len(s['claims'])} geprüfte Aussagen, {len(s['widerlegt'])} negative Ergebnisse, "
              f"Kosten {s['kosten_usd']:.2f} USD; jede Runde vor dem Experiment präregistriert (prereg.md).", "level": "observed", "status": "bestätigt"})
    return C


def story_plan(C, D, lang="en", salt=""):
    """Story vor dem Schreiben: EINE Kernfrage, EINE Kernaussage, informativer Titel, Rolle jedes Claims."""
    from .llm import ask_json
    rel = [c for c in C if not c.get("anhang") and c["level"] != "hypothesis" and not c["claim_id"].startswith("C-lit")]
    liste = "\n".join(f"- [{c['claim_id']}] ({c['level']}, relevance={c.get('relevanz', '?')}) {c['text'][:400]}" for c in rel)
    r = ask_json(f"Research field: {D.kontext}\n\nVerified claims:\n{liste}\n\nPlan the article BEFORE it is written. Choose ONE core question and ONE core "
                 "statement (a single sentence) that the main results support. Assign every claim a role: hauptresultat (supports the core statement directly), "
                 "stuetze (needed for a main result), beispiel (illustration), anhang (only in the appendix), weglassen (unrelated to the core statement). "
                 "Propose an informative title that states the core result (no marketing words such as 'beyond', 'towards', 'novel', 'revisited'). "
                 'JSON: {"kernfrage": "...", "kernaussage": "...", "titel": "...", "zuordnung": {"C-...": "hauptresultat|stuetze|beispiel|anhang|weglassen"}}',
                 "You are a senior scientific editor. Answer with valid JSON only.", salt=f"story-{salt}")
    r.setdefault("zuordnung", {})
    for c in rel: r["zuordnung"].setdefault(c["claim_id"], c.get("relevanz") or "anhang")
    return r


def apply_story(C, plan):
    out = []
    for c in C:
        role = plan["zuordnung"].get(c["claim_id"])
        if role == "weglassen": continue
        if role == "anhang": c = dict(c, anhang=True)
        if role in ("hauptresultat", "stuetze", "beispiel"): c = dict(c, rolle=role)
        out.append(c)
    return out


UNI = {"η": r"\eta", "Δ": r"\Delta", "σ": r"\sigma", "μ": r"\mu", "≥": r"\geq", "≤": r"\leq", "×": r"\times", "→": r"\to",
       "≈": r"\approx", "−": "-", "·": r"\cdot", "∈": r"\in", "…": r"\ldots", "²": r"^{2}", "³": r"^{3}", "√": r"\surd", "±": r"\pm",
       "⁻": r"^{-}", "¹": r"^{1}", "₀": r"_{0}", "₁": r"_{1}", "₂": r"_{2}", "α": r"\alpha", "β": r"\beta", "γ": r"\gamma",
       "ε": r"\varepsilon", "τ": r"\tau", "ν": r"\nu", "∞": r"\infty", "≠": r"\neq", "π": r"\pi", "λ": r"\lambda", "ρ": r"\rho", "θ": r"\theta"}
ENVS = ["theorem", "proposition", "lemma", "example", "observation", "remark", "corollary", "definition"]


def bib_entries(C, d):
    """BibTeX aus den zitierten Literatur-Claims: Metadaten über Crossref (DOI) bzw. arXiv-API; nie erfinden, sonst [unverified]."""
    from .research import crossref_doi, arxiv_meta
    cache_p = f"{d}/bibcache.json"; cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    keys, bib = {}, []
    for c in C:
        q = c.get("quelle")
        if not q or q in keys: continue
        if q not in cache:
            try:
                m = crossref_doi(q[4:]) if q.startswith("doi:") else arxiv_meta(q) if q.lower().startswith("arxiv:") else None
                cache[q] = {k: m.get(k, "") for k in ("titel", "autoren", "jahr", "journal", "volume", "seiten")} if m else None
            except Exception:
                cache[q] = None
        m = cache[q]; key = re.sub(r"[^A-Za-z0-9]", "", q.split(":", 1)[-1])[-24:] or f"ref{len(keys)}"
        if m and m.get("autoren"):
            first = m["autoren"].split(",")[0].split()[-1] if m["autoren"] else "anon"; key = re.sub(r"[^A-Za-z]", "", first)[:12] + str(m.get("jahr", "")) + key[-4:]
        keys[q] = key
        esc = lambda t: str(t).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")
        if m and m.get("titel"):
            auth = " and ".join(a.strip() for a in m["autoren"].split(",") if a.strip()) or "Anonymous"
            fields = [f"author = {{{esc(auth)}}}", f"title = {{{{{esc(m['titel'])}}}}}", f"year = {{{m.get('jahr', '')}}}"]
            if m.get("journal"): fields.append(f"journal = {{{esc(m['journal'])}}}")
            if m.get("volume"): fields.append(f"volume = {{{m['volume']}}}")
            if m.get("seiten"): fields.append(f"pages = {{{esc(m['seiten'])}}}")
            if q.startswith("doi:"): fields.append(f"doi = {{{q[4:]}}}")
            bib.append(f"@article{{{key},\n  " + ",\n  ".join(fields) + "\n}")
        else:
            bib.append(f"@misc{{{key},\n  title = {{[unverified] {esc(q)}}},\n  note = {{metadata could not be resolved}}\n}}")
    json.dump(cache, open(cache_p, "w"), ensure_ascii=False, indent=1)
    open(f"{d}/references.bib", "w").write("\n\n".join(bib) + "\n")
    return keys


def provenance(md, C):
    """Zuordnung Aussage -> claim_ids (aus der Version MIT IDs), gruppiert pro Theorem/Proposition/... und Abschnitt."""
    by = {c["claim_id"]: c for c in C}; rows = []; sec = ""; counters = {}
    blocks = re.split(r"(^:::[^\n]*\n.*?^:::\s*$)", md, flags=re.M | re.S)
    for b in blocks:
        m = re.match(r"^:::\s*\{?\.?(\w+)\]?\s*(?:\[([^\]]*)\])?", b)
        if m and m.group(1).lower() in ENVS:
            env = m.group(1).lower(); counters[env] = counters.get(env, 0) + 1
            ids = sorted({i for i in re.findall(r"C-[\w\-*.]+", b) if i in by})
            rows.append((f"{env.capitalize()} {counters[env]}" + (f" ({m.group(2)})" if m.group(2) else ""), ids))
            continue
        for line in b.split("\n"):
            h = re.match(r"^#+\s*(.*)", line)
            if h: sec = h.group(1).strip(); continue
            ids = sorted({i for i in re.findall(r"C-[\w\-*.]+", line) if i in by and not i.startswith("C-lit")})
            if ids and sec and not sec.lower().startswith(("appendix b", "abstract")): rows.append((f"Section „{sec}“", ids))
    merged = {}
    for k, ids in rows: merged.setdefault(k, set()).update(ids)
    return [(k, sorted(v), sorted({by[i]["level"] for i in v})) for k, v in merged.items()]


def md_to_latex_body(md, keys, C, lang):
    """Markdown (mit IDs) -> LaTeX-Rumpf: Umgebungen, Zitate (\cite), IDs entfernt, Mathematik und Tabellen über pandoc."""
    import pypandoc
    by = {c["claim_id"]: c for c in C}
    body = md.replace("–", "--").replace("—", "---").replace("’", "'").replace("“", "``").replace("”", "''").replace("„", ",,")
    def outside_math(t, fn):
        parts = re.split(r"(\$\$.*?\$\$|\$[^$\n]+\$)", t, flags=re.S)
        return "".join(p if i % 2 else fn(p) for i, p in enumerate(parts))
    body = outside_math(body, lambda t: re.sub(r"(?<![\w])e\^\{([^}]*)\}", lambda m: "$e^{" + "".join(UNI.get(c, c) for c in m.group(1)) + "}$", t))
    body = outside_math(body, lambda t: re.sub(r"(?<![\w{])e\^(-?\d*)\s*(Δ|\\Delta|Delta)", lambda m: "$e^{" + m.group(1) + "\\Delta}$", t))
    def cite(m):
        ids = re.findall(r"C-[\w\-*.]+", m.group(0)); ks = sorted({keys[by[i]["quelle"]] for i in ids if i in by and by[i].get("quelle") in keys})
        return (" \\cite{" + ",".join(ks) + "}") if ks else ""
    body = re.sub(r"\s*\[(?:C-[\w\-*.]+(?:\s*[,;]\s*)?)+\]", cite, body)               # Claim-IDs raus, Literatur als \cite
    conv0 = lambda t: pypandoc.convert_text(t, "latex", format="markdown+raw_tex+tex_math_dollars", extra_args=["--wrap=preserve"]).strip()
    out, buf, env, title = [], None, None, None
    for line in body.split("\n"):
        m = re.match(r"^:::\s*\{?\.?(\w+)\}?\s*(?:\[([^\]]*)\])?\s*(.*)$", line)
        if buf is None and m and m.group(1).lower() in ENVS:
            env, title, buf = m.group(1).lower(), (m.group(2) or (m.group(3).strip() or None)), []; continue
        if buf is not None and line.strip() == ":::":
            inner = conv0("\n".join(buf)) if any(x.strip() for x in buf) else ""
            out += ["", f"\\begin{{{env}}}" + (f"[{title}]" if title else "") + "\n" + inner + f"\n\\end{{{env}}}", ""]; buf = None; continue
        if buf is not None: buf.append(line); continue
        if line.strip() == ":::": continue
        out.append(line)
    if buf is not None:
        out += ["", f"\\begin{{{env}}}\n" + conv0("\n".join(buf)) + f"\n\\end{{{env}}}", ""]
    body = "\n".join(out)
    body = re.sub(r"^(#+)\s*(?:\d+(?:\.\d+)*\.?\s+)", r"\1 ", body, flags=re.M)        # manuelle Nummern raus (LaTeX nummeriert)
    abstract = ""
    m = re.search(r"^##\s*(Abstract|Zusammenfassung)\s*\n(.*?)(?=^##\s)", body, re.M | re.S)
    if m: abstract = m.group(2).strip(); body = body[:m.start()] + body[m.end():]
    body = re.sub(r"^##\s*(Appendix|Anhang)\s*A\s*[:.]?\s*", "\\\\appendix\n\n## ", body, count=1, flags=re.M)
    body = re.sub(r"^##\s*(Appendix|Anhang)\s*[B-Z]\s*[:.]?\s*", "## ", body, flags=re.M)
    conv = lambda t: pypandoc.convert_text(t, "latex", format="markdown+raw_tex+tex_math_dollars+pipe_tables", extra_args=["--wrap=preserve", "--shift-heading-level-by=-1"])
    tex = conv(body); abs_tex = conv(abstract) if abstract else ""
    return tex, abs_tex


TEMPLATE = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{microtype}
\usepackage[%(babel)s]{babel}\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{amsmath,amssymb,amsthm}\usepackage{graphicx}\usepackage{booktabs,longtable,array,calc}
\usepackage[hidelinks]{hyperref}\usepackage[capitalise,noabbrev]{cleveref}\usepackage{newunicodechar}
%(unicode)s
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newtheorem{theorem}{Theorem}\newtheorem{proposition}[theorem]{Proposition}\newtheorem{lemma}[theorem]{Lemma}\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}\newtheorem{definition}[theorem]{Definition}\newtheorem{example}[theorem]{Example}
\newtheorem{observation}[theorem]{%(obs)s}\theoremstyle{remark}\newtheorem{remark}[theorem]{Remark}
\title{%(title)s}
\author{%(authors)s\\[2pt] \small %(aff)s}
\date{%(date)s}
\begin{document}
\maketitle
\begin{abstract}
%(abstract)s
\par\medskip\noindent\textbf{%(kwlabel)s:} %(keywords)s
\end{abstract}
%(body)s
%(figures)s
\bibliographystyle{unsrt}
\bibliography{references}
\end{document}
"""


def build_latex(md, title, authors, aff, C, d, lang, figs, keywords):
    import shutil
    keys = bib_entries(C, d); prov = provenance(md, C)
    tbl = ["", "| Statement | Evidence (claim ids) | Level |", "|---|---|---|"]
    tbl += [f"| {k} | {', '.join(i.replace('_', '-') for i in ids)} | {', '.join(lv)} |" for k, ids, lv in prov]
    md2 = md
    mb = re.search(r"^##\s*(Appendix|Anhang)\s*B[^\n]*\n", md2, re.M)
    if mb:
        nxt = re.search(r"^##\s", md2[mb.end():], re.M); ins = mb.end() + (nxt.start() if nxt else len(md2) - mb.end())
        md2 = md2[:ins] + "\n" + "\n".join(tbl) + ("\n\nThe complete automatic checking protocol of the writing process is stored as pruefprotokoll.json in the "
                                                  "project directory of the repository.\n" if lang == "en" else
                                                  "\n\nDas vollständige automatische Prüfprotokoll des Schreibprozesses liegt als pruefprotokoll.json im Projektverzeichnis.\n") + "\n" + md2[ins:]
    body, abstract = md_to_latex_body(md2, keys, C, lang)
    fig_tex = "".join(f"\\begin{{figure}}[t]\\centering\\includegraphics[width=0.75\\textwidth]{{{fn}}}\\caption{{{cap}}}\\end{{figure}}\n" for fn, cap, *_ in figs)
    uni = "".join(f"\\newunicodechar{{{k}}}{{\\ensuremath{{{v}}}}}\n" for k, v in UNI.items())
    esc = lambda t: t.replace("&", r"\&").replace("%", r"\%")
    tex = TEMPLATE % {"babel": "english" if lang == "en" else "ngerman", "unicode": uni, "title": esc(title),
                      "authors": r" \and ".join(a.strip() for a in authors.split(",")), "aff": esc(aff), "date": r"Preprint, \today",
                      "abstract": abstract, "kwlabel": "Keywords" if lang == "en" else "Schlüsselwörter", "keywords": esc(keywords),
                      "body": body, "figures": fig_tex, "obs": "Numerical observation" if lang == "en" else "Numerische Beobachtung"}
    open(f"{d}/paper.tex", "w").write(tex)
    for cmd in (["pdflatex", "-interaction=nonstopmode", "paper.tex"], ["bibtex", "paper"], ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
                ["pdflatex", "-interaction=nonstopmode", "paper.tex"]):
        if shutil.which(cmd[0]): subprocess.run(cmd, cwd=d, capture_output=True, timeout=300)
    return prov


def _env_statements(md):
    return sorted(re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", "", m.group(2))).strip()
                  for m in re.finditer(r"^:::\s*\{?\.?(\w+)[^\n]*\n(.*?)^:::\s*$", md, re.M | re.S) if m.group(1).lower() in ENVS)


def _numbers(md):
    from .writer import _nums
    return sorted(_nums(re.sub(r"\[[^\]]*\]", "", re.sub(r"C-[\w\-*.]+", "", md))))


def editor_pass(md, C, gate, lang, salt):
    """Lektorat: Sprache, Fluss, Übergänge. Harte Regel per Code: Zahlen, Theorem-Aussagen und zitierte IDs bleiben gleich, Gate bleibt bei 0."""
    from .llm import ask
    sys_ = ("You are a professional copy editor for physics/mathematics journals. Improve language, flow, transitions and academic style. "
            "Do NOT change, add or remove any number, any formula, any formal statement inside ::: blocks, or any citation [C-...]. Return the full text.")
    new = ask(f"Edit this article in {'English' if lang == 'en' else 'German'}:\n\n{md}", sys_, salt=f"editor-{salt}")
    ok = (_numbers(new) == _numbers(md) and _env_statements(new) == _env_statements(md)
          and sorted(set(re.findall(r"C-[\w\-*.]+", new))) == sorted(set(re.findall(r"C-[\w\-*.]+", md))) and not (check(new, C) + gate(new)))
    return (new if ok else md), {"lektorat_uebernommen": ok}


def referee_pass(pdf_text, md, C, gate, title, outline, lang, salt, d):
    """Gutachter sieht nur den PDF-Text: 5 größte Schwächen. Behebbares wird mit den vorhandenen Claims behoben, Rest -> referee_report.md."""
    from .llm import ask_json, ask
    r = ask_json(f"Article (plain text of the PDF):\n\n{pdf_text[:60000]}\n\nAct as a demanding referee for a physics/mathematics journal. List the 5 most "
                 "serious weaknesses. For each say whether it can be fixed by rewriting with the evidence already present in the paper (fixable_by_rewriting).\n"
                 'JSON: {"weaknesses": [{"title": "...", "detail": "...", "fixable_by_rewriting": true|false, "suggestion": "..."}]}',
                 "You are an expert referee. Answer with valid JSON only.", salt=f"referee-{salt}")
    W = r.get("weaknesses", [])[:5]; fix = [w for w in W if w.get("fixable_by_rewriting")]; new = md; applied = False
    if fix:
        cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}" + (f", allowed environment={c['env']}" if c.get("env") else "") + f") {c['text']}" for c in C)
        fb = "\n".join(f"- {w['title']}: {w['detail']} Suggestion: {w.get('suggestion', '')}" for w in fix)
        cand = ask(f"Title: {title}\n\nOutline:\n{outline}\n\nClaim list (only allowed source):\n{cl}\n\nCurrent article:\n{md}\n\nA referee raised these points:\n{fb}\n\n"
                   "Revise the article to address them using ONLY the claims above (keep all citations [C-...]). Return the full article in Markdown.",
                   "You revise scientific articles. Every statement must cite its claim id; no number that is not in a cited claim.", salt=f"referee-fix-{salt}")
        if not (check(cand, C) + gate(cand)): new, applied = cand, True
    L = [f"# Referee report ({'en' if lang == 'en' else 'de'})", "", f"Fixable points addressed in a revision: {'yes' if applied else 'no (revision failed the checks or nothing fixable)'}", ""]
    for j, w in enumerate(W, 1):
        L += [f"## {j}. {w.get('title')}", "", w.get("detail", ""), "", f"- Fixable by rewriting: {w.get('fixable_by_rewriting')}",
              f"- Suggestion: {w.get('suggestion', '')}", f"- Status: {'addressed in revision' if applied and w.get('fixable_by_rewriting') else 'open'}", ""]
    open(f"{d}/referee_report.md", "w").write("\n".join(L))
    return new, {"referee_schwaechen": len(W), "behoben_versucht": len(fix), "revision_uebernommen": applied}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--domain", required=True); ap.add_argument("--titel", default="", help="leer = informativer Titel aus der Kernaussage")
    ap.add_argument("--autoren", required=True); ap.add_argument("--affiliation", default=""); ap.add_argument("--sprache", default="en", choices=["de", "en"])
    ap.add_argument("--keywords", default=""); ap.add_argument("--hinweise", default="", help="zusätzliche Gliederungshinweise (Datei oder Text)")
    ap.add_argument("--repo", default="https://github.com/alizema700/Daddys-Project"); a = ap.parse_args()
    D = get_domain(a.domain); d = f"projects/{a.domain}"; C = claims_of(a.domain, a.sprache)
    import subprocess as sp
    branch = sp.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
    C.append({"claim_id": "C-verfuegbarkeit", "text": f"Code and data: repository {a.repo}, branch {branch}, directory {d}; reproduce all certificates with "
              f"'python -m asd.recheck {a.domain}' and rebuild the paper with 'python -m asd.paper --domain {a.domain}'.", "level": "observed", "status": "bestätigt"})
    for c in C: c.setdefault("relevanz", None)
    plan = story_plan(C, D, a.sprache, salt=a.domain); C = apply_story(C, plan); a.titel = a.titel or plan.get("titel", a.domain)
    rollen = "\n".join(f"- {cid}: {rolle}" for cid, rolle in plan["zuordnung"].items() if rolle != "weglassen")
    story = (f"STORY PLAN (binding): core question: {plan.get('kernfrage')}\ncore statement: {plan.get('kernaussage')}\nclaim roles:\n{rollen}\n"
             "Main results (hauptresultat) come first in Results; stuetze become propositions/lemmas, beispiel become examples; claims marked APPENDIX ONLY "
             "appear only in the appendices; claims not listed must not be used. Use for each formal statement exactly the allowed environment of its claim.")
    extra = open(a.hinweise).read() if a.hinweise and os.path.exists(a.hinweise) else a.hinweise
    outline = (OUTLINE_EN if a.sprache == "en" else OUTLINE_DE) + "\n\n" + story + ("\n\n" + extra if extra else "")
    for c in C: c["env"] = env_name(c) if c["claim_id"].startswith("C-" + a.domain) and not c["claim_id"].endswith("-I") and "-RT" not in c["claim_id"] else None
    gate = lambda m: rule_issues(m) + env_issues(m, C) + scope_issues(m, C)
    md, log = write(a.titel, f"Research field: {D.kontext}\n\n{outline}", C, salt=f"paper2-{a.domain}-{a.sprache}", lang=a.sprache, extra_check=gate)
    md, ed_log = editor_pass(md, C, gate, a.sprache, salt=a.domain); log["lektorat"] = ed_log
    figs = []
    try: figs = D.figures(json.load(open(f"{d}/state.json")), d, lang=a.sprache)
    except TypeError: figs = [(f[0], f[1], []) for f in D.figures(json.load(open(f"{d}/state.json")), d)]
    for fn, cap, ids in figs:
        md += f"\n<!-- Abbildung {fn}: Belege {', '.join(ids)} -->\n"
    open(f"{d}/paper.md", "w").write(f"# {a.titel}\n\n{a.autoren}, {a.affiliation}\n\n{md}\n")
    json.dump({"claims": C, "story": plan}, open(f"{d}/paper_belege.json", "w"), ensure_ascii=False, indent=1)
    kw = a.keywords or plan.get("kernfrage", "")[:120]
    prov = build_latex(md, a.titel, a.autoren, a.affiliation, C, d, a.sprache, figs, kw)
    pdf_text = sp.run(["pdftotext", f"{d}/paper.pdf", "-"], capture_output=True, text=True).stdout if os.path.exists(f"{d}/paper.pdf") else md
    md, ref_log = referee_pass(pdf_text, md, C, gate, a.titel, outline, a.sprache, a.domain, d); log["referee"] = ref_log
    if ref_log["revision_uebernommen"]:
        open(f"{d}/paper.md", "w").write(f"# {a.titel}\n\n{a.autoren}, {a.affiliation}\n\n{md}\n")
        prov = build_latex(md, a.titel, a.autoren, a.affiliation, C, d, a.sprache, figs, kw)
    rest = check(md, C) + gate(md)
    proto = {"claims_zitiert": len(set(re.findall(r"C-[\w\-*.]+", md))), "korrekturrunden": log["runden"], "entfernt": log["entfernt"],
             "lektorat": log.get("lektorat"), "referee": log.get("referee"),
             "verbleibende_verstoesse": [list(x) for x in rest], "story": plan, "provenance_zeilen": len(prov)}
    json.dump(proto, open(f"{d}/pruefprotokoll.json", "w"), ensure_ascii=False, indent=1)
    print(f"{d}/paper.pdf" if os.path.exists(f"{d}/paper.pdf") else "PDF fehlt", "| verbleibende Verstöße:", len(rest), "| Titel:", a.titel)
    return md, C, a, D, d, figs


if __name__ == "__main__":
    main()
