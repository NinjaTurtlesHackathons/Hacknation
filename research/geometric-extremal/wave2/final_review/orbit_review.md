# Independent analytic support-envelope review

Date2026-10-04. Verdict: **ORBIT_EXCLUSION.md is mathematically sound under its stated scope**. The standalone script orbit_review.py imports no construction/discovery module. Its output is orbit_review.json.

For P(s,1), the a-coordinate values of the nine vertices are
0,s,3s,3s+1,4s+1,3s+1,3s,s,0.
The values of 2a+b are
0,0,3s,3s+2,6s+2,6s+2,6s+1,3s+1,1.
For s>=1 these have exact extrema0..4s+1 and0..6s+2. Linear functionals attain their extrema at polygon vertices, so these bounds hold throughout the polygon, hence for every included lattice site. Every difference p-q therefore satisfies |a|<=4s+1 and|2a+b|<=6s+2.

The centered120degree rotation and centered reflection proved in the ninegon review have affine translations. Applying each to both p andq cancels the translation, so the difference body inherits their LINEAR parts. It also has central symmetry since q-p=-(p-q). Composition of rotations120and180generates rotation60. Applying its powers to the two absolute bounds yields |a|,|b|,|a+b|<=4s+1 and|2a+b|,|a+2b|,|a-b|<=6s+2. These are necessary conditions; the proof does not need a sufficiency theorem or saturation of the convex difference body by actual lattice differences.

The vector(3s+1,1) has2a+b=6s+3and hence violates a cap. Every image under the twelve lattice dihedral transformations likewise violates a transformed cap. Its squared norm is9s²+9s+3, equal to the independently proved N(s,1). This excludes its orbit ONLY. A squared norm may admit other noncongruent lattice representations, and the appendix correctly warns against generalizing orbit exclusion to norm exclusion for all s.

At s3, coordinate completeness for norm111 follows from4Q(a,b)=(2a+b)²+3b² and its coordinate-swapped version: |a|,|b|<=sqrt(444/3)<13. Independent enumeration of[-12,12]² produces precisely12representations of111 and all are the orbit of(10,1). Thus the orbit exclusion removes this entire norm in this exemplar.

The s3 support caps bound coordinates by13, so[-13,13]² exhausts the integer support envelope. Independent enumeration gives420nonzero vectors,41positive norms and maximum127, in exact agreement with the frozen envelope JSON. Every actual difference of the111-point candidate passes these caps, and its pair loop realizes every one of the41norms. This provides an upper certificate from support widths and a separate lower realization certificate from points; global plane optimality is not implied.

For representable norms<=127, the same square completion gives |a|,|b|<=sqrt(508/3)<14. Exhaustive integer enumeration in[-13,13]² gives45positive representable norms. Of the first41, the support-envelope palette omits111 and adds127. The other omitted norms up to127are117,121,124. Both class-exchange and complete norm111 exclusion are thereby checked independently.

No material objection remains. This explains a finite construction geometrically and supplies an exact upper bound on its number of distances; it does not establish a new universally improving family, an asymptotic theorem, or novelty of support clipping/palette exchange.
