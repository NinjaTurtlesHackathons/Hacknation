#!/usr/bin/env python3
"""Exact filled lattice nine-gons: six diagonal edges + three distinguished t-edges."""
import pathlib,itertools,collections,json,time,datetime,hashlib
H=pathlib.Path(__file__).resolve().parent;OUT=H.parents[1]/'candidates'/'wave2_family'
def vertices(s,t):
 edges=[(s,-2*s),(2*s,-s),(t,0),(s,s),(-s,2*s),(-t,t),(-2*s,s),(-s,-s),(0,-t)]
 v=[(0,0)]
 for a,b in edges:v.append((v[-1][0]+a,v[-1][1]+b))
 assert v[-1]==v[0]
 return v[:-1]
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def points(v):
 return [(a,b) for a in range(min(p[0] for p in v),max(p[0] for p in v)+1) for b in range(min(p[1] for p in v),max(p[1] for p in v)+1) if all(cross(x,y,(a,b))>=0 for x,y in zip(v,v[1:]+v[:1]))]
def hist(p):
 h=collections.Counter()
 for (a,b),(c,d) in itertools.combinations(p,2):x,y=a-c,b-d;h[x*x+x*y+y*y]+=1
 return h
if __name__=='__main__':
 table=json.loads((H.parent/'literature'/'few_distance_k24_50.json').read_text())['bounds'];params=list(itertools.product(range(1,9),range(0,9)))
 (H/'preregister_ninegon.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parameters':params,'hypothesis':'D3 nine-gon edge lengths infer111point witness and extend strict bounds','point_formula':'9s²+6st+t(t+3)/2+3s+1','doubled_coordinate_area':'18s²+12st+t²','boundary_sites':'6s+3t','distance_evaluation':'exact complete integer pair norms','code_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'workers':1,'literature_thresholds_above50':'unavailable; no record claim'},indent=2))
 rows=[]
 for s,t in params:
  tick=time.perf_counter();v=vertices(s,t);p=points(v);h=hist(p);k=len(h);n=len(p);n_formula=9*s*s+6*s*t+t*(t+3)//2+3*s+1
  area2=sum(a*d-b*c for (a,b),(c,d) in zip(v,v[1:]+v[:1]));assert area2==18*s*s+12*s*t+t*t;assert n==n_formula
  old=table.get(str(k));row={'s':s,'t':t,'n':n,'k':k,'baseline':old,'strict_audited_improvement':old is not None and n>old,'norm_histogram':dict(sorted(h.items())),'runtime_seconds':time.perf_counter()-tick};rows.append(row)
  path=OUT/f'ninegon_s{s}_t{t}_k{k}_n{n}.json';path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':p,'max_distances':k,'provenance':{'method':'filled integer nine-gon edge program','s':s,'t':t,'vertices':v,'point_formula':n_formula}},indent=2));print({q:row[q] for q in ['s','t','n','k','baseline','strict_audited_improvement','runtime_seconds']},flush=True)
  if (s,t)==(3,1):
   source=json.loads((H.parents[1]/'candidates'/'wave2_family'/'support_k41_n111_code7324998.json').read_text())['points'];assert set(p)=={(a+6,b-2) for a,b in source}
 (H/'ninegon_results.json').write_text(json.dumps(rows,indent=2))
