"""Numerical free-orientation triangle packing with analytic active-axis gradients."""
import argparse
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import json,time,math
from polygon_verify import verify

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'candidates/wave2_polygon'
DATA=HERE/'source/polygon_n12_m3_l4.txt'


def geometry(z,n):
    a=z[:-1].reshape(n,3);theta=a[:,2,None]+2*np.pi/3*np.arange(3)
    v=np.stack([np.cos(theta),np.sin(theta)],axis=2)
    return a,v,a[:,:2,None].transpose(0,2,1)+v


def evaluate(z,n,derivative=False):
    a,v,points=geometry(z,n);i,j=np.triu_indices(n,1);m=len(i)
    angles=np.c_[a[i,2,None]+np.pi/3+2*np.pi/3*np.arange(3),a[j,2,None]+np.pi/3+2*np.pi/3*np.arange(3)]
    axes=np.stack([np.cos(angles),np.sin(angles)],axis=2)
    pi=np.einsum('mak,mvk->mav',axes,points[i]);pj=np.einsum('mak,mvk->mav',axes,points[j])
    forward=pj.min(axis=2)-pi.max(axis=2);backward=pi.min(axis=2)-pj.max(axis=2)
    gaps=np.stack([forward,backward],axis=2);choice=np.argmax(gaps.reshape(m,12),axis=1);axis=choice//2;rev=choice%2;k=np.arange(m)
    pair=gaps[k,axis,rev];bound=z[-1]-np.abs(points).max(axis=1).ravel()
    if not derivative:return np.r_[pair,bound]
    J=np.zeros((m+2*n,3*n+1));normal=axes[k,axis]*(1-2*rev[:,None]);
    projection_i=np.einsum('mk,mvk->mv',normal,points[i]);projection_j=np.einsum('mk,mvk->mv',normal,points[j])
    vi=projection_i.argmax(axis=1);vj=projection_j.argmin(axis=1);diff=points[j,vj]-points[i,vi]
    for dim in (0,1):J[k,3*i+dim]=-normal[:,dim];J[k,3*j+dim]=normal[:,dim]
    rot_i=np.c_[-v[i,vi,1],v[i,vi,0]];rot_j=np.c_[-v[j,vj,1],v[j,vj,0]]
    J[k,3*i+2]=-np.sum(normal*rot_i,axis=1);J[k,3*j+2]=np.sum(normal*rot_j,axis=1)
    owner=np.where(axis<3,i,j);rot_n=np.c_[-normal[:,1],normal[:,0]];J[k,3*owner+2]+=np.sum(rot_n*diff,axis=1)
    for dim in (0,1):
        idx=np.argmax(np.abs(points[:,:,dim]),axis=1);sgn=np.sign(points[np.arange(n),idx,dim]);row=m+2*np.arange(n)+dim
        J[row,3*np.arange(n)+dim]=-sgn;J[row,3*np.arange(n)+2]=-sgn*(np.c_[-v[np.arange(n),idx,1],v[np.arange(n),idx,0]])[:,dim];J[row,-1]=1
    return J


def solve(a,h):
    n=len(a);z=np.r_[a.ravel(),h];g=np.zeros(len(z));g[-1]=1
    r=minimize(lambda z:z[-1],z,jac=lambda z:g,constraints={'type':'ineq','fun':lambda z:evaluate(z,n),'jac':lambda z:evaluate(z,n,True)},bounds=[(-4,4),(-4,4),(-20,20)]*n+[(1,4)],method='SLSQP',options={'maxiter':300,'ftol':1e-11})
    return r.x[:-1].reshape(n,3),r.x[-1],dict(nit=int(r.nit),success=bool(r.success),gap=float(evaluate(r.x,n).min()))


