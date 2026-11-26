"""X11 predictions W1-W7 (PREREGISTRATION.md, X11 and its amendment), judged after the run, with the entry's definitions.

    podman run -i --rm -v "$PWD/work:/data:ro" -v "$PWD/notes:/notes:ro" soup python3 - < notes/x11_predictions.py

Inputs: x11's results, stats.jsonl, journal and searcher heartbeats; work/check/families.json (F1, rebuilt with x11);
notes/disconnected_x11_x10.out (notes/disconnected.py x11 x10). X10 = its own 578 theories, or the x10 directory for F1.
"""
import collections
import glob
import json
import os
import re

D = '/data/x11'
rs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')}
mine = {k: r for k, r in rs.items() if str(r.get('run', '')).startswith('x11')}
print(f'results {len(rs)}: x11 {len(mine)} {dict(collections.Counter(r["run"] for r in mine.values()))}')

L = [json.loads(l) for l in open(f'{D}/logs/stats.jsonl')]
blocks = collections.OrderedDict()
for s in L: blocks.setdefault(s['run'], []).append(s)


def hours(T, f):
    return sum(f(T[i]) * (T[i + 1]['t'] - T[i]['t']) for i in range(len(T) - 1)) / 3600


# W1: verifier-marked parameter definitions
scr = collections.Counter(r.get('screened') for r in mine.values() if r.get('screened'))
par = scr.get('parameter definition', 0)
print(f'W1: screened {dict(scr)}; parameter definitions {par} of {len(mine)} ({par / max(1, len(mine)):.1%}) -> '
      f'{"holds" if par <= 0.05 * len(mine) else "fails"} (<= 5%; X10 50.9%)')

# W2: evaluations per searcher-hour (each searcher's final evals, as soup.funnel) and the Mace4 share of searcher time
ev, sh = {}, {}
for run, T in blocks.items():
    ev[run] = sum(json.load(open(f)).get('evals', 0) for f in glob.glob(f'{D}/runs/{run}/archive_s*.json'))
    sh[run] = hours(T, lambda s: s['n_search'])
rate = sum(ev.values()) / max(1e-9, sum(sh.values())) / 1e6
hb = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/logs/workers/s*.json'))]
mace = sum(h.get('pskip_mace_secs', 0) for h in hb)
share = mace / max(1e-9, 3600 * sum(sh.values()))
print(f'W2: evaluations {ev}, searcher-hours {({k: round(v, 2) for k, v in sh.items()})}, {rate:.2f}M per '
      f'searcher-hour; Mace4 {mace:.0f} s = {share:.2%} of searcher time -> '
      f'{"holds" if rate >= 0.75 and share <= 0.05 else "fails"} (>= 0.75M and <= 5%)')
for h in hb:
    print(f'  {h.get("name")}: evals {h.get("evals"):,}, cell wins skipped {h.get("par_skipped")}, distinct law sets '
          f'skipped {h.get("pskip_fired")}, Mace4 calls {h.get("pskip_mace")} ({h.get("pskip_mace_secs")} s), '
          f'countermodels added {h.get("pskip_added")}')
print(f'  in all: cell wins skipped {sum(h.get("par_skipped", 0) for h in hb)}, distinct law sets '
      f'{sum(h.get("pskip_fired", 0) for h in hb)}, countermodels added {sum(h.get("pskip_added", 0) for h in hb)}')

# W3 and W6: F1 on the x11 directory
F = json.load(open('/data/check/families.json'))
from soup.taxonomy import RUNS
th = F['theories']
by_run = {d: [t for t in th if t['run'] == d] for d in RUNS}
x = by_run.get('x11', [])
prim = collections.Counter(t['primary'] for t in x)
st = prim.get('structured', 0)
print(f'W3: x11 in families.json {len(x)}: {dict(prim)}; structured {st / max(1, len(x)):.1%} -> '
      f'{"holds" if st >= 0.30 * len(x) else "fails"} (>= 30%; X10 11.0%)')
seen = set()
for d in RUNS[:RUNS.index('x11')]:
    seen |= {t['family'] for t in by_run.get(d, []) if t['primary'] == 'structured'}
