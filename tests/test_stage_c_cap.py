"""The stage-c cap and the drain rule (after X9, 25 Nov 2026).

X9: once pending was empty, every verifier took a stage-c task (six at once tripped the memory rule), and since no
verifier went idle the rebalancer never started a searcher. With --cap-c the stage-c lane holds at most N claimed
tasks, the verifiers it turns away go idle, and the rebalancer makes them searchers down to N + 1 verifiers.
"""
import multiprocessing as mp
import os
import time
from pathlib import Path
from types import SimpleNamespace

from soup.stream.fqueue import FileQueue

CAP = {'stage2c': 3}
AB_FIRST = ('pending', 'stage2c')


def test_cap_turns_verifiers_away(tmp_path):
    Q = FileQueue(tmp_path)
    for i in range(6): Q.push(f'c{i}', {'T': [i]}, 0.1 * i, lane='stage2c')
    got = [Q.claim(f'v{i}', AB_FIRST, CAP) for i in range(4)]
    assert all(got[:3]) and got[3] is None                   # nothing pending, stage c full: v3 goes idle
    assert Q.running('stage2c') == 3
    Q.push('p0', {'T': [9]}, 1.0)
    _, t = Q.claim('v3', AB_FIRST, CAP); assert t['key'] == 'p0'
    Q.done(got[0][0]); _, t = Q.claim('v4', AB_FIRST, CAP); assert t['lane'] == 'stage2c'
    assert Q.running('stage2c') == 3
    assert Q.claim('v5', AB_FIRST) is not None               # no cap: what X9 did (a fourth stage-c task)


def test_stale_lock_is_removed(tmp_path):
    Q = FileQueue(tmp_path)
    Q.push('c0', {'T': [1]}, 0.1, lane='stage2c')
    lock = Path(tmp_path) / '.lock_stage2c'
    lock.touch(); assert Q.claim('v0', ('stage2c',), CAP) is None      # held by someone: lane skipped this round
    old = time.time() - 120; os.utime(lock, (old, old))
    assert Q.claim('v0', ('stage2c',), CAP) is not None                 # left by a killed worker: removed
    assert not lock.exists()


def _claimer(args):
    root, name = args
    Q = FileQueue(root); t_end = time.time() + 1.5
    while time.time() < t_end:
        if Q.claim(name, AB_FIRST, CAP): return 1
    return 0


def test_cap_holds_under_concurrent_claims(tmp_path):
    Q = FileQueue(tmp_path)
    for i in range(12): Q.push(f'c{i}', {'T': [i]}, 0.01 * i, lane='stage2c')
    with mp.get_context('spawn').Pool(8) as pool:
        won = pool.map(_claimer, [(str(tmp_path), f'v{i}') for i in range(8)])
    assert sum(won) == 3 and Q.running('stage2c') == 3


def test_floors_and_idle():
    from soup.stream.supervisor import verifier_floor, is_idle
    assert verifier_floor(SimpleNamespace(), 5) == 2                    # no cap: as before X9
    assert verifier_floor(SimpleNamespace(cap_c=3), 0) == 2
    assert verifier_floor(SimpleNamespace(cap_c=3), 3) == 4             # three on stage c and one free
    assert is_idle({'state': 'idle', 't': 10}, 5)
    assert not is_idle({'state': 'idle', 't': 1}, 5)                    # an earlier run's heartbeat
    assert not is_idle({'state': 'stage c', 't': 10}, 5) and not is_idle(None, 5)


class _P:
    def __init__(self, name, prefer):
        self.name, self.role, self.prefer, self.t0, self.retiring = name, 'verify', prefer, 0.0, False
        self.p = SimpleNamespace(poll=lambda: None)


def _drain(tmp_path, monkeypatch, cap_c):
    """X9's end state: 7 verifiers, no searcher, nothing pending, a stage-c backlog."""
    import soup.stream.supervisor as S
    Q = FileQueue(tmp_path)
    for i in range(10): Q.push(f'c{i}', {'T': [i]}, 0.1, lane='stage2c')
    caps = {'stage2c': cap_c} if cap_c else None
    state = {}
    for i in range(7):
        got = Q.claim(f'v{i}', ('stage2c', 'pending') if i == 0 else AB_FIRST, caps)
        state[f'v{i}'] = 'stage c' if got else 'idle'
    sup = object.__new__(S.Supervisor)
    sup.a = SimpleNamespace(arm='fusion4', cap_c=cap_c, min_searchers=1, verifiers=7)
    sup.Q, sup.results = Q, {}
    sup.procs = {f'v{i}': _P(f'v{i}', 'c' if i == 0 else 'ab') for i in range(7)}
    monkeypatch.setattr(S, 'read_json', lambda path: {'state': state[Path(path).stem], 't': 1.0})
    started = []
    sup.start_searcher = lambda: started.append(1) or f's{len(started)}'
    sup.retire = lambda p: setattr(p, 'retiring', True)
    for _ in range(8): sup.rebalance()
    return len(started), sum(not p.retiring for p in sup.procs.values()), Q.running('stage2c')


def test_drain_turns_back_into_search(tmp_path, monkeypatch):
    assert _drain(tmp_path / 'x9', monkeypatch, 0) == (0, 7, 7)         # X9: all on stage c, no searcher
    assert _drain(tmp_path / 'cap', monkeypatch, 3) == (3, 4, 3)        # cap 3: 3 searchers, 4 verifiers
