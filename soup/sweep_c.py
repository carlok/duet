"""Stage c over every claim still open in SOUP_DATA/results (our pipeline only; no offline input).

    python -m soup.sweep_c [--jobs 10]

For each result with a claim in status 'unknown' or 'open': verify.stage_c with DEFAULTS (E 2M processed
clauses, certified saturations; Mace4 from the smallest size stage a left unsearched up to 10; long z3 run).
The result file is rewritten (stage 'c'), countermodels go to the shared corpus as in the stream.
A summary of every claim's new status is written to SOUP_DATA/check/sweep_c.json.
"""
import argparse
import glob
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from .paths import data, ensure
from .stream.common import write_json


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


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--jobs', type=int, default=10)
    a = ap.parse_args()
    paths = [p for p in sorted(glob.glob(str(data('results', '*.json'))))
             if any(c['status'] in ('unknown', 'open') for c in json.load(open(p)).get('claims', []))]
    print(f'{len(paths)} results with open claims', flush=True)
    res = []
    with ProcessPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(one, p) for p in paths]):
            try: x = f.result()
            except Exception as e: x = {'error': repr(e)}
            res.append(x)
            json.dump(res, open(ensure('check') / 'sweep_c.json', 'w'), ensure_ascii=False, indent=1)
            print(json.dumps(x, ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
