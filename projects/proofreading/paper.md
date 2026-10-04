# Error rates below $e^{-2\Delta}$ in two-bound-state proofreading networks: exact classification of 88 topologies and certified counterexamples

Colin Ji, Laurenz Thümmler, Noah Schittenhelm, Ali Suleman, ETH Zürich

# Error rates below $e^{-2\Delta}$ in two-bound-state proofreading networks: exact classification of 88 topologies and certified counterexamples

## Abstract

An enzyme discriminates a right substrate R from a wrong substrate W by kinetic proofreading. For the linear Hopfield chain with $n$ stages, the error rate is compared with the limit $e^{-(n+1)\Delta}$ [C-proofreading-R3]. The classification of two-bound-state networks and its counterexamples were not found in a targeted literature search [C-fakt-neuheit]. We fix $\Delta=\ln 100$ [C-modell]. For $n=2$ we prove $\eta\ge e^{-3\Delta}$ for all positive rates and fuel potentials [C-proofreading-R9]. Among the 88 non-degenerate two-bound-state topologies [C-fakt-familie], 50 provably obey $\eta\ge e^{-2\Delta}$, three (fam2_66, fam2_9, fam2_11) have exactly certified counterexamples, and 35 remain open [C-fakt-klassifikation]. The topology fam2_66 reaches $\eta=$ 5.082802e-07 at speed $v=$ 1.4746e-03 [C-fakt-fam66]. The method combines symbolic positivity proofs with exact rational arithmetic. The main limitation is that 35 topologies are unresolved [C-fakt-klassifikation]. Moreover, the counterexamples are certified only for log-rates in $[-10,10]$ [C-modell].

## Introduction

Kinetic proofreading raises specificity beyond what free-energy differences or kinetic barriers allow when the reaction is strongly but nonspecifically driven [C-lit8]. The accuracy of error-correcting pathways is set by the displacement of nucleoside triphosphates from equilibrium [C-lit3]. Several checking steps reach a given accuracy with less dissipation than a single step [C-lit4]. Models with more proofreading steps have better trade-offs between speed, error and dissipation [C-lit12]. These Pareto fronts are studied numerically [C-lit13]. Energy-relay proofreading shows trade-off relations and scaling laws [C-lit1]. Its mixed regime shows a dynamical phase transition in the error–entropy-production trade-off [C-lit2].

Bounds also exist at the level of general principles. A fundamental error bound is fixed by the transition-state energy differences [C-lit10, C-lit20]. Thermodynamic uncertainty relations constrain the precision of outputs [C-lit14]. For Hopfield's original network there are scalings in which $\sigma\ln(\mu)/P$ is asymptotically infinite [C-lit22]. Numerical calculations suggest that more restrictive parametric assumptions restore a bound [C-lit23]. Discrimination that is too strong can remove the nonequilibrium advantage [C-lit26], and one regime is anti-proofreading [C-lit25].

**Open question.** Does $\eta\ge e^{-(n+1)\Delta}$ hold for all rates and fuel potentials [C-proofreading-R9]? Which of the 88 non-degenerate topologies with two bound states obey $\eta\ge e^{-2\Delta}$, and which do not [C-fakt-klassifikation]?

**Contribution.** We prove the bound for the chain with $n=2$ by a symbolic positivity argument [C-proofreading-R9]. We classify the 88 two-bound-state topologies [C-fakt-familie] into proved, refuted and open members [C-fakt-klassifikation]. For three members we give exactly certified counterexamples [C-fakt-klassifikation].

**Summary of results.**
- The Hopfield-bound theorem proves $\eta\ge e^{-3\Delta}$ for the chain with $n=2$ for all rates and fuel potentials [C-proofreading-R9].
- The classification theorem sorts the 88 topologies into 50 proved, 3 refuted and 35 open [C-fakt-klassifikation].
- The theorem on 50 topologies states the proved bound [C-proofreading-R11].
- The counterexample theorems give exactly certified counterexamples for fam2_66 [C-proofreading-R4] and for fam2_9 and fam2_11 [C-proofreading-R12].
- The supporting propositions and the lemma cover family generation [C-fakt-familie], subfamily bounds [C-proofreading-R6, C-proofreading-R7], verifier output [C-fakt-r12] and the self-test [C-fakt-selbsttest].
- The examples give exactly certified attainable points for the chain with $n=1$ [C-proofreading-R1, C-proofreading-R3, C-proofreading-R8, C-proofreading-R10].

## Model and assumptions

