# Final referee review

Reviewed: `projects/expressivity/paper.md` (final text), checked against `projects/expressivity/paper_claims.json`, and against the earlier review (`expressivity/analysis/review_report.md`, `expressivity/review.json`). Small fixes are in `expressivity/errata.json` (20 items, each with its exact old text, which occurs once in the paper).

## Verdict: minor revision

Most of the earlier major issues have been fixed:

- **Abstract.** It now reports the failures: 47/61 for our predictor vs 50 and 48 for the representation baselines, the H-EX2 criterion not met, the unlearned $A_5$ cells, and the device sensitivity. It also states the hypotheses (real states, finite-state, token-local, $\beta = 2$).
- **Predictor errors.** All 14 errors are listed, and they match C-H-accuracy (61 − 47 = 14).
- **Secondary outcome.** The preregistered 7x–8x outcome is reported, including the collapses.
- **D5.** It carries the MPS/CPU replication caveat.
- **D1–D3 vs D4–D6.** The paper now says that D1–D3, the only tests that separate our predictor from the representation baselines, are non-significant, and that D4–D6 do not separate them.
- **BH correction.** m = 9 now matches the claims.
- **Complex KDA (arXiv:2609.24797).** The relation is stated as "neither result contains the other". The tn extension is labelled as our own hand observation.
- **DeltaProduct.** It is credited for the SO(3) upper bound.
- **Howe.** The law is quoted with "that length-generalizes" and with its no-additive-pathway setting.
- **$S_5$.** It is kept apart from the certified instances.
- **Proof-status lists.** The hand-proof list is complete (L2, L3, L5, L7, Theorem 1, open-$\beta$, complex remark, $S_5$, $Q_8$).
- **Prior-work wording.** The Deletang wording is fixed, and the contested and withdrawn rounds are explained.

The remaining errata fix residual overstatements and formatting:

- **Novelty and proof status.** "First" lower bound, "no general minimum was known", and "explains DeltaProduct's observation" are overstated. The abstract does not say that Theorem 1 is a hand proof, and the contributions bullet omits the theorem's hypotheses.
- **Softened failures.** "At least as well" should be "better". "Largely fails" misstates H-EX2, where the predictor matched 5 of 6 cells.
- **Howe.** "Fails" is unfair to Howe given the different evaluation length (16x vs 7x–8x).
- **Prior-work hypotheses.** The finite-precision hypotheses of Grazzi et al. and Shakerinava et al. are missing.
- **Formatting and citations.**
  - the title is duplicated;
  - there are dangling "Appendix C" references;
  - "abs(H)" appears as a column header;
  - Table 3 is inconsistent (62 + 42 ≠ 105);
  - some H-EX2 bullets have no claim id.

## Issues not fixable by small errata (or not covered because of the 20-item limit)

1. **Trailing verification log.** The final block (`---` / `Verification log: 137 claims cited, ...`) is pipeline meta text and must be deleted. It is left out of the errata only because of the 20-item cap. The generator should stop emitting it.
2. **Figure and table placement.** Figures appear in the order 1, 3, 2 and tables in the order 1, 2, 4, 3. Numbering follows the order of mention, but the floats should be placed in numeric order, or renumbered. This is a generator-level fix in `write_paper.py` / `export_tables.py`.
3. **Duplicated figure captions.** Each figure prints its caption twice: once as image alt text and once as an italic caption. The captions also contain claim-id meta text ("Claims [C-G-*]", "Evidence: claims C-X-(model)-(task) ..."). Keep one caption and drop the claim-id text. This is a generator fix.
4. **Table 3 structure.** The cleaner fix is an "h = 1" column (or a $\mathbb{Z}_2$ row) generated from code, so that the abelian row sums to 105. The errata only add a caption note.
5. **E2 supplementary test.** E2 is reported as significant, but its supplementary permutation test (p = 0.110, CI 0.75–2.39) does not meet the project criterion. This is not mentioned, although the paper reports supplementary results for D1–D3. Add one sentence, or drop supplementary results everywhere. Not included only because of the cap.
6. **Device confound in H-EX2.** The text says "most H-EX1 cells for hh2–hh4 ran on the CPU". Per the C-G claims, every hh2–hh4 cell ran on the CPU, while hh1 and the diagonal cells ran on MPS. Within H-EX1, architecture is therefore confounded with device. The D5 caveat touches on this, but the confound is not discussed in general. A proper fix needs a re-run on a single device, which is beyond the scope of errata.
7. **Weak citations for protocol statements.** Two general statements cite a single cell claim (C-G-diag_pm-Z2-all): "For every highlighted cell we also report the preregistered secondary outcome..." and the parenthetical convention. C-H-protocol does not define the secondary outcome. The claims file should gain a protocol-level claim for the 7x–8x secondary outcome.
8. **Scope of the H-EX1 learnability evidence (substantive, not wording).** The post-hoc restriction to the LSTM-solvable tasks gives a three-way tie (26/30 each). The preregistered experiments therefore give no evidence that $h^*$ predicts learnability better than the permutation or faithful baselines. The paper now says this, but the title phrase "Where Training Falls Short" understates it: training falls short of the predictor itself, not only of the theory. This is acceptable as framing, so no change is required.

No German text was found. Apart from the items above, no sentence presents a hypothesis-level claim as machine-checked. L1 and L4 are the only items labelled as machine-checked, consistent with C-L1 and C-L4.
