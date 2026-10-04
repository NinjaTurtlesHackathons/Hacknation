#!/usr/bin/env python3
"""Scientific vector figure from frozen exact witnesses; matplotlib only.
Run: python3 research/geometric-extremal/demo/figure_few_distance.py
Optional --preview /absolute/path.png for visual inspection.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import argparse, hashlib, json, math, datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

BASE=Path(__file__).resolve().parents[1]
CASES=[
 {'path':'candidates/wave2_joint_palette/k31_n81_r6_seed42102.json','sha':'a85a2a990531ebd5b40165eacb0f23c84bac6676404cb858f7b5c2c63b83d94c','n':81,'k':31,'baseline':80,'highlight_q':91,'highlight_pairs':4,'color':'#bd3a33'},
 {'path':'candidates/wave2_family/support_k41_n111_code7324998.json','sha':'2d1216002f65a2c2cccbaa30299ea4f26c21c6f493fe3ad0e164de11ad0aa3b1','n':111,'k':41,'baseline':109,'highlight_q':127,'highlight_pairs':6,'color':'#176c86'},
]
def determinant(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
def hull(points):
 p=sorted(points);lo=[];hi=[]
 for v in p:
  while len(lo)>1 and determinant(lo[-2],lo[-1],v)<=0:lo.pop()
  lo.append(v)
 for v in reversed(p):
  while len(hi)>1 and determinant(hi[-2],hi[-1],v)<=0:hi.pop()
  hi.append(v)
 return lo[:-1]+hi[:-1]
def load(c):
 raw=(BASE/c['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==c['sha'],'Frozen witness changed'
 d=json.loads(raw);p=sorted(map(tuple,d['points']));assert len(p)==c['n']==len(set(p));assert all(type(a)is int and type(b)is int for a,b in p)
 hist=Counter();selected=[]
 for a,b in combinations(p,2):
  u=a[0]-b[0];v=a[1]-b[1];q=u*u+u*v+v*v;assert q>0;hist[q]+=1
  if q==c['highlight_q']:selected.append((a,b))
 assert len(hist)==c['k'] and len(selected)==c['highlight_pairs'];assert sum(hist.values())==math.comb(c['n'],2)
 return p,selected

def main(preview=None):
 matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'ai-agent-lab-few-distance-20261004','pdf.fonttype':42,'axes.unicode_minus':False})
 fig,axs=plt.subplots(1,2,figsize=(10.7,6.75));fig.subplots_adjust(left=.045,right=.955,bottom=.17,top=.80,wspace=.17)
 fig.suptitle('Two exact planar few-distance constructions',x=.5,y=.968,fontsize=17,fontweight='bold',color='#1c2733')
 fig.text(.5,.918,'Improved construction bounds relative to Ahmed–Snevily (2013)',ha='center',fontsize=10.6,color='#56616c')
 descriptions=[]
 for idx,(ax,c) in enumerate(zip(axs,CASES)):
  p,selected=load(c);mean_a=sum(a for a,b in p)/len(p);mean_b=sum(b for a,b in p)/len(p)
  # Common scale and only a translation for presentation; all exact checks above.
  def embedding(v):
   a=v[0]-mean_a;b=v[1]-mean_b;return(a+b/2,math.sqrt(3)*b/2)
  xy=[embedding(v) for v in p];poly=[embedding(v) for v in hull(p)];px,py=zip(*poly)
  ax.fill(px,py,facecolor='#edf0f3',edgecolor='#a7afb7',linewidth=.85,zorder=0)
  lines=[[embedding(a),embedding(b)] for a,b in selected];ax.add_collection(LineCollection(lines,colors=c['color'],linewidths=1.5,alpha=.87,zorder=1))
  ax.scatter(*zip(*xy),s=17,c='#25323c',edgecolors='white',linewidths=.24,zorder=2)
  ends={v for ab in selected for v in ab};ax.scatter(*zip(*(embedding(v) for v in sorted(ends))),s=28,c=c['color'],edgecolors='white',linewidths=.35,zorder=3)
  ax.set_aspect('equal',adjustable='box');ax.set_xlim(-6.2,6.2);ax.set_ylim(-6.3,6.3);ax.axis('off')
  ax.text(.0,1.145,f"({chr(97+idx)})  {c['n']} points · {c['k']} distances",transform=ax.transAxes,fontsize=13,fontweight='bold',color='#1c2733')
  ax.text(.0,1.065,rf"$G({c['k']})\geq {c['n']}$   ·   published bound: {c['baseline']}",transform=ax.transAxes,fontsize=10.8,color='#56616c')
  ax.text(.5,-.085,rf"$d^2={c['highlight_q']}$: {c['highlight_pairs']} highlighted pairs",transform=ax.transAxes,ha='center',fontsize=11,color=c['color'])
  descriptions.append(f"{c['n']} distinct points; {c['k']} distinct distances; highlighted squared distance {c['highlight_q']} occurs in {len(selected)} unordered pairs; source SHA256 {c['sha']}")
 # One explicit unit bar uses the identical data scale in both panels.
 ax=axs[0];ax.plot([-5.5,-4.5],[-6.05,-6.05],color='#56616c',linewidth=1);ax.plot([-5.5,-5.5],[-6.15,-5.95],color='#56616c',linewidth=.8);ax.plot([-4.5,-4.5],[-6.15,-5.95],color='#56616c',linewidth=.8);ax.text(-5,-5.8,'1 unit',ha='center',fontsize=8.3,color='#56616c')
 fig.text(.5,.050,'Identical unit spacing in both panels; coordinates translated for display. Faint regions are the filled convex hulls.',ha='center',fontsize=8.4,color='#56616c')
 desc='; '.join(descriptions)+'. All pair counts verified with integer triangular norm a²+ab+b² before plotting. Historical comparison values are point counts, not displayed historical coordinates.'
 stamp=datetime.datetime(2026,10,4,tzinfo=datetime.timezone.utc)
 out=Path(__file__).parent
 fig.savefig(out/'few_distance_figure.svg',metadata={'Title':'Exact planar few-distance constructions','Description':desc,'Creator':'AI Agent Lab; exact frozen witness plotting','Date':stamp.isoformat()})
 fig.savefig(out/'few_distance_figure.pdf',metadata={'Title':'Exact planar few-distance constructions','Subject':desc,'Creator':'AI Agent Lab; matplotlib vector figure','CreationDate':stamp,'ModDate':stamp})
 if preview:fig.savefig(preview,dpi=170)
 print(json.dumps({'passed':True,'figure_paths':[str(out/'few_distance_figure.svg'),str(out/'few_distance_figure.pdf')],'cases':descriptions,'common_data_limits':[-6.2,6.2,-6.3,6.3],'matplotlib_version':matplotlib.__version__},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--preview');args=a.parse_args();main(args.preview)
