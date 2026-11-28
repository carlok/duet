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

N2 (28 Nov 2026, PREREGISTRATION.md, N2, item C3): `--union --out dedupe2` reads the union of every run's corpus
(soup.funnel.DIRS) and gives every unordered pair one of three outcomes: equivalent (E proves both directions for some
relabelling: 20 s per law, then a second pass of E 120 s and Vampire 120 s), separated (for every relabelling a corpus
structure satisfies one theory and fails a law of the other) or unknown. Candidates with no model in the union corpus
are listed as never compared. Level 5 is a range: classes of the equivalent pairs (upper), and with the unknown pairs
merged too (lower). The default path above (N1) is unchanged.
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data


def union_corpus():
    """Every run's corpus in one Corpus (structures deduplicated by key), in memory only."""
    from .core import Corpus
    from .funnel import DIRS
    C = Corpus(store=data('corpus'))
    for d in DIRS:
        p = data(d, 'corpus') if d != '.' else None
        if p is not None and p.exists(): C.store = p; C.refresh()
    C.store = None
    return C


def pair_outcomes(cand, implied, rels, relabel_law):
    """Model filter for every unordered pair. Returns (never compared keys, separated pairs, {pair: [(rname, RB)]}):
    a pair is separated when every relabelling is separated by a corpus structure, else its passing relabellings are
    listed (to be proved). A relabelling whose relabelled laws are not all in the table cannot be tested; a pair with
    such a relabelling and no passing one is kept with an empty list (unknown without a prover call)."""
    never = [c['key'] for c in cand if implied(c['T']) is None]
    sep, todo = [], {}
    for i, A in enumerate(cand):
        iA = implied(A['T'])
        if iA is None: continue
        for B in cand[i + 1:]:
            if implied(B['T']) is None: continue
            passing, untested = [], False
            for rname, r in rels:
                RB = [relabel_law(t, r) for t in B['T']]
                if None in RB: untested = True; continue
                iB = implied(RB)                    # None: r(B) has no corpus model, so no structure separates this way
                if not all(iA[t] for t in RB): continue
                if iB is not None and not all(iB[t] for t in A['T']): continue
                passing.append((rname, RB))
            if passing or untested: todo[(A['key'], B['key'])] = passing
            else: sep.append((A['key'], B['key']))
    return never, sep, todo


def classes_of(keys, pairs):
    """Union-find classes (lists of keys, only those with more than one member) of the given pairs."""
    parent = {k: k for k in keys}
    def find(k):
        while parent[k] != k: k = parent[k]
        return k
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb: parent[rb] = ra
    cl = {}
    for k in keys: cl.setdefault(find(k), []).append(k)
    return [v for v in cl.values() if len(v) > 1], len(cl)


def _direction(A, B, secs, vampire):
    """A proves every law of B (E at secs, then Vampire at secs for what E leaves, if vampire)."""
    from .provers import prove_e, prove_vampire
    for b in B:
        if b in A: continue
        if prove_e(sorted(A), b, processed_limit=500_000, cpu_limit=secs)['status'] == 'proved': continue
        if vampire and prove_vampire(sorted(A), b, cpu_limit=secs)['status'] == 'proved': continue
        return False
    return True


def n2(a, cand):
    from .relabel import relabellings, relabel_law
    t0 = time.time()
    C = union_corpus()
    print(f'union corpus: {len(C)} found structures', flush=True)
    cache = {}
    def implied(T):
        k = tuple(sorted(T))
        if k not in cache: cache[k] = C.implied(list(k))
        return cache[k]
    never, sep, todo = pair_outcomes(cand, implied, list(relabellings()), relabel_law)
    n_items = sum(len(v) for v in todo.values())
    print(f'{len(cand)} candidates, {len(never)} never compared (no model in the union corpus); '
          f'{len(sep)} pairs separated by a model, {len(todo)} pairs left with {n_items} (pair, relabelling) items '
          f'({round(time.time() - t0)} s)', flush=True)
    eq = {}
    def run(passes):
        items = [(p, rn, RB) for p, lst in todo.items() if p not in eq for rn, RB in lst]
        TA = {c['key']: c['T'] for c in cand}
        def job(it):
            (ka, kb), rn, RB = it
            ok = all(_direction(TA[ka], RB, s, v) and _direction(RB, TA[ka], s, v) for s, v in passes)
            return it, ok
        with ThreadPoolExecutor(a.jobs) as ex:
            futs = [ex.submit(job, it) for it in items]
            for n, f in enumerate(as_completed(futs), 1):
                (p, rn, _), ok = f.result()
                if ok and p not in eq: eq[p] = rn
                if n % 50 == 0 or n == len(items):
                    print(f'  {n}/{len(items)} items, {len(eq)} equivalent pairs ({round(time.time() - t0)} s)', flush=True)
    run([(a.secs, False)])                                   # pass 1: as N1
    run([(a.secs2, True)])                                   # pass 2: E then Vampire, only pairs still open
    unknown = [p for p in todo if p not in eq]
    keys = [c['key'] for c in cand]
    upper_multi, upper = classes_of(keys, eq.keys())
    lower_multi, lower = classes_of(keys, list(eq.keys()) + unknown)
    out = {'corpus': len(C), 'never_compared': never, 'separated': len(sep),
           'equivalent': [{'a': p[0], 'b': p[1], 'relabel': rn} for p, rn in eq.items()],
           'unknown': [{'a': p[0], 'b': p[1], 'relabellings': [rn for rn, _ in todo[p]]} for p in unknown],
           'classes': upper_multi, 'classes_with_unknown_merged': lower_multi,
           'level5': {'lower': lower, 'upper': upper}, 'secs': [a.secs, a.secs2], 'wall_s': round(time.time() - t0)}
    json.dump(out, open(data('check', f'{a.out}_{a.set}.json'), 'w'), indent=1)
    print(f'equivalent pairs {len(eq)}, unknown {len(unknown)}, separated {len(sep)}; level 5 between {lower} and '
          f'{upper} varieties ({len(upper_multi)} classes with more than one member)', flush=True)


def main():
    from .core import Corpus
    from .relabel import relabellings, relabel_law, _proves
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='candidates')
    ap.add_argument('--secs', type=int, default=20)
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--union', action='store_true', help='N2: union corpus, three outcomes, second pass')
    ap.add_argument('--out', default='dedupe', help='output prefix (N2: dedupe2)')
    ap.add_argument('--secs2', type=int, default=120, help='N2: E and Vampire seconds per law in the second pass')
    a = ap.parse_args()
    cand = json.load(open(data('check', f'{a.set}.json')))
    if a.union:
        if a.out == 'dedupe': raise SystemExit('--union writes N2 output: pass --out dedupe2')
        return n2(a, cand)
    # every run's corpus: a candidate from a later run may have no model in the main corpus, and a theory with no
    # corpus model is never compared (first version: main corpus only)
    C = Corpus(store=data('corpus'))
    for d in ('t4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'):
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
