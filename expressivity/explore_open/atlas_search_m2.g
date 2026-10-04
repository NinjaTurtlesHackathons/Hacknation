# For every open atlas row (G, alphabet all): scan covers H -> G with |H| = m |G| (m in MULTS, |H| <= MAXH, orders in SKIP
# omitted) and record the smallest target k for which some faithful real representation of H gives every letter class a lift
# with codim Fix <= k. Exact character theory.
Read("cover_search.g"); Read("atlas_rows.g");
MULTS := [2];; MAXH := 126;; SKIP := [];;
for row in ROWS{[START..Length(ROWS)]} do
  G := SmallGroup(row[1], row[2]);
  letters := List(Filtered(ConjugacyClasses(G), c -> Representative(c) <> One(G)), Representative);
  best := row[3]; witness := "none";
  for m in MULTS do
    n := m * row[1];
    if n > MAXH or n in SKIP then continue; fi;
    for i in [1 .. NrSmallGroups(n)] do
      if best = 2 then break; fi;
      H := SmallGroup(n, i);
      if not IsSolvable(G) and IsSolvable(H) then continue; fi;
      for target in [2 .. best - 1] do
        r := SearchH(H, G, letters, target);
        if r = fail then break; fi;
        if r <> false then best := target; witness := [IdGroup(H), r.dims]; break; fi;
      od;
    od;
  od;
  Print("ROW ", row[1], "_", row[2], " ", StructureDescription(G), " old_upper ", row[3], " new_upper ", best, " witness ", witness, "\n");
od;
Print("ALLDONE\n");
QUIT;
