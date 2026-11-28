"""N2, item C4 (PREREGISTRATION.md, N2; post hoc, 28 Nov 2026): run N1's undecided checks to a decision.

    python -m soup.decide [--jobs 2]

Reads check/n2_pre.json (soup.novelty2 --stage pre) and decides every flag of the candidates that pass C1-C3.
- 'split None' / 'split not run': soup.split.screen on sizes 2-5 (up to 3,000 Mace4 models and 300 s per size), then
  the split proof with the one-operation laws of order <= 3 that hold on the union corpus (E 120 s per call); one
  subprocess per theory, 3,600 s wall time. Outcome true, false (a mixed-table certificate) or none.
- 'R1 kind?': every law the relation lacks gets E for 300 s; for a law E does not prove, Mace4 on sizes 2-8 (600 s),
  then Vampire FMB (300 s), then soup.linear.claim (rings to q = 64, affine to 16, 600 s) look for a separating model,
  re-checked on its tables (law_vector). Outcome 'known' (every law proved), 'not' (a separating model) or
  'undecided'.
Writes check/decide_n2.json (resumable: decided theories are kept).
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

from .paths import data

SPLIT_WALL = 3600


def split_one(T, cand):
    """Child process: the split decision for one theory, given its candidate one-operation laws."""
    from .provers import prove_e
    from .split import screen, one_op
    s = screen(T, sizes=(2, 3, 4, 5), cap=3000, secs=300)
    if s['split'] is False: return s
    proved = [t for t in cand if prove_e(sorted(T), t, processed_limit=200_000, cpu_limit=120)['status'] == 'proved']
    for t in T:
        if t in proved or one_op(t): continue
        if prove_e(sorted(set(proved) | {u for u in T if one_op(u)}), t, processed_limit=500_000,
                   cpu_limit=240)['status'] != 'proved':
            return {'split': None, 'why': 'E did not derive a bridge law from one-operation consequences',
                    'one_op_consequences': len(proved)}
    return {'split': True, 'one_op_consequences': len(proved)}


def _split_job(key, T, cand):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
        json.dump({'T': T, 'cand': cand}, fh); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, '-m', 'soup.decide', '--split-one', path], capture_output=True, text=True,
                           timeout=SPLIT_WALL)
        res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {'split': None, 'why': r.stderr[-300:]}
    except subprocess.TimeoutExpired:
        res = {'split': None, 'why': f'wall time {SPLIT_WALL} s'}
    res['secs'] = round(time.time() - t0)
    return key, res


def _model_fails(prem, goal, F, G):
    from .core import law_vector
    F, G = np.asarray(F), np.asarray(G)
    v = law_vector(F, G, len(F))
    return bool(all(v[t] for t in prem) and not v[goal])


def decide_goal(prem, goal):
    """'proved', or ('model', how, tables) for a separating model re-checked on its tables, or 'undecided'."""
    from .provers import prove_e, mace4, prove_vampire
    from .linear import claim
    if prove_e(sorted(prem), goal, processed_limit=2_000_000, cpu_limit=300)['status'] == 'proved':
        return {'goal': goal, 'outcome': 'proved'}
    m = mace4(sorted(prem), goal, 2, 8, 600)
    if m['size'] and _model_fails(prem, goal, *m['tables']):
        return {'goal': goal, 'outcome': 'model', 'how': f"Mace4, size {m['size']}", 'tables': m['tables']}
    v = prove_vampire(sorted(prem), goal, cpu_limit=300, extra=('-sa', 'fmb'))
    mod = v.get('model')
    if mod and mod.get('f') is not None and mod.get('g') is not None and _model_fails(prem, goal, mod['f'], mod['g']):
        return {'goal': goal, 'outcome': 'model', 'how': f"Vampire FMB, size {mod['n']}", 'tables': [mod['f'], mod['g']]}
    c = claim(sorted(prem), goal, budget=600)
    if c['status'] == 'refuted':
        return {'goal': goal, 'outcome': 'model', 'how': f"soup.linear, {c['family']} over {c['ring']}",
                'recheck': {k: c[k] for k in c if k not in ('params',)}}
    return {'goal': goal, 'outcome': 'undecided', 'mace4': m['reason'], 'mace4_searched_to': m['searched_to'],
            'vampire_fmb': v['status'], 'linear': c['status']}


def _r1_job(key, T, rel, N):
    if rel['kind'] == 'fragment?':
        prem, goals = list(N), [t for t in T if t not in N]
    else:
        prem, goals = list(T), [v for v in N if v not in T]
    res = [decide_goal(prem, g) for g in goals]
    if all(r['outcome'] == 'proved' for r in res): out = 'known'
    elif any(r['outcome'] == 'model' for r in res): out = 'not'
    else: out = 'undecided'
    return key, dict(rel, outcome=out, goals=res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--split-one')
    a = ap.parse_args()
    if a.split_one:
        job = json.load(open(a.split_one))
        print(json.dumps(split_one(job['T'], job['cand']))); return
    from .core import ORDER
    from .dedupe import union_corpus
    from .rediscover import variants
    from .split import one_op
    pre = json.load(open(data('check', 'n2_pre.json')))
    path = data('check', 'decide_n2.json')
    out = json.load(open(path)) if path.exists() else {}
    r1 = (json.load(open(data('check', 'rediscover.json'))) or {}).get('sources', {})
    V = {(name, rname): N for name, rname, N in variants()}
    todo_split, todo_r1 = [], []
    C = None
    for r in pre:
        if not r['flags']: continue
        d = out.setdefault(r['key'], {})
        if any(f.startswith('split') for f in r['flags']) and 'split' not in d:
            if C is None: C = union_corpus()
            imp = C.implied(sorted(r['T']))
            cand = [int(t) for t in np.nonzero(imp)[0] if ORDER[t] <= 3 and one_op(int(t)) and t not in r['T']][:200] \
                if imp is not None else []
            todo_split.append((r['key'], r['T'], cand))
        done = {(x['entry'], x['relabel'], x['kind']) for x in d.get('r1', [])}
        for x in r1.get(r['source'], {}).get('relations', []):
            if x['key'] != r['key'] or not x['kind'].endswith('?'): continue
            if (x['entry'], x['relabel'], x['kind']) in done: continue
            todo_r1.append((r['key'], r['T'], x, V[(x['entry'], x['relabel'])]))
    del C
    print(f'{len(todo_split)} split decisions, {len(todo_r1)} R1 relations to decide', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(_split_job, *j) for j in todo_split] + [ex.submit(_r1_job, *j) for j in todo_r1]
        for n, f in enumerate(as_completed(futs), 1):
            key, res = f.result()
            d = out.setdefault(key, {})
            if 'kind' in res: d.setdefault('r1', []).append(res); what = f"R1 {res['kind']} {res['entry']}: {res['outcome']}"
            else: d['split'] = res['split']; d['split_detail'] = res; what = f"split: {res['split']}"
            json.dump(out, open(path, 'w'), indent=1, default=int)
            print(f'  {n}/{len(futs)} {key[:8]} {what} ({round(time.time() - t0)} s)', flush=True)
    print(json.dumps({'split': {str(v): sum(1 for d in out.values() if d.get('split', 'x') == v) for v in (True, False, None)},
                      'r1': {o: sum(1 for d in out.values() for x in d.get('r1', []) if x['outcome'] == o)
                             for o in ('known', 'not', 'undecided')}}))


if __name__ == '__main__':
    main()
