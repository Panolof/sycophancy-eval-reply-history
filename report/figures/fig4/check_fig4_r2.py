import json,re,struct,sys,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent; IMG=HERE.parent;HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'results/h-mini/h_numbers.json').read_text())['pooled_counts'];root=ET.parse(HERE/'fig4_r2.svg').getroot(); ns='{http://www.w3.org/2000/svg}';ts=root.findall('.//'+ns+'text');vals=[x.text for x in ts]; bars=[x for x in root.findall('.//'+ns+'rect') if x.get('data-arm')]
assert len(bars)==4
assert [x.text for x in ts if x.get('data-generation')]==['1','1','2','3']
for b in bars:
 a=b.get('data-arm');v=d[a]; assert b.get('fill')=={'S-main':'#777777','H':'#707878','G':TEAL,'S-prime':'#aaaaaa'}[a]; assert b.get('fill')!=TEAL or a=='G'; assert abs(float(b.get('width'))-v['planted']*8)<=.5 and int(b.get('data-count'))==v['planted'];assert f"{v['planted']}/{v['obtained']}" in vals
assert [(d[a]['planted'],d[a]['obtained']) for a in ('S-main','H','G','S-prime')]==[(29,222),(9,222),(36,222),(25,222)]
assert all(not re.search(re.escape(w),' '.join(vals),re.I) for w in BANNED)
pt=min(float(t.get('font-size')) for t in ts)*PLACED_MM/25.4*72/WIDTH;assert pt>=8 and 275/WIDTH*PLACED_MM<=35
with (HERE/'fig4_r2.png').open('rb') as f:f.read(16);w,h=struct.unpack('>II',f.read(8))
assert w/(PLACED_MM/25.4)>=300
print(f'PASS: 29, 9, 36, 25 of 222; SVG bar lengths proportional within 0.5 px; text {pt:.2f} pt; height {275/WIDTH*PLACED_MM:.2f} mm.')
