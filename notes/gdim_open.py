"""The candidates that soup.rediscover left as 'subvariety?' of a g-dimonoid entry (E's 10 s per law ran out; the
model filter passed): E again with 120 s and 2M processed clauses per law, under the same relabelling.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/gdim_open.py
"""
import json

from soup.data import LAWS
from soup.provers import prove_e
from soup.rediscover import variants

NEW = ('g-dimonoid', 'commutative g-dimonoid')
A = json.load(open('/data/check/rediscover.json'))
cand = {c['key']: c for c in json.load(open('/data/check/candidates.json'))}
V = {(name, rname): N for name, rname, N in variants() if name in NEW}
todo = {}
for s, r in A['sources'].items():
    for x in r['relations']:
        if x['entry'] in NEW and x['kind'] == 'subvariety?' and x['key'] in cand:
            todo.setdefault(x['key'], []).append((x['entry'], x['relabel']))
for key, rels in todo.items():
    T = cand[key]['T']
    print(f"{key[:8]} ({cand[key]['source']}): {' & '.join(LAWS[t] for t in T)}", flush=True)
    for entry, rname in rels:
        N = V[(entry, rname)]
        res = {}
        for v in N:
            if v in T: res[v] = 'axiom'; continue
            res[v] = prove_e(sorted(T), v, 2_000_000, 120)['status']
        verdict = ('subvariety' if all(s in ('axiom', 'proved') for s in res.values())
                   else 'not a subvariety' if 'countersatisfiable' in res.values() else 'open')
        print(f'  {entry} ({rname}): {verdict}', flush=True)
        for v, s in res.items():
            if s != 'axiom': print(f'    {LAWS[v]:26s} {s}', flush=True)
