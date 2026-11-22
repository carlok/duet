"""The diagonal attractor: which emergent laws the verified theories prove (22 Nov 2026, PREREGISTRATION.md X4).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - [dirs ...] < notes/diagonal.py

Default directories: t4-prior t4-noprior x1 x2 x3. Counts theories with a positive verified score, those proving an
emergent law in one variable, the most frequent proved emergent laws, and proved emergent associativity and
commutativity.
"""
import collections
import glob
import json
import re
import sys

dirs = sys.argv[1:] or ['t4-prior', 't4-noprior', 'x1', 'x2', 'x3']
R = [json.load(open(f)) for d in dirs for f in glob.glob(f'/data/{d}/results/*.json')]
pos = [r for r in R if r.get('score', 0) > 0]


def nvars(law): return len(set(re.findall(r'[xyzwuv]', law)))


cnt, onevar = collections.Counter(), 0
for r in pos:
    pr = [c['law'] for c in r.get('claims', []) if c['status'] == 'proved']
    cnt.update(pr)
    if any(nvars(l) == 1 for l in pr): onevar += 1
print(f'{" ".join(dirs)}: {len(R)} results, {len(pos)} with positive score, {onevar} prove a one-variable emergent law')
for law, n in cnt.most_common(10): print(f'{n:6d}  {law}  ({nvars(law)} variable{"s" if nvars(law) > 1 else ""})')
A = {'(x · y) · z = x · (y · z)', '(x ∘ y) ∘ z = x ∘ (y ∘ z)'}
K = {'x · y = y · x', 'x ∘ y = y ∘ x'}
print('proved emergent associativity', sum(cnt[a] for a in A), '| commutativity', sum(cnt[k] for k in K))
