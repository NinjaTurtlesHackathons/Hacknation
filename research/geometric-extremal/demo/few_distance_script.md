# Three-minute presentation: two exact lower-bound improvements

Open `few_distance.html` locally. Every depicted configuration belongs to this work. The comparison bars represent published cardinalities, rather than fabricated historical point coordinates.

**0:00–0:35.** “How many points can fit in the plane while all their pairwise distances use only 41 different lengths? The audited published lower bound is 109. Our explicit configuration has111.” Emphasize that the plane has no bounding box or diameter constraint; every pair, including long diagonals, matters. Define G(k) as maximum cardinality with at most k distances.

**0:35–1:15.** Show the111point filled nonagon. Select squared distance127: exactly6pairs appear. Select1:291pairs appear. The class labels are squared distances; actual distances are their square roots. Explain the threefold rotations and reflections. Tour the classes, then pause.

**1:15–1:50.** Press “Recompute every pair exactly”:6105pairs,41classes. The browser uses integer arithmetic. Press “Attack: duplicate a point”: the extra point is rejected. Open coordinates and halfplanes: rational lattice labels embed as (a+b/2,√3b/2). The verifier is independent of the search optimizer.

**1:50–2:20.** Switch to31distance case. The new81point filled decagon exceeds the explicitly published80point witness. It has only one reflection. Select91: just4pairs occur, while81 and84 never occur. This is a concrete palette choice. Trading distance classes is prior art, so do not claim a new mechanism from this observation.

**2:20–3:00.** “The paper proves G(31)≥81 and G(41)≥111 with complete finite integer certificates. We do not know whether either value is globally optimal. Our current primary-source audit found no prior equal or stronger target construction; its coverage is documented. The team retained failed searches, source corrections, algorithms, exact coordinates and independently runnable checkers.” Show the reproduction command and the paper's prior-work comparison.

No claim of a conjecture counterexample, global optimality, uniformly improving infinite family, or exhaustive worldwide literature coverage. At42the previously published115point construction is stronger. The original checkpoint remains archived as a failed first wave; the two new inequalities belong to the continued second wave.
