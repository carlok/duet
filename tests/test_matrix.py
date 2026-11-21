"""The matrix in SOUP_DATA is the reference one, and law indices mean what they meant in the cloud runs."""
import hashlib
import pickle
from pathlib import Path

import numpy as np
import pytest

from soup.paths import data, REPO

HASHES = REPO / 'tests' / 'matrix.sha256'


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def test_matrix_files_match_reference_hashes():
    ref = dict(line.split()[::-1] for line in HASHES.read_text().splitlines() if line.strip())
    for name, digest in ref.items():
        assert sha256(data(name)) == digest, name


def test_counts():
    from soup.data import NL, NP, LAWS, PM, LM
    assert NL == 71369 and NP == 12509
    assert sum('·' in s and '∘' in s for s in LAWS) == 61983
    assert isinstance(PM, np.memmap) and isinstance(LM, np.memmap)


@pytest.mark.parametrize('name', ['loopdual_31.pkl', 'loop_3.pkl'])
def test_law_order_matches_cloud_results(name):
    from soup.data import LAWS
    V = pickle.load(open(REPO / 'results-cloud' / name, 'rb'))['verified']
    assert len(V) > 50
    for T, r in V.items():
        assert r['laws'] == [LAWS[t] for t in sorted(set(T))]


def test_law_vector_matches_matrix_rows():
    from soup.core import law_vector
    from soup.data import PM, unpack_laws
    from soup.probes import build
    P = build()
    for i in (0, 17, 300, 4000, 9000, 12508):
        _, n, F, G = P[i]
        assert (law_vector(F, G, n) == unpack_laws(PM[i])).all()
