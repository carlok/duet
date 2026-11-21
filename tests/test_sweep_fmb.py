"""Vampire's finite model builder, as used by soup.sweep_fmb: a model it returns passes our own check."""
from soup.check_offline import check_finite
from soup.named import law_index
from soup.sweep_fmb import fmb

ABS = [law_index('x·(x∘y) = x'), law_index('x∘(x·y) = x')]


def test_fmb_finds_a_checked_countermodel():
    comm = law_index('x·y = y·x')                   # absorption alone does not force commutativity
    st, m, out = fmb(ABS, comm, secs=30)
    assert st == 'model' and m['n'] >= 2
    assert check_finite(ABS, [comm], m['f'], m['g'])['ok']


def test_v3_fmb_step_refutes_with_a_checked_model():
    from soup.core import Corpus
    from soup.verify import _fmb, V2, V3
    assert 'fmb_secs' not in V2 and V3['fmb_secs'] > 0          # V2 (T4) is unchanged
    c = {'idx': law_index('x·y = y·x'), 'status': 'pending'}
    assert _fmb(Corpus(), c, ABS, 30, 2)
    assert c['status'].startswith('false (size') and c['status'].endswith('Vampire FMB)')


def test_fmb_does_not_refute_a_consequence():
    st, m, _ = fmb(ABS, law_index('x·x = x'), secs=10)   # absorption implies idempotence: no finite countermodel
    assert m is None and st != 'model'
