#!/usr/bin/env python3
"""Manuscript-only exact reproduction, standard Python. No search or generic imports."""
from collections import Counter
from pathlib import Path
import json, hashlib, math
SPEC = {'S31': {'path': 'candidates/wave2_joint_palette/k31_n81_r6_seed42102.json', 'sha256': 'a85a2a990531ebd5b40165eacb0f23c84bac6676404cb858f7b5c2c63b83d94c', 'n': 81, 'k': 31, 'pairs': 3240, 'rows': [[-5, 1, 3], [-4, -1, 4], [-3, -3, 5], [-2, -3, 5], [-1, -4, 4], [0, -4, 4], [1, -5, 3], [2, -5, 3], [3, -6, 2], [4, -5, 0], [5, -4, -2]], 'halfplanes': [[-2, -1, 9], [-1, -2, 9], [1, -1, 9], [1, 0, 5], [2, 1, 8], [1, 1, 5], [1, 2, 8], [0, 1, 5], [-1, 1, 8], [-1, 0, 5]], 'histogram': {'1': 208, '3': 189, '4': 175, '7': 314, '9': 144, '12': 135, '13': 254, '16': 115, '19': 212, '21': 198, '25': 88, '27': 81, '28': 158, '31': 146, '36': 63, '37': 112, '39': 108, '43': 98, '48': 36, '49': 110, '52': 64, '57': 54, '61': 40, '63': 36, '64': 19, '67': 28, '73': 16, '75': 9, '76': 16, '79': 10, '91': 4}}, 'S41': {'path': 'candidates/wave2_family/support_k41_n111_code7324998.json', 'sha256': '2d1216002f65a2c2cccbaa30299ea4f26c21c6f493fe3ad0e164de11ad0aa3b1', 'n': 111, 'k': 41, 'pairs': 6105, 'rows': [[-6, 2, 3], [-5, 0, 4], [-4, -2, 5], [-3, -4, 6], [-2, -4, 5], [-1, -5, 5], [0, -5, 4], [1, -6, 4], [2, -6, 3], [3, -7, 3], [4, -7, 2], [5, -6, 0], [6, -5, -2], [7, -4, -4]], 'halfplanes': [[-2, -1, 10], [-1, -2, 11], [1, -1, 11], [1, 0, 7], [2, 1, 10], [1, 1, 6], [1, 2, 9], [0, 1, 6], [-1, 1, 9], [-1, 0, 6]], 'histogram': {'1': 291, '3': 270, '4': 252, '7': 462, '9': 216, '12': 207, '13': 390, '16': 180, '19': 342, '21': 324, '25': 147, '27': 144, '28': 276, '31': 258, '36': 117, '37': 222, '39': 216, '43': 198, '48': 81, '49': 249, '52': 156, '57': 144, '61': 114, '63': 108, '64': 60, '67': 102, '73': 90, '75': 36, '76': 72, '79': 66, '81': 36, '84': 54, '91': 84, '93': 36, '97': 30, '100': 12, '103': 18, '108': 9, '109': 18, '112': 12, '127': 6}}}
BASE = Path(__file__).resolve().parents[2]
def verify():
    results=[]
    for name,s in SPEC.items():
        rows={a:(L,U) for a,L,U in s['rows']};P=sorted((a,b) for a,(L,U) in rows.items() for b in range(L,U+1))
        # The facet bounds imply [-20,20]^2 contains the entire lattice polygon.
        facets=s['halfplanes'];Alo=min(rows);Ahi=max(rows)
        assert any(A==-1 and B==0 and C==-Alo for A,B,C in facets)
        assert any(A==1 and B==0 and C==Ahi for A,B,C in facets)
        clipped=sorted((a,b) for a in range(-20,21) for b in range(-20,21) if all(A*a+B*b<=C for A,B,C in facets));assert clipped==P
        hist=Counter()
        for i,(a,b) in enumerate(P):
            for c,d in P[:i]:
                q4=(2*(a-c)+b-d)**2+3*(b-d)**2
                assert q4>0 and q4%4==0
                hist[q4//4]+=1
        assert len(P)==s['n'] and len(hist)==s['k']
        assert dict(hist)=={int(k):v for k,v in s['histogram'].items()}
        assert sum(hist.values())==math.comb(len(P),2)==s['pairs']
        raw=(BASE/s['path']).read_bytes();candidate=json.loads(raw)
        assert hashlib.sha256(raw).hexdigest()==s['sha256']
        assert sorted(map(tuple,candidate['points']))==P
        results.append({'name':name,'passed':True,'n':len(P),'distances':len(hist),'pairs':sum(hist.values()),'sha256':s['sha256']})
    return results
if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
