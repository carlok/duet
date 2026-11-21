"""Stage c over every claim still open in SOUP_DATA/results (our pipeline only; no offline input).

    python -m soup.sweep_c [--jobs 5] [--timeout 5400]
    python -m soup.sweep_c --summary          # table for REPORT.md from SOUP_DATA/check/sweep_c.json

For each result with a claim in status 'unknown' or 'open' that has not been swept yet: verify.stage_c with
DEFAULTS (E 2M processed clauses, certified saturations; Mace4 from the smallest size stage a left unsearched
up to 10; long z3 run). The result file is rewritten (stage 'c', field 'sweep_c'), countermodels go to the
shared corpus as in the stream. Each result runs in its own child process (a dying worker took the whole
process pool down in the first run of 21 Nov 2026); a child that dies or overruns --timeout is recorded as
crashed and its result file is left untouched. Rerunning skips results already swept.
Summary: SOUP_DATA/check/sweep_c.json (appended across runs).
"""
import argparse
import glob
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data, ensure
from .stream.common import write_json

MARK = 'SWEEP-C-RESULT '


def one(path):
    from .core import Corpus, set_memory_limit
    from .verify import stage_c
    set_memory_limit(1500)
    r = json.load(open(path)); key = r['key']
    before = {c['law']: c['status'] for c in r['claims']}
    for c in r['claims']:
        if c['status'] == 'open': c['status'] = 'unknown'      # stage c handles 'unknown' only
    t0 = time.time()
    C = Corpus(store=data('corpus'))
    out = stage_c(C, r, tag=f':{key}:sweep_c')
    out.setdefault('secs', {})['c'] = round(time.time() - t0, 1); out['sweep_c'] = time.strftime('%Y-%m-%d %H:%M:%S')
    write_json(path, out)
    return {'key': key, 'laws': out['laws'],
            'claims': [{'law': c['law'], 'before': before[c['law']], 'after': c['status'],
                        'certificate': c.get('certificate'), 'mace4_sizes': c.get('mace4_sizes'),
                        'mace4_searched_to': c.get('mace4_searched_to'), 'e_status': c.get('e_status'),
                        'e_steps': c.get('e_steps')}
                       for c in out['claims'] if before[c['law']] in ('unknown', 'open')],
            'secs': out['secs']['c']}


def run_child(path, timeout):
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, '-m', 'soup.sweep_c', '--one', path], capture_output=True, text=True,
                           timeout=timeout)
        lines = [l for l in p.stdout.splitlines() if l.startswith(MARK)]
        if p.returncode == 0 and lines: return json.loads(lines[-1][len(MARK):])
        why = f'exit code {p.returncode}'; tail = p.stderr[-1500:]
    except subprocess.TimeoutExpired:
        why = f'timeout after {timeout} s'; tail = ''
    return {'key': json.load(open(path)).get('key'), 'status': 'crashed', 'why': why, 'stderr_tail': tail,
            'secs': round(time.time() - t0, 1)}


def todo():
    out = []
    for p in sorted(glob.glob(str(data('results', '*.json')))):
        r = json.load(open(p))
        if r.get('sweep_c'): continue
        if any(c['status'] in ('unknown', 'open') for c in r.get('claims', [])): out.append(p)
    return out


SURVIVORS = {'00f017a6': 'S1', '45b1f0fb': 'S2', '4ec6760a': 'S3', '513de1ad': 'S4', '5e0dc923': 'S5',
             'bbdd0d1c': 'S6', 'cdf702b5': 'S7', 'd25065b6': 'S8', 'e6403d7a': 'S9', 'f096b282': 'S10',
             'f5321de4': 'S11', 'f5e53602': 'S12'}          # work/journal/survivors.md


def summary():
    """One line per swept result (survivor label, outcome per claim), totals, and the results not swept yet."""
    import collections
    s = json.load(open(data('check', 'sweep_c.json')))
    tot, surv, secs = collections.Counter(), collections.Counter(), []
    for r in s:
        if r.get('status') == 'crashed':
            print('crashed', r['key'][:8], r.get('why')); continue
        lab = SURVIVORS.get(r['key'][:8], '-'); secs.append(r['secs']); parts = []
        for c in r['claims']:
            o = c['after']; tot[o] += 1
            if lab != '-': surv[o] += 1
            x = f"{c['law']}: {o}"
            if o == 'proved' and c.get('e_steps'): x += f" (E {c['e_steps']} steps)"
            if o == 'open': x += f" (Mace4 sizes {c.get('mace4_sizes')}, complete to {c.get('mace4_searched_to')})"
            parts.append(x)
        print(lab, r['key'][:8], f"{len(r['laws'])} laws, {r['secs']} s |", '; '.join(parts))
    print(len(secs), 'results swept; claims', dict(tot), '; survivor claims', dict(surv))
    if secs: print('seconds per result: min', min(secs), 'median', sorted(secs)[len(secs) // 2], 'max', max(secs))
    print('not swept yet:', [SURVIVORS.get(p.split('/')[-1][:8], '-') + ' ' + p.split('/')[-1][:8] for p in todo()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=5); ap.add_argument('--timeout', type=float, default=5400)
    ap.add_argument('--one'); ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()
    if a.summary:
        summary(); return
    if a.one:
        print(MARK + json.dumps(one(a.one), ensure_ascii=False), flush=True); return
    paths = todo()
    out_path = ensure('check') / 'sweep_c.json'
    res = json.load(open(out_path)) if out_path.exists() else []
    res = [x for x in res if 'error' not in x]                 # drop the broken-pool records of the first run
    print(f'{len(paths)} results with open claims not yet swept; {len(res)} earlier records kept', flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(run_child, p, a.timeout) for p in paths]):
            x = f.result(); res.append(x)
            json.dump(res, open(out_path, 'w'), ensure_ascii=False, indent=1)
            print(json.dumps(x, ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
