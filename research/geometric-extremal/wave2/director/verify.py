"""Exact, search-independent certificate for variable-radius square packing."""
import json
import sys
from fractions import Fraction as F


def rational(x):
    if isinstance(x, bool) or not isinstance(x, (str, int)):
        raise ValueError('Only integer or rational string input accepted')
    return F(x)


def verify(obj):
    if obj.get('problem') != 'sum_radii_square':
        raise ValueError('Wrong problem')
    c = [[rational(v) for v in row] for row in obj['circles']]
    if type(obj['n']) is not int or len(c) != obj['n'] or not c or any(len(row) != 3 for row in c):
        raise ValueError('Wrong dimensions')
    for x, y, r in c:
        if r <= 0 or min(x-r, y-r, 1-x-r, 1-y-r) < 0:
            raise ValueError('Radius or boundary violation')
    for i, (x, y, r) in enumerate(c):
        for xx, yy, rr in c[:i]:
            if (x-xx)**2+(y-yy)**2 < (r+rr)**2:
                raise ValueError('Overlap')
    value = sum((row[2] for row in c), F(0))
    answer = dict(passed=True, n=len(c), value=str(value), approximate=float(value), pairs=len(c)*(len(c)-1)//2)
    if 'comparison' in obj:
        gap = value-rational(obj['comparison'])
        answer.update(comparison_gap=str(gap), improves_frozen_comparison=gap > 0)
    return answer


def selftest():
    good = dict(problem='sum_radii_square', n=2, circles=[['1/4','1/2','1/4'],['3/4','1/2','1/4']])
    assert verify(good)['value'] == '1/2'
    for change in ('overlap', 'boundary', 'zero', 'float', 'count', 'bool_count'):
        bad = json.loads(json.dumps(good))
        if change == 'overlap': bad['circles'][1][0] = '7/10'
        if change == 'boundary': bad['circles'][0][0] = '1/5'
        if change == 'zero': bad['circles'][0][2] = '0'
        if change == 'float': bad['circles'][0][2] = 0.25
        if change == 'count': bad['n'] = 3
        if change == 'bool_count': bad['n'] = True
        try: verify(bad)
        except ValueError: continue
        raise AssertionError(change)
    return {'passed': True, 'controls': 7}


if __name__ == '__main__':
    print(json.dumps(selftest() if sys.argv[1:] == ['--selftest'] else verify(json.load(open(sys.argv[1]))), indent=2))
