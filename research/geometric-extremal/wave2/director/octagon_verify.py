"""Independent rational feasibility and Q(sqrt2) comparator, apothem-one octagon."""
from fractions import Fraction as F
import json,sys


def rational(x):
    if type(x) not in (int,str):raise ValueError('Rational strings or integers only')
    return F(x)


def radical_sign(a,b):
    if not b:return (a>0)-(a<0)
    if not a:return (b>0)-(b<0)
    if a>0 and b>0:return 1
    if a<0 and b<0:return -1
    d=a*a-2*b*b
    return ((d>0)-(d<0))*(1 if a>0 else -1)


def verify(o,comparison=None):
    if o.get('problem')!='circle_packing_octagon_apothem' or type(o.get('n')) is not int:raise ValueError('Problem/count')
    p=[[rational(v) for v in row] for row in o['points']];r=rational(o['radius']);h=1-r
    if o['n']<=0 or len(p)!=o['n'] or any(len(row)!=2 for row in p) or r<=0 or h<0:raise ValueError('Dimensions/radius')
    for i,(x,y) in enumerate(p):
        if abs(x)>h or abs(y)>h or (abs(x)+abs(y))**2>2*h*h:raise ValueError('Outside offset octagon')
        for xx,yy in p[:i]:
            if (x-xx)**2+(y-yy)**2<4*r*r:raise ValueError('Overlap')
    v=dict(passed=True,n=len(p),radius_apothem=str(r),squared_radius_circumradius_rational_part=str(r*r/2),squared_radius_circumradius_sqrt2_part=str(r*r/4),arithmetic='exact rational and Q(sqrt2)')
    if comparison is not None:
        target=rational(comparison);a=r*r/2-target*target;b=r*r/4
        v.update(trusted_comparison_circumradius=str(target),strictly_beats_supplied_scalar=radical_sign(a,b)>0)
    return v


def selftest():
    o=dict(problem='circle_packing_octagon_apothem',n=2,points=[['-1/2','0'],['1/2','0']],radius='1/2')
    assert verify(o)['passed']
    bads=[dict(o,radius='501/1000'),dict(o,points=[['-1/2','0'],['49/100','0']]),dict(o,points=[['-1/2','1/2'],['1/2','1/2']]),dict(o,n=True),dict(o,radius=.5)]
    for bad in bads:
        try:verify(bad)
        except ValueError:continue
        raise AssertionError('False acceptance')
    assert verify(o,'46/100')['strictly_beats_supplied_scalar']
    assert not verify(o,'47/100')['strictly_beats_supplied_scalar']
    assert radical_sign(F(2),F(-1))>0 and radical_sign(F(1),F(-1))<0
    return dict(passed=True,controls=10)


if __name__=='__main__':print(json.dumps(selftest() if sys.argv[1:]==['--selftest'] else verify(json.load(open(sys.argv[1])),sys.argv[2] if len(sys.argv)>2 else None),indent=2))
