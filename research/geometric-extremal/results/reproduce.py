#!/usr/bin/env python3
"""Exact replay of the two new few-distance witnesses; Python stdlib only.

This is a witness proof, not an optimality or novelty oracle. All coordinates
are integers in the basis (1,0),(1/2,sqrt(3)/2). Discovery code is never loaded.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import hashlib, json, importlib.util
BASE=Path(__file__).resolve().parents[1]

def load(name, file):
    spec=importlib.util.spec_from_file_location(name,file)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def check(record):
    path=BASE/record['candidate']
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==record['sha256'], 'candidate hash'
    spec=json.loads(raw);p=spec['points']
    assert all(type(a) is int and type(b) is int for a,b in p)
    assert len(p)==record['n'] and len(set(map(tuple,p)))==len(p)
    assert spec['metric']=='triangular' and spec['problem']=='few_distance'
    # Regenerate all lattice sites, with bounds entailed by the halfplanes.
    h=record['halfplanes']
    assert type(h) is list and len(h)==10
    assert all(type(v) is list and len(v)==3 and all(type(x) is int for x in v) for v in h)
    bounds={tuple(v[:2]):v[2] for v in h}
    assert len(bounds)==len(h), 'duplicate halfplane normal'
    amin,amax=-bounds[-1,0],bounds[1,0]
    bmax=bounds[0,1]
    bmin=min((-bounds[-1,-2]-a+1)//2 for a in range(amin,amax+1))
    rebuilt={(a,b) for a in range(amin,amax+1) for b in range(bmin,bmax+1)
             if all(u*a+v*b<=c for u,v,c in h)}
    assert rebuilt==set(map(tuple,p)), 'filled polygon equality'
    # Independent Cartesian computation: 4d²=(2Δa+Δb)²+3Δb².
    hist=Counter()
    for (a,b),(c,d) in combinations(p,2):
        X,Y=2*(a-c)+(b-d),b-d
        numerator=X*X+3*Y*Y
        assert numerator>0 and numerator%4==0
        hist[numerator//4]+=1
    assert len(hist)==record['k']
    assert sorted(hist)==record['squared_distances']
    assert {str(q):count for q,count in sorted(hist.items())}==record['multiplicities'], 'histogram metadata'
    assert sum(hist.values())==len(p)*(len(p)-1)//2
    for name,file in [('rational','verify.py'),('integer','independent_audit.py')]:
        result=load(name,BASE/'certification'/file).verify(spec)
        assert result['passed'] and result['distance_count']==record['k']
    assert record['n']>record['audited_published_lower_bound']
    return {'id':record['id'],'passed':True,'points':len(p),'distance_classes':len(hist),
            'pairs':sum(hist.values()),'histogram':dict(sorted(hist.items())),
            'sha256':record['sha256'],'scope':'exact existence lower bound; no optimality assertion'}

def main():
    data=json.loads((BASE/'results/records.json').read_text())
    reports=[check(r) for r in data['records']]
    print(json.dumps({'passed':True,'certificates':reports,'novelty_status':data['novelty_status']},indent=2))
if __name__=='__main__':main()
