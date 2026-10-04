#!/usr/bin/env python3
from pathlib import Path
import json,itertools,hashlib
base=Path(__file__).resolve().parents[3]
records=json.loads((base/'results/records.json').read_text())
for rec in records['records']:
 raw=(base/rec['candidate']).read_bytes(); p=json.loads(raw)['points']; hist={}
 assert hashlib.sha256(raw).hexdigest()==rec['sha256']
 assert len(p)==rec['n'] and len({tuple(x) for x in p})==len(p)
 for x,y in itertools.combinations(p,2):
  a,b=x[0]-y[0],x[1]-y[1];q=a*a+a*b+b*b
  assert q>0;hist[q]=hist.get(q,0)+1
 assert len(hist)==rec['k'] and sorted(hist)==rec['squared_distances']
 h=rec['halfplanes']
 box={(a,b) for a in range(-30,31) for b in range(-30,31) if all(u*a+v*b<=c for u,v,c in h)}
 assert box==set(map(tuple,p))
 print(rec['id'],len(p),len(hist),sum(hist.values()),'PASS')
