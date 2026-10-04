"""Companion proof ledger (team convention, cf. results.pdf on the quivers branch): expressivity/theory.md -> projects/expressivity/theory_ledger.pdf.
  python expressivity/scripts/build_ledger.py"""
import subprocess

SYM = {"∈": r"$\in$", "≠": r"$\neq$", "≤": r"$\leq$", "≥": r"$\geq$", "⊆": r"$\subseteq$", "→": r"$\to$", "⊕": r"$\oplus$"}
md = open("expressivity/theory.md").read()
for k, v in SYM.items(): md = md.replace(k, v)
open("projects/expressivity/theory_ledger.md", "w").write(md)
r = subprocess.run(["pandoc", "theory_ledger.md", "-o", "theory_ledger.pdf", "--pdf-engine=xelatex", "-V", "mainfont=STIXGeneral", "-V", "mathfont=STIX Two Math",
                    "-V", "geometry:margin=2cm", "-V", "fontsize=10pt", "-M", "title=Companion ledger: definitions, lemmas and proofs",
                    "-M", "author=Team Ninja Turtles"], cwd="projects/expressivity", capture_output=True, text=True)
print("missing glyphs:", r.stderr.count("Missing character"), "| exit", r.returncode)
