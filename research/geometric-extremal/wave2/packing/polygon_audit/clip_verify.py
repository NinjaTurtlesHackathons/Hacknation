#!/usr/bin/env python3
"""Independent exact convex intersection audit; no SAT verifier imported.
Arithmetic field Q(sqrt(3)), order by refining rational isolating intervals.
Interior disjointness follows from zero intersection area after clipping.
"""
from fractions import Fraction as F
from math import isqrt
from functools import lru_cache
import json,sys
@lru_cache(None)
def root_interval(bits):
 den=1<<bits;lo=isqrt(3*den*den);return F(lo,den),F(lo+1,den)
class E:
 def __init__(self,a=0,b=0):self.a=F(a);self.b=F(b)
 def __add__(self,z):
  z=z if isinstance(z,E) else E(z);return E(self.a+z.a,self.b+z.b)
 __radd__=__add__
 def __neg__(self):return E(-self.a,-self.b)
 def __sub__(self,z):return self+-z if isinstance(z,E) else self+E(-F(z))
 def __mul__(self,z):
  z=z if isinstance(z,E) else E(z);return E(self.a*z.a+3*self.b*z.b,self.a*z.b+self.b*z.a)
 __rmul__=__mul__
 def __truediv__(self,z):
  z=z if isinstance(z,E) else E(z);den=z.a*z.a-3*z.b*z.b
  if not den:raise ZeroDivisionError()
  return self*E(z.a/den,-z.b/den)
 def sign(self):
  if not self.b:return (self.a>0)-(self.a<0)
  bits=16
  while True:
   lo,hi=root_interval(bits)
   lower=self.a+self.b*(lo if self.b>0 else hi)
   upper=self.a+self.b*(hi if self.b>0 else lo)
   if lower>0:return 1
   if upper<0:return -1
   bits*=2
 def zero(self):return self.a==0 and self.b==0
def add(p,q):return (p[0]+q[0],p[1]+q[1])
def sub(p,q):return (p[0]-q[0],p[1]-q[1])
def mul(t,p):return (t*p[0],t*p[1])
def cross(p,q):return p[0]*q[1]-p[1]*q[0]
def dot(p,q):return p[0]*q[0]+p[1]*q[1]
def clip(subject,A,B):
 if not subject:return []
 edge=sub(B,A);result=[]
 previous=subject[-1];fp=cross(edge,sub(previous,A));sp=fp.sign()
 for current in subject:
  fc=cross(edge,sub(current,A));sc=fc.sign()
  if (sc>=0)!=(sp>=0):
   t=fp/(fp-fc);result.append(add(previous,mul(t,sub(current,previous))))
  if sc>=0:result.append(current)
  previous,fp,sp=current,fc,sc
 return result
def area2(poly):
 return sum((cross(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))),E())
def exact(x):
 if type(x) not in (int,str):raise ValueError('Rational integer/string required')
 return F(x)
def verify(o):
 if o.get('problem')!='equilateral_triangles_square':raise ValueError('Problem')
 n=o['n'];h=exact(o['half_side'])
 if type(n)!=int or n<=0 or h<=0 or len(o['triangles'])!=n:raise ValueError('Dimensions')
 allpoly=[];checks=0
 for row in o['triangles']:
  if len(row)!=3:raise ValueError('Row length')
  x,y,t=map(exact,row);c=(1-t*t)/(1+t*t);s=2*t/(1+t*t)
  assert c*c+s*s==1
  center=(E(x),E(y));poly=[]
  for v in ((E(1),E()),(E('-1/2'),E(0,'1/2')),(E('-1/2'),E(0,'-1/2'))):
   p=add(center,(c*v[0]-s*v[1],s*v[0]+c*v[1]));poly.append(p)
   assert (dot(sub(p,center),sub(p,center))-1).zero()
   if any((E(h)-coord).sign()<0 or (E(h)+coord).sign()<0 for coord in p):raise ValueError('Wall violation')
   checks+=4
  for k in range(3):assert (dot(sub(poly[k],poly[(k+1)%3]),sub(poly[k],poly[(k+1)%3]))-3).zero()
  if area2(poly).sign()<=0:raise ValueError('Triangle orientation/degeneracy')
  allpoly.append(poly)
 pairs=0
 for i,A in enumerate(allpoly):
  for j,B in enumerate(allpoly[:i]):
   intersection=A[:]
   for k in range(3):intersection=clip(intersection,B[k],B[(k+1)%3])
   sign=area2(intersection).sign();pairs+=1
   if sign<0:raise AssertionError('Clipping generated reversed polygon')
   if sign>0:raise ValueError(f'Positive-area interior overlap {j},{i}')
 ans={'passed':True,'n':n,'pairs':pairs,'wall_checks':checks,'unit_circumradius_checks':3*n,'unit_side_squared_checks':3*n,'square_circumradius_squared':str(2*h*h),'arithmetic':'Q(sqrt3) with rational isolating-root order','method':'exact convex polygon clipping and intersection area'}
 if 'benchmark_R_squared_lower' in o:
  b=exact(o['benchmark_R_squared_lower']);ans['supplied_benchmark_gap']=str(b-2*h*h);ans['improves_supplied_benchmark']=2*h*h<b
 return ans
def selftest():
 tests=[]
 def check(name,o,want):
  try:r=verify(o);got=True
  except ValueError:got=False
  assert got==want,(name,got,want);tests.append({'name':name,'passed':True,'expected_feasible':want})
 base={'problem':'equilateral_triangles_square','n':1,'half_side':'1','triangles':[['0','0','0']]}
 check('unit triangle tangent square right wall',base,True)
 check('wall crossing',dict(base,half_side='999/1000'),False)
 check('wrong orientation changes wall feasibility',dict(base,half_side='9/10',triangles=[['0','0','1']]),False)
 check('orientation zero fails asymmetric wall',dict(base,half_side='13/10',triangles=[['2/5','0','0']]),False)
 check('orientation quarter turn fits same asymmetric wall',dict(base,half_side='13/10',triangles=[['2/5','0','1']]),True)
 check('exact edge vertex contact',dict(base,n=2,half_side='3',triangles=[['0','0','0'],['3/2','0','0']]),True)
 check('small positive area overlap',dict(base,n=2,half_side='3',triangles=[['0','0','0'],['149/100','0','0']]),False)
 check('identical triangle',dict(base,n=2,triangles=base['triangles']*2),False)
 check('floating parameters rejected',dict(base,half_side=1.0),False)
 check('boolean count rejected',dict(base,n=True),False)
 check('large rotation rational tan-half',dict(base,half_side='2',triangles=[['0','0','1000000000000']]),True)
 assert E(2,-1).sign()>0 and E(-2,1).sign()<0 and E(1,-1).sign()<0
 assert not verify(dict(base,benchmark_R_squared_lower='2'))['improves_supplied_benchmark']
 assert verify(dict(base,benchmark_R_squared_lower='2001/1000'))['improves_supplied_benchmark']
 assert not verify(dict(base,benchmark_R_squared_lower='1999/1000'))['improves_supplied_benchmark']
 return {'passed':True,'controls':tests,'order_controls':3,'strict_comparison_controls':3}
if __name__=='__main__':
 print(json.dumps(selftest() if sys.argv[1:]==['--selftest'] else verify(json.loads(open(sys.argv[1]).read())),indent=2))
