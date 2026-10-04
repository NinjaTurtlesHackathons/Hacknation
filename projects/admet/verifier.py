import math
import numpy as np
TOL=1e-6
def mae(y,p):
 if len(y)==0 or len(y)!=len(p):raise ValueError('empty/misaligned')
 if not all(math.isfinite(float(v)) for v in list(y)+list(p)):raise ValueError('nonfinite')
 return math.fsum(abs(float(a)-float(b)) for a,b in zip(y,p))/len(y)
def paired(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float)
 if len(a)!=20 or len(b)!=20 or not np.isfinite(a).all() or not np.isfinite(b).all() or (b<=0).any():raise ValueError('requires 20 finite pairs')
 idx=np.random.default_rng(909).integers(0,len(a),(5000,len(a)));ci=np.quantile(a[idx].mean(1)/b[idx].mean(1),[.025,.975]);d=a-b
 flips=np.random.default_rng(910).choice([-1,1],(20000,len(a)));p=(1+np.count_nonzero((flips*d).mean(1)>=d.mean()))/20001
 return dict(ratio=float(a.mean()/b.mean()),ci_low=float(ci[0]),ci_high=float(ci[1]),p=float(p))
def bh(ps,q=.1):
 ps=np.asarray(ps,float);order=np.argsort(ps);ranked=ps[order];ok=ranked<=q*np.arange(1,len(ps)+1)/len(ps);k=np.max(np.where(ok,np.arange(1,len(ps)+1),0));rej=np.zeros(len(ps),bool);rej[order[:k]]=True
 adjusted=np.minimum.accumulate((ranked*len(ps)/np.arange(1,len(ps)+1))[::-1])[::-1];out=np.empty(len(ps));out[order]=np.minimum(adjusted,1)
 return rej.tolist(),out.tolist()
