"""C4 (28 Nov 2026): the single-cell hypothesis, syntactic (soup.sc)."""
from soup.named import law_index
from soup.data import TREES
from soup.sc import classify, law_kind


def K(s, op='g'): return law_kind(*TREES[law_index(s)], op)


def test_law_kinds():
    assert K('x·(y·z)=x·y') == 'free'
    assert K('((x∘y)·(z·z))·x=x') == 'constraint'           # 1f430506's B: one ∘ cell
    assert K('(x·y)·(x∘z)=z∘x') == 'constraint-swap'        # 1f430506's A: (x,z) and (z,x)
    assert K('x∘(x·y)=x∘y') == 'tie'                        # 3818b88f
    assert K('x∘(y∘z)=x∘y') == 'bad'                        # ∘ inside ∘
    assert K('x·(x∘y)=y∘(x·x)') == 'bad'                    # two different cells, not a tie


def test_classify_needs_commutativity_for_a_swap():
    A, B = law_index('(x·y)·(x∘z)=z∘x'), law_index('((x∘y)·(z·z))·x=x')
    assert classify([A, B], 'g', comm=True) == 'SC'
    assert classify([A, B], 'g', comm=False) == 'neither'
    tie = law_index('x∘(x·y)=x∘y')
    assert classify([B, tie], 'g', comm=False) == 'SC+ties'
