#!/usr/bin/env python3
"""One-worker topology/defect search; all accepted witnesses independently exact checked."""
import argparse,json,time,sys,os
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'certification'))
from verify import verify
OUT=ROOT/'candidates/torus'; LOG=Path(__file__).parent/'experiments.jsonl'
def lattice(n,a,b): return np.array([[(b*k%n)/n,(a*k%n)/n] for k in range(n)])
def value(p):
 i,j=np.triu_indices(len(p),1); v=p[i]-p[j]; v-=np.rint(v)
 return np.min(np.sum(v*v,axis=1))
def target(n): return 2/(np.sqrt(3)*n)-8/(25*n*n)
def record(row):
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
def save(p,name,meta):
 z=10**12; ints=np.rint((p%1)*z).astype(np.int64)%z
 s={'problem':'torus_distance','points':ints.tolist(),'scale':z,'provenance':meta}
 r=verify(s); s['bound']=r['value']; path=OUT/(name+'.json');path.write_text(json.dumps(s,indent=2)+'\n')
 return r,str(path.relative_to(ROOT))
def optimize(p,maxiter=400):
 n=len(p);i,j=np.triu_indices(n,1);m=len(i)
 # Fix translation with first centre at origin; nearest periodic shifts updated dynamically.
 p=(p-p[0])%1
 def unpack(z):return np.vstack((np.zeros(2),z[:-1].reshape(n-1,2)))
 def con(z):
  q=unpack(z);v=q[i]-q[j];v-=np.rint(v)
  return np.sum(v*v,axis=1)-z[-1]
 def jac(z):
  q=unpack(z);v=q[i]-q[j];v-=np.rint(v);J=np.zeros((m,2*(n-1)+1));J[:,-1]=-1
  for coord in range(2):
   good=i>0;J[np.arange(m)[good],2*(i[good]-1)+coord]=2*v[good,coord]
   good=j>0;J[np.arange(m)[good],2*(j[good]-1)+coord]=-2*v[good,coord]
  return J
 z=np.r_[p[1:].ravel(),value(p)]
 res=minimize(lambda x:-x[-1],z,jac=lambda x:np.r_[np.zeros(len(x)-1),-1],method='SLSQP',bounds=[(None,None)]*(len(z)-1)+[(0,1)],constraints={'type':'ineq','fun':con,'jac':jac},options={'maxiter':maxiter,'ftol':1e-12})
 q=unpack(res.x)%1
 return q,{'optimizer_success':bool(res.success),'iterations':int(res.nit),'message':res.message,'objective':float(res.x[-1]),'actual':float(value(q))}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=90);args=ap.parse_args()
 OUT.mkdir(exist_ok=True,parents=True)
 p15=lattice(15,4,1)
 for n,a,b in [(15,4,1),(209,15,4)]:
  s={'problem':'torus_distance','points':[[(b*k)%n,(a*k)%n] for k in range(n)],'scale':n,'provenance':{'known_lattice':[a,b]}}
  r=verify(s);s['bound']=r['value'];p=OUT/f'baseline_n{n}.json';p.write_text(json.dumps(s,indent=2)+'\n')
  record({'kind':'baseline','n':n,'certificate':r,'artifact':str(p.relative_to(ROOT))})
 # Prospective preregistration is written before first optimization.
 record({'kind':'prospective_batch','seeds':[1000,1019],'methods':['single_disk_deletion','low_fourier_symmetry_release','farthest_hole_insertion'],'seconds':args.seconds,'workers':1,'claim':'M>25/4 iff d2>2/(sqrt3*N)-8/(25*N*N)'})
 start=time.monotonic();best={}
 for seed in range(1000,1020):
  for n in [14,15,16]:
   if time.monotonic()-start>args.seconds:return
   rng=np.random.default_rng(seed*100+n)
   if n==14:p=np.delete(p15,seed%15,axis=0);method='single_disk_deletion'
   elif n==15:
    p=p15.copy();freq=1+seed%6;amp=[.015,.05,.1,.2][seed%4]
    phase=2*np.pi*np.arange(15)*freq/15
    p+=amp*np.column_stack((np.sin(phase+rng.uniform(0,6)),np.cos(phase+rng.uniform(0,6))));method='low_fourier_symmetry_release'
   else:
    p=p15.copy();grid=rng.random((1000,2));v=grid[:,None,:]-p[None,:,:];v-=np.rint(v)
    hole=grid[np.argmax(np.min(np.sum(v*v,axis=2),axis=1))];p=np.vstack((p,hole));method='farthest_hole_insertion'
   p+=(rng.random(p.shape)-.5)*(.03 if n!=15 else .005)
   t=time.monotonic();q,info=optimize(p);v=value(q)
   row={'kind':'experiment','seed':seed,'n':n,'method':method,'elapsed_seconds':time.monotonic()-t,'starting_d2':float(value(p)),'target_d2':float(target(n)),**info}
   if v>best.get(n,0):
    best[n]=v;r,path=save(q,f'best_n{n}',row);row.update(certificate=r,artifact=path)
   record(row)
   print(json.dumps({'n':n,'seed':seed,'d2':float(v),'target':float(target(n)),'best':best[n]}),flush=True)
if __name__=='__main__':main()
