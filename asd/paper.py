"""Paper aus einem Projekt der Labor-Schleife: nur geprüfte Aussagen, jede Zahl belegt (Halluzinations-Gate).
  python -m asd.paper --domain proofreading --titel "..." --autoren "A, B, C" --affiliation "ETH Zürich"
Erzeugt projects/<domain>/paper.md, paper.tex (und paper.pdf, wenn pdflatex installiert ist)."""
import argparse, json, os, re, shutil, subprocess
from .writer import write, check
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


def modell_claim(D):
    par = D.parameter() if hasattr(D, "parameter") else {}
    if not par:
        print(f"WARNUNG: Domäne {D.name} definiert keine parameter(); feste Modellkonstanten dürfen dann nicht im Paper stehen.")
        return []
    txt = "; ".join(f"{k} = {v[0]} ({v[1]})" for k, v in par.items())
    return [{"claim_id": "C-modell", "text": f"Fixed model parameters and assumptions: {txt}.", "level": "computed_rigorous", "status": "bestätigt"}]


def claims_of(domain):
    RT_STAT.clear()
    s = json.load(open(f"projects/{domain}/state.json")); D = get_domain(domain); C = modell_claim(D)
    for c in s["claims"]:
        text = D.describe(c["pruefung"]) if c.get("pruefung") else c["text"]          # nur was die Prüfung beweist
        C.append({"claim_id": f"C-{c['id']}", "text": f"Untersuchte Frage: {c['frage']} Geprüftes Resultat: {text} Prüfer: {sanitize(c['grund'])}",
                  "level": c["level"], "status": c["status"]})
        interp = c.get("interpretation_ungeprueft") or c["text"].split("->")[-1]
        C.append({"claim_id": f"C-{c['id']}-I", "text": f"Ungeprüfte Interpretation des Agenten zu {c['id']} (nicht als Resultat verwenden): {interp}",
                  "level": "hypothesis", "status": "offen"})
        for j, r in enumerate(c.get("red_team", [])):
            erg = r.get("ergebnis") or ("nicht_ausfuehrbar" if nicht_ausfuehrbar(r.get("grund", "")) and not r["bestanden"] else ("bestanden" if r["bestanden"] else "nicht_bestanden"))
            RT_STAT[erg] = RT_STAT.get(erg, 0) + 1
            if erg == "nicht_ausfuehrbar": continue                        # lief nie: nur als Anzahl in Appendix A
            res = ("passed and logically contradicts the statement (statement contested)" if r.get("widerspruch") else
                   "passed, but does not contradict the statement") if erg == "bestanden" else "did not pass"
            C.append({"claim_id": f"C-{c['id']}-RT{j + 1}", "text": f"Counter-check (adversarial test) of {c['id']}: {r['idee']} Result: {res}. Verifier: {sanitize(r.get('grund', ''))}",
                      "level": D.level(r["pruefung"]) if erg == "bestanden" else "observed", "status": "bestätigt", "anhang": True})
    for j, w in enumerate(s["widerlegt"]): C.append({"claim_id": f"C-neg{j + 1}", "text": f"Negatives Ergebnis: {w}", "level": "observed", "status": "bestätigt"})
    for j, w in enumerate(s["wissen"][:30]):
        C.append({"claim_id": f"C-lit{j + 1}", "text": f"Literatur: {w['text']} (Zitat: „{w['zitat']}“, {w['quelle']})", "level": "observed", "status": "bestätigt"})
    fp = f"projects/{domain}/fakten.json"                               # per Code ermittelte Zusatzfakten (Zertifikats-Logs, Zählungen)
    if os.path.exists(fp):
        for f in json.load(open(fp)): C.append({"claim_id": f"C-{f['id']}", "text": f["text"], "level": f.get("level", "observed"), "status": "bestätigt"})
    C.append({"claim_id": "C-redteam", "text": f"Counter-checks (adversarial tests) in total: {sum(RT_STAT.values())}; passed: {RT_STAT.get('bestanden', 0)}, "
              f"did not pass: {RT_STAT.get('nicht_bestanden', 0)}, not executable: {RT_STAT.get('nicht_ausfuehrbar', 0)}.", "level": "observed", "status": "bestätigt", "anhang": True})
    C.append({"claim_id": "C-methode", "text": f"Das Labor lief {len(s['runden'])} Runden, {len(s['claims'])} geprüfte Aussagen, {len(s['widerlegt'])} negative Ergebnisse, "
              f"Kosten {s['kosten_usd']:.2f} USD; jede Runde vor dem Experiment präregistriert (prereg.md).", "level": "observed", "status": "bestätigt"})
    return C


