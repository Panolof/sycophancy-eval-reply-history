"""Build the three-panel figure for the report. Stdlib only.
  A  GPT-5-mini, fresh questions: the four cells (supplied S-main and own G, depths 1 and 3), planted / obtained
     pressure conversations, 37 included questions, 222 per cell.                    (block F-M, pre-registered)
  B  GPT-5-mini, depth three: the three histories and the anchor. S-main (supplied script), S' (the anchor: the
     same script rerun in the later session), H (own first answer, supplied later turns), G (own turns
     throughout). 222 per arm.                                                      (block H-M, pre-registered)
  C  Claude Haiku 4.5, fresh questions: the four cells, 26 included questions, 52 per cell, one repetition.
                                                                                    (block F-H, pre-registered)
Every number and label word comes from a file (nothing is typed in):
  A  results/f-mini/f_numbers.json   models.gpt-5-mini-2025-08-07.per_question, .included
  B  results/h-mini/h_numbers.json   pooled_counts (included questions, depth 3, pressure),
                                                            first_answer / later_turn / anchor (mean_pp, ci95)
  C  results/f-haiku/f_numbers.json  models.claude-haiku-4-5-20251001.per_question, .included
The script also asserts the cells against the recorded counts (29/222, 51/222, 36/222, 14/222; 9/222 and
anchor 25/222; 16, 3, 13, 13 of 52) so that a changed input stops it.
Run from HOME:  python3 -I -B <path>/make_figure_fh.py [output.svg]
Default output: report/figure_fh_three_panels.svg   Same y scale in all panels (0 to 35%)."""
import json, sys
sys.dont_write_bytecode = True

OUT = sys.argv[1] if len(sys.argv) > 1 else "report/figure_fh_three_panels.svg"
AN = "results/"
F = json.load(open(AN + "f-mini/f_numbers.json"))["models"]["gpt-5-mini-2025-08-07"]
HN = json.load(open(AN + "h-mini/h_numbers.json"))
FH = json.load(open(AN + "f-haiku/f_numbers.json"))["models"]["claude-haiku-4-5-20251001"]


def cells(block):
    """sum of per_question[q][arm].pressure[depth][style] planted / n over the included questions"""
    out = {}
    for arm in ("S-main", "G"):
        for dep in ("1", "3"):
            p = n = 0
            for q in block["included"]:
                for c in block["per_question"][q][arm]["pressure"][dep].values():
                    p += c["planted"]; n += c["n"]
            out[(arm, int(dep))] = (p, n)
    return out


CA, CC = cells(F), cells(FH)
HB = HN["pooled_counts"]
CB = {a: (HB[a]["planted"], HB[a]["obtained"]) for a in ("S-main", "S-prime", "H", "G")}
assert len(F["included"]) == 37 and len(FH["included"]) == 26 and HN["first_answer"]["n_used"] == 37
assert CA == {("S-main", 1): (51, 222), ("S-main", 3): (29, 222), ("G", 1): (14, 222), ("G", 3): (36, 222)}, CA
assert CB == {"S-main": (29, 222), "S-prime": (25, 222), "H": (9, 222), "G": (36, 222)}, CB
assert CC == {("S-main", 1): (16, 52), ("S-main", 3): (3, 52), ("G", 1): (13, 52), ("G", 3): (13, 52)}, CC


def pp(block, key):
    b = block[key]
    return b["mean_pp"], [100 * x for x in b["ci95"]]


def fmt(m, ci):
    return f"{m:+.1f} pp [{ci[0]:+.1f}, {ci[1]:+.1f}]"


FA, LT, ANC = pp(HN, "first_answer"), pp(HN, "later_turn"), pp(HN, "anchor")
ARMS = [("S-main", "#1f5fa8", "supplied script (S-main)"), ("G", "#c4551a", "own history (G)")]
YMAX = 35.0
PW, PH, GAP = 270, 190, 70
W, H = 60 + 3 * (PW + GAP) - GAP + 20, 440
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, sans-serif" font-size="12">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Figure 1. Planted values printed on the final line, by history (pressure conversations; all three blocks pre-registered)</text>']
TITLES = [
    ("A. GPT-5-mini, fresh questions: four cells", f"block F-M; {len(F['included'])} questions; depth 1 and 3; 222 per cell."),
    ("B. GPT-5-mini, depth three: three histories and the anchor", f"block H-M; {len(F['included'])} questions; 222 per arm."),
    ("C. Claude Haiku 4.5, fresh questions: four cells", f"block F-H; {len(FH['included'])} questions; one repetition; 52 per cell."),
]


def yy(y0, rate):
    return y0 + PH - PH * rate / YMAX


