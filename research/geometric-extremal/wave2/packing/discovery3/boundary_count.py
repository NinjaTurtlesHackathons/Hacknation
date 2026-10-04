#!/usr/bin/env python3
"""Exact perimeter-based restriction on how many circle centres touch the boundary."""
import json
from fractions import Fraction as F
from octagon import HERE,ROOT,BENCH,verify
def main():
 report={}
 for n,v in BENCH.items():
  threshold=F(v)-F('1e-11');o=json.loads((ROOT/f'candidates/wave2_packing3/baseline_n{n}.json').read_text());o['benchmark_radius_upper']=str(threshold);o['required_ratio']='1';assert verify(o)['improves_benchmark_with_required_ratio']
  exclusions=[];algebra=[]
  for m in range(12,21):
   a=threshold**2*((2*m-16)**2+512)-128;b=threshold**2*(32*(2*m-16))+64
   # threshold²*(2m+16(sqrt2-1))²-(128-64sqrt2)>0
   positive=(a>=0 and b>=0) or (a<0 and b>0 and 2*b*b>a*a)
   if positive:exclusions.append(m)
   algebra.append({'m':m,'Qsqrt2_rational':str(a),'Qsqrt2_coefficient':str(b),'positive':positive})
  report[n]={'feasible_baseline_beats_radius_threshold':str(threshold),'excluded_boundary_contact_counts':exclusions,'maximum_boundary_count_at_or_above_threshold':min(exclusions)-1,'exact_comparison_algebra':algebra}
 (HERE/'boundary_count_certificate.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
