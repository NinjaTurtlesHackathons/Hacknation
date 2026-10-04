"""T6: consistent() loopholes. Each answer below has checks that ALL pass check() and passes consistent(), yet its text
contradicts the truth or the certificate. Mirrors asd.discovery.solve_cascade acceptance: all checks pass and consistent()."""
import json
from expressivity.domain import DOMAIN

def accepted(ans):
    ps = [q for q in (ans.get("pruefungen") or [ans.get("pruefung")]) if isinstance(q, dict)]
    res = [DOMAIN.check(q)[0] for q in ps]
    return bool(ps) and all(res) and all(DOMAIN.consistent(ans, q) for q in ps), res

cases = [
    ("number only in text, no 'zahl' field; contradicts the certificate h*(A5,all)=2",
     {"antwort": "h*(A5, all) = 1, a single reflection suffices", "pruefungen": [{"typ": "hstar_lower", "group": "A5", "alphabet": "all", "k": 2}]}),
    ("negative answer backed by the trivial lower bound k=0 (truth: h*(S3,transpositions)=1, HH_1 suffices)",
     {"antwort": "No, DeltaNet (HH_1) cannot track S3 with transpositions", "pruefungen": [{"typ": "hstar_lower", "group": "S3", "alphabet": "transpositions", "k": 0}]}),
    ("h vs h* confusion: zahl matched by h_faithful, text about h*",
     {"antwort": "h*(S5, all) = 4", "zahl": 4, "pruefungen": [{"typ": "h_faithful", "group": "S5", "alphabet": "all", "value": 4}]}),
    ("check about an unrelated group",
     {"antwort": "Yes, A5 with all letters needs only 1 reflection", "zahl": 1, "pruefungen": [{"typ": "hstar_value", "group": "A5", "alphabet": "involutions", "value": 1}]}),
    ("number word instead of digit",
     {"antwort": "h*(A5, all) equals one", "pruefungen": [{"typ": "realisation", "group": "A5", "alphabet": "all", "k": 2, "construction": "so3", "twist": "none"}]}),
    ("negation not caught by regex ('does not')",
     {"antwort": "Two reflections are enough? This does not hold; S4 needs more than two", "pruefungen": [{"typ": "realisation", "group": "S4", "alphabet": "all", "k": 2, "construction": "so3", "twist": "none"}]}),
    ("zahl=True coerces to 1.0",
     {"antwort": "yes", "zahl": True, "pruefungen": [{"typ": "hstar_value", "group": "A5", "alphabet": "involutions", "value": 1}]}),
]
for name, ans in cases:
    ok, res = accepted(ans)
    print(f"[{'LOOPHOLE' if ok else 'blocked '}] {name}\n    answer={json.dumps(ans)}\n    checks pass={res}")
print("\nNote: only describe(first check) is published as 'text'; the answer text is stored as 'interpretation_ungeprueft' but it is"
      " what solve_cascade returns as the agent's answer and what discovery scoring compares against.")
