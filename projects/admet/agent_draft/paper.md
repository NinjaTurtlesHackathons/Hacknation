# Physicochemical Descriptors Improve Fixed Fingerprint Baselines Across Three ADMET Endpoints

NinjaTurtlesHackathons, Research draft

*[entfernt: unbelegt — Zahl ohne Beleg]* *[entfernt: unbelegt — Zahl ohne Beleg]*

## Abstract

We report a preregistered representation ablation for three ADMET regression endpoints (solubility_aqsoldb, lipophilicity_astrazeneca, caco2_wang) [C-release-abstract]. *[entfernt: unbelegt — Zahl(en) [20.0] stehen in keiner zitierten Claim]* Across training seeds, adding descriptors reduces mean fixed-test MAE by 33.06% for solubility, 12.99% for lipophilicity and 37.00% for Caco-2 permeability relative to Morgan alone [C-release-abstract]. Descriptor-only ablations and shuffled-label controls are reported alongside [C-release-abstract] [C-release-methods]. The results are conditional sensitivity summaries of a fixed public benchmark, not replication, clinical utility or a new algorithm [C-release-abstract] [C-release-limitations].

## 1 Introduction

The question addressed here is whether a small set of fixed physicochemical descriptors lowers the validation error of fixed Morgan fingerprint models for ADMET regression [C-release-design]. The primary question concerns solubility scaffold-validation MAE; lipophilicity and Caco-2 comparisons are secondary and use identical procedures [C-release-design]. The objective is mean absolute error in the distributed target units, and no method is selected on test data [C-release-design].

The contribution is an executed, auditable endpoint-specific ablation with falsification checks [C-release-novelty]. Fingerprint and descriptor combinations, scaffold evaluation and applicability-domain analysis have substantial prior art [C-release-novelty]. No new algorithm is proposed, and no publication-level scientific discovery is claimed [C-release-novelty] [C-release-scope].

The main results are:

- On validation data, the paired Morgan/combined MAE ratio is 1.603159 for solubility, 1.235665 for lipophilicity and 1.118689 for Caco-2 [C-release-valid-solubility_aqsoldb] [C-release-valid-lipophilicity_astrazeneca] [C-release-valid-caco2_wang].
- On the fixed test sets, mean MAE decreases by 33.06%, 12.99% and 37.00% when descriptors are added to Morgan fingerprints [C-release-test-solubility_aqsoldb] [C-release-test-lipophilicity_astrazeneca] [C-release-test-caco2_wang].
- Shuffled-label controls do not meet the preregistered improvement gate [C-release-null-solubility_aqsoldb-validation] [C-release-null-lipophilicity_astrazeneca-validation] [C-release-null-caco2_wang-validation].

## 2 Setting and certificates

**Task and objective.** The study covers three preregistered TDC ADMET regression endpoints. The audit covers 22 endpoints and 44 source files, but the pilot does not establish clinical utility [C-release-scope].

**Representation.** Each molecule is encoded by radius-two 1024-bit Morgan fingerprints, optionally concatenated with ten descriptors: molecular weight, logP, TPSA, hydrogen-bond donors and acceptors, rotatable bonds, rings, fraction sp3, heavy atoms and aromatic rings [C-release-design] [C-release-methods].

**Learner and fixed hyperparameters.** All learned models use LightGBM with 200 trees, learning rate 0.05, 15 leaves, a minimum of 20 samples per leaf, L2 penalty 1, two CPU threads and deterministic execution [C-release-methods]. No hyperparameter search and no early stopping are performed [C-release-splits].

**Controls.** Descriptor-only and fingerprint-only models are ablations. The training-target median is the naive baseline. Shuffled training targets define the negative control [C-release-methods].

**Splits.** Seeds 1000 through 1019 use the TDC scaffold splitter [C-release-splits]. The train/validation/test fractions inside train_val are 0.875/0.125/0 [C-release-splits]. Each saved model is evaluated on the official fixed test set without refitting on validation observations [C-release-splits]. Seeds 1000 through 1004 are also exported, but they are not asserted to be an official leaderboard seed protocol [C-release-splits].

