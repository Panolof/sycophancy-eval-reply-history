#!/usr/bin/env python3
"""Build the deterministic v2 depth x pressure matrix from versioned sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEEDS_PATH = ROOT / "data" / "seeds_v2.json"
TEMPLATES_PATH = ROOT / "data" / "pressure_templates_v2.json"
OUTPUT_PATHS = (
    ROOT / "data" / "matrix_v2.json",
    ROOT / "src" / "inspect_sycophancy_eval" / "resources" / "matrix_v2.json",
)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _messages(
    seed: dict[str, Any],
    templates: dict[str, Any],
    variant: dict[str, Any],
    condition: str,
    depth: int,
) -> list[dict[str, str]]:
    values = {
        "correct_answer": seed["correct_answer"],
        "incorrect_suggestion": seed["incorrect_suggestion"],
    }
    messages = [
        {"role": "user", "content": seed["question"]},
        {
            "role": "assistant",
            "content": templates["initial_answer"].format(**values),
        },
    ]
    turn_key = "pressure_turns" if condition == "pressure" else "control_turns"
    for turn_index in range(depth):
        user_content = variant[turn_key][turn_index].format(**values)
        if turn_index == depth - 1:
            user_content += "\n\n" + templates["final_answer_contract"]
        messages.append(
            {
                "role": "user",
                "content": user_content,
            }
        )
        if turn_index < depth - 1:
            messages.append(
                {
                    "role": "assistant",
                    "content": templates["seeded_bridges"][turn_index],
                }
            )
    return messages


def build_matrix(
    seeds: list[dict[str, Any]], templates: dict[str, Any]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    version = templates["dataset_version"]
    for seed in seeds:
        for variant in templates["variants"]:
            for depth in templates["depth_conditions"]:
                pair_id = f"{seed['id']}__{variant['id']}__d{depth}"
                for condition in ("control", "pressure"):
                    records.append(
                        {
                            "id": f"{pair_id}__{condition}",
                            "pair_id": pair_id,
                            "seed_id": seed["id"],
                            "category": seed["category"],
                            "condition": condition,
                            "pressure_variant": variant["id"],
                            "pressure_strength": variant["strength"],
                            "depth": depth,
                            "question": seed["question"],
                            "correct_answer": seed["correct_answer"],
                            "incorrect_suggestion": seed["incorrect_suggestion"],
                            "correct_aliases": seed.get("correct_aliases", []),
                            "incorrect_aliases": seed.get("incorrect_aliases", []),
                            "messages": _messages(
                                seed, templates, variant, condition, depth
                            ),
                            "dataset_version": version,
                        }
                    )
    return records


def _render(records: list[dict[str, Any]]) -> bytes:
    return (json.dumps(records, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if either committed matrix differs from deterministic output",
    )
    args = parser.parse_args()

    seeds = _read_json(SEEDS_PATH)
    templates = _read_json(TEMPLATES_PATH)
    rendered = _render(build_matrix(seeds, templates))

    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path in OUTPUT_PATHS
            if not path.exists() or path.read_bytes() != rendered
        ]
        if mismatches:
            raise SystemExit("matrix mismatch: " + ", ".join(mismatches))
        print(f"matrix_v2 deterministic: {len(json.loads(rendered))} samples")
        return

    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(rendered)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
