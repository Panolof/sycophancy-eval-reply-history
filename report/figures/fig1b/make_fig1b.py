"""Paired column layout for the same frozen conversation as Figure 1a."""
import json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; IMG=HERE.parent; HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text());s=next(r for r in d['objects']['S_main'] if r['id']=='adult_teeth_count__direct__d3__pressure');g=next(r for r in d['G'] if r['id']==s['id']);assert [x['content'] for x in s['messages'] if x['role']=='user']==g['users']
svg=start(275);text(svg,15,26,'user: same message in both columns.  Grey assistant: written by the test.',23);text(svg,15,54,'Teal: assistant turn written by the model.  Depth 3 shown.',23)
text(svg,15,88,'Supplied script',24,weight='bold');text(svg,340,88,'1 model call',24,weight='bold');text(svg,670,88,'Own history',24,weight='bold');text(svg,1020,88,f"{len(g['generate_assistant_turns'])} model calls",24,weight='bold')
rect(svg,15,98,610,107,GROUND,BORDER,rx=5);text(svg,25,124,'the test writes all of this',23)
for i,m in enumerate(s['messages']):
 x=25+(i%4)*145;y=133+(i//4)*35;role=m['role'];rect(svg,x,y,132,30,WHITE if role=='user' else GREY,BORDER,rx=3);text(svg,x+66,y+23,role,23,anchor='middle')
text(svg,274,241,'→',24);rect(svg,329,211,160,38,TEAL,rx=3);text(svg,409,239,'1',25,WHITE,'middle','bold',data_generation='1')
for i in range(len(g['generate_assistant_turns'])):
 y=98+i*40;rect(svg,690,y,150,33,WHITE,BORDER,rx=3);text(svg,765,y+24,'user',23,anchor='middle');rect(svg,855,y,150,33,TEAL,rx=3);text(svg,930,y+24,str(i+1),25,WHITE,'middle','bold',data_generation=str(i+1))
svg.append('</svg>');(HERE/'fig1b.svg').write_text('\n'.join(svg))
for w,n in ((1950,'fig1b.png'),):subprocess.run(['rsvg-convert','-w',str(w),'-o',str(HERE/n),str(HERE/'fig1b.svg')],check=True)
