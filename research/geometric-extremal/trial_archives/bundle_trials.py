#!/usr/bin/env python3
"""Lossless trial bundles keep mathematical review paths visible in GitHub.
Raw trials remain in the complete release zip; a fresh clone restores them
before archive validation or full pipeline reintegration.
"""
from pathlib import Path
import hashlib,json,tarfile,sys
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
GROUPS=['area','transfer','wave2_area','wave2_director','wave2_polygon','wave2_polygon_transfer','wave2_family']
KEEP={'candidates/wave2_family/support_k41_n111_code7324998.json','candidates/wave2_family/ninegon_s3_t1_k41_n111.json'}
def pack():
 out={}
 for group in GROUPS:
  files=[p for p in sorted((BASE/'candidates'/group).glob('*.json')) if str(p.relative_to(BASE)) not in KEEP]
  target=HERE/(group+'.tar.gz')
  with tarfile.open(target,'w:gz',compresslevel=6) as tar:
   for p in files:
    info=tar.gettarinfo(str(p),str(p.relative_to(BASE)));info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
    with p.open('rb') as f:tar.addfile(info,f)
  out[target.name]={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 (HERE/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('Bundled trial files',sum(len(v['files']) for v in out.values()))
def restore():
 count=0
 for name,entry in json.loads((HERE/'manifest.json').read_text()).items():
  target=HERE/name
  if hashlib.sha256(target.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Bundle hash: '+name)
  with tarfile.open(target,'r:gz') as tar:
   for member in tar:
    if not member.isfile() or member.name not in entry['files'] or '..' in Path(member.name).parts or member.name.startswith('/'):raise ValueError('Unexpected member')
    data=tar.extractfile(member).read()
    if hashlib.sha256(data).hexdigest()!=entry['files'][member.name]:raise ValueError('Trial hash')
    p=BASE/member.name
    if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);count+=1
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=entry['files'][member.name]:raise ValueError('Changed existing trial')
 return count
if __name__=='__main__':
 if '--pack' in sys.argv:pack()
 else:print('Exact trial restore PASS:',restore(),'files restored')
