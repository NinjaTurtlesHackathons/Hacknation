from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent
files=list((p/'predictions').glob('*'))+[p/'engine.py',p/'verifier.py',p/'frozen_protocol.md']
(p/'release_hashes.json').write_text(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
