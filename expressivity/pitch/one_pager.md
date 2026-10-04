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
| **1** | Householder reflection per token suffices to track A5 exactly when the inputs are its involutions (h*(A5, involutions) = 1), although every faithful representation of A5 needs 2 (h = 2), and A5 is the textbook NC1-complete case. Certified, **not learned**: hh1 on A5/involutions 0/20 seeds (hh2 0/20, hh3 20/20) | `expressivity/results/certified.json`, row A5/involutions (`lower` 1, `upper` 1, `upper_construction` so3/involutions, `upper_H_order` 120, `h_faithful` 2); `confirmatory.json` `cells`; live: `demo_path.md` D2, D3 |
| **18/20 vs 0/20** | seeds that length-generalise on A5 (3-cycle + 5-cycle) with 2 vs 1 reflections per token, where the permutation-representation law (Howe 2026) predicted 4; Fisher p = 1.7e-9 (BH-adjusted 2.5e-9). Siems et al. 2025 had already observed A5 extrapolating with 2; our addition is the certified minimum, fixed in a preregistration before the run. The preregistered H-EX2 criterion as a whole **failed** (S4/tn with 2: 6/20) | `expressivity/results/confirmatory.json`, `H-EX2.cells`, `H-EX2.tests` (E1), `H-EX2.success` false; `expressivity/prereg.md` (Addendum H-EX2); `evidence.md` (DeltaProduct full-text quote) |
| **138 of 319** | groups of order <= 63 for which h* is determined exactly (certified lower bound = certified upper bound); an explorer agent then lowered 17 further atlas upper bounds with certified covers of order 2abs(G) (18 of 18 certificates re-checked) | `expressivity/results/atlas.json`, `summary` (`groups` 319, `exact` 138); `expressivity/results/explore_certified.json`; `expressivity/explore_open/findings.md` |

## One insight: which assumption did we break?
**"Circuit complexity orders how hard state tracking is."** For a Householder-product recurrent layer (DeltaNet, DeltaProduct) the
per-layer cost is not ordered by the group's circuit class: representation theory orders it. The cost h* depends on the input
alphabet and on which covering group the layer may represent. Certified examples: the abelian Z3 needs 2 reflections per token
(lower bound by the Lean-checked lemma L4) and the solvable Q8 needs 3 (h*(Q8, all) <= 3 certified via the cover C4:C4, = 3 by a hand
argument), while the non-solvable A5 with involution inputs and S5 with transposition inputs need 1 (`certified.json`, rows Z3/all,
A5/involutions, S5/transpositions; `theory.md`, C1-C3; `explore_open/findings.md`). **Learnability is a separate bottleneck**: the
preregistered prediction test H-EX1 was not met (below), and A5/involutions with one reflection is realisable but was not learned.

## Abstract for laypeople (three sentences)
Modern language models must keep track of changing situations, like the order of cards after a series of shuffles, and the classic
theory says some of these tracking tasks are fundamentally hard. Our team of AI agents, checked at every step by exact computer
algebra and a proof assistant, worked out exactly how much machinery one layer of a popular new architecture needs per word, and
found that some "hard" tasks need only the smallest possible amount once the inputs are chosen well. We then trained 20 models per
setting under rules fixed in advance: on the hardest case the predicted minimum of two worked (18 of 20 models) where a rule from
earlier work said four, but our predictor did not beat that rule on the full grid, and the models did not learn every task the theory
allows, which we report openly.

## Positioning (prior and concurrent work)
- Complex KDA (Siems et al. 2026, arXiv:2609.24797) anticipates the compression idea (finite-state tracker -> finite group mapping
  onto G via an idempotent word) and the S5 minimum of four Householders, both under non-expansive transitions
  (`expressivity/novelty.md`, `expressivity/ckda_comparison.md`).
- Two Householders for A5 and S4 via SO(3) are known constructions (Siems et al. 2025, arXiv:2502.10297).
- New here: the general law k >= h*(G, Sigma) over covering groups for a fixed input alphabet (Theorem 1); compression without any norm
  assumption (L2); one reflection per token for A5 over its involutions (via H3 = A5 x Z2); the atlas over all 319 groups of order <= 63.

## What we do not claim
- **H-EX1, the preregistered prediction test, is not met**: our predictor gets 47/61 cells right, the permutation law 50/61, faithful
  representations only 48/61, circuit class 41/61 (`confirmatory.json`, `accuracy`; `gates.H-EX1_success` false). Exploratory, post
  hoc, not preregistered: on the 5 tasks where the LSTM positive control succeeds, ours = permutation law = faithful-only 26/30 vs
  circuit class 16/30 (`exploratory_positive_control_tasks`).
- Theorem 1 (exact iff) combines Lean-checked lemmas (L1, L4) with hand proofs (L2, L3); the hand proofs are reviewed by the red team,
  not machine-checked (`expressivity/theory.md`, status legend).
- The law is about one layer, token-local transitions, finite state and exact arithmetic (`expressivity/assumptions.md` A1-A4);
  production DeltaNet uses a short convolution, which is outside the theorem.
- Learnability is a separate problem: H-EX2 as a whole is not a success (S4/tn with 2 reflections: 6/20, `H-EX2.success` false);
  A5/involutions with 1 reflection is certified but 0/20 seeds learn it; models fail on A5/all and S5/all even with 4 reflections
  (0/20 each), as does the LSTM.
- Training results are device-sensitive: hh1 on Z2/all succeeds in 18/20 seeds on MPS but 0/20 on CPU (`replication_mps_vs_cpu`).
- h*(S5, all) = 4 rests on Complex KDA's Theorem 4 plus a hand step of ours (`theory.md` C5; certified interval only 2..4);
  h*(Q8, all) = 3 rests on a hand lower bound (certified upper bound 3). Still open: h*(SL(2,3), all); h*(S5, tn) = 4 pending review.
