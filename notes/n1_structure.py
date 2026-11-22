"""Basic structure of N1's top 10 (22 Nov 2026): which standard laws each theory implies (E, 10 s per goal), or
refutes in its smallest model. Input for the literature checks; not a ranking input.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/n1_structure.py

'-' means E found no proof in 10 s and the law holds in the smallest model, so it is undecided.
"""
import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from soup.core import law_vector
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves

GOALS = ['x·x=x', 'x∘x=x', 'x·x=x∘x', 'x·y=y·x', 'x∘y=y∘x', '(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)',
         'x·(x∘y)=x', 'x∘(x·y)=x', '(x·y)·z=x·z', 'x·(y·x)=x', 'x·(x·y)=x·y', '(x·y)·y=x·y', 'x·(x·y)=y',
         '(x·y)·y=x', 'x∘(x∘y)=x∘y', '(x∘y)∘y=x∘y', 'x∘(y∘x)=x']
o = json.load(open('/data/check/novelty_ranking.json'))['ranked'][:10]
cm = {json.load(open(f'/data/check/cand{i}_model.json'))['key']: json.load(open(f'/data/check/cand{i}_model.json'))
      for i in range(14, 24)}


def one(r):
    T = r['T']; m = cm.get(r['key'])
    lv = law_vector(np.array(m['F']), np.array(m['G']), m['n']) if m else None
    out = []
    for g in GOALS:
        i = law_index(g)
        if i in T: out.append(f'{LAWS[i]}: axiom'); continue
        if lv is not None and not lv[i]: out.append(f'{LAWS[i]}: fails in the {m["n"]}-element model'); continue
        out.append(f'{LAWS[i]}: ' + ('proved' if _proves(T, [i], 10) else '-'))
    return r, out


with ThreadPoolExecutor(4) as ex:
    for r, out in ex.map(one, o):
        print(f"== N1 {r['n1_rank']} {r['key'][:8]} ({r['source']}): {' & '.join(r['laws'])}")
        print('   off-diagonal emergent:', '; '.join(r['offdiag_laws']))
        m = cm.get(r['key'])
        if m: print(f"   smallest model ({m['n']} elements): · = {m['F']}, ∘ = {m['G']}")
        for line in out:
            if not line.endswith(': -'): print('   ', line)
