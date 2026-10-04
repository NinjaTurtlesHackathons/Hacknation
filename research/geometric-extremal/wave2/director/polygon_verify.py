"""Exact Q(sqrt(3)) triangle-in-square separating-axis certificate."""
from fractions import Fraction as F
import json
import sys


class Q:
    def __init__(self,a=0,b=0):self.a=F(a);self.b=F(b)
    def __add__(self,x):
        if not isinstance(x,Q):x=Q(x)
        return Q(self.a+x.a,self.b+x.b)
    __radd__=__add__
    def __neg__(self):return Q(-self.a,-self.b)
    def __sub__(self,x):return self+-x if isinstance(x,Q) else self+Q(-F(x))
    def __mul__(self,x):
        if not isinstance(x,Q):x=Q(x)
        return Q(self.a*x.a+3*self.b*x.b,self.a*x.b+self.b*x.a)
    __rmul__=__mul__
    def sign(self):
        a,b=self.a,self.b
        if not b:return (a>0)-(a<0)
        if not a:return (b>0)-(b<0)
        if a>0 and b>0:return 1
        if a<0 and b<0:return -1
        d=a*a-3*b*b
        return ((d>0)-(d<0))*(1 if a>0 else -1)
    def __lt__(self,x):return (self-x).sign()<0


def frac(x):
    if type(x) not in (int,str):raise ValueError('Exact rational strings required')
    return F(x)


def verify(o):
    if o['problem']!='equilateral_triangles_square' or type(o['n']) is not int or o['n']<=0:raise ValueError('Problem/count')
    h=frac(o['half_side']);polys=[]
    if h<=0 or len(o['triangles'])!=o['n']:raise ValueError('Dimensions')
    for row in o['triangles']:
        if len(row)!=3:raise ValueError('Dimensions')
        x,y,t=map(frac,row);c=(1-t*t)/(1+t*t);s=2*t/(1+t*t)
        v=[]
        for a,b in ((Q(1),Q(0)),(Q('-1/2'),Q(0,'1/2')),(Q('-1/2'),Q(0,'-1/2'))):
            xx=Q(x)+c*a-s*b;yy=Q(y)+s*a+c*b
            if (Q(h)-xx).sign()<0 or (Q(h)+xx).sign()<0 or (Q(h)-yy).sign()<0 or (Q(h)+yy).sign()<0:raise ValueError('Outside square')
            v.append((xx,yy))
        polys.append(v)
    for i,A in enumerate(polys):
        for B in polys[:i]:
            separated=False
            for P in (A,B):
                for k in range(3):
                    a,b=P[k],P[(k+1)%3];nx=-(b[1]-a[1]);ny=b[0]-a[0]
                    pa=[nx*x+ny*y for x,y in A];pb=[nx*x+ny*y for x,y in B]
                    if (min(pb)-max(pa)).sign()>=0 or (min(pa)-max(pb)).sign()>=0:separated=True;break
                if separated:break
            if not separated:raise ValueError('Interior overlap')
    ans=dict(passed=True,n=o['n'],half_side=str(h),circumradius_squared=str(2*h*h),arithmetic='exact Q(sqrt3)',pairs=o['n']*(o['n']-1)//2)
    if 'benchmark_R_squared_lower' in o:
        gap=frac(o['benchmark_R_squared_lower'])-2*h*h
        ans.update(gap_to_supplied_benchmark_lower=str(gap),improves_supplied_benchmark=gap>0)
    return ans


def selftest():
    assert Q(2,-1).sign()>0 and Q(1,-1).sign()<0 and Q(-2,1).sign()<0
    o=dict(problem='equilateral_triangles_square',n=1,half_side='1',triangles=[['0','0','0']])
    assert verify(o)['passed']
    for p in [dict(o,half_side='4/5'),dict(o,n=2,triangles=[['0','0','0'],['0','0','0']]),dict(o,n=True),dict(o,half_side=1.)]:
        try:verify(p)
        except ValueError:continue
        raise AssertionError('Negative control')
    assert verify(dict(o,n=2,half_side='3',triangles=[['-1','0','0'],['1','0','0']]))['passed']
    return dict(passed=True,controls=9)


if __name__=='__main__':print(json.dumps(selftest() if sys.argv[1:]==['--selftest'] else verify(json.load(open(sys.argv[1]))),indent=2))
