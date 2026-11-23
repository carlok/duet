"""How much of the theory space the searches have touched (22 Nov 2026).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/coverage.py

Counts, per data directory: verified theories (results/*.json), theories pushed to the verification queue
(queue/seen, deduplicated up to the three dualities), and cheap surrogate evaluations (the largest `evals_total`
per run in logs/stats.jsonl; repeats of one theory are counted again, so this bounds the distinct theories scored
from above). Compares them with the number of law sets the search can form: 1 to 6 laws (searcher.MAX_LAWS) out of
71,369 two-operation laws of order <= 4. Law sets overcount varieties (many are equivalent or trivial); how many
distinct varieties there are is not known.
"""
import glob
import json
import math
import os

DIRS = ['.', 't4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6']
L, MAX_LAWS = 71369, 6
tv = tq = te = 0
for d in DIRS:
    base = os.path.join('/data', d)
    v = len(glob.glob(os.path.join(base, 'results', '*.json')))
    q = len(os.listdir(os.path.join(base, 'queue', 'seen'))) if os.path.isdir(os.path.join(base, 'queue', 'seen')) else 0
    per_run = {}
    p = os.path.join(base, 'logs', 'stats.jsonl')
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            e = r.get('search', {}).get('evals_total') if isinstance(r.get('search'), dict) else r.get('evals_total')
            if e is None:
                for val in r.values():
                    if isinstance(val, dict) and 'evals_total' in val:
                        e = val['evals_total']
            if e is not None:
                per_run[r.get('run')] = max(per_run.get(r.get('run'), 0), e)
    e = sum(per_run.values())
    print(f'{d:11s} verified {v:6d}  queued {q:6d}  evaluations {e:11,d}  runs {sorted(map(str, per_run))}')
    tv, tq, te = tv + v, tq + q, te + e
print(f'{"total":11s} verified {tv:6d}  queued {tq:6d}  evaluations {te:11,d}')
for k in range(1, MAX_LAWS + 1):
    print(f'law sets of size {k}: {math.comb(L, k):.3e}')
allsets = sum(math.comb(L, k) for k in range(1, MAX_LAWS + 1))
print(f'law sets of size 1..{MAX_LAWS}: {allsets:.3e}; evaluations / sets = {te / allsets:.1e}; '
      f'verified / pairs alone = {tv / math.comb(L, 2):.1e}')
