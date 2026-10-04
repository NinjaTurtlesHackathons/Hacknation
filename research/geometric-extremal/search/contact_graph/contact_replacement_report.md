# N=15 periodic contact replacement: completed negative batch

## Question and assumptions

On the fixed unit square torus, can a nonlocal replacement of the two Hamiltonian contact cycles of the known Gaussian 15-point packing improve its minimum squared periodic separation `17/225`? The baseline labels are `p_k=(k,4k)/15 mod 1`. Original contacts have increments 1 and 4; increment 3 has lift `(3,-3)/15`, squared length `18/225`, and is initially a noncontact.

This batch forces one, two, or three selected increment-3 lifts to become equal-length contacts while opening selected original increment-1/4 lifts. It therefore changes the contact requirements explicitly instead of performing random coordinate jitter. All 105 pairwise periodic distance inequalities remain active. The period lattice and point count remain fixed; global optimality is not assumed.

## Prospective protocol and implementation

`contact_replace.py` writes all seeds 3000–3099 and their exact edge-index/shift hypotheses to `experiments.jsonl` before running a single compute worker. Each hypothesis records new lifted edges, original lifted edges required to open, and an opening gap in squared distance chosen from `0.00005, 0.0002, 0.0008, 0.002, 0.004`. Integer lift compatibility is checked through each triangle `k -> k+4 -> k+3 -> k`; its shift sum is exactly zero. Selected pair contractions supply deterministic starting points. Analytic-gradient SLSQP solves the forced constraints, followed by unrestricted all-pair polishing.

The run contained **100 jobs, 90 distinct labelled hypotheses**. Ten duplicates arose because the single-diagonal modes 0 and 1 selected identical edge data. Distinct labelled hypotheses are not asserted to be inequivalent under every torus symmetry. This duplication was found during the post-run audit; the bounded batch was stopped and was not repeated. The recorded whole-batch wall time was **3.8178734999964945 seconds**, including prospective-result processing and candidate verification during execution, excluding the later audit and report.

## Results and independent exact checks

All 100 forced endpoints passed the recorded *numerical* feasibility thresholds (inequalities at least `-1e-9`, new-contact equality residuals at most `1e-9`). Their best objective was approximately `0.07536358160080651`, below the existing `17/225 = 0.075555555555555...`. Free-polished objectives ranged from `0.07555555555535738` to `0.07555555555555532`, numerically matching the known baseline without exceeding it. Geometry equivalence to the baseline was not independently certified and is not needed for this comparison.

The best forced and polished endpoints were snapped to integer coordinates with scale `10^12`. The separate exact rational checker in `certification/verify.py` recomputed all 105 periodic pair distances:

| Saved artifact (under `candidates/contact_graph/`) | Exact minimum squared separation | Interpretation |
| --- | --- | --- |
| `best_forced_contact_replacement.json` | `9420447700070903429453/125000000000000000000000` | Valid packing, strictly worse than baseline |
| `best_contact_replacement.json` | `9444444444388888888889/125000000000000000000000` | Valid packing, strictly worse than baseline after rounding |

Both exact witnesses fail the strict Markov-conjecture counterexample threshold `d² > 2/(sqrt(3) N) - 8/(25 N²)`. The exact checker certifies the **whole packing feasibility and minimum distance**, not exact tangency of the numerically forced graph. Opening constraints concern the originally selected lifts; after large motion they do not imply that every periodic lift between those labels is noncontact. The integer triangle-winding checks are exact independently of this limitation.

## Conclusion and continuation boundary

The experiment reached feasible graph-altered endpoints but gave no improved construction or counterexample. It prunes these particular forced diagonal/opening patterns as productive starting points for the implemented optimizer; it does not exclude the graphs globally or prove optimality. Further identical seed extension is unjustified. A materially different continuation would require a different winding/contact topology or a multi-point defect outside this increment-3 replacement family.

Reproduction from repository root (appends a new run to the register):

```sh
.venv/bin/python research/geometric-extremal/search/contact_graph/contact_replace.py
```

The existing register and exact witnesses should be inspected before any rerun. Search history remains append-only; no failed job was removed.
