"""Figure 1 for the main text. Share of Mini pressure conversations that gave the planted answer at the
final turn, by depth, per arm (supplied S-main, own G). Three panels, each with its own style set and label:
  A  first run, all three styles (direct, expert, weak), depths 1, 2, 3, 270 per cell   (exploratory: found after looking)
  B  first run recut to direct and expert, depths 1 and 3, 180 per cell                  (exploratory: recut after looking)
  C  fresh run, direct and expert, depths 1 and 3, 222 per cell                          (pre-registered)
Panels B and C draw only the depths that exist in their statistic: no depth-2 point and no depth-2 tick.
Every number and label word comes from a file (nothing is typed in):
  A  results/exploratory/x1_stats.json            keys models.mini.depth.<arm>.<depth>
  B  results/exploratory/first_run_recut.json   keys results.direct_expert.styles, .pooled.cells, .pooled.n_questions
  C  results/f-mini/f_numbers.json    keys models.gpt-5-mini-2025-08-07.per_question, .included, .repetitions_whole
Writes: report/figure_1_crossing.svg
Run from HOME:  <venv python> -I -B analysis/make_figure_crossing.py
Same y scale in all panels (0 to 25%)."""
import json, sys
sys.dont_write_bytecode = True

X1 = json.load(open("results/exploratory/x1_stats.json"))["models"]["mini"]["depth"]
RC = json.load(open("results/exploratory/first_run_recut.json"))["results"]["direct_expert"]
F = json.load(open("results/f-mini/f_numbers.json"))["models"]["gpt-5-mini-2025-08-07"]
PQ, INC = F["per_question"], F["included"]
REPS = len(F["repetitions_whole"])

# all three first-run styles: the style keys that X1 itself used (read from the file, not typed)
X1_STYLES = list(json.load(open("results/exploratory/x1_stats.json"))["models"]["mini"]["depth_by_style"]["S-main"].keys())
assert set(RC["styles"]) <= set(X1_STYLES)


def fresh(arm, dep):
    p = n = 0
    styles = None
    for q in INC:
        cells = PQ[q][arm]["pressure"][str(dep)]
        styles = sorted(cells.keys())
        for c in cells.values():
            p += c["planted"]; n += c["n"]
    return p, n, styles


ARMS = [("S-main", "#1f5fa8", "supplied script"), ("G", "#c4551a", "own history")]
fresh_styles = fresh("S-main", 1)[2]
nq_first = RC["pooled"]["n_questions"]
PANELS = [
    (f"A. First run, {len(X1_STYLES)} styles (" + ", ".join(X1_STYLES) + ")",
     f"{nq_first} questions, {REPS} repetitions. Exploratory: found after looking.",
     {a: {d: (X1[a][str(d)]["planted"], X1[a][str(d)]["n"]) for d in (1, 2, 3)} for a, _, _ in ARMS}, (1, 2, 3)),
    ("B. First run, " + " and ".join(RC["styles"]) + " only",
     f"{nq_first} questions, {REPS} repetitions. Exploratory: recut after looking.",
     {a: {d: (RC["pooled"]["cells"][f"{a}|{d}"]["planted"], RC["pooled"]["cells"][f"{a}|{d}"]["n"]) for d in (1, 3)} for a, _, _ in ARMS}, (1, 3)),
    ("C. Fresh run, " + " and ".join(fresh_styles) + " only",
     f"{len(INC)} questions, {REPS} repetitions. Pre-registered.",
     {a: {d: fresh(a, d)[:2] for d in (1, 3)} for a, _, _ in ARMS}, (1, 3)),
]
YMAX = 25.0
PW, PH, GAP = 270, 180, 70
W, H = 60 + 3 * (PW + GAP) - GAP + 20, 340
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, sans-serif" font-size="12">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Figure 1. Planted answers by depth, supplied against own history (GPT-5-mini, pressure conversations)</text>']
for i, (title, sub, data, depths) in enumerate(PANELS):
    x0, y0 = 60 + i * (PW + GAP), 78
    o.append(f'<text x="{x0-30}" y="{y0-26}" font-size="11" font-weight="bold">{title}</text>')
    o.append(f'<text x="{x0-30}" y="{y0-12}" font-size="10" fill="#444444">{sub}</text>')
    for t in range(0, int(YMAX) + 1, 5):
        y = y0 + PH - PH * t / YMAX
        o.append(f'<line x1="{x0}" x2="{x0+PW}" y1="{y:.1f}" y2="{y:.1f}" stroke="#dddddd"/><text x="{x0-6}" y="{y+4:.1f}" text-anchor="end" fill="#444444">{t}%</text>')
    span = max(depths) - min(depths)
    xs = {d: x0 + 40 + (d - min(depths)) * (PW - 80) / span for d in depths}
    for d in depths:  # ticks only for depths that the panel's statistic uses
        o.append(f'<text x="{xs[d]:.1f}" y="{y0+PH+16}" text-anchor="middle" fill="#444444">depth {d}</text>')
    for arm, col, _ in ARMS:
        pts = []
        for d in depths:
            p, n = data[arm][d]
            r = 100.0 * p / n
            pts.append((xs[d], y0 + PH - PH * r / YMAX, p, n, d))
        o.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (col, " ".join(f"{x:.1f},{y:.1f}" for x, y, *_ in pts)))
        for x, y, p, n, d in pts:
            dy = -9 if (arm == "S-main") == (d == min(depths)) else 16
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"/><text x="{x+8:.1f}" y="{y+dy:.1f}" font-size="11" fill="{col}">{p}/{n}</text>')
for j, (arm, col, lab) in enumerate(ARMS):
    o.append(f'<line x1="{30+j*220}" x2="{56+j*220}" y1="292" y2="292" stroke="{col}" stroke-width="2.5"/><text x="{62+j*220}" y="296">{lab} ({arm})</text>')
o.append('<text x="12" y="318" font-size="10" fill="#444444">Planted / obtained pressure conversations at the final turn, literal FINAL line. Same y scale in all panels. The questions are the unit of analysis.</text>')
o.append(f'<text x="12" y="331" font-size="10" fill="#444444">Sources: x1_stats.json models.mini.depth; first_run_recut_run3.json results.direct_expert.pooled.cells; f_numbers.json models.gpt-5-mini-2025-08-07.per_question ({len(INC)} included questions).</text>')
o.append('</svg>')
open(sys.argv[1] if len(sys.argv) > 1 else "report/figure_1_crossing.svg", "w").write("\n".join(o))
print("ok", {a: PANELS[2][2][a] for a in PANELS[2][2]}, {a: PANELS[1][2][a] for a in PANELS[1][2]})
