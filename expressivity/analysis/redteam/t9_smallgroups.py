"""T9: SG<n>_<i> groups (GROUP_RE accepts them; data from results/smallgroups.json, written by another team member during the
session). Does the stored permutation group really have GAP id [n, i]? One GAP call with IdGroup for every entry."""
import json, os, subprocess, tempfile
from expressivity.gap_oracle import GAP, _gap_perm
from expressivity.groups import get_group

path = os.path.join("expressivity", "results", "smallgroups.json")
sg = json.load(open(path))
keys = sorted(sg, key=lambda k: tuple(map(int, k.split("_"))))
lines = ["SizeScreen([60000, 1000]);;"]
for k in keys:
    gens = ", ".join(_gap_perm(tuple(g)) for g in sg[k]["gens"]) or "()"
    lines.append(f'Print("{k} ", IdGroup(Group([{gens}])), "\\n");')
lines.append("QUIT;")
with tempfile.NamedTemporaryFile("w", suffix=".g", delete=False) as f: f.write("\n".join(lines)); p = f.name
out = subprocess.run([GAP, "-q", "-b", p], capture_output=True, text=True, timeout=600).stdout; os.unlink(p)
bad = []; n = 0
for line in out.splitlines():
    if "[" not in line: continue
    k, rest = line.split(" ", 1); ids = json.loads(rest.replace(" ", "")); n += 1
    want = list(map(int, k.split("_")))
    if ids != want: bad.append((k, ids))
print(f"{n}/{len(keys)} entries checked with IdGroup; mismatches: {bad}")
# the in-process group must have the right order too
ordbad = [k for k in keys if get_group("SG" + k).order != int(k.split("_")[0])]
print("order mismatches in get_group:", ordbad)
from expressivity.domain import GROUP_RE
print("largest key:", keys[-1], "; regex admits SG up to 999_9999; missing key -> KeyError -> claim refused (sound)")
