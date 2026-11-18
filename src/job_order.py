"""The dispatch order. Waves by repetition (repetition 1 of all arms, then 2,
then 3). Inside a wave, DESIGN's order: SHA256 of UTF-8 `run2-v3|arm|model|record_id|repetition`,
the full tuple breaking ties; arms interleave because the hash ignores arm grouping.

One job is one conversation. A G job is d+1 sequential calls. No call is made here.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HOME = Path(__file__).resolve().parents[1]


def _arms(path=None) -> dict:
    import build_arms
    v = build_arms.load_verified_arms(path)          # hashes checked; schedules from the hashed object
    return {"objects": v["objects"], "schedules": v["schedules"]}


def jobs_for(model: str, arms: dict | None = None) -> list[dict]:
    arms = arms or _arms()
    depth = {r["id"]: r["depth"] for r in arms["objects"]["S_original"]}
    raw = []
    for r in arms["objects"]["S_original"]:
        raw.append(("S-original", r["id"], 1, 1))
    for r in arms["objects"]["S_main"]:
        for rep in (1, 2, 3):
            raw.append(("S-main", r["id"], rep, 1))
    for g in arms["schedules"]:
        for rep in (1, 2, 3):
            raw.append(("G", g["id"], rep, depth[g["id"]] + 1))
    jobs = []
    for arm, rid, rep, calls in raw:
        h = hashlib.sha256(f"run2-v3|{arm}|{model}|{rid}|{rep}".encode("utf-8")).hexdigest()
        jobs.append({"arm": arm, "model": model, "record_id": rid, "repetition": rep,
                     "calls": calls, "sort_hash": h})
    jobs.sort(key=lambda j: (j["repetition"], j["sort_hash"], j["arm"], j["model"], j["record_id"]))
    return jobs


def wave_summary(jobs: list[dict]) -> list[dict]:
    out = []
    for wave in sorted({j["repetition"] for j in jobs}):
        w = [j for j in jobs if j["repetition"] == wave]
        out.append({"wave": wave, "conversations": len(w), "calls": sum(j["calls"] for j in w),
                    "by_arm": {a: sum(1 for j in w if j["arm"] == a) for a in ("S-original", "S-main", "G")}})
    return out


if __name__ == "__main__":
    for m in ("claude-haiku-4-5-20251001", "gpt-5-mini-2025-08-07"):
        print(m, json.dumps(wave_summary(jobs_for(m))))
