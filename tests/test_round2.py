"""The 10-element countermodel of S10 (found by Vampire's finite model builder in round 2, 21 Nov 2026) and the
parser that reads Vampire's FiniteModel block."""
from soup.check_offline import check_finite
from soup.named import law_index
from soup.provers import parse_vampire_model

S12 = [law_index(s) for s in ('x·(y∘(y∘(x∘y))) = x', 'x∘(y·(y·(x·y))) = x',
                               '(((x∘y)∘x)∘x)·y = y', '(((x·y)·x)·x)∘y = y')]
S10 = S12 + [law_index('x·x = x∘x')]
F = [[1, 2, 3, 5, 5, 3, 3, 5, 0, 0], [6, 1, 5, 1, 5, 5, 6, 1, 1, 1], [0, 1, 2, 3, 4, 5, 6, 2, 8, 2],
     [4, 1, 4, 3, 4, 5, 3, 1, 3, 3], [6, 6, 4, 4, 4, 5, 6, 4, 8, 4], [6, 5, 5, 5, 5, 5, 6, 6, 5, 5],
     [4, 6, 6, 3, 6, 6, 6, 6, 6, 6], [0, 1, 2, 3, 4, 5, 6, 7, 7, 9], [6, 1, 8, 3, 8, 5, 3, 7, 8, 9],
     [6, 5, 2, 3, 5, 5, 3, 9, 9, 9]]
G = [[1, 2, 9, 0, 9, 0, 9, 8, 9, 8], [9, 1, 9, 3, 9, 1, 1, 7, 8, 9], [7, 2, 2, 2, 2, 2, 2, 7, 2, 9],
     [7, 3, 9, 3, 3, 3, 6, 8, 8, 9], [0, 0, 2, 3, 4, 4, 4, 7, 4, 9], [7, 1, 2, 3, 4, 5, 5, 8, 8, 9],
     [0, 1, 2, 6, 4, 5, 6, 7, 8, 9], [2, 7, 7, 7, 7, 7, 7, 7, 8, 7], [2, 8, 2, 8, 4, 8, 2, 8, 8, 8],
     [7, 7, 9, 9, 7, 9, 7, 7, 8, 9]]


def test_s10_countermodel():
    r = check_finite(S10, [law_index(s) for s in ('x·x = x', 'x∘x = x', 'x·(x·x) = x')], F, G)
    assert r['ok'] and r['nondeg'] and r['law_vector_agrees']
    r = check_finite(S12, [law_index('x·x = x'), law_index('x∘x = x')], F, G)     # S10 models are S12 models
    assert r['ok']
    assert not check_finite(S12, [law_index('x·x = x∘x')], F, G)['ok']           # that claim stays open


def test_parse_vampire_model():
    out = ("% SZS output start FiniteModel for t\n"
           "tff('declare_$i1',type,'fmb_$i_1':$i).\ntff('declare_$i2',type,'fmb_$i_2':$i).\n"
           "tff(function_f,axiom,\n f('fmb_$i_1','fmb_$i_1') = 'fmb_$i_2'\n & f('fmb_$i_1','fmb_$i_2') = 'fmb_$i_1'\n"
           " & f('fmb_$i_2','fmb_$i_1') = 'fmb_$i_1'\n & f('fmb_$i_2','fmb_$i_2') = 'fmb_$i_2'\n).\n"
           "% SZS output end FiniteModel for t\n")
    assert parse_vampire_model(out) == {'n': 2, 'f': [[1, 0], [0, 1]], 'g': None}
    assert parse_vampire_model(out.replace("& f('fmb_$i_2','fmb_$i_2') = 'fmb_$i_2'\n", '')) is None   # incomplete
    assert parse_vampire_model('% SZS status Timeout') is None
