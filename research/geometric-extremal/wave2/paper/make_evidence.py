#!/usr/bin/env python3
"""Freeze manuscript evidence; generates rows and a second, row-correlation count."""
from pathlib import Path
from collections import Counter
import json,hashlib
BASE=Path(__file__).resolve().parents[2]
items=[('S31','candidates/wave2_joint_palette/k31_n81_r6_seed42102.json',[[-2,-1,9],[-1,-2,9],[1,-1,9],[1,0,5],[2,1,8],[1,1,5],[1,2,8],[0,1,5],[-1,1,8],[-1,0,5]]),('S41','candidates/wave2_family/support_k41_n111_code7324998.json',[[-2,-1,10],[-1,-2,11],[1,-1,11],[1,0,7],[2,1,10],[1,1,6],[1,2,9],[0,1,6],[-1,1,9],[-1,0,6]])]
out={}
for name,rel,facets in items:
 p=BASE/rel;d=json.loads(p.read_text());pts=sorted(map(tuple,d['points']));rows=[]
 for a in sorted({a for a,b in pts}):
  bs=sorted(b for x,b in pts if x==a);assert bs==list(range(min(bs),max(bs)+1));rows.append([a,min(bs),max(bs)])
 generated=[(a,b) for a,L,U in rows for b in range(L,U+1)];assert generated==pts
 bounds=range(-20,21);clipped=sorted((a,b) for a in bounds for b in bounds if all(A*a+B*b<=C for A,B,C in facets));assert clipped==pts
 R={a:(L,U) for a,L,U in rows};lo=min(L for _,L,U in rows);hi=max(U for _,L,U in rows);ordered=Counter()
 for u in range(min(R)-max(R),max(R)-min(R)+1):
  for v in range(lo-hi,hi-lo+1):
   if not(u or v):continue
   count=0
   for a,(L,U) in R.items():
    if a-u in R:
     l,h=R[a-u];count+=max(0,min(U,h+v)-max(L,l+v)+1)
   if count:ordered[u*u+u*v+v*v]+=count
 assert all(c%2==0 for c in ordered.values());hist={q:c//2 for q,c in sorted(ordered.items())};assert sum(hist.values())==len(pts)*(len(pts)-1)//2
 # Independent Cartesian embedding expands to four times the norm.
 direct=Counter(((2*(a-c)+b-e)**2+3*(b-e)**2)//4 for i,(a,b) in enumerate(pts) for c,e in pts[:i]);assert direct==hist
 out[name]={'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'n':len(pts),'k':len(hist),'pairs':sum(hist.values()),'rows':rows,'halfplanes':facets,'histogram':hist}
Path(__file__).with_name('evidence.json').write_text(json.dumps(out,indent=2)+'\n');print({name:(d['n'],d['k'],d['pairs']) for name,d in out.items()})
