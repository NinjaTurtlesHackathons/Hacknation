# Physicochemical Descriptors Improve Fixed Fingerprint Baselines Across Three ADMET Endpoints

NinjaTurtlesHackathons | ADMET research draft | 4 October 2026

## Abstract

We evaluate a preregistered representation ablation for ADMET prediction with fixed CPU gradient-boosted models and an independently audited scorer; adding ten physicochemical descriptors to Morgan fingerprints reduces fixed-test mean absolute error by 33.06% for solubility, 12.99% for lipophilicity and 37.00% for Caco-2 permeability across twenty training seeds; descriptor-only ablations expose endpoint dependence and shuffled-label controls provide falsification checks; an audit covers twenty-two benchmark endpoints and preserves two invalid-structure test rows through a frozen median fallback; overlapping splits, public labels, assay heterogeneity and absent prospective validation limit interpretation; this pilot establishes endpoint-specific performance against fixed baselines, not a new algorithm, leaderboard record or clinical result. [C-release-abstract]

## Introduction and contribution

This reproducible pilot compares fixed molecular representations on three preregistered TDC ADMET regression endpoints; the structural audit covers 22 endpoints and 44 source files; the pilot does not establish clinical utility, a leaderboard record, a novel representation algorithm, or accelerated scientific discovery. [C-release-scope]

The primary question is whether adding ten fixed physicochemical descriptors to radius-two 1024-bit Morgan fingerprints lowers solubility scaffold-validation MAE; identical lipophilicity and Caco-2 comparisons are secondary; the objective is mean absolute error in the distributed target units, with no test-based method selection. [C-release-design]

Fingerprint and descriptor combinations, scaffold evaluation, and applicability-domain analysis have substantial prior art; the contribution here is an executed, auditable endpoint-specific ablation with falsification checks, rather than a new algorithm or a demonstrated publication-level scientific discovery; stronger impact requires replication and a specific mechanism or methodological improvement that survives stronger baselines. [C-release-novelty]

## Preregistered experiment

All learned models use LightGBM with 200 trees, learning rate 0.05, 15 leaves, minimum 20 samples per leaf, L2 penalty 1, two CPU threads and deterministic execution; descriptors are molecular weight, logP, TPSA, hydrogen-bond donors and acceptors, rotatable bonds, rings, fraction sp3, heavy atoms and aromatic rings; descriptor-only and fingerprint-only models are ablations, the training-target median is the naive baseline, and shuffled training targets define the negative control. [C-release-methods]

Seeds 1000 through 1019 use the TDC scaffold splitter with train/validation/test fractions 0.875/0.125/0 inside train_val; an explicit source-row column survives index resetting; each saved model is evaluated on the official fixed test set without refitting on validation observations; no early stopping or hyperparameter search is performed; seeds 1000 through 1004 are also exported but are not asserted to be an official leaderboard seed protocol. [C-release-splits]

The preregistered comparison uses paired one-sided sign flips with 20000 Monte Carlo draws and a plus-one correction, 5000 paired bootstrap resamples, and Benjamini-Hochberg at q=0.1; the primary hypothesis family has three endpoint comparisons; overlapping splits and reused test molecules make the intervals and p-values conditional sensitivity summaries rather than independent biological replication or prospective population inference. [C-release-inference]

The protocol document existed before computation; a working-directory error prevented the intended first commit and the following training command failed a row-alignment assertion before any model fit or score inspection; the document and correction were committed before successful experiments; therefore strict commit-before-first-computation compliance is not claimed. [C-release-precommit]

## Data coverage and structural audit

The source audit found 0 missing targets, 0 invalid training structures, 2 invalid test structures, and 0 canonical-molecule overlaps and 0 scaffold overlaps across train_val/test; within-split duplicates remain as distributed, so row-weighted scores need not equal unique-molecule-weighted scores. [C-release-audit]

