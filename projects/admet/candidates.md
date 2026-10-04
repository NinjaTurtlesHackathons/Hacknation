# Candidate register — Analogist

Scope: numerical prediction from sparse discrete local-pattern features `b`, continuous global summaries `z`, and group identifier `g`. Train on one group partition and forecast disjoint groups. No target-domain outcomes were supplied to this role; no performance result is claimed. The preregistered in-domain candidate, concatenation `[b,z]`, remains fixed. This register cannot add methods, tune settings, or change the confirmatory suite.

## Common structure and limits

Shared principle: local-pattern distributions and whole-object summaries describe different resolutions of the same object; their complementarity is a question for held-out prediction.

What follows from the representation: `[b,z]` retains both blocks; a sufficiently expressive hypothesis class can represent a rule that ignores either block. That does **not** imply that a finite-data fitted model improves. Summaries can be redundant, noisy, or group proxies. Disjoint group membership establishes the specified partition, not statistical independence or applicability to every future group.

All candidates have transfer tier **`(empty, infinity)`**, written mathematically `(∅,∞)`: no transferred theorem class, no certified loss bound. The sources motivate questions and controls, not adoption of their algorithms. No method-transfer theorem or formal reduction is asserted.

## Two source domains

### A. Text difficulty assessment

Structural mapping: text → object; local token/transition patterns → `b`; sentence length and entity-density summaries → `z`; reading level → numerical response; author/publication families → proposed grouping.

Literature support: Feng, Jansche, Huenerfauth and Elhadad compare language-model, syntactic, discourse and shallow features. Their paper includes local entity-transition distributions and document summaries, and describes its own reading-grade task as **classification**, not continuous regression. [Primary paper](https://aclanthology.org/C10-2032.pdf), §§1, 3 (tool evidence `turn9view1`; title/authors verified via [ACL record](https://aclanthology.org/C10-2032/), `turn8search0`).

Implication: this is a concrete multiresolution representation analogy. It supports comparing blocks and redundancy; it supplies no guarantee for the present response or split. Numeric regression and author-disjoint evaluation in the mapping are proposed adaptations, **not** claims about that paper.

Hypothesis A: global summaries help most when held-out objects contain local patterns poorly represented in training. Testable prediction: validation improvement of `[b,z]` over `b` is larger in a prespecified low-support stratum, defined only from training pattern frequencies. Naive alternative: summaries merely measure object size; a size-only model or size-matched strata explain the difference.

### B. Visual perception and image-quality prediction

Structural mapping: image → object; histogram of quantized local patches → `b`; global color/transform statistics → `z`; human quality score → response; source image/capture family → proposed grouping.

Literature support is deliberately split: Gidaris et al. describe quantization of local visual features into a vocabulary and visual-word histograms in [Learning Representations by Predicting Bags of Visual Words](https://arxiv.org/abs/2002.12247) (tool `turn10view0`, abstract). Ghadiyaram and Bovik describe color/transform statistics and regression against human image-quality opinions in [Perceptual Quality Prediction on Authentically Distorted Images Using a Bag of Features Approach](https://arxiv.org/abs/1609.04757) (tool `turn9view0`, lines 16–19). Neither source establishes the combined construction or group protocol proposed here.

Implication: aggregate local patterns and numerical global statistics are concrete representations, and numerical quality regression exists in this source domain. Their combination under unseen-group evaluation remains a hypothesis.

Hypothesis B: summaries correct systematic errors of a local-pattern model when aggregate intensity or scale changes while pattern composition stays similar. Prediction: in validation groups, residual association with `z` decreases after adding `z`, accompanied by lower prediction loss. Naive alternative: a global-summary-only regressor already captures the useful signal; fusion adds complexity without gain. Residual decorrelation alone does not validate prediction quality.

Rejected verbal analogy: “more context always improves understanding.” It defines neither a shared relation nor a falsifiable prediction and cannot justify a candidate.

## Selection matrix

Judgment scores, **not measured results**; 1–5, higher better. V = verifiability, Gain = expected gain, Data = readiness, Time = timebox fit, Jury = explanation fit, Copy = hard to copy, Explain = 30-second clarity. V/Data = 1 is a veto. Jury weight depends on the project’s recorded jury type; it is not chosen here.

| Candidate | V | Gain | Data | Time | Jury | Copy | Explain | Status / tier |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Training mean/median | 5 | 1 | 5 | 5 | 2 | 1 | 5 | Naive reference; `(∅,∞)` |
| Local block `b` only | 5 | 3 | 5 | 5 | 4 | 1 | 5 | Fixed-suite comparator if preregistered; `(∅,∞)` |
| Concatenated `[b,z]` | 5 | 3 | 4 | 5 | 5 | 1 | 5 | **Fixed preregistered candidate**; `(∅,∞)` |
| Global `z` only / size only | 5 | 2 | 4 | 5 | 4 | 1 | 5 | Naive exploratory controls; `(∅,∞)` |
| Separate predictors with validation-weighted fusion | 5 | 2 | 4 | 3 | 3 | 1 | 4 | Future exploratory alternative only; `(∅,∞)` |

No novelty or defensibility claim follows from this matrix. Any moat would require verified execution, provenance and evaluation quality. Failure to beat the fixed baseline leads to the preregistered fallback, not an unregistered replacement winner.

## Validation-only precheck plan

1. Use only training plus the designated group-disjoint validation partition. Fit vocabularies, scaling, imputations, support thresholds and model choices on training only. Preserve the sealed test partition and the existing confirmatory method list.
2. Record every exploratory comparison and subgroup definition before execution. Compare fixed `[b,z]` against `b`, training constant, `z` only and size only where permitted as exploratory controls; use equal tuning budgets and paired seeds.
3. Report validation loss differences, group-level uncertainty and support-stratum counts; retain negative effects. Group resampling needs enough groups and cannot be replaced silently by row-level resampling. Association and subgroup gains are diagnostic, not causal claims.
4. Shuffle the summary block within validation groups as a diagnostic negative control, with the limitation that correlated blocks make permutation samples unrealistic. Audit feature availability and any group/target proxies. Count all tests for the project’s multiplicity policy.
5. These prechecks may label hypotheses plausible, unsupported or infeasible. They cannot change the preregistered candidate, its confirmatory comparison, or test interpretation. Any future alternative needs a new preregistration and a fresh untouched evaluation set.

Status: literature verified; structural mappings explicit; hypotheses untested. Gate 2 requires actual precheck evidence from the execution owner.
