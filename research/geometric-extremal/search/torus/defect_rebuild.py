#!/usr/bin/env python3
"""Topology-changing macro mutation: remove a cluster, relax, rebuild holes."""
from search import *
record({'kind':'prospective_batch','seeds':[2000,2019],'method':'remove_three_relax_reinsert_one_by_one','n':15,'workers':1,'success':'exact conjecture threshold','stop':'20 macro reconstructions without progress'})
base=lattice(15,4,1);best=value(base)
for seed in range(2000,2020):
 rng=np.random.default_rng(seed);t=time.monotonic()
 # Remove either contact-connected cluster or dispersed points; intermediate
 # systems can change their contacts, unlike symmetry-release near fixed N.
 origin=seed%15
 deleted=[origin,(origin+1)%15,(origin+4)%15] if seed%2 else rng.choice(15,3,replace=False).tolist()
 p=np.delete(base,deleted,axis=0);p,info=optimize(p)
 steps=[{'n':12,'actual':float(value(p))}]
 for n in [13,14,15]:
  grid=rng.random((4000,2));v=grid[:,None,:]-p[None,:,:];v-=np.rint(v)
  hole=grid[np.argmax(np.min(np.sum(v*v,axis=2),axis=1))]
  p=np.vstack((p,hole));p,info=optimize(p,maxiter=600)
  steps.append({'n':n,'actual':float(value(p))})
 v=float(value(p));r,path=save(p,f'defect_seed{seed}',{'seed':seed,'method':'remove_three_relax_reinsert','deleted':deleted})
 record({'kind':'defect_rebuild','seed':seed,'deleted':deleted,'steps':steps,'actual':v,'certificate':r,'artifact':path,'elapsed_seconds':time.monotonic()-t,'exceeds_lattice':bool(v>best+1e-11),'exceeds_conjecture_numeric':bool(v>target(15))})
 print(seed,v,flush=True)
