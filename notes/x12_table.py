"""X12's REPORT table: the two arms of block x12a side by side, and the verifier time each arm lost to tasks that never
finished (post hoc: a deviation found after the run, REPORT "X12").

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x12_table.py

Claim outcomes as in notes/x11_table.py. "Verifier time in finished tasks" is the sum of stages a and b over the arm's
results; the arm had 2 verifier slots for 28,800 s. "Stuck at the end" is, for each verifier alive at the stop, the time
from its last result (or its start, if later) to the stop; its claimed task was put back unfinished.
"""
import collections
import glob
import json
import os
from math import comb

ARMS = ['x12-f5', 'x12-f6']


def results(d):
    return {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'/data/{d}/results/*.json')}


def outcome(c):
    s = c['status']
    if s == 'proved': return 'proved'
    if 'Vampire FMB' in s: return 'FMB'
    if 'linear model' in s: return 'linear'
    if 'E saturation' in s: return 'E saturation'
    if s.startswith('false'): return 'finite (stage a/c)'
    return s


def row(d, R):
    claims = [c for r in R for c in r.get('claims', [])]
    st = collections.Counter(outcome(c) for c in claims)
    sec = lambda st_: sum((r.get('secs') or {}).get(st_, 0) for r in R) / 3600
    nb = sum(1 for r in R if (r.get('secs') or {}).get('b'))
    scr = collections.Counter(r.get('screened') for r in R if r.get('screened'))
    L = [json.loads(l) for l in open(f'/data/{d}/logs/stats.jsonl')]
    t0, t1 = L[0]['t'] - L[0]['elapsed_s'], L[-1]['t']
    last = {}
    for r in R: last[r['verifier']] = max(last.get(r['verifier'], 0), r['t_done'])
    alive = [w['name'] for w in L[-1]['workers'] if w['role'] == 'verify']
    first = {}                                   # a verifier's start: the first tick that lists it
    for s in L:
        for w in s['workers']:
            if w['role'] == 'verify': first.setdefault(w['name'], s['t'])
    stuck = {v: round((t1 - max(last.get(v, 0), first.get(v, t0))) / 3600, 2) for v in alive}
    hourly = collections.Counter(int((r['t_done'] - t0) // 3600) for r in R)
    return {
        'theories': len(R),
        'positive score': sum((r.get('score') or 0) > 0 for r in R),
        'no claim at all': sum(1 for r in R if not r.get('claims')),
        'screened param / split': f"{scr.get('parameter definition', 0)} / {scr.get('split', 0)}",
        'stage a / b hours': f"{sec('a'):.2f} / {sec('b'):.2f}",
        'verifier time in finished tasks': f"{sec('a') + sec('b'):.2f} h of {2 * (t1 - t0) / 3600:.2f} h",
        'stuck at the end (h)': stuck,
        'results per hour': [hourly.get(h, 0) for h in range(8)],
        'mean stage b per theory (s)': f"{3600 * sec('b') / max(1, nb):.0f}",
        'claims / proved': f"{len(claims)} / {st['proved']}",
        'refuted: finite (a/c) / FMB / linear / E sat': (f"{st['finite (stage a/c)']} / {st['FMB']} / {st['linear']} / "
                                                         f"{st['E saturation']}"),
        'unknown / open': f"{st['unknown']} / {st['open']}",
        'top score': max((r.get('score') or 0) for r in R),
    }


R = {d: [r for r in results(d).values() if str(r.get('run', '')).startswith(d.replace('-', ''))] for d in ARMS}
rows = {d: row(d, R[d]) for d in ARMS}
for name in rows[ARMS[0]]:
    print(f'{name:45s} ' + ' | '.join(f'{d}: {rows[d][name]}' for d in ARMS))

# post hoc, beside Y5: new structured families (against every run up to X11) at equal sample size, by exact rarefaction
F = json.load(open('/data/check/families.json'))
from soup.taxonomy import RUNS
th = F['theories']
seen = {t['family'] for t in th if t['run'] in RUNS[:RUNS.index('x11') + 1] and t['primary'] == 'structured'}
fam = {d: collections.Counter(t['family'] for t in th if t['run'] == d and t['primary'] == 'structured') for d in ARMS}
m = min(sum(c.values()) for c in fam.values())
for d in ARMS:
    N = sum(fam[d].values())
    e = sum(1 - comb(N - n, m) / comb(N, m) for f, n in fam[d].items() if f not in seen)
    print(f'post hoc {d}: structured {N}, new families {sum(1 for f in fam[d] if f not in seen)}; expected new at m = {m}: '
          f'{e:.1f}')
