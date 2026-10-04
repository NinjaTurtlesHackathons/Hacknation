#!/usr/bin/env python3
"""Attack a temporary witness copy; never mutate canonical research artifacts."""
from pathlib import Path
import tempfile,json,hashlib,importlib.util,copy
BASE=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('replay',BASE/'results/reproduce.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=json.loads((BASE/'results/records.json').read_text())['records'][0]
p=json.loads((BASE/r['candidate']).read_text());reports=[]
with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
 t=Path(tmp);(t/'certification').symlink_to(BASE/'certification',target_is_directory=True);out=t/r['candidate'];out.parent.mkdir(parents=True);m.BASE=t
 def run(name,mutate,expect_reject=True,recompute_hash=True):
  x=copy.deepcopy(p);record=copy.deepcopy(r);mutate(x,record);raw=json.dumps(x).encode();out.write_bytes(raw)
  if recompute_hash:record['sha256']=hashlib.sha256(raw).hexdigest()
  try:m.check(record);rejected=False;reason='accepted'
  except Exception as e:rejected=True;reason=str(e) or type(e).__name__
  reports.append({'control':name,'expected_reject':expect_reject,'rejected':rejected,'passed':rejected==expect_reject,'reason':reason})
 run('unaltered',lambda x,r:None,False)
 run('duplicate',lambda x,r:x['points'].__setitem__(1,x['points'][0]))
 run('fractional',lambda x,r:x['points'][0].__setitem__(0,x['points'][0][0]+.1))
 run('boolean-coordinate',lambda x,r:x['points'][0].__setitem__(0,False))
 run('wrong-metric',lambda x,r:x.__setitem__('metric','square'))
 run('wrong-k',lambda x,r:r.__setitem__('k',30))
 run('wrong-palette',lambda x,r:r['squared_distances'].__setitem__(-1,90))
 run('changed-wall',lambda x,r:r['halfplanes'][0].__setitem__(2,0))
 run('byte-hash',lambda x,r:None,recompute_hash=False)
 run('wrong-multiplicity',lambda x,r:r['multiplicities'].__setitem__('1',999))
print(json.dumps(reports,indent=2))
(Path(__file__).parent/'failure_controls.json').write_text(json.dumps(reports,indent=2)+'\n')
