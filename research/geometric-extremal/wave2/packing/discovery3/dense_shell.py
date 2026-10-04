#!/usr/bin/env python3
"""Adaptive shell-topology pivot:16–18 shell sites, fewer bulk lattice sites."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import itertools,json,time,argparse
import numpy as np
from octagon import HERE,OUT,BENCH,C,actual_radius,motif,free,certify
LOG=HERE/'dense_shell_experiments.jsonl'
def record(r):
 with LOG.open('a') as f:f.write(json.dumps(r)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=180);args=ap.parse_args()
 # Row counts are interleaved here. The preceding family only executed m12;
 # this branch changes shell cardinality and interior contact patch topology.
 jobs=[(n,m,phase,turn,pattern) for pattern in range(4) for phase in (0,.25,.5,.75) for turn in (0,4,2,6) for n in range(28,34) for m in (16,17,18)]
 record({'kind':'prospective','seed_base':80000,'jobs':len(jobs),'seconds_cap':args.seconds,'workers':1,'representation_change':'dense16to18 boundary shell vs former12; bulk count drops by4to6','order':'interleave shell counts and Ns, then lattice rotation,clock andcutpattern','stop':'100 stagnant programs or wall cap; not an unchanged extension of m12','success':'exact improvement by1e-4 relative radius versus fresh upper comparison'})
 best={n:actual_radius(np.loadtxt(HERE/f'source/coc{n}.txt')[:,1:]/C) for n in range(28,34)};stale=0;start=time.monotonic();done=0
 for index,(n,m,phase,turn,pattern) in enumerate(jobs):
  if time.monotonic()-start>args.seconds:break
  job=time.monotonic();p,r,mi=motif(n,m,phase,turn,pattern);q,rr,fi=free(p,r)
  row={'kind':'result','seed':80000+index,'n':n,'shell_count':m,'bulk_count':n-m,'clock_start':phase/m,'rotation_start':turn*np.pi/48,'cut_pattern':pattern,'motif':mi,'free':fi,'radius_original':rr*C,'whole_seconds':time.monotonic()-job}
  improved=rr>best[n]+1e-10
  if improved:
   cert,path=certify(q,rr,f'dense_shell_best_n{n}',row)
   if cert:best[n]=rr;row.update(exact_certificate=cert,artifact=path)
  stale=0 if improved else stale+1;done+=1;record(row)
  if done%20==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'stale':stale,'best_original':{n:best[n]*C for n in best}}),flush=True)
  if stale>=100:record({'kind':'stop','reason':'100 stagnant dense-shell programs; do not extrapolate to other unsearched families'});break
 record({'kind':'complete','jobs':done,'whole_seconds':time.monotonic()-start,'best_original':{n:best[n]*C for n in best}})
if __name__=='__main__':main()
