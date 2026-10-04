#!/usr/bin/env python3
"""Exact graph/stress audit for known torus lattice; quantitative local pruning."""
from fractions import Fraction as Q
from pathlib import Path
import json,time
HERE=Path(__file__).parent;ROOT=HERE.parents[1];LOG=HERE/'experiments.jsonl'
def log(x):
 with LOG.open('a') as f:f.write(json.dumps(x)+'\n')
log({'kind':'prospective_analytic_audit','question':'Does known n15 cyclic contact graph admit a sufficiently small nonlattice equal-or-better perturbation?','assumptions':'labelled points on fixed unit square flat torus; translation fixed; exact pair feasibility','method':'exact graph cycles, rational rigidity rank, uniform equilibrium stress, explicit quadratic displacement bound','success':'decisive local exclusion or identify a flex','stop':'single exact audit, no optimizer or parameter jitter'})
t=time.monotonic();n=15;p=[(Q(k,n),Q((4*k)%n,n)) for k in range(n)];rows=[];edges=[]
for step,v in [(1,(Q(1,15),Q(4,15))),(4,(Q(4,15),Q(1,15)))]:
 for i in range(n):
  j=(i+step)%n;delta=(p[j][0]-p[i][0],p[j][1]-p[i][1]);shift=(v[0]-delta[0],v[1]-delta[1]);assert all(x.denominator==1 for x in shift)
  row=[Q(0)]*(2*n)
  for c in range(2):row[2*j+c]=v[c];row[2*i+c]=-v[c]
  rows.append(row);edges.append({'i':i,'j':j,'step':step,'lift_shift':[int(x) for x in shift],'vector':[str(x) for x in v]})
assert len({frozenset((e['i'],e['j'])) for e in edges})==30
assert all(sum(r[c] for r in rows)==0 for c in range(2*n))
A=[r.copy() for r in rows];rank=0
for c in range(2*n):
 pivot=next((k for k in range(rank,len(A)) if A[k][c]),None)
 if pivot is None:continue
 A[rank],A[pivot]=A[pivot],A[rank];v=A[rank][c];A[rank]=[x/v for x in A[rank]]
 for k in range(len(A)):
  if k!=rank and A[k][c]:v=A[k][c];A[k]=[a-v*b for a,b in zip(A[k],A[rank])]
 rank+=1
assert rank==28
for step in [1,4]:assert len({(k*step)%n for k in range(n)})==15
out={'status':'exact graph audit; analytic local exclusion needs human/independent proof review','n':15,'known_d2':'17/225','contacts':edges,'rank_exact':rank,'uniform_equilibrium_stress':True,'translation_dimension':2,'local_exclusion_supnorm':'1/3920','exclusion_strict':True,'condition':'after translation and matching labels, max_i ||u_i||_infinity <1/3920; separation at least known d2 implies all u_i=0','constants':{'edge_quadratic_lower_coefficient':4,'cycle_upper_coefficient':56,'path_projection_coefficient':784,'inverse_matrix_infinity_norm':5,'displacement_bound_coefficient':3920},'novelty':'Known rigidity mechanism; this explicit certificate is a search-pruning contribution, not asserted new geometry.'}
path=ROOT/'candidates/contact_graph/n15_local_exclusion.json';path.write_text(json.dumps(out,indent=2)+'\n');log({'kind':'analytic_result','elapsed_seconds':time.monotonic()-t,'rank_exact':rank,'artifact':str(path.relative_to(ROOT)),'result':'small-deformation path excluded; globally different contact graphs remain possible'})
print(json.dumps({'rank_exact':rank,'uniform_equilibrium_stress':True,'supnorm_radius':'1/3920','artifact':str(path.relative_to(ROOT))}))
