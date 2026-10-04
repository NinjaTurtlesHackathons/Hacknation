# Decisions: expressivity domain

| ID | Time | Decision | Alternatives | Evidence | Reversible? | Owner |
|---|---|---|---|---|---|---|
| EX1 | Sun 02:00 | Base branch `expressivity` on the framework commit b636a25 (common base of all research branches); own top-level folder `expressivity/` plus a 2-line registry shim `asd/domains/expressivity_domain.py` and `projects/expressivity/`; shared core files untouched | base on `main` (outdated, no framework) or on `paper-bell` (another project's state) | git graph: ML_3-(CJ), algo-efficiency and paper-bell all branch from b636a25; algo-efficiency used the same layout (its decision AE7) | yes | user (dirigent), Claude |
| EX2 | Sun 02:00 | All files of this domain in English | German like the rest of the repo | repository author's global rule (everything that lands in a repository is English); same as algo-efficiency AE8 | yes | Claude |
| EX3 | Sun 02:05 | Oracles installed locally: GAP 4 (conda-forge, exact cyclotomic character tables, SmallGroups library) and Lean 4 + Mathlib (elan, Mathlib cache) | no external oracle; numerical character tables only | skill module F: "Orakel (Lean, Intervallarithmetik, exakte Rechnung)" and "Abgleich mit unabhängigen Bibliotheken" | yes | Claude |
| EX4 | Sun 02:10 | Mode Full; jury type Quant/Science; modules F (mathematics) and B (ML validation) | Lite | 4-person team, 21 h, open problem in a foreign field (skill section 0) | yes | Claude |
| EX5 | Sun 02:10 | Scout and Analogist started in parallel as separate subagents (Scout without solution ideas, Analogist with only the functional abstraction) | do the literature myself | skill section 3 (asymmetric roles) | - | Claude |
