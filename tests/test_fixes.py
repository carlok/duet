"""Regression tests for the fixes of 21 Nov 2026 (evening): stage-c sizes, certified saturations,
the drop-one mutation, the crash-proof calibration runner."""
import json
import random
import sys

from soup.named import law_index
from soup.verify import c_size_range, DEFAULTS, V1, _e

A = ['x·(x∘x) = x', 'x∘(x∘y) = y', '((x∘y)∘x)·y = x']


def test_stage_c_starts_at_smallest_unsearched_size():
    assert c_size_range({'cm_unknown_sizes': [5, 6]}, DEFAULTS) == (5, 10)
    assert c_size_range({'cm_unknown_sizes': [6]}, DEFAULTS) == (6, 10)
    assert c_size_range({}, DEFAULTS) == (7, 10)


def test_v1_is_frozen_and_does_not_certify():
    assert V1['n_cands'] == 3 and V1['max_tried'] == 9 and not V1['certify_e']
    assert DEFAULTS['certify_e']


def test_e_saturation_is_certified():
    T = [law_index(s) for s in A]
    c = {'idx': law_index('x·x = x'), 'status': 'pending'}
    assert _e(c, T, 20_000, 20, certify=True) == 'countersatisfiable'
    assert c['status'] == 'false (E saturation)' and c['certificate'] is True


def test_drop_one_removes_exactly_one_law():
    from soup.stream.searcher import drop_one
    rng = random.Random(0)
    for _ in range(200):
        a = rng.sample(range(100, 200), 6)
        b = drop_one(a, rng)
        assert len(b) == 5 and set(b) < set(a)


def test_calib_resume_skips_done_and_keeps_preregistered_jobs():
    from soup.calib import jobs, pending, job_key
    js = jobs(2, 11)
    assert jobs(2, 11) == js                       # deterministic
    done = [{'name': n, 'kind': k, 'T': T} for n, k, T in js[:3]]
    assert pending(js, done) == js[3:]
    assert len({job_key(*j) for j in js}) == len(js)


def test_calib_records_a_crashed_child():
    from soup.calib import run_one
    r = run_one(('x', 'null', [1, 2]), cmd=[sys.executable, '-c', 'import sys; sys.exit(9)'])
    assert r['status'] == 'crashed' and 'exit code 9' in r['why'] and r['score'] is None


def test_calib_child_runs_one_theory():
    from soup.calib import run_one
    r = run_one(('absorption pair', 'named', sorted(law_index(s) for s in ['x·(x∘y) = x', 'x∘(x·y) = x'])))
    assert r.get('status') == 'ok' and r['score'] > 0 and r['dualities'] == ['swap']
