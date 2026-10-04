# Assumptions register

| ID | Assumption | Used by | Testable? | Status / test |
|---|---|---|---|---|
| A1 | Finitely many reachable states in an exact realisation (true for every finite-state construction; excludes realisations whose states drift without bound) | L2, L5 (necessity) | no (modelling) | stated in every theorem; trained models are tested empirically instead (prereg.md) |
| A2 | Transitions depend only on the current token (no short convolution, no input-dependent mixing of several tokens) | L2 | partially | the experiments use token-local transitions exactly; production DeltaNet/DeltaProduct use a short convolution, which is outside the theorem (limitation) |
| A3 | One layer; readout from the state only (arbitrary function) | L2, L3 | yes | multi-layer results are not claimed; one-layer models in the experiments |
| A4 | Exact real arithmetic | L2, L3 | partially | certificates are exact (Q, Q(sqrt 5)); trained models run in float32 and are judged by length generalisation (4x and 8x the training length) |
| A5 | Word-problem formulation: target g_t = s_t ... s_1 at every position; alphabet = a generating subset of G | all | no (definition) | the same definition as in the state-tracking literature (evidence.md); alphabets are stated explicitly per task |
| A6 | Length generalisation of a trained model is evidence that it found an exact (or near-exact) finite-state solution; failure for k < h* is predicted by the theorem only asymptotically | prereg H-EX1 | yes | test at 4x and 8x training length; negative control with random targets; LSTM positive control |
| A7 | The agents' prior knowledge of the literature does not bias truth | lab loop | yes | irrelevant for truth: only the code verifier accepts claims; contamination can only bias which questions are asked |
| A8 | Small groups (order <= 120 in the atlas, <= 120 in the experiments) show the phenomena that matter for the architecture debate | atlas, experiments | partially | A5 and S5 (the canonical NC1-complete examples) are included; nothing is claimed for larger groups |
