import json, re, struct, sys, xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent; IMG=HERE.parent; HOME=IMG.parents[1]; sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text()); ident='adult_teeth_count__direct__d3__pressure'
s=next(r for r in d['objects']['S_main'] if r['id']==ident); g=next(r for r in d['G'] if r['id']==ident)
assert [m['content'] for m in s['messages'] if m['role']=='user']==g['users']
root=ET.parse(HERE/'fig1a.svg').getroot(); ns='{http://www.w3.org/2000/svg}'
texts=root.findall('.//'+ns+'text'); strings=[''.join(t.itertext()) for t in texts]
allowed={'user: same message in both rows.  Grey assistant: written by the test.','Teal: assistant turn written by the model.  Depth 3 shown.','Supplied script','Own history','the test writes all of this','user','assistant','1 model call','4 model calls','1','2','3','4'}
assert set(strings)<=allowed
assert [t.text for t in texts if t.get('data-generation')]==['1','1','2','3','4']
assert len(g['generate_assistant_turns'])==4 and len(s['messages'])==7
assert all(not re.search(re.escape(w),' '.join(strings),re.I) for w in BANNED)
pt=min(float(t.get('font-size')) for t in texts)*PLACED_MM/25.4*72/WIDTH
assert pt>=8 and 275/WIDTH*PLACED_MM<=35
with (HERE/'fig1a.png').open('rb') as f: header=f.read(24)
w,h=struct.unpack('>II',header[16:24]); dpi=w/(PLACED_MM/25.4); assert dpi>=300
print(f'PASS: source conversation structure, generation counts 1 and 4, labels and banned words. Smallest text {pt:.2f} pt; height {275/WIDTH*PLACED_MM:.2f} mm; {dpi:.1f} dpi.')
