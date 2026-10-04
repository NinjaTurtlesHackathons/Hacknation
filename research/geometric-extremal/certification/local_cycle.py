"""Exact dependency checker for a narrow, independently reviewed local lemma.
Trust basis: elementary inequalities spelled out in general_cycle_lemma.md;
Python integer/Fraction arithmetic checks graph/lift/constants, not Lean.
"""
from fractions import Fraction as Q
from math import gcd
from itertools import combinations

def check():
 n=15;p=[(Q(k,n),Q((4*k)%n,n)) for k in range(n)]
 shortest=min(min((a[0]-b[0]+u)**2+(a[1]-b[1]+v)**2 for u in (-1,0,1) for v in (-1,0,1)) for a,b in combinations(p,2))
 assert shortest==Q(17,225)
 vectors=[(Q(1,15),Q(4,15)),(Q(4,15),Q(1,15))]
 for step,z in zip((1,4),vectors):
  assert gcd(step,n)==1
  for i in range(n):
   j=(i+step)%n
   assert all((z[c]-(p[j][c]-p[i][c])).denominator==1 for c in (0,1))
   assert z[0]**2+z[1]**2==shortest
 a,b=vectors[0];c,d=vectors[1];det=a*d-b*c
 inv=((d/det,-b/det),(-c/det,a/det));norm=max(sum(abs(x) for x in row) for row in inv)
 assert norm==5
 coefficient=4*(n-1)**2*norm;assert coefficient==3920
 return {'passed':True,'n':n,'squared_separation':str(shortest),'strict_supnorm_radius':str(1/coefficient),'displacement_quadratic_coefficient':str(coefficient),'assumptions':'fixed unit-square torus; labelled compatible lifts p_i+u_i, u_0=0; max ||u_i||∞ strictly below radius; all periodic-copy distances >=17/225','conclusion':'all u_i=0','level':'computed_rigorous','scope':'local exclusion only; known mechanism; novelty not established','proof_basis':'exact lift and rational constant identities plus independently reviewed cycle-sum and quadratic displacement argument; no formal proof assistant'}
if __name__=='__main__':
 import json;print(json.dumps(check()))
