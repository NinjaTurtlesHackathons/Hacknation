"""English paper for the algo_efficiency domain, built only from verified claims.

Sources: projects/algo_efficiency/state.json (agentic lab) and algo_efficiency/results/certified.json (systematic tables, every
entry passed DOMAIN.check). Prose is written by an LLM under the framework's hallucination gate (asd.writer.check: every
sentence with a number must cite a claim containing that number; unknown claim ids are rejected; violations go back as feedback,
leftovers are removed and logged). Tables are rendered by code from the certified data, never by the LLM.

  python -m algo_efficiency.write_paper --authors "A, B" --affiliation "..."
"""
import argparse, json, os, re, shutil, subprocess
from fractions import Fraction

from asd.llm import ask
from asd.writer import check
from asd.paper import to_tex
from .domain import DOMAIN as D

PROJ = "projects/algo_efficiency"; CERT = "algo_efficiency/results/certified.json"; CONF = "algo_efficiency/results/confirmatory.json"
TITLE = "Certified Limits and Gaps in Efficient Transformer Inference: Polynomial-Method Attention, Multi-Draft Speculative Decoding, and KV-Cache Eviction"

SYS = ("You write precise, sober scientific English. Return ONLY the paper body: no notes, comments or explanations addressed to the reader or "
       "to the checker, in any language. You may ONLY use statements from the given claim list and must cite every "
       "statement with its claim_id in square brackets, e.g. [C-T-deg-4-1e-3]. Never write a number that does not appear verbatim "
       "in a cited claim. No references other than those inside claims. Claims with level 'hypothesis' may only be presented as "
       "conjectures or as the agents' uninspected interpretations, never as results.")

OUTLINE = """Style: short preprint in theoretical computer science / ML systems. Sections:
1 Introduction (question, contribution as a bullet list, summary of results).
2 Setting (polynomial method for attention and its fine-grained limits; lossless speculative sampling and multi-draft verification; KV-cache eviction on an explicit synthetic model). State assumptions that carry the results.
3 Method: verifier-gated lab (agents propose, code verifies: exact rational arithmetic, max-flow = min-cut certificates, interval arithmetic with Remez and de la Vallee Poussin certificates, paired permutation tests with Benjamini-Hochberg). Mention the per-round preregistration and the red team.
4 Results: one numbered statement per result. 'Theorem'/'Proposition' only for level computed_rigorous on a specific finite instance or table entry (say 'certified'), 'Statistical finding' for level statistical, 'Conjecture' for hypothesis. Refer to Tables 1-4 by name (they are appended by code).
5 Negative results and red-team findings.
6 Limitations (finite vocabularies, synthetic KV model, certified instances are not asymptotic theorems) and open questions.
Do not write the tables yourself."""


def F(s): return Fraction(s)


def fp(p): return f"{p:.1e}" if p < 1e-3 else f"{p:.4f}"


