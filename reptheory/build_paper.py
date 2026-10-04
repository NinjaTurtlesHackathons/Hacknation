"""Builds reptheory/paper.pdf behind a gate.

1. runs the verifier (certify.py: self-test, then all certificates) and the reference check output (out/refs.json);
2. generates the character tables of the paper from the verifier (out/tables_*.tex), so no table entry is typed by hand;
3. paper gate: every theorem-like environment carries \\claim{ID} with an ID that exists in out/claims.csv with status
   verified/proved; every claim of out/claims.csv is used; every \\cite key is verified in out/refs.json;
4. pdflatex twice.
Any failure stops the build with exit code 1.

    python3 reptheory/build_paper.py
"""
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)


def fail(msg):
    print("GATE FAILED:", msg); sys.exit(1)


def run_verifier():
    r = subprocess.run([sys.executable, os.path.join(HERE, "certify.py")], capture_output=True, text=True)
    if r.returncode != 0:
        fail("certify.py:\n" + r.stdout + r.stderr)
    gates = list(csv.DictReader(open(os.path.join(OUT, "gates.csv"))))
    for g in gates:
        print(f"  gate {g['gate']}: {g['passed']} ({g['reason']})")
    if not all(g["passed"] == "True" for g in gates):
        fail("a verifier gate is red")


def latex_value(x, N):
    from cyclo import Cyc
    q = x.rational()
    if q is not None:
        return f"${q}$"
    names = {3: lambda k: r"\omega" if k == 1 else r"\omega^2", 4: lambda k: "i" if k == 1 else "-i"}
    for k in range(1, N):
        for s in (1, -1):
            if x == Cyc.zeta(N, k) * s:
                if N in names and s == 1:
                    return f"${names[N](k)}$"
                if N == 4 and k == 1 and s == -1:
                    return "$-i$"
                return f"${'-' if s < 0 else ''}\\zeta_{{{N}}}^{{{k}}}$"
    raise ValueError(f"cannot typeset {x!r}")


CLASS_LABELS = {  # labels of class representatives in the order computed by certify.py (checked below via orders)
    "S3": ["$e$", "$(12)$", "$(123)$"],
    "D4": ["$e$", "$r$", "$s$", "$r^2$", "$rs$"],
    "Q8": ["$1$", "$i$", "$j$", "$-1$", "$k$"],
    "A4": ["$e$", "$(123)$", "$(12)(34)$", "$(132)$"],
    "S4": ["$e$", "$(12)$", "$(1234)$", "$(123)$", "$(12)(34)$"],
    "C4": ["$e$", "$c$", "$c^2$", "$c^3$"],
}
EXPECTED_ORDERS = {"S3": [1, 2, 3], "D4": [1, 4, 2, 2, 2], "Q8": [1, 4, 4, 2, 4], "A4": [1, 3, 2, 3],
                   "S4": [1, 2, 4, 3, 2], "C4": [1, 4, 2, 4]}
IRREP_LABELS = {
    "S3": ["trivial", "sign", "standard"],
    "D4": [r"$\varepsilon_{++}$", r"$\varepsilon_{+-}$", r"$\varepsilon_{-+}$", r"$\varepsilon_{--}$", "plane"],
    "Q8": [r"$\varepsilon_{++}$", r"$\varepsilon_{+-}$", r"$\varepsilon_{-+}$", r"$\varepsilon_{--}$", "quaternion"],
    "A4": [r"$\lambda_0$", r"$\lambda_1$", r"$\lambda_2$", "standard"],
    "S4": ["trivial", "sign", r"$\sigma_2$", "standard", r"standard$\otimes$sign"],
    "C4": [r"$\chi_0$", r"$\chi_1$", r"$\chi_2$", r"$\chi_3$"],
}


