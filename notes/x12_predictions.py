"""X12 predictions Y1-Y8 (PREREGISTRATION.md, X12), judged after the run with the entry's definitions. Written during
block x12a, before any of its F1 labels, candidates or N1 entries existed; only the journals' live counts had been read.

    podman run -i --rm -v "$PWD/work:/data:ro" -v "$PWD/notes:/notes:ro" soup python3 - < notes/x12_predictions.py

Inputs, per arm (x12-f5 = fusion5, x12-f6 = fusion6): results, stats.jsonl, journal, searcher heartbeats and archives;
work/check/families.json (F1, rebuilt with both arms in taxonomy.RUNS); work/check/candidates.json,
dedupe_candidates.json and novelty_ranking.json (N1); notes/disconnected_x12-f6_x12-f5.out
(notes/disconnected.py x12-f6 x12-f5); notes/push_gate_x12.out (notes/push_gate.py x12-f5 x12-f6).
"""
import collections
import glob
import json
import os
import re
from math import comb

ARMS = {'x12-f5': 'fusion5', 'x12-f6': 'fusion6'}


def hours(T, f):
    return sum(f(T[i]) * (T[i + 1]['t'] - T[i]['t']) for i in range(len(T) - 1)) / 3600


def fisher_two_sided(a, b, c, d):
    """Fisher's exact test on [[a, b], [c, d]]: the sum of the table probabilities not above the observed one."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    p = lambda x: comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
    p0 = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9)))


def rarefied(counts, m):
    """Expected distinct families in a subsample of m without replacement (exact)."""
    N = sum(counts)
    if m >= N: return float(len(counts))
    return sum(1 - comb(N - n, m) / comb(N, m) for n in counts)


# ---- per arm: results, blocks, searchers
A = {}
for d in ARMS:
    D = f'/data/{d}'
    rs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')}
    mine = {k: r for k, r in rs.items() if str(r.get('run', '')).startswith(d.replace('-', ''))}
    L = [json.loads(l) for l in open(f'{D}/logs/stats.jsonl')]
    blocks = collections.OrderedDict()
    for s in L: blocks.setdefault(s['run'], []).append(s)
    ev = {run: sum(json.load(open(f)).get('evals', 0) for f in glob.glob(f'{D}/runs/{run}/archive_s*.json'))
          for run in blocks}
    sh = {run: hours(T, lambda s: s['n_search']) for run, T in blocks.items()}
    hb = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/logs/workers/s*.json'))]
    A[d] = dict(rs=rs, mine=mine, L=L, blocks=blocks, ev=ev, sh=sh, hb=hb,
                journal=open(f'{D}/journal/journal.md').read())
    st = collections.Counter(r.get('status') for r in mine.values())
    print(f'{d} ({ARMS[d]}): results {len(rs)}, this run {len(mine)} {dict(collections.Counter(r["run"] for r in mine.values()))}; '
          f'status {dict(st)}')

# ---- F1
F = json.load(open('/data/check/families.json'))
from soup.taxonomy import RUNS
th = F['theories']
by_run = {d: [t for t in th if t['run'] == d] for d in RUNS}
seen = set()
for d in RUNS[:RUNS.index('x11') + 1]:
    seen |= {t['family'] for t in by_run.get(d, []) if t['primary'] == 'structured'}
fam = {}
for d in ARMS:
    x = by_run.get(d, [])
    prim = collections.Counter(t['primary'] for t in x)
    fam[d] = collections.Counter(t['family'] for t in x if t['primary'] == 'structured')
    print(f'F1 {d}: {len(x)} theories, {dict(prim)}; structured {prim.get("structured", 0)}, '
          f'{len(fam[d])} families; largest {fam[d].most_common(3)}')

# Y1: rarefied structured families at the smaller arm's size
n5, n6 = sum(fam['x12-f5'].values()), sum(fam['x12-f6'].values())
m = min(n5, n6)
E5, E6 = rarefied(list(fam['x12-f5'].values()), m), rarefied(list(fam['x12-f6'].values()), m)
ratio = E6 / E5 if E5 else float('inf')
print(f'Y1: structured theories fusion5 {n5}, fusion6 {n6}; at m = {m}: expected families fusion5 {E5:.1f}, '
      f'fusion6 {E6:.1f}, ratio {ratio:.2f} -> {"holds" if ratio >= 1.5 else "fails"} (>= 1.5)')
print(f'    raw distinct: fusion5 {len(fam["x12-f5"])}, fusion6 {len(fam["x12-f6"])}')

# Y2: largest family's share of structured theories
sh5 = fam['x12-f5'].most_common(1)[0][1] / n5 if n5 else 0
sh6 = fam['x12-f6'].most_common(1)[0][1] / n6 if n6 else 0
print(f'Y2: largest share fusion5 {sh5:.1%}, fusion6 {sh6:.1%} -> '
      f'{"holds" if sh6 <= 0.5 * sh5 else "fails"} (fusion6 <= half of fusion5)')

# Y3: positive share of verified theories, non-inferiority at 0.8, Fisher beside it
pos = {d: sum(1 for r in A[d]['mine'].values() if (r.get('score') or 0) > 0) for d in ARMS}
ver = {d: len(A[d]['mine']) for d in ARMS}
p5, p6 = pos['x12-f5'] / max(1, ver['x12-f5']), pos['x12-f6'] / max(1, ver['x12-f6'])
fp = fisher_two_sided(pos['x12-f6'], ver['x12-f6'] - pos['x12-f6'], pos['x12-f5'], ver['x12-f5'] - pos['x12-f5'])
print(f'Y3: positive fusion5 {pos["x12-f5"]}/{ver["x12-f5"]} ({p5:.1%}), fusion6 {pos["x12-f6"]}/{ver["x12-f6"]} '
      f'({p6:.1%}); ratio {p6 / p5 if p5 else float("inf"):.2f}; Fisher two-sided p = {fp:.2g} -> '
      f'{"holds" if p6 >= 0.8 * p5 else "fails"} (>= 0.8)')

# Y4: disconnected (notes/disconnected.py x12-f6 x12-f5) and funnel level 7, per arm's 20 candidates
out = open('/notes/disconnected_x12-f6_x12-f5.out').read()
dis = {d: (int(mm.group(1)), int(mm.group(2))) if (mm := re.search(rf'{re.escape(d)}: (\d+) of (\d+) disconnected', out))
       else None for d in ARMS}
cand = json.load(open('/data/check/candidates.json'))
ck = {d: [c['key'] for c in cand if c['source'] == d] for d in ARMS}
dd = json.load(open('/data/check/dedupe_candidates.json'))
cls_of = {}
for c in dd['classes']:
    ks = [k if isinstance(k, str) else k.get('key') for k in c]
    for k in ks: cls_of[k] = set(ks)
R = json.load(open('/data/check/novelty_ranking.json'))['ranked']
L7 = {r['key'] for r in R if r['offdiag_laws'] and not r['classical_models'] and not r['related']}
l7 = {}
for d in ARMS:
    own = sum(1 for k in ck[d] if k in L7)                                   # the arm's candidate is N1's entry
    via = sum(1 for k in ck[d] if k not in L7 and cls_of.get(k, set()) & L7)  # merged into another run's entry
    l7[d] = (own, via)
    print(f'    {d}: candidates {len(ck[d])}, disconnected {dis[d]}, level 7 {own} as N1 entries (+{via} through a '
          f'dedupe class)')
ok4 = (dis['x12-f6'] and dis['x12-f5'] and dis['x12-f6'][0] >= dis['x12-f5'][0]
       and l7['x12-f6'][0] >= l7['x12-f5'][0])
print(f'Y4: disconnected fusion6 {dis["x12-f6"]}, fusion5 {dis["x12-f5"]}; level 7 fusion6 {l7["x12-f6"][0]}, '
      f'fusion5 {l7["x12-f5"][0]} -> {"holds" if ok4 else "fails"} (both at least as many)')

# Y5: new structured families against every run up to X11 (the other arm does not count)
new = {d: {f: c for f, c in fam[d].items() if f not in seen} for d in ARMS}
print(f'Y5: new families fusion5 {len(new["x12-f5"])}, fusion6 {len(new["x12-f6"])} -> '
      f'{"holds" if len(new["x12-f6"]) > len(new["x12-f5"]) else "fails"} (fusion6 more)')
both = set(new['x12-f5']) & set(new['x12-f6'])
print(f'    new in both arms: {len(both)}')
for d in ARMS:
    for f, c in sorted(new[d].items(), key=lambda kv: -kv[1])[:8]:
        print(f'    new in {d}: {f}: {c}')

# Y6: fusion6's speed and the share of rescores plus Mace4
for d in ARMS:
    a = A[d]; hb = a['hb']; shs = sum(a['sh'].values())
    rate = sum(a['ev'].values()) / max(1e-9, shs) / 1e6
    resc = sum(h.get('rescore_secs', 0) or 0 for h in hb); mace = sum(h.get('pskip_mace_secs', 0) or 0 for h in hb)
    share = (resc + mace) / max(1e-9, 3600 * shs)
    a['y6'] = (rate, share)
    print(f'    {d}: evaluations {a["ev"]}, searcher-hours {round(shs, 2)}, {rate:.2f}M per searcher-hour; rescores '
          f'{sum(h.get("rescores", 0) or 0 for h in hb)} in {resc:.0f} s, Mace4 {mace:.0f} s, together {share:.2%}; '
          f'cell wins {sum(h.get("wins", 0) or 0 for h in hb):,}, pushed {sum(h.get("pushed", 0) or 0 for h in hb):,}, '
          f'held {sum(h.get("held", 0) or 0 for h in hb):,}, parameter skips {sum(h.get("par_skipped", 0) or 0 for h in hb)}')
rate6, share6 = A['x12-f6']['y6']
print(f'Y6: fusion6 {rate6:.2f}M per searcher-hour, rescores + Mace4 {share6:.2%} -> '
      f'{"holds" if rate6 >= 0.5 and share6 <= 0.15 else "fails"} (>= 0.5M and <= 15%)')

# Y7: the push gate, from notes/push_gate.py
pg = open('/notes/push_gate_x12.out').read()
y7 = {}
for d in ARMS:
    run1 = next(iter(A[d]['blocks']))
    mm = re.search(rf'^{run1}: .*?99% of pushes by (\d+) s \(([\d.]+)% of the block\)', pg, re.M)
    y7[d] = float(mm.group(2)) if mm else None
    print(f'    {d} {run1}: {mm.group(0) if mm else "not found"}')
print(f'Y7: 99% of pushes by {y7["x12-f5"]}% (fusion5) and {y7["x12-f6"]}% (fusion6) of block 1 -> '
      f'{"holds" if all(v is not None and v <= 10 for v in y7.values()) else "fails"} (both within 10%)')

# Y8: no memory stop, at least 300 verified per arm
ok8 = True
for d in ARMS:
    a = A[d]
    for run, T in a['blocks'].items():
        part = a['journal'].split(f'run {run} started')[1] if f'run {run} started' in a['journal'] else a['journal']
        part = part.split(f'run {run} ended')[0]
        stop = 'memory rule' if 'memory rule:' in part else ('budget' if 'budget reached' in part else 'other')
        lo = min(T, key=lambda s: s.get('mem_available_mb') or 1e9)
        print(f'    {d} {run}: {len(T)} ticks, elapsed {T[-1]["elapsed_s"]:.0f} s, stopped by {stop}; min MemAvailable '
              f'{lo.get("mem_available_mb")} MB at {lo["ts"]}')
        ok8 &= stop == 'budget'
    ok8 &= ver[d] >= 300
print(f'Y8: verified fusion5 {ver["x12-f5"]}, fusion6 {ver["x12-f6"]} -> {"holds" if ok8 else "fails"} '
      f'(no memory stop, >= 300 each)')

# beside the predictions
for d in ARMS:
    mine = A[d]['mine']
    noc = sum(1 for r in mine.values() if not r.get('claims'))
    secs = [(r.get('secs_a') or 0) + (r.get('secs_b') or 0) for r in mine.values()]
    op = sum(1 for r in mine.values() for c in r.get('claims', []) if c.get('status') in ('open', 'unknown'))
    scr = collections.Counter(r.get('screened') for r in mine.values() if r.get('screened'))
    q = A[d]['L'][-1]['queue']
    top = sorted(mine.items(), key=lambda kv: -(kv[1].get('score') or 0))[:3]
    print(f'other {d}: no claims {noc}; mean stages a + b {sum(secs) / max(1, len(secs)):.0f} s; open or unknown claims '
          f'{op}; screened {dict(scr)}; queue at the end pending {q["pending"]}, stage c {q["stage2c"]}, dropped '
          f'{q["dropped"]}; top {[(k[:8], round(r.get("score") or 0, 3)) for k, r in top]}')