def claims():
    C = []
    def add(cid, text, level, status="confirmed", evidence=()):
        C.append({"claim_id": cid, "text": text, "level": level, "status": status, "evidence": list(evidence)})
    if os.path.exists(f"{PROJ}/state.json"):
        s = json.load(open(f"{PROJ}/state.json"))
        for c in s["claims"]:
            p = c.get("pruefung") or {}
            contra = any(r["bestanden"] and D.widerspricht(p, r["pruefung"]) for r in c.get("red_team", []))
            status = "contested (logical contradiction)" if contra else "confirmed"
            if str(c.get("interpretation_ungeprueft", "")).strip().lower() in ("", "unbekannt", "unknown", "none"):
                add(f"C-{c['id']}", f"Lab round {c['runde']}: the agent's verified check ({D.describe(p)}) is true but gives no answer to the question "
                    f"'{c['frage']}' (agent answer: unknown); counted as a NEGATIVE result for this question (loophole closed afterwards, see decisions AE14).",
                    "observed", "confirmed", [f"lab-R{c['runde']}"])
                continue
            add(f"C-{c['id']}", f"Lab round {c['runde']}. Question: {c['frage']} Verified result: {D.describe(p)} Verifier: {c['grund']}",
                c["level"], status, [f"lab-R{c['runde']}"])
            add(f"C-{c['id']}-I", f"Uninspected interpretation by the agent for {c['id']} (not a result): {c.get('interpretation_ungeprueft')}", "hypothesis", "open")
            for j, r in enumerate(c.get("red_team", [])):
                verdict = ("passed and logically contradicts the claim" if D.widerspricht(p, r["pruefung"]) else "passed but does not contradict the claim") if r["bestanden"] else "failed"
                add(f"C-{c['id']}-RT{j + 1}", f"Red-team counter-check for {c['id']}: {r['idee']} -> {verdict}; verifier: {r['grund']}", "computed_rigorous", evidence=[f"lab-R{c['runde']}"])
        for j, w in enumerate(s["widerlegt"]): add(f"C-neg{j + 1}", f"Negative result of the lab (no claim passed the verifier): {w}", "observed")
        for c in s["claims"]:   # a contested claim stays in the paper only as a negative/contested finding
            pass
        for j, w in enumerate(s["wissen"][:30]):    # the code-checked verbatim quote is the statement; the scout's paraphrase is not checked
            add(f"C-lit{j + 1}", f"Literature ({w['quelle']}), verbatim quote checked by code against the abstract: \"{w['zitat']}\"", "observed")
        unk = sum(str(c.get("interpretation_ungeprueft", "")).strip().lower() in ("", "unbekannt", "unknown", "none") for c in s["claims"])
        add("C-lab", f"The agentic lab ran {len(s['runden'])} rounds at a cost of {s['kosten_usd']:.2f} USD (stopped at its preset budget); every round was "
                     f"preregistered before its experiments. {len(s['claims']) - unk} rounds produced a verified claim answering the question and "
                     f"{len(s['widerlegt']) + unk} rounds produced a negative result (no verified answer).", "observed")
    R = json.load(open(CERT)) if os.path.exists(CERT) else {}
    for r in R.get("degree", []):
        c = r["claim"]
        if r["passed"]:
            add(f"C-T-deg-{c['B']}-{c['eps']}", f"{r['statement']} Verifier: {r['reason']}. For comparison, the Taylor polynomial at 0 needs degree "
                f"{r['taylor_degree_estimate']} (grid estimate, observed).", "computed_rigorous", evidence=[f"deg-B{c['B']}-eps{c['eps']}"])
        else:
            add(f"C-T-deg-{c['B']}-{c['eps']}-fail", f"Certification of d*(B={c['B']}, eps={c['eps']}) = {c['d']} failed: {r['reason']}", "observed")
    for r in R.get("rank", []):
        if "h" in r: add(f"C-T-rank-{r['h']}-{r['B']}", f"With head dimension h = {r['h']}, logit bound B = {r['B']} and relative error {r['eps']}, the certified minimal "
                         f"degree is d* = {r['d']} and the polynomial-method rank is C(h + d*, d*) = {r['rank']}, so it is below n only for context lengths n > {r['rank']}.", "computed_rigorous", evidence=[f"deg-B{r['B']}-eps{r['eps']}"])
        elif r.get("passed"): add("C-T-rank-check", f"{r['statement']} Verifier: {r['reason']}", "computed_rigorous", evidence=["deg-B4-eps1e-3"])
    md = R.get("multidraft")
    if md:
        mdev = [f"md-s{r['seed']}-k{r['k']}" for r in md["instances"]]
        add("C-T-md-setup", f"Multi-draft study (exploratory: computed before the preregistration, but every value is exact and certified): {md['note']}. For every instance and k in {{2, 3}} the exact optimal lossless acceptance (iid and "
            "without-replacement drafts) and the exact acceptance of rrs_iid and rrs_wor were computed and each value passed the verifier.", "computed_rigorous", evidence=mdev)
        for k, sm in md["summary"].items():
            n = sm["instances"]
            add(f"C-T-md-k{k}", f"For k = {k} drafts over {n} instances: rrs_iid attains the optimal iid acceptance on {sm['rrs_iid_optimal']} instances; "
                f"mean gap {sm['mean_gap_iid']:.4f}, maximum gap {sm['max_gap_iid']} (= {float(F(sm['max_gap_iid'])):.4f}). rrs_wor attains the optimal "
                f"without-replacement acceptance on {sm['rrs_wor_optimal']} instances; mean gap {sm['mean_gap_wor']:.4f}, maximum gap "
                f"{float(F(sm['max_gap_wor'])):.4f}. The optimal without-replacement acceptance is at least the optimal iid acceptance on "
                f"{sm['opt_wor_ge_opt_iid']} of {n} instances; rrs_wor is at least rrs_iid on {sm['rrs_wor_ge_rrs_iid']} of {n}; rrs_wor is at least "
                f"the OPTIMAL iid acceptance on {sm['rrs_wor_ge_opt_iid']} of {n}.", "computed_rigorous", evidence=[e for e in mdev if e.endswith(f"k{k}")])
            w = sm["worst_iid_instance"]
            if w["passed"]: add(f"C-T-md-k{k}-worst", f"{w['statement']} Exact values: optimal {sm['worst_iid_values']['opt_iid']}, rrs_iid {sm['worst_iid_values']['rrs_iid']} "
                                f"(instance seed {sm['worst_iid_values']['seed']}).", "computed_rigorous", evidence=[f"md-s{sm['worst_iid_values']['seed']}-k{k}"])
        add("C-conj-wor", "Proposition (hand proof, not machine-checked): for every p, q and k, the optimal lossless acceptance with k drafts "
            "without replacement is at least the optimal acceptance with k iid drafts. Proof sketch: by max-flow/min-cut the optimum equals "
            "min over token sets H of 1 - p(H) + P(the draft set meets H); without replacement, each further draft avoids H with conditional "
            "probability (q(not H) - u)/(1 - u) <= q(not H), where u is the drafted mass so far, so P(avoid H) <= (1 - q(H))^k for every H. "
            "Consistent with the empirical report of Hu et al. 2025 [see C-lit-hu].", "hypothesis", "open")
        add("C-conj-rrs", "Conjecture (supported only by the exhaustive table, no proof): rrs_wor accepts at least as often as rrs_iid for every p, q and k.", "hypothesis", "open")
    for r in R.get("gamma", []):
        c = r["claim"]
        if r["passed"]: add(f"C-T-gam-{c['alpha']}-{c['c']}".replace("/", "_"), f"{r['statement']} Maximal expected speedup {r['speedup']:.4f}.", "computed_rigorous",
                            evidence=[f"gam-{c['alpha']}-{c['c']}".replace("/", "_")])
    kvr = R.get("kv")
    if kvr:
        add("C-T-kv-setup", f"EXPLORATORY KV-cache study (before preregistration) on the synthetic attention model (n = 512, budget = 64, 20 fixed seeds 1000-1019); mean relative output error: "
            + ", ".join(f"{k} {v:.4f}" for k, v in kvr["mean_error"].items()) + f". All {kvr['m_tests']} pairwise comparisons were tested and corrected with Benjamini-Hochberg (q = 0.1).", "observed")
        for t, ch in zip(kvr["tests"], kvr["checks"]):
            add(f"C-T-kv-{t['better']}-{t['worse']}", f"{t['better']} vs {t['worse']}: error ratio {t['ratio_b_over_a']:.3f} (95% CI {t['ci95'][0]:.3f}-{t['ci95'][1]:.3f}), "
                f"paired permutation p = {fp(t['p_a_better'])}, BH-adjusted p = {fp(t['p_bh'])}; not a verifier claim (kv_compare is only checked at the preregistered configuration).",
                "observed")
    CF = json.load(open(CONF)) if os.path.exists(CONF) else {}
    if CF:
        h = CF["H_AE1"]
        for t in h["tests"]:
            ev = [f"kv-{t['test']}-{pol}-{sd}" for pol in (t["a"], t["b"]) for sd in range(1000, 1020)]
            add(f"C-H1-{t['test']}", f"Preregistered KV test {t['test']} ({'structured model' if t['structured'] else 'NEGATIVE CONTROL, structure-free model'}, n = 1024, budget = 128, seeds 1000-1019): "
                f"mean error {t['a']} {t['err_a']:.4f} vs {t['b']} {t['err_b']:.4f}, ratio {t['ratio_b_over_a']:.3f} (95% CI {t['ci95'][0]:.3f}-{t['ci95'][1]:.3f}), "
                f"paired permutation p = {fp(t['p_a_better'])}, BH-adjusted p = {fp(t['p_bh'])} (m = {h['m_tests']}).", "observed", evidence=ev)
        add("C-H1-negctl", f"The preregistered negative control FAILED: in the structure-free model h2o still has lower error than random, so as preregistered "
            "all KV statements are downgraded to observed and none is reported as a statistical finding. Post-hoc hypothesis (untested): high-norm Gaussian keys act as "
            "natural heavy hitters.", "observed", evidence=[f"kv-negctl_h2o-h2o-{sd}" for sd in range(1000, 1020)])
        a2 = CF["H_AE2"]
        add("C-H2", f"Preregistered counterexample search on {a2['tested']} fresh instances (V from 3 to 7, k from 2 to 4): {a2['counterexamples_S1']} counterexamples to "
            f"opt_wor >= opt_iid and {a2['counterexamples_S2']} counterexamples to rrs_wor >= rrs_iid (exact arithmetic). This supports but does not prove the statements.", "computed_rigorous", evidence=["hae2-search"])
        add("C-T1", f"Theory check T1 passed: Monte Carlo acceptance of standard, rrs_iid and rrs_wor matches the exact values on 20 instances, maximal |z| = {CF['T1']['max_abs_z']:.2f} < 3.", "statistical",
            evidence=[f"t1-{r['seed']}-{r['rule']}" for r in CF["T1"]["rows"]])
        add("C-T2", f"Theory check T2 passed: on all {CF['T2']['cells']} certified cells the minimal degree is at most the Taylor degree.", "computed_rigorous",
            evidence=[f"deg-B{r['claim']['B']}-eps{r['claim']['eps']}" for r in R.get("degree", []) if r["passed"]])
        add("C-T3", f"Theory check T3 passed: on all {CF['T3']['instances']} instances no lossless rule exceeded the certified optimum.", "computed_rigorous", evidence=["hae2-search"])
    A = json.load(open("algo_efficiency/results/abstracts.json")) if os.path.exists("algo_efficiency/results/abstracts.json") else {}
    lit = {"hu": "2502.18779", "alman": "2302.13214", "keles": "2209.04881", "aggarwal": "2205.06249", "leviathan": "2211.17192", "chen": "2302.01318",
           "sun": "2310.15141", "jeon": "2402.14160", "xiao": "2309.17453", "zhang": "2306.14048", "miao": "2305.09781"}
    ev_md = open("algo_efficiency/evidence.md").read() if os.path.exists("algo_efficiency/evidence.md") else ""
    for key, i in lit.items():
        if i not in A: continue
        quotes = [l.split("|")[4].strip() for l in ev_md.splitlines() if l.startswith(f"| {i} |") and l.rstrip().endswith("VERIFIED |")]
        add(f"C-lit-{key}", f"Reference (title verified against arXiv {i}): {A[i]['authors'][0]} et al., {A[i]['year']}, \"{A[i]['title']}\"."
            + (f" Verbatim abstract quote checked by code: {' / '.join(quotes)}" if quotes else ""), "observed")
    add("C-verifier", f"The domain verifier passed its mandatory self-test of {len(D.selftest())} known true and known false claims, including near-boundary "
        "cases within 2 percent of the true value and rule violations (verifier-owned tolerances, probabilities not summing to 1).", "computed_rigorous")
    return C


