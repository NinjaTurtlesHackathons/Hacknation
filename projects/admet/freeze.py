"""For fresh reruns only: seal before first final test. Never replace an existing seal."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
if (ROOT/'seal.json').exists():raise SystemExit('Seal already exists: use a fresh artifact directory/branch')
(ROOT/'frozen_protocol.md').write_bytes((ROOT/'prereg.md').read_bytes())
files=[ROOT/'engine.py',ROOT/'verifier.py',ROOT/'frozen_protocol.md']+list((ROOT/'cache').glob('*'))+list((ROOT/'predictions').glob('*valid*'))
for e in ['solubility_aqsoldb','lipophilicity_astrazeneca','caco2_wang']:files += [ROOT/'data/admet_group'/e/'train_val.csv',ROOT/'data/admet_group'/e/'test.csv']
(ROOT/'seal.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}},indent=2))
