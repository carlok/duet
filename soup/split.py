"""Is a theory 'split': equivalent to a set of laws in · alone plus a set of laws in ∘ alone, with no bridge needed?

    python -m soup.split --set candidates       -> SOUP_DATA/check/split_candidates.json and a table
    python -m soup.split --laws 'law; law; ...'

The search requires a bridge law syntactically, but a theory can have bridges that only look like bridges. Example
(candidate 4dc33674): with x·(x·y) = y every left translation of · is a bijection, so x∘(x∘(x·y)) = x says no more
than x∘(x∘z) = x. Such a theory is two one-operation theories side by side, not a fusion.

Finite certificate of NOT split. If T were equivalent to V(·) ∪ W(∘), the · table of any model of T and the ∘
table of any model of T of the same size would form a model of T. So a pair (F of one model, G of another) that
fails a law of T proves that T is not split. The models are all models of sizes 2-4 (Mace4, as in soup.profile).

Proof of split. One-operation laws of order <= 3 that hold in every corpus model of T are proved from T by E. If E
then proves every law of T from the proved ones, T is split. Otherwise the answer is 'unknown' (no certificate
either way). Added 22 Nov 2026 as an equivalence check (rule 4); not part of the preregistered T5a ranking.
"""
import argparse
import itertools
import json

import numpy as np

from .paths import data, ensure


def _ev(t, X, F, G):
    if t[0] == 'v': return X[t[1]]
    a, b = _ev(t[1], X, F, G), _ev(t[2], X, F, G)
    return (F if t[0] == 'f' else G)[a, b]


def holds(T, F, G):
    from .data import TREES
    n = len(F); F = np.asarray(F); G = np.asarray(G)
    for t in T:
        L, R = TREES[t]
        X = np.meshgrid(*[np.arange(n)] * 4, indexing='ij')
        if not (_ev(L, X, F, G) == _ev(R, X, F, G)).all(): return False
    return True


def screen(T, sizes=(2, 3, 4), cap=80):
    from .profile import all_models
    for n in sizes:
        ms = all_models(T, n, 3000, 60)[0][:cap]
        Fs = {np.asarray(F).tobytes(): F for _, F, _ in ms}
        Gs = {np.asarray(G).tobytes(): G for _, _, G in ms}
        for F, G in itertools.product(Fs.values(), Gs.values()):
            if not holds(T, F, G):
                return {'split': False, 'witness': {'n': n, 'F': np.asarray(F).tolist(), 'G': np.asarray(G).tolist()}}
    return {'split': None}


def one_op(t):
    from .data import TREES
    ops = set()
    def walk(u):
        if u[0] != 'v': ops.add(u[0]); walk(u[1]); walk(u[2])
    L, R = TREES[t]; walk(L); walk(R)
    return len(ops) == 1


def prove_split(T, max_order=3, secs=30, cap=200):
    from .core import Corpus, ORDER
    from .provers import prove_e
    C = Corpus(store=data('corpus'))
    imp = C.implied(sorted(T))
    if imp is None: return {'split': None, 'why': 'no corpus model'}
    cand = [int(t) for t in np.nonzero(imp)[0] if ORDER[t] <= max_order and one_op(int(t)) and t not in T][:cap]
    proved = [t for t in cand if prove_e(sorted(T), t, processed_limit=200_000, cpu_limit=secs)['status'] == 'proved']
    for t in T:
        if t in proved or one_op(t): continue
        if prove_e(sorted(set(proved) | {u for u in T if one_op(u)}), t, processed_limit=500_000,
                   cpu_limit=secs * 2)['status'] != 'proved':
            return {'split': None, 'why': 'E did not derive a bridge law from one-operation consequences',
                    'one_op_consequences': len(proved)}
    return {'split': True, 'one_op_consequences': len(proved)}


def check(T):
    s = screen(T)
    if s['split'] is False: return s
    return prove_split(T)


def main():
    from .named import law_index
    from .data import LAWS
    ap = argparse.ArgumentParser()
    ap.add_argument('--set'); ap.add_argument('--laws')
    a = ap.parse_args()
    if a.set == 'candidates':
        jobs = [(str(r['key']), r['source'], r['laws'], r['T']) for r in json.load(open(data('check', 'candidates.json')))]
    else:
        laws = [s.strip() for s in a.laws.split(';')]
        jobs = [('adhoc', 'cli', laws, [law_index(s.replace(' ', '')) for s in laws])]
    res = []
    for key, src, laws, T in jobs:
        r = check(T); res.append(dict(r, key=key, source=src, laws=laws, T=T))
        print(f"{key[:8]:8s} {src:10s} split {r['split']} {r.get('why', '')} "
              f"{'(witness n = %d)' % r['witness']['n'] if r.get('witness') else ''}", flush=True)
    if a.set: json.dump(res, open(ensure('check') / f'split_{a.set}.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