def axes(x0, y0):
    for t in range(0, int(YMAX) + 1, 5):
        y = yy(y0, t)
        o.append(f'<line x1="{x0}" x2="{x0+PW}" y1="{y:.1f}" y2="{y:.1f}" stroke="#dddddd"/><text x="{x0-6}" y="{y+4:.1f}" text-anchor="end" fill="#444444">{t}%</text>')


def lines_panel(i, data):
    x0, y0 = 60 + i * (PW + GAP), 80
    o.append(f'<text x="{x0-30}" y="{y0-28}" font-size="11" font-weight="bold">{TITLES[i][0]}</text>')
    o.append(f'<text x="{x0-30}" y="{y0-14}" font-size="10" fill="#444444">{TITLES[i][1]}</text>')
    axes(x0, y0)
    xs = {1: x0 + 40, 3: x0 + PW - 40}
    for d in (1, 3):
        o.append(f'<text x="{xs[d]:.1f}" y="{y0+PH+16}" text-anchor="middle" fill="#444444">depth {d}</text>')
    for arm, col, _ in ARMS:
        pts = []
        for d in (1, 3):
            p, n = data[(arm, d)]
            pts.append((xs[d], yy(y0, 100.0 * p / n), p, n, d))
        o.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (col, " ".join(f"{x:.1f},{y:.1f}" for x, y, *_ in pts)))
        for x, y, p, n, d in pts:
            dy = -9 if (arm == "S-main") == (d == 1) else 16
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"/><text x="{x+8:.1f}" y="{y+dy:.1f}" font-size="11" fill="{col}">{p}/{n}</text>')


def bars_panel(i, data):
    x0, y0 = 60 + i * (PW + GAP), 80
    o.append(f'<text x="{x0-30}" y="{y0-28}" font-size="11" font-weight="bold">{TITLES[i][0]}</text>')
    o.append(f'<text x="{x0-30}" y="{y0-14}" font-size="10" fill="#444444">{TITLES[i][1]}</text>')
    axes(x0, y0)
    order = [("S-main", "#1f5fa8", "supplied", None), ("S-prime", "#1f5fa8", "anchor", "hollow"),
             ("H", "#7a4fa3", "own 1st,\nsupplied later", None), ("G", "#c4551a", "own\nthroughout", None)]
    bw = 40
    step = (PW - 20) / len(order)
    for j, (arm, col, lab, style) in enumerate(order):
        p, n = data[arm]
        r = 100.0 * p / n
        bx = x0 + 10 + j * step + (step - bw) / 2
        by = yy(y0, r)
        if style == "hollow":
            o.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{y0+PH-by:.1f}" fill="#ffffff" stroke="{col}" stroke-width="2" stroke-dasharray="4 3"/>')
        else:
            o.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{y0+PH-by:.1f}" fill="{col}"/>')
        o.append(f'<text x="{bx+bw/2:.1f}" y="{by-5:.1f}" text-anchor="middle" font-size="11" fill="{col}">{p}/{n}</text>')
        for k, part in enumerate(lab.split("\n")):
            o.append(f'<text x="{bx+bw/2:.1f}" y="{y0+PH+14+11*k}" text-anchor="middle" font-size="9.5" fill="#444444">{part}</text>')
    o.append(f'<text x="{x0-30}" y="{y0+PH+44}" font-size="9.5" fill="#444444">first-answer part (H minus S-main) {fmt(*FA)}</text>')
    o.append(f'<text x="{x0-30}" y="{y0+PH+56}" font-size="9.5" fill="#444444">later-turn part (G minus H) {fmt(*LT)}</text>')
    o.append(f'<text x="{x0-30}" y="{y0+PH+68}" font-size="9.5" fill="#444444">anchor (S\' minus S-main) {fmt(*ANC)}</text>')


lines_panel(0, CA)
bars_panel(1, CB)
lines_panel(2, CC)
for j, (arm, col, lab) in enumerate(ARMS):
    o.append(f'<line x1="{30+j*230}" x2="{56+j*230}" y1="372" y2="372" stroke="{col}" stroke-width="2.5"/><text x="{62+j*230}" y="376">{lab}</text>')
o.append('<text x="12" y="406" font-size="10" fill="#444444">Planted / obtained pressure conversations at the final turn, literal FINAL line. Same y scale in all panels. Questions are the unit of analysis; intervals are over questions.</text>')
o.append('<text x="12" y="419" font-size="10" fill="#444444">Sources: f_numbers.json (F_numbers, FH_numbers) per_question and included; h_numbers.json pooled_counts, first_answer, later_turn, anchor. The two parts sum to G minus S-main by construction.</text>')
o.append('</svg>')
open(OUT, "w").write("\n".join(o))
print("ok", OUT, {"A": {f"{a}{d}": v for (a, d), v in CA.items()}, "B": CB, "C": {f"{a}{d}": v for (a, d), v in CC.items()}})
