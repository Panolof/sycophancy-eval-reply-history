import json,re,struct,sys,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;IMG=HERE.parent;HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'data/arms_F.json').read_text());get=lambda s,c:next(r for r in d['G'] if r['id']==f'adult_teeth_count__{s}__d3__{c}')['users'][1:];cols=[get('direct','control'),get('direct','pressure'),get('expert','pressure')];root=ET.parse(HERE/'g2.svg').getroot();ts=root.findall('.//{http://www.w3.org/2000/svg}text'); vals=[x.text or '' for x in ts]
for i in range(3):
 for j in range(3):
  cells=[x for x in ts if x.get('data-cell')==f'{i}-{j}'];assert cells and ' '.join(' '.join(x.text or '' for x in cells).split())==' '.join(cols[j][i].split())
assert all(not re.search(re.escape(w),' '.join(vals),re.I) for w in BANNED)
pt=min(float(x.get('font-size')) for x in ts)*PLACED_MM/25.4*72/WIDTH;assert pt>=8
with (HERE/'g2.png').open('rb') as f:f.read(16);w,h=struct.unpack('>II',f.read(8))
assert w/(PLACED_MM/25.4)>=300
print(f'PASS: all nine cells match frozen user messages; banned words absent; text {pt:.2f} pt; height {1000/WIDTH*PLACED_MM:.2f} mm.')
