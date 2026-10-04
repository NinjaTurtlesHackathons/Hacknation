Read("cover_search.g");
G := SmallGroup(8, 4);;
letters := List(Filtered(ConjugacyClasses(G), c -> Size(c) > 0 and Representative(c) <> One(G)), Representative);;
Print("letter classes: ", Length(letters), "\n");
found := RunSearch(G, letters, [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120], 3);;
Print("TOTAL FOUND ", Length(found), "\n");
QUIT;
