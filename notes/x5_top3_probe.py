"""X5's top 3 candidates: which classical laws they imply (E, 20 s each). Post hoc, 23 Nov 2026, night.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x5_top3_probe.py
"""
import json
from soup.named import law_index
from soup.relabel import _proves

cands = [c for c in json.load(open('/data/check/candidates.json')) if c.get('source') == 'x5']
cands.sort(key=lambda c: -c.get('score', 0))
LAWS = ['x·y=y·x', 'x∘y=y∘x', '(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)', 'x·(x·y)=y', 'x∘(x∘y)=y', '(x·y)·y=x',
        '(x∘y)∘y=x', 'x·x=y·y', 'x∘x=y∘y', 'x·x=x∘x', 'x·(y∘z)=(x·y)∘z', 'x·(y∘z)=y∘(x·z)', 'x·y=x∘(y∘(x∘x))']
for c in cands[:3]:
    print(c['key'][:8], round(c['score'], 3), ' & '.join(c['laws']))
    for s in LAWS:
        print(f'   {s:22s}', _proves(c['T'], [law_index(s)], 20), flush=True)

# part 2: is ∘ the · loop translated by ∘'s identity (and back)? (E, 30 s each)
print('part 2')
for c in cands[:3]:
    print(c['key'][:8])
    for s in ['x∘y=(x·y)·(z∘z)', 'x·y=(x∘y)∘(z·z)', 'x∘y=(x·y)·(x∘x)', 'x·(y∘z)=(x∘y)·z']:
        print(f'   {s:28s}', _proves(c['T'], [law_index(s)], 30), flush=True)

# part 3: every X5 candidate: ∘ a translate of · by ∘'s identity, and back; Steiner-loop laws for · (E, 30 s each)
print('part 3')
TR = [law_index(s) for s in ['x∘y=(x·y)·(z∘z)', 'x·y=(x∘y)∘(z·z)']]
ST = [law_index(s) for s in ['x·y=y·x', 'x·(x·y)=y', 'x·x=y·y']]
n_tr = n_st = 0
for c in cands:
    tr, st = _proves(c['T'], TR, 30), _proves(c['T'], ST, 30)
    n_tr += tr; n_st += st
    print(f"   {c['key'][:8]} translate both ways {tr}; · a Steiner loop {st}", flush=True)
print(f'part 3: {n_tr} of {len(cands)} translates both ways; {n_st} with · a Steiner loop (E, 30 s per law)')
