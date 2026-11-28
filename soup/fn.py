"""Review item C3 (PREREGISTRATION.md, "Review items B1, B3, C3, C4"; post hoc, 28 Nov 2026): a false-novelty rate.

    python -m soup.fn generate [--jobs 4]      -> check/fn_fragments.json (fragments of known structures)
    python -m soup.fn setup --dir fn-test      -> a run directory whose queue holds the fragments (then a verifier run)

Known two-operation structures outside R1 and R2 (fixed in the preregistration), each with its (·, ∘) terms. A
fragment is a seeded random set of 2-4 laws of the table that hold in the structure's Mace4 models (sizes 2-6, 200 per
size) under the terms, with at least one bridge, under a random relabelling (one of the 8), and that passes the search's
own cheap test: an off-diagonal emergent law on the union corpus (offdiag_gain). Its laws must then be E-proved from the
structure's axioms (60 s each). Draws stop at 10 kept fragments, or 5,000 draws. Duplicates under theory_key are dropped.
"""
import argparse
import json
import random
import time

import numpy as np

from .paths import data

STRUCTURES = {
    'moufang': {'sig': {'m': 2, 'l': 2, 'q': 2, 'e': 0}, 'terms': (('m', 'x', 'y'), ('l', 'x', 'y')),
                'source': 'Bruck 1958; Jipsen: Moufang loops',
                'ax': ['m(e,x) = x', 'm(x,e) = x', 'l(x,m(x,y)) = y', 'm(x,l(x,y)) = y', 'q(m(x,y),y) = x',
                       'm(q(x,y),y) = x', 'm(m(m(x,y),x),z) = m(x,m(y,m(x,z)))']},
    'bol': {'sig': {'m': 2, 'l': 2, 'q': 2, 'e': 0}, 'terms': (('m', 'x', 'y'), ('l', 'x', 'y')),
            'source': 'Robinson 1966 (left Bol loops); Jipsen: Bol loops',
            'ax': ['m(e,x) = x', 'm(x,e) = x', 'l(x,m(x,y)) = y', 'm(x,l(x,y)) = y', 'q(m(x,y),y) = x',
                   'm(q(x,y),y) = x', 'm(x,m(y,m(x,z))) = m(m(x,m(y,x)),z)']},
    'cml': {'sig': {'m': 2, 'l': 2, 'q': 2, 'e': 0}, 'terms': (('m', 'x', 'y'), ('l', 'x', 'y')),
            'source': 'Bruck 1958 (commutative Moufang loops)',
            'ax': ['m(e,x) = x', 'l(x,m(x,y)) = y', 'm(x,l(x,y)) = y', 'q(m(x,y),y) = x', 'm(q(x,y),y) = x',
                   'm(x,y) = m(y,x)', 'm(m(m(x,y),x),z) = m(x,m(y,m(x,z)))']},
    'commutator': {'sig': {'m': 2, 'i': 1, 'e': 0},
                   'terms': (('m', 'x', 'y'), ('m', ('m', ('i', 'x'), ('i', 'y')), ('m', 'x', 'y'))),
                   'source': 'groups (TPTP GRP004-0) with the commutator x⁻¹y⁻¹xy',
                   'ax': ['m(m(x,y),z) = m(x,m(y,z))', 'm(e,x) = x', 'm(x,e) = x', 'm(i(x),x) = e', 'm(x,i(x)) = e']},
    'cycleset': {'sig': {'r': 2, 's': 2}, 'terms': (('r', 'x', 'y'), ('s', 'x', 'y')),
                 'source': 'Rump 2005 (cycle sets), with the inverse translation',
                 'ax': ['r(r(x,y),r(x,z)) = r(r(y,x),r(y,z))', 's(x,r(x,y)) = y', 'r(x,s(x,y)) = y']},
    'lie': {'sig': {'a': 2, 'n': 1, 'k': 0, 'b': 2}, 'terms': (('a', 'x', 'y'), ('b', 'x', 'y')),
            'source': 'Lie rings (abelian group, bilinear alternating bracket, Jacobi)',
            'ax': ['a(a(x,y),z) = a(x,a(y,z))', 'a(x,y) = a(y,x)', 'a(k,x) = x', 'a(n(x),x) = k',
                   'b(a(x,y),z) = a(b(x,z),b(y,z))', 'b(x,a(y,z)) = a(b(x,y),b(x,z))', 'b(x,x) = k',
                   'a(a(b(x,b(y,z)),b(y,b(z,x))),b(z,b(x,y))) = k']},
    'isemiring': {'sig': {'a': 2, 'm': 2}, 'terms': (('a', 'x', 'y'), ('m', 'x', 'y')),
                  'source': 'idempotent semirings without constants (Jipsen: idempotent semirings)',
                  'ax': ['a(a(x,y),z) = a(x,a(y,z))', 'a(x,y) = a(y,x)', 'a(x,x) = x', 'm(m(x,y),z) = m(x,m(y,z))',
                         'm(x,a(y,z)) = a(m(x,y),m(x,z))', 'm(a(x,y),z) = a(m(x,z),m(y,z))']},
}


