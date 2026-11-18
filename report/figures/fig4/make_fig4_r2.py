"""Draw the three assistant histories and their split-run counts."""
import json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; IMG=HERE.parent; HOME=IMG.parents[1];sys.path.insert(0,str(IMG))
from style import *
d=json.loads((HOME/'results/h-mini/h_numbers.json').read_text())['pooled_counts']; assert [(d[a]['planted'],d[a]['obtained']) for a in ('S-main','H','G','S-prime')]==[(29,222),(9,222),(36,222),(25,222)]
svg=start(275);text(svg,15,28,'Grey: test-written turn.  Teal: model-written turn.  Bars: planted answers.',24)
rows=[('S-main','Supplied script',(0,0,0)),('H','Own first answer, supplied later turns',(1,0,0)),('G','Own history',(1,1,1)),('S-prime','Supplied script, rerun in the split session',(0,0,0))]
for i,(arm,label,turns) in enumerate(rows):
 y=53+i*53
 text(svg,15,y+24,label,23,textLength=490,lengthAdjust='spacingAndGlyphs')
 for j,own in enumerate(turns):
  rect(svg,530+62*j,y,53,34,TEAL if own else GREY,BORDER,rx=3)
  if own: text(svg,556.5+62*j,y+25,str(j+1),23,WHITE,'middle','bold',data_generation=str(j+1))
 val=d[arm];rect(svg,744,y+3,val['planted']*8,28,{'S-main':'#777777','H':'#707878','G':TEAL,'S-prime':'#aaaaaa'}[arm],data_arm=arm,data_count=val['planted']);text(svg,1055,y+25,f"{val['planted']}/{val['obtained']}",24)
svg.append('</svg>');(HERE/'fig4_r2.svg').write_text('\n'.join(svg))
for w,n in ((1950,'fig4_r2.png'),):subprocess.run(['rsvg-convert','-w',str(w),'-o',str(HERE/n),str(HERE/'fig4_r2.svg')],check=True)