Before any successful model fit or score inspection, two solubility test SMILES failed strict RDKit parsing; a documented amendment preserves both rows and uses the training-target median for every method on these structures, marks them invalid, and assigns similarity zero; no chemical repair or silent deletion is performed; structural audit read target completeness but no test score guided the amendment. [C-release-invalid]

solubility_aqsoldb has 1997 fixed test rows, validation size ranges from 999 to 2940 rows across seeds, and combined MAE restricted to strictly valid test structures is 0.846374; unequal validation sizes are induced by whole-scaffold groups, not silent row removal. [C-release-coverage-solubility_aqsoldb]

lipophilicity_astrazeneca has 840 fixed test rows, validation size ranges from 420 to 420 rows across seeds, and combined MAE restricted to strictly valid test structures is 0.635495; unequal validation sizes are induced by whole-scaffold groups, not silent row removal. [C-release-coverage-lipophilicity_astrazeneca]

caco2_wang has 182 fixed test rows, validation size ranges from 91 to 91 rows across seeds, and combined MAE restricted to strictly valid test structures is 0.301909; unequal validation sizes are induced by whole-scaffold groups, not silent row removal. [C-release-coverage-caco2_wang]

## Validation results and fixed-test evaluation

On the fixed solubility_aqsoldb test set, across 20 training seeds, MAE mean +/- seed standard deviation is median: 1.894131 +/- 0.048473; morgan: 1.266789 +/- 0.039799; descriptors: 0.899143 +/- 0.011470; combined: 0.847962 +/- 0.017176; shuffled: 1.891085 +/- 0.037153; adding descriptors to Morgan reduces mean test MAE by 33.06% relative to Morgan alone; this is a conditional descriptive comparison with every official test row retained. [C-release-test-solubility_aqsoldb]

On the fixed lipophilicity_astrazeneca test set, across 20 training seeds, MAE mean +/- seed standard deviation is median: 0.963613 +/- 0.002624; morgan: 0.730368 +/- 0.005053; descriptors: 0.769887 +/- 0.005581; combined: 0.635495 +/- 0.007778; shuffled: 1.013711 +/- 0.018586; adding descriptors to Morgan reduces mean test MAE by 12.99% relative to Morgan alone; this is a conditional descriptive comparison with every official test row retained. [C-release-test-lipophilicity_astrazeneca]

On the fixed caco2_wang test set, across 20 training seeds, MAE mean +/- seed standard deviation is median: 0.586401 +/- 0.006519; morgan: 0.479220 +/- 0.037340; descriptors: 0.340505 +/- 0.015110; combined: 0.301909 +/- 0.015109; shuffled: 0.625006 +/- 0.051972; adding descriptors to Morgan reduces mean test MAE by 37.00% relative to Morgan alone; this is a conditional descriptive comparison with every official test row retained. [C-release-test-caco2_wang]

For solubility_aqsoldb validation, Morgan MAE is 1.449784, descriptors MAE is 0.942899, and combined MAE is 0.904329; the paired Morgan/combined ratio is 1.603159, with bootstrap 95% interval [1.488537, 1.750759] and nominal one-sided p=0.00005000. [C-release-valid-solubility_aqsoldb]

For lipophilicity_astrazeneca validation, Morgan MAE is 0.754238, descriptors MAE is 0.760264, and combined MAE is 0.610390; the paired Morgan/combined ratio is 1.235665, with bootstrap 95% interval [1.217388, 1.253459] and nominal one-sided p=0.00005000. [C-release-valid-lipophilicity_astrazeneca]

For caco2_wang validation, Morgan MAE is 0.437256, descriptors MAE is 0.407075, and combined MAE is 0.390865; the paired Morgan/combined ratio is 1.118689, with bootstrap 95% interval [1.048756, 1.190120] and nominal one-sided p=0.00214989. [C-release-valid-caco2_wang]

The solubility_aqsoldb validation comparison passes the preregistered improvement criteria on this fixed dataset; after including all six additional negative-control comparisons in an expanded family of nine tests, the BH-adjusted p-value is 0.00022499; the larger family is a post-preregistration sensitivity check and does not strengthen prospective inference. [C-release-gate-solubility_aqsoldb]

