#!/usr/bin/env python3
"""Independent common-denominator integer checker. No search/generic imports.
Exact Cartesian determinants, gift-wrapped hull, explicit nine torus translates.
"""
import json,math,sys
from pathlib import Path
from fractions import Fraction
from itertools import combinations

def number(v):
    if type(v) is int:return Fraction(v)
    if type(v) is str and len(v)<=500:return Fraction(v)
    raise ValueError('exact integer/rational input required')
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def dist2(a,b):return (a[0]-b[0])**2+(a[1]-b[1])**2
def gift_hull(p):
    start=min(p); cur=start; h=[]
    while True:
        h.append(cur); nxt=next(x for x in p if x!=cur)
        for x in p:
            z=cross(cur,nxt,x)
            if z<0 or (z==0 and dist2(cur,x)>dist2(cur,nxt)):nxt=x
        cur=nxt
        if cur==start:break
        if len(h)>len(p):raise ValueError('hull cycle')
    return h

def verify(s):
    try:
        if type(s) is not dict:raise ValueError('object required')
        if any(x in s for x in ['tolerance','toleranz','epsilon','precision']):raise ValueError('tolerance forbidden')
        kind=s['problem']
        if type(kind) is not str:raise ValueError('problem string required')
        scale=s.get('scale',1)
        if type(scale) is not int or scale<=0:raise ValueError('positive integer scale required')
        raw=s['points']
        if type(raw) is not list or not 2<=len(raw)<=500:raise ValueError('2..500 points required')
        if any(type(x) not in (list,tuple) or len(x)!=2 for x in raw):raise ValueError('2 coordinates required')
        rp=[(number(x)/scale,number(y)/scale) for x,y in raw]
        if len(set(rp))!=len(rp):raise ValueError('duplicate')
        L=math.lcm(*(v.denominator for p in rp for v in p));p=[(int(x*L),int(y*L)) for x,y in rp]
        n=len(p);out={'passed':True,'problem':kind,'n':n,'integer_denominator':str(L)}
        if kind=='few_distance':
            metric=s.get('metric','euclidean')
            if metric not in ('triangular','euclidean'):raise ValueError('metric')
            # Triangular Cartesian embedding X=(2a+b)/2,Y=sqrt(3)b/2.
            numer=[(2*(a[0]-b[0])+a[1]-b[1])**2+3*(a[1]-b[1])**2 if metric=='triangular' else 4*dist2(a,b) for a,b in combinations(p,2)]
            ds=sorted(set(Fraction(d,4*L*L) for d in numer));k=s.get('max_distances',len(ds))
            if type(k) is not int or k<1 or len(ds)>k:raise ValueError('distance count')
            out.update(distance_count=len(ds),squared_distances=[str(d) for d in ds])
        elif kind=='torus_distance':
            if any(x<0 or x>=L or y<0 or y>=L for x,y in p):raise ValueError('fundamental region')
            # Include shortest self-translate L and all neighboring image cells.
            D=min([L*L]+[(a[0]-b[0]+u*L)**2+(a[1]-b[1]+v*L)**2 for a,b in combinations(p,2) for u in [-1,0,1] for v in [-1,0,1]])
            value=Fraction(D,L*L);t=value+Fraction(8,25*n*n);excess=3*n*n*t*t-4
            applicable=n>=6
            out.update(value=str(value),markov_counterexample=applicable and excess>0,markov_threshold_squared_excess=str(excess),markov_conjecture_applicable=applicable)
            if s.get('claim_counterexample') is True and (not applicable or excess<=0):raise ValueError('counterexample assertion false or outside N>=6 scope')
        elif kind.startswith('heilbronn_'):
            if n<3:raise ValueError('three points required')
            region=kind[len('heilbronn_'):];denominator=2*L*L
            if region=='square':
                if any(x<0 or x>L or y<0 or y>L for x,y in p):raise ValueError('square')
            elif region=='disk':
                if any(x*x+y*y>L*L for x,y in p):raise ValueError('disk')
            elif region=='triangle':
                if any(x<0 or y<0 or x+y>L for x,y in p):raise ValueError('reference triangle')
                denominator=L*L
            elif region=='convex':
                h=gift_hull(p);denominator=abs(sum(x*v-y*u for (x,y),(u,v) in zip(h,h[1:]+h[:1])))
                if denominator==0:raise ValueError('degenerate hull')
                out.update(hull_area=str(Fraction(denominator,2*L*L)),hull_vertices=len(h))
            else:raise ValueError('region')
            A=min(abs(cross(a,b,c)) for a,b,c in combinations(p,3))
            if A==0:raise ValueError('collinear')
            value=Fraction(A,denominator);out['value']=str(value)
        elif kind=='circle_packing_triangle':
            radius=number(s['radius'])
            if radius<=0:raise ValueError('radius')
            for x,y in rp:
                if x<radius or y<radius or 1-x-y<0 or (1-x-y)**2<2*radius**2:raise ValueError('boundary')
            if any(dist2(a,b)<4*radius**2 for a,b in combinations(rp,2)):raise ValueError('overlap')
            out['radius']=str(radius)
        else:raise ValueError('unknown problem')
        if kind!='few_distance' and 'bound' in s and 'value' in out and Fraction(out['value'])<number(s['bound']):raise ValueError('bound assertion false')
        return out
    except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError) as e:return {'passed':False,'reason':str(e)}

