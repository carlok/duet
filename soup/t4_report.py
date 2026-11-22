"""T4 analysis (PREREGISTRATION.md, T4). Run after `SOUP_DATA=/data/t4-<arm> python -m soup.fragments` for both arms.

    python -m soup.t4_report          reads /data/t4-prior and /data/t4-noprior; writes /data/t4_report.json

Primary: among verified theories with positive score, the share that are fragments of a named theory, per
arm; one-sided Fisher exact test (prior > noprior), undecided theories excluded, plus the two bounds with
undecided counted as fragments / as non-fragments.
Secondary: the top 10 non-fragment theories per arm by score, deduplicated across both arms up to the three
dualities (theory_key) and up to equivalence (each theory proves every law of the other with E; compared only
when their model counts on 2-5 elements agree, a necessary condition).
"""
import json
from concurrent.futures import ProcessPoolExecutor

from .calib_report import fisher_greater
from .duality import theory_key
from .paths import DATA

ARMS = ('prior', 'noprior')


def proves_all(job):
    from .provers import prove_e
    A, B = job
    for t in B:
        if t in A: continue
        s = prove_e(A, t, processed_limit=200_000, cpu_limit=60)['status']
        if s != 'proved': return None if s == 'error' else False     # 'error': E was killed, e.g. by the OOM killer
    return True


def main():
    F = {a: json.load(open(DATA / f't4-{a}' / 'fragments.json')) for a in ARMS}
    R = {a: {} for a in ARMS}
    for a in ARMS:
        import glob
        for f in glob.glob(str(DATA / f't4-{a}' / 'results' / '*.json')):
            r = json.load(open(f)); R[a][r['key']] = r
    out = {'primary': {}, 'secondary': []}
    tab = {}
    for a in ARMS:
        rows = F[a]
        fr = sum(bool(x['fragment_of']) for x in rows)
        und = sum(not x['fragment_of'] and bool(x['undecided']) for x in rows)
        no = len(rows) - fr - und
        tab[a] = (fr, no, und)
        out['primary'][a] = {'positive_score': len(rows), 'fragment': fr, 'not_fragment': no, 'undecided': und,
                             'share_decided': round(fr / max(1, fr + no), 3),
                             'bounds': [round(fr / max(1, len(rows)), 3), round((fr + und) / max(1, len(rows)), 3)]}
    (a1, b1, _), (a2, b2, _) = tab['prior'], tab['noprior']
    out['primary']['fisher_one_sided_p'] = fisher_greater(a1, b1, a2, b2)
    # secondary
    cand = []
    for a in ARMS:
        nf = [x for x in F[a] if not x['fragment_of'] and not x['undecided']]
        nf.sort(key=lambda x: -(x['score'] or 0))
        cand += [dict(x, arm=a) for x in nf[:10]]
    groups = []
    for x in cand:
        x['dkey'] = theory_key(x['T']); x['mc'] = R[x['arm']][x['key']].get('model_counts')
    pairs = [(i, j) for i in range(len(cand)) for j in range(i + 1, len(cand))
             if cand[i]['dkey'] != cand[j]['dkey'] and cand[i]['mc'] == cand[j]['mc']]
    import os
    with ProcessPoolExecutor(int(os.environ.get('T4R_JOBS', 10))) as ex:   # 10 E runs at once hit the OOM killer
        fw = list(ex.map(proves_all, [(cand[i]['T'], cand[j]['T']) for i, j in pairs]))
        bw = list(ex.map(proves_all, [(cand[j]['T'], cand[i]['T']) for i, j in pairs]))
    same = {(i, j) for (i, j), f, b in zip(pairs, fw, bw) if f and b}
    out['equivalence_pairs'] = len(pairs)
    out['equivalence_unknown'] = [[i, j] for (i, j), f, b in zip(pairs, fw, bw) if f is None or b is None]
    rep = list(range(len(cand)))
    for i in range(len(cand)):
        for j in range(i):
            if cand[i]['dkey'] == cand[j]['dkey'] or (j, i) in same: rep[i] = rep[j]; break
    for i, x in enumerate(cand):
        out['secondary'].append({'arm': x['arm'], 'score': x['score'], 'laws': x['laws'], 'dualities': x['dualities'],
                                 'same_as': None if rep[i] == i else rep[i]})
    json.dump(out, open(DATA / 't4_report.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out['primary'], indent=1))
    for i, s in enumerate(out['secondary']):
        print(i, s['arm'], s['score'], ' & '.join(s['laws'])[:110], '' if s['same_as'] is None else f"= #{s['same_as']}")


if __name__ == '__main__':
    main()
