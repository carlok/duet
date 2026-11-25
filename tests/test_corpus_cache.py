"""Corpus.has: the per-law column cache behind Corpus.sat (25 Nov 2026). It must give exactly what reading the
column of XP gives, after appends and after evictions."""
import random

import numpy as np

from soup.core import Corpus, _bits_have


def _random_structure(rng, n):
    F = rng.integers(0, n, (n, n)); G = rng.integers(0, n, (n, n))
    return F, G


def test_column_cache_is_exact(tmp_path, monkeypatch):
    monkeypatch.setattr(Corpus, 'COL_CACHE', 16)                    # small, so evictions happen
    rng = np.random.default_rng(5); prng = random.Random(5)
    C = Corpus(store=tmp_path)
    laws = [prng.randrange(71369) for _ in range(40)]
    for step in range(6):
        for _ in range(7):                                          # 7 rows per step: never a multiple of 8
            n = int(rng.integers(2, 4)); C.add(f's{step}', n, *_random_structure(rng, n))
        for t in laws[:24] + laws[:8]:                              # repeats: hits, extensions and evictions
            want = _bits_have(C.XP, t)
            got = np.unpackbits(C.has(t), count=len(C)).astype(bool)
            assert (got == want).all()
        T = prng.sample(laws, 3)
        want = np.ones(len(C), bool)
        for t in T: want &= _bits_have(C.XP, t)
        assert (C.sat(T)[1] == want).all()
    assert len(C._cols) <= 16
    other = Corpus(store=tmp_path)                                  # a second process: rows in file order
    assert len(other) == len(C)
    for t in laws[:5]:
        assert (np.unpackbits(other.has(t), count=len(other)).astype(bool) == _bits_have(other.XP, t)).all()
        assert np.unpackbits(other.has(t)).sum() == np.unpackbits(C.has(t)).sum()
    assert C.sat([])[1].all() and len(C.sat([])[1]) == len(C)
