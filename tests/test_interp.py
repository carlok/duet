"""B1, R2 (28 Nov 2026): soup.interp's prover-free parts, and the model-filter half of the positive control R2a."""
import json

import numpy as np

from soup.core import law_vector
from soup.data import TREES
from soup.interp import ENTRIES, evalt, models, show, terms, translate, tvars
from soup.named import law_index


def test_terms_and_translation():
    T = terms(ENTRIES['G']['sig'])
    assert ('m', 'x', 'y') in T and ('m', ('i', 'x'), 'y') in T
    assert all(tvars(t) <= {'x', 'y'} for t in T)
    law = TREES[law_index('x·y=y·x')]
    assert translate(law, ('me', 'x', 'y'), ('j', 'x', 'y')) == 'me(x,y) = me(y,x)'
    law = TREES[law_index('x∘(x·y)=x')]
    assert translate(law, ('j', 'x', 'y'), ('me', 'x', 'y')) == 'me(x,j(x,y)) = x'


def test_holds_batch_agrees_with_law_vector():
    from soup.interp import holds_batch
    rng = np.random.default_rng(7)
    laws = rng.choice(len(TREES), 400, replace=False)
    true = 0
    for n in (2, 3, 4):
        X, Y = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
        structured = [(X + Y) % n, (X - Y) % n, X, (2 * X + 2 * Y) % n]      # many laws hold here, not only fail
        for F in [rng.integers(0, n, (n, n)), (X + Y) % n, X]:
            Gs = np.stack([rng.integers(0, n, (n, n)) for _ in range(3)] + structured)
            V = [law_vector(F, G, n) for G in Gs]
            cache = {}
            for t in laws:
                got = holds_batch(TREES[t], F, Gs, n, cache)
                assert list(got) == [bool(v[t]) for v in V], (n, t)
                true += int(got.sum())
    assert true > 100


def test_a9295908_passes_the_filter_in_heyting_algebras():
    # a9295908 = {x·(x∘x) = x, (x∘y)·y = y, x·y = x∘(y·x)}; ledger: · = ∧, x∘y = (y→x)→y (notes/a9295908.md)
    T = sorted(law_index(s) for s in ['x·(x∘x)=x', '(x∘y)·y=y', 'x·y=x∘(y·x)'])
    Ms = models('HA', sizes=range(2, 5), per=20, secs=60)
    assert Ms
    t1, t2 = ('me', 'x', 'y'), ('h', ('h', 'y', 'x'), 'y')
    for n, M in Ms:
        v = law_vector(evalt(t1, M, n), evalt(t2, M, n), n)
        assert all(v[t] for t in T), (n, show(t2))
