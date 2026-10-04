#!/usr/bin/env python3
"""Adaptive representation: independently sliding shell contacts, triangular bulk."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,time,argparse,math
import numpy as np
from scipy.optimize import minimize
from octagon import HERE,BENCH,C,POLY,NORMALS,bulk_cells,actual_radius,free,certify
LOG=HERE/'facet_experiments.jsonl'
def record(r):
 with LOG.open('a') as f:f.write(json.dumps(r)+'\n')
def solve(n,m,clock,turn,pattern):
 cells=bulk_cells(n-m,pattern);u=(np.arange(m)/m+clock/m)%1*8;faces=np.floor(u).astype(int);fractions=u-faces;edges=POLY[(faces+1)%8]-POLY[faces]
 i,j=np.triu_indices(n,1)
 def geom(z):
  r,theta,x,y=z[:4];rot=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]]);bulk=cells@rot.T;base=POLY[faces]+z[4:,None]*edges
  p=np.vstack(((1-r)*base,2*r*bulk+[x,y]));D=np.zeros((n,2,len(z)));D[:m,:,0]=-base;D[m:,:,0]=2*bulk;D[m:,:,1]=2*r*np.column_stack((-bulk[:,1],bulk[:,0]));D[m:,0,2]=1;D[m:,1,3]=1
  for k in range(m):D[k,:,4+k]=(1-r)*edges[k]
  return p,D
 def con(z):
  p,_=geom(z);return np.r_[np.sum((p[i]-p[j])**2,axis=1)-4*z[0]**2,(1-z[0]-p@NORMALS.T).ravel()]
 def jac(z):
  p,D=geom(z);J=2*np.einsum('mc,mcd->md',p[i]-p[j],D[i]-D[j]);J[:,0]-=8*z[0];W=-np.einsum('ak,nkd->nad',NORMALS,D).reshape(8*n,len(z));W[:,0]-=1;return np.vstack((J,W))
 z=np.r_[float(BENCH[n])/C,turn*np.pi/48,0,0,fractions];t=time.monotonic()
 res=minimize(lambda z:-z[0],z,jac=lambda z:np.r_[-1,np.zeros(len(z)-1)],constraints={'type':'ineq','fun':con,'jac':jac},method='SLSQP',bounds=[(.02,.3),(-np.pi/12,np.pi/2),(-.3,.3),(-.3,.3)]+[(0,1)]*m,options={'maxiter':350,'ftol':1e-11})
 p,_=geom(res.x);return p,actual_radius(p),{'success':bool(res.success),'iterations':int(res.nit),'seconds':time.monotonic()-t,'faces':faces.tolist(),'parameters':res.x.tolist(),'min_constraint':float(con(res.x).min())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=240);args=ap.parse_args()
 # Interleave promising shell counts13,14,15 and every N before changing rotation.
 jobs=[(n,m,clock,turn,pattern) for pattern in range(4) for clock in (0,.25,.5,.75) for turn in (0,4,2,6,1,5,3,7) for n in range(28,34) for m in (13,14,15)]
 record({'kind':'prospective','seed_base':90000,'count':len(jobs),'seconds_cap':args.seconds,'workers':1,'representation_change':'replace equally spaced boundary shell with13to15 independent facet sliders, keep triangular bulk contact graph until final release','stop':'100 stagnant programs; no repetition','motivation':'perimeter bound disfavors17to18 boundary contacts, while13to15 may beat every target'})
 start=time.monotonic();stale=0;best={n:actual_radius(np.loadtxt(HERE/f'source/coc{n}.txt')[:,1:]/C) for n in range(28,34)};done=0
 for index,(n,m,clock,turn,pattern) in enumerate(jobs):
  if time.monotonic()-start>args.seconds:break
  job=time.monotonic();p,r,mi=solve(n,m,clock,turn,pattern);q,rr,fi=free(p,r);row={'kind':'result','seed':90000+index,'n':n,'shell_count':m,'clock':clock,'turn':turn,'bulk_cut_pattern':pattern,'motif':mi,'free':fi,'radius_original':rr*C,'whole_seconds':time.monotonic()-job}
  improved=rr>best[n]+1e-10
  if improved:
   cert,path=certify(q,rr,f'facet_best_n{n}',row)
   if cert:best[n]=rr;row.update(exact_certificate=cert,artifact=path)
  stale=0 if improved else stale+1;done+=1;record(row)
  if done%20==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'stale':stale,'best_original':{n:best[n]*C for n in best}}),flush=True)
  if stale>=100:record({'kind':'stop','reason':'100 stagnant facet-slider programs'});break
 record({'kind':'complete','jobs':done,'whole_seconds':time.monotonic()-start,'best_original':{n:best[n]*C for n in best}})
if __name__=='__main__':main()
