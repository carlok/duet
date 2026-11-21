"""Verifier process: pulls theories from the queue and verifies them in stages (see soup.verify).

Lane 'pending' -> stages a and b, result written to results/<key>.json; claims still open after b
go to lane 'stage2c'. Lane 'stage2c' -> stage c, the result file is rewritten.
A verifier started with --prefer c takes stage-c work first (so long runs always progress).
"""
import argparse
import os
import random
import time

from ..core import Corpus, interrupt_all, set_memory_limit
from ..duality import dualities
from ..paths import data, ensure
from ..verify import stage_a, stage_b, stage_c
from .common import StopWatcher, heartbeat, read_json, write_json, memory
from .fqueue import FileQueue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True); ap.add_argument('--run', required=True)
    ap.add_argument('--prefer', default='ab', choices=['ab', 'c'])
    a = ap.parse_args()
    stop = StopWatcher(interrupt_all)
    set_memory_limit(int(os.environ.get('SOUP_Z3_MEMORY_MB', 1500)))
    C = Corpus(store=ensure('corpus')); Q = FileQueue(data('queue')); R = ensure('results')
    c_first, ab_first = ('stage2c', 'pending'), ('pending', 'stage2c')
    done = {'ab': 0, 'c': 0}; busy = 0.0; t_start = time.time()
    hb = lambda state, **kw: heartbeat(a.name, role='verify', run=a.run, prefer=a.prefer, state=state, done=done,
                                       busy_frac=round(busy / max(1e-9, time.time() - t_start), 3),
                                       corpus=len(C), mem=memory(os.getpid()), **kw)
    print(f'{a.name}: prefers {a.prefer}, corpus {len(C)} found structures', flush=True)
    claimed = None
    try:
        while not stop.set:
            C.refresh()
            # stage c first for the c verifier, and for the others with a probability that grows with the
            # stage-c backlog (10% per 10 waiting, at most 50%), so long runs never starve
            backlog = Q.counts()['stage2c'] if a.prefer != 'c' else 0
            lanes = c_first if a.prefer == 'c' or random.random() < min(0.5, backlog / 100) else ab_first
            got = Q.claim(a.name, lanes)
            if got is None:
                hb('idle'); time.sleep(2); continue
            claimed, task = got; key = task['key']; t0 = time.time()
            tag = f':{key}'
            if task['lane'] == 'pending':
                hb('stage a', key=key)
                out = stage_a(C, task['T'], tag=tag)
                hb('stage b', key=key)
                out = stage_b(C, out)
                done['ab'] += 1
            else:
                out = read_json(R / f'{key}.json')
                if out is None: Q.done(claimed); claimed = None; continue
                hb('stage c', key=key)
                out = stage_c(C, out, tag=tag)
                done['c'] += 1
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
    except KeyboardInterrupt:
        pass
    finally:
        if claimed is not None: Q.release(claimed)     # unfinished: back to its lane for someone else
        hb('stopped')
    print(f'{a.name}: stopped, done {done}', flush=True)


if __name__ == '__main__':
    main()
