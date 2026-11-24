"""V6 against V7 on stage b, on a fixed sample of X8 + x8b theories (24 Nov 2026, before the X9 preregistration).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/v7_bench.py > notes/v7_bench.out

Each theory's recorded stage-a output is reused: claims stage a refuted (false (size k), k <= 6) stay, every other claim
is reset to pending. Then stage_b runs once with V6 and once with V7, each on an empty in-memory corpus (models found are
not written anywhere). Sample: seed 9, 12 theories with an E-proved claim on which z3 hit its cap, and 12 with a claim
stage b left unknown or refuted by FMB, among theories whose recorded stage b took at most 600 s (the slowest ones, up
to 75 min, are left out to keep the benchmark short; this biases the measured saving down).
"""
import copy
import glob
import json
import random
import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from soup.core import Corpus
from soup.verify import V6, V7, stage_b

STAGE_A = re.compile(r'^false \(size \d+\)$')
KEEP = ('law', 'idx', 'order', 'status', 'cm_unknown_sizes')


def reset(r):
    out = {k: r[k] for k in ('T', 'laws', 'model_sizes', 'model_counts', 'richness', 'key') if k in r}
    out['redundant'] = r.get('redundant', [])
    out['claims'] = [{k: c[k] for k in KEEP if k in c} if STAGE_A.match(c['status'])
                     else dict({k: c[k] for k in KEEP if k in c and k != 'status'}, status='pending')
                     for c in r['claims']]
    return out


def run(r):
    res = {}
    for name, cfg in (('V6', V6), ('V7', V7)):
        t0 = time.time(); o = stage_b(Corpus(), copy.deepcopy(reset(r)), cfg)
        res[name] = {'secs': round(time.time() - t0, 1), 'score': o.get('score'),
                     'claims': [c['status'] for c in o['claims']]}
    return r['key'], res


rs = [json.load(open(f)) for f in sorted(glob.glob('/data/x8/results/*.json'))]
rs = [r for r in rs if r.get('stage') in ('b', 'c') and not r.get('screened') and (r.get('secs_b') or 0) <= 600]
z3cap = [r for r in rs if any(c.get('e_status') == 'proved' and c.get('z3_unproved') for c in r['claims'])]
hard = [r for r in rs if r not in z3cap and any(c['status'] in ('unknown', 'open') or 'Vampire FMB' in c['status']
                                                  or 'linear model' in c['status'] for c in r['claims'])]
rng = random.Random(9)
sample = rng.sample(z3cap, 12) + rng.sample(hard, 12)
print(f'pool: {len(rs)} theories (stage b <= 600 s); {len(z3cap)} with a z3-capped E proof, {len(hard)} with a hard claim; '
      f'sample 12 + 12', flush=True)
tot = {'V6': 0.0, 'V7': 0.0}; changed = 0; score_diff = 0
with ProcessPoolExecutor(8) as ex:
    futs = {ex.submit(run, r): ('z3cap' if i < 12 else 'hard') for i, r in enumerate(sample)}
    for f in as_completed(futs):
        key, res = f.result(); grp = futs[f]
        for k in tot: tot[k] += res[k]['secs']
        diff = [(a, b) for a, b in zip(res['V6']['claims'], res['V7']['claims']) if a != b]
        changed += len(diff); score_diff += res['V6']['score'] != res['V7']['score']
        print(f"{key[:8]} {grp:5s} V6 {res['V6']['secs']:7.1f} s  V7 {res['V7']['secs']:7.1f} s  score {res['V6']['score']} / "
              f"{res['V7']['score']}  changed {diff}", flush=True)
print(f"total stage b: V6 {tot['V6']:.0f} s, V7 {tot['V7']:.0f} s ({100 * (1 - tot['V7'] / tot['V6']):.0f}% less); "
      f"claims with a different outcome {changed}; theories with a different score {score_diff}")
