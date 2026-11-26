"""When the searchers stop pushing: the push gate over a run's ticks (found after X11, 26 Nov 2026; post hoc).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - x11 x10 x8 < notes/push_gate.py

A searcher pushes a cell win only if k x priority >= gate x (the 20th best verified score of the arm), gate = 0.5
(supervisor --gate). Otherwise the win is 'held' in the archive. For each block: pushes, holds and the bar at a few
times, and the time after which 99% of the block's pushes had been made.
"""
import collections
import json
import sys

for d in sys.argv[1:] or ['x11']:
    L = [json.loads(l) for l in open(f'/data/{d}/logs/stats.jsonl')]
    blocks = collections.OrderedDict()
    for s in L: blocks.setdefault(s['run'], []).append(s)
    for run, T in blocks.items():
        # per searcher name: a counter only grows while the process lives; a name missing from a tick is skipped, and
        # a counter that falls means a new process under that name (count from zero again)
        last = {'pushed': {}, 'held': {}}
        inc_p, inc_h = [], []
        for s in T:
            for f, inc in (('pushed', inc_p), ('held', inc_h)):
                n = 0
                for w in s['workers']:
                    if w.get('role') != 'search' or f not in w: continue
                    v, prev = w[f], last[f].get(w['name'], 0)
                    n += v - prev if v >= prev else v
                    last[f][w['name']] = v
                inc.append(n)
        inc_p, inc_h = inc_p[1:], inc_h[1:]
        if not any(inc_p):
            print(f'{run}: no searcher pushes recorded'); continue
        tot_p, tot_h = sum(inc_p), sum(inc_h)
        acc, t99 = 0, None
        for s, x in zip(T[1:], inc_p):
            acc += x
            if t99 is None and acc >= 0.99 * tot_p: t99 = s['elapsed_s']
        end = T[-1]['elapsed_s']
        print(f'{run}: {len(T)} ticks, {end:.0f} s; pushes {tot_p:,}, held {tot_h:,}; 99% of pushes by {t99:.0f} s '
              f'({t99 / end:.1%} of the block); pending at the end {T[-1]["queue"]["pending"]}, '
              f'bar at the end {T[-1]["queue"]["threshold"]} x gate, k {T[-1]["queue"]["k"]}')
        for frac in (0.02, 0.05, 0.1, 0.25, 0.5, 1.0):
            s = min(T, key=lambda s: abs(s['elapsed_s'] - frac * end))
            i = T.index(s)
            print(f'   at {s["elapsed_s"]:6.0f} s: pushes so far {sum(inc_p[:i]):6,}, held {sum(inc_h[:i]):6,}, '
                  f'pending {s["queue"]["pending"]}, bar {s["queue"]["threshold"]}, k {s["queue"]["k"]}')
