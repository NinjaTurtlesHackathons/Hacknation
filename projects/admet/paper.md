**Abstract** We study a fixed representation ablation on three public ADMET regression endpoints. A common gradient-boosted learner is fitted to Morgan fingerprints, ten physicochemical descriptors, and their concatenation under twenty scaffold-training splits. On the fixed test sets, concatenation reduces mean absolute error relative to fingerprints alone by 33.06% for solubility, 12.99% for lipophilicity, and 37.00% for Caco-2 permeability. Descriptor-only models expose endpoint dependence, while shuffled-target controls fail the prespecified improvement criterion. A structural audit covers twenty-two endpoints; two invalid solubility test structures are retained through a frozen median fallback. Source-grounded rescoring and a fresh numerical rerun reproduce the reported results. The observations concern a fixed benchmark and fixed learner. They establish neither a novel representation method nor prospective biological or clinical validity.

**Keywords:** ADMET; molecular representations; scaffold splitting; numerical reproducibility; verification.

# Introduction

Molecular property prediction assigns a numerical assay target to a molecular structure. Its evaluation depends both on the representation supplied to the learner and on the relationship between training and evaluation molecules. Learned molecular representations and the elements underlying molecular property prediction have been studied in the literature . Here we isolate a narrower empirical question: for a fixed learner and fixed scaffold protocol, does supplementing a binary fingerprint with a small physicochemical descriptor vector reduce prediction error?

Let $`F`$, $`D`$, and $`F\oplus D`$ denote the fingerprint, descriptor, and concatenated representations. The primary comparison concerns solubility; the same lipophilicity and Caco-2 comparisons are secondary. The benchmark source is the Therapeutics Data Commons (TDC) ADMET group . We use its fixed test rows and construct repeated scaffold partitions within the distributed training and validation portion.

Two remarks delimit the content. First, fingerprint–descriptor combinations are established tools; our contribution is an executed, auditable ablation, rather than a new algorithm or a leaderboard record. Second, the repeated partitions overlap and share the same fixed test molecules. Variation across seeds therefore measures conditional sensitivity on these datasets, rather than independent biological replication.

**Summary of results.**

- Concatenation lowers mean fixed-test error relative to fingerprints on all three endpoints (Observation <a href="#obs:test" data-reference-type="ref" data-reference="obs:test">1</a> and Table <a href="#tab:test" data-reference-type="ref" data-reference="tab:test">[tab:test]</a>).

- Descriptor-only performance differs by endpoint, preventing a uniform conclusion that one representation dominates (Observation <a href="#obs:ablation" data-reference-type="ref" data-reference="obs:ablation">2</a>).

- The prespecified validation gates pass, whereas the shuffled-target controls do not (Section <a href="#sec:validation" data-reference-type="ref" data-reference="sec:validation">4</a>).

- Independent rescoring and a fresh rerun reproduce the numerical release; the verification boundary is made explicit (Section <a href="#sec:verification" data-reference-type="ref" data-reference="sec:verification">5</a> and Appendices <a href="#app:protocol" data-reference-type="ref" data-reference="app:protocol">7</a>–<a href="#app:evidence" data-reference-type="ref" data-reference="app:evidence">9</a>).

# Setting and evaluation

## Data and partitions

The three fitted endpoints are `solubility_aqsoldb`, `lipophilicity_astrazeneca`, and `caco2_wang`. Their fixed test sets contain 1997, 840, and 182 rows, respectively. Targets remain in the units supplied by the benchmark; errors from different endpoints are not pooled into one score.

For seeds $`s\in\{1000,\ldots,1019\}`$, the TDC scaffold splitter partitions the distributed `train_val` rows into training and validation fractions 0.875 and 0.125. An explicit source-row column survives index resetting. Whole-scaffold grouping produces validation sizes of 999–2940 for solubility, 420 for lipophilicity, and 91 for Caco-2. Molecular frameworks provide the structural basis for this kind of partition . We do not refit on validation rows before final-test evaluation.

## Representations and learner

The fingerprint is a radius-two, 1024-bit Morgan vector. The descriptor vector consists of molecular weight, logP, topological polar surface area, hydrogen-bond donor and acceptor counts, rotatable bonds, ring count, fraction sp3, heavy-atom count, and aromatic-ring count. We compare $`F`$, $`D`$, and $`F\oplus D`$, together with a training-target median baseline and a shuffled-training-target control using concatenated features with permuted training labels.

