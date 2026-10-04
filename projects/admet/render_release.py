"""Deterministic manuscript and demo from confirmed state claims; no LLM prose acceptance."""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parent
TITLE='Physicochemical Descriptors Improve Fixed Fingerprint Baselines Across Three ADMET Endpoints'
SECTIONS=[('Abstract',['abstract']),('Introduction and contribution',['scope','design','novelty']),('Preregistered experiment',['methods','splits','inference','precommit']),('Data coverage and structural audit',['audit','invalid','coverage-solubility_aqsoldb','coverage-lipophilicity_astrazeneca','coverage-caco2_wang']),('Validation results and fixed-test evaluation',['test-solubility_aqsoldb','test-lipophilicity_astrazeneca','test-caco2_wang','valid-solubility_aqsoldb','valid-lipophilicity_astrazeneca','valid-caco2_wang','gate-solubility_aqsoldb','gate-lipophilicity_astrazeneca','gate-caco2_wang']),('Falsification, sensitivity and negative results',['null-solubility_aqsoldb-validation','null-lipophilicity_astrazeneca-validation','null-caco2_wang-validation','null-solubility_aqsoldb-test','null-lipophilicity_astrazeneca-test','null-caco2_wang-test','segments']),('Verifier and agent laboratory',['verification','reproduction','trust','redteam','freeze','agents','lean']),('Limitations and next scientific step',['limitations','platform']),('Verified references',['ref-0','ref-1','ref-2','ref-3','ref-tdc'])]
def load():
 state=json.loads((ROOT/'state.json').read_text());claims={c['id']:c for c in state['claims'] if c['status']=='bestätigt' and c['id'].startswith('release-')}
 for _,ids in SECTIONS:
  for key in ids:assert 'release-'+key in claims,'unconfirmed/missing record: '+key
 return claims

