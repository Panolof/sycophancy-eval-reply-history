"""Figure 3, planted answers by depth, per arm, per model. Reads results/exploratory/x1_stats.json. Writes figure_3_depth.svg.
Run from HOME:  python3 -I -B analysis/make_depth_figure.py
Exploratory layer. Counts are planted / obtained pressure conversations at the final turn (literal FINAL line)."""
import json, sys
sys.dont_write_bytecode = True
D = json.load(open("results/exploratory/x1_stats.json"))["models"]
PANELS = [("mini", "gpt-5-mini-2025-08-07", 12.0), ("haiku", "claude-haiku-4-5-20251001", 6.0)]
ARMS = [("S-original", "#7a7a7a", "S-original (supplied, 1 repetition)"), ("S-main", "#1f5fa8", "S-main (supplied)"), ("G", "#c4551a", "G (own history)")]
W, H = 760, 330
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, sans-serif" font-size="12">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Figure 3. Planted answers at the final turn, by depth (exploratory layer)</text>']
for i, (key, name, ymax) in enumerate(PANELS):
    x0, y0, pw, ph = 50 + i * 370, 50, 300, 190
    o.append(f'<text x="{x0}" y="{y0-8}" font-weight="bold">{name}</text>')
    for t in range(0, int(ymax) + 1, 3 if ymax > 7 else 2):
        y = y0 + ph - ph * t / ymax
        o.append(f'<line x1="{x0}" x2="{x0+pw}" y1="{y:.1f}" y2="{y:.1f}" stroke="#dddddd"/><text x="{x0-6}" y="{y+4:.1f}" text-anchor="end">{t}%</text>')
    for d in (1, 2, 3):
        x = x0 + 40 + (d - 1) * (pw - 80) / 2
        o.append(f'<text x="{x:.1f}" y="{y0+ph+16}" text-anchor="middle">depth {d}</text>')
    for arm, col, _ in ARMS:
        pts = []
        for d in (1, 2, 3):
            c = D[key]["depth"][arm][str(d)]
            r = 100.0 * c["planted"] / c["n"]
            x = x0 + 40 + (d - 1) * (pw - 80) / 2
            y = y0 + ph - ph * r / ymax
            pts.append((x, y, c["planted"], c["n"]))
        o.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>' % (col, " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)))
        for x, y, p, n in pts:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{col}"/><text x="{x+5:.1f}" y="{y-6:.1f}" font-size="10" fill="{col}">{p}/{n}</text>')
for j, (arm, col, lab) in enumerate(ARMS):
    o.append(f'<line x1="{50+j*230}" x2="{74+j*230}" y1="285" y2="285" stroke="{col}" stroke-width="2"/><text x="{80+j*230}" y="289">{lab}</text>')
o.append('<text x="12" y="316" font-size="11">Planted / obtained pressure conversations. Source: results/exploratory/x1_stats.json, key models.&lt;model&gt;.depth.&lt;arm&gt;.&lt;depth&gt;.</text>')
o.append('</svg>')
open(sys.argv[1] if len(sys.argv) > 1 else "report/figure_3_depth.svg", "w").write("\n".join(o))
print("ok")
