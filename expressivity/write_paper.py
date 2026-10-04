"""English paper for the expressivity domain, built only from verified claims (framework rules: no sentence without claim_id,
no number that is not in a cited claim, no reference without a code-checked source).

Sources: theory (Lean proofs, hand proofs reviewed by the red team), certified table (results/certified.json, every entry passed
DOMAIN.check), atlas (results/atlas.json, own character tables agreeing with GAP), preregistered confirmatory grid
(results/confirmatory.json), the agentic lab (projects/expressivity/state.json, every stored claim RE-CHECKED with the hardened
verifier and consistency rule), literature (results/citations.tsv + code-checked verbatim quotes), red team (analysis/redteam.md).
Prose: LLM under the hallucination gate (asd.writer.check), reviewer round, logged errata; tables and figures by code.
  python -m expressivity.write_paper --authors "..." --affiliation "..." [--review expressivity/review.json] [--errata expressivity/errata.json]
"""
import argparse, json, os, re, shutil, subprocess

from asd.llm import ask
from asd.writer import check as gate_check
from asd.paper import to_tex
from .domain import DOMAIN as D

PROJ = "projects/expressivity"; R = "expressivity/results"
TITLE = "How Many Householders Does State Tracking Need? An Exact Law for One-Layer Linear RNNs That Circuit Complexity Does Not Predict"

SYS = ("You write precise, sober scientific English for a machine-learning theory preprint. Return ONLY the paper body (Markdown): "
       "no notes, comments or explanations addressed to the reader or to the checker, in any language. You may ONLY use statements "
       "from the given claim list and must cite every statement with its claim_id in square brackets, e.g. [C-T-A5-involutions]. Never "
       "write a number (digits) that does not appear verbatim in a cited claim; write small counts as words only if they are not results. "
       "No references other than those inside claims. Claims with level 'hypothesis' may only be presented as hand proofs (say "
       "'proved by hand, not machine-checked'), conjectures or the agents' uninspected interpretations, never as machine-verified results. "
       "Claims with level 'proved_lean' may be called machine-checked. Use 'Theorem' only for the combination stated in C-thm1.")

OUTLINE = """Style: concise ML-theory preprint (6-8 pages), sober, no marketing. Sections:
Abstract (<= 180 words): the question (why do architectures fail at state tracking; circuit complexity says TC0 vs NC1), our answer for one-layer linear RNNs with Householder-product transitions (DeltaNet, DeltaProduct): an exact law h*, the first lower bound on Householder factors per token, the headline instances (A5 with involution inputs needs one reflection; A5 needs two; the S4/A5 formats of the closest prior work need two), the atlas, the preregistered training grid and its outcome, and that every statement is machine-verified or certified.
1 Introduction: architecture debate (Transformers and diagonal SSMs in TC0, non-solvable word problems NC1-complete) from literature claims; the gap (prior work gives only constructions; DeltaProduct's unexplained S4/A5 observation; Howe's representation law); contributions as a bullet list.
2 Setting and definitions: word problem, one-layer realisation, finite-state, transition families, h and h*.
3 Results I (theory): Lemma L1 (machine-checked), Lemma L4 (machine-checked), Lemma L2 (hand proof), L3, Theorem 1, diagonal families (L5), abelian cover (L7); explain what is proved how.
4 Results II (certified instances): Table 1 (appended by code); A5 with involutions (H3 cover), A5/all, S4 and A5 in the generator format of prior work, S5, Z2^3; contrast with circuit complexity.
5 Results III (atlas): coverage, own-vs-GAP agreement, non-monotonicity of h with respect to solvability; Figure 2 and Table 3 are appended by code.
6 Results IV (preregistered experiments): protocol, predictors, cell outcomes, accuracy of each predictor, discriminating tests with BH, negative and positive controls; Figure 1 and Table 2 are appended by code. Report learnability failures honestly.
7 The agentic lab and the verification pipeline: scout, integrator, cascade, verifier, red team; negative rounds; loopholes found and closed; red-team bugs fixed.
8 Limitations and open questions (finite-state assumption, token-local transitions without short convolution, one layer, exact arithmetic vs float, open intervals such as S5/all, multi-layer, chain of thought / padding as a Householder budget as a hypothesis).
Refer to Tables 1-3 and Figures 1-2 by name only; do not write tables yourself."""


def fp(p): return f"{p:.1e}" if p < 1e-3 else f"{p:.3f}"


