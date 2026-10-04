"""Exact geometry domain adapter to the existing verifier-gated lab."""
import importlib.util,json
from pathlib import Path
from .base import Domain
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('geometry_independent_checker',ROOT/'research/geometric-extremal/certification/verify.py')
V=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V)
class GeometricExtremalDomain(Domain):
    name='geometric_extremal'
    recherche_ziel='Geometric extremal constructions with independently exact rational witnesses'
    kontext='Propose finite planar configurations. Declare region and normalization. A verified witness establishes feasibility and a constructive lower bound only, never global optimality or novelty.'
    primitive_doc='evaluate {spec}: independently evaluate an exact proposed witness; floats are forbidden.'
    claim_doc='A witness object has problem heilbronn_square/disk/triangle/convex, torus_distance, or few_distance; integer/rational-string points, optional integer scale, rational bound; few_distance has metric and max_distances. Tolerance fields forbidden.'
    def run_op(self,op,args):
        if op=='evaluate': return V.verify(args.get('spec',args))
        return {'fehler':'unknown operation'}
    def check(self,p):
        if isinstance(p,dict) and p.get('problem')=='torus_local_cycle':
            if p != {'problem':'torus_local_cycle','n':15}: return False,'fixed theorem input required',{}
            spec=importlib.util.spec_from_file_location('cycle_certificate',ROOT/'research/geometric-extremal/certification/local_cycle.py')
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.check()
            return r['passed'],json.dumps(r),r
        r=V.verify(p); return r['passed'],json.dumps(r),r
    def selftest(self): return V.selftest()
    def level(self,p): return 'computed_rigorous'
    def describe(self,p):
        if isinstance(p,dict) and p.get('problem')=='torus_local_cycle':
            ok,why,r=self.check(p)
            if not ok: return 'Rejected local theorem: '+why
            return 'For the known 15-point square-torus packing, labelled compatible lifts with translation fixed and maximum coordinate displacement strictly below '+r['strict_supnorm_radius']+' cannot have squared periodic separation at least '+r['squared_separation']+' unless every displacement is zero. Independently reviewed elementary proof; exact graph/lift/constant dependencies checked; local exclusion only, known mechanism, novelty and global optimality not established.'
        r=V.verify(p)
        return ('Exact witness certificate: '+json.dumps(r)) if r['passed'] else 'Rejected witness: '+r['reason']
    def consistent(self,answer,p): return answer==self.describe(p)
DOMAIN=GeometricExtremalDomain()
