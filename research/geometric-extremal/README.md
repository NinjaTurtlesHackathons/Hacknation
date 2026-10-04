# Geometric Extremal Lab — two exact lower-bound improvements

**G(31) ≥ 81 and G(41) ≥ 111.** Here G(k) is the maximum number of points in the unrestricted Euclidean plane using at most k distinct nonzero pair distances. Both constructions improve the explicit Ahmed–Snevily (2013) lower bounds80 and109. The independent primary-source audit through4October2026 found no prior equal or stronger target witness. Global optimality, certainty about unindexed/unpublished work, a new palette-exchange principle, and a conjecture counterexample are not claimed.

## Exact replay

From repository root; Python standard library only:

```sh
python3 research/geometric-extremal/results/reproduce.py
```

This regenerates every integer lattice site from the two polygons, checks frozen hashes and all3240/6105pairs with multiple exact implementations, and verifies the complete distance histograms. Run `results/controls.py` for deliberate corrupted-metadata controls; `wave2/paper/verify_witnesses.py` independently checks the manuscript's row-correlation proof. Existing baseline/local-lemma replay remains `reproduce.py`.

## Paper, demonstration and evidence

- `paper/manuscript.md` and standalone `paper/manuscript.tex`: current paper, full elementary proofs, explicit coordinates, source comparisons, and D3ninegon cardinality formula.
- `demo/few_distance.html`: portable interactive visualization; browser BigInt all-pair replay, class highlighting, animation, and invalid duplicate attack.
- `demo/few_distance_script.md`: three-minute presentation.
- `results/records.json`: frozen geometries and audited comparison data; `results/certificates.json`: exact output.
- `wave2/packing/few_distance_novelty/VERDICT.md`: independent primary-literature and implicit-family attack.
- `wave2/final_review/`: adversarial arithmetic, symmetry, mutation and family reviews.
- `wave2/construction_family/`: finite support-program searches, complete compressed logs, parameter family and analytic orbit-exclusion explanation.
- `portfolio.md`, `literature/`, `STATUS.md`, `research_chronicle.md`, `prereg.md`, `wave2/prereg.md`:18initialquestions, assumptions, chronology, negative campaigns and restart state.

Rebuild the new demo with `python3 research/geometric-extremal/demo/build_few_distance.py`. `demo/index.html` remains a gallery of inherited baseline constructions; it is not the presentation of the new results. The first unsuccessful checkpoint paper is retained separately. Original records and previous commits are preserved rather than retroactively described as successful research.

## Existing lab infrastructure

The `asd.domains.geometric_extremal_domain` acceptance gate certifies witness feasibility, separately from source comparison and novelty. `python -m asd.selftest geometric_extremal` checks the API gate. `pipeline/integrate.py` freezes claims/tables and the existing `projects/geometric_extremal/state.json`; the two new claims passed Domain.check. Optional numerical search needs `requirements.txt`; exact replay needs no installed package. Search reruns can append logs, so copy the research directory before rerunning discovery.

The branch inherits the existing Lab infrastructure from `algo-efficiency` dff8d99. Review against that branch; main c622004 contains only the original chemistry script. Other lab domains are unchanged. The human supplied direction and authorized autonomous research; agents chose targets, implemented searches, exact certification and adversarial review. Public methods and constructions are credited. No researcher contact or external endorsement is implied.

Raw negative and intermediate candidate trials are losslessly bundled in `trial_archives/` to keep the PR reviewable. Their per-file hashes are verified during restoration by `trial_archives/bundle_trials.py`. Both canonical result witnesses remain ordinary directly reviewable JSON files. The complete local release zip also contains every original unbundled trial. `verify_archive.py` and full pipeline reintegration restore missing trials from these bundles automatically.


## Paper document.pdf and presentation materials

The exact PDF supplied as `document.pdf` is preserved at [paper/document.pdf](paper/document.pdf), with a complete text extraction at [paper/document.txt](paper/document.txt). Earlier manuscript sources and the original research archive remain in this directory.

The [presentation package](presentation/README.md) contains an offline interactive lab, six-slide HTML/PDF presentation, handout, SVG/PNG figures, speaker notes, coordinates, exact distance histograms, and an independent Python verifier. Open `presentation/index.html` in a browser or run:

```sh
python3 research/geometric-extremal/presentation/verify.py
python3 research/geometric-extremal/results/reproduce.py
python3 research/geometric-extremal/wave2/paper/verify_witnesses.py
```

The new publication supplement has a separate hash manifest at `presentation/CONTENTS_SHA256.json`. No global optimality is asserted: the certified statements are G(31) >= 81 and G(41) >= 111.
