"""Systematically release regular/equiangular hexagon symmetry and try ellipses."""
import json,time
import numpy as np
from search import BASE,OUT,LOG
source=[16,19,21,24,27,27,31,34,37,37,42,45,48,49,55,58,61,63,63,69,72,75,75,79,79,85,88,91]
baseline=dict(zip(range(7,35),source)); best=dict(baseline); start=time.perf_counter(); trials=0
allp=np.array([(a,b) for a in range(-14,15) for b in range(-14,15)],dtype=np.int64)
diff=allp[:,None,:]-allp[None,:,:]
dm=diff[:,:,0]**2+diff[:,:,0]*diff[:,:,1]+diff[:,:,1]**2
def evaluate(ids,meta):
    global trials
    n=len(ids)
    if n<=16 or n>110: return
    possible=[k for k in best if n>best[k]]
    if not possible:return
    trials+=1; ds=np.unique(dm[np.ix_(ids,ids)]); count=len(ds)-1
    if count>34:return
    k=max(7,count)
    if n>best[k]:
        p=allp[ids].tolist(); path=OUT/f'candidate_windows_k{k}_n{n}.json'
        path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':p,'max_distances':k,'method':'asymmetric_window','parameters':meta},indent=2)+'\n')
        for j in best:
            if j>=k:best[j]=max(best[j],n)
        rec={'method':'asymmetric_window','n':n,'k':k,'baseline':baseline[k],'candidate':str(path.relative_to(BASE)),'parameters':meta,'runtime_s':time.perf_counter()-start}
        with LOG.open('a') as f:f.write(json.dumps(rec)+'\n')
        print('IMPROVEMENT',rec,flush=True)

for A in range(2,15):
    for B in range(2,A+1):
        for L in range(A+B):
            for U in range(L+1,A+B+1):
                mask=(allp[:,0]>=0)&(allp[:,0]<=A)&(allp[:,1]>=0)&(allp[:,1]<=B)&(allp.sum(axis=1)>=L)&(allp.sum(axis=1)<=U)
                evaluate(np.flatnonzero(mask),{'A':A,'B':B,'L':L,'U':U})
    print('hexprogress',A,'trials',trials,flush=True)
for aa in range(1,7):
    for bb in range(1,7):
        for cc in range(-min(aa,bb),min(aa,bb)+1):
            for tx,ty in [(0,0),(1,0),(1,1)]:
                # Scaled integers let half-cell shifts be exact.
                x=2*allp[:,0]-tx;y=2*allp[:,1]-ty; form=aa*x*x+bb*y*y+cc*x*y
                for radius in range(30,450,4):evaluate(np.flatnonzero(form<=radius),{'ellipse':[aa,bb,cc,tx,ty,radius]})
record={'method':'asymmetric_window','trials':trials,'runtime_s':time.perf_counter()-start,'best':best,'baseline':baseline,'status':'improved' if best!=baseline else 'negative'}
with LOG.open('a') as f:f.write(json.dumps(record)+'\n')
print(record,flush=True)