Two substrates R and W traverse the same Markov network. W leaves bound states faster by the factor $e^{\Delta}$ [C-modell]. The error rate is $\eta=J_W/J_R$, the speed is $v=J_R$, and $\sigma$ is the entropy production per product in units of $kT$. Every edge has a reverse edge, local detailed balance holds, and cycle affinities arise only from the fuel potential $\mu$ per activation and $\mu_P$ per product (modelling rules of the task). Write $D=e^{\Delta}$ and $G=e^{\mu}$ [C-proofreading-R9].

Fixed parameters; every entry is taken from [C-modell]:

| Symbol | Value | Meaning |
|---|---|---|
| $\Delta$ | $\ln 100$ ($e^{\Delta}=100$, $e^{-\Delta}=0.01$) [C-modell] | discrimination free-energy difference in $kT$ |
| $L$ | $10$ [C-modell] | every rate, including derived reverse rates, lies in $[e^{-10},e^{10}]$ |
| $\mu$ | $\ge 0$, explored in $[0,20]$ [C-modell] | fuel potential per fuel-driven step |
| $\mu_P$ | $\ge 0$, explored in $[0,20]$ [C-modell] | chemical potential of product formation |
| max_states | $10$ [C-modell] | unbound states plus R and W copies of bound states |
| concentrations | $1$ [C-modell] | absorbed into binding rates |
| rationalisation | denominator $\le 10^{6}$ [C-modell] | rounding for exact certificates |
| $k$ | $2$ [C-modell] | bound states in the enumerated family (88 non-degenerate members) |

The linear chain is called hopfield_n$n$ with $n$ proofreading stages. The Hopfield limit is $e^{-(n+1)\Delta}$ [C-proofreading-R3].

## Method

Two certificate types are used.

- **Certificate (a), exact reachability.** Rates are rounded to rationals with denominator at most $10^{6}$ [C-modell]. The error rate $\eta$ is evaluated exactly in rational arithmetic, and the entropy production is enclosed in an interval [C-proofreading-R1]. A statement of the form "$\eta\le\eta_{\max}$ is attainable" is certified if the rational rates lie in $[e^{-10},e^{10}]$ and satisfy local detailed balance [C-proofreading-R4].
- **Certificate (b), symbolic positivity.** The difference between $\eta$ and the claimed bound is written as a quotient $N/D$ of polynomials. The bound holds for all positive rates and fuel potentials if all coefficients are nonnegative [C-proofreading-R9]. This proof is independent of the rate range [C-proofreading-R9].

A verifier generates the topologies, enforces the model rules, and passes a self-test with 18 of 18 cases [C-fakt-selbsttest]. Its code is the trusted base. Optimiser output is only a numerical candidate until it is certified by (a). Numerical scans are labelled as numerical.

The work was carried out by an automated, verifier-gated laboratory. Every statement below was accepted only after code verification (details in Appendix A).

## Results

### Main results

::: theorem [Hopfield bound for the chain with $n=2$]
For hopfield_n2, $\eta\ge e^{-3\Delta}$ holds for all positive rates and all fuel potentials $\mu,\mu_P\ge0$ [C-proofreading-R9].
:::

**Certificate.** Symbolic positivity proof (b): $\eta-e^{-3\Delta}=N/D$ with 1374 and 2048 terms, respectively, and all coefficients nonnegative (checked in 6.8 s) [C-proofreading-R9]. Novelty status: not found in a targeted search of 40 abstracts on 2026-10-04 [C-proofreading-R9]. Qualitatively this is a reproduction of the Hopfield bound, here with a rigorous proof [C-fakt-neuheit].

::: proposition [Family generation]
For two bound states the verifier's generator produces 92 rule-conforming topologies [C-fakt-familie]. Four of these are degenerate (no net production possible, $\eta=0/0$) and are excluded [C-fakt-familie]. This leaves 88 non-degenerate topologies [C-fakt-familie].
:::

::: theorem [Classification of two-bound-state topologies]
Of the 88 non-degenerate topologies with two bound states [C-fakt-klassifikation], 50 satisfy a proved bound $\eta\ge e^{-2\Delta}$ (certificate (b)) [C-fakt-klassifikation]. Three of them (fam2_66, fam2_9, fam2_11) have an exactly certified counterexample $\eta<e^{-2\Delta}$ (certificate (a)) [C-fakt-klassifikation]. The remaining 35 are open [C-fakt-klassifikation].
:::

**Certificate.** The three theorems below on the bound for 50 topologies and on the counterexamples [C-proofreading-R11, C-proofreading-R4, C-proofreading-R12]. Novelty status: not found in the research [C-fakt-neuheit].

