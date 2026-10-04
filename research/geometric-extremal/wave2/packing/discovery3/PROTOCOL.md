# Discovery3: octagonal boundary and triangular bulk

Fresh primary comparison: [Specht octagon table](https://packomania.com/coc/coc.html), updated23-Sep-2026, retrieved2026-10-04. Circles have common radiusr in an octagon of circumradius1. N28–33 values are0.160404294689,0.154929849312,0.152319579409,0.149878153406,0.147297380425,0.145306599845. The N29 andN32 entries are Zorcic July/August2026 constructions newly added in September; historical Amore2023 values alone are insufficient. Each text-coordinate file was freshly downloaded. The table metadata's boundary count0 for new entries is contradicted by visible geometric wall contacts and is not treated as an assumption.

## Definition and independent exact checking

Rotate/scale the container to apothem1. Its supporting normals are axis directions and45° diagonals. Equal circles of radiusrho have rational centres satisfying

`|x|<=1-rho`, `|y|<=1-rho`, `(abs(x)+abs(y))²<=2(1-rho)²`, `0<rho<=1`,

and pair squared distances at least `4rho²`. These are exact rational constraints. Standard circumradius-normalized radius satisfies

`r²=rho²*(2+sqrt2)/4`.

Saved candidates contain rational strings. The in-construction checker uses integer/rational arithmetic for geometry and an exact radical comparison for the objective. Seven adversarial controls pass. The director developed a separate verifier from the problem and checked the N29 baseline independently. A prospective success must beat the freshly printed comparison plus1e−12 uncertainty by a relative radius factor of at least1.0001; small numerical polishing is not a discovery claim.

## Adaptive programs, all single-process searches

1. Equally spaced shell on the offset octagon plus a rotated triangular lattice patch. Five-variable motif fit precedes full coordinate release. The initial enumeration's100 executed programs all had shell count12; the register preserves this scheduling imbalance. It does **not** exclude other shell counts. After100 stagnant jobs it changed representation to100 coherent source-boundary face-reassignment programs, rotating three boundary centres by one or two octagonal faces before full relaxation.
2. A separate prospectively registered family changes the contact topology to16–18 shell sites, reducing bulk count by4–6. Counts and N are interleaved. It executed100 programs and stopped at its stagnation rule.
3. The perimeter obstruction below motivates the promising13–15 boundary-contact range. Equal arclength spacing was dropped: each boundary centre independently slides along a specified supporting facet, while the bulk retains a triangular contact patch. Analytic derivatives cover radius, bulk angle/offset and every facet slider.100 programs executed, stopped at stagnation. This completes representation of shell cardinalities12–18, without pretending all continuous parameters were globally exhausted.
4. A distinct neighboring-count reconstruction removes4–6 source circles and inserts a regular5–7 contact ring, first fitting four ring parameters, then releasing all centres. This targetsN29–33 from freshN28–32 source witnesses. Its prospective first135 programs cover nine physical anchors, every target and every ring cardinality before a100-stagnation rule can stop it. Numerical ring contacts are not claimed exact after rational snapping; whole-circle geometry is independently checked.

Every family uses its own seed range and append-only register. No candidate objective is accepted from solver success alone. Registered wall caps are limits, not actual measured durations. Completed durations and outcomes belong in RESULTS.md.

## A rigorous pruning mechanism (no novelty claim)

The apothem-one regular octagon has perimeter `P=16(sqrt2-1)`. Centres of boundary-contact circles lie on its inward-offset perimeter `P(1-rho)`. If m distinct circle centres touch the boundary, order them along this perimeter. The sum of consecutive chord lengths is at most the perimeter and each chord length is at least2rho. Thus

`2m*rho <= P(1-rho)`, hence `rho <= P/(2m+P)`.

This holds for **any** such packing, without equal arclength spacing or triangular bulk. It concerns the number of circles touching the boundary, not the number of individual wall contacts; a corner-touching circle is counted once. Translating to the standard normalization and squaring gives

`r² <= (128-64sqrt2)/((2m-16)²+512+32(2m-16)sqrt2)`.

The exact executable `boundary_count.py` compares this bound to rational thresholds1e−11 below the published radii, and first verifies that our independently feasible baseline certificates exceed those thresholds. At or above those thresholds, the maximum boundary-circle counts areN28:15, N29/30:16, N31/32/33:17. Therefore18-boundary-contact motifs cannot improve any current target;16 contacts already obstruct improvement atN28. The unrestricted final solver can shed prescribed boundary contacts, so this bound does not justify skipping all free releases from such seeds.

This is a standard perimeter argument used to change search allocation. It is not presented as a new geometric theorem or discovery. It motivated facet-slider and ring-defect alternatives instead of repeating failed dense shells.
