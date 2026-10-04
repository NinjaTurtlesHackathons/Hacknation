#!/usr/bin/env python3
"""Exact support-program family generalizing the 81-point witness."""
import collections,itertools,json,pathlib,datetime,time
H=pathlib.Path(__file__).resolve().parent;OUT=H.parents[1]/'candidates'/'wave2_family'
def constraints(r):return [[-2,-1,2*r-1],[-1,-2,2*r-1],[1,-1,2*r-1],[1,0,r],[2,1,2*r-2],[1,1,r],[1,2,2*r-2],[0,1,r],[-1,1,2*r-2],[-1,0,r]]
def points(c):
 # Derive coordinate bounds from the constraints, never truncate a grid.
 return [(a,b) for a in range(-c[9][2],c[3][2]+1) for b in range((-a-c[1][2]+1)//2,c[7][2]+1) if all(x*a+y*b<=z for x,y,z in c)]
def evaluate(p):
 h=collections.Counter()
 for (a,b),(c,d) in itertools.combinations(p,2):
  x,y=a-c,b-d;h[x*x+x*y+y*y]+=1
 return h
if __name__=='__main__':
 table=json.loads((H.parents[0]/'literature'/'few_distance_k24_50.json').read_text())['bounds']
 (H/'preregister_formula_family.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'radii':list(range(2,21)),'formula':'supports r on coordinate facets; 2r-1 on three slanted facets; 2r-2 on three other slanted facets; exact source at r5','metric':'a²+ab+b²','criterion':'strictly beat consolidated source table where available; unknown k>50 not record evidence'},indent=2))
 rows=[]
 for r in range(2,21):
  tick=time.perf_counter();c=constraints(r);p=points(c);hist=evaluate(p);k=len(hist);n=len(p);baseline=table.get(str(k));row={'r':r,'n':n,'k':k,'baseline':baseline,'improved_audited_threshold':baseline is not None and n>baseline,'norm_histogram':dict(sorted(hist.items())),'runtime_seconds':time.perf_counter()-tick};rows.append(row)
  (OUT/f'formula_r{r}_k{k}_n{n}.json').write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':p,'max_distances':k,'provenance':{'method':'exact ten-facet support family','halfplanes':c,'r':r}},indent=2));print({k:row[k] for k in ['r','n','k','baseline','improved_audited_threshold','runtime_seconds']},flush=True)
 (H/'formula_family_results.json').write_text(json.dumps(rows,indent=2))
