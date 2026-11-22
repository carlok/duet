"""Candidates up to logical equivalence (post hoc, added 22 Nov 2026).

    python -m soup.dedupe [--set candidates] [--secs 20]

The candidate list deduplicates up to the three dualities on the law sets (duality.theory_key), not up to logical
equivalence: on 22 Nov 2026 the variety of `2dc27508` reached the top ten twice, as `69dfbd8e`. This groups the
candidates into equivalence classes under the 8 relabellings (soup.relabel): A ~ B if A implies r(B) and r(B)
implies A for some relabelling r. Model filter first (the corpus models of each theory must satisfy the other's
laws), then E (secs per law, 500,000 processed clauses); only proofs count. The ranking itself is not changed.
Output: SOUP_DATA/check/dedupe_<set>.json.
"""
import argparse
import json

from .paths import data


def main():
    from .core import Corpus
    from .relabel import relabellings, relabel_law, _proves
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='candidates')
    ap.add_argument('--secs', type=int, default=20)
    a = ap.parse_args()
    cand = json.load(open(data('check', f'{a.set}.json')))
    C = Corpus(store=data('corpus'))
    imp = {c['key']: C.implied(sorted(c['T'])) for c in cand}
    cache = {}
    def implied(T):
        k = tuple(sorted(T))
        if k not in cache: cache[k] = C.implied(list(k))
        return cache[k]
    parent = {c['key']: c['key'] for c in cand}
    def find(k):
        while parent[k] != k: k = parent[k]
        return k
    pairs = []
    for i, A in enumerate(cand):
        for B in cand[i + 1:]:
            if find(A['key']) == find(B['key']): continue
            for rname, r in relabellings():
                RB = [relabel_law(t, r) for t in B['T']]
                if None in RB: continue
                iA, iB = imp[A['key']], implied(RB)
                if iA is None or iB is None: continue
                if not (all(iA[t] for t in RB) and all(iB[t] for t in A['T'])): continue
                if _proves(A['T'], RB, a.secs) and _proves(RB, A['T'], a.secs):
                    parent[find(B['key'])] = find(A['key'])
                    pairs.append({'a': A['key'], 'b': B['key'], 'relabel': rname}); break
    classes = {}
    for c in cand: classes.setdefault(find(c['key']), []).append(c['key'])
    multi = [v for v in classes.values() if len(v) > 1]
    json.dump({'pairs': pairs, 'classes': multi}, open(data('check', f'dedupe_{a.set}.json'), 'w'), indent=1)
    print(f'{len(cand)} candidates, {len(classes)} classes up to equivalence under the 8 relabellings; '
          f'{len(multi)} classes with more than one member')
    src = {c['key']: c.get('source') for c in cand}
    for v in multi: print('  ', ', '.join(f'{k[:8]} ({src[k]})' for k in v))


if __name__ == '__main__':
    main()
