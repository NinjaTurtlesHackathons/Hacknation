---
title: "Beyond the Hopfield chain: certified bounds and counterexamples for kinetic proofreading networks with two bound states"
author:
  - Colin Ji
  - Laurenz Thümmler
  - Noah Schittenhelm
  - Ali Suleman
date: "ETH Zürich · Preprint"
documentclass: article
classoption: [twocolumn, 10pt]
geometry: margin=1.7cm
lang: en
header-includes: |
  \usepackage{newunicodechar}
  \newunicodechar{η}{\ensuremath{\eta}}
  \newunicodechar{Δ}{\ensuremath{\Delta}}
  \newunicodechar{σ}{\ensuremath{\sigma}}
  \newunicodechar{μ}{\ensuremath{\mu}}
  \newunicodechar{≥}{\ensuremath{\geq}}
  \newunicodechar{≤}{\ensuremath{\leq}}
  \newunicodechar{×}{\ensuremath{\times}}
  \newunicodechar{→}{\ensuremath{\to}}
  \newunicodechar{≈}{\ensuremath{\approx}}
  \newunicodechar{−}{\ensuremath{-}}
  \newunicodechar{·}{\ensuremath{\cdot}}
  \newunicodechar{∈}{\ensuremath{\in}}
  \newunicodechar{…}{\ensuremath{\ldots}}
  \newunicodechar{²}{\ensuremath{^{2}}}
  \newunicodechar{³}{\ensuremath{^{3}}}
  \newunicodechar{√}{\ensuremath{\surd}}
  \newunicodechar{±}{\ensuremath{\pm}}
  \newunicodechar{⁻}{\ensuremath{^{-}}}
  \newunicodechar{¹}{\ensuremath{^{1}}}
  \newunicodechar{₀}{\ensuremath{_{0}}}
  \newunicodechar{₁}{\ensuremath{_{1}}}
  \newunicodechar{₂}{\ensuremath{_{2}}}
  \newunicodechar{α}{\ensuremath{\alpha}}
  \newunicodechar{β}{\ensuremath{\beta}}
  \newunicodechar{γ}{\ensuremath{\gamma}}
  \newunicodechar{ε}{\ensuremath{\varepsilon}}
  \newunicodechar{τ}{\ensuremath{\tau}}
  \newunicodechar{ν}{\ensuremath{\nu}}
  \newunicodechar{∞}{\ensuremath{\infty}}
  \newunicodechar{≠}{\ensuremath{\neq}}
  \newunicodechar{π}{\ensuremath{\pi}}
  \newunicodechar{λ}{\ensuremath{\lambda}}
---



## Abstract

An enzyme discriminates a right substrate R from a wrong substrate W that traverse the same Markov network. W unbinds from bound states faster by a factor $e^{\Delta}$. For the linear Hopfield chain with n = 2 proofreading stages, we certify symbolically that the error rate satisfies η ≥ $e^{-3\Delta}$ for all positive rates and all fuel potentials \textsubscript{[C-proofreading-R9]}. This makes the reproduction of Hopfield's bound rigorous \textsubscript{[C-fakt-neuheit]}. Our main new result concerns networks with two bound states. The generator produces 92 rule-conforming topologies, 4 of them degenerate, leaving 88 \textsubscript{[C-fakt-familie]}. Of these, 50 provably obey η ≥ $e^{-2\Delta}$, 3 have exactly certified counterexamples below it (fam2_66, fam2_9, fam2_11), and 35 remain open \textsubscript{[C-fakt-klassifikation]}. We also give exactly certified achievable points of the chain at finite dissipation and speed, and we report negative results, red-team findings and deviations from the preregistration.

## 1 Introduction

**Question.** Is the Hopfield-type bound η ≥ $e^{-(n+1)\Delta}$ a property of the chain only, or does it hold for general proofreading networks with the same number of bound states? Hopfield showed that a simple kinetic pathway, driven strongly but nonspecifically, increases specificity beyond the equilibrium limit \textsubscript{[C-lit8]}. Later work addresses error--cost bounds \textsubscript{[C-lit10]}, Pareto fronts \textsubscript{[C-lit12]}\textsubscript{[C-lit13]}\textsubscript{[C-lit1]} and scaling relations \textsubscript{[C-lit22]}. Whether the bound $e^{-2\Delta}$ is universal for two bound states is classified here \textsubscript{[C-fakt-klassifikation]}. The classification and its counterexamples were not found in the retrieved literature \textsubscript{[C-fakt-neuheit]}.

