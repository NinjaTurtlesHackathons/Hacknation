# Completed adaptive area campaign — no new record

This campaign has finished. It does not establish the requested exceptional discovery. No candidate strictly exceeds its exact primary coordinate comparator. The next campaign should change the combinatorial representation again instead of repeating these phases.

The consolidated machine-readable evidence is `summary.json`. Source JSON files are frozen with SHA256 and fetch-UTC sidecars. Every result can be evaluated from its own rational coordinates with the separate `certification/verify.py`. Original source constructions remain credited to their authors; the generated negative candidates are lab search artifacts.

| Method | Completed | Exact-valid | Strict exact improvements |
|---|---:|---:|---:|
| Full critical-line reflection + coupled active-triple SLP | 480 | 480 | 0 |
| Contact-linked block reflection + exact-axis LP | 357 | 356 | 0 |
| Critical-triple coordinate permutation + exact-axis LP | 847 | 842 | 0 |
| Soft active-facet release + exact-axis LP | 460 | 460 | 0 |
| Forced single-sign LP synthesis + exact-axis LP | 1,800 | 1,755 | 0 |
| Coupled recovery of distinct synthesized cells | 150 | 150 | 0 |
| **Total** | **4,094** | **4,043** | **0** |

Sum of measured job durations: **1,562.3539702732014 seconds**. This excludes setup, primary-source retrieval, reporting, manual analysis and other agents. One numerical worker was active at a time. The 51 rejected candidates are preserved. Unexecuted preregistered seeds and interrupted in-flight jobs are excluded.

Targets were convex18/20/23/25/31/33, triangle20/29, square21/23/25/35, then triangle14, convex15 and square20. The small-case extension freshly froze the current square20 coordinates, avoiding the known stale July-versus-September HTML cache mismatch.

## What changed and what was learned

Large block reflections damaged cross-block determinants severely, so they were stopped. Coordinate permutations reached many poor cells and occasionally nearly recovered a source; these recoveries were strictly below the rational comparator and do not count as equalities.

In all 460 completed soft-facet-release jobs, the numerical orientation test reported no changed sign. Removing a handful of active determinant inequalities was insufficient to escape the order cell: other constraints indirectly pinned it. This is empirical evidence, not a proof of global redundancy.

Explicitly flipping one selected triple constraint while retaining every other sign produced 1,227 numerical single-flip mutations among 1,800 jobs. The remaining jobs include infeasible chart slices, degeneracies and multiple flips after tiny branch perturbations; all final outputs still faced exact geometric verification. Feasibility failure in a fixed axis chart does not exclude full two-coordinate geometry.

The best genuinely changed-cell recovery is
`candidates/wave2_area/square35_recovery_3402.json`, at **0.99889949856709** times the exact source objective (illustrative decimal ratio; exact fractions are in the artifact). It is a deficit of roughly 0.11%, not a record. A separate exact Fraction calculation of every one of its 6,545 determinants shows **exactly one orientation differs from the source**, and neither configuration has a zero determinant. The frozen exact order-type audit is `best_adjacent_cell_exact_audit.json`. The next best coupled recovery was convex31 at approximately 0.996070 of its comparator.

The geometric interpretation is limited: the coordinate-slice bottleneck mattered because joint recovery raised many synthesized cells substantially, but these tested adjacent cells still did not beat their current witnesses. This does not show that the source is globally optimal or that every adjacent cell is inferior.

## Resume with a genuinely different hypothesis

Recommended next hypothesis: coherent multi-sign changes tied to rank-3 oriented-matroid circuits, or enumerating the line-arrangement cells accessible to a selected moving vertex while preserving the remaining labels. The current single-triple inversion can force an unnecessarily expensive isolated change; arbitrary contact-block reflection destroys too many unrelated constraints. A circuit-compatible transition could occupy the middle ground. Enumerate combinatorial patterns first, then solve a full joint-coordinate feasibility problem under a prescribed improvement threshold, rather than optimize random point perturbations.

An alternative is structured small-dimensional construction synthesis with exact algebraic parameters and current source contact hypergraphs. The source configurations have many near-active triangles; exact and approximate active sets must remain distinguished. The present campaign provides no new theorem concerning those patterns.

## Reproduce existing evidence

From the repository root:

```sh
.venv/bin/python research/geometric-extremal/wave2/area/summarize.py
.venv/bin/python research/geometric-extremal/certification/verify.py research/geometric-extremal/candidates/wave2_area/square35_recovery_3402.json
```

The numerical scripts are `program_search.py`, `facet_surgery.py`, and `recover_cells.py`. Prospective registers specify exact executed seed ranges and source targets; partial phases must be replayed only up to completed registry entries if reproducing measured campaign totals. Repeating a phase appends new entries: use a fresh directory or archive the existing registry before a new experimental run. Read `METHOD.md` for mathematical normalization and candidate-generation assumptions. Canonical main claims and paper tables remain owned by the root agent; this memo does not alter them or make a novelty claim.
