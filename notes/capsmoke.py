"""Smoke runs of the stage-c cap (25 Nov 2026). capsmoke: six of X9's stage-c tasks, 5 verifiers, no searcher,
--cap-c 2 (output capsmoke.out). x10smoke: a copy of the X10 fork with the X10 command, 15 min at most
(x10smoke_cap3.out: 6 searchers, 5 verifiers, cap 3; x10smoke_cap2.out: 6 searchers, 4 verifiers, cap 2).

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" soup python3 /notes/capsmoke.py /data/<dir>

Reads logs/stats.jsonl: per tick, the workers whose heartbeat says stage c, and the live searchers and verifiers.
"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else '/data/capsmoke')
L = [json.loads(s) for s in open(d / 'logs' / 'stats.jsonl')]
print(f'{len(L)} ticks, {L[0]["ts"]} to {L[-1]["ts"]} ({L[-1]["elapsed_s"]:.0f} s)')
peak = 0
for x in L:
    c = sum(w.get('state') == 'stage c' and w['alive'] and not w['retiring'] for w in x['workers'])
    peak = max(peak, c)
    st = ' '.join(f"{w['name']}:{(w.get('state') or '-').replace(' ', '')}" for w in x['workers'] if w['alive'])
    print(f"{x['elapsed_s']:6.0f} s  avail {x.get('mem_available_mb') or '-':>5} MB  "
          f"search {x['n_search']}  verify {x['n_verify']}  stage c {c}  "
          f"pending {x['queue']['pending']} stage2c {x['queue']['stage2c']}  evals {x['evals_total']:,}  {st}"
          + (f"  | {x['rebalance']}" if 'rebalance' in x else ''))
live = [x for x in L if x['n_search'] + x['n_verify'] > 0]          # the last tick is after the workers stopped
avail = [x['mem_available_mb'] for x in L if x.get('mem_available_mb')]
print(f'peak stage-c tasks at a tick: {peak}; at the last live tick: {live[-1]["n_search"]} searchers, '
      f'{live[-1]["n_verify"]} verifiers, {live[-1]["evals_total"]:,} evaluations; '
      f'PSS max {max(x["mem_total"]["pss_mb"] for x in L):.0f} MB'
      + (f'; MemAvailable min {min(avail):,} MB' if avail else ''))
