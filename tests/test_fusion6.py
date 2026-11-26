"""Arm 'fusion6' (prototype, 26 Nov 2026): the rescore throttle (Searcher._maybe_rescore)."""
from soup.stream.searcher import RESCORE_EVERY, Searcher


def _stub(family):
    S = Searcher.__new__(Searcher)                 # no data directory needed: only the throttle's state
    S.family = family; S.stale = False; S.t_rescore = 0.0; S.rescores = 0; S.rescore_secs = 0.0
    S.calls = []; S.rescore = lambda: S.calls.append(1)
    return S


def test_fusion6_rescores_at_most_once_per_window():
    S = _stub(True); t = 10_000.0
    assert S._maybe_rescore(True, now=t)                       # the first growth: at once
    assert not S._maybe_rescore(True, now=t + 20)              # inside the window: deferred, but remembered
    assert not S._maybe_rescore(False, now=t + 40)
    assert S._maybe_rescore(False, now=t + RESCORE_EVERY + 1)  # the deferred growth, once the window is over
    assert not S._maybe_rescore(False, now=t + 2 * RESCORE_EVERY + 2)   # nothing new: nothing to do
    assert len(S.calls) == 2 and S.rescores == 2


def test_other_arms_rescore_at_once_as_before():
    S = _stub(False); t = 10_000.0
    assert S._maybe_rescore(True, now=t) and S._maybe_rescore(True, now=t + 1)
    assert not S._maybe_rescore(False, now=t + 2)
    assert len(S.calls) == 2
