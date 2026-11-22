"""Per-run statistics of verified results: claim outcomes, FMB refutations, V4 screen marks (22 Nov 2026).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <dir> < notes/runstats.py
"""
import json, glob, collections, sys
d = sys.argv[1]
R = [json.load(open(f)) for f in glob.glob(f'/data/{d}/results/*.json')]
claims = [c for r in R for c in r.get('claims', [])]
st = collections.Counter()
for c in claims:
    s = c['status']
    if s == 'proved': st['proved'] += 1
    elif 'Vampire FMB' in s: st['FMB'] += 1
    elif 'E saturation, uncertified' in s: st['E sat (uncertified)'] += 1
    elif 'E saturation' in s: st['E sat'] += 1
    elif s.startswith('false'): st['finite (stage a/c)'] += 1
    else: st[s] += 1
fmb_sizes = collections.Counter(c['fmb'].get('n') for c in claims if 'Vampire FMB' in c['status'])
fmb_ran = sum(1 for c in claims if 'fmb' in c)
pos = [r for r in R if r.get('score', 0) > 0]
emerg = [r for r in R if any(c['status'] == 'proved' for c in r.get('claims', []))]
print(f'{d}: results {len(R)}, score>0 {len(pos)}, with emergent law {len(emerg)}, claims {len(claims)}')
print(' claim outcomes:', dict(st))
print(' FMB ran on', fmb_ran, 'claims; refutation sizes', dict(sorted(fmb_sizes.items())))
print(' stage c results:', sum(1 for r in R if r.get('stage') == 'c'), '| verifier cfgs:', dict(collections.Counter(r.get('verifier_cfg') for r in R)))
scr = collections.Counter(r.get('screened') for r in R if r.get('screened'))
secs = sorted(r['screen']['secs'] for r in R if 'screen' in r)
print(' V4 screens:', dict(scr), '| screen secs median', secs[len(secs) // 2] if secs else None, 'max', secs[-1] if secs else None)
