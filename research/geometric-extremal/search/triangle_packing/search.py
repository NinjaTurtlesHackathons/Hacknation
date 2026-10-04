#!/usr/bin/env python3
"""One-worker right-isosceles-triangle packing, exact rational output."""
import os,sys,json,time,re,hashlib
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.optimize import minimize
HERE=Path(__file__).parent;ROOT=HERE.parents[1];OUT=ROOT/'candidates/triangle_packing';LOG=HERE/'experiments.jsonl'
SQ=np.sqrt(2)
def record(x):
 with LOG.open('a') as f:f.write(json.dumps(x)+'\n')
def read(n):
 rows=[l.split() for l in (HERE/f'source/crt{n}.txt').read_text().splitlines() if l.strip()]
 return [[r[1],r[2]] for r in rows]
def radius(p):
 i,j=np.triu_indices(len(p),1)
 return min(np.min(p),np.min(1-p.sum(axis=1))/SQ,np.min(np.linalg.norm(p[i]-p[j],axis=1))/2)
def exact_check(points,r):
 p=[[Q(v) for v in xy] for xy in points];r=Q(r)
 if r<=0:return False
 if any(x<r or y<r or 1-x-y<0 or (1-x-y)**2<2*r*r for x,y in p):return False
 return all((p[i][0]-p[j][0])**2+(p[i][1]-p[j][1])**2>=4*r*r for i in range(len(p)) for j in range(i))
def save(p,name,meta):
 z=10**13;points=[[str(Q(int(v),z)) for v in row] for row in np.rint(p*z).astype(np.int64)]
 r=Q(max(0,int(radius(np.array([[float(Q(v)) for v in row] for row in points]))*z)-2),z)
 if not exact_check(points,r):raise RuntimeError('Exact output failed internal checker')
 s={'problem':'circle_packing_triangle','points':points,'radius':str(r),'provenance':meta};path=OUT/(name+'.json');path.write_text(json.dumps(s,indent=2)+'\n');return s,str(path.relative_to(ROOT))
def optimize(p):
 n=len(p);i,j=np.triu_indices(n,1);m=len(i)
 def con(z):
  p=z[:-1].reshape(n,2);r=z[-1];v=p[i]-p[j]
  return np.r_[np.sum(v*v,axis=1)-4*r*r,p[:,0]-r,p[:,1]-r,1-p.sum(axis=1)-SQ*r]
 def jac(z):
  p=z[:-1].reshape(n,2);r=z[-1];v=p[i]-p[j];J=np.zeros((m+3*n,2*n+1));J[:m,-1]=-8*r
  for c in range(2):J[np.arange(m),2*i+c]=2*v[:,c];J[np.arange(m),2*j+c]=-2*v[:,c]
  for k in range(n):
   J[m+k,2*k]=1;J[m+n+k,2*k+1]=1;J[m+2*n+k,2*k:2*k+2]=-1
  J[m:m+2*n,-1]=-1;J[m+2*n:,-1]=-SQ
  return J
 z=np.r_[p.ravel(),max(.001,radius(p))]
 t=time.monotonic();res=minimize(lambda z:-z[-1],z,jac=lambda z:np.r_[np.zeros(len(z)-1),-1],method='SLSQP',constraints={'type':'ineq','fun':con,'jac':jac},bounds=[(0,1)]*(2*n)+[(.001,.3)],options={'ftol':1e-13,'maxiter':500})
 p=res.x[:-1].reshape(n,2)
 return p,{'optimizer_success':bool(res.success),'iterations':int(res.nit),'elapsed_seconds':time.monotonic()-t,'optimizer_radius':float(res.x[-1]),'actual_radius':float(radius(p))}
def hole(p,rng):
 grid=rng.random((6000,2));grid[:,1]*=1-grid[:,0]
 clear=np.minimum(np.min(grid,axis=1),(1-grid.sum(axis=1))/SQ)
 clear=np.minimum(clear,np.min(np.linalg.norm(grid[:,None,:]-p[None,:,:],axis=2),axis=1)/2)
 return grid[np.argmax(clear)]
def main():
 OUT.mkdir(parents=True,exist_ok=True);baselines={n:np.array(read(n),float) for n in [22,23,24]}
 for n,p in baselines.items():
  raw=read(n);r=Q(raw[0][0])-Q(1,10**27)
  # n22/24 first x equals printed table radius, as does n23.
  assert exact_check(raw,r)
  s={'problem':'circle_packing_triangle','points':raw,'radius':str(r),'provenance':{'source':f'https://packomania.com/crt/txt/crt{n}.txt','retrieved':'2026-10-04','normalization':'triangle x>=0,y>=0,x+y<=1; legs1','radius_shrink':'1/10^27','source_sha256':hashlib.sha256((HERE/f'source/crt{n}.txt').read_bytes()).hexdigest()}}
  path=OUT/f'baseline_n{n}.json';path.write_text(json.dumps(s,indent=2)+'\n');record({'kind':'baseline','n':n,'radius':str(r),'internal_exact_pass':True,'artifact':str(path.relative_to(ROOT))})
 record({'kind':'prospective_batch','seeds':[1000,1019],'n':[22,23,24],'methods':['contact_pair_rotation','boundary_cluster_hole_surgery','adjacent_count_transfer'],'workers':1,'stop':'20seeds perN stagnation','success':'rational feasible radius exceeds same-assumption fresh published comparator'})
 best={n:radius(p) for n,p in baselines.items()}
 for seed in range(1000,1020):
  for n in [22,23,24]:
   rng=np.random.default_rng(seed*100+n);p=baselines[n].copy();method=seed%3
   if method==0:
    i,j=np.triu_indices(n,1);dist=np.linalg.norm(p[i]-p[j],axis=1);choices=np.argsort(dist)[:3*n];edge=choices[seed%len(choices)];a,b=i[edge],j[edge];mid=(p[a]+p[b])/2;v=p[a]-mid;angle=rng.choice([np.pi/3,np.pi/2]);rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);p[a]=mid+rot@v;p[b]=mid-rot@v;name='contact_pair_rotation'
   elif method==1:
    boundary=np.minimum(np.min(p,axis=1),(1-p.sum(axis=1))/SQ);inds=np.argsort(boundary)[:n//2];deleted=rng.choice(inds,3,replace=False);p=np.delete(p,deleted,axis=0);p,_=optimize(p)
    for _ in range(3):p=np.vstack((p,hole(p,rng)));p,_=optimize(p)
    name='boundary_cluster_hole_surgery'
   else:
    if n<24:p=np.delete(baselines[n+1],seed%(n+1),axis=0)
    else:p=np.vstack((baselines[23],hole(baselines[23],rng)))
    name='adjacent_count_transfer'
   p,info=optimize(p);v=radius(p);row={'kind':'experiment','n':n,'seed':seed,'method':name,**info,'baseline_radius':float(radius(baselines[n]))}
   if v>best[n]+1e-12:
    s,path=save(p,f'best_n{n}',row);best[n]=v;row.update(artifact=path,exact_radius=s['radius'],internal_exact_pass=True)
   record(row);print(json.dumps({'n':n,'seed':seed,'r':float(v),'best':float(best[n])}),flush=True)
if __name__=='__main__':main()
