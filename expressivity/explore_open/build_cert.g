# Build explicit rational matrices for a cover witness found by cover_search.g.
# Inputs (set before Read): GN, GI (SmallGroup id of G), VGENS (verifier generators, 1-based image lists), HN, HI, TARGET, OUT.
SizeScreen([100000, 1000]);;
Read("cover_search.g");
RationalModule := function(H, psi, t)
  local cl, K, hom, deg, P, h, B, ok, cand, pos;
  if not ForAll(psi, IsRat) then return fail; fi;
  cl := ConjugacyClasses(t);
  for cand in ConjugacyClassesSubgroups(H) do
    K := Representative(cand);
    hom := FactorCosetAction(H, K); deg := Index(H, K);
    P := NullMat(deg, deg);
    for h in Elements(H) do
      pos := PositionProperty(cl, c -> h^-1 in c);
      P := P + psi[pos] * PermutationMat(Image(hom, h), deg);
    od;
    B := BaseMat(P);
    if Length(B) = psi[1] then return [hom, deg, B]; fi;
  od;
  return fail;
end;

G := SmallGroup(GN, GI);; H := SmallGroup(HN, HI);;
letters := List(Filtered(ConjugacyClasses(G), c -> Representative(c) <> One(G)), Representative);;
t := CharacterTable(H);; real := RealIrreps(t);; cl := ConjugacyClasses(t);;
nontriv := Filtered(real, psi -> ForAny(psi, x -> x <> psi[1]) and ForAll(psi, IsRat));;   # rational-valued only
cods := List(nontriv, psi -> CodimVec(t, psi));;
kers := List(nontriv, psi -> Filtered([1..Length(psi)], c -> psi[c] = psi[1]));;
idclass := PositionProperty(cl, c -> One(H) in c);;
chosen := fail;;
for epi in GQuotients(H, G) do
  K := Kernel(epi);
  preim := List(letters, g -> Set(List(Elements(K), x -> PositionProperty(cl, c -> PreImagesRepresentative(epi, g) * x in c))));
  S := FeasibleSet(cods, kers, preim, TARGET, idclass);
  if S <> fail then chosen := [epi, S]; break; fi;
od;;
if chosen = fail then PrintTo(OUT, "FAIL no rational-valued solution\n"); FORCE_QUIT_GAP(0); fi;
epi := chosen[1];; S := chosen[2];; K := Kernel(epi);;
mods := List(S, i -> RationalModule(H, nontriv[i], t));;
if fail in mods then PrintTo(OUT, "FAIL irrational\n"); else
Rep := function(h)   # block-diagonal matrix, row-vector convention
  local blocks, m, M;
  blocks := [];
  for m in mods do
    M := m[3] * PermutationMat(Image(m[1], h), m[2]);
    Add(blocks, List(M, row -> SolutionMat(m[3], row)));
  od;
  return DirectSumMat(blocks);
end;;
P := Group(List(VGENS, PermList));;
iso := IsomorphismGroups(P, G);;
codS := h -> Sum(S, i -> cods[i][PositionProperty(cl, c -> h in c)]);;
PrintTo(OUT, "[\n");
first := true;;
for p in Elements(P) do
  if p = One(P) then continue; fi;
  g := Image(iso, p); h0 := PreImagesRepresentative(epi, g);
  best := fail; bc := infinity;
  for x in Elements(K) do if codS(h0 * x) < bc then bc := codS(h0 * x); best := h0 * x; fi; od;
  if not first then AppendTo(OUT, ",\n"); fi; first := false;
  AppendTo(OUT, "[", ListPerm(p, LargestMovedPoint(P)), ", ", List(Rep(best), r -> List(r, String)), "]");
od;
AppendTo(OUT, "\n]\n");
fi;
QUIT;
