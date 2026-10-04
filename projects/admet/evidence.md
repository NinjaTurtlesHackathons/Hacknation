# ADMET evidence register

Scout literature pass, 2026-10-04. Scope: representation baselines, chemical generalization, prediction reliability and applicability domains. Literature findings only; no project model results and no novelty claim. Quotes below are short source excerpts; tool IDs identify the retrieval. DOI/title pairs marked verified were visible together in primary-paper publisher, PubMed or PMC records. A primary paper mirrored in PubMed/PMC remains the cited research source. This is a focused seed-and-one-hop pass, not an exhaustive systematic review.

## Recent layer (approximately five years)

### E1 — Representation comparison and activity cliffs

- **Verified title/DOI:** Deng et al. (2023), *A systematic study of key elements underlying molecular property prediction*, [10.1038/s41467-023-41948-6](https://doi.org/10.1038/s41467-023-41948-6).
- **Tool evidence:** `turn7search2`, `turn7search3`, Crossmark `turn7search6`; [primary text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10575948/). Publisher direct-open failed; searchable PMC text and PubMed metadata succeeded.
- **Quote:** “activity cliffs can significantly impact model prediction.”
- **Strength:** Peer-reviewed extensive empirical comparison, including fixed descriptors, SMILES and graph representations; not a theorem or prospective validation of our dataset.
- **Mechanism:** Representation choice, sample size, label distribution and activity cliffs jointly affect evaluation. The paper challenges treating learned representations as automatically superior and examines intra-/inter-scaffold behavior.
- **Transfer:** Include fingerprint/descriptor models as serious baselines; inspect errors within structurally similar groups, not only between held-out scaffolds.
- **Limit:** Benchmark-level conclusions are task dependent. A scaffold split alone does not establish arbitrary chemical-space generalization.

### E2 — Therapeutics benchmark contract

- **Verified title:** Huang et al. (2021), *Therapeutics Data Commons: Machine Learning Datasets and Tasks for Drug Discovery and Development*. [Official NeurIPS proceedings](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/4c56ff4ce4aaf9573aa5dff913df997a-Abstract-round1.html); [arXiv:2102.09548](https://arxiv.org/abs/2102.09548). No journal DOI asserted.
- **Tool evidence:** `turn3search1`, `turn3search13`, `turn3academia15`.
- **Quote:** “robust generalization to novel data points.”
- **Strength:** Peer-reviewed dataset/benchmark paper with selected experiments.
- **Mechanism:** A meaningful task combines a curated dataset, split, metrics and systematic evaluation; ADMET is a collection of endpoints, not one label.
- **Transfer:** Record endpoint units, source version, duplicate handling, split IDs and endpoint metric before fitting.
- **Limit:** Published resource counts describe the paper's release, not current availability. A public leaderboard does not verify a bespoke data preprocessing pipeline.

### E3 — Explicit domain checks alongside calibrated uncertainty

- **Verified title/DOI:** Hosni, Gillet and Marchese Robinson (2026), *Explicit Applicability Domain Calculations Can Help Determine When Uncertainty Estimates Are Less Reliable*, [10.1021/acsomega.5c11875](https://doi.org/10.1021/acsomega.5c11875).
- **Tool evidence:** `turn6search3`; [primary text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12854501/). Search returned title, authors, DOI and abstract; direct PMC opening encountered a browser challenge.
- **Quote:** “their performance is limited when they are applied to compounds sampled from a different distribution”
- **Strength:** Peer-reviewed, directly relevant empirical primary research; retrieved abstract supports the distribution-shift warning, not every internal experiment.
- **Mechanism:** Explicit AD assessment and calibrated uncertainty are distinct checks. Conformal regression and Venn-ABERS can lose their intended reliability under changes in training/calibration versus query distributions.
- **Transfer:** Evaluate coverage and error separately by similarity/domain strata; expose low-domain-support predictions rather than interpreting narrow uncertainty as universally trustworthy.
- **Limit:** No universal similarity threshold is established by the retrieved excerpt. Any project cutoff must be selected on development data and evaluated on held-out data.
- **Prior-art boundary:** Combining explicit AD with uncertainty already has direct published precedent; it is not by itself a novelty claim.

## Canonical same-problem and analogous layers

### E4 — Established molecular benchmark

- **Verified title/DOI:** Wu et al., *MoleculeNet: a benchmark for molecular machine learning* (online 2017; volume 2018), [10.1039/C7SC02664A](https://doi.org/10.1039/C7SC02664A).
- **Tool evidence:** `turn2search1`, `turn2search3`; [publisher primary paper](https://pubs.rsc.org/en/content/articlelanding/2017/sc/c7sc02664a).
- **Quote:** “Learnable representations still struggle to deal with complex tasks under data scarcity and highly imbalanced classification.”
- **Strength:** Peer-reviewed benchmark with implementations and split/metric conventions.
- **Mechanism:** Controlled comparisons require shared datasets and meaningful splits. Model success depends on the task, data scarcity and imbalance.
- **Transfer:** Evaluate the simplest working endpoint predictor, then fingerprints/descriptors, before expensive representations; choose imbalance-sensitive metrics when appropriate.
- **Limit:** Its broad learned-representation results do not prove superiority for every ADMET endpoint or split.

### E5 — Fixed versus learned representation and scaffold proxy

- **Verified title/DOI:** Yang et al. (2019), *Analyzing Learned Molecular Representations for Property Prediction*, [10.1021/acs.jcim.9b00237](https://doi.org/10.1021/acs.jcim.9b00237).
- **Tool evidence:** `turn2search0`, `turn2search2`, author PDF `turn2search13`.
- **Quote:** “fingerprint models can outperform learned representations”
- **Strength:** Peer-reviewed broad comparison including public and industrial datasets.
- **Mechanism:** Bond-directed message passing can be combined with computed features; representation and tuning effects depend on sample size. Scaffold splitting approximates some temporal evaluations, while chronological data remain preferable when available.
- **Transfer:** Use fingerprint models as substantive baselines and compare both random and scaffold splits; use temporal evaluation when timestamps actually support it.
- **Limit:** Scaffold and temporal splits are not interchangeable guarantees. Hybrid features and strong tuning are existing methods, not novelty evidence.

### E6 — Prospective-prediction evaluation

- **Verified title/DOI:** Sheridan (2013), *Time-split cross-validation as a method for estimating the goodness of prospective prediction*, [10.1021/ci400084k](https://doi.org/10.1021/ci400084k).
- **Tool evidence:** `turn4search0`; [primary abstract](https://pubmed.ncbi.nlm.nih.gov/23521722/).
- **Quote:** “This estimate of predictivity can be optimistic or pessimistic compared to true prospective prediction”
- **Strength:** Peer-reviewed empirical comparison of validation selection strategies.
- **Mechanism:** Future queries differ from random held-out training-like compounds. Validation estimates depend on test selection, not only the algorithm.
- **Transfer:** Label random-split estimates as interpolation-style evidence; prefer real acquisition-time holdouts for prospective claims.
- **Limit:** Time-split behavior in this study is not a universal bound on other datasets. Dataset row order is not a validated timestamp.

### E7 — Reliability scoring is already an established QSAR task

- **Verified title/DOI:** Toplak et al. (2014), *Assessment of machine learning reliability methods for quantifying the applicability domain of QSAR regression models*, [10.1021/ci4006595](https://doi.org/10.1021/ci4006595).
- **Tool evidence:** `turn7search1`; [primary abstract](https://pubmed.ncbi.nlm.nih.gov/24490838/).
- **Quote:** “the quality of reliability scoring methods is sensitive to data set characteristics”
- **Strength:** Peer-reviewed comparison of ten reliability scores over twenty public continuous-response QSAR datasets.
- **Mechanism:** Estimated local prediction error can outperform similarity-only confidence scores; the scoring quality depends on the regression method and dataset.
- **Transfer:** Compare nearest-training similarity against a learned or ensemble reliability estimate; report whether rejection improves error at a declared retained coverage.
- **Limit:** Distance is a proxy for support, not a certificate of error; empirical improvement must be demonstrated per endpoint.

### E8 — UQ method comparison

- **Verified title/DOI:** Hirschfeld et al. (2020), *Uncertainty Quantification Using Neural Networks for Molecular Property Prediction*, [10.1021/acs.jcim.0c00502](https://doi.org/10.1021/acs.jcim.0c00502).
- **Tool evidence:** `turn3search2`, primary preprint `turn3academia16`; [PubMed](https://pubmed.ncbi.nlm.nih.gov/32702986/).
- **Quote:** “none of the methods we tested is unequivocally superior to all others”
- **Strength:** Peer-reviewed empirical UQ comparison on five regression benchmarks with complementary metrics.
- **Mechanism:** A uncertainty number needs validation as an error-ranking and calibration tool; methods perform differently across datasets.
- **Transfer:** Evaluate both interval coverage/width and ranking of held-out errors. Ensemble spread alone is not validated reliability.
- **Limit:** Study covers regression and a specific method set; cannot directly certify classification probabilities or new endpoints.

### E9 — Analogous canonical type: statistical prediction sets

- **Verified title:** Shafer and Vovk (2008), *A Tutorial on Conformal Prediction*, JMLR 9:371–421. [Official primary paper](https://jmlr.csail.mit.edu/papers/v9/shafer08a.html). No DOI needed or asserted.
- **Tool evidence:** `turn3search0`, `turn3search12`.
- **Quote:** “sampled independently from the same distribution”
- **Strength:** Foundational mathematical treatment, with explicit assumptions.
- **Shared structure:** Molecular regression and generic conformal inference both map observed examples into prediction sets using conformity/error scores.
- **Mechanism:** Under appropriate exchangeability assumptions, calibration can support marginal prediction-set coverage without assuming a correct parametric model.
- **Transfer:** Reserve calibration data, state the assumptions, and measure coverage on held-out scaffold or temporal groups.
- **Limit:** Marginal coverage does not imply coverage for every molecule or subgroup. Standard guarantees do not automatically survive chemical distribution shift; their use in a scaffold holdout requires empirical assessment and qualified claims.

## Pre-2000 layer

### E10 — Chemical structural groups

- **Verified title/DOI:** Bemis and Murcko (1996), *The properties of known drugs. 1. Molecular frameworks*, [10.1021/jm9602928](https://doi.org/10.1021/jm9602928).
- **Tool evidence:** `turn6search0`; [primary abstract](https://pubmed.ncbi.nlm.nih.gov/8709122/).
- **Quote:** “group the atoms of each drug molecule into ring, linker, framework, and side chain atoms.”
- **Strength:** Peer-reviewed structural analysis of a drug collection; foundational structural grouping rather than modern ML validation evidence.
- **Mechanism:** Framework abstractions group related molecular structures and reveal repeated families.
- **Transfer:** Keep related framework groups together when testing transfer across chemical families; document the exact scaffold implementation and treatment of acyclic compounds.
- **Limit:** Framework equality ignores potentially consequential substituent differences. Group disjointness does not eliminate activity cliffs or guarantee dissimilarity under every chemical representation.

## Methodological synthesis for the integrator

These are design implications inferred from the sources, not measured project findings:

1. Define the endpoint, units, label provenance and split before training. The verifier is held-out experimental labels; it cannot establish in-vivo safety or clinical efficacy.
2. Compare mean/majority prediction, fingerprint plus simple learner, and any more complex model on identical holdouts. Representation complexity is not evidence of improvement (E1/E4/E5).
3. Audit canonicalized structure duplicates and scaffold leakage. Add random and scaffold results with distinct interpretations; use actual acquisition dates if available (E5/E6/E10).
4. Treat chemical similarity, calibrated uncertainty and error ranking as separate observable quantities (E3/E7/E8/E9).
5. For a refusal/reliability feature, preregister retained coverage versus error and evaluate across domain strata. Never advertise a selectively filtered error without also reporting rejected coverage.
6. A combination of fingerprints, ensemble uncertainty, similarity-based refusal and conformal calibration has substantial prior art. A project contribution would require a specific executed comparison and a narrower demonstrated improvement; none is claimed here.

## Retrieval limitations

This pass did not reproduce any cited experiment, independently re-evaluate every DOI through Crossref API, inspect every supplement, or establish regulatory acceptance. Direct publisher/PMC opens sometimes failed, although searchable primary article records and abstracts were available. Title/DOI validation confirms bibliographic identity, not correctness of all paper claims. Current model rankings and resource download availability require a separate live check.
