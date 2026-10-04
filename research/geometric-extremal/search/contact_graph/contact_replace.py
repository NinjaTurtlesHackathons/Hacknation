#!/usr/bin/env python3
"""Explicit periodic contact replacement, not local jitter restart.
All-pair inequalities stay enforced. New diagonals are forced tangencies;
selected old contact lifts are forced open. Endpoint is freely polished.
"""
import os,sys,json,time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'search/torus'));from search import lattice,value,optimize
sys.path.insert(0,str(ROOT/'certification'));from verify import verify
OUT=ROOT/'candidates/contact_graph';LOG=HERE/'experiments.jsonl'
def record(row):
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
n=15;baseline=lattice(n,4,1);i,j=np.triu_indices(n,1);m=len(i)
def edge(a,b):
 a%=n;b%=n;v=baseline[b]-baseline[a];s=-np.rint(v).astype(int)
 return {'i':a,'j':b,'shift':s.tolist(),'baseline_numerator':[int(round((v[c]+s[c])*n)) for c in range(2)]}
def hypothesis(seed):
 # Translation-equivalent single diagonals collapse to one; use distinct
 # multiple-defect separations and old-contact release patterns instead.
 mode=(seed-3000)%10;origins=[0] if mode<2 else [0,1+(mode-2)%7]
 if mode==9:origins=[0,3,6]
 new=[edge(k,k+3) for k in origins]
 old=[]
 for k in origins:
  options=[edge(k,k+1),edge(k+3,k+4),edge(k,k+4),edge(k+3,k+7)]
  pattern=((seed-3000)//10)%4
  old.extend(options if pattern==3 else options[pattern:pattern+2])
 unique={tuple(sorted((e['i'],e['j']))):e for e in old};old=list(unique.values())
 gap=[.00005,.0002,.0008,.002,.004][((seed-3000)//20)%5]
 # New k->k+3 closes triangle with old k->k+4 and reverse step1.
 # Exact integer winding closes: shift04-shift34-shift03=0.
 cycles=[]
 for k in origins:
  a=edge(k,k+4);b=edge(k+3,k+4);c=edge(k,k+3)
  winding=np.array(a['shift'])-np.array(b['shift'])-np.array(c['shift'])
  assert np.all(winding==0)
  cycles.append({'vertices':[k%n,(k+4)%n,(k+3)%n,k%n],'integer_winding':winding.tolist()})
 return {'seed':seed,'required_new_contacts':new,'released_old_contacts':old,'opening_gap_d2':gap,'closed_triangle_winding_checks':cycles,'target_n':n,'constraint':'every periodic pair distance>=q; selected new lift squared distance=q; selected old lift squared distance>=q+gap'}
def replace(p,H):
 new=H['required_new_contacts'];old=H['released_old_contacts'];gap=H['opening_gap_d2']
 def unpack(z):return np.vstack((np.zeros(2),z[:-1].reshape(n-1,2)))
 def ed(q,e):return q[e['j']]-q[e['i']]+np.array(e['shift'])
 def con(z):
  q=unpack(z);v=q[i]-q[j];v-=np.rint(v)
  return np.r_[np.sum(v*v,axis=1)-z[-1],[ed(q,e)@ed(q,e)-z[-1]-gap for e in old]]
 def eq(z):
  q=unpack(z);return np.array([ed(q,e)@ed(q,e)-z[-1] for e in new])
 def ej(z,es):
  q=unpack(z);J=np.zeros((len(es),2*(n-1)+1));J[:,-1]=-1
  for k,e in enumerate(es):
   v=ed(q,e)
   if e['j']>0:J[k,2*(e['j']-1):2*e['j']]+=2*v
   if e['i']>0:J[k,2*(e['i']-1):2*e['i']]-=2*v
  return J
 def jac(z):
  q=unpack(z);v=q[i]-q[j];v-=np.rint(v);J=np.zeros((m,2*(n-1)+1));J[:,-1]=-1
  for c in range(2):
   good=i>0;J[np.arange(m)[good],2*(i[good]-1)+c]=2*v[good,c]
   good=j>0;J[np.arange(m)[good],2*(j[good]-1)+c]=-2*v[good,c]
  return np.vstack((J,ej(z,old)))
 # Deterministic contact-directed contraction supplies seed, rather than
 # random coordinate jitter; scale around each required pair midpoint.
 q=p.copy()
 for e in new:
  a,b=e['i'],e['j'];v=ed(q,e);q[a]+=.055*v;q[b]-=.055*v
 q-=q[0]
 z=np.r_[q[1:].ravel(),.9*17/225]
 t=time.monotonic();res=minimize(lambda z:-z[-1],z,jac=lambda z:np.r_[np.zeros(len(z)-1),-1],method='SLSQP',constraints=[{'type':'ineq','fun':con,'jac':jac},{'type':'eq','fun':eq,'jac':lambda z:ej(z,new)}],bounds=[(None,None)]*(2*(n-1))+[(.04,.085)],options={'maxiter':500,'ftol':1e-12})
 q=unpack(res.x);r={'success':bool(res.success),'iterations':int(res.nit),'elapsed_seconds':time.monotonic()-t,'objective_d2':float(res.x[-1]),'actual_d2':float(value(q)),'min_inequality':float(min(con(res.x))),'max_new_contact_residual':float(max(abs(eq(res.x))))}
 return q%1,r
def save(p,name,metadata):
 z=10**12;pts=(np.rint((p%1)*z).astype(np.int64)%z).tolist();s={'problem':'torus_distance','points':pts,'scale':z,'provenance':metadata};r=verify(s)
 assert r['passed'];s['bound']=r['value'];path=OUT/(name+'.json');path.write_text(json.dumps(s,indent=2)+'\n');return r,str(path.relative_to(ROOT))
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 Hs=[hypothesis(seed) for seed in range(3000,3100)]
 record({'kind':'prospective_contact_replacement_batch','seed_range':[3000,3099],'count':100,'method':'force_diagonal_tangency_and_old_contact_opening_then_free_polish','worker_count':1,'hypotheses':Hs,'stop':'one bounded batch; no unchanged extensions','success':'exact all-pair feasible Markov counterexample or independently audited record'})
 best=0;best_forced=0;start=time.monotonic()
 for H in Hs:
  job=time.monotonic();p,info=replace(baseline,H);q,polish=optimize(p,maxiter=500)
  row={'kind':'contact_replacement_result','hypothesis':H,'forced':info,'free_polish':polish,'whole_job_seconds':time.monotonic()-job}
  forced_ok=info['min_inequality']>=-1e-9 and info['max_new_contact_residual']<=1e-9
  row['forced_numerically_feasible']=forced_ok
  if forced_ok and value(p)>best_forced:
   best_forced=float(value(p));r,path=save(p,'best_forced_contact_replacement',row);row.update(forced_exact_certificate=r,forced_artifact=path)
  if value(q)>best:
   best=float(value(q));r,path=save(q,'best_contact_replacement',row);row.update(exact_certificate=r,artifact=path)
  record(row)
  print(json.dumps({'seed':H['seed'],'forced_d2':info['actual_d2'],'forced_ok':forced_ok,'polished_d2':float(value(q)),'best':best}),flush=True)
 record({'kind':'contact_replacement_batch_complete','jobs':len(Hs),'whole_batch_seconds':time.monotonic()-start,'best_free_d2_numeric':best,'best_forced_d2_numeric':best_forced,'interpretation':'See exact saved witnesses; no global exclusion from batch.'})
if __name__=='__main__':main()