def make_tables():
    import certify as C
    groups = {"S3": C.S3(), "D4": C.D4(), "Q8": C.Q8(), "A4": C.A4(), "S4": C.S4(), "C4": C.cyclic(4)}
    for name, G in groups.items():
        R = C.reps_of(G)
        ok, why, _ = C.cert_character_table(G, R)
        if not ok:
            fail(f"table {name}: {why}")
        orders = [G.order(c[0]) for c in G.classes]
        if orders != EXPECTED_ORDERS[name]:
            fail(f"class order changed for {name}: {orders}; update CLASS_LABELS")
        T = C.char_table(G, R)
        cols = len(G.classes)
        lines = [r"\begin{tabular}{l" + "r" * cols + "}", r"\toprule",
                 " & ".join(["class"] + CLASS_LABELS[name]) + r" \\",
                 " & ".join(["size"] + [f"${len(c)}$" for c in G.classes]) + r" \\",
                 " & ".join([r"$|C_G(g)|$"] + [f"${G.centralizer_size(c[0])}$" for c in G.classes]) + r" \\", r"\midrule"]
        for lab, row in zip(IRREP_LABELS[name], T):
            lines.append(" & ".join([lab] + [latex_value(x, G.N) for x in row]) + r" \\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        open(os.path.join(OUT, f"table_{name}.tex"), "w").write("\n".join(lines) + "\n")
    print("  tables generated from the verifier:", ", ".join(groups))


def make_provenance(claims):
    rows = [r"\begin{longtable}{p{1.6cm}p{3.0cm}p{1.3cm}p{6.8cm}}", r"\toprule",
            r"claim & level & status & evidence \\", r"\midrule", r"\endhead"]
    for c in claims:
        ev = c["evidence"].replace("_", r"\_")
        rows.append(f"\\texttt{{{c['claim_id']}}} & {{\\footnotesize\\texttt{{{c['level'].replace('_', '-')}}}}} & {c['status']} & "
                    f"\\footnotesize {ev} \\\\")
    rows += [r"\bottomrule", r"\end{longtable}"]
    open(os.path.join(OUT, "provenance.tex"), "w").write("\n".join(rows) + "\n")


def paper_gate(tex, claims, refs):
    ok_ids = {c["claim_id"] for c in claims if c["status"] in ("verified", "proved")}
    all_ids = {c["claim_id"] for c in claims}
    envs = re.findall(r"\\begin\{(theorem|lemma|proposition|corollary|example)\}(.*?)\\end\{\1\}", tex, re.S)
    used = set()
    for kind, body in envs:
        ids = re.findall(r"\\claim\{([^}]*)\}", body)
        if not ids:
            fail(f"{kind} without \\claim: {body[:80]!r}")
        for group in ids:
            for cid in [x.strip() for x in group.split(",")]:
                if cid not in ok_ids:
                    fail(f"{kind} cites claim {cid} that is not verified/proved")
                used.add(cid)
    used |= {x.strip() for g in re.findall(r"\\claim\{([^}]*)\}", tex) for x in g.split(",")}
    if all_ids - used:
        fail(f"claims not used in the paper: {sorted(all_ids - used)}")
    for key in {k.strip() for g in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]*)\}", tex) for k in g.split(",")}:
        if refs.get(key, {}).get("status") != "verified":
            fail(f"citation {key} not verified by Crossref (would be UNVERIFIED)")
    print(f"  paper gate: {len(envs)} theorem-like environments, all carry verified/proved claim_ids; "
          f"{len(used)} claims used; citations verified")


def main():
    run_verifier()
    claims = list(csv.DictReader(open(os.path.join(OUT, "claims.csv"))))
    refs = json.load(open(os.path.join(OUT, "refs.json")))
    make_tables()
    make_provenance(claims)
    tex = open(os.path.join(HERE, "paper.tex")).read()
    paper_gate(tex, claims, refs)
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"], cwd=HERE,
                           capture_output=True, text=True)
        if r.returncode != 0:
            fail("pdflatex:\n" + r.stdout[-3000:])
    print("  built reptheory/paper.pdf")


if __name__ == "__main__":
    main()
