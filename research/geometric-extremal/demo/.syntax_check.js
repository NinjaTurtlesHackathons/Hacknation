
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
function renderFacts(){let facts=$('facts');facts.replaceChildren();for(let [label,value]of [['Points',points.length],['Problem and normalization',certificate.normalization||problem()],['Exact checker',certificate.passed===true?'Passed':'See reviewed claim'],['Claim ID',current.claim_id||'See table'],['Comparison status',current.status||data.status||'No new result claimed']]){let dt=document.createElement('dt'),dd=document.createElement('dd');text(dt,label);text(dd,value);facts.append(dt,dd);}}
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
 else if(ids.length>=2)node('line',{x1:sx(p[ids[0]][0]),y1:sy(p[ids[0]][1]),x2:sx(p[ids[1]][0]),y2:sy(p[ids[1]][1]),stroke:'#ffc879','stroke-width':2},svg);
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
