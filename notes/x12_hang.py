"""Where verification stalled in X12 (deviation 13, found after the run).
- fusion5: verifiers v2 and v8 sat in stage a on one theory each for their last 7.3 and 5.2 hours.
- fusion6: four verifiers died with z3's out_of_memory_error (exit -6) about 70 minutes apart, each time with one task
  claimed, which went back to the queue.
Reruns stages a and b (stage a only with --a-only) on one theory with the given verifier config, on a private copy of
the arm's corpus, and prints the Python stack every N seconds (faulthandler), so the step that runs long shows up.

    podman run -i --rm -v "$PWD/work:/data:ro" -e SOUP_DATA=/data/x12-f5 soup timeout 1200 \
        python3 - 14,17,5027,17379,28801 300 [--dir x12-f5] [--cfg V7] [--a-only] < notes/x12_hang.py
"""
import argparse
import faulthandler
import json
import shutil
import time

from soup.core import Corpus, set_memory_limit
from soup.verify import stage_a, stage_b, CONFIGS, LAWS

ap = argparse.ArgumentParser()
ap.add_argument('T'); ap.add_argument('every', type=int, nargs='?', default=300)
ap.add_argument('--dir', default='x12-f5'); ap.add_argument('--cfg', default='V7'); ap.add_argument('--a-only', action='store_true')
a = ap.parse_args()
T = [int(x) for x in a.T.split(',')]
print('T', T, 'laws', [LAWS[t] for t in T], 'cfg', a.cfg, flush=True)
set_memory_limit(1500)                                     # as the stream verifier (SOUP_Z3_MEMORY_MB default)
shutil.copytree(f'/data/{a.dir}/corpus', '/tmp/corpus')
C = Corpus(store='/tmp/corpus')
print('corpus', len(C), flush=True)
faulthandler.dump_traceback_later(a.every, repeat=True)
cfg = CONFIGS[a.cfg]
t0 = time.time()
out = stage_a(C, T, cfg, tag=':diag')
print(f'stage a finished in {time.time() - t0:.1f} s', flush=True)
if not a.a_only:
    out = stage_b(C, out, cfg)
    print(f'stage b finished at {time.time() - t0:.1f} s', flush=True)
faulthandler.cancel_dump_traceback_later()
print('result:', json.dumps({k: out.get(k) for k in ('status', 'score', 'secs_a', 'secs_b', 'model_counts',
                                                     'independence_unconfirmed', 'claims')}, default=str)[:3000])
