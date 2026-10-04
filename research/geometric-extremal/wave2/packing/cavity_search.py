#!/usr/bin/env python3
"""Nonlocal periodic Delaunay cavity reconstruction, one compute worker."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,time,argparse
from pathlib import Path
import numpy as np
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'search/torus'))
from search import value,optimize,target
sys.path.insert(0,str(ROOT/'certification'))
from verify import verify
HERE=Path(__file__).parent;OUT=ROOT/'candidates/wave2_packing';LOG=HERE/'experiments.jsonl'
def log(r):
 with LOG.open('a') as f:f.write(json.dumps(r)+'\n')
def cyclic(n):
 best=(-1,None,None)
 for a in range(1,n):
  p=np.array([[(k%n)/n,(a*k%n)/n] for k in range(n)])
  v=value(p)
  if v>best[0]:best=(v,p,a)
 return best
def mesh(p):
 shifts=np.array([(x,y) for x in (-1,0,1) for y in (-1,0,1)])
 cloud=(p[None,:,:]+shifts[:,None,:]).reshape(-1,2)
 tri=Delaunay(cloud)
 return cloud,tri
def holes(p,count=6):
 cloud,tri=mesh(p);ts=cloud[tri.simplices]
 a=2*(ts[:,1]-ts[:,0]);b=2*(ts[:,2]-ts[:,0])
 rhs=np.column_stack((np.sum(ts[:,1]**2-ts[:,0]**2,axis=1),np.sum(ts[:,2]**2-ts[:,0]**2,axis=1)))
 A=np.stack((a,b),axis=1);good=abs(np.linalg.det(A))>1e-12
 centers=np.linalg.solve(A[good],rhs[good,:,None])[...,0]
 centers=centers[np.all((centers>=0)&(centers<1),axis=1)]
 if len(centers)==0:raise RuntimeError('no periodic Voronoi vertices')
 centers=np.unique(np.round(centers,12),axis=0)
 v=centers[:,None,:]-p[None,:,:];v-=np.rint(v)
 d=np.min(np.sum(v*v,axis=2),axis=1)
 return [(centers[k],float(d[k])) for k in np.argsort(-d)[:count]]
def topology(p):
 cloud,tri=mesh(p);n=len(p);edges=set();wind=[]
 for simplex in tri.simplices:
  ts=cloud[simplex];centroid=ts.mean(axis=0)
  if not np.all((centroid>=0)&(centroid<1)):continue
  labels=[int(k%n) for k in simplex]
  lifts=[np.rint(cloud[k]-p[k%n]).astype(int) for k in simplex]
  sums=np.zeros(2,dtype=int)
  for h in range(3):
   a,b=labels[h],labels[(h+1)%3];shift=lifts[(h+1)%3]-lifts[h];sums+=shift
   if a<b:edges.add((a,b,int(shift[0]),int(shift[1])))
   else:edges.add((b,a,int(-shift[0]),int(-shift[1])))
  assert np.all(sums==0)
  wind.append({'labels':labels,'shift_sum':sums.tolist()})
 deg=[0]*n
 for a,b,_,_ in edges:deg[a]+=1;deg[b]+=1
 return {'degree_histogram':{str(k):deg.count(k) for k in sorted(set(deg))},'edges':[list(e) for e in sorted(edges)],'triangles_winding':wind}
def cavity(p,seed,k,beam_width):
 rng=np.random.default_rng(seed);n=len(p);anchor=seed%n
 v=p-p[anchor];v-=np.rint(v)
 # Alternate a round cavity and an oriented elongated seam: coherent removal,
 # never independent point jitter. Orientation is a discrete program parameter.
 if seed%2:
  angle=(seed%7)*np.pi/7;u=np.array([np.cos(angle),np.sin(angle)])
  t=v@u;w=v@np.array([-u[1],u[0]]);dist=t*t/2+2*w*w
 else:dist=np.sum(v*v,axis=1)
 removed=np.argsort(dist)[:k];base=np.delete(p,removed,axis=0)
 beams=[(base,[])]
 for depth in range(k):
  options=[]
  for q,path in beams:
   hs=holes(q,6)
   for rank,(h,d) in enumerate(hs):
    z=np.vstack((q,h));score=value(z)
    # Beam selection by actual current minimum distance, with tiny seeded
    # tie-breaking only in discrete programs; coordinates remain Voronoi vertices.
    options.append((score+rng.uniform(0,1e-10),z,path+[{'hole_rank':rank,'empty_radius_d2':d,'point':h.tolist()}]))
  options.sort(key=lambda z:z[0],reverse=True)
  beams=[(z,path) for _,z,path in options[:beam_width]]
 return [(q,{'removed_labels':removed.tolist(),'insertions':path,'cavity':'elongated_seam' if seed%2 else 'round'}) for q,path in beams]
def save(p,n,meta):
 scale=10**12;points=(np.rint((p%1)*scale).astype(np.int64)%scale).tolist()
 s={'problem':'torus_distance','points':points,'scale':scale,'provenance':meta};r=verify(s)
 assert r['passed'];s['bound']=r['value'];path=OUT/f'best_n{n}.json';path.write_text(json.dumps(s,indent=2)+'\n')
 return r,str(path.relative_to(ROOT))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=240);args=ap.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 log({'kind':'prospective','seed_range':[4000,4999],'seconds_cap':args.seconds,'workers':1,'Ns':[14,15,16,17,18,19,20,21], 'method':'periodic_Delaunay_5_to_7_point_cavity_beam_reconstruction_then_all_pair_relaxation','stages':'first 120 jobs broad; subsequent jobs adapt N to best threshold ratio and increase cavity size/beam width','success':'exact Markov counterexample; gains over cyclic subgroup only not asserted current records','stop':'wall cap or 1000 jobs; no unchanged extension; periodic triangulation degree/winding logged'})
 start=time.monotonic();states={};best={};initial={};done=0;stagnant=0
 for n in range(14,22):
  v,p,a=cyclic(n);q,inf=optimize(p,maxiter=500)
  states[n]=q;best[n]=float(value(q));initial[n]=best[n]
  log({'kind':'initial_baseline','n':n,'cyclic_slope':a,'cyclic_d2':float(v),'polished_d2':best[n],'target':float(target(n)),'comparison_scope':'reproduced cyclic subgroup plus numerical relaxation; not a published optimum','topology':topology(q)})
  save(q,n,{'kind':'initial search baseline','n':n,'cyclic_slope':a})
 for seed in range(4000,5000):
  if time.monotonic()-start>=args.seconds:break
  if done<120:n=14+done%8;k=5+done//8%3;beam=2
  else:
   ranked=sorted(best,key=lambda x:best[x]/target(x),reverse=True)
   n=ranked[(done-120)%3];k=7;beam=4
  job=time.monotonic();programs=cavity(states[n],seed,k,beam);results=[];improved=False
  for p,program in programs:
   before=topology(p);q,inf=optimize(p,maxiter=700);d=float(value(q))
   result={'program':program,'starting_d2':float(value(p)),'starting_topology':before,'optimizer':inf,'d2':d,'final_topology':topology(q)}
   if d>best[n]+1e-11:
    best[n]=d;states[n]=q;improved=True;r,path=save(q,n,{'seed':seed,'n':n,'program':program,'method':'Delaunay cavity beam reconstruction'});result.update(exact_certificate=r,artifact=path)
   results.append(result)
  done+=1;stagnant=0 if improved else stagnant+1
  log({'kind':'cavity_result','seed':seed,'n':n,'removed_count':k,'beam_width':beam,'whole_seconds':time.monotonic()-job,'results':results,'best':best[n],'initial_baseline':initial[n],'improved_search_baseline':improved,'stagnant_jobs':stagnant})
  if done%20==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'best':best,'stagnant':stagnant}),flush=True)
  # A systematic stage-2 blockade ends this representation, without repeating it.
  if done>=180 and stagnant>=80:
   log({'kind':'systemic_blockade','jobs':done,'decision':'stop: graph-changing Voronoi cavity reinsertion failed; do not extend equivalent seeds','best':best});break
 log({'kind':'complete','jobs':done,'whole_campaign_seconds':time.monotonic()-start,'best':best,'initial':initial,'gains':{n:best[n]-initial[n] for n in best}})
if __name__=='__main__':main()