def claims():
    C = []

    def add(cid, text, level, status="confirmed"):
        C.append({"claim_id": cid, "text": text, "level": level, "status": status})

    # ---------------- theory
    add("C-L1", "Lemma L1 (machine-checked in Lean 4 with Mathlib, theorems rank_prod_sub_one_le and deltaproduct_rank_le): if R_1, ..., R_k "
        "have rank at most one, then rank(prod_i (I + R_i) - I) <= k; in particular a token transition made of k generalized Householder "
        "factors I - beta u u^T differs from the identity by rank at most k. Negative control: the strengthened bound k - 1 is refuted in "
        "Lean (strengthened_bound_false); all theorems use only the standard axioms propext, Classical.choice and Quot.sound.", "proved_lean")
    add("C-L4", "Lemma L4 (machine-checked in Lean 4 with Mathlib, theorems sq_eq_one_of_rank_le_one_of_pow_eq_one and "
        "no_single_householder_lift): a real matrix of finite order with rank(M - I) <= 1 is an involution; hence if rho is a faithful real "
        "representation of a finite group H, pi: H -> G a homomorphism and pi(t) = s with s of order at least 3, then rank(rho(t) - I) > 1. "
        "Consequence: h*(G, Sigma) >= 2 whenever the alphabet contains a letter of order at least 3, even when a larger covering group is used.",
        "proved_lean")
    add("C-L2", "Lemma L2 (compression lemma; proved by hand, not machine-checked; reviewed by an independent red-team agent, which "
        "found it valid for finite-state realisations, including affine input terms, beta in [0, 2], matrix-valued states and singular "
        "transitions): if a one-layer recurrence h_t = A(s_t) h_{t-1} + B(s_t) with an arbitrary readout solves the word problem of (G, Sigma) "
        "for every length with finitely many reachable states, and rank(A(s) - I) <= k for every letter, then h*(G, Sigma) <= k. Proof idea: "
        "the reachable states form a finite transformation monoid mapping onto G; an idempotent e of its minimal ideal gives a group eTe mapping "
        "onto G; the compressed maps A(u)A(s) restricted to the column space of the affine span of e(Q) form a faithful representation of a "
        "covering group whose generators satisfy rank(A(u)(A(s) - I)) <= k.", "hypothesis", "open")
    add("C-L3", "Lemma L3 (sufficiency; proved by hand, and re-verified on every concrete instance by the exact verifier): if a finite group H "
        "maps onto G with generating lifts t_s and a faithful real representation rho with rank(rho(t_s) - I) <= k, then an exact finite-state "
        "one-layer realisation with k Householder reflections per token (beta in {0, 2}) exists in dimension dim rho: an H-invariant inner "
        "product makes rho orthogonal, Cartan-Dieudonne factors each rho(t_s) into rank(rho(t_s) - I) reflections, a generic initial state "
        "separates H, and the readout maps rho(x) h_0 to pi(x).", "hypothesis", "open")
    add("C-thm1", "Theorem 1 (from Lemma L2, proved by hand, and Lemma L3): for every finite group G and generating alphabet Sigma, a "
        "finite-state one-layer realisation of the word problem with k Householder factors per token exists if and only if k >= h*(G, Sigma), "
        "where h*(G, Sigma) is the least k for which a finite group H, a surjection pi: H -> G, generating lifts t_s of the letters and a "
        "faithful real representation rho of H exist with rank(rho(t_s) - I) <= k for every letter; h(G, Sigma) denotes the same minimum "
        "restricted to H = G.", "hypothesis", "open")
    add("C-L5", "Lemma L5 (proved by hand via the compression lemma, not machine-checked; consistent with prior theorems on diagonal SSMs): "
        "a finite-state one-layer realisation exists for diagonal transitions with entries in [0, 1] only for the trivial group, for real "
        "diagonal transitions with entries in [-1, 1] exactly for elementary abelian 2-groups, and for complex diagonal transitions exactly for "
        "abelian groups.", "hypothesis", "open")
    add("C-L7", "Lemma L7 (proved by hand; instances certified): for an abelian group h*(G, Sigma) is 1 if every letter is an involution and 2 "
        "otherwise; the upper bound tracks each letter's count modulo its order (count cover), which needs a dimension equal to the number of "
        "involution letters plus twice the number of other letters.", "hypothesis", "open")
    add("C-L6", "Computation of h (standard character theory): codim Fix rho(g) = dim rho - (1/|g|) sum_j chi_rho(g^j), codimensions add over "
        "direct sums, and a sum of real irreducible representations is faithful iff their kernels intersect trivially; h(G, Sigma) is therefore "
        "a finite optimisation over the real character table.", "observed")
    # ---------------- certified table
    cert = json.load(open(f"{R}/certified.json")) if os.path.exists(f"{R}/certified.json") else {"rows": []}
    for r in cert["rows"]:
        if not r["all_passed"]: add(f"C-T-{r['group']}-{r['alphabet']}-fail", f"Certification incomplete for {r['group']} / {r['alphabet']}.", "observed"); continue
        stm = " ".join(c["statement"] for c in r["checks"] if c["passed"] and c["claim"]["typ"] in ("realisation", "hstar_value", "hstar_lower", "h_faithful"))
        diag = "; ".join(c["statement"] for c in r["checks"] if c["claim"]["typ"] == "diag_realisable")
        add(f"C-T-{r['group']}-{r['alphabet']}".replace("^", "p"),
            f"Certified ({r['group']}, alphabet '{r['alphabet']}', order {r['order']}, {r['letters']} letters, {'solvable' if r['solvable'] else 'non-solvable'}): "
            f"lower bound {r['lower']}, best certified realisation k = {r['upper']} via {r['upper_construction']} (covering group of order "
            f"{r['upper_H_order']}, dimension {r['upper_dim']}), faithful h = {r['h_faithful']}, permutation-representation cost {r['perm_law']}"
            f"{', h* determined exactly' if r['exact'] else ', h* not determined (bounds differ)'}. {stm} {diag}", "computed_rigorous")
    add("C-verifier", f"The domain verifier passed its mandatory self-test of {len(D.selftest())} known true and known false claims (near-boundary "
        "cases such as the same matrices without the sign lift, k one below the certified value, rule violations, and regressions for every bug "
        "found by the red team).", "computed_rigorous")
    # ---------------- atlas
    if os.path.exists(f"{R}/atlas.json"):
        A = json.load(open(f"{R}/atlas.json")); s = A["summary"]; rows = A["rows"]
        nonab = [r for r in rows if not r.get("abelian", True)]; solv_nonab = [r for r in nonab if r.get("solvable")]
        add("C-atlas", f"Atlas over all {s['groups']} groups of order at most {s['N']} (GAP SmallGroups library), full alphabet: own numerical "
            f"character tables and GAP's exact tables give the same faithful h for every group ({len(s['disagreements_own_vs_gap'])} "
            f"disagreements). h* is determined exactly for {s['exact']} of {s['groups']} groups ({s['nonabelian_exact']} of {s['nonabelian']} "
            f"non-abelian groups; every abelian group by Lemma L7).", "computed_rigorous")
        ns = [r for r in rows if not r.get("solvable", True)]
        add("C-atlas-nonsolvable", f"In the atlas the only non-solvable group is {', '.join(r['name'] for r in ns)} (order "
            f"{', '.join(str(r['order']) for r in ns)}), with faithful h = {', '.join(str(r['h']) for r in ns)} and h* = "
            f"{', '.join(str(r['hstar']) for r in ns)} determined exactly.", "computed_rigorous")
        ge3 = [r for r in solv_nonab if r["h"] >= 3]
        add("C-atlas-monotone", f"Non-monotonicity: {len(ge3)} of the {len(solv_nonab)} solvable non-abelian groups of order at most {s['N']} have "
            f"faithful h >= 3, i.e. every faithful representation of them needs more Householder factors per token than the non-solvable A5 "
            f"(h = 2); the largest faithful h in the atlas is {max(r['h'] for r in rows)} ({max(rows, key=lambda r: r['h'])['name']}). For h* these "
            f"groups have certified bounds [2, upper] only, so a strict separation in h* is not claimed.", "computed_rigorous")
        tw = [r for r in nonab if r.get("twist", 99) < r["h"]]
        add("C-atlas-twist", f"Sign lifts to G x Z2 (multiply a letter's matrix by -1) lower the certified upper bound below the faithful h for "
            f"{len(tw)} of the {len(nonab)} non-abelian groups.", "computed_rigorous")
        from collections import Counter
        dist = sorted(Counter(r["h"] for r in nonab).items())
        add("C-atlas-dist", "Distribution of faithful h over the non-abelian groups of the atlas (value: number of groups): " +
            ", ".join(f"{k}: {v}" for k, v in dist) + ".", "computed_rigorous")
    # ---------------- confirmatory grid
    if os.path.exists(f"{R}/confirmatory.json"):
        CF = json.load(open(f"{R}/confirmatory.json"))
        add("C-H-protocol", "Preregistered protocol (prereg.md, committed before the first confirmatory run): one-layer models diag_pos, diag_pm, "
            "hh1, hh2, hh3, hh4 (DeltaNet/DeltaProduct with beta in [0, 2]) and an LSTM, 64-dimensional state, MLP readout, 20 seeds "
            "(1000-1019) per cell, 3000 steps, length curriculum 8 to 64 and a final stage at 128; a seed succeeds if its token accuracy on "
            "positions 257-512 of length-512 sequences is at least 0.9; a cell succeeds if at least 10 of 20 seeds succeed; 9 tasks x 7 "
            "architectures.", "observed")
        for c in CF["cells"]:
            cid = f"C-G-{c['arch']}-{c['group']}-{c['alphabet']}".replace("^", "p")
            add(cid, f"Grid cell {c['arch']} on {c['group']}/{c['alphabet']}: {c['succ_primary']} of {c['n']} seeds succeed at 2x-4x the longest "
                f"training length ({c['succ_secondary']} of {c['n']} at 7x-8x); mean accuracy {c['mean_primary']:.3f} (chance {c['chance']:.3f}); "
                f"in-distribution mean accuracy {c['mean_indist']:.3f}; cell outcome {'success' if c['outcome'] else 'failure'}; our predictor "
                f"{ {True: 'success', False: 'failure', None: 'undetermined'}[c['pred']['ALG']] }.", "statistical")
        acc = CF["accuracy"]
        names = {"ALG": "our algebraic predictor", "B1_circuit": "circuit class (solvable)", "B2_abelian": "abelian", "B3_size": "group size",
                 "B4_perm_law": "representation law in the permutation representation", "B5_faithful": "faithful representations only"}
        add("C-H-accuracy", "Agreement of each predictor with the cell outcomes on the determined cells: " +
            "; ".join(f"{names[k]} {v['correct']} of {v['cells']}" for k, v in acc.items()) + ".", "statistical")
        for t in CF["tests"]:
            add(f"C-H-{t['test']}", f"Preregistered test {t['test']} ({'negative control, random targets' if t.get('negative_control') else 'one-sided Fisher exact test'}): "
                f"cell {t['cell']}" + (f" vs control {t['control']}" if t.get("control") else "") + f", successful seeds {t['succ']}, p = {fp(t['p'])}, "
                f"Benjamini-Hochberg adjusted p = {fp(t['p_bh'])} (m = {len(CF['tests'])}, q = 0.1), {'significant' if t['bh_reject'] else 'not significant'}"
                + (f"; supplementary paired permutation test on per-seed accuracies p = {fp(t['paired_perm_p'])}, ratio of mean accuracies "
                   f"{t['acc_ratio']:.2f} (paired bootstrap 95% CI {t['acc_ratio_ci95'][0]:.2f}-{t['acc_ratio_ci95'][1]:.2f})" if 'paired_perm_p' in t else "") + ".", "statistical")
        g = CF["gates"]
        add("C-H-gates", f"Preregistered success criteria: accuracy beats every baseline: {g['H-EX1.1_accuracy_beats_all_baselines']}; all six "
            f"discriminating tests significant after BH: {g['H-EX1.2_discriminating_tests_BH']}; negative control clean: {g['negative_control_clean']}; "
            f"H-EX1 overall: {g['H-EX1_success']}.", "statistical")
    # ---------------- lab (every stored claim re-checked with the hardened verifier)
    if os.path.exists(f"{PROJ}/state.json"):
        s = json.load(open(f"{PROJ}/state.json")); kept = withdrawn = 0
        for c in s["claims"]:
            p = c.get("pruefung") or {}
            ok, why, _ = D.check(p)
            ans = {"antwort": c.get("interpretation_ungeprueft"), "pruefungen": [p]}
            cons = D.consistent(ans, p)
            if not ok:
                withdrawn += 1
                add(f"C-{c['id']}-withdrawn", f"Lab round {c['runde']}: a claim accepted by the earlier verifier fails the hardened verifier and is withdrawn ({why[:160]}).", "observed")
                continue
            kept += 1
            add(f"C-{c['id']}", f"Lab round {c['runde']}. Question: {c['frage']} Verified result: {D.describe(p)}", "computed_rigorous",
                "contested by red-team counter-check" if c.get("status") == "angefochten" else "confirmed")
            add(f"C-{c['id']}-I", f"Uninspected interpretation by the agent for {c['id']} (not a result; {'consistent' if cons else 'NOT consistent'} with the "
                f"hardened consistency rule): {c.get('interpretation_ungeprueft')}", "hypothesis", "open")
        for j, w in enumerate(s["widerlegt"]): add(f"C-neg{j + 1}", f"Negative result of the lab (no claim passed the verifier and the consistency rule): {w}", "observed")
        add("C-lab", f"The agentic lab (literature scout with code-checked quotes, integrator, cascade of four researcher agents, exact verifier, "
            f"red-team agent, per-round preregistration) ran {len(s['runden'])} rounds at a cost of {s['kosten_usd']:.2f} USD: {len(s['claims'])} rounds "
            f"produced an accepted claim ({kept} survive re-checking with the hardened verifier, {withdrawn} withdrawn) and {len(s['widerlegt'])} rounds "
            f"produced a negative result; the scout kept {len(s['wissen'])} literature findings whose verbatim quote was found by code in the abstract.", "observed")
    add("C-loophole1", "Loophole found in lab round 1 and closed: an agent answered 'no' (one reflection is not enough for A5 with involution "
        "inputs) and backed it with two true but weaker checks; the verifier had refuted the agent's claim h* = 2 by finding a certificate with "
        "k = 1 itself; the consistency rule now requires an impossibility certificate for negative answers and exact-value checks for numbers.", "observed")
    add("C-redteam", "An independent red-team agent (read and execute only) found three bugs: group names S1, D1, D2 denoted wrong groups "
        "(one false sentence each could be printed), the published h* sentence omitted the finite-state hypothesis, and the consistency rule "
        "accepted unchecked numbers in answer texts; all three were fixed and turned into regression cases. It confirmed the exact core: 189 library "
        "constructions and 15556 exhaustive explicit-matrix claims against an independent re-implementation and character tables of all 319 "
        "SmallGroups against GAP gave 0 disagreements.", "observed")
    # ---------------- literature (title verified by code; verbatim quote checked by code against the abstract or the HTML full text)
    lit = literature()
    for k, v in lit.items(): add(f"C-lit-{k}", v, "observed")
    return C


