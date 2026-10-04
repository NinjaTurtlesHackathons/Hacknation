"""Independent re-check of every explorer certificate with the exact verifier: expressivity/explore_open/certs/*.json -> results/explore_certified.json"""
import glob, json, os
from expressivity.domain import DOMAIN as D
out = []
for f in sorted(glob.glob("expressivity/explore_open/certs/*.json")):
    c = json.load(open(f)); ok, why, ev = D.check(c, timeout=3600)
    out.append({"file": os.path.basename(f), "group": c.get("group"), "alphabet": c.get("alphabet"), "k": c.get("k"), "passed": bool(ok), "reason": why})
    print(os.path.basename(f), ok, why[:110], flush=True)
json.dump(out, open("expressivity/results/explore_certified.json", "w"), indent=1)
print(sum(o["passed"] for o in out), "of", len(out), "certificates pass")