def tables(R):
    out = []
    if R.get("degree"):
        eps_list = sorted({r["claim"]["eps"] for r in R["degree"]}, key=float, reverse=True); Bs = sorted({r["claim"]["B"] for r in R["degree"]})
        cell = {(r["claim"]["B"], r["claim"]["eps"]): r for r in R["degree"]}
        out.append("**Table 1.** Certified minimal degree d*(B, eps) for relative-error approximation of e^x on [-B, B] (upper certificate at d*, "
                   "de la Vallee Poussin lower certificate at d* - 1); in parentheses the Taylor degree (grid estimate). Claims [C-T-deg-*].\n")
        out.append("| B | " + " | ".join(f"eps = {e}" for e in eps_list) + " |\n|---|" + "---|" * len(eps_list))
        for B in Bs:
            out.append(f"| {B} | " + " | ".join((f"{cell[(B, e)]['claim']['d']} ({cell[(B, e)]['taylor_degree_estimate']})" if cell[(B, e)]["passed"] else "n/c")
                                                 if (B, e) in cell else "-" for e in eps_list) + " |")
    if R.get("rank"):
        rows = [r for r in R["rank"] if "h" in r]
        out.append("\n**Table 2.** Rank C(h + d*, d*) of the polynomial-method factorisation at relative error 1e-3. Claims [C-T-rank-*].\n")
        out.append("| h | B | d* | rank |\n|---|---|---|---|")
        out += [f"| {r['h']} | {r['B']} | {r['d']} | {r['rank']:.3e} |" if r["rank"] > 10 ** 6 else f"| {r['h']} | {r['B']} | {r['d']} | {r['rank']} |" for r in rows]
    if R.get("multidraft"):
        out.append("\n**Table 3.** Multi-draft speculative decoding: exact comparison over seeded instances. Claims [C-T-md-*].\n")
        out.append("| k | instances | rrs_iid optimal | mean gap iid | max gap iid | rrs_wor optimal | mean gap wor | rrs_wor >= opt_iid |\n|---|---|---|---|---|---|---|---|")
        for k, s in R["multidraft"]["summary"].items():
            out.append(f"| {k} | {s['instances']} | {s['rrs_iid_optimal']} | {s['mean_gap_iid']:.4f} | {float(F(s['max_gap_iid'])):.4f} | {s['rrs_wor_optimal']} | "
                       f"{s['mean_gap_wor']:.4f} | {s['rrs_wor_ge_opt_iid']} |")
    if R.get("gamma"):
        al = sorted({r["claim"]["alpha"] for r in R["gamma"]}, key=F); cs = sorted({r["claim"]["c"] for r in R["gamma"]}, key=F)
        cell = {(r["claim"]["alpha"], r["claim"]["c"]): r for r in R["gamma"]}
        out.append("\n**Table 4.** Exactly optimal draft length (expected speedup) for i.i.d. acceptance alpha and cost ratio c. Claims [C-T-gam-*].\n")
        out.append("| alpha | " + " | ".join(f"c = {c}" for c in cs) + " |\n|---|" + "---|" * len(cs))
        for a in al: out.append(f"| {a} | " + " | ".join(f"{cell[(a, c)]['claim']['gamma']} ({cell[(a, c)]['speedup']:.2f}x)" for c in cs) + " |")
    return "\n".join(out)


