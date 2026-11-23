"""Candidate 742cc445 (X4; N1 rank 4): structure (23 Nov 2026, during X6; single-threaded E, 30 s per goal).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/742cc445_checks.py

T = {x·(y∘(x∘z)) = x (McKenzie's L1), x∘((x∘y)·(z∘x)) = x}.
Part 1: which lattice-type laws T proves (E), including McKenzie's L2-L4 and both absorptions.
"""
import sys
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


T = L(['x·(y∘(x∘z))=x', 'x∘((x∘y)·(z∘x))=x'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'
print('T =', ' & '.join(LAWS[t] for t in T))
GOALS = {
    'McKenzie L2': 'x∘(y·(x·z))=x', 'McKenzie L3': '((y∘x)·(x∘z))·x=x', 'McKenzie L4': '((y·x)∘(x·z))∘x=x',
    'absorption ·∘': 'x·(x∘y)=x', 'absorption ∘·': 'x∘(x·y)=x', 'idempotent ·': 'x·x=x', 'idempotent ∘': 'x∘x=x',
    '· commutative': 'x·y=y·x', '∘ commutative': 'x∘y=y∘x', '· associative': '(x·y)·z=x·(y·z)',
    '∘ associative': '(x∘y)∘z=x∘(y∘z)', '∘ left-zero': 'x∘y=x', '· left-zero': 'x·y=x',
    'x∘(x∘y)=x': 'x∘(x∘y)=x', 'x∘(y∘x)=x∘y': 'x∘(y∘x)=x∘y', '(x∘y)∘z=x∘z': '(x∘y)∘z=x∘z',
    'x∘(y∘z)=x∘z': 'x∘(y∘z)=x∘z', '(x·y)·z=x·z': '(x·y)·z=x·z', 'x·(y·z)=x·z': 'x·(y·z)=x·z',
    'x·(y·x)=x·y': 'x·(y·x)=x·y', '(x∘y)·x=x∘y': '(x∘y)·x=x∘y', 'x·(y∘y)=x·y': 'x·(y∘y)=x·y',
}
if part == '1':
    for name, s in GOALS.items():
        print(f'  {name:16s} {s:22s}', _proves(T, L([s]), 30), flush=True)

# part 2: which proved laws need both axioms, and a candidate reading C
A1, A2 = L(['x·(y∘(x∘z))=x']), L(['x∘((x∘y)·(z∘x))=x'])
PROVED = ['x·(x∘y)=x', 'x·x=x', 'x∘x=x', 'x∘(x∘y)=x', '(x∘y)·x=x∘y', 'x·(y∘y)=x·y', 'x∘(y·y)=x∘y', 'x·(y∘x)=x']
if part == '2':
    for s in PROVED:
        print(f'  {s:16s} T {_proves(T, L([s]), 30)}  A1 alone {_proves(A1, L([s]), 20)}  A2 alone {_proves(A2, L([s]), 20)}',
              flush=True)
    C = L(['x·(x∘y)=x', 'x·(y∘x)=x', 'x∘(x∘y)=x', '(x∘y)·x=x∘y'])
    print('C =', ' & '.join(LAWS[c] for c in C))
    print('  C => A1', _proves(C, A1, 60), '| C => A2', _proves(C, A2, 60), '| A1 + C => A2', _proves(A1 + C, A2, 60),
          '| A2 + C => A1', _proves(A2 + C, A1, 60), flush=True)

# part 3: checks of the literature agent's claims (23 Nov)
if part == '3':
    from soup.offdiag import lat2
    import numpy as np
    from soup.core import law_vector
    swapped = law_vector(np.array([[0, 0], [0, 1]]), np.array([[0, 1], [1, 1]]), 2)   # · = meet, ∘ = join
    for nm, s in [('A1', 'x·(y∘(x∘z))=x'), ('A2', 'x∘((x∘y)·(z∘x))=x')]:
        i = law_index(s)
        print(f'  {nm} holds in the 2-element lattice: (· join, ∘ meet) {bool(lat2()[i])}, (· meet, ∘ join) {bool(swapped[i])}')
    ass = L(['(x∘y)∘z=x∘(y∘z)'])
    print('  T + ∘ associative => x∘y = x:', _proves(T + ass, L(['x∘y=x']), 60),
          '| => x·y = x∘y:', _proves(T + ass, L(['x·y=x∘y']), 60), flush=True)
    print('  shadow of A1 = ETP 54 (x = x◇(y◇(x◇z))):', law_index('x·(y·(x·z))=x') == law_index('x=x·(y·(x·z))'),
          '| shadow of A2 = ETP 828 (x = x◇((x◇y)◇(z◇x))):', law_index('x·((x·y)·(z·x))=x') == law_index('x=x·((x·y)·(z·x))'))
