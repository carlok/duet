"""The R1 catalogue: every entry is in the law table (order <= 4) and has a model where its laws hold."""
import numpy as np

from soup.catalogue import KNOWN, laws_of
from soup.core import ORDER
from soup.split import holds


def test_entries_in_law_table():
    for name in KNOWN:
        T = laws_of(name)
        assert None not in T, name
        assert all(ORDER[t] <= 4 for t in T), name


def test_one_post_hoc_entry():
    assert [n for n, k in KNOWN.items() if k['post_hoc']] == ['Delta-bijective pair']


def test_known_models():
    chain_max = [[max(a, b) for b in range(2)] for a in range(2)]
    chain_min = [[min(a, b) for b in range(2)] for a in range(2)]
    assert holds(laws_of('weakly associative lattice'), chain_max, chain_min)
    z2 = [[(a + b) % 2 for b in range(2)] for a in range(2)]
    assert holds(laws_of('doppelsemigroup'), z2, z2)
    rect = [[2 * (a // 2) + b % 2 for b in range(4)] for a in range(4)]      # 2x2 rectangular band
    assert holds(laws_of('Delta-bijective pair'), rect, rect)
    left = [[a for b in range(2)] for a in range(2)]          # left projection: (x,y) -> (x,y), bijective, self-decoding
    assert holds(laws_of('Delta-bijective pair'), left, left)
    const = [[0, 0], [0, 0]]                                  # constant: (x,y) -> (0,0), not bijective
    assert not holds(laws_of('Delta-bijective pair'), const, const)
