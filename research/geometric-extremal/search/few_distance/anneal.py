"""Different discovery method: move sites, not allowed-distance palettes."""
import json, math, random, time
from pathlib import Path
import numpy as np
from search import q,norms,BASE,OUT,LOG

def run(k,n,baseline,seed,steps=250000):
    rng=random.Random(seed); start=time.perf_counter()
    sites=[(a,b) for a in range(-12,13) for b in range(-12,13) if q(a,b)<=100]
    offset=baseline[0]; baseline=[(a-offset[0],b-offset[1]) for a,b in baseline]
    center=np.mean(baseline,axis=0).round().astype(int)
    baseline=[(a-int(center[0]),b-int(center[1])) for a,b in baseline]
    pts=baseline+[min((s for s in sites if s not in baseline),key=lambda s:len(norms(baseline+[s])))]
    p=np.array(pts,dtype=np.int64); occupied=set(pts); hist=np.zeros(1201,dtype=np.int64)
    for i in range(n):
        d=p[:i]-p[i]; vals=d[:,0]**2+d[:,0]*d[:,1]+d[:,1]**2
        hist+=np.bincount(vals,minlength=len(hist))
    energy=lambda h:float(np.count_nonzero(h))+.015*float(np.sqrt(h).sum())
    e=energy(hist); best=int(np.count_nonzero(hist)); bestp=p.copy(); accepted=0
    for step in range(steps):
        i=rng.randrange(n); old=tuple(p[i]); fresh=rng.choice(sites)
        if fresh in occupied: continue
        other=np.concatenate((p[:i],p[i+1:]))
        do=other-p[i]; dn=other-np.array(fresh)
        vo=do[:,0]**2+do[:,0]*do[:,1]+do[:,1]**2; vn=dn[:,0]**2+dn[:,0]*dn[:,1]+dn[:,1]**2
        hh=hist-np.bincount(vo,minlength=len(hist))+np.bincount(vn,minlength=len(hist))
        ee=energy(hh); temp=.03+.6*(1-(step%25000)/25000)**3
        if ee<=e or rng.random()<math.exp(min(0,(e-ee)/temp)):
            hist=hh; e=ee; p[i]=fresh; occupied.remove(old); occupied.add(fresh); accepted+=1
            cnt=int(np.count_nonzero(hist))
            if cnt<best:
                best=cnt; bestp=p.copy(); print('best',k,n,best,'step',step,flush=True)
                if best<=k:
                    witness={'problem':'few_distance','metric':'triangular','points':bestp.tolist(),'max_distances':k,'seed':seed,'method':'site_swap_annealing'}
                    file=OUT/f'candidate_k{k}_n{n}_seed{seed}.json'; file.write_text(json.dumps(witness,indent=2)+'\n'); break
        if step and step%50000==0:
            # Restart from best, progressively escape the discovered basin.
            print('progress',k,step,'best',best,'current',np.count_nonzero(hist),flush=True)
    record={'seed':seed,'method':'site_swap_annealing','k':k,'n':n,'steps':step+1,'accepted':accepted,'best_distance_count':best,'runtime_s':time.perf_counter()-start,'status':'candidate' if best<=k else 'negative'}
    (OUT/f'observed_k{k}_n{n}_seed{seed}.json').write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':bestp.tolist(),'max_distances':best,'target_max_distances':k,'status':'observed_nonimproving'},indent=2)+'\n')
    with LOG.open('a') as f: f.write(json.dumps(record)+'\n')
    print(record,flush=True)

if __name__=='__main__':
    b12=json.loads((OUT/'baseline_k12_n27.json').read_text())['points']
    b16=json.loads((OUT/'baseline_k16_n37.json').read_text())['points']
    b19=[(a,b) for a in range(8) for b in range(8) if 3<=a+b<=10]
    b23=[(a,b) for a in range(-4,5) for b in range(-4,5) if abs(a+b)<=4]
    for k,n,b in [(12,28,b12),(16,38,b16),(19,49,b19),(23,62,b23)]:
        assert len(b)==n-1 and len(norms(b))<=k
        f=OUT/f'baseline_structured_k{k}_n{n-1}.json'; f.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':b,'max_distances':k,'attribution':'Known Bao-Yu lower-bound construction; independent reconstruction'},indent=2)+'\n')
        run(k,n,b,41218+k)
