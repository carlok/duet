"""Verifier V7 (PREREGISTRATION.md, X9): no z3 after an E proof, and the linear-model screen in stage b."""
from soup.core import Corpus, LAWS, ORDER
from soup.named import law_index
from soup.verify import CONFIGS, V6, V7, stage_b


def _out(laws, claim):
    T = sorted(law_index(s) for s in laws); e = law_index(claim)
    return {'T': T, 'laws': [LAWS[t] for t in T], 'model_sizes': [3], 'model_counts': {3: 1}, 'richness': 1,
            'claims': [{'law': LAWS[e], 'idx': e, 'order': int(ORDER[e]), 'status': 'pending'}]}


def test_config():
    assert CONFIGS['V7'] is V7
    assert V7['z3_after_e'] is False and V7['linear_secs'] and V7['c_linear_secs']
    new = ('z3_after_e', 'linear_secs', 'linear_qmax', 'linear_affine_qmax', 'c_linear_secs')
    assert {k: v for k, v in V7.items() if k not in new} == V6


def test_no_z3_after_an_e_proof():
    out = stage_b(Corpus(), _out(['x·(x∘y)=x', 'x∘(x·y)=x'], 'x·x=x'), V7)       # absorption forces idempotence
    c = out['claims'][0]
    assert c['status'] == 'proved' and c['e_status'] == 'proved' and c.get('z3_skipped')
    assert 'effort' not in c and c['difficulty'] == round(c['e_steps'] / 10, 3)


def test_linear_screen_refutes_in_stage_b():
    """X8's 24e6b56a: E's small run leaves x·y = y·x open; a linear model on Z/9 refutes it."""
    C = Corpus()
    out = stage_b(C, _out(['(x·y)·(y·(x∘y))=y', '(x·y)·((z∘y)·z)=x'], 'x·y=y·x'), V7)
    c = out['claims'][0]
    assert c['status'].startswith('false (size 9, linear model over Z/9')
    assert c['linear']['check'] == 'all' and 'fmb' not in c
    assert any(name == 'cm-linear-9' for name, *_ in C.tables)
