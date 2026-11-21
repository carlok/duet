"""The offline checker accepts what it should and rejects what it should."""
import z3

from soup.check_offline import check_finite, prove_over_Z, check_s7, lemmas, check_lemmas
from soup.named import law_index

ABS = [law_index('x·(x∘y) = x'), law_index('x∘(x·y) = x')]
MIN = [[0, 0], [0, 1]]; MAX = [[0, 1], [1, 1]]


def test_finite_model_check():
    assert check_finite(ABS, [law_index('x·y = x')], MIN, MAX)['ok']          # the 2-element lattice
    assert not check_finite(ABS, [law_index('x·y = y·x')], MIN, MAX)['ok']    # commutativity holds there
    assert not check_finite(ABS, [law_index('x·y = x')], MIN, MIN)['ok']      # absorption fails
    assert not check_finite(ABS, [law_index('x·y = x')], [[0, 2], [0, 1]], MAX)['ok']   # out of range


def test_models_over_Z():
    comm = law_index('x·y = y·x')
    assert prove_over_Z(comm, lambda x, y: x + y, lambda x, y: x) == 'proved'
    assert prove_over_Z(comm, lambda x, y: x - y, lambda x, y: x) == 'counterexample'
    assert prove_over_Z(law_index('x·(x∘y) = x'), lambda x, y: z3.If(x <= y, x, y), lambda x, y: z3.If(x >= y, x, y)) == 'proved'


def test_s7_term_model():
    T = [law_index('x·x = x'), law_index('(x∘y)·(z∘(z·x)) = x')]
    r = check_s7(T, [law_index('x·(y·x) = x')], n_triples=20_000)
    assert r['ok'] and r['claims_fail_at_generators']['x · (y · x) = x']


def test_lemma_parsing_and_proof():
    body = ('  - E5. `x · (x ∘ x) = x`. E2 with y := x.\n'
            '  - E4. If `y · x = y` then `x · y = x`: not a lemma.\n'
            '```\nE6. x ∘ (x · x) = x\n```\n- E6: axiom 3 with ...\n')
    ls = lemmas(body)
    assert [n for n, *_ in ls] == ['E5', 'E6']
    res = check_lemmas(ABS, body)
    assert [x['status'] for x in res] == ['proved', 'proved']     # both follow from absorption
