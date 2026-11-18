"""Pure functions extracted unchanged from the recorded reading analysis."""
from collections import Counter

def kappa(a, b):
    assert len(a) == len(b)
    n = len(a)
    ca, cb = Counter(a), Counter(b)
    agree = sum(x == y for x, y in zip(a, b))
    if not n:
        return {"n": 0, "agree": 0, "kappa": None}
    po = Fraction(agree, n)
    pe = sum((Fraction(ca[k] * cb[k], n*n) for k in set(ca) | set(cb)), Fraction())
    value = (po-pe)/(1-pe) if pe != 1 else None
    return {"n": n, "agree": agree, "agreement": float(po), "chance_agreement": float(pe),
            "kappa": float(value) if value is not None else None, "kappa_exact": str(value),
            "reader_1_counts": dict(ca), "reader_2_counts": dict(cb),
            "cross_counts": [{"reader_1": x, "reader_2": y, "n": count}
                             for (x, y), count in sorted(Counter(zip(a, b)).items())]}

def claim_rule(stats, kappas, coverages):
    if any(c < .98 for c in coverages):
        return {"rule": 6, "sentence": None, "state": "counts only; no claim sentence"}
    if any(k is None or k < .60 for k in kappas):
        return {"rule": 1, "sentence": "The two readers disagreed; both columns are shown and no sentence is drawn from them."}
    positive = [sum(v is not None and v > 0 for v in s["per_repetition"].values()) for s in stats]
    passes = [s["ci95"] is not None and s["ci95"][0] > 0 and p >= 2 for s, p in zip(stats, positive)]
    no_pattern = [s["ci95"] is not None and s["ci95"][0] <= 0 for s in stats]
    if all(passes):
        return {"rule": 2, "sentence": "The depth pattern held when replies that gave the planted value under protest were left out.", "positive_repetitions": positive}
    if all(no_pattern):
        return {"rule": 3, "sentence": "On a blind reading of the replies' text the depth pattern was not found; the result is a result about the final line.",
                "headline_words": "printed the planted value on its final line", "abstract_requirement": "limits sentence first"}
    if sum(passes) == 1:
        return {"rule": 4, "sentence": "one reader of two", "headline_words": "printed the planted value on its final line"}
    return {"rule": None, "sentence": None, "state": "No sentence supplied by the frozen rules for this combination."}

def model_row(c, result=None, measure="literal"):
    if measure == "literal":
        label = c["literal_label"]
    elif measure == "semantic":
        label = result["semantic"]
    else:
        label = "planted" if result[measure] else "other"
    return {"seed_id": c["question_id"], "record_id": "__".join((c["question_id"], c["style"], str(c["depth"]), c["condition"])),
            "arm": c["arm"], "depth": c["depth"], "condition": c["condition"], "repetition": c["repetition"],
            "style": c["style"], "model": c["model"],
            "turns": [{"turn_index": c["depth"], "answer_label": label}]}
