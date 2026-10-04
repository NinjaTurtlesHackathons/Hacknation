# Rational-valued characters only. Inverted scan (faster): for each H of order 2|G|, for each normal subgroup N of order 2 with H/N an open atlas group G,
# test targets 2 .. upper-1 for the epimorphism H -> H/N (alphabet all).
Read("cover_search.g"); Read("atlas_rows.g");
TestEpi := function(H, epi, G, target)
  local t, real, cl, idclass, nontriv, cods, kers, K, letters, preim, g, h0;
  t := CharacterTable(H); real := RealIrreps(t); cl := ConjugacyClasses(t);
  idclass := PositionProperty(cl, c -> One(H) in c);
  nontriv := Filtered(real, psi -> ForAny(psi, x -> x <> psi[1]) and ForAll(psi, IsRat));
  cods := List(nontriv, psi -> CodimVec(t, psi));
  kers := List(nontriv, psi -> Filtered([1..Length(psi)], c -> psi[c] = psi[1]));
  K := Kernel(epi);
  letters := List(Filtered(ConjugacyClasses(G), c -> Representative(c) <> One(G)), Representative);
  preim := List(letters, g -> Set(List(Elements(K), x -> PositionProperty(cl, c -> PreImagesRepresentative(epi, g) * x in c))));
  return FeasibleSet(cods, kers, preim, target, idclass);
end;
best := rec();; wit := rec();;
todo := Filtered(ROWS, r -> [r[1], r[2]] in TODO);;
for row in todo do best.(Concatenation(String(row[1]), "_", String(row[2]))) := row[3]; od;
for n in Set(List(todo, r -> 2 * r[1])) do
  if n > 126 then continue; fi;
  for i in [1..NrSmallGroups(n)] do
    H := SmallGroup(n, i);
    for N in Filtered(NormalSubgroups(H), x -> Size(x) = 2) do
      hom := NaturalHomomorphismByNormalSubgroup(H, N); Q := Image(hom); id := IdGroup(Q);
      key := Concatenation(String(id[1]), "_", String(id[2]));
      if IsBound(best.(key)) and best.(key) > 2 then
        G := SmallGroup(id[1], id[2]); iso := IsomorphismGroups(Q, G); epi := CompositionMapping(iso, hom);
        for target in [2 .. best.(key) - 1] do
          if TestEpi(H, epi, G, target) <> fail then best.(key) := target; wit.(key) := [n, i]; break; fi;
        od;
      fi;
    od;
  od;
  Print("done order ", n, "\n");
od;
for row in todo do
  key := Concatenation(String(row[1]), "_", String(row[2]));
  if IsBound(wit.(key)) then w := wit.(key); else w := "none"; fi;
  Print("ROW ", key, " old_upper ", row[3], " new_upper ", best.(key), " witness ", w, "\n");
od;
Print("ALLDONE\n");
QUIT;
