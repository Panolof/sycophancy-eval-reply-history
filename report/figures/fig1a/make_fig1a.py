"""One model call versus four, from the frozen conversation structure."""
import json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
IMG=HERE.parent
HOME=IMG.parents[1]
sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text())
s=next(r for r in d['objects']['S_main'] if r['id']=='adult_teeth_count__direct__d3__pressure')
g=next(r for r in d['G'] if r['id']==s['id'])
msgs=s['messages']; users=[m for m in msgs if m['role']=='user']; assistants=[m for m in msgs if m['role']=='assistant']
assert [m['content'] for m in users]==g['users'] and len(msgs)==7
calls=g['generate_assistant_turns']; assert len(calls)==len(users) and len(assistants)+1==len(calls)
svg=start(275)
text(svg,12,27,'user: same message in both rows.  Grey assistant: written by the test.',24)
text(svg,12,56,'Teal: assistant turn written by the model.  Depth 3 shown.',24)
text(svg,12,105,'Supplied script',24,weight='bold')
text(svg,12,201,'Own history',24,weight='bold')
rect(svg,203,74,742,76,GROUND,BORDER,rx=7)
text(svg,215,99,'the test writes all of this',23)
xs=[215,310,405,500,595,690,785]
for x,m in zip(xs,msgs):
    role=m['role']; rect(svg,x,108,88,33,WHITE if role=='user' else GREY,BORDER,rx=4)
    text(svg,x+44,132,role,23,anchor='middle',textLength=80,lengthAdjust='spacingAndGlyphs')
svg.append('<path d="M947 125 h31 m-8 -6 l8 6 l-8 6" fill="none" stroke="#263238" stroke-width="3"/>')
rect(svg,985,105,95,38,TEAL,rx=4); text(svg,1032.5,132,str(len(msgs)-len(assistants)-len(users)+1),25,WHITE,'middle','bold',data_generation='1')
text(svg,1100,132,f'{1} model call',25,weight='bold')
for i,x in enumerate((215,405,595,785)):
    rect(svg,x,175,88,36,WHITE,BORDER,rx=4); text(svg,x+44,201,'user',23,anchor='middle')
    rect(svg,x+95,175,88,36,TEAL,rx=4); text(svg,x+139,201,str(i+1),25,WHITE,'middle','bold',data_generation=str(i+1))
text(svg,1100,201,f'{len(calls)} model calls',25,weight='bold')
svg.append('</svg>')
(HERE/'fig1a.svg').write_text('\n'.join(svg),encoding='utf-8')
for width,name in ((1950,'fig1a.png'),):
    subprocess.run(['rsvg-convert','-w',str(width),'-o',str(HERE/name),str(HERE/'fig1a.svg')],check=True)
