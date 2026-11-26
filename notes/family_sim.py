"""Offline prototype of arm fusion6 (family pressure) against fusion5 (26 Nov 2026). No run, no verification.

    podman run -i --rm -v "$PWD/work:/data" -e SOUP_DATA=/data/famsim soup python3 - <arm> <seed> <N> < notes/family_sim.py

One searcher of the given arm makes N proposals on famsim's corpus (a fork of x10's, deleted afterwards). Its queue is a
stub that records pushes and writes nothing, and the corpus store is detached, so Mace4's countermodels stay in memory.
There is no maintenance: no corpus refresh, no verified scores, no gate. Every push is kept with its priority.
Output: one JSON line. TOP is about what a run's verifiers reach (x10b verified 555 theories in 7.4 h).
- families among the archive elites and the pushes;
- for the TOP pushes by the arm's own priority: distinct families, the largest family's share, the effective number
  exp(H), the mean cheap score, and how many have a family F1 has never seen among structured theories
  (/data/check/families.json).
"""
import collections
import json
import math
import sys
import time

from soup.stream.searcher import Searcher
from soup.taxonomy import family_of

arm, seed, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
TOP = 500


class StubQueue:
    def __init__(self): self.items, self.seen = [], set()
    def mark_seen(self, k):
        if k in self.seen: return False
        self.seen.add(k); return True
    def push(self, key, item, prio): self.items.append((prio, key, item))


t0 = time.time()
S = Searcher(f'sim{seed}', seed, arm, 'famsim')
S.Q = StubQueue(); S.C.store = None
t_ready = time.time() - t0
t0 = time.time()
while S.evals < N:
    T = S.propose()
    if not T or len(set(T)) < 2: continue
    s = S.surrogate(T); S.evals += 1
    if s: S.insert(s)
secs = time.time() - t0

fam = lambda T: family_of(S.C.implied(T))
F1 = {t['family'] for t in json.load(open('/data/check/families.json'))['theories'] if t['primary'] == 'structured'}


def spread(labels):
    c = collections.Counter(labels); n = sum(c.values())
    H = -sum(v / n * math.log(v / n) for v in c.values()) if n else 0.0
    return {'n': n, 'distinct': len(c), 'largest_share': round(max(c.values()) / n, 3) if n else None,
            'effective': round(math.exp(H), 1), 'top3': c.most_common(3)}


pushes = sorted(S.Q.items, key=lambda x: -x[0])
plab = [x[2].get('family') or fam(x[2]['T']) for x in pushes]
top = pushes[:TOP]; tlab = plab[:TOP]
print(json.dumps({
    'arm': arm, 'seed': seed, 'evals': S.evals, 'secs': round(secs), 'evals_per_s': round(S.evals / secs, 1),
    'ready_s': round(t_ready), 'corpus_end': len(S.C), 'par_skipped': S.par_skipped,
    'archive': len(S.archive), 'archive_families': len({fam(e['T']) for e in S.archive.values()}),
    'pushes': spread(plab), 'top': spread(tlab),
    'top_mean_cheap': round(sum(x[2]['cheap'] for x in top) / max(1, len(top)), 3),
    'top_new_to_F1': sum(l not in F1 for l in tlab), 'top_new_to_F1_families': len({l for l in tlab if l not in F1}),
    'pushes_new_to_F1_families': len({l for l in plab if l not in F1})}, ensure_ascii=False))
