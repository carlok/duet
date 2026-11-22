"""A named theory up to all 8 relabellings of the operations: does T imply it, or is T a fragment of it?

    python -m soup.relabel --set candidates       -> SOUP_DATA/check/relabel_candidates.json and a table

The fragment check (fragments.py) and the dualities (duality.py) use the named theories as written and three
symmetries: swapping the operations, reversing both, or both. Writing x∘y for y∘x in one operation alone is also
only notation. Example (candidate 8a512957): its laws x·(y∘x) = y∘y and x·x = (y·x)∘y, with the emergent
idempotence, say that y∘x is the left division of ·. That is a left quasigroup with ∘ written in reverse.

A relabelling: swap the operations or not, reverse the arguments of · or not, of ∘ or not (8 in all). For each
named theory N of T3 (calib.NAMED) and each relabelling r:
  T implies r(N)        every law of r(N) holds in every corpus model of T, and E proves it from T;
  T is a fragment of    every law of T holds in every corpus model of r(N), and E proves it from r(N).
E: 30 s, 500,000 processed clauses per law. Only proofs count. Added 22 Nov 2026 as an equivalence check (rule 4).
"""
import argparse
import itertools
import json

from .paths import data, ensure


def _apply(t, swap, rf, rg):
    if t[0] == 'v': return t
    a, b = _apply(t[1], swap, rf, rg), _apply(t[2], swap, rf, rg)
    if (t[0] == 'f' and rf) or (t[0] == 'g' and rg): a, b = b, a
    op = {'f': 'g', 'g': 'f'}[t[0]] if swap else t[0]
    return (op, a, b)


def relabellings():
    for swap, rf, rg in itertools.product((0, 1), repeat=3):
        name = ' '.join(s for s, on in (('rev·', rf), ('rev∘', rg), ('swap', swap)) if on) or 'as written'
        yield name, (swap, rf, rg)


def relabel_law(i, r):
    from .data import TREES
    from .laws import canon_vars
    from .named import KEY
    L, R = (_apply(t, *r) for t in TREES[i])
    return KEY.get(min(repr(canon_vars(L, R)), repr(canon_vars(R, L))))


def _proves(A, B, secs):
    from .provers import prove_e
    return all(prove_e(sorted(A), b, processed_limit=500_000, cpu_limit=secs)['status'] == 'proved' for b in B if b not in A)


def check(T, C, secs=30):
    from .calib import NAMED
    from .named import law_index
    T = sorted(set(T)); impT = C.implied(T)
    out = {'implies': [], 'fragment_of': [], 'equivalent_to': []}
    for nm, laws in NAMED.items():
        N0 = [law_index(s.replace(' ', '')) for s in laws]
        seen = set()
        for rname, r in relabellings():
            N = sorted({relabel_law(i, r) for i in N0})
            if None in N or tuple(N) in seen: continue
            seen.add(tuple(N)); tag = f'{nm} ({rname})'
            imp = impT is not None and all(impT[v] for v in N) and _proves(T, N, secs)
            impN = C.implied(N)
            frag = impN is not None and all(impN[t] for t in T) and _proves(N, T, secs)
            if imp: out['implies'].append(tag)
            if frag: out['fragment_of'].append(tag)
            if imp and frag: out['equivalent_to'].append(tag)
    return out


def main():
    from .core import Corpus
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='candidates')
    a = ap.parse_args()
    C = Corpus(store=data('corpus'))
    res = []
    for r in json.load(open(data('check', 'candidates.json'))):
        x = check(r['T'], C); res.append(dict(x, key=str(r['key']), source=r['source'], laws=r['laws'], T=r['T']))
        print(f"{str(r['key'])[:8]:8s} {r['source']:10s} implies {x['implies'] or '-'} | fragment of "
              f"{x['fragment_of'] or '-'} | equivalent {x['equivalent_to'] or '-'}", flush=True)
    json.dump(res, open(ensure('check') / f'relabel_{a.set}.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
