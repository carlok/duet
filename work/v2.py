"""v2 scoring: fusion gain verified by countermodel search + z3 proof effort, times model richness."""
import sys, math, time
sys.path.insert(0, '/home/claude/soup')
import numpy as np, itertools
CAP = 8
def relabel(T, p):
    n = len(p); inv = [0] * n
    for i, j in enumerate(p): inv[j] = i
    return np.array([[p[T[inv[x], inv[y]]] for y in range(n)] for x in range(n)])
from soup2 import Corpus, find_model, prove, LAWS, ORDER, NL, TREES
BRIDGE = np.array(['·' in s and '∘' in s for s in LAWS])

def fusion_gain(C, T):
    """Laws implied (on the corpus) by T but by no single law of T."""
    imp = C.implied(T)
    if imp is None: return None
    single = np.zeros(NL, bool)
    for t in T:
        s = C.implied([t])
        if s is not None: single |= s
    return np.flatnonzero(imp & ~single)

def verify(C, T, n_cands=3, prove_rlimit=30_000_000, model_rlimit=10_000_000):
    T = sorted(set(T)); out = {'T': T, 'laws': [LAWS[t] for t in T]}
    counts = {}
    for n in (2, 3, 4):
        found = []
        while len(found) < CAP:
            avoid = [(relabel(F, p), relabel(G, p)) for F, G in found for p in itertools.permutations(range(n))]
            r = find_model(T, n, nondeg=True, rlimit=model_rlimit, avoid=avoid)
            if not isinstance(r, tuple): break
            found.append(r); C.add(f'model-{n}', n, *r)
        counts[n] = len(found)
    r = find_model(T, 5, nondeg=True, rlimit=model_rlimit)
    if isinstance(r, tuple): C.add('model-5', 5, *r)
    counts[5] = 1 if isinstance(r, tuple) else 0
    sizes = [n for n, c in counts.items() if c]
    out['model_sizes'] = sizes; out['model_counts'] = counts; out['richness'] = sum(counts.values())
    if not sizes: out.update(score=0.0, status='no small non-degenerate model'); return out
    # independence: each law must fail somewhere the others hold
    redundant, unconfirmed = [], []
    for t in T:
        rest = [u for u in T if u != t]
        imp = C.implied(rest)
        if imp is not None and not imp[t]: continue
        ok = False
        for n in (2, 3, 4, 5):
            r = find_model(rest, n, goal=t, rlimit=model_rlimit)
            if isinstance(r, tuple): C.add(f'indep-{n}', n, *r); ok = True; break
        if not ok:
            st, _ = prove(rest, t, 10_000_000)
            (redundant if st == 'proved' else unconfirmed).append(LAWS[t])
    out['redundant'] = redundant; out['independence_unconfirmed'] = unconfirmed
    base = max(1, prove(T, T[0], 5_000_000)[1])
    claims = []
    tried = set()
    for _ in range(3 * n_cands):   # refuted claims are replaced by the next-shortest candidates
        fg = fusion_gain(C, T)
        if fg is None: break
        fg = [e for e in sorted(fg, key=lambda e: (ORDER[e], e)) if e not in tried]
        if not fg or len([c for c in claims if c['status'] != 'false']) >= n_cands: break
        e = fg[0]; tried.add(e); c = {'law': LAWS[e], 'order': int(ORDER[e])}
        refuted = False
        for n in (2, 3, 4):
            r = find_model(T, n, goal=e, rlimit=model_rlimit)
            if isinstance(r, tuple): C.add(f'cm-{n}', n, *r); refuted = True; c['status'] = f'false (size {n})'; break
        if not refuted:
            st, used = prove(T, e, prove_rlimit)
            c['status'] = st; c['effort'] = used; c['difficulty'] = round(max(0.0, math.log10(used / base)), 3)
        claims.append(c)
    out['claims'] = claims
    gain = sum(max(c['difficulty'], 0.1) / (1 + c['order']) for c in claims if c['status'] == 'proved')
    out['open'] = [c['law'] for c in claims if c['status'] == 'unknown']
    out['gain'] = round(gain, 4); out['n_proved'] = sum(c['status'] == 'proved' for c in claims)
    out['max_difficulty'] = max([c['difficulty'] for c in claims if c['status'] == 'proved'] or [0.0])
    out['score'] = round(gain * math.log2(1 + out['richness']) / math.log2(1 + 3 * CAP + 1) * (0.5 if redundant else 1.0), 4)
    out['status'] = 'ok'
    return out