| Class | Members | Certificate |
|---|---|---|
| bound $\eta\ge e^{-2\Delta}$ proved | 50 [C-fakt-klassifikation] | (b) |
| counterexample $\eta<e^{-2\Delta}$ | 3 [C-fakt-klassifikation] | (a) |
| open | 35 [C-fakt-klassifikation] | none |

*Table 1.* Classification of the 88 topologies [C-fakt-klassifikation].

::: theorem [The bound for 50 topologies]
For 50 topologies of the verifier-generated family with at most two bound states (one unbound state, edge catalogue of the model), $\eta\ge 1/D^{2}$ holds for all positive rates and fuel potentials [C-proofreading-R11].
:::

**Certificate.** Symbolic certificate (b): the bound is proved for 50 of 50 members [C-proofreading-R11]. Novelty status: not found in a targeted search of 48 abstracts on 2026-10-04 [C-proofreading-R11].

::: theorem [Counterexample fam2_66]
For fam2_66 there exist rational rates in $[e^{-10},e^{10}]$ satisfying local detailed balance with $\eta\le 0.0001$ and $v\ge 0.0001$ [C-proofreading-R4]. The exact values are $\eta=$ 5.082802e-07, $\sigma=$ 8.341626 $kT$ per product and $v=$ 1.4746e-03 [C-fakt-fam66].
:::

**Certificate.** Certificate (a), exact rational evaluation, with $\sigma\in[8.341626,8.341626]$ [C-proofreading-R4]. The edges of fam2_66 are binding to C0, a fuel-driven conversion C0 to C1, a fuel-driven discard from C1, and product formation from C1 [C-fakt-fam66]. Novelty status: not found in a targeted search of 48 abstracts on 2026-10-04 [C-proofreading-R4].

::: theorem [Counterexamples fam2_9 and fam2_11]
For each of the two topologies fam2_11 and fam2_9 there exist rational rates in $[e^{-10},e^{10}]$ satisfying local detailed balance with $\eta\le 0.0001$ [C-proofreading-R12].
:::

**Certificate.** Certificate (a) passed for 2 of 2 cases [C-proofreading-R12, C-fakt-r12]. Novelty status: not found in a targeted search of 42 abstracts on 2026-10-04 [C-proofreading-R12].

### Supporting statements

::: proposition [Subfamily bound]
For 3 topologies of the verifier-generated family with at most two bound states, $\eta\ge 1/D^{2}$ holds for all positive rates and fuel potentials [C-proofreading-R6].
:::

**Certificate.** Symbolic certificate (b): 3 of 3 members proved [C-proofreading-R6].

::: proposition [Subfamily bound, second question]
The same conclusion holds for 3 topologies when the question is whether a fuel-driven discard exit at the product state is necessary [C-proofreading-R7].
:::

**Certificate.** Symbolic certificate (b): 3 of 3 members proved [C-proofreading-R7]. This verified result is subsumed by the theorem on 50 topologies [C-proofreading-R11], and by itself does not decide necessity of the discard exit.

::: lemma [Verifier output of the counterexample round]
The verifier output of round 12 is: certificate (a) passed for 2 of 2 cases [C-fakt-r12].
:::

::: proposition [Verifier self-test]
The verifier passes its self-test with 18 of 18 cases (true, false, borderline, rule-violating) [C-fakt-selbsttest].
:::

### Examples (chain with $n=1$)

These are attainable points. They certify reachability, not optimality.

::: example [Moderate dissipation]
For hopfield_n1 there exist rational rates in $[e^{-10},e^{10}]$ satisfying local detailed balance with $\eta\le 0.0004$, $\sigma\le 6.0$ $kT$ per product and $v\ge 0.001$ [C-proofreading-R1].
:::

The certificate gives $\eta=$ 3.650169e-04, $\sigma\in[6.000000,6.000000]$ and $v=$ 1.0417e-01 [C-proofreading-R1]. Novelty status: not found in a targeted search of 62 abstracts on 2026-10-04 [C-proofreading-R1].

::: example [Moderate error rate]
For hopfield_n1 there exist rational rates with $\eta\le 0.01$ and $v\ge 0.001$ [C-proofreading-R3].
:::

The certificate gives $\eta=$ 5.909757e-03, $\sigma\in[3.998555,3.998555]$ and $v=$ 7.1214e-03 [C-proofreading-R3]. Novelty status: not found in a targeted search of 45 abstracts on 2026-10-04 [C-proofreading-R3].

