#!/usr/bin/env python3
"""Integer-denominator independent certificate; no discovery/referee imports.
Record comparison requires explicit trusted threshold argument, not witness metadata.
"""
import json,sys,math
from pathlib import Path
from fractions import Fraction
from itertools import combinations

def rational(x):
    if type(x) is int:return Fraction(x)
    if type(x) is str and len(x)<=10000:return Fraction(x)
    raise ValueError('Exact rational input required')

def verify(obj,comparison=None):
    try:
        if type(obj) is not dict or obj.get('problem')!='sum_radii_square':raise ValueError('Problem object required')
        if any(k in obj for k in ['tolerance','epsilon','precision']):raise ValueError('Tolerances forbidden')
        n=obj['n'];raw=obj['circles']
        if type(n) is not int or not 1<=n<=20000:raise ValueError('Positive integer n required')
        if type(raw) is not list or len(raw)!=n or any(type(row) is not list or len(row)!=3 for row in raw):raise ValueError('Circle dimensions')
        q=[[rational(x) for x in row] for row in raw]
        L=math.lcm(*(v.denominator for row in q for v in row));c=[[int(v*L) for v in row] for row in q]
        for x,y,r in c:
            if r<=0 or x<r or y<r or x+r>L or y+r>L:raise ValueError('Radius or boundary')
        slack=None
        for (x,y,r),(xx,yy,rr) in combinations(c,2):
            d=(x-xx)**2+(y-yy)**2-(r+rr)**2
            if d<0:raise ValueError('Overlap')
            slack=d if slack is None else min(slack,d)
        value=Fraction(sum(row[2] for row in c),L)
        out={'passed':True,'n':n,'value':str(value),'integer_denominator':str(L),'pairs':n*(n-1)//2,'smallest_squared_pair_slack':str(Fraction(slack,L*L)) if slack is not None else None}
        if comparison is not None:
            threshold=rational(comparison);out.update(trusted_comparison=str(threshold),comparison_gap=str(value-threshold),improves_frozen_comparison=value>threshold)
        elif 'comparison' in obj:
            out.update(untrusted_witness_comparison=str(rational(obj['comparison'])),record_comparison_certified=False)
        return out
    except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError) as e:return {'passed':False,'reason':str(e)}

def selftest():
    good={'problem':'sum_radii_square','n':2,'circles':[['1/4','1/2','1/4'],['3/4','1/2','1/4']]}
    tests=[(good,True),({'problem':'sum_radii_square','n':1,'circles':[['1/2','1/2','1/2']]},True)]
    for key,value in [('problem',17),('n',True),('n',3),('n',0),('circles',None),('circles',[[0,0]]),('epsilon',0)]:tests.append(({**good,key:value},False))
    for row,col,value in [(1,0,'7/10'),(0,0,'1/5'),(0,2,'0'),(0,2,0.25),(0,2,True),(0,2,'1/0')]:
        bad=json.loads(json.dumps(good));bad['circles'][row][col]=value;tests.append((bad,False))
    result=[{'expected':want,'result':verify(obj)} for obj,want in tests]
    assert all(r['expected']==r['result']['passed'] for r in result)
    assert verify(good,'1/2')['improves_frozen_comparison'] is False
    assert verify(good,'499999999999999999/1000000000000000000')['improves_frozen_comparison'] is True
    assert verify({**good,'comparison':0})['record_comparison_certified'] is False
    return {'passed':True,'controls':len(tests)+3,'rows':result}

if __name__=='__main__':
    if sys.argv[1:]==['--selftest']:out=selftest()
    else:
        try:out=verify(json.loads(Path(sys.argv[1]).read_text()),sys.argv[2] if len(sys.argv)>2 else None)
        except (ValueError,OSError,IndexError) as e:out={'passed':False,'reason':str(e)}
    print(json.dumps(out,indent=2));sys.exit(0 if out['passed'] else 1)
