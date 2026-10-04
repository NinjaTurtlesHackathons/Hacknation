#!/usr/bin/env python3
"""Circle packing in apothem-one regular octagon; shell/bulk programs."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,time,math,itertools,argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize
HERE=Path(__file__).parent;ROOT=HERE.parents[2];OUT=ROOT/'candidates/wave2_packing3'
LOG=HERE/'experiments.jsonl';C=math.cos(math.pi/8)
BENCH={28:'0.160404294689',29:'0.154929849312',30:'0.152319579409',31:'0.149878153406',32:'0.147297380425',33:'0.145306599845'}
angles=np.arange(8)*np.pi/4;NORMALS=np.column_stack((np.cos(angles),np.sin(angles)))
def record(row):
 with LOG.open('a') as f:f.write(json.dumps(row)+'\n')
def verify(o):
 if o['problem']!='circle_packing_octagon_apothem':raise ValueError('Problem')
 def frac(x):
  if type(x) not in (str,int):raise ValueError('Rational literal required')
  return F(x)
 r=frac(o['radius']);pts=[tuple(map(frac,p)) for p in o['points']];n=len(pts)
 if type(o['n'])!=int or n!=o['n'] or n<=0 or r<=0 or r>1 or any(len(p)!=2 for p in pts):raise ValueError('Dimension/radius')
 for x,y in pts:
  if abs(x)>1-r or abs(y)>1-r or (abs(x)+abs(y))**2>2*(1-r)**2:raise ValueError('Octagon wall')
 for i,(x,y) in enumerate(pts):
  for X,Y in pts[:i]:
   if (x-X)**2+(y-Y)**2<4*r*r:raise ValueError('Circle overlap')
 ans={'passed':True,'n':n,'pairs':n*(n-1)//2,'radius_apothem_one':str(r),'original_radius_squared_Qsqrt2':{'rational':str(r*r/2),'sqrt2_coefficient':str(r*r/4)}}
 if 'benchmark_radius_upper' in o:
  benchmark=frac(o['benchmark_radius_upper']);factor=frac(o.get('required_ratio','1'))
  a=r*r/2-(benchmark*factor)**2;b=r*r/4
  better=a>=0 or 2*b*b>a*a
  ans.update(improves_benchmark_with_required_ratio=better,required_ratio=str(factor))
 return ans
def actual_radius(p):
 i,j=np.triu_indices(len(p),1)
 return min(float((1-p@NORMALS.T).min()),float(np.sqrt(np.sum((p[i]-p[j])**2,axis=1).min())/2))
def constraints(p,r):
 i,j=np.triu_indices(len(p),1);return np.r_[np.sum((p[i]-p[j])**2,axis=1)-4*r*r,(1-r-p@NORMALS.T).ravel()]
def free(p,r):
 n=len(p);i,j=np.triu_indices(n,1);m=len(i)
 def con(z):return constraints(z[:-1].reshape(n,2),z[-1])
 def jac(z):
  q=z[:-1].reshape(n,2);v=q[i]-q[j];J=np.zeros((m+8*n,2*n+1));J[:m,-1]=-8*z[-1]
  for k in range(2):J[np.arange(m),2*i+k]=2*v[:,k];J[np.arange(m),2*j+k]=-2*v[:,k]
  J[m:,-1]=-1
  for a in range(n):J[m+8*a:m+8*a+8,2*a:2*a+2]=-NORMALS
  return J
 z=np.r_[p.ravel(),max(.02,min(r,actual_radius(p)))];t=time.monotonic()
 res=minimize(lambda z:-z[-1],z,jac=lambda z:np.r_[np.zeros(len(z)-1),-1],method='SLSQP',constraints={'type':'ineq','fun':con,'jac':jac},bounds=[(-1,1)]*(2*n)+[(.02,.3)],options={'maxiter':600,'ftol':1e-12})
 q=res.x[:-1].reshape(n,2);return q,actual_radius(q),{'success':bool(res.success),'iterations':int(res.nit),'min_constraint':float(con(res.x).min()),'seconds':time.monotonic()-t}
def certify(p,r,name,meta):
 for shrink in (5e-12,5e-11,5e-10,5e-9):
  rr=max(0,r-shrink);o={'problem':'circle_packing_octagon_apothem','n':len(p),'radius':f'{rr:.14f}','points':[[f'{x:.14f}',f'{y:.14f}'] for x,y in p],'benchmark_radius_upper':str(F(BENCH[len(p)])+F('0.000000000001')),'required_ratio':'10001/10000','provenance':meta}
  try:cert=verify(o)
  except ValueError:continue
  path=OUT/(name+'.json');path.write_text(json.dumps(o,indent=2)+'\n');return cert,str(path.relative_to(ROOT))
 return None,None
T=math.sqrt(2)-1
POLY=np.array([(1,T),(T,1),(-T,1),(-1,T),(-1,-T),(-T,-1),(T,-1),(1,-T)])
def shell(m,clock):
 u=(np.arange(m)/m+clock)%1*8;k=np.floor(u).astype(int);f=u-k
 return POLY[k]*(1-f[:,None])+POLY[(k+1)%8]*f[:,None]
def bulk_cells(count,pattern):
 v=np.array([(i+j/2,math.sqrt(3)*j/2) for i in range(-5,6) for j in range(-5,6)])
 offset=[(0,0),(.5,0),(.25,math.sqrt(3)/4),(.5,math.sqrt(3)/6)][pattern]
 v-=offset;d=np.sum(v*v,axis=1);order=np.lexsort((v[:,1],v[:,0],d));return v[order[:count]]
def motif(n,m,phase,turn,pattern):
 cells=bulk_cells(n-m,pattern)
 def build(z):
  r,clock,theta,x,y=z;rot=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
  return np.vstack(((1-r)*shell(m,clock),2*r*cells@rot.T+[x,y]))
 z=np.array([float(BENCH[n])/C,phase/m,turn*np.pi/48,0.,0.]);t=time.monotonic()
 res=minimize(lambda z:-z[0],z,method='SLSQP',constraints={'type':'ineq','fun':lambda z:constraints(build(z),z[0])},bounds=[(.02,.3),(0,1/m),(-np.pi/12,np.pi/2),(-.3,.3),(-.3,.3)],options={'maxiter':180,'ftol':1e-11})
 p=build(res.x);return p,actual_radius(p),{'success':bool(res.success),'iterations':int(res.nit),'seconds':time.monotonic()-t,'parameters':res.x.tolist(),'min_constraint':float(constraints(p,res.x[0]).min())}
def source_shell_surgery(p,r,index):
 # Pivot changes shell face assignment; retains bulk centers and rotates a
 # coherent group of shell centers by one or two octagonal faces.
 slack=1-r-p@NORMALS.T;ids=np.where(slack.min(axis=1)<1e-6)[0]
 chosen=ids[index%len(ids):][:3]
 if len(chosen)<3:chosen=ids[:3]
 direction=1 if index%2 else -1;angle=direction*(1+index//2%2)*np.pi/4
 rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);q=p.copy();q[chosen]=q[chosen]@rot.T
 return q,{'shell_labels':chosen.tolist(),'integer_face_shift':direction*(1+index//2%2),'bulk_fixed_start':True}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=300);args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 record({'kind':'prospective','seed_base':60000,'workers':1,'wall_cap_seconds':args.seconds,'N_range':[28,33],'methods':['regular_offset_boundary_shell_plus_rotated_triangular_bulk','pivot_coherent_source_shell_face_reassignment'],'success':'exact radius ratio>=1.0001 over freshly published upper comparator; no tiny polish record claim','stop':'100 consecutive nonimproving motif jobs triggers representation pivot;100 stagnant pivot jobs stops'})
 states={};best={};source={};start=time.monotonic()
 for n in range(28,34):
  p=np.loadtxt(HERE/f'source/coc{n}.txt')[:,1:]/C;r=actual_radius(p);source[n]=p;states[n]=p;best[n]=r
  cert,path=certify(p,r,f'baseline_n{n}',{'source':'Specht23-Sep2026','normalization':'coordinates divided by cos(pi/8)'})
  assert cert
  record({'kind':'baseline','n':n,'radius_apothem':r,'published_radius':BENCH[n],'exact_certificate':cert,'artifact':path})
 jobs=[(n,m,phase,turn,pattern) for m in range(12,19) for turn in range(8) for phase in (0,.25,.5,.75) for pattern in range(4) for n in range(28,34)]
 stale=0;done=0;pivot=False
 for n,m,phase,turn,pattern in jobs:
  if time.monotonic()-start>args.seconds:break
  seed=60000+done;job=time.monotonic();p,r,mi=motif(n,m,phase,turn,pattern);q,rr,fi=free(p,r)
  row={'kind':'motif_result','seed':seed,'n':n,'shell_count':m,'shell_clock_start':phase/m,'bulk_turn_start':turn*np.pi/48,'bulk_cut_pattern':pattern,'motif':mi,'free':fi,'published_radius_result':rr*C,'starting_motif_radius':r,'whole_seconds':time.monotonic()-job}
  improved=rr>best[n]+1e-10
  if improved:
   cert,path=certify(q,rr,f'best_n{n}',row)
   if cert:best[n]=rr;states[n]=q;row.update(exact_certificate=cert,artifact=path)
  stale=0 if improved else stale+1;done+=1;record(row)
  if done%20==0:print(json.dumps({'jobs':done,'seconds':time.monotonic()-start,'best_original_radius':{n:best[n]*C for n in best},'stale':stale}),flush=True)
  if stale>=100:pivot=True;record({'kind':'adaptive_pivot','after_jobs':done,'reason':'100 stagnant motif programs','next':'coherent source boundary-face reassignment'});break
 if pivot:
  stale=0
  for index in range(150):
   if time.monotonic()-start>args.seconds:break
   n=28+index%6;p,pr=source_shell_surgery(states[n],best[n],index//6);q,rr,fi=free(p,best[n]);row={'kind':'shell_face_result','seed':70000+index,'n':n,'program':pr,'free':fi,'published_radius_result':rr*C}
   improved=rr>best[n]+1e-10
   if improved:
    cert,path=certify(q,rr,f'best_n{n}',row)
    if cert:best[n]=rr;states[n]=q;row.update(exact_certificate=cert,artifact=path)
   stale=0 if improved else stale+1;record(row)
   if stale>=100:record({'kind':'stop','reason':'100 stagnant boundary-face reassignment jobs'});break
 record({'kind':'complete','motif_jobs':done,'whole_campaign_seconds':time.monotonic()-start,'best_original_radius':{n:best[n]*C for n in best},'published_baseline':BENCH,'interpretation':'exact witness gate governs claims; local minima are not global optima'})
if __name__=='__main__':main()
