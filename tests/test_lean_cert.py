"""soup.lean_cert: the packed table encoding (24 Nov 2026). Lean itself runs in lean/check.sh, not here."""
from soup.lean_cert import module, packed, unpack

COMM = ('x · y = y · x', (('f', ('v', 0), ('v', 1)), ('f', ('v', 1), ('v', 0))))


def test_packed_round_trip():
    T = [[1, 0, 2], [0, 2, 1], [2, 1, 0]]
    assert unpack(packed(T, 3), 3) == T
    assert packed([[0, 0, 0], [0, 0, 2], [0, 0, 0]], 3) == 486      # the example of packed-table-footprint


def test_module_encodings():
    T3 = [[(x + y) % 3 for y in range(3)] for x in range(3)]
    src = module('A', [COMM], [], 3, T3, T3, 'test')
    assert 'def Ftbl : Nat :=' in src and 'Nat.mod_lt _ (by decide)' in src
    assert 'exponentiation.threshold' not in src and '![' not in src
    assert '![' in module('B', [COMM], [], 3, T3, T3, 'test', encoding='vec')
    n = 17; T = [[(x + y) % n for y in range(n)] for x in range(n)]
    assert f'set_option exponentiation.threshold {n * n}' in module('C', [COMM], [], n, T, T, 'test')
