"""Stage c over every claim still open in SOUP_DATA/results (our pipeline only; no offline input).

    python -m soup.sweep_c [--jobs 5] [--timeout 5400]

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=5); ap.add_argument('--timeout', type=float, default=5400)
    ap.add_argument('--one')
    a = ap.parse_args()
    if a.one:
        print(MARK + json.dumps(one(a.one), ensure_ascii=False), flush=True); return
    paths = todo()
    summary = ensure('check') / 'sweep_c.json'
    res = json.load(open(summary)) if summary.exists() else []
    res = [x for x in res if 'error' not in x]                 # drop the broken-pool records of the first run
    print(f'{len(paths)} results with open claims not yet swept; {len(res)} earlier records kept', flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(run_child, p, a.timeout) for p in paths]):
            x = f.result(); res.append(x)
            json.dump(res, open(summary, 'w'), ensure_ascii=False, indent=1)
            print(json.dumps(x, ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
