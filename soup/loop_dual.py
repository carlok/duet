"""v2 search: rounds of (cheap MAP-Elites surrogate on the growing corpus) -> (verify top elites)."""
"""Superseded by soup.stream (T1); kept to reproduce the batch-round runs in results-cloud/."""
import sys, random, pickle, json, time, math
import numpy as np
from .verify import Corpus, verify, BRIDGE, LAWS, ORDER, NL, LEGACY
from .duality import dualities, image
from .core import TREES
from .paths import data
def _ops(t): return set() if t[0] == 'v' else {t[0]} | _ops(t[1]) | _ops(t[2])
def _vars(t): return {t[1]} if t[0] == 'v' else _vars(t[1]) | _vars(t[2])
def _definitional(L, R):
    # one side is the bare operation on two distinct variables, the other a term in the other operation alone
    for a, b in ((L, R), (R, L)):
        if a[0] in 'fg' and a[1][0] == 'v' and a[2][0] == 'v' and a[1] != a[2]:
            other = 'g' if a[0] == 'f' else 'f'
            if _ops(b) <= {other} and _vars(b) <= _vars(a): return True
    return False
DEFN = np.array([_definitional(L, R) for L, R in TREES])

random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 1500
W = {0: 0, 1: 1.0, 2: 0.5, 3: 0.1, 4: 0.0}
by_order = {o: [i for i in range(NL) if ORDER[i] == o] for o in range(1, 5)}
def rand_law():
    return random.choice(by_order[random.choices([1, 2, 3, 4], weights=[1, 3, 6, 10])[0]])
C = Corpus(); verified = {}; t_start = time.time(); rnd = 0
single_cache = {}
def imp1(t):
    if t not in single_cache: single_cache[t] = C.implied([t])
    return single_cache[t]
def surrogate(T):
    T = sorted(set(T))
    if len(T) < 2: return None
    m, nd, sizes = C.stats(T)
    if m < 5 or not nd or len(sizes) < 2: return None
    imp = C.implied(T)
    single = np.zeros(NL, bool)
    for t in T:
        s = imp1(t)
        if s is not None: single |= s
    if (imp & DEFN).any(): return None   # one operation is a term in the other: not a real fusion
    fg = np.flatnonzero(imp & ~single)
    if not len(fg): return None
    du = dualities(T)
    score = sum(W[ORDER[e]] for e in fg) / (1 + sum(ORDER[t] for t in T)) * (1 + len(du))
    nb = int(sum(BRIDGE[t] for t in T))
    return {'T': T, 'score': score, 'desc': (len(T), len(du), nb, min(4, int(math.log2(m)) // 2), int(min(ORDER[e] for e in fg)))}
while time.time() - t_start < BUDGET:
    rnd += 1; archive = {}; t0 = time.time(); evals = 0
    for r in verified.values():   # verified elites seed the next round
        s = surrogate(r['T'])
        if s: archive[s['desc']] = s
    while time.time() - t0 < 90:
        if len(archive) < 20 or random.random() < 0.1: T = [rand_law(), rand_law()]
        else:
            a = random.choice(list(archive.values()))['T']; u = random.random()
            if u < 0.25:
                sw, op = random.choice([(1, 0), (0, 1), (1, 1)]); T = sorted(set(a) | {image(t, sw, op) for t in a})
                if len(T) > 6: continue
            elif u < 0.5: T = list(a); T[random.randrange(len(T))] = rand_law()
            elif u < 0.65: T = list(a) + [rand_law()] if len(a) < 6 else [t for t in a if t != random.choice(a)]
            else:
                b = random.choice(list(archive.values()))['T']
                T = list({random.choice(a), random.choice(b)} | ({random.choice(b)} if random.random() < 0.5 else set()))
        s = surrogate(T); evals += 1
        if s and (s['desc'] not in archive or s['score'] > archive[s['desc']]['score']): archive[s['desc']] = s
    cands = sorted([s for s in archive.values() if tuple(s['T']) not in verified and any(BRIDGE[t] for t in s['T'])], key=lambda s: -s['score'])[:12]
    before = len(C.extra)
    for s in cands:
        r = verify(C, s['T'], LEGACY); r['dualities'] = dualities(s['T']); r['round'] = rnd; r['surrogate'] = s['score']; verified[tuple(s['T'])] = r
        print(json.dumps({'round': rnd, 'dualities': r['dualities'], 'score': r['score'], 'laws': r['laws'], 'claims': r.get('claims', []), 'open': r.get('open', [])}, ensure_ascii=False), flush=True)
        if time.time() - t_start > BUDGET: break
    single_cache.clear()
    print(f'# round {rnd}: {evals} surrogate evaluations, archive {len(archive)}, verified {len(cands)}, corpus +{len(C.extra) - before} structures (total extra {len(C.extra)})', flush=True)
    pickle.dump({'verified': verified, 'extra': [(e[0], e[1], e[2], e[3]) for e in C.extra]}, open(data(f'loopdual_{sys.argv[2] if len(sys.argv) > 2 else 3}.pkl'), 'wb'))
print('done', flush=True)