def certify(a,h,name):
    for scale in (1+1e-9,1+1e-8,1+1e-7,1+1e-6):
        b=a.copy();b[:,:2]*=scale
        hh=h*scale+(scale-1)*2
        o=dict(problem='equilateral_triangles_square',n=len(a),half_side=f'{hh:.14f}',triangles=[[f'{x:.14f}',f'{y:.14f}',f'{math.tan(theta/2):.14f}'] for x,y,theta in b],benchmark_R_squared_lower='982209829000000/100000000000000')
        # benchmark lower deliberately coarse 9.82209829; source R² is larger.
        try:result=verify(o)
        except ValueError:continue
        path=OUT/f'{name}.json';path.write_text(json.dumps(o,indent=2)+'\n');return result,str(path.relative_to(HERE.parents[3]))
    return None,None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=360);ap.add_argument('--seed',type=int,default=42000);args=ap.parse_args()
    lines=DATA.read_text().splitlines();R=float(lines[1]);a=np.loadtxt(lines[2:]);a[:,2]=np.pi/2-a[:,2];h=R/math.sqrt(2)
    z=np.r_[a.ravel(),h];assert evaluate(z,12).min()>-1e-6
    # Independent finite difference gradient check off branch boundaries.
    rng=np.random.default_rng(args.seed);q=z+rng.normal(0,.001,len(z));eps=1e-7
    num=np.column_stack([(evaluate(q+eps*np.eye(len(q))[k],12)-evaluate(q-eps*np.eye(len(q))[k],12))/(2*eps) for k in range(len(q))])
    error=float(np.max(abs(num-evaluate(q,12,True))));assert error<1e-5,error
    OUT.mkdir(exist_ok=True,parents=True);v,p=certify(a,h,'baseline12');pool=[(a,h)];best=h;start=time.monotonic();jobs=0;stale=0
    log=open(HERE/'polygon_experiments.jsonl','a',buffering=1);print(json.dumps(dict(baseline_R=R,baseline_h=h,gradient_error=error,certificate=v)),flush=True)
    while time.monotonic()-start<args.seconds:
        b,hh=pool[int(rng.integers(len(pool)))];b=b.copy();method=jobs%4
        if method==0:
            ids=rng.choice(12,int(rng.integers(1,5)),replace=False);b[ids,2]+=np.pi/3
        elif method==1:
            center=rng.uniform(-hh,hh,2);ids=np.argsort(np.linalg.norm(b[:,:2]-center,axis=1))[:int(rng.integers(2,5))];b[ids,:2]=rng.uniform(-hh+.8,hh-.8,(len(ids),2));b[ids,2]+=rng.uniform(-np.pi/3,np.pi/3,len(ids))
        elif method==2:b[:,2]+=rng.normal(0,.16,12);b[:,:2]+=rng.normal(0,.15,(12,2))
        else:
            b[:,:2]+=rng.normal(0,.5,(12,2));b[:,2]+=rng.normal(0,.5,12)
        t=time.monotonic();c,ch,info=solve(b,hh*1.08);v,p=certify(c,ch,f'job{jobs:04d}') if info['gap']>-1e-7 else (None,None)
        improved=bool(v and float(v['half_side'])<best-1e-7) if v and '/' not in v['half_side'] else bool(v and ch<best-1e-7)
        if improved:best=ch;pool.insert(0,(c,ch));pool=pool[:8];stale=0
        else:stale+=1
        if v and ch<h+.005 and len(pool)<8:pool.append((c,ch))
        row=dict(kind='experiment',job=jobs,seed=args.seed,method=method,h=float(ch),R=float(ch*math.sqrt(2)),baseline_R=R,wall_seconds=time.monotonic()-t,certificate=p,exact=v,improved=improved,**info);log.write(json.dumps(row)+'\n')
        if improved or jobs%10==0:print(json.dumps({k:row[k] for k in ('job','method','R','improved','gap')}),flush=True)
        jobs+=1
        if stale>=80:pool=[pool[0]];stale=0
    (HERE/'polygon_summary.json').write_text(json.dumps(dict(jobs=jobs,best_R=best*math.sqrt(2),baseline_R=R,wall_seconds=time.monotonic()-start),indent=2)+'\n')


if __name__=='__main__':main()
