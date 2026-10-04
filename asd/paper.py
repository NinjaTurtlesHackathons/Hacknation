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
    fp = f"projects/{domain}/fakten.json"                               # per Code ermittelte Zusatzfakten (Zertifikats-Logs, Zählungen)
    if os.path.exists(fp):
        for f in json.load(open(fp)): C.append({"claim_id": f"C-{f['id']}", "text": f["text"], "level": f.get("level", "observed"), "status": "bestätigt"})
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
    outline = (OUTLINE_EN if a.sprache == "en" else OUTLINE) + ("\n\n" + extra if extra else "")
    md, log = write(a.titel, f"Research field: {D.kontext}\n\n{outline}", C, salt=f"paper-{a.domain}-{a.sprache}", lang=a.sprache)
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
