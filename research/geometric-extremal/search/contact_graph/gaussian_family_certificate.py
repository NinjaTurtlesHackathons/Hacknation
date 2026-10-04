#!/usr/bin/env python3
"""Exact, compact certificates for known Gaussian cyclic torus packings.
No optimizer, floats, numpy, external checker, or dense rigidity matrix.
"""
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import json,time,hashlib
HERE=Path(__file__).parent;ROOT=HERE.parents[1];LOG=HERE/'experiments.jsonl'
def log(row):
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
log({'kind':'prospective_family_certificate','members':[[4,1],[15,4],[56,15]],'question':'Do these known Gaussian lattices satisfy general two-Hamiltonian-cycle local-exclusion hypotheses?','method':'all nonzero integer modular differences; exact cycle/inverse matrix arithmetic','allowed':'fixed square torus, equal radii, compatible labelled lifts, translation gauge','success':'exact shortest contacts plus independent Hamiltonian cycles; no new-discovery assertion','workers':1})
def cert(a,b):
 start=time.monotonic();assert a>b>0 and gcd(a,b)==1
 n=a*a-b*b;assert n>=3;assert gcd(a,n)==gcd(b,n)==1
 t=(a*pow(b,-1,n))%n
 assert (t*b-a)%n==0 and (t*a-b)%n==0
 assert gcd(t,n)==1
 # p_0=0. Translation invariance reduces every pair difference to p_k.
 dnums=[]
 for k in range(1,n):
  x=(b*k)%n;y=(a*k)%n;x=min(x,n-x);y=min(y,n-y)
  dnums.append(x*x+y*y)
 shortest=min(dnums);assert shortest==a*a+b*b
 # This additionally checks no self-copy is closer; period length^2 is1.
 d2=Q(shortest,n*n);assert d2<=1
 contacts=[k for k,v in enumerate(dnums,1) if v==shortest]
 assert set(contacts)=={1,n-1,t,n-t}
 Z=[[Q(b,n),Q(a,n)],[Q(a,n),Q(b,n)]];inverse=[[-b,a],[a,-b]]
 for i in range(2):
  for j in range(2):assert sum(Z[i][k]*inverse[k][j] for k in range(2))==int(i==j)
 K=a+b;assert K==max(sum(abs(x) for x in r) for r in inverse)
 C=4*(n-1)**2*K
 # Modular identities certify every contact lift. Both cycles visit alln
 # vertices; cycle-sum proof of rank avoids quadratic-size linear algebra.
 rows={'a':a,'b':b,'n':n,'formula':'p_k=((b*k mod n)/n,(a*k mod n)/n),k=0..n-1','squared_separation':str(d2),'nonzero_differences_checked':n-1,'critical_differences':contacts,'cycle_steps':[1,t],'gcd_cycle_steps':[1,gcd(t,n)],'contact_vectors':[[str(x) for x in r] for r in Z],'contact_lifts_integral':True,'Z_inverse':inverse,'inverse_infinity_norm':K,'local_radius_strict':str(Q(1,C)),'displacement_bound_coefficient':C,'rigidity_rank_by_cycle_argument':2*n-2,'certificate_arithmetic':'integer and rational; no numerical geometry','global_optimality_claim':False,'novelty':'Known Gaussian lattice; conditional analytic pruning lemma awaiting independent proof review','elapsed_seconds':time.monotonic()-start}
 rows['objective_data_sha256']=hashlib.sha256(json.dumps(dnums,separators=(',',':')).encode()).hexdigest()
 return rows
results=[cert(a,b) for a,b in [(4,1),(15,4),(56,15)]]
out={'passed_exact_family_hypotheses':True,'members':results,'analytic_lemma_file':'search/contact_graph/general_cycle_lemma.md','analytic_proof_status':'requires independent review; computed hypotheses pass'}
path=ROOT/'candidates/contact_graph/gaussian_family_local_exclusion.json';path.write_text(json.dumps(out,indent=2)+'\n');log({'kind':'family_certificate_result','artifact':str(path.relative_to(ROOT)),**out})
print(json.dumps([{'n':r['n'],'d2':r['squared_separation'],'second_cycle_step':r['cycle_steps'][1],'radius':r['local_radius_strict']} for r in results],indent=2))
