"""X7 predictions Q2 and Q4 (PREREGISTRATION.md, X7); Q1 and Q3 come from the post-run checks.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x7_predictions.py
"""
import glob, json, math, collections
import numpy as np
from soup.stream.searcher import BLOOM_BITS

hs = [json.load(open(f)) for f in glob.glob('/data/x7/logs/workers/s*.json')]
raw = sum(h.get('evals') or 0 for h in hs)
bl = [np.load(f) for f in glob.glob('/data/x7/runs/x7/bloom_*.npy')]
U = np.bitwise_or.reduce(bl)
fill = int(np.bitwise_count(U).sum(dtype=np.int64))
distinct = -BLOOM_BITS * math.log(1 - fill / BLOOM_BITS)
print(f'searchers {len(hs)}, bitmaps {len(bl)}; raw evaluations {raw:,}; distinct (union, linear counting) {distinct:,.0f} '
      f'= {100 * distinct / raw:.1f}% -> Q2 {"holds" if distinct >= 0.8 * raw else "fails"} (>= 80%)')
for k in ('known_skipped', 'cand_skipped', 'seen_skipped', 'lat_skipped', 'ign_skipped'):
    print(f'  {k}: {sum(h.get(k) or 0 for h in hs):,}')
rs = [json.load(open(f)) for f in glob.glob('/data/x7/results/*.json')]
scr = collections.Counter(r.get('screened') for r in rs if r.get('screened'))
p = scr.get('parameter definition', 0)
print(f'verified {len(rs)}; screened {dict(scr)}; parameter screen {p} = {100 * p / len(rs):.1f}% -> Q4 '
      f'{"holds" if p / len(rs) < 0.24 else "fails"} (< 24%)')
