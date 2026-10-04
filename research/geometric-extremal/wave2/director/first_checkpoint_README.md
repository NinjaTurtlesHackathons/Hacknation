# Geometric Extremal Lab — reviewed research checkpoint

**No exceptional new geometric discovery has been established.** This branch delivers a reproducible research campaign, independently exact certificates, an explicit local exclusion around a known torus packing, a working manuscript, and an offline demonstration. Feasibility, local isolation, global optimality and novelty are separate claims.

## Strongest derived statement

For the known 15-point square-torus packing p_k=(k/15,4k/15) mod Z², fix labels, compatible lifts and translation u_0=0. If max_k ||u_k||∞ <1/3920 and the perturbed packing has minimum squared periodic separation at least17/225, then every u_k=0. Two Hamiltonian contact cycles yield epsilon <=3920epsilon². This is an independently reviewed local pruning lemma based on a known rigidity mechanism; novelty and global optimality are **not** claimed.

## Replay the certificates

From repository root, Python standard library only:

```sh
python3 research/geometric-extremal/reproduce.py
```

Two independent programs use rational determinants/monotone hull versus common-denominator integer arithmetic/gift-wrapped hull and explicit periodic images. They recompute the accepted configurations. The known two-point torus example must be rejected as a conjecture counterexample because the source conjecture requires N>=6.

To rebuild the offline demo from the sole reviewed data table:

```sh
python3 research/geometric-extremal/demo/build_demo.py
```

Open `demo/index.html`. Geometry interactions use approximate display arithmetic; fixed published certificate values are exact. Primary source credit appears in each case.

## Review navigation

- `portfolio.md` and `literature/`:18 concretely defined questions, primary sources and current-source gaps.
- `context.md`, `prereg.md`, `STATUS.md`:scope, gate decisions and resumable next work.
- `analysis/`:discovery outcomes, independent attacks and novelty review.
- `certification/`:two standalone checkers, controls, local-proof dependencies and accepted witness objects.
- `tables/`:sole experiments/claims/gates/demo source. No numeric speedup is asserted.
- `paper/manuscript.md`, `paper/manuscript.tex`:working scientific report, not a paper announcing a new world record.
- `demo/demo_script.md`:short presentation script.
- `search/`, `candidates/`:all seeds, methods, negative logs, exact candidates and frozen author-source snapshots.

## Discovery replay

Numerical searches additionally require numpy/scipy/sympy/mpmath/python-flint/networkx; `requirements.txt` freezes observed versions. See the exact commands in the analysis logs. Native annealing is optional and can be rebuilt from its C source. Re-running search may append duplicate experiments; copy the research directory first for a clean replay.

Existing `asd.domains.geometric_extremal_domain` preserves the Lab Domain API; `python -m asd.selftest geometric_extremal` runs its acceptance gate. Accepted canonical claims are also stored in `projects/geometric_extremal/state.json`. The built-in LLM loop was not used to fabricate trials: delegated agents implemented independently logged search methods, then integration passed claims through Domain.check. The original chemistry benchmarks are unchanged.

The branch inherits existing Lab infrastructure from `algo-efficiency` dff8d99 because `main` c622004 has only the original chemistry script. Review this branch against `algo-efficiency`. Literature freshness is audited but no claim is made that searches prove an open problem remains open. No researchers were contacted. Source snapshots retain provenance; third-party code was not copied from unlicensed repositories.
