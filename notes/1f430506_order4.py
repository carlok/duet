"""1f430506: every one-operation law of order 4 that holds in all its Mace4 models on 2-4 elements (cap 20,000 per
size; 4 incomplete), checked with E from T (15 s each). 27 Nov 2026.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/1f430506_order4.py
"""
import numpy as np
from soup.named import law_index
from soup.data import LAWS, ORDER
from soup.profile import all_models
from soup.core import law_vector
from soup.provers import prove_e
def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)
T = L(['(x·y)·(x∘z)=z∘x', '((x∘y)·(z·z))·x=x'])
acc = None
for n in (2, 3, 4):
    ms, complete, err = all_models(T, n, cap=20000, secs=120)
    for m in ms:
        v = law_vector(m[1], m[2], n); acc = v if acc is None else acc & v
one = [int(i) for i in np.flatnonzero(acc) if ORDER[i] == 4 and not ('·' in LAWS[i] and '∘' in LAWS[i])]
print('order-4 one-op laws true on n<=4 models found:', len(one), flush=True)
for i in one:
    r = prove_e(T, i, 300_000, 15); print(f'  {LAWS[i]:38s} {r["status"]}', flush=True)