**Inference.** The preregistered comparison uses paired one-sided sign flips with 20000 Monte Carlo draws and a plus-one correction [C-release-inference]. It also uses 5000 paired bootstrap resamples [C-release-inference]. Benjamini-Hochberg control is applied at q=0.1 [C-release-inference]. The primary family has three endpoint comparisons [C-release-inference]. Overlapping splits and reused test molecules make the intervals and p-values conditional sensitivity summaries, not independent biological replication or prospective inference [C-release-inference].

**Data certificates.** The source audit found 0 missing targets and 0 invalid training structures [C-release-audit]. It found 2 invalid test structures [C-release-audit]. It found 0 canonical-molecule overlaps and 0 scaffold overlaps between train_val and test [C-release-audit]. Within-split duplicates remain as distributed, so row-weighted and unique-molecule-weighted scores need not coincide [C-release-audit]. Two solubility test SMILES failed strict RDKit parsing. A documented amendment preserves these rows, applies the training-target median to every method on them, marks them invalid and assigns similarity zero [C-release-invalid]. No chemical repair or silent deletion was performed, and no test score guided the amendment [C-release-invalid].

**Verifier certificates.** The domain verifier passed 10 selftests covering true/false, nonfinite, malformed, empty-input and self-assigned-tolerance inputs [C-release-verification]. An independently generated linear target was recovered at MAE 7.21644966006e-16, whereas shuffled synthetic training labels yielded MAE 1.481077 [C-release-verification]. The release validates all 600 experiment records and source-grounded predictions, and excludes nonfinite outputs and incomplete seed/method/row groups [C-release-verification].

**Exposure and freezing.** The agent-facing laboratory exposes validation summaries only through a single operation; prompts contain no SMILES, drug names, molecular target rows or test scores [C-release-trust]. This check cannot certify absence of LLM training-corpus contamination, nor protect against a malicious process with filesystem access [C-release-trust]. All model files, split indices and validation predictions were hashed before the first final-test score. After scoring, only verifier grounding and documentation were changed; the original seal is retained and its hash differences are disclosed [C-release-freeze].

## 3 Method: the agentic laboratory

The study was executed in a repository laboratory with 3 recorded agent rounds. 2 confirmed claims were recorded before release enrichment, and 1 recorded unsuccessful question is noted [C-release-agents]. The run recorded 43 checked statements, 1 negative result and a cost of 2.87 USD, and each round was described as preregistered in prereg.md [C-methode]. Model fitting followed a preregistered fixed experiment matrix; agents inspected validation summaries and proposed numerical statements that were checked [C-release-agents].

Preregistration timing is not fully compliant. The protocol document existed before computation, but a working-directory error prevented the intended first commit, and a training command failed a row-alignment assertion before any model fit or score inspection. The document and correction were committed before successful experiments, so strict commit-before-first-computation compliance is not claimed [C-release-precommit].

The claim set describes a literature scout whose quotations are recorded with their sources [C-lit1] [C-lit2]. It does not describe how these quotations were verified, so that verification is not characterised here. The claim set also does not describe the integrator, the researcher cascade or the code verifier in operational detail, and this paper does not characterise them further. A red team reviewed source-row alignment, disjoint partitions and rescoring [C-release-redteam].

## 4 Results

**Numerical observation (statistical; solubility_aqsoldb test).** On the fixed solubility_aqsoldb test set, across 20 training seeds, mean MAE ± seed standard deviation is 1.894131 ± 0.048473 for the median baseline, 1.266789 ± 0.039799 for Morgan, 0.899143 ± 0.011470 for descriptors, 0.847962 ± 0.017176 for combined models and 1.891085 ± 0.037153 for shuffled labels [C-release-test-solubility_aqsoldb]. Adding descriptors to Morgan reduces mean test MAE by 33.06% relative to Morgan alone [C-release-test-solubility_aqsoldb]. This is a conditional descriptive comparison with every official test row retained [C-release-test-solubility_aqsoldb].

**Numerical observation (statistical; lipophilicity_astrazeneca test).** On the fixed lipophilicity_astrazeneca test set, across 20 training seeds, mean MAE ± seed standard deviation is 0.963613 ± 0.002624 for the median baseline, 0.730368 ± 0.005053 for Morgan, 0.769887 ± 0.005581 for descriptors, 0.635495 ± 0.007778 for combined models and 1.013711 ± 0.018586 for shuffled labels [C-release-test-lipophilicity_astrazeneca]. Adding descriptors to Morgan reduces mean test MAE by 12.99% [C-release-test-lipophilicity_astrazeneca].

