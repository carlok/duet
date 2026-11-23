"""The two filters X5 called for (23 Nov 2026): definitions with a constant square (soup.hidden.hidden_param, the V6
screen) and argument-ignoring laws whose ignored variable may occur more than once (soup.offdiag.IGNORE2, arm
'fusion3')."""
from soup.named import law_index
from soup.offdiag import IGNORE, IGNORE2
from soup.hidden import hidden_param
from soup.verify import V6


def T(ls): return sorted(law_index(s.replace(' ', '')) for s in ls)


EBB197CC = ['x · ((y · y) ∘ x) = z ∘ z', 'x ∘ ((y · (y ∘ x)) · y) = y', '(x ∘ y) ∘ (y · (x · x)) = x',
            '((x · x) ∘ (y · x)) ∘ x = y', '((x ∘ (x · y)) · y) ∘ x = x']          # X5 rank 1, ledger row 12
C55CB2C91 = ['x · (x ∘ y) = x', 'x · y = ((y · z) · x) ∘ x']
ABSORPTION = ['x·(x∘y)=x', 'x∘(x·y)=x']


def test_ignore2_mask():
    assert int(IGNORE.sum()) == 53 and int(IGNORE2.sum()) == 187 and (IGNORE <= IGNORE2).all()
    for law in ['x·(x·x)=y·(x·y)', 'x·x=y·y', 'x·(x·y)=x·(x·z)', 'x·x=x·y']:
        assert IGNORE2[law_index(law)], law
    for law in ['x·(x·y)=x·x', 'x·(x·y)=y', 'x·y=y·x', '(x·y)·z=x·(y·z)', 'x·(x∘y)=x', 'x·x=x', 'x·y=x']:
        assert not IGNORE2[law_index(law)], law


def test_param_definition_catches_x5_steiner_translate():
    h = hidden_param(T(EBB197CC))
    assert h['models'] > 0 and h['definitional'], h


def test_param_definition_spares_genuine_fusions():
    for th in (C55CB2C91, ABSORPTION):
        h = hidden_param(T(th))
        assert h['models'] > 0 and not h['definitional'], (th, h)


def test_v6_has_the_screen():
    assert V6['param_screen'] and V6['offdiag'] and V6['split_screen'] and V6['division_screen']
