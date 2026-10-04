"""Re-run the exact verifier on every saved certificate in certs/."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from expressivity.domain import DOMAIN as D
for f in sorted(os.listdir(os.path.join(HERE, "certs"))):
    c = json.load(open(os.path.join(HERE, "certs", f)))
    ok, why, ev = D.check(c)
    print(f, c["group"], "k =", c["k"], ok, "|H| =", ev.get("H_order"), "dim =", ev.get("dim"))
