# Assumptions register

| ID | Assumption | Used by | Testable? | Status / test |
|---|---|---|---|---|
| A1 | Small vocabularies (V <= 8) expose the same qualitative multi-draft phenomena as real vocabularies | (B) | partially | consistent with Hu et al. 2025 at vocabulary sizes in the thousands (evidence.md); our numbers are NOT claimed for large V |
| A2 | Logit bound B is the right parameter for attention cost | (A) | yes, theory | matches the sharp transition of Alman & Song 2023 (evidence.md) |
| A3 | Relative entrywise error eps is the relevant error notion for softmax attention | (A) | yes | relative entrywise error eps on exp(QK^T) gives softmax rows with relative error <= 2 eps / (1 - eps) (row normalisation); absolute-error variant also supported by the verifier |
| A4 | i.i.d. acceptance alpha per position for the draft-length model | (B) gamma | no (model) | standard modelling assumption of Leviathan et al.; results are exact only under it |
| A5 | Synthetic attention model (sinks, heavy hitters, locality, logit scale 6) is a meaningful test bed for eviction | (C) | partially | negative control (structure-free model) preregistered; results are labelled synthetic and never claimed for LLMs |
| A6 | Random instances (Dirichlet / Zipf, denominators 1000) are representative | (B) tables | no | stated as the instance distribution; worst cases reported separately |
| A7 | Agents' knowledge of the literature does not bias truth | all | yes | irrelevant for truth: only the code verifier accepts claims; contamination affects only which questions are asked |
