"""soup.linear: rings, the exact coefficient test against the tables, and a refutation (24 Nov 2026)."""
import numpy as np

from soup.data import TREES
from soup.linear import _ev, claim, gf, holds, law_k, rings, tables, zmod
from soup.named import law_index


def test_gf_is_a_field():
    for p, k in [(2, 2), (2, 3), (3, 2), (2, 4)]:
        R = gf(p, k); q = R.q
        for x in range(1, q):
            assert (R.mul[x] == 1).sum() == 1                      # every nonzero element has one inverse
        x, y, z = np.indices((q, q, q)).reshape(3, -1)
        assert np.array_equal(R.mul[x, R.add[y, z]], R.add[R.mul[x, y], R.mul[x, z]])
        assert np.array_equal(R.mul[x, R.mul[y, z]], R.mul[R.mul[x, y], z])
        assert np.array_equal(R.add[x, R.add[y, z]], R.add[R.add[x, y], z])


def test_rings_in_size_order():
    names = [R.name for R in rings(9)]
    assert names == ['GF(2)', 'GF(3)', 'Z/4', 'GF(4)', 'GF(5)', 'Z/6', 'GF(7)', 'Z/8', 'GF(8)', 'Z/9', 'GF(9)']


def test_coefficient_test_matches_tables():
    """The exact test from coefficients agrees with evaluating the Cayley tables on every assignment."""
    rng = np.random.default_rng(1)
    laws = [int(i) for i in rng.choice(len(TREES), 400, replace=False) if law_k(int(i)) <= 3]
    for R in (zmod(4), gf(2, 2), gf(3, 1), zmod(6)):
        for _ in range(4):
            p = dict(zip('abcdef', (int(v) for v in rng.integers(0, R.q, 6))))
            P = {k: np.array([v], np.int16) for k, v in p.items()}
            F, G = tables(R, p)
            for i in laws:
                env = [a.ravel() for a in np.indices((R.q,) * law_k(i))]
                L, Rt = TREES[i]
                direct = bool(np.array_equal(_ev(L, env, F, G), _ev(Rt, env, F, G)))
                assert bool(holds(i, P, R, 1)[0]) == direct, (R.name, p, i)


def test_commutative_does_not_imply_associative():
    T = [law_index('x·y=y·x')]; goal = law_index('(x·y)·z=x·(y·z)')
    rec = claim(T, goal, qmax=8, affine_qmax=4, budget=60)
    assert rec['status'] == 'refuted' and rec['check'] == 'all'
    F, n = np.array(rec['F']), rec['q']
    assert (F == F.T).all()
    assert any(F[F[x, y], z] != F[x, F[y, z]] for x in range(n) for y in range(n) for z in range(n))


def test_no_model_for_a_true_implication():
    """Lattice absorption implies x·x = x, so the family has no countermodel."""
    T = [law_index('x·(x∘y)=x'), law_index('x∘(x·y)=x')]
    assert claim(T, law_index('x·x=x'), qmax=9, affine_qmax=5, budget=60)['status'] == 'none'
