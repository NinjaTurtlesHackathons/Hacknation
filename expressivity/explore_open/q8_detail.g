Read("cover_search.g");
G := SmallGroup(8, 4);;
letters := List(Filtered(ConjugacyClasses(G), c -> Representative(c) <> One(G)), Representative);;
found := RunSearch(G, letters, [16, 24, 32, 40, 48], 3);;
for id in [[64,59],[64,16],[32,0]] do
  if id[2] = 0 then continue; fi;
  H := SmallGroup(id[1], id[2]); r := SearchH(H, G, letters, 3);
  Print(id, " exponent ", Exponent(H), " irreps chosen (chars): ", r.irreps, "\n");
  Print("  rational-valued: ", ForAll(r.irreps, psi -> ForAll(psi, IsRat)), "\n");
od;
QUIT;