def literature():
    out = {}
    tsv = {l.split("\t")[4]: l.split("\t") for l in open(f"{R}/citations.tsv").read().splitlines()[1:]} if os.path.exists(f"{R}/citations.tsv") else {}
    ev = open("expressivity/scout_evidence.md").read().splitlines()
    want = {"merrill-tc0": "arXiv:2207.00729", "illusion": "arXiv:2404.08819", "grazzi": "arXiv:2411.12537", "deltaproduct": "arXiv:2502.10297",
            "rwkv7": "arXiv:2503.14456", "sarrof": "arXiv:2405.17394", "shakerinava": "arXiv:2603.01959", "howe": "arXiv:2609.18966",
            "liu": "arXiv:2210.10749", "cot": "arXiv:2310.07923", "hahn": "arXiv:1906.06755", "deletang": "arXiv:2207.02098", "li-cot": "arXiv:2402.12875"}
    for key, rid in want.items():
        row = tsv.get(rid)
        if not row or not row[0].startswith("VERIFIED"): continue
        quote = next((l.split("|")[4].strip() for l in ev if l.startswith(f"| {rid} |")), "")
        qtxt = f" Verbatim abstract quote checked by code: {quote}" if row[0] == "VERIFIED" and quote else ""
        out[key] = f"Reference ({rid}, title verified by code against arXiv): \"{row[6]}\".{qtxt}"
    bq = f"{R}/body_quotes.json"
    if os.path.exists(bq):
        for key, q in json.load(open(bq)).items():
            if q.get("verified"): out[key + "-body"] = f"Reference {q['id']} (full-text quote checked by code against the arXiv HTML): \"{q['quote']}\""
    row = tsv.get("doi:10.1016/0022-0000(89)90037-8")
    if row and row[0].startswith("VERIFIED"): out["barrington"] = f"Reference (doi:10.1016/0022-0000(89)90037-8, title verified by code against Crossref): \"{row[6]}\" (Barrington)."
    return out