def _prove(name, goal, secs):
    from .interp import fof
    from .provers import prove_e, prove_vampire
    S = STRUCTURES[name]
    src = '\n'.join(fof(a, f'a{k}', 'axiom') for k, a in enumerate(S['ax'])) + '\n' + fof(goal, 'g', 'conjecture') + '\n'
    if prove_e([], src, processed_limit=1_000_000, cpu_limit=secs)['status'] == 'proved': return True
    return prove_vampire([], src, cpu_limit=secs)['status'] == 'proved'


def true_on_models(name):
    """Laws of the table true in every Mace4 model of the structure under its terms (bool vector), and the model count."""
    from .core import law_vector
    from .interp import ENTRIES, evalt, models
    S = STRUCTURES[name]
    ENTRIES[f'fn:{name}'] = {'sig': S['sig'], 'ax': S['ax'], 'source': S['source']}      # models() reads ENTRIES
    Ms = models(f'fn:{name}')
    acc = None
    t1, t2 = S['terms']
    for n, M in Ms:
        v = law_vector(evalt(t1, M, n), evalt(t2, M, n), n)
        acc = v if acc is None else acc & v
    return acc, len(Ms), sorted({n for n, _ in Ms})


def generate(name, C, seed, keep=10, max_draws=5000):
    from .data import TREES
    from .duality import theory_key
    from .interp import translate
    from .offdiag import offdiag_gain
    from .relabel import relabellings, relabel_law
    from .verify import BRIDGE
    acc, n_models, sizes = true_on_models(name)
    if acc is None: return {'structure': name, 'models': 0, 'fragments': []}
    true = np.flatnonzero(acc); bridges = [int(t) for t in true if BRIDGE[t]]
    nonb = [int(t) for t in true if not BRIDGE[t]]
    rng = random.Random(seed); rels = list(relabellings())
    S = STRUCTURES[name]; proved = {}
    kept, keys, draws, cheap_pass = [], set(), 0, 0
    while len(kept) < keep and draws < max_draws and bridges:
        draws += 1
        k = rng.randint(2, 4)
        T = {rng.choice(bridges)} | set(rng.sample(true.tolist(), k - 1))
        T = sorted(int(t) for t in T)
        if len(T) < 2: continue
        rname, r = rng.choice(rels)
        RT = [relabel_law(t, r) for t in T]
        if None in RT: continue
        RT = sorted(set(RT))
        key = theory_key(RT)
        if key in keys: continue
        g = offdiag_gain(C, RT)
        if g is None or not len(g): continue
        cheap_pass += 1
        ok = True
        for t in T:                       # truth in the structure is checked on the unrelabelled laws
            if t not in proved: proved[t] = _prove(name, translate(TREES[t], *S['terms']), 60)
            if not proved[t]: ok = False; break
        if not ok: continue
        keys.add(key)
        kept.append({'key': key, 'T': RT, 'structure': name, 'relabel': rname, 'unrelabelled': T})
    return {'structure': name, 'models': n_models, 'sizes': sizes, 'true_on_models': int(len(true)),
            'bridges': len(bridges), 'draws': draws, 'cheap_pass': cheap_pass, 'fragments': kept}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['generate', 'setup'])
    ap.add_argument('--dir', default='fn-test')
    a = ap.parse_args()
    if a.cmd == 'generate':
        from .dedupe import union_corpus
        C = union_corpus()
        out = []
        for i, name in enumerate(STRUCTURES):
            t0 = time.time()
            r = generate(name, C, seed=2601 + i)
            r['secs'] = round(time.time() - t0)
            out.append(r)
            json.dump(out, open(data('check', 'fn_fragments.json'), 'w'), indent=1)
            print(f"{name}: {r['models']} models, {r.get('true_on_models')} laws true on them ({r.get('bridges')} bridges), "
                  f"{r.get('draws')} draws, {r.get('cheap_pass')} pass the cheap test, {len(r['fragments'])} kept "
                  f"({r['secs']} s)", flush=True)
        return
    # setup: push every kept fragment to a fresh run directory's queue (priority 1: all are verified)
    from .data import LAWS
    from .duality import canonical
    from .stream.fqueue import FileQueue
    frs = [f for r in json.load(open(data('check', 'fn_fragments.json'))) for f in r['fragments']]
    Q = FileQueue(data(a.dir, 'queue'))
    for f in frs:
        Q.mark_seen(f['key'])
        Q.push(f['key'], {'T': list(canonical(f['T'])), 'cheap': 1.0, 'desc': [], 'novelty': 0.0, 'arm': 'fn', 'run': 'fn',
                          'searcher': 'fn', 't_pushed': time.time(), 'structure': f['structure'],
                          'laws': [LAWS[t] for t in f['T']]}, 1.0)
    print(f'{len(frs)} fragments pushed to {a.dir}/queue')


if __name__ == '__main__':
    main()
