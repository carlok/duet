"""Light dig of one candidate (23 Nov 2026, night): short consequences and the one-operation shadow.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <key prefix> < notes/dig_light.py

1. Laws of order <= 3 that T implies on the merged corpora, tested with E (20 s each, 3 threads), starred if no
   single law implies them on the corpus.
2. The shadow T + (x·y = x∘y): does it collapse (x·y = x and x·y = y), and a few named one-operation laws (E, 30 s).
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor

from soup.core import Corpus, ORDER
from soup.data import LAWS
from soup.named import law_index
from soup.relabel import _proves

key = sys.argv[1]
c = next(c for c in json.load(open('/data/check/candidates.json')) if c['key'].startswith(key))
T = sorted(c['T']); src = c['source']
print(key, src, 'T =', ' & '.join(LAWS[t] for t in T))
C = Corpus(store='/data/corpus' if src == '.' else f'/data/{src}/corpus')
imp = C.implied(T); singles = [C.implied([t]) for t in T]
cand = [int(e) for e in range(len(LAWS)) if imp[e] and ORDER[e] <= 3 and e not in T]
with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(lambda e: (e, _proves(T, [e], 20)), cand))
proved = [e for e, ok in res if ok]
emergent = [e for e in proved if not any(s is not None and s[e] for s in singles)]
print(f'1. {len(cand)} laws of order <= 3 implied on the corpus; {len(proved)} proved by E; {len(emergent)} emergent')
for e in sorted(proved, key=lambda e: (ORDER[e], LAWS[e])):
    if ORDER[e] >= 1: print(('  * ' if e in emergent else '    ') + LAWS[e])
S = T + [law_index('x·y=x∘y')]
print('2. shadow T + (x·y = x∘y):')
for s in ['x·y=x', 'x·y=y', 'x·x=x', 'x·y=y·x', '(x·y)·z=x·(y·z)', 'x·(x·y)=y', '(x·y)·y=x', 'x·(y·z)=x·y']:
    print(f'   => {s:18s}', _proves(S, [law_index(s)], 30), flush=True)
