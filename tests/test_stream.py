"""File queue and shared corpus store: the pieces processes use to talk to each other."""
import numpy as np

from soup.core import Corpus
from soup.named import law_index
from soup.stream.fqueue import FileQueue


def test_queue_priority_claim_dedup(tmp_path):
    Q = FileQueue(tmp_path)
    assert Q.mark_seen('a') and not Q.mark_seen('a')
    Q.push('a', {'T': [1, 2]}, 0.5); Q.push('b', {'T': [3, 4]}, 2.0); Q.push('c', {'T': [5, 6]}, 0.1, lane='stage2c')
    p, t = Q.claim('w1'); assert t['key'] == 'b'               # highest priority first
    p2, t2 = Q.claim('w2'); assert t2['key'] == 'a'
    Q.release(p2); assert Q.counts()['pending'] == 1
    p3, t3 = Q.claim('w2', ('stage2c', 'pending')); assert t3['key'] == 'c' and t3['lane'] == 'stage2c'
    assert Q.recover('w1') == 1 and Q.counts()['pending'] == 2
    Q.done(p3); assert Q.counts()['claimed'] == 0


def test_corpus_store_shared_between_processes(tmp_path):
    a, b = Corpus(store=tmp_path), Corpus(store=tmp_path)
    F = np.array([[0, 0], [0, 1]]); G = np.array([[0, 1], [1, 1]])        # the 2-element lattice
    assert a.add('lattice-2', 2, F, G) and not a.add('again', 2, F, G)
    assert b.refresh() == 1 and b.refresh() == 0
    lat = [law_index(s) for s in ['x·(x∘y) = x', 'x∘(x·y) = x']]
    assert b.sat(lat)[1].tolist() == [True]
    assert (b.XP[0] == a.XP[0]).all() and b.nd.tolist() == [True]
    assert b.implied(lat) is not None
