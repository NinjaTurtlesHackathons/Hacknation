#!/usr/bin/env python3
"""Joint exact lattice-site and distance-alphabet MILP; finite-window discovery."""
import argparse,json,time,os,warnings
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
import networkx as nx
from collections import defaultdict
warnings.filterwarnings('ignore',message='Unrecognized options detected')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'candidates/wave2_joint_palette';LOG=HERE/'experiments.jsonl'
def log(row):
 row['utc']=datetime.now(timezone.utc).isoformat()
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps({k:v for k,v in row.items() if k not in ['points','palette']}),flush=True)
def norm(a,b):
 x=a[0]-b[0];y=a[1]-b[1];return x*x+x*y+y*y

def run(r,k,record,seconds,seed,shape="hex",free_origin=False):
 t=time.monotonic();limit=r if shape=='hex' else 2*r
 points=[(a,b) for a in range(-limit,limit+1) for b in range(-limit,limit+1) if (abs(a+b)<=r if shape=='hex' else a*a+a*b+b*b<=r*r)];n=len(points)
 if n<=record:
  log({'kind':'skip','r':r,'shape':shape,'k':k,'window_vertices':n,'record':record,'reason':'window cardinality cannot exceed known construction'});return
 pairs=[(i,j,norm(points[i],points[j])) for i in range(n) for j in range(i)];qs=sorted(set(q for i,j,q in pairs));idx={q:n+z for z,q in enumerate(qs)};nv=n+len(qs)
 graphs=defaultdict(nx.Graph)
 for i,j,q in pairs:graphs[q].add_edge(i,j)
 matches={q:list(nx.max_weight_matching(g,maxcardinality=True)) for q,g in graphs.items()}
 for q,edges in matches.items():
  assert len({v for edge in edges for v in edge})==2*len(edges)
  assert all(norm(points[i],points[j])==q for i,j in edges)
 alpha={q:n-len(matches[q]) for q in qs}
 if shape=='disk' and r==7:
  covers=json.loads((HERE/'disk7_cover_certificate.json').read_text());assert covers['vertices']==[list(p) for p in points]
  for q in qs:
   cert=covers['classes'][str(q)];flat=[v for b in cert['triangles']+cert['edges'] for v in b];assert len(flat)==len(set(flat));assert all(norm(points[i],points[j])==q for a,b,c in cert['triangles'] for i,j in [(a,b),(a,c),(b,c)]);assert all(norm(points[a],points[b])==q for a,b in cert['edges']);assert cert['alpha_upper']==n-2*len(cert['triangles'])-len(cert['edges'])
   alpha[q]=min(alpha[q],cert['alpha_upper'])
 mandatory=[q for q in qs if record+1>alpha[q]]
 if len(mandatory)>k:
  log({'kind':'matching_window_exclusion','r':r,'shape':shape,'k':k,'record':record,'mandatory_classes':len(mandatory),'palette':mandatory,'reason':'disjoint distance edges imply independent-set cardinality <= n-matching; target forces too many norms','scope':'finite window only; no optimizer certificate'});return

 rr=[];cc=[];vv=[]
 for z,(i,j,q) in enumerate(pairs):rr.extend([z,z,z]);cc.extend([i,j,idx[q]]);vv.extend([1,1,-1])
 m=len(pairs);rr.extend([m]*len(qs));cc.extend(range(n,nv));vv.extend([1]*len(qs))
 rr.extend([m+1]*n);cc.extend(range(n));vv.extend([1]*n)
 for z,q in enumerate(qs):
  rr.extend([m+2+z]*n);cc.extend(range(n));vv.extend([1]*n)
  rr.append(m+2+z);cc.append(idx[q]);vv.append(-(n-alpha[q]))
 A=coo_matrix((vv,(rr,cc)),shape=(m+2+len(qs),nv)).tocsc();upper=np.r_[np.ones(m),k,np.inf,[alpha[q] for q in qs]];lower=np.r_[np.full(m,-np.inf),-np.inf,record+1,np.full(len(qs),-np.inf)]
 low=np.zeros(nv);high=np.ones(nv);
 if not free_origin:low[points.index((0,0))]=1
 for q in mandatory:low[idx[q]]=1
 objective=np.r_[-np.ones(n),np.zeros(len(qs))]
 log({'kind':'prospective_instance','r':r,'shape':shape,'k':k,'record':record,'success_cardinality':record+1,'seed':seed,'threads':1,'time_limit_seconds':seconds,'vertices':n,'norm_classes':len(qs),'largest_norm':max(qs),'constraints':m+2+len(qs),'mandatory_norms':mandatory,'matching_cuts':True,'restriction':('origin free' if free_origin else 'origin selected')+'; finite complete '+shape+' window; no symmetry assumed','method':'joint vertices+distance palette binary MILP, lower cardinality target, maximize cardinality'})
 result=milp(objective,integrality=np.ones(nv),bounds=Bounds(low,high),constraints=LinearConstraint(A,lower,upper),options={'time_limit':seconds,'threads':1,'random_seed':seed,'mip_rel_gap':0.0,'presolve':True})
 elapsed=time.monotonic()-t;row={'kind':'result','r':r,'shape':shape,'k':k,'record':record,'elapsed_seconds':elapsed,'status':int(result.status),'message':result.message,'mip_nodes':int(getattr(result,'mip_node_count',0) or 0),'mip_gap':float(getattr(result,'mip_gap',float('nan')) or 0),'dual_bound':float(getattr(result,'mip_dual_bound',float('nan')) or 0)}
 if result.x is not None:
  chosen=[points[i] for i,v in enumerate(result.x[:n]) if v>.5];actual=sorted({norm(a,b) for i,a in enumerate(chosen) for b in chosen[:i]});assert len(actual)<=k and len(chosen)>record and len(set(chosen))==len(chosen)
  path=OUT/f'k{k}_n{len(chosen)}_{shape}_r{r}_seed{seed}.json';path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':chosen,'max_distances':k,'provenance':{'method':'joint palette MILP','r':r,'shape':shape,'seed':seed,'comparison_lower_bound':record,'certification':'exact construction validation by discovery code only; independent certification pending'}},indent=2)+'\n');row.update(cardinality=len(chosen),distance_classes=len(actual),palette=actual,artifact=str(path.relative_to(ROOT)),success=True)
 else:row.update(success=False,interpretation='no better witness within allotted finite search; no unrestricted upper bound')
 log(row)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=180);p.add_argument('--seed',type=int,default=42000);p.add_argument('--targets',default='24,25,31,34,37,40,43,47,48,49,50');p.add_argument('--radius',type=int);p.add_argument('--shape',choices=['hex','disk'],default='hex');p.add_argument('--free-origin',action='store_true');a=p.parse_args();bounds=json.loads((HERE.parent/'few_distance_k24_50.json').read_text())['bounds']
 for z,k in enumerate(map(int,a.targets.split(','))):
  record=bounds[str(k)];r=a.radius or next(r for r in [4,5,6,7] if 1+3*r*(r+1)>record)
  run(r,k,record,a.seconds,a.seed+z,a.shape,a.free_origin)
