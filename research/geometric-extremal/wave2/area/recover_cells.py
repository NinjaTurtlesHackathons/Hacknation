#!/usr/bin/env python3
"""Joint-coordinate recovery in independently synthesized order cells."""
import program_search as P
import json,datetime,time,hashlib
import numpy as np
from fractions import Fraction as Q

def main():
 rows=[json.loads(l) for l in (P.HERE/'forced_facet_experiments.jsonl').read_text().splitlines()]
 selected=[]
 for kind,n in P.TARGETS+[('triangle',14),('convex',15),('square',20)]:
  eligible=[r for r in rows if (r['kind'],r['n'])==(kind,n) and r['program'].get('orientation_changes')==1 and r['ratio_to_baseline']]
  seen=set()
  for r in sorted(eligible,key=lambda x:x['ratio_to_baseline'],reverse=True):
   key=(r['program']['axis'],tuple(r['program']['released']))
   if key in seen:continue
   seen.add(key);selected.append(r)
   if len(seen)==10:break
 (P.HERE/'preregister_joint_recovery.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'ranked 10 distinct adjacent orientation cells per target; coupled determinant/hull SLP 180 steps then exact-axis LP up to100 cycles; no fresh random perturbation','selection':[{k:r[k] for k in ['kind','n','seed','program']} for r in selected],'workers':1,'source_campaign_sha256':hashlib.sha256((P.HERE/'forced_facet_experiments.jsonl').read_bytes()).hexdigest()},indent=2))
 registry=P.HERE/'recovery_experiments.jsonl'
 for r in selected:
  kind,n,seed=r['kind'],r['n'],r['seed'];path=P.OUT/f'{kind}{n}_facet_{seed}.json';old=json.loads(path.read_text());p=np.array(old['points'],float);geo=P.Geometry(kind,n);tick=time.perf_counter()
  try:
   q,a=P.polish(p,geo,180);q,b=P.axis_polish(q,geo,100);raw=P.rationalize(q,geo);cert=P.VERIFIER.verify({'problem':'heilbronn_'+kind,'points':raw});ratio=float(Q(cert['value'])/Q(r['baseline'])) if cert['passed'] else None;err=None
  except Exception as e:raw=None;cert={'passed':False,'reason':repr(e)};ratio=None;a=b={};err=repr(e)
  rec={'kind':kind,'n':n,'seed':seed,'method':'joint_recovery_of_forced_order_cell','initial_ratio':r['ratio_to_baseline'],'ratio_to_baseline':ratio,'baseline':r['baseline'],'certificate':cert,'source_candidate':str(path),'runtime_seconds':time.perf_counter()-tick,'lp_stats':[a,b],'error':err}
  with registry.open('a') as f:f.write(json.dumps(rec)+'\n')
  out=P.OUT/f'{kind}{n}_recovery_{seed}.json';out.write_text(json.dumps({'problem':'heilbronn_'+kind,'points':raw,**rec},indent=2));print(json.dumps({k:rec[k] for k in ['kind','n','seed','initial_ratio','ratio_to_baseline','runtime_seconds','error']}),flush=True)
  if ratio and ratio>1.000000001:(P.HERE/'RECOVERY_PROMISING.json').write_text(json.dumps({'candidate':str(out),'record':rec},indent=2))
if __name__=='__main__':main()
