"""Verification of a theory, in stages (T1).

  stage a  model census (non-isomorphic non-degenerate models, <= 8 per size on 2-4, one on 5),
           independence of each law (countermodel to size 6, else a bounded proof),
           emergent-law claims (fusion gain on the corpus) checked by countermodel search to size 6.
           Seconds.
  stage b  E first (20k processed clauses): saturation refutes the claim, a proof gives e_steps; then a
           bounded z3 proof; z3 effort -> difficulty (kept for comparability); score.
  stage c  only for claims still open after b: grounded countermodel search on 7-8 elements, E with
           2M processed clauses, then a long z3 run. Each claim ends as proved, false (size k) or open with the budget stated.

Every model found goes into the corpus immediately (and so into the shared store, when there is one).
"""
import itertools
import math
import time

import numpy as np

from .core import Corpus, Grounding, prove, LAWS, ORDER, NL, TREES
from .provers import prove_e

CAP = 8
BRIDGE = np.array(['·' in s and '∘' in s for s in LAWS])

DEFAULTS = dict(
    census_sizes=(2, 3, 4), census_single=(5,), model_rlimit=10_000_000,
    indep_sizes=(2, 3, 4, 5, 6), redundant_rlimit=10_000_000,
    claim_sizes=(2, 3, 4, 5, 6), n_cands=3, max_tried=9,
    prove_rlimit=30_000_000, base_rlimit=5_000_000,
    c_sizes=(7, 8), c_model_rlimit=50_000_000, c_prove_rlimit=300_000_000,
    e_limit=20_000, e_cpu=20, c_e_limit=2_000_000, c_e_cpu=300, use_e=True,
)
# The first-session verifier (countermodels only to size 4/5): kept to reproduce results-cloud/.
LEGACY = dict(DEFAULTS, indep_sizes=(2, 3, 4, 5), claim_sizes=(2, 3, 4), use_e=False)


def relabel(T, p):
    n = len(p); inv = [0] * n
    for i, j in enumerate(p): inv[j] = i
    return np.array([[p[T[inv[x], inv[y]]] for y in range(n)] for x in range(n)])


def fusion_gain(C, T):
    """Laws implied (on the corpus) by T but by no single law of T."""
    imp = C.implied(T)
    if imp is None: return None
    single = np.zeros(NL, bool)
    for t in T:
        s = C.implied([t])
        if s is not None: single |= s
    return np.flatnonzero(imp & ~single)


class _G:
    """Groundings cached for the duration of one verification."""
    def __init__(self): self.c = {}
    def __call__(self, T, n):
        k = (tuple(T), n)
        if k not in self.c: self.c[k] = Grounding(T, n)
        return self.c[k]


def _countermodel(C, G, T, goal, sizes, rlimit, tag):
    """Smallest model of T violating goal on the given sizes. Returns (size or None, sizes where z3 ran out)."""
    unknown = []
    for n in sizes:
        r = G(T, n).find(goal=goal, rlimit=rlimit)
        if isinstance(r, tuple):
            C.add(f'{tag}-{n}', n, *r); return n, unknown
        if r == 'unknown': unknown.append(n)
    return None, unknown


def stage_a(C, T, cfg=DEFAULTS, tag=''):
    t0 = time.time()
    T = sorted(set(T)); out = {'T': T, 'laws': [LAWS[t] for t in T]}
    G = _G()
    counts = {}
    for n in cfg['census_sizes']:
        found = []
        while len(found) < CAP:
            avoid = [(relabel(F, p), relabel(Gt, p)) for F, Gt in found for p in itertools.permutations(range(n))]
            r = G(T, n).find(nondeg=True, rlimit=cfg['model_rlimit'], avoid=avoid)
            if not isinstance(r, tuple): break
            found.append(r); C.add(f'model-{n}{tag}', n, *r)
        counts[n] = len(found)
    for n in cfg['census_single']:
        r = G(T, n).find(nondeg=True, rlimit=cfg['model_rlimit'])
        if isinstance(r, tuple): C.add(f'model-{n}{tag}', n, *r)
        counts[n] = 1 if isinstance(r, tuple) else 0
    sizes = [n for n, c in counts.items() if c]
    out['model_sizes'] = sizes; out['model_counts'] = counts; out['richness'] = sum(counts.values())
    if not sizes:
        out.update(score=0.0, status='no small non-degenerate model', claims=[], open=[], stage='a',
                   secs_a=round(time.time() - t0, 1))
        return out
    redundant, unconfirmed = [], []
    for t in T:
        rest = [u for u in T if u != t]
        imp = C.implied(rest)
        if imp is not None and not imp[t]: continue
        n, _ = _countermodel(C, G, rest, t, cfg['indep_sizes'], cfg['model_rlimit'], f'indep{tag}')
        if n is None:
            st, _ = prove(rest, t, cfg['redundant_rlimit'])
            (redundant if st == 'proved' else unconfirmed).append(LAWS[t])
    out['redundant'] = redundant; out['independence_unconfirmed'] = unconfirmed
    claims, tried = [], set()
    while len(tried) < cfg['max_tried'] and len([c for c in claims if c['status'] == 'pending']) < cfg['n_cands']:
        fg = fusion_gain(C, T)          # recomputed: every refutation adds a structure to the corpus
        if fg is None: break
        fg = [e for e in sorted(fg, key=lambda e: (ORDER[e], e)) if e not in tried]
        if not fg: break
        e = int(fg[0]); tried.add(e)
        c = {'law': LAWS[e], 'idx': e, 'order': int(ORDER[e])}
        n, unk = _countermodel(C, G, T, e, cfg['claim_sizes'], cfg['model_rlimit'], f'cm{tag}')
        c['status'] = f'false (size {n})' if n else 'pending'
        if unk: c['cm_unknown_sizes'] = unk
        claims.append(c)
    out['claims'] = claims; out['stage'] = 'a'; out['secs_a'] = round(time.time() - t0, 1)
    return out


