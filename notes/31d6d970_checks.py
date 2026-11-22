"""Candidate 31d6d970 (X3, rank 3): structure and the associative case (22 Nov 2026; E, 10-20 s per goal).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/31d6d970_checks.py

'-' means E found no proof in the time given, not that the law fails.
"""
import numpy as np

from soup.core import law_vector
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves


def L(ss): return [law_index(s) for s in ss]


T = L(['x·(x∘y)=x', '(x∘y)·y=y', '(x·x)·(y·x)=x', '(x·y)·(x·x)=x'])
print('T = 31d6d970:', ' & '.join(LAWS[t] for t in T))
F = np.array([[0, 0, 0], [1, 1, 2], [2, 1, 2]]); G = np.array([[0, 1, 1], [0, 1, 1], [0, 2, 2]])
LV = law_vector(F, G, 3); assert all(LV[t] for t in T)   # the smallest non-degenerate model (dossier, Cand13)
def verdict(i, ok): return 'proved' if ok else ('fails in the 3-element model' if not LV[i] else '-')
for g in ['x·x=x', 'x∘x=x', 'x·(y·x)=x', '(x·y)·x=x', '(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)', '(x·y)·z=x·z',
          'x∘(x·y)=x', '(x·y)∘y=y', 'x∘y=y∘x', 'x·y=y·x', 'x∘y=y·x']:
    i = law_index(g); print(f'T => {LAWS[i]:28s}', verdict(i, _proves(T, [i], 10)))
TA = T + L(['(x·y)·z=x·(y·z)'])
for g in ['x∘y=y·x', '(x·y)·z=x·z', '(x∘y)∘z=x∘(y∘z)', 'x∘(x·y)=x', '(y·x)∘x=x']:
    print(f'T + assoc(·) => {LAWS[law_index(g)]:24s}', 'proved' if _proves(TA, [law_index(g)], 20) else '-')
RB = L(['x·x=x', '(x·y)·z=x·z', 'x·(y·z)=x·z', 'x∘y=y·x'])
print('rectangular band with ∘ its transpose => T:', 'proved' if _proves(RB, T, 20) else '-')
