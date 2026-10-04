#!/usr/bin/env python3
import json,pathlib,collections,hashlib,datetime
from fractions import Fraction as Q
H=pathlib.Path(__file__).resolve().parent
files=['experiments.jsonl','facet_experiments.jsonl','forced_facet_experiments.jsonl','recovery_experiments.jsonl']
rows=[];file_summary={}
for fn in files:
 p=H/fn
 if not p.exists():continue
 part=[json.loads(x) for x in p.read_text().splitlines()];rows+=part
 file_summary[fn]={'completed':len(part),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'measured_job_seconds':sum(r['runtime_seconds'] for r in part)}
methods={}
for method in sorted(set(r['method'] for r in rows)):
 part=[r for r in rows if r['method']==method];valid=[r for r in part if r['certificate'].get('passed')]
 methods[method]={'completed':len(part),'exact_valid':len(valid),'exact_improvements':sum(Q(r['certificate']['value'])>Q(r['baseline']) for r in valid),'measured_job_seconds':sum(r['runtime_seconds'] for r in part)}
best={}
for r in rows:
 if not r['certificate'].get('passed'):continue
 key=f"{r['kind']}{r['n']}";ratio=Q(r['certificate']['value'])/Q(r['baseline'])
 if key not in best or ratio>Q(best[key]['exact_ratio']):
  if r['method']=='active_facet_surgery' or r['method']=='forced_single_facet':suffix='facet'
  elif r['method']=='joint_recovery_of_forced_order_cell':suffix='recovery'
  else:suffix=r['method'].split('_contact_program_')[0]
  best[key]={'candidate':f"candidates/wave2_area/{key}_{suffix}_{r['seed']}.json",'seed':r['seed'],'method':r['method'],'value':r['certificate']['value'],'baseline':r['baseline'],'exact_ratio':str(ratio),'ratio_illustrative':float(ratio),'improved':ratio>1}
result={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed_jobs':len(rows),'measured_job_seconds':sum(r['runtime_seconds'] for r in rows),'files':file_summary,'methods':methods,'best':best,'novelty':'none established','scope':'search negative only; no global impossibility or optimality statement; interrupted jobs and unused preregistered seeds excluded'}
(H/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
