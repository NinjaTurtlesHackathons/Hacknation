# Exhaustive search over covering groups H -> G (H from the SmallGroups library) for a faithful real representation of H in which
# every letter class of G has a preimage with codim Fix <= target. Exact character theory (GAP cyclotomics).
# Usage: set G, letterClassReps (elements of G), orders (list of |H|), target; then Read this file and call RunSearch().

RealIrreps := function(t)
  local irr, real, used, i, j, ind;
  irr := Irr(t); real := []; used := [];
  for i in [1..Length(irr)] do
    if not i in used then
      ind := Indicator(t, [irr[i]], 2)[1];
      if ind = 1 then Add(real, irr[i]); Add(used, i);
      elif ind = -1 then Add(real, 2*irr[i]); Add(used, i);
      else j := Position(irr, ComplexConjugate(irr[i])); Add(real, irr[i] + irr[j]); Add(used, i); Add(used, j);
      fi;
    fi;
  od;
  return real;
end;

CodimVec := function(t, psi)
  local ords, nc;
  ords := OrdersClassRepresentatives(t); nc := NrConjugacyClasses(t);
  return List([1..nc], c -> psi[1] - Sum([0..ords[c]-1], j -> psi[PowerMap(t, j)[c]]) / ords[c]);
end;

# DFS over subsets of nontrivial real irreps (index increasing); feas[l] = list of [preimage class, partial codim]
FeasibleSet := function(cods, kers, preim, target, idclass)
  local nirr, best, dfs;
  nirr := Length(cods); best := fail;
  dfs := function(start, chosen, feas, ker)
    local i, nf, ok, l, f, nk;
    if ker = [idclass] then best := ShallowCopy(chosen); return true; fi;
    for i in [start..nirr] do
      nk := Intersection(ker, kers[i]);
      if nk <> ker then
        nf := []; ok := true;
        for l in [1..Length(feas)] do
          f := List(Filtered(feas[l], p -> p[2] + cods[i][p[1]] <= target), p -> [p[1], p[2] + cods[i][p[1]]]);
          if f = [] then ok := false; break; fi;
          Add(nf, f);
        od;
        if ok then
          Add(chosen, i);
          if dfs(i + 1, chosen, nf, nk) then return true; fi;
          Remove(chosen);
        fi;
      fi;
    od;
    return false;
  end;
  dfs(1, [], List(preim, p -> List(p, c -> [c, 0])), [1..Length(cods[1])]);
  return best;
end;

SearchH := function(H, G, letters, target)
  local epis, t, real, cods, kers, cl, idclass, epi, K, preim, g, h0, S, res, nontriv, i;
  epis := GQuotients(H, G);
  if epis = [] then return fail; fi;
  t := CharacterTable(H); real := RealIrreps(t); cl := ConjugacyClasses(t);
  idclass := PositionProperty(cl, c -> One(H) in c);
  nontriv := Filtered(real, psi -> ForAny(psi, x -> x <> psi[1]));
  cods := List(nontriv, psi -> CodimVec(t, psi));
  kers := List(nontriv, psi -> Filtered([1..Length(psi)], c -> psi[c] = psi[1]));
  for epi in epis do
    K := Kernel(epi);
    preim := [];
    for g in letters do
      h0 := PreImagesRepresentative(epi, g);
      Add(preim, Set(List(Elements(K), x -> PositionProperty(cl, c -> h0 * x in c))));
    od;
    S := FeasibleSet(cods, kers, preim, target, idclass);
    if S <> fail then
      return rec(H := IdGroup(H), irreps := List(S, i -> nontriv[i]), dims := List(S, i -> nontriv[i][1]),
                 epiimages := List(GeneratorsOfGroup(H), x -> Image(epi, x)), gens := GeneratorsOfGroup(H));
    fi;
  od;
  return false;
end;

RunSearch := function(G, letters, orders, target)
  local n, i, H, r, cnt, found;
  found := [];
  for n in orders do
    cnt := 0;
    for i in [1..NrSmallGroups(n)] do
      H := SmallGroup(n, i);
      r := SearchH(H, G, letters, target);
      if r <> fail then cnt := cnt + 1; fi;
      if r <> fail and r <> false then Print("FOUND ", IdGroup(H), " ", StructureDescription(H), " dims ", r.dims, "\n"); Add(found, r); fi;
    od;
    Print("order ", n, ": ", cnt, " groups with a quotient onto G checked\n");
  od;
  return found;
end;
