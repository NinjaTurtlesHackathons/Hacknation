"""Rigid-contact cluster and neighbor-count search, separate prospective stage."""
import argparse,json,math,time
from fractions import Fraction as F
import numpy as np
from polygon_search import solve,evaluate,HERE
from polygon_verify import verify

OUT=HERE.parents[1]/'candidates/wave2_polygon_transfer'
FLOORS={10:'2.377',11:'2.490',12:'2.558',13:'2.595',14:'2.726'}


def load(n):
    s=(HERE/f'source/polygon_n{n}_m3_l4.txt').read_text().splitlines();R=float(s[1]);a=np.loadtxt(s[2:]);a[:,2]=np.pi/2-a[:,2]
    assert evaluate(np.r_[a.ravel(),R/math.sqrt(2)],n).min()>-1e-6
    return a,R/math.sqrt(2)


def certify(a,h,n,name):
    for extra in (1e-9,1e-8,1e-7,1e-6):
        scale=1+extra;b=a.copy();b[:,:2]*=scale;hh=h*scale+2*extra
        o=dict(problem='equilateral_triangles_square',n=n,half_side=f'{hh:.14f}',triangles=[[f'{x:.14f}',f'{y:.14f}',f'{math.tan(theta/2):.14f}'] for x,y,theta in b],benchmark_R_squared_lower=str(F(3,2)*F(FLOORS[n])**2),benchmark_note='Conservative current Friedman side/edge display floor; compare R squared = 3/2 times side/edge squared.')
        try:v=verify(o)
        except ValueError:continue
        p=OUT/f'{name}.json';p.write_text(json.dumps(o,indent=2)+'\n');return v,str(p.relative_to(HERE.parents[3]))
    return None,None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=360);ap.add_argument('--seed',type=int,default=43000);args=ap.parse_args()
    rng=np.random.default_rng(args.seed);OUT.mkdir(parents=True,exist_ok=True);pool={n:[load(n)] for n in range(10,16)};start=time.monotonic();jobs=0
    log=open(HERE/'polygon_transfer_experiments.jsonl','a',buffering=1);best={n:pool[n][0][1] for n in range(10,15)}
    # All deletions are exhaustive for the frozen neighbor seeds, not for geometry.
    tasks=[(n,'delete',i) for n in range(10,15) for i in range(n+1)]
    while time.monotonic()-start<args.seconds:
        if jobs<len(tasks):n,method,delete=tasks[jobs];b,hh=pool[n+1][0];b=np.delete(b,delete,axis=0)
        else:
            n=10+(jobs-len(tasks))%5;b,hh=pool[n][int(rng.integers(len(pool[n])))];b=b.copy();method=('cluster_rotate','cluster_reflect','insert')[jobs//5%3]
            if method=='insert':
                c,hh=pool[n-1][0] if n>10 else load(10);n=len(c)+1;b=np.vstack([c,np.r_[rng.uniform(-hh+.5,hh-.5,2),rng.uniform(-np.pi,np.pi)]])
            else:
                i=int(rng.integers(n));size=int(rng.integers(2,min(7,n)));ids=np.argsort(np.linalg.norm(b[:,:2]-b[i,:2],axis=1))[:size];center=b[ids,:2].mean(axis=0)
                if method=='cluster_rotate':
                    angle=float(rng.choice([math.pi/2,-math.pi/2,math.pi,math.pi/3,-math.pi/3]));rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
                    b[ids,:2]=(b[ids,:2]-center)@rot.T+center;b[ids,2]+=angle
                else:
                    dim=int(rng.integers(2));b[ids,dim]=2*center[dim]-b[ids,dim];b[ids,2]=(math.pi-b[ids,2]) if dim==0 else -b[ids,2]
        t=time.monotonic();a,h,info=solve(b,hh*1.03);v,p=certify(a,h,n,f'job{jobs:04d}_n{n}') if info['gap']>-1e-7 else (None,None)
        ch=float(F(v['half_side'])) if v else float('inf');better=bool(v and ch<best[n]-1e-8)
        if better:best[n]=ch;pool[n].insert(0,(a,h));pool[n]=pool[n][:6]
        elif v and ch<pool[n][0][1]+.002 and len(pool[n])<6:pool[n].append((a,h))
        row=dict(kind='experiment',job=jobs,n=n,seed=args.seed,method=method,wall_seconds=time.monotonic()-t,R=float(h*math.sqrt(2)),side_edge=float(h*2/math.sqrt(3)),improves_source_seed=better,certificate=p,exact=v,**info);log.write(json.dumps(row)+'\n')
        if better or jobs%10==0:print(json.dumps({k:row[k] for k in ('job','n','method','side_edge','improves_source_seed')}),flush=True)
        jobs+=1
    (HERE/'polygon_transfer_summary.json').write_text(json.dumps(dict(jobs=jobs,wall_seconds=time.monotonic()-start,best_halfside=best),indent=2)+'\n')


if __name__=='__main__':main()
