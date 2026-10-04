"""Abgabe-Artefakte aus eingefrorenen Zahlen: submission/summary.md (<= 280 Wörter), submission/OnePager.pdf, submission/code.zip.

  python -m asd.freeze && python -m asd.submission

Zahlen-Gate: Jede Zahl in den Texten muss wörtlich in results/FROZEN.json vorkommen, sonst Abbruch (wie das Halluzinations-Gate des Papers)."""
import json, os, re, shutil, subprocess, sys

ZAHL = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?:e[-+]?\d+)?")


def gate(text, frozen_txt, wo):
    fehlt = sorted({z for z in ZAHL.findall(text) if not re.search(r"(?<![\d.])" + re.escape(z) + r"(?![\d])", frozen_txt)})
    if fehlt: sys.exit(f"ZAHLEN-GATE ROT in {wo}: nicht in results/FROZEN.json: {fehlt}")


def texte(F):
    M, R, T, V, K = F["metrics"], F["replay"], F["trust"], F["verifier_stress"], F["flaggschiff"]
    H = R["tests"]; a, b, c = H["H8a"], H["H8b"], H["H8c"]; BN = R["bedingungen"]
    ci = lambda t: f"95% CI {t['ki95'][0]} to {t['ki95'][1]}"
    summary = f"""# Verifier-Gated Discovery Lab

**Agents propose, Omnigent orchestrates, only a code verifier accepts.** Our lab turns the scientific method into an executable loop: a
planner chooses between rival experiments under a budget, researchers run them, and a domain verifier (exact rational certificates,
symbolic proofs, fixed tolerances) is the only authority that confirms a claim. A red team on a different model attacks every confirmed
claim; surprises reopen assumptions; humans approve publication through Omnigent policies. Every action is logged with input and output
ids and sealed in a hash chain.

**Result.** In the first recorded Omnigent run ({M['laufzeit_min']} min, {M['kosten_gesamt_usd']} USD) the lab produced {M['zertifizierte_claims']} certified
claims and rejected {M['abgelehnte_behauptungen']}. Across {F['omnigent_laeufe']} recorded runs the lab found {K['neu_in_omnigent_laeufen']} new exactly
certified violations of the kinetic-proofreading bound. The {K['topologien']}-topology family now reads {K['bewiesen']} proved / {K['verletzt']} violated / {K['offen']} open.

**Measured acceleration.** Verifier result to next decision: median {M['latenz_median_s']} s (n = {M['latenz_n']}); question to certified claim:
median {M['frage_zu_zertifikat_median_s']} s (one run, small n). Preregistered replay ({R['n_seeds']} paired seeds):
the lab needs {BN['LAB']['mean_N']} verifier calls on average, a hand-written heuristic {BN['HEURISTIK']['mean_N']}, random proposals {BN['ZUFALL']['mean_N']}.
That is {b['speedup']}x fewer calls than the strong heuristic ({ci(b)}, p = {b['p']}) and {a['speedup']}x fewer than random ({ci(a)}, p = {a['p']});
versus the same agents without verifier feedback {c['speedup']}x, not significant.

**Trust.** On {T['B']['n']} answers each: Claude alone {T['A1']['anteil_falsch_pct']}% false, Claude with Python {T['A2']['anteil_falsch_pct']}% false, the lab
{T['B']['anteil_falsch_pct']}% false (95% CI {T['B']['falsch_ki95_pct'][0]} to {T['B']['falsch_ki95_pct'][1]}%). Caveat: 12 questions from one paper, a small home-field sample. Blind stress test: {V['blind_akzeptiert']} of {V['blind_claims']} random claims accepted.

The same lab runs as an MCP server inside anyone's own Claude.
"""
    secs = [
        ("Challenge and users", "Agentic scientific discovery (Databricks challenge). Users: researchers who need results they can trust without re-checking every line."),
        ("Tools", "Omnigent (orchestration, policies), Claude via the Claude Code CLI, Python verifiers (sympy, python-flint, scipy), MCP server, LaTeX."),
        ("What worked", f"The verifier-gated loop: {M['zertifizierte_claims']} certified and {M['abgelehnte_behauptungen']} rejected claims in one run; a surprise reopened "
                        f"an assumption and changed the plan; the family classification moved to {K['bewiesen']} / {K['verletzt']} / {K['offen']}."),
        ("What was hard", "Making the agents' claims exactly as strong as the evidence; keeping tolerances inside the verifier; parallel agents writing one state file (fixed with a file lock)."),
        ("Time use", f"Recorded run {M['laufzeit_min']} min, of which {M['mensch_warten_min']} min waiting for human approval; agents/LLM at least {M['zeit_agenten_llm_s']} s, "
                     f"verifier at most {M['zeit_verifier_s']} s, experiments at most {M['zeit_experimente_s']} s."),
        ("Results", f"{K['verletzt']} exactly certified violations of the proofreading bound among {K['topologien']} topologies, {K['neu_in_omnigent_laeufen']} of them new in the recorded Omnigent runs; "
                    f"trust benchmark: lab {T['B']['anteil_falsch_pct']}% false vs. Claude alone {T['A1']['anteil_falsch_pct']}%."),
        ("Measured speedup", f"Replay, {R['n_seeds']} paired seeds: {b['speedup']}x vs. a hand-written heuristic ({ci(b)}, p = {b['p']}), {a['speedup']}x vs. random ({ci(a)}, p = {a['p']}); "
                             f"vs. no feedback {c['speedup']}x (not significant). Result-to-decision latency median {M['latenz_median_s']} s (n = {M['latenz_n']}, one run). "
                             "No comparison with a human or a real laboratory was measured."),
        ("Next 24 h", f"Decide the {K['offen']} open topologies (cycle decomposition for proofs, wider counterexample search); second domain."),
    ]
    return summary, secs


