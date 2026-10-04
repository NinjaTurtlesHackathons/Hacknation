#!/usr/bin/env python3
"""Build a portable offline demo exclusively from the reviewed demo table.

No search files, candidate coordinates or remote JavaScript are read here.
Run from any cwd: python research/geometric-extremal/demo/build_demo.py
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tables'/'demo_data.json'
TARGET=Path(__file__).resolve().parent/'index.html'

HTML=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Geometry Lab · Certificates before claims</title>
<style>
:root{color-scheme:dark;--bg:#10181e;--panel:#17242d;--fg:#e8f0f5;--dim:#a7bbc9;--accent:#5fe3ba;--warn:#ffc879}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,sans-serif}main{max-width:1200px;margin:auto;padding:38px 24px}h1{font-size:clamp(30px,5vw,54px);line-height:1.08;max-width:900px;margin:12px 0 22px;letter-spacing:-1.5px}h2{font-size:20px;margin:0 0 14px}p{max-width:820px}a{color:var(--accent)}.eyebrow{font-size:12px;letter-spacing:2px;color:var(--accent);text-transform:uppercase}.status{border:1px solid #637279;border-radius:8px;padding:12px 16px;color:var(--warn);margin:22px 0}.grid{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(290px,1fr);gap:22px}.card{background:var(--panel);border:1px solid #30414e;border-radius:16px;padding:22px}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin-bottom:18px}label{display:flex;flex-direction:column;gap:5px;font-size:13px;color:var(--dim)}select,input,button{font:inherit;color:var(--fg);background:#243642;border:1px solid #587282;border-radius:7px;padding:8px 10px;max-width:100%}button{cursor:pointer}button:hover{background:#314d5d}:focus-visible{outline:3px solid var(--accent);outline-offset:3px}svg{display:block;width:100%;height:auto;max-height:560px;background:#101a22;border-radius:8px}svg .point{fill:var(--accent);stroke:#101a22;stroke-width:1.5}svg .selected{fill:var(--warn)}svg text{fill:var(--dim);font-size:11px}.metric{font-size:28px;font-variant-numeric:tabular-nums;line-height:1.2;color:var(--accent);word-break:break-word}.fraction{font-family:ui-monospace,monospace;font-size:12px;overflow-wrap:anywhere}.caption,.small{font-size:13px;color:var(--dim)}dl{margin:18px 0}dt{color:var(--dim);font-size:13px}dd{margin:3px 0 14px}.pass{color:var(--accent)}.fail{color:var(--warn)}footer{margin-top:28px;color:var(--dim);font-size:13px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}@media(max-width:760px){main{padding:24px 15px}.grid{grid-template-columns:1fr}.card{padding:16px}}
</style></head><body><main>
<div class="eyebrow">AI Agent Lab · geometric extremal research</div>
<h1 id="title">Certificates before claims</h1>
<p id="intro">Explore the geometry, then inspect the exact witness. Search proposes; an independent checker decides.</p>
<div class="status" id="status" role="status">Loading reviewed results…</div>
<div class="controls"><label>Reviewed case<select id="case"></select></label><label>Geometry view<select id="view"><option value="critical">Certified critical subset</option><option value="selected">Choose a subset</option><option value="edges">All pairwise edges</option></select></label></div>
<div class="grid"><section class="card" aria-labelledby="geometry-heading"><h2 id="geometry-heading">A configuration you can inspect</h2><div class="controls" id="selectors"></div><svg id="geometry" viewBox="0 0 600 520" role="img" aria-label="Point configuration and selected geometric subset"></svg><p class="caption" id="geometry-note">Drawing and selected-subset arithmetic use floating point for illustration.</p></section>
<section class="card" aria-labelledby="certificate-heading"><h2 id="certificate-heading">Independent exact certificate</h2><div class="metric" id="metric"></div><p class="fraction" id="fraction"></p><dl id="facts"></dl><p id="selected-value" class="small"></p><label>Test a proposed lower bound<input id="threshold" type="text" inputmode="decimal" autocomplete="off" aria-describedby="threshold-note"></label><p id="threshold-result" aria-live="polite"></p><p class="small" id="threshold-note">This compares your bound against the fixed certified rational value using exact integer cross multiplication. It does not prove global optimality.</p><p class="small" id="source"></p></section></div>
<section class="card" style="margin-top:22px"><h2>What the evidence supports</h2><div id="claims"></div></section>
<footer>Portable offline demonstration. No network requests, no remote libraries. Rational certificates remain fixed; visual calculations are illustrative. Human direction, public baselines, agent search and independent verification are credited in the manuscript.</footer>
</main><script type="application/json" id="reviewed-data">__DATA__</script><script>
'use strict';
const data=JSON.parse(document.getElementById('reviewed-data').textContent);
const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
const cases=data.cases||data.configurations||[];
let current=null,points=[],selected=[],certificate={};
function text(el,t){el.textContent=String(t??'');}
function q(s){s=String(s).trim();if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:\/\d+)?$/.test(s))throw Error('Use a decimal or integer fraction.');
 if(s.includes('/')){let [a,b]=s.split('/');return[BigInt(a),BigInt(b)];}
 let sign=1n;if(s.startsWith('-')){sign=-1n;s=s.slice(1);}else if(s.startsWith('+'))s=s.slice(1);
 let [a,b='']=s.split('.');return[sign*BigInt((a||'0')+b),10n**BigInt(b.length)];}
function number(s){let [a,b]=q(s);return Number(a)/Number(b);}
function node(tag,attributes,parent){let e=document.createElementNS(NS,tag);for(let[k,v]of Object.entries(attributes))e.setAttribute(k,v);if(parent)parent.append(e);return e;}
function determinant(a,b,c){return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);}
function hull(p){let ids=p.map((_,i)=>i).sort((i,j)=>p[i][0]-p[j][0]||p[i][1]-p[j][1]),out=[];
 for(let seq of [ids,[...ids].reverse()]){let h=[];for(let i of seq){while(h.length>=2&&determinant(p[h[h.length-2]],p[h[h.length-1]],p[i])<=0)h.pop();h.push(i);}out.push(...h.slice(0,-1));}return out;}
function problem(){return current.problem||current.kind||'heilbronn_'+current.variant;}
function isPair(){return ['torus_distance','few_distance','circle_packing_triangle'].includes(problem());}
function renderFacts(){let facts=$('facts');facts.replaceChildren();let values=[['Points',points.length],['Problem and normalization',certificate.normalization||problem()],['Exact checker',certificate.passed===true?'Passed':'See reviewed claim'],['Claim ID',current.claim_id||'See table'],['Comparison status',current.status||data.status||'No new result claimed']];
 if(String(current.id).startsWith('GE-SEARCH')){let baseline=cases.find(c=>String(c.id).startsWith('GE-BASE')&&c.problem===problem()&&c.points.length===points.length),bv=baseline?.certificate?.value,cv=certificate.value;
  if(bv&&cv){let[a,b]=q(cv),[c,d]=q(bv),delta=a*d-c*b;values.push(['Inherited exact comparison witness',bv],['Exact comparison',delta<0n?'Below the inherited witness':delta===0n?'Equal to the inherited witness':'Above this comparison witness; novelty requires separate audit']);}}
 for(let [label,value]of values){let dt=document.createElement('dt'),dd=document.createElement('dd');text(dt,label);text(dd,value);if(label.includes('exact comparison witness'))dd.className='fraction';facts.append(dt,dd);}}
function draw(){let svg=$('geometry');svg.replaceChildren();if(!points.length)return;
 let kind=problem(),p=points;if(kind==='few_distance'&&current.metric==='triangular')p=points.map(([x,y])=>[x+y/2,y*Math.sqrt(3)/2]);
 let xs=p.map(v=>v[0]),ys=p.map(v=>v[1]);let minx=Math.min(...xs),maxx=Math.max(...xs),miny=Math.min(...ys),maxy=Math.max(...ys);
 if(kind.includes('square')||kind==='torus_distance'){minx=miny=0;maxx=maxy=1;}
 if(kind.includes('triangle')){minx=miny=0;maxx=maxy=1;}
 if(kind.includes('disk')){minx=miny=-1;maxx=maxy=1;}
 let span=Math.max(maxx-minx,maxy-miny,.001),sx=x=>65+440*(x-minx)/span,sy=y=>465-440*(y-miny)/span;
 let frame=null;
 if(kind.includes('triangle'))frame=[[0,0],[1,0],[0,1]];
 else if(kind.includes('square')||kind==='torus_distance')frame=[[0,0],[1,0],[1,1],[0,1]];
 else if(kind.includes('convex'))frame=hull(p).map(i=>p[i]);
 if(frame)node('polygon',{points:frame.map(([x,y])=>sx(x)+','+sy(y)).join(' '),fill:'none',stroke:'#718796','stroke-width':1.5},svg);
 if(kind.includes('disk'))node('circle',{cx:sx(0),cy:sy(0),r:440/span,fill:'none',stroke:'#718796','stroke-width':1.5},svg);
 if(kind==='circle_packing_triangle'){let radius=number(current.radius||certificate.radius);for(let point of p)node('circle',{cx:sx(point[0]),cy:sy(point[1]),r:440*radius/span,fill:'#5fe3ba','fill-opacity':.08,stroke:'#5fe3ba','stroke-opacity':.6,'stroke-width':1},svg);}
 let ids=$('view').value==='critical'?(certificate.critical_triple||certificate.critical_pair||current.critical_triple||selected):selected;
 if($('view').value==='edges'){for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)node('line',{x1:sx(p[i][0]),y1:sy(p[i][1]),x2:sx(p[j][0]),y2:sy(p[j][1]),stroke:'#496171','stroke-opacity':.3},svg);}
 else if(ids.length===3&&!isPair())node('polygon',{points:ids.map(i=>sx(p[i][0])+','+sy(p[i][1])).join(' '),fill:'#ffc879', 'fill-opacity':.16,stroke:'#ffc879','stroke-width':2},svg);
 else if(ids.length>=2){if(kind==='torus_distance'){
  let defs=node('defs',{},svg),clip=node('clipPath',{id:'periodic-clip'},defs);node('rect',{x:sx(0),y:sy(1),width:440/span,height:440/span},clip);
  let a=p[ids[0]],b=p[ids[1]],dx=b[0]-a[0],dy=b[1]-a[1];dx-=Math.round(dx);dy-=Math.round(dy);
  for(let tx of [-1,0,1])for(let ty of [-1,0,1])node('line',{x1:sx(a[0]+tx),y1:sy(a[1]+ty),x2:sx(a[0]+dx+tx),y2:sy(a[1]+dy+ty),stroke:'#ffc879','stroke-width':2,'clip-path':'url(#periodic-clip)'},svg);
 }else node('line',{x1:sx(p[ids[0]][0]),y1:sy(p[ids[0]][1]),x2:sx(p[ids[1]][0]),y2:sy(p[ids[1]][1]),stroke:'#ffc879','stroke-width':2},svg);}
 for(let i=0;i<p.length;i++){node('circle',{cx:sx(p[i][0]),cy:sy(p[i][1]),r:5,class:'point'+(ids.includes(i)?' selected':'')},svg);let label=node('text',{x:sx(p[i][0])+8,y:sy(p[i][1])-8},svg);text(label,String(i));}
 let value;
 if(isPair()){let a=p[ids[0]],b=p[ids[1]],dx=Math.abs(a[0]-b[0]),dy=Math.abs(a[1]-b[1]);if(kind==='torus_distance'){dx=Math.min(dx,1-dx);dy=Math.min(dy,1-dy);}value=dx*dx+dy*dy;}
 else{value=Math.abs(determinant(p[ids[0]],p[ids[1]],p[ids[2]]))/2;if(kind.includes('triangle'))value*=2;if(kind.includes('convex')){let h=hull(p),twice=0;for(let i=0;i<h.length;i++){let a=p[h[i]],b=p[h[(i+1)%h.length]];twice+=a[0]*b[1]-a[1]*b[0];}value/=Math.abs(twice)/2;}}
 text($('selected-value'),(isPair()?'Selected squared separation: ':'Selected normalized triangle area: ')+Number(value).toPrecision(9)+' (floating point illustration).');}
function threshold(){try{let v=certificate.value||certificate.value_fraction||certificate.radius||current.value_fraction||current.value;
 if(!v||certificate.passed!==true){text($('threshold-result'),'No fixed verified rational bound is available for this case.');return;}
 let[a,b]=q(v),[c,d]=q($('threshold').value);if(b<=0n||d<=0n)throw Error('Positive denominator required.');let pass=a*d>=c*b;
 text($('threshold-result'),pass?'Supported by this exact witness.':'Not supported by this witness.');$('threshold-result').className=pass?'pass':'fail';}catch(e){text($('threshold-result'),e.message);$('threshold-result').className='small';}}
function show(){current=cases[Number($('case').value)];if(!current)return;certificate=current.certificate||current.verification||{};
 let scale=Number(current.scale||1);points=(current.points||[]).map(row=>row.map(x=>number(x)/scale));selected=isPair()?[0,1]:[0,1,2];
 text($('metric'),certificate.approximate!==undefined?Number(certificate.approximate).toPrecision(12):(certificate.distance_count!==undefined?certificate.distance_count+' squared distances':'Exact witness'));
 let value=certificate.value||certificate.value_fraction||certificate.radius||current.value_fraction||current.value; text($('fraction'),value||'Certificate details in reviewed table');
 $('selectors').replaceChildren();selected.forEach((id,k)=>{let label=document.createElement('label'),sel=document.createElement('select');text(label,'Point '+(k+1));for(let i=0;i<points.length;i++){let opt=document.createElement('option');opt.value=i;text(opt,i);sel.append(opt);}sel.value=id;sel.addEventListener('change',()=>{selected[k]=Number(sel.value);$('view').value='selected';if(new Set(selected).size===selected.length)draw();else text($('selected-value'),'Choose distinct point indices.');});label.append(sel);$('selectors').append(label);});
 renderFacts();let source=$('source');source.replaceChildren();let url=current.baseline?.source_url||current.source_url||current.source?.url;if(url){let credit=document.createElement('span');text(credit,'Public baseline / external construction credited to its source: ');source.append(credit);let a=document.createElement('a');a.href=url;a.rel='noopener';text(a,'Inspect original provenance');source.append(a);}text($('threshold'),value||'');$('threshold').value=value||'';threshold();draw();}
text($('title'),data.title||'Certificates before claims');text($('intro'),data.intro||'An independently checked witness is a reproducible result. A reproduced incumbent is not a discovery.');text($('status'),typeof data.status==='string'?data.status:'No geometric novelty claimed; see verified claims below.');
cases.forEach((c,i)=>{let o=document.createElement('option');o.value=i;text(o,c.title||c.id||c.problem||'Case '+i);$('case').append(o);});
for(let claim of data.summary||data.claims||[]){let p=document.createElement('p');text(p,(claim.text||claim.claim||String(claim))+(claim.claim_id?' ['+claim.claim_id+']':''));$('claims').append(p);}
$('case').addEventListener('change',show);$('view').addEventListener('change',draw);$('threshold').addEventListener('input',threshold);show();
</script></body></html>'''

def main():
    data=json.loads(SOURCE.read_text())
    if not isinstance(data,dict):raise ValueError('reviewed demo table must be an object')
    cases=data.get('cases',data.get('configurations',[]))
    if not cases:raise ValueError('No reviewed cases; refusing to invent demo results')
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<',chr(92)+'u003c')
    TARGET.write_text(HTML.replace('__DATA__',payload))
    print(TARGET)

if __name__=='__main__':main()
