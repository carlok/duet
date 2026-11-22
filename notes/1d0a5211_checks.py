"""Candidate 1d0a5211 (the early runs; N1 rank 2): structure (22-23 Nov 2026, night).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - [part] < notes/1d0a5211_checks.py

T = {x·(x∘y) = y∘x, (x∘(y·z))∘z = z}. Part 1: the short consequences of T (order <= 3) that the corpus suggests,
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


T = L(['x·(x∘y)=y∘x', '(x∘(y·z))∘z=z'])
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

A, B = L(['x·(x∘y)=y∘x']), L(['(x∘(y·z))∘z=z'])
K = L(['(x·y)∘y=y'])                                   # the key consequence (part 1)

if part == '2':
    # where (x·y)∘y = y comes from, and whether it can replace B
    print('A => K', _proves(A, K, 30), '| B => K', _proves(B, K, 30), '| T => K', _proves(T, K, 60))
    print('A + K => B', _proves(A + K, B, 120))
    for s in ['x·((y·x)·x)=x', 'x·(x∘(y·x))=x', 'x·(x∘x)=x∘x', '(x∘y)∘y=y', 'x∘(x·y)=y',
              '(x·y)·y=x·y', 'x·(y·x)=x', 'x·x=x', 'x∘x=x', '(x∘y)·y=x', 'x·(y∘x)=x']:
        print(f'  T => {s:22s}', _proves(T, L([s]), 30))

if part == '3':
    # the one-operation shadow: add x·y = x∘y (ETP numbers 335 and 238 by the profile)
    S = T + L(['x·y=x∘y'])
    for s in ['x·y=x', 'x·y=y', 'x·x=x', 'x·y=y·x', 'x·(y·z)=(x·y)·z', '(x·y)·y=x', 'x·(x·y)=y', 'x=y']:
        print(f'  T + (x·y = x∘y) => {s:18s}', _proves(S, L([s]), 30) if s != 'x=y' else '-')
    from soup.provers import mace4
    from soup.named import law_index
    r = mace4(S, law_index('x·y=x'), start=2, end=6, seconds=120)
    print('  Mace4, shadow model with x·y != x on 2-6:', {k: r[k] for k in r if k != 'out'})
