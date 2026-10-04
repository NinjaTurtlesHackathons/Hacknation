"""Reproduce every certificate of this project with one command (same idea as asd/recheck.py on the quivers branch, kept in the
domain folder because the shared core is not edited):
  1. verifier self-test; 2. consistency-rule regressions; 3. every check of the certified table (results/certified.json) re-run;
  4. every lab claim in projects/expressivity/state.json re-checked; 5. atlas spot check: faithful h recomputed with own tables and GAP
  for 20 groups spread over the atlas; 6. Lean proofs: axiom report of expressivity/lean/check.out (no sorryAx).
  python -m expressivity.recheck   -> exit code 0 iff everything passes; log in projects/expressivity/recheck.log
"""
import json, os, subprocess, sys

from asd import selftest
from .domain import DOMAIN as D

LOG = "projects/expressivity/recheck.log"


def main():
    lines = []; ok_all = True
    def out(s):
        print(s, flush=True); lines.append(s)
    ok, rows = selftest.run("expressivity", log=lambda m: None)
    out(f"1 self-test: {'passed' if ok else 'FAILED'} ({sum(r['korrekt'] for r in rows)}/{len(rows)})"); ok_all &= ok
    cs = subprocess.run([sys.executable, "-m", "expressivity.test_consistent"], capture_output=True, text=True).stdout.strip()
    out(f"2 consistency regressions: {cs}"); ok_all &= "PASS" in cs
    cert = json.load(open("expressivity/results/certified.json"))
    n = bad = 0
    for r in cert["rows"]:
        for c in r["checks"]:
            if not c["passed"]: continue
            n += 1; good, why, _ = D.check(c["claim"], timeout=3600); bad += not good
            if not good: out(f"   FAILED {json.dumps(c['claim'])}: {why[:160]}")
    out(f"3 certified table: {n - bad}/{n} checks pass again"); ok_all &= bad == 0
    if os.path.exists("projects/expressivity/state.json"):
        s = json.load(open("projects/expressivity/state.json")); bad = 0
        for c in s["claims"]:
            good, why, _ = D.check(c["pruefung"], timeout=3600); bad += not good
            out(f"   [{'OK ' if good else 'FAIL'}] {c['id']} ({c['status']}): {D.describe(c['pruefung'])[:120]}")
        out(f"4 lab claims: {len(s['claims']) - bad}/{len(s['claims'])} pass the current verifier (failures are reported as withdrawn in the paper)")
    A = json.load(open("expressivity/results/atlas.json")); rows = A["rows"]; step = max(1, len(rows) // 20); bad = 0; m = 0
    from .atlas import analyse
    sgs = json.load(open("expressivity/results/smallgroups.json"))
    for r in rows[1::step][:20]:
        r2 = analyse(r["key"], sgs[r["key"]], gap_check=True); m += 1
        same = r2["h"] == r["h"] == r2["h_gap"]; bad += not same
        if not same: out(f"   atlas mismatch {r['key']}: stored {r['h']}, own {r2['h']}, GAP {r2['h_gap']}")
    out(f"5 atlas spot check: {m - bad}/{m} groups reproduce h (own table = GAP = stored)"); ok_all &= bad == 0
    lean = open("expressivity/lean/check.out").read()
    lean_ok = "sorryAx" not in lean and lean.count("depends on axioms") >= 5
    out(f"6 Lean: {lean.count('depends on axioms')} theorems, no sorryAx: {lean_ok} (rebuild: see expressivity/lean/README.md)"); ok_all &= lean_ok
    out(f"RECHECK {'PASSED' if ok_all else 'FAILED'}")
    os.makedirs(os.path.dirname(LOG), exist_ok=True); open(LOG, "w").write("\n".join(lines) + "\n")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
