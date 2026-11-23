"""Candidate 97a7dfcf (X4; N1 rank 5): structure (23 Nov 2026, during X6; single-threaded E).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/97a7dfcf_checks.py

T = {x·x = y·y, x·(y∘x) = x∘y, (x·y)·z = y∘(z·y)}. Write 0 for the constant x·x.
Part 1: nilpotency laws (E, 30 s each). Part 2: a plain reading C and T <=> C (E, 60 s per law).
"""
import sys
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


T = L(['x·x=y·y', 'x·(y∘x)=x∘y', '(x·y)·z=y∘(z·y)'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'
print('T =', ' & '.join(LAWS[t] for t in T))
if part == '1':
    for s in ['(x·y)·z=w·w', 'x·(y·z)=w·w', 'x∘(y·z)=w·w', '(x·y)∘z=w·w', 'x·(y∘z)=x∘z', 'x∘x=y·y', 'x∘y=y∘x',
              'x·y=y·x', 'x∘(y∘z)=w·w', '(x∘y)∘z=w·w', 'x·(x·y)=z·z', 'x·y=z·z', 'x∘y=z·z', 'x·(y∘z)=w·w']:
        print(f'  {s:18s}', _proves(T, L([s]), 30), flush=True)

# part 2: a plain reading: 0 = x·x; x·(y∘x) = x∘y; ·-products of a product on the left vanish; ∘ of a product vanishes
C = L(['x·x=y·y', 'x·(y∘x)=x∘y', '(x·y)·z=w·w', 'x∘(y·z)=w·w'])
if part == '2':
    print('C =', ' & '.join(LAWS[c] for c in C))
    print('  T => C', _proves(T, C, 60), '| C => T', _proves(C, T, 60), flush=True)
    print('  with ∘ = ·: T + x·y = x∘y => x·y = z·z (a null semigroup):', _proves(T + L(['x·y=x∘y']), L(['x·y=z·z']), 60))
