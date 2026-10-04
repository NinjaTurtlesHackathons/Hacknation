"""Prospectively registered radius/center contact surgery; numerical search only."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, linprog
from verify import verify

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'candidates/wave2_director'


def source(n):
    rows=[]
    for line in (HERE/f'source/csqv{n}.txt').read_text().splitlines():
        tok=line.split()
        if len(tok)==4 and tok[0].isdigit():rows.append([float(tok[1])+.5,float(tok[2])+.5,float(tok[3])])
    return np.array(rows)


def solve(c, maxiter=200):
    n=len(c); ii,jj=np.triu_indices(n,1); m=len(ii)
    objgrad=np.tile([0.,0.,-1.],n)
    def cons(z):
        a=z.reshape(n,3); xy=a[:,:2];r=a[:,2];d=xy[ii]-xy[jj]
        return np.r_[np.sum(d*d,axis=1)-(r[ii]+r[jj])**2,(xy-r[:,None]).ravel(),(1-xy-r[:,None]).ravel()]
    def jac(z):
        a=z.reshape(n,3);d=a[ii,:2]-a[jj,:2];rs=a[ii,2]+a[jj,2]
        J=np.zeros((m+4*n,3*n));k=np.arange(m)
        for dim in (0,1):J[k,3*ii+dim]=2*d[:,dim];J[k,3*jj+dim]=-2*d[:,dim]
        J[k,3*ii+2]=-2*rs;J[k,3*jj+2]=-2*rs
        for dim in (0,1):
            k=m+2*np.arange(n)+dim;J[k,3*np.arange(n)+dim]=1;J[k,3*np.arange(n)+2]=-1
            k=m+2*n+2*np.arange(n)+dim;J[k,3*np.arange(n)+dim]=-1;J[k,3*np.arange(n)+2]=-1
        return J
    result=minimize(lambda z:-z[2::3].sum(),c.ravel(),jac=lambda z:objgrad,bounds=[(0,1),(0,1),(1e-8,.5)]*n,constraints={'type':'ineq','fun':cons,'jac':jac},method='SLSQP',options={'maxiter':maxiter,'ftol':2e-11})
    return result.x.reshape(n,3),dict(nit=int(result.nit),success=bool(result.success),message=result.message,numerical_min_constraint=float(cons(result.x).min()))


def refill(c, count, rng):
    for _ in range(count):
        points=rng.uniform(0,1,(2500,2))
        wall=np.min(np.c_[points,1-points],axis=1)
        if len(c):wall=np.minimum(wall,np.min(np.linalg.norm(points[:,None]-c[None,:,:2],axis=2)-c[None,:,2],axis=1))
        i=int(np.argmax(wall));r=max(1e-7,wall[i]*.98)
        c=np.vstack([c,np.r_[points[i],r]])
    return c


def surgery(c, rng, mode):
    n=len(c)
    if mode=='cavity':
        k=int(rng.integers(2,7));center=rng.uniform(.05,.95,2)
        remove=np.argsort(np.linalg.norm(c[:,:2]-center,axis=1))[:k]
        return refill(np.delete(c,remove,axis=0),k,rng)
    if mode=='boundary':
        k=int(rng.integers(2,6));side=int(rng.integers(4));center=rng.random()
        distance=np.abs(c[:,side%2]-center)+2*(c[:,(side+1)%2] if side<2 else 1-c[:,(side+1)%2])
        return refill(np.delete(c,np.argsort(distance)[:k],axis=0),k,rng)
    if mode=='mixed':
        k=int(rng.integers(1,5));p=1/(c[:,2]+.03);p/=p.sum()
        return refill(np.delete(c,rng.choice(n,k,replace=False,p=p),axis=0),k,rng)
    a=c.copy();a[:,:2]=np.clip(a[:,:2]+rng.normal(0,.025,(n,2)),0,1);a[:,2]*=.8
    return a


def certificate(c,n,comparison,name):
    # Deliberate 1e-9 radius safety loss; exact checker is the sole acceptance gate.
    for margin in (1e-9,1e-8,1e-7,1e-6):
        circles=[[f'{x:.14f}',f'{y:.14f}',f'{max(0,r-margin):.14f}'] for x,y,r in c]
        obj=dict(problem='sum_radii_square',n=n,circles=circles,comparison=f'{comparison:.12f}',note='Comparison is frozen source coordinate sum; current record and queue audit separate.')
        try:v=verify(obj)
        except ValueError:continue
        p=OUT/f'{name}.json';p.write_text(json.dumps(obj,indent=2)+'\n');return str(p.relative_to(HERE.parents[3])),v
    return None, None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=360);ap.add_argument('--seed',type=int,default=41000);ap.add_argument('--max-jobs',type=int,default=2000);args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);start=time.monotonic();rng=np.random.default_rng(args.seed)
    ns=list(range(26,41));pool={n:[source(n)] for n in ns};baseline={n:pool[n][0][:,2].sum() for n in ns};best=baseline.copy();jobs=0;stale=0
    log=open(HERE/'experiments.jsonl','a',buffering=1)
    for n in ns:
        p,v=certificate(pool[n][0],n,baseline[n],f'baseline{n}')
        print(json.dumps(dict(kind='baseline',n=n,sum=baseline[n],exact=v)),flush=True)
    while jobs<args.max_jobs and time.monotonic()-start<args.seconds:
        n=ns[jobs%len(ns)];mode=('cavity','boundary','mixed','shake')[jobs//len(ns)%4]
        if jobs%11==0 and n+1 in pool:
            src=pool[n+1][int(rng.integers(len(pool[n+1])))];ids=np.argsort(src[:,2]);c=np.delete(src,int(rng.choice(ids[:8])),axis=0);method='neighbor_delete'
        elif jobs%13==0 and n-1 in pool:
            c=refill(pool[n-1][int(rng.integers(len(pool[n-1])))].copy(),1,rng);method='neighbor_insert'
        else:c=surgery(pool[n][int(rng.integers(len(pool[n])))],rng,mode);method=mode
        t=time.monotonic();a,info=solve(c);value=a[:,2].sum();feasible=info['numerical_min_constraint']>=-1e-7
        p,v=certificate(a,n,baseline[n],f'job{jobs:05d}_n{n}') if feasible else (None,None)
        improved=bool(v is not None and v['approximate']>best[n]+1e-8)
        if improved:
            best[n]=v['approximate'];pool[n].insert(0,a);pool[n]=pool[n][:5];stale=0
        else:stale+=1
        if feasible and len(pool[n])<5 and value>baseline[n]-.008:pool[n].append(a)
        row=dict(kind='experiment',job=jobs,seed=args.seed,n=n,method=method,wall_seconds=time.monotonic()-t,baseline=baseline[n],value=float(value),certificate=p,exact=v,improved=improved,**info)
        log.write(json.dumps(row)+'\n')
        if improved or jobs%15==0:print(json.dumps(dict(job=jobs,n=n,method=method,value=value,best=best[n],gap=best[n]-baseline[n],stale=stale)),flush=True)
        jobs+=1
        if stale>=100:
            # Adaptive reset: switch between elite-source and nearest-count basins,
            # changing cavity scale via the registered distinct mutation modes.
            ns=ns[::-1];stale=0
    summary=dict(jobs=jobs,seed=args.seed,wall_seconds=time.monotonic()-start,baseline=baseline,best=best,completed=True)
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