fx = collections.Counter(t['family'] for t in x if t['primary'] == 'structured')
new = {f: c for f, c in fx.items() if f not in seen}
print(f'W6: x11 has {len(fx)} structured families, {len(new)} new -> {"holds" if len(new) >= 5 else "fails"} '
      f'(>= 5; X10 3)')
for f, c in sorted(new.items(), key=lambda kv: -kv[1]):
    print(f'  new: {f}: {c}')
top = fx.most_common(5)
print(f'  largest in x11: {top}')

# W4 and W5: the candidates, from notes/disconnected.py x11 x10
out = open('/notes/disconnected_x11_x10.out').read().split('== x10')[0]
rows = re.findall(r'^([0-9a-f]{8}) works=(\S+) .* classical=(\d+)', out, re.M)
cl = sum(1 for _, _, c in rows if int(c) > 0)
m = re.search(r'x11: (\d+) of (\d+) disconnected', out)
dis = int(m.group(1)) if m else None
print(f'W4: {cl} of {len(rows)} candidates with a classical model -> {"holds" if cl <= 10 else "fails"} (<= 10; X10 15)')
print(f'W5: {dis} of {len(rows)} disconnected -> {"holds" if dis is not None and dis >= 8 else "fails"} (>= 8; X10 4)')

# W7: memory
journal = open(f'{D}/journal/journal.md').read()
for run, T in blocks.items():
    part = journal.split(f'run {run} started')[1].split(f'run {run} ended')[0] if f'run {run} started' in journal else ''
    stop = 'memory rule' if 'memory rule:' in part else 'budget'
    lo = min((s.get('mem_available_mb') for s in T if s.get('mem_available_mb')), default=None)
    t_lo = min((s for s in T if s.get('mem_available_mb')), key=lambda s: s['mem_available_mb'])['ts']
    print(f'W7: {run}: {len(T)} ticks, elapsed {T[-1]["elapsed_s"]:.0f} s, stopped by {stop}; min MemAvailable {lo} MB '
          f'at {t_lo} -> {"holds" if stop == "budget" else "fails"}')

# beside the predictions: stage c and the open claims
c = [r for r in mine.values() if r.get('stage') == 'c']
pos = sum(1 for r in mine.values() if (r.get('score') or 0) > 0)
op = sum(1 for r in mine.values() for cl_ in r.get('claims', []) if cl_.get('status') in ('open', 'unknown'))
print(f'other: positive score {pos}; through stage c {len(c)}; open or unknown claims {op}; stage-c lane at the end '
      f'{L[-1]["queue"]["stage2c"]}, pending {L[-1]["queue"]["pending"]}')

# beside the predictions: what stage c settled (the markers of notes/x10_predictions.py, U3)
def settled_in_c(cl):
    s = cl.get('status', '')
    if s == 'open': return None
    if cl.get('proved_in') in ('c', 'c (E)'): return 'proved'
    if not s.startswith('false'): return None
    if 'mace4_sizes' in cl and 'size' in s and 'FMB' not in s and 'linear' not in s: return 'Mace4'
    if (cl.get('fmb') or {}).get('secs', 0) > 60 and 'FMB' in s: return 'FMB'
    if (cl.get('linear') or {}).get('qmax') == 64 and 'linear' in s: return 'linear'
    if 'E saturation' in s and (cl.get('e_processed') or 0) > 20_000: return 'E saturation'
    return None


k = collections.Counter()
for r in c:
    for cl_ in r.get('claims', []):
        if cl_.get('status') == 'open': k['open'] += 1
        else:
            how = settled_in_c(cl_)
            if how: k[how] += 1
n = sum(k.values())
mins = sorted(round((r.get('secs') or {}).get('c', 0) / 60, 1) for r in c)
print(f'stage c: {len(c)} theories, minutes {mins}; claims ~{n}: open {k["open"]}, settled {n - k["open"]}: '
      f'{dict((m, v) for m, v in k.items() if m != "open")}')
for kk, r in sorted(mine.items(), key=lambda kv: -(kv[1].get('score') or 0))[:3]:
    print(f'  top: {kk[:8]} score {r.get("score"):.3f} stage {r.get("stage")} models {r.get("models")}')
