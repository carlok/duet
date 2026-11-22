"""Candidates up to logical equivalence (post hoc, added 22 Nov 2026).

    python -m soup.dedupe [--set candidates] [--secs 20] [--jobs 6]

The candidate list deduplicates up to the three dualities on the law sets (duality.theory_key), not up to logical
equivalence: on 22 Nov 2026 the variety of `2dc27508` reached the top ten twice, as `69dfbd8e`. This groups the
candidates into equivalence classes under the 8 relabellings (soup.relabel): A ~ B if A implies r(B) and r(B)
implies A for some relabelling r. Model filter first (the corpus models of each theory must satisfy the other's
laws), then E (secs per law, 500,000 processed clauses); only proofs count. The ranking itself is not changed.

Since 22 Nov 2026 evening: all (pair, relabelling) that pass the model filter are collected first (count printed),
then E runs in parallel (--jobs), with progress. The classes are the transitive closure of the proved equivalences,
as before (the first version stopped at the first proved relabelling of a pair and skipped pairs already joined;
the classes are the same).
Output: SOUP_DATA/check/dedupe_<set>.json.
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data


def main():
    from .core import Corpus
    from .relabel import relabellings, relabel_law, _proves
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='candidates')
    ap.add_argument('--secs', type=int, default=20)
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    cand = json.load(open(data('check', f'{a.set}.json')))
    # every run's corpus: a candidate from a later run may have no model in the main corpus, and a theory with no
    # corpus model is never compared (first version: main corpus only)
    C = Corpus(store=data('corpus'))
    for d in ('t4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x5'):
        p = data(d, 'corpus')
        if p.exists(): C.store = p; C.refresh()
    C.store = None
    print(f'corpus: {len(C)} found structures from all runs', flush=True)
    cache = {}
    def implied(T):
        k = tuple(sorted(T))
        if k not in cache: cache[k] = C.implied(list(k))
        return cache[k]
    t0 = time.time()
    todo = []                                              # (A key, B key, relabelling, A laws, r(B) laws)
    for i, A in enumerate(cand):
        iA = implied(A['T'])
        if iA is None: continue
        for B in cand[i + 1:]:
            for rname, r in relabellings():
                RB = [relabel_law(t, r) for t in B['T']]
                if None in RB: continue
                iB = implied(RB)
                if iB is None: continue
                if all(iA[t] for t in RB) and all(iB[t] for t in A['T']):
                    todo.append((A['key'], B['key'], rname, A['T'], RB))
    print(f'{len(cand)} candidates; {len(todo)} (pair, relabelling) pass the model filter '
          f'({round(time.time() - t0)} s)', flush=True)

    def job(item):
        ka, kb, rname, TA, RB = item
        return item, _proves(TA, RB, a.secs) and _proves(RB, TA, a.secs)
    proved = []
    with ThreadPoolExecutor(a.jobs) as ex:                 # E runs as a subprocess: threads are enough
        futs = [ex.submit(job, it) for it in todo]
        for n, f in enumerate(as_completed(futs), 1):
            item, ok = f.result()
            if ok: proved.append({'a': item[0], 'b': item[1], 'relabel': item[2]})
            if n % 20 == 0 or n == len(todo):
                print(f'  {n}/{len(todo)} checked, {len(proved)} equivalences ({round(time.time() - t0)} s)', flush=True)

    parent = {c['key']: c['key'] for c in cand}
    def find(k):
        while parent[k] != k: k = parent[k]
        return k
    for p in proved:
        ra, rb = find(p['a']), find(p['b'])
        if ra != rb: parent[rb] = ra
    classes = {}
    for c in cand: classes.setdefault(find(c['key']), []).append(c['key'])
    multi = [v for v in classes.values() if len(v) > 1]
    json.dump({'pairs': proved, 'classes': multi, 'checked': len(todo), 'secs': a.secs},
              open(data('check', f'dedupe_{a.set}.json'), 'w'), indent=1)
    print(f'{len(cand)} candidates, {len(classes)} classes up to equivalence under the 8 relabellings; '
          f'{len(multi)} classes with more than one member')
    src = {c['key']: c.get('source') for c in cand}
    for v in multi: print('  ', ', '.join(f'{k[:8]} ({src[k]})' for k in v))


if __name__ == '__main__':
    main()
