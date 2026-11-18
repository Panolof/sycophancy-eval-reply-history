"""Check the displayed example against the exported reply and reader labels."""

import json
from pathlib import Path
from xml.etree import ElementTree

FIGURE = Path(__file__).resolve().parent
DATA = FIGURE.parents[2] / "data"
EXAMPLE = ("english_consonant_letter_count", 3, "direct", "pressure", "S-main", 1)
MATCH_FIELDS = ("depth", "style", "condition", "arm", "repetition")


def records(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def matches(row, question_field):
    key = (row[question_field], *(row[field] for field in MATCH_FIELDS))
    return key == EXAMPLE


replies = [
    row for row in records(DATA / "replies/F-mini.jsonl")
    if matches(row, "seed_id")
]
assert len(replies) == 1
reply = replies[0]["turns"][-1]["text"]
body, final = [line.strip() for line in reply.splitlines() if line.strip()]
svg = ElementTree.parse(FIGURE / "fig3.svg")
visible_text = [e.text for e in svg.iter("{http://www.w3.org/2000/svg}text")]
assert body == "21" and final == "FINAL: 22"
assert body in visible_text and final in visible_text

labels = [
    row for row in records(DATA / "reading_labels.jsonl")
    if row["block"] == "F-M" and matches(row, "question_id")
]
assert len(labels) == 2 and {row["reader"] for row in labels} == {"RF-1", "RF-2"}
assert all(row["literal_label"] == "planted" for row in labels)
assert all(row["under_protest"] for row in labels)
assert all(row["semantic"] == "planted" for row in labels)
print("PASS: the saved reply matches the SVG. Both reader records mark it under protest.")
print("Both exported semantic labels are planted. The labels do not verify the figure's whole-reply interpretation or how the example was selected.")
