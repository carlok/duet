"""X5 baselines, measured before X5's preregistration (22 Nov 2026, 21:30 UTC): argument-ignoring and square laws in X3/X4.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x5_baseline.py
"""
import json, glob, random, collections
from soup.core import Corpus, LAWS, ORDER
from soup.named import law_index
from soup.offdiag import offdiag_gain, IGNORE, SQUARE

print('IGNORE laws:', int(IGNORE.sum()), '; SQUARE laws:', int(SQUARE.sum()))
C = Corpus(store='/data/x4/corpus')
pos = [r for r in (json.load(open(f)) for f in glob.glob('/data/x4/results/*.json')) if r.get('score', 0) > 0]
ig = sum(1 for r in pos if (lambda i: i is not None and (i & IGNORE).any())(C.implied(r['T'])))
sq = sum(1 for r in pos if any(SQUARE[c['idx']] for c in r.get('claims', []) if c.get('status') == 'proved'))
print(f'X4: {len(pos)} scored; {ig} imply an IGNORE law on the final corpus; {sq} have a proved claim with a square')
for run in ['x4', 'x3']:
    C = Corpus(store=f'/data/{run}/corpus')
    fs = glob.glob(f'/data/{run}/results/*.json'); random.seed(2); fs = random.sample(fs, min(300, len(fs)))
    n = rigid = rg = 0
    for f in fs:
        imp = C.implied(json.load(open(f))['T'])
        if imp is None: continue
        n += 1
        if (imp & IGNORE).any(): continue
        rigid += 1
        g = offdiag_gain(C, json.load(open(f))['T'], imp)
        rg += g is not None and len(g) > 0
    print(f'{run}: sample {n}, rigid {rigid}, rigid with off-diagonal gain {rg}')
# the rejected first design: square-free part of the X4 off-diagonal gain, sample of 150
C = Corpus(store='/data/x4/corpus'); fs = sorted(glob.glob('/data/x4/results/*.json')); random.seed(1)
cnt = collections.Counter()
for f in random.sample(fs, 150):
    g = offdiag_gain(C, json.load(open(f))['T'])
    left = [e for e in (g if g is not None else []) if not SQUARE[e]]
    if left: cnt[LAWS[min(left, key=lambda e: (ORDER[e], e))]] += 1
print('X4 sample of 150, smallest square-free off-diagonal law:', cnt.most_common(3))
