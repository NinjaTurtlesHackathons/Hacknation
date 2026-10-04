#!/usr/bin/env python3
"""Standalone integer support-envelope and norm audit; no discovery imports."""
from pathlib import Path
import json,itertools
B=Path(__file__).resolve().parents[2]
Q=lambda a,b:a*a+a*b+b*b
vec={(a,b) for a in range(-13,14) for b in range(-13,14) if (a or b) and abs(a+b)<=13 and max(abs(2*a+b),abs(a+2*b),abs(a-b))<=20}
norms={Q(*v) for v in vec};assert len(vec)==420 and len(norms)==41 and max(norms)==127
# Completing squares bounds BOTH coordinates of representations bysqrt(4q/3).
rep111={(a,b) for a in range(-12,13) for b in range(-12,13) if Q(a,b)==111}
assert len(rep111)==12
orbit=set()
for reflected in [False,True]:
 a,b=(1,10) if reflected else (10,1)
 for k in range(6):orbit.add((a,b));a,b=-b,a+b
assert orbit==rep111 and orbit.isdisjoint(vec)
# To bound all positive representable norms<=127: 3a²<=4Q, idem b, hence |a|,|b|<=13.
allnorms=sorted({Q(a,b) for a in range(-13,14) for b in range(-13,14) if 0<Q(a,b)<=127})
assert len(allnorms)==45
first41=set(allnorms[:41]);assert first41-norms=={111} and norms-first41=={127}
source=json.loads((B/'wave2/construction_family/difference_envelope_s3.json').read_text())
assert set(map(tuple,source['nonzero_integer_vectors']))==vec
p=json.loads((B/'candidates/wave2_family/support_k41_n111_code7324998.json').read_text())['points']
actual={(a-c,b-d) for a,b in p for c,d in p if(a,b)!=(c,d)}
assert actual<=vec and {Q(*v) for v in actual}==norms
out={'passed':True,'envelope_vectors':len(vec),'norm_classes':len(norms),'maximum_norm':max(norms),'norm111_representations':sorted(rep111),'first41_deleted':sorted(first41-norms),'first41_added':sorted(norms-first41),'all45_up_to127_omitted':sorted(set(allnorms)-norms),'actual_difference_vectors':len(actual),'actual_differences_contained':True,'claims':'Necessary envelope inclusion proven analytically in orbit_review.md; equality of lattice envelopes and difference sets is not needed.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
