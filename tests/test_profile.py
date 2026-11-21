"""The algebraist's profile on cases with known answers."""
from soup.named import NAMED, law_index
from soup.profile import profile, canon
import numpy as np


def test_lattice_profile():
    p = profile([law_index(s) for s in NAMED['lattice']], sizes=(2, 3, 4))
    assert p['malcev']['majority']['proved']               # lattices are congruence distributive
    assert p['clone2']['functions'] == 4 and p['clone2']['closed']   # free lattice on 2 generators: 4 elements
    assert [p['spectrum'][n]['iso'] for n in (2, 3, 4)] == [1, 1, 2]
    assert p['features']['malcev_term'] and p['features']['finite_free2']


def test_canon_identifies_isomorphic_tables():
    F = np.array([[0, 0], [0, 1]], np.int16); G = np.array([[0, 1], [1, 1]], np.int16)
    swap = np.array([1, 0])
    F2 = swap[F[np.ix_(swap, swap)]]; G2 = swap[G[np.ix_(swap, swap)]]
    assert canon(2, F, G) == canon(2, F2, G2)
