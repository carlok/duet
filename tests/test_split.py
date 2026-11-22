"""Split theories: a ·-theory and a ∘-theory side by side, whatever the bridges look like."""
from soup.named import NAMED, law_index
from soup.split import check, holds


def test_disguised_bridges_are_split():
    # candidate 4dc33674: both bridges reduce to one-operation laws through the involutions
    T = [law_index(s) for s in ('x·(x·y)=y', '(x∘y)∘y=x', 'x∘(x∘(x·y))=x', '((x∘y)·y)·y=y')]
    assert check(T)['split'] is True


def test_five_variable_laws():
    # order 4 allows 5 variables; the T4 scan crashed on these before the fix
    t = law_index('((x·y)·(z·w))·u=x')
    left = [[a for b in range(3)] for a in range(3)]; right = [[b for b in range(3)] for a in range(3)]
    assert holds([t], left, left) and not holds([t], right, right)


def test_lattices_are_not_split():
    T = [law_index(s) for s in NAMED['lattice']]
    r = check(T)
    assert r['split'] is False
    w = r['witness']; assert not holds(T, w['F'], w['G'])
