"""Two small counts for Section 4.6 that no table file states. Stdlib only. Run from HOME.
For Claude Haiku 4.5 (block F-H), included questions, pressure conversations: on how many questions does each arm
hold at least one planted final, and how many planted finals in total (both depths, both styles)?
Reads results/f-haiku/f_numbers.json, keys models.claude-haiku-4-5-20251001.per_question, .included."""
import json, sys
sys.dont_write_bytecode = True
fh = json.load(open("results/f-haiku/f_numbers.json"))["models"]["claude-haiku-4-5-20251001"]
for arm in ("S-main", "G"):
    per = {q: sum(c["planted"] for d in fh["per_question"][q][arm]["pressure"].values() for c in d.values()) for q in fh["included"]}
    print(arm, "questions with a planted final:", sum(1 for v in per.values() if v), "of", len(per), "; planted finals in total:", sum(per.values()))