def to_tex(md, titel, autoren, aff, figs=(), lang="de"):
    body = md
    body = re.sub(r"^### (.*)$", r"\\subsubsection*{\1}", body, flags=re.M)
    body = re.sub(r"^## (.*)$", r"\\section{\1}", body, flags=re.M)
    body = re.sub(r"^# (.*)$", r"", body, flags=re.M)
    body = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", body); body = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"\\emph{\1}", body)
    body = re.sub(r"\[(C-[^\]]+)\]", lambda m: r"{\scriptsize[" + m.group(1).replace("_", r"\_") + "]}", body)
    lines, out, inlist = body.split("\n"), [], False
    for l in lines:
        if re.match(r"^\s*[-*] ", l):
            if not inlist: out.append(r"\begin{itemize}"); inlist = True
            out.append(r"\item " + re.sub(r"^\s*[-*] ", "", l))
        else:
            if inlist: out.append(r"\end{itemize}"); inlist = False
            out.append(l)
    if inlist: out.append(r"\end{itemize}")
    body = "\n".join(out).replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")
    for fn, cap in figs:
        cap_t = re.sub(r"\[(C-[^\]]+)\]", lambda m: r"[" + m.group(1).replace("_", r"\_") + "]", cap).replace("%", r"\%")
        body += "\n\\begin{figure}[t]\\centering\\includegraphics[width=\\columnwidth]{" + fn + "}\\caption{" + cap_t + "}\\end{figure}\n"
    return (r"""\documentclass[10pt,twocolumn]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage[""" + ("english" if lang == "en" else "ngerman") + r"""]{babel}\usepackage{amsmath,amssymb}\usepackage[margin=1.8cm]{geometry}
\usepackage{times}\usepackage{graphicx}\usepackage{hyperref}
\title{\textbf{""" + titel + r"""}}
\author{""" + r" \and ".join(a.strip() for a in autoren.split(",")) + r"""\\ \small """ + aff + r"""}
\date{Preprint, \today}
\begin{document}\maketitle
""" + body + "\n\\end{document}\n")


