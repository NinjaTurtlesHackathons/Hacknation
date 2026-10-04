#!/usr/bin/env python3
"""Large discrete geometry programs + active-triple LP continuation.

This wave is deliberately different from the first-wave fixed-cell SLSQP.
Mutations reflect entire contact-linked blocks across critical triple lines,
or splice an elite point block. LP polishing uses an explicit constraint
generation loop, trust-region adaptation, and true-score backtracking.
Float calculations generate candidates. Acceptance is exact and independent.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse, datetime, hashlib, importlib.util, itertools, json, time, urllib.request
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'candidates'/'wave2_area'
TARGETS=[('convex',18),('convex',20),('convex',23),('convex',25),('convex',31),('convex',33),
         ('triangle',20),('triangle',29),('square',21),('square',23),('square',25),('square',35)]
SPEC=importlib.util.spec_from_file_location('independent_verifier',ROOT/'certification'/'verify.py')
VERIFIER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(VERIFIER)

def fetch(kind,n):
    path=HERE/f'source_{kind}{n}.json';url=f'https://math.tejstead.com/heilbronn/{kind}/{n}/points.json'
    if not path.exists():
        data=urllib.request.urlopen(url,timeout=45).read();path.write_bytes(data)
        (HERE/f'source_{kind}{n}.provenance.json').write_text(json.dumps({'url':url,
          'sha256':hashlib.sha256(data).hexdigest(),'fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    data=json.loads(path.read_text());payload={'problem':'heilbronn_'+kind,'points':data['points']}
    cert=VERIFIER.verify(payload)
    if not cert['passed']:raise ValueError((kind,n,cert))
    return np.array(data['points'],float),cert

class Geometry:
    def __init__(self,kind,n):
        self.kind=kind;self.n=n;self.ix=np.array(list(itertools.combinations(range(n),3)))
    def determinant(self,p):
        a,b,c=p[self.ix[:,0]],p[self.ix[:,1]],p[self.ix[:,2]]
        return (b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0])
    def values(self,p):
        d=abs(self.determinant(p))
        if self.kind=='square':return d/2
        if self.kind=='triangle':return d
        return d/(2*ConvexHull(p).volume)
    def gradient(self,p):
        a,b,c=p[self.ix[:,0]],p[self.ix[:,1]],p[self.ix[:,2]];signed=self.determinant(p)
        sign=np.sign(signed);sign[sign==0]=1;d=sign*signed
        g=np.zeros((len(d),2*self.n));rows=np.arange(len(d))
        for k,dx,dy in [(0,b[:,1]-c[:,1],c[:,0]-b[:,0]),(1,c[:,1]-a[:,1],a[:,0]-c[:,0]),(2,a[:,1]-b[:,1],b[:,0]-a[:,0])]:
            g[rows,2*self.ix[:,k]]=sign*dx;g[rows,2*self.ix[:,k]+1]=sign*dy
        if self.kind=='square':return d/2,g/2
        if self.kind=='triangle':return d,g
        h=ConvexHull(p).vertices;q=p[h];twice=sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1));hg=np.zeros(2*self.n)
        hg[2*h]=np.roll(q[:,1],-1)-np.roll(q[:,1],1);hg[2*h+1]=np.roll(q[:,0],1)-np.roll(q[:,0],-1)
        return d/twice,g/twice-d[:,None]*hg[None,:]/twice**2
    def normalize(self,p):
        p=p.copy()
        if self.kind in ('triangle','square'):
            p=np.clip(p,0,1)
            if self.kind=='triangle':p/=np.maximum(p.sum(axis=1,keepdims=True),1)
        else:
            p-=p.mean(axis=0);p/=max(np.linalg.norm(p,axis=1))
        return p
    def score(self,p):return float(min(self.values(p)))
    def fit(self,p):
        # Affine container repair preserves all nonzero orientation signs;
        # clipping a macro mutation would create bogus collinear triples.
        if self.kind=='convex':return self.normalize(p)
        p=p.copy();p-=p.min(axis=0)
        if self.kind=='square':p/=np.maximum(p.max(axis=0),1e-8)
        else:p/=max(p.sum(axis=1))
        return p

def axis_polish(p,geo,maxiter=65):
    """Each axis solve is a linear program, not a first-order approximation.

    Determinants are linear in all x's when y's are fixed (and conversely).
    For a free hull use a Charnes-Cooper axis normalization: its shoelace
    sum is fixed to1. Orientation constraints preserve the full hull order.
    Two zero anchors remove translation/shear gauges. This is conditional
    coordinate-slice optimization; no global geometric-optimality claim.
    """
    p=geo.normalize(p);trace=[];calls=0
    for it in range(maxiter):
        prior=geo.score(p)
        for axis in (0,1):
            other=1-axis; a,b,c=p[geo.ix[:,0]],p[geo.ix[:,1]],p[geo.ix[:,2]]
            signed=geo.determinant(p);sign=np.sign(signed);sign[sign==0]=1
            H=np.zeros((len(signed),geo.n));rows=np.arange(len(signed))
            if axis==0:derivatives=[b[:,1]-c[:,1],c[:,1]-a[:,1],a[:,1]-b[:,1]]
            else:derivatives=[c[:,0]-b[:,0],a[:,0]-c[:,0],b[:,0]-a[:,0]]
            for k,derivative in enumerate(derivatives):H[rows,geo.ix[:,k]]=sign*derivative
            if geo.kind=='square':H/=2
            A=np.column_stack([-H,np.ones(len(H))]);target=np.r_[np.zeros(geo.n),-1.]
            if geo.kind=='convex':
                h=ConvexHull(p).vertices;q=p[h];area=2*ConvexHull(p).volume
                normal=np.zeros(geo.n)
                if axis==0:normal[h]=np.roll(q[:,1],-1)-np.roll(q[:,1],1)
                else:normal[h]=np.roll(q[:,0],1)-np.roll(q[:,0],-1)
                equal=[np.r_[normal,0.]];rhs=[1.]
                anchor=int(np.argmax(abs(p[:,other]-p[0,other])))
                for j in (0,anchor):
                    row=np.zeros(geo.n+1);row[j]=1;equal.append(row);rhs.append(0.)
                # The bound is a numerical chart guard, not an asserted
                # restriction on the unrestricted geometric problem.
                bounds=[(-30,30)]*geo.n+[(0,None)]
                sol=linprog(target,A_ub=A,b_ub=np.zeros(len(A)),A_eq=np.array(equal),b_eq=np.array(rhs),bounds=bounds,method='highs')
            else:
                bounds=[(0,max(0.,1-float(p[i,other])) if geo.kind=='triangle' else 1.) for i in range(geo.n)]+[(0,None)]
                sol=linprog(target,A_ub=A,b_ub=np.zeros(len(A)),bounds=bounds,method='highs')
            calls+=1
            if sol.success:
                q=p.copy();q[:,axis]=sol.x[:-1];q=geo.normalize(q);actual=geo.score(q)
                if actual>=geo.score(p)-1e-11:p=q
        after=geo.score(p);trace.append(after)
        if after<=prior+max(1e-12,prior*1e-8):break
    return p,{'lp_calls':calls,'axis_cycles':len(trace),'objective_trace':trace,'linear_slices':'exact determinant/hull linear programs; numerical solver output requires rational verifier'}

def polish(p,geo,maxiter=65,release=0):
    p=geo.normalize(p);rho=.045;history=[];lp_calls=0
    for it in range(maxiter):
        d,g=geo.gradient(p);current=float(min(d));order=np.argsort(d)
        active=set(order[:min(len(d),max(3*geo.n,48))].tolist())
        if release and it<4:
            # Temporarily release a small active-contact face, then restore full
            # objective on later steps; the result still faces exact acceptance.
            active.difference_update(order[:release].tolist())
        objective=np.r_[np.zeros(2*geo.n),-1.]
        if geo.kind in ('triangle','square'):
            bounds=[(max(-rho,-float(x)),min(rho,1-float(x))) for x in p.ravel()]+[(0,None)]
        else:bounds=[(-rho,rho)]*(2*geo.n)+[(0,None)]
        sol=None
        for generation in range(6):
            ids=np.array(sorted(active),int);A=np.column_stack([-g[ids],np.ones(len(ids))]);b=d[ids]
            if geo.kind=='triangle':
                edge=np.zeros((geo.n,2*geo.n+1));edge[np.arange(geo.n),2*np.arange(geo.n)]=1;edge[np.arange(geo.n),2*np.arange(geo.n)+1]=1
                A=np.vstack([A,edge]);b=np.r_[b,1-p.sum(axis=1)]
            sol=linprog(objective,A_ub=A,b_ub=b,bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
            lp_calls+=1
            if not sol.success:break
            step=sol.x[:-1];predicted=d+g@step
            violated=np.flatnonzero(predicted<sol.x[-1]-1e-9)
            if release and it<4:violated=violated[~np.isin(violated,order[:release])]
            if not len(violated):break
            active.update(violated.tolist())
        if sol is None or not sol.success:
            rho*=.35
            if rho<1e-8:break
            continue
        delta=sol.x[:-1].reshape(-1,2)
        best=None
        for factor in [1,.5,.25,.125,.0625,.03125,.015625]:
            q=geo.normalize(p+factor*delta);score=geo.score(q)
            if release and it<4:
                # A controlled larger active-face escape, not a claim of ascent.
                criterion=score>=max(current*.65,1e-8)
            else:criterion=score>current+max(1e-13,current*1e-10)
            if criterion:best=(q,score,factor);break
        if best:
            p,value,factor=best;rho=min(.10,rho*(1.15 if factor==1 else .85));history.append(value)
        else:
            rho*=.45
            if rho<2e-7:break
    return p,{'lp_calls':lp_calls,'accepted_steps':len(history),'final_trust_radius':rho,'objective_trace':history}

def program(p,geo,rng,mode,elite):
    p=p.copy();values=geo.values(p);near=np.argsort(values)[:max(3*geo.n,24)]
    if mode=='splice' and len(elite)>1:
        donor=elite[rng.integers(len(elite))]['points'];cluster=rng.choice(geo.n,size=rng.integers(2,max(3,geo.n//3)),replace=False)
        p[cluster]=donor[cluster];return geo.normalize(p),{'program':'elite_block_splice','block':cluster.tolist()}
    triple=geo.ix[int(rng.choice(near))];pivot=int(rng.integers(3));i=int(triple[pivot]);j,k=map(int,np.delete(triple,pivot))
    if mode=='permutation':
        axis=int(rng.integers(2));cluster=list(map(int,triple))
        extra=rng.choice(geo.n,size=int(rng.integers(0,4)),replace=False)
        cluster=list(dict.fromkeys(cluster+list(map(int,extra))))
        perm=rng.permutation(len(cluster));old=p[cluster,axis].copy();p[cluster,axis]=old[perm]
        before=np.sign(geo.determinant(elite[0]['points']));p=geo.fit(p);after=np.sign(geo.determinant(p))
        return p,{'program':'coordinate_order_type_permutation','axis':axis,'cluster':cluster,'permutation':perm.tolist(),
                  'orientation_changes_from_baseline':int(np.sum(before!=after))}
    axis=p[k]-p[j];denom=np.dot(axis,axis)
    if denom<1e-15:return p,{'program':'rejected_zero_axis'}
    cluster=[i]
    if mode in ('block','release'):
        # Contact-connected block: repeatedly add a vertex linked through one of
        # the baseline's current near-active triples, leaving axis labels fixed.
        target=int(rng.integers(2,min(8,geo.n-2)))
        edges=geo.ix[near]
        while len(cluster)<target:
            linked=set(int(x) for t in edges if any(int(x) in cluster for x in t) for x in t)-set(cluster)-{j,k}
            if not linked:break
            cluster.append(int(rng.choice(sorted(linked))))
    overshoot=float(rng.choice([1.0,1.2,1.6,2.2]))
    for label in cluster:
        proj=p[j]+axis*np.dot(p[label]-p[j],axis)/denom
        # Full reflection (factor1) preserves the selected triangle's absolute
        # area. Larger overshoots cross additional walls deliberately.
        p[label]=proj-overshoot*(p[label]-proj)
    before=np.sign(geo.determinant(elite[0]['points']));p=geo.fit(p);after=np.sign(geo.determinant(p))
    return p,{'program':'critical_line_reflection','axis':[j,k],'block':cluster,'overshoot':overshoot,'orientation_changes_from_baseline':int(np.sum(before!=after))}

def rationalize(p,geo):
    if geo.kind in ('square','triangle'):
        p=geo.normalize(p)
        p=(p+2e-14)/(1+(8e-14 if geo.kind=='triangle' else 4e-14))
    return [[format(float(x),'.15f') for x in row] for row in p]

def run(args):
    OUT.mkdir(parents=True,exist_ok=True)
    targets=TARGETS if args.target=='all' else [(args.target[:-2],int(args.target[-2:]))]
    registry=HERE/'experiments.jsonl';fresh={};pool={}
    for kind,n in targets:
        p,certificate=fetch(kind,n);geo=Geometry(kind,n);fresh[(kind,n)]=(p,certificate,geo)
        pool[(kind,n)]=[{'score':geo.score(p),'points':p,'program':'external_baseline'}]
        print('SOURCE',kind,n,certificate['value'],flush=True)
    prereg={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seeds':list(range(args.start,args.stop)),
            'targets':targets,'mode':args.mode,'max_lp_iterations':args.iterations,'exact_improvement_screen':5e-4,
            'workers':1,'adaptive_rule':'after a completed negative phase change block/reflection/release/splice method; retain elite diversity by rounded order signatures',
            'acceptance':'external independent stdlib verifier, no numeric tolerance; root independently certifies any improvement'}
    prereg['polisher']=args.polisher
    (HERE/f'preregister_{args.mode}_{args.polisher}_{args.start}.json').write_text(json.dumps(prereg,indent=2))
    for seed in range(args.start,args.stop):
        for kind,n in targets:
            rng=np.random.default_rng(seed*1009+n);original,base,geo=fresh[(kind,n)];elite=pool[(kind,n)]
            if len(elite)>1 and rng.random()<.7:parent=elite[int(rng.integers(len(elite)))]['points']
            else:parent=original
            start=time.perf_counter();mutant,description=program(parent,geo,rng,args.mode,elite)
            initial=geo.score(mutant)
            try:
                if args.polisher=='axis':candidate,stats=axis_polish(mutant,geo,args.iterations)
                else:candidate,stats=polish(mutant,geo,args.iterations,release=2 if args.mode=='release' else 0)
                raw=rationalize(candidate,geo);certificate=VERIFIER.verify({'problem':'heilbronn_'+kind,'points':raw})
                score=float(Q(certificate['value'])) if certificate['passed'] else None
                # Keep diversified high-ranking geometries, never accept the
                # optimizer's success flag as a mathematical conclusion.
                if score is not None:
                    signature=np.packbits(geo.determinant(candidate)>0).tobytes().hex()
                    if not any(e.get('signature')==signature for e in elite):
                        elite.append({'score':score,'points':candidate,'signature':signature,'program':description});elite[1:]=sorted(elite[1:],key=lambda x:x['score'],reverse=True)[:18]
                ratio=float(Q(certificate['value'])/Q(base['value'])) if score is not None else None
                message=None
            except Exception as e:
                raw=None;certificate={'passed':False,'reason':repr(e)};stats={};score=None;ratio=None;message=repr(e)
            record={'seed':seed,'kind':kind,'n':n,'method':args.mode+'_contact_program_'+args.polisher,'program':description,'initial':initial,
                    'score':score,'baseline':base['value'],'ratio_to_baseline':ratio,'certificate':certificate,
                    'lp_stats':stats,'runtime_seconds':time.perf_counter()-start,'error':message,'elite_count':len(elite)}
            with registry.open('a') as f:f.write(json.dumps(record)+'\n')
            path=OUT/f'{kind}{n}_{args.mode}_{seed}.json';path.write_text(json.dumps({'problem':'heilbronn_'+kind,'points':raw,**record},indent=2))
            if score is not None and ratio>1.0005:
                (HERE/'PROMISING.json').write_text(json.dumps({'candidate':str(path),'record':record},indent=2))
                print('PROMISING',str(path),ratio,flush=True)
            print(json.dumps({k:v for k,v in record.items() if k not in ('certificate','lp_stats','program')}),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--mode',choices=['reflection','block','release','splice','permutation'],default='reflection')
    a.add_argument('--polisher',choices=['slp','axis'],default='slp')
    a.add_argument('--start',type=int,default=3000);a.add_argument('--stop',type=int,default=3040);a.add_argument('--iterations',type=int,default=65)
    a.add_argument('--target',default='all');run(a.parse_args())
