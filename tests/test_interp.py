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


def test_a9295908_passes_the_filter_in_heyting_algebras():
    # a9295908 = {x·(x∘x) = x, (x∘y)·y = y, x·y = x∘(y·x)}; ledger: · = ∧, x∘y = (y→x)→y (notes/a9295908.md)
    T = sorted(law_index(s) for s in ['x·(x∘x)=x', '(x∘y)·y=y', 'x·y=x∘(y·x)'])
    Ms = models('HA', sizes=range(2, 5), per=20, secs=60)
    assert Ms
    t1, t2 = ('me', 'x', 'y'), ('h', ('h', 'y', 'x'), 'y')
    for n, M in Ms:
        v = law_vector(evalt(t1, M, n), evalt(t2, M, n), n)
        assert all(v[t] for t in T), (n, show(t2))
