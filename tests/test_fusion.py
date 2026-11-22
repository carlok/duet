"""Arm 'fusion' and verifier V5 (PREREGISTRATION.md, X4): off-diagonal gain, the 2-element-lattice exclusion, pools."""
import numpy as np

from soup.core import Corpus, LAWS
from soup.named import law_index
from soup.paths import data
from soup.offdiag import ONEVAR, ONLY_F, ONLY_G, lat2, offdiag_gain, pools
from soup.verify import fusion_gain

C = Corpus()          # base probes only: deterministic, independent of any run's corpus

# McKenzie's 1970 lattice basis (· = join, ∘ = meet); none of the four laws is commutativity or associativity
MCKENZIE = ['x·(y∘(x∘z))=x', 'x∘(y·(x·z))=x', '((y∘x)·(x∘z))·x=x', '((y·x)∘(x·z))∘x=x']
ABSORPTION = ['x·(x∘y)=x', 'x∘(x·y)=x']
DELTA = ['(x·y)∘(y·x)=x', '(x∘y)·(y∘x)=x']


def T(ls): return sorted(law_index(s) for s in ls)


def test_onevar_and_pure_masks():
    assert ONEVAR[law_index('x·x=x')] and ONEVAR[law_index('x·x=x∘x')]
    assert not ONEVAR[law_index('x·y=y·x')]
    assert ONLY_F[law_index('x·y=y·x')] and ONLY_G[law_index('x∘y=y∘x')]
    assert not ONLY_F[law_index('x·(x∘y)=x')] and not ONLY_G[law_index('x·(x∘y)=x')]


def test_lat2_holds_lattice_laws_only():
    L = lat2()
    assert all(L[t] for t in T(MCKENZIE + ABSORPTION + ['x·y=y·x', '(x·y)·z=x·(y·z)']))
    assert not all(L[t] for t in T(DELTA))


def test_mckenzie_has_offdiagonal_synergy():
    # positive control (PREREGISTRATION.md, X4): commutativity of both operations follows from the basis, and no single
    # law together with the one-variable consequences (idempotence, ...) gives it on the corpus
    g = set(offdiag_gain(C, T(MCKENZIE)).tolist())
    for law in ['x·y=y·x', 'x∘y=y∘x']:
        assert law_index(law) in g, law


def test_mckenzie_associativity_needs_the_found_structures():
    # Associativity also follows from the basis, but on the base probes alone it looks covered: all 61 base structures
    # satisfying x·(y∘(x∘z)) = x plus the one-variable laws happen to be ·-associative (22 Nov 2026). The main corpus
    # (structures found by the runs) has the witnesses. A growing corpus only removes laws from the covered sets, and
    # associativity is a theorem of the basis, so once in the gain it stays there.
    assert law_index('(x·y)·z=x·(y·z)') not in set(offdiag_gain(C, T(MCKENZIE)).tolist())
    g = set(offdiag_gain(Corpus(store=data('corpus')), T(MCKENZIE)).tolist())
    for law in ['(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)']:
        assert law_index(law) in g, law


def test_diagonal_laws_never_count():
    t = T(ABSORPTION)
    idem = law_index('x·x=x')
    assert idem in set(fusion_gain(C, t).tolist())          # the classical emergent law of the absorption pair ...
    g = offdiag_gain(C, t)
    assert idem not in set(g.tolist()) and not ONEVAR[g].any()   # ... is on the diagonal, so it does not count


def test_pools_are_one_operation_and_nonempty():
    pf, pg = pools(C)
    assert len(pf) > 10 and len(pg) > 10
    assert ONLY_F[pf].all() and ONLY_G[pg].all()
