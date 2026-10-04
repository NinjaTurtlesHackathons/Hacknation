#!/usr/bin/env python3
"""Independent exact witness checker; stdlib only; no search imports.
Heilbronn square/disk: physical area. Triangle/convex: area/container area.
Torus: squared periodic separation. Few-distance: exact norm count.
Only integer/rational-string coordinates accepted; scale positive integer.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib,json,sys

def rat(x):
    if type(x) is int: return Q(x)
    if isinstance(x,str) and len(x)<=500: return Q(x)
    raise ValueError('integer or rational string required, floats/bools forbidden')

def det(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def hull(p):
    s=sorted(p); chains=[]
    for seq in (s,s[::-1]):
        h=[]
        for v in seq:
            while len(h)>=2 and det(h[-2],h[-1],v)<=0: h.pop()
            h.append(v)
        chains.append(h[:-1])
    return chains[0]+chains[1]

def verify(s):
    try:
        if not isinstance(s,dict): raise ValueError('object required')
        if any(k in s for k in ('tolerance','toleranz','epsilon','precision')): raise ValueError('agent tolerance forbidden')
        z=s.get('scale',1)
        if type(z) is not int or z<=0: raise ValueError('positive integer scale required')
        raw=s['points']
        if not isinstance(raw,list) or not 2<=len(raw)<=500: raise ValueError('expected 2..500 points')
        if any(not isinstance(v,(list,tuple)) or len(v)!=2 for v in raw): raise ValueError('two coordinates required')
        p=[tuple(rat(x)/z for x in v) for v in raw]
        if len(set(p))!=len(p): raise ValueError('duplicate points')
        kind=s['problem']
        if not isinstance(kind,str): raise ValueError('problem name must be string')
        out={'passed':True,'problem':kind,'n':len(p),'arithmetic':'exact rational'}
        if kind.startswith('heilbronn_'):
            if len(p)<3: raise ValueError('three points required')
            region=kind.removeprefix('heilbronn_'); norm=Q(1)
            if region=='square':
                if any(not(0<=x<=1 and 0<=y<=1) for x,y in p): raise ValueError('outside square')
            elif region=='disk':
                if any(x*x+y*y>1 for x,y in p): raise ValueError('outside radius-one disk')
            elif region=='triangle':
                if any(x<0 or y<0 or x+y>1 for x,y in p): raise ValueError('outside reference triangle')
                norm=Q(1,2)
            elif region=='convex':
                h=hull(p); norm=abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(h,h[1:]+h[:1])))/2
                if not norm: raise ValueError('degenerate hull')
                out.update(hull_area=str(norm),hull_vertices=len(h))
            else: raise ValueError('unknown region')
            a=[(abs(det(p[i],p[j],p[k]))/(2*norm),(i,j,k)) for i,j,k in combinations(range(len(p)),3)]
            value,triple=min(a)
            if value<=0: raise ValueError('collinear triple')
            out.update(value=str(value),approximate=float(value),critical_triple=list(triple),tested_triples=len(a),exact_ties=sum(v==value for v,_ in a),normalization='physical area' if region in ('square','disk') else 'area/container area')
            if 'bound' in s and value<rat(s['bound']): raise ValueError('claimed bound exceeds exact witness')
        elif kind=='torus_distance':
            if any(not(0<=x<1 and 0<=y<1) for x,y in p): raise ValueError('torus representatives outside [0,1)^2')
            ds=[]
            for i,j in combinations(range(len(p)),2):
                dx=abs(p[i][0]-p[j][0]); dy=abs(p[i][1]-p[j][1]); dx=min(dx,1-dx); dy=min(dy,1-dy)
                ds.append((dx*dx+dy*dy,(i,j)))
            value,pair=min(ds); value=min(value,Q(1))
            out.update(value=str(value),approximate=float(value),critical_pair=list(pair),tested_pairs=len(ds),normalization='squared periodic separation; radius=sqrt(value)/2')
            if 'bound' in s and value<rat(s['bound']): raise ValueError('claimed bound exceeds exact separation')
            # Markov M>25/4 iff d² + 8/(25n²)>2/(sqrt(3)n).
            # Both sides positive: squaring preserves equivalence, exact rational.
            t=value+Q(8,25*len(p)**2)
            excess=3*len(p)**2*t*t-4
            out.update(markov_conjecture_applicable=len(p)>=6,markov_counterexample=len(p)>=6 and excess>0,markov_threshold_squared_excess=str(excess))
            if s.get('claim_counterexample') is True and (len(p)<6 or excess<=0): raise ValueError('not a Markov conjecture counterexample')
        elif kind=='circle_packing_triangle':
            radius=rat(s['radius'])
            if radius<=0: raise ValueError('positive radius required')
            for x,y in p:
                gap=1-x-y
                if x<radius or y<radius or gap<0 or gap*gap<2*radius*radius: raise ValueError('disk leaves reference right triangle')
            pair_slacks=[((a[0]-b[0])**2+(a[1]-b[1])**2-4*radius*radius) for a,b in combinations(p,2)]
            if min(pair_slacks)<0: raise ValueError('overlapping disks')
            out.update(radius=str(radius),approximate=float(radius),min_pair_slack=str(min(pair_slacks)),tested_pairs=len(pair_slacks),normalization='circle radius; right triangle legs1')
        elif kind=='few_distance':
            metric=s.get('metric','euclidean')
            if metric not in ('euclidean','triangular'): raise ValueError('unknown metric')
            ds=set()
            for a,b in combinations(p,2):
                dx=a[0]-b[0]; dy=a[1]-b[1]; ds.add(dx*dx+dy*dy+(dx*dy if metric=='triangular' else 0))
            k=s.get('max_distances',len(ds))
            if type(k) is not int or k<1 or len(ds)>k: raise ValueError('too many distances / invalid count')
            out.update(distance_count=len(ds),squared_distances=[str(v) for v in sorted(ds)],tested_pairs=len(p)*(len(p)-1)//2,normalization=metric)
        else: raise ValueError('unknown problem')
        return out
    except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError) as e: return {'passed':False,'reason':str(e)}

def selftest():
    sq={'problem':'heilbronn_square','points':[[0,0],[1,0],[1,1],[0,1]],'bound':'1/2'}
    tr={'problem':'heilbronn_triangle','points':[[0,0],[1,0],[0,1]],'bound':'1'}
    di={'problem':'heilbronn_disk','points':[[1,0],[0,1],[-1,0],[0,-1]],'bound':'1'}
    return [(sq,True),(tr,True),(di,True),({**sq,'bound':'500000000000000000001/1000000000000000000000'},False),({**sq,'points':[[0,0],[1,0],[0,0]]},False),({**sq,'tolerance':1},False),({**di,'points':[[1,0],[0,1],[-1,'1/100000000000000000000']]},False),({**tr,'points':[[0,0],[1,0],['1/2','1/2']]},False),({**tr,'points':[[0,0],[1,0],['1/2','500000000000000000001/1000000000000000000000']]},False),({**sq,'points':[[0,0],['1/2','1/2'],[1,1]]},False),({**sq,'points':[[0.0,0],[1,0],[0,1]]},False),({'problem':'torus_distance','points':[[0,0],['9/10',0]],'bound':'1/100'},True),({'problem':'torus_distance','points':[[0,0],['9/10',0]],'bound':'1/99'},False),({'problem':'few_distance','metric':'triangular','points':[[0,0],[1,0],[0,1]],'max_distances':1},True),({'problem':'few_distance','points':[[0,0],[1,0],[0,1]],'max_distances':1},False),({'problem':'heilbronn_convex','points':[[0,0],[2,0],[0,3]],'bound':'1'},True),({'problem':'circle_packing_triangle','points':[['1/5','1/5'],['3/5','1/5']],'radius':'1/10'},True),({'problem':'circle_packing_triangle','points':[['1/5','1/5'],['3/5','1/5']],'radius':'1/5'},False),({'problem':'circle_packing_triangle','points':[['1/5','1/5'],['21/100','1/5']],'radius':'1/10'},False),({'problem':'torus_distance','points':[[0,0],['9/10',0]],'claim_counterexample':True},False),({'problem':17,'points':[[0,0],[1,0],[0,1]]},False),({'problem':'torus_distance','points':[[0,0],['1/2','1/2']],'claim_counterexample':True},False)]

if __name__=='__main__':
    if sys.argv[1:]==['--selftest']:
        rows=[{'expected':want,'result':verify(p)} for p,want in selftest()]; ok=all(r['expected']==r['result']['passed'] for r in rows)
        print(json.dumps({'passed':ok,'tests':rows},indent=2)); sys.exit(0 if ok else 1)
    ok=True
    for name in sys.argv[1:]:
        b=Path(name).read_bytes(); r=verify(json.loads(b)); r.update(file=name,sha256=hashlib.sha256(b).hexdigest()); print(json.dumps(r)); ok &= r['passed']
    sys.exit(0 if ok else 1)
