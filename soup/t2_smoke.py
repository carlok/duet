"""T2 smoke test for E: reference cases, the open implications A-D, a soundness control on refuted claims,
and proof length vs z3 effort on claims z3 proved.  python -m soup.t2_smoke [--limit N] [--cpu S]"""
import argparse
import glob
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .named import law_index
from .paths import data
from .provers import prove_e

L = lambda *ss: [law_index(s) for s in ss]
IDEM = 'x·x = x'
CASES = {
    'absorption => x·x=x': (L('x·(x∘y) = x', 'x∘(x·y) = x'), IDEM),
    'T1 => x·x=x': (L('(x·x)∘x = x', '((x·(y·z))∘z)·y = y'), IDEM),
    'T1 => x·x=x∘x': (L('(x·x)∘x = x', '((x·(y·z))∘z)·y = y'), 'x·x = x∘x'),
    'T2 => x·x=x': (L('x∘(y·(y∘x)) = x', 'x·((x∘x)·y) = x'), IDEM),
    'T2 => x·x=x∘x': (L('x∘(y·(y∘x)) = x', 'x·((x∘x)·y) = x'), 'x·x = x∘x'),
    'McKenzie => x·y=y·x': (L('x·(y∘(x∘z)) = x', 'x∘(y·(x·z)) = x', '((y∘x)·(x∘z))·x = x', '((y·x)∘(x·z))∘x = x'), 'x·y = y·x'),
    'A => x·x=x': (L('x·(x∘x) = x', 'x∘(x∘y) = y', '((x∘y)∘x)·y = x'), IDEM),
    'B => x·x=x': (L('(x·y)·y = x', '(x·x)∘x = x', 'x∘(y·(x·y)) = y'), IDEM),
    'C => x·x=x': (L('x·(x·x) = x', '(x·y)·y = x', '(x∘y)·(y∘x) = y'), IDEM),
    'D => x·x=x': (L('x·(x∘x) = x', '(x∘y)·x = y', 'x·((y∘y)∘x) = x'), IDEM),
}


def _run(args):
    name, T, goal, limit, cpu = args
    return name, prove_e(T, goal, processed_limit=limit, cpu_limit=cpu)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=500_000); ap.add_argument('--cpu', type=int, default=300)
    ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--control', type=int, default=200)
    a = ap.parse_args()
    jobs = []
    for name, (T, g) in CASES.items():
        assert None not in T and law_index(g) is not None, name
        jobs.append((name, T, law_index(g), a.limit, a.cpu))
    results = [json.load(open(f)) for f in sorted(glob.glob(str(data('results', '*.json'))))]
    refuted = [(r['T'], c) for r in results for c in r.get('claims', []) if c['status'].startswith('false')][:a.control]
    proved = [(r['T'], c) for r in results for c in r.get('claims', []) if c['status'] == 'proved']
    for i, (T, c) in enumerate(refuted): jobs.append((f'control{i}', T, c['idx'], 20_000, 30))
    for i, (T, c) in enumerate(proved): jobs.append((f'z3proved{i}', T, c['idx'], 50_000, 60))
    with ProcessPoolExecutor(a.jobs) as ex: out = dict(ex.map(_run, jobs))
    report = {'cases': {n: out[n] for n in CASES}}
    ctrl = [out[f'control{i}'] for i in range(len(refuted))]
    report['control'] = {'n': len(ctrl), 'proved_by_E (must be 0)': sum(r['status'] == 'proved' for r in ctrl),
                         'countersatisfiable': sum(r['status'] == 'countersatisfiable' for r in ctrl)}
    pz = [(c['effort'], out[f'z3proved{i}']) for i, (T, c) in enumerate(proved)]
    both = [(e, r['proof_steps'], r['processed']) for e, r in pz if r['status'] == 'proved']
    report['cross'] = {'z3_proved': len(pz), 'E_proved_too': len(both),
                       'E_failed': [proved[i][1]['law'] for i, (e, r) in enumerate(pz) if r['status'] != 'proved'][:10]}
    if len(both) >= 5:
        z, s, p = map(np.array, zip(*both))
        report['cross'].update(spearman_z3effort_vs_E_steps=round(spearman(z, s), 3),
                               spearman_z3effort_vs_E_processed=round(spearman(z, p), 3),
                               spearman_E_steps_vs_E_processed=round(spearman(s, p), 3),
                               E_steps_median=int(np.median(s)), E_steps_max=int(s.max()))
    json.dump(report, open(data('check', 't2_smoke_e.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
