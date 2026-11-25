"""Stage c so far, and the 156 tasks waiting in x9's stage-c lane (input to the X10 preregistration, 25 Nov 2026).

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" -e PYTHONPATH=/app soup python3 /notes/stagec_history.py

Part 1, per data directory: theories with a stage-c result, wall time of stage c (secs['c'], else secs_c), and what
stage c did to the claims. A claim counts as settled in stage c by its markers: proved_in 'c' or 'c (E)'; a Mace4
model (mace4_sizes set, status false); a Vampire FMB model with the stage-c budget (fmb.secs > 60); a linear model on
the stage-c range (linear.qmax 64); an E saturation after more than stage b's 20,000 processed clauses. 'open' is
what stage c left. The markers are an approximation: a claim settled in stage b that also carries one would be
counted here.

Part 2: the tasks in /data/x9/queue/stage2c: claims still unknown per task, priority, and whether the key is a
candidate (check/candidates.json) or in an N1 table.
"""
import glob
import json
import os
import statistics as st
from collections import Counter

from soup.funnel import DIRS

ROOT = '/data'


def settled_in_c(c):
    s = c.get('status', '')
    if s == 'open': return None
    if c.get('proved_in') in ('c', 'c (E)'): return 'proved'
    if not s.startswith('false'): return None
    if 'mace4_sizes' in c and 'size' in s and 'FMB' not in s and 'linear' not in s: return 'Mace4'
    if (c.get('fmb') or {}).get('secs', 0) > 60 and 'FMB' in s: return 'FMB'
    if (c.get('linear') or {}).get('qmax') == 64 and 'linear' in s: return 'linear'
    if 'E saturation' in s and (c.get('e_processed') or 0) > 20_000: return 'E saturation'
    return None


print('Part 1: stage c per data directory')
allsecs, tot, groups = [], Counter(), {'streaming runs, T4 to X9': Counter(), 'with FMB in stage c, X5 to X9': Counter()}
for d in DIRS:
    rs = []
    for f in glob.glob(os.path.join(ROOT, d, 'results', '*.json')):
        try: r = json.load(open(f))
        except Exception: continue
        if r.get('stage') == 'c': rs.append(r)
    if not rs: continue
    secs = [(r.get('secs') or {}).get('c') or r.get('secs_c') or 0 for r in rs]
    k = Counter()
    for r in rs:
        for c in r.get('claims', []):
            if c.get('status') == 'open': k['open'] += 1
            else:
                how = settled_in_c(c)
                if how: k[how] += 1
    allsecs += [s for s in secs if s > 0]; tot.update(k)
    if d != '.': groups['streaming runs, T4 to X9'].update(k)
    if d in ('x5', 'x6', 'x7', 'x8', 'x9'): groups['with FMB in stage c, X5 to X9'].update(k)
    n_in = sum(k.values())
    print(f"  {d:11s} theories {len(rs):4d}  stage c min mean {st.mean(secs) / 60:5.1f} median {st.median(secs) / 60:5.1f} "
          f"max {max(secs) / 60:5.1f}  claims in c ~{n_in}: open {k['open']}, settled {n_in - k['open']} "
          f"({', '.join(f'{m} {v}' for m, v in k.items() if m != 'open')})")
n_in = sum(tot.values())
print(f"  all: {len(allsecs)} theories with time > 0, mean {st.mean(allsecs) / 60:.1f} min, median "
      f"{st.median(allsecs) / 60:.1f} min; claims ~{n_in}, settled {n_in - tot['open']} "
      f"({(n_in - tot['open']) / max(1, n_in):.1%})")
for name, k in groups.items():
    n = sum(k.values())
    print(f"  {name}: claims ~{n}, settled {n - k['open']} ({(n - k['open']) / max(1, n):.1%}): "
          f"{', '.join(f'{m} {v}' for m, v in k.items() if m != 'open')}")

print('\nPart 2: x9 stage-c lane')
lane = sorted(e for e in os.listdir(f'{ROOT}/x9/queue/stage2c') if e.startswith('p'))
cands = set()
try:
    for c in json.load(open(f'{ROOT}/check/candidates.json')):
        cands.add(c.get('key') if isinstance(c, dict) else c)
except Exception as e:
    print('  candidates.json unreadable:', e)
n1 = set()
for f in ('/data/check/novelty_ranking.json',):
    if os.path.exists(f):
        try:
            j = json.load(open(f)); rows = j.get('ranked', j) if isinstance(j, dict) else j
            n1 |= {r.get('key') for r in rows if isinstance(r, dict)}
        except Exception: pass
unk, prio, runs, inc, inn = [], [], Counter(), 0, 0
for f in lane:
    key = f[:-5].split('_', 1)[1]
    t = json.load(open(f'{ROOT}/x9/queue/stage2c/{f}'))
    r = json.load(open(f'{ROOT}/x9/results/{key}.json'))
    u = sum(c['status'] == 'unknown' for c in r.get('claims', []))
    unk.append(u); prio.append(t.get('prio', 0)); runs[r.get('run')] += 1
    inc += key in cands or any(key.startswith(str(c)[:8]) for c in cands if c)
    inn += key in n1
print(f'  tasks {len(lane)}; unknown claims per task: total {sum(unk)}, mean {st.mean(unk):.2f}, '
      f'distribution {sorted(Counter(unk).items())}')
print(f'  priority: max {max(prio):.3f}, median {st.median(prio):.3f}, min {min(prio):.3f}')
print(f'  verified in run: {dict(runs)}')
print(f'  candidates among them: {inc}; in an N1 table: {inn}')