def controls():
    sq={'problem':'heilbronn_square','points':[[0,0],[1,0],[1,1],[0,1]],'bound':'1/2'}
    tr={'problem':'heilbronn_triangle','points':[[0,0],[1,0],[0,1]],'bound':1}
    disk={'problem':'heilbronn_disk','points':[[1,0],[0,1],[-1,0],[0,-1]],'bound':1}
    convex={'problem':'heilbronn_convex','points':[[0,0],[2,0],[0,3]],'bound':1}
    tor={'problem':'torus_distance','points':[[0,0],['9/10',0]],'bound':'1/100'}
    few={'problem':'few_distance','metric':'triangular','points':[[0,0],[1,0],[0,1]],'max_distances':1}
    return [(sq,True),(tr,True),(disk,True),(convex,True),(tor,True),(few,True),({**few,'metric':'euclidean'},False),({**few,'max_distances':True},False),({**few,'metric':'garbage'},False),({**sq,'points':[[0,0],[1,0],[0,0]]},False),({**sq,'bound':'5000000000000000000001/10000000000000000000000'},False),({**disk,'points':[[1,0],[0,1],[-1,'1/10000000000000000']]},False),({**tr,'points':[[0,0],[1,0],['1/2','500000000000000001/1000000000000000000']]},False),({**tr,'points':[[0,0],[1,0],[1,1]]},False),({**tor,'points':[[0,0],[1,0]]},False),({**tor,'bound':'1/99'},False),({**tor,'claim_counterexample':True},False),({'problem':'torus_distance','points':[[0,0],['1/2','1/2']],'claim_counterexample':True},False),({**sq,'tolerance':1},False),({**sq,'points':[[0.0,0],[1,0],[0,1]]},False),({**sq,'problem':17},False),({**sq,'scale':True},False),({**sq,'points':[['1/0',0],[1,0],[0,1]]},False)]

def local_exclusion_dependencies():
    """Reconstruct n15 contact cycles and every quantitative proof dependency."""
    Q=Fraction; n=15;p=[(Q(k,n),Q((4*k)%n,n)) for k in range(n)]
    d2=min(min(dist2(a,(b[0]+u,b[1]+v)) for u in [-1,0,1] for v in [-1,0,1]) for a,b in combinations(p,2))
    vectors=[(Q(1,15),Q(4,15)),(Q(4,15),Q(1,15))];shifts=[]
    for step,z in zip([1,4],vectors):
        cycle=[(t*step)%n for t in range(n)]
        assert len(set(cycle))==n
        for i,j in zip(cycle,cycle[1:]+cycle[:1]):
            off=[z[c]-(p[j][c]-p[i][c]) for c in range(2)]
            assert all(x.denominator==1 for x in off)
            assert sum(x*x for x in z)==d2
            shifts.append({'i':i,'j':j,'step':step,'shift':list(map(int,off))})
    a,b=vectors[0];c,d=vectors[1];det=a*d-b*c
    inverse=[[d/det,-b/det],[-c/det,a/det]]
    assert all(sum(inverse[i][k]*vectors[k][j] for k in range(2))==(i==j) for i in range(2) for j in range(2))
    norm=max(sum(abs(x) for x in row) for row in inverse)
    edge=Q(2*(2**2),2);cycle=(n-1)*edge;path=(n-1)*cycle;constant=norm*path
    assert d2==Q(17,225) and constant==3920
    return {'passed':True,'scope':'fixed unit square torus, labelled lifts, u0=0','baseline_d2':str(d2),'contact_edges':shifts,'inverse':[[str(x) for x in row] for row in inverse],'edge_bound':str(edge),'cycle_bound':str(cycle),'path_bound':str(path),'inverse_norm':str(norm),'displacement_constant':str(constant),'strict_epsilon_radius':str(1/constant),'proof_dependency':'feasibility of every periodic image; cyclic projections telescope; epsilon<=constant*epsilon^2','novelty':'not asserted'}

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--tree':
        import hashlib,time
        from collections import Counter
        root=Path(sys.argv[2]);t=time.monotonic();rows=[];counts=Counter();skipped=0
        for path in sorted(root.rglob('*.json')):
            try: raw=path.read_bytes();spec=json.loads(raw)
            except (ValueError,OSError):skipped+=1;continue
            if not isinstance(spec,dict) or 'points' not in spec or 'problem' not in spec:skipped+=1;continue
            result=verify(spec);counts[spec['problem']]+=1
            rows.append({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'independent':result})
        print(json.dumps({'recognized':len(rows),'counts':dict(counts),'skipped':skipped,'elapsed_seconds':time.monotonic()-t,'rows':rows}))
        sys.exit(0 if rows and all(r['independent']['passed'] for r in rows) else 1)
    if sys.argv[1:]==['--local-proof']:
        print(json.dumps(local_exclusion_dependencies()));sys.exit(0)
    if sys.argv[1:]==['--selftest']:
        rows=[{'expected':w,'result':verify(s)} for s,w in controls()];ok=all(r['expected']==r['result']['passed'] for r in rows)
        print(json.dumps({'passed':ok,'tests':len(rows),'rows':rows}));sys.exit(not ok)
    results=[]
    for filename in sys.argv[1:]:
        try: result=verify(json.loads(Path(filename).read_text()))
        except (OSError,ValueError) as e:result={'passed':False,'reason':str(e)}
        results.append(result);print(json.dumps({'file':filename,**result}))
    sys.exit(0 if results and all(r['passed'] for r in results) else 1)
