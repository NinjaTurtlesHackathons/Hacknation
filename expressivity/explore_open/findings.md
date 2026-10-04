# Explorer findings (open intervals of h*), written from the explorer subagent's report; certificates re-checked independently

All certificates: `certs/*.json`, re-checked with the exact verifier by `python -m expressivity.explore_open.recheck_all`
-> `../results/explore_certified.json` (18 of 18 pass).

| Finding | Method | Status |
|---|---|---|
| h*(Q8, all) <= 3 (better than the faithful h = 4): cover H = C4:C4 (SmallGroup(16,4)), a -> i, b -> j, rational 4-dim representation a -> R + I, b -> F + R (R = rotation by 90 degrees, F = diag(1, -1)) | `q8_k3_cert.py`, `certs/SG8_4_k3.json` | CERTIFIED |
| 17 atlas upper bounds lowered by covers of order 2 abs(G) (16_12 5->4, 16_13 4->3, 32_8 8->5, 32_24 6->4, 32_26 6->5, 32_29 5->4, 32_30 6->4, 32_31 6->4, 32_32 8->5, 32_33 8->4, 32_35 6->4, 32_44 8->5, 32_48 5->4, 32_50 8->5, 48_34 5->4, 48_39 6->4, 48_40 6->5) | `certify_cover.py`, `certs/SG*_k*.json` | CERTIFIED |
| Further 4->3, 5->4, 6->4/5 improvements for 23 atlas groups (exact GAP characters; certificates need irrational entries) | `atlas_search*.log` | CANDIDATE (not certified) |
| A rational matrix with a letter of order 5, 8 or 12 has rank(M - I) >= 4 (>= 6 for order 7 or 9), so rational certificates cannot give k < 4 for such groups | cyclotomic degree argument | ARGUMENT (hand) |
| h*(Q8, all) >= 3, hence = 3 | lifts of i, j are planar rotations in SO(4); finite subgroups of S^3 x S^3 / +-1; Goursat; GAP: no cover of order <= 120 reaches k = 2 | ARGUMENT (hand) + computational support |
| h*(S5, tn) >= 3 and h*(S5, all) >= 3, unconditional | no finite subgroup of SO(4) or O(3) maps onto S5; a rank-2 orthogonal map has det +1, so the transposition lift is a reflection | ARGUMENT (hand) |
| h*(S5, Sigma) = 4 for every generating Sigma containing a 5-cycle | Lange–Mikhailova classification (arXiv:1509.06922) | ARGUMENT (hand, conditional on the classification); consistent with C5 (via arXiv:2609.24797) |
| S5/tn with k = 3: no cover of order <= 720 works (31 covers) | `s5_search.log` | NEGATIVE |
| SL(2,3) and other open rows: no improvement from covers of order 2 abs(G) (some also 3 abs(G), 4 abs(G)) | GAP search | NEGATIVE |
