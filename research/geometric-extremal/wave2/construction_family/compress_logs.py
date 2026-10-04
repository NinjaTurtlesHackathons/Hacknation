#!/usr/bin/env python3
"""Preserve every completed trial row, with verified compression round trip."""
from pathlib import Path
import gzip,hashlib,json,datetime
H=Path(__file__).resolve().parent
manifest=H/'log_archive_manifest.json'
existing=json.loads(manifest.read_text())['entries'] if manifest.exists() else []
entries=[]
for path in sorted(H.glob('*.csv')):
 rawhash=hashlib.sha256();size=0;lines=0;out=path.with_suffix('.csv.gz')
 with path.open('rb') as src,gzip.open(out,'wb',compresslevel=6) as dst:
  while chunk:=src.read(1<<20):rawhash.update(chunk);size+=len(chunk);lines+=chunk.count(b'\n');dst.write(chunk)
 check=hashlib.sha256();restored=0
 with gzip.open(out,'rb') as src:
  while chunk:=src.read(1<<20):check.update(chunk);restored+=len(chunk)
 assert check.hexdigest()==rawhash.hexdigest() and restored==size
 entries.append({'original':str(path),'compressed':str(out),'original_sha256':rawhash.hexdigest(),'compressed_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'uncompressed_bytes':size,'compressed_bytes':out.stat().st_size,'data_rows':lines-1,'roundtrip_verified':True,'meaning':'one row per executed support program; not only Pareto records; code,n,actual norm-class count; candidate coordinates reconstruct from published support program'})
 path.unlink()
changed={e['original'] for e in entries};entries=[e for e in existing if e['original'] not in changed]+entries
manifest.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries},indent=2));print(json.dumps(entries,indent=2))
