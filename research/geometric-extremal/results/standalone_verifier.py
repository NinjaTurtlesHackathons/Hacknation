#!/usr/bin/env python3
"""Self-contained exact witness replay: no package, archive or network needed.

Coordinates(a,b) embed as(a+b/2,sqrt(3)b/2). The direct integer norm
computation is the separate literature critic's verifier formula, packaged
here with both frozen point lists by the director. This is not an optimality
or novelty oracle. Full provenance/hashes/alternative Cartesian verifier
and polygon-completeness proof are in the research archive.
"""
import itertools,json
RECORDS=[{'id': 'GE-LOWER-G31', 'n': 81, 'k': 31, 'points': [[-5, 1], [-5, 2], [-5, 3], [-4, -1], [-4, 0], [-4, 1], [-4, 2], [-4, 3], [-4, 4], [-3, -3], [-3, -2], [-3, -1], [-3, 0], [-3, 1], [-3, 2], [-3, 3], [-3, 4], [-3, 5], [-2, -3], [-2, -2], [-2, -1], [-2, 0], [-2, 1], [-2, 2], [-2, 3], [-2, 4], [-2, 5], [-1, -4], [-1, -3], [-1, -2], [-1, -1], [-1, 0], [-1, 1], [-1, 2], [-1, 3], [-1, 4], [0, -4], [0, -3], [0, -2], [0, -1], [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, -5], [1, -4], [1, -3], [1, -2], [1, -1], [1, 0], [1, 1], [1, 2], [1, 3], [2, -5], [2, -4], [2, -3], [2, -2], [2, -1], [2, 0], [2, 1], [2, 2], [2, 3], [3, -6], [3, -5], [3, -4], [3, -3], [3, -2], [3, -1], [3, 0], [3, 1], [3, 2], [4, -5], [4, -4], [4, -3], [4, -2], [4, -1], [4, 0], [5, -4], [5, -3], [5, -2]], 'palette': [1, 3, 4, 7, 9, 12, 13, 16, 19, 21, 25, 27, 28, 31, 36, 37, 39, 43, 48, 49, 52, 57, 61, 63, 64, 67, 73, 75, 76, 79, 91]}, {'id': 'GE-LOWER-G41', 'n': 111, 'k': 41, 'points': [[-6, 2], [-6, 3], [-5, 0], [-5, 1], [-5, 2], [-5, 3], [-5, 4], [-4, -2], [-4, -1], [-4, 0], [-4, 1], [-4, 2], [-4, 3], [-4, 4], [-4, 5], [-3, -4], [-3, -3], [-3, -2], [-3, -1], [-3, 0], [-3, 1], [-3, 2], [-3, 3], [-3, 4], [-3, 5], [-3, 6], [-2, -4], [-2, -3], [-2, -2], [-2, -1], [-2, 0], [-2, 1], [-2, 2], [-2, 3], [-2, 4], [-2, 5], [-1, -5], [-1, -4], [-1, -3], [-1, -2], [-1, -1], [-1, 0], [-1, 1], [-1, 2], [-1, 3], [-1, 4], [-1, 5], [0, -5], [0, -4], [0, -3], [0, -2], [0, -1], [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, -6], [1, -5], [1, -4], [1, -3], [1, -2], [1, -1], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, -6], [2, -5], [2, -4], [2, -3], [2, -2], [2, -1], [2, 0], [2, 1], [2, 2], [2, 3], [3, -7], [3, -6], [3, -5], [3, -4], [3, -3], [3, -2], [3, -1], [3, 0], [3, 1], [3, 2], [3, 3], [4, -7], [4, -6], [4, -5], [4, -4], [4, -3], [4, -2], [4, -1], [4, 0], [4, 1], [4, 2], [5, -6], [5, -5], [5, -4], [5, -3], [5, -2], [5, -1], [5, 0], [6, -5], [6, -4], [6, -3], [6, -2], [7, -4]], 'palette': [1, 3, 4, 7, 9, 12, 13, 16, 19, 21, 25, 27, 28, 31, 36, 37, 39, 43, 48, 49, 52, 57, 61, 63, 64, 67, 73, 75, 76, 79, 81, 84, 91, 93, 97, 100, 103, 108, 109, 112, 127]}]

def verify(r):
 p=r['points']
 if len(p)!=r['n'] or any(len(x)!=2 or any(type(v) is not int for v in x) for x in p):raise ValueError('Coordinates/count')
 if len(set(map(tuple,p)))!=len(p):raise ValueError('Duplicate point')
 histogram={}
 for x,y in itertools.combinations(p,2):
  a,b=x[0]-y[0],x[1]-y[1];q=a*a+a*b+b*b
  if q<=0:raise ValueError('Degenerate pair')
  histogram[q]=histogram.get(q,0)+1
 if len(histogram)!=r['k'] or sorted(histogram)!=r['palette']:raise ValueError('Distance classes')
 return dict(id=r['id'],passed=True,points=len(p),distances=len(histogram),pairs=sum(histogram.values()),squared_distances=sorted(histogram))
if __name__=='__main__':print(json.dumps([verify(r) for r in RECORDS],indent=2))
