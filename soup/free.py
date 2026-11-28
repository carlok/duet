"""Review item B3 (PREREGISTRATION.md, "Review items B1, B3, C3, C4"; post hoc, 28 Nov 2026): how free is one operation
once the other is fixed?

    python -m soup.free --set calib|n2 [--jobs 3]     -> check/free_<set>.json

For a theory T and a direction (∘ given ·, or · given ∘) and a fixed table F of the given operation, the tables G of the
other with (F, G) |= T are counted by a backtracking search over G's cells: every law instance is checked as soon as
the cells it reads are assigned (partial evaluation, -1 = unassigned). k(F) is capped at CAP.
  H   = mean over F with k(F) > 0 of log k(F) / (n^2 log n)          (choice entropy, 0 = determined)
  rho = mean over F of k(F) / prod |S_xy|, S_xy the values cell xy takes in F's models (1 = a product over cells);
        for a capped F, the share of models among 200 seeded draws from the product, flagged.
Reducts: n = 3, every table F satisfying T's laws in the given operation alone, with k(F) > 0 (exhaustive);
n = 4, 200 distinct tables drawn with seed 0 from Mace4's models of T (up to 20,000).
Certificate: T proves s·(x∘y) = s·t(x,y) or (x∘y)·s = t(x,y)·s for a ·-term t of at most 2 symbols (and the same with
the operations swapped): filtered on the n = 3 models, then E 30 s per survivor.
Wall time WALL s per theory and direction; a theory past it is reported incomplete.
"""
import argparse
import itertools
import json
import math
import random
import time

import numpy as np

from .paths import data

CAP = 100_000
WALL = 600


class Stop(Exception):
    pass


def swap_ops(t):
    if t[0] == 'v': return t
    return ({'f': 'g', 'g': 'f'}[t[0]], swap_ops(t[1]), swap_ops(t[2]))


def has(t, op): return t[0] != 'v' and (t[0] == op or has(t[1], op) or has(t[2], op))


def nvars(t): return t[1] + 1 if t[0] == 'v' else max(nvars(t[1]), nvars(t[2]))


def instances(L, R, n):
    k = max(nvars(L), nvars(R))
    return [a.ravel() for a in np.meshgrid(*[np.arange(n)] * k, indexing='ij')]


def ev(t, X, F, G):
    """Partial evaluation: -1 where an unassigned cell of G is read."""
    if t[0] == 'v': return X[t[1]]
    a, b = ev(t[1], X, F, G), ev(t[2], X, F, G)
    tab = F if t[0] == 'f' else G
    ok = (a >= 0) & (b >= 0)
    out = np.full(a.shape, -1, dtype=np.int64)
    out[ok] = tab[a[ok], b[ok]]
    return out


def holds_all(laws, F, G):
    for L, R, X in laws:
        if not np.array_equal(ev(L, X, F, G), ev(R, X, F, G)): return False
    return True


def count(laws, F, n, deadline):
    """(k, value sets per cell, capped) for the G with (F, G) |= laws; laws: [(L, R, X)] with the unknown op as 'g'."""
    G = np.full((n, n), -1, dtype=np.int64)
    cells = [(i, j) for i in range(n) for j in range(n)]
    seen = [set() for _ in cells]
    k = [0]
    def ok():
        for L, R, X in laws:
            a, b = ev(L, X, F, G), ev(R, X, F, G)
            if ((a >= 0) & (b >= 0) & (a != b)).any(): return False
        return True
    def rec(c):
        if k[0] >= CAP: raise Stop('cap')
        if time.time() > deadline: raise Stop('wall')
        if c == len(cells):
            k[0] += 1
            for m, (i, j) in enumerate(cells): seen[m].add(int(G[i, j]))
            return
        i, j = cells[c]
        for v in range(n):
            G[i, j] = v
            if ok(): rec(c + 1)
        G[i, j] = -1
    try:
        rec(0); stop = None
    except Stop as e:
        stop = str(e)
    return k[0], seen, stop


def rho_sampled(laws, F, seen, n, rng, draws=200):
    hits = 0
    for _ in range(draws):
        G = np.array([rng.choice(sorted(s)) for s in seen], dtype=np.int64).reshape(n, n)
        hits += holds_all(laws, F, G)
    return hits / draws


def measure(T, direction, n, reducts, deadline):
    """Measures for one theory, one direction, one size. reducts: list of F tables, or None for exhaustive."""
    from .data import TREES
    trees = [TREES[t] for t in T]
    if direction == 'dot_given_circ': trees = [(swap_ops(L), swap_ops(R)) for L, R in trees]
    known = [(L, R, instances(L, R, n)) for L, R in trees if not has(L, 'g') and not has(R, 'g')]
    laws = [(L, R, instances(L, R, n)) for L, R in trees if has(L, 'g') or has(R, 'g')]
    empty = np.full((n, n), -1, dtype=np.int64)
    if reducts is None:
        reducts = (np.array(v, dtype=np.int64).reshape(n, n) for v in itertools.product(range(n), repeat=n * n))
    rng = random.Random(0)
    Hs, rhos, flags, nF, total = [], [], {'cap': 0, 'wall': 0}, 0, 0
    for F in reducts:
        if time.time() > deadline: flags['wall'] += 1; break
        if known and not holds_all(known, F, empty): continue
        k, seen, stop = count(laws, F, n, deadline)
        if stop == 'wall': flags['wall'] += 1; break
        if k == 0: continue
        nF += 1; total += k
        Hs.append(math.log(k) / (n * n * math.log(n)))
        if stop == 'cap':
            flags['cap'] += 1; rhos.append(rho_sampled(laws, F, seen, n, rng))
        else:
            rhos.append(k / math.prod(len(s) for s in seen))
    return {'n': n, 'reducts_with_models': nF, 'models': total, 'H': float(np.mean(Hs)) if Hs else None,
            'rho': float(np.mean(rhos)) if rhos else None, 'capped': flags['cap'], 'incomplete': flags['wall'] > 0}


