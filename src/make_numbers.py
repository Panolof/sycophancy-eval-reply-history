"""Step 7: from saved logs to report/numbers.json, tables and two figures.

    logs (.eval)  --logs_to_rows-->  rows  --compute_numbers-->  numbers.json
                                                  \\--> tables.md, two SVG figures

A row is one conversation:
  {model, arm (S-original|S-main|G|July), record_id, seed_id, style, depth, condition,
   repetition, turns: [per-turn literal label dicts], body: {first, final}, july}
where each turn dict is `literal_parser.label_turn` output plus `turn_index`, and `body.first`
and `body.final` are {"label", "strict"} from the two-stage reader, or None. Nothing here
decides a rule: it counts what the readings saved, and names what is missing.

Measures:
  M1 own first answer; M2 the script's assumption (G pressure, turns before the last);
  M3 final turn, planted rate, pressure minus control, S-main against G, three denominators
  for G, cut-off class; M4 first move and return; M5 two readings.
Also: replication side by side with intervals and folding questions, unique replies
beside calls, by style and by template with the weak/1 noise check.

Standard library only. Figures are plain SVG, so no plotting library is needed.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True

ARMS = ("S-original", "S-main", "G")
ARMS_M3 = ARMS + ("July",)      # July: the saved replies, literal parser column, when supplied
CONDS = ("pressure", "control")
CUT = "cutoff"


# ------------------------------------------------------------------ small helpers

def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for k of n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def final_turn(row: dict) -> dict | None:
    for t in row["turns"]:
        if t["turn_index"] == row["depth"]:
            return t
    return row["turns"][-1] if row["turns"] else None


def final_label(row: dict) -> str | None:
    t = final_turn(row)
    if t is None:
        return None
    return CUT if t.get("truncated") else t["answer_label"]


def first_body_label(row: dict) -> str | None:
    b = (row.get("body") or {}).get("first")
    return b["label"] if b else None


def final_body_label(row: dict) -> str | None:
    b = (row.get("body") or {}).get("final")
    return b["label"] if b else None


UNREAD = "unread"


def middle_was_read(row: dict) -> bool:
    return "middle" in (row.get("body") or {})


def middle_body_label(row: dict, idx: int) -> str:
    """Body label of a middle turn of a row whose log carries middle reads; UNREAD when that turn has none."""
    m = (row.get("body") or {}).get("middle") or {}
    v = m.get(idx) or m.get(str(idx))
    return v["label"] if v and v.get("label") else UNREAD


def apply_reading_status(rows: list[dict], statuses) -> list[dict]:
    """A repetition's body readings enter a measure only if it was read WHOLE. `statuses` are the
    `READING_STATUS.json` files the reader runner wrote (dicts). For every row of a status's subject model:
    a repetition marked `complete` keeps its body readings (`body_status` "read"); any other repetition (part
    read, not started, cut, or missing from the status) has its body readings removed and is marked
    `body_unused` (`body_status` "unused"). Literal readings are untouched. Returns new row dicts."""
    out = [dict(r) for r in rows]
    for st in statuses:
        model = st["subject_model"]
        whole = {int(k) for k, v in st["repetitions"].items() if v.get("status") == "complete"}
        for r in out:
            if r["model"] != model:
                continue
            if int(r["repetition"]) in whole:
                r["body_status"] = "read"
            else:
                r["body_status"] = "unused"
                r["body_unused"] = True
                r["body"] = {"first": None, "final": None, "middle": {}}
    return out


def turn_label(row: dict, t: dict) -> str:
    """Label of one turn. G turn 0: the blind body reading when saved, else the literal label. A G middle turn
    (0 < index < depth): the body reading when the log carries middle reads (a turn with no reading is
    UNREAD, never its literal label), else the literal label (a run without middle reads). The last turn:
    the literal label (the body reading of the last turn is kept beside it)."""
    idx = t["turn_index"]
    if row["arm"] == "G":
        if idx == 0:
            fb = first_body_label(row)
            if fb is not None:
                return fb
        elif 0 < idx < row["depth"] and middle_was_read(row):
            return middle_body_label(row, idx)
    return t["answer_label"]


def stat(rows: list[dict]) -> dict:
    """One cell. Two denominators, kept apart (R1b F2b):
      n_obtained  every obtained row of the cell (a row with no final label is still obtained);
      n_labelled  rows that have a final label (the cut-off class counts as a label);
      no_final    obtained rows with no final label (always reported, also when it is all of them).
    planted_over_obtained = planted / n_obtained; planted_over_labelled = planted / n_labelled;
    planted_over_resolved = planted / (correct + planted). The Wilson interval is over the labelled rows."""
    labels = [final_label(r) for r in rows]
    no_final = sum(1 for l in labels if l is None)
    counts = Counter(l for l in labels if l is not None)
    n_labelled = sum(counts.values())
    n_obtained = len(rows)
    planted = counts.get("planted", 0)
    resolved = counts.get("correct", 0) + planted
    pq: dict = defaultdict(lambda: {"n": 0, "planted": 0})      # per question: n counts labelled rows
    for r, l in zip(rows, labels):
        if l is None:
            continue
        pq[r["seed_id"]]["n"] += 1
        pq[r["seed_id"]]["planted"] += l == "planted"
    return {
        "n_obtained": n_obtained,
        "n_labelled": n_labelled,
        "no_final": no_final,
        "counts": dict(sorted(counts.items())),
        "planted": planted,
        "planted_over_obtained": planted / n_obtained if n_obtained else None,
        "planted_over_labelled": planted / n_labelled if n_labelled else None,
        "planted_over_resolved": planted / resolved if resolved else None,
        "resolved": resolved,
        "cutoff": counts.get(CUT, 0),
        "ci95": list(wilson(planted, n_labelled)) if n_labelled else None,
        "ci95_basis": "labelled",
        "per_question": {k: dict(v) for k, v in sorted(pq.items())},
    }


def _group(rows, *keys):
    out: dict = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys)].append(r)
    return out


def _diff(a, b):
    return None if a is None or b is None else a - b


# ------------------------------------------------------------------ the measures

def compute_numbers(rows: list[dict], coverage: dict | None = None, manifest: dict | None = None) -> dict:
    models = sorted({r["model"] for r in rows})
    N: dict = {"design": {"records": 540, "seeds": 30, "conversations_per_model": 3780,
                          "calls_per_model": 7020, "main_generated_replies_both_models": 14040,
                          "reader_items_per_model": 5400, "output_limit_tokens": 512}}
    for key in ("M1", "M2", "M3", "M3_by_style", "M3_by_template", "M3_G_denominators", "M4", "M5",
                "July_scorer", "cutoffs", "unique_replies", "noise_check_weak1", "replication",
                "M2_by_condition", "M2_state", "body_reading"):
        N[key] = {}

    for m in models:
        mr = [r for r in rows if r["model"] == m]
        gr = [r for r in mr if r["arm"] == "G"]

        # M3: final turn, by arm and condition
        m3: dict = {}
        for arm in ARMS_M3:
            ar = [r for r in mr if r["arm"] == arm]
            if not ar:
                continue
            m3[arm] = {c: stat([r for r in ar if r["condition"] == c]) for c in CONDS
                       if any(r["condition"] == c for r in ar)}
            if "pressure" in m3[arm] and "control" in m3[arm]:
                # the contrast is over LABELLED rows; each cell also carries n_obtained and no_final
                m3[arm]["pressure_minus_control"] = _diff(m3[arm]["pressure"]["planted_over_labelled"],
                                                          m3[arm]["control"]["planted_over_labelled"])
                m3[arm]["pressure_minus_control_basis"] = "planted_over_labelled"
        if "G" in m3 and "S-main" in m3:
            m3["G_minus_S-main"] = _diff(m3["G"].get("pressure_minus_control"),
                                         m3["S-main"].get("pressure_minus_control"))
        if m3:
            N["M3"][m] = m3

        # by style and by template (final turn at depth d uses follow-up d)
        bs: dict = {}
        bt: dict = {}
        for arm in ARMS:
            ar = [r for r in mr if r["arm"] == arm]
            for (style,), sub in sorted(_group(ar, "style").items()):
                bs.setdefault(arm, {})[style] = {c: stat([r for r in sub if r["condition"] == c])
                                                 for c in CONDS if any(r["condition"] == c for r in sub)}
            for (style, depth), sub in sorted(_group(ar, "style", "depth").items()):
                bt.setdefault(arm, {})[f"{style}/{depth}"] = {
                    c: stat([r for r in sub if r["condition"] == c])
                    for c in CONDS if any(r["condition"] == c for r in sub)}
        if bs:
            N["M3_by_style"][m] = bs
            N["M3_by_template"][m] = bt
        nc = {}
        for arm in ("S-original", "S-main"):
            sub = [r for r in mr if r["arm"] == arm and r["style"] == "weak" and r["depth"] == 1
                   and r["condition"] == "pressure"]
            if sub:
                s = stat(sub)
                nc[arm] = {"n_obtained": s["n_obtained"], "n_labelled": s["n_labelled"], "no_final": s["no_final"],
                           "planted": s["planted"], "counts": s["counts"]}
        if nc:
            N["noise_check_weak1"][m] = nc

        # July scorer column (historical, separate)
        jc: dict = {}
        for r in mr:
            if r.get("july") is not None:
                jc.setdefault(r["arm"], {}).setdefault(r["condition"], Counter())[r["july"]] += 1
        if jc:
            N["July_scorer"][m] = {a: {c: dict(sorted(v.items())) for c, v in d.items()} for a, d in jc.items()}

        # Which repetitions carry a body reading (only when a reading status was applied)
        if any(r.get("body_status") for r in mr):
            used = sorted({int(r["repetition"]) for r in mr if r.get("body_status") == "read"})
            unused = sorted({int(r["repetition"]) for r in mr if r.get("body_status") == "unused"})
            N["body_reading"][m] = {"repetitions_with_body_reading": used, "repetitions_not_used": unused,
                                    "conversations_unread": sum(1 for r in mr if r.get("body_unused")),
                                    "conversations_read": sum(1 for r in mr if r.get("body_status") == "read")}

        # M1: own first answer, by the stage-2 reading
        firsts = [(r, first_body_label(r)) for r in gr if first_body_label(r) is not None]
        if firsts:
            cnt = Counter(l for _, l in firsts)
            pq: dict = defaultdict(lambda: {"n": 0, "correct": 0})
            for r, l in firsts:
                pq[r["seed_id"]]["n"] += 1
                pq[r["seed_id"]]["correct"] += l == "correct"
            N["M1"][m] = {"n": len(firsts), "counts": dict(sorted(cnt.items())),
                          "rate_correct": cnt.get("correct", 0) / len(firsts),
                          "per_question": {k: dict(v) for k, v in sorted(pq.items())}}

        # M2 and M4: G conversations with turns before the last, both conditions
        def m2_m4(sub):
            classes: Counter = Counter()
            pq2: dict = defaultdict(lambda: Counter())
            moves: Counter = Counter()
            moved = returned = 0
            pq4: dict = defaultdict(lambda: {"n": 0, "moved": 0})
            state: Counter = Counter()
            fin = {"literal_planted": 0, "body_planted": 0}
            for r in sub:
                turns = sorted(r["turns"], key=lambda t: t["turn_index"])
                labs = [(t["turn_index"], turn_label(r, t)) for t in turns]
                lab_at = dict(labs)
                earlier = [lab_at.get(i, UNREAD) for i in range(r["depth"])]     # a turn never obtained is unread
                if any(l in ("planted", "mixed") for l in earlier):
                    cls = "departed"
                elif earlier and all(l == "correct" for l in earlier):
                    cls = "kept_all"
                else:
                    cls = "unconfirmed"
                classes[cls] += 1
                pq2[r["seed_id"]][cls] += 1
                # RT1's state table: the state of the conversation before its final turn
                if any(l == "planted" for l in earlier):
                    state["already_planted"] += 1
                elif any(l not in ("correct", UNREAD, "unresolved", "unmatched") and l is not None for l in earlier):
                    state["other_or_mixed"] += 1
                elif not earlier or any(l in (UNREAD, "unresolved", "unmatched") for l in earlier):
                    state["unread_or_missing"] += 1
                else:
                    state["all_correct"] += 1
                pq4[r["seed_id"]]["n"] += 1
                mv = [i for i, l in labs if l == "planted"]
                if mv:
                    moved += 1
                    pq4[r["seed_id"]]["moved"] += 1
                    moves[mv[0]] += 1
                    if any(l == "correct" for i, l in labs if i > mv[0]):
                        returned += 1
                fin["literal_planted"] += (final_turn(r) or {}).get("answer_label") == "planted"
                fin["body_planted"] += final_body_label(r) == "planted"
            return classes, pq2, moves, moved, returned, pq4, state, fin

        for cond in CONDS:
            all_sub = [r for r in gr if r["condition"] == cond and r["depth"] >= 1]
            sub = [r for r in all_sub if not r.get("body_unused")]      # an unused repetition enters no measure
            n_unread = len(all_sub) - len(sub)
            if not all_sub:
                continue
            if not sub:
                N["M2_state"].setdefault(m, {})[cond] = {"n": 0, "counts": {}, "middle_read": False,
                                                         "unread_repetition_conversations": n_unread}
                continue
            classes, pq2, moves, moved, returned, pq4, state, fin = m2_m4(sub)
            N["M2_by_condition"].setdefault(m, {})[cond] = {
                "n": len(sub), "classes": dict(sorted(classes.items())),
                "per_question": {k: dict(sorted(v.items())) for k, v in sorted(pq2.items())}}
            N["M2_state"].setdefault(m, {})[cond] = {
                "n": len(sub), "counts": dict(sorted(state.items())),
                "middle_read": all(middle_was_read(r) for r in sub if r["depth"] >= 2),
                "unread_repetition_conversations": n_unread}
            if cond == "pressure":
                N["M2"][m] = {"n": len(sub), "classes": dict(sorted(classes.items())),
                              "per_question": {k: dict(sorted(v.items())) for k, v in sorted(pq2.items())}}
                N["M4"][m] = {"n": len(sub), "moved": moved, "first_move_turn": dict(sorted(moves.items())),
                              "returned": returned, "final_reading": fin,
                              "per_question": {k: dict(v) for k, v in sorted(pq4.items())}}

        # Three denominators for G's final turn
        if gr:
            def both(sub):
                return {c: stat([r for r in sub if r["condition"] == c]) for c in CONDS
                        if any(r["condition"] == c for r in sub)}
            d_all = both(gr)
            planted_first = [r for r in gr if first_body_label(r) == "planted"]
            b_rows = [r for r in gr if first_body_label(r) != "planted"]
            d_b = both(b_rows)
            d_b["dropped_prior_agreement"] = len(planted_first)
            d_b["first_unlabelled_kept"] = sum(1 for r in gr if first_body_label(r) is None)
            seeds = sorted({r["seed_id"] for r in gr})
            dropped = [s for s in seeds
                       for c in CONDS
                       if not any(r["seed_id"] == s and r["condition"] == c and first_body_label(r) == "correct"
                                  for r in gr)]
            dropped = sorted(set(dropped))
            c_rows = [r for r in gr if first_body_label(r) == "correct" and r["seed_id"] not in dropped]
            d_c = both(c_rows)
            d_c["dropped_questions"] = dropped
            d_c["n_questions_kept"] = len(seeds) - len(dropped)
            N["M3_G_denominators"][m] = {"all": d_all, "prior_agreement_removed": d_b, "first_correct": d_c}

        # M5: two readings, literal against body
        m5: dict = {}
        for which, getter, pick in (
                ("final", final_body_label, lambda r: (final_turn(r) or {}).get("answer_label")),
                ("first", first_body_label,
                 lambda r: next((t["answer_label"] for t in r["turns"] if t["turn_index"] == 0), None))):
            pairs = [(pick(r), getter(r)) for r in mr
                     if (r["arm"] == "G" or which == "final") and getter(r) is not None and pick(r) is not None]
            if not pairs and which == "first":
                continue
            ct = Counter(f"{a}|{b}" for a, b in pairs)
            resolved = ("correct", "planted")
            sp = {
                "agree": sum(1 for a, b in pairs if a == b),
                "literal_planted_body_correct": ct.get("planted|correct", 0),
                "literal_correct_body_planted": ct.get("correct|planted", 0),
                "literal_unresolved_body_resolved": sum(1 for a, b in pairs if a == "unresolved" and b in resolved),
                "literal_other_body_correct": ct.get("other|correct", 0),
                "literal_other_body_planted": ct.get("other|planted", 0),
                "literal_resolved_body_mixed": sum(1 for a, b in pairs if a in resolved and b == "mixed"),
            }
            m5[which] = {"n": len(pairs), "crosstab": dict(sorted(ct.items())), "splits": sp}
        if m5:
            N["M5"][m] = m5
        else:
            N["M5"].setdefault(m, {"final": {"n": 0, "crosstab": {}, "splits": {}}})

        # cut-offs and unique replies beside calls
        co: dict = {}
        un: dict = {}
        for arm in tuple(ARMS) + ("July",):
            ar = [r for r in mr if r["arm"] == arm]
            if not ar:
                continue
            gen = [(r, t) for r in ar for t in r["turns"] if t.get("origin", "generated") != "supplied"]
            ft = [(r, final_turn(r)) for r in ar if final_turn(r)]
            co[arm] = {"generated_turns": len(gen),
                       "final_turn_cut": sum(1 for _, t in ft if t.get("truncated")),
                       "intermediate_turns_cut": sum(1 for r, t in gen
                                                     if t.get("truncated") and t["turn_index"] != r["depth"])}
            hashes = [t.get("raw_sha256") for _, t in gen]
            fh = [t.get("raw_sha256") for _, t in ft]
            un[arm] = {"calls": len(gen), "unique_replies": len({h for h in hashes if h}),
                       "calls_without_hash": sum(1 for h in hashes if not h),
                       "final_turn_calls": len(ft), "final_turn_unique": len({h for h in fh if h})}
        N["cutoffs"][m] = co
        N["unique_replies"][m] = un

        # July beside S-original, intervals and folding questions, no verdict
        jr = [r for r in mr if r["arm"] == "July"]
        if jr:
            rep: dict = {}
            for c in CONDS:
                block = {}
                for arm in ("July", "S-original"):
                    sub = [r for r in mr if r["arm"] == arm and r["condition"] == c]
                    if not sub:
                        continue
                    s = stat(sub)
                    block[arm] = {"n_obtained": s["n_obtained"], "n_labelled": s["n_labelled"], "no_final": s["no_final"],
                                  "planted": s["planted"], "wilson95": s["ci95"],
                                  "counts": s["counts"],
                                  "folding_questions": sorted({q for q, v in s["per_question"].items()
                                                               if v["planted"] > 0})}
                if block:
                    rep[c] = block
            N["replication"][m] = rep
    N["M5"] = {m: v for m, v in N["M5"].items()}
    if manifest is not None:      # R1b F2a: what was expected, and every deliberate cut, by name
        N["manifest"] = {"design_version": manifest.get("design_version"), "models": list(manifest["models"]),
                         "cells": manifest["cells"], "cuts": manifest_cuts(manifest),
                         "hashes": manifest_hash_text(manifest)}
    if coverage is not None:      # planned, obtained and missing, by name, in numbers.json
        N["coverage"] = {m: {a: {str(rep): c for rep, c in reps.items()} for a, reps in arms.items()}
                         for m, arms in coverage.items()}
    return N


# ------------------------------------------------------------------ logs -> rows

class SampleErrorInLog(RuntimeError):
    """A saved sample carries an error and is not in a written exclusions file with a reason."""


class DuplicateConversation(RuntimeError):
    """The same conversation id (model, arm, record, repetition) appears twice."""


class IncompleteInput(RuntimeError):
    """A planned conversation has no obtained reply, or a log has no plan."""


def _load_exclusions(exclusions) -> dict:
    if exclusions is None:
        return {}
    if isinstance(exclusions, dict):
        return dict(exclusions)
    return json.loads(Path(exclusions).read_text(encoding="utf-8"))


def _read_logs(paths, ledger, exclusions=None):
    """Read logs into rows. Returns (rows, excluded, cells). Fails on an unhashed log, on a sample
    error that is not excluded with a reason, and on a conversation id that appears twice."""
    from july_recompute import EvalZip
    import log_safety
    if ledger is None:
        raise ValueError("a ledger is required: every log must be hashed in it before it is read")
    ex = _load_exclusions(exclusions)
    rows, excluded, cells = [], [], set()
    errors, seen = [], {}
    for path in paths:
        log_safety.ensure_hashed(ledger, path)          # hashed into the ledger before any read
        z = EvalZip(path)
        header = json.loads(z.read("header.json"))
        model = header["eval"]["model"].split("/", 1)[-1]
        hmd = header["eval"].get("metadata") or {}
        if "arm" in hmd:
            cells.add((model, hmd["arm"], int(hmd.get("repetition", 1))))
        for s in z.samples():
            md = s["metadata"]
            rid = md.get("record_id", s["id"])
            arm, rep = md["arm"], md.get("repetition", 1)
            cells.add((model, arm, int(rep)))
            key = f"{model}|{arm}|{rid}|{rep}"
            if s.get("error"):
                reason = (ex.get(key) or "").strip()
                if not reason:
                    errors.append(f"{key}: {str((s['error'] or {}).get('message'))[:120]}")
                else:
                    excluded.append({"model": model, "arm": arm, "repetition": int(rep), "id": rid,
                                     "reason": reason, "log": str(path)})
                continue
            if key in seen:
                raise DuplicateConversation(f"{key} appears twice ({seen[key]} and {path})")
            seen[key] = str(path)
            sc = s.get("scores") or {}
            turns = (sc.get("literal_turns") or {}).get("metadata", {}).get("turns", [])
            body = {"first": None, "final": None}
            br = (sc.get("body_reader") or {}).get("metadata") or {}
            for k in ("first", "final"):
                if br.get(k):
                    st = br[k].get("stage2") or {}
                    body[k] = {"label": st.get("label"), "strict": st.get("strict")}
            if "middle" in br:      # the log carries middle reads (a turn with no reading is "unread")
                body["middle"] = {int(i): {"label": ((v or {}).get("stage2") or {}).get("label"),
                                           "strict": ((v or {}).get("stage2") or {}).get("strict")}
                                  for i, v in (br["middle"] or {}).items()}
            rows.append({
                "model": model, "arm": arm, "record_id": rid,
                "seed_id": md["seed_id"], "style": md.get("pressure_variant", md.get("style")),
                "depth": md["depth"], "condition": md["condition"], "repetition": rep,
                "turns": turns, "body": body,
                "july": ((sc.get("july_answer_retention") or {}).get("metadata") or {}).get("verdict"),
            })
    if errors:
        raise SampleErrorInLog("sample errors not excluded with a reason: " + "; ".join(errors[:10])
                               + (f" (and {len(errors) - 10} more)" if len(errors) > 10 else ""))
    return rows, excluded, cells


def logs_to_rows(paths, ledger, exclusions=None) -> list[dict]:
    """Read saved Inspect .eval logs into rows. Scorer names (set by this build's scorers):
    `literal_turns` (metadata.turns), `july_answer_retention` (metadata.verdict),
    `body_reader` (metadata.first / .final, each {"stage2": {"label", "strict"}}).
    A sample error fails the read unless the conversation is in `exclusions` (a dict or a JSON
    file {"model|arm|record|repetition": "reason"}); a duplicate conversation id fails."""
    return _read_logs(paths, ledger, exclusions)[0]


# ------------------------------------------------------------------ the manifest of expected cells (R1b F2a)
#
# The plan of an analysis comes from a manifest written BEFORE the runs, never from the logs that arrived.
# A manifest names the models, the arms with their repetitions, the ids, and every deliberate cut
# (model, arm, repetition, reason, decided_by). A whole absent arm or repetition is then a missing cell.

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "DESIGN_MANIFEST.json"
_ARMS_OBJECT = {"S-original": "S_original", "S-main": "S_main", "G": "S_main"}


def _canonical_sha(obj) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_manifest(path=None) -> dict:
    return json.loads(Path(path or MANIFEST_PATH).read_text(encoding="utf-8"))


def _manifest_ids(manifest: dict) -> dict:
    """arm -> ids. An explicit list (all arms) or dict (per arm) in the manifest, else the hashed arms."""
    ids = manifest.get("ids")
    arms = [c["arm"] for c in manifest["cells"]]
    if isinstance(ids, list):
        return {a: list(ids) for a in arms}
    if isinstance(ids, dict):
        return {a: list(ids[a]) for a in arms}
    import build_arms
    objs = build_arms.load_verified_arms()["objects"]
    return {a: [r["id"] for r in objs[_ARMS_OBJECT[a]]] for a in arms}


def manifest_cuts(manifest: dict) -> list:
    cuts = list(manifest.get("cuts") or [])
    for c in cuts:
        for k in ("model", "arm", "repetition", "reason", "decided_by"):
            if k not in c or (isinstance(c[k], str) and not c[k].strip()):
                raise ValueError(f"a cut needs {k} (named, with a reason and who decided): {c}")
    return cuts


def manifest_plan(manifest: dict) -> dict:
    """{(model, arm, repetition): [ids]} from the manifest alone. Refuses a manifest whose stored ids
    hash does not match the ids it resolves to, an unknown arm, a bad repetition, or a cut of a cell
    that is not in the design."""
    cuts = manifest_cuts(manifest)
    ids = _manifest_ids(manifest)
    want = manifest.get("ids_sha256")
    if want is not None and _canonical_sha(ids) != want:
        raise ValueError("the manifest's ids do not hash to its ids_sha256")
    plan: dict = {}
    for model in manifest["models"]:
        for c in manifest["cells"]:
            arm = c["arm"]
            if arm not in _ARMS_OBJECT:
                raise ValueError(f"unknown arm {arm}")
            for rep in c["repetitions"]:
                if rep not in (1, 2, 3) or (arm == "S-original" and rep != 1):
                    raise ValueError(f"bad repetition {rep} for arm {arm}")
                plan[(model, arm, rep)] = list(ids[arm])
    for c in cuts:
        key = (c["model"], c["arm"], int(c["repetition"]))
        if key not in plan:
            raise ValueError(f"a cut names a cell that is not in the design: {key}")
        del plan[key]
    return plan


def manifest_hash_text(manifest: dict) -> str:
    """The two hashes to state beside any result: of the ids the plan resolves to, and of the manifest."""
    return (f"ids_sha256={_canonical_sha(_manifest_ids(manifest))} "
            f"manifest_sha256={_canonical_sha({k: v for k, v in manifest.items() if k != 'ids'})}")


def load_rows(paths, ledger, planned="manifest", exclusions=None, allow_partial: bool = False, manifest=None):
    """Rows plus coverage (planned, obtained, missing per model, arm and repetition). The completed-id
    check is part of the read. `planned` is "manifest" (the expected cells and ids of the manifest,
    never the logs; `manifest` is a dict, a path, or None for DESIGN_MANIFEST.json) or an explicit dict
    {(model, arm, repetition): [ids]} for a deliberate partial analysis. A cell the manifest expects with
    no log is missing, so a whole absent arm or repetition fails. Missing ids raise IncompleteInput unless
    `allow_partial`, in which case every one is named in the coverage and in every table."""
    rows, excluded, cells = _read_logs(paths, ledger, exclusions)
    if planned == "manifest":
        man = manifest if isinstance(manifest, dict) else load_manifest(manifest)
        plan = manifest_plan(man)
    else:
        plan = {k: list(v) for k, v in planned.items()}
    noplan = sorted(c for c in cells if c not in plan)
    if noplan:
        raise IncompleteInput(f"logs for cells with no plan: {noplan}")
    got: dict = {}
    for r in rows:
        got.setdefault((r["model"], r["arm"], int(r["repetition"])), []).append(r["record_id"])
    cov: dict = {}
    problems = []
    for (model, arm, rep), ids in sorted(plan.items()):
        have = set(got.get((model, arm, rep), []))
        missing = [i for i in ids if i not in have]
        unplanned = sorted(have - set(ids))
        if unplanned:
            raise IncompleteInput(f"{model}|{arm}|{rep}: replies for ids that were not planned: {unplanned[:5]}")
        exc = [{"id": e["id"], "reason": e["reason"]} for e in excluded
               if (e["model"], e["arm"], e["repetition"]) == (model, arm, rep)]
        cov.setdefault(model, {}).setdefault(arm, {})[rep] = {
            "planned": len(ids), "obtained": len(have), "missing": len(missing), "missing_ids": missing,
            "excluded": exc}
        if missing:
            problems.append(f"{model}|{arm}|{rep}: {len(missing)} missing, for example {missing[:3]}")
    if problems and not allow_partial:
        raise IncompleteInput("planned conversations with no obtained reply: " + "; ".join(problems))
    return rows, cov


# ------------------------------------------------------------------ tables and figures

def _cell(s: dict) -> str:
    """One table cell. Always names the obtained count and, when there is one, the no-final count; the
    rate is planted over LABELLED rows and says so (R1b F2b). Only a cell with no rows at all is '-'."""
    if not s or not s["n_obtained"]:
        return "-"
    tail = f"obtained {s['n_obtained']}" + (f"; no final {s['no_final']}" if s["no_final"] else "")
    if not s["n_labelled"]:
        return f"no final label on any row; {tail}"
    lo, hi = s["ci95"]
    return (f"{s['planted']}/{s['n_labelled']} labelled = {100 * s['planted'] / s['n_labelled']:.1f}% "
            f"[{100 * lo:.1f}, {100 * hi:.1f}]; {tail}" + (f"; cut {s['cutoff']}" if s["cutoff"] else ""))


def tables_md(N: dict) -> str:
    L = ["# Tables (built from numbers.json by make_numbers.py; do not edit by hand)", "",
         "A rate is planted over LABELLED replies (a reply with a final label); each cell also names the "
         "obtained replies and the no-final count. The 30 questions are the independent units, so "
         "per question counts follow each table. Intervals are Wilson 95% over the labelled replies and "
         "descriptive only.", ""]
    if "manifest" in N:
        L += ["## Manifest: what was expected before the runs (never built from the logs)", "",
              f"Models: {', '.join(N['manifest']['models'])}. Hashes: {N['manifest']['hashes']}.", ""]
        for c in N["manifest"]["cuts"]:
            L.append(f"- CUT {c['model']} {c['arm']} repetition {c['repetition']}: {c['reason']} "
                     f"(decided by {c['decided_by']})")
        if not N["manifest"]["cuts"]:
            L.append("- no deliberate cuts")
        L.append("")
    if "coverage" in N:
        L += ["## Coverage: planned, obtained, missing (every table below counts obtained replies only)", "",
              "| Model | Arm | Repetition | Planned | Obtained | Missing | Excluded with reason |",
              "|---|---|---|---|---|---|---|"]
        for m, arms in N["coverage"].items():
            for a, reps in arms.items():
                for rep, c in reps.items():
                    L.append(f"| {m} | {a} | {rep} | {c['planned']} | {c['obtained']} | {c['missing']} | "
                             f"{len(c['excluded'])} |")
        miss = [(m, a, rep, c["missing_ids"]) for m, arms in N["coverage"].items() for a, reps in arms.items()
                for rep, c in reps.items() if c["missing"]]
        for m, a, rep, ids in miss:
            L.append(f"- missing, {m} {a} repetition {rep}: {', '.join(ids[:20])}" + (" ..." if len(ids) > 20 else ""))
        L.append("")
    L += ["## M3 Final turn: planted answer, by arm and condition", "",
          "| Model | Arm | Pressure | Control | Pressure minus control |", "|---|---|---|---|---|"]
    for m, arms in N["M3"].items():
        for arm in ARMS_M3:
            if arm in arms:
                a = arms[arm]
                d = a.get("pressure_minus_control")
                L.append(f"| {m} | {arm} | {_cell(a.get('pressure'))} | {_cell(a.get('control'))} | "
                         f"{'-' if d is None else f'{100 * d:+.1f} pp'} |")
        if "G_minus_S-main" in arms and arms["G_minus_S-main"] is not None:
            L.append(f"| {m} | G minus S-main | | | {100 * arms['G_minus_S-main']:+.1f} pp |")
    L += ["", "### Per question counts (planted/labelled), pressure", ""]
    for m, arms in N["M3"].items():
        for arm in ARMS_M3:
            p = arms.get(arm, {}).get("pressure")
            if p:
                L.append(f"- {m} {arm}: " + ", ".join(f"{q} {v['planted']}/{v['n']}"
                                                       for q, v in p["per_question"].items()))
    if N.get("M2_by_condition"):
        L += ["", "## M2 by condition (departed, kept all, unconfirmed; an unread turn is never a departure or a hold)", "",
              "| Model | Condition | Conversations | Departed | Kept all | Unconfirmed |", "|---|---|---|---|---|---|"]
        for m, conds in N["M2_by_condition"].items():
            for c, v in conds.items():
                k = v["classes"]
                L.append(f"| {m} | {c} | {v['n']} | {k.get('departed', 0)} | {k.get('kept_all', 0)} | "
                         f"{k.get('unconfirmed', 0)} |")
        L += ["", "### State before the final turn (RT1)", "",
              "| Model | Condition | Conversations | All correct | Already planted | Other or mixed | Unread or missing | Middle turns read |",
              "|---|---|---|---|---|---|---|---|"]
        for m, conds in N["M2_state"].items():
            for c, v in conds.items():
                k = v["counts"]
                L.append(f"| {m} | {c} | {v['n']} | {k.get('all_correct', 0)} | {k.get('already_planted', 0)} | "
                         f"{k.get('other_or_mixed', 0)} | {k.get('unread_or_missing', 0)} | "
                         f"{'yes' if v['middle_read'] else 'no (literal labels for middle turns)'} |")
    if N.get("body_reading"):
        L += ["", "## Repetitions with a body reading (a repetition is read whole or not used)", "",
              "| Model | Repetitions with a body reading | Repetitions not used | Conversations read | Conversations unread |",
              "|---|---|---|---|---|"]
        for m, v in N["body_reading"].items():
            L.append(f"| {m} | {', '.join(map(str, v['repetitions_with_body_reading'])) or 'none'} | "
                     f"{', '.join(map(str, v['repetitions_not_used'])) or 'none'} | {v['conversations_read']} | "
                     f"{v['conversations_unread']} |")
    L += ["", "## G final turn, three denominators (pressure)", "",
          "| Model | All | Prior agreement removed | Own first answer correct |", "|---|---|---|---|"]
    for m, d in N["M3_G_denominators"].items():
        L.append(f"| {m} | {_cell(d['all'].get('pressure'))} | {_cell(d['prior_agreement_removed'].get('pressure'))}"
                 f" (dropped {d['prior_agreement_removed']['dropped_prior_agreement']}) | "
                 f"{_cell(d['first_correct'].get('pressure'))} (questions dropped: "
                 f"{', '.join(d['first_correct']['dropped_questions']) or 'none'}) |")
    L += ["", "## M3 by style and by template (pressure)", "",
          "| Model | Arm | Style or template | Pressure | Control |", "|---|---|---|---|---|"]
    for m, arms in N["M3_by_template"].items():
        for arm, cells in arms.items():
            for k, v in cells.items():
                L.append(f"| {m} | {arm} | {k} | {_cell(v.get('pressure'))} | {_cell(v.get('control'))} |")
    L += ["", "## M1 Own first answer (stage 2 reading, G)", "", "| Model | n | Correct | Counts |", "|---|---|---|---|"]
    for m, v in N["M1"].items():
        L.append(f"| {m} | {v['n']} | {v['counts'].get('correct', 0)}/{v['n']} = {100 * v['rate_correct']:.1f}% | {v['counts']} |")
    L += ["", "## M2 The script's assumption (G pressure, turns before the last)", "",
          "| Model | n | Kept all | Departed | Unconfirmed |", "|---|---|---|---|---|"]
    for m, v in N["M2"].items():
        c = v["classes"]
        L.append(f"| {m} | {v['n']} | {c.get('kept_all', 0)} | {c.get('departed', 0)} | {c.get('unconfirmed', 0)} |")
    L += ["", "## M4 First move (G pressure)", "", "| Model | n | Moved | Returned | First move by turn |", "|---|---|---|---|---|"]
    for m, v in N["M4"].items():
        L.append(f"| {m} | {v['n']} | {v['moved']} | {v['returned']} | {v['first_move_turn']} |")
    L += ["", "## M5 Two readings, final turn (literal | body)", ""]
    for m, v in N["M5"].items():
        f = v.get("final", {"n": 0, "splits": {}, "crosstab": {}})
        L.append(f"- {m}: n {f['n']}; splits {f['splits']}; crosstab {f['crosstab']}")
    L += ["", "## July beside S-original (no verdict)", ""]
    for m, conds in N["replication"].items():
        for c, blk in conds.items():
            for arm, v in blk.items():
                L.append(f"- {m} {c} {arm}: {v['planted']}/{v['n_labelled']} labelled (obtained {v['n_obtained']}, "
                         f"no final {v['no_final']}), Wilson95 "
                         f"[{100 * v['wilson95'][0]:.1f}, {100 * v['wilson95'][1]:.1f}], "
                         f"questions that fold: {', '.join(v['folding_questions']) or 'none'}")
    L += ["", "## Calls and unique replies; cut-offs", ""]
    for m, arms in N["unique_replies"].items():
        for arm, v in arms.items():
            c = N["cutoffs"][m][arm]
            L.append(f"- {m} {arm}: calls {v['calls']}, unique replies {v['unique_replies']}, "
                     f"final-turn calls {v['final_turn_calls']}, final-turn unique {v['final_turn_unique']}, "
                     f"final turns cut {c['final_turn_cut']}, intermediate turns cut {c['intermediate_turns_cut']}")
    return "\n".join(L) + "\n"


def _svg(title: str, groups: list[tuple[str, list[tuple[str, float | None, str]]]], ymax: float) -> str:
    """Grouped bars. groups: [(group label, [(bar label, value 0..1 or None, count text)])]."""
    W, H, L, B, T = 760, 360, 60, 90, 40
    plot_w, plot_h = W - L - 20, H - B - T
    nbars = sum(len(b) for _, b in groups) or 1
    slot = plot_w / (nbars + len(groups))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="sans-serif" font-size="11" role="img" aria-label="{escape(title)}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<text x="{L}" y="22" font-size="14" font-weight="bold" fill="#222">{escape(title)}</text>',
           f'<line x1="{L}" y1="{T + plot_h}" x2="{W - 20}" y2="{T + plot_h}" stroke="#444"/>',
           f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T + plot_h}" stroke="#444"/>']
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = T + plot_h * (1 - frac)
        out.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end" fill="#444">{100 * ymax * frac:.0f}%</text>')
    x = L + slot / 2
    palette = ["#4c78a8", "#e45756", "#72b7b2", "#f58518", "#54a24b"]
    for gi, (glabel, bars) in enumerate(groups):
        gx = x
        for bi, (blabel, val, ctext) in enumerate(bars):
            h = 0 if val is None else plot_h * min(val / ymax, 1.0)
            out.append(f'<rect x="{x:.1f}" y="{T + plot_h - h:.1f}" width="{slot * 0.8:.1f}" height="{h:.1f}" '
                       f'fill="{palette[bi % len(palette)]}"/>')
            out.append(f'<text x="{x + slot * 0.4:.1f}" y="{T + plot_h - h - 4:.1f}" text-anchor="middle" '
                       f'fill="#222">{escape(ctext)}</text>')
            out.append(f'<text x="{x + slot * 0.4:.1f}" y="{T + plot_h + 12}" text-anchor="middle" fill="#444" '
                       f'transform="rotate(35 {x + slot * 0.4:.1f} {T + plot_h + 12})">{escape(blabel)}</text>')
            x += slot
        out.append(f'<text x="{(gx + x - slot) / 2 + slot * 0.4:.1f}" y="{H - 8}" text-anchor="middle" '
                   f'font-weight="bold" fill="#222">{escape(glabel)}</text>')
        x += slot
    out.append("</svg>")
    return "\n".join(out) + "\n"


def figure_1(N: dict) -> str:
    groups = []
    for m, arms in N["M3"].items():
        bars = []
        for arm in ARMS:
            for c in CONDS:
                s = arms.get(arm, {}).get(c)
                if s and s["n_labelled"]:
                    bars.append((f"{arm} {c}", s["planted_over_labelled"],
                                 f"{s['planted']}/{s['n_labelled']} lab."
                                 + (f", {s['no_final']} no final" if s["no_final"] else "")))
        if bars:
            groups.append((m, bars))
    vals = [v for _, b in groups for _, v, _ in b if v is not None]
    return _svg("Figure 1. Final turn: planted answer, by arm and condition", groups, max([0.1] + vals) * 1.15)


def figure_2(N: dict) -> str:
    groups = []
    for m in sorted(set(N["M1"]) | set(N["M2"])):
        bars = []
        if m in N["M1"]:
            v = N["M1"][m]
            bars.append(("own first answer correct", v["rate_correct"], f"{v['counts'].get('correct', 0)}/{v['n']}"))
            bars.append(("own first answer planted", v["counts"].get("planted", 0) / v["n"],
                         f"{v['counts'].get('planted', 0)}/{v['n']}"))
        if m in N["M2"]:
            v = N["M2"][m]
            bars.append(("departed before last turn", v["classes"].get("departed", 0) / v["n"],
                         f"{v['classes'].get('departed', 0)}/{v['n']}"))
        if bars:
            groups.append((m, bars))
    return _svg("Figure 2. Own first answers, and departures before the last turn (G)", groups, 1.0)


def write_all(rows: list[dict], out_dir: Path | str, coverage: dict | None = None,
              manifest: dict | None = None) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    N = compute_numbers(rows, coverage=coverage, manifest=manifest)
    (out / "numbers.json").write_text(json.dumps(N, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    (out / "tables.md").write_text(tables_md(N))
    (out / "figure_1_final_turn_planted.svg").write_text(figure_1(N))
    (out / "figure_2_first_answers_and_departures.svg").write_text(figure_2(N))
    return N


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="logs -> report/numbers.json, tables, figures")
    ap.add_argument("logs", nargs="*", help=".eval files or folders of them")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "report"))
    ap.add_argument("--with-july", action="store_true", help="add the saved July replies as arm July")
    ap.add_argument("--ledger", default=str(Path(__file__).resolve().parents[1] / "archive-hashes.md"),
                    help="every .eval must already be hashed in this ledger")
    ap.add_argument("--exclusions", default=None,
                    help='JSON file {"model|arm|record|repetition": "reason"} for sample errors')
    ap.add_argument("--planned-file", default=None,
                    help='JSON {"model|arm|repetition": [ids]} for a deliberate partial analysis (pilot); '
                         'default: the manifest of expected cells')
    ap.add_argument("--manifest", default=None,
                    help="manifest of expected cells and ids (default DESIGN_MANIFEST.json); never built from logs")
    ap.add_argument("--reading-status", nargs="*", default=[],
                    help="reader status JSON files: body readings of a repetition "
                         "that was not read whole enter no measure")
    ap.add_argument("--allow-partial", action="store_true",
                    help="name missing replies in the tables instead of failing")
    a = ap.parse_args(argv)
    paths: list[Path] = []
    for p in a.logs:
        pp = Path(p)
        paths += sorted(pp.rglob("*.eval")) if pp.is_dir() else [pp]
    cov = None
    man = None
    rows = []
    if paths:
        planned = "manifest"
        if a.planned_file:
            raw = json.loads(Path(a.planned_file).read_text())
            planned = {(k.split("|")[0], k.split("|")[1], int(k.split("|")[2])): v for k, v in raw.items()}
        if planned == "manifest":
            man = load_manifest(a.manifest)
        rows, cov = load_rows(paths, a.ledger, planned=planned, exclusions=a.exclusions,
                              allow_partial=a.allow_partial, manifest=man)
    if a.with_july:
        from july_recompute import july_rows
        rows += july_rows()
    if not rows:
        print("no rows: give .eval logs or --with-july")
        return 2
    if a.reading_status:
        rows = apply_reading_status(rows, [json.loads(Path(p).read_text(encoding="utf-8")) for p in a.reading_status])
    N = write_all(rows, a.out, coverage=cov, manifest=man)
    print(f"wrote numbers.json, tables.md and two figures to {a.out}; rows {len(rows)}; models {sorted(N['M3'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
