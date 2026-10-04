#!/usr/bin/env python3
"""Exact symbolic coefficient and concrete witness check; no discovery import."""
from pathlib import Path
import json, math
# Each coordinate is its (s,t) coefficient pair.
V=[((0,0),(0,0)),((1,0),(-2,0)),((3,0),(-3,0)),((3,1),(-3,0)),((4,1),(-2,0)),((3,1),(0,0)),((3,0),(0,1)),((1,0),(1,1)),((0,0),(0,1))]
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def sub(x,y):return tuple(a-b for a,b in zip(x,y))
def neg(x):return tuple(-a for a in x)
def mul(x,y):return(x[0]*y[0],x[0]*y[1]+x[1]*y[0],x[1]*y[1])
def cross(x,y):return sub(mul(x[0],y[1]),mul(y[0],x[1]))
area=(0,0,0)
for i,v in enumerate(V):area=add(area,cross(v,V[(i+1)%9]))
assert area==(18,12,1)
E=[(sub(V[(i+1)%9][0],v[0]),sub(V[(i+1)%9][1],v[1])) for i,v in enumerate(V)]
turns=[cross(E[i],E[(i+1)%9]) for i in range(9)];assert turns==[(3,0,0),(0,1,0),(0,1,0)]*3
rot={(add(neg(add(a,b)),(3,1)),add(a,(-3,0))) for a,b in V};ref={(add(b,(3,0)),add(a,(-3,0))) for a,b in V};assert rot==ref==set(V)
v=[(3*a+b,3*c+d) for (a,b),(c,d) in V];A2=sum(cross(((a,0),(b,0)),((c,0),(d,0)))[0] for (a,b),(c,d) in zip(v,v[1:]+v[:1]));boundary=sum(math.gcd(abs(c-a),abs(d-b)) for (a,b),(c,d) in zip(v,v[1:]+v[:1]));assert(A2,boundary)==(199,21)
def det(p,a,b):return(a[0]-p[0])*(b[1]-p[1])-(a[1]-p[1])*(b[0]-p[0])
filled={(a,b) for a in range(min(x for x,y in v),max(x for x,y in v)+1) for b in range(min(y for x,y in v),max(y for x,y in v)+1) if all(det(v[i],v[(i+1)%9],(a,b))>=0 for i in range(9))}
p=Path(__file__).resolve().parents[2]/'candidates/wave2_family/support_k41_n111_code7324998.json';S={(a+6,b-2) for a,b in json.loads(p.read_text())['points']};assert filled==S and len(S)==111
print(json.dumps({'passed':True,'shoelace_coefficients_s2_st_t2':area,'consecutive_turn_coefficients':turns,'symbolic_D3_vertex_actions':True,'at_s3_t1_area2':A2,'boundary':boundary,'N_by_Pick':(A2+boundary)//2+1,'all_polygon_lattice_sites_match_translated_S41':True},indent=2))