**Contribution.** A verifier-gated agentic laboratory produced exact rational or symbolic certificates. These cover the chain bound, the achievable points of the chain, and a classification of the two-bound-state family \textsubscript{[C-methode]}.

**Summary of results.**

- Chain with n = 2: η ≥ $e^{-3\Delta}$ for all positive rates and fuel potentials (Theorem A) \textsubscript{[C-proofreading-R9]}.
- Two bound states: the bound $e^{-2\Delta}$ is not universal \textsubscript{[C-fakt-klassifikation]}. The 88 non-degenerate networks split into 50 proved, 3 refuted and 35 open (Theorems B and C) \textsubscript{[C-fakt-klassifikation]}.
- Exact achievable points of the chain at finite σ and v (Theorems D--F) \textsubscript{[C-proofreading-R1]}\textsubscript{[C-proofreading-R2]}\textsubscript{[C-proofreading-R10]}.
- The reported kink in the Pareto front of hopfield_n1 is an optimizer artifact \textsubscript{[C-proofreading-R1-RT1]}\textsubscript{[C-proofreading-R1-RT2]}.
- Negative results: the claimed necessity of a fuel-driven discard feature remains unresolved \textsubscript{[C-neg1]}. The L2c success criterion was missed \textsubscript{[C-fakt-praereg]}.

## 2 Model

The assumptions that carry the results are as follows.

- Both substrates traverse the same Markov network. Every edge has a reverse edge. Local detailed balance holds, and cycle affinities arise only from the fuel potentials μ per activation and μ_P per product (as stated in the task specification).
- Log-rates lie in [-10, 10], so rational rates lie in [$e^{-10}$, $e^{10}$] \textsubscript{[C-proofreading-R1]}. Symbolic bounds hold for all positive rates, independent of this range \textsubscript{[C-proofreading-R9]}.
- Observables are the error rate η = J_W/J_R, the dissipation σ in kT per product, and the speed v = J_R.
- Notation: D = $e^{\Delta}$ and G = e^μ \textsubscript{[C-proofreading-R9]}.
- The family "bound states ≤ 2" has one unbound state and an edge catalog fixed by the model rules \textsubscript{[C-proofreading-R11]}. Networks with no possible net production (η = 0/0) are degenerate and excluded \textsubscript{[C-fakt-familie]}.
- Admissible edge attributes are constrained. For instance, a discriminating edge is allowed only for bound → unbound transitions \textsubscript{[C-proofreading-R7-RT2]}.

## 3 Method: the verifier-gated agentic lab

The pipeline has the following components.

- **Scout.** Literature search over 2752 retrieved sources (arXiv, Europe PMC, Crossref, citation chain) \textsubscript{[C-fakt-recherche]}. 2502 were screened \textsubscript{[C-fakt-recherche]}. This gave 158 findings whose verbatim quote was confirmed by code in the abstract \textsubscript{[C-fakt-recherche]}. All 11 classic searches had hits \textsubscript{[C-fakt-recherche]}.
- **Integrator and preregistration.** Every round was preregistered before the experiment (prereg.md) \textsubscript{[C-methode]}. Preregistration H6 (commit 6184672) preceded the first run, and amendments are dated \textsubscript{[C-fakt-praereg]}.
- **Researcher agents.** They propose claims and parameters. Their interpretations are stored as hypotheses and are never used as results (claims with suffix -I).
- **Code verifier.** It issues two kinds of certificate: (a) exact rational reachability, and (b) symbolic positivity proofs (a rational function N/D whose coefficients are all nonnegative) \textsubscript{[C-proofreading-R9]}. It passes its self-test on 18 of 18 cases (true, false, borderline, rule violations) \textsubscript{[C-fakt-selbsttest]}.
- **Red team.** It attacks each claim with a counter-claim. An attack may fail, may be inconclusive, or may be non-executable.
- **Budget.** The lab ran 12 rounds with 11 verified statements and 1 negative result, at a cost of 3.53 USD \textsubscript{[C-methode]}.

