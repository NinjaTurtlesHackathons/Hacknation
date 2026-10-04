#!/usr/bin/env python3
"""Independent exact replay using only the Python standard library.

The definitions below are transcribed from the manuscript, not imported from
the discovery code. Checks the half-plane/row descriptions and every pair.
Run from any directory: python3 /path/to/verify.py
"""
from collections import Counter
from pathlib import Path
import json

NORMALS = [(-2,-1),(-1,-2),(1,-1),(1,0),(2,1),(1,1),(1,2),(0,1),(-1,1),(-1,0)]
CASES = [
    (31,81,[9,9,9,5,8,5,8,5,8,5],
     [(-5,1,3),(-4,-1,4),(-3,-3,5),(-2,-3,5),(-1,-4,4),(0,-4,4),
      (1,-5,3),(2,-5,3),(3,-6,2),(4,-5,0),(5,-4,-2)]),
    (41,111,[10,11,11,7,10,6,9,6,9,6],
     [(-6,2,3),(-5,0,4),(-4,-2,5),(-3,-4,6),(-2,-4,5),(-1,-5,5),
      (0,-5,4),(1,-6,4),(2,-6,3),(3,-7,3),(4,-7,2),(5,-6,0),
      (6,-5,-2),(7,-4,-4)]),
]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify():
    references = json.loads((Path(__file__).parent/'data/witnesses.json').read_text())['datasets']
    for k,n,constants,rows in CASES:
        # The a-b and b upper caps give a finite global enumeration bound.
        a_min=-constants[-1]; a_max=constants[3]
        b_min=a_min-constants[2]; b_max=constants[7]
        points=[(a,b) for a in range(a_min,a_max+1) for b in range(b_min,b_max+1)
                if all(A*a+B*b<=C for (A,B),C in zip(NORMALS,constants))]
        row_points=[(a,b) for a,lo,hi in rows for b in range(lo,hi+1)]
        require(points==row_points, 'Half-planes and row intervals disagree')
        require(len(points)==n, 'Point count mismatch')
        histogram=Counter()
        for i,(a,b) in enumerate(points):
            for c,d in points[i+1:]:
                u,v=a-c,b-d
                # Cartesian numerator: (2 dx)^2 + (2 dy)^2 = 4d².
                numerator=(2*u+v)**2+3*v*v
                require(numerator%4==0 and numerator>0, 'Invalid squared distance')
                histogram[numerator//4]+=1
        require(len(histogram)==k, 'Distance-class count mismatch')
        require(sum(histogram.values())==n*(n-1)//2, 'Missing point pairs')
        reference=next(case for case in references if case['k']==k)
        require(points==[tuple(p) for p in reference['points']], 'Frozen point set differs')
        require(dict(histogram)=={int(q):c for q,c in reference['histogram'].items()}, 'Histogram differs')
        if k==41:
            require({(-a-b,a-1) for a,b in points}==set(points), 'Rotation fails')
            require({(b+1,a-1) for a,b in points}==set(points), 'Reflection fails')
        print(f'PASS: {n} points, exactly {k} distances, {sum(histogram.values())} unordered pairs; full histogram agrees.')
    print('Scope: exact existence statements, not global optimality or exhaustive literature novelty.')

if __name__=='__main__':
    verify()
