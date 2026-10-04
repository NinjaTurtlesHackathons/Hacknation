"""Paper aus einem Projekt der Labor-Schleife: nur geprüfte Aussagen, jede Zahl belegt (Halluzinations-Gate).
  python -m asd.paper --domain proofreading --titel "..." --autoren "A, B, C" --affiliation "ETH Zürich"
Erzeugt projects/<domain>/paper.md, paper.tex (und paper.pdf, wenn pdflatex installiert ist)."""
import argparse, json, os, re, shutil, subprocess
from .writer import write, check
from .domains.base import get_domain

OUTLINE = """Stil: kurzes mathematisch-physikalisches Preprint. Abschnitte: 1 Einleitung (Frage, Beitrag, Zusammenfassung der Resultate als Liste),
2 Modell (Annahmen, die die Resultate tragen), 3 Methode: das agentische Labor (Scout, Integrator, Forscher, Code-Prüfer, Red-Team,
Präregistrierung), 4 Resultate: jedes Resultat als nummerierte Aussage (Theorem/Proposition nur für computed_rigorous oder proved_lean,
sonst 'Numerischer Befund' bzw. 'Beobachtung') mit Evidenzstufe in Klammern, 5 Negative Ergebnisse und Red-Team-Befunde,
6 Grenzen und offene Fragen. Literatur nur aus Claims mit Quelle."""


OUTLINE_EN = """Style: short mathematical-physics preprint in English (like an arXiv paper). Sections: Abstract; 1 Introduction (question, contribution,
bullet list summarising the results); 2 Model (assumptions that carry the results, stated explicitly); 3 Method: the verifier-gated agentic lab
(scout with code-checked quotes, integrator, preregistration, researcher agents, code verifier with exact rational and symbolic certificates,
red team); 4 Results: each result as a numbered statement - call it Theorem/Proposition ONLY for computed_rigorous or proved_lean claims, otherwise
'Numerical observation' - with its evidence level in parentheses; 5 Negative results and red-team findings; 6 Limitations and open questions;
References (only sources that appear in claims, with DOI/arXiv id)."""


def claims_of(domain):
    s = json.load(open(f"projects/{domain}/state.json")); C = []; D = get_domain(domain)
    for c in s["claims"]:
        text = D.describe(c["pruefung"]) if c.get("pruefung") else c["text"]          # nur was die Prüfung beweist
        C.append({"claim_id": f"C-{c['id']}", "text": f"Untersuchte Frage: {c['frage']} Geprüftes Resultat: {text} Prüfer: {c['grund']}",
                  "level": c["level"], "status": c["status"]})
        interp = c.get("interpretation_ungeprueft") or c["text"].split("->")[-1]
        C.append({"claim_id": f"C-{c['id']}-I", "text": f"Ungeprüfte Interpretation des Agenten zu {c['id']} (nicht als Resultat verwenden): {interp}",
                  "level": "hypothesis", "status": "offen"})
        for j, r in enumerate(c.get("red_team", [])):
            C.append({"claim_id": f"C-{c['id']}-RT{j + 1}", "text": f"Red-Team-Gegenprüfung zu {c['id']}: {r['idee']} -> {('bestanden, logischer Widerspruch: Aussage angefochten' if r.get('widerspruch') else 'bestanden, aber kein logischer Widerspruch') if r['bestanden'] else 'nicht bestanden'}; {r['grund']}",
                      "level": "computed_rigorous", "status": "bestätigt"})
    for j, w in enumerate(s["widerlegt"]): C.append({"claim_id": f"C-neg{j + 1}", "text": f"Negatives Ergebnis: {w}", "level": "observed", "status": "bestätigt"})
    for j, w in enumerate(s["wissen"][:30]):
        C.append({"claim_id": f"C-lit{j + 1}", "text": f"Literatur: {w['text']} (Zitat: „{w['zitat']}“, {w['quelle']})", "level": "observed", "status": "bestätigt"})
    C.append({"claim_id": "C-methode", "text": f"Das Labor lief {len(s['runden'])} Runden, {len(s['claims'])} geprüfte Aussagen, {len(s['widerlegt'])} negative Ergebnisse, "
              f"Kosten {s['kosten_usd']:.2f} USD; jede Runde vor dem Experiment präregistriert (prereg.md).", "level": "observed", "status": "bestätigt"})
    return C


UNI_TEX = {"δ": r"\delta", "α": r"\alpha", "β": r"\beta", "λ": r"\lambda", "≤": r"\le", "≥": r"\ge", "≠": r"\neq", "−": "-", "→": r"\to",
           "×": r"\times", "Σ": r"\Sigma", "²": "^2", "³": "^3", "≅": r"\cong", "∈": r"\in", "∞": r"\infty", "ℓ": r"\ell", "·": r"\cdot",
           "∪": r"\cup", "⊕": r"\oplus", "Q̄": r"\overline{\mathbb Q}"}
TEXT_ESC = {"_": r"\_", "%": r"\%", "&": r"\&", "#": r"\#", "^": r"\^{}", "~": r"\textasciitilde{}"}