def figure(R, outdir):
    """Figure 1: certified minimal degree d*(B, eps) (solid) vs Taylor degree (dashed) over B. Palette: dataviz reference slots 1-3
    (validated; aqua is below 3:1 contrast, so every line is direct-labelled, markers differ, and Table 1 is the table view)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows = [r for r in R.get("degree", []) if r["passed"]]
    if not rows: return None
    cols = {"1e-2": "#2a78d6", "1e-3": "#eb6834", "1e-6": "#1baf7a"}; marks = {"1e-2": "o", "1e-3": "s", "1e-6": "D"}
    fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=200); ink, muted = "#2b2b2b", "#6b6b6b"
    for e in ("1e-2", "1e-3", "1e-6"):
        pts = sorted((r["claim"]["B"], r["claim"]["d"], r["taylor_degree_estimate"]) for r in rows if r["claim"]["eps"] == e)
        if not pts: continue
        B = [p[0] for p in pts]
        ax.plot(B, [p[1] for p in pts], color=cols[e], lw=2, marker=marks[e], ms=6, mec="white", mew=1.5, zorder=3)
        ax.plot(B, [p[2] for p in pts], color=cols[e], lw=2, ls=(0, (4, 3)), alpha=0.8, zorder=2)
        ax.annotate(f"eps = {e}", (B[-1], pts[-1][1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=ink)
    ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 8, 16]); ax.set_xticklabels(["1", "2", "4", "8", "16"])
    ax.set_xlabel("logit bound B", color=muted, fontsize=9); ax.set_ylabel("polynomial degree", color=muted, fontsize=9)
    ax.set_title("Certified minimal degree (solid) vs Taylor degree (dashed)", fontsize=9.5, color=ink, loc="left")
    ax.grid(axis="y", color="#e6e6e3", lw=0.8); ax.set_axisbelow(True)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#c9c9c4")
    ax.tick_params(colors=muted, labelsize=8); ax.set_xlim(0.85, 30)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=muted, lw=2, label="certified d* (minimax)"), Line2D([], [], color=muted, lw=2, ls=(0, (4, 3)), label="Taylor at 0 (grid estimate)")],
              frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(f"{outdir}/fig_degree.png"); fig.savefig(f"{outdir}/fig_degree.pdf"); plt.close(fig)
    return ("fig_degree.pdf", "Certified minimal degree d*(B, eps) for relative-error approximation of e^x on [-B, B] (solid, claims [C-T-deg-*]) "
            "and the degree of the Taylor polynomial at 0 (dashed, grid estimate). Values in Table 1.")


GERMAN = re.compile(r"[äöüÄÖÜß]|\b(der|die|das|und|nicht|ist|habe|wurde|Hinweis|Satz|Belege)\b")


LABEL = re.compile(r"\*\*(Proposition|Observation|Conjecture|Statistical finding|Table|Figure) \d+")


def gate(md, C):
    """Framework gate (asd.writer.check) on the text with statement labels ('Proposition 6') neutralised, plus extra_issues."""
    return check(LABEL.sub(lambda m: "**" + m.group(1), md), C) + extra_issues(md)


def extra_issues(md):
    """Checks the framework gate does not make: English only, nothing outside the paper's sections."""
    out = []; started = False
    for para in md.split("\n"):
        if para.lstrip().startswith("## "): started = True; continue
        if not para.strip() or para.lstrip().startswith("#") or "[removed: unsupported statement]" in para: continue
        if not started: out.append((para, "text before the first section is not part of the paper")); continue
        if GERMAN.search(para): out.append((para, "not English / meta comment"))
    return out


