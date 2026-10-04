"""Affine invariant cross-container and point-deletion search. Director-owned.
Fresh sources frozen; no author's algorithm copied. Sequential linearization
of determinant/hull-area epigraph, evaluate true objective after each step.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[k]='1'
from pathlib import Path
import json,time,hashlib,urllib.request,itertools,sys,importlib.util
from fractions import Fraction
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[2]; OUT=BASE/'candidates/transfer'; OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('exact',BASE/'certification/verify.py'); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
LOG=OUT/'experiments.jsonl'
def log(d):
 with LOG.open('a') as f: f.write(json.dumps(d)+'\n')
def source(kind,n):
 p=OUT/f'source_{kind}_{n}.json'; u=f'https://math.tejstead.com/heilbronn/{kind}/{n}/points.json'
 if not p.exists():
  b=urllib.request.urlopen(u,timeout=30).read(); p.write_bytes(b); log({'event':'source','url':u,'sha256':hashlib.sha256(b).hexdigest(),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 return json.loads(p.read_text())
def measure(P,T):
 a,b,c=P[T[:,0]],P[T[:,1]],P[T[:,2]]
 D=(b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0])
 h=ConvexHull(P).vertices; H=sum(P[i,0]*P[j,1]-P[i,1]*P[j,0] for i,j in zip(h,np.roll(h,-1)))
 return abs(D).min()/H,D,h,H
def polish(P,steps=180):
 P=P.copy(); n=len(P); T=np.array(list(itertools.combinations(range(n),3))); trust=.025
 best,D,h,H=measure(P,T)
 for it in range(steps):
  if trust<1e-9: break
  v,D,h,H=measure(P,T); sig=np.sign(D); G=np.zeros((len(T),2*n)); rows=np.arange(len(T)); a,b,c=T.T
  G[rows,2*a]=P[b,1]-P[c,1]; G[rows,2*b]=P[c,1]-P[a,1]; G[rows,2*c]=P[a,1]-P[b,1]
  G[rows,2*a+1]=P[c,0]-P[b,0]; G[rows,2*b+1]=P[a,0]-P[c,0]; G[rows,2*c+1]=P[b,0]-P[a,0]
  gH=np.zeros(2*n)
  for z,i in enumerate(h):
   j=h[(z+1)%len(h)]; k=h[(z-1)%len(h)]; gH[2*i]=P[j,1]-P[k,1]; gH[2*i+1]=P[k,0]-P[j,0]
  A=np.column_stack([-sig[:,None]*G+v*gH,H*np.ones(len(T))]); rhs=abs(D)-v*H
  obj=np.zeros(2*n+1); obj[-1]=-1
  r=linprog(obj,A_ub=A,b_ub=rhs,bounds=[(-trust,trust)]*(2*n)+[(None,None)],method='highs')
  if not r.success: trust*=.5; continue
  Q=P+r.x[:-1].reshape(n,2); w=measure(Q,T)[0]
  if w>best+2e-13:
   P=Q; best=w; trust=min(.03,trust*1.3)
  else: trust*=.5
 return P,best,it+1

def save(P,n,label):
 s={'problem':'heilbronn_convex','points':[[format(x,'.16g'),format(y,'.16g')] for x,y in P],'origin':label}
 r=V.verify(s); p=OUT/f'candidate_n{n}_{label}.json'; p.write_text(json.dumps(s,indent=2)); return r,str(p.relative_to(BASE))

def main():
 ns=range(18,36); log({'event':'prospective_batch','method':'source baseline + cross-container sequential LP; affine normalized determinants','ns':list(ns),'max_steps':180,'seeds':'deterministic source transfer and every deletion from convex n+1'})
 for n in ns:
  for kind in ('convex','square','triangle'):
   try: s=source(kind,n)
   except Exception as e: log({'event':'source_gap','n':n,'kind':kind,'error':str(e)}); continue
   b=source('convex',n); baseline=float(Fraction(b['value']['fraction'])); P=np.array(s['points'],float); t=time.monotonic()
   start=measure(P,np.array(list(itertools.combinations(range(n),3))))[0]; Q,w,iterations=polish(P)
   r,path=save(Q,n,kind); d={'event':'experiment','method':'cross-container LP','n':n,'origin':kind,'initial':start,'baseline':baseline,'result':r,'iterations':iterations,'wall_seconds':time.monotonic()-t,'candidate':path}; log(d)
   print(n,kind,'initial',start,'result',w,'baseline',baseline,'gain',w/baseline-1,flush=True)
   if r['passed'] and float(Fraction(r['value']))>baseline*1.0005: print('SUBSTANTIVE CANDIDATE',path,flush=True)
 # distinct topology change: all single-point deletions of source larger hulls
 for n in (20,21,22,24,26,28,30,32,34):
  try: s=source('convex',n+1); b=source('convex',n)
  except Exception: continue
  P=np.array(s['points'],float); baseline=float(Fraction(b['value']['fraction']))
  for j in range(n+1):
   t=time.monotonic(); Q,w,it=polish(np.delete(P,j,axis=0),100); r,path=save(Q,n,f'delete{j}from{n+1}')
   log({'event':'experiment','method':'delete + hull LP','n':n,'deleted':j,'baseline':baseline,'result':r,'iterations':it,'wall_seconds':time.monotonic()-t,'candidate':path})
   print('delete',n,j,w,baseline,w/baseline-1,flush=True)
if __name__=='__main__': main()
