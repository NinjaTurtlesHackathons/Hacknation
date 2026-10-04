# Referee report (en)

Fixable points addressed in a revision: no (revision failed the checks or nothing fixable)

## 1. Bound threshold e^{-2Δ} is inconsistent: the text says it equals 1e-4, yet the table violations are inconsistent with the theorems' stated threshold, and the 'bound' is not the Hopfield bound

With Δ = ln 100, e^{-2Δ} = 1e-4 and e^{-3Δ} = 1e-6. Theorems 2-4 certify only η ≤ 1e-4, not η < 1e-4, so as stated they do not strictly refute η ≥ e^{-2Δ}. The table values (e.g., 2.0e-05) are below 1e-4, but the theorem statements should say strict inequality. The abstract and introduction frame this as a violation of the Hopfield bound e^{-(n+1)Δ}. For k=2 bound states that bound is e^{-3Δ}, and the Hopfield chain obeys it (Theorem 5). The claim that 'the Hopfield bound' is broken is therefore misleading: 1e-4 is a different, stronger conjecture, and several violators (e.g., 4.1e-07, 1.4e-12) are indeed below e^{-3Δ} = 1e-6, which would be a genuinely stronger claim that the paper never discusses explicitly. Also, fam2_43 with η = 1.4e-12 is far beyond any plausible bound and suggests a degenerate or boundary regime that needs scrutiny.

- Severity: major
- Fixable by rewriting: True
- Suggestion: State thresholds numerically and with strict inequalities, separate e^{-2Δ} from e^{-3Δ}, and explicitly report which violators also break e^{-3Δ}. Explain the fam2_43 value (0 net-flux limit, rate range edge, vanishing JR).
- Status: open

## 2. Internal inconsistencies in counts and theorem statements

Theorem 4 says '10 topologies' but lists 10 names including fam2_9 and fam2_11, while fam2_66 is omitted and the text says it 'adds eight' to Theorem 3. The union of Theorems 2-4 gives 11 only if fam2_66 is counted separately; this is never stated cleanly. Theorem 1 has no statement, only 'The bound is therefore violated by these 11 networks'. Theorem 1's certificate says counts were 'recomputed from confirmed claims by the classification script', which is circular. Proposition 2 duplicates Theorem 6. Proposition 1 (3 topologies) is superseded and adds noise. The workflow section says '2 found in round 12, 3 in total' for counterexamples while the paper claims 11. The summary bullet for Theorem 2 says η = 5.082802e-07 while the abstract quotes 1.386398e-12 as the minimum, which is fine, but the workflow numbers contradict the 11. Theorem 2 requires v ≥ 1e-4 but Theorems 3 and 4 do not require any speed, so many violations may be at vanishing throughput.

- Severity: major
- Fixable by rewriting: True
- Suggestion: Write Theorem 1 as an actual statement (50+11+27=88 with explicit lists), remove duplicates and superseded propositions, fix the Theorem 4 list, reconcile the round-12 counts, and report v and σ for every violator in Table 1.
- Status: open

## 3. Classification of the family is not defined or reproducible from the paper itself

The 88 'admissible' topologies come from an 'edge catalogue of the model' that is never given. Which edges, what a 'fuel-driven discard' is, how four are judged degenerate, how topologies are counted up to isomorphism, and whether fam2_k labels are meaningful are all undescribed. Table 1's 'Source' column (proofreading-R12 etc.) refers to internal run IDs. The rate-model (how Δ enters, how W vs R rates relate, how products are formed, how μ and μP enter detailed balance) is only sketched. No topology is drawn, except a verbal description of fam2_66. The reader cannot verify any claim or understand which structural feature matters. The ‘one unbound state’ and ‘at most 10 states’ constraints are also not tied to the k=2 family.

- Severity: major
- Fixable by rewriting: False
- Suggestion: Add a precise model definition (graph, rate parametrization, η, σ, v formulas), draw all 11 violating and representative proved topologies, and give the rational rate vectors in an appendix or data file. This requires new material, not just rewriting.
- Status: open

## 4. Validity of the violation certificates is not independently established; the trusted base is the authors' own verifier

Violations rest on an unpublished verifier with an 18-case self-test, and the paper offers no analytic or independent reproduction for even one case. The reader is pointed to a GitHub repository. Rates are limited to [e^-10, e^10], and fam2_13 failed with |log k|=10.06, which shows boundary sensitivity. Rounding to denominator ≤ 1e6 can interact with the window. Local detailed balance and the definition of η (a ratio of steady-state fluxes, JW/JR for the same network with different rate constants) must be checked for each point, but no rates are reported. The red-team record (29 checks, only 5 passed, 12 failed, 12 not executable) is mentioned but not interpreted. The unexplained discrepancy with the 'reported jump of the front' and with the independent n=2 search (ηmin = 3.1e-5 at σ = 2665) remains in the Discussion without resolution. An unconstrained-dissipation-limit argument might also give arbitrarily small η.

- Severity: major
- Fixable by rewriting: False
- Suggestion: Publish all rate vectors with a minimal independent script (e.g., a few lines of sympy/fractions) that recomputes η for fam2_66, and, if possible, provide an analytic mechanism explaining the violation. Report the red-team outcomes and resolve the stated contradictions.
- Status: open

## 5. Weak scientific contribution and interpretation; 27 open cases, no mechanism; presentation issues

The headline claim is partial: 27 of 88 remain unresolved, so the classification is incomplete, and no structural criterion or mechanism is identified (the paper itself says the discard-exit hypothesis is not established). A proof that e^{-3Δ} holds for only the linear chain n=2 is a reproduction of Hopfield. Novelty statements ('not found in a targeted search of 48 abstracts') are weak evidence and inappropriate in a physics paper. Section 6 mixes discussion with workflow logs (agent names, rounds, preregistration commits), and Example 1-4 results for hopfield_n1 are tangential. Counter-checks are described confusingly (e.g., the claimed attempt to prove η ≥ 1.2e^{-2Δ}). The figures referenced are not explained, the abstract duplicates the summary list, and the authorship/affiliation (single email, AI-generated text) is not credible for a journal submission. The unusual 'Eleven exactly certified' framing overstates what 'exact' guarantees given that model assumptions drive the result.

- Severity: minor
- Fixable by rewriting: True
- Suggestion: Cut novelty-search statements, workflow logs and tangential examples. Reframe as a computational exploration with 11 certified counterexamples and an open classification, clearly separating certified facts from conjecture, and state the physical meaning of the violations (e.g., which driving or discard step reduces η) with the evidence already present.
- Status: open
