"""Vampire finite model building over every claim still open in SOUP_DATA/results (our tools only; no offline input).

    python -m soup.sweep_fmb [--jobs 8] [--secs 3600] [--start 2]
    python -m soup.sweep_fmb --summary          # table for REPORT.md from SOUP_DATA/check/sweep_fmb.json

Why: on S10 (21 Nov 2026) Mace4 did not finish size 7 in two hours, while Vampire's finite model builder
(-sa fmb: each domain size is a complete SAT search, sizes tried in increasing order) found a 10-element model in
under two minutes. Stage c (V2, preregistered for T4) has no FMB, so this is a separate, post-hoc sweep.

For each result with a claim in status 'unknown' or 'open' and no 'sweep_fmb' field yet: for each such claim,
Vampire -sa fmb from size --start for --secs seconds. A model is parsed (provers.parse_vampire_model) and accepted
only if check_offline.check_finite confirms, with both of our evaluators, that every axiom holds and the claim
fails; it is then tested against the result's other open claims too. Accepted models go to the shared corpus, the
claim becomes 'false (size n, Vampire FMB)', and the result file is rewritten (field 'sweep_fmb'). Full Vampire
output: SOUP_DATA/check/fmb/<key>_<claim number>.out. One child process per result; a child that dies or overruns
is recorded as crashed and its result file is left untouched. Rerunning skips results already swept.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data, ensure
from .stream.common import write_json

MARK = 'SWEEP-FMB-RESULT '


def fmb(T, goal, secs=60, start=2):
    """Vampire -sa fmb on axioms T and goal (law index). Returns (status, model or None, full output)."""
    from .provers import V_BIN, PROVER_MB, problem, parse_vampire_model
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(problem(T, goal)); path = fh.name
    try:
        r = subprocess.run([V_BIN, '-sa', 'fmb', '-fmbss', str(start), '-m', str(PROVER_MB), '-t', str(secs), path],
                           capture_output=True, text=True, timeout=secs + 60)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 'unknown', None, 'wall timeout'
    finally:
        os.unlink(path)
    model = parse_vampire_model(out)
    status = 'model' if model else ('proved' if 'Refutation found' in out or 'SZS status Theorem' in out else 'unknown')
    return status, model, out


def one(path, secs, start):
    import numpy as np
    from .check_offline import check_finite
    from .core import Corpus, set_memory_limit
    from .named import law_index
    set_memory_limit(1500)
    r = json.load(open(path)); key = r['key']; T = r['T']
    C = Corpus(store=data('corpus')); outdir = ensure('check', 'fmb')
    open_ids = [i for i, c in enumerate(r['claims']) if c['status'] in ('unknown', 'open')]
    log = []
    for i in open_ids:
        c = r['claims'][i]
        if c['status'] not in ('unknown', 'open'): continue          # refuted by a model found for an earlier claim
        g = law_index(c['law'].replace(' ', ''))
        t0 = time.time(); st, m, out = fmb(T, g, secs, start)
        open(outdir / f'{key}_{i}.out', 'w').write(out)
        entry = {'claim': c['law'], 'status': st, 'secs': round(time.time() - t0, 1)}
        if m and m['g'] is not None:
            for j in open_ids:
                cj = r['claims'][j]
                if cj['status'] not in ('unknown', 'open'): continue
                chk = check_finite(T, [law_index(cj['law'].replace(' ', ''))], m['f'], m['g'])
                if chk['ok'] and chk['law_vector_agrees']:
                    cj['status'] = f"false (size {m['n']}, Vampire FMB)"
                    cj['fmb'] = {'n': m['n'], 'F': m['f'], 'G': m['g'], 'found_for': c['law'], 'nondeg': chk['nondeg']}
                    entry.setdefault('refutes', []).append(cj['law'])
            entry['n'] = m['n']
            if entry.get('refutes'):
                C.add(f'fmb:{key}', m['n'], np.array(m['f']), np.array(m['g']))
            else:
                entry['status'] = 'model rejected by our check'
        log.append(entry)
    r['sweep_fmb'] = {'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'secs_per_claim': secs, 'start': start, 'log': log}
    write_json(path, r)
    return {'key': key, 'laws': r['laws'], 'log': log}


def run_child(path, secs, start, n_claims):
    t0 = time.time(); timeout = n_claims * (secs + 90) + 300
    try:
        p = subprocess.run([sys.executable, '-m', 'soup.sweep_fmb', '--one', path, '--secs', str(secs),
                            '--start', str(start)], capture_output=True, text=True, timeout=timeout)
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
        if r.get('sweep_fmb'): continue
        n = sum(c['status'] in ('unknown', 'open') for c in r.get('claims', []))
        if n: out.append((p, n))
    return out


def summary():
    from .sweep_c import SURVIVORS
    s = json.load(open(data('check', 'sweep_fmb.json')))
    found = 0
    for x in s:
        lab = SURVIVORS.get(x['key'][:8], '-')
        if x.get('status') == 'crashed':
            print(lab, x['key'][:8], 'crashed', x.get('why')); continue
        for e in x['log']:
            found += bool(e.get('refutes'))
            print(lab, x['key'][:8], '|', e['claim'], '|', e['status'], e.get('n', ''), '| refutes', e.get('refutes', []),
                  f"| {e['secs']} s")
    print(len(s), 'results swept;', found, 'models accepted; not swept yet:', len(todo()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=8); ap.add_argument('--secs', type=int, default=3600)
    ap.add_argument('--start', type=int, default=2); ap.add_argument('--one'); ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()
    if a.summary:
        summary(); return
    if a.one:
        print(MARK + json.dumps(one(a.one, a.secs, a.start), ensure_ascii=False), flush=True); return
    paths = todo()
    out_path = ensure('check') / 'sweep_fmb.json'
    res = json.load(open(out_path)) if out_path.exists() else []
    print(f'{len(paths)} results with open claims not yet swept; {len(res)} earlier records kept', flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(run_child, p, a.secs, a.start, n) for p, n in paths]):
            x = f.result(); res.append(x)
            json.dump(res, open(out_path, 'w'), ensure_ascii=False, indent=1)
            print(json.dumps({k: v for k, v in x.items() if k != 'laws'}, ensure_ascii=False), flush=True)
    print('done', len(res), flush=True)


if __name__ == '__main__':
    main()
