"""Canonical records derived from independently rescored artifacts; final paper uses these sentences verbatim."""
from pathlib import Path
from functools import lru_cache
import json,hashlib,re
import numpy as np,pandas as pd
from engine import ENDPOINTS,summary
from verifier import paired,bh
ROOT=Path(__file__).resolve().parent

@lru_cache(maxsize=1)
def records():
 out={}
 def put(key,text,level='observed'):out[key]={'text':text,'level':level}
 cov=pd.read_csv(ROOT/'coverage.csv');ex=pd.read_csv(ROOT/'experiments.csv');v=json.loads((ROOT/'verification.json').read_text());assert v['passed']
 for name,h in json.loads((ROOT/'release_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
 put('scope',f'This reproducible pilot compares fixed molecular representations on three preregistered TDC ADMET regression endpoints; the structural audit covers {cov.dataset.nunique()} endpoints and {len(cov)} source files; the pilot does not establish clinical utility, a leaderboard record, a novel representation algorithm, or accelerated scientific discovery')
 put('design','The primary question is whether adding ten fixed physicochemical descriptors to radius-two 1024-bit Morgan fingerprints lowers solubility scaffold-validation MAE; identical lipophilicity and Caco-2 comparisons are secondary; the objective is mean absolute error in the distributed target units, with no test-based method selection')
 put('methods','All learned models use LightGBM with 200 trees, learning rate 0.05, 15 leaves, minimum 20 samples per leaf, L2 penalty 1, two CPU threads and deterministic execution; descriptors are molecular weight, logP, TPSA, hydrogen-bond donors and acceptors, rotatable bonds, rings, fraction sp3, heavy atoms and aromatic rings; descriptor-only and fingerprint-only models are ablations, the training-target median is the naive baseline, and shuffled training targets define the negative control')
 put('splits','Seeds 1000 through 1019 use the TDC scaffold splitter with train/validation/test fractions 0.875/0.125/0 inside train_val; an explicit source-row column survives index resetting; each saved model is evaluated on the official fixed test set without refitting on validation observations; no early stopping or hyperparameter search is performed; seeds 1000 through 1004 are also exported but are not asserted to be an official leaderboard seed protocol')
 put('inference','The preregistered comparison uses paired one-sided sign flips with 20000 Monte Carlo draws and a plus-one correction, 5000 paired bootstrap resamples, and Benjamini-Hochberg at q=0.1; the primary hypothesis family has three endpoint comparisons; overlapping splits and reused test molecules make the intervals and p-values conditional sensitivity summaries rather than independent biological replication or prospective population inference')
 put('audit',f'The source audit found {int(cov.missing_y.sum())} missing targets, {int(cov.loc[cov.split=="train_val","invalid"].sum())} invalid training structures, {int(cov.loc[cov.split=="test","invalid"].sum())} invalid test structures, and {int(cov.loc[cov.split=="test","canonical_overlap"].sum())} canonical-molecule overlaps and {int(cov.loc[cov.split=="test","scaffold_overlap"].sum())} scaffold overlaps across train_val/test; within-split duplicates remain as distributed, so row-weighted scores need not equal unique-molecule-weighted scores')
 put('invalid','Before any successful model fit or score inspection, two solubility test SMILES failed strict RDKit parsing; a documented amendment preserves both rows and uses the training-target median for every method on these structures, marks them invalid, and assigns similarity zero; no chemical repair or silent deletion is performed; structural audit read target completeness but no test score guided the amendment')
 put('precommit','The protocol document existed before computation; a working-directory error prevented the intended first commit and the following training command failed a row-alignment assertion before any model fit or score inspection; the document and correction were committed before successful experiments; therefore strict commit-before-first-computation compliance is not claimed')
 put('verification',f'The domain verifier passed {len(v["selftest"])} true/false, nonfinite, malformed, empty-input and self-assigned-tolerance selftests; an independently generated linear target is recovered at MAE {v["checks"]["synthetic_recovery"]["mae"]:.12g}, whereas shuffled synthetic training labels yield MAE {v["checks"]["synthetic_recovery"]["shuffled_mae"]:.6f}; the release validates all {len(ex)} experiment records and source-grounded predictions, and excludes nonfinite outputs and incomplete seed/method/row groups')
 put('trust','The agent-facing laboratory exposes validation summaries only through domain.run_op; no benchmark molecular identities, per-molecule target rows or test scores are provided through these agent-facing operations; neutral identifier invariance follows from feature computation using SMILES alone and named endpoint labels without molecular identities; this narrower exposure check cannot certify absence of LLM training-corpus contamination or protect against a malicious process with filesystem access')
 put('redteam','Independent review verified source-row alignment, disjoint molecular/scaffold partitions and rescoring, and reproduced saved seed-1000 predictions; it also found that a mutable prediction table could spoof the original scorer and that the shared manuscript gate checks numerical token membership rather than semantic truth; source grounding and frozen prediction hashes now reject the demonstrated target and hash tampering, while the final manuscript uses canonical verified state records rather than relying on the shared sentence gate alone')
 put('freeze','All model files, split indices and validation predictions were hashed before the first final-test score; after scoring, only verifier grounding and documentation were hardened; the original seal is retained, its engine/document hash differences are disclosed, and release_hashes records the hardened implementation and unchanged prediction artifacts')
 put('limitations','This pilot uses a single public benchmark snapshot and fixed model hyperparameters; it lacks prospective temporal validation, independent new assays, clinical evaluation, external expert review, and a comparison against competitive tuned models; descriptor effects cannot identify causal chemical mechanisms; a held-out benchmark result is evidence about the distributed assay targets, not patient safety')
 put('novelty','Fingerprint and descriptor combinations, scaffold evaluation, and applicability-domain analysis have substantial prior art; the contribution here is an executed, auditable endpoint-specific ablation with falsification checks, rather than a new algorithm or a demonstrated publication-level scientific discovery; stronger impact requires replication and a specific mechanism or methodological improvement that survives stronger baselines')
 put('platform','The run is local CPU research; Databricks, Unity Catalog and Spark have not been provisioned or tested; the experiment, claim and gate tables are the authoritative release inputs and can be imported into a platform integration; no live cloud deployment is claimed')
 ps=[];controls=[];comparisons=[]
 for endpoint in ENDPOINTS:
  va,vr=summary(endpoint);te,tr=summary(endpoint,'test');cmp=paired([r['mae'] for r in vr if r['method']=='morgan'],[r['mae'] for r in vr if r['method']=='combined']);ps.append(cmp['p']);comparisons.append(cmp)
  for stage,rows in [('validation',vr),('test',tr)]:controls.append((endpoint,stage,paired([r['mae'] for r in rows if r['method']=='median'],[r['mae'] for r in rows if r['method']=='shuffled'])))
  vals='; '.join(f'{m}: {te[m]["mean_mae"]:.6f} +/- {te[m]["sd_mae"]:.6f}' for m in ['median','morgan','descriptors','combined','shuffled']);gain=100*(1-te['combined']['mean_mae']/te['morgan']['mean_mae'])
  put('test-'+endpoint,f'On the fixed {endpoint} test set, across 20 training seeds, MAE mean +/- seed standard deviation is {vals}; adding descriptors to Morgan reduces mean test MAE by {gain:.2f}% relative to Morgan alone; this is a conditional descriptive comparison with every official test row retained')
  put('valid-'+endpoint,f'For {endpoint} validation, Morgan MAE is {va["morgan"]["mean_mae"]:.6f}, descriptors MAE is {va["descriptors"]["mean_mae"]:.6f}, and combined MAE is {va["combined"]["mean_mae"]:.6f}; the paired Morgan/combined ratio is {cmp["ratio"]:.6f}, with bootstrap 95% interval [{cmp["ci_low"]:.6f}, {cmp["ci_high"]:.6f}] and nominal one-sided p={cmp["p"]:.8f}', 'statistical')
  df=pd.read_csv(ROOT/'predictions'/f'{endpoint}_test.csv.gz');clean=df[~df.invalid_structure.astype(bool)];clean_mae=np.abs(clean[clean.method=='combined'].y-clean[clean.method=='combined'].pred).mean()
  n=len(df[(df.seed==1000)&(df.method=='combined')]);counts=[len(pd.read_csv(ROOT/'predictions'/f'{endpoint}_valid.csv.gz').query('seed==@seed and method=="combined"')) for seed in range(1000,1020)]
  put('coverage-'+endpoint,f'{endpoint} has {n} fixed test rows, validation size ranges from {min(counts)} to {max(counts)} rows across seeds, and combined MAE restricted to strictly valid test structures is {clean_mae:.6f}; unequal validation sizes are induced by whole-scaffold groups, not silent row removal')
 gains=[]
 for e in ENDPOINTS:
  t,_=summary(e,'test');gains.append(100*(1-t['combined']['mean_mae']/t['morgan']['mean_mae']))
 put('abstract',f'We evaluate a preregistered representation ablation for ADMET prediction with fixed CPU gradient-boosted models and an independently audited scorer; adding ten physicochemical descriptors to Morgan fingerprints reduces fixed-test mean absolute error by {gains[0]:.2f}% for solubility, {gains[1]:.2f}% for lipophilicity and {gains[2]:.2f}% for Caco-2 permeability across twenty training seeds; descriptor-only ablations expose endpoint dependence and shuffled-label controls provide falsification checks; an audit covers twenty-two benchmark endpoints and preserves two invalid-structure test rows through a frozen median fallback; overlapping splits, public labels, assay heterogeneity and absent prospective validation limit interpretation; this pilot establishes endpoint-specific performance against fixed baselines, not a new algorithm, leaderboard record or clinical result')
 allps=ps+[z['p'] for _,_,z in controls];rej,adj=bh(allps)
 for i,e in enumerate(ENDPOINTS):
  primary_reject,_=bh(ps)
  success=primary_reject[i] and ps[i]<.05 and comparisons[i]['ci_low']>1
  outcome='passes' if success else 'fails'
  put('gate-'+e,f'The {e} validation comparison {outcome} the preregistered improvement criteria on this fixed dataset; after including all six additional negative-control comparisons in an expanded family of nine tests, the BH-adjusted p-value is {adj[i]:.8f}; the larger family is a post-preregistration sensitivity check and does not strengthen prospective inference','statistical')
 for endpoint,stage,z in controls:put('null-'+endpoint+'-'+stage,f'The {endpoint} {stage} shuffled-label control has median-baseline/shuffled MAE ratio {z["ratio"]:.6f}, bootstrap 95% interval [{z["ci_low"]:.6f}, {z["ci_high"]:.6f}], and nominal improvement p={z["p"]:.8f}; it does not meet the improvement gate; failure to detect improvement is not proof of independence','statistical')
 seg=pd.read_csv(ROOT/'segments.csv');text=[]
 for e in ENDPOINTS:
  ss=seg[(seg.dataset==e)&(seg.method=='combined')]
  text.append(e+': '+', '.join(f'{r.segment} n-seed-row={r.rows}, MAE={r.mae:.6f}' for r in ss.itertuples() if pd.notna(r.mae)))
 put('segments','Exploratory nearest-training Morgan Tanimoto strata use thresholds 0.3 and 0.6; the pooled seed-row errors for the combined model are '+ '; '.join(text)+'; counts reuse test molecules across seeds and are not unique molecule counts; these fixed descriptive strata neither certify an applicability domain nor explain a causal mechanism')
 lean=(ROOT/'lean_check.txt').read_text();assert 'error:' not in lean and 'depends on axioms' in lean
 axioms=re.search(r'depends on axioms: \[(.*?)\]',lean).group(1)
 put('lean',f'A Lean 4 core proof checks that the sum of natural absolute values of integer residuals is zero exactly when every residual is zero; its trusted axioms are {axioms}; this arithmetic anchor does not certify floating-point model fitting, statistical significance, chemical mechanism or clinical validity','proved_lean')
 if (ROOT/'state.json').exists():
  state=json.loads((ROOT/'state.json').read_text());put('agents',f'The repository laboratory executed {len(state["runden"])} recorded agent rounds, with {sum(c["status"]=="bestätigt" for c in state["claims"] if c["id"].startswith("admet-R"))} confirmed recorded claims before release enrichment and {len(state["widerlegt"])} recorded unsuccessful questions; model fitting was a preregistered fixed experiment matrix, while agents inspected validation summaries and proposed checked numerical statements; no agent-discovery speedup was measured')
 if (ROOT/'references_crossref.json').exists():
  for i,r in enumerate(json.loads((ROOT/'references_crossref.json').read_text())):
   if r['status']=='VERIFIED':put('ref-'+str(i),r['author']+': '+r['title']+'; DOI '+r['doi']+'; '+r['url']+'; title/DOI verified through Crossref or Europe PMC; existence verification does not reproduce the paper findings')
 replica=json.loads((ROOT/'reproduction.json').read_text())
 assert replica['engine_sha256']==hashlib.sha256((ROOT/'engine.py').read_bytes()).hexdigest()
 assert replica['provenance']['files']==json.loads((ROOT/'provenance.json').read_text())['files']
 deltas=[]
 for e in ENDPOINTS:
  current,_=summary(e,'test')
  for m in ['median','morgan','descriptors','combined','shuffled']:deltas.append(abs(current[m]['mean_mae']-replica['test_results'][e][m]['mean_mae']))
 assert max(deltas)<1e-8
 put('reproduction',f'A separate fresh numerical run downloaded identical source CSV hashes, refitted the entire fixed experiment matrix, froze models before test scoring and reproduced all {len(deltas)} endpoint-method mean test MAEs within absolute tolerance 1e-8; the maximum mean-MAE difference was {max(deltas):.12g}; numerical reproduction strengthens implementation evidence but is not an independent biological replication')
 put('ref-tdc','Therapeutics Data Commons: ADMET Benchmark Group; official benchmark documentation, accessed 4 October 2026; https://tdcommons.ai/benchmark/admet_group/overview/; https://dataverse.harvard.edu/api/access/datafile/4426004; raw snapshot hashes are recorded in provenance.json')
 return out