Every learned model uses LightGBM with 200 trees, learning rate 0.05, at most 15 leaves, at least 20 samples per leaf, and L2 penalty 1. Execution is deterministic with two CPU threads. There is no hyperparameter search or early stopping. Consequently, a representation effect in this study is conditional on this particular learner configuration.

## Scores and comparisons

For evaluation rows $`I`$, targets $`y_i`$, and predictions $`\widehat y_{i,m,s}`$ from method $`m`$ and seed $`s`$, define
``` math
\begin{equation}
\label{eq:mae}
E_{m,s}(I)=\frac{1}{|I|}\sum_{i\in I}|y_i-\widehat y_{i,m,s}|.
\end{equation}
```
The reported seed-average error and relative reduction are
``` math
\begin{align}
\overline E_m&=\frac1{20}\sum_s E_{m,s},\label{eq:mean}\\
\Delta&=100\left(1-\frac{\overline E_{F\oplus D}}{\overline E_F}\right).\label{eq:reduction}
\end{align}
```
Thus $`\Delta>0`$ means lower error for concatenation. Validation inference uses paired seed scores, 20000 one-sided Monte Carlo sign flips with a plus-one correction, and 5000 paired bootstrap resamples. Benjamini–Hochberg correction uses $`q=0.1`$ for the three endpoint comparisons. The improvement gate requires twenty seeds, nominal $`p<0.05`$, BH rejection, and a ratio interval with lower bound greater than one. These are fixed-dataset summaries; overlapping partitions do not justify population-level confidence claims.

# Fixed-test observations

<div class="table*">

| Endpoint | Median | Fingerprint $`F`$ | Descriptors $`D`$ | $`F\oplus D`$ | Shuffled | Reduction |
|:---|---:|---:|---:|---:|---:|---:|
| Solubility | 1.894 (0.048) | 1.267 (0.040) | 0.899 (0.011) | 0.848 (0.017) | 1.891 (0.037) | 33.06% |
| Lipophilicity | 0.964 (0.003) | 0.730 (0.005) | 0.770 (0.006) | 0.635 (0.008) | 1.014 (0.019) | 12.99% |
| Caco-2 | 0.586 (0.007) | 0.479 (0.037) | 0.341 (0.015) | 0.302 (0.015) | 0.625 (0.052) | 37.00% |

</div>

<div id="obs:test" class="observation">

**Numerical observation 1**. For the fixed test rows and twenty fitted models per representation, concatenation reduces seed-average MAE relative to the fingerprint model by 33.06%, 12.99%, and 37.00% for solubility, lipophilicity, and Caco-2, respectively.

</div>

*Numerical verification.* Apply equations <a href="#eq:mae" data-reference-type="eqref" data-reference="eq:mae">[eq:mae]</a>–<a href="#eq:reduction" data-reference-type="eqref" data-reference="eq:reduction">[eq:reduction]</a> to the saved predictions after matching source rows and targets. Table <a href="#tab:test" data-reference-type="ref" data-reference="tab:test">[tab:test]</a> reports the resulting errors; Figure <a href="#fig:reduction" data-reference-type="ref" data-reference="fig:reduction">1</a> displays their relative reductions. The models and validation predictions were sealed before the first final-test score. This procedure is a reproducible calculation, not a mathematical proof of future predictive performance.

<div id="obs:ablation" class="observation">

**Numerical observation 2**. The descriptor-only model has lower mean test MAE than the fingerprint model for solubility and Caco-2, but higher mean test MAE for lipophilicity. Concatenation has lower mean error than either constituent representation on all three endpoints.

</div>

*Numerical verification.* Compare the three representation columns of Table <a href="#tab:test" data-reference-type="ref" data-reference="tab:test">[tab:test]</a>. The endpoint dependence supports reporting the ablations separately. It does not identify which descriptors cause the improvement, and it does not establish a chemical mechanism.

<figure id="fig:reduction" data-latex-placement="t">

<figcaption>Reduction from concatenating descriptors with fingerprints, relative to the fixed fingerprint model, using equation <a href="#eq:reduction" data-reference-type="eqref" data-reference="eq:reduction">[eq:reduction]</a>. Each bar is a ratio of seed-average MAEs on one fixed test set. No independent-population uncertainty is implied.</figcaption>
</figure>

