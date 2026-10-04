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

OUTLINE = r"""Style: concise ML-theory preprint (6-8 pages), sober, no marketing. Sections:
Abstract (<= 180 words): the question (why do architectures fail at state tracking; circuit complexity says TC0 vs NC1), our answer for one-layer linear RNNs with Householder-product transitions (DeltaNet, DeltaProduct): an exact law h*, the first lower bound on Householder factors per token, the headline instances (A5 with involution inputs needs one reflection; A5 needs two; the S4/A5 formats of the closest prior work need two), the atlas, the preregistered training grid and its outcome, and that every statement is machine-verified or certified.
1 Introduction: architecture debate (Transformers and diagonal SSMs in TC0, non-solvable word problems NC1-complete) from literature claims; the gap (constructions in DeltaProduct/Grazzi/RWKV-7; DeltaProduct's unexpected S4/A5 observation; Howe's representation law; Complex KDA's S5 lower bound under non-expansion, C-ckda-relation, C-lit-ckda-*); contributions as a bullet list, positioned honestly with C-novelty (the exact law for all groups and alphabets, the norm-free compression, the one-reflection A5 result and the atlas are new; S5 = 4 builds on Complex KDA).
2 Setting and definitions: word problem, one-layer realisation, finite-state, transition families, h and h*.
3 Results I (theory): Lemma L1 (machine-checked), Lemma L4 (machine-checked), Lemma L2 (hand proof), L3, Theorem 1 (state 'proof in the companion ledger' and cite C-ledger), diagonal families (L5), abelian cover (L7); explain what is proved how.
4 Results II (certified instances): Table 1 (appended by code); A5 with involutions (H3 cover), A5/all, S4 and A5 in the generator format of prior work, S5, Z2^3; contrast with circuit complexity.
5 Results III (atlas): coverage, own-vs-GAP agreement, non-monotonicity of h with respect to solvability; Figure 2 and Table 3 are appended by code.
6 Results IV (preregistered experiments): (a) H-EX1 grid: protocol, predictors, cell outcomes, accuracy of each predictor, discriminating tests with BH, negative and positive controls; Figure 1 and Table 2. Report learnability failures honestly. (b) H-EX2 addendum: the prior work's own generator formats, Table 4 and Figure 3; state precisely what it supports and what not (it tests a sufficiency prediction against a necessity claim of prior work under our protocol and readout).
7 The agentic lab and the verification pipeline: scout, integrator, cascade, verifier, red team; negative rounds; loopholes found and closed; red-team bugs fixed.
8 Limitations and open questions (finite-state assumption, real states (C-complex), token-local transitions without short convolution, one layer, exact arithmetic vs float, open parameterisations only approximate (C-open-beta), remaining open intervals such as Q8, multi-layer, chain of thought / padding as a Householder budget as a hypothesis, device sensitivity of training (C-H-replication)).
Refer to Tables 1-4 and Figures 1-3 by name only; do not write tables yourself.
Mathematics: write every formula in LaTeX math, inline $...$ (for example $h^*(G,\Sigma)$, $\operatorname{rank}(\rho(t_s)-I)\le k$, $A_5$, $S_4$,
$\mathbb{Z}_2^3$), never as plain ASCII like rank(rho(t_s) - I) <= k. Keep alphabet names (all, involutions, transpositions, tn, c3c5) and
architecture names (hh1, hh2, diag_pm) as plain text. Bold statement labels such as **Lemma L1 (machine-checked).** are fine."""


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
    add("C-L2", "Lemma L2 (compression lemma; proved by hand, not machine-checked; reviewed by two independent red-team agents, the second of "
        "which checked the construction exactly on adversarial instances and found it valid after wording fixes, for real states, affine input "
        "terms, beta in [0, 2] including singular transitions, matrix-valued states and arbitrary readouts; expressivity/analysis/redteam_theory.md): "
        "if a one-layer real recurrence h_t = A(s_t) h_{t-1} + B(s_t) with an arbitrary readout solves the word problem of (G, Sigma) "
        "for every length with finitely many reachable states, and rank(A(s) - I) <= k for every letter, then h*(G, Sigma) <= k. Proof idea: "
        "the reachable states form a finite transformation monoid mapping onto G; an idempotent e of its minimal ideal gives a group eTe mapping "
        "onto G; the compressed maps A(u)A(s) restricted to the column space of the affine span of e(Q) form a faithful representation of a "
        "covering group whose generators satisfy rank(A(u)(A(s) - I)) <= k.", "hypothesis", "open")
    add("C-L3", "Lemma L3 (sufficiency; proved by hand, and re-verified on every concrete instance by the exact verifier): if a finite group H "
        "maps onto G with generating lifts t_s and a faithful real representation rho with rank(rho(t_s) - I) <= k, then an exact finite-state "
        "one-layer realisation with k Householder reflections per token (beta in {0, 2}) exists in dimension dim rho: an H-invariant inner "
        "product makes rho orthogonal, Cartan-Dieudonne factors each rho(t_s) into rank(rho(t_s) - I) reflections, a generic initial state "
        "separates H, and the readout maps rho(x) h_0 to pi(x). It needs beta = 2 exactly with unit keys; with a zero initial state, as in DeltaNet, the "
        "input term v = -c k supplies the offset.", "hypothesis", "open")
    add("C-thm1", "Theorem 1 (from Lemma L2, proved by hand, and Lemma L3): for every finite group G and generating alphabet Sigma, a "
        "finite-state one-layer realisation of the word problem with k Householder factors per token exists if and only if k >= h*(G, Sigma), "
        "where h*(G, Sigma) is the least k for which a finite group H, a surjection pi: H -> G, generating lifts t_s of the letters and a "
        "faithful real representation rho of H exist with rank(rho(t_s) - I) <= k for every letter; h(G, Sigma) denotes the same minimum "
        "restricted to H = G. Hypotheses: real states, finitely many reachable states, transitions depending only on the current token (no short "
        "convolution), one layer, beta allowed to equal 2; requiring the lifts to generate H does not change h*.", "hypothesis", "open")
    add("C-open-beta", "Corollary (proved by hand; found by the theory red team): if beta is confined to [0, 2), as with a sigmoid parameterisation, "
        "no nontrivial group is exactly realisable for any number of factors; likewise open intervals for diagonal entries admit only the trivial "
        "group. Trained models with open parameterisations can therefore only approximate, and the theory's predictions for them concern "
        "approximation; our preregistered protocol uses a parameterisation that reaches beta = 0 and beta = 2 exactly.", "hypothesis", "open")
    add("C-complex", "Remark (theory red team): the law is stated for real states; a complex realisation of complex rank k only gives h* <= 2k "
        "(a 1x1 complex rotation tracks Z3 with complex rank 1, while h*(Z3, all) = 2).", "hypothesis", "open")
    add("C-ledger", "The definitions and the complete written proofs of Lemmas L2, L3, L4, L5, L7 and Theorem 1 are given in the companion ledger "
        "(projects/expressivity/theory_ledger.pdf, built from expressivity/theory.md); the Lean sources of L1 and L4 are in expressivity/lean.", "observed")
    add("C-L5", "Lemma L5 (proved by hand via the compression lemma, not machine-checked; consistent with prior theorems on diagonal SSMs): "
        "a finite-state one-layer realisation exists for diagonal transitions with entries in [0, 1] only for the trivial group, for real "
        "diagonal transitions with entries in [-1, 1] exactly for elementary abelian 2-groups, and for complex diagonal transitions exactly for "
        "abelian groups (closed parameter sets; complex entries of modulus at most 1).", "hypothesis", "open")
    add("C-L7", "Lemma L7 (proved by hand; instances certified): for a nontrivial abelian group h*(G, Sigma) is 1 if every letter is an involution and 2 "
        "otherwise; the upper bound tracks each letter's count modulo its order (count cover), which uses a dimension equal to the number of "
        "involution letters plus twice the number of other letters (an upper bound on the dimension, not the minimum).", "hypothesis", "open")
    add("C-S5", "Result (lower bound by a hand step combined with a published theorem; upper bound certified): h*(S5, all) = 4 under exact finite "
        "reachability. A cover with rank(rho(t_s) - I) <= 3 can be made orthogonal by averaging; rank at most 3 leaves at most one non-real "
        "eigenvalue pair, so it is a single-head, orthogonal, finite-state tracker of S5 of the kind excluded by Theorem 4 of arXiv:2609.24797 "
        "(our step, by hand); the upper bound 4 is the certified permutation construction. The argument only needs an alphabet containing a "
        "5-cycle and a transposition.", "hypothesis", "open")
    add("C-ckda-relation", "Relation to arXiv:2609.24797 (Complex KDA), from a full-text comparison (expressivity/ckda_comparison.md): its "
        "compression passes from finite reachability to a finite group mapping onto S5 via a minimal-norm idempotent word and needs non-expansive "
        "transitions; our Lemma L2 uses the minimal ideal of the transition monoid, needs no norm bound and transfers the rank bound; that paper "
        "proves the S5 minimum of four Householder factors under its assumptions, but defines no invariant like h* and does not state the "
        "one-reflection realisation of A5 with involution inputs.", "observed")
    add("C-novelty", "Novelty check against the literature (expressivity/novelty.md): the exact law h* over covering groups with a fixed alphabet "
        "and the atlas were not found in prior work; the closest notion, minimal generation in codimension k (arXiv:1804.05089), concerns faithful "
        "representations without an alphabet; that a real reflection has order 2 is classical; the compression idea appears for S5 in "
        "arXiv:2609.24797.", "observed")
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
            if c["mean_primary"] is None:
                txt = (f"Grid cell {c['arch']} on {c['group']}/{c['alphabet']}: {c['succ_primary']} of {c['n']} seeds succeed at 2x-4x the longest training "
                       f"length (primary run on the MPS GPU; only the success count survives in the runner log, see prereg addendum 07:00); cell outcome "
                       f"{'success' if c['outcome'] else 'failure'}; our predictor {({True: 'success', False: 'failure', None: 'undetermined'})[c['pred']['ALG']]}.")
            else:
                txt = (f"Grid cell {c['arch']} on {c['group']}/{c['alphabet']} ({c.get('device', 'cpu')}): {c['succ_primary']} of {c['n']} seeds succeed at 2x-4x the "
                       f"longest training length ({c['succ_secondary']} of {c['n']} at 7x-8x); mean accuracy {c['mean_primary']:.3f} (chance {c['chance']:.3f}); "
                       f"in-distribution mean accuracy {c['mean_indist']:.3f}; cell outcome {'success' if c['outcome'] else 'failure'}; our predictor "
                       f"{({True: 'success', False: 'failure', None: 'undetermined'})[c['pred']['ALG']]}.")
            add(cid, txt, "statistical")
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
                   f"{t['acc_ratio']:.2f} (paired bootstrap 95% CI {t['acc_ratio_ci95'][0]:.2f}-{t['acc_ratio_ci95'][1]:.2f}); project criterion "
                   f"(permutation p < 0.05 and CI excluding 1) {'met' if t.get('claude_md_criterion') else 'not met'}" if t.get('paired_perm_p') is not None else "")
                + f"; BH over all 12 tests: adjusted p = {fp(t['p_bh_all'])}, {'significant' if t['bh_all_reject'] else 'not significant'}.", "statistical")
        E = CF.get("H-EX2", {})
        if E.get("cells"):
            add("C-X-protocol", "Preregistered addendum H-EX2 (committed before its runs, prereg.md 2026-10-04 05:00): the closest prior work's generator "
                "formats S4/tn (a transposition and a 4-cycle) and A5/c3c5 (a 3-cycle and a 5-cycle), architectures hh1, hh2, hh3, 20 seeds each, protocol "
                "identical to H-EX1, run on the MPS GPU; predictions: ours hh1 fails and hh2, hh3 succeed; the representation law in the permutation "
                "representation predicts that S4/tn needs 3 and A5/c3c5 needs 4 factors.", "observed")
            for c in E["cells"]:
                add(f"C-X-{c['arch']}-{c['group']}-{c['alphabet']}", f"H-EX2 cell {c['arch']} on {c['group']}/{c['alphabet']}: {c['succ_primary']} of {c['n']} seeds "
                    f"succeed at 2x-4x the longest training length ({c['succ_secondary']} of {c['n']} at 7x-8x); mean accuracy {c['mean_primary']:.3f} (chance "
                    f"{c['chance']:.3f}); in-distribution {c['mean_indist']:.3f}; outcome {'success' if c['outcome'] else 'failure'}; predicted by us: "
                    f"{'success' if c['pred_ALG'] else 'failure'}; predicted by the permutation-representation law: {'success' if c['pred_B4'] else 'failure'}.", "statistical")
            for t in E["tests"]:
                add(f"C-X-{t['test']}", f"H-EX2 test {t['test']} (one-sided Fisher exact): {t['cell']} vs {t['control']}, successful seeds {t['succ']}, p = {fp(t['p'])}, "
                    f"BH-adjusted p = {fp(t['p_bh'])} (m = 3, q = 0.1), {'significant' if t['bh_reject'] else 'not significant'}; supplementary paired permutation "
                    f"p = {fp(t['paired_perm_p'])}, accuracy ratio {t['acc_ratio']:.2f} (95% CI {t['acc_ratio_ci95'][0]:.2f}-{t['acc_ratio_ci95'][1]:.2f}); "
                    f"BH over all 12 tests: adjusted p = {fp(t['p_bh_all'])}, {'significant' if t['bh_all_reject'] else 'not significant'}.", "statistical")
            add("C-X-result", f"H-EX2 outcome: our predictor matches {E['accuracy']['ALG']} of {len(E['cells'])} cells, the permutation-representation law "
                f"matches {E['accuracy']['B4']} of {len(E['cells'])}; preregistered success criterion of H-EX2: {E['success']}.", "statistical")
        rp = [r for r in CF.get("replication_mps_vs_cpu", []) if r.get("cpu_succ") is not None]
        if rp:
            add("C-H-replication", "Device replication (the same protocol and seeds run twice, once on the MPS GPU and once on the CPU, because of a runner "
                "bug, prereg addendum 07:00): " + "; ".join(f"{r['arch']} on {r['group']}/{r['alphabet']}: MPS {r['mps_succ']} of 20, CPU {r['cpu_succ']} of 20"
                for r in rp) + ". Training outcomes can depend strongly on floating-point details of the device.", "statistical")
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
            interp = str(c.get("interpretation_ungeprueft"))
            # the question decides what a number refers to: if it asks about h*, a value backed only by h (faithful) does not answer it
            ans = {"antwort": interp + (" [answer to a question about h*]" if "h*" in c["frage"] else ""), "pruefungen": [p]}
            cons = D.consistent(ans, p)
            if not ok:
                withdrawn += 1
                add(f"C-{c['id']}-withdrawn", f"Lab round {c['runde']}: a claim accepted by the earlier verifier fails the hardened verifier and is withdrawn ({why[:160]}).", "observed")
                continue
            kept += 1
            add(f"C-{c['id']}", f"Lab round {c['runde']}. Question: {to_english(c['frage'], c['id'] + '-q')} Verified result: {D.describe(p)}", "computed_rigorous",
                "contested by red-team counter-check" if c.get("status") == "angefochten" else "confirmed")
            add(f"C-{c['id']}-I", f"Uninspected interpretation by the agent for {c['id']} (not a result; {'consistent' if cons else 'NOT consistent'} with the "
                f"hardened consistency rule): {to_english(c.get('interpretation_ungeprueft'), c['id'] + '-i')}", "hypothesis", "open")
        for j, w in enumerate(s["widerlegt"]): add(f"C-neg{j + 1}", f"Negative result of the lab (no claim passed the verifier and the consistency rule): {to_english(w, f'neg{j}')}", "observed")
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


