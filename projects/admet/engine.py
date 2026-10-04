"""Fixed ADMET experiment runner; no test scoring before seal.json exists."""
from pathlib import Path
import hashlib,json,time,sys,importlib.metadata,math
import numpy as np,pandas as pd
from rdkit import Chem,DataStructs,RDLogger
from rdkit.Chem import Descriptors,rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error
from tdc.benchmark_group import admet_group
RDLogger.DisableLog('rdApp.*')
ROOT=Path(__file__).resolve().parent
ENDPOINTS=['solubility_aqsoldb','lipophilicity_astrazeneca','caco2_wang']
SEEDS=list(range(1000,1020)); METHODS=['median','morgan','descriptors','combined','shuffled']
DESC=['MolWt','MolLogP','TPSA','NumHDonors','NumHAcceptors','NumRotatableBonds','RingCount','FractionCSP3','HeavyAtomCount','NumAromaticRings']
GEN=rdFingerprintGenerator.GetMorganGenerator(radius=2,fpSize=1024)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def group():return admet_group(path=str(ROOT/'data'))
def features(smiles, allow_invalid=False):
 mols=[Chem.MolFromSmiles(str(s)) for s in smiles]
 if any(m is None for m in mols) and not allow_invalid:raise ValueError('Invalid training SMILES: blocked')
 mols=[m if m is not None else Chem.MolFromSmiles('') for m in mols]
 fps=[GEN.GetFingerprint(m) for m in mols]
 x=np.array([np.asarray(fp,dtype=np.float32) for fp in fps])
 d=np.array([[getattr(Descriptors,n)(m) for n in DESC] for m in mols],dtype=np.float32)
 if not np.isfinite(d).all():raise ValueError('Nonfinite descriptors: blocked')
 return {'morgan':x,'descriptors':d,'combined':np.concatenate([x,d],axis=1)},fps

def audit():
 G=group();rows=[];manifest={}
 for endpoint in G.dataset_names:
  sets={s:pd.read_csv(ROOT/'data/admet_group'/endpoint/(s+'.csv')) for s in ['train_val','test']}
  meta={}
  for split,df in sets.items():
   if not {'Drug','Y','Drug_ID'}<=set(df):raise ValueError('Missing columns')
   mols=[Chem.MolFromSmiles(str(s)) for s in df.Drug]
   good=[m for m in mols if m is not None]
   canon=[Chem.MolToSmiles(m) for m in good]
   scaff=[MurckoScaffold.MurckoScaffoldSmiles(mol=m) for m in good]
   meta[split]={'canon':set(canon),'scaff':set(scaff)}
   rows.append(dict(dataset=endpoint,split=split,n=len(df),invalid=len(df)-len(good),missing_y=int(df.Y.isna().sum()),duplicate_canonical=len(canon)-len(set(canon)),empty_scaffold=scaff.count('')))
   p=ROOT/'data/admet_group'/endpoint/(split+'.csv');manifest[str(p.relative_to(ROOT))]=digest(p)
  rows[-1]['canonical_overlap']=len(meta['test']['canon']&meta['train_val']['canon'])
  rows[-1]['scaffold_overlap']=len(meta['test']['scaff']&meta['train_val']['scaff'])
  rows[-1]['nonempty_scaffold_overlap']=len((meta['test']['scaff']&meta['train_val']['scaff'])-{''})
 pd.DataFrame(rows).to_csv(ROOT/'coverage.csv',index=False)
 out={'files':manifest,'packages':{n:importlib.metadata.version(n) for n in ['PyTDC','numpy','pandas','scipy','scikit-learn','rdkit','lightgbm']},'benchmark_download_id':4426004,'source':'https://dataverse.harvard.edu/api/access/datafile/4426004','endpoints':G.dataset_names}
 (ROOT/'provenance.json').write_text(json.dumps(out,indent=2));return rows

def summary(endpoint,split='valid'):
 # Independent re-scoring from persisted rows, NOT model's reported score.
 pred=pd.read_csv(ROOT/'predictions'/f'{endpoint}_{split}.csv.gz')
 rows=[]
 for (seed,method),df in pred.groupby(['seed','method']):
  score=math.fsum(abs(float(a)-float(b)) for a,b in zip(df.y,df.pred))/len(df)
  rows.append({'seed':int(seed),'method':method,'mae':score,'n':len(df),'bias':math.fsum(float(b)-float(a) for a,b in zip(df.y,df.pred))/len(df)})
 out={m:{'mean_mae':float(np.mean([r['mae'] for r in rows if r['method']==m])),'sd_mae':float(np.std([r['mae'] for r in rows if r['method']==m],ddof=1))} for m in METHODS}
 out.update(endpoint=endpoint,split=split,seeds=20)
 return out,rows

