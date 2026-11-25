"""Evaluations per searcher-hour in a smoke run (25 Nov 2026), from its logs/stats.jsonl, measured the same way as
the cap-2 smoke in x10smoke_cap2.out: from the first tick with evaluations to the last tick with live workers,
divided by the live searchers. Also the new results (the fork holds 156 copied ones) and each searcher's evals.

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" soup python3 /notes/smoke_rate.py /data/<dir> [copied]
"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1]); copied = int(sys.argv[2]) if len(sys.argv) > 2 else 156
L = [json.loads(s) for s in open(d / 'logs' / 'stats.jsonl')]
live = [x for x in L if x['n_search'] + x['n_verify'] > 0]
first = next(x for x in live if x['evals_total'] > 0)
last = live[-1]
dt = last['elapsed_s'] - first['elapsed_s']
ns = sorted({x['n_search'] for x in live if x['elapsed_s'] >= first['elapsed_s']})
rate = (last['evals_total'] - first['evals_total']) / dt / last['n_search'] * 3600
avail = [x['mem_available_mb'] for x in L if x.get('mem_available_mb')]
peak_c = max(sum(w.get('state') == 'stage c' and w['alive'] and not w['retiring'] for w in x['workers']) for x in L)
print(f'{d.name}: evaluations {first["evals_total"]:,} at {first["elapsed_s"]:.0f} s -> {last["evals_total"]:,} at '
      f'{last["elapsed_s"]:.0f} s, searchers {ns}: {rate / 1e6:.3f}M per searcher-hour')
print(f'peak stage-c tasks at a tick {peak_c}; MemAvailable min {min(avail):,} MB; '
      f'new results {len(list((d / "results").glob("*.json"))) - copied}; queue at the end {last["queue"]}')
for a in sorted((d / 'runs').glob('*/archive_s*.json')):
    print(f'  {a.parent.name}/{a.name}: evals {json.load(open(a)).get("evals", 0):,}')
