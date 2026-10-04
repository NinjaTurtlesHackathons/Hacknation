"""Adversarial comparison, independently derived physical Cartesian norm.
Does not import discovery code, tables or its norm function.
"""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import importlib.util,json,random,time
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('checked_verifier',ROOT/'certification'/'verify.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def independent(s):
    p=[tuple(Fraction(x)/s.get('scale',1) for x in ab) for ab in s['points']]
    if len(set(p))!=len(p): return None
    ds=set()
    for (a,b),(c,d) in combinations(p,2):
        dx=a-c;dy=b-d
        # The triangular lattice maps to Cartesian X=a+b/2,Y=sqrt(3)b/2.
        ds.add(((2*dx+dy)**2+3*dy**2)/4 if s.get('metric')=='triangular' else dx**2+dy**2)
    return sorted(ds)
start=time.perf_counter(); rows=[];rng=random.Random(41242)
for file in sorted((ROOT/'candidates'/'few_distance').glob('*.json')):
    s=json.loads(file.read_text());expected=independent(s); result=module.verify(s)
    rows.append({'test':file.name,'agreement':result['passed'] and result['distance_count']==len(expected) and result['squared_distances']==[str(v) for v in expected],'passed':result['passed'],'n':len(s['points']),'distance_count':len(expected),'discovery':file.name.startswith('candidate_')})
for trial in range(1000):
    p=rng.sample([(a,b) for a in range(-5,6) for b in range(-5,6)],rng.randrange(2,25))
    scale=rng.choice([1,2,3,7]);s={'problem':'few_distance','metric':rng.choice(['triangular','euclidean']),'points':p,'scale':scale}
    ds=independent(s);s['max_distances']=len(ds)+rng.choice([-1,0,1]);want=len(ds)<=s['max_distances'] and s['max_distances']>=1
    result=module.verify(s);good=result['passed']==want
    if result['passed']:good &= result['squared_distances']==[str(v) for v in ds]
    rows.append({'test':f'fuzz{trial}','agreement':good})
seed={'problem':'few_distance','metric':'triangular','points':[[0,0],[1,0],[0,1]],'max_distances':1}
malformed=[{**seed,'points':[[0,0],[0,0]]},{**seed,'points':[[0.0,0],[1,0],[0,1]]},{**seed,'points':[[True,0],[1,0],[0,1]]},{**seed,'scale':0},{**seed,'scale':True},{**seed,'max_distances':True},{**seed,'metric':'hexagonal'},{**seed,'tolerance':1e-10},{**seed,'points':[['NaN',0],[1,0],[0,1]]},{**seed,'points':[['1/0',0],[1,0],[0,1]]},{**seed,'points':[[0,0],[1,0],[100,100]]}]
for i,s in enumerate(malformed):
    result=module.verify(s);rows.append({'test':f'malformed{i}','agreement':not result['passed'],'result':result})
report={'passed':all(r['agreement'] for r in rows),'tests':len(rows),'seed':41242,'runtime_s':time.perf_counter()-start,'definition':'physical map (a+b/2,sqrt(3)b/2), exact norm via Cartesian square expansion','rows':rows}
(Path(__file__).parent/'adversarial_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'})); print('failures',[r for r in rows if not r['agreement']])
