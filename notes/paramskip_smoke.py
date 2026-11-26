"""Paired smoke runs of the parameter-disguise skip (26 Nov 2026): pskip4 (arm fusion4) and pskip5 (arm fusion5), started
together on two copies of x10's corpus, same seeds (1501+), 4 searchers and 1 verifier each, 600 s.

    podman run -i --rm -v "$PWD/work:/data:ro" -e SOUP_DATA=/data/x10 soup python3 - < notes/paramskip_smoke.py

Per run: evaluations per searcher-hour; the searchers' heartbeats (cell wins, pushes, skips, Mace4 time); the theories
pushed (pending lane and results) and the final archive elites, each checked offline with soup.paramskip on x10's
corpus (with the Mace4 step), to see how many are parameter disguises; the verified results and V6's marks.
"""
import glob
import json

from soup.core import Corpus
from soup.paramskip import ParamSkip
from soup.paths import data

C = Corpus(store=data('corpus')); C.store = None
PS = ParamSkip(C)
for run in ('pskip4', 'pskip5'):
    D = f'/data/{run}'
    L = [json.loads(s) for s in open(f'{D}/logs/stats.jsonl')]
    sh = sum(L[i]['n_search'] * (L[i + 1]['t'] - L[i]['t']) for i in range(len(L) - 1)) / 3600
    arch = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/runs/{run}/archive_s*.json'))]
    ev = sum(a['evals'] for a in arch)
    hb = [json.load(open(f)) for f in sorted(glob.glob(f'{D}/logs/workers/s*.json'))]
    tot = lambda k: sum(h.get(k) or 0 for h in hb)
    pss = max((h.get('mem') or {}).get('pss_mb', 0) for h in hb)
    print(f'== {run}: {L[-1]["elapsed_s"]:.0f} s, {sh:.2f} searcher-hours, {ev:,} evaluations = '
          f'{ev / max(1e-9, sh) / 1e6:.2f}M per searcher-hour; searcher PSS max {pss:.0f} MB; '
          f'MemAvailable min {min(x.get("mem_available_mb") or 1e9 for x in L):.0f} MB')
    print(f'   wins {tot("wins"):,}, pushed {tot("pushed"):,}, held {tot("held"):,}; skips: ignore {tot("ign_skipped"):,}, '
          f'known {tot("known_skipped"):,}, candidate {tot("cand_skipped"):,}, seen {tot("seen_skipped"):,}, '
          f'parameter {tot("par_skipped"):,} (step 1 fired {tot("pskip_fired"):,}, Mace4 {tot("pskip_mace"):,} calls, '
          f'{tot("pskip_mace_secs"):.0f} s, {tot("pskip_added")} countermodels)')
    pushed = [json.load(open(f))['T'] for f in glob.glob(f'{D}/queue/pending/*.json')]
    rs = [json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')]
    pushed += [r['T'] for r in rs]
    elites = [e['T'] for a in arch for e in a['elites']]
    print(f'   pushed {len(pushed)}: parameter disguises (offline check) {sum(PS.check(T) for T in pushed)}')
    print(f'   final archive elites {len(elites)}: disguises {sum(PS.check(T) for T in elites)}')
    print(f'   verified {len(rs)}: V6 parameter definition {sum(r.get("screened") == "parameter definition" for r in rs)}, '
          f'positive score {sum((r.get("score") or 0) > 0 for r in rs)}')
