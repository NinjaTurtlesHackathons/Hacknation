"""Render the reviewed Suleman-style manuscript from checked release evidence."""
from pathlib import Path
import csv, json, subprocess, sys, hashlib
ROOT=Path(__file__).resolve().parent
NAMES={'solubility_aqsoldb':'Solubility','lipophilicity_astrazeneca':'Lipophilicity','caco2_wang':'Caco-2'}
SUPPORT={
 'Abstract':['abstract'],
 '1 Introduction':['scope','design','novelty','ref-0','ref-3','ref-tdc'],
 '2 Setting and evaluation':['methods','splits','inference','coverage-solubility_aqsoldb','coverage-lipophilicity_astrazeneca','coverage-caco2_wang','ref-1'],
 '3 Fixed-test observations':['test-'+e for e in NAMES]+['freeze'],
 '4 Validation and falsification':['valid-'+e for e in NAMES]+['gate-'+e for e in NAMES]+['null-'+e+'-'+p for e in NAMES for p in ['validation','test']]+['segments','ref-2'],
 '5 Source-grounded verification':['verification','reproduction','lean'],
 '6 Discussion':['limitations','novelty','platform','agents'],
 'A Protocol and structural audit':['audit','invalid','precommit','freeze','coverage-solubility_aqsoldb'],
 'B Verifier and laboratory boundary':['verification','redteam','trust','agents'],
 'C Evidence and reproducibility':['reproduction','freeze','redteam']}

def render():
 from validate import validate
 if '--release' not in sys.argv:sys.argv.append('--release')
 validate()
 from release_records import records
 known=records()
 state=json.loads((ROOT/'state.json').read_text())
 claims={c['id'][8:]:c for c in state['claims'] if c['status']=='bestätigt' and c['id'].startswith('release-')}
 for key,c in claims.items():assert c['text']==known[key]['text']
 assert set(known)==set(claims)
 for keys in SUPPORT.values():assert all(k in claims for k in keys)
 rows=list(csv.DictReader((ROOT/'experiments.csv').open()))
 import numpy as np
 table=[]; reductions=[]
 for endpoint,name in NAMES.items():
  scores={m:np.array([float(r['y']) for r in rows if r['dataset']==endpoint and r['policy']==m and r['step']=='1']) for m in ['median','morgan','descriptors','combined','shuffled']}
  assert all(len(v)==20 for v in scores.values())
  reduction=100*(1-scores['combined'].mean()/scores['morgan'].mean());reductions.append(reduction)
  table.append(name+' & '+' & '.join(f'{v.mean():.3f} ({v.std(ddof=1):.3f})' for v in scores.values())+f' & {reduction:.2f}\\%'+r'\\')
 tex=(ROOT/'latex/manuscript.tex').read_text().replace('@@TEST_ROWS@@','\n'.join(table)).replace('@@REDUCTIONS@@',' '.join(f'({v:.8f},{i})' for i,v in enumerate(reductions)))
 assert '@@' not in tex
 (ROOT/'paper.tex').write_text(tex)
 # Editorial support is disclosed honestly; no token gate is called semantic verification.
 evidence={'claims':[{'claim_id':'C-release-'+k,**v} for k,v in claims.items()], 'section_support':SUPPORT,'verification':{'canonical_records_match_regenerated_evidence':True,'confirmed_only':True,'claim_count':len(claims),'table_generated_from_checked_experiments':True,'editorial_semantics_machine_proved':False,'manuscript_sha256':hashlib.sha256(tex.encode()).hexdigest(),'limitation':'Editorial prose is reviewed separately; support mapping is not a semantic proof.'}}
 (ROOT/'paper_belege.json').write_text(json.dumps(evidence,indent=2)+'\n')
 subprocess.run(['pandoc',str(ROOT/'paper.tex'),'-f','latex','-t','gfm','--wrap=none','-o',str(ROOT/'paper.md')],check=True)
 subprocess.run(['pandoc',str(ROOT/'paper.tex'),'-f','latex','-t','html','-s','-o',str(ROOT/'paper.html')],check=True)
 print('Validated evidence; rendered standalone LaTeX, Markdown, HTML and support map. Compile the source to export PDF.')
if __name__=='__main__':render()
