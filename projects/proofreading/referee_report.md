# Referee report (en)

Fixable points addressed in a revision: no (revision failed the checks or nothing fixable)

## 1. Counterexamples rest on an unverifiable, unexplained model and inconsistent edge definitions

The fam2_66 counterexample (eta = 5.08e-07, far below e^{-2Δ} = 1e-4, nearly three orders of magnitude lower) is a striking claim, yet the paper gives no rates, no network diagram, no fuel potentials, and no explanation of the mechanism. The edge description (binding to C0, fuel-driven C0->C1, fuel-driven discard from C1, product from C1) is too terse to reproduce by hand. The network has a fuel-driven discard from the product-forming state, which together with the 'rule' that a discriminating edge is only allowed bound->unbound and cycle affinities arise only from µ, µP, makes it unclear whether local detailed balance is truly satisfied. Also the theorem statement (η ≤ 1e-4, v ≥ 1e-4) is much weaker than the values quoted, and the text speaks of 'two bound states' but the counterexample is described with C0, C1 only. Theorems 5 and 6 are unclear: for fam2_9 and fam2_11 no values of eta, sigma, v, or rates are reported at all.

- Fixable by rewriting: False
- Suggestion: Provide the full rate tables (rational values), µ and µP, the graph for each of the three counterexamples, an explicit calculation of η, v, σ that a reader can check independently, and a physical interpretation of why the bound fails. This requires adding data from the certificates, not just rewording.
- Status: open

## 2. Classification is incomplete (35 of 88 open) and the headline claim overstates it

The title and abstract promise an 'exact classification of 88 topologies', but 35 (40%) are unresolved with the reason 'unknown'. The paper also admits that the 5-counterexample success criterion was missed. The counterexample for the bound is only certified for log-rates in [-10,10] and Δ = ln 100, so the 'proved' bounds are for all rates yet the counterexamples are range-restricted, making the dichotomy asymmetric. The 3+50 split could shift with other rate ranges or Δ. Without any analysis of the open cases (e.g., which of them are numerically below or above the bound), the classification is a partial sorting.

- Fixable by rewriting: True
- Suggestion: Retitle and reword the abstract and contributions to 'partial classification'. Report, from existing optimiser output, what numerical scans show for the 35 open topologies (labelled numerical), and state structural features distinguishing proved, refuted, and open sets.
- Status: open

## 3. Proofs are computer-assisted black boxes with no human-checkable content or structural insight

Theorem 1 and 4 rely on N/D polynomial quotients (1374 and 2048 terms) having nonnegative coefficients, with no explicit polynomial, no indication of variable substitutions (how reverse rates, detailed balance and fuel factors enter, and how rates bounded in [e^-10, e^10] are handled), and no sanity check that the exact expressions are correct. 'Nonnegative coefficients' is sufficient but not necessary, so the 35 open cases may merely reflect a method failure. Theorem 4 does not even say which 50 topologies are proved; theorem 1 is 'qualitatively a reproduction' of Hopfield's bound, and the proved bound for n=2 is e^{-3Δ}, while the sharper claim for n=2 is not discussed. The trusted base (verifier code, 18 self-test cases) is not described, and the red-team record (4 passed, 8 failed, 10 not executable) undermines confidence.

- Fixable by rewriting: False
- Suggestion: Include the explicit rate parametrisation, a derivation of η as a rational function, a hand-checkable proof for the smallest case, an independent verification (e.g. a different CAS), the list of the 50 proved topologies, and an explanation of the red-team failures.
- Status: open

## 4. Internal inconsistencies, redundant results and presentation errors

Theorem numbering differs between the text and provenance table; garbled labels ('fam26 6', 'fam29 andf am21 1'); Table 2 has an empty 'Source' column; Table 1 duplicates Figure 2. Propositions 7 and 8 (3 topologies each) are subsumed by Theorem 4 and add nothing; Proposition 8 is about a necessity question it does not decide. Lemma 9 and Proposition 10 merely restate verifier outputs and are not mathematical statements. Theorem 3's 'Certificate' paragraph refers vaguely to 'the three theorems below'. The 'at most 10 states' and the 'at most two bound states' wording is inconsistent with 'exactly two bound states'. Appendix A says 11 verified statements and 1 negative result but the main text lists many more. The discussion says 'high dissipation can favour speed' citing [6] without support. Example 13 has v ~ 9e-9, a physically negligible speed, so its significance is doubtful. Several numbers (σ = 8.34 kT) are given without noting how the entropy production per product is defined for topologies with discard.

- Fixable by rewriting: True
- Suggestion: Fix numbering and labels, delete or merge redundant propositions and the 'Lemma', fill in the Source column, harmonise 'exactly/at most two bound states', define σ precisely, and reconcile counts of statements.
- Status: open

## 5. Weak novelty and literature positioning, and overclaimed relevance of the 'abstract searches'

Novelty is asserted via 'not found in a targeted search of N abstracts' for each statement, which is not a valid novelty argument (abstract-level search of a few dozen papers, and the paper itself says the Hopfield bound reproduction and chain examples are qualitatively known). Closely related work (Wong–Amir–Gunawardena on energy-speed-accuracy, Yu–Kolomeisky–Igoshin, Banerjee et al. on anti-proofreading, Chiuchiu et al. on Pareto fronts) is cited only in passing and the paper does not state how a violation of e^{-2Δ} with two bound states relates to known results that errors can go below the Hopfield limit when discrimination is applied to several steps or when rates are unbounded. The motivation (why e^{-2Δ} is the right benchmark for networks that are not the Hopfield chain) is missing, and the counterexamples at v ~ 1e-3 are not related to any speed-accuracy-dissipation tradeoff. The agentic-laboratory framing (roles named sparsam, numeriker, etc.) occupies space but does not support scientific claims.

- Fixable by rewriting: True
- Suggestion: Remove per-statement 'not found in search' novelty claims; add a proper related-work discussion comparing with Wong et al. and Yu et al., justify e^{-2Δ} as the benchmark, discuss the physical consequences of the violation (speed, dissipation) using the data already present, and shorten the lab-process description to a brief methods note.
- Status: open
