"""Search process: continuous MAP-Elites over theories, scored by a cheap surrogate on the shared corpus.

Every theory that wins or improves an archive cell (and has a bridge law) is pushed at once to the
verification queue. Verified scores flow back from results/ and replace the cheap score of the elite.

Arms: 'prior' (duality-closure mutation, score bonus per duality) or 'noprior' (same filters and law cap,
no duality operator, no duality bonus). Elites are only shared within an arm.
"""
import argparse
import math
import os
import random
import time

import numpy as np

from ..core import Corpus, LAWS, ORDER, NL, TREES
from ..duality import dualities, image, theory_key, canonical
from ..paths import data, ensure
from ..verify import BRIDGE
from .common import StopFlag, heartbeat, read_json, write_json, memory
from .fqueue import FileQueue

MAX_LAWS = 6
W = {0: 0, 1: 1.0, 2: 0.5, 3: 0.1, 4: 0.0}


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


def drop_one(a, rng):
    """Remove exactly one law (drawn once; until 21 Nov 2026 the draw sat inside the comprehension and
    removed a random number of laws)."""
    drop = rng.choice(a)
    return [t for t in a if t != drop]
BY_ORDER = {o: np.flatnonzero(ORDER == o) for o in range(1, 5)}


class Searcher:
    def __init__(self, name, seed, arm, run):
        self.name, self.arm, self.run = name, arm, run
        self.prior = arm == 'prior'
        self.rng = random.Random(seed)
        self.C = Corpus(store=ensure('corpus'))
        self.Q = FileQueue(data('queue'))
        self.results_dir = ensure('results')
        self.archive = {}           # desc -> elite {T, key, cheap, desc, verified}
        self.where = {}             # key -> desc of the elite holding it
        self.verified = {}          # key -> verified score (this arm)
        self.ratio = [0.0, 0.0]     # sums of verified and cheap scores: calibrates cheap -> verified scale
        self.seen_results = {}      # result file -> mtime when last read
        self.pushed_laws = set()
        self.single = {}
        self.evals = self.pushed = self.wins = self.held = 0
        self.gate = {'k': 1.0, 'threshold': 0.0}   # from the supervisor (queue/gate.json)

    # ---- cheap surrogate
    def imp1(self, t):
        if t not in self.single: self.single[t] = self.C.implied([t])
        return self.single[t]

    def surrogate(self, T):
        T = sorted(set(T))
        if len(T) < 2: return None
        m, nd, sizes = self.C.stats(T)
        if m < 5 or not nd or len(sizes) < 2: return None
        imp = self.C.implied(T)
        if (imp & DEFN).any(): return None       # one operation is a term in the other: not a real fusion
        single = np.zeros(NL, bool)
        for t in T:
            s = self.imp1(t)
            if s is not None: single |= s
        fg = np.flatnonzero(imp & ~single)
        if not len(fg): return None
        du = dualities(T)
        score = sum(W[ORDER[e]] for e in fg) / (1 + sum(ORDER[t] for t in T)) * ((1 + len(du)) if self.prior else 1)
        nb = int(sum(BRIDGE[t] for t in T))
        desc = (len(T), len(du), nb, min(4, int(math.log2(m)) // 2), int(min(ORDER[e] for e in fg)))
        return {'T': T, 'cheap': score, 'desc': desc, 'dualities': du, 'n_gain': int(len(fg))}

    def k(self):
        v, c = self.ratio
        return v / c if c > 0 and len(self.verified) >= 5 else 1.0

    def eff(self, e):
        v = self.verified.get(e['key'])
        return v if v is not None else self.k() * e['cheap']

    # ---- archive
    def insert(self, s, push=True):
        key = theory_key(s['T']); s['key'] = key
        cell = self.archive.get(s['desc'])
        if cell is not None and (cell['key'] == key or self.eff(s) <= self.eff(cell)): return False
        if cell is not None: self.where.pop(cell['key'], None)
        old = self.where.get(key)
        if old is not None and old != s['desc']: self.archive.pop(old, None)
        self.archive[s['desc']] = s; self.where[key] = s['desc']; self.wins += 1
        if push and any(BRIDGE[t] for t in s['T']) and key not in self.verified:
            novelty = sum(t not in self.pushed_laws for t in s['T']) / len(s['T'])
            prio = s['cheap'] * (1 + novelty)      # raw (cheap scale); the supervisor rescales with k
            # gate: only theories whose calibrated priority could reach the current top 20 enter the queue;
            # the others stay in the archive (not marked seen) and are pushed if they improve later
            if self.gate['k'] * prio < self.gate['threshold']:
                self.held += 1; return True
            if not self.Q.mark_seen(key): return True
            self.Q.push(key, {'T': list(canonical(s['T'])), 'cheap': s['cheap'], 'desc': list(s['desc']),
                              'novelty': novelty, 'arm': self.arm, 'run': self.run, 'searcher': self.name,
                              't_pushed': time.time()}, prio)
            self.pushed_laws |= set(s['T']); self.pushed += 1
        return True

    def rescore(self):
        """The corpus grew: cheap scores and descriptors may have changed (claims refuted)."""
        self.single.clear()
        old = list(self.archive.values()); self.archive.clear(); self.where.clear()
        for e in old:
            s = self.surrogate(e['T'])
            if s is None:
                if self.verified.get(e['key'], 0) > 0: s = e          # verified and positive: keep
                else: continue
            self.insert(s, push=False)

    def ingest_results(self):
        for e in os.scandir(self.results_dir):
            if not e.name.endswith('.json') or e.name.startswith('.'): continue
            mt = e.stat().st_mtime
            if self.seen_results.get(e.name, 0) >= mt: continue       # unchanged since last read
            r = read_json(e.path)
            if r is None or r.get('stage') not in ('b', 'c'): continue
            self.seen_results[e.name] = mt
            if r.get('arm') != self.arm: continue
            key = r['key']; prev = self.verified.get(key)
            self.verified[key] = r.get('score', 0.0)
            if prev is None and r.get('cheap'):
                self.ratio[0] += r.get('score', 0.0); self.ratio[1] += r['cheap']
            if key in self.where:      # our elite: its verified score now stands in for the cheap one
                continue
            if r.get('score', 0) > 0:  # elites of other searchers of the same arm migrate in
                s = self.surrogate(r['T'])
                if s: self.insert(s, push=False)

    # ---- mutation
    def rand_law(self):
        o = self.rng.choices([1, 2, 3, 4], weights=[1, 3, 6, 10])[0]
        return int(self.rng.choice(BY_ORDER[o]))

    def propose(self):
        rng = self.rng
        if len(self.archive) < 20 or rng.random() < 0.1: return [self.rand_law(), self.rand_law()]
        elites = list(self.archive.values())
        a = rng.choice(elites)['T']; u = rng.random()
        if u < 0.25 and self.prior:
            sw, op = rng.choice([(1, 0), (0, 1), (1, 1)])
            T = sorted(set(a) | {image(t, sw, op) for t in a})
            return T if len(T) <= MAX_LAWS else None
        if u < 0.5:
            T = list(a); T[rng.randrange(len(T))] = self.rand_law(); return T
        if u < 0.65:
            return list(a) + [self.rand_law()] if len(a) < MAX_LAWS else drop_one(a, rng)
        b = rng.choice(elites)['T']
        return list({rng.choice(a), rng.choice(b)} | ({rng.choice(b)} if rng.random() < 0.5 else set()))

    def maintenance(self, t_start):
        g = read_json(data('queue', 'gate.json'))
        if g and g.get('arm') == self.arm: self.gate = g
        new = self.C.refresh()
        if new: self.rescore()
        self.ingest_results()
        heartbeat(self.name, role='search', arm=self.arm, run=self.run, state='searching',
                  evals=self.evals, evals_per_s=round(self.evals / max(1e-9, time.time() - t_start), 1),
                  archive=len(self.archive), wins=self.wins, pushed=self.pushed, held=self.held, gate=self.gate.get('threshold'), corpus=len(self.C),
                  verified_seen=len(self.verified), k=round(self.k(), 4), mem=memory(os.getpid()))

    def snapshot(self):
        ensure('runs', self.run)
        write_json(data('runs', self.run, f'archive_{self.name}.json'),
                   {'name': self.name, 'arm': self.arm, 'evals': self.evals, 'pushed': self.pushed,
                    'elites': [{'T': e['T'], 'key': e['key'], 'cheap': e['cheap'], 'desc': list(e['desc']),
                                'verified': self.verified.get(e['key'])} for e in self.archive.values()]})

    def loop(self, budget, every=20.0):
        stop = StopFlag()
        t_start = time.time(); t_maint = 0.0; t_snap = time.time()
        while not stop.set and time.time() - t_start < budget:
            if time.time() - t_maint > every:
                self.maintenance(t_start); t_maint = time.time()
            if time.time() - t_snap > 300: self.snapshot(); t_snap = time.time()
            T = self.propose()
            if not T or len(set(T)) < 2: continue
            s = self.surrogate(T); self.evals += 1
            if s: self.insert(s)
        self.maintenance(t_start); self.snapshot()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True); ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--arm', default='prior', choices=['prior', 'noprior'])
    ap.add_argument('--run', required=True); ap.add_argument('--budget', type=float, default=1e9)
    a = ap.parse_args()
    s = Searcher(a.name, a.seed, a.arm, a.run)
    print(f'{a.name}: seed {a.seed}, arm {a.arm}, corpus {len(s.C)} found structures', flush=True)
    s.loop(a.budget)
    print(f'{a.name}: done, {s.evals} evaluations, {s.pushed} pushed, archive {len(s.archive)}', flush=True)


if __name__ == '__main__':
    main()
