"""T3 calibration: named two-operation theories against size-matched random theories.

    python -m soup.calib            env: CALIB_NULL (random theories per size, default 30), CALIB_SEED (11),
                                         CALIB_JOBS (10), CALIB_OUT (calib_t3.json)

Random theories: k distinct laws drawn uniformly from all 71,368 non-trivial laws, kept only if at least
one is a bridge and the base corpus has a non-degenerate model of them (same filter as the first session).
Every theory goes through verify (stages a+b, with E) on the shared corpus store.
"""
import json
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .data import NONDEG, unpack_probes, LM, NL
from .duality import dualities
from .named import law_index, NAMED as BASE_NAMED
from .paths import data, ensure
from .verify import BRIDGE

NAMED = dict(BASE_NAMED)
NAMED.update({
    'bisemilattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·y = y·x', 'x∘y = y∘x', 'x·x = x', 'x∘x = x'],
    'right absorption pair': ['x·(y∘x) = x', 'x∘(y·x) = x'],
    'idempotent left quasigroup': ['x·(x∘y) = y', 'x∘(x·y) = y', 'x·x = x'],
    'idempotent right quasigroup': ['(x·y)∘y = x', '(x∘y)·y = x', 'x·x = x'],
})

_C = None


def _verify(job):
    global _C
    from .core import Corpus
    from .verify import verify
    if _C is None: _C = Corpus(store=ensure('corpus'))
    _C.refresh()
    name, kind, T = job
    t0 = time.time(); r = verify(_C, T)
    r.update(name=name, kind=kind, dualities=dualities(T), secs_total=round(time.time() - t0, 1))
    return r


def random_theories(k, count, rng):
    out = []
    while len(out) < count:
        T = sorted(rng.sample(range(1, NL), k))
        if not any(BRIDGE[t] for t in T): continue
        if not (unpack_probes(np.bitwise_and.reduce(LM[T], axis=0)) & NONDEG).any(): continue
        out.append(T)
    return out


def main():
    N = int(os.environ.get('CALIB_NULL', 30)); rng = random.Random(int(os.environ.get('CALIB_SEED', 11)))
    jobs = []
    for name, ls in NAMED.items():
        T = [law_index(s) for s in ls]; assert None not in T, name
        jobs.append((name, 'named', sorted(T)))
    for k in sorted({len(T) for _, _, T in jobs}):
        jobs += [(f'random-{k}', 'null', T) for T in random_theories(k, N, rng)]
    out = data(os.environ.get('CALIB_OUT', 'calib_t3.json'))
    res = []
    with ProcessPoolExecutor(int(os.environ.get('CALIB_JOBS', 10))) as ex:
        for r in ex.map(_verify, jobs):
            res.append(r); json.dump(res, open(out, 'w'), ensure_ascii=False, default=int)
            print(json.dumps({k: r.get(k) for k in ('name', 'score', 'gain', 'max_difficulty', 'richness', 'dualities', 'secs_total')},
                             ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