def reducts4(T, direction, cap=20_000, k=200):
    from .profile import all_models
    ms, complete, err = all_models(T, 4, cap, 120)
    tabs = {}
    for _, F, G in ms:
        X = np.asarray(F if direction == 'circ_given_dot' else G, dtype=np.int64)
        tabs.setdefault(X.tobytes(), X)
    keys = sorted(tabs)
    random.Random(0).shuffle(keys)
    return [tabs[x] for x in keys[:k]], len(tabs), complete


def small_terms(op):
    """Terms in x, y of op with at most 2 symbols."""
    V = [('v', 0), ('v', 1)]
    one = [(op, a, b) for a in V for b in V]
    two = [(op, a, b) for a in one for b in V] + [(op, a, b) for a in V for b in one]
    return V + one + two


def certificate(T, models):
    """Laws s·(x∘y) = s·t, (x∘y)·s = t·s (t a ·-term, <= 2 symbols), and the same with the operations swapped, that
    hold in every given model of T and that E proves (30 s). models: [(F, G)]. Variables: x, y, and s = 2."""
    from .provers import prove_e, fof
    from .data import TREES
    s = ('v', 2)
    out = []
    for op, other in (('f', 'g'), ('g', 'f')):
        xy = (other, ('v', 0), ('v', 1))
        for t in small_terms(op):
            for L, R in (((op, s, xy), (op, s, t)), ((op, xy, s), (op, t, s))):
                if any(not np.array_equal(ev(L, X, F, G), ev(R, X, F, G))
                       for F, G in models for X in [instances(L, R, len(F))]):
                    continue
                from .data import tptp
                vs = sorted({c for c in tptp(L) + tptp(R) if c in 'XYZWUV'})
                goal = f"fof(goal,conjecture,! [{','.join(vs)}] : ({tptp(L)} = {tptp(R)}))."
                src = '\n'.join([fof(u, f'a{k}', 'axiom') for k, u in enumerate(T)] + [goal]) + '\n'
                if prove_e(sorted(T), src, processed_limit=500_000, cpu_limit=30)['status'] == 'proved':
                    out.append(f'{tptp(L)} = {tptp(R)}')
    return out


def theory(item, parts='all'):
    """parts: 'all', 'counts' (no prover) or 'certificate' (E only), so the prover part can wait for free slots."""
    from .profile import all_models
    name, T = item
    out = {'name': name, 'T': T}
    if parts in ('all', 'certificate'):
        ms = all_models(T, 3, 20_000, 120)[0] + all_models(T, 2, 1000, 60)[0]
        out['certificate'] = certificate(T, [(np.asarray(F, dtype=np.int64), np.asarray(G, dtype=np.int64))
                                             for _, F, G in ms])
    if parts == 'certificate': return out
    for d in ('circ_given_dot', 'dot_given_circ'):
        deadline = time.time() + WALL
        r3 = measure(T, d, 3, None, deadline)
        R4, n4, complete = reducts4(T, d)
        r4 = measure(T, d, 4, R4, deadline)
        r4.update(reduct_tables_seen=n4, mace4_complete=complete)
        out[d] = {'n3': r3, 'n4': r4, 'incomplete': r3['incomplete'] or r4['incomplete']}
    return out


def calib_set():
    from .catalogue import KNOWN, laws_of
    cal = json.load(open(data('calib_t3.json')))
    items = [(f'catalogue:{name}', laws_of(name)) for name in KNOWN]
    items += [(f"random:{i}", sorted(c['T'])) for i, c in enumerate(cal) if c.get('kind') == 'null']
    return items


def n2_set():
    rk = json.load(open(data('check', 'novelty2_ranking.json')))['ranked']
    L7 = [r for r in rk if r['offdiag_laws'] and not r['classical_models'] and not r['related']]
    return [(f"n2:{r['key']}", sorted(r['T'])) for r in L7]


def main():
    from concurrent.futures import ProcessPoolExecutor, as_completed
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True, choices=['calib', 'n2'])
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--parts', default='all', choices=['all', 'counts', 'certificate'])
    a = ap.parse_args()
    items = calib_set() if a.set == 'calib' else n2_set()
    path = data('check', f'free_{a.set}.json')
    done = {r['name']: r for r in (json.load(open(path)) if path.exists() else [])}
    need = {'all': ('certificate', 'circ_given_dot'), 'counts': ('circ_given_dot',), 'certificate': ('certificate',)}
    todo = [it for it in items if not all(k in done.get(it[0], {}) for k in need[a.parts])]
    print(f'{len(items)} theories, {len(todo)} to do ({a.parts})', flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(theory, it, a.parts): it[0] for it in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: r = f.result()
            except Exception as e: r = {'name': futs[f], 'error': f'{type(e).__name__}: {e}'}
            done[r['name']] = dict(done.get(r['name'], {}), **r)
            json.dump(list(done.values()), open(path, 'w'), indent=1)
            print(f'  {i}/{len(todo)} {r["name"]} ({round(time.time() - t0)} s)', flush=True)


if __name__ == '__main__':
    main()
