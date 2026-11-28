"""X13 design: how much would an incremental rescore have cost fusion6 in x12f6a? Read-only replay on work/x12-f6.
27 Nov 2026, before the X13 preregistration.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - [2] < notes/x13_replay.py

An elite T needs rescoring only when a new corpus structure satisfies one of T's laws (every corpus-dependent part of
searcher.surrogate reads only structures that satisfy a law of T). For each searcher's final archive and each window of
w seconds of the block, U = the laws satisfied by some structure written in that window (corpus file mtimes), and the
affected elites are those with a law in U. The projected cost is the affected count times the mean cost of one
elite's surrogate, estimated from the searcher's own full rescores: rescore_secs / (rescores × mean archive size).
Caveat: a proxy. The final archive is used for the whole block, though the archive grew during it; per-elite cost is
an average.
"""
import glob
import json
import os

import numpy as np

from soup.core import unpack_laws
from soup.data import NL

D = '/data/x12-f6'
stats = [json.loads(l) for l in open(f'{D}/logs/stats.jsonl')]
stats = [s for s in stats if s.get('run') == 'x12f6a']
t0, t1 = stats[0]['t'] - stats[0]['elapsed_s'], stats[-1]['t']
print(f'block x12f6a: {t1 - t0:.0f} s')

# structures written during the block
new = []
for p in glob.glob(f'{D}/corpus/*.npz'):
    m = os.stat(p).st_mtime
    if t0 <= m <= t1: new.append((m, p))
new.sort()
print(f'corpus files: {len(glob.glob(D + "/corpus/*.npz"))}, written during the block: {len(new)}')
vecs = np.array([unpack_laws(np.load(p)['lawvec']) for _, p in new])
times = np.array([m for m, _ in new])
print(f'mean share of the {NL} laws a new structure satisfies: {vecs.mean():.4f}')

for name in ('s1801', 's1802'):
    hb = json.load(open(f'{D}/logs/workers/{name}.json'))
    arch = [w['archive'] for s in stats for w in s['workers'] if w['name'] == name and w.get('archive')]
    per = hb['rescore_secs'] / (hb['rescores'] * np.mean(arch))
    el = json.load(open(f'{D}/runs/x12f6a/archive_{name}.json'))['elites']
    Ts = [e['T'] if isinstance(e['T'], list) else json.loads(e['T']) for e in el]
    P = np.full((len(Ts), 6), NL)
    for i, T in enumerate(Ts): P[i, :len(T)] = T
    print(f'\n{name}: {hb["rescores"]} full rescores, {hb["rescore_secs"]:.0f} s; mean archive {np.mean(arch):.0f}, '
          f'final {len(Ts)}; {per * 1000:.1f} ms per elite')
    for w in (20, 120, 600):
        bins = ((times - t0) // w).astype(int)
        aff_tot, fr = 0, []
        for b in np.unique(bins):
            U = np.append(vecs[bins == b].any(axis=0), False)
            a = int(U[P].any(axis=1).sum()); aff_tot += a; fr.append(a / len(Ts))
        cost = aff_tot * per
        print(f'  window {w:4d} s: {len(fr)} windows with new structures; affected per window median '
              f'{np.median(fr):.1%}, max {max(fr):.1%}; projected {cost:.0f} s = {cost / (t1 - t0):.1%} of searcher time '
              f'(full rescores: {hb["rescore_secs"] / (t1 - t0):.1%})', flush=True)

# ---- part 2 (run with argument 2): the finer test. A new structure s changes T's surrogate only if s satisfies all of
# T (new model: stats, implied, family), or s satisfies some law t of T and every one-variable law D_T that T implies
# (offdiag_gain's covered set comes from the models of {t} ∪ D_T). D_T is taken on the final corpus, which can only
# make it smaller than during the block, so the affected counts are upper bounds for this test.
import sys
if len(sys.argv) > 1 and sys.argv[1] == '2':
    import time
    from soup.core import Corpus
    from soup.offdiag import DIAG
    C = Corpus(store=f'{D}/corpus')
    print(f'\npart 2: corpus loaded, {len(C)} found structures', flush=True)
    for name in ('s1801', 's1802'):
        hb = json.load(open(f'{D}/logs/workers/{name}.json'))
        arch = [w['archive'] for s in stats for w in s['workers'] if w['name'] == name and w.get('archive')]
        per = hb['rescore_secs'] / (hb['rescores'] * np.mean(arch))
        el = json.load(open(f'{D}/runs/x12f6a/archive_{name}.json'))['elites']
        t_s = time.time(); hit = np.zeros((len(el), len(new)), bool); nD = []
        for i, e in enumerate(el):
            T = e['T'] if isinstance(e['T'], list) else json.loads(e['T'])
            imp = C.implied(T)
            Dl = np.flatnonzero(imp & DIAG) if imp is not None else np.array([], int)
            nD.append(len(Dl))
            allT = vecs[:, T].all(axis=1)
            some = vecs[:, T].any(axis=1) & (vecs[:, Dl].all(axis=1) if len(Dl) else True)
            hit[i] = allT | some
        print(f'{name}: {len(el)} elites, D_T size median {np.median(nD):.0f} (0 for {np.mean(np.array(nD) == 0):.1%}); '
              f'{time.time() - t_s:.0f} s', flush=True)
        for w in (20, 120, 600):
            bins = ((times - t0) // w).astype(int)
            aff_tot, fr = 0, []
            for b in np.unique(bins):
                a = int(hit[:, bins == b].any(axis=1).sum()); aff_tot += a; fr.append(a / len(el))
            cost = aff_tot * per
            print(f'  window {w:4d} s: affected per window median {np.median(fr):.1%}, max {max(fr):.1%}; projected '
                  f'{cost:.0f} s = {cost / (t1 - t0):.1%} of searcher time', flush=True)
