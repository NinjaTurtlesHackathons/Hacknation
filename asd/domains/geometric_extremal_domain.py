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
    claim_doc='A witness object has problem heilbronn_square/disk/triangle/convex, torus_distance, few_distance, sum_radii_square, equilateral_triangles_square, or circle_packing_octagon_apothem; integer/rational-string points, optional integer scale, rational bound; few_distance has metric and max_distances. Tolerance fields forbidden.'
    def wave2(self,p):
        files={'sum_radii_square':'verify.py','equilateral_triangles_square':'polygon_verify.py','circle_packing_octagon_apothem':'octagon_verify.py'}
        name=p.get('problem') if isinstance(p,dict) else None
        if name not in files:return None
        if 'tolerance' in p or 'epsilon' in p: return {'passed':False,'reason':'Agent tolerance fields forbidden'}
        spec=importlib.util.spec_from_file_location('geometry_wave2_'+name,ROOT/'research/geometric-extremal/wave2/director'/files[name])
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        # Agent-supplied scalar comparisons cannot create a record claim.
        geometry={k:v for k,v in p.items() if k not in ('comparison','benchmark_R_squared_lower')}
        try:r=m.verify(geometry)
        except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError) as e:return {'passed':False,'reason':str(e)}
        r['scope']='Exact feasibility/construction bound only; novelty, literature comparison and global optimality require separate evidence.'
        return r
    def run_op(self,op,args):
        if op=='evaluate':
            p=args.get('spec',args);r=self.wave2(p)
            return r if r is not None else V.verify(p)
        return {'fehler':'unknown operation'}
    def check(self,p):
        if isinstance(p,dict) and p.get('problem')=='torus_local_cycle':
            if p != {'problem':'torus_local_cycle','n':15}: return False,'fixed theorem input required',{}
            spec=importlib.util.spec_from_file_location('cycle_certificate',ROOT/'research/geometric-extremal/certification/local_cycle.py')
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.check()
            return r['passed'],json.dumps(r),r
        r=self.wave2(p)
        if r is None:r=V.verify(p)
        return r['passed'],json.dumps(r),r
    def selftest(self):
        # Gate routing must preserve exact constraints, including malformed
        # geometry and agent-supplied comparison metadata.
        circles={'problem':'sum_radii_square','n':2,'circles':[['1/4','1/2','1/4'],['3/4','1/2','1/4']]}
        triangles={'problem':'equilateral_triangles_square','n':1,'half_side':'1','triangles':[['0','0','0']]}
        octagon={'problem':'circle_packing_octagon_apothem','n':2,'radius':'1/2','points':[['-1/2','0'],['1/2','0']]}
        return V.selftest()+[
            (circles,True),
            ({**circles,'circles':[['1/4','1/2','1/4'],['7/10','1/2','1/4']]},False),
            ({**circles,'circles':[['1/4','1/2','0'],['3/4','1/2','1/4']]},False),
            ({**circles,'n':True},False),
            ({**circles,'comparison':'1000000000'},True),
            (triangles,True),
            ({**triangles,'half_side':'4/5'},False),
            ({**triangles,'n':2,'triangles':[['0','0','0'],['0','0','0']]},False),
            ({**triangles,'benchmark_R_squared_lower':'1000000000'},True),
            (octagon,True),
            ({**octagon,'points':[['-1/2','1/2'],['1/2','1/2']]},False),
            ({**octagon,'radius':0.5},False),
            ({**octagon,'epsilon':'1/1000'},False),
        ]
    def level(self,p): return 'computed_rigorous'
    def describe(self,p):
        if isinstance(p,dict) and p.get('problem')=='torus_local_cycle':
            ok,why,r=self.check(p)
            if not ok: return 'Rejected local theorem: '+why
            return 'For the known 15-point square-torus packing, labelled compatible lifts with translation fixed and maximum coordinate displacement strictly below '+r['strict_supnorm_radius']+' cannot have squared periodic separation at least '+r['squared_separation']+' unless every displacement is zero. Independently reviewed elementary proof; exact graph/lift/constant dependencies checked; local exclusion only, known mechanism, novelty and global optimality not established.'
        r=self.wave2(p)
        if r is None:r=V.verify(p)
        return ('Exact witness certificate: '+json.dumps(r)) if r['passed'] else 'Rejected witness: '+r['reason']
    def consistent(self,answer,p): return answer==self.describe(p)
DOMAIN=GeometricExtremalDomain()
