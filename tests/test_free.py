"""B3 (28 Nov 2026): the counter of soup.free against known counts."""
import time

import numpy as np

from soup.free import measure
from soup.named import law_index


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


def test_1f430506_on_two_elements_matches_mace4():
    T = L(['(x·y)·(x∘z)=z∘x', '((x∘y)·(z·z))·x=x'])          # 12 labelled models on 2 elements (notes/1f430506.md)
    r = measure(T, 'circ_given_dot', 2, None, time.time() + 60)
    assert r['models'] == 12
    # ∘ is commutative, which ties cell (x,y) to (y,x): a product over unordered cells, so rho < 1 over ordered ones
    assert r['rho'] < 1


def test_one_cell_constraints_give_a_product():
    T = L(['((x∘y)·(z·z))·x=x'])                             # 1f430506's B alone: SC, one cell, no swap
    r = measure(T, 'circ_given_dot', 3, None, time.time() + 120)
    assert r['rho'] == 1.0


def test_lattice_meet_is_determined_by_join():
    T = L(['x·(x∘y)=x', 'x∘(x·y)=x', 'x·y=y·x', 'x∘y=y∘x', '(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)'])
    r = measure(T, 'circ_given_dot', 3, None, time.time() + 60)
    assert r['H'] == 0.0 and r['models'] == r['reducts_with_models']    # exactly one ∘ for each lattice ·