::: example [Very low dissipation]
For hopfield_n1 there exist rational rates with $\eta\le 0.00012$ and $\sigma\le 0.2$ $kT$ per product [C-proofreading-R8].
:::

The certificate gives $\eta=$ 1.095823e-04, $\sigma\in[0.006292,0.006292]$ and $v=$ 9.1487e-09 [C-proofreading-R8]. Novelty status: not found in a targeted search of 49 abstracts on 2026-10-04 [C-proofreading-R8].

::: example [Speed constraint]
For hopfield_n1 there exist rational rates with $\eta\le 0.0002$, $\sigma\le 10$ $kT$ per product and $v\ge 0.001$ [C-proofreading-R10].
:::

The certificate gives $\eta=$ 1.189200e-04, $\sigma\in[4.271813,4.271813]$ and $v=$ 1.0000e-03 [C-proofreading-R10]. Novelty status: not found in a targeted search of 37 abstracts on 2026-10-04 [C-proofreading-R10]. Attainable points of the chain are qualitatively known, and are here exact [C-fakt-neuheit].

| Case | $\eta$ | $\sigma$ ($kT$) | $v$ | Source |
|---|---|---|---|---|
| fam2_66 | 5.082802e-07 | 8.341626 | 1.4746e-03 | [C-proofreading-R4] |
| hopfield_n1, Ex. 1 | 3.650169e-04 | 6.000000 | 1.0417e-01 | [C-proofreading-R1] |
| hopfield_n1, Ex. 2 | 5.909757e-03 | 3.998555 | 7.1214e-03 | [C-proofreading-R3] |
| hopfield_n1, Ex. 3 | 1.095823e-04 | 0.006292 | 9.1487e-09 | [C-proofreading-R8] |
| hopfield_n1, Ex. 4 | 1.189200e-04 | 4.271813 | 1.0000e-03 | [C-proofreading-R10] |

*Table 2.* Certificate (a) data (exact rational $\eta$, interval enclosure of $\sigma$).

**Remark (status of the computer-assisted parts).** The Hopfield-bound theorem and the theorem on 50 topologies rest on certificate (b) [C-proofreading-R9, C-proofreading-R11]. The counterexample theorems and the four examples rest on certificate (a) [C-proofreading-R4, C-proofreading-R12, C-proofreading-R1]. The trusted base is the verifier, including its exact rational arithmetic and its symbolic positivity check. A third party re-runs everything with the command in the Declarations [C-verfuegbarkeit]. The optimiser that finds candidates is not trusted.

## Negative results

- **The 35 open topologies.** For these members neither a proof of $\eta\ge e^{-2\Delta}$ (certificate (b)) nor a certified counterexample (certificate (a)) was obtained [C-fakt-klassifikation]. The reason is unknown.
- **Necessity of a fuel-driven discard exit.** The question was posed in a form that asks for either a counterexample without the feature or a proof of the bound on the subfamily without it. The verified result covers only 3 topologies, so the question is not decided here [C-proofreading-R7]. The failed attempts and their causes (verifier faults, later fixed) are documented in Appendix A [C-neg1].

## Discussion, limitations and open questions

The chain with $n=2$ respects its Hopfield limit for all rates and fuel potentials [C-proofreading-R9]. Three two-bound-state topologies (fam2_66, fam2_9, fam2_11) have certified counterexamples to $\eta\ge e^{-2\Delta}$ [C-fakt-klassifikation]. The certified example fam2_66 uses a fuel-driven discard from the product-forming state [C-fakt-fam66]. A mixed regime with a phase transition in the front was reported in the literature [C-lit2]. A speed–accuracy trade-off need not be universal [C-lit9]. High dissipation can favour speed [C-lit11].

**Limitations.**
- The classification is for $\Delta=\ln 100$ and rates in $[e^{-10},e^{10}]$ [C-modell].
- The counterexamples are certified for rational rates with denominator at most $10^{6}$, and for $\mu,\mu_P$ explored in $[0,20]$ [C-modell].
- Counterexamples are certified at low speed. For fam2_66, $v=$ 1.4746e-03 [C-fakt-fam66].
- The results concern at most $10$ states and substrate concentrations normalised to one [C-modell].
- The four examples are attainable points, not Pareto optima.

**Open questions.**
1. (i) What decides the 35 open topologies [C-fakt-klassifikation]?
2. (ii) Is a fuel-driven discard exit at the product state necessary to go below $e^{-2\Delta}$ [C-fakt-klassifikation]? Only a partial result for 3 topologies exists [C-proofreading-R7].
3. (iii) Do bounds of the type $e^{-(n+1)\Delta}$ hold for other chains with $n=2$ and general branched topologies, beyond hopfield_n2 [C-proofreading-R9]?

