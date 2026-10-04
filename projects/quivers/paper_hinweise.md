Topic and required structure (overrides the default section list where they differ):

Title page abstract: the paper studies indecomposable representations of quivers that are NOT Dynkin, with emphasis on star quivers
(n leaves attached to a centre, no edges between leaves) and on 3-cycles and 4-cycles, and tries to classify the infinitely many indecomposables.

1. Introduction: question, contribution, bullet list of results (each bullet cites its claim ids).
2. Definitions (brief, no numbers needed): quiver Q = (Q_0, Q_1, s, t); representation (vector space per vertex, linear map per arrow);
   morphisms; direct sums; indecomposable; dimension vector; Tits form q(x) = sum x_i^2 - sum over arrows x_s x_t; real and imaginary roots;
   A_alpha(q) = number of absolutely indecomposable representations over F_q. Krull-Schmidt.
3. Gabriel's theorem: state it with the literature claims (Gabriel, Bernstein-Gelfand-Ponomarev). Then the lab's confirmation:
   Tits types of the stars and cycles, 12 positive roots of D4, exhaustive counts over F_2 and F_3.
4. Beyond Dynkin: Kac's theorem and Kac polynomials (literature claims), tame = Euclidean (Nazarova, Ringel), wild otherwise.
5. Star quivers.
   5a Four subspace problem (star4 = D~4): delta = (2;1,1,1,1); the one-parameter family V_t of lines (1,0), (0,1), (1,1), (1,t), certified
      pairwise non-isomorphic bricks; the six configurations with exactly one coinciding pair of lines; complete lists over F_2, F_3, F_5;
      A_delta(q) = q + 4; explicit indecomposables for real roots. Interpretation (uncertified): the six extra classes sit at the three degenerate
      cross ratios, two each, matching three tubes of rank 2 (Ringel).
   5b Classification theorem for alpha_n = (2;1^n), proved in the companion ledger results.tex: a representation is a tuple of vectors in k^2;
      it is indecomposable iff all vectors are non-zero and they span at least three distinct lines; such representations are bricks and their
      isoclasses are PGL_2-orbits of point configurations in P^1 with at least three distinct points; counting gives
      A(q) = ((q+1)^(n-1) - 1 - (2^(n-1) - 1) q) / (q (q - 1)), of degree n - 3 = 1 - q(alpha_n). Present it as a Theorem with this proof sketch,
      and cite the kac_polynom claims as the computer verification.
   5c Wild stars: indefinite Tits form, number of parameters 1 - q grows without bound (cite the parameter claims), two-parameter family slices,
      complete list over F_2 for star5.
6. Cycles: 3-cycle and 4-cycle, oriented and acyclic. Classification theorem for the oriented cycle (proved in results.tex via Fitting's lemma):
   indecomposables are nilpotent strings S(i, l) and bands (all spaces k^m, last arrow an invertible indecomposable matrix, i.e. Jordan block
   or companion matrix). Cite the exhaustive zykel_box checks. A_delta(q) = q + n - 1 independent of orientation; complete lists over F_3.
7. Multiples of delta: counts for 2 delta and the consequence A_{2 delta} = A_delta at the tested q.
8. Method: the verifier-gated lab (exact verifier, self-test, preregistration, red-team counter-checks), briefly.
9. Negative results, red team, limitations: no claim refuted or contested; what was not computed (see C-methode and the verifier notes);
   Kac polynomials certified only at finitely many primes plus Kac's theorem; results on stars and cycles are reproductions of classical facts.
References: only the literature claims, with DOI.
Use standard mathematical notation. Use the canonical claim statements, not the agents' interpretations, for results.
