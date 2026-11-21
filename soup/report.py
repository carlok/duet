"""Summarise calibration (named vs size-matched random theories) and the duality-prior search."""
import glob, pickle
import numpy as np
from .paths import data
def pct(x, xs):   # share of null values strictly below x, plus half the ties
    xs = np.asarray(xs, float); return round(100 * ((xs < x).mean() + 0.5 * (xs == x).mean()), 1) if len(xs) else None
R = []
for f in glob.glob(str(data('calib_results*.pkl'))):
    if 'buggy' not in f: R += pickle.load(open(f, 'rb'))
named = [r for r in R if r.get('kind') == 'named']; null = [r for r in R if r.get('kind') == 'null']
print(f'CALIBRATION: {len(named)} named theories, {len(null)} random theories')
for k in sorted({len(r['T']) for r in null}):
    nk = [r for r in null if len(r['T']) == k]
    print(f'  null k={k}: n={len(nk)}, with any duality: {sum(bool(r.get("dualities")) for r in nk)}')
print(f'  {"theory":18s} k  gain   pct | maxdiff pct | richness pct | dualities')
for r in named:
    nk = [x for x in null if len(x['T']) == len(r['T'])]
    g = [x.get('gain', 0) for x in nk]; d = [x.get('max_difficulty', 0) for x in nk]; ri = [x.get('richness', 0) for x in nk]
    print(f"  {r['name']:18s} {len(r['T'])}  {r.get('gain',0):5.3f} {pct(r.get('gain',0), g)} | {r.get('max_difficulty',0):5.3f} {pct(r.get('max_difficulty',0), d)} | {r.get('richness',0):3d} {pct(r.get('richness',0), ri)} | {','.join(r.get('dualities', [])) or '-'}")
V = {}
for f in glob.glob(str(data('loopdual_*.pkl'))):
    V.update(pickle.load(open(f, 'rb'))['verified'])
if V:
    vs = sorted(V.values(), key=lambda r: -r.get('score', 0))
    print(f'\nDUALITY-PRIOR SEARCH: {len(vs)} verified theories; with a duality: {sum(bool(r.get("dualities")) for r in vs)}')
    nset = {r['name']: set(r['T']) for r in named}
    for r in vs[:15]:
        match = [n for n, s in nset.items() if set(r['T']) == s] or [n for n, s in nset.items() if set(r['T']) < s]
        claims = [(c['law'], c['status'], c.get('difficulty')) for c in r.get('claims', [])]
        print(f"  {r.get('score',0):.3f} {','.join(r.get('dualities', [])) or '-':14s} {' & '.join(r['laws'])}")
        print(f"        claims {claims} open {r.get('open', [])} richness {r.get('richness')} {('= or inside ' + ','.join(match)) if match else ''}")
    opens = [(r['laws'], r['open']) for r in vs if r.get('open')]
    print(f'\nOPEN CLAIMS (no proof, no countermodel up to size 4): {len(opens)} theories')
    for laws, o in opens[:20]: print('  ', ' & '.join(laws), '==>', '; '.join(o))
