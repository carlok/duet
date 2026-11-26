"""X10 predictions U1-U5 (PREREGISTRATION.md, X10 and its four amendments), over both blocks x10a and x10b.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x10_predictions.py

Copied tasks are the 156 files in /data/x9/queue/stage2c (X10's fork copied them, with their stage-b results). A claim
counts as settled in stage c by the markers of notes/stagec_history.py (copied below).
"""
import collections
import glob
import json
import os

D, X9 = '/data/x10', '/data/x9'
qkey = lambda f: os.path.basename(f)[:-5].split('_', 1)[1]
copied_c = {qkey(f) for f in glob.glob(f'{X9}/queue/stage2c/*.json')}
copied_p = {qkey(f) for f in glob.glob(f'{X9}/queue/pending/*.json')}
rs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')}
mine = {k: r for k, r in rs.items() if str(r.get('run', '')).startswith('x10')}
by_run = collections.Counter(r['run'] for r in mine.values())
print(f'results {len(rs)}: x10 {len(mine)} {dict(by_run)}; copied stage-c tasks {len(copied_c)}, copied pending '
      f'{len(copied_p)}; copied results not redone {sum(1 for k in copied_c if k in rs and k not in mine)}')

L = [json.loads(l) for l in open(f'{D}/logs/stats.jsonl')]
blocks = collections.OrderedDict()
for s in L: blocks.setdefault(s['run'], []).append(s)


def hours(T, f):
    return sum(f(T[i]) * (T[i + 1]['t'] - T[i]['t']) for i in range(len(T) - 1)) / 3600


def n_c(s):
    return sum(1 for w in s['workers'] if w.get('alive') and w.get('role') == 'verify' and w.get('state') == 'stage c')


# U1: the cap, and the budget reached without the memory rule
journal = open(f'{D}/journal/journal.md').read()
mx = max(n_c(s) for s in L)
print(f'U1: most workers in stage c at one tick: {mx} (cap 2) -> cap {"holds" if mx <= 2 else "fails"}')
stops = {}
for run, T in blocks.items():
    stops[run] = 'memory rule' if 'memory rule:' in journal.split(f'run {run} started')[1].split('ended')[0] else 'budget'
    lo = min((s.get('mem_available_mb') for s in T if s.get('mem_available_mb')), default=None)
    print(f'  {run}: {len(T)} ticks, elapsed {T[-1]["elapsed_s"]:.0f} s, stopped by {stops[run]}, '
          f'min MemAvailable {lo} MB, most in stage c {max(n_c(s) for s in T)}')
mem = [r for r, s in stops.items() if s == 'memory rule']
print(f'  -> U1 {"fails" if mem or mx > 2 else "holds"}: memory rule in {mem or "no block"}')

# U2: copied tasks through stage c
c = {k: r for k, r in mine.items() if r.get('stage') == 'c'}
cc = {k: r for k, r in c.items() if k in copied_c}
mins = sorted(round((r.get('secs') or {}).get('c', 0) / 60, 1) for r in c.values())
print(f'U2: {len(c)} theories through stage c, {len(cc)} of them copied, {len(c) - len(cc)} from X10\'s own search '
      f'-> {"holds" if len(cc) >= 12 else "fails"} (>= 12 copied)')
print(f'  minutes in stage c: {mins}; mean {sum(mins) / max(1, len(mins)):.1f}')
for run, T in blocks.items():
    print(f'  {run}: stage-c lane {T[0]["queue"]["stage2c"]} at the start, {T[-1]["queue"]["stage2c"]} at the end; '
          f'stage-c worker-hours {hours(T, n_c):.2f}')


# U3: what stage c settled
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
for r in c.values():
    for cl in r.get('claims', []):
        if cl.get('status') == 'open': k['open'] += 1
        else:
            how = settled_in_c(cl)
            if how: k[how] += 1
n = sum(k.values())
settled = n - k['open']
print(f'U3: claims in stage c ~{n}: open {k["open"]}, settled {settled} ({settled / max(1, n):.1%}): '
      f'{dict((m, v) for m, v in k.items() if m != "open")}; proved {k["proved"]} -> '
      f'{"holds" if settled >= 0.05 * n and k["proved"] <= 1 else "fails"} (>= 5% settled, <= 1 proved)')

# U4: level 0, from each searcher's final evals in runs/<run>/archive_s*.json (as soup.funnel)
ev = {}
for run in blocks:
    ev[run] = sum(json.load(open(f)).get('evals', 0) for f in glob.glob(f'{D}/runs/{run}/archive_s*.json'))
tot = sum(ev.values())
print(f'U4: evaluations {ev}, sum {tot:,} -> {"holds" if tot >= 22e6 else "fails"} (>= 22M, restated); '
      f'level 0 {115_133_315 + tot:,} (115,133,315 before)')
for run, T in blocks.items():
    sh = hours(T, lambda s: s['n_search'])
    print(f'  {run}: searcher-hours {sh:.2f}, {ev[run] / max(1e-9, sh) / 1e6:.2f}M per searcher-hour, '
          f'searchers at most {max(s["n_search"] for s in T)}')

# U5: new theories through stages a and b
new = {kk: r for kk, r in mine.items() if kk not in copied_c}
print(f'U5: {len(new)} theories through stages a and b in X10 ({sum(kk in copied_p for kk in new)} of them the copied '
      f'pending one) -> {"holds" if len(new) >= 400 else "fails"} (>= 400)')
for run, T in blocks.items():
    ab = hours(T, lambda s: sum(1 for w in s['workers'] if w.get('alive') and w.get('role') == 'verify'
                                and w.get('state') != 'stage c'))
    nr = sum(1 for r in new.values() if r['run'] == run)
    print(f'  {run}: {nr} theories, {ab:.2f} verifier-hours outside stage c, {nr / max(1e-9, ab):.1f} per hour')
pos = sum(1 for r in new.values() if (r.get('score') or 0) > 0)
print(f'  positive score: {pos}; open claims left in X10 results: '
      f'{sum(1 for r in mine.values() for cl in r.get("claims", []) if cl.get("status") in ("open", "unknown"))}')
