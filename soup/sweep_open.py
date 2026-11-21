"""Re-check every open claim in results/ with E (long budget); saturations get the independent convergence
certificate and a Vampire cross-check; proofs get a Vampire cross-check.  python -m soup.sweep_open"""
import glob
import json
from concurrent.futures import ProcessPoolExecutor

from .confluence import check
from .paths import data
from .provers import prove_e, prove_vampire


def one(job):
    key, T, laws, c = job
    e = prove_e(T, c['idx'], processed_limit=2_000_000, cpu_limit=300)
    out = {'key': key, 'laws': laws, 'claim': c['law'], 'e': e['status'], 'e_steps': e.get('proof_steps')}
    if e['status'] in ('proved', 'countersatisfiable'):
        out['vampire'] = prove_vampire(T, c['idx'], cpu_limit=120)['status']
    if e['status'] == 'countersatisfiable':
        cert = check(T, c['idx'])
        out['certificate'] = cert['ok']; out['cert_detail'] = {k: cert.get(k) for k in ('rules', 'critical_pairs', 'why')}
    return out


def main():
    jobs = []
    for f in sorted(glob.glob(str(data('results', '*.json')))):
        r = json.load(open(f))
        for c in r.get('claims', []):
            if c['status'] in ('unknown', 'open'): jobs.append((r['key'], r['T'], r['laws'], c))
    with ProcessPoolExecutor(10) as ex: res = list(ex.map(one, jobs))
    json.dump(res, open(data('check', 'open_sweep.json'), 'w'), indent=1, ensure_ascii=False)
    for x in res: print(json.dumps(x, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
