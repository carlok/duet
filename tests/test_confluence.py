"""The confluence checker must reject what it should, and certify A-D (open in the pilot) as refuted."""
from soup.confluence import critical_pairs, normal, parse_term, check
from soup.named import law_index


def test_detects_non_joinable_critical_pair():
    l, _ = parse_term('f(X,f(Y,Z))'); r, _ = parse_term('X')
    R = [(l, r)]
    assert any(normal(a, R) != normal(b, R) for a, b in critical_pairs(R))


def test_joinable_system_passes():
    l, _ = parse_term('g(X,g(X,Y))'); r, _ = parse_term('Y')
    R = [(l, r)]
    assert all(normal(a, R) == normal(b, R) for a, b in critical_pairs(R))


def test_A_does_not_imply_idempotence():
    T = [law_index(s) for s in ['x·(x∘x) = x', 'x∘(x∘y) = y', '((x∘y)∘x)·y = x']]
    assert check(T, law_index('x·x = x'))['ok']


def test_true_implication_is_not_certified():
    T = [law_index(s) for s in ['x·(x∘y) = x', 'x∘(x·y) = x']]
    assert not check(T, law_index('x·x = x'))['ok']