## 4 Results

"Theorem" is used only for computed_rigorous claims. Every claim below carries this evidence level; none is proved in Lean.

**Theorem A (Hopfield bound, n = 2; computed_rigorous).** For hopfield_n2, η ≥ 1 * $e^{-3\Delta}$ for all positive rates and all fuel potentials μ, μ_P ≥ 0 \textsubscript{[C-proofreading-R9]}. The certificate is a symbolic positivity proof, independent of the rate range \textsubscript{[C-proofreading-R9]}. The difference η − $e^{-3\Delta}$ is N/D with 1374 and 2048 terms, all coefficients nonnegative \textsubscript{[C-proofreading-R9]}. This is a reproduction of Hopfield's bound, made rigorous for all rates \textsubscript{[C-fakt-neuheit]}.

**Theorem B (bound in a subfamily; computed_rigorous).** For 50 topologies of the family "bound states ≤ 2", η ≥ 1/D² for all positive rates and fuel, where D = $e^{\Delta}$ \textsubscript{[C-proofreading-R11]}. An earlier partial list with 3 of 3 members was proved \textsubscript{[C-proofreading-R6]}\textsubscript{[C-proofreading-R7]}.

**Theorem C (counterexamples; computed_rigorous).**

- For fam2_66 there exist rational rates in [$e^{-10}$, $e^{10}$] with local detailed balance and η ≤ 0.0001, v ≥ 0.0001 \textsubscript{[C-proofreading-R4]}. The exact certificate gives η = 5.082802e-07, σ = 8.341626 kT per product and v = 1.4746e-03 \textsubscript{[C-fakt-fam66]}.
- The edges of fam2_66 are binding at C0, fuel-driven conversion C0→C1, fuel-driven discard from C1, and product formation from C1 \textsubscript{[C-fakt-fam66]}.
- Two further exact counterexamples with η ≤ 0.0001 exist for fam2_11 and fam2_9 \textsubscript{[C-proofreading-R12]}\textsubscript{[C-fakt-r12]}.
- Consequently the bound $e^{-2\Delta}$ is not universal for two bound states \textsubscript{[C-fakt-klassifikation]}. The complete classification is 50 proved, 3 refuted and 35 open \textsubscript{[C-fakt-klassifikation]}.

*Interpretation (not a theorem).* In fam2_66 the best candidate mechanism is fuel-driven unbinding from the product-forming state (editing), which is qualitatively known \textsubscript{[C-fakt-neuheit]}. Whether this feature is necessary is unresolved (see the negative results below) \textsubscript{[C-neg1]}.

**Theorem D (achievable points of hopfield_n1, I; computed_rigorous).** There exist rational rates with local detailed balance and simultaneously η ≤ 0.0004, σ ≤ 6.0 kT per product and v ≥ 0.001 \textsubscript{[C-proofreading-R1]}. The exact point is η = 3.650169e-04, σ = 6.000000 kT, v = 1.0417e-01 \textsubscript{[C-proofreading-R1]}.

**Theorem E (achievable points of hopfield_n1, II; computed_rigorous).** The following points are exactly certified \textsubscript{[C-proofreading-R2]}.

- η = 3.156120e-04 at σ = 6.000000 kT with v = 2.4255e-02 \textsubscript{[C-proofreading-R2]}.
- η = 2.043712e-04 at σ = 3.079633 kT with v = 2.2592e-03 \textsubscript{[C-proofreading-R2]}.

Both are admissible under η ≤ 0.0004 and v ≥ 0.001 with σ_max = 8 \textsubscript{[C-proofreading-R2]}. The second is also admissible with σ_max = 6 \textsubscript{[C-proofreading-R2-RT2]}.

**Theorem F (further achievable points, hopfield_n1; computed_rigorous).**

- η = 1.189200e-04 at σ = 4.271813 kT with v = 1.0000e-03, satisfying η ≤ 0.0002 and σ ≤ 10 kT \textsubscript{[C-proofreading-R10]}.
- η = 1.095823e-04 at σ = 0.006292 kT with v = 9.1487e-09, satisfying η ≤ 0.00012 and σ ≤ 0.2 kT \textsubscript{[C-proofreading-R8]}.
- η = 5.909757e-03 at σ = 3.998555 kT with v = 7.1214e-03, satisfying η ≤ 0.01 and v ≥ 0.001 \textsubscript{[C-proofreading-R3]}.

