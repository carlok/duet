"""Model families: they find what exists, report none where nothing exists, and every model is checked."""
from soup.families import cyclic, check_tables, z_piecewise
from soup.named import law_index

COMM = [law_index('x·y = y·x')]
IDEM = law_index('x·x = x')
ABS = [law_index('x·(x∘y) = x'), law_index('x∘(x·y) = x')]


def test_cyclic_finds_commutative_non_idempotent_model():
    assert cyclic(COMM, IDEM, 2) is None                 # needs F[1] - F[1] = 1 mod 2: impossible
    F, G = cyclic(COMM, IDEM, 3)
    assert check_tables(COMM, IDEM, F, G)


def test_cyclic_respects_a_true_implication():
    for n in (2, 3, 4, 5):
        assert cyclic(ABS, IDEM, n) is None              # absorption implies idempotence


def test_z_piecewise_model_is_proved_over_Z():
    m = z_piecewise(COMM, IDEM, W=0, slopes=range(0, 2))
    assert isinstance(m, dict)
    assert z_piecewise(ABS, IDEM, W=0, slopes=range(0, 2)) is None