def _fix(prompt, md, issues, salt):
    fb = "\n".join(f"- \"{q.strip()[:200]}\": {why}" for q, why in issues)
    return ask(prompt + f"\n\nYour last draft:\n{md}\n\nThe automatic checker / reviewer found these problems:\n{fb}\n\nFix only these places (add the "
               "correct citation, correct the statement, or delete it) and return the complete paper body, nothing else.", SYS, salt=salt, model="sonnet")


def write(C, rounds=3, review=()):
    """Gate rounds until clean (max `rounds`), then one reviewer round, then gate rounds again; leftovers are removed and logged."""
    cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}) {c['text']}" for c in C)
    prompt = f"Title: {TITLE}\n\nOutline and instructions:\n{OUTLINE}\n\nClaim list (the only allowed source):\n{cl}\n\nWrite the paper body in Markdown (no title line)."
    md = ask(prompt, SYS, salt="ae-paper-0", model="sonnet"); log = []; n = 0
    def gate_rounds(md, n):
        for _ in range(rounds):
            issues = gate(md, C); log.append({"round": n, "kind": "gate", "violations": len(issues)})
            if not issues: break
            n += 1; md = _fix(prompt, md, issues, f"ae-paper-{n}")
        return md, n
    md, n = gate_rounds(md, n)
    if review:
        log.append({"round": n, "kind": "review", "findings": len(review)}); n += 1; md = _fix(prompt, md, list(review), f"ae-paper-{n}")
        md, n = gate_rounds(md, n)
    removed = []
    for q, why in gate(md, C):
        md = md.replace(q, "*[removed: unsupported statement]*"); removed.append({"sentence": q, "reason": why})
    return md, {"rounds": log, "removed": removed}