**Remark on the Pareto upper curve.** The feasible set grows with σ_max, so min η(σ_max) is non-increasing \textsubscript{[C-proofreading-R1-RT1]}. The point of Theorem D remains admissible at σ_max = 8 and σ_max = 20, which rules out a jump to η > 0.008 for σ ≥ 8 \textsubscript{[C-proofreading-R1-RT1]}\textsubscript{[C-proofreading-R1-RT2]}. The reported kink, which would parallel the dynamical phase transition of the mixed regime in the literature \textsubscript{[C-lit2]}, is therefore an optimizer artifact for hopfield_n1 \textsubscript{[C-proofreading-R1-RT1]}.

## 5 Negative results and red-team findings

- **Necessity of a fuel-driven discard (L3).** No claim passed the check \textsubscript{[C-neg1]}. The red-team candidates without a discard at the product state were not executable (TypeError: Invalid NaN comparison) \textsubscript{[C-proofreading-R7-RT1]}. A second borderline topology violated the model rules (a discriminating edge is allowed only for bound → unbound) \textsubscript{[C-proofreading-R7-RT2]}.
- **Failed or non-executable red-team attacks.** Several attacks against certified claims did not conclude, because of NaN comparisons or index errors \textsubscript{[C-proofreading-R4-RT1]}\textsubscript{[C-proofreading-R4-RT2]}\textsubscript{[C-proofreading-R9-RT1]}\textsubscript{[C-proofreading-R11-RT1]}\textsubscript{[C-proofreading-R11-RT2]}\textsubscript{[C-proofreading-R12-RT2]}. These are failures of the attack, not logical contradictions.
- **Attacks that did not prove their counter-claim.**
  - The symbolic attack that η ≥ 1.2·$e^{-2\Delta}$ holds for all rates failed (coefficients not all nonnegative), as expected given the certified point of Theorem F \textsubscript{[C-proofreading-R8-RT1]}. The attacker's own search found η_min = 1.0962e-04 at σ = 0.090, v = 6.296e-08, against a claimed 1.2500e-04 \textsubscript{[C-proofreading-R8-RT2]}.
  - For n = 2, the attacker's search found η_min = 3.1387e-05 at σ = 2665.585, v = 2.037e-06, and did not reach the claimed 1.0000e-07 \textsubscript{[C-proofreading-R9-RT2]}.
  - Attacks on fam2_9, fam2_11 and fam2_13 found the bound unprovable for them, consistent with counterexamples \textsubscript{[C-proofreading-R12-RT1]}.
- **Tighter bound for hopfield_n1.** The σ = 6 optimum (η ≈ 3.16e-4) does not meet the tighter bound η_max = 2.2e-4 at σ_max = 8 \textsubscript{[C-proofreading-R2-RT1]}. The point with η = 2.043712e-04 is nonetheless certified separately \textsubscript{[C-proofreading-R2-RT2]}.
- **Weak-driving check.** The attacker's search at the claimed parameter regime found η_min = 3.3490e-03 at σ = 0.422, v = 2.719e-03 \textsubscript{[C-proofreading-R10-RT2]}. The claimed value 2.0000e-03 was not matched \textsubscript{[C-proofreading-R10-RT2]}. The symbolic bound check was inconclusive \textsubscript{[C-proofreading-R10-RT1]}. The exact certificate of the corresponding achievable point stands independently \textsubscript{[C-proofreading-R10]}.
- **Saturation of the n = 1 front.** The symbolic attack on the saturation floor was not certified (symbolic computation > 600 s) \textsubscript{[C-proofreading-R3-RT2]}. The question of saturation toward the Hopfield limit is therefore not answered here.
- **Preregistration deviations.** The L2c success criterion (at least 5 counterexamples in a round) was missed: 2 in round 12, 3 in total \textsubscript{[C-fakt-praereg]}. Degenerate networks (η = 0/0) were excluded \textsubscript{[C-fakt-familie]}.

