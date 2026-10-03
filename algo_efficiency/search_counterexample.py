"""Exact counterexample search for two statements on multi-draft speculative decoding (V <= 6, k <= 4):
  (S1) optimal acceptance without replacement >= optimal acceptance with iid drafts   (hand proof exists, see write_paper.py)
  (S2) rrs_wor acceptance >= rrs_iid acceptance                                      (conjecture)
Instances: seeded Dirichlet draws with concentration in {0.1, 0.3, 1, 3}; exact rationals (denominator 1000).
  python -m algo_efficiency.search_counterexample [n]   ->  algo_efficiency/results/counterexample_search.json"""
import json, sys
from fractions import Fraction
from . import spec as S
from .domain import DOMAIN as D

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000; found = {"S1": [], "S2": []}; tested = 0; minmargin = {"S1": None, "S2": None}
for seed in range(n):
    V = 3 + seed % 4; k = 2 + (seed // 4) % 3; conc = (0.1, 0.3, 1.0, 3.0)[(seed // 12) % 4]
    if V ** k > 1300: k = 2
    x = S.random_instance(V=V, seed=10000 + seed, family="dirichlet", conc=conc); P, Q = S.parse_pair(x["p"], x["q"])
    oi, _ = S.optimal_multidraft(P, Q, k, "iid"); ow, _ = S.optimal_multidraft(P, Q, k, "wor")
    ri = S.step_output(P, Q, "rrs_iid", k=k)[1]; rw = S.step_output(P, Q, "rrs_wor", k=k)[1]; tested += 1
    for key, d in (("S1", ow - oi), ("S2", rw - ri)):
        minmargin[key] = d if minmargin[key] is None else min(minmargin[key], d)
        if d < 0:
            inst = {"p": x["p"], "q": x["q"], "k": k, "seed": 10000 + seed}
            if key == "S2":   # certify both values through the domain verifier
                inst["check_iid"] = D.check({"typ": "scheme_acceptance", "p": x["p"], "q": x["q"], "rule": "rrs_iid", "k": k, "value": S.fstr(ri)})[:2]
                inst["check_wor"] = D.check({"typ": "scheme_acceptance", "p": x["p"], "q": x["q"], "rule": "rrs_wor", "k": k, "value": S.fstr(rw)})[:2]
            inst.update(iid=S.fstr(ri if key == "S2" else oi), wor=S.fstr(rw if key == "S2" else ow)); found[key].append(inst)
res = {"tested": tested, "counterexamples": {k: v[:5] for k, v in found.items()}, "n_counterexamples": {k: len(v) for k, v in found.items()},
       "min_margin": {k: S.fstr(v) for k, v in minmargin.items()}}
json.dump(res, open("algo_efficiency/results/counterexample_search.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "counterexamples"}), json.dumps(res["counterexamples"])[:600])
