"""X6's N1 ranks 1-4 (23 Nov 2026): bc43fd42, d0e963d9, d14ced44 (a family) and 3818b88f. E, 30-60 s per goal.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/x6_top4_checks.py

Part 1: implications among the three family members, and against a common core K.
Part 2: 3818b88f: is · a totally symmetric quasigroup, what ∘ is, and a plain reading.
"""
import sys
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


F = {'bc43fd42': L(['x·(y·z)=x·(z∘y)', 'x·(((y∘y)·z)·w)=x']),
     'd0e963d9': L(['x·(y∘y)=x', 'x·((x·y)·x)=x', 'x·(y·z)=x·(z∘y)']),
     'd14ced44': L(['x·(y∘y)=x', 'x·(y·z)=x·(z∘y)', 'x·((x·y)∘y)=x·y'])}
K = L(['x·(y·z)=x·(z∘y)', 'x·(y·y)=x', 'x·(y∘y)=x'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'
if part == '1':
    for a in F:
        for b in F:
            if a != b: print(f'  {a} => {b}:', _proves(F[a], F[b], 60), flush=True)
    print('K =', ' & '.join(LAWS[k] for k in K))
    for a in F: print(f'  {a} => K:', _proves(F[a], K, 60), f'| K => {a}:', _proves(K, F[a], 60), flush=True)
    for s in ['x·(y∘z)=x', 'x·(y·z)=x', '(x·y)·z=x·z', 'x·(y·z)=x·y', 'x∘(y·z)=x∘(z·y)', '(x·y)·y=x·y', 'x·(y∘z)=x·(z·y)',
              'x∘y=y·x', 'x·(x∘y)=x']:
        print(f'  K => {s:18s}', _proves(K, L([s]), 30), flush=True)
T4 = L(['x·(x·y)=y', '(x·y)·y=x', 'x∘(x·y)=x∘y', '(x·x)∘(x∘x)=x', '(x·(x·x))∘x=x'])
if part == '2':
    for s in ['x·y=y·x', 'x·x=x', 'x·x=y·y', 'x∘x=x', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', 'x∘(y∘x)=x', 'x∘(x∘y)=x∘y',
              '(x·x)∘x=x', 'x∘(y·x)=x∘y', '(x∘y)·y=x·y', 'x∘(x·x)=x', 'x∘y=x', '(x·y)∘y=x∘y', 'x·(x∘y)=y']:
        print(f'  T => {s:18s}', _proves(T4, L([s]), 30), flush=True)
    C = L(['x·y=y·x', 'x·(x·y)=y', 'x∘x=x', 'x∘(x·y)=x∘y', '(x·x)∘x=x'])
    print('C =', ' & '.join(LAWS[c] for c in C))
    print('  T => C', _proves(T4, C, 60), '| C => T', _proves(C, T4, 60), flush=True)
