"""Regression tests for DOMAIN.consistent (lab round-1 loophole EX10 and red-team bug 3). python -m expressivity.test_consistent"""
from .domain import DOMAIN as D

CASES = [
    ({"antwort": "h*(A5, all) = 1, a single reflection suffices", "pruefungen": [{"typ": "hstar_lower", "group": "A5", "alphabet": "all", "k": 2}]}, False),
    ({"antwort": "No, DeltaNet (HH_1) cannot track S3 with transpositions", "pruefungen": [{"typ": "hstar_lower", "group": "S3", "alphabet": "transpositions", "k": 0}]}, False),
    ({"antwort": "h*(S5, all) = 4", "zahl": 4, "pruefungen": [{"typ": "h_faithful", "group": "S5", "alphabet": "all", "value": 4}]}, False),
    ({"antwort": "It does not hold", "pruefungen": [{"typ": "realisation", "group": "A5", "alphabet": "all", "k": 2, "construction": "so3", "twist": "none"}]}, False),
    ({"antwort": "Nein", "zahl": 2, "pruefungen": [{"typ": "realisation", "group": "A5", "alphabet": "involutions", "k": 2, "construction": "so3", "twist": "none"},
                                                    {"typ": "h_faithful", "group": "A5", "alphabet": "involutions", "value": 2}]}, False),
    ({"antwort": "yes", "zahl": True, "pruefungen": [{"typ": "hstar_value", "group": "Z2", "alphabet": "all", "value": 1}]}, False),
    ({"antwort": "Yes: h*(A5, involutions) = 1, one reflection per token suffices", "zahl": 1, "pruefungen": [{"typ": "hstar_value", "group": "A5", "alphabet": "involutions", "value": 1}]}, True),
    ({"antwort": "No: h*(A5, all) = 2, one reflection is not enough", "zahl": 2, "pruefungen": [{"typ": "hstar_value", "group": "A5", "alphabet": "all", "value": 2}]}, True),
]

if __name__ == "__main__":
    res = [D.consistent(a, a["pruefungen"][0]) == w for a, w in CASES]
    print(f"consistent() regressions: {sum(res)}/{len(res)} {'PASS' if all(res) else 'FAIL'}")
