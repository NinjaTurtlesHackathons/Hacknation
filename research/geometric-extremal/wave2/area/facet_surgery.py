#!/usr/bin/env python3
"""Delete selected oriented-matroid facets in one exact axis LP then restore.
All assertions are candidate-generation only. External verifier checks output.
"""
import program_search as P
import argparse, datetime, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from fractions import Fraction as Q

def surgery(p,g,rng,force=False):
    axis=int(rng.integers(2));other=1-axis
    signed=g.determinant(p);sign=np.sign(signed);sign[sign==0]=1
    a,b,c=p[g.ix[:,0]],p[g.ix[:,1]],p[g.ix[:,2]]
    ds=[b[:,1]-c[:,1],c[:,1]-a[:,1],a[:,1]-b[:,1]] if axis==0 else [c[:,0]-b[:,0],a[:,0]-c[:,0],b[:,0]-a[:,0]]
    H=np.zeros((len(signed),g.n));rr=np.arange(len(signed))
    for k,d in enumerate(ds):H[rr,g.ix[:,k]]=sign*d
    if g.kind=='square':H/=2
    order=np.argsort(g.values(p));near=order[:max(2*g.n,12)]
    count=1 if force else int(rng.integers(1,6));released=rng.choice(near,count,replace=False)
    keep=np.ones(len(H),bool)
    if force:H[released]*=-1
    else:keep[released]=False
    A=np.column_stack([-H[keep],np.ones(sum(keep))]);cost=np.r_[np.zeros(g.n),-1.]
    eq=None;rhs=None
    if g.kind=='convex':
        hull=ConvexHull(p).vertices;v=p[hull];normal=np.zeros(g.n)
        normal[hull]=np.roll(v[:,other],-1)-np.roll(v[:,other],1)
        if axis==1:normal=-normal
        eq=[np.r_[normal,0.]];rhs=[1.]
        anchor=int(np.argmax(abs(p[:,other]-p[0,other])))
        for j in [0,anchor]:
            row=np.zeros(g.n+1);row[j]=1;eq.append(row);rhs.append(0.)
        bounds=[(-30,30)]*g.n+[(0,None)]
    else:bounds=[(0,max(0.,1-p[i,other]) if g.kind=='triangle' else 1.) for i in range(g.n)]+[(0,None)]
    sol=linprog(cost,A_ub=A,b_ub=np.zeros(len(A)),A_eq=eq,b_eq=rhs,bounds=bounds,method='highs')
    if not sol.success:return p,{'axis':axis,'released':released.tolist(),'lp_failed':sol.message}
    q=p.copy();q[:,axis]=sol.x[:-1]
    # Convex gauge of relaxed LP differs from source. First transform the
    # source to this gauge before blending; otherwise interpolation meaningless.
    base=p.copy()
    if g.kind=='convex':
        slope=(base[anchor,axis]-base[0,axis])/(base[anchor,other]-base[0,other])
        base[:,axis]-=base[0,axis]+slope*(base[:,other]-base[0,other])
        base[:,axis]/=2*ConvexHull(base).volume
    alpha=1. if force else float(rng.choice([.35,.7,1.,1.15,1.5]))
    q[:,axis]=base[:,axis]+alpha*(q[:,axis]-base[:,axis])
    q=g.fit(q)
    # Tiny branch choice if deletion lands on an exact orientation wall.
    q+=rng.normal(0,1e-8,q.shape);q=g.fit(q)
    return q,{'axis':axis,'released':released.tolist(),'released_triples':g.ix[released].tolist(),'relaxed_epigraph':float(sol.x[-1]),'alpha':alpha,'force_one_flip':force,'orientation_changes':int(sum(np.sign(g.determinant(p))!=np.sign(g.determinant(q))))}

def main(start,stop,force=False):
    registry=P.HERE/('forced_facet_experiments.jsonl' if force else 'facet_experiments.jsonl');sources={}
    for kind,n in P.TARGETS:sources[kind,n]=(*P.fetch(kind,n),P.Geometry(kind,n))
    (P.HERE/f'preregister_facets_{start}.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seeds':list(range(start,stop)),'targets':P.TARGETS,'method':'release 1–5 active determinant facets in one exact coordinate LP, then full constraints restored in changed order type; independent rational acceptance','workers':1,'force_one_flip':force,'axis_cycles':100,'stop_rule':'1200 jobs or certified improvement; adapt if release cannot cross useful cells'},indent=2))
    for seed in range(start,stop):
      for (kind,n),(p,base,g) in sources.items():
        tick=time.perf_counter();rng=np.random.default_rng(seed*1009+n)
        try:
          q,desc=surgery(p,g,rng,force);initial=g.score(q);q,stats=P.axis_polish(q,g,100)
          raw=P.rationalize(q,g);cert=P.VERIFIER.verify({'problem':'heilbronn_'+kind,'points':raw})
          ratio=float(Q(cert['value'])/Q(base['value'])) if cert['passed'] else None;error=None
        except Exception as e:raw=None;cert={'passed':False,'reason':repr(e)};ratio=None;error=repr(e);desc={};stats={};initial=None
        record={'seed':seed,'kind':kind,'n':n,'method':'forced_single_facet' if force else 'active_facet_surgery','program':desc,'initial':initial,'ratio_to_baseline':ratio,'baseline':base['value'],'certificate':cert,'lp_stats':stats,'runtime_seconds':time.perf_counter()-tick,'error':error}
        with registry.open('a') as f:f.write(json.dumps(record)+'\n')
        path=P.OUT/f'{kind}{n}_facet_{seed}.json';path.write_text(json.dumps({'problem':'heilbronn_'+kind,'points':raw,**record},indent=2))
        print(json.dumps({k:record[k] for k in ['seed','kind','n','ratio_to_baseline','runtime_seconds','error']}),flush=True)
        if ratio and ratio>1.000000001:(P.HERE/'FACET_PROMISING.json').write_text(json.dumps({'candidate':str(path),'record':record},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--start',type=int,default=3220);a.add_argument('--stop',type=int,default=3320);a.add_argument('--force',action='store_true');a.add_argument('--small',action='store_true');args=a.parse_args()
    if args.small:P.TARGETS=[('triangle',14),('convex',15),('square',20)]
    main(args.start,args.stop,args.force)
