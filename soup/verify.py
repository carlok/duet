"""Verification of a theory, in stages (T1).

  stage a  model census (non-isomorphic non-degenerate models, <= 8 per size on 2-4, one on 5),
           independence of each law (countermodel to size 6, else a bounded proof),
           emergent-law claims (fusion gain on the corpus) checked by countermodel search to size 6.
           Seconds.
  stage b  E first (20k processed clauses): saturation refutes the claim, a proof gives e_steps; then a
           bounded z3 proof; z3 effort -> difficulty (kept for comparability); score.
  stage c  only for claims still open after b: E with 2M processed clauses, Mace4 up to 10 elements, from
           the smallest size stage a left unsearched, else from 7 (wall-time budget, sizes reached recorded),
           then a long z3 run. With certify_e every E saturation gets a soup.confluence certificate. Each claim ends as proved, false (size k) or open with the budget stated.

Every model found goes into the corpus immediately (and so into the shared store, when there is one).
"""
import itertools
import math
import time

import numpy as np

from .core import Corpus, Grounding, prove, LAWS, ORDER, NL, TREES
from .provers import prove_e, mace4
from .confluence import check

CAP = 8
BRIDGE = np.array(['·' in s and '∘' in s for s in LAWS])

# V1: the verifier as of 21 Nov 2026 morning (the streaming runs test10/fix5/e10 and the T3 calibration).
# Frozen: T3 is preregistered against it, so later changes to DEFAULTS must not reach it.
V1 = dict(
    census_sizes=(2, 3, 4), census_single=(5,), model_rlimit=10_000_000,
    indep_sizes=(2, 3, 4, 5, 6), redundant_rlimit=10_000_000,
    claim_sizes=(2, 3, 4, 5, 6), n_cands=3, max_tried=9,
    prove_rlimit=30_000_000, base_rlimit=5_000_000,
    c_sizes=(7, 10), c_mace4_secs=300, c_model_rlimit=50_000_000, c_prove_rlimit=300_000_000,
    e_limit=20_000, e_cpu=20, c_e_limit=2_000_000, c_e_cpu=300, use_e=True,
    certify_e=False,
)
# Current verifier: V1 plus a convergence certificate for every E saturation in stages b and c.
DEFAULTS = dict(V1, certify_e=True)
# V2 (for T4, preregistered): difficulty from E proof steps instead of z3 effort; stage a takes one claim per
# order level (up to 4 pending, 12 tried) instead of the 3 lowest-order claims.
V2 = dict(DEFAULTS, difficulty='e_steps', claims_per_order=True, n_cands=4, max_tried=12)
# V3 (exploratory run X1, after T4): V2 plus Vampire finite model building. In stage b, for every pending claim
# that E's small run neither proves nor saturates (fmb_secs); in stage c, before Mace4 (c_fmb_secs). A model
# counts only after check_offline.check_finite accepts it. On S10, Mace4 stalled at size 7 for two hours where
# Vampire's FMB found a 10-element model in under two minutes (21 Nov 2026).
V3 = dict(V2, fmb_secs=60, c_fmb_secs=600)
CONFIGS = {'V1': V1, 'DEFAULTS': DEFAULTS, 'V2': V2, 'V3': V3}      # the stream verifier picks one by SOUP_VERIFIER
# The first-session verifier (countermodels only to size 4/5): kept to reproduce results-cloud/.
LEGACY = dict(V1, indep_sizes=(2, 3, 4, 5), claim_sizes=(2, 3, 4), use_e=False)


def c_size_range(c, cfg):
    """Sizes for the stage-c Mace4 search: from the smallest size stage a left unsearched (z3 ran out of
    budget there), else from cfg['c_sizes'][0]. Until 21 Nov 2026 stage c always started at 7, so sizes 5-6
    that stage a could not finish were never searched again."""
    lo, hi = cfg['c_sizes']
    return min(list(c.get('cm_unknown_sizes') or []) + [lo]), hi


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
        if cfg.get('claims_per_order'):    # V2: at most one pending claim per order level
            busy = {c['order'] for c in claims if c['status'] == 'pending'}
            fg = [e for e in fg if int(ORDER[e]) not in busy]
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


def _e(c, T, limit, cpu, certify=False):
    """Run E on claim c. Saturation without proof (CounterSatisfiable) refutes the claim in equational
    logic (the countermodel may be infinite). Proof length goes into e_steps (second difficulty measure).
    With certify, a saturation is re-checked by soup.confluence (convergent rewrite system, independent of
    E's correctness); the claim counts as refuted either way, the status says whether it is certified."""
    r = prove_e(T, c['idx'], processed_limit=limit, cpu_limit=cpu)
    c['e_status'] = r['status']; c['e_processed'] = r.get('processed')
    if r['status'] == 'proved': c['e_steps'] = r['proof_steps']
    if r['status'] == 'countersatisfiable':
        c['status'] = 'false (E saturation)'
        if certify:
            cert = check(T, c['idx'])
            c['certificate'] = bool(cert.get('ok'))
            if not cert.get('ok'):
                c['certificate_why'] = cert.get('why'); c['status'] = 'false (E saturation, uncertified)'
    return r['status']


