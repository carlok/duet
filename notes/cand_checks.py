"""Equivalence checks and ranks of one source's candidates (22 Nov 2026).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <source> < notes/cand_checks.py

Reads work/check/{candidates,split_candidates,hidden_candidates,relabel_candidates,ranking}.json.
"""
import collections
import json
import sys

src = sys.argv[1] if len(sys.argv) > 1 else 'x3'
cand = {c['key']: c for c in json.load(open('/data/check/candidates.json')) if c.get('source') == src}
sp = {c['key']: c for c in json.load(open('/data/check/split_candidates.json')) if c['key'] in cand}
hd = {c['key']: c for c in json.load(open('/data/check/hidden_candidates.json')) if c['key'] in cand}
rl = {c['key']: c for c in json.load(open('/data/check/relabel_candidates.json')) if c['key'] in cand}
print(f'{src}: {len(cand)} candidates; checked: split {len(sp)}, hidden {len(hd)}, relabel {len(rl)}')
print(' split:', dict(collections.Counter(str(c.get('split')) for c in sp.values())))
print(' hidden definitional:', sum(1 for c in hd.values() if c.get('definitional')))
imp = collections.Counter(n for c in rl.values() for n in (c.get('implies') or []))
print(' relabel: imply a named theory', sum(1 for c in rl.values() if c.get('implies')), dict(imp),
      '| fragment of one', sum(1 for c in rl.values() if c.get('fragment_of')),
      '| equivalent to one', sum(1 for c in rl.values() if c.get('equivalent')))
rk = json.load(open('/data/check/ranking.json'))['candidates']
print(' ranks among', len(rk), ':', [i for i, r in enumerate(rk, 1) if r.get('source') == src])
