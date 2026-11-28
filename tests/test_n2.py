"""N2 (PREREGISTRATION.md, N2; 28 Nov 2026): the dedupe's three outcomes, the level-5 range, and the C1, C2 and C5
rules of soup.novelty2."""
import numpy as np

from soup.dedupe import classes_of, pair_outcomes
from soup.novelty2 import LEDGER_N2, confirmed, param_mark


def _implied(table):
    def f(T):
        k = tuple(sorted(T))
        return table.get(k)
    return f


def test_three_outcomes_of_the_model_filter():
    NL = 10
    v = lambda *on: np.isin(np.arange(NL), on)
    # A = {1}, B = {2}: A's models satisfy 2 and B's satisfy 1 -> passes the filter (to be proved)
    # C = {3}: its models fail 1 and 2 -> separated from A and B; D = {4}: no corpus model -> never compared
    table = {(1,): v(1, 2), (2,): v(1, 2), (3,): v(3), (4,): None}
    cand = [{'key': k, 'T': [t]} for k, t in (('A', 1), ('B', 2), ('C', 3), ('D', 4))]
    rels = [('id', None)]
    never, sep, todo = pair_outcomes(cand, _implied(table), rels, lambda t, r: t)
    assert never == ['D']
    assert set(sep) == {('A', 'C'), ('B', 'C')}
    assert list(todo) == [('A', 'B')] and todo[('A', 'B')] == [('id', [2])]


def test_an_untestable_relabelling_leaves_the_pair_unknown_not_separated():
    NL = 10
    v = lambda *on: np.isin(np.arange(NL), on)
    table = {(1,): v(1), (3,): v(3)}
    cand = [{'key': 'A', 'T': [1]}, {'key': 'C', 'T': [3]}]
    rels = [('id', None), ('swap', 'x')]
    never, sep, todo = pair_outcomes(cand, _implied(table), rels, lambda t, r: None if r == 'x' else t)
    assert sep == [] and todo == {('A', 'C'): []}          # no prover call possible: it stays unknown


def test_level5_is_a_range():
    keys = list('ABCDE')
    eq = [('A', 'B')]; unknown = [('C', 'D')]
    up_multi, upper = classes_of(keys, eq)
    lo_multi, lower = classes_of(keys, eq + unknown)
    assert (upper, lower) == (4, 3)
    assert sorted(map(sorted, lo_multi)) == [['A', 'B'], ['C', 'D']]


def test_c1_c2_c5_rules():
    assert param_mark({'definitional': True, 'matches': ['x∘y = (x·y)·(z∘z)']}).startswith('definitional with a parameter')
    assert param_mark({'definitional': False}) is None and param_mark(None) is None
    assert {'a9295908', '71fd2cc6', '69dfbd8e'} <= set(LEDGER_N2)
    proved = [{'idx': 41, 'law': 'x ∘ y = y ∘ x'}, {'idx': 7, 'law': 'x · x = x'}]
    assert confirmed(proved, {'41': True, '7': False}) == [proved[0]]   # unconfirmed does not count as proved
    assert confirmed(proved, {}) == []
