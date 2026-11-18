import json,re,struct,sys,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;IMG=HERE.parent;HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text());s=next(r for r in d['objects']['S_main'] if r['id']=='adult_teeth_count__direct__d3__pressure');g=next(r for r in d['G'] if r['id']==s['id']);assert [m['content'] for m in s['messages'] if m['role']=='user']==g['users'] and len(s['messages'])==7 and len(g['generate_assistant_turns'])==4
r=ET.parse(HERE/'fig1b.svg').getroot();t=r.findall('.//{http://www.w3.org/2000/svg}text');v=[x.text for x in t];assert [x.text for x in t if x.get('data-generation')]==['1','1','2','3','4'];assert all(not re.search(re.escape(w),' '.join(v),re.I) for w in BANNED)
pt=min(float(x.get('font-size')) for x in t)*PLACED_MM/25.4*72/WIDTH;assert pt>=8 and 275/WIDTH*PLACED_MM<=35
with (HERE/'fig1b.png').open('rb') as f:f.read(16);w,h=struct.unpack('>II',f.read(8))
assert w/(PLACED_MM/25.4)>=300
print(f'PASS: source structure, one and four calls, banned words; text {pt:.2f} pt; height {275/WIDTH*PLACED_MM:.2f} mm.')
