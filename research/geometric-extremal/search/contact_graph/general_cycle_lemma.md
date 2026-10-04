# Two spanning contact cycles: quantitative local exclusion

Status: independently derived analytic search-pruning lemma; requires independent proof review before accepted lab claim. Not asserted a novel theorem: periodic rigidity and grid-like Gaussian torus packings have substantial existing literature. No global density or optimality claim.

## Definition and assumptions

Work on the fixed flat square torus T²=R²/Z². The squared separation of labelled points p_0,...,p_{n-1} is

`D(p)=min_{i!=j, m in Z²} ||p_j-p_i+m||_2²`.

Take n>=3, distinct points, and d>0 with D(p)=d². Suppose there are **two directed Hamiltonian cycles** C_1,C_2 on these same labels. For every directed edge i→j of C_s an integer vector m_ij is specified, such that

`p_j-p_i+m_ij=z_s`

for one constant vector z_s throughout that cycle. The two vectors z_1,z_2 are linearly independent, and both have squared length d². Thus all selected edges are genuine shortest contacts. Integer shifts and equal-vector conditions are part of the certificate, not inferred from a rounded picture. Let Z be the 2x2 matrix with rows z_1^T,z_2^T, and K=||Z^{-1}||_infinity, the induced matrix norm (maximum absolute row sum).

The statement also works for a fixed arbitrary period lattice if its period shifts replace Z² and the same Euclidean contact-lift conditions hold. The certificate implementation below uses the unit square torus only.

## Claim

Let q be another labelled torus configuration admitting compatible lifts q_i=p_i+u_i modulo Z². Remove common translation so u_0=0 and set epsilon=max_i||u_i||_infinity. If

`epsilon < 1/[4(n-1)² K]`

and D(q)>=d², then all u_i=0. Therefore the baseline is the only equal-or-better packing, modulo translation, within this explicit labelled neighborhood. Distinct better packings outside that neighborhood are not excluded. Rotations/relabelings may produce equivalent representatives outside the chosen gauge; this is not a claim about them.

## Proof with all periodic copies accounted for

Fix a selected edge i→j of cycle C_s. The baseline shift m_ij still supplies a legitimate integer-period lift of the new pair, whose vector is z_s+(u_j-u_i). The condition D(q)>=d² requires **every** periodic pair lift to have squared length at least d². In particular,

`2 z_s·(u_j-u_i)+||u_j-u_i||_2² >=0`.

The selected lift need not remain the nearest lift; the above implication remains valid. Thus no hidden retained-contact or nearest-branch assumption is needed.

Each coordinate difference is bounded by2epsilon, so ||u_j-u_i||²<=8epsilon². Writing a_ij=z_s·(u_j-u_i), we have a_ij>=-4epsilon². Because z_s is constant and C_s is a directed cycle, summing all its n values telescopes to0. Consequently any particular a_ij is at most4(n-1)epsilon², giving

`|a_ij| <=4(n-1)epsilon²`.

Since the cycle is Hamiltonian, each vertex k can be reached from0 in at most n-1 directed edges. Telescoping along that path gives

`|z_s·u_k| <=4(n-1)²epsilon²` for s=1,2.

Hence ||Z u_k||_infinity<=4(n-1)²epsilon², and multiplication by Z^{-1} yields

`||u_k||_infinity <=4(n-1)² K epsilon²`.

Taking the maximum over k implies epsilon<=4(n-1)² K epsilon². Either epsilon=0 or epsilon>=1/[4(n-1)²K]. The strict neighborhood assumption excludes the second possibility. QED.

The proof covers equal-or-better separation, so it establishes isolated local maximality modulo translation. It is not merely a first-order statement. It does not require differentiability, an infinitesimal motion curve, numerical rank, or a nonzero improvement margin.

## Exact first-order corollary

If infinitesimal velocities v_i weakly increase all selected contact lengths, then z_s·(v_j-v_i)>=0. Cycle sums vanish, so every such expression equals0. Hamiltonicity forces z_s·v_k constant in k for each s. Independence of z_1,z_2 forces all v_k equal. Thus only translations are possible; after gauge v_0=0, the contact rigidity rank is2n-2. This argument avoids a dense2n-by2n matrix computation at large n.

## Known Gaussian cyclic family

For coprime positive integers a>b with N=a²-b², use

`p_k=((b*k mod N)/N,(a*k mod N)/N)`, k=0,...,N-1.

The step1 cycle has z_1=(b,a)/N. A second step t satisfies `t*b=a (mod N)` and `t*a=b (mod N)`; take t=a*b^{-1} (mod N). Coprimality implies b and a are invertible modulo N, hence gcd(t,N)=1 and both steps form Hamiltonian cycles. Their lift shifts are integers by these modular identities.

`Z^{-1}=[[-b,a],[a,-b]]`, so K=a+b.

The proposed contact objective is d²=(a²+b²)/N². It is a valid shortest contact only if all other nonzero modular differences have squared norm at least that value. This condition is checked exactly for the three instantiated family members, rather than assumed for arbitrary a,b. The general lemma is conditional, and not every coprime a,b supplies the shortest-vector assumption.

|a,b|N|Exact shortest d²|Second cycle step t|K|Strict local supnorm radius|
|---|---|---|---|---|---|
|4,1|15|17/225|4|5|1/3920|
|15,4|209|241/43681|56|19|1/3288064|
|56,15|2911|3361/8473921|780|71|1/2404940400|

Run `n15_exclusion.py` for the original exact rank audit, and `gaussian_family_certificate.py` for compact O(N) modular shortest-vector checks, both Hamiltonian-cycle conditions and exact neighborhood constants. The latter performs no numerical optimization and uses only Python integer/Fraction arithmetic. Points are specified by a reproducible integer formula; it is not dependent on a separately trusted point file. N2911 exceeds the standalone generic verifier's point-count cap, so that certificate uses exact translational invariance to reduce all pair checks to N-1 nonzero modular differences. This is a specialized independent family certificate, not a bypass for arbitrary configurations.

## Nonlocal next attack

Any successful perturbation must leave the explicit neighborhood; the most useful next representation is **periodic triangulation surgery**. Remove one rhombic contact strip, reconnect the periodic triangulation with a5–7 defect pair, and solve the resulting edge-length realization with fixed period lattice. The elementary strip must close in both integer winding directions; check those winding constraints before numerical realization. A defect that merely changes an unequal-radius system or deforms the container is inadmissible for the equal-radius square-torus conjecture.

This is a grounded alternative because it changes the contact cycles themselves. No new witness is supplied by the lemma, and no claim is made that such a defect can improve density; the explicit winding/feasibility checks are its first go/no-go test. Existing gaussian continued-fraction families and general jamming theory must be cited before any novelty claim.
