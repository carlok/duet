"""Verifier process: pulls theories from the queue and verifies them in stages (see soup.verify).

Lane 'pending' -> stages a and b, result written to results/<key>.json; claims still open after b
go to lane 'stage2c'. Lane 'stage2c' -> stage c, the result file is rewritten.
A verifier started with --prefer c takes stage-c work first (so long runs always progress).
--cap-c N: at most N stage-c tasks run at once over all verifiers (FileQueue.claim with caps).
"""
import argparse
import os
import sys
import time

from ..core import Corpus, interrupt_all, set_memory_limit
from ..duality import dualities
from ..paths import data, ensure
from ..verify import stage_a, stage_b, stage_c, CONFIGS
from .common import StopWatcher, heartbeat, read_json, write_json, memory
from .fqueue import FileQueue

RECYCLE_RC = 75       # exit code of a verifier that stops itself to free memory; the supervisor restarts it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True); ap.add_argument('--run', required=True)
    ap.add_argument('--prefer', default='ab', choices=['ab', 'c'])
    ap.add_argument('--max-c', type=int, default=2,
                    help='non-c verifiers take stage c first while fewer than this many run it (a floor, not a cap)')
    ap.add_argument('--cap-c', type=int, default=0,
                    help='never more than this many stage-c tasks at once, over all verifiers (0: no cap, as before X9)')
    a = ap.parse_args()
    caps = {'stage2c': a.cap_c} if a.cap_c > 0 else None
    cfg_name = os.environ.get('SOUP_VERIFIER', 'DEFAULTS'); cfg = CONFIGS[cfg_name]
    stop = StopWatcher(interrupt_all)
    set_memory_limit(int(os.environ.get('SOUP_Z3_MEMORY_MB', 1500)))
    C = Corpus(store=ensure('corpus')); Q = FileQueue(data('queue')); R = ensure('results')
    c_first, ab_first = ('stage2c', 'pending'), ('pending', 'stage2c')
    done = {'ab': 0, 'c': 0}; busy = 0.0; t_start = time.time()
    hb = lambda state, **kw: heartbeat(a.name, role='verify', run=a.run, prefer=a.prefer, state=state, done=done,
                                       busy_frac=round(busy / max(1e-9, time.time() - t_start), 3),
                                       corpus=len(C), mem=memory(os.getpid()), **kw)
    print(f'{a.name}: prefers {a.prefer}, corpus {len(C)} found structures', flush=True)
    # SOUP_VERIFIER_RECYCLE_MB > 0: after a finished task, exit if private memory exceeds it (0: never; X8 on)
    recycle_mb = int(os.environ.get('SOUP_VERIFIER_RECYCLE_MB', 0)); recycled = False
    claimed = None
    try:
        while not stop.set:
            C.refresh()
            # stage c first for the c verifier; the others help with the stage-c backlog first only while fewer
            # than --max-c verifiers are on stage c (stage c runs for minutes per theory). With nothing pending
            # they fall through to stage c, and only --cap-c stops them: six at once tripped X9's memory rule.
            # A verifier the cap turns away with nothing pending goes idle, and the rebalancer can make it a searcher.
            lanes = c_first if a.prefer == 'c' or Q.running('stage2c') < a.max_c else ab_first
            got = Q.claim(a.name, lanes, caps)
            if got is None:
                hb('idle'); time.sleep(2); continue
            claimed, task = got; key = task['key']; t0 = time.time()
            tag = f':{key}'
            if task['lane'] == 'pending':
                hb('stage a', key=key)
                out = stage_a(C, task['T'], cfg, tag=tag)
                hb('stage b', key=key)
                out = stage_b(C, out, cfg)
                done['ab'] += 1
            else:
                out = read_json(R / f'{key}.json')
                if out is None: Q.done(claimed); claimed = None; continue
                hb('stage c', key=key)
                out = stage_c(C, out, cfg, tag=tag)
                done['c'] += 1
            out.update(verifier_cfg=cfg_name)
            out.update(key=key, arm=task.get('arm'), run_pushed=task.get('run'), run=a.run, cheap=task.get('cheap'),
                       prio=task.get('prio'), novelty=task.get('novelty'), desc=task.get('desc'),
                       searcher=task.get('searcher'), t_pushed=task.get('t_pushed'), t_done=time.time(),
                       verifier=a.name, dualities=dualities(out['T']))
            out.setdefault('secs', {})[out['stage']] = round(time.time() - t0, 1)
            write_json(R / f'{key}.json', out)
            if out['stage'] == 'b' and any(c['status'] == 'unknown' for c in out.get('claims', [])):
                Q.push(key, dict(task, t_pushed=time.time()), task.get('prio', 0), lane='stage2c')
            Q.done(claimed); claimed = None; busy += time.time() - t0
            hb('wrote', key=key)
            if recycle_mb:                 # memory grows over many verifications (X6, X7): restart between tasks
                m = memory(os.getpid()) or {}
                if (m.get('private_mb') or 0) > recycle_mb:
                    print(f"{a.name}: private memory {m['private_mb']:.0f} MB > {recycle_mb} MB: recycling", flush=True)
                    recycled = True; break
    except KeyboardInterrupt:
        pass
    finally:
        if claimed is not None: Q.release(claimed)     # unfinished: back to its lane for someone else
        hb('recycled' if recycled else 'stopped')
    print(f'{a.name}: stopped, done {done}', flush=True)
    if recycled: sys.exit(RECYCLE_RC)


if __name__ == '__main__':
    main()
