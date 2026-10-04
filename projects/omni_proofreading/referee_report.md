# Referee report (en)

Fixable points addressed in a revision: no (revision failed the checks or nothing fixable)

## 1. Inconsistent and mis-stated bound: e^{-2∆} vs 1/D^2 and the 'open question' framing

The central claim is about η ≥ e^{-2∆}, yet the Hopfield limit is stated as e^{-(n+1)∆}, so a linear chain with one proofreading step (n=1) gives e^{-2∆}. Violations are then reported for 'two-bound-state' networks, which are not the n=1 chain and whose relation to the Hopfield bound is never justified. Nothing in the paper explains why e^{-2∆} is the right benchmark for generic two-bound-state networks, so 'violation' is not shown to be surprising or to contradict any published theorem. Theorem 2 uses 1/D^2 while Theorem 7 uses e^{-2∆}, and the identification is left implicit. The 'Open question' also mentions the 'linear chain with one proofreading step', which is not analysed in the results (only n=2 is).

- Severity: major
- Fixable by rewriting: True
- Suggestion: State explicitly that D=e^∆ so 1/D^2 = e^{-2∆}, justify why this is the relevant benchmark for two-bound-state networks, and clearly delimit what is claimed against the Hopfield bound. Reword the motivation so it does not imply a contradiction of established results.
- Status: open

## 2. Violations depend on an undefined, inconsistent model: the 'rules' are never stated and the rate cap is arbitrary

The model section says networks 'follow the rules in' (a reference that is missing). The edge catalogue, the definition of rule-compliance, the topology generator, the enumeration of the 92 topologies, the meaning of 'fam2_k' labels, the steady-state equations, the definition of JW and JR, and the treatment of fuel/discard edges are not given. The model allows rates only in [e^{-10}, e^{10}] and requires local detailed balance with fuel-driven steps, but whether a state with η~1e-12 relies on this particular construction or on unphysical features (e.g. a discard edge, product removal, unbound-state accounting) cannot be assessed. Results such as η=1.39e-12 for fam2_43 are very extreme compared with the others (1e-5 to 1e-7), and are reported with no rates, no σ, no v, and no explanation. The 'classification' is therefore not reproducible or interpretable from the paper itself.

- Severity: major
- Fixable by rewriting: False
- Suggestion: Add a full formal model definition (states, edge catalogue, rate parametrisation, local detailed balance, steady-state equations, η, v, σ), the generator rules, and a table of topologies with edge lists. Provide the exact rational rates (or an appendix) and σ, v for all 11 violations, with an explanation of why fam2_43 is so extreme.
- Status: open

## 3. Classification is mostly unresolved and the headline is weaker than the title suggests; reporting inconsistencies

Of 88 topologies, 27 (31%) are undecided, so the 'classification' is incomplete. Theorem 5 lists ten topologies and Theorem 4/3 give subsets, so Theorems 3–6 are redundant restatements of one result with inflated theorem count. Theorem 6 merely restates Theorem 2 ('consistency'). The Abstract says 'Hopfield bound ... for n+1' but the introduction and results are inconsistent in framing. Appendix A states 'L2c criterion... 3 in total' and fam2_13 failed with |log k|=10.06, indicating that the search for the open topologies is shallow, not that they truly resist; no attempt is made to prove or disprove them by other means. Also, the 11 violations may exploit a single mechanism, but this is not investigated (open question ii says the discard-edge claim is verified only for fam2_66), so conclusions about mechanism are unsupported. The abstract claim that 'all violation certificates lie in a bounded log-rate range' is a restriction, not a result.

- Severity: major
- Fixable by rewriting: True
- Suggestion: Merge Theorems 3–6 into one theorem with the table, delete redundant statements, rename the title to reflect partial classification, and state plainly that 27 remain open with search-effort details. Remove or qualify any mechanistic claims not shown.
- Status: open

## 4. Trust in the computer-assisted proofs: no independent verification, no interval arithmetic, no reproducible certificates in the paper

Proofs of the bounds (Theorems 1 and 2) rest on the claim that all coefficients of N and D are nonnegative, after symbolic expansion by a trusted but unpublished verifier with an 18-case self-test. The paper gives no explicit polynomial, no description of how the numerator N was constructed (the elimination, the use of D and G as variables, whether ∆ was symbolic or fixed to ln 100), and no independent check. Theorem 1 states η ≥ e^{-3∆} 'for all positive rates and fuel potentials' but the model assumptions specify µ ≥ 0 and rate-range limits, so the domain of validity is unclear. Theorem 2 states the bound for 'at most two bound states' while the main text speaks of exactly two. The check of 'positive coefficients' is sufficient but not necessary, so failures of that test do not mean violations, which is probably why the 27 are open; this should be discussed. The authors also say the exact rational certificates are in a repository, but a reader cannot verify them from the text. The fraction of counter-checks that passed (5 of 29, with 12 not executable) undermines confidence in the verification pipeline.

- Severity: major
- Fixable by rewriting: False
- Suggestion: Include (in an appendix or supplement) explicit rational rates and the full verification outputs for each violation, an outline of the certificate (b) derivation with a small worked example, and an independent re-check (e.g. a second CAS or high-precision numerics). Explain the 5/29 counter-check result and the sufficiency-only nature of the positivity test.
- Status: open

## 5. Weak literature context, overclaimed novelty and unsupported process claims; presentation issues

Novelty is asserted from 'targeted searches of N abstracts' (searching abstracts, not papers) on a single date, which is not evidence of novelty; the 'novelty status: not checked' entries for several theorems are inappropriate in a journal paper. Process material (agentic laboratory, preregistration commit, counter-check statistics, German-named files, provenance table, claim ids) takes much space and substitutes for physical interpretation. There is no discussion of the physical meaning of violating the bound (e.g. relation to the known results of Yu–Kolomeisky–Igoshin on networks with more states, Banerjee et al. on discrimination, or whether the violation relies on high dissipation σ≈8.3 kT with very low speed v~1e-3). Example 15 has v=9e-9, and Figure 1 conflates achievable thresholds with bounds; Figure 1 compares only hopfield_n1 and n2, not the two-bound-state networks. The reference list is short and cites the same paper twice ([5],[6]); the reference to 'the rules in' is dangling, and Appendix A has a stray Example 18 placed after the negative results; the Pareto remark ('jump is an optimizer artefact') is unsupported by data shown. Citing 2026 journal volumes and a 'preprint' from a lab without named authors raises accountability issues.

- Severity: minor
- Fixable by rewriting: True
- Suggestion: Replace the abstract-count novelty statements with a short, honest related-work discussion, drop 'not checked' labels, move process/provenance material to supplementary data, fix dangling references and duplicate citations, move Example 18 into Section 4.3, and add a physical interpretation of the violations including their speed and dissipation cost.
- Status: open
