"""Calibration checks on named theories (z3-solver 5.4.1.0)."""
import pytest

from soup.core import Corpus, prove, find_model
from soup.named import NAMED, law_index
from soup.duality import dualities, canonical, image
from soup.verify import verify

IDEM_F, IDEM_G = law_index('x·x = x'), law_index('x∘x = x')
ABS = [law_index(s) for s in NAMED['absorption pair']]


def test_lattice_model_counts():
    r = verify(Corpus(), [law_index(s) for s in NAMED['lattice']])
    assert [r['model_counts'][n] for n in (2, 3, 4)] == [1, 1, 2]


def test_absorption_synergy_proved():
    for t in ABS:   # each absorption law alone does not force idempotence
        assert isinstance(find_model([t], 2, goal=IDEM_F), tuple)
    st, effort = prove(ABS, IDEM_F)
    assert st == 'proved'
    assert effort == 494          # reference effort on z3 5.4.1 (cloud session)
    r = verify(Corpus(), ABS)
    proved = {c['law'] for c in r['claims'] if c['status'] == 'proved'}
    assert {'x · x = x', 'x ∘ x = x'} <= proved
    assert all(c.get('e_status') == 'proved' and c['e_steps'] > 0 for c in r['claims'] if c['status'] == 'proved')


def test_e_prover_reference_cases():
    from soup.provers import prove_e
    r = prove_e(ABS, IDEM_F)
    assert r['status'] == 'proved' and r['proof_steps'] == 9     # E 3.2.5, --auto
    assert prove_e(ABS[:1], IDEM_F)['status'] == 'countersatisfiable'
    mck = [law_index(s) for s in ['x·(y∘(x∘z)) = x', 'x∘(y·(x·z)) = x', '((y∘x)·(x∘z))·x = x', '((y·x)∘(x·z))∘x = x']]
    assert prove_e(mck, law_index('x·y = y·x'))['status'] == 'proved'


@pytest.mark.parametrize('name', list(NAMED))
def test_named_theories_have_a_duality(name):
    assert dualities([law_index(s) for s in NAMED[name]])


def test_canonical_is_duality_invariant():
    T = sorted(law_index(s) for s in NAMED['dimonoid'])
    for sw, op in ((1, 0), (0, 1), (1, 1)):
        assert canonical({image(t, sw, op) for t in T}) == canonical(T)


def test_vampire_agrees_with_e_on_reference_and_A_to_D():
    from soup.provers import prove_vampire
    assert prove_vampire(ABS, IDEM_F)['status'] == 'proved'
    for laws in (['x·(x∘x) = x', 'x∘(x∘y) = y', '((x∘y)∘x)·y = x'], ['(x·y)·y = x', '(x·x)∘x = x', 'x∘(y·(x·y)) = y'],
                 ['x·(x·x) = x', '(x·y)·y = x', '(x∘y)·(y∘x) = y'], ['x·(x∘x) = x', '(x∘y)·x = y', 'x·((y∘y)∘x) = x']):
        assert prove_vampire([law_index(s) for s in laws], IDEM_F)['status'] == 'countersatisfiable'


def test_mace4_model_is_parsed_correctly():
    import numpy as np
    from soup.core import law_vector
    from soup.provers import mace4
    r = mace4(ABS[:1], IDEM_F, 2, 4, 30)
    assert r['size'] == 2
    F, G = (np.array(x) for x in r['tables'])
    lv = law_vector(F, G, 2)
    assert lv[ABS[0]] and not lv[IDEM_F]
