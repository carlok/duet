"""The funnel over all runs (23 Nov 2026): cheap evaluations -> verified -> scored -> non-fragments -> candidates ->
varieties -> not known (N1) -> the N1 entries with every mark.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/funnel.py
"""
import glob, json, os
DIRS = ['.', 't4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x5']
tot = dict(verified=0, scored=0, nonfrag=0)
for d in DIRS:
    base = '/data' if d == '.' else f'/data/{d}'
    rs = [json.load(open(f)) for f in glob.glob(f'{base}/results/*.json')]
    sc = [r for r in rs if r.get('score', 0) > 0]
    fp = f'{base}/fragments.json'
    nf = None
    if os.path.exists(fp):
        fr = json.load(open(fp))
        nf = sum(1 for r in fr if not r.get('fragment_of') and not any(v == 'fragment' for v in r.get('per_named', {}).values()))
    tot['verified'] += len(rs); tot['scored'] += len(sc); tot['nonfrag'] += nf or 0
    print(f'{d:11s} verified {len(rs):5d}  scored {len(sc):5d}  non-fragments {nf}')
print('total', tot)
cand = json.load(open('/data/check/candidates.json'))
dd = json.load(open('/data/check/dedupe_candidates.json'))
merged = sum(len(c) - 1 for c in dd['classes'])
print(f'candidates {len(cand)}; varieties {len(cand) - merged}')
nr = json.load(open('/data/check/novelty_ranking.json'))
rows = nr['ranked'] if isinstance(nr, dict) and 'ranked' in nr else nr
print('novelty file keys:', list(nr)[:8] if isinstance(nr, dict) else type(nr))
R = nr['ranked']
print('ranked (not known)', len(R), '| fields', sorted(R[0])[:20])
off = [r for r in R if r['offdiag_laws']]
nocl = [r for r in off if not r['classical_models']]
unrel = [r for r in nocl if not r['related']]
lit = [r for r in unrel if str(r['literature']).startswith(('Nothing found', '-'))]
print(f'not known {len(R)}; with an off-diagonal emergent law {len(off)}; and no classical model {len(nocl)}; '
      f'and not related by hand {len(unrel)}; and "Nothing found" in the literature column {len(lit)}')
for r in unrel[:20]:
    print(f"  N1 {r['n1_rank']:3d} {r['key'][:8]} {r['source']:10s} sizes {r['nondeg_sizes']} lit: {str(r['literature'])[:45]}")
