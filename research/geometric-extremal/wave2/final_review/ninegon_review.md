# Independent general proof review of NINEGON_PROOF.md

Date2026-10-04. No discovery module imported. Verdict: **cardinality, centered transformations and exact D3 symmetry for all integers s>=1,t>0 are correct**. At t=0 the polygon is a regular hexagon with D6 symmetry. This is a parameterized construction/counting theorem, not an infinite sequence of new record improvements or a distinct-distance asymptotic theorem.

## General area and lattice count

Write each listed vertex coordinate as a linear form in s,t. Independent coefficient multiplication and summation of det(v_j,v_{j+1}) gives coefficients(18,12,1) for(s²,st,t²), hence oriented doubled coordinate area A2=18s²+12st+t². This is a polynomial identity, checked by the executable coefficient arithmetic, not interpolation from examples.

For t>0, the ordered physical edge directions have positive turning angles60,30,30 repeated three times. Their total360degrees and displayed vertices give a simple convex polygon; each vertex is extreme. The zero t-edges at t=0 are removed and the remaining six edges have equal physical length sqrt(3)s and successive60degree turns, so give a regular hexagon. For all s>=1,t>=0 area is positive.

A primitive coordinate direction spans a lattice interval, and each edge contributes gcd(|da|,|db|) boundary intervals. Six s-edges contribute s apiece; three t-edges contribute t apiece, including zero contribution when t=0. Thus B=6s+3t. Pick applies to the ordinary integer-coordinate lattice polygon: N=A+B/2+1=9s²+6st+t(t+3)/2+3s+1. It counts boundary AND interior sites. Integrality of t(t+3)/2 follows because t and t+3 have opposite parity. The physical embedding determinant is sqrt(3)/2, so physical area is sqrt(3)/2 times coordinate area, namely sqrt(3)A2/4; substituting physical area into ordinary Pick without covolume division would be wrong. The source correctly uses coordinate area.

## General symmetry proof

Let v_j be the displayed vertices indexed0..8. Direct substitution gives R(v_j)+(3s+t,-3s)=v_(j+3 mod9), where R(a,b)=(-a-b,a). Likewise F(v_j)+(3s,-3s)=v_(2-j mod9), where F(a,b)=(b,a). These are respectively Euclidean120degree rotation and reflection in the physical embedding. Their common center is c=(2s+t/3,-s+t/3). The translations are integral even when c is not a lattice site, so both preserve the lattice and the filled polygon. They generate six distinct D3 transformations.

For t>0, physical lengths of the three t-edges are t, and of the other six edges sqrt(3)s. These are unequal for positive integers since equality would make sqrt(3)=t/s rational. Any Euclidean isometry preserving the filled lattice set preserves its convex hull, whose extreme vertices are exactly the nine listed vertices. Therefore it permutes the three t-edges as a distinguished length class. Their coordinate midpoints are

(3s+t/2,-3s), (3s+t/2,t/2), (0,t/2).

Every squared physical side length is (3s+t/2)², by Q(u,v)=u²+uv+v². Thus this is a nondegenerate equilateral triangle. A symmetry of the set injects into the six-element isometry group of this triangle (an isometry fixing three noncollinear midpoints is identity). Consequently the filled set has at most six symmetries; the six established transformations imply **exactlyD3**. This proves the general claim, rather than only checking finite parameters. At t=0 the distinguished edges collapse and the hull is a regular hexagon;60degree rotation about c preserves the lattice because c is integral and the triangular lattice is invariant, so the filled set has exactlyD6.

One wording correction: the source called t-edges “short” for arbitraryt. This is false when t>sqrt(3)s (e.g.s1,t2). Replace with “distinguished t-edges.” The mathematical unequal-length argument is unaffected.

## Exact exemplar and supplementary checks

The independently written executable ninegon_review.py expands the area polynomial, directly enumerates all72 cases s1..8,t0..8 with exact integer halfplane tests, checks boundary count and both transformations, and confirms the s3,t1 polygon is the frozen111-point candidate after translation(6,-2). Output:ninegon_review.json. These finite checks supplement the general proof, and do not replace it. The previously independent all6105pairs result establishes exactly41distance classes for this exemplar only; no formula for distance classes over all parameters follows from cardinality.

The novelty audit is completed with qualified scope elsewhere. Update the source’s “ongoing” audit wording; no worldwide-first or conjecture-counterexample claim is justified by this family proof alone. The corrected wrong-polygon failure control is separately registered; changing a support without changing the integer geometry cannot serve as a negative control.
