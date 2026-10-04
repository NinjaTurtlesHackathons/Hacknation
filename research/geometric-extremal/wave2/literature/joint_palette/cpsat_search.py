#!/usr/bin/env python3
"""Alternative Boolean constraint search, free translation/origin, exact geometry."""
import json,time,argparse,math
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import networkx as nx
from ortools.sat.python import cp_model
from search import norm,log,HERE,ROOT,OUT

def run(r,k,record,seconds,seed,hint_path=None,core_radius=None):
 t0=time.monotonic();pts=[(a,b) for a in range(-r,r+1) for b in range(-r,r+1) if abs(a+b)<=r];n=len(pts)
 pairs=[(i,j,norm(pts[i],pts[j])) for i in range(n) for j in range(i)];qs=sorted({q for _,_,q in pairs});model=cp_model.CpModel();x=[model.new_bool_var(f'x{i}') for i in range(n)];y={q:model.new_bool_var(f'y{q}') for q in qs}
 for i,j,q in pairs:model.add_bool_or([x[i].Not(),x[j].Not(),y[q]])
 model.add(sum(y.values())<=k);model.maximize(sum(x))
 graphs=defaultdict(nx.Graph)
 for i,j,q in pairs:graphs[q].add_edge(i,j)
 for q,g in graphs.items():
  edges=list(nx.max_weight_matching(g,maxcardinality=True));assert len({v for e in edges for v in e})==2*len(edges)
  alpha=n-len(edges);model.add(sum(x)<=alpha+(n-alpha)*y[q])
 # Strong exact source hint, or reproducible regular-hex fallback.
 if hint_path:
  hp=Path(hint_path);hint=json.loads(hp.read_text());chosen_hint={tuple(v) for v in hint['points']};assert len(chosen_hint)==len(hint['points']) and chosen_hint<=set(pts)
  inside=[i for i,v in enumerate(pts) if v in chosen_hint]
 else:
  hr=max(z for z in range(1,r+1) if len({norm(a,b) for a,b in combinations([(a,b) for a in range(-z,z+1) for b in range(-z,z+1) if abs(a+b)<=z],2)})<=k)
  inside=[i for i,(a,b) in enumerate(pts) if max(abs(a),abs(b),abs(a+b))<=hr]
 palette={norm(pts[i],pts[j]) for i in inside for j in inside if i>j};assert len(palette)<=k
 fixed=[]
 if core_radius is not None:
  fixed=[i for i in inside if max(abs(pts[i][0]),abs(pts[i][1]),abs(sum(pts[i])))<=core_radius]
  for i in fixed:model.add(x[i]==1)
 for i,var in enumerate(x):model.add_hint(var,int(i in inside))
 for q,var in y.items():model.add_hint(var,int(q in palette))
 # No fixed origin, no fixed anchor and no rotational/reflection restriction.
 model.export_to_file(str(HERE/f'cpsat_r{r}_k{k}_seed{seed}.txt'))
 log({'kind':'prospective_cpsat','r':r,'k':k,'record':record,'seed':seed,'time_limit_seconds':seconds,'workers':1,'vertices':n,'norm_classes':len(qs),'largest_norm':max(qs),'hint_cardinality':len(inside),'hint_distances':len(palette),'restriction':'complete finite hex window only; origin free; no symmetry constraint','method':'Boolean clauses plus cardinality and matching cuts, exact warm hint, maximize all sites','hint_path':str(hint_path),'fixed_core_radius':core_radius,'fixed_core_cardinality':len(fixed)})
 class Observer(cp_model.CpSolverSolutionCallback):
  def __init__(self):super().__init__();self.best=0
  def on_solution_callback(self):
   chosen=[pts[i] for i in range(n) if self.value(x[i])];actual=sorted({norm(a,b) for a,b in combinations(chosen,2)});assert len(actual)<=k and len(chosen)>self.best;self.best=len(chosen)
   name=f'cpsat_k{k}_n{len(chosen)}_r{r}_seed{seed}.json';path=OUT/name;path.write_text(json.dumps({'problem':'few_distance','metric':'triangular','points':chosen,'max_distances':k,'provenance':{'method':'CP-SAT joint palette','r':r,'seed':seed,'comparison_lower_bound':record,'status':'candidate improvement pending independent check' if len(chosen)>record else 'search observation below/equal published lower bound'}},indent=2)+'\n')
   log({'kind':'cpsat_incumbent','r':r,'k':k,'seed':seed,'cardinality':len(chosen),'distance_classes':len(actual),'elapsed_seconds':time.monotonic()-t0,'improves':len(chosen)>record,'artifact':str(path.relative_to(ROOT))})
 solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed;solver.parameters.log_search_progress=False;obs=Observer();status=solver.solve(model,obs)
 log({'kind':'cpsat_result','r':r,'k':k,'seed':seed,'record':record,'status':solver.status_name(status),'elapsed_seconds':time.monotonic()-t0,'best_cardinality':obs.best,'finite_bound':solver.best_objective_bound,'branches':solver.num_branches,'conflicts':solver.num_conflicts,'solver_summary':solver.response_stats(),'improves':obs.best>record,'scope':'finite model only; no global planar upper bound or independent infeasibility proof'})
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--radius',type=int,default=9);ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--targets',default='47,48,49,50');ap.add_argument('--seed',type=int,default=42600);ap.add_argument('--hint');ap.add_argument('--core-radius',type=int);a=ap.parse_args();bounds=json.loads((HERE.parent/'few_distance_k24_50.json').read_text())['bounds']
 for z,k in enumerate(map(int,a.targets.split(','))):run(a.radius,k,bounds[str(k)],a.seconds,a.seed+z,a.hint,a.core_radius)
