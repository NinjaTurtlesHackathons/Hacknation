"""Exact-integer geometric witnesses; heuristic palette discovery, timed clique search.
Independent implementation; inspired by Bao/Yu distance-palette clique reduction.
No completeness claim: unit-distance anchor and finite palette universe restrict search.
"""
import argparse, json, random, time
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'candidates'/'few_distance'
LOG=Path(__file__).parent/'experiments.jsonl'
def q(a,b): return a*a+a*b+b*b
def norms(points):
    return sorted({q(a-c,b-d) for i,(a,b) in enumerate(points) for c,d in points[:i]})

def clique(palette, incumbent, seconds):
    start=time.perf_counter(); allowed=set(palette); m=max(allowed); radius=int(2*m**.5)+2
    vertices=[(a,b) for a in range(-radius,radius+1) for b in range(-radius,radius+1)
              if (a,b) not in [(0,0),(1,0)] and q(a,b) in allowed and q(a-1,b) in allowed]
    # Degree ordering gives a consistent deterministic graph.
    raw=[sum(1<<j for j,(c,d) in enumerate(vertices) if i!=j and q(a-c,b-d) in allowed)
         for i,(a,b) in enumerate(vertices)]
    order=sorted(range(len(vertices)), key=lambda i: raw[i].bit_count(), reverse=True)
    vertices=[vertices[i] for i in order]
    adj=[sum(1<<j for j,(c,d) in enumerate(vertices) if i!=j and q(a-c,b-d) in allowed)
         for i,(a,b) in enumerate(vertices)]
    best=[]; target=incumbent-2; calls=0; timed=False
    def color(p):
        vs=[]; bounds=[]; c=0
        while p:
            c+=1; avail=p
            while avail:
                v=(avail & -avail).bit_length()-1; bit=1<<v
                vs.append(v); bounds.append(c); p^=bit; avail &= ~bit & ~adj[v]
        return vs,bounds
    def expand(p, chosen):
        nonlocal best,target,calls,timed
        calls+=1
        if calls%128==0 and time.perf_counter()-start>seconds:
            timed=True; return
        vs,cs=color(p)
        for i in range(len(vs)-1,-1,-1):
            if len(chosen)+cs[i]<=target or timed: return
            v=vs[i]; nxt=p & adj[v]
            if nxt: expand(nxt,chosen+[v])
            elif len(chosen)+1>target:
                best=chosen+[v]; target=len(best)
            p &= ~(1<<v)
    expand((1<<len(vertices))-1,[])
    points=[(0,0),(1,0)]+[vertices[i] for i in best] if best else []
    return points, {'runtime_s':time.perf_counter()-start,'vertices':len(vertices),'calls':calls,'timed_out':timed}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=41217)
    ap.add_argument('--trials',type=int,default=500); ap.add_argument('--seconds',type=float,default=.3)
    args=ap.parse_args(); rng=random.Random(args.seed); OUT.mkdir(parents=True,exist_ok=True)
    universe=sorted({q(a,b) for a in range(-15,16) for b in range(-15,16) if 0<q(a,b)<=100})
    baselines={7:16,10:24,12:27,16:37,19:48,23:61}; best=dict(baselines); pools={k:[] for k in best}
    # Known hexagons furnish exact palettes distinct from shortest-distance palettes.
    hexpal=[]
    for s in range(1,6):
        h=[(a,b) for a in range(-s,s+1) for b in range(-s,s+1) if abs(a+b)<=s]
        hexpal.append(norms(h))
    seen=set()
    for t in range(args.trials):
        k=list(best)[t%len(best)]
        if t<len(best): pal=universe[:k]
        elif rng.random()<.3 and any(len(p)<=k for p in hexpal):
            hp=rng.choice([p for p in hexpal if len(p)<=k]); pal=hp+rng.sample([v for v in universe[:min(len(universe),k+10)] if v not in hp],k-len(hp))
        else:
            pal=list(rng.choice(pools[k]) if pools[k] and rng.random()<.75 else universe[:k])
            changes=rng.choice([1,1,2,3]); mutable=[v for v in pal if v!=1]
            for v in rng.sample(mutable,changes): pal.remove(v)
            choices=[v for v in universe[:min(len(universe),k+8)] if v not in pal]
            pal+=rng.sample(choices,changes)
        pal=sorted(pal); key=(k,tuple(pal))
        if key in seen: continue
        seen.add(key)
        pts,stat=clique(pal, max(2,baselines[k]-3),args.seconds)
        n=len(pts); ds=norms(pts)
        assert len(ds)<=k and (not pts or min(ds)>0)
        record={'experiment':t,'seed':args.seed,'k':k,'palette':pal,'n':n,'baseline':baselines[k],'method':'palette_mutation_coloring_clique','status':'exact_witness' if pts else 'no_witness','distinct_norms':ds,**stat}
        if n>=baselines[k]-2: pools[k].append(pal)
        if n>best[k]:
            best[k]=n; path=OUT/f'candidate_k{k}_n{n}_seed{args.seed}.json'
            path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':pts,'max_distances':k,'squared_distances':ds,'seed':args.seed,'palette':pal},indent=2)+'\n')
            record['candidate']=str(path.relative_to(BASE)); print('IMPROVEMENT',record,flush=True)
        if t<len(best) and pts:
            path=OUT/f'baseline_k{k}_n{n}.json'; path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':pts,'max_distances':k,'squared_distances':ds,'attribution':'Independent reconstruction using Bao-Yu shortest-distance palette'},indent=2)+'\n')
        with LOG.open('a') as f: f.write(json.dumps(record)+'\n')
        if t%30==0: print('progress',t,'best',best,flush=True)
    print('final',best,flush=True)

if __name__=='__main__': main()
