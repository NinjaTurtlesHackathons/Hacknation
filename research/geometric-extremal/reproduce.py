#!/usr/bin/env python3
"""Dependency-free independent certificate replay; discovery is optional."""
from pathlib import Path
import json,importlib.util,hashlib,sys
BASE=Path(__file__).resolve().parent

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=module('rational_checker',BASE/'certification/verify.py')
B=module('integer_checker',BASE/'certification/independent_audit.py')
L=module('local_cycle_checker',BASE/'certification/local_cycle.py')
passed=True;checks=[]
for label,tests,checker in [('rational',A.selftest(),A.verify),('integer',B.controls(),B.verify)]:
 for spec,want in tests:
  got=checker(spec)['passed']; passed &= got==want
 print(label,'controls',len(tests),'passed' if passed else 'FAILED')
claims=json.loads((BASE/'tables/claims.json').read_text())
for c in claims:
 spec=c.get('pruefung')
 if not spec:continue
 if spec['problem']=='torus_local_cycle':
  r=L.check();passed &= r['passed'];checks.append({'claim_id':c['claim_id'],'local_proof_dependencies':r});continue
 a=A.verify(spec);b=B.verify(spec);ok=a['passed'] and b['passed']
 for key in ('value','radius','distance_count','squared_distances','hull_area','hull_vertices','markov_counterexample'):
  if key in a or key in b:ok &= a.get(key)==b.get(key)
 passed &= ok;checks.append({'claim_id':c['claim_id'],'agreement':ok,'certificate':a})
 print(c['claim_id'],'PASS' if ok else 'FAIL')
report={'passed':bool(passed),'certificates':checks,'novelty':'not established','trust_basis':'two stdlib exact arithmetic programs; elementary local proof independently reviewed; no formal proof assistant'}
print(json.dumps({'passed':bool(passed),'reviewed_certificates':len(checks),'discovery_claim':False}))
sys.exit(0 if passed else 1)
