# Right-triangle circle-packing checkpoint

2026-10-04. No improved construction. Exact independent verifier certifies faithfully attributed baseline witnesses for n22,23,24. Source is Specht's `crt` database, not the PBTS square/cube archive.

Problem: n equal disks in T={(x,y):x>=0,y>=0,x+y<=1}. Both perpendicular legs have length1. Centres satisfy x>=r,y>=r,(1-x-y)>=sqrt(2)r, pair distance>=2r. Thus the hypotenuse check can use exact rationals h>=0 and h²>=2r². No container-area or point-distance rescaling is applied to these circle radii.

Primary source [author table](https://packomania.com/crt/crt.html) was downloaded along with raw coordinates `search/triangle_packing/source/crt22.txt`, `crt23.txt`, `crt24.txt` and archived SHA256 hashes in candidate provenance. Table header18-Mar-2011; footer21-Jun-2018. Row attribution [6] refers to Specht's program crt,2009–2010. [HAMSP2025 author paper](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalCOR2025.pdf), section4.2, evaluates right-triangle counts151..200, and therefore does not itself replace22–24. This establishes relevant comparison, not exhaustive proof of current world-record priority.

Literature radii:

|n|r from original coordinates/table|
|---|---|
|22|0.072895080875273247425094690768|
|23|0.071581718995599529585444225012|
|24|0.069914330471767597225541240229|

Baseline certificates retain original decimal centres as exact rational strings. Radius is reduced by1e-27 to absorb published rounding; exact rational containment and pair inequalities pass. These are infrastructure reproductions of existing results, never lab discoveries.

Prospective seeds1000–1019, each count22,23,24 (60 final optimizer results): contact-pair rotation by60/90degrees, boundary-cluster removal of3 circles followed by relaxation and sequential farthest-hole reinsertion, and neighboring-count insertion/deletion. These are contact-topology changes, not just local jitter. One compute worker, SLSQP analytic constraint Jacobian. The fast evaluator independently measures physical radius from returned centres, ignoring optimizer's radius if infeasible. Best results return to the source baselines or below, so no speculative improved candidate is saved.

Final optimizer statuses: n22 20/20 success, n23 19/20, n24 18/20. Some failure cases have zero or negative true radius because centres leave the triangle; they remain logged and were not accepted. Sum of final optimizer times4.513seconds. Nested surgery optimization times were not separately captured, so this sum is **not total experiment runtime** and must not enter a speedup claim. Global optimality is not inferred from60 unsuccessful searches.

Reproduce:

```sh
.venv/bin/python research/geometric-extremal/search/triangle_packing/search.py
.venv/bin/python research/geometric-extremal/certification/verify.py research/geometric-extremal/candidates/triangle_packing/baseline_n22.json research/geometric-extremal/candidates/triangle_packing/baseline_n23.json research/geometric-extremal/candidates/triangle_packing/baseline_n24.json
```

Stop criterion reached: all prospective starts completed without improvement. Next useful approach: discrete row-count/contact-graph enumeration or a parameterized boundary-defect construction across larger counts, rather than extending unchanged SLSQP mutation batches. Source-table timestamps should remain explicit in any future novelty audit.
