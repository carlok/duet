"""What the post hoc catalogue entries g-dimonoid and commutative g-dimonoid (27 Nov 2026, after 71fd2cc6) relate,
from soup.rediscover's output, against a copy of that output taken before they were added.

    podman run -i --rm -v "$PWD/work:/data:ro" -v <dir with rediscover.before-gdim.json>:/before:ro soup \
        python3 - < notes/gdim_relations.py

Per source: verified theories that are a fragment, subvariety or equivalent of either entry (E-proved; '?' kinds,
left open by E's budget, counted apart). Then the candidates (check/candidates.json) and N1's level-7 and level-8
theories that the new entries relate. The relations of the old entries must not change (a sanity check).
"""
import collections
import json

NEW = ('g-dimonoid', 'commutative g-dimonoid')
LEVEL8 = ['bc43fd42', 'de0c0cf3', 'd0e963d9', 'd14ced44', '3818b88f', '55cb2c91', '1d0a5211', '742cc445', '97a7dfcf']
A = json.load(open('/data/check/rediscover.json'))
B = json.load(open('/before/rediscover.before-gdim.json'))

old = lambda res: {(s, x['entry'], x['key'], x['kind'], x['relabel']) for s, r in res['sources'].items()
                   for x in r['relations'] if x['entry'] not in NEW}
lost, gained = old(B) - old(A), old(A) - old(B)
print(f'old entries: relations before {len(old(B))}, after {len(old(A))}; lost {len(lost)}, gained {len(gained)}')
for x in sorted(lost)[:5]: print('  lost', x)
for x in sorted(gained)[:5]: print('  gained', x)

rel = collections.defaultdict(set)            # key -> {(entry, kind)}
tot = collections.Counter()
for s, r in A['sources'].items():
    per = collections.defaultdict(set)
    for x in r['relations']:
        if x['entry'] in NEW:
            per[(x['entry'], x['kind'])].add(x['key']); rel[x['key']].add((x['entry'], x['kind']))
    row = '; '.join(f'{e} {k} {len(v)}' for (e, k), v in sorted(per.items()))
    print(f"{s}: {r['theories']} theories, E jobs {r['e_jobs']}, unknown {r['unknown']}, skipped at the wall "
          f"{r['e_skipped_wall']}: {row or '-'}")
    for (e, k), v in per.items(): tot[(e, k)] += len(v)
print('all runs:', dict(tot))
firm = {k for k, v in rel.items() if any(kind in ('fragment', 'subvariety', 'equivalent') for _, kind in v)}
print(f'verified theories with a firm relation to a new entry: {len(firm)}')

cand = json.load(open('/data/check/candidates.json'))
R = {r['key']: r for r in json.load(open('/data/check/novelty_ranking.json'))['ranked']}
L7 = {k for k, r in R.items() if r['offdiag_laws'] and not r['classical_models'] and not r['related']}
print(f'\ncandidates related (of {len(cand)}):')
for c in cand:
    if c['key'] in rel:
        k = c['key']; r = R.get(k)
        print(f"  {k[:8]} {c['source']:10s} {sorted(rel[k])} N1 rank {r['n1_rank'] if r else '-'}"
              f"{' level 7' if k in L7 else ''}{' LEVEL 8' if k[:8] in LEVEL8 else ''}")
print('level 8 related:', [k for k in LEVEL8 if any(key.startswith(k) for key in rel)] or 'none')
