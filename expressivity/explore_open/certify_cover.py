"""Turn a cover witness (G = SmallGroup(GN, GI), H = SmallGroup(HN, HI), target k) into explicit rational matrices with GAP
(build_cert.g) and check them with the exact verifier (realisation_matrices, alphabet 'all')."""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
from expressivity.domain import DOMAIN as D
from expressivity.groups import get_group, alphabet
GAP = os.path.expanduser("~/.conda_envs/gap/bin/gap")


def certify(gn, gi, hn, hi, k, name=None):
    name = name or f"SG{gn}_{gi}"
    G = get_group(name); S = alphabet(G, "all")
    deg = max(len(g) for g in G.gens)
    vgens = [[x + 1 for x in g] for g in G.gens]
    out = tempfile.mktemp(suffix=".txt", dir=HERE)
    pre = f"GN := {gn};; GI := {gi};; HN := {hn};; HI := {hi};; TARGET := {k};; VGENS := {vgens};; OUT := \"{out}\";;\n"
    script = tempfile.mktemp(suffix=".g", dir=HERE)
    open(script, "w").write(pre + 'Read("build_cert.g");\n')
    subprocess.run([GAP, "-q", "-b", script], cwd=HERE, capture_output=True, text=True, timeout=3000, stdin=subprocess.DEVNULL)
    txt = open(out).read(); os.unlink(out); os.unlink(script)
    if txt.startswith("FAIL"): return None, txt.strip()
    data = json.loads(txt.replace("\n", " "))
    table = {}
    for perm, M in data:
        perm = tuple(x - 1 for x in perm) + tuple(range(len(perm), deg))
        table[perm[:deg]] = M
    results = []
    for variant in ("row", "col"):
        mats = []
        for s in S:
            M = table[tuple(s)]
            if variant == "col": M = [list(r) for r in zip(*M)]
            mats.append([[str(x) for x in r] for r in M])
        claim = {"typ": "realisation_matrices", "group": name, "alphabet": "all", "k": k, "matrices": mats}
        ok, why, ev = D.check(claim)
        results.append((variant, ok, why))
        if ok: return claim, why
    return None, results


if __name__ == "__main__":
    a = list(map(int, sys.argv[1:6])); name = sys.argv[6] if len(sys.argv) > 6 else None
    claim, why = certify(*a, name=name)
    print(why)
    if claim:
        fn = os.path.join(HERE, "certs", f"{claim['group']}_k{claim['k']}.json"); os.makedirs(os.path.dirname(fn), exist_ok=True)
        json.dump(claim, open(fn, "w")); print("saved", fn)
