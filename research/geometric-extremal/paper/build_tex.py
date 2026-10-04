#!/usr/bin/env python3
"""Pandoc standalone export with Unicode math and a self-contained figure."""
from pathlib import Path
from itertools import combinations
import json,math,subprocess,re
BASE=Path(__file__).resolve().parents[1]
source=(BASE/'paper/manuscript.md').read_text().replace('−','-').replace('∎',r'\(\square\)')
# Spaces permit line wrapping in the redundant inline palette lists.
source=re.sub(r'`([0-9,]{50,})`',lambda m:m.group(1).replace(',',', '),source)
source=re.sub(r'\| witness file, relative to research/geometric-extremal \| SHA256 \|.*?\n\n',lambda m:'Witness hashes are listed below; file paths are relative to the research directory.\n\n'+''.join(f'{r["id"]}: `{r["candidate"]}`\n\n```\n{r["sha256"]}\n```\n\n' for r in json.loads((BASE/'results/records.json').read_text())['records']),source,flags=re.S)
r=subprocess.run(['pandoc','-f','markdown+tex_math_single_backslash','-t','latex','-s','-V','geometry:margin=22mm'],input=source,text=True,capture_output=True,check=True)
text=r.stdout
ops={'φ':r'\varphi','⊂':r'\subset','∈':r'\in','√':r'\surd','‖':r'\Vert','≠':r'\ne','≥':r'\ge','≤':r'\le','↦':r'\mapsto','∑':r'\sum','∞':r'\infty','∩':r'\cap','²':r'{}^2','⊆':r'\subseteq','³':r'{}^3','Δ':r'\Delta','ε':r'\epsilon'}
# All remaining literal symbols occur in prose, not source-code environments.
parts=re.split(r'(\\begin\{verbatim\}.*?\\end\{verbatim\})',text,flags=re.S)
for i in range(0,len(parts),2):
 for ch,tex in ops.items():parts[i]=parts[i].replace(ch,r'\ensuremath{'+tex+'}')
text=''.join(parts)
# Built-in editor accepts only standalone files: embed drawing instructions.
fig=[r'\begin{figure}[ht]',r'\centering',r'\setlength{\unitlength}{1pt}',r'\begin{picture}(440,200)']
for index,record in enumerate(json.loads((BASE/'results/records.json').read_text())['records']):
 points=record['points'];xy=[(a+b/2,math.sqrt(3)*b/2) for a,b in points]
 cx=(min(x for x,y in xy)+max(x for x,y in xy))/2;cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
 xy=[(110+220*index+12*(x-cx),102+12*(y-cy)) for x,y in xy]
 q=91 if index==0 else 127
 fig.append(r'{\color{'+('red' if index==0 else 'blue')+'}')
 for i,j in combinations(range(len(points)),2):
  a,b=points[i];c,d=points[j];u,v=a-c,b-d
  if u*u+u*v+v*v==q:
   x,y=xy[i];z,w=xy[j]
   fig.append(f'\\qbezier({x:.3f},{y:.3f})({(x+z)/2:.3f},{(y+w)/2:.3f})({z:.3f},{w:.3f})')
 fig.append('}')
 for x,y in xy:fig.append(f'\\put({x:.3f},{y:.3f}){{\\circle*{{2.8}}}}')
 fig.append(f'\\put({110+220*index},185){{\\makebox(0,0){{\\small {record["n"]} points, {record["k"]} distances}}}}')
 fig.append(f'\\put({110+220*index},17){{\\makebox(0,0){{\\small Published comparison: {record["audited_published_lower_bound"]}}}}}')
fig.extend([r'\end{picture}',r'\caption{Exact lattice constructions on the same drawing scale. Colored segments show all four pairs at squared distance 91 (left) and all six pairs at 127 (right). Comparison counts refer to Ahmed--Snevily (2013).}',r'\end{figure}'])
text=text.replace(r'\subsection{1. Problem and statements}', '\n'.join(fig)+'\n\n'+r'\subsection{1. Problem and statements}',1)
(BASE/'paper/manuscript.tex').write_text(text)
print(BASE/'paper/manuscript.tex')