def _inline(t, math=False):
    """Markdown-Inline -> LaTeX. Mathe-Segmente ($...$, $$...$$) bleiben unverändert; im Text werden Sonderzeichen maskiert,
    Unicode-Mathezeichen in $...$ gesetzt und Claim-Belege klein gedruckt."""
    out = []
    for seg in re.split(r"(\$\$.+?\$\$|\$[^$]+?\$)", t):
        if seg.startswith("$"):
            for k, v in UNI_TEX.items(): seg = seg.replace(k, v + (" " if v[-1].isalpha() else ""))
            seg = re.sub(r"\\text(?:rm|tt)?\{([^{}]*)\}", lambda m: m.group(0).replace("_", r"\_"), seg)   # Unterstriche in \text{...}
            out.append(seg.replace("%", r"\%")); continue
        seg = re.sub(r"\[(C-[^\]]+)\]", lambda m: "\x00" + m.group(1) + "\x01", seg)
        seg = re.sub(r"`([^`]+)`", lambda m: "\x02" + m.group(1) + "\x03", seg)
        seg = "".join(TEXT_ESC.get(c, c) for c in seg)
        for k, v in UNI_TEX.items(): seg = seg.replace(k, f"${v}$")
        seg = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", seg); seg = re.sub(r"(?<![*\w])\*(?!\*)(.+?)\*(?!\w)", r"\\emph{\1}", seg)
        seg = re.sub("\x00([^\x01]*)\x01", lambda m: r"{\scriptsize[" + m.group(1) + "]}", seg)
        seg = re.sub("\x02([^\x03]*)\x03", lambda m: r"\texttt{" + m.group(1) + "}", seg)
        out.append(seg)
    return "".join(out)


def to_tex(md, titel, autoren, aff, figs=(), lang="de"):
    md = re.sub(r"\$\$(.+?)\$\$", lambda m: "$$" + " ".join(m.group(1).split("\n")) + "$$", md, flags=re.S)   # Display-Mathe auf eine Zeile
    lines, out, inlist, intab = md.split("\n"), [], False, False
    for l in lines:
        if re.match(r"^\s*\|", l):                                       # Markdown-Tabelle -> tabular
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells): continue
            if not intab: out.append(r"\begin{center}\small\begin{tabular}{" + "l" * len(cells) + "}\\hline"); intab = True
            out.append(" & ".join(_inline(c) for c in cells) + r" \\"); continue
        if intab: out.append(r"\hline\end{tabular}\end{center}"); intab = False
        if re.match(r"^\s*[-*] ", l):
            if not inlist: out.append(r"\begin{itemize}"); inlist = True
            out.append(r"\item " + _inline(re.sub(r"^\s*[-*] ", "", l))); continue
        if inlist: out.append(r"\end{itemize}"); inlist = False
        m = re.match(r"^(#+) (.*)$", l)
        if m:
            lvl, txt = len(m.group(1)), _inline(m.group(2))
            out.append("" if lvl == 1 else (r"\section*{" if lvl == 2 else r"\subsection*{") + txt + "}" if lvl > 1 else ""); continue
        if l.strip() == "---": out.append(r"\par\noindent\rule{\columnwidth}{0.4pt}\par"); continue
        out.append(_inline(l))
    if inlist: out.append(r"\end{itemize}")
    if intab: out.append(r"\hline\end{tabular}\end{center}")
    body = "\n".join(out)
    for fn, cap in figs:
        body += "\n\\begin{figure}[t]\\centering\\includegraphics[width=\\columnwidth]{" + fn + "}\\caption{" + _inline(cap) + "}\\end{figure}\n"
    return (r"""\documentclass[10pt,twocolumn]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage[""" + ("english" if lang == "en" else "ngerman") + r"""]{babel}\usepackage{amsmath,amssymb}\usepackage[margin=1.8cm]{geometry}
\usepackage{times}\usepackage{graphicx}\usepackage{hyperref}
\title{\textbf{""" + titel + r"""}}
\author{""" + r" \and ".join(a.strip() for a in autoren.split(",")) + r"""\\ \small """ + aff + r"""}
\date{Preprint, \today}
\begin{document}\maketitle\sloppy\emergencystretch=3em
""" + body + "\n\\end{document}\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--domain", required=True); ap.add_argument("--titel", required=True)
    ap.add_argument("--autoren", required=True); ap.add_argument("--affiliation", default=""); ap.add_argument("--sprache", default="de", choices=["de", "en"])
    ap.add_argument("--hinweise", default="", help="zusätzliche Gliederungshinweise (Datei oder Text)"); a = ap.parse_args()
    D = get_domain(a.domain); C = claims_of(a.domain)
    extra = open(a.hinweise).read() if a.hinweise and os.path.exists(a.hinweise) else a.hinweise
    outline = (OUTLINE_EN if a.sprache == "en" else OUTLINE) + ("\n\n" + extra if extra else "")
    md, log = write(a.titel, f"Research field: {D.kontext}\n\n{outline}", C, salt=f"paper-{a.domain}-{a.sprache}", lang=a.sprache)
    d = f"projects/{a.domain}"; rest = check(md, C); n_cited = len(set(re.findall(r"C-[\w\-*.]+", md))); runden = json.dumps(log["runden"], ensure_ascii=False)
    proto = (f"\n\n---\nPrüfprotokoll: {n_cited} Claims zitiert, Korrekturrunden {runden}, "
             f"{len(log['entfernt'])} unbelegte Sätze entfernt, verbleibende Verstöße: {len(rest)}.")
    figs = D.figures(json.load(open(f"{d}/state.json")), d); md_fig = md
    for fn, cap in figs: md_fig += f"\n\n![{cap}]({fn.replace('.pdf', '.png')})\n"
    open(f"{d}/paper.md", "w").write(f"# {a.titel}\n\n{a.autoren}, {a.affiliation}\n\n{md_fig}{proto}\n")
    open(f"{d}/paper.tex", "w").write(to_tex(md + proto, a.titel, a.autoren, a.affiliation, figs, a.sprache))
    json.dump({"claims": C, "log": log}, open(f"{d}/paper_belege.json", "w"), ensure_ascii=False, indent=1)
    if shutil.which("pdflatex"):
        for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=d, capture_output=True)
    print(f"{d}/paper.md, paper.tex" + (", paper.pdf" if os.path.exists(f"{d}/paper.pdf") else "") + proto)


if __name__ == "__main__":
    main()
