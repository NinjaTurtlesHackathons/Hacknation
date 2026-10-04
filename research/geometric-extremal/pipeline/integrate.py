"""Freeze exact certificates, existing Project state and sole demo tables.
Does not infer novelty from feasibility. Immutable sources compared separately.
"""
from pathlib import Path
from fractions import Fraction
import json,sys,hashlib,csv,time,importlib.util
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'research/geometric-extremal'; TABLE=BASE/'tables'
sys.path.insert(0,str(ROOT));from asd.domains.geometric_extremal_domain import DOMAIN as D
from asd.lab_loop import Project
# Project imports scipy through existing framework; optional LLM not called.
TABLE.mkdir(exist_ok=True); claims=[]; cases=[]; gates=[]
def write(name,obj): (TABLE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def claim(cid,text,level='observed',status='bestätigt',**extra):
 c={'claim_id':cid,'text':text,'level':level,'status':status,**extra};claims.append(c);return c

def case(cid,path,title,source_url,provenance='reproduction',baseline=None):
 data=json.loads(path.read_text())
 if 'problem' not in data:
  data['problem']='heilbronn_'+data['variant']
 spec={k:v for k,v in data.items() if k in ('problem','points','scale','radius','bound','metric','max_distances')}
 ok,why,cert=D.check(spec)
 gates.append({'gate':cid+'-exact','passed':ok,'reason':why,'ts':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 if not ok:return
 digest=hashlib.sha256(path.read_bytes()).hexdigest();(BASE/'certification'/f'{cid}.json').write_text(json.dumps(spec,indent=2)+'\n')
 text=title+': '+D.describe(spec)+'. Status: '+provenance+'; no novel record or global optimality established.'
 c=claim(cid,text,'computed_rigorous',pruefung=spec,evidence_run_ids=[str(path.relative_to(ROOT))],sha256=digest,source_url=source_url,novelty='not_established')
 z=data.get('scale',1); pts=[[str(Fraction(str(x))/z) for x in p] for p in data['points']]
 cases.append({'id':cid,'title':title,'problem':data['problem'],'points':pts,'certificate':cert,'claim_id':cid,'status':provenance,'source_url':source_url,'baseline':baseline,'radius':data.get('radius'),'metric':data.get('metric')})

selftests=json.loads((TABLE/'verifier_selftest.json').read_text()); count=len(selftests['tests'])
claim('GE-SELFTEST',f'Standalone exact rational checker passes {count} of {count} positive/negative controls, including area normalization, overlap, periodic wraparound, duplicate points, collinear triples, agent tolerances and nonstring problem rejection.','computed_rigorous',evidence_run_ids=['research/geometric-extremal/tables/verifier_selftest.json'])
for kind,n in [('triangle',14),('convex',15)]:
 case(f'GE-BASE-{kind.upper()}{n}',BASE/f'search/area/source_{kind}{n}.json',f'Known Heilbronn {kind} n={n}',f'https://math.tejstead.com/heilbronn/{kind}/{n}/points.json')
for n in (15,209):
 case(f'GE-BASE-TORUS{n}',BASE/f'candidates/torus/baseline_n{n}.json',f'Known square torus n={n}','https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf')
for n in (22,23,24):
 case(f'GE-BASE-PACK{n}',BASE/f'candidates/triangle_packing/baseline_n{n}.json',f'Known triangle circle packing n={n}',f'https://packomania.com/crt/txt/crt{n}.txt')
for f in sorted((BASE/'candidates/few_distance').glob('baseline_structured_*.json')):
 d=json.loads(f.read_text());k=d['max_distances'];n=len(d['points'])
 case(f'GE-BASE-FD{k}-{n}',f,f'Known triangular lattice {n} points, at most {k} distances','https://arxiv.org/abs/2509.00880')
# top recorded area candidate per problem/count; feasibility independently recomputed
best={}
for f in (BASE/'candidates/area').glob('*.json'):
 d=json.loads(f.read_text()); key=(d.get('variant'),d.get('n'));value=d.get('candidate_metric') or -1
 if key[0] and value>best.get(key,(-1,None))[0]:best[key]=(value,f)
for (kind,n),(value,f) in sorted(best.items()):
 case(f'GE-SEARCH-{kind.upper()}{n}',f,f'Searched Heilbronn {kind} n={n}',f'https://math.tejstead.com/heilbronn/{kind}/{n}/points.json','nonimproving numerical-search witness')
for n in (14,15,16):
 f=BASE/f'candidates/torus/best_n{n}.json'
 if f.exists():case(f'GE-SEARCH-TORUS{n}',f,f'Searched square torus n={n}','https://connellytensegrity.com/pdf/10.1007_s00454-016-9843-x.pdf','non-counterexample')
# Baseline+search comparisons are separate, never novelty based on a tolerated tie.
rows=[]
for path in sorted(BASE.glob('**/experiments.jsonl')):
 for line in path.read_text().splitlines():
  try:d=json.loads(line)
  except json.JSONDecodeError:continue
  if d.get('kind')=='experiment' or d.get('event')=='experiment' or ('method'in d and ('runtime_s'in d or 'runtime_seconds'in d)):
   rows.append({'run_id':f'GE-E{len(rows)+1:05d}','seed':d.get('seed'),'policy':d.get('method'),'dataset':str(path.relative_to(ROOT)),'step':d.get('steps',d.get('iterations')),'x_index':None,'y':d.get('candidate_metric',d.get('actual',d.get('best_distance_count',d.get('result',{}).get('approximate')))),'mlflow_run_id':None,'ts':None,'raw':d})
area=[r for r in rows if 'search/area/' in r['dataset']]
claim('GE-AREA-NEGATIVE',f'Area discovery register contains {len(area)} candidate trials. No certified >=0.05% improvement over frozen same-normalization triangle14/convex15/neighbor incumbents was found. These finite search failures prove no global upper bound.',evidence_run_ids=['research/geometric-extremal/search/area/experiments.jsonl'])
claim('GE-STATUS','No new geometric record, counterexample, globally optimal configuration, novel theorem or construction family is established in this checkpoint. Exact certification of inherited constructions and finite unsuccessful searches are infrastructure, not a geometric discovery.',novelty='not_established')
claim('GE-PROVENANCE','Current Heilbronn coordinates were downloaded from Tej Stead author table with source URLs and SHA256 snapshots; known torus lattice seeds derive from Connelly et al.; triangular-lattice lower bounds require combining Bao–Yu2025 with Ahmed–Snevily2013 rather than using the newer table alone.',evidence_run_ids=['research/geometric-extremal/literature/area_portfolio.md','research/geometric-extremal/analysis/few_distance.md'])
claim('GE-METHOD','Human supplied repository, topic, ambition and autonomous delegation authorization. Codex chose targets and methods, used four concurrent slots (director plus three agents), independent literature scouting and search waves, exact rational acceptance and adversarial audit. No external researcher endorsement or formal Lean proof, no statistical speedup or cost claim. Discovery scripts save seeds and failed trials. One palette-search batch was retrospectively registered and is disclosed.',evidence_run_ids=['research/geometric-extremal/context.md','research/geometric-extremal/prereg.md'])
claim('GE-EXACT-TIES','Frozen triangle14 and convex15 rational literal configurations each have one exactly minimal triangle; source counts23 and25 describe approximate active sets. Exact ties are computed by equality of rational determinants, independently of floating tolerances.','computed_rigorous')
scope=claim('GE-AUDIT-SCOPE','Independent adversarial review found and corrected a nonstring problem crash and a false Markov counterexample acceptance outside the published N>=6 conjecture scope. The known two-point packing now fails a counterexample assertion. Circle-packing source links were corrected to the right-triangle CRT coordinates; source-circle-circle attribution was erroneous.',evidence_run_ids=['research/geometric-extremal/analysis/adversarial_review.md'])
area_runtime=sum(r['raw'].get('runtime_seconds',0) for r in area)
claim('GE-AREA-RUNTIME',f'Sum of recorded area candidate wall times is {area_runtime:.6f} seconds, excluding source retrieval, compilation, reporting and director/team time. It is not total session time or CPU time, and supports no speedup claim.',evidence_run_ids=['research/geometric-extremal/search/area/experiments.jsonl'])
p={'problem':'torus_local_cycle','n':15};ok,why,proof=D.check(p)
assert ok
claim('GE-LOCAL-CYCLE',D.describe(p),'computed_rigorous',pruefung=p,novelty='not_established',evidence_run_ids=['research/geometric-extremal/certification/local_cycle.py','research/geometric-extremal/analysis/novelty_review.md','research/geometric-extremal/analysis/adversarial_review.md'])
audit_path=BASE/'analysis/adversarial_snapshot.json'
if audit_path.exists():
 audit=json.loads(audit_path.read_text())
 claim('GE-INDEPENDENT-AUDIT','Independent common-denominator checker recomputes Cartesian norms, all nine neighboring periodic cells and a gift-wrapped convex hull; its controls and hashed candidate snapshot are archived. Both checkers agreed on acceptance and exact values in the recorded audit. This agreement is not a novelty proof or formal verification.',evidence_run_ids=['research/geometric-extremal/analysis/adversarial_snapshot.json','research/geometric-extremal/analysis/adversarial_review.md'])
write('claims.json',claims);write('gates.json',gates);write('experiments.json',rows)
write('demo_data.json',{'title':'Geometry under exact scrutiny','status':'Research checkpoint: no new discovery established','summary':[{'claim_id':c['claim_id'],'text':c['text']} for c in claims if c['claim_id'] in ('GE-STATUS','GE-LOCAL-CYCLE','GE-SELFTEST','GE-AREA-NEGATIVE')],'cases':cases})
P=Project('geometric_extremal'); P.s['claims']=[{'id':c['claim_id'],'frage':c['text'],'text':c['text'],'grund':c['text'],'level':c['level'],'status':c['status'],'pruefung':c.get('pruefung'),'red_team':[]} for c in claims];P.s['runden']=[{'phase':'integration','verified_cases':len(cases),'logged_experiments':len(rows)}];P.s['widerlegt']=['No new result certified; finite search results do not exclude superior constructions.'];P.s['wissen']=[];P.s['kosten_usd']=0.0;P.s['costs_measured']=False;P.save()
for name,data,cols in [('claims',claims,['claim_id','text','level','evidence_run_ids','status']),('gates',gates,['gate','passed','reason','ts']),('experiments',rows,['run_id','seed','policy','dataset','step','x_index','y','mlflow_run_id','ts'])]:
 with (TABLE/(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(data)
print(json.dumps({'claims':len(claims),'verified_cases':len(cases),'experiments':len(rows),'status':'no discovery established'}))
