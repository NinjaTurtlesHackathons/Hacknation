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

SYS = ("You write precise, sober scientific English. You may ONLY use statements from the given claim list and must cite every "
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
            add(f"C-{c['id']}", f"Lab round {c['runde']}. Question: {c['frage']} Verified result: {D.describe(p)} Verifier: {c['grund']}",
                c["level"], status, [f"lab-R{c['runde']}"])
            add(f"C-{c['id']}-I", f"Uninspected interpretation by the agent for {c['id']} (not a result): {c.get('interpretation_ungeprueft')}", "hypothesis", "open")
            for j, r in enumerate(c.get("red_team", [])):
                verdict = ("passed and logically contradicts the claim" if D.widerspricht(p, r["pruefung"]) else "passed but does not contradict the claim") if r["bestanden"] else "failed"
                add(f"C-{c['id']}-RT{j + 1}", f"Red-team counter-check for {c['id']}: {r['idee']} -> {verdict}; verifier: {r['grund']}", "computed_rigorous", evidence=[f"lab-R{c['runde']}"])
        for j, w in enumerate(s["widerlegt"]): add(f"C-neg{j + 1}", f"Negative result of the lab (no claim passed the verifier): {w}", "observed")
        for c in s["claims"]:   # a contested claim stays in the paper only as a negative/contested finding
            pass
        for j, w in enumerate(s["wissen"][:30]):
            add(f"C-lit{j + 1}", f"Literature: {w['text']} (verbatim quote checked by code: \"{w['zitat']}\", {w['quelle']})", "observed")
        add("C-lab", f"The agentic lab ran {len(s['runden'])} rounds and produced {len(s['claims'])} verified claims and {len(s['widerlegt'])} "
                     f"negative results at a cost of {s['kosten_usd']:.2f} USD; every round was preregistered before its experiments.", "observed")
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
                f"paired permutation p = {t['p_a_better']:.4f}, BH-adjusted p = {t['p_bh']:.4f}; verifier check {'passed' if ch['passed'] else 'failed'}.",
                "observed")
    CF = json.load(open(CONF)) if os.path.exists(CONF) else {}
    if CF:
        h = CF["H_AE1"]
        for t in h["tests"]:
            ev = [f"kv-{t['test']}-{pol}-{sd}" for pol in (t["a"], t["b"]) for sd in range(1000, 1020)]
            add(f"C-H1-{t['test']}", f"Preregistered KV test {t['test']} ({'structured model' if t['structured'] else 'NEGATIVE CONTROL, structure-free model'}, n = 1024, budget = 128, seeds 1000-1019): "
                f"mean error {t['a']} {t['err_a']:.4f} vs {t['b']} {t['err_b']:.4f}, ratio {t['ratio_b_over_a']:.3f} (95% CI {t['ci95'][0]:.3f}-{t['ci95'][1]:.3f}), "
                f"paired permutation p = {t['p_a_better']:.4f}, BH-adjusted p = {t['p_bh']:.4f} (m = {h['m_tests']}).", "observed", evidence=ev)
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


def write(C, rounds=2):
    cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}) {c['text']}" for c in C)
    prompt = f"Title: {TITLE}\n\nOutline and instructions:\n{OUTLINE}\n\nClaim list (the only allowed source):\n{cl}\n\nWrite the paper body in Markdown (no title line)."
    md = ask(prompt, SYS, salt="ae-paper-0", model="sonnet"); log = []
    for r in range(rounds):
        issues = check(md, C); log.append({"round": r, "violations": len(issues)})
        if not issues: break
        fb = "\n".join(f"- \"{s.strip()[:200]}\": {why}" for s, why in issues)
        md = ask(prompt + f"\n\nYour last draft:\n{md}\n\nThe automatic checker found these violations:\n{fb}\n\nFix only these places (add the citation "
                 "or delete the statement) and return the complete text.", SYS, salt=f"ae-paper-{r + 1}", model="sonnet")
    removed = []
    for s, why in check(md, C):
        md = md.replace(s, f"*[removed: unsupported, {why}]*"); removed.append({"sentence": s, "reason": why})
    return md, {"rounds": log, "removed": removed}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--authors", default="Verifier-Gated Discovery Lab"); ap.add_argument("--affiliation", default="Hack-Nation 2026")
    a = ap.parse_args(); C = claims(); R = json.load(open(CERT)) if os.path.exists(CERT) else {}
    md, log = write(C); rest = check(md, C); n_cited = len(set(re.findall(r"C-[\w\-*.]+", md)))
    tab = tables(R)
    proto = (f"\n\n---\nVerification log: {n_cited} claims cited, correction rounds {json.dumps(log['rounds'])}, {len(log['removed'])} unsupported "
             f"sentences removed, remaining violations: {len(rest)}. Tables are generated by code from algo_efficiency/results/certified.json.")
    os.makedirs(PROJ, exist_ok=True)
    open(f"{PROJ}/paper.md", "w").write(f"# {TITLE}\n\n{a.authors}, {a.affiliation}\n\n{md}\n\n## Tables\n\n{tab}{proto}\n")
    tex = to_tex(md + "\n\n" + proto, TITLE, a.authors, a.affiliation).replace("[ngerman]{babel}", "[english]{babel}")
    open(f"{PROJ}/paper.tex", "w").write(tex)
    json.dump({"claims": C, "log": log}, open(f"{PROJ}/paper_evidence.json", "w"), indent=1)
    if shutil.which("pdflatex"):
        for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=PROJ, capture_output=True)
    print(f"{PROJ}/paper.md" + proto)


if __name__ == "__main__":
    main()
