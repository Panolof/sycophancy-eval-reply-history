"""Derived numbers for the draft. Reads only script outputs; makes no model call.
Inputs : results/f-mini/f_numbers.json  (producer of block F)
         results/exploratory/x1_stats.json          (first run, Mini depth cells)
Output : report/part2_numbers.json
Run from HOME:  <venv python> -I -B analysis/derive_part2_numbers.py
Every value here is a sum or a ratio of keys in the two inputs. The key paths are in the output under "source"."""
import json, sys
sys.dont_write_bytecode = True

F = json.load(open("results/f-mini/f_numbers.json"))
X1 = json.load(open("results/exploratory/x1_stats.json"))
FM = F["models"]["gpt-5-mini-2025-08-07"]
PQ = FM["per_question"]
INC = set(FM["included"])


def fresh_cells(questions):
    out = {}
    for arm in ("S-main", "G"):
        for dep in ("1", "3"):
            p = n = 0
            for q in questions:
                for sty, c in PQ[q][arm]["pressure"][dep].items():
                    p += c["planted"]
                    n += c["n"]
            out[f"{arm}|{dep}"] = {"planted": p, "n": n, "rate_pct": round(100.0 * p / n, 2)}
    return out


def fresh_cells_kind(kind):
    qs = [q for q in INC if PQ[q]["kind"] == kind]
    return len(qs), fresh_cells(qs)


first = {}
for arm in ("S-main", "G"):
    for dep in ("1", "2", "3"):
        c = X1["models"]["mini"]["depth"][arm][dep]
        first[f"{arm}|{dep}"] = {"planted": c["planted"], "n": c["n"], "rate_pct": round(100.0 * c["planted"] / c["n"], 2)}

out = {
    "source": {
        "fresh_cells": "f_numbers.json models.gpt-5-mini-2025-08-07.per_question.<q>.<arm>.pressure.<depth>.<style> summed over models...included (37 questions); fresh_cells_all40 over all 40 questions",
        "first_run_cells": "x1_stats.json models.mini.depth.<arm>.<depth> (fields planted, n)",
        "statistic_A": "f_numbers.json models.gpt-5-mini-2025-08-07.statistic_A (mean_pp, ci95, per_repetition, n_included, n_used)",
        "control_counts": "f_numbers.json models.gpt-5-mini-2025-08-07.control_counts (all 40 questions)",
    },
    "fresh_cells_included37": fresh_cells(INC),
    "fresh_cells_all40": fresh_cells(PQ.keys()),
    "first_run_cells_mini": first,
    "statistic_A": {
        "mean_pp": round(FM["statistic_A"]["mean_pp"], 2),
        "ci95_pp": [round(100 * v, 2) for v in FM["statistic_A"]["ci95"]],
        "per_repetition_pp": {k: round(100 * v, 2) for k, v in FM["statistic_A"]["per_repetition"].items()},
        "n_included": FM["statistic_A"]["n_included"], "n_used": FM["statistic_A"]["n_used"],
    },
    "statistic_A_by_kind": {k: {"mean_pp": round(v["mean_pp"], 2), "ci95_pp": [round(100 * x, 2) for x in v["ci95"]], "n": v["n_included"]} for k, v in FM["statistic_A_by_kind"].items()},
    "statistic_B_kindA": {"mean_pp": round(FM["statistic_B"]["mean_pp"], 2), "ci95_pp": [round(100 * x, 2) for x in FM["statistic_B"]["ci95"]], "n": FM["statistic_B"]["n_included"]},
    "statistic_B_kindB": {"mean_pp": round(FM["statistic_B_kind_B"]["mean_pp"], 2), "ci95_pp": [round(100 * x, 2) for x in FM["statistic_B_kind_B"]["ci95"]], "n": FM["statistic_B_kind_B"]["n_included"]},
    "pooled_G_minus_Smain": {"G_pct": round(100 * FM["G_minus_S_main_pressure"]["G"], 2), "S_main_pct": round(100 * FM["G_minus_S_main_pressure"]["S-main"], 2),
                             "difference_pp": round(100 * FM["G_minus_S_main_pressure"]["difference"], 2),
                             "ci95_pp": [round(100 * x, 2) for x in FM["statistic_B_all_included"]["ci95"]],
                             "n_each_arm": FM["G_minus_S_main_pressure"]["n_G"]},
    "control_counts": FM["control_counts"],
    "final_label_counts": FM["final_label_counts"],
    "final_format_counts": FM["final_format_counts"],
    "kind_cells": {},
    "excluded": [{"question": e.get("question", e.get("id")), "n_control": e["n_control"], "correct": e["correct"], "planted": e.get("planted", 0)} for e in FM["excluded_items"]],
}
for k in ("A", "B"):
    n, cells = fresh_cells_kind(k)
    out["kind_cells"][k] = {"n_questions": n, "cells": cells}
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "report/part2_numbers.json", "w"), indent=1)
print("ok", out["fresh_cells_included37"]["S-main|1"], out["statistic_A"])
