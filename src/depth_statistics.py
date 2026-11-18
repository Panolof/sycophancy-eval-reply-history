"""Original first-run depth functions; log access omitted."""
from collections import Counter, defaultdict
import make_numbers as mn
RESAMPLES=10000

def pct(x):
    return None if x is None else round(100 * x, 2)

def pressure(rows, arm):
    return [r for r in rows if r["arm"] == arm and r["condition"] == "pressure"]

def per_q(rows):
    """question -> [planted, n] over labelled rows (same labels as make_numbers.stat)."""
    d = defaultdict(lambda: [0, 0])
    for r in rows:
        lab = mn.final_label(r)
        if lab is None:
            continue
        d[r["seed_id"]][1] += 1
        d[r["seed_id"]][0] += lab == "planted"
    return dict(sorted(d.items()))

def bootstrap(qs, pq_g, pq_s, rng):
    """Resample the questions with replacement (the same draw for both arms). Statistic: pooled rate G minus pooled rate S-main."""
    diffs = []
    k = len(qs)
    for _ in range(RESAMPLES):
        pick = [qs[rng.randrange(k)] for _ in range(k)]
        gp = sum(pq_g[q][0] for q in pick)
        gn = sum(pq_g[q][1] for q in pick)
        sp = sum(pq_s[q][0] for q in pick)
        sn = sum(pq_s[q][1] for q in pick)
        diffs.append(gp / gn - sp / sn)
    diffs.sort()
    lo = diffs[int(0.025 * RESAMPLES)]
    hi = diffs[int(0.975 * RESAMPLES) - 1]
    return lo, hi

def top_share(pq, k=5):
    tot = sum(v[0] for v in pq.values())
    ranked = sorted(pq.items(), key=lambda kv: (-kv[1][0], kv[0]))
    return {"total_planted": tot,
            "questions_with_any": sum(1 for v in pq.values() if v[0] > 0),
            "top": [{"question": q, "planted": v[0], "n": v[1], "share_of_total": round(v[0] / tot, 3) if tot else None}
                    for q, v in ranked[:k] if v[0] > 0],
            "top2_share": round(sum(v[0] for _, v in ranked[:2]) / tot, 3) if tot else None,
            "top3_share": round(sum(v[0] for _, v in ranked[:3]) / tot, 3) if tot else None}

def cover_set(pq, frac=0.5):
    """Smallest set of top questions whose planted answers cover at least `frac` of the arm's total."""
    tot = sum(v[0] for v in pq.values())
    out, acc = [], 0
    for q, v in sorted(pq.items(), key=lambda kv: (-kv[1][0], kv[0])):
        if v[0] == 0 or acc >= frac * tot:
            break
        out.append(q)
        acc += v[0]
    return out

def style_template(rows, arm, qs):
    """For the questions qs: planted/labelled by style and by style/depth template, pressure."""
    by_style: dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    by_tpl: dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in pressure(rows, arm):
        if r["seed_id"] not in qs:
            continue
        lab = mn.final_label(r)
        if lab is None:
            continue
        for d, k in ((by_style, r["style"]), (by_tpl, f"{r['style']}/{r['depth']}")):
            d[r["seed_id"]][k][1] += 1
            d[r["seed_id"]][k][0] += lab == "planted"
    fmt = lambda d: {q: {k: v for k, v in sorted(m.items())} for q, m in sorted(d.items())}
    return {"by_style": fmt(by_style), "by_template": fmt(by_tpl)}