GERMAN = re.compile(r"\b(und|nicht|der|die|das|wird|gilt|wenn|man|ist|eine|einer|welche|lässt|sich|über|auch|noch|statt|beliebige|Darstellung|Gruppen|Reflektion\w*|genügen|Schranke|untere|obere)\b")


def to_english(text, salt):
    """Lab questions/answers written by the agents in German are translated before they become claims (compliance audit, EX24)."""
    if not GERMAN.search(str(text)): return str(text)
    t = ask(f"Translate into English, faithfully and literally, keeping every symbol, number and group name unchanged. Return only the translation:\n\n{text}",
            "You are a precise scientific translator.", model="sonnet", salt=f"translate-{salt}").strip()
    return t + " (translated from the agent's German)"


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
    if os.path.exists(f"{R}/confirmatory.json") and json.load(open(f"{R}/confirmatory.json")).get("H-EX2", {}).get("cells"):
        E = json.load(open(f"{R}/confirmatory.json"))["H-EX2"]
        out.append("\n**Table 4.** Preregistered addendum H-EX2: the generator formats of the closest prior work. Successful seeds of 20 at 2x-4x "
                   "(7x-8x); predicted outcome by our law (h* = 2 for both tasks) and by the permutation-representation law. Claims [C-X-*].\n")
        out.append("| task | model | seeds 2x-4x | seeds 7x-8x | ours | permutation law |\n|---|---|---|---|---|---|")
        for c in E["cells"]:
            out.append(f"| {c['group']}/{c['alphabet']} | {c['arch']} | {c['succ_primary']} | {c['succ_secondary']} | {'success' if c['pred_ALG'] else 'failure'} | "
                       f"{'success' if c['pred_B4'] else 'failure'} |")
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
    CF = json.load(open(f"{R}/confirmatory.json")) if os.path.exists(f"{R}/confirmatory.json") else {}
    E = CF.get("H-EX2", {}).get("cells", [])
    if E:
        tasks = [("A5", "c3c5", "#2a78d6", "A5: 3-cycle + 5-cycle", 4), ("S4", "tn", "#eb6834", "S4: transposition + 4-cycle", 3)]
        fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.7), dpi=200, sharey=True); fig.patch.set_facecolor(surf)
        for ax, (g, al, col, lab, law) in zip(axs, tasks):
            ax.set_facecolor(surf); cells = {c["arch"]: c for c in E if c["group"] == g and c["alphabet"] == al}
            ks = [1, 2, 3]; vals = [cells[f"hh{k}"]["succ_primary"] if f"hh{k}" in cells else 0 for k in ks]
            ax.bar(ks, vals, width=0.55, color=col, zorder=3)
            for k, v in zip(ks, vals): ax.text(k, v + 0.6, f"{v}/20", ha="center", fontsize=7.5, color=ink)
            ax.axhline(10, color=muted, lw=0.7, ls=(0, (3, 3)), zorder=1)
            ax.axvline(1.5, color=ink, lw=1.0, zorder=2)
            if law <= 3: ax.axvline(law - 0.5, color=muted, lw=1.0, ls=(0, (1, 2)), zorder=2)
            ax.set_xticks(ks); ax.set_xticklabels(["hh1", "hh2", "hh3"], fontsize=7.5, color=muted); ax.set_xlim(0.5, 3.6); ax.set_ylim(0, 23)
            ax.set_title(f"{lab}\nmin. k: ours 2 (solid), perm. law {law}" + (" (dotted)" if law <= 3 else " (> hh3)"), fontsize=7.5, color=ink, loc="left")
            for sp in ("top", "right"): ax.spines[sp].set_visible(False)
            for sp in ("left", "bottom"): ax.spines[sp].set_color("#c9c8c3")
            ax.tick_params(colors=muted, labelsize=7)
        axs[0].set_ylabel("seeds that length-generalise (of 20)", fontsize=7.5, color=muted)
        fig.tight_layout(); p = f"{outdir}/fig_hex2"; fig.savefig(p + ".pdf"); fig.savefig(p + ".png"); plt.close(fig)
        figs.append(("fig_hex2", "Figure 3. Preregistered addendum H-EX2 on the generator formats of the closest prior work: successful seeds (of 20) for one, two "
                     "and three Householder factors per token; solid line: minimum predicted by our law (h* = 2, certified); dotted line: the "
                     "permutation-representation law (3 for S4, 4 for A5); dashed line: the cell-success threshold of 10 seeds. Evidence: claims C-X-hh1/hh2/hh3-<task>, C-X-E1-E3 (Appendix C)."))
    if os.path.exists(f"{R}/atlas.json"):
        rows = [r for r in json.load(open(f"{R}/atlas.json"))["rows"] if not r.get("abelian", True)]
        fig, ax = plt.subplots(figsize=(5.4, 3.2), dpi=200); fig.patch.set_facecolor(surf); ax.set_facecolor(surf)
        from collections import Counter
        for solv, col, lab in [(True, "#2a78d6", "solvable non-abelian"), (False, "#eb6834", "non-solvable (A5)")]:
            cnt = Counter((r["order"], r["h"]) for r in rows if r.get("solvable") == solv)
            xs = [k[0] for k in cnt]; ys = [k[1] for k in cnt]; ss = [14 + 14 * (v - 1) for v in cnt.values()]
            ax.scatter(xs, ys, s=ss if solv else [70] * len(xs), color=col, edgecolor=surf, linewidth=1.2, label=lab,
                       zorder=3 if not solv else 2, marker="o" if solv else "D")
        a5 = next((r for r in rows if not r.get("solvable", True)), None)
        if a5: ax.annotate("A5 (non-solvable): h = h* = 2", (a5["order"], a5["h"]), xytext=(-150, -20), textcoords="offset points", fontsize=7.5, color=ink,
                           arrowprops=dict(arrowstyle="-", color=muted, lw=0.8))
        ax.axhline(2, color=muted, lw=0.8, ls=(0, (3, 3)), zorder=1)
        ax.set_ylim(0.7, 10.6); ax.set_yticks(range(2, 11))
        ax.text(3, 1.6, "dashed: lower bound 2 (Lemma L4, Lean)", fontsize=6.5, color=muted)
        ax.set_xlabel("group order", fontsize=8, color=muted); ax.set_ylabel("faithful h (Householders per token)", fontsize=8, color=muted)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"): ax.spines[sp].set_color("#c9c8c3")
        ax.tick_params(colors=muted, labelsize=7); ax.grid(axis="y", color="#ecebe7", lw=0.6, zorder=0)
        from matplotlib.lines import Line2D
        ax.legend(handles=[Line2D([], [], marker="o", ls="", color="#2a78d6", markersize=6, label="solvable non-abelian (area = number of groups)"),
                           Line2D([], [], marker="D", ls="", color="#eb6834", markersize=6, label="non-solvable (A5)")], fontsize=7, frameon=False, loc="upper left")
        ax.set_title("Householder cost is not ordered by circuit complexity", fontsize=8.5, color=ink, loc="left")
        fig.tight_layout(); p = f"{outdir}/fig_atlas"; fig.savefig(p + ".pdf"); fig.savefig(p + ".png"); plt.close(fig)
        figs.append(("fig_atlas", "Figure 2. Atlas of all non-abelian groups of order at most 63: faithful h against group order (dot area = number of groups with that order and h). "
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


def protect_hstar(md):
    """Outside inline math, write h* as $h^*$ so that Markdown does not read the asterisk as emphasis."""
    parts = re.split(r"(\$[^$]+\$)", md)
    return "".join(p if p.startswith("$") else re.sub(r"\bh\*", r"$h^*$", p) for p in parts)


def pdf_via_pandoc(md_path, authors, affiliation):
    """PDF export with Pandoc + XeLaTeX (skill rigorous-innovation section 5: "PDF per Pandoc"); also writes paper.tex."""
    d = os.path.dirname(md_path); md = open(md_path).read()
    body = md.split("\n", 3)[3] if md.startswith("# ") else md          # title and author line come from the YAML header
    yaml = ("---\n" f"title: \"{TITLE}\"\n" f"author: \"{authors} ({affiliation})\"\n" "date: \"Preprint, 4 October 2026\"\n"
            "mainfont: \"STIX Two Text\"\nmathfont: \"STIX Two Math\"\nfontsize: 10pt\ngeometry: margin=2cm\nlinkcolor: blue\n"
            "header-includes:\n  - \\usepackage{etoolbox}\n  - \\AtBeginEnvironment{longtable}{\\scriptsize}\n---\n\n")
    open(f"{d}/paper_pandoc.md", "w").write(yaml + protect_hstar(body))
    for out in ("paper.tex", "paper.pdf"):
        r = subprocess.run(["pandoc", "paper_pandoc.md", "-s", "-o", out, "--pdf-engine=xelatex", "--resource-path=."], cwd=d, capture_output=True, text=True)
        if r.returncode: print("pandoc", out, r.stderr[-1500:])


SULEMAN = r"""% Team convention (paper-bell, research/admet): preprint form in the style of Suleman 2026. Every numbered statement is traced to its
% verifier claims in Appendix C (claim ids from projects/expressivity/paper_evidence.json). Built by expressivity/write_paper.py.
\documentclass[10pt,twocolumn,a4paper]{article}
\usepackage{fontspec}\setmainfont{STIXGeneral}
\usepackage{amsmath,amssymb}\usepackage{unicode-math}\setmathfont{STIX Two Math}
\usepackage[english]{babel}
\usepackage[a4paper,top=22mm,bottom=24mm,left=17mm,right=17mm,columnsep=7mm]{geometry}
\usepackage{booktabs,longtable,array,calc,graphicx,microtype,fancyhdr,xcolor}
\usepackage[hidelinks]{hyperref}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Preprint (2026)}\fancyhead[R]{\small Team Ninja Turtles: Householder complexity of state tracking}
\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}
\fancypagestyle{first}{\fancyhf{}\fancyfoot[C]{\small\thepage}}
\begin{document}\thispagestyle{first}
\twocolumn[{%
\noindent{\small Preprint}\\[-1pt]{\small Machine Learning; Computational Complexity}\\[14pt]
\begin{center}{\LARGE\bfseries <<TITLE>>}\\[12pt]{\large <<AUTHORS>>}\\[3pt]{\small <<AFFIL>>}\\[8pt]{\small Preprint, October 2026}\end{center}
\vspace{6pt}\begin{quote}\small\noindent\textbf{Abstract}\enspace <<ABSTRACT>>\end{quote}\vspace{10pt}}]
<<BODY>>
<<FLOATS>>
\onecolumn
\appendix
\section{Claim trace (Appendix C)}
Every statement in the text cites claim identifiers in square brackets. The table lists every claim with its evidence level
(proved\_lean: Lean 4 + Mathlib; computed\_rigorous: exact verifier; statistical: preregistered tests; observed; hypothesis: hand
proof or uninspected interpretation) and the start of its canonical text. Full texts: projects/expressivity/paper\_evidence.json;
proofs of the hand-proved lemmas: expressivity/theory.md (companion ledger).
<<TRACE>>
\end{document}
"""


def pandoc_fragment(md):
    md = md.replace("≥", "$\\geq$").replace("≤", "$\\leq$").replace("⊆", "$\\subseteq$").replace("→", "$\\to$")
    r = subprocess.run(["pandoc", "-f", "markdown-implicit_figures", "-t", "latex", "--wrap=preserve", "--shift-heading-level-by=-1"],
                       input=md, capture_output=True, text=True)
    tex = r.stdout
    # longtable does not work in two-column mode: turn pandoc's tables into plain tabulars inside the column
    tex = re.sub(r"\\begin\{longtable\}\[\]\{([^\n]*)\}", lambda m: "\\begin{center}\\scriptsize\\begin{tabular}{" + m.group(1) + "}", tex)
    tex = tex.replace("\\end{longtable}", "\\end{tabular}\\end{center}")
    tex = "\n".join(l for l in tex.split("\n") if not re.match(r"\s*\\(endhead|endfirsthead|endfoot|endlastfoot)\b", l))
    tex = re.sub(r"\\begin\{minipage\}\[[a-z]\]\{[^}]*\}\\(raggedright|centering|raggedleft)\s*", "", tex)
    tex = tex.replace("\\end{minipage}", "")
    return tex


def build_suleman_pdf(md, figs, tab, C, authors, affiliation):
    d = PROJ
    m = re.search(r"^#+\s*Abstract\s*\n+(.*?)(?=\n#+\s)", md, re.S | re.M)
    abstract = m.group(1).strip() if m else ""
    body = md.replace(m.group(0), "") if m else md
    body = "\n".join(l for l in body.split("\n") if not re.match(r"^# ", l))               # the title is set by the template
    body_tex = pandoc_fragment(protect_hstar(body))
    abs_tex = pandoc_fragment(protect_hstar(abstract)).strip()
    floats = "".join("\\begin{figure*}[t]\\centering\\includegraphics[width=0.78\\textwidth]{" + name + ".pdf}\\caption{" +
                     pandoc_fragment(cap.split(". ", 1)[1]).strip() + "}\\end{figure*}\n" for name, cap in figs)
    floats += tables_tex(tab)
    trace_md = "| claim | level | status | canonical text (start) |\n|---|---|---|---|\n" + "\n".join(
        f"| {c['claim_id']} | {c['level']} | {c['status']} | {c['text'][:150].replace('|', '/')}... |" for c in C)
    trace = pandoc_fragment(trace_md)
    trace = trace.replace("\\begin{center}\\scriptsize\\begin{tabular}", "\\begin{scriptsize}\\begin{longtable}").replace("\\end{tabular}\\end{center}", "\\end{longtable}\\end{scriptsize}")
    tex = (SULEMAN.replace("<<TITLE>>", TITLE).replace("<<AUTHORS>>", authors).replace("<<AFFIL>>", affiliation)
           .replace("<<ABSTRACT>>", abs_tex).replace("<<BODY>>", body_tex).replace("<<FLOATS>>", floats).replace("<<TRACE>>", trace))
    open(f"{d}/paper.tex", "w").write(tex)
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "paper.tex"], cwd=d, capture_output=True, text=True)
    errs = [l for l in open(f"{d}/paper.log", errors="replace").read().split("\n") if l.startswith("!")]
    return errs


