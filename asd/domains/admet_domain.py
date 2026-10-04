"""ADMET adapter; validation-only agent experiments, fixed verifier tolerances."""
from .base import Domain
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'projects/admet'
sys.path.insert(0,str(ROOT))
from verifier import mae,paired,TOL
ENDPOINTS=['solubility_aqsoldb','lipophilicity_astrazeneca','caco2_wang']
class ADMETDomain(Domain):
 name='admet'
 recherche_ziel='ADMET scaffold-split prediction, molecular descriptors, Morgan fingerprints, validation reliability'
 recherche_sperre=['ADMET leaderboard','test.csv','test_results.json','Critical Assessment of ML Models']
 kontext='Supervised ADMET regression on solubility_aqsoldb, lipophilicity_astrazeneca, caco2_wang. Validation only. Fixed Morgan, descriptors, combined, median, shuffled models. No test access or tuning. Twenty overlapping scaffold splits measure fixed-dataset sensitivity, not biological replication.'
 primitive_doc='JSON {"op":"validation","args":{"endpoint":"solubility_aqsoldb"}} (also lipophilicity_astrazeneca, caco2_wang). Returns MAE for all methods and Morgan/combined ratio plus inference. No other operation allowed.'
 claim_doc='Checks: {"typ":"score","endpoint":string,"method":"median|morgan|descriptors|combined|shuffled","value":float} or {"typ":"ratio","endpoint":string,"value":float}. Validation only, absolute tolerance fixed 1e-6; no tolerance fields. Use returned full precision. Ratio Morgan/combined >1 means combined better. Answer must contain claimed numeric value in zahl. Claim only a numerical observation, no significance or mechanism.'
 def run_op(self,op,args):
  try:
   if op!='validation' or set(args)!={'endpoint'} or args['endpoint'] not in ENDPOINTS:return {'fehler':'outside frozen protocol'}
   from engine import summary
   out,rows=summary(args['endpoint']);out['comparison']=paired([r['mae'] for r in rows if r['method']=='morgan'],[r['mae'] for r in rows if r['method']=='combined']);return out
  except Exception as e:return {'fehler':str(e)[:200]}
 def check(self,p):
  try:
   typ=p.get('typ')
   if typ=='mae_anchor':
    if set(p)!={'typ','y','pred','value'}:return False,'forbidden fields',{}
    v=mae(p['y'],p['pred'])
   elif typ in ('score','ratio'):
    allowed={'typ','endpoint','value'}|({'method'} if typ=='score' else set())
    if set(p)!=allowed or p['endpoint'] not in ENDPOINTS:return False,'invalid protocol/schema',{}
    out=self.run_op('validation',{'endpoint':p['endpoint']})
    if 'fehler' in out:return False,out['fehler'],{}
    v=out[p['method']]['mean_mae'] if typ=='score' else out['comparison']['ratio']
   else:return False,'unknown check',{}
   target=p['value']
   if isinstance(target,bool) or not isinstance(target,(int,float)) or not math.isfinite(target):return False,'nonfinite claim',{}
   return abs(v-target)<=TOL,f'independent numerical value={v:.9f}; fixed tolerance={TOL}',{'value':v}
  except Exception as e:return False,'invalid check: '+str(e)[:150],{}
 def selftest(self):
  return [({'typ':'mae_anchor','y':[0,2],'pred':[1,2],'value':.5},True),({'typ':'mae_anchor','y':[1,1],'pred':[1,1],'value':0},True),({'typ':'mae_anchor','y':[0,2],'pred':[1,2],'value':.51},False),({'typ':'mae_anchor','y':[1],'pred':[1],'value':.01},False),({'typ':'mae_anchor','y':[0],'pred':[0],'value':100,'toleranz':1000},False),({'typ':'mae_anchor','y':[],'pred':[],'value':0},False),({'typ':'mae_anchor','y':[0],'pred':[float('nan')],'value':0},False),({'typ':'mae_anchor','y':[0],'pred':[0],'value':True},False),({'typ':'score','endpoint':'arbitrary','method':'combined','value':0},False),({'typ':'test_score','value':0},False)]
 def consistent(self,a,p):
  try:return math.isfinite(float(a['zahl'])) and abs(float(a['zahl'])-p['value'])<=TOL
  except:return False
 def level(self,p):return 'observed'
 def describe(self,p):return f"Fixed numerical validation {p['typ']} for {p.get('endpoint','synthetic anchor')}, method {p.get('method','Morgan/combined')}: {p['value']}. A fixed-dataset observation, not an independent clinical result."
DOMAIN=ADMETDomain()
