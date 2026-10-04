#!/usr/bin/env python3
"""Release row restrictions once for each saved best row-program packing."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'search/torus'));from search import optimize,value
sys.path.insert(0,str(ROOT/'certification'));from verify import verify
OUT=ROOT/'candidates/wave2_packing';LOG=Path(__file__).parent/'row_release.jsonl'
def log(row):
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
def main():
 paths=sorted(OUT.glob('row_best_n*.json'))
 log({'kind':'prospective','method':'release uniform-geodesic-row restrictions once per best saved row candidate; all pair inequalities remain','files':[p.name for p in paths],'workers':1,'maxiter':800,'success':'exact counterexample only; current record status unaudited'})
 start=time.monotonic()
 for path in paths:
  s=json.loads(path.read_text());p=np.array(s['points'],dtype=float)/int(s['scale']);q,info=optimize(p,maxiter=800)
  scale=10**12;z={'problem':'torus_distance','points':(np.rint(q*scale).astype(np.int64)%scale).tolist(),'scale':scale,'provenance':{'source':path.name,'method':'one row-symmetry release','optimizer':info}}
  cert=verify(z);assert cert['passed'];z['bound']=cert['value'];dest=OUT/('released_'+path.name);dest.write_text(json.dumps(z,indent=2)+'\n')
  log({'kind':'result','source':path.name,'before':float(value(p)),'after':float(value(q)),'optimizer':info,'exact_certificate':cert,'artifact':dest.name})
 log({'kind':'complete','whole_seconds':time.monotonic()-start})
if __name__=='__main__':main()
