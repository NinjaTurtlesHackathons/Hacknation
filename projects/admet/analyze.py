from pathlib import Path
import json
import pandas as pd,numpy as np
from engine import ENDPOINTS,summary
from verifier import paired,bh
ROOT=Path(__file__).resolve().parent
out={};family=[]
for endpoint in ENDPOINTS:
 s,rows=summary(endpoint);a=[r['mae'] for r in rows if r['method']=='morgan'];b=[r['mae'] for r in rows if r['method']=='combined'];z=paired(a,b);family.append(z['p']);out[endpoint]={'validation':s,'comparison':z}
rej,adj=bh(family)
for i,e in enumerate(ENDPOINTS):
 out[e]['comparison'].update(bh_q=adj[i],bh_reject=rej[i],gate3=bool(rej[i] and family[i]<.05 and out[e]['comparison']['ci_low']>1))
 if (ROOT/'test_results.json').exists():
  s,rows=summary(e,'test');out[e]['test']=s
  d=pd.read_csv(ROOT/'predictions'/f'{e}_test.csv.gz');valid=d[~d.invalid_structure.astype(bool)]
  out[e]['test_valid_structures']={m:float(np.abs(sub.y-sub.pred).mean()) for m,sub in valid.groupby('method')}
  out[e]['first_five_test']={m:float(np.abs(sub.y-sub.pred).mean()) for m,sub in d[d.seed<1005].groupby('method')}
(ROOT/'analysis.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
