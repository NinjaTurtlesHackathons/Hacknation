Read("cover_search.g");
G := SmallGroup(8, 4);;
letters := List(Filtered(ConjugacyClasses(G), c -> Representative(c) <> One(G)), Representative);;
found := RunSearch(G, letters, [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120], 2);;
Print("TOTAL FOUND target 2: ", Length(found), "\n");
QUIT;
