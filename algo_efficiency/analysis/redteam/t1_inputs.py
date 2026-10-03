"""Red team T1: malformed / out-of-domain inputs that a verifier should reject. Prints (passed, reason) per probe."""
from algo_efficiency.domain import DOMAIN as D

p3, q3 = ["1/2", "1/4", "1/4"], ["1/5", "3/5", "1/5"]
probes = {
    # scaled rule: lambda is never range-checked
    "scaled lambda=-1 acceptance -1 (negative probability)": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "scaled", "lambda": -1, "value": "-1"},
    "scaled lambda=-1 unbiased True": {"typ": "unbiased", "p": p3, "q": q3, "rule": "scaled", "lambda": -1, "unbiased": True},
    "scaled lambda=0 acceptance 0": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "scaled", "lambda": 0, "value": "0"},
    # k is ignored for standard/scaled
    "standard with k=4 acceptance = single-draft value": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "standard", "k": 4, "value": "13/20"},
    "standard with k=0": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "standard", "k": 0, "value": "13/20"},
    "standard with k=-3": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "standard", "k": -3, "value": "13/20"},
    # lambda silently ignored for non-scaled rules, but printed by describe()
    "standard with lambda=5 unbiased": {"typ": "unbiased", "p": p3, "q": q3, "rule": "standard", "lambda": 5, "unbiased": True},
    # int() truncation of non-integer fields
    "rrs_iid k=2.9 (truncated to 2)": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "rrs_iid", "k": 2.9, "value": "77/100"},
    "rrs_iid k=True (bool -> 1)": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "rrs_iid", "k": True, "value": "13/20"},
    "gamma 8.7 (truncated to 8)": {"typ": "optimal_gamma", "alpha": "4/5", "c": "1/20", "gamma": 8.7},
    "exp_min_degree d=4.99": {"typ": "exp_min_degree", "B": 1, "eps": "5.1e-4", "error": "relative", "d": 4.99},
    "multidraft k=2.5": {"typ": "multidraft_optimal", "p": p3, "q": q3, "k": 2.5, "mode": "iid", "value": "43/50"},
    # unknown mode/bound/error spellings
    "multidraft mode='WOR' (typo)": {"typ": "multidraft_optimal", "p": p3, "q": q3, "k": 2, "mode": "WOR", "value": "43/50"},
    "scheme_optimal extra lambda": {"typ": "scheme_optimal", "p": p3, "q": q3, "k": 1, "rule": "rrs_iid", "optimal": True, "lambda": 3},
    "unbiased given as string 'false'": {"typ": "unbiased", "p": p3, "q": q3, "rule": "standard", "unbiased": "false"},
    "optimal given as string 'false'": {"typ": "scheme_optimal", "p": p3, "q": q3, "k": 2, "rule": "rrs_iid", "optimal": "false"},
    # forbidden key bypass via differently named key (should simply be ignored, not used)
    "key 'Tolerance' (case)": {"typ": "acceptance_rate", "p": p3, "q": q3, "value": "13/20", "Tolerance": 1},
    # k larger than support in wor
    "rrs_wor k=4 V=3": {"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "rrs_wor", "k": 4, "value": "1"},
    "multidraft wor k=4 V=3 value 1": {"typ": "multidraft_optimal", "p": p3, "q": q3, "k": 4, "mode": "wor", "value": "1"},
    # float vs fraction: 0.1 float is repr'd ('0.1') -> exact 1/10
    "float probabilities 0.1/0.2/0.7": {"typ": "acceptance_rate", "p": [0.1, 0.2, 0.7], "q": [0.7, 0.2, 0.1], "value": "2/5"},
    # q with zeros where p>0
    "q zero where p>0": {"typ": "unbiased", "p": ["1/2", "1/2"], "q": ["1", "0"], "rule": "rrs_wor", "k": 2, "unbiased": True},
}
for name, c in probes.items():
    ok, why, _ = D.check(c)
    print(f"{'PASS' if ok else 'fail'} | {name} | {why[:140]}")
print("describe() of the 'standard with lambda=5' claim:", D.describe(probes["standard with lambda=5 unbiased"]))
print("describe() of 'standard with k=4':", D.describe(probes["standard with k=4 acceptance = single-draft value"]))
print("describe() of 'gamma 8.7':", D.describe(probes["gamma 8.7 (truncated to 8)"]))
print("describe() of 'unbiased string false':", D.describe(probes["unbiased given as string 'false'"]))