# Validation and falsification

<div id="tab:valid">

| Endpoint      |    Ratio |           95% interval |
|:--------------|---------:|-----------------------:|
| Solubility    | 1.603159 | \[1.488537, 1.750759\] |
| Lipophilicity | 1.235665 | \[1.217388, 1.253459\] |
| Caco-2        | 1.118689 | \[1.048756, 1.190120\] |

Validation fingerprint/combined MAE ratio and paired bootstrap interval. Intervals describe repeated partitions of fixed data.

</div>

The mean validation MAEs for fingerprints and concatenation are 1.449784 and 0.904329 for solubility, 0.754238 and 0.610390 for lipophilicity, and 0.437256 and 0.390865 for Caco-2. All three comparisons pass the prespecified gate. The nominal one-sided $`p`$-values are 0.00005000, 0.00005000, and 0.00214989. Table <a href="#tab:valid" data-reference-type="ref" data-reference="tab:valid">1</a> reports the corresponding ratio intervals.

An expanded family includes six shuffled-target comparisons, giving nine tests in total. This post-preregistration sensitivity analysis yields BH-adjusted $`p`$-values of 0.00022499, 0.00022499, and 0.00644968 for the representation comparisons. It does not strengthen prospective inference.

For every endpoint, shuffled-label controls fail the improvement gate on both validation and test. Their validation median-baseline/shuffled MAE ratios are 0.961914, 0.973205, and 0.940133; the corresponding test ratios are 1.001611, 0.950579, and 0.938232. The solubility test ratio is close to one, while the other test ratios favour the median. Failure to detect improvement is not proof that every possible leakage channel is absent.

## Exploratory similarity strata

We also partition test predictions by nearest-training Morgan Tanimoto similarity, using thresholds 0.3 and 0.6. For the combined model, pooled seed-row MAEs in the low, medium, and high strata are 1.007285, 0.856216, and 0.703991 for solubility; 0.934878, 0.719061, and 0.524077 for lipophilicity; and 0.303108, 0.319482, and 0.265280 for Caco-2. Caco-2 does not exhibit a monotone low-to-high sequence. These descriptive strata reuse test molecules across seeds. They neither certify an applicability domain nor explain a causal mechanism; explicit applicability-domain calculations are a separate research question .

# Source-grounded verification

The release verifier matches prediction rows and targets against the pinned source snapshot, rejects nonfinite values and incomplete groups, and recomputes MAE independently of the experiment logger. It checks 600 logged evaluations, including all endpoint, seed, method, and partition groups. Independent review also checks source-row alignment and partition disjointness.

A fresh numerical run downloads identical source CSV hashes, refits the complete fixed experiment matrix, and freezes models before scoring its test predictions. All fifteen endpoint–method mean test MAEs match the release; the maximum absolute difference is zero under a tolerance of $`10^{-8}`$. This establishes numerical reproduction in the tested environment. It is not an independent assay replication.

<div id="lem:zero" class="lemma">

**Lemma 1**. *For a finite list of integer residuals $`r_1,\ldots,r_n`$, the sum of their natural absolute values is zero if and only if every residual is zero.*

</div>

<div class="proof">

*Proof.* Each summand is nonnegative. If their sum is zero, each summand is zero, so every residual is zero. Conversely, zero residuals give a zero sum. The repository contains a Lean 4 check by induction on the residual list. ◻

</div>

The printed trusted axioms for this Lean check are `propext` and `Quot.sound`. Lemma <a href="#lem:zero" data-reference-type="ref" data-reference="lem:zero">1</a> is an exact arithmetic anchor only. It does not certify floating-point fitting, statistical significance, chemical mechanism, or clinical validity.

# Discussion

Under a shared fixed learner, ten physicochemical descriptors improve the fingerprint baseline on the three evaluated endpoints. The descriptor-only comparison changes direction for lipophilicity, so the result cannot be reduced to a uniform ranking of fingerprints and descriptors. Concatenation performs best among these fixed representations, but competitive tuned models remain untested.

The principal limitations are the single public snapshot, fixed hyperparameters, overlapping partitions, assay heterogeneity, and absent prospective temporal validation or new assays. No clinical evaluation or external expert review has been completed. Public benchmark labels also preclude a general claim of freedom from training-corpus contamination. A held-out assay score is not evidence of patient safety.

