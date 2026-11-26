"""Arm 'fusion5' (after X10, 26 Nov 2026): the search-side parameter-disguise skip (soup.paramskip)."""
import numpy as np

from soup.core import Corpus
from soup.named import law_index
from soup.paramskip import CF, CG, DIRECTION, NTERMS, OP, PLEN, PROGS, X, Y, ParamSkip, _match, term_str
from soup.profile import all_models


def T(ls): return sorted(law_index(s.replace(' ', '')) for s in ls)


D40846 = ['x · (x · y) = y', 'x · (y ∘ x) = (y · z) ∘ z', '(x · (y ∘ (y ∘ z))) · z = x']   # X10; V6: a parameter definition
C94D69 = ['x · (y · x) = y ∘ y', '(x ∘ y) · x = y ∘ x', '(x · x) · x = (y ∘ x) ∘ x']        # X4 candidate, funnel level 7


def test_terms():
    assert NTERMS == 2 * 2504
    for i in range(NTERMS):
        p = list(PROGS[i, :PLEN[i]])
        assert p.count(X) == 1 and p.count(Y) == 1 and p.count(CF) + p.count(CG) >= 1 and 2 <= p.count(OP) <= 4
    names = {term_str(i) for i in range(NTERMS)}
    assert 'x ∘ y = (x · (z·z · (y · z∘z)))' in names      # X10's disguise
    assert 'x ∘ y = (x · (y · z∘z))' in names              # X6's
    assert 'x · y = (x ∘ (z·z ∘ (y ∘ z∘z)))' in names      # the same, the other way round


def test_kernel_on_a_constructed_disguise():
    # · = XOR on Z/2 x Z/2, ∘ = XOR translated by a = 1: z·z = 0 and z∘z = a for every z, so ∘ = x·(y·(z∘z))
    n, a = 4, 1
    F = np.array([[x ^ y for y in range(n)] for x in range(n)]); G = F ^ a
    ok = _match(PROGS, PLEN, DIRECTION, F.ravel().astype(np.int64), G.ravel().astype(np.int64),
                np.array([0], np.int64), np.array([n], np.int64), np.array([0], np.int64))
    hits = {term_str(i) for i in np.flatnonzero(ok)}
    assert 'x ∘ y = (x · (y · z∘z))' in hits and 'x ∘ y = (z∘z · (x · y))' in hits
    assert 'x ∘ y = (x · (y · z·z))' not in hits           # z·z = 0: that term is x XOR y, not ∘


def test_a_disguise_is_skipped():
    C = Corpus()                                           # base probes, plus the theory's own models on 2-4 elements
    for k in (2, 3, 4):
        for m in all_models(T(D40846), k, 300, 60)[0]: C.add('test', *m)
    PS = ParamSkip(C)
    assert PS.check(T(D40846)) and PS.fired == 1
    assert PS.check(T(D40846)) and PS.fired == 1           # cached


def test_a_thin_corpus_is_corrected_by_mace4():
    C = Corpus()                                           # base probes only: too few models of C94D69
    PS = ParamSkip(C)
    assert len(PS.matches(T(C94D69))) > 0                  # step 1 alone would skip it
    assert not PS.check(T(C94D69))                         # Mace4 finds models where the terms fail
    assert PS.added >= 1 and len(C) == PS.added and not len(PS.matches(T(C94D69)))
    no = ParamSkip(Corpus(), confirm=False)
    assert no.check(T(C94D69))                             # without the confirmation it is skipped