def write(C, review=(), rounds=3):
    cl = "\n".join(f"- [{c['claim_id']}] ({c['level']}, {c['status']}) {c['text']}" for c in C)
    prompt = f"Title: {TITLE}\n\nOutline and instructions:\n{OUTLINE}\n\nClaim list (the only allowed source):\n{cl}\n\nWrite the paper body in English, in Markdown."
    md = ask(prompt, SYS, model="opus", salt="expressivity-paper-0", timeout=1800); log = []
    if review:
        fb = "\n".join(f"- \"{q}\": {f}" for q, f in review)
        md = ask(prompt + f"\n\nYour draft:\n{md}\n\nA reviewer found these problems:\n{fb}\n\nFix exactly these and return the full text.", SYS, model="opus",
                 salt="expressivity-paper-review", timeout=1800)
    for r in range(rounds):
        issues = gate(md, C); log.append({"round": r, "violations": len(issues)})
        if not issues: break
        fb = "\n".join(f"- \"{s.strip()[:200]}\": {why}" for s, why in issues)
        md = ask(prompt + f"\n\nYour last draft:\n{md}\n\nThe automatic checker found these violations:\n{fb}\n\nFix only these places (add the "
                 "correct citation or delete the statement) and return the complete text.", SYS, model="opus", salt=f"expressivity-paper-fix-{r}", timeout=1800)
    issues = gate(md, C); removed = []
    for s, why in issues:
        md = md.replace(s, f"*[removed: unsupported - {why}]*"); removed.append({"sentence": s, "reason": why})
    log.append({"final_removed": len(removed)})
    return md, {"rounds": log, "removed": removed}


