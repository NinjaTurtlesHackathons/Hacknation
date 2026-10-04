# Independent polygon certification and adversarial novelty audit

## Finding

The rational witness `candidates/wave2_polygon/job0326.json` is feasible for12 congruent equilateral triangles of circumradius1 in a square. Its exact square circumradius squared is

`49110490340507880476972068129/5000000000000000000000000000`.

It is smaller than the supplied comparison scalar9.82209829 by

`1109492119523027931871/5000000000000000000000000000`.

**This does not establish a new structural construction or an extraordinary discovery.** After square dihedral matching and label assignment, the candidate already matches the source under the identity transformation and identity labels. Maximum coordinate discrepancy is3.1044557e−8, RMS centre distance2.3531023e−8, and maximum orientation difference modulo120° is1.7953156e−8. Pair-contact graph and wall pattern agree at tolerances1e−7 and1e−6. Circumradius reduction is only3.6524624e−8. These are strong numerical indications of local polishing of the known configuration; contact tolerance comparisons are not exact combinatorial proofs.

The scalar9.82209829 is a conservative lower comparison to the **printed source objective**, not a lower bound on the best geometric realization of that known contact construction. No algebraic optimum or rigorous lower bound for the source's structural family has been supplied. Public claims should therefore say feasible witness/local numerical refinement, and should not assert a new record or a genuinely different discovery from this audit alone.

## Independent verifier design

`clip_verify.py` imports no discovery or root verifier code. It reconstructs the triangles from rational centres and rational tangent-half-angle rotations. Exact checks confirm rotation norm1, all36 vertex circumradii squared1, all36 sides squared3, orientation/nondegeneracy, and144 wall inequalities. Each of66 triangle pairs is checked by **exact convex polygon clipping**, followed by exact signed intersection area. Zero area allows boundary contact; positive area rejects overlapping interiors. This differs from the director's separating-axis certificate.

Arithmetic is `Q(sqrt(3))` with rational coefficients. Order is computed by refining rational isolating bounds for sqrt(3), using integer square roots at increasing binary precision. Arithmetic division uses the field conjugate. No numeric tolerance occurs in the clipping verifier. The implication from zero intersection area to disjoint interiors uses convex, nondegenerate triangles, which are explicitly checked.

Eleven geometric/schema adversarial controls, three field-order controls and three strict-improvement controls pass. They include exact edge/vertex contact, a positive-area overlap of width1/100, duplicate triangles, wall crossings, orientation-dependent wall feasibility, floating inputs and Boolean counts. A large finite tangent-half-angle is accepted; infinite tan-half-angle is outside the input format rather than silently approximated.

The ten distinct strongest/baseline files selected from the live candidate directory all independently passed. Selection was a snapshot, not a claim that every later candidate was audited. Results are in `audit_results.json`.

## Source normalization and orientation independently confirmed

Source problem: [Dominik Kamp's public supplement](https://github.com/DominikKamp/Packing), regular m-gons of unit circumradius packed in regular l-gons, minimize outer circumradiusR. The N12 file uses l=4,m=3. The square is centred at the origin with half-side `h=R/sqrt(2)`. The triangle side is sqrt(3), hence the unit-side normalization of Friedman's table is `s=sqrt(2/3)R`; side length and circumradius must not be compared directly.

The freshly downloaded file matches the director's frozen file by SHA256. Fresh path commit metadata has latest entry16-Apr-2026. Its printed sourceR is3.134022702061933, whose exact decimal square is

`9822098297039579660009767696489/10^30`.

The supplied9.82209829 lies about7.04e−9 below that square, and remains below even after reducing displayedR by1e−15. This supports a conservative comparison to the printed scalar; it does not support optimality of a known construction.

`source_interval_audit.py` separately checks the original decimal centres, angles andR using60-digit **outward-rounded interval transcendental evaluation**. Source triangles use vertices `(x+sin(theta+j*2pi/3), y+cos(theta+j*2pi/3))`, corresponding to standard angle `alpha=pi/2-theta`. All144 wall inequalities and66 pair separation certificates are nonnegative under that convention. The initially proposed half-step convention `theta+(j+0.5)*phi` is a negative control: it produces definite wall violations and overlaps. The director corrected this before its search.

Source interval endpoints are converted to exact rational numbers from the interval library's binary endpoint tuples before min/max reductions. The resulting certificate relies on mpmath's outward interval elementary-function implementation. It is distinct from the rational candidate clipping verifier, which uses only the Python standard library.

## Fresh comparison audit (2026-10-04)

The directly retrieved [Friedman triangles-in-squares table](https://erich-friedman.github.io/packing/triinsqu/) still credits N12, s2.558+, to Dominik Kamp in April2026. Later July/September entries on that same page concern larger N; they do not supersede N12 in the retrieved table. This is positive source evidence, not a completeness proof over every possible unpublished result.

For adjacent-count selection, fresh table values and attribution are:

| N | Unit-triangle-side square side s (table precision only) | Attribution/date |
|---|---|---|
|10|2.377+|David W. Cantrell, July2002|
|11|2.490+|Maurizio Morandi, June2008|
|12|2.558+|Dominik Kamp, April2026|
|13|2.595+|David W. Cantrell, July2002|
|14|2.726+|David W. Cantrell, July2002|
|15|2.82989+|Jake Loyd, June2026|
|16|2.9000+|Ian Watson, April2026|
|17|2.982+|Maurizio Morandi, June2008|
|18|3.051+|Maurizio Morandi, June2008|
|19|3.12929+|Jake Loyd, June2026|
|20|3.2305+|Ian Watson, April2026|

In particular, cached April2026 files must not be assumed current atN15 orN19 merely because their author repository is unchanged. The table's truncated values are insufficient for a tiny improvement claim; precise author coordinates/objectives must be compared under identical normalization.

## Reproduction

```sh
.venv/bin/python research/geometric-extremal/wave2/packing/polygon_audit/clip_verify.py --selftest
.venv/bin/python research/geometric-extremal/wave2/packing/polygon_audit/clip_verify.py research/geometric-extremal/candidates/wave2_polygon/job0326.json
.venv/bin/python research/geometric-extremal/wave2/packing/polygon_audit/source_interval_audit.py
.venv/bin/python research/geometric-extremal/wave2/packing/polygon_audit/structure_compare.py
```

`current_source.txt`, `current_commits.json`, `audit_results.json`, `source_interval_results.json` and `structure_comparison.json` preserve the evidence. Geometry feasibility is certified; structural novelty and a stronger incumbent-family comparison are not.