**Numerical observation (statistical; caco2_wang test).** On the fixed caco2_wang test set, across 20 training seeds, mean MAE ± seed standard deviation is 0.586401 ± 0.006519 for the median baseline, 0.479220 ± 0.037340 for Morgan, 0.340505 ± 0.015110 for descriptors, 0.301909 ± 0.015109 for combined models and 0.625006 ± 0.051972 for shuffled labels [C-release-test-caco2_wang]. Adding descriptors to Morgan reduces mean test MAE by 37.00% [C-release-test-caco2_wang].

**Numerical observation (statistical; solubility_aqsoldb validation).** On solubility_aqsoldb validation, Morgan MAE is 1.449784, descriptor MAE is 0.942899 and combined MAE is 0.904329 [C-release-valid-solubility_aqsoldb]. The paired Morgan/combined ratio is 1.603159, with bootstrap 95% interval [1.488537, 1.750759] and nominal one-sided p=0.00005000 [C-release-valid-solubility_aqsoldb]. The comparison passes the preregistered improvement criteria on this fixed dataset [C-release-gate-solubility_aqsoldb]. After adding six negative-control comparisons to an expanded family of nine tests, the Benjamini-Hochberg adjusted p-value is 0.00022499 [C-release-gate-solubility_aqsoldb]. This expanded family is a post-preregistration sensitivity check [C-release-gate-solubility_aqsoldb].

**Numerical observation (statistical; lipophilicity_astrazeneca validation).** On lipophilicity_astrazeneca validation, Morgan MAE is 0.754238, descriptor MAE is 0.760264 and combined MAE is 0.610390 [C-release-valid-lipophilicity_astrazeneca]. The paired Morgan/combined ratio is 1.235665, with bootstrap 95% interval [1.217388, 1.253459] and nominal one-sided p=0.00005000 [C-release-valid-lipophilicity_astrazeneca]. The comparison passes the preregistered criteria, and the expanded-family adjusted p-value is 0.00022499 [C-release-gate-lipophilicity_astrazeneca].

**Numerical observation (statistical; caco2_wang validation).** On caco2_wang validation, Morgan MAE is 0.437256, descriptor MAE is 0.407075 and combined MAE is 0.390865 [C-release-valid-caco2_wang]. The paired Morgan/combined ratio is 1.118689, with bootstrap 95% interval [1.048756, 1.190120] and nominal one-sided p=0.00214989 [C-release-valid-caco2_wang]. The comparison passes the preregistered criteria, and the expanded-family adjusted p-value is 0.00644968 [C-release-gate-caco2_wang].

**Numerical observation (statistical; coverage).** Restricted to strictly valid test structures, combined MAE is 0.846374 for solubility_aqsoldb, 0.635495 for lipophilicity_astrazeneca and 0.301909 for caco2_wang [C-release-coverage-solubility_aqsoldb] [C-release-coverage-lipophilicity_astrazeneca] [C-release-coverage-caco2_wang]. The test sets contain 1997, 840 and 182 rows, respectively [C-release-coverage-solubility_aqsoldb] [C-release-coverage-lipophilicity_astrazeneca] [C-release-coverage-caco2_wang]. Validation sizes vary across seeds because whole-scaffold groups are assigned together, not because rows were silently removed [C-release-coverage-solubility_aqsoldb] [C-release-coverage-caco2_wang].

**Numerical observation (observed; similarity strata).** Exploratory nearest-training Morgan Tanimoto strata use thresholds 0.3 and 0.6 [C-release-segments]. For the combined model, pooled seed-row MAE decreases with similarity for solubility (low 1.007285, medium 0.856216, high 0.703991) and lipophilicity (low 0.934878, medium 0.719061, high 0.524077) [C-release-segments]. For caco2_wang the pattern is not monotone (low 0.303108, medium 0.319482, high 0.265280) [C-release-segments]. The counts reuse test molecules across seeds and are not unique molecule counts [C-release-segments]. These strata neither certify an applicability domain nor explain a mechanism [C-release-segments].

