"""Arm 'fusion7' (X13, 28 Nov 2026): fusion6 with a rolling rescore inside a fixed share of searcher time
(Searcher._roll). The exact incremental rescore was measured first and saves nothing (notes/x13_replay.out)."""
from soup.stream import searcher as sm
from soup.stream.searcher import ROLL_SHARE, Searcher


class _Clock:
    def __init__(self, t): self.t = t
    def __call__(self): return self.t


def _stub(n_elites, corpus_len=10, cost=1.0, drop=()):
    """A searcher with n_elites fake elites, all scored on a corpus of 5 structures (stale), oldest first by t_scored.
    Its surrogate costs `cost` seconds on a fake clock and returns None for the laws in `drop`."""
    S = Searcher.__new__(Searcher)
    S.rolling = True; S.family = True; S.stale = False
    S.t_rescore = 1000.0; S.rescores = 0; S.rescore_secs = 0.0; S.rolled = 0; S.roll_lag = 0.0
    S.clock = _Clock(2000.0)
    S.C = list(range(corpus_len))                   # only len() is used
    S.verified = {}; S.archive = {}; S.where = {}; S.calls = []
    for i in range(n_elites):
        e = {'T': [i, 10_000 + i], 'key': f'k{i}', 'cheap': 1.0, 'desc': (i,), 'n_scored': 5, 't_scored': float(i)}
        S.archive[e['desc']] = e; S.where[e['key']] = e['desc']

    def surrogate(T):
        S.calls.append(T[0]); S.clock.t += cost
        if T[0] in drop: return None
        return {'T': T, 'cheap': 2.0, 'desc': (T[0],), 'n_scored': len(S.C), 't_scored': S.clock()}

    def insert(s, push=True):
        assert push is False
        s['key'] = f'k{s["T"][0]}'; S.archive[s['desc']] = s; S.where[s['key']] = s['desc']; return True
    S.surrogate = surrogate; S.insert = insert
    return S


def test_fusion7_is_a_family_arm_with_the_rolling_rescore():
    for sets in (sm.FUSION_ARMS, sm.RIGID_ARMS, sm.FAMILY_ARMS, sm.PSKIP_ARMS, sm.LIB_ARMS):
        assert 'fusion6' in sets and 'fusion7' in sets
    assert sm.ROLLING_ARMS == ('fusion7',)


def test_the_pass_stays_inside_its_share_of_the_time_since_the_last_one():
    S = _stub(100)
    now = S.t_rescore + 100.0                       # 100 s since the last pass: a budget of ROLL_SHARE * 100 s
    S.clock.t = now
    assert S._maybe_rescore(True, now=now)
    budget = ROLL_SHARE * 100.0
    assert len(S.calls) == int(budget)              # one elite costs 1 s: it stops once the budget is used
    assert S.rescore_secs == len(S.calls) and S.rolled == len(S.calls)
    assert S.t_rescore == now + len(S.calls)        # the next budget counts from the end of this pass


def test_oldest_scored_first_and_fresh_elites_left_alone():
    S = _stub(30)
    for i in range(0, 30, 2):                       # every even elite was scored on the current corpus
        S.archive[(i,)]['n_scored'] = len(S.C)
    now = S.t_rescore + 1000.0; S.clock.t = now     # budget 100 s: enough for all
    S._maybe_rescore(False, now=now)
    assert S.calls == list(range(1, 30, 2))         # only the stale ones, in order of t_scored
    assert all(e['n_scored'] == len(S.C) for e in S.archive.values())
    S.calls.clear(); S._maybe_rescore(False, now=now + 1000.0)
    assert S.calls == []                            # nothing stale: nothing to do


def test_an_elite_that_no_longer_scores_is_dropped_unless_verified_positive():
    S = _stub(4, drop=(1, 2)); S.verified = {'k2': 0.7}
    now = S.t_rescore + 1000.0; S.clock.t = now
    S._maybe_rescore(False, now=now)
    assert (1,) not in S.archive and 'k1' not in S.where
    assert (2,) in S.archive and S.archive[(2,)]['n_scored'] == len(S.C)   # kept, as rescore() keeps it, and stamped
    assert S.archive[(0,)]['cheap'] == 2.0 and S.archive[(3,)]['cheap'] == 2.0


def test_the_lag_reports_the_oldest_elite_left_stale():
    S = _stub(50)
    now = S.t_rescore + 50.0; S.clock.t = now       # budget 5 s: elites 0-4 rescored, 5 is the oldest left
    S._maybe_rescore(False, now=now)
    assert S.calls == [0, 1, 2, 3, 4]
    assert S.roll_lag == now - 5.0


def test_fusion6_keeps_its_throttled_full_rescore():
    S = Searcher.__new__(Searcher)
    S.family = True; S.stale = False; S.t_rescore = 0.0; S.rescores = 0; S.rescore_secs = 0.0
    S.calls = []; S.rescore = lambda: S.calls.append(1)
    assert S._maybe_rescore(True, now=10_000.0) and S.calls == [1]          # no `rolling` attribute: the old path