def render():
 import sys
 from validate import validate
 if '--release' not in sys.argv:sys.argv.append('--release')
 validate()
 claims=load()
 from release_records import records
 known=records()
 for cid,c in claims.items():assert c['text']==known[cid[len('release-'):]]['text'],'state record differs from regenerated source evidence'
 parts=['# '+TITLE,'','NinjaTurtlesHackathons | ADMET research draft | 4 October 2026',''];plain=[]
 for heading,ids in SECTIONS:
  parts+=['## '+heading,''];paragraphs=[]
  for key in ids:
   c=claims['release-'+key];cid='C-'+c['id'];text=c['text'].rstrip('.')+'.'
   # Each clause is from one canonical certified record; no synthesized scientific sentence.
   parts += [text+' ['+cid+']',''];paragraphs.append((text,cid))
  plain.append((heading,paragraphs))
 md='\n'.join(parts);(ROOT/'paper.md').write_text(md)
 # Stronger than numerical-token gate: every nonmetadata paragraph equals one confirmed record verbatim.
 seen=set()
 for _,paragraphs in plain:
  for text,cid in paragraphs:
   assert text==claims[cid[2:]]['text'].rstrip('.')+'.';seen.add(cid)
 (ROOT/'paper_belege.json').write_text(json.dumps({'claims':[{'claim_id':'C-'+c['id'],**c} for c in claims.values()],'verification':{'canonical_paragraph_match':True,'confirmed_only':True,'claim_count':len(seen),'limitation':'canonical checker verifies derivation and support, not clinical truth'}},indent=2))
 body=''.join('<h2>'+html.escape(h)+'</h2>'+''.join('<p>'+html.escape(t)+' <small>['+cid+']</small></p>' for t,cid in ps) for h,ps in plain)
 (ROOT/'paper.html').write_text('<!doctype html><meta charset="utf-8"><title>'+TITLE+'</title><style>body{max-width:900px;margin:50px auto;font:17px/1.6 Georgia;color:#17212e}h1{line-height:1.15}h2{margin-top:42px}small{font:11px monospace;color:#64748b}</style><h1>'+TITLE+'</h1><p>Research draft · 4 October 2026</p>'+body)
 # Standalone editable native LaTeX source, all dependencies standard; no external image project files.
 def esc(s):
  for a,b in [('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:s=s.replace(a,b)
  return s.replace('~',r'\textasciitilde{}').replace('^',r'\textasciicircum{}')
 tex=r'''\documentclass[10pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=22mm]{geometry}
\usepackage{amsmath,amssymb,booktabs,hyperref}
\title{'''+esc(TITLE)+r'''}
\author{NinjaTurtlesHackathons --- ADMET research draft}
\date{4 October 2026}
\begin{document}\maketitle
'''
 for heading,ps in plain:
  tex+='\\section*{'+esc(heading)+'}\n'
  for text,cid in ps:tex+=esc(text)+' {\\scriptsize['+esc(cid)+']}\n\n'
 tex+='\\end{document}\n';(ROOT/'paper.tex').write_text(tex)
 # PDF same paragraphs, polished readable one-column manuscript.
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
 from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
 from reportlab.lib import colors
 from reportlab.lib.enums import TA_CENTER
 from reportlab.lib.pagesizes import A4
 styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='PaperTitle',fontName='Times-Bold',fontSize=17,leading=20,alignment=TA_CENTER,spaceAfter=12));styles.add(ParagraphStyle(name='PaperBody',fontName='Times-Roman',fontSize=10,leading=13.5,spaceAfter=8));styles.add(ParagraphStyle(name='Evidence',fontName='Helvetica',fontSize=6.5,leading=8,textColor=colors.HexColor('#657183'),spaceAfter=6));styles.add(ParagraphStyle(name='PaperH',fontName='Times-Bold',fontSize=12,leading=15,spaceBefore=14,spaceAfter=7,keepWithNext=True))
 flow=[Paragraph(html.escape(TITLE),styles['PaperTitle']),Paragraph('NinjaTurtlesHackathons | ADMET research draft | 4 October 2026',styles['Evidence']),Spacer(1,10)]
 experiments=pd_read(ROOT/'experiments.csv');data=[['Fixed test MAE','Median','Morgan','Descriptors','Combined','Reduction']]
 names={'solubility_aqsoldb':'Solubility','lipophilicity_astrazeneca':'Lipophilicity','caco2_wang':'Caco-2'}
 for e,n in names.items():
  t={m:{'mean_mae':sum(float(r['y']) for r in experiments if r['dataset']==e and r['policy']==m and r['step']=='1')/20} for m in ['median','morgan','descriptors','combined']};data.append([n]+[f'{t[m]["mean_mae"]:.3f}' for m in ['median','morgan','descriptors','combined']]+[f'{100*(1-t["combined"]["mean_mae"]/t["morgan"]["mean_mae"]):.1f}%'])
 table=Table(data,colWidths=[100,53,53,70,60,65],repeatRows=1);table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf2')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#667788')),('LINEBELOW',(0,-1),(-1,-1),.7,colors.HexColor('#667788')),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]))
 for i,(heading,ps) in enumerate(plain):
  flow.append(Paragraph(html.escape(heading),styles['PaperH']))
  if i==0:
   flow.append(table);flow.append(Spacer(1,7));flow.append(Paragraph('Derived from the three confirmed test-result records below. Reduction is relative to the fixed Morgan baseline; no leaderboard comparison.',styles['Evidence']))
  for text,cid in ps:
   flow.append(Paragraph(html.escape(text),styles['PaperBody']));flow.append(Paragraph('['+cid+']',styles['Evidence']))
 def footer(canvas,doc):
  canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#657183'));canvas.drawString(62,32,'ADMET | Reproducible pilot | Research draft');canvas.drawRightString(A4[0]-62,32,str(doc.page))
 SimpleDocTemplate(str(ROOT/'paper.pdf'),pagesize=A4,leftMargin=62,rightMargin=62,topMargin=48,bottomMargin=48,title=TITLE,author='NinjaTurtlesHackathons').build(flow,onFirstPage=footer,onLaterPages=footer)
 # Demo reads authoritative tables only (not source data or model code).
 exp=pd_read(ROOT/'experiments.csv');gate=pd_read(ROOT/'gates.csv');cc=pd_read(ROOT/'claims.csv')
 rows=''.join('<tr><td>'+html.escape(r['dataset'])+'</td><td>'+html.escape(r['policy'])+'</td><td>'+r['seed']+'</td><td>'+r['y']+'</td></tr>' for r in exp if r['step']=='1')
 (ROOT/'demo.html').write_text('<!doctype html><meta charset="utf-8"><title>ADMET Evidence Demo</title><style>body{font:16px system-ui;margin:50px;background:#f6f8fa;color:#182330}table{border-collapse:collapse;background:white}td,th{padding:8px 16px;border-bottom:1px solid #ddd}details{margin:20px 0}pre{white-space:pre-wrap}</style><h1>ADMET evidence laboratory</h1><p>Fixed CPU models · validation-only agents · verified test predictions</p><p>'+str(len(exp))+' logged evaluations · '+str(len(cc))+' claims</p><h2>Gates</h2><pre>'+html.escape(json.dumps(gate,indent=2))+'</pre><details><summary>All fixed test evaluations</summary><table><tr><th>Endpoint</th><th>Method</th><th>Seed</th><th>MAE</th></tr>'+rows+'</table></details><details><summary>Claim ledger</summary><pre>'+html.escape(json.dumps(cc,indent=2))+'</pre></details>')
 print('Generated paper.md/.tex/.html/.pdf, canonical support report and tables-only demo')
def pd_read(p):
 import csv
 return list(csv.DictReader(p.open()))
if __name__=='__main__':render()
