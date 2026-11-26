"""Paired live smoke runs of arm fusion6 against fusion5 (26 Nov 2026, after X11): fam5 (fusion5) and fam6 (fusion6),
started together on two copies of x11's corpus with a known library rebuilt after X11. Same seeds (1701+), 4 searchers
and 1 verifier each, 900 s, normal maintenance (corpus refresh, verified scores, gate). The copies are deleted afterwards.

    podman run -i --rm -v "$PWD/work:/data:ro" -e SOUP_DATA=/data/x11 soup python3 - < notes/fusion6_smoke.py

Per run: evaluations per searcher-hour; the rescores (count, seconds, share of searcher time) and the archive size from
the searchers' heartbeats; pushes and holds; and the families of every pushed theory (pending, claimed, stage c,
dropped and verified), labelled on one common corpus (x11's, unchanged by the smoke runs) with soup.taxonomy.family_of,
so the two runs are labelled alike. 'New to F1': a family no structured theory in check/families.json has.
"""
import collections
import glob
import json
import math
import os

from soup.core import Corpus
from soup.paths import data
from soup.taxonomy import family_of

C = Corpus(store=data('corpus')); C.store = None
F1 = {t['family'] for t in json.load(open('/data/check/families.json'))['theories'] if t['primary'] == 'structured'}
cache = {}


def fam(T):
    k = tuple(sorted(T))
    if k not in cache: cache[k] = family_of(C.implied(list(k)))
    return cache[k]


def spread(labels):
    c = collections.Counter(labels); n = sum(c.values())
    if not n: return {'n': 0}
    H = -sum(v / n * math.log(v / n) for v in c.values())
    return {'n': n, 'distinct': len(c), 'largest_share': round(max(c.values()) / n, 3),
            'effective': round(math.exp(H), 1), 'new_to_F1': sum(1 for f in c if f not in F1)}


for run, arm in (('fam5', 'fusion5'), ('fam6', 'fusion6')):
    D = f'/data/{run}'
    L = [json.loads(s) for s in open(f'{D}/logs/stats.jsonl')]
    sh = sum(L[i]['n_search'] * (L[i + 1]['t'] - L[i]['t']) for i in range(len(L) - 1)) / 3600
    arch = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/runs/{run}/archive_s*.json'))]
    ev = sum(a['evals'] for a in arch)
    hb = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/logs/workers/s*.json'))]
    tot = lambda k: sum(h.get(k) or 0 for h in hb)
    pss = max((h.get('mem') or {}).get('pss_mb', 0) for h in hb)
    print(f'== {run} ({arm}): {L[-1]["elapsed_s"]:.0f} s, {sh:.2f} searcher-hours, {ev:,} evaluations = '
          f'{ev / max(1e-9, sh) / 1e6:.2f}M per searcher-hour; searcher PSS max {pss:.0f} MB; '
          f'MemAvailable min {min(x.get("mem_available_mb") or 1e9 for x in L):.0f} MB')
    print(f'   archive elites {sum(len(a["elites"]) for a in arch):,} (per searcher {[len(a["elites"]) for a in arch]}); '
          f'rescores {tot("rescores")} in {tot("rescore_secs"):.0f} s = '
          f'{tot("rescore_secs") / max(1e-9, 3600 * sh):.1%} of searcher time; per searcher '
          f'{[(h.get("rescores"), round(h.get("rescore_secs") or 0)) for h in hb]}')
    print(f'   wins {tot("wins"):,}, pushed {tot("pushed"):,}, held {tot("held"):,}; parameter skips {tot("par_skipped")} '
          f'(Mace4 {tot("pskip_mace")} calls, {tot("pskip_mace_secs"):.0f} s)')
    items = []
    for lane in ('pending', 'claimed', 'stage2c', 'dropped'):
        items += [json.load(open(f)) for f in glob.glob(f'{D}/queue/{lane}/*.json')]
    rs = [json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')]
    pushedT = [it['T'] for it in items if 'T' in it] + [r['T'] for r in rs]
    print(f'   pushed theories found {len(pushedT)}: families {spread([fam(T) for T in pushedT])}')
    print(f'   verified {len(rs)}: positive {sum((r.get("score") or 0) > 0 for r in rs)}, screened '
          f'{dict(collections.Counter(r.get("screened") for r in rs if r.get("screened")))}; families '
          f'{spread([fam(r["T"]) for r in rs])}')
    top = collections.Counter(fam(T) for T in pushedT).most_common(3)
    print(f'   largest families among pushes: {top}')
    # what the verifiers reach: the pending lane is claimed highest priority first (X11: about 80 theories per hour)
    pend = sorted((json.load(open(f)) for f in glob.glob(f'{D}/queue/pending/*.json')), key=lambda it: -it['prio'])
    for n in (80, 500, len(pend)):
        P = pend[:n]
        print(f'   pending top {n}: mean cheap {sum(it["cheap"] for it in P) / max(1, len(P)):.2f}, families '
              f'{spread([fam(it["T"]) for it in P])}')
