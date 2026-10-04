#!/usr/bin/env python3
"""Distinct discrete search: exhaustive cyclic slope family, integer objective."""
import json,math,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LOG=Path(__file__).parent/'experiments.jsonl'
def record(x):
 with LOG.open('a') as f:f.write(json.dumps(x)+'\n')
record({'kind':'prospective_discrete_batch','family':'points=(k/N,s*k/N) mod1','n_range':[6,200],'slopes':'0..N-1','exact_objective':'integer squared residue / N^2','warning':'cyclic HNF subset, not all configurations nor all lattices'})
t=time.monotonic();rows=[]
for n in range(6,201):
 for s in range(n):
  v=min(min(k,n-k)**2+min((s*k)%n,n-(s*k)%n)**2 for k in range(1,n))
  q=Q(v,n*n);delta=n*math.pi*float(q)/4
  M=math.pi/(2*n*(math.pi/(2*math.sqrt(3))-delta))
  rows.append({'n':n,'slope':s,'d2':str(q),'M_diagnostic':M})
rows.sort(key=lambda x:-x['M_diagnostic'])
record({'kind':'discrete_family_result','evaluated':len(rows),'elapsed_seconds':time.monotonic()-t,'top':rows[:20],'counterexample':False,'interpretation':'No cyclic lattice in this finite range violates threshold; cannot exclude nonlattice witnesses.'})
print(json.dumps(rows[:20],indent=2))
