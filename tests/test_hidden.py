"""Hidden definitional theories: one operation a term in the other."""
from soup.hidden import hidden
from soup.named import NAMED, law_index


def test_lattice_is_not_definitional():
    assert hidden([law_index(s) for s in NAMED['lattice']])['definitional'] is False


def test_swapped_operation_is_found():
    T = [law_index(s) for s in ('x∘y=y·x', 'x·(x·y)=y')]
    h = hidden(T)
    assert h['definitional'] and any(m['term'] == '(y · x)' and m['e'] == 'proved' for m in h['matches'])
