"""Candidate 55cb2c91 (the early runs; N1 rank 1): structure (22 Nov 2026, evening).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - [part] < notes/55cb2c91_checks.py

T = {x·(x∘y) = x, x·y = ((y·z)·x)∘x}. Part 1: the short consequences of T (order <= 3) that the corpus suggests,
tested with E (20 s each), split into those a single law already gives and the rest.
"""
import sys
from concurrent.futures import ThreadPoolExecutor

from soup.core import Corpus, ORDER
from soup.data import LAWS
from soup.named import law_index
from soup.paths import data
from soup.relabel import _proves


def L(ss): return sorted(law_index(s) for s in ss)


T = L(['x·(x∘y)=x', 'x·y=((y·z)·x)∘x'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'
print('T =', ' & '.join(LAWS[t] for t in T))

if part == '1':
    C = Corpus(store=data('corpus'))
    imp = C.implied(T)
    singles = [C.implied([t]) for t in T]
    cand = [int(e) for e in range(len(LAWS)) if imp[e] and ORDER[e] <= 3 and e not in T]
    print(len(cand), 'laws of order <= 3 implied on the corpus')
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda e: (e, _proves(T, [e], 20)), cand))
    proved = [e for e, ok in res if ok]
    emergent = [e for e in proved if not any(s is not None and s[e] for s in singles)]
    print(len(proved), 'proved by E;', len(emergent), 'of them not implied by a single law on the corpus')
    for e in sorted(proved, key=lambda e: (ORDER[e], LAWS[e])):
        print(('  * ' if e in emergent else '    ') + LAWS[e])

# a candidate reading: C = {x·(y·z) = x·y, (x·y)·y = x·y, x·(x∘y) = x, x·y = (y·x)∘x}
C = L(['x·(y·z)=x·y', '(x·y)·y=x·y', 'x·(x∘y)=x', 'x·y=(y·x)∘x'])

if part == '2':
    print('C =', ' & '.join(LAWS[t] for t in C))
    for name, A, B in (('T => C', T, C), ('C => T', C, T)):
        print(name, {LAWS[b]: _proves(A, [b], 60) for b in B if b not in A})
    for c in C:                                             # is each law of C needed?
        rest = [d for d in C if d != c]
        print(f'  C minus {LAWS[c]:22s} => it:', _proves(rest, [c], 30))

if part == '3':
    # which · admit a ∘ making a model of T? Prediction: exactly those with x·(y·z) = x·y, (x·y)·y = x·y,
    # (i) x is a value of x·- , and (ii) y·x = y'·x implies x·y = x·y'. Brute force on 3 elements.
    import itertools
    n = 3
    R = range(n)
    def ok_T(F, G):
        f = lambda a, b: F[a * n + b]; g = lambda a, b: G[a * n + b]
        return all(f(x, g(x, y)) == x for x in R for y in R) and \
               all(f(x, y) == g(f(f(y, z), x), x) for x in R for y in R for z in R)
    agree = disagree = extendable = 0
    for F in itertools.product(R, repeat=n * n):
        f = lambda a, b: F[a * n + b]
        if not all(f(x, f(y, z)) == f(x, y) for x in R for y in R for z in R): continue
        pred = all(f(f(x, y), y) == f(x, y) for x in R for y in R) and \
               all(any(f(x, y) == x for y in R) for x in R) and \
               all(f(x, y) == f(x, y2) for x in R for y in R for y2 in R if f(y, x) == f(y2, x))
        ext = any(ok_T(F, G) for G in itertools.product(R, repeat=n * n))
        extendable += ext
        if pred == ext: agree += 1
        else: disagree += 1
    print(f'· tables on 3 elements with x·(y·z) = x·y: prediction agrees on {agree}, disagrees on {disagree}; '
          f'{extendable} extend to a model of T')

if part == '4':
    # the literature check says: with x·y = x∘y, law 2 is ETP 4174, equivalent to a constant law, and with ETP 9 the
    # pair has only one-element models. Checked with E.
    M = sorted({law_index(LAWS[t].replace('∘', '·').replace(' ', '')) for t in T})
    print('merged:', ' & '.join(LAWS[t] for t in M))
    e4174 = [law_index('x·y=((y·z)·x)·x')]
    print('  4174 alone => x·x = y·z (constant):', _proves(e4174, [law_index('x·x=y·z')], 30))
    print('  4174 => x·y = z·w:', _proves(e4174, [law_index('x·y=z·w')], 30))
    print('  9 & 4174 => x = y (one element):', _proves(M, [law_index('x=y')], 30))
