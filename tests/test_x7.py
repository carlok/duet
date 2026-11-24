"""Arm 'fusion4' (X7): the known library (soup.known), the seen-before skip, the distinct counter, the memory stop."""
import json
import os
import tempfile

import numpy as np

from soup.core import Corpus
from soup.named import law_index
from soup.paths import data
from soup.known import build, Library


def T(ls): return sorted(law_index(s.replace(' ', '')) for s in ls)


ABSORPTION = ['x·(x∘y)=x', 'x∘(x·y)=x']
EBB197CC = ['x · ((y · y) ∘ x) = z ∘ z', 'x ∘ ((y · (y ∘ x)) · y) = y', '(x ∘ y) ∘ (y · (x · x)) = x',
            '((x · x) ∘ (y · x)) ∘ x = y', '((x ∘ (x · y)) · y) ∘ x = x']      # X5, ledger row 12
C55 = ['x · (x ∘ y) = x', 'x · y = ((y · z) · x) ∘ x']
C38 = ['x · (x · y) = y', '(x · y) · y = x', 'x ∘ (x · y) = x ∘ y', '(x · x) ∘ (x ∘ x) = x', '(x · (x · x)) ∘ x = x']

_OUT = tempfile.mkdtemp()
build(_OUT, notes=os.environ.get('SOUP_NOTES', '/notes'))
C = Corpus(store=data('corpus'))
LIB = Library(C, _OUT)


def cls(th):
    t = T(th); imp = C.implied(t)
    assert imp is not None, th
    return LIB.classify(t, imp)


def test_library_built():
    lib = json.load(open(os.path.join(_OUT, 'known_library.json')))
    assert any(e['kind'] == 'known' for e in lib) and any(e['kind'] == 'candidate' for e in lib)
    assert len(json.load(open(os.path.join(_OUT, 'seen_before.json')))) > 1000


def test_known_are_skipped():
    assert cls(ABSORPTION) == 'known'          # a fragment of lattices
    assert cls(EBB197CC) in ('known', 'candidate')   # ledger row 12 (a known identification), or its own candidate


def test_unidentified_candidates_are_skipped_only_as_equivalents():
    assert cls(C55) == 'candidate' and cls(C38) == 'candidate'
    t = T(C55 + ['x·x=x'])                     # a strengthening of an unidentified candidate is new ground
    imp = C.implied(t)
    assert imp is None or LIB.classify(t, imp) != 'candidate'


def test_distinct_counter():
    from soup.stream.searcher import BLOOM_BITS
    import math
    bloom = np.zeros(BLOOM_BITS // 8, np.uint8); rng = np.random.default_rng(1)
    keys = rng.integers(0, 2**62, 200_000)
    for k in list(keys) + list(keys[:50_000]):           # 50,000 repeats
        h = hash(int(k)) & (BLOOM_BITS - 1); bloom[h >> 3] |= np.uint8(1 << (h & 7))
    fill = int(np.bitwise_count(bloom).sum(dtype=np.int64))
    est = -BLOOM_BITS * math.log(1 - fill / BLOOM_BITS)
    assert abs(est - 200_000) / 200_000 < 0.01


def test_memory_stop_reader():
    from soup.stream.supervisor import mem_available_mb
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('MemTotal: 12000000 kB\nMemAvailable:     700000 kB\n')
    assert mem_available_mb(f.name) == 683
    assert mem_available_mb('/nonexistent') is None


def test_searcher_floor():
    from types import SimpleNamespace
    from soup.stream.supervisor import searcher_floor
    assert searcher_floor(SimpleNamespace()) == 1                     # old runs: retire down to one searcher
    assert searcher_floor(SimpleNamespace(min_searchers=0)) == 1
    assert searcher_floor(SimpleNamespace(min_searchers=8)) == 8      # X8: 8 searchers stay