def fit_validation():
 G=group();(ROOT/'predictions').mkdir(exist_ok=True);(ROOT/'cache').mkdir(exist_ok=True)
 rows=[]
 for endpoint in ENDPOINTS:
  source=pd.read_csv(ROOT/'data/admet_group'/endpoint/'train_val.csv');Xs,fps=features(source.Drug)
  # TDC retains source indices in scaffold splits; map exact rows, never by molecule alone.
  source['_row']=np.arange(len(source));store=[]
  for seed in SEEDS:
   train,valid=G.get_train_valid_split(seed,endpoint)
   tr=train.index.to_numpy();va=valid.index.to_numpy()
   if not np.array_equal(source.iloc[tr].Y.to_numpy(),train.Y.to_numpy()):raise ValueError('Index alignment')
   y=train.Y.to_numpy(float);yv=valid.Y.to_numpy(float)
   for method in METHODS:
    t=time.monotonic();model=None
    if method=='median':prediction=np.full(len(va),np.median(y))
    else:
     name='combined' if method=='shuffled' else method
     yy=np.random.default_rng(seed+50000).permutation(y) if method=='shuffled' else y
     model=LGBMRegressor(n_estimators=200,learning_rate=.05,num_leaves=15,min_child_samples=20,reg_lambda=1.,n_jobs=2,random_state=seed,deterministic=True,force_col_wise=True,verbosity=-1)
     model.fit(Xs[name][tr],yy);prediction=model.predict(Xs[name][va])
     model.booster_.save_model(str(ROOT/'cache'/f'{endpoint}_{seed}_{method}.txt'))
    score=float(mean_absolute_error(yv,prediction));rid=f'{endpoint}-{seed}-{method}-valid'
    rows.append(dict(run_id=rid,seed=seed,policy=method,dataset=endpoint,step=0,x_index=-1,y=score,mlflow_run_id='',ts=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seconds=time.monotonic()-t))
    store.append(pd.DataFrame(dict(seed=seed,method=method,row=va,y=yv,pred=prediction)))
   np.savez_compressed(ROOT/'cache'/f'{endpoint}_{seed}_indices.npz',train=tr,valid=va)
   print(endpoint,seed,'complete',flush=True)
  pd.concat(store,ignore_index=True).to_csv(ROOT/'predictions'/f'{endpoint}_valid.csv.gz',index=False)
 pd.DataFrame(rows).to_csv(ROOT/'experiments.csv',index=False)
 out={e:summary(e)[0] for e in ENDPOINTS};(ROOT/'validation.json').write_text(json.dumps(out,indent=2))

def final_test():
 seal=json.loads((ROOT/'seal.json').read_text())
 for rel,h in seal['files'].items():
  if digest(ROOT/rel)!=h:raise ValueError('Frozen artifact modified: '+rel)
 import lightgbm as lgb
 from sklearn.metrics import pairwise_distances
 rows=[];segments=[]
 for endpoint in ENDPOINTS:
  test=pd.read_csv(ROOT/'data/admet_group'/endpoint/'test.csv');trainval=pd.read_csv(ROOT/'data/admet_group'/endpoint/'train_val.csv')
  invalid=np.array([Chem.MolFromSmiles(str(s)) is None for s in test.Drug])
  Xt,tfp=features(test.Drug,allow_invalid=True);Xv,vfp=features(trainval.Drug);store=[]
  for seed in SEEDS:
   ids=np.load(ROOT/'cache'/f'{endpoint}_{seed}_indices.npz')['train'];yv=trainval.iloc[ids].Y.to_numpy(float)
   sim=np.array([max(DataStructs.BulkTanimotoSimilarity(fp,[vfp[i] for i in ids])) for fp in tfp])
   for method in METHODS:
    if method=='median':pred=np.full(len(test),np.median(yv))
    else:
     name='combined' if method=='shuffled' else method
     model=lgb.Booster(model_file=str(ROOT/'cache'/f'{endpoint}_{seed}_{method}.txt'));pred=model.predict(Xt[name],num_threads=2)
    pred[invalid]=np.median(yv);sim[invalid]=0
    store.append(pd.DataFrame(dict(seed=seed,method=method,row=np.arange(len(test)),y=test.Y.to_numpy(float),pred=pred,similarity=sim,invalid_structure=invalid)))
    rid=f'{endpoint}-{seed}-{method}-test';score=float(mean_absolute_error(test.Y,pred))
    rows.append(dict(run_id=rid,seed=seed,policy=method,dataset=endpoint,step=1,x_index=-1,y=score,mlflow_run_id='',ts=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seconds=0))
   print('test',endpoint,seed,flush=True)
  pred_df=pd.concat(store,ignore_index=True);pred_df.to_csv(ROOT/'predictions'/f'{endpoint}_test.csv.gz',index=False)
  for method in METHODS:
   for label,lo,hi in [('low',0,.3),('medium',.3,.6),('high',.6,1.000001)]:
    sub=pred_df[(pred_df.method==method)&(pred_df.similarity>=lo)&(pred_df.similarity<hi)]
    segments.append(dict(dataset=endpoint,method=method,segment=label,rows=len(sub),mae=float(np.mean(np.abs(sub.y-sub.pred))) if len(sub) else None))
 old=pd.read_csv(ROOT/'experiments.csv');pd.concat([old,pd.DataFrame(rows)]).to_csv(ROOT/'experiments.csv',index=False)
 pd.DataFrame(segments).to_csv(ROOT/'segments.csv',index=False)
 out={e:summary(e,'test')[0] for e in ENDPOINTS};(ROOT/'test_results.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
 {'audit':audit,'valid':fit_validation,'test':final_test}[sys.argv[1]]()
