#!/usr/bin/env python3
"""Prospectively specified release mutations for trusted record metadata."""
import copy,json
from pathlib import Path
import reproduce
BASE=Path(__file__).resolve().parents[1]
r=json.loads((BASE/'results/records.json').read_text())['records'][0]
mutations={
 'wrong_histogram':lambda s:s['multiplicities'].__setitem__('1',s['multiplicities']['1']+1),
 'wrong_palette':lambda s:s['squared_distances'].append(81),
 'wrong_count':lambda s:s.__setitem__('n',82),
 'wrong_budget':lambda s:s.__setitem__('k',30),
 'wrong_hash':lambda s:s.__setitem__('sha256','0'*64),
 'boolean_halfplane':lambda s:s['halfplanes'][0].__setitem__(0,True),
 'missing_halfplane':lambda s:s['halfplanes'].pop(),
 'wrong_polygon':lambda s:s['halfplanes'][3].__setitem__(2,4),
 'nonimprovement':lambda s:s.__setitem__('audited_published_lower_bound',81),
}
reports=[]
for label,f in mutations.items():
 s=copy.deepcopy(r);f(s)
 try:reproduce.check(s)
 except (AssertionError,KeyError,ValueError) as e:reports.append({'control':label,'rejected':True,'reason':str(e)})
 else:raise AssertionError('Invalid record accepted: '+label)
print(json.dumps({'passed':True,'controls':reports},indent=2))
