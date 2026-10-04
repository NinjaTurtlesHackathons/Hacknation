#!/usr/bin/env python3
"""Neighbor-count reconstruction via4->5,5->6,6->7 contact-ring replacement."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,time,argparse,math
import numpy as np
from scipy.optimize import minimize
from octagon import HERE,BENCH,C,actual_radius,free,certify,constraints
LOG=HERE/'ring_experiments.jsonl'
def record(r):
 with LOG.open('a') as f:f.write(json.dumps(r)+'\n')
def ring_program(p,k,anchor,phase):
 removed=np.argsort(np.sum((p-anchor)**2,axis=1))[:k];rest=np.delete(p,removed,axis=0);center=p[removed].mean(axis=0);m=k+1
 def build(z):
  rho,x,y,theta=z;angle=theta+np.arange(m)*2*np.pi/m;ring=(rho/math.sin(np.pi/m))*np.column_stack((np.cos(angle),np.sin(angle)))+[x,y]
  return np.vstack((rest,ring))
 r=actual_radius(p);z=np.r_[.95*r,center,phase*np.pi/m];t=time.monotonic()
 res=minimize(lambda z:-z[0],z,method='SLSQP',constraints={'type':'ineq','fun':lambda z:constraints(build(z),z[0])},bounds=[(.02,.3),(-.8,.8),(-.8,.8),(-4*np.pi,4*np.pi)],options={'maxiter':250,'ftol':1e-11})
 q=build(res.x);return q,actual_radius(q),{'removed_labels':removed.tolist(),'inserted_ring_count':m,'ring_radius_multiplier':1/math.sin(np.pi/m),'center_start':center.tolist(),'parameters':res.x.tolist(),'success':bool(res.success),'iterations':int(res.nit),'min_constraint':float(constraints(q,res.x[0]).min()),'seconds':time.monotonic()-t}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=240);args=ap.parse_args();anchors=np.array([(x,y) for x in (-.5,0,.5) for y in (-.5,0,.5)])
 jobs=[(n,k,ai,phase) for phase in range(3) for ai in range(9) for n in range(29,34) for k in (4,5,6)]
 record({'kind':'prospective','seed_base':100000,'program_count':len(jobs),'workers':1,'seconds_cap':args.seconds,'methods':'replace k source neighbors by regular k+1 contact ring; four-variable constrained ring fit then all-pair release','N_targets':[29,33],'source_N':'target minus1','ring_changes':[[4,5],[5,6],[6,7]],'stop':'100 stagnating after initial135 programs covering all9 anchors/everyN/everyring size, or wall cap','success':'exact relative improvement>=1e-4 over current comparison'})
 sources={n:np.loadtxt(HERE/f'source/coc{n}.txt')[:,1:]/C for n in range(28,34)};best={n:actual_radius(sources[n]) for n in range(29,34)};family_best={};stale=0;done=0;start=time.monotonic()
 for index,(n,k,ai,phase) in enumerate(jobs):
  if time.monotonic()-start>args.seconds:break
  job=time.monotonic();p,r,mi=ring_program(sources[n-1],k,anchors[ai],phase);q,rr,fi=free(p,r);row={'kind':'result','seed':100000+index,'n':n,'source_N':n-1,'removed_count':k,'anchor':anchors[ai].tolist(),'phase_start':phase,'ring_fit':mi,'free':fi,'radius_original':rr*C,'whole_seconds':time.monotonic()-job}
  improved=rr>best[n]+1e-10
  if rr>family_best.get(n,0)+1e-10:
   cert,path=certify(q,rr,f'ring_family_best_n{n}',row)
   if cert:family_best[n]=rr;row.update(exact_certificate=cert,artifact=path)
  if improved:best[n]=rr
  stale=0 if improved else stale+1;done+=1;record(row)
  if done%20==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'best_original':{n:best[n]*C for n in best},'stale':stale}),flush=True)
  if stale>=100 and done>=135:record({'kind':'stop','reason':'initial135 diverse ring programs complete without progress; no unchanged extension'});break
 record({'kind':'complete','jobs':done,'whole_seconds':time.monotonic()-start,'best_original':{n:best[n]*C for n in best},'best_ring_family_original':{n:v*C for n,v in family_best.items()}})
if __name__=='__main__':main()
