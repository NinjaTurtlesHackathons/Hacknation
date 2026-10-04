#!/usr/bin/env python3
"""Necessary, not sufficient, test for arbitrary unit triangular blades on Pa cores."""
import json,sys
from pathlib import Path
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parents[3]/'candidates/wave2_joint_palette/k31_n81_r6_seed42102.json'
S={tuple(x) for x in json.loads(p.read_text())['points']};dirs=[(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]
hits=[]
for z in range(6):
 T=set(S)
 for _ in range(z):T={(-b,a+b) for a,b in T}
 for A in range(1,16):
  for r1 in range(1,16):
   for r2 in range(A+r1):
    P={(c,-j) for j in range(r1+1) for c in range(A+j)}|{(c,-r1-j) for j in range(1,r2+1) for c in range(j,A+r1)}
    if len(P)>len(S):continue
    minpa=min(a for a,b in P);maxpa=max(a for a,b in P);minpb=min(b for a,b in P);maxpb=max(b for a,b in P)
    for da in range(min(a for a,b in T)-minpa,max(a for a,b in T)-maxpa+1):
     for db in range(min(b for a,b in T)-minpb,max(b for a,b in T)-maxpb+1):
      C={(a+da,b+db) for a,b in P}
      if not C<=T:continue
      extra=T-C
      if all(any((a+dirs[j][0],b+dirs[j][1]) in C and (a+dirs[(j+1)%6][0],b+dirs[(j+1)%6][1]) in C for j in range(6)) for a,b in extra):hits.append({'rotation':z,'A':A,'r1':r1,'r2':r2,'offset':[da,db],'core_n':len(C),'blade_n':len(extra)})
out={'test':'necessary Pa-core plus individual unit triangle exterior site test, not complete arbitrary blade-definition equivalence','witness':str(p),'matches':hits,'parameter_ranges':{'A':[1,15],'r1':[1,15],'r2':'0..A+r1-1'},'meaning':'absence rejects this precise one-layer blade interpretation only; cannot prove literature novelty'}
(Path(__file__).with_suffix('.json') if len(sys.argv)<3 else Path(sys.argv[2])).write_text(json.dumps(out,indent=2)+'\n');print(out)
