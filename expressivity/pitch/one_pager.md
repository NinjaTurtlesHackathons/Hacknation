# One-pager: how many reflections does a recurrent layer need to keep track of state?

## Core graphic
`projects/expressivity/fig_hex2.png` (vector version `fig_hex2.pdf`): preregistered test H-EX2, seeds out of 20 that
length-generalise for 1, 2 and 3 Householder reflections per token. The solid line marks our certified minimum (2), the dotted line
marks the permutation-representation law of prior work (3 for S4; 4 for A5, beyond the plot). Left panel: A5 given as a 3-cycle and
a 5-cycle, 0/20, 18/20, 18/20. Right panel: S4 given as a transposition and a 4-cycle, 0/20, 6/20, 19/20. The figure shows the
prediction, the confirmation and the honest failure (S4, hh2) in one picture.
Backup graphic for the coverage story: `projects/expressivity/fig_atlas.png` (faithful Householder cost h of all 319 groups of
order <= 63; A5 at h = h* = 2).

## Three numbers
| Number | What it means | Source |
|---|---|---|
| **1** | Householder reflection per token suffices to track A5 exactly when the inputs are its involutions (h*(A5, involutions) = 1), although every faithful representation of A5 needs 2 (h = 2), and A5 is the textbook NC1-complete case | `expressivity/results/certified.json`, row A5/involutions (`lower` 1, `upper` 1, `upper_construction` so3/involutions, `upper_H_order` 120, `h_faithful` 2); live: `demo_path.md` D2, D3 |
| **18/20 vs 0/20** | seeds that length-generalise on A5 (3-cycle + 5-cycle) with 2 vs 1 reflections per token; prior work's law said 4 are needed; Fisher p = 1.7e-9 (BH-adjusted 2.5e-9) | `expressivity/results/confirmatory.json`, `H-EX2.cells` and `H-EX2.tests` (E1); preregistered in `expressivity/prereg.md` (Addendum H-EX2) |
| **138 of 319** | groups of order <= 63 for which h* is determined exactly (certified lower bound = certified upper bound) | `expressivity/results/atlas.json`, `summary` (`groups` 319, `exact` 138) |

## One insight: which assumption did we break?
**"Circuit complexity orders how hard state tracking is."** For a Householder-product recurrent layer (DeltaNet, DeltaProduct) the
per-layer cost is not a property of the group's circuit class, or even of the group alone: it depends on the input alphabet and on
which larger group the layer is allowed to represent. Certified examples: the abelian, solvable Z3 needs 2 reflections per token
(lower bound by the Lean-checked lemma L4), while the non-solvable A5 with involution inputs and S5 with transposition inputs need 1
(`certified.json`, rows Z3/all, A5/involutions, S5/transpositions; `theory.md`, C1-C3).

## Abstract for laypeople (three sentences)
Modern language models must keep track of changing situations, like the order of cards after a series of shuffles, and the classic
theory says some of these tracking tasks are fundamentally hard. Our team of AI agents, checked at every step by exact computer
algebra and a proof assistant, worked out exactly how much machinery one layer of a popular new architecture needs per word, and
found that some "hard" tasks need only the smallest possible amount once the inputs are chosen well. We then trained 20 models per
setting under rules fixed in advance: the predicted minimum worked on the hardest case (18 of 20 models), a rule from earlier work
was contradicted, and where training failed we report it openly.

## What we do not claim
- Theorem 1 (exact iff) combines Lean-checked lemmas (L1, L4) with hand proofs (L2, L3); the hand proofs are reviewed by the red team,
  not machine-checked (`expressivity/theory.md`, status legend).
- The law is about one layer, token-local transitions, finite state and exact arithmetic (`expressivity/assumptions.md` A1-A4);
  production DeltaNet uses a short convolution, which is outside the theorem.
- Learnability is a separate problem: H-EX2 as a whole is not a success (S4/tn with 2 reflections: 6/20, `confirmatory.json`
  `H-EX2.success` false), and models fail on A5/all and S5/all even with 4 reflections (completed H-EX1 cells; grid in progress).
- H-EX1 accuracy of the predictor: {H-EX1 accuracy} vs best baseline {best baseline accuracy}; fill only from
  `results/confirmatory.json` after `python -m expressivity.analyze`.
- h*(S5, all) and h*(Q8, all) remain open (certified bounds 2..4 and 2..6, `certified.json`).
