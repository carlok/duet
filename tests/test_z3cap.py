"""The wall-time cap on z3 proofs (V8, after X12's deviation 13): z3 ran 5.2 and 7.3 h on stage a's redundancy proofs
of two fusion5 theories at rlimit 10M, without reaching the rlimit. With core.prove(..., secs) every such proof ends."""
import time

from soup.core import prove
from soup.verify import CONFIGS

# one of the two theories that hung in X12 (x12-f5, key 52ef5b80...; notes/x12_hang.py)
STUCK = [14, 17, 5027, 17379, 28801]


def test_capped_redundancy_proofs_end():
    for t in STUCK:
        rest = [u for u in STUCK if u != t]
        t0 = time.time()
        st, used = prove(rest, t, 10_000_000, secs=3)
        assert time.time() - t0 < 15, f'law {t}: {time.time() - t0:.0f} s'
        assert st in ('proved', 'unknown')


def test_v8_is_v7_plus_caps():
    v7, v8 = CONFIGS['V7'], CONFIGS['V8']
    assert 'z3_secs' not in v7 and 'c_z3_secs' not in v7          # V7 stays as X9-X12 ran it
    assert v8['z3_secs'] == 120 and v8['c_z3_secs'] == 1800
    assert {k: v for k, v in v8.items() if k not in ('z3_secs', 'c_z3_secs')} == v7