The lipophilicity_astrazeneca validation comparison passes the preregistered improvement criteria on this fixed dataset; after including all six additional negative-control comparisons in an expanded family of nine tests, the BH-adjusted p-value is 0.00022499; the larger family is a post-preregistration sensitivity check and does not strengthen prospective inference. [C-release-gate-lipophilicity_astrazeneca]

The caco2_wang validation comparison passes the preregistered improvement criteria on this fixed dataset; after including all six additional negative-control comparisons in an expanded family of nine tests, the BH-adjusted p-value is 0.00644968; the larger family is a post-preregistration sensitivity check and does not strengthen prospective inference. [C-release-gate-caco2_wang]

## Falsification, sensitivity and negative results

The solubility_aqsoldb validation shuffled-label control has median-baseline/shuffled MAE ratio 0.961914, bootstrap 95% interval [0.943069, 0.982480], and nominal improvement p=0.99825009; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-solubility_aqsoldb-validation]

The lipophilicity_astrazeneca validation shuffled-label control has median-baseline/shuffled MAE ratio 0.973205, bootstrap 95% interval [0.958639, 0.988007], and nominal improvement p=0.99850007; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-lipophilicity_astrazeneca-validation]

The caco2_wang validation shuffled-label control has median-baseline/shuffled MAE ratio 0.940133, bootstrap 95% interval [0.910216, 0.973390], and nominal improvement p=0.99835008; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-caco2_wang-validation]

The solubility_aqsoldb test shuffled-label control has median-baseline/shuffled MAE ratio 1.001611, bootstrap 95% interval [0.991002, 1.011327], and nominal improvement p=0.39113044; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-solubility_aqsoldb-test]

The lipophilicity_astrazeneca test shuffled-label control has median-baseline/shuffled MAE ratio 0.950579, bootstrap 95% interval [0.942861, 0.958420], and nominal improvement p=1.00000000; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-lipophilicity_astrazeneca-test]

The caco2_wang test shuffled-label control has median-baseline/shuffled MAE ratio 0.938232, bootstrap 95% interval [0.905757, 0.973442], and nominal improvement p=0.99810009; it does not meet the improvement gate; failure to detect improvement is not proof of independence. [C-release-null-caco2_wang-test]

Exploratory nearest-training Morgan Tanimoto strata use thresholds 0.3 and 0.6; the pooled seed-row errors for the combined model are solubility_aqsoldb: low n-seed-row=4186, MAE=1.007285, medium n-seed-row=29434, MAE=0.856216, high n-seed-row=6320, MAE=0.703991; lipophilicity_astrazeneca: low n-seed-row=954, MAE=0.934878, medium n-seed-row=7590, MAE=0.719061, high n-seed-row=8256, MAE=0.524077; caco2_wang: low n-seed-row=1298, MAE=0.303108, medium n-seed-row=1554, MAE=0.319482, high n-seed-row=788, MAE=0.265280; counts reuse test molecules across seeds and are not unique molecule counts; these fixed descriptive strata neither certify an applicability domain nor explain a causal mechanism. [C-release-segments]

## Verifier and agent laboratory

The domain verifier passed 10 true/false, nonfinite, malformed, empty-input and self-assigned-tolerance selftests; an independently generated linear target is recovered at MAE 7.21644966006e-16, whereas shuffled synthetic training labels yield MAE 1.481077; the release validates all 600 experiment records and source-grounded predictions, and excludes nonfinite outputs and incomplete seed/method/row groups. [C-release-verification]

A separate fresh numerical run downloaded identical source CSV hashes, refitted the entire fixed experiment matrix, froze models before test scoring and reproduced all 15 endpoint-method mean test MAEs within absolute tolerance 1e-8; the maximum mean-MAE difference was 0; numerical reproduction strengthens implementation evidence but is not an independent biological replication. [C-release-reproduction]

