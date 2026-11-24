"""Independent re-check of the linear sweep's refutations in one data directory: each model's tables are rebuilt from
its ring and parameters and passed to soup.check_offline.check_finite (the check that Vampire FMB models go through:
its own evaluator, plus agreement with law_vector).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - x8 < notes/linear_x8_check.py
"""
import json
import sys

from soup.check_offline import check_finite
from soup.data import LAWS
from soup.linear import rings, tables

d = sys.argv[1] if len(sys.argv) > 1 else 'x8'
R = {r.name: r for r in rings(64)}
rows = [x for x in json.load(open(f'/data/{d}/check/linear_sweep.json')) if x['status'] == 'refuted']
ok = 0
for x in rows:
    res = json.load(open(f"/data/{d}/results/{x['key']}.json"))
    F, G = tables(R[x['ring']], x['params'])
    F = [[int(v) for v in row] for row in F]; G = [[int(v) for v in row] for row in G]
    c = check_finite(res['T'], [x['idx']], F, G)
    ok += c['ok']
    print(f"{x['key'][:8]} {x['ring']:7s} {x['family']:6s} {LAWS[x['idx']]:32s} ok {c['ok']} nondeg {c['nondeg']} "
          f"law_vector_agrees {c['law_vector_agrees']}", flush=True)
print(f'{ok} of {len(rows)} refutations pass check_finite')
