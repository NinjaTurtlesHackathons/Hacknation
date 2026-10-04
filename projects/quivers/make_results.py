"""Ergebnis-Ledger ohne Paper-Schreiber: results_body.tex (Sätze, Beweise, Verweise auf claim_ids, von Hand) + Anhang mit jeder
geprüften Aussage aus state.json (kanonische Aussage, Stufe, Prüfer-Begründung, Red-Team) -> results.tex; Rohdaten -> results.json.
Prüft außerdem, dass jede im Text zitierte claim_id existiert.
  python projects/quivers/make_results.py"""
import json, os, re, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from asd.domains.quivers_domain import DOMAIN as D

OUT = os.path.dirname(os.path.abspath(__file__))
ESC = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "_": r"\_", "#": r"\#", "$": r"\$", "%": r"\%", "&": r"\&", "~": r"\textasciitilde{}",
       "^": r"\textasciicircum{}"}


UNI = {"Q̄": r"$\overline{\mathbb Q}$", "≅": r"$\cong$", "≠": r"$\neq$", "≤": r"$\le$", "≥": r"$\ge$", "→": r"$\to$", "δ": r"$\delta$"}


def esc(s):
    out = "".join(ESC.get(c, c) for c in s)
    for k, v in UNI.items(): out = out.replace(k, v)
    return out


def main():
    s = json.load(open(f"{OUT}/state.json")); body = open(f"{OUT}/results_body.tex").read()
    ids = {c["id"] for c in s["claims"]}
    cited = set()
    for a, b in re.findall(r"\\C\{(quivers-R\d+-\d+)\}(?:--\\C\{(quivers-R\d+-\d+)\})?", body):
        if b:
            lo, hi = int(a.rsplit("-", 1)[1]), int(b.rsplit("-", 1)[1])
            cited |= {c["id"] for c in s["claims"] if lo <= int(c["id"].rsplit("-", 1)[1]) <= hi}
        cited.add(a)
    missing = sorted(cited - ids)
    if missing: sys.exit(f"zitierte, aber nicht geprüfte claim_ids: {missing}")
    rows = []
    for c in s["claims"]:
        rt = "; ".join(f"{esc(r['idee'])} $\\to$ {'bestanden' if r['bestanden'] else 'durchgefallen'}" for r in c.get("red_team", []))
        rows.append(f"\\noindent\\textbf{{\\texttt{{[C-{esc(c['id'])}]}}}} ({c['level']}, {c['status']})\\\\\n"
                    f"\\textit{{Aussage:}} {esc(D.describe(c['pruefung']))}\\\\\n\\textit{{Prüfer:}} {esc(c['grund'])}\\\\\n"
                    f"\\textit{{Red-Team:}} {rt or '--'}\\par\\medskip\n")
    lit = "\n".join(f"\\noindent {esc(w['quelle'])}: {esc(w['zitat'])} ({w.get('jahr')}); {esc(', '.join(w.get('autoren', [])))}. Crossref-Titel per Code geprüft.\\par"
                    for w in s["wissen"])
    uncited = sorted(ids - cited)
    tail = (f"\\small\n{''.join(rows)}\n\\section{{Literature retrieved via Crossref}}\n{lit}\n"
            f"\\par\\medskip\\noindent Claims in \\texttt{{state.json}}: {len(ids)}; cited in the body: {len(cited & ids)}; uncited: {esc(', '.join(uncited)) or 'none'}.\n")
    open(f"{OUT}/results.tex", "w").write(body.replace("%%CLAIMS%%", tail))
    json.dump({"claims": [{"id": c["id"], "level": c["level"], "status": c["status"], "aussage": D.describe(c["pruefung"]), "pruefung": c["pruefung"],
                           "pruefer": c["grund"], "red_team": c["red_team"]} for c in s["claims"]], "literatur": s["wissen"],
               "widerlegt": s["widerlegt"]}, open(f"{OUT}/results.json", "w"), ensure_ascii=False, indent=1)
    print(f"results.tex, results.json: {len(ids)} Claims, {len(cited & ids)} im Text zitiert, nicht zitiert: {uncited}")


if __name__ == "__main__":
    main()
