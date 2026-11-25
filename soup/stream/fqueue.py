"""A plain file-based priority queue for one machine.

  queue/pending/p<inv>_<key>.json     stage a+b tasks; <inv> = 10^10-1 - priority*10^6, so the
  queue/stage2c/p<inv>_<key>.json     lexicographically first file is the highest priority
  queue/claimed/<worker>__<lane>__<file>   taken by a worker (atomic rename; one winner)
  queue/dropped/<file>               trimmed from pending (lowest priority) when it exceeds its cap
  queue/.lock_<lane>                  held for the count-and-claim of a lane with a cap on running tasks
  queue/seen/<key>                    dedup marker, created with O_EXCL: each theory (up to the three
                                      dualities) enters the queue once, ever
"""
import json
import os
import time
from pathlib import Path

from .common import write_json

LANES = ('pending', 'stage2c')


def _fname(key, prio):
    inv = 10 ** 10 - 1 - max(0, min(int(prio * 1e6), 10 ** 10 - 1))
    return f'p{inv:010d}_{key}.json'


class FileQueue:
    def __init__(self, root):
        self.root = Path(root)
        for d in LANES + ('claimed', 'seen', 'dropped'): (self.root / d).mkdir(parents=True, exist_ok=True)

    def mark_seen(self, key):
        """True the first time a key is offered (by any process), False afterwards."""
        try:
            os.close(os.open(self.root / 'seen' / key, os.O_CREAT | os.O_EXCL | os.O_WRONLY)); return True
        except FileExistsError:
            return False

    def is_seen(self, key): return (self.root / 'seen' / key).exists()

    def push(self, key, task, prio, lane='pending'):
        task = dict(task, key=key, prio=prio, lane=lane)
        write_json(self.root / lane / _fname(key, prio), task)

    def claim(self, worker, lanes=LANES, caps=None):
        """Take the highest-priority task of the first non-empty lane. Returns (claimed path, task) or None.

        caps = {lane: n}: a capped lane is skipped while n of its tasks are claimed. The count and the claim
        happen under a lock file, so concurrent workers never take more than n (after X9, 25 Nov 2026)."""
        caps = caps or {}
        for lane in lanes:
            cap = caps.get(lane)
            if not cap:
                got = self._claim_lane(worker, lane)
            elif not self._lock(lane):
                continue                                    # another worker is claiming from this lane
            else:
                try: got = self._claim_lane(worker, lane) if self.running(lane) < cap else None
                finally: self._unlock(lane)
            if got: return got
        return None

    def _claim_lane(self, worker, lane):
        d = self.root / lane
        for f in sorted(e for e in os.listdir(d) if e.startswith('p')):
            dst = self.root / 'claimed' / f'{worker}__{lane}__{f}'
            try: os.rename(d / f, dst)
            except FileNotFoundError: continue              # another worker was faster
            try: return dst, json.loads(dst.read_text())
            except json.JSONDecodeError: dst.unlink(); continue
        return None

    def _lock(self, lane, stale_s=60):
        """O_EXCL lock file for a capped lane. It is held for milliseconds; one left by a killed worker is
        removed after stale_s seconds."""
        p = self.root / f'.lock_{lane}'
        for _ in range(2):
            try:
                os.close(os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)); return True
            except FileExistsError:
                try:
                    if time.time() - p.stat().st_mtime > stale_s: p.unlink(missing_ok=True); continue
                except FileNotFoundError:
                    continue
                return False
        return False

    def _unlock(self, lane): (self.root / f'.lock_{lane}').unlink(missing_ok=True)

    def running(self, lane):
        return sum(f'__{lane}__' in e for e in os.listdir(self.root / 'claimed'))

    def done(self, claimed): Path(claimed).unlink(missing_ok=True)

    def release(self, claimed):
        claimed = Path(claimed); _, lane, f = claimed.name.split('__', 2)
        try: os.rename(claimed, self.root / lane / f)
        except FileNotFoundError: pass

    def recover(self, worker):
        """Put back every task a (dead or retired) worker had claimed."""
        n = 0
        for e in os.listdir(self.root / 'claimed'):
            if e.startswith(f'{worker}__'): self.release(self.root / 'claimed' / e); n += 1
        return n

    @staticmethod
    def prio_of(fname): return (10 ** 10 - 1 - int(fname[1:11])) / 1e6

    def priorities(self, lane='pending'):
        return [self.prio_of(e) for e in os.listdir(self.root / lane) if e.startswith('p')]

    def trim(self, qmax, lane='pending'):
        """Keep the qmax highest-priority tasks; move the rest to queue/dropped/ (kept, never verified)."""
        fs = sorted(e for e in os.listdir(self.root / lane) if e.startswith('p'))
        for f in fs[qmax:]:
            try: os.rename(self.root / lane / f, self.root / 'dropped' / f)
            except FileNotFoundError: pass
        return max(0, len(fs) - qmax)

    def counts(self):
        c = {lane: sum(1 for e in os.listdir(self.root / lane) if e.startswith('p')) for lane in LANES}
        c['claimed'] = len(os.listdir(self.root / 'claimed'))
        c['seen'] = len(os.listdir(self.root / 'seen'))
        c['dropped'] = len(os.listdir(self.root / 'dropped'))
        return c
