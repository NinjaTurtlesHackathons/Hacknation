# Discovery3 completed bounded campaign: no improved octagon witness

**No new record, no relative0.01% improvement, and no discovery claim.** Eleven rational witnesses are geometrically feasible under a separately implemented exact verifier; none strictly beats its fresh published comparison plus1e−12. The geometric programs and source evidence remain available for continuation.

## Work actually executed

| Representation | Actual jobs | Actual measured whole-campaign seconds | Stop/adaptation |
|---|---:|---:|---|
|12-site equal-arclength shell + triangular bulk, then coherent source-face reassignment|100+100|92.71228987500217|100 stagnant shell programs triggered a different contact program;100 stagnant face swaps stopped it|
|16–18-site dense shells + smaller triangular bulk|100|49.052332500003104|Counts/N interleaved;100 stagnant programs|
|13–15 independently sliding boundary-facet sites + triangular bulk|100|52.76979729100276|Abandoned equal arclength restriction;100 stagnant programs|
|Neighbor-count4→5,5→6,6→7 contact-ring replacement|135|57.53604045799875|Every targetN29–33, nine anchors and every ring size represented before stopping|

Actual total:535 construction/relaxation jobs, approximately252.07 seconds of computation, one search process at a time. This excludes implementation, source browsing/downloads, independent audits and report writing. A job may contain a motif solver and a subsequent full-coordinate solver; jobs are not being conflated with total optimizer calls. The wall caps were300,180,240,240 seconds respectively, not measured runtimes.

The first stage's ordering imbalance is explicitly retained: all100 equal-arclength-shell jobs used12 sites. Subsequent stages sampled16–18 and13–15 with interleaved cardinalities, so no unsupported extrapolation from the initial12-site result is required. Most continuous parameters and many discrete programs remain unsearched; failure in the executed batch is not a global exclusion argument.

## Baseline and candidate comparison

Fresh source coordinates are archived forN28–33 with SHA256 hashes in `source_manifest.json`. The [primary octagon table](https://packomania.com/coc/coc.html) is dated23-Sep-2026. Its N29 andN32 replacements are stronger than earlier Amore constructions. Radius normalization is documented in PROTOCOL.md; the original table fixes octagon circumradius1, while our exact rational geometry fixes apothem1.

| N | Published circle radius, circumradius-one container | Best ring-family numerical radius | Outcome |
|---|---:|---:|---|
|28|0.160404294689|not a ring target|Baseline reproduced|
|29|0.154929849312|0.15492984931148618|Reproduced within source/solver precision|
|30|0.152319579409|0.1519922857521579|Worse|
|31|0.149878153406|0.14987815340620117|Rounding-scale difference only|
|32|0.147297380425|0.14729738042484053|Reproduced within source/solver precision|
|33|0.145306599845|0.14514231930646018|Worse|

The N31 difference is about2e−13 and is not classified as progress. Rational snapping and a conservative radius shrink are applied before geometry checks; none of the saved ring candidates beats the separately supplied comparison. Six baseline files and five best ring-family files are under `candidates/wave2_packing3/`. The root's exact rational/Q(sqrt2) verifier independently passed all eleven files,0 strict improvements; evidence is in `independent_root_checks.json`.

The first three representations gave no numerical gain above the source baseline by the prospectively used1e−10 apothem-radius threshold, so only the ring family needed additional feasible candidate artifacts. Their failures and status/parameters are all retained in the registers rather than hidden behind a best-value summary.

## What changed the research allocation

The exact perimeter argument in PROTOCOL.md yields maximum boundary-circle counts15 atN28,16 atN29/30, and17 atN31–33 for any packing at or above independently certified near-current radius thresholds. In particular,18-site boundary-shell motifs cannot reach any target while preserving all boundary contacts;16 already fails atN28. This is a rigorous pruning mechanism, not an asserted new theorem. It motivated fewer boundary sites with independent facet sliding and neighboring-count ring defects instead of further unchanged dense-shell starts.

Source contact diagnostics also identify actual boundary counts around12–15 and rattlers atN29/30/32, so metadata boundary0 in new table entries was not used to infer an all-interior configuration. Rattler freedom alone did not produce a radius improvement. Optimizing those loose centres without changing the load-bearing structure would be a weak next attempt.

The chosen representations now show consistent recovery of incumbents or lower values. A justified next campaign would need to change the interior **nontriangular load-bearing contact topology** (for example, a connected strip of vacancies/interstitials reaching the boundary) rather than preserving a perfect triangular core, modifying only a small regular ring, or adding independent coordinate jitter. That is a new hypothesis requiring its own program generator and prospective register; this batch does not claim to have executed it.

## Reproduce or audit

```sh
.venv/bin/python research/geometric-extremal/wave2/packing/discovery3/octagon.py --seconds 300
.venv/bin/python research/geometric-extremal/wave2/packing/discovery3/dense_shell.py --seconds 180
.venv/bin/python research/geometric-extremal/wave2/packing/discovery3/facet_program.py --seconds 240
.venv/bin/python research/geometric-extremal/wave2/packing/discovery3/ring_surgery.py --seconds 240
.venv/bin/python research/geometric-extremal/wave2/packing/discovery3/boundary_count.py
```

Registers are append-only; do not rerun unchanged programs merely to increase counts. Each family has a distinct seed range. Independent root verification may be run per candidate using `wave2/director/octagon_verify.py` and a separately provided trusted radius scalar. The exact baseline, metadata uncertainty, objective conversion, expected success margin and stop criteria are documented in PROTOCOL.md.