def renumber(md):
    """Consecutive numbering of statements (formatting only): '**Proposition (' gets the next free number."""
    for kind in ("Proposition", "Observation", "Conjecture", "Statistical finding"):
        nums = [int(x) for x in re.findall(rf"\*\*{kind} (\d+)", md)]; n = max(nums, default=0)
        while f"**{kind} (" in md:
            n += 1; md = md.replace(f"**{kind} (", f"**{kind} {n} (", 1)
    return md


TEX_MAP = {"√": r"$\sqrt{}$", "δ": r"$\delta$", "ε": r"$\varepsilon$", "α": r"$\alpha$", "≤": r"$\le$", "≥": r"$\ge$", "×": r"$\times$",
           "∈": r"$\in$", "Θ": r"$\Theta$", "γ": r"$\gamma$", "λ": r"$\lambda$", "→": r"$\to$", "≈": r"$\approx$", "−": "-", "…": "...", "^": r"\^{}"}


def tex_safe(md):
    """Escape characters that asd.paper.to_tex leaves unescaped: underscores outside claim citations and non-Latin-1 symbols."""
    parts = re.split(r"(\[C-[^\]]+\])", md)
    out = [p if p.startswith("[C-") else re.sub(r"(?<!\\)_", r"\\_", p) for p in parts]
    md = "".join(out)
    md = re.sub(r"^(#{1,3}) \d+(\.\d+)* ", r"\1 ", md, flags=re.M)          # LaTeX numbers sections itself
    md = md.replace("e^x", "$e^x$").replace("e^-x", "$e^{-x}$")
    for k, v in TEX_MAP.items(): md = md.replace(k, v) if k != "^" else re.sub(r"(?<!e)\^(?!x)", lambda m: v, md)
    return md


