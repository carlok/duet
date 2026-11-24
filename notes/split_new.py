"""Split check for the candidates of the given sources that check/split_candidates.json does not have yet, one child
process per candidate with a wall-time cap, merged into check/split_candidates.json. A capped candidate is recorded
with split None and why 'timeout'. (`soup.split --set candidates` works in file order and stalls on X4's unchecked
candidates: CLAUDE.md pitfall.)

    podman run -i --rm -v "$PWD/work:/data" soup python3 - x8 [--secs 900 --jobs 6] < notes/split_new.py
"""
import argparse
import json
import multiprocessing as mp
import time

from soup.paths import data
from soup.split import check


def _run(T, q):
    try: q.put(check(T))
    except Exception as e: q.put({'split': None, 'why': f'error: {e!r}'})


ap = argparse.ArgumentParser(); ap.add_argument('sources', nargs='+')
ap.add_argument('--secs', type=float, default=900); ap.add_argument('--jobs', type=int, default=6)
a = ap.parse_args()
path = data('check', 'split_candidates.json')
res = json.load(open(path))
done = {json.dumps(sorted(r['T'])) for r in res}
todo = [c for c in json.load(open(data('check', 'candidates.json')))
        if c['source'] in a.sources and json.dumps(sorted(c['T'])) not in done]
print(f'{len(todo)} candidates to check from {a.sources}', flush=True)
running = []
while todo or running:
    while todo and len(running) < a.jobs:
        c = todo.pop(0); q = mp.Queue(); p = mp.Process(target=_run, args=(c['T'], q)); p.start()
        running.append((c, p, q, time.time()))
    time.sleep(1)
    for item in list(running):
        c, p, q, t0 = item
        r = None
        if not q.empty(): r = q.get()
        elif time.time() - t0 > a.secs: p.terminate(); r = {'split': None, 'why': 'timeout', 'secs': a.secs}
        elif not p.is_alive():
            try: r = q.get(timeout=5)
            except Exception: r = {'split': None, 'why': 'child died'}
        if r is None: continue
        p.join(1); running.remove(item)
        res.append(dict(r, key=str(c['key']), source=c['source'], laws=c['laws'], T=c['T']))
        json.dump(res, open(path, 'w'), ensure_ascii=False, indent=1)
        w = f"(witness n = {r['witness']['n']})" if r.get('witness') else ''
        print(f"{str(c['key'])[:8]} {c['source']:6s} split {r['split']} {r.get('why', '')} {w}", flush=True)
