"""Independent oriented-determinant epigraph search; witnesses rechecked exactly.

Run from repository root: .venv/bin/python research/geometric-extremal/search/area/discover.py
One compute worker. scipy SLSQP is a candidate generator, never a certificate.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse, datetime, hashlib, itertools, json, time, urllib.request, subprocess
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'candidates'/'area'
BASE={'triangle':(14,'0.023775773107572772515833024334'),
      'convex':(15,'0.0245640556132301679615750232227')}

def load_source(variant,n=None):
    if n is None:n=BASE[variant][0]
    url=f'https://math.tejstead.com/heilbronn/{variant}/{n}/points.json'
    p=HERE/f'source_{variant}{n}.json'
    if not p.exists():
        data=urllib.request.urlopen(url,timeout=30).read(); p.write_bytes(data)
        (HERE/f'source_{variant}{n}.provenance.json').write_text(json.dumps({'url':url,
            'sha256':hashlib.sha256(data).hexdigest(),'fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    return json.loads(p.read_text())

def hull_indices(points):
    # Exact monotone chain, intentionally independent of scipy's float hull.
    ordered=sorted(range(len(points)),key=lambda k:points[k])
    def cross(a,b,c):
        u,v,w=points[a],points[b],points[c]
        return (v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0])
    halves=[]
    for order in [ordered,ordered[::-1]]:
        q=[]
        for k in order:
            while len(q)>=2 and cross(q[-2],q[-1],k)<=0:q.pop()
            q.append(k)
        halves.append(q[:-1])
    return halves[0]+halves[1]

def exact_check(raw,variant):
    p=[tuple(F(str(t)) for t in row) for row in raw]; n=len(p)
    if len(set(p))!=n: raise ValueError('duplicate points')
    if variant=='triangle' and any(x<0 or y<0 or x+y>1 for x,y in p):raise ValueError('outside triangle')
    vals=[]
    for i,j,k in itertools.combinations(range(n),3):
        a,b,c=p[i],p[j],p[k]
        vals.append((abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])),(i,j,k)))
    md,triple=min(vals)
    if md<=0:raise ValueError('degenerate triangle')
    hull=hull_indices(p)
    hs=abs(sum(p[hull[i]][0]*p[hull[(i+1)%len(hull)]][1]-p[hull[i]][1]*p[hull[(i+1)%len(hull)]][0] for i in range(len(hull))))
    val=md if variant=='triangle' else md/hs
    return {'value_fraction':str(val),'value_decimal':format(float(val),'.17g'),'min_triple':triple,'hull_indices':hull}

class Eval:
    def __init__(self,p,variant):
        self.n=len(p);self.variant=variant;self.ix=np.array(list(itertools.combinations(range(self.n),3)))
        self.sign=np.sign(self.det(p)); self.sign[self.sign==0]=1
        self.cache=None
    def det(self,p):
        a,b,c=p[self.ix[:,0]],p[self.ix[:,1]],p[self.ix[:,2]]
        return (b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0])
    def calc(self,z):
        if self.cache is not None and np.array_equal(z,self.cache[0]):return self.cache[1:]
        p=z[:-1].reshape(self.n,2); t=z[-1]; a,b,c=p[self.ix[:,0]],p[self.ix[:,1]],p[self.ix[:,2]]
        d=self.sign*self.det(p); g=np.zeros((len(d),2*self.n+1))
        for vertex, dx,dy in [(0,b[:,1]-c[:,1],c[:,0]-b[:,0]),(1,c[:,1]-a[:,1],a[:,0]-c[:,0]),(2,a[:,1]-b[:,1],b[:,0]-a[:,0])]:
            g[np.arange(len(d)),2*self.ix[:,vertex]]=self.sign*dx
            g[np.arange(len(d)),2*self.ix[:,vertex]+1]=self.sign*dy
        if self.variant=='convex':
            h=ConvexHull(p).vertices; q=p[h]; area=np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))
            ag=np.zeros(2*self.n)
            ag[2*h]=np.roll(q[:,1],-1)-np.roll(q[:,1],1)
            ag[2*h+1]=np.roll(q[:,0],1)-np.roll(q[:,0],-1)
            g[:,:-1]=g[:,:-1]/area-d[:,None]*ag[None,:]/area**2
            d=d/area
        g[:,-1]=-1
        values=d-t
        if self.variant=='triangle':
            edge=1-p.sum(axis=1);eg=np.zeros((self.n,2*self.n+1))
            eg[np.arange(self.n),2*np.arange(self.n)]=-1;eg[np.arange(self.n),2*np.arange(self.n)+1]=-1
            values=np.r_[values,edge];g=np.vstack([g,eg])
        self.cache=(z.copy(),values,g)
        return values,g
    def score(self,p):
        d=np.min(abs(self.det(p)))
        return d if self.variant=='triangle' else d/(2*ConvexHull(p).volume)

def perturb(p,rng,variant,scale):
    q=p+rng.normal(0,scale,p.shape)
    if variant=='triangle':
        q=np.maximum(q,0);q=q/np.maximum(q.sum(axis=1,keepdims=True),1)
    else:
        q=q-q.mean(axis=0);q=q/max(np.linalg.norm(q,axis=1))
    return q

def run(variant,seed,maxiter,mode):
    source=load_source(variant);original=np.array(source['points'],float)
    sourcecheck=exact_check(source['points'],variant)
    rng=np.random.default_rng(seed);p=original.copy();anneal_seconds=0
    if mode=='neighbor':
        # Transfer via add/delete rather than another jitter-only search.
        if seed%2==0:p=np.delete(p,rng.integers(len(p)),axis=0)
        else:
            if variant=='triangle':
                bary=rng.dirichlet([1,1,1]);new=bary[:2]
            else:new=rng.normal(0,.25,2)
            p=np.vstack([p,new])
    elif mode=='transfer':
        # Delete every possible label over successive seeds from an n+1 source,
        # or insert in an n-1 incumbent's bottleneck neighbourhood.
        n=len(original); transfer_n=n+1 if seed%2==0 else n-1
        donor=load_source(variant,transfer_n);p=np.array(donor['points'],float)
        exact_check(donor['points'],variant)
        if transfer_n>n:p=np.delete(p,(seed//2)%len(p),axis=0)
        else:
            if variant=='triangle':new=rng.dirichlet([1,1,1])[:2]
            else:new=rng.uniform(-.65,.65,2)
            p=np.vstack([p,new])
    elif mode=='cellflip':
        # Cross an explicitly selected oriented-triple wall. This is a discrete
        # order-type operation, not stochastic jitter around a stationary point.
        flips=[]
        for i in range(len(p)):
            others=[j for j in range(len(p)) if j!=i]
            for j,k in itertools.combinations(others,2):
                v=p[k]-p[j];proj=p[j]+v*np.dot(p[i]-p[j],v)/np.dot(v,v)
                distance=np.linalg.norm(p[i]-proj)
                flips.append((distance,i,j,k,proj))
        flips.sort(key=lambda x:x[0])
        rank=(seed-1120)%len(flips)
        distance,i,j,k,proj=flips[rank]
        p[i]=proj-.05*(p[i]-proj)
    elif mode=='anneal':
        if variant!='triangle':raise ValueError('annealer only supports triangle')
        sa_start=time.perf_counter()
        stdin=str(len(p))+'\n'+'\n'.join(' '.join(map(str,row)) for row in p)+'\n'
        out=subprocess.check_output([str(HERE/'triangle_anneal'),str(seed),'200000'],input=stdin.encode())
        lines=out.decode().splitlines();p=np.array([[float(t) for t in line.split()] for line in lines[1:]])
        anneal_seconds=time.perf_counter()-sa_start
    elif mode=='crossdomain':
        if variant!='convex':raise ValueError('crossdomain disk transfer supports convex only')
        donor=json.loads((HERE/'source_disk15_convex.json').read_text())
        p=np.array([[float(F(t)) for t in row] for row in donor['points']])
    scale=[.003,.015,.05,.15][seed%4] if mode in ['local','crossdomain'] else .0005
    p=perturb(p,rng,variant,scale)
    ev=Eval(p,variant)
    if len(p)==len(original):baseline=ev.score(original)
    else:
        incumbent=load_source(variant,len(p));sourcecheck=exact_check(incumbent['points'],variant)
        baseline=float(F(sourcecheck['value_fraction']))
    z=np.r_[p.ravel(),ev.score(p)*.9]; initial=ev.score(p)
    bounds=[(0,1)]*(2*len(p))+[(1e-8,.5)] if variant=='triangle' else [(-3,3)]*(2*len(p))+[(1e-8,.5)]
    start=time.perf_counter()
    try:
        res=minimize(lambda x:-x[-1],z,jac=lambda x:np.r_[np.zeros(len(x)-1),-1.],method='SLSQP',bounds=bounds,
                     constraints=[{'type':'ineq','fun':lambda x:ev.calc(x)[0],'jac':lambda x:ev.calc(x)[1]}],
                     options={'maxiter':maxiter,'ftol':2e-12,'disp':False})
        q=res.x[:-1].reshape(-1,2)
        # Round then move triangle boundary literals inside by a controlled margin.
        if variant=='triangle':
            q=np.maximum(q,0);q=q/np.maximum(q.sum(axis=1,keepdims=True),1)
            q=(q+2e-13)/(1+8e-13)
        raw=[[format(float(t),'.14f') for t in row] for row in q]
        cert=exact_check(raw,variant)
        metric=float(F(cert['value_fraction']));status='valid_witness';message=str(res.message)
    except Exception as e:
        raw=None;cert=None;metric=None;status='failed';message=repr(e)
    record={'problem':'heilbronn_'+variant,'variant':variant,'n':len(p),'seed':seed,'method':mode+'-oriented-SLSQP','jitter':scale,
            'runtime_seconds':time.perf_counter()-start+anneal_seconds,'anneal_seconds':anneal_seconds,'initial_metric':initial,'baseline_metric':baseline,
            'candidate_metric':metric,'verification':status,'optimizer_message':message,
            'source_baseline_check':sourcecheck,'points':raw,'certificate':cert}
    out=OUT/f'{variant}{len(p)}_{mode}_{seed}.json';out.write_text(json.dumps(record,indent=2))
    with (HERE/'experiments.jsonl').open('a') as f:f.write(json.dumps({k:v for k,v in record.items() if k!='points'})+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['points','certificate','source_baseline_check']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',default='local');parser.add_argument('--maxiter',type=int,default=250)
    parser.add_argument('--start',type=int,default=1000);parser.add_argument('--stop',type=int,default=1020);a=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    for v in BASE:
        source=load_source(v)
        print('SOURCE',v,json.dumps(exact_check(source['points'],v)),flush=True)
    (HERE/f'preregister_{a.mode}_{a.start}.json').write_text(json.dumps({'seeds':list(range(a.start,a.stop)),
        'variants':list(BASE),'method':a.mode,'maxiter':a.maxiter,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    for seed in range(a.start,a.stop):
        variants=['triangle'] if a.mode=='anneal' else (['convex'] if a.mode=='crossdomain' else BASE)
        for v in variants:run(v,seed,a.maxiter,a.mode)
