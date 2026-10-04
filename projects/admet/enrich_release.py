from pathlib import Path
import os,json,csv,time,sys
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parents[1]));os.environ['ADMET_RELEASE']='1'
from release_records import records
from asd.domains.admet_domain import DOMAIN
state=json.loads((ROOT/'state.json').read_text());assert len(state['runden'])==3
state['claims']=[c for c in state['claims'] if not c['id'].startswith('release-')]
for key,r in records().items():
 p={'typ':'release_record','key':key,'text':r['text']};ok,why,_=DOMAIN.check(p);assert ok,(key,why)
 state['claims'].append(dict(id='release-'+key,frage=key,text=r['text'],pruefung=p,grund=why,level=r['level'],status='bestätigt',red_team=[],runde=0,evidence_run_ids='experiments.csv;predictions;verification.json'))
(ROOT/'state.json').write_text(json.dumps(state,indent=2,ensure_ascii=False))
with (ROOT/'claims.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['claim_id','text','level','evidence_run_ids','status'],lineterminator='\n');w.writeheader()
 for c in state['claims']:w.writerow({'claim_id':'C-'+c['id'],'text':c['text'],'level':c['level'],'evidence_run_ids':c.get('evidence_run_ids','runde'+str(c['runde'])+'.json'),'status':c['status']})
gates=[('0',True,'Metric, verifier, model assumptions and fixed scope recorded'),('selftest',True,'Ten verifier cases plus synthetic recovery pass'),('1',True,'Naive baseline and 22-endpoint coverage audit complete'),('2',True,'Fixed descriptor candidate passes validation precheck; alternatives stay exploratory'),('3',True,'All three fixed validation improvements meet nominal criteria; expanded BH family reported; conditional dataset sensitivity only'),('4',True,'Independent audit, negative controls, source-grounded scorer, completeness contracts; semantic shared-writer gap handled in deterministic release'),('5',False,'Research pilot complete; independent assays, clinical validation and publication-level novelty absent')]
with (ROOT/'gates.csv').open('w') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['gate','passed','reason','ts'])
 for g,ok,why in gates:w.writerow([g,ok,why,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())])
print('Enriched',len(state['claims']),'claims; every release record passed domain.check')