The next scientific step is independent replication with competitive baselines and a specific methodological or mechanistic hypothesis. Publication-level novelty remains an open gate. No agent-discovery speedup has been measured, and the local CPU experiment has not been deployed to Databricks, Unity Catalog, or Spark.

# Protocol and structural audit

The audit covers twenty-two endpoints and forty-four source files. It finds no missing targets, no invalid training structures, and two invalid test structures. Canonical-molecule and scaffold overlaps between the distributed `train_val` and test portions are zero. Within-partition duplicates remain as distributed, so row-weighted scores need not equal unique-molecule-weighted scores.

The invalid structures are solubility test rows with zero-based source indices 1159 and 1160. Before successful fitting or score inspection, a documented amendment fixed the training-target median fallback for every method on both rows. No chemical repair or deletion was performed. Restricting solubility evaluation to valid structures gives combined mean MAE 0.846374, compared with 0.847962 with all rows retained.

The protocol document existed before computation. A working-directory error prevented its intended first commit; the subsequent training command failed a row-alignment assertion before any fit or score inspection. The document and correction were committed before successful experiments. Accordingly, strict commit-before-first-computation compliance is not claimed. The structural audit checked target completeness, but no test score guided the fallback amendment.

All models, split indices, and validation predictions were hashed before final-test scoring. Later changes hardened verifier grounding and documentation. The original seal remains available, with engine and document hash differences disclosed; the release hashes identify the hardened implementation and unchanged prediction artifacts.

# Verifier and laboratory boundary

The domain verifier passes ten true/false, nonfinite, malformed, empty-input, and self-assigned-tolerance checks. A synthetic linear target is recovered at MAE $`7.21644966006\times10^{-16}`$, while shuffled synthetic training labels yield 1.481077.

Review found that mutable prediction targets could spoof the original scorer. Source grounding and frozen prediction hashes now reject the demonstrated target and hash tampering. Review also found that the shared writer’s numerical-token gate does not establish semantic truth. The present manuscript is an editorial rewrite of checked records with an explicit support map; its wording is reviewed separately rather than declared machine-proved.

The agent-facing domain operations expose validation summaries without molecular identities, per-molecule target rows, or test scores. They do not defend against a malicious process with filesystem access. Three recorded laboratory rounds produced two confirmed claims and one unanswered, out-of-protocol question. The experiments themselves are a fixed matrix, not adaptively selected discoveries.

# Evidence and reproducibility

The project directory `projects/admet/` contains the frozen protocol, raw-source provenance, split indices, model seals, saved predictions, experiment and gate tables, verifier reports, numerical reproduction report, and Lean source. The machine-readable ledger `paper_belege.json` retains forty-three canonical checked records and maps manuscript sections to them. It records support, rather than a proof of semantic equivalence between every editorial sentence and a checker output.

Table <a href="#tab:test" data-reference-type="ref" data-reference="tab:test">[tab:test]</a> is generated directly from the authoritative experiment table after source-grounded validation. The standalone LaTeX source, accompanying Markdown, and PDF are built from one manuscript. The repository retains the original framework-generated draft separately. A fresh numerical rerun uses `reproduce.py`; manuscript rendering uses `render_release.py` without fitting new models or calling a language model.

<div class="thebibliography">

9 Yang et al. *Analyzing Learned Molecular Representations for Property Prediction*. [doi:10.1021/acs.jcim.9b00237](https://doi.org/10.1021/acs.jcim.9b00237). Deng et al. *A systematic study of key elements underlying molecular property prediction*. [doi:10.1038/s41467-023-41948-6](https://doi.org/10.1038/s41467-023-41948-6). Therapeutics Data Commons. *ADMET Benchmark Group*. <https://tdcommons.ai/benchmark/admet_group/overview/>. Accessed 4 October 2026. Raw snapshot hashes are recorded in `provenance.json`. Bemis and Murcko. *The Properties of Known Drugs. 1. Molecular Frameworks*. [doi:10.1021/jm9602928](https://doi.org/10.1021/jm9602928). Hosni et al. *Explicit Applicability Domain Calculations Can Help Determine When Uncertainty Estimates Are Less Reliable*. [doi:10.1021/acsomega.5c11875](https://doi.org/10.1021/acsomega.5c11875).

</div>
