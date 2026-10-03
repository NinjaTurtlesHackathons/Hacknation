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


OUTLINE_EN = """Style: concise mathematical-physics preprint (about 4-6 pages), sober and precise, no marketing language, no speculation.
Sections: Abstract (at most 150 words). 1 Introduction (question, contribution, bullet list of results). 2 Setting and certificates (the model
assumptions and the verifier's certificates that carry the results). 3 Method: the agentic laboratory (literature scout with code-verified
quotes, integrator, researcher cascade, code verifier, red team, preregistration), briefly. 4 Results: each result as a numbered
statement (Proposition only for computed_rigorous or proved_lean, otherwise 'Numerical observation'), with its evidence level in parentheses,
and one Markdown table summarising the certified values. 5 Negative results, preregistration outcome and red-team findings. 6 Limitations and
open questions (state explicitly what is not shown, and that no novelty is claimed beyond what the claims support). Related work only from
claims with a literature source. Translate the German claim texts faithfully; keep every number exactly as in the claims. Do not write a title, author names, affiliations
or contact details (they are added automatically); start directly with the Abstract. Prefer derived claims (C-kombi*) where they combine results."""


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
            C.append({"claim_id": f"C-{c['id']}-RT{j + 1}", "text": f"Red-Team-Gegenprüfung zu {c['id']}: {r['idee']} -> {'bestanden (Aussage angefochten)' if r['bestanden'] else 'nicht bestanden'}; {r['grund']}",
                      "level": "computed_rigorous", "status": "bestätigt"})
    for j, w in enumerate(s["widerlegt"]): C.append({"claim_id": f"C-neg{j + 1}", "text": f"Negatives Ergebnis: {w}", "level": "observed", "status": "bestätigt"})
    for j, w in enumerate(s["wissen"][:30]):
        C.append({"claim_id": f"C-lit{j + 1}", "text": f"Literatur: {w['text']} (Zitat: „{w['zitat']}“, {w['quelle']})", "level": "observed", "status": "bestätigt"})
    extra = f"projects/{domain}/zusatz_claims.json"           # z. B. Auswertung der Präregistrierung, Selbsttest (per Code erzeugt)
    if os.path.exists(extra): C += json.load(open(extra))
    C.append({"claim_id": "C-methode", "text": f"Das Labor lief {len(s['runden'])} Runden, {len(s['claims'])} geprüfte Aussagen, {len(s['widerlegt'])} negative Ergebnisse, "
              f"Kosten {s['kosten_usd']:.2f} USD; jede Runde vor dem Experiment präregistriert (prereg.md).", "level": "observed", "status": "bestätigt"})
    return C


def to_tex(md, titel, autoren, aff, lang="de"):
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
    return (r"""\documentclass[10pt,twocolumn]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage[""" + ("english" if lang == "en" else "ngerman") + r"""]{babel}\usepackage{amsmath,amssymb}\usepackage[margin=1.8cm]{geometry}
\usepackage{times}\usepackage{hyperref}
\title{\textbf{""" + titel + r"""}}
\author{""" + r" \and ".join(a.strip() for a in autoren.split(",")) + r"""\\ \small """ + aff + r"""}
\date{Preprint, \today}
\begin{document}\maketitle
""" + body + "\n\\end{document}\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--domain", required=True); ap.add_argument("--titel", required=True)
    ap.add_argument("--autoren", required=True); ap.add_argument("--affiliation", default="")
    ap.add_argument("--lang", default="de", choices=["de", "en"]); a = ap.parse_args()
    D = get_domain(a.domain); C = claims_of(a.domain)
    outline = OUTLINE_EN if a.lang == "en" else OUTLINE
    md, log = write(a.titel, f"Forschungsgebiet: {D.kontext}\n\n{outline}", C, salt=f"paper-{a.domain}-{a.lang}", lang=a.lang)
    md = "\n".join(l for l in md.split("\n") if not re.match(r"^# ", l) and not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", l)).strip()  # Titel/Kontakt setzt der Code
    d = f"projects/{a.domain}"; rest = check(md, C); n_cit = len(set(re.findall(r"C-[\w\-*.]+", md)))
    if a.lang == "en":
        seq = " → ".join(str(r["verstoesse"]) for r in log["runden"] if "verstoesse" in r)
        proto = (f"\n\n---\n*Verification log (automatic):* {n_cit} claim IDs cited; unsupported statements per writing round: {seq}; "
                 f"{len(log['entfernt'])} sentences removed; remaining violations: {len(rest)}. Claim texts and evidence: `paper_belege.json`.")
    else: proto = (f"\n\n---\nPrüfprotokoll: {n_cit} Claims zitiert, Korrekturrunden {json.dumps(log['runden'], ensure_ascii=False)}, "
             f"{len(log['entfernt'])} unbelegte Sätze entfernt, verbleibende Verstöße: {len(rest)}.")
    open(f"{d}/paper.md", "w").write(f"# {a.titel}\n\n{a.autoren}, {a.affiliation}\n\n{md}{proto}\n")
    open(f"{d}/paper.tex", "w").write(to_tex(md + proto, a.titel, a.autoren, a.affiliation, a.lang))
    json.dump({"claims": C, "log": log}, open(f"{d}/paper_belege.json", "w"), ensure_ascii=False, indent=1)
    if shutil.which("pdflatex"):
        for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=d, capture_output=True)
    print(f"{d}/paper.md, paper.tex" + (", paper.pdf" if os.path.exists(f"{d}/paper.pdf") else "") + proto)


if __name__ == "__main__":
    main()