def gate(md, C):
    """Framework gate plus English/meta check: German words or notes to the checker are violations."""
    issues = gate_check(re.sub(r"\*\*(Lemma|Theorem|Proposition|Observation|Statistical finding|Conjecture) [\dA-Z.]+\*\*", "", md), C)
    for line in md.split("\n"):
        if re.search(r"\b(und|nicht|der|die|das|wird|Prüf|Anmerkung)\b", line) and not line.startswith("#"):
            issues.append((line.strip()[:200], "German text"))
    return issues


def tables():
    out = []
    cert = json.load(open(f"{R}/certified.json")) if os.path.exists(f"{R}/certified.json") else {"rows": []}
    if cert["rows"]:
        out.append("**Table 1.** Certified one-layer Householder complexity (exact verifier). lower: certified lower bound (Lemma L4 for 2); "
                   "upper: best exact realisation found by the verifier (construction / sign twist, covering-group order |H|, dimension d); h: faithful "
                   "representations of G only (own and GAP character tables); perm: cost in the permutation representation (the representation law of "
                   "prior work). Claims [C-T-*].\n")
        out.append("| G | alphabet | order | solvable | lower | upper | construction | abs(H) | d | h | perm |\n|---|---|---|---|---|---|---|---|---|---|---|")
        for r in cert["rows"]:
            out.append(f"| {r['group']} | {r['alphabet']} | {r['order']} | {'yes' if r['solvable'] else 'no'} | {r['lower']} | {r['upper']} | "
                       f"{r['upper_construction']} | {r['upper_H_order']} | {r['upper_dim']} | {r['h_faithful']} | {r['perm_law']} |")
    if os.path.exists(f"{R}/confirmatory.json"):
        CF = json.load(open(f"{R}/confirmatory.json")); archs = ["diag_pos", "diag_pm", "hh1", "hh2", "hh3", "hh4", "lstm"]
        idx = {(c["arch"], c["group"], c["alphabet"]): c for c in CF["cells"]}
        tasks = []
        for c in CF["cells"]:
            if (c["group"], c["alphabet"]) not in tasks: tasks.append((c["group"], c["alphabet"]))
        out.append("\n**Table 2.** Preregistered grid: successful seeds out of 20 (accuracy >= 0.9 on positions 257-512 of length-512 sequences); "
                   "mark: predicted success (+), predicted failure (-), undetermined (?) by our predictor. Claims [C-G-*].\n")
        out.append("| task | " + " | ".join(archs) + " |\n|---|" + "---|" * len(archs))
        sym = {True: "+", False: "-", None: "?"}
        for g, a in tasks:
            out.append(f"| {g}/{a} | " + " | ".join((f"{idx[(ar, g, a)]['succ_primary']} {sym[idx[(ar, g, a)]['pred']['ALG']]}" if (ar, g, a) in idx else "n/a") for ar in archs) + " |")
    if os.path.exists(f"{R}/atlas.json"):
        A = json.load(open(f"{R}/atlas.json")); rows = A["rows"]
        out.append(f"\n**Table 3.** Atlas, all {A['summary']['groups']} groups of order <= {A['summary']['N']}, full alphabet. Claims [C-atlas*].\n")
        out.append("| class | groups | h* exact | faithful h = 2 | faithful h >= 3 |\n|---|---|---|---|---|")
        for name, sel in [("abelian", lambda r: r.get("abelian", True) and r["order"] > 1), ("solvable non-abelian", lambda r: r.get("solvable") and not r.get("abelian", True)),
                          ("non-solvable", lambda r: not r.get("solvable", True))]:
            rr = [r for r in rows if sel(r)]
            out.append(f"| {name} | {len(rr)} | {sum(r['exact'] for r in rr)} | {sum(r['h'] == 2 for r in rr)} | {sum(r['h'] >= 3 for r in rr)} |")
    return "\n".join(out)


