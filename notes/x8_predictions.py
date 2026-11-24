"""X8 predictions R2 and R3 (PREREGISTRATION.md, X8), judged over X8 and x8b together (deviation 10), with each
part's counts. R1 comes from soup.funnel, R4 from soup.taxonomy.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x8_predictions.py
"""
import collections
import glob
import json
import math

import numpy as np
from soup.stream.searcher import BLOOM_BITS

D = '/data/x8'


def distinct(files):
    U = np.bitwise_or.reduce([np.load(f) for f in files])
    fill = int(np.bitwise_count(U).sum(dtype=np.int64))
    return -BLOOM_BITS * math.log(1 - fill / BLOOM_BITS), fill / BLOOM_BITS


def raw(run):
    return sum(json.load(open(f)).get('evals') or 0 for f in glob.glob(f'{D}/runs/{run}/archive_s*.json'))


print('R2: distinct evaluations (union of the bitmaps, linear counting) against raw (searchers\' final evals)')
parts = {'x8': raw('x8'), 'x8b': raw('x8b')}
for name, runs in (('x8', ['x8']), ('x8b', ['x8b']), ('x8 + x8b', ['x8', 'x8b'])):
    r = sum(parts[x] for x in runs)
    d, fill = distinct([f for x in runs for f in glob.glob(f'{D}/runs/{x}/bloom_*.npy')])
    print(f'  {name}: raw {r:,}; distinct {d:,.0f} = {100 * d / r:.1f}% (bitmap fill {100 * fill:.1f}%)')
r = sum(parts.values()); d, _ = distinct(glob.glob(f'{D}/runs/x8*/bloom_*.npy'))
print(f'  -> R2 {"holds" if d >= 0.7 * r else "fails"} (>= 70%)')

hs = [json.load(open(f)) for f in glob.glob(f'{D}/logs/workers/s*.json')]
for k in ('known_skipped', 'cand_skipped', 'seen_skipped', 'lat_skipped', 'ign_skipped'):
    print(f'  {k}: {sum(h.get(k) or 0 for h in hs):,}')

print('R3: parameter screen among verified theories')
rs = [json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')]
tot_p = 0
for run in ('x8', 'x8b'):
    sub = [x for x in rs if x.get('run') == run]
    scr = collections.Counter(x.get('screened') for x in sub if x.get('screened'))
    p = scr.get('parameter definition', 0); tot_p += p
    pos = sum(1 for x in sub if (x.get('score') or 0) > 0)
    print(f'  {run}: verified {len(sub)}, positive {pos}, screened {dict(scr)}, parameter {p} = '
          f'{100 * p / max(1, len(sub)):.1f}%')
print(f'  x8 + x8b: verified {len(rs)}, parameter {tot_p} = {100 * tot_p / len(rs):.1f}% -> R3 '
      f'{"holds" if tot_p / len(rs) < 0.05 else "fails"} (< 5%)')

claims = [c for x in rs for c in x.get('claims', [])]
st = collections.Counter()
for c in claims:
    s = c['status']
    st['proved' if s == 'proved' else 'E saturation' if 'saturation' in s else 'finite model' if s.startswith('false')
       else s] += 1
print(f'claims {len(claims)}: {dict(st)}; stage c: {sum(1 for x in rs if x.get("stage") == "c")}')
