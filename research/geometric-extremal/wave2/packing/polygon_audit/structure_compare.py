#!/usr/bin/env python3
"""Source/candidate matching under square dihedral symmetry and label permutation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,math,sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linear_sum_assignment
HERE=Path(__file__).parent;ROOT=HERE.parents[2]
def vertices(c,a):
 angles=a[:,None]+2*np.pi/3*np.arange(3)
 return c[:,None,:]+np.stack((np.cos(angles),np.sin(angles)),axis=2)
def pair_gap(A,B):
 gaps=[]
 for P in (A,B):
  for j in range(3):
   edge=P[(j+1)%3]-P[j];normal=np.array([-edge[1],edge[0]])/np.linalg.norm(edge)
   pa=A@normal;pb=B@normal
   gaps.extend((float(min(pb)-max(pa)),float(min(pa)-max(pb))))
 return max(gaps)
def contacts(v,h,tol):
 n=len(v);edges=[];walls=[]
 for i in range(n):
  for j in range(i):
   gap=pair_gap(v[i],v[j])
   if gap<tol:edges.append([j,i])
  for dim in range(2):
   for sign in (-1,1):
    if h-max(sign*v[i,:,dim])<tol:walls.append([i,dim,sign])
 return {'pair_edges':edges,'walls':walls}
def main():
 path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'candidates/wave2_polygon/job0326.json'
 src=HERE/'current_source.txt';lines=src.read_text().splitlines();R=float(lines[1]);h0=R/math.sqrt(2);a=np.loadtxt(lines[2:]);c=a[:,:2];angles=np.pi/2-a[:,2]
 obj=json.loads(path.read_text());q=np.array([[float(F(x)) for x in row] for row in obj['triangles']]);h=float(F(obj['half_side']));cand_cent=q[:,:2];cand_angles=2*np.arctan(q[:,2]);best=None
 for reflection in (1,-1):
  for quarter in range(4):
   g=quarter*np.pi/2;rot=np.array([[np.cos(g),-np.sin(g)],[np.sin(g),np.cos(g)]]);M=rot@np.diag([1,reflection]);cent=c@M.T;ang=reflection*angles+g
   ii,jj=linear_sum_assignment(np.sum((cent[:,None,:]-cand_cent[None,:,:])**2,axis=2));cost=float(np.sum((cent[ii]-cand_cent[jj])**2))
   if best is None or cost<best[0]:best=(cost,reflection,quarter,jj,cent,ang)
 _,reflection,quarter,jj,cent,ang=best;delta=cand_cent[jj]-cent;phase=(cand_angles[jj]-ang+np.pi/3)%(2*np.pi/3)-np.pi/3
 source_vertices=vertices(cent,ang);candidate_vertices=vertices(cand_cent[jj],cand_angles[jj]);cmp={}
 for tol in (1e-8,1e-7,1e-6):
  source_contact=contacts(source_vertices,h0,tol);candidate_contact=contacts(candidate_vertices,h,tol)
  cmp[str(tol)]={'same_pair_graph':source_contact['pair_edges']==candidate_contact['pair_edges'],'same_wall_pattern':source_contact['walls']==candidate_contact['walls'],'source':source_contact,'candidate':candidate_contact}
 report={'candidate':str(path),'best_square_dihedral':{'reflection_y_sign':reflection,'quarter_turns':quarter},'candidate_labels_by_source':jj.tolist(),'max_coordinate_discrepancy':float(abs(delta).max()),'rms_center_distance':float(np.sqrt(np.mean(np.sum(delta*delta,axis=1)))),'max_orientation_discrepancy_mod_2pi_over3':float(abs(phase).max()),'source_R':R,'candidate_R':h*math.sqrt(2),'R_reduction_from_displayed':R-h*math.sqrt(2),'contact_tolerance_comparison':cmp,'interpretation':'numerical structural audit; tolerance contact graph is not a rigorous exact combinatorial certificate'}
 (HERE/'structure_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='contact_tolerance_comparison'},indent=2));print({tol:{k:v for k,v in row.items() if k.startswith('same')} for tol,row in cmp.items()})
if __name__=='__main__':main()
