# ADMET live-demo script

1. Problem: drug candidates need reliable predictions of assay-level properties; this pilot studies three ADMET regression endpoints.
2. Show preregistration and its two disclosed deviations: failed index initialization before fit; two invalid-SMILES median fallbacks.
3. Run verifier selftest; show rejection of fabricated MAE, NaN and agent-provided tolerance.
4. Show coverage audit: all 22 endpoints, all official test rows preserved in the three modeled tasks.
5. Open demo.html; read test evaluation table and claims/gates only. Three figures: reductions against fixed Morgan baseline; no leaderboard claim.
6. Show descriptor-only ablation: benefits differ by endpoint; descriptors alone are weaker than Morgan on fixed lipophilicity test.
7. Show shuffled-target controls and repeated-split limitations; a tiny solubility null improvement is retained and not significant.
8. Show tamper rejection and canonical manuscript support log.
9. End with the evidence boundary: prospective assays and competitive tuned baselines are still needed for a strong scientific publication.

Technical video: domain adapter -> frozen models -> prediction artifacts -> source-grounded scorer -> claim state -> deterministic paper/demo.
Team video: Scout, Analogist, Red-Team and main integrator have separate artifacts; actual people/authorship must be supplied by the team before public submission.
Live demo video: steps 3–8 above. No video recording, outreach or public submission has been performed by this run.

Moat check: one hour copies the feature combination; one day copies a prototype; the auditable evidence trail and execution checks require careful reproduction but are not a scientific novelty moat.