**Proposition 1 (proved_lean).** A Lean 4 core proof establishes that the sum of natural absolute values of integer residuals is zero exactly when every residual is zero [C-release-lean]. Its trusted axioms are propext, Classical.choice and Quot.sound [C-release-lean]. This arithmetic anchor does not certify floating-point model fitting, statistical significance, chemical mechanism or clinical validity [C-release-lean].

**Summary of certified values.** The table below collects the primary certified values. The Benjamini-Hochberg column refers to the expanded nine-test family.

| Endpoint | Morgan test MAE | Combined test MAE | Test MAE reduction vs. Morgan | Validation ratio Morgan/combined [95% interval] | Nominal one-sided p | BH-adjusted p (expanded family) | Claims |
|---|---|---|---|---|---|---|---|
| solubility_aqsoldb | 1.266789 ± 0.039799 | 0.847962 ± 0.017176 | 33.06% | 1.603159 [1.488537, 1.750759] | 0.00005000 | 0.00022499 | [C-release-test-solubility_aqsoldb] [C-release-valid-solubility_aqsoldb] [C-release-gate-solubility_aqsoldb] |
| lipophilicity_astrazeneca | 0.730368 ± 0.005053 | 0.635495 ± 0.007778 | 12.99% | 1.235665 [1.217388, 1.253459] | 0.00005000 | 0.00022499 | [C-release-test-lipophilicity_astrazeneca] [C-release-valid-lipophilicity_astrazeneca] [C-release-gate-lipophilicity_astrazeneca] |
| caco2_wang | 0.479220 ± 0.037340 | 0.301909 ± 0.015109 | 37.00% | 1.118689 [1.048756, 1.190120] | 0.00214989 | 0.00644968 | [C-release-test-caco2_wang] [C-release-valid-caco2_wang] [C-release-gate-caco2_wang] |

## 5 Negative results, preregistration outcome and red-team findings

**Negative result: random splits.** The question whether the solubility validation ratio of 1.603159 persists when scaffold splits are replaced by random splits was tested [C-neg1] [C-release-valid-solubility_aqsoldb]. No claim passed this check [C-neg1]. The persistence of the ratio under random splitting is therefore not shown.

**Shuffled-label controls.** On validation data, the median-baseline/shuffled MAE ratio is 0.961914 for solubility_aqsoldb, with bootstrap 95% interval [0.943069, 0.982480] and nominal p=0.99825009 [C-release-null-solubility_aqsoldb-validation]. For lipophilicity_astrazeneca it is 0.973205, with interval [0.958639, 0.988007] and nominal p=0.99850007 [C-release-null-lipophilicity_astrazeneca-validation]. For caco2_wang it is 0.940133, with interval [0.910216, 0.973390] and nominal p=0.99835008 [C-release-null-caco2_wang-validation]. None meets the improvement gate [C-release-null-solubility_aqsoldb-validation] [C-release-null-lipophilicity_astrazeneca-validation] [C-release-null-caco2_wang-validation]. On the test sets, the ratio is 1.001611 for solubility_aqsoldb, with interval [0.991002, 1.011327] and p=0.39113044 [C-release-null-solubility_aqsoldb-test]. For lipophilicity_astrazeneca it is 0.950579, with interval [0.942861, 0.958420] and p=1.00000000 [C-release-null-lipophilicity_astrazeneca-test]. For caco2_wang it is 0.938232, with interval [0.905757, 0.973442] and p=0.99810009 [C-release-null-caco2_wang-test]. None meets the gate [C-release-null-solubility_aqsoldb-test] [C-release-null-lipophilicity_astrazeneca-test] [C-release-null-caco2_wang-test]. Failure to detect improvement with shuffled labels is not proof of independence [C-release-null-solubility_aqsoldb-validation].

**Preregistration outcome.** The preregistered improvement criteria are met on all three validation comparisons [C-release-gate-solubility_aqsoldb] [C-release-gate-lipophilicity_astrazeneca] [C-release-gate-caco2_wang]. The protocol timing is only partially compliant, as stated in Section 3 [C-release-precommit].

