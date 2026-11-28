"""N2, item C5 (PREREGISTRATION.md, N2; post hoc, 28 Nov 2026): a second prover for every claim E proved.

    python -m soup.reprove [--secs 120] [--jobs 2]

Reads check/n2_pre.json (soup.novelty2 --stage pre: the candidates that pass C1-C3, with their proved claims). Each
claim is given to Vampire (prove_vampire, discount, secs) and, if Vampire does not prove it, to Twee (secs). Writes
check/reprove_n2.json: {key: {claim index: true if a second prover confirms it, else false}} and the details. A claim
that a prover reports countersatisfiable with a model is re-checked on the model's tables and listed; none is called
false unless a finite model refutes it. Resumable: claims already decided are kept.
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data


def confirm(T, idx, secs):
    from .provers import prove_vampire, prove_twee
    v = prove_vampire(sorted(T), idx, cpu_limit=secs)
    rec = {'vampire': v['status'], 'vampire_secs': v.get('secs')}
    if v['status'] == 'proved': return True, rec
    if v.get('model'):
        rec['vampire_model'] = v['model']
    t = prove_twee(sorted(T), idx, seconds=secs)
    rec.update(twee=t['status'], twee_secs=t.get('secs'))
    return t['status'] == 'proved', rec


def refuted_by(T, idx, model):
    """True if the model (Vampire's parsed tables) satisfies T and fails the claim, re-checked with law_vector."""
    import numpy as np
    from .core import law_vector
    if not model or model.get('f') is None or model.get('g') is None: return None
    F, G = np.array(model['f']), np.array(model['g'])
    v = law_vector(F, G, len(F))
    return bool(all(v[t] for t in T) and not v[idx])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--secs', type=int, default=120)
    ap.add_argument('--jobs', type=int, default=2)
    a = ap.parse_args()
    pre = json.load(open(data('check', 'n2_pre.json')))
    path = data('check', 'reprove_n2.json')
    out = json.load(open(path)) if path.exists() else {'confirmed': {}, 'details': {}}
    items = [(r['key'], r['T'], idx) for r in pre for idx in r['proved_idx']
             if str(idx) not in out['confirmed'].get(r['key'], {})]
    print(f'{len(pre)} candidates, {sum(len(r["proved_idx"]) for r in pre)} proved claims, {len(items)} to do', flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(a.jobs) as ex:              # provers run as subprocesses: threads are enough
        futs = {ex.submit(confirm, T, idx, a.secs): (key, T, idx) for key, T, idx in items}
        for n, f in enumerate(as_completed(futs), 1):
            key, T, idx = futs[f]
            ok, rec = f.result()
            if 'vampire_model' in rec: rec['refuted'] = refuted_by(T, idx, rec.pop('vampire_model'))
            out['confirmed'].setdefault(key, {})[str(idx)] = ok
            out['details'].setdefault(key, {})[str(idx)] = rec
            if n % 20 == 0 or n == len(items):
                json.dump(out, open(path, 'w'), indent=1)
                c = sum(v for d in out['confirmed'].values() for v in d.values())
                tot = sum(len(d) for d in out['confirmed'].values())
                print(f'  {n}/{len(items)} done; confirmed {c} of {tot} ({round(time.time() - t0)} s)', flush=True)
    json.dump(out, open(path, 'w'), indent=1)
    flat = [(k, i, out['details'][k][i]) for k, d in out['confirmed'].items() for i, v in d.items() if not v]
    print(f'unconfirmed: {len(flat)} claims in {len({k for k, _, _ in flat})} candidates')
    for k, i, rec in flat: print(f'  {k[:8]} claim {i}: {rec}')


if __name__ == '__main__':
    main()
