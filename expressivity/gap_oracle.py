"""Independent oracle: GAP 4 (exact cyclotomic character tables). Computes, for a permutation group, the codimension of the fixed
space and the multiplicity of eigenvalue -1 of every real irreducible representation on every conjugacy class, the kernels, and
the class of every element. Exact rationals throughout; GAP refuses non-integral results by construction (we check integrality).
"""
import json, os, shutil, subprocess, tempfile

GAP = os.environ.get("GAP_EXE") or shutil.which("gap") or os.path.expanduser("~/.conda_envs/gap/bin/gap")

SCRIPT = r"""
SizeScreen([60000, 1000]);;
G := Group(%s);;
t := CharacterTable(G);; irr := Irr(t);; nc := NrConjugacyClasses(t);; ords := OrdersClassRepresentatives(t);;
cl := ConjugacyClasses(t);;
real := [];; used := [];;
for i in [1..Length(irr)] do
  if not i in used then
    ind := Indicator(t, [irr[i]], 2)[1];
    if ind = 1 then Add(real, [ind, irr[i]]); Add(used, i);
    elif ind = -1 then Add(real, [ind, 2*irr[i]]); Add(used, i);
    else
      j := Position(irr, ComplexConjugate(irr[i]));
      Add(real, [ind, irr[i] + irr[j]]); Add(used, i); Add(used, j);
    fi;
  fi;
od;
Print("BEGIN\n");
for r in real do
  psi := r[2];
  cod := List([1..nc], c -> psi[1] - Sum([0..ords[c]-1], j -> psi[PowerMap(t, j)[c]]) / ords[c]);
  mm := List([1..nc], function(c) if ords[c] mod 2 = 0 then return Sum([0..ords[c]-1], j -> (-1)^j * psi[PowerMap(t, j)[c]]) / ords[c]; else return 0; fi; end);
  ker := Filtered([1..nc], c -> psi[c] = psi[1]);
  Print("IRREP ", psi[1], " ", r[1], " ", cod, " ", mm, " ", ker, "\n");
od;
for g in Elements(G) do
  Print("ELT ", ListPerm(g, %d), " ", PositionProperty(cl, c -> g in c), "\n");
od;
Print("END\n");
QUIT;
"""


def _gap_perm(p):
    """0-based image tuple -> GAP cycle notation (1-based)."""
    seen = set(); cyc = []
    for i in range(len(p)):
        if i in seen or p[i] == i: continue
        c = []; j = i
        while j not in seen: seen.add(j); c.append(j + 1); j = p[j]
        cyc.append("(" + ",".join(map(str, c)) + ")")
    return "".join(cyc) or "()"


def codim_table_gap(G, timeout=600):
    if not os.path.exists(GAP): raise FileNotFoundError("GAP not installed")
    gens = ", ".join(_gap_perm(g) for g in G.gens)
    with tempfile.NamedTemporaryFile("w", suffix=".g", delete=False) as f:
        f.write(SCRIPT % (f"[{gens}]" if gens else "[()]", G.n)); path = f.name
    out = subprocess.run([GAP, "-q", "-b", path], capture_output=True, text=True, timeout=timeout).stdout
    os.unlink(path)
    lines = out[out.index("BEGIN"):out.index("END")].splitlines()[1:]
    codim, minus, kernels, irreps, cls = [], [], [], [], {}
    for line in lines:
        if line.startswith("IRREP"):
            parts = line.split(" ", 3)
            deg, ind = int(parts[1]), int(parts[2])
            rest = parts[3]
            lists = json.loads("[" + rest.replace("] [", "],[") + "]")
            cd, mm, ker = lists
            if any(isinstance(x, float) or (isinstance(x, str)) for x in cd + mm): raise ArithmeticError("non-integral")
            irreps.append({"deg": deg, "fs": ind}); codim.append([int(x) for x in cd]); minus.append([int(x) for x in mm])
            kernels.append(frozenset(c - 1 for c in ker))
        elif line.startswith("ELT"):
            _, rest = line.split(" ", 1)
            perm_s, c = rest.rsplit(" ", 1)
            cls[tuple(x - 1 for x in json.loads(perm_s))] = int(c) - 1
    if len(cls) != G.order: raise ArithmeticError("GAP element list incomplete")
    return {"irreps": irreps, "codim": codim, "minus": minus, "kernels": kernels, "n_classes": len(codim[0]),
            "class_of": lambda g: cls[tuple(g)], "class_map": cls}