UNI = {"η": r"\eta", "Δ": r"\Delta", "σ": r"\sigma", "μ": r"\mu", "≥": r"\geq", "≤": r"\leq", "×": r"\times", "→": r"\to",
       "≈": r"\approx", "−": "-", "·": r"\cdot", "∈": r"\in", "…": r"\ldots", "²": r"^{2}", "³": r"^{3}", "√": r"\surd", "±": r"\pm",
       "⁻": r"^{-}", "¹": r"^{1}", "₀": r"_{0}", "₁": r"_{1}", "₂": r"_{2}", "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "ε": r"\varepsilon", "τ": r"\tau", "ν": r"\nu", "∞": r"\infty", "≠": r"\neq", "π": r"\pi", "λ": r"\lambda"}
HEADER = "\\usepackage{newunicodechar}\n" + "".join(f"\\newunicodechar{{{k}}}{{\\ensuremath{{{v}}}}}\n" for k, v in UNI.items())


def md_to_pdf(md, titel, autoren, aff, d, lang):
    """Preprint-PDF über pandoc (Markdown-Mathematik, Unicode-Zeichen, Bilder), zweispaltig."""
    import pypandoc
    import unicodedata
    body = "\n".join(l for l in md.split("\n") if not l.startswith("# "))           # Titel kommt aus den Metadaten
    body = body.replace("–", "--").replace("—", "---").replace("’", "'").replace("“", "``").replace("”", "''").replace("„", ",,")
    body = re.sub(r"(?<![$\w])e\^\((-?[0-9]*)\s*\*?\s*Delta\)", lambda m: "$e^{" + m.group(1) + "\\Delta}$", body)
    body = re.sub(r"(?<![$\w{])e\^(-?[0-9]*)(Δ|Delta)", lambda m: "$e^{" + m.group(1) + "\\Delta}$", body)
    body = "".join(c if (ord(c) < 256 or c in UNI) else (unicodedata.normalize("NFKD", c).encode("latin-1", "ignore").decode("latin-1") or "?") for c in body)
    body = re.sub(r"(?<![$\w])e\^\{([^}]*)\}", lambda m: "$e^{" + "".join(UNI.get(c, c) for c in m.group(1)) + "}$", body)
    body = re.sub(r"\[(C-[^\]]+)\]", lambda m: "\\textsubscript{[" + m.group(1).replace("_", "\\_") + "]}", body)
    yaml = ("---\ntitle: \"" + titel.replace('"', "'") + "\"\nauthor:\n" + "".join(f"  - {a.strip()}\n" for a in autoren.split(",")) +
            f"date: \"{aff} · Preprint\"\ndocumentclass: article\nclassoption: [twocolumn, 10pt]\ngeometry: margin=1.7cm\n"
            f"lang: {'en' if lang == 'en' else 'de'}\nheader-includes: |\n" + "".join("  " + l + "\n" for l in HEADER.strip().split("\n")) + "---\n\n")
    open(f"{d}/paper_pdf.md", "w").write(yaml + body)
    pypandoc.convert_file(f"{d}/paper_pdf.md", "latex", outputfile=f"{d}/paper.tex", extra_args=["--standalone"])
    pypandoc.convert_file(f"{d}/paper_pdf.md", "pdf", outputfile=f"{d}/paper.pdf", extra_args=["--pdf-engine=pdflatex", f"--resource-path={d}"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--domain", required=True); ap.add_argument("--titel", required=True)
    ap.add_argument("--autoren", required=True); ap.add_argument("--affiliation", default=""); ap.add_argument("--sprache", default="de", choices=["de", "en"])
    ap.add_argument("--hinweise", default="", help="zusätzliche Gliederungshinweise (Datei oder Text)"); a = ap.parse_args()
    D = get_domain(a.domain); C = claims_of(a.domain)
    extra = open(a.hinweise).read() if a.hinweise and os.path.exists(a.hinweise) else a.hinweise
    outline = (OUTLINE_EN if a.sprache == "en" else OUTLINE_DE) + ("\n\n" + extra if extra else "")
    md, log = write(a.titel, f"Research field: {D.kontext}\n\n{outline}", C, salt=f"paper-{a.domain}-{a.sprache}", lang=a.sprache, extra_check=rule_issues)
    d = f"projects/{a.domain}"; rest = check(md, C); n_cited = len(set(re.findall(r"C-[\w\-*.]+", md))); runden = json.dumps(log["runden"], ensure_ascii=False)
    proto = (f"\n\n---\nPrüfprotokoll: {n_cited} Claims zitiert, Korrekturrunden {runden}, "
             f"{len(log['entfernt'])} unbelegte Sätze entfernt, verbleibende Verstöße: {len(rest)}.")
    figs = D.figures(json.load(open(f"{d}/state.json")), d); md_fig = md
    for fn, cap in figs: md_fig += f"\n\n![{cap}]({fn.replace('.pdf', '.png')})\n"
    open(f"{d}/paper.md", "w").write(f"# {a.titel}\n\n{a.autoren}, {a.affiliation}\n\n{md_fig}{proto}\n")
    json.dump({"claims": C, "log": log}, open(f"{d}/paper_belege.json", "w"), ensure_ascii=False, indent=1)
    try: md_to_pdf(md_fig + proto, a.titel, a.autoren, a.affiliation, d, a.sprache)
    except Exception as e:                                               # Rückfall: einfacher Konverter
        print("pandoc fehlgeschlagen:", str(e)[:300]); open(f"{d}/paper.tex", "w").write(to_tex(md + proto, a.titel, a.autoren, a.affiliation, figs, a.sprache))
    print(f"{d}/paper.md, paper.tex" + (", paper.pdf" if os.path.exists(f"{d}/paper.pdf") else "") + proto)


if __name__ == "__main__":
    main()
