#!/usr/bin/env python3
"""Mixed-scale closed-geodesic row programs: discrete row counts, exact windings."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,time,itertools,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'search/torus'));from search import value,target
sys.path.insert(0,str(ROOT/'certification'));from verify import verify
LOG=HERE/'row_experiments.jsonl';OUT=ROOT/'candidates/wave2_packing'
def log(r):
 with LOG.open('a') as f:f.write(json.dumps(r)+'\n')
def programs(n):
 for R in range(3,7):
  for counts in itertools.product(range(2,8),repeat=R):
   if sum(counts)!=n:continue
   rotations=[counts[k:]+counts[:k] for k in range(R)]
   rev=counts[::-1];rotations +=[rev[k:]+rev[:k] for k in range(R)]
   if counts==min(rotations):yield counts
def solve(counts,h,k,mode):
 R=len(counts);S=h*h+k*k;n=sum(counts);i,j=np.triu_indices(n,1)
 rows=np.repeat(np.arange(R),counts);frac=np.concatenate([np.arange(m)/m for m in counts])
 e=np.array([h,k]);f=np.array([-k,h])/S
 def unpack(z):
  phases=np.r_[0,z[:R-1]];normal=np.r_[0,z[R-1:2*(R-1)]]
  return (phases[rows]+frac)[:,None]*e+normal[rows,None]*f
 D=np.zeros((n,2,2*(R-1)))
 for r in range(1,R):D[rows==r,:,r-1]=e;D[rows==r,:,R-2+r]=f
 diff=D[i]-D[j]
 def con(z):
  p=unpack(z);v=p[i]-p[j];v-=np.rint(v);return np.sum(v*v,axis=1)-z[-1]
 def jac(z):
  p=unpack(z);v=p[i]-p[j];v-=np.rint(v)
  return np.column_stack((2*np.einsum('mc,mcd->md',v,diff),-np.ones(len(i))))
 # Both phases are winding-compatible: each row closes by exactly (h,k).
 phases=np.arange(R)*(0.5 if mode==0 else 1/(2*R));normal=np.arange(R)/R
 z=np.r_[phases[1:],normal[1:],0.01]
 z[-1]=value(unpack(z))
 t=time.monotonic();res=minimize(lambda z:-z[-1],z,jac=lambda z:np.r_[np.zeros(len(z)-1),-1],method='SLSQP',constraints={'type':'ineq','fun':con,'jac':jac},bounds=[(None,None)]*(2*(R-1))+[(0,1)],options={'maxiter':600,'ftol':1e-12})
 return unpack(res.x)%1,{'success':bool(res.success),'iterations':int(res.nit),'seconds':time.monotonic()-t,'d2':float(value(unpack(res.x))),'min_inequality':float(min(con(res.x))),'parameters':res.x[:-1].tolist()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=180);args=ap.parse_args()
 dirs=[(1,1),(2,1),(3,1),(3,2),(4,1),(4,3)]
 jobs=[(n,c,h,k,mode) for n in [15,14,16,17,18,19,20,21] for c in programs(n) for h,k in dirs for mode in [0,1]]
 log({'kind':'prospective','seed_base':5000,'jobs':len(jobs),'workers':1,'wall_cap_seconds':args.seconds,'method':'enumerate_mixed_uniform_closed_geodesic_rows','row_count':[3,6],'per_row_counts':[2,7],'directions':dirs,'phase_modes':['half_period_alternation','winding_ramp'],'success':'independently exact checked Markov counterexample','stop':'wall cap or full discrete enumeration; do not repeat unchanged phase starts'})
 start=time.monotonic();best={};done=0
 for index,(n,c,h,k,mode) in enumerate(jobs):
  if time.monotonic()-start>args.seconds:break
  # Within-row valid periodic copies give an exact necessary upper bound.
  if (h*h+k*k)/max(c)**2<=best.get(n,0):continue
  p,info=solve(c,h,k,mode);done+=1
  row={'kind':'row_result','seed':5000+index,'n':n,'counts':c,'direction':[h,k],'integer_loop_winding':[h,k],'mode':mode,**info}
  if info['d2']>best.get(n,0)+1e-12 and info['min_inequality']>=-1e-9:
   best[n]=info['d2'];scale=10**12
   s={'problem':'torus_distance','points':(np.rint(p*scale).astype(np.int64)%scale).tolist(),'scale':scale,'provenance':row}
   cert=verify(s);assert cert['passed'];s['bound']=cert['value'];path=OUT/f'row_best_n{n}.json';path.write_text(json.dumps(s,indent=2)+'\n');row.update(exact_certificate=cert,artifact=str(path.relative_to(ROOT)))
  log(row)
  if done%100==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'best':best,'last_n':n}),flush=True)
 log({'kind':'complete','executed_jobs':done,'all_program_count':len(jobs),'whole_seconds':time.monotonic()-start,'best':best,'scope':'within row-program subclass only; not global optimality or current record'})
if __name__=='__main__':main()
