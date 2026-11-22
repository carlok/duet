"""X5 predictions P1-P3 (PREREGISTRATION.md, X5); written during the run, before any X5 result was read.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x5_predictions.py

P1: no scored X5 theory implies an argument-ignoring law on X5's final corpus (by construction).
P2: X5's ten most frequent proved emergent laws share at most 3 with X4's.
P3: the share of scored theories with a proved claim containing a square is below X4's (483 of 565, 85%).
P4 is read from notes/disconnected.py x5 x4 (the "no classical model" mark).
"""
import json, glob, collections
from soup.core import Corpus
from soup.offdiag import IGNORE, SQUARE


def load(run):
    return [r for r in (json.load(open(f)) for f in glob.glob(f'/data/{run}/results/*.json')) if r.get('score', 0) > 0]


top, out = {}, {}
for run in ['x5', 'x4']:
    pos = load(run)
    C = Corpus(store=f'/data/{run}/corpus')
    ign = sum(1 for r in pos if (lambda i: i is not None and bool((i & IGNORE).any()))(C.implied(r['T'])))
    proved = [[c for c in r.get('claims', []) if c.get('status') == 'proved'] for r in pos]
    sq = sum(1 for cl in proved if any(SQUARE[c['idx']] for c in cl))
    cnt = collections.Counter(c['law'] for cl in proved for c in cl)
    top[run] = [l for l, _ in cnt.most_common(10)]
    print(f'{run}: {len(pos)} scored; implying an IGNORE law on the final corpus: {ign}; '
          f'with a proved claim containing a square: {sq} ({100 * sq / max(1, len(pos)):.0f}%)')
    for l, c in cnt.most_common(10): print(f'    {c:4d}  {l}')
shared = set(top['x5']) & set(top['x4'])
print("P1: holds iff the x5 IGNORE count above is 0")
print(f'P2: top-10 laws shared with X4: {len(shared)} {sorted(shared)}  -> {"holds" if len(shared) <= 3 else "fails"}')
