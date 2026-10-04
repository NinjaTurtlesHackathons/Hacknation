Read("cover_search.g");
G := SymmetricGroup(5);;
letters := [(1,2), (1,2,3,4,5)];;   # alphabet tn (class representatives suffice: the best lift depends only on the class)
for n in [120, 240, 360, 480, 600, 720, 840] do
  cnt := 0;
  for i in [1..NrSmallGroups(n)] do
    H := SmallGroup(n, i);
    if not IsSolvable(H) then
      r := SearchH(H, G, letters, 3);
      if r <> fail then cnt := cnt + 1; fi;
      if r <> fail and r <> false then Print("FOUND ", IdGroup(H), " ", StructureDescription(H), " dims ", r.dims, "\n"); fi;
    fi;
  od;
  Print("order ", n, ": ", cnt, " groups onto S5 checked, target 3, alphabet tn\n");
od;
QUIT;
