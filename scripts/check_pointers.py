"""Verify the public path and JSON field targets in the submitted-report ledger."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "report/evidence/pointers.json"
EXPECTED_LINES = (
    65, 93, 103, 173, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190,
    248, 295, 296, 297, 298, 299, 620,
)


def as_markdown(row):
    links = []
    for target in row["targets"]:
        path = target["path"]
        fields = ["`" + address.replace("|", r"\|") + "`" for address in target["fields"]]
        links.append(" ".join([f"[{path}]({path})", *fields]))
    destinations = "; ".join(links) or "**NOT IN THIS RELEASE**"
    return f"| {row['line']} | {row['pointer']} | {destinations} | {row['note']} |"


def verify(root=ROOT):
    rows = json.loads(LEDGER.read_text())
    if tuple(row["line"] for row in rows) != EXPECTED_LINES:
        raise ValueError("Report line coverage differs from the 21 audited pointers")
    actual = [
        line for line in (ROOT / "POINTERS.md").read_text().splitlines()
        if re.match(r"^\| \d+ \|", line)
    ]
    if actual != [as_markdown(row) for row in rows]:
        raise ValueError("POINTERS.md and the machine ledger differ")
    checked = 0
    for row in rows:
        if not row["targets"] and "NOT IN THIS RELEASE" not in row["note"]:
            raise ValueError(f"Report line {row['line']} has neither targets nor an omission reason")
        for target in row["targets"]:
            relative = Path(target["path"])
            path = root / relative
            if relative.is_absolute() or ".." in relative.parts or not path.is_file():
                raise ValueError(f"Missing or invalid target at report line {row['line']}: {relative}")
            fields = target["fields"]
            if fields:
                document = json.loads(path.read_text())
                for field in fields:
                    if not field.startswith("/"):
                        raise ValueError(f"Invalid JSON pointer at line {row['line']}: {field}")
                    value = document
                    for key in field[1:].split("/"):
                        key = key.replace("~1", "/").replace("~0", "~")
                        if not isinstance(value, dict) or key not in value:
                            raise ValueError(f"Missing field at report line {row['line']}: {relative} {field}")
                        value = value[key]
                    checked += 1
            else:
                checked += 1
    print(f"PASS: {len(rows)} report pointers, {checked} packaged file or field targets")


if __name__ == "__main__":
    verify()