def renumber(md):
    for kind in ("Proposition", "Observation", "Conjecture", "Statistical finding"):
        n = max([int(x) for x in re.findall(rf"\*\*{kind} (\d+)", md)], default=0)
        while f"**{kind} (" in md:
            n += 1; md = md.replace(f"**{kind} (", f"**{kind} {n} (", 1)
    return md


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--authors", default="Team Ninja Turtles"); ap.add_argument("--affiliation", default="Hack-Nation 2026, Challenge 3 (Agentic Scientific Discovery)")
    ap.add_argument("--errata", default=""); ap.add_argument("--review", default=""); ap.add_argument("--claims-only", action="store_true")
    a = ap.parse_args(); C = claims(); os.makedirs(PROJ, exist_ok=True)
    german = [c["claim_id"] for c in C if GERMAN.search(c["text"].replace("(translated from the agent's German)", ""))]
    if german: print("WARNING: German text left in claims:", german)
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
    errs = build_suleman_pdf(md, figs, tab, C, a.authors, a.affiliation)
    print("LaTeX errors:", errs[:5])
    json.dump({"claims": C, "log": log, "errata": errata, "remaining": [list(x) for x in rest]}, open(f"{PROJ}/paper_evidence.json", "w"), indent=1)
    print(f"{PROJ}/paper.md" + proto)


if __name__ == "__main__":
    main()