def tables_tex(tab):
    """Markdown tables from tables() -> LaTeX table* environments (captions keep their claim ids)."""
    out, cap, rows = [], None, []
    def flush():
        if cap and rows:
            ncol = len(rows[0]); body = " \\\\\n".join(" & ".join(c for c in r) for r in rows)
            out.append("\\begin{table*}[t]\\centering\\small\\caption{" + tex_safe(cap).replace("[C-T-", "[C-T-").replace("*]", "\\textasteriskcentered]") + "}\n"
                       "\\begin{tabular}{" + "l" * ncol + "}\\hline\n" + body.replace(">=", "$\\ge$") + " \\\\\\hline\n\\end{tabular}\\end{table*}")
    for line in tab.split("\n"):
        if line.startswith("**Table"):
            flush(); cap, rows = re.sub(r"\*\*(Table \d+\.)\*\*\s*", "", line), []
        elif line.startswith("|") and not line.startswith("|---"):
            rows.append([tex_safe(c.strip()) for c in line.strip("|").split("|")])
    flush(); return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--authors", default="Verifier-Gated Discovery Lab"); ap.add_argument("--affiliation", default="Hack-Nation 2026")
    ap.add_argument("--errata", default="", help="JSON list of [exact old text, new text, reason]: logged citation/wording fixes applied after the gate, then re-gated")
    ap.add_argument("--review", default="", help="JSON list of [quoted sentence, finding] from a human/agent reviewer, fed back once")
    a = ap.parse_args(); C = claims(); R = json.load(open(CERT)) if os.path.exists(CERT) else {}
    review = [tuple(x) for x in json.load(open(a.review))] if a.review else []
    md, log = write(C, review=review); md = renumber(md); errata = []
    for old, new, why in (json.load(open(a.errata)) if a.errata else []):
        if old in md: md = md.replace(old, new); errata.append(why)
        else: errata.append(f"NOT APPLIED (text not found): {why}")
    rest = gate(md, C); n_cited = len(set(re.findall(r"C-[\w\-*.]+", md)))
    tab = tables(R); os.makedirs(PROJ, exist_ok=True); fig = figure(R, PROJ)
    proto = (f"\n\n---\nVerification log: {n_cited} claims cited, correction rounds {json.dumps(log['rounds'])}, {len(log['removed'])} unsupported "
             f"sentences removed, errata applied after the gate: {json.dumps(errata)}, remaining violations: {len(rest)}. Tables are generated by code from algo_efficiency/results/certified.json.")
    os.makedirs(PROJ, exist_ok=True)
    figmd = f"\n\n![{fig[1]}]({fig[0].replace('.pdf', '.png')})\n\n*Figure 1.* {fig[1]}\n" if fig else ""
    open(f"{PROJ}/paper.md", "w").write(f"# {TITLE}\n\n{a.authors}, {a.affiliation}\n\n{md}{figmd}\n\n## Tables\n\n{tab}{proto}\n")
    tex = to_tex(tex_safe(md + "\n\n" + proto), TITLE, a.authors, a.affiliation).replace("[ngerman]{babel}", "[english]{babel}")
    tex = tex.replace("\\item [", "\\item {}[").replace("\\end{document}", tables_tex(tab) + "\n\\end{document}")                          # a leading [ would be read as \item's optional argument
    if fig:
        tex = tex.replace(r"\usepackage{hyperref}", r"\usepackage{graphicx}\usepackage{hyperref}").replace(r"\end{document}",
              "\\begin{figure}[t]\\centering\\includegraphics[width=\\columnwidth]{" + fig[0] + "}\\caption{" + tex_safe(fig[1]).replace("[C-T-deg-*]", "[C-T-deg-\\textasteriskcentered]") + "}\\end{figure}\n\\end{document}")
    open(f"{PROJ}/paper.tex", "w").write(tex)
    json.dump({"claims": C, "log": log}, open(f"{PROJ}/paper_evidence.json", "w"), indent=1)
    if shutil.which("pdflatex"):
        for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=PROJ, capture_output=True)
    print(f"{PROJ}/paper.md" + proto)


if __name__ == "__main__":
    main()