def score(out):
    claims = out.get('claims', [])
    proved = [c for c in claims if c['status'] == 'proved']
    gain = sum(max(c['difficulty'], 0.1) / (1 + c['order']) for c in proved)
    out['open'] = [c['law'] for c in claims if c['status'] in ('unknown', 'open', 'pending')]
    out['gain'] = round(gain, 4); out['n_proved'] = len(proved)
    out['n_refuted'] = sum(c['status'].startswith('false') for c in claims)
    out['max_difficulty'] = max([c['difficulty'] for c in proved] or [0.0])
    if not out.get('model_sizes'):
        out['score'] = 0.0; return out
    out['score'] = round(gain * math.log2(1 + out['richness']) / math.log2(1 + 3 * CAP + 1)
                         * (0.5 if out.get('redundant') else 1.0), 4)
    out['status'] = 'ok'
    return out


def _e(c, T, limit, cpu):
    """Run E on claim c. Saturation without proof (CounterSatisfiable) refutes the claim in equational
    logic (the countermodel may be infinite). Proof length goes into e_steps (second difficulty measure)."""
    r = prove_e(T, c['idx'], processed_limit=limit, cpu_limit=cpu)
    c['e_status'] = r['status']; c['e_processed'] = r.get('processed')
    if r['status'] == 'proved': c['e_steps'] = r['proof_steps']
    if r['status'] == 'countersatisfiable': c['status'] = 'false (E saturation)'
    return r['status']


def stage_b(C, out, cfg=DEFAULTS):
    t0 = time.time()
    if not out.get('model_sizes'): return out
    T = out['T']
    base = max(1, prove(T, T[0], cfg['base_rlimit'])[1])
    out['base_effort'] = base
    for c in out['claims']:
        if c['status'] != 'pending': continue
        if cfg['use_e'] and _e(c, T, cfg['e_limit'], cfg['e_cpu']) == 'countersatisfiable':
            continue
        st, used = prove(T, c['idx'], cfg['prove_rlimit'])
        if st != 'proved' and c.get('e_status') == 'proved':
            st = 'proved'; c['z3_unproved'] = True       # E's proof stands; z3 effort is then a lower bound
        c['status'] = st; c['effort'] = used
        c['difficulty'] = round(max(0.0, math.log10(used / base)), 3)
    out['stage'] = 'b'; out['secs_b'] = round(time.time() - t0, 1)
    return score(out)


def stage_c(C, out, cfg=DEFAULTS, tag=''):
    """Long runs for claims left open by stage b."""
    t0 = time.time()
    T = out['T']; G = _G(); base = out.get('base_effort', 1)
    budget = (f"countermodels to size {max(cfg['claim_sizes'] + cfg['c_sizes'])} "
              f"(z3 rlimit {cfg['c_model_rlimit']:.0e}), z3 proof rlimit {cfg['c_prove_rlimit']:.0e}")
    for c in out['claims']:
        if c['status'] != 'unknown': continue
        n, unk = _countermodel(C, G, T, c['idx'], cfg['c_sizes'], cfg['c_model_rlimit'], f'cm{tag}')
        if n:
            c['status'] = f'false (size {n})'; continue
        if unk: c['cm_unknown_sizes'] = c.get('cm_unknown_sizes', []) + unk
        if cfg['use_e']:
            st = _e(c, T, cfg['c_e_limit'], cfg['c_e_cpu'])
            if st == 'countersatisfiable': continue
        st, used = prove(T, c['idx'], cfg['c_prove_rlimit'])
        if st != 'proved' and c.get('e_status') == 'proved':      # E proved it, z3 did not: still proved
            c['status'] = 'proved'; c['effort'] = used; c['difficulty'] = round(max(0.0, math.log10(used / base)), 3)
            c['proved_in'] = 'c (E)'; continue
        if st == 'proved':
            c['status'] = 'proved'; c['effort'] = used; c['difficulty'] = round(max(0.0, math.log10(used / base)), 3)
            c['proved_in'] = 'c'
        else:
            c['status'] = 'open'; c['budget'] = budget
    out['stage'] = 'c'; out['secs_c'] = round(time.time() - t0, 1)
    return score(out)


def verify(C, T, cfg=DEFAULTS, tag=''):
    """Stages a and b in one call (calibration, tests)."""
    return stage_b(C, stage_a(C, T, cfg, tag), cfg)
