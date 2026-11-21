"""T3 calibration: named two-operation theories against size-matched random theories.

    python -m soup.calib            env: CALIB_NULL (random theories per size, default 30), CALIB_SEED (11),
                                         CALIB_JOBS (6), CALIB_OUT (calib_t3.json), CALIB_TIMEOUT (3600 s)

Random theories: k distinct laws drawn uniformly from all 71,368 non-trivial laws, kept only if at least
one is a bridge and the base corpus has a non-degenerate model of them (same filter as the first session).
Every theory goes through verify (stages a+b, with E, verifier V1) on the shared corpus store.

Each theory runs in its own child process (python -m soup.calib --one, z3 capped at SOUP_Z3_MEMORY_MB,
E and Vampire at SOUP_PROVER_MEMORY_MB). A child that dies or overruns CALIB_TIMEOUT is recorded as
crashed and the run goes on (PREREGISTRATION.md, T3 deviation 2: the first run lost its process pool to one
OOM-killed worker). The run resumes: theories already in the output file are not run again.
"""
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

MODEL_FIRST_SIZES = (6,)   # uniform rejection sampling accepts 0 in 267,682 draws at k = 6 (PREREGISTRATION.md, deviation 1)


def model_first_theories(k, count, rng):
    """Pick a non-degenerate base structure uniformly, then k distinct laws it satisfies (>= 1 bridge)."""
    from .data import PM, unpack_laws
    nd = np.flatnonzero(NONDEG); out = []
    while len(out) < count:
        laws = np.flatnonzero(unpack_laws(PM[int(rng.choice(nd))]))
        laws = laws[laws > 0]
        if len(laws) < k or not BRIDGE[laws].any(): continue
        T = sorted(int(t) for t in rng.sample(list(laws), k))
        if any(BRIDGE[t] for t in T): out.append(T)
    return out


def random_theories(k, count, rng):
    if k in MODEL_FIRST_SIZES: return model_first_theories(k, count, rng)
    out = []
    while len(out) < count:
        T = sorted(rng.sample(range(1, NL), k))
        if not any(BRIDGE[t] for t in T): continue
        if not (unpack_probes(np.bitwise_and.reduce(LM[T], axis=0)) & NONDEG).any(): continue
        out.append(T)
    return out


def jobs(N, seed):
    """The preregistered job list (deterministic in N and seed): named theories, then random ones per size."""
    rng = random.Random(seed); js = []
    for name, ls in NAMED.items():
        T = [law_index(s) for s in ls]; assert None not in T, name
        js.append((name, 'named', sorted(T)))
    for k in sorted({len(T) for _, _, T in js}):
        js += [(f'random-{k}', 'null', T) for T in random_theories(k, N, rng)]
    return js


def job_key(name, kind, T): return f"{kind}:{name}:{','.join(map(str, sorted(T)))}"


def sampler(kind, T):
    if kind != 'null': return None
    return 'model-first' if len(T) in MODEL_FIRST_SIZES else 'uniform'


def pending(js, done):
    """Jobs whose result is not yet in the output (resume)."""
    have = {job_key(r['name'], r['kind'], r['T']) for r in done}
    return [j for j in js if job_key(*j) not in have]


RESULT = 'CALIB-RESULT '


def run_one(job, cmd=None, timeout=3600):
    """Verify one theory in a child process. Returns its result, or a 'crashed' record."""
    name, kind, T = job
    cmd = cmd or [sys.executable, '-m', 'soup.calib', '--one']
    t0 = time.time()
    try:
        p = subprocess.run(cmd, input=json.dumps(job), capture_output=True, text=True, timeout=timeout)
        lines = [l for l in p.stdout.splitlines() if l.startswith(RESULT)]
        if p.returncode == 0 and lines:
            return json.loads(lines[-1][len(RESULT):])
        why = f'exit code {p.returncode}'; tail = p.stderr[-2000:]
    except subprocess.TimeoutExpired:
        why = f'timeout after {timeout} s'; tail = ''
    return {'name': name, 'kind': kind, 'T': sorted(T), 'status': 'crashed', 'why': why, 'stderr_tail': tail,
            'dualities': dualities(T), 'score': None, 'secs_total': round(time.time() - t0, 1)}


def child():
    """--one: read a job on stdin, verify it with V1, print the result on one line."""
    from .core import Corpus, set_memory_limit
    from .verify import verify, V1
    set_memory_limit(int(os.environ.get('SOUP_Z3_MEMORY_MB', 1500)))
    name, kind, T = json.loads(sys.stdin.read())
    C = Corpus(store=ensure('corpus'))
    t0 = time.time(); r = verify(C, T, V1)
    r.update(name=name, kind=kind, dualities=dualities(T), secs_total=round(time.time() - t0, 1))
    print(RESULT + json.dumps(r, ensure_ascii=False, default=int), flush=True)


def main():
    if '--one' in sys.argv: return child()
    N = int(os.environ.get('CALIB_NULL', 30)); seed = int(os.environ.get('CALIB_SEED', 11))
    out = data(os.environ.get('CALIB_OUT', 'calib_t3.json'))
    res = json.load(open(out)) if out.exists() else []
    todo = pending(jobs(N, seed), res)
    print(f'{len(res)} results on file, {len(todo)} to run', flush=True)
    timeout = float(os.environ.get('CALIB_TIMEOUT', 3600))
    with ThreadPoolExecutor(int(os.environ.get('CALIB_JOBS', 6))) as ex:
        futs = [ex.submit(run_one, j, None, timeout) for j in todo]
        for f in as_completed(futs):      # write as each finishes: a slow theory blocks nothing
            r = f.result()
            r['sampler'] = sampler(r['kind'], r['T'])
            res.append(r)
            tmp = out.with_name(f'.{out.name}.tmp'); json.dump(res, open(tmp, 'w'), ensure_ascii=False, default=int)
            os.replace(tmp, out)
            print(json.dumps({k: r.get(k) for k in ('name', 'status', 'score', 'gain', 'max_difficulty', 'richness',
                                                    'dualities', 'secs_total')}, ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
