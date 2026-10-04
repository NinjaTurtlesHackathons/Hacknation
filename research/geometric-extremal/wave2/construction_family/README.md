# Finite construction-family campaign: handoff

The independent halfplane search produced an exact **111-point / 41-distance** witness, exceeding the consolidated historical threshold109. The root agent's two independent checkers passed all6,105 pairs. Packing_scout independently passed the geometric proof and compact difference-envelope certificate. **Current-literature novelty was separately audited through4October2026: no prior equal/stronger targetwitness located in the auditedprimarysources; no global optimality or Bao–Yu counterexample is claimed.**

Main artifacts:

- `SUMMARY.json`: counts, measured timers, source/candidate paths, method hashes and limits.
- `NINEGON_PROOF.md`: exact edge program and Pick count for a parameterized construction containing111/41.
- `ORBIT_EXCLUSION.md`: linear support mechanism, full norm111 orbit exclusion and independent420-vector upper certificate.
- `k41_n111_independent.json`: exact6105-pair histogram and verifier output.
- `difference_envelope_s3.json`: compact complete420-vector upper certificate and12-vector norm111 audit.
- `ninegon_results.json`:72 exact parameter cases with full palettes; no extra audited improvement.
- `formula_family_results.json`:19 cases of a different support-scaling formula; no extra audited improvement.
- `log_archive_manifest.json`: verified compressed full-trial logs and original/compressed SHA256 values.
- `conjecture_scope.md`: primary-source quantifiers and date/version caveat.

All4 finite native batches finished: 25,355,100 support programs, including duplicate/equivalent geometric sets. Each compressed CSV has one row per completed program `(code,n,actual_distance_count)`; these are **not merely Pareto rows**. Candidates retained every new best exact-class count during each sweep. The family coordinates are deterministically reconstructed from the code and support enumeration. Every serious witness additionally has explicit integer coordinates.

Summed native timers are approximately171.2104 seconds, printed at six significant digits; the independent91 parameter cases sum2.392689 measured seconds. These exclude compilation, proof analysis, compression, external-source work and other agents. One numerical worker ran at a time. No speedup claim is made.

The halfplane families independently reproduced the81/31 candidate discovered by the root's joint-palette MILP and then found111/41 by support variation. The primitive nine-gon `(s,t)=(3,1)` replaces norm111 among the first41 triangular-lattice classes with norm127. It is a different construction from the81-point reflection-only ten-gon.

The search did **not** produce a Conjecture3 counterexample. The best exact28-class and34-class counts in these support families were73 and90. These negative finite sweeps do not prove impossibility elsewhere.

## Reproduce the concise scientific certificates

From the repository root:

```sh
.venv/bin/python research/geometric-extremal/wave2/construction_family/ninegon_family.py
.venv/bin/python research/geometric-extremal/certification/verify.py research/geometric-extremal/candidates/wave2_family/ninegon_s3_t1_k41_n111.json
```

Independent review scripts live in `wave2/final_review/ninegon_review.py` and `orbit_review.py`, owned by packing_scout. The compact envelope enumeration is also embedded in `ORBIT_EXCLUSION.md`; it does not import discovery conclusions.

## Reproduce exhaustive support sweeps

The native code uses only standard C++17. Original executed sources are preserved as `support_search_delta12.cpp` (10 variable facets), `support_search_canonical.cpp` (8 free facets,2 fixed), and `support_twelve_executed.cpp` (10 free facets,2 fixed). `support_twelve.cpp` differs from its executed copy only by corrected coordinate-bound comments.

```sh
clang++ -O3 -std=c++17 research/geometric-extremal/wave2/construction_family/support_search_delta12.cpp -o research/geometric-extremal/wave2/construction_family/replay_support
research/geometric-extremal/wave2/construction_family/replay_support 2 research/geometric-extremal/candidates/wave2_family research/geometric-extremal/wave2/construction_family/support_delta2.csv
.venv/bin/python research/geometric-extremal/wave2/construction_family/compress_logs.py
```

Use the prospective registers to reconstruct the other exact argument ranges. Gzip logs retain every completed trial; originals were removed only after decompressed SHA256 and byte counts matched. The archives are each below GitHub's100MB per-file limit. Compression reruns preserve existing manifest entries. No native worker remains running.

## Next independent research decision

The completed literature audit supports the scoped111/41 improvement. A broader independent classification against general bladed families remains a possible future question. Ask whether other compact support polygons yield more than one additional improved k and whether the excluded-orbit mechanism permits a useful general distance-count bound. The parameter family does not give a closed formula for k. Norms can have additional lattice representations, so excluding a single12-vector orbit does not exclude that norm in all larger cases. Do not extrapolate the observed prime-like behavior into an unproved theorem or assume records for k>50 without fresh sources.
