"""Build the three-by-three table directly from the frozen user messages."""
import json,subprocess,sys,textwrap
from pathlib import Path
HERE=Path(__file__).resolve().parent;IMG=HERE.parent;HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text());
def get(style,condition):return next(r for r in d['G'] if r['id']==f'adult_teeth_count__{style}__d3__{condition}')['users'][1:]
columns=[get('direct','control'),get('direct','pressure'),get('expert','pressure')];svg=start(1000)
text(svg,15,30,'The user messages at each push',25,weight='bold')
for j,label in enumerate(('Control','Direct pressure','Expert pressure')):text(svg,150+j*380,70,label,24,weight='bold')
for i in range(3):
 y=85+i*300;text(svg,10,y+27,f'Push {i+1}',23,weight='bold')
 for j in range(3):
  x=145+j*380;v=columns[j][i];rect(svg,x,y,370,290,WHITE,BORDER)
  lines=[line for paragraph in v.split('\n') for line in (textwrap.wrap(paragraph,width=28,break_long_words=False,break_on_hyphens=False) or [''])]
  assert len(lines)<=10
  for k,line in enumerate(lines):text(svg,x+8,y+28+k*26,line,23,data_cell=f'{i}-{j}',data_line=str(k),data_source=v if k==0 else '')
svg.append('</svg>');(HERE/'g2.svg').write_text('\n'.join(svg))
for w,n in ((1950,'g2.png'),):subprocess.run(['rsvg-convert','-w',str(w),'-o',str(HERE/n),str(HERE/'g2.svg')],check=True)