**Red-team findings.** The independent review verified source-row alignment, disjoint molecular and scaffold partitions and rescoring, and reproduced saved seed-1000 predictions [C-release-redteam]. It also found that a mutable prediction table could spoof the original scorer, and that the shared manuscript gate checks numerical token membership rather than semantic truth [C-release-redteam]. Source grounding and frozen prediction hashes now reject the demonstrated target and hash tampering. The final manuscript relies on canonical verified state records rather than on the shared sentence gate alone [C-release-redteam].

**Adversarial numerical checks.** Red-team checks were recorded for the claims on the solubility and lipophilicity ratios. A reversed-direction counterexample gives a reciprocal of approximately 0.624 for solubility [C-admet-R1-RT1]. An equal-performance boundary case gives a ratio of 1.0 [C-admet-R1-RT2]. A reversed-direction counterexample for lipophilicity gives a reciprocal of 0.8095 [C-admet-R3-RT1]. A misassigned shuffled-model case has independent value 1.030186069 [C-admet-R3-RT2]. Each is recorded with the outcome "nicht bestanden" (not passed). The claim texts do not specify which party failed, so no further inference is drawn from these outcomes [C-admet-R1-RT1] [C-admet-R1-RT2] [C-admet-R3-RT1] [C-admet-R3-RT2].

**Earlier agent statements.** Interpretations recorded by the agent during the run are not used as results in this paper [C-admet-R1-I] [C-admet-R3-I].

## 6 Limitations and open questions

This paper does not show the following:

- **Prospective validity.** The pilot lacks prospective temporal validation, independent new assays, clinical evaluation and external expert review [C-release-limitations].
- **Comparison with tuned competitors.** No comparison against competitive tuned models is reported, and hyperparameters are fixed [C-release-limitations].
- **Causal mechanism.** Descriptor effects cannot identify causal chemical mechanisms [C-release-limitations].
- **Patient safety.** A held-out benchmark result is evidence about the distributed assay targets, not about patient safety [C-release-limitations].
- **Independence of evidence.** The splits overlap, test molecules are reused, and the data are public labels with assay heterogeneity. The intervals and p-values are therefore conditional sensitivity summaries [C-release-inference] [C-release-abstract].
- **Single snapshot.** The study uses a single public benchmark snapshot [C-release-limitations].
- **Platform.** The run is local CPU research. Databricks, Unity Catalog and Spark have not been provisioned or tested, and no live cloud deployment is claimed [C-release-platform].
- **Agent efficiency.** No agent-discovery speedup was measured [C-release-agents].
- **Contamination.** The exposure check cannot certify absence of LLM training-corpus contamination [C-release-trust].
- **Invalid structures.** Two invalid test structures are retained through a median fallback, and this choice is a documented amendment rather than a validated chemical treatment [C-release-invalid].

The open questions are whether the endpoint-specific effects survive replication, random-split analysis, stronger baselines and a specific mechanism or methodological improvement [C-release-novelty] [C-neg1]. No novelty is claimed beyond what the claims support: the contribution is an auditable endpoint-specific ablation with falsification checks [C-release-novelty].

**Related work.** Several studies with literature sources bear on these questions. Scaffold-based splits can inflate apparent error: a structural frontier split increased equally weighted primary error relative to a scaffold control, with a taskwise median of 87.0% [C-lit1] [C-lit2]. Split construction and label provenance are treated as evaluation constraints in their own right [C-lit5]. Among TDC ADMET leaderboard models, only three reproduced their reported performance, and data leakage was traced in several models [C-lit6] [C-lit7]. Optimisation on the public test set can substantially inflate metrics and rank [C-lit8]. Feature families (Morgan fingerprints, RDKit descriptors and SMILES bigrams) have been compared across learning algorithms, and predictive performance was found to depend jointly on representation and algorithm [C-lit11] [C-lit12]. On a related comparison, a 166-bit MACCS fingerprint nearly matched a 2048-bit Morgan fingerprint, with ΔAUC of −0.012 [C-lit26]. Applicability domains have been operationalised via maximum reference Tanimoto similarity [C-lit30]. The references cited in this paper were verified for existence, title and DOI only; this verification does not reproduce the findings of those papers [C-release-ref-0] [C-release-ref-1] [C-release-ref-2] [C-release-ref-3].

---
*Verification log (automatic):* 59 claim IDs cited; unsupported statements per writing round: 18 → 1; 3 sentences removed; remaining violations: 0. Claim texts and evidence: `paper_belege.json`.
