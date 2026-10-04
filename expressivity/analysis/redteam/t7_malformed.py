"""T7: malformed / boundary inputs. Does check() refuse cleanly, does it stay within time, and does describe() ever print a
sentence that check() did not prove? Each claim runs in a child process with a 90 s wall-clock limit (a SIGALRM inside
check() is swallowed by its own `except Exception`, so the verifier has no internal time limit at all)."""
import json, os, subprocess, sys, time
from expressivity.domain import DOMAIN

CHILD = "import json,sys; from expressivity.domain import DOMAIN; p=json.loads(sys.argv[1]); ok,why,_=DOMAIN.check(p); print(json.dumps([ok, why]))"
def run(p, limit=90):
    try:
        r = subprocess.run([sys.executable, "-c", CHILD, json.dumps(p)], capture_output=True, text=True, timeout=limit)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired: return [f"TIMEOUT(>{limit}s)", ""]

claims = [
    {"typ": "realisation", "group": "A5", "alphabet": "all", "k": 10**9, "construction": "so3"},
    {"typ": "realisation", "group": "A5", "alphabet": "all", "k": -1, "construction": "so3"},
    {"typ": "realisation", "group": "A5", "alphabet": "all", "k": 16, "construction": "so3"},
    {"typ": "realisation", "group": "S3", "alphabet": "cycles3", "k": 2, "construction": "perm"},
    {"typ": "realisation", "group": "S3", "alphabet": "list:1,2", "k": 2, "construction": "perm"},
    {"typ": "realisation", "group": "S3", "alphabet": "all", "k": 2, "construction": "planar"},
    {"typ": "realisation", "group": "S3", "alphabet": "all", "k": 2, "construction": "planar", "twist": "all"},
    {"typ": "realisation", "group": "Z2^6", "alphabet": "all", "k": 1, "construction": "count"},
    {"typ": "realisation", "group": "Z257", "alphabet": "gens", "k": 2, "construction": "planar"},
    {"typ": "realisation", "group": "Z60", "alphabet": "gens", "k": 2, "construction": "planar"},
    {"typ": "realisation", "group": "SG8_3", "alphabet": "all", "k": 2, "construction": "perm"},
    {"typ": "realisation", "group": " A5", "alphabet": "all", "k": 2, "construction": "so3"},
    {"typ": "realisation", "group": "A5\n", "alphabet": "all", "k": 2, "construction": "so3"},
    {"typ": "realisation", "group": "A5", "alphabet": "all", "k": 2, "construction": "so3", "Tolerance": 1},
    {"typ": "realisation", "group": "A5", "alphabet": "all", "k": 2, "construction": "so3", "tol_rel": 1, "max_k": 99},
    {"typ": "hstar_value", "group": "Z2^4", "alphabet": "all", "value": 1},
    {"typ": "hstar_value", "group": "S1", "alphabet": "all", "value": 1},
    {"typ": "hstar_lower", "group": "Z3", "alphabet": "all", "k": 0},
    {"typ": "diag_realisable", "family": "cdiag", "group": "Z2^2", "alphabet": "all", "value": True},
    {"typ": "diag_realisable", "family": "diag_pos", "group": "D1", "alphabet": "all", "value": True},
    {"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["-1"]]], "construction": "so3"},
]
for p in claims:
    t0 = time.time(); ok, why = run(p)
    print(f"{json.dumps(p)[:120]}\n   -> {ok} ({time.time()-t0:.1f}s) {why[:140]}")
    if ok is True: print("   PUBLISHED:", DOMAIN.describe(p))

print("\nGAP unavailable: h_faithful still passes and describe() still says 'own and GAP'")
import expressivity.gap_oracle as go
go.GAP = "/nonexistent/gap"
p = {"typ": "h_faithful", "group": "Q8", "alphabet": "all", "value": 4}
ok, why, ev = DOMAIN.check(p); print("  ", ok, why, "\n   PUBLISHED:", DOMAIN.describe(p))
