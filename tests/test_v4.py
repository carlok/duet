"""Verifier V4's screens for known disguises (PREREGISTRATION.md, X3), on three candidates of 22 Nov 2026."""
from soup.core import Corpus
from soup.named import law_index
from soup.paths import data
from soup.verify import V4, screens

SPLIT = ['x·(x·y)=y', '(x∘y)∘y=x', 'x∘(x∘(x·y))=x', '((x∘y)·y)·y=y']                          # 4dc33674
DIVISION = ['x·(y∘x)=y∘y', 'x·x=(y·x)∘y', 'x∘(x∘((y·z)∘x))=x', '((x·(y∘z))·x)·x=x']          # 8a512957
NEITHER = ['x·(y∘x)=x·x', 'x∘(y·x)=x∘x', '(x∘y)·x=x·x', '(x·y)∘x=x∘x', '(x∘y)·(y∘x)=x', '(x·y)∘(y·x)=x']  # 10c98c4b

C = Corpus(store=data('corpus'))


def T(ls): return sorted(law_index(s) for s in ls)


def test_split_is_screened():
    assert screens(C, T(SPLIT), [], V4).get('hit') == 'split'


def test_division_is_screened():
    r = screens(C, T(DIVISION), [], V4)
    assert r.get('hit') == 'division' and any('left quasigroup' in t or 'right quasigroup' in t for t in r['division'])


def test_orthogonality_candidate_passes():
    assert screens(C, T(NEITHER), [], V4).get('hit') is None