def figures(outdir):
    """Figure 1: grid heatmap (sequential blue ramp of the dataviz reference palette, every cell labelled, Table 2 = table view).
    Figure 2: atlas, faithful h vs order (two series: solvable blue, non-solvable orange; validated palette, direct label)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    ink, muted, surf = "#0b0b0b", "#52514e", "#fcfcfb"; figs = []
    if os.path.exists(f"{R}/confirmatory.json"):
        CF = json.load(open(f"{R}/confirmatory.json")); archs = ["diag_pos", "diag_pm", "hh1", "hh2", "hh3", "hh4", "lstm"]
        tasks = []
        for c in CF["cells"]:
            if (c["group"], c["alphabet"]) not in tasks: tasks.append((c["group"], c["alphabet"]))
        idx = {(c["arch"], c["group"], c["alphabet"]): c for c in CF["cells"]}
        M = np.array([[idx[(a, g, al)]["succ_primary"] if (a, g, al) in idx else np.nan for a in archs] for g, al in tasks])
        cmap = LinearSegmentedColormap.from_list("blue", ["#f3f7fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
        fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200); fig.patch.set_facecolor(surf); ax.set_facecolor(surf)
        ax.imshow(M, cmap=cmap, vmin=0, vmax=20, aspect="auto")
        for i, (g, al) in enumerate(tasks):
            for j, a in enumerate(archs):
                c = idx.get((a, g, al))
                if not c: continue
                pr = {True: "+", False: "−", None: "?"}[c["pred"]["ALG"]]
                ax.text(j, i, f"{c['succ_primary']}{pr}", ha="center", va="center", fontsize=7.5, color="white" if c["succ_primary"] >= 11 else ink)
        ax.set_xticks(range(len(archs))); ax.set_xticklabels(archs, fontsize=7.5, color=muted)
        ax.set_yticks(range(len(tasks))); ax.set_yticklabels([f"{g} / {al}" for g, al in tasks], fontsize=7.5, color=muted)
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.set_xticks(np.arange(-.5, len(archs)), minor=True); ax.set_yticks(np.arange(-.5, len(tasks)), minor=True)
        ax.grid(which="minor", color=surf, linewidth=2); ax.tick_params(which="both", length=0)
        ax.set_title("Seeds (of 20) that length-generalise; + / − / ? = our predicted outcome", fontsize=8.5, color=ink, loc="left")
        fig.tight_layout(); p = f"{outdir}/fig_grid"; fig.savefig(p + ".pdf"); fig.savefig(p + ".png"); plt.close(fig)
        figs.append(("fig_grid", "Figure 1. Preregistered grid: number of seeds (out of 20) whose accuracy on positions 257-512 is at least 0.9, with the "
                     "outcome predicted by the algebraic law (+ success, − failure, ? undetermined). Table 2 is the table view. Claims [C-G-*]."))
    if os.path.exists(f"{R}/atlas.json"):
        rows = [r for r in json.load(open(f"{R}/atlas.json"))["rows"] if not r.get("abelian", True)]
        fig, ax = plt.subplots(figsize=(5.4, 3.2), dpi=200); fig.patch.set_facecolor(surf); ax.set_facecolor(surf)
        rng = np.random.default_rng(0)
        for solv, col, lab in [(True, "#2a78d6", "solvable non-abelian"), (False, "#eb6834", "non-solvable (A5)")]:
            rr = [r for r in rows if r.get("solvable") == solv]
            ax.scatter([r["order"] for r in rr], [r["h"] + rng.uniform(-0.12, 0.12) for r in rr], s=18 if solv else 60, color=col, edgecolor=surf,
                       linewidth=1.2, label=lab, zorder=3 if not solv else 2, marker="o" if solv else "D")
        a5 = next((r for r in rows if not r.get("solvable", True)), None)
        if a5: ax.annotate("A5: h = h* = 2", (a5["order"], a5["h"]), xytext=(-70, 22), textcoords="offset points", fontsize=7.5, color=ink,
                           arrowprops=dict(arrowstyle="-", color=muted, lw=0.8))
        ax.axhline(2, color=muted, lw=0.8, ls=(0, (3, 3)), zorder=1)
        ax.text(1, 2.1, "lower bound for every group with an element of order >= 3 (Lemma L4)", fontsize=6.5, color=muted)
        ax.set_xlabel("group order", fontsize=8, color=muted); ax.set_ylabel("faithful h (Householders per token)", fontsize=8, color=muted)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"): ax.spines[sp].set_color("#c9c8c3")
        ax.tick_params(colors=muted, labelsize=7); ax.grid(axis="y", color="#ecebe7", lw=0.6, zorder=0)
        ax.legend(fontsize=7, frameon=False, loc="upper left")
        ax.set_title("Householder cost is not ordered by circuit complexity", fontsize=8.5, color=ink, loc="left")
        fig.tight_layout(); p = f"{outdir}/fig_atlas"; fig.savefig(p + ".pdf"); fig.savefig(p + ".png"); plt.close(fig)
        figs.append(("fig_atlas", "Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h (jittered vertically) against group order. "
                     "The only non-solvable group, A5, sits at the minimum value 2 while most solvable groups need more. Claims [C-atlas-monotone], [C-atlas-nonsolvable]."))
    return figs


TEX_MAP = {"≤": r"$\le$", "≥": r"$\ge$", "×": r"$\times$", "∈": r"$\in$", "→": r"$\to$", "−": "-", "…": "...", "ρ": r"$\rho$", "π": r"$\pi$",
           "Σ": r"$\Sigma$", "β": r"$\beta$", "√": r"$\sqrt{}$", "⊆": r"$\subseteq$", "≈": r"$\approx$", "λ": r"$\lambda$", "τ": r"$\tau$"}


def tex_safe(md):
    parts = re.split(r"(\[C-[^\]]+\])", md)
    md = "".join(p if p.startswith("[C-") else re.sub(r"(?<!\\)_", r"\\_", p) for p in parts)
    md = re.sub(r"^(#{1,3}) \d+(\.\d+)*\.? ", r"\1 ", md, flags=re.M)
    md = re.sub(r"h\*", r"h$^*$", md)
    md = md.replace("^", r"\^{}").replace(r"h$\^{}*$", "h$^*$")
    for k, v in TEX_MAP.items(): md = md.replace(k, v)
    return md


def tables_tex(tab):
    out, cap, rows = [], None, []
    def flush():
        if cap and rows:
            ncol = len(rows[0]); body = " \\\\\n".join(" & ".join(c for c in r) for r in rows)
            out.append("\\begin{table*}[t]\\centering\\small\\caption{" + tex_safe(cap).replace("*]", "\\textasteriskcentered]") + "}\n"
                       "\\begin{tabular}{" + "l" * ncol + "}\\hline\n" + body + " \\\\\\hline\n\\end{tabular}\\end{table*}")
    for line in tab.split("\n"):
        if line.startswith("**Table"):
            flush(); cap, rows = re.sub(r"\*\*(Table \d+\.)\*\*\s*", "", line), []
        elif line.startswith("|") and not line.startswith("|---"):
            rows.append([tex_safe(c.strip()) for c in line.strip("|").split("|")])
    flush(); return "\n".join(out)


def renumber(md):
    for kind in ("Proposition", "Observation", "Conjecture", "Statistical finding"):
        n = max([int(x) for x in re.findall(rf"\*\*{kind} (\d+)", md)], default=0)
        while f"**{kind} (" in md:
            n += 1; md = md.replace(f"**{kind} (", f"**{kind} {n} (", 1)
    return md


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--authors", default="Verifier-Gated Discovery Lab"); ap.add_argument("--affiliation", default="Hack-Nation 2026")
    ap.add_argument("--errata", default=""); ap.add_argument("--review", default=""); ap.add_argument("--claims-only", action="store_true")
    a = ap.parse_args(); C = claims(); os.makedirs(PROJ, exist_ok=True)
    json.dump(C, open(f"{PROJ}/paper_claims.json", "w"), indent=1)
    if a.claims_only: print(len(C), "claims"); return
    review = [tuple(x) for x in json.load(open(a.review))] if a.review else []
    md, log = write(C, review=review); md = renumber(md); errata = []
    for old, new, why in (json.load(open(a.errata)) if a.errata else []):
        if old in md: md = md.replace(old, new); errata.append(why)
        else: errata.append(f"NOT APPLIED (text not found): {why}")
    rest = gate(md, C); n_cited = len(set(re.findall(r"C-[\w\-*.]+", md)))
    tab = tables(); figs = figures(PROJ)
    proto = (f"\n\n---\nVerification log: {n_cited} claims cited, correction rounds {json.dumps(log['rounds'])}, {len(log['removed'])} unsupported "
             f"sentences removed, errata applied after the gate: {json.dumps(errata)}, remaining violations: {len(rest)}. Tables and figures are generated by code "
             f"from expressivity/results/.")
    figmd = "".join(f"\n\n![{cap}]({name}.png)\n\n*{cap}*\n" for name, cap in figs)
    open(f"{PROJ}/paper.md", "w").write(f"# {TITLE}\n\n{a.authors}, {a.affiliation}\n\n{md}{figmd}\n\n## Tables\n\n{tab}{proto}\n")
    tex = to_tex(tex_safe(md + "\n\n" + proto), TITLE, a.authors, a.affiliation).replace("[ngerman]{babel}", "[english]{babel}")
    tex = tex.replace("\\item [", "\\item {}[").replace(r"\usepackage{hyperref}", r"\usepackage{graphicx}\usepackage{hyperref}")
    figtex = "".join("\\begin{figure*}[t]\\centering\\includegraphics[width=0.8\\textwidth]{" + name + ".pdf}\\caption{" + tex_safe(cap.split('. ', 1)[1]).replace("*]", "\\textasteriskcentered]") + "}\\end{figure*}\n" for name, cap in figs)
    tex = tex.replace("\\end{document}", figtex + tables_tex(tab) + "\n\\end{document}")
    open(f"{PROJ}/paper.tex", "w").write(tex)
    json.dump({"claims": C, "log": log, "errata": errata, "remaining": [list(x) for x in rest]}, open(f"{PROJ}/paper_evidence.json", "w"), indent=1)
    if shutil.which("pdflatex"):
        for _ in range(2): subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=PROJ, capture_output=True)
    print(f"{PROJ}/paper.md" + proto)


if __name__ == "__main__":
    main()