ONEPAGER = r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=1.8cm]{geometry}\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{microtype}\usepackage{titlesec}
\titleformat{\section}{\normalfont\bfseries}{}{0pt}{}\titlespacing*{\section}{0pt}{5pt}{1pt}\setlength{\parindent}{0pt}\pagestyle{empty}
\begin{document}
{\Large\bfseries Verifier-Gated Discovery Lab}\\[2pt]{\small Agents propose, Omnigent orchestrates, only a code verifier accepts. \quad Commit %(commit)s}\par\medskip
%(body)s
\end{document}
"""


def tex_esc(t): return t.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#").replace("$", r"\$")


def main():
    F = json.load(open("results/FROZEN.json")); ft = json.dumps(F, ensure_ascii=False)
    summary, secs = texte(F)
    n_worte = len(re.findall(r"\b\w[\w'.-]*\b", re.sub(r"[#*]", "", summary)))
    if n_worte > 280: sys.exit(f"summary.md hat {n_worte} Wörter (> 280)")
    gate(summary, ft, "summary.md")
    plain = "\n".join(f"{h}: {t}" for h, t in secs); gate(plain, ft, "OnePager")
    os.makedirs("submission", exist_ok=True)
    open("submission/summary.md", "w").write(summary)
    body = "\n".join(f"\\section{{{tex_esc(h)}}}\n{tex_esc(t)}\\par" for h, t in secs)
    open("submission/OnePager.tex", "w").write(ONEPAGER % {"commit": tex_esc(F["commit"]), "body": body})
    for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "OnePager.tex"], cwd="submission", capture_output=True)
    for x in ("aux", "log", "out"):
        if os.path.exists(f"submission/OnePager.{x}"): os.remove(f"submission/OnePager.{x}")
    if os.path.exists("submission/code.zip"): os.remove("submission/code.zip")
    subprocess.run(["git", "archive", "--format=zip", "-o", "submission/code.zip", "HEAD", "--", ".", ":(exclude)cache", ":(exclude)rxnpredict",
                    ":(exclude)research/kb", ":(exclude)results/benchmark", ":(exclude)runs/omnigent/*/sessions"], check=True)
    seiten = subprocess.run(["pdfinfo", "submission/OnePager.pdf"], capture_output=True, text=True).stdout
    print(json.dumps({"summary_woerter": n_worte, "zahlen_gate": "grün", "onepager_seiten": re.search(r"Pages:\s+(\d+)", seiten).group(1) if "Pages" in seiten else "?",
                      "code_zip_mb": round(os.path.getsize("submission/code.zip") / 1e6, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