The agent-facing laboratory exposes validation summaries only through domain.run_op; no benchmark molecular identities, per-molecule target rows or test scores are provided through these agent-facing operations; neutral identifier invariance follows from feature computation using SMILES alone and named endpoint labels without molecular identities; this narrower exposure check cannot certify absence of LLM training-corpus contamination or protect against a malicious process with filesystem access. [C-release-trust]

Independent review verified source-row alignment, disjoint molecular/scaffold partitions and rescoring, and reproduced saved seed-1000 predictions; it also found that a mutable prediction table could spoof the original scorer and that the shared manuscript gate checks numerical token membership rather than semantic truth; source grounding and frozen prediction hashes now reject the demonstrated target and hash tampering, while the final manuscript uses canonical verified state records rather than relying on the shared sentence gate alone. [C-release-redteam]

All model files, split indices and validation predictions were hashed before the first final-test score; after scoring, only verifier grounding and documentation were hardened; the original seal is retained, its engine/document hash differences are disclosed, and release_hashes records the hardened implementation and unchanged prediction artifacts. [C-release-freeze]

The repository laboratory executed 3 recorded agent rounds, with 2 confirmed recorded claims before release enrichment and 1 recorded unsuccessful questions; model fitting was a preregistered fixed experiment matrix, while agents inspected validation summaries and proposed checked numerical statements; no agent-discovery speedup was measured. [C-release-agents]

A Lean 4 core proof checks that the sum of natural absolute values of integer residuals is zero exactly when every residual is zero; its trusted axioms are propext, Quot.sound; this arithmetic anchor does not certify floating-point model fitting, statistical significance, chemical mechanism or clinical validity. [C-release-lean]

## Limitations and next scientific step

This pilot uses a single public benchmark snapshot and fixed model hyperparameters; it lacks prospective temporal validation, independent new assays, clinical evaluation, external expert review, and a comparison against competitive tuned models; descriptor effects cannot identify causal chemical mechanisms; a held-out benchmark result is evidence about the distributed assay targets, not patient safety. [C-release-limitations]

The run is local CPU research; Databricks, Unity Catalog and Spark have not been provisioned or tested; the experiment, claim and gate tables are the authoritative release inputs and can be imported into a platform integration; no live cloud deployment is claimed. [C-release-platform]

## Verified references

Yang et al.: Analyzing Learned Molecular Representations for Property Prediction.; DOI 10.1021/acs.jcim.9b00237; https://doi.org/10.1021/acs.jcim.9b00237; title/DOI verified through Crossref or Europe PMC; existence verification does not reproduce the paper findings. [C-release-ref-0]

Bemis and Murcko: The Properties of Known Drugs. 1. Molecular Frameworks; DOI 10.1021/jm9602928; https://doi.org/10.1021/jm9602928; title/DOI verified through Crossref or Europe PMC; existence verification does not reproduce the paper findings. [C-release-ref-1]

Hosni et al.: Explicit Applicability Domain Calculations Can Help Determine When Uncertainty Estimates Are Less Reliable.; DOI 10.1021/acsomega.5c11875; https://doi.org/10.1021/acsomega.5c11875; title/DOI verified through Crossref or Europe PMC; existence verification does not reproduce the paper findings. [C-release-ref-2]

Deng et al.: A systematic study of key elements underlying molecular property prediction; DOI 10.1038/s41467-023-41948-6; https://doi.org/10.1038/s41467-023-41948-6; title/DOI verified through Crossref or Europe PMC; existence verification does not reproduce the paper findings. [C-release-ref-3]

Therapeutics Data Commons: ADMET Benchmark Group; official benchmark documentation, accessed 4 October 2026; https://tdcommons.ai/benchmark/admet_group/overview/; https://dataverse.harvard.edu/api/access/datafile/4426004; raw snapshot hashes are recorded in provenance.json. [C-release-ref-tdc]