def _fmb(C, c, T, secs, start):
    """V3: Vampire finite model building on claim c. True if a model passes our own check (claim refuted)."""
    from .check_offline import check_finite
    from .sweep_fmb import fmb
    t0 = time.time()
    st, m, _ = fmb(T, c['idx'], secs, start)
    c['fmb'] = {'status': st, 'secs': round(time.time() - t0, 1), 'start': start}
    if not (m and m['g'] is not None): return False
    chk = check_finite(T, [c['idx']], m['f'], m['g'])
    if not (chk['ok'] and chk['law_vector_agrees']):
        c['fmb']['status'] = 'model rejected by our check'; return False
    C.add(f"cm-fmb-{m['n']}", m['n'], np.array(m['f']), np.array(m['g']))
    c['status'] = f"false (size {m['n']}, Vampire FMB)"; c['fmb']['n'] = m['n']
    return True


def stage_b(C, out, cfg=DEFAULTS):
    t0 = time.time()
    if not out.get('model_sizes'): return out
    T = out['T']
    base = max(1, prove(T, T[0], cfg['base_rlimit'])[1])
    out['base_effort'] = base
    for c in out['claims']:
        if c['status'] != 'pending': continue
        if cfg['use_e'] and _e(c, T, cfg['e_limit'], cfg['e_cpu'], cfg.get('certify_e')) == 'countersatisfiable':
            continue
        if cfg.get('fmb_secs') and c.get('e_status') != 'proved' and \
                _fmb(C, c, T, cfg['fmb_secs'], min(list(c.get('cm_unknown_sizes') or []) + [7])):
            continue
        st, used = prove(T, c['idx'], cfg['prove_rlimit'])
        if st != 'proved' and c.get('e_status') == 'proved':
            st = 'proved'; c['z3_unproved'] = True       # E's proof stands; z3 effort is then a lower bound
        c['status'] = st; c['effort'] = used
        c['difficulty_z3'] = round(max(0.0, math.log10(used / base)), 3)
        if st == 'proved' and cfg.get('use_e') and c.get('e_status') != 'proved' and cfg.get('difficulty') == 'e_steps':
            _e(c, T, cfg['c_e_limit'], cfg['c_e_cpu'])   # z3 proved it, E (small budget) did not: E again, long budget
        set_difficulty(c, cfg)
    out['stage'] = 'b'; out['secs_b'] = round(time.time() - t0, 1)
    return score(out)


def set_difficulty(c, cfg):
    """V1: log10(z3 effort / effort of a trivial proof), capped by the z3 budget, so a claim that only E
    proved got the cap (the leaderboard artifact of 21 Nov 2026). V2 ('e_steps'): E proof steps / 10 (E 3.2.5
    --auto: absorption 9 steps -> 0.9); a claim E did not prove gets 0.1 and the flag no_e_proof."""
    if cfg.get('difficulty') == 'e_steps':
        if c.get('e_steps'): c['difficulty'] = round(c['e_steps'] / 10, 3)
        else: c['difficulty'] = 0.1; c['no_e_proof'] = True
    else:
        c['difficulty'] = c['difficulty_z3']


def stage_c(C, out, cfg=DEFAULTS, tag=''):
    """Long runs for claims left open by stage b."""
    t0 = time.time()
    T = out['T']; G = _G(); base = out.get('base_effort', 1)
    for c in out['claims']:
        if c['status'] != 'unknown': continue
        if cfg['use_e'] and _e(c, T, cfg['c_e_limit'], cfg['c_e_cpu'], cfg.get('certify_e')) == 'countersatisfiable':
            continue                    # E first: a saturation settles it in seconds
        lo, hi = c_size_range(c, cfg)
        budget = (f"E {cfg['c_e_limit']:.0e} processed clauses, Mace4 sizes {lo}-{hi} "
                  f"({cfg['c_mace4_secs']} s), z3 proof rlimit {cfg['c_prove_rlimit']:.0e}")
        if c.get('e_status') != 'proved' and cfg.get('c_fmb_secs') and _fmb(C, c, T, cfg['c_fmb_secs'], lo):
            continue                    # V3: Vampire FMB before Mace4
        if c.get('e_status') != 'proved':      # a claim E proved has no countermodel: skip the model search
            m = mace4(T, c['idx'], lo, hi, cfg['c_mace4_secs'])          # Mace4 replaces z3 grounding beyond size 6
            c['mace4_sizes'] = [lo, hi]
            if m['size']:
                F, Gt = (np.array(x) for x in m['tables']); C.add(f'cm-mace4-{m["size"]}{tag}', m['size'], F, Gt)
                c['status'] = f"false (size {m['size']})"; continue
            c['mace4_searched_to'] = m['searched_to']
        st, used = prove(T, c['idx'], cfg['c_prove_rlimit'])
        if st == 'proved' or c.get('e_status') == 'proved':        # E's proof stands even if z3 gives up
            c['status'] = 'proved'; c['effort'] = used
            c['difficulty_z3'] = round(max(0.0, math.log10(used / base)), 3)
            if st != 'proved': c['z3_unproved'] = True
            c['proved_in'] = 'c' if st == 'proved' else 'c (E)'
            set_difficulty(c, cfg)
        else:
            c['status'] = 'open'; c['budget'] = budget
    out['stage'] = 'c'; out['secs_c'] = round(time.time() - t0, 1)
    return score(out)


def verify(C, T, cfg=DEFAULTS, tag=''):
    """Stages a and b in one call (calibration, tests)."""
    return stage_b(C, stage_a(C, T, cfg, tag), cfg)
