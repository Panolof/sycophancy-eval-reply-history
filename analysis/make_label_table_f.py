"""Print the block F table of final-turn labels, by arm, depth and condition, as Markdown.

Source: results/f-mini/f_numbers.json, model gpt-5-mini-2025-08-07,
key `M3_by_arm_depth_style_kind` (counts per arm, condition, depth, style and question kind;
labels correct, planted, unresolved, other). This script sums the style and kind levels, over
all 40 questions and all obtained conversations (no inclusion rule). It checks the sums against
`final_label_counts` (1,920 obtained) and `control_counts`. It also writes label_table_f.json
(beside this script) so the number checker can read every figure in the table.

    python3 -I -B \
        analysis/make_label_table_f.py > label_table_f.md

If f_numbers.json lacked this breakdown, the script would stop with an error; it does not.
Calls no model. Writes only label_table_f.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
SRC = "results/f-mini/f_numbers.json"
MODEL = "gpt-5-mini-2025-08-07"
LABELS = ["correct", "planted", "unresolved", "other"]
ARMS = [("S-main", "Supplied script (S-main)"), ("G", "Own history (G)")]
CONDS = ["pressure", "control"]


def main() -> int:
    d = json.loads((HOME / SRC).read_text(encoding="utf-8"))["models"][MODEL]
    m3 = d["M3_by_arm_depth_style_kind"]
    cells: dict = {}
    for arm, _ in ARMS:
        for cond in CONDS:
            for depth in sorted(m3[arm][cond], key=int):
                tot = {k: 0 for k in LABELS}
                tot["obtained"] = 0
                tot["no_final"] = 0
                for style, kinds in m3[arm][cond][depth].items():
                    for kind, c in kinds.items():
                        tot["obtained"] += c["n_obtained"]
                        tot["no_final"] += c["no_final"]
                        tot["planted"] += c["planted"]
                        for k in ("correct", "unresolved", "other"):
                            tot[k] += c["counts"].get(k, 0)
                        assert sum(c["counts"].get(k, 0) for k in ("correct", "unresolved", "other")) + c["planted"] == c["n_obtained"], (arm, cond, depth, style, kind)
                cells[(arm, cond, depth)] = tot
    # checks against the file's own totals
    fl = d["final_label_counts"]
    grand = {k: sum(c[k] for c in cells.values()) for k in LABELS}
    grand_n = sum(c["obtained"] for c in cells.values())
    assert grand == {k: fl[k] for k in LABELS}, (grand, fl)
    assert grand_n == 1920 and sum(fl.values()) == 1920
    cc = d["control_counts"]
    for arm, _ in ARMS:
        ctrl = {k: sum(cells[(arm, "control", dp)][k] for dp in ("1", "3")) for k in ("correct", "planted", "other", "unresolved")}
        # control_counts files `unresolved` finals under `other`
        assert ctrl["correct"] == cc[arm]["correct"] and ctrl["planted"] == cc[arm]["planted"] and ctrl["other"] + ctrl["unresolved"] == cc[arm]["other"], (arm, ctrl, cc[arm])
    assert all(c["no_final"] == 0 for c in cells.values())

    out = []
    P = out.append
    P("**Table B1a. Final-turn labels of the fresh run by arm, depth and condition (Mini, all 40 questions, no inclusion rule).** "
      "Each cell is the count of obtained final turns with that literal label, of the obtained conversations in the cell. "
      "Styles (direct, expert), question kinds and the three repetitions are summed. Percentages are of the obtained "
      "conversations in the row. Labels: `correct` and `planted` are the two values; `unresolved` is no single final value; "
      "`other` is a final value that is neither. A label is the parse of the `FINAL:` line only; it says nothing about the body "
      "of the reply or about why the model gave it.")
    P("")
    P("| Arm | Condition | Depth | Correct | Planted | Unresolved | Other | Obtained |")
    P("|---|---|---|---:|---:|---:|---:|---:|")
    for arm, name in ARMS:
        for cond in CONDS:
            for depth in ("1", "3"):
                c = cells[(arm, cond, depth)]
                n = c["obtained"]
                row = " | ".join(f"{c[k]} ({100 * c[k] / n:.1f}%)" for k in LABELS)
                P(f"| {name} | {cond} | {depth} | {row} | {n} |")
    tot = {k: grand[k] for k in LABELS}
    P("| All cells | both | 1 and 3 | " + " | ".join(f"{tot[k]} ({100 * tot[k] / grand_n:.1f}%)" for k in LABELS) + f" | {grand_n} |")
    P("")
    P(f"Source: `{SRC}`, model `{MODEL}`, key `M3_by_arm_depth_style_kind` "
      "(path `<arm>.<condition>.<depth>.<style>.<kind>`, fields `counts`, `planted`, `n_obtained`), summed by "
      "`analysis/make_label_table_f.py`. The script checks its sums against `final_label_counts` "
      "(1,590 correct, 143 planted, 126 unresolved, 61 other, of 1,920) and `control_counts` in the same file (which files unresolved finals under `other`), and "
      "finds no obtained conversation without a final value. The planted cells of the pressure rows are the four cells of Table 1 "
      "on all 40 questions, not on the 37 included. `G-check/f_extract_gcheck.jsonl` was not needed: the producer's file holds the breakdown.")
    sys.stdout.write("\n".join(out) + "\n")

    j = {f"{a}|{c}|{dp}": v for (a, c, dp), v in cells.items()}
    for v in j.values():
        n = v.get("obtained", grand_n)
        v["percent"] = {k: 100 * v[k] / n for k in LABELS}
    j["grand"] = {**grand, "obtained": grand_n, "percent": {k: 100 * grand[k] / grand_n for k in LABELS}}
    (Path(sys.argv[1]) if len(sys.argv) > 1 else HOME / "report/label_table_f.json").write_text(json.dumps(j, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
