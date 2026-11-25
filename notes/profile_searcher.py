"""Why the searchers slowed down (25 Nov 2026): X10's smoke run made 0.28M evaluations per searcher-hour on X9's
corpus, against about 0.72M in X8 + x8b.

    record:  SOUP_DATA=/data/prof_x9 python3 /notes/profile_searcher.py record 40000 1401
    replay:  SOUP_DATA=/data/prof_<c> python3 /notes/profile_searcher.py replay
    outputs: SOUP_DATA=/data/prof_<c> python3 /notes/profile_searcher.py outputs /data/<file>.json

record runs one fusion4 searcher (seed, N proposals, its archive grows as in a run) and saves the proposals.
replay times surrogate() on exactly those proposals with the corpus of its data dir, under cProfile, and prints
the time per evaluation, the top functions and the number of corpus models per implied() call. The prof_* dirs
link the matrix files and a corpus and copy x10's known library and seen-before keys, so only the corpus differs.
"""
import cProfile
import io
import json
import pstats
import sys
import time

import numpy as np

from soup.paths import data
from soup.stream.searcher import Searcher

cmd = sys.argv[1]
t0 = time.time()
S = Searcher('prof', int(sys.argv[3]) if cmd == 'record' else 1401, 'fusion4', 'prof')
print(f'{data()}: corpus {len(S.C)} structures, searcher ready in {time.time() - t0:.0f} s', flush=True)

if cmd == 'record':          # N proposals, keep the last KEEP: by then the archive is full, as in a run
    N = int(sys.argv[2]); KEEP = 3000; Ts = []; t0 = time.time(); marks = []
    while len(Ts) < N:
        T = S.propose()
        if not T or len(set(T)) < 2: continue
        Ts.append(sorted(set(int(t) for t in T)))
        s = S.surrogate(T)
        if s: S.insert(s, push=False)
        if len(Ts) % (N // 8) == 0: marks.append((len(Ts), round(time.time() - t0, 1), len(S.archive)))
    dt = time.time() - t0
    print(f'recorded {N} proposals in {dt:.1f} s ({1000 * dt / N:.2f} ms each); (proposals, s, archive): {marks}')
    json.dump(Ts[-KEEP:], open('/data/prof_Ts.json', 'w'))
elif cmd == 'outputs':       # surrogate() on every recorded proposal, to compare code versions exactly
    Ts = json.load(open('/data/prof_Ts.json'))
    out = []
    for T in Ts:
        s = S.surrogate(T)
        out.append(None if s is None else [s['T'], round(s['cheap'], 12), list(s['desc']), s['n_gain'], s['dualities']])
    out.append([S.lat_skipped, S.ign_skipped, S.known_skipped, S.cand_skipped])
    json.dump(out, open(sys.argv[2], 'w'))
    print(f'{sum(o is not None for o in out[:-1])} of {len(Ts)} proposals scored; skips {out[-1]}; written {sys.argv[2]}')
else:
    Ts = json.load(open('/data/prof_Ts.json'))
    sizes = []
    orig = S.C.implied
    def implied(T, _o=orig):                     # count the corpus rows each call reduces over
        base, ext = S.C.sat(T); sizes.append((int(base.sum()), int(ext.sum())))
        return _o(T)
    t0 = time.time()
    for T in Ts: S.surrogate(T)
    dt = time.time() - t0
    print(f'replayed {len(Ts)} proposals in {dt:.1f} s: {1000 * dt / len(Ts):.2f} ms per evaluation')
    pr = cProfile.Profile(); pr.enable()
    for T in Ts[:1000]: S.surrogate(T)
    pr.disable()
    out = io.StringIO(); pstats.Stats(pr, stream=out).sort_stats('tottime').print_stats(14)
    print('\n'.join(l for l in out.getvalue().splitlines() if l.strip())[:4000])
    S.C.implied = implied
    for T in Ts[:300]: S.surrogate(T)
    from soup.offdiag import _implied_from
    b = np.array([s[0] for s in sizes]); e = np.array([s[1] for s in sizes])
    print(f'implied() of T, first 300: {len(sizes)} calls; base models median {np.median(b):.0f}, '
          f'corpus models median {np.median(e):.0f}, mean {e.mean():.0f}, max {e.max()}')
