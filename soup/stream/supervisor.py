"""Supervisor: starts search and verifier processes, rebalances them by queue length, and is the single
writer of logs/stats.jsonl, journal/journal.md and journal/leaderboard.md.

    python -m soup.stream.supervisor --budget 600 --searchers 3 --verifiers 8

Rebalancing (every --rebalance seconds, one move at a time, total process count fixed). The signal is the
number of *competitive* pending theories: priority (cheap score x (1 + novelty), times k = sum verified /
sum cheap over verified theories of the arm) at least the score
of the 20th best theory verified so far in this arm (0 until there are 20).
  competitive > HIGH (= 4 x verifiers) and searchers > floor     -> retire a searcher, start a verifier
  competitive < LOW  (= verifiers), verifiers > floor, one idle  -> retire that verifier, start a searcher
The searcher floor is --min-searchers (default 1). The verifier floor is 2; with --cap-c it is also at least the
stage-c tasks running plus one, so one verifier stays free for new pending theories.
Non-c verifiers take stage c first while fewer than --max-c (default verifiers/4, at least 1) run it. That is a floor: with nothing
pending they all take stage c (X9: six at once tripped the memory rule, and no verifier ever went idle, so a run
that drained its queue never turned back into a search). --cap-c N caps the stage-c tasks over all verifiers; a
verifier it turns away with nothing pending goes idle, and the second rule then makes it a searcher.
--drain-c S (25 Nov 2026, for runs done in blocks): in the last S seconds of the budget no verifier starts a stage-c
task (each verifier gets --c-until), so the stop cuts only stage-c tasks longer than S. The journal's end entry
counts the stage-c tasks the stop cut; they go back to the lane and start over in the next run on the directory.
The pending lane is trimmed to --qmax tasks (lowest priority moved to queue/dropped/). Searchers push only
theories with k x priority >= --gate x (20th best score); the supervisor publishes k and that bar in
queue/gate.json every tick. Workers get SIGTERM at the budget; verifiers interrupt z3 at once.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time

import z3

from ..paths import data, ensure, DATA
from .common import dumps, memory, read_json, write_json
from .fqueue import FileQueue
from .journal import Journal, leaderboard, result_line, hm, ymd_hm
from .verifier import RECYCLE_RC


def mem_available_mb(path='/proc/meminfo'):
    """MemAvailable of the VM in MB (a container sees the VM's /proc/meminfo), or None if unreadable."""
    try:
        for line in open(path):
            if line.startswith('MemAvailable:'): return int(line.split()[1]) // 1024
    except OSError:
        return None
    return None


class Proc:
    def __init__(self, name, role, cmd, log):
        self.name, self.role, self.cmd = name, role, cmd
        self.logf = open(log, 'a')
        env = dict(os.environ, NUMBA_NUM_THREADS='1', OMP_NUM_THREADS='1')
        self.p = subprocess.Popen(cmd, stdout=self.logf, stderr=subprocess.STDOUT, env=env)
        self.t0 = time.time(); self.retiring = False


class Supervisor:
    def __init__(self, a):
        self.a = a; self.recycled = 0
        if a.recycle_mb: os.environ['SOUP_VERIFIER_RECYCLE_MB'] = str(a.recycle_mb)   # inherited by the verifiers
        self.run = a.run or time.strftime('r%Y%m%d-%H%M%S')
        for d in ('logs', 'journal', 'results', 'corpus', 'queue'): ensure(d)
        ensure('logs', self.run); ensure('runs', self.run)
        self.Q = FileQueue(data('queue')); self.J = Journal()
        self.procs = {}; self.next_seed = a.seed0; self.next_v = 0
        self.results = {}; self.mtimes = {}
        self.top_key = None; self.t_start = time.time(); self.events = []
        self.ticks = 0; self.journaled = 0; self.quiet = 0
        self.c_until = c_until(a, self.t_start); self.drain_logged = False

    # ---- processes
    def start_searcher(self):
        seed = self.next_seed; self.next_seed += 1; name = f's{seed}'
        cmd = [sys.executable, '-m', 'soup.stream.searcher', '--name', name, '--seed', str(seed),
               '--arm', self.a.arm, '--run', self.run]
        self.procs[name] = Proc(name, 'search', cmd, data('logs', self.run, f'{name}.log'))
        return name

    def start_verifier(self, prefer=None):
        name = f'v{self.next_v}'; self.next_v += 1
        if prefer is None:     # keep exactly one verifier that prefers stage c
            prefer = 'ab' if any(getattr(p, 'prefer', None) == 'c' for p in self.active('verify')) else 'c'
        cmd = [sys.executable, '-m', 'soup.stream.verifier', '--name', name, '--run', self.run, '--prefer', prefer,
               '--max-c', str(stage_c_floor(self.a)), '--cap-c', str(getattr(self.a, 'cap_c', 0) or 0),
               '--c-until', f"{getattr(self, 'c_until', 0.0):.1f}"]
        self.procs[name] = Proc(name, 'verify', cmd, data('logs', self.run, f'{name}.log'))
        self.procs[name].prefer = prefer
        return name

    def active(self, role): return [p for p in self.procs.values() if p.role == role and not p.retiring and p.p.poll() is None]

    def retire(self, p):
        p.retiring = True; p.t_retire = time.time(); p.p.send_signal(signal.SIGTERM)

    def reap(self):
        for name, p in list(self.procs.items()):
            rc = p.p.poll()
            if rc is None:
                if p.retiring and time.time() - p.t_retire > 90: p.p.kill()
                continue
            back = self.Q.recover(name)
            if not p.retiring and p.role == 'verify' and rc == RECYCLE_RC:     # stopped itself to free memory
                self.recycled += 1
                self.event(f'{name} recycled (memory); {back} claimed task(s) put back; starting a fresh verifier')
                del self.procs[name]
                self.start_verifier(getattr(p, 'prefer', None))
            elif not p.retiring:            # crashed: say so and replace it
                self.event(f'**{name} ({p.role}) exited with code {rc}**; {back} claimed task(s) put back; restarting the role')
                del self.procs[name]
                self.start_searcher() if p.role == 'search' else self.start_verifier(getattr(p, 'prefer', None))
            else:
                del self.procs[name]
            p.logf.close()

    def threshold(self):
        sc = sorted((r.get('score', 0) for r in self.results.values() if r.get('arm') == self.a.arm), reverse=True)
        return sc[19] if len(sc) >= 20 else 0.0

    def k(self):
        """Calibration cheap -> verified scale: ratio of sums over verified theories of this arm."""
        rs = [r for r in self.results.values() if r.get('arm') == self.a.arm and r.get('cheap')]
        c = sum(r['cheap'] for r in rs)
        return sum(r.get('score', 0) for r in rs) / c if len(rs) >= 5 and c > 0 else 1.0

    def competitive(self):
        th, k = self.threshold(), self.k()
        return sum(k * p >= th for p in self.Q.priorities()), th

    def rebalance(self):
        q = self.Q.counts(); s, v = self.active('search'), self.active('verify')
        comp, th = self.competitive()
        high, low = 4 * len(v), len(v)
        if comp > high and len(s) > searcher_floor(self.a):
            victim = min(s, key=lambda p: p.t0); self.retire(victim); new = self.start_verifier()
            return f'{comp} competitive pending (priority >= {th:.3f}) > {high}: retired searcher {victim.name}, started verifier {new}'
        idle = [p for p in v if is_idle(read_json(data('logs', 'workers', f'{p.name}.json')), p.t0)
                and getattr(p, 'prefer', '') != 'c']
        floor = verifier_floor(self.a, self.Q.running('stage2c'))
        if comp < low and len(v) > floor and idle:  # only a verifier with nothing to do is surplus
            victim = idle[-1]
            self.retire(victim); new = self.start_searcher()
            return f'{comp} competitive pending (priority >= {th:.3f}) < {low}: retired verifier {victim.name}, started searcher {new}'
        return None

    # ---- monitoring
    def event(self, text):
        self.events.append(text); self.J.write(f'- {hm()} · {text}')

    def scan_results(self):
        new = []
        for e in os.scandir(data('results')):
            if not e.name.endswith('.json') or e.name.startswith('.'): continue
            mt = e.stat().st_mtime
            if self.mtimes.get(e.name, 0) >= mt: continue
            r = read_json(e.path)
            if r is None: continue
            first = e.name not in self.mtimes
            self.mtimes[e.name] = mt; self.results[r['key']] = r
            if not self.initial: new.append((r, first))
        return new

    def tick(self, action=None):
        self.ticks += 1
        new = self.scan_results()
        rs = sorted((r for r in self.results.values() if r.get('score', 0) > 0), key=lambda r: -r['score'])
        top10 = {r['key'] for r in rs[:10]}
        for r, first in sorted(new, key=lambda x: x[0].get('t_done', 0)):
            # detailed entry only when notable: enters the top 10, finished stage c, or has an open claim
            if r['key'] in top10 or r.get('stage') == 'c' or r.get('open'):
                self.J.write(result_line(r)); self.journaled += 1
            else:
                self.quiet += 1
        if rs and rs[0]['key'] != self.top_key and new:
            self.top_key = rs[0]['key']
            self.event(f"**new #1**: `{rs[0]['key'][:8]}` score {rs[0]['score']:.3f}: {' & '.join(rs[0]['laws'])}")
        trimmed = self.Q.trim(self.a.qmax)
        q = self.Q.counts(); comp, th = self.competitive()
        write_json(data('queue', 'gate.json'), {'arm': self.a.arm, 'k': self.k(), 'threshold': th * self.a.gate})
        workers = []
        for name, p in sorted(self.procs.items()):
            hb = read_json(data('logs', 'workers', f'{name}.json')) or {}
            w = {'name': name, 'role': p.role, 'pid': p.p.pid, 'alive': p.p.poll() is None, 'retiring': p.retiring,
                 'state': hb.get('state'), 'mem': memory(p.p.pid)}
            for k in ('evals', 'evals_per_s', 'archive', 'pushed', 'held', 'wins', 'k', 'done', 'busy_frac', 'key', 'corpus', 'prefer'):
                if k in hb: w[k] = hb[k]
            workers.append(w)
        mems = [w['mem'] for w in workers if w['mem']]
        run_results = [r for r in self.results.values() if r.get('run') == self.run]
        line = {
            'ts': ymd_hm(), 't': round(time.time(), 1), 'elapsed_s': round(time.time() - self.t_start, 1), 'run': self.run,
            'queue': dict(q, competitive=comp, threshold=round(th, 4), k=round(self.k(), 4), trimmed_now=trimmed),
            'results': {'total': len(self.results), 'this_run': len(run_results),
                        'positive_this_run': sum(r.get('score', 0) > 0 for r in run_results),
                        'stage_c_this_run': sum(r.get('stage') == 'c' for r in run_results),
                        'open_claims_this_run': sum(sum(c['status'] in ('unknown', 'open') for c in r.get('claims', [])) for r in run_results),
                        'top_score': rs[0]['score'] if rs else 0.0},
            'corpus_files': sum(1 for e in os.listdir(data('corpus')) if e.endswith('.npz') and not e.startswith('.')),
            'n_search': len(self.active('search')), 'n_verify': len(self.active('verify')),
            'evals_total': sum(w.get('evals', 0) for w in workers if w['role'] == 'search'),
            'mem_total': {'rss_mb': round(sum(m['rss_mb'] for m in mems), 1), 'pss_mb': round(sum(m['pss_mb'] for m in mems), 1)},
            'mem_available_mb': mem_available_mb(),          # the VM's, as the memory rule reads it (X10 on)
            'workers': workers,
        }
        if action: line['rebalance'] = action
        with open(data('logs', 'stats.jsonl'), 'a') as fh: fh.write(dumps(line) + '\n')
        leaderboard(list(self.results.values()),
                    header=f"Run {self.run}: {line['n_search']} searchers, {line['n_verify']} verifiers, queue {q['pending']} pending / {q['stage2c']} stage c.")
        if self.ticks % max(1, int(300 / self.a.tick)) == 0:
            self.J.write(f"- {hm()} · status: {line['results']['this_run']} verified this run "
                         f"({line['results']['positive_this_run']} positive), queue {q['pending']} pending / {q['claimed']} claimed / "
                         f"{q['stage2c']} stage c ({comp} competitive at >= {th:.3f}, {q['dropped']} dropped), {self.quiet} unremarkable results not listed, corpus {line['corpus_files']} found structures, "
                         f"{line['evals_total']:,} surrogate evaluations, PSS total {line['mem_total']['pss_mb']:.0f} MB")
        return line

    def main(self):
        a = self.a
        self.initial = True; self.scan_results(); self.initial = False
        cfg = {'run': self.run, 'budget_s': a.budget, 'searchers': a.searchers, 'verifiers': a.verifiers, 'arm': a.arm,
               'seed0': a.seed0, 'gate': a.gate, 'qmax': a.qmax, 'tick_s': a.tick, 'rebalance_s': a.rebalance,
               'min_searchers': searcher_floor(a), 'cap_c': a.cap_c, 'max_c': stage_c_floor(a), 'drain_c': a.drain_c,
               'recycle_mb': a.recycle_mb, 'mem_stop_mb': a.mem_stop_mb, 'z3': z3.get_version_string(),
               'data': str(DATA), 'cores': os.cpu_count(), 'results_before': len(self.results),
               'corpus_before': sum(1 for e in os.listdir(data('corpus')) if e.endswith('.npz')),
               'queue_before': self.Q.counts(), 'started': ymd_hm()}
        write_json(data('runs', self.run, 'config.json'), cfg)
        self.J.write(f"\n## {ymd_hm()} · run {self.run} started\n\n"
                     f"- budget {a.budget:.0f} s · {a.searchers} searchers (seeds {a.seed0}–{a.seed0 + a.searchers - 1}, arm {a.arm}) · "
                     f"{a.verifiers} verifiers (v0 prefers stage c"
                     f"{f', at most {a.cap_c} stage-c tasks at once' if a.cap_c else ''}"
                     f"{f', none started in the last {a.drain_c:.0f} s' if a.drain_c else ''}) · z3 {cfg['z3']} · {cfg['cores']} cores\n"
                     f"- before: {cfg['results_before']} verified theories, {cfg['corpus_before']} found structures, "
                     f"queue {cfg['queue_before']['pending']} pending / {cfg['queue_before']['stage2c']} stage c\n")
        for name in os.listdir(data('queue', 'claimed')):         # leftovers of a killed earlier run
            self.Q.release(data('queue', 'claimed', name))
        write_json(data('queue', 'gate.json'), {'arm': a.arm, 'k': self.k(), 'threshold': self.threshold() * a.gate})
        for _ in range(a.searchers): self.start_searcher()
        for i in range(a.verifiers): self.start_verifier('c' if i == 0 else 'ab')
        stop = {'set': False}
        def h(*_): stop['set'] = True
        signal.signal(signal.SIGTERM, h); signal.signal(signal.SIGINT, h)
        t_reb = time.time(); mem_stop = None
        while not stop['set'] and time.time() - self.t_start < a.budget:
            time.sleep(a.tick)
            self.reap()
            action = None
            if time.time() - t_reb > a.rebalance:
                action = self.rebalance(); t_reb = time.time()
                if action: self.event(f'rebalance: {action}')
            self.tick(action)
            if self.c_until and not self.drain_logged and time.time() >= self.c_until:
                self.drain_logged = True
                self.event(f'drain: no new stage-c task from now on ({self.Q.running("stage2c")} running)')
            if a.mem_stop_mb:                      # the preregistered memory rule, applied by the supervisor (X7)
                avail = mem_available_mb()
                if avail is not None and avail < a.mem_stop_mb:
                    mem_stop = avail; break
        self.event(f"memory rule: {mem_stop} MB available < {a.mem_stop_mb} MB after {time.time() - self.t_start:.0f} s: stopping workers"
                   if mem_stop is not None else
                   f"budget reached ({time.time() - self.t_start:.0f} s): stopping workers" if not stop['set'] else 'stopped by signal')
        cut_c = self.Q.running('stage2c')     # stage-c tasks the stop cuts; the verifiers put them back as they exit
        for p in self.procs.values():
            if p.p.poll() is None: p.retiring = True; p.p.send_signal(signal.SIGTERM)
        t0 = time.time()
        while any(p.p.poll() is None for p in self.procs.values()) and time.time() - t0 < 30: time.sleep(1)
        for p in self.procs.values():
            if p.p.poll() is None: p.p.kill(); p.p.wait()
        for name in list(self.procs): self.Q.recover(name)
        line = self.tick()
        r = line['results']; q = line['queue']
        self.J.write(f"\n### {ymd_hm()} · run {self.run} ended\n\n"
                     f"- {r['this_run']} theories verified ({r['positive_this_run']} positive score, {r['stage_c_this_run']} through stage c), "
                     f"{r['open_claims_this_run']} claims still open\n"
                     f"- stage-c tasks cut by the stop and put back: {cut_c}\n"
                     f"- {line['evals_total']:,} surrogate evaluations; {line['corpus_files'] - cfg['corpus_before']} structures added to the corpus\n"
                     f"- queue left: {q['pending']} pending, {q['stage2c']} stage c (kept for the next run)\n"
                     f"- top score overall {r['top_score']:.3f}; see leaderboard.md\n")


def searcher_floor(a):
    """The rebalancer never retires a searcher below this many (--min-searchers; X8, 24 Nov 2026). Default 1."""
    return max(1, getattr(a, 'min_searchers', 1) or 1)


def stage_c_floor(a):
    """Non-c verifiers take stage c first while fewer than this many run it: --max-c, else verifiers/4 (at least 1).
    With searchers keeping pending full, this is how many stage-c tasks actually run, so a run that wants --cap-c N
    stage-c tasks sets --max-c N too (X10)."""
    return getattr(a, 'max_c', 0) or max(1, a.verifiers // 4)


def c_until(a, t_start):
    """The Unix time after which no verifier starts a stage-c task: the end of the budget minus --drain-c, or 0
    (no limit) without it (25 Nov 2026)."""
    drain = getattr(a, 'drain_c', 0) or 0
    return t_start + a.budget - drain if drain > 0 else 0.0


def verifier_floor(a, running_c):
    """The rebalancer never retires a verifier below this many: 2, as before X9. With --cap-c (25 Nov 2026) also
    the stage-c tasks running plus one, so that new pending theories do not wait behind stage c (~44 min each)."""
    cap = getattr(a, 'cap_c', 0) or 0
    return max(2, running_c + 1) if cap > 0 else 2


def is_idle(hb, t0):
    """A heartbeat says idle, and it was written by this process: a verifier still loading its corpus has only
    the heartbeat an earlier run's worker of the same name left, and that one may say idle."""
    return bool(hb) and hb.get('state') == 'idle' and hb.get('t', 0) >= t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=float, default=float(os.environ.get('BUDGET', 3600)))
    ap.add_argument('--searchers', type=int, default=int(os.environ.get('SEARCHERS', 3)))
    ap.add_argument('--verifiers', type=int, default=int(os.environ.get('VERIFIERS', 8)))
    ap.add_argument('--arm', default=os.environ.get('ARM', 'prior'), choices=['prior', 'noprior', 'fusion', 'fusion2', 'fusion3', 'fusion4', 'fusion5', 'fusion6'])
    ap.add_argument('--seed0', type=int, default=int(os.environ.get('SEED0', 101)))
    ap.add_argument('--tick', type=float, default=15.0)
    ap.add_argument('--rebalance', type=float, default=120.0)
    ap.add_argument('--qmax', type=int, default=1500)
    ap.add_argument('--gate', type=float, default=0.5, help='push only if k*priority >= gate * 20th best score')
    ap.add_argument('--run', default=os.environ.get('RUN_ID'))
    ap.add_argument('--mem-stop-mb', type=int, default=0, help='stop cleanly when MemAvailable falls below this (0: off)')
    ap.add_argument('--recycle-mb', type=int, default=0, help='verifiers restart themselves between tasks above this private memory (0: never)')
    ap.add_argument('--min-searchers', type=int, default=1, help='the rebalancer never retires searchers below this many')
    ap.add_argument('--cap-c', type=int, default=0, help='at most this many stage-c tasks at once over all verifiers (0: no cap)')
    ap.add_argument('--max-c', type=int, default=0, help='verifiers take stage c first while fewer than this many run it (0: verifiers/4)')
    ap.add_argument('--drain-c', type=float, default=0, help='start no stage-c task in the last this many seconds of the budget (0: off)')
    Supervisor(ap.parse_args()).main()


if __name__ == '__main__':
    main()