## 6 Limitations and open questions

- 35 of the 88 topologies with two bound states are open: neither a proof of η ≥ $e^{-2\Delta}$ nor an exact counterexample is available \textsubscript{[C-fakt-klassifikation]}.
- The mechanism behind fam2_66 is an interpretation. Its necessity is unresolved \textsubscript{[C-neg1]}.
- Within the claim list, only n = 2 carries a certified chain bound \textsubscript{[C-proofreading-R9]}. Corresponding certificates for other n are not part of the retained claims.
- The certified achievable points are single points, not complete Pareto fronts. Saturation toward the Hopfield limit is not established \textsubscript{[C-proofreading-R3-RT2]}.
- Novelty: the classification and counterexamples were not found in the retrieved literature, but that search is limited to the 158 confirmed findings \textsubscript{[C-fakt-neuheit]}\textsubscript{[C-fakt-recherche]}.

## References

Only sources appearing in the claims are listed.

- Hopfield, kinetic proofreading, doi:10.1073/pnas.71.10.4135 \textsubscript{[C-lit8]}.
- Energy-relay proofreading and Pareto fronts, doi:10.1098/rsif.2024.0232 \textsubscript{[C-lit1]}\textsubscript{[C-lit2]}.
- Ultimate accuracy and multiple checking steps, doi:10.1016/s0006-3495(80)85063-6 \textsubscript{[C-lit3]}\textsubscript{[C-lit4]}.
- Error--cost bound, doi:10.1098/rsif.2021.0883 \textsubscript{[C-lit10]}\textsubscript{[C-lit11]}; arXiv:2106.01418v2 \textsubscript{[C-lit20]}\textsubscript{[C-lit21]}.
- Generalized Hopfield model Pareto front, doi:10.1088/1367-2630/acc757 \textsubscript{[C-lit12]}\textsubscript{[C-lit13]}.
- Scaling and asymptotic bounds, arXiv:1710.06038v1 \textsubscript{[C-lit22]}\textsubscript{[C-lit23]}\textsubscript{[C-lit24]}.
- Dissipation--error trade-off, arXiv:2111.01189v3 \textsubscript{[C-lit6]}\textsubscript{[C-lit7]}.
- Master-equation thermodynamics of proofreading, arXiv:1504.02494v1 \textsubscript{[C-lit15]}\textsubscript{[C-lit16]}.
- Stochastic Hopfield--Ninio model, doi:10.1137/24m1664861 \textsubscript{[C-lit5]}.
- Discrimination regimes in the Hopfield network, doi:10.1063/5.0312257 \textsubscript{[C-lit25]}\textsubscript{[C-lit26]}.
- Ribosome induced fit, doi:10.1093/emboj/18.13.3800 \textsubscript{[C-lit27]}.
- Speed--accuracy universality, doi:10.1128/mbio.02056-26 \textsubscript{[C-lit9]}.
- Thermodynamic uncertainty relation, doi:10.1103/physrevlett.114.158101 \textsubscript{[C-lit14]}; arXiv:2109.11890v1 \textsubscript{[C-lit17]}.
- Nonequilibrium receptors, arXiv:2002.10567v3 \textsubscript{[C-lit28]}\textsubscript{[C-lit29]}.
- Concentration-estimation accuracy and energy, arXiv:1405.4001v3 \textsubscript{[C-lit30]}.
- Speed limits and dissipated work, arXiv:2402.17931v2 \textsubscript{[C-lit18]}\textsubscript{[C-lit19]}.

![Zweiseitige Pareto-Front: Punkte = zertifiziert erreichbar, gestrichelt = bewiesene untere Schranken. Belege: \textsubscript{[C-proofreading-R1]}, \textsubscript{[C-proofreading-R2]}, \textsubscript{[C-proofreading-R8]}, \textsubscript{[C-proofreading-R9]}, \textsubscript{[C-proofreading-R10]}](pareto_front.png)


---
Prüfprotokoll: 70 Claims zitiert, Korrekturrunden [{"runde": 0, "verstoesse": 17}, {"runde": 1, "verstoesse": 0}, {"final_verstoesse_entfernt": 0}], 0 unbelegte Sätze entfernt, verbleibende Verstöße: 0.
