#!/usr/bin/env python3
"""Outward-rounded mpmath interval audit of fixed source decimal coordinates.
Independent geometry convention check, including deliberately wrong half-step.
"""
from fractions import Fraction as F
from pathlib import Path
import json
from mpmath import iv
iv.dps=60
def endpoint(t):
 sign,man,exp,_=t
 return F((-1 if sign else 1)*man)*(F(2)**exp)
def bounds(x):return tuple(endpoint(t) for t in x._mpi_)
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def min_interval(items):
 b=[bounds(x) for x in items];return min(x[0] for x in b),min(x[1] for x in b)
def max_interval(items):
 b=[bounds(x) for x in items];return max(x[0] for x in b),max(x[1] for x in b)
def gap(a,b):
 # intervals of min(b)-max(a)
 low_b,high_b=min_interval(b);low_a,high_a=max_interval(a)
 return low_b-high_a,high_b-low_a
def audit(path,half_step=False):
 lines=path.read_text().splitlines();l,m,n=map(int,lines[0].split());assert (l,m,n)==(4,3,12)
 R=iv.mpf(lines[1]);h=R/iv.sqrt(2);polys=[];walls=[]
 for row in lines[2:]:
  xs,ys,ts=row.split();x,y,t=map(iv.mpf,(xs,ys,ts));p=[]
  for j in range(3):
   angle=t+(j+(iv.mpf('0.5') if half_step else 0))*2*iv.pi/3
   v=(x+iv.sin(angle),y+iv.cos(angle));p.append(v)
   for vcoord in v:walls.extend([bounds(h-vcoord),bounds(h+vcoord)])
  polys.append(p)
 lower_gaps=[];upper_gaps=[]
 for i,A in enumerate(polys):
  for B in polys[:i]:
   candidates=[]
   for P in (A,B):
    for k in range(3):
     d=sub(P[(k+1)%3],P[k]);normal=(-d[1],d[0])
     pa=[dot(normal,x) for x in A];pb=[dot(normal,x) for x in B]
     candidates.extend([gap(pa,pb),gap(pb,pa)])
   lower_gaps.append(max(a for a,b in candidates));upper_gaps.append(max(b for a,b in candidates))
 return {'source_convention':'sin(theta+(j+0.5)*phi),cos' if half_step else 'sin(theta+j*phi),cos','wall_min_lower':str(min(a for a,b in walls)),'wall_min_upper':str(min(b for a,b in walls)),'pair_best_axis_min_lower':str(min(lower_gaps)),'pair_best_axis_min_upper':str(min(upper_gaps)),'all_walls_and_pairs_certified':all(a>=0 for a,b in walls) and all(a>=0 for a in lower_gaps),'precision_decimal_digits':60,'arithmetic':'outward interval transcendental evaluation, exact rational endpoint reductions','pair_count':len(lower_gaps),'wall_count':len(walls)}
if __name__=='__main__':
 path=Path(__file__).parent/'current_source.txt'
 report={'correct_source':audit(path),'wrong_half_step_control':audit(path,True)}
 (path.parent/'source_interval_results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
