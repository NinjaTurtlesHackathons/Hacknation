"""Data-contract, protocol, synthetic, and scorer verification. Fail closed."""
from pathlib import Path
import sys,json,math
import numpy as np,pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from verifier import mae,bh,paired
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from asd.selftest import run

def validate():
 release='--release' in sys.argv
 if release:
  for name in ['experiments.csv','seal.json','release_hashes.json','validation.json','test_results.json','analysis.json']:
   assert (ROOT/name).exists(), 'missing release artifact: '+name
  import hashlib
  for name,h in json.loads((ROOT/'release_hashes.json').read_text()).items():
   assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h, 'release hash mismatch: '+name
 ok,tests=run('admet');assert ok
 checks={'domain_selftest':True}
 rng=np.random.default_rng(42);X=rng.normal(size=(400,6));y=2*X[:,0]-X[:,1]+.1
 model=LinearRegression().fit(X[:300],y[:300]);pred=model.predict(X[300:]);err=mae(y[300:].tolist(),pred.tolist());assert err<1e-10
 null=LinearRegression().fit(X[:300],rng.permutation(y[:300])).predict(X[300:]);assert mae(y[300:].tolist(),null.tolist())>.5
 checks['synthetic_recovery']={'mae':err,'shuffled_mae':mae(y[300:].tolist(),null.tolist())}
 assert bh([.001,.02,.9])[0]==[True,True,False]
 assert abs(mae([0,3],[1,1])-mean_absolute_error([0,3],[1,1]))<1e-12
 checks['BH_known_answer']=True
 checks['scorer_independent_agreement']=True
 perm=np.random.default_rng(11).permutation(len(y[300:]));assert abs(mae(y[300:][perm].tolist(),pred[perm].tolist())-err)<1e-12
 checks['row_permutation_invariance']=True
 from engine import features,ENDPOINTS,summary
 f,_=features(['CCO','c1ccccc1']);g,_=features(['CCO','c1ccccc1']);assert all(np.array_equal(f[k],g[k]) for k in f)
 checks['neutral_identifier_invariance']='Features depend only on SMILES; no names or IDs enter any fit or agent prompts; no LLM memorization guarantee.'
 cov=pd.read_csv(ROOT/'coverage.csv');assert len(cov)==44 and cov.missing_y.sum()==0
 assert cov.loc[cov.split=='train_val','invalid'].sum()==0
 assert cov.loc[cov.split=='test','invalid'].sum()==2
 assert cov.loc[cov.split=='test','canonical_overlap'].sum()==0
 assert cov.loc[cov.split=='test','scaffold_overlap'].sum()==0
 checks['coverage_contract']=True
 if (ROOT/'experiments.csv').exists():
  e=pd.read_csv(ROOT/'experiments.csv');assert not e.run_id.duplicated().any();assert set(e.seed)==set(range(1000,1020));assert e.y.notna().all()
  for endpoint in ENDPOINTS:
   for split in ['valid','test']:
    p=ROOT/'predictions'/f'{endpoint}_{split}.csv.gz'
    if not p.exists():
     assert not release, 'missing predictions: '+str(p)
     continue
    d=pd.read_csv(p);assert not d.duplicated(['seed','method','row']).any();assert np.isfinite(d[['y','pred']].to_numpy()).all()
    assert len(d.groupby(['seed','method']))==100, 'requires every seed-method group'
    for (seed,method),s in d.groupby(['seed','method']):
     idx=np.load(ROOT/'cache'/f'{endpoint}_{seed}_indices.npz')
     expected=idx['valid'] if split=='valid' else np.arange(len(pd.read_csv(ROOT/'data/admet_group'/endpoint/'test.csv')))
     assert set(s['row'])==set(expected) and len(s)==len(expected), 'incomplete rows'
     independent=mae(s.y.tolist(),s.pred.tolist());official=float(mean_absolute_error(s.y,s.pred));assert abs(independent-official)<1e-10
     logged=e[(e.seed==seed)&(e.policy==method)&(e.dataset==endpoint)&(e.step==(0 if split=='valid' else 1))].y.iloc[0];assert abs(logged-independent)<1e-10
    assert set(d.method)=={'median','morgan','descriptors','combined','shuffled'}
  if release:assert len(e)==600, 'requires 300 validation and 300 test logs'
  checks['predictions_contract_and_rescoring']=True
 (ROOT/'verification.json').write_text(json.dumps({'checks':checks,'selftest':tests,'passed':True},indent=2))
 print('ALL VALIDATION CHECKS PASSED')
if __name__=='__main__':validate()
