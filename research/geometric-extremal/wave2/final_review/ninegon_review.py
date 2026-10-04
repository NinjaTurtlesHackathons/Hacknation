#!/usr/bin/env python3
"""Independent polynomial and exact geometric audit; no discovery imports."""
from pathlib import Path
from math import gcd
from fractions import Fraction
import json
# linear form pairs (coefficient of s, coefficient of t)
V=[((0,0),(0,0)),((1,0),(-2,0)),((3,0),(-3,0)),((3,1),(-3,0)),((4,1),(-2,0)),((3,1),(0,0)),((3,0),(0,1)),((1,0),(1,1)),((0,0),(0,1))]
def mul(a,b):return [a[0]*b[0],a[0]*b[1]+a[1]*b[0],a[1]*b[1]]
area=[0,0,0]
for v,w in zip(V,V[1:]+V[:1]):
 pos,neg=mul(v[0],w[1]),mul(v[1],w[0]);area=[x+y-z for x,y,z in zip(area,pos,neg)]
assert area==[18,12,1]
def evalv(v,s,t):return tuple(x*s+y*t for x,y in v)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def points(s,t):
 v=[evalv(z,s,t) for z in V];v=list(dict.fromkeys(v));p={(a,b) for a in range(min(x[0] for x in v),max(x[0] for x in v)+1) for b in range(min(x[1] for x in v),max(x[1] for x in v)+1) if all(cross(u,w,(a,b))>=0 for u,w in zip(v,v[1:]+v[:1]))};return v,p
checks=[]
for s in range(1,9):
 for t in range(9):
  v,p=points(s,t);n=9*s*s+6*s*t+t*(t+3)//2+3*s+1
  boundary=sum(gcd(abs(w[0]-u[0]),abs(w[1]-u[1])) for u,w in zip(v,v[1:]+v[:1]));assert boundary==6*s+3*t
  assert len(p)==n
  assert {(-a-b+3*s+t,a-3*s) for a,b in p}==p
  assert {(b+3*s,a-3*s) for a,b in p}==p
  checks.append({'s':s,'t':t,'n':n,'boundary':boundary,'passed':True})
B=Path(__file__).resolve().parents[2];spec=json.loads((B/'candidates/wave2_family/support_k41_n111_code7324998.json').read_text());_,p=points(3,1)
assert p=={(a+6,b-2) for a,b in spec['points']}
out={'passed':True,'symbolic_shoelace_coefficients_s2_st_t2':area,'symbolic_boundary':'6s+3t','symbolic_cardinality':'9s^2+6st+t(t+3)/2+3s+1','physical_area_factor':'sqrt(3)/2 times coordinate area','rotation_translation':'(3s+t,-3s)','reflection_translation':'(3s,-3s)','independent_cases':checks,'s3_t1_equals_translated_candidate':True,'general_proof':'See ninegon_review.md; finite cases supplement, do not establish the general formula.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print('symbolic area, 72 cases, centered actions and111 translation PASS')
