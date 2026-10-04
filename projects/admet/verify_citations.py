from pathlib import Path
import json,urllib.request,urllib.parse,difflib
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
REFS=[('Yang et al.','Analyzing Learned Molecular Representations for Property Prediction','10.1021/acs.jcim.9b00237'),('Bemis and Murcko','The properties of known drugs. 1. Molecular frameworks','10.1021/jm9602928'),('Hosni et al.','Explicit Applicability Domain Calculations Can Help Determine When Uncertainty Estimates Are Less Reliable','10.1021/acsomega.5c11875'),('Deng et al.','A systematic study of key elements underlying molecular property prediction','10.1038/s41467-023-41948-6')]
def check(r):
 author,title,doi=r
 try:
  req=urllib.request.Request('https://api.crossref.org/works/'+urllib.parse.quote(doi),headers={'User-Agent':'Hacknation-ADMET-research/1.0'})
  with urllib.request.urlopen(req,timeout=30) as f:d=json.load(f)['message']
  found=d['title'][0];sim=difflib.SequenceMatcher(None,title.lower(),found.lower()).ratio()
  return dict(author=author,title=found,doi=doi,expected_title=title,status='VERIFIED' if sim>=.9 else 'MISMATCH',similarity=sim,url='https://doi.org/'+doi)
 except Exception as e:return dict(author=author,title=title,doi=doi,status='UNVERIFIED',reason=type(e).__name__)
with ThreadPoolExecutor(4) as pool:out=list(pool.map(check,REFS))
(ROOT/'references_crossref.json').write_text(json.dumps(out,indent=2));print([(r['title'],r['status']) for r in out])
