"""'Disconnected' candidates (PREREGISTRATION.md, X4, added 22 Nov 2026 12:54 UTC; written during X4, before any X4
result was read).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - x4 x3 < notes/disconnected.py

For each source, its candidates (work/check/candidates.json: the top-20 non-fragments) get three marks:
- works: non-degenerate census models at two or more sizes, and at least one proved emergent law (results/<key>.json;
  under V5 the claims are off-diagonal by construction);
- unconnected: no relation from any check. That means:
  - no R1 fragment, subvariety or equivalence (work/check/rediscover.json); a 'fragment?' or 'subvariety?' left by E's
    budget makes it 'unknown';
  - no V4 mark, not split (split None is 'unknown'), not definitional;
  - nothing in soup.relabel's implies / fragment_of / equivalent_to;
- no classical model: no non-degenerate base probe on 3 or more elements satisfies the theory, other than random
  tables (rand*) and the complete set on 2 elements (all2*). All other probes are built from structured operations
  (affine, chains, F4, Klein, Boolean, group-derived, Z/n ring operations, M3, N5, and mixed pairs of these).
  Structures found by the search are not probes, so they never count as classical.

"Unconnected" means unconnected to our checks and catalogue. It is no claim about the literature.
"""
import json
import os
import re
import sys

import numpy as np

from soup.data import NONDEG, PROBES, SIZES, sat_base, unpack_probes

srcs = sys.argv[1:] or ['x4', 'x3']
CHECK = '/data/check'


def load(name):
    p = os.path.join(CHECK, name)
    return json.load(open(p)) if os.path.exists(p) else None


cands = load('candidates.json')
split = {c['key']: c.get('split') for c in load('split_candidates.json') or []}
hidden = {c['key']: c.get('definitional') for c in load('hidden_candidates.json') or []}
relab = {c['key']: c for c in load('relabel_candidates.json') or []}
r1 = (load('rediscover.json') or {}).get('sources', {})
CLASSICAL = np.array([not re.match(r'(rand|all2)', name) for name, _ in PROBES])


def classical_models(T):
    base = unpack_probes(sat_base(list(T)))
    hit = base & NONDEG & (SIZES >= 3) & CLASSICAL
    return sorted({PROBES[i][0] for i in np.flatnonzero(hit)})


def marks(src, c):
    rpath = f'/data/{src}/results/{c["key"]}.json'
    r = json.load(open(rpath)) if os.path.exists(rpath) else {}
    works = len(r.get('model_sizes') or []) >= 2 and any(x.get('status') == 'proved' for x in r.get('claims', []))
    why, unknown = [], []
    rel = [x for x in r1.get(src, {}).get('relations', []) if x['key'] == c['key']]
    why += [f"R1 {x['kind']} {x['entry']} ({x['relabel']})" for x in rel if not x['kind'].endswith('?')]
    unknown += [f"R1 {x['kind']} {x['entry']}" for x in rel if x['kind'].endswith('?')]
    if r.get('screened'): why.append(f"V4 {r['screened']}")
    s = split.get(c['key'], 'not run')
    if s is True: why.append('split')
    elif s is None or s == 'not run': unknown.append(f'split {s}')
    if hidden.get(c['key']): why.append('definitional')
    rl = relab.get(c['key'], {})
    for k in ('implies', 'fragment_of', 'equivalent_to'):
        for n in rl.get(k) or []: (unknown if '?' in n else why).append(f'relabel {k} {n}')
    if c['key'] not in relab: unknown.append('relabel not run')
    cl = classical_models(c['T'])
    return works, why, unknown, cl


for src in srcs:
    cs = [c for c in cands if c.get('source') == src]
    full = []
    print(f'== {src}: {len(cs)} candidates')
    for c in cs:
        works, why, unknown, cl = marks(src, c)
        unconnected = not why and not unknown
        tag = 'DISCONNECTED' if works and unconnected and not cl else ''
        if tag: full.append(c['key'])
        print(f"{c['key'][:8]} works={works} connected={'; '.join(why) or '-'} unknown={'; '.join(unknown) or '-'} "
              f"classical={len(cl)}{' e.g. ' + cl[0] if cl else ''} {tag}")
        if tag: print('   ', ' & '.join(c['laws']))
    print(f'{src}: {len(full)} of {len(cs)} disconnected (works, unconnected, no classical model)')