## Declarations

**AI usage.** The results were produced and checked by an automated laboratory. Every statement was verified by code.

**Code and data availability.** Repository https://github.com/alizema700/Daddys-Project, branch `claude/paper-pipeline-v2`, directory `projects/proofreading`. Reproduce all certificates with `python -m asd.recheck proofreading`. Rebuild the paper with `python -m asd.paper --domain proofreading` [C-verfuegbarkeit].

**Competing interests.** None.

## Appendix A: Agentic laboratory

**Workflow.** The laboratory ran 12 rounds with 11 verified statements and 1 negative results [C-methode]. Every round was preregistered before the experiment [C-methode].

**Roles.** The roles in the failed attempts of the negative result were sparsam, numeriker, skeptiker and theoretiker [C-neg1].

**Preregistration.** Preregistration H6 (commit 6184672) was made before the first run, with dated addenda [C-fakt-praereg]. The L2c success criterion (at least 5 counterexamples in one round) was missed: 2 were found in round 12, and 3 in total [C-fakt-praereg].

**Literature search.** 2752 sources were retrieved (arXiv, Europe PMC, Crossref, citation chain) [C-fakt-recherche]. 2502 were screened, and 158 findings have a verbatim quote confirmed in the abstract by code [C-fakt-recherche]. All 11 classic searches had hits [C-fakt-recherche].

**Red team.** In total there were 22 counter-checks, of which 4 passed, 8 did not pass and 10 were not executable [C-redteam].

**Negative result.** For the question on the necessity of a fuel-driven discard exit no claim passed the verifier. Four attempts (sparsam, numeriker, skeptiker, theoretiker) failed because of a verifier error that was later fixed [C-neg1]. One boundary-case topology was rejected by the rule check: a discriminating edge is allowed only from bound to unbound [C-proofreading-R7-RT2].

**Additional counter-checks.**
- A counter-check of Example 1 shows that the feasible set grows with the allowed dissipation, so the minimal $\eta$ is non-increasing. The same parameter set remains feasible at larger dissipation budgets. A reported kink in the front is therefore an optimiser artefact [C-proofreading-R1-RT1, C-proofreading-R1-RT2].
- The attempt to prove $\eta\ge 1.2\,e^{-2\Delta}$ for the chain with $n=1$ fails symbolically, as expected from the very-low-dissipation example [C-proofreading-R8-RT1].
- For fam2_9, fam2_11 and fam2_13 the attempt to prove the bound gave 0 of 3 members proved [C-proofreading-R12-RT1]. This is consistent with the certified counterexamples for fam2_9 and fam2_11 [C-proofreading-R12]. For fam2_13 no counterexample is claimed here [C-proofreading-R12-RT1].
- An independent numerical search with 24 starts for the chain with $n=2$ found a minimum of 3.1387e-05, which did not support a claim of a value much below $e^{-3\Delta}$ [C-proofreading-R9-RT2]. This is numerical only, and not a proof.

::: example [Supplementary: pareto-front check, appendix only]
For hopfield_n1 there exist rational rates in $[e^{-10},e^{10}]$ satisfying local detailed balance with $\eta\le 0.0004$, $\sigma\le 8$ $kT$ per product and $v\ge 0.001$ [C-proofreading-R2]. The certificates give $\eta=$ 3.156120e-04 at $\sigma\in[6.000000,6.000000]$ with $v=$ 2.4255e-02, and $\eta=$ 2.043712e-04 at $\sigma\in[3.079633,3.079633]$ with $v=$ 2.2592e-03 [C-proofreading-R2]. Novelty status: not found in a targeted search of 57 abstracts on 2026-10-04 [C-proofreading-R2].
:::

## Appendix B: Provenance

The provenance table mapping every statement to its evidence follows; it is generated automatically.

## Appendix C: Verifier self-test

The verifier of the domain passes its self-test with 18 of 18 cases, covering true statements, false statements, borderline cases and rule violations [C-fakt-selbsttest]. For example, a topology that violates the model rules is rejected by the rule check [C-proofreading-R7-RT2].
<!-- Abbildung pareto_front.pdf: Belege C-proofreading-R1, C-proofreading-R2, C-proofreading-R8, C-proofreading-R9, C-proofreading-R10 -->

<!-- Abbildung klassifikation.pdf: Belege C-proofreading-R4, C-proofreading-R6, C-proofreading-R7, C-proofreading-R11, C-proofreading-R12 -->

