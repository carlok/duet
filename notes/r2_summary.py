"""R2 (review item B1) summary: fragment theories per entry, the hypotheses R2a-R2c, and where the candidate fragments sit in
the funnel. Reads check/interp_r2.json and check/interp_r2_ha.json (deviation 16).

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" -e PYTHONPATH=/app soup python3 /notes/r2_summary.py > notes/r2_summary.out
"""
import json
import os
from collections import defaultdict

from soup.paths import data

E = {}
for f in ('interp_r2.json', 'interp_r2_ha.json'):
    p = data('check', f)
    if p.exists():
        for e, r in json.load(open(p))['entries'].items():
            E.setdefault(e, r)                       # HA: the parallel run (the ordered run did not finish HA)
L8 = set('1f430506 1238c063 bc43fd42 de0c0cf3 d0e963d9 d14ced44 3818b88f 55cb2c91 1d0a5211 742cc445 97a7dfcf'.split())
pre = {r['key'] for r in json.load(open(data('check', 'n2_pre.json')))}           # N2 pre-stage: the 164
nov = json.load(open(data('check', 'novelty_ranking.json'))) if data('check', 'novelty_ranking.json').exists() else None
L7 = set()
if nov:
    rows = nov['ranked'] if isinstance(nov, dict) else nov
    L7 = {r['key'] for r in rows if r.get('offdiag_laws') and not r.get('classical_models') and not r.get('related')}
order = ['G', 'AG', 'R', 'CR', 'BR', 'DL', 'BA', 'HA', 'Hp', 'Rk', 'Qd', 'Qg']
frag = defaultdict(dict)                           # key -> entry -> first proved (t1, t2)
print('entry  models  groups  survivors  refuted_7_8  proved_pairs  fragment theories (random / candidate)  secs')
for e in order:
    if e not in E:
        print(f'{e:4}   not run'); continue
    r = E[e]
    ks = {}
    for x in r['results']:
        if x['result'] == 'fragment': ks.setdefault(x['key'], (x['t1'], x['t2']))
    for k, v in ks.items(): frag[k][e] = v
    rnd = sum(k.startswith('random:') for k in ks)
    unk = sum(x['result'] == 'unknown' for x in r['results'])
    print(f"{e:4} {r['models']:7} {r.get('groups', r.get('classes')):7} {r['filter_survivors']:10} "
          f"{r.get('refuted_7_8', 0):12} {sum(x['result'] == 'fragment' for x in r['results']):13}   "
          f"{len(ks):4} ({rnd} / {len(ks) - rnd}), unknown pairs {unk}   {r['secs']}")
print()
cands = {k: v for k, v in frag.items() if not k.startswith('random:')}
rands = {k: v for k, v in frag.items() if k.startswith('random:')}
print(f'R2b: {len(rands)} of 120 random theories are a fragment of at least one entry (prediction: 0)')
print(f'candidates that are a fragment of at least one entry: {len(cands)} of 318')
a = [k for k in cands if k.startswith('a9295908')]
print('R2a: a9295908', 'fragment of ' + ', '.join(f'{e} with · = {t1}, ∘ = {t2}' for e, (t1, t2) in cands[a[0]].items())
      if a else 'NOT found as a fragment')
print(f"R2c (descriptive): of N2's pre-stage 164, {len([k for k in cands if k in pre])} are fragments; "
      f"of N1's level 7 ({len(L7)}), {len([k for k in cands if k in L7])}; "
      f"of the 11 at level 8, {len([k for k in cands if k[:8] in L8])}")
print()
print('candidate fragments in the N2 pre-stage, with the entries and the first proved terms:')
for k in sorted(cands, key=lambda k: (k not in L7, k)):
    if k not in pre: continue
    tag = ' L8' if k[:8] in L8 else (' L7' if k in L7 else '')
    print(f'  {k[:8]}{tag}: ' + '; '.join(f'{e} · = {t1}, ∘ = {t2}' for e, (t1, t2) in cands[k].items()))
