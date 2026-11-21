"""For each verified theory: which named theories validate all its laws (z3 proof of each law from the named axioms)?"""
import sys, glob, pickle
sys.path.insert(0, '/home/claude/soup')
from soup2 import prove
from named import law_index
NAMED = {
  'lattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·y = y·x', 'x∘y = y∘x', 'x·(x∘y) = x', 'x∘(x·y) = x'],
  'skew lattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·(x∘y) = x', '(y∘x)·x = x', 'x∘(x·y) = x', '(y·x)∘x = x'],
  'dimonoid': ['(x·y)·z = x·(y·z)', '(x·y)·z = x·(y∘z)', '(x∘y)·z = x∘(y·z)', '(x·y)∘z = x∘(y∘z)', '(x∘y)∘z = x∘(y∘z)']}
AX = {k: [law_index(s) for s in v] for k, v in NAMED.items()}
import numpy as np
from soup import LM, PM, unpack_probes, unpack_laws
from soup2 import find_model, law_vector
HOLDS = {}
for n, ax in AX.items():   # laws true in every corpus model of the named theory, plus small z3-found models
    s_ = unpack_probes(np.bitwise_and.reduce(LM[ax], axis=0)); acc = unpack_laws(np.bitwise_and.reduce(PM[s_], axis=0))
    for size in (3, 4):
        found = []
        for _ in range(4):
            r = find_model(ax, size, rlimit=5_000_000, avoid=found)
            if not isinstance(r, tuple): break
            found.append(r); acc &= law_vector(r[0], r[1], size)
    HOLDS[n] = acc
_cache = {}
def valid_in(name, t):
    if not HOLDS[name][t]: return False
    if (name, t) not in _cache: _cache[(name, t)] = prove(AX[name], t, 2_000_000)[0] == 'proved'
    return _cache[(name, t)]
V = {}
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else 'loopdual_*.pkl')):
    V.update(pickle.load(open(f, 'rb'))['verified'])
rows = []
for T, r in V.items():
    if r.get('score', 0) <= 0: continue
    frag = [n for n in AX if all(valid_in(n, t) for t in T)]
    rows.append((r['score'], r.get('dualities', []), r['laws'], frag))
rows.sort(key=lambda x: -x[0])
print(f'{len(rows)} verified theories with positive score; lattice fragments: {sum("lattice" in x[3] for x in rows)}, skew-lattice fragments: {sum("skew lattice" in x[3] for x in rows)}, dimonoid fragments: {sum("dimonoid" in x[3] for x in rows)}')
for s, d, laws, frag in rows[:20]:
    print(f"{s:.3f} {','.join(d) or '-':14s} {' & '.join(laws)[:120]}  -> {', '.join(frag) or 'not a fragment of these'}")
pickle.dump(rows, open('fragments.pkl', 'wb'))
