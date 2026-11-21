"""Calibration: score named two-operation theories against size-matched random theories."""
import sys, random, pickle, json, time
sys.path.insert(0, '/home/claude/soup')
import numpy as np
from v2 import *
from named import parse, law_index
from soup import NONDEG, unpack_probes, LM
from duality import dualities
import os
random.seed(int(os.environ.get('CALIB_SEED', '7')))
NAMED = {
  'lattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·y = y·x', 'x∘y = y∘x', 'x·(x∘y) = x', 'x∘(x·y) = x'],
  'skew lattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·(x∘y) = x', '(y∘x)·x = x', 'x∘(x·y) = x', '(y·x)∘x = x'],
  'dimonoid': ['(x·y)·z = x·(y·z)', '(x·y)·z = x·(y∘z)', '(x∘y)·z = x∘(y·z)', '(x·y)∘z = x∘(y∘z)', '(x∘y)∘z = x∘(y∘z)'],
  'absorption pair': ['x·(x∘y) = x', 'x∘(x·y) = x'],
  'left quasigroup': ['x·(x∘y) = y', 'x∘(x·y) = y'],
  'right quasigroup': ['(x·y)∘y = x', '(x∘y)·y = x'],
}
C = Corpus(); results = []
def log(r):
    results.append(r); pickle.dump(results, open(os.environ.get('CALIB_OUT', 'calib_results.pkl'), 'wb'))
    print(json.dumps({k: r.get(k) for k in ('name', 'score', 'gain', 'max_difficulty', 'richness', 'dualities')}, ensure_ascii=False), flush=True)
for name, ls in NAMED.items():
    T = [law_index(s) for s in ls]; assert None not in T, name
    t0 = time.time(); r = verify(C, T); r['dualities'] = dualities(T); r['name'] = name; r['kind'] = 'named'; r['secs'] = round(time.time() - t0, 1); log(r)
# null: random theories of the same sizes, with at least one bridge law and a non-degenerate corpus model
N = int(os.environ.get('CALIB_NULL', '15'))
by_size = {2: 2 * N, 5: N, 6: N}
for k, count in by_size.items():
    got = 0
    while got < count:
        T = sorted(random.sample(range(1, NL), k))
        if not any(BRIDGE[t] for t in T): continue
        s = unpack_probes(np.bitwise_and.reduce(LM[T], axis=0))
        if not (s & NONDEG).any(): continue
        t0 = time.time(); r = verify(C, T); r['dualities'] = dualities(T); r['name'] = f'random-{k}'; r['kind'] = 'null'; r['secs'] = round(time.time() - t0, 1); log(r); got += 1
pickle.dump([(e[0], e[1], e[2], e[3]) for e in C.extra], open('calib_corpus_extra.pkl', 'wb'))
print('done', flush=True)
