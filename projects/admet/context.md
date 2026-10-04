# ADMET context

Owner: user, autonomous execution authorized. Mode Full; jury type Quant/Science. Supplied challenge wording: “Agentic Scientific Discovery”; full official jury rubric unavailable, UNVERIFIED. Domain only ADMET. Framework from origin/paper-bell; original main reaction benchmark preserved.

## Model
x_i: molecular SMILES, dimensionless string; y_i: endpoint assay target (TDC units: solubility log mol/L, lipophilicity log-ratio, Caco2 transformed permeability target as distributed). f(x_i): predicted target. e_i=|f(x_i)-y_i| >=0, same target unit. M=(1/n) sum e_i. Objective: minimize held-out M, with fixed method menu and untouched test until freeze. Ratio R=M_Morgan/M_combined, dimensionless. Features cannot use Y, Drug_ID or test statistics. No clinical efficacy implication.

Axioms: MAE nonnegative, zero iff exact predictions (known arithmetic); row permutation invariance tested; feature invariance to opaque identifier changes tested; fixed verifier tolerances; missing/invalid observations explicitly block rather than impute. Bootstrap and sign-flip assumptions remain empirical, overlapping splits documented. Fermi: 3 endpoints x20 seeds x4 learned/control configurations =240 fits plus naive baselines; roughly minutes to tens of minutes, CPU measured rather than asserted.

TRIZ tension: faster exploratory research vs honest fixed evaluation; resolve by validation-only agent operations and frozen final scorer.

Canonical problem: supervised regression with scaffold distribution shift. Baseline median and fixed fingerprint gradient boosting. Coverage: all 22 datasets audited, models only three. Fixed primary metric MAE. Gate3 criteria in prereg. Fallback: report conditional representation benefits or failed hypotheses; never manufacture leaderboard impact.

Formal transfer tier: (empty, infinity). No imported theorem from analogy. Module B; conformal omitted per CLAUDE.md, no exchangeability guarantee. Calibration here: regression residual bias and error by similarity segment. Databricks/Unity Catalog not provisioned; local tables and optional integration only, not claimed live.
