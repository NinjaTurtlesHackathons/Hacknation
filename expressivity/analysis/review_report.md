# Referee report: "How Many Householders Does State Tracking Need?"

Reviewed: `projects/expressivity/paper.md`, checked against `projects/expressivity/paper_claims.json` (the only admissible sources), plus `theory.md`, `ckda_comparison.md`, `novelty.md`, `prereg.md` and `results/confirmatory.json`. The missing LSTM cells are ignored, as instructed. Itemised findings with exact quotes are in `expressivity/review.json` (25 items, most important first).

## Summary

The paper defines $h^*(G,\Sigma)$: the minimal per-letter rank defect $\operatorname{rank}(\rho(t_s)-I)$ over faithful real representations of finite covering groups. It claims (Theorem 1, hand-proved) that $h^*$ is exactly the number of Householder factors per token that a real, finite-state, token-local one-layer linear RNN needs.

- **Machine-checked parts.** Two Lean lemmas: L1 (rank of a product of $k$ factors) and L4 (order $\ge 3$ forces $\ge 2$ factors).
- **Hand-proved parts.** The compression lemma L2, the sufficiency lemma L3, and the theorem itself.
- **Instances and atlas.** Certified instances (for example $h^*(A_5,\text{inv})=1$ and $h^*(A_5,\text{all})=2$), and an atlas over 319 groups.
- **Experiments.** Two preregistered training experiments. Both failed their preregistered criteria.

The theory is clearly stated, and its machine-checked and hand-proved parts are labelled consistently in the body. The numbers match the claims file. The main weaknesses are in how the experimental failures are reported, especially in the abstract, and in some positioning against prior work.

## Major issues

1. **The abstract under-reports the failures.** It reports 42/52 and "criterion not met". It omits:
   - that the permutation-representation law (45/52) and faithful-only (43/52) baselines beat the predictor;
   - that H-EX2's preregistered criterion is False;
   - that the flagship one-reflection $A_5$/involutions cell and all $A_5$/all cells were not learned (0/20);
   - the device sensitivity (18/20 vs 0/20).

   The abstract is also 190 words, over the 180-word limit.
2. **The error list is incomplete.** The predictor has 10 errors, but only 9 learnability failures are listed. hh4 on $S_5$/all (predicted success, 0/20) is missing, so the sentence "Its errors are the learnability failures listed above" is false as written.
3. **A preregistered secondary outcome is missing.** The 7x–8x outcome is unreported for H-EX1. Several headline successes collapse there: diag_pm $\mathbb Z_2^3$ 20→0, hh3 $\mathbb Z_2^3$ 20→0, hh4 $A_5$/inv 20→0, hh2 $S_3$/all 19→1. Table 4 reports this metric for H-EX2 but Table 2 does not report it for H-EX1, which is inconsistent.
4. **The test results are interpreted too favourably.**
   - D5's significance rests on an MPS run whose per-seed data were overwritten. The CPU replication of the same cell gave 0/20.
   - The significant tests D4–D6 do not separate the predictor from the representation baselines. The tests that do (D1–D3) were all non-significant.
   - "Clearly beats" the circuit baseline is untested.
   - D2 is mislabelled as targeting the one-reflection result.
5. **Positioning against prior work needs fixes.**
   - "None of these results gives the minimal number..." is uncited and contradicted by Complex KDA ($S_5$ = 4) and by Howe.
   - Howe's law is quoted without "that length-generalizes" and without its "input only through orthogonal transitions" setting. Our zero-initial-state construction uses the additive pathway that Howe excludes.
   - "L2 replaces the norm-minimal word" implies that L2 strictly generalises Complex KDA. The full-text comparison says neither result contains the other (CKDA keeps spectra and handles heads and gating). C-ckda-relation should be extended before the paper says this.
   - Extending the $S_5$ bound to the tn alphabet is our hand reading of CKDA's proof, not their theorem.
   - The upper bound 2 for the $S_4$/$A_5$ formats is DeltaProduct's SO(3) construction and should be credited.
6. **Some proof-status labels are overstated.**
   - The abstract says "every instance value is certified" and cites C-verifier and C-redteam. Lower bounds use hand-proved L2, and $h^*(S_5,\text{all})=4$ is a hand step, not certified.
   - $S_5$ = 4 is listed under "Certified instances".
   - The title says "exact law" for a hypothesis-level theorem.
   - The abstract omits the real-state, token-local and $\beta=2$ hypotheses. The $\beta=2$ hypothesis is decisive by C-open-beta.

## Minor issues

- Notation clash: the state $h_t$ and the invariants $h$, $h^*$ share a symbol. $h^*$ is used in the introduction before it is defined.
- The Deletang result is misstated ("other networks often fail" on regular tasks).
- Table 3 does not add up to 319 groups / 138 exact (rows give 318 / 137; abelian row 62+42 ≠ 105).
- The hand-proof list in Limitations omits L3 and the open-beta corollary.
- Several statements are over-generalised: "symmetric groups with transpositions", and the diagonal-family sentences that cite two claims for all instances.
- Supplementary permutation results are reported selectively (D3 only, not D1).
- The deviation from the preregistered m = 9 is not stated.
- The "contested" rounds conflict with "0 withdrawn".
- Some H-EX2 bullets have no claim id. H-EX2 ran on MPS while most H-EX1 cells ran on CPU, a device confound that is not mentioned.
- Meta text and structure:
  - the title is duplicated;
  - figure captions contain claim-id text and refer to an "Appendix C" that does not exist;
  - figures and tables are out of order (Figure 1, 3, 2; Table 1, 2, 4, 3);
  - a trailing verification log remains;
  - "abs(H)" appears as a column header;
  - some math is plain text in captions and tables.
- The chain-of-thought hypothesis cites a literature claim for our own conjecture.

## Verdict

**Major revision.** The theory, its proof-status labelling in the body, and the atlas are sound relative to the claims. The positioning against Complex KDA is mostly fair. The paper is not yet acceptable because:

- the abstract does not show the experimental failures prominently;
- one predictor error is omitted;
- the preregistered secondary outcome is missing;
- D5 is reported as significant without its replication caveat;
- several prior-work comparisons (Howe, CKDA, DeltaProduct) are stated less precisely than the claims allow.

All of these can be fixed in the text without new experiments.
