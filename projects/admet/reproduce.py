"""Re-run fixed matrix in a NEW directory; original evidence stays intact."""
from pathlib import Path
import shutil,subprocess,sys,datetime,json
ROOT=Path(__file__).resolve().parent
new=ROOT/'reproductions'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
new.mkdir(parents=True,exist_ok=False)
for name in ['engine.py','verifier.py','freeze.py','record_test_hashes.py','analyze.py']:
 shutil.copy2(ROOT/name,new/name)
shutil.copy2(ROOT/'frozen_protocol.md',new/'prereg.md')
for operation in ['audit','valid']:
 subprocess.run([sys.executable,str(new/'engine.py'),operation],check=True)
original=json.loads((ROOT/'provenance.json').read_text())['files'];fresh=json.loads((new/'provenance.json').read_text())['files']
if original!=fresh:raise SystemExit('Downloaded snapshot changed: preserve new outputs and inspect provenance; no comparability claim')
for script in ['freeze.py']:
 subprocess.run([sys.executable,str(new/script)],check=True)
subprocess.run([sys.executable,str(new/'engine.py'),'test'],check=True)
for script in ['record_test_hashes.py','analyze.py']:subprocess.run([sys.executable,str(new/script)],check=True)
a=json.loads((ROOT/'test_results.json').read_text());b=json.loads((new/'test_results.json').read_text());differences=[]
for endpoint in a:
 for method in ['median','morgan','descriptors','combined','shuffled']:
  delta=abs(a[endpoint][method]['mean_mae']-b[endpoint][method]['mean_mae']);differences.append(dict(endpoint=endpoint,method=method,absolute_difference=delta))
(new/'reproduction_check.json').write_text(json.dumps(differences,indent=2))
assert all(x['absolute_difference']<1e-8 for x in differences),'Numerical reproduction differs; inspect preserved reproduction_check.json'
print('REPRODUCTION PASSED:',new)
