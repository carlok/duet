"""Review item B1, R2 (PREREGISTRATION.md, "Review items B1, B3, C3, C4"; post hoc, 28 Nov 2026): fragments of classical
structures under a term interpretation, beyond the order-4 law table.

    python -m soup.interp [--entries G,AG,...] [--jobs 4] [--wall 28800]   -> check/interp_r2.json

An entry K is an axiom set in its own signature (constants and unary operations allowed). For every ordered pair (t1,
t2) of binary terms in x, y of K's signature (at most 3 symbols, both variables, up to equality in K), "T is a fragment
of (K; t1, t2)" is tested in two stages:
  1. model filter: Mace4 models of K on sizes 2-6 (up to 200 per size, 120 s per size); t1, t2 become the tables of
     · and ∘, and every law of T must hold in every model (law_vector);
  2. proof: E proves each law of T, with · := t1 and ∘ := t2, from K's axioms (60 s), then Vampire (60 s).
Result per (T, K, t1, t2): 'fragment' (all proved), 'not' (a model fails a law: never reported, the filter drops it) or
'unknown'. Term equality: terms with the same tables on every model are grouped, and a member joins its group's
smallest term only when E proves the equality (10 s); otherwise it stays a class of its own.
Targets: the 318 candidates (check/candidates.json) and T3's 120 random theories (calib_t3.json).
Variables are x, y, z, w, u, v in the entries (LADR's convention); constants and operations never start with u-z.
"""
import argparse
import itertools
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from .paths import data

# signature: symbol -> arity. Sources: TPTP v9 (GRP, RNG, LAT, BOO), Jipsen's Mathematical Structures pages.
ENTRIES = {
    'G': {'sig': {'m': 2, 'i': 1, 'e': 0}, 'source': 'TPTP GRP004-0 (groups, equational)',
          'ax': ['m(m(x,y),z) = m(x,m(y,z))', 'm(e,x) = x', 'm(x,e) = x', 'm(i(x),x) = e', 'm(x,i(x)) = e']},
    'AG': {'sig': {'m': 2, 'i': 1, 'e': 0}, 'source': 'TPTP GRP004-0 plus commutativity',
           'ax': ['m(m(x,y),z) = m(x,m(y,z))', 'm(e,x) = x', 'm(i(x),x) = e', 'm(x,y) = m(y,x)']},
    'R': {'sig': {'a': 2, 'n': 1, 'k': 0, 'm': 2, 'o': 0}, 'source': 'TPTP RNG (rings with 1), Jipsen: rings',
          'ax': ['a(a(x,y),z) = a(x,a(y,z))', 'a(x,y) = a(y,x)', 'a(k,x) = x', 'a(n(x),x) = k',
                 'm(m(x,y),z) = m(x,m(y,z))', 'm(o,x) = x', 'm(x,o) = x',
                 'm(x,a(y,z)) = a(m(x,y),m(x,z))', 'm(a(x,y),z) = a(m(x,z),m(y,z))']},
    'CR': {'sig': {'a': 2, 'n': 1, 'k': 0, 'm': 2, 'o': 0}, 'source': 'rings with 1, commutative',
           'ax': ['a(a(x,y),z) = a(x,a(y,z))', 'a(x,y) = a(y,x)', 'a(k,x) = x', 'a(n(x),x) = k',
                  'm(m(x,y),z) = m(x,m(y,z))', 'm(o,x) = x', 'm(x,y) = m(y,x)', 'm(x,a(y,z)) = a(m(x,y),m(x,z))']},
    'BR': {'sig': {'a': 2, 'n': 1, 'k': 0, 'm': 2, 'o': 0}, 'source': 'Boolean rings (rings with 1, x·x = x)',
           'ax': ['a(a(x,y),z) = a(x,a(y,z))', 'a(x,y) = a(y,x)', 'a(k,x) = x', 'a(n(x),x) = k',
                  'm(m(x,y),z) = m(x,m(y,z))', 'm(o,x) = x', 'm(x,o) = x', 'm(x,x) = x',
                  'm(x,a(y,z)) = a(m(x,y),m(x,z))', 'm(a(x,y),z) = a(m(x,z),m(y,z))']},
    'DL': {'sig': {'j': 2, 'me': 2}, 'source': 'TPTP LAT001-0 (lattices) plus distributivity; Jipsen: distributive lattices',
           'ax': ['j(x,y) = j(y,x)', 'me(x,y) = me(y,x)', 'j(j(x,y),z) = j(x,j(y,z))', 'me(me(x,y),z) = me(x,me(y,z))',
                  'j(x,me(x,y)) = x', 'me(x,j(x,y)) = x', 'me(x,j(y,z)) = j(me(x,y),me(x,z))']},
    'BA': {'sig': {'j': 2, 'me': 2, 'c': 1, 'b': 0, 't': 0}, 'source': 'TPTP BOO (Boolean algebras); Jipsen',
           'ax': ['j(x,y) = j(y,x)', 'me(x,y) = me(y,x)', 'j(j(x,y),z) = j(x,j(y,z))', 'me(me(x,y),z) = me(x,me(y,z))',
                  'j(x,me(x,y)) = x', 'me(x,j(x,y)) = x', 'me(x,j(y,z)) = j(me(x,y),me(x,z))',
                  'j(x,c(x)) = t', 'me(x,c(x)) = b']},
    'HA': {'sig': {'j': 2, 'me': 2, 'h': 2, 'b': 0, 't': 0}, 'source': 'Jipsen: Heyting algebras (equational basis)',
           'ax': ['j(x,y) = j(y,x)', 'me(x,y) = me(y,x)', 'j(j(x,y),z) = j(x,j(y,z))', 'me(me(x,y),z) = me(x,me(y,z))',
                  'j(x,me(x,y)) = x', 'me(x,j(x,y)) = x', 'j(x,b) = x', 'me(x,t) = x',
                  'h(x,x) = t', 'me(x,h(x,y)) = me(x,y)', 'me(y,h(x,y)) = y', 'h(x,me(y,z)) = me(h(x,y),h(x,z))']},
    'Hp': {'sig': {'m': 2, 'h': 2, 't': 0}, 'source': 'Blok and Ferreirim 2000; Jipsen: hoops',
           'ax': ['m(m(x,y),z) = m(x,m(y,z))', 'm(x,y) = m(y,x)', 'm(x,t) = x', 'h(x,x) = t',
                  'm(x,h(x,y)) = m(y,h(y,x))', 'h(m(x,y),z) = h(x,h(y,z))']},
    'Rk': {'sig': {'r': 2, 's': 2}, 'source': 'Fenn and Rourke 1992 (racks); Jipsen: racks',
           'ax': ['r(x,r(y,z)) = r(r(x,y),r(x,z))', 's(x,r(x,y)) = y', 'r(x,s(x,y)) = y']},
    'Qd': {'sig': {'r': 2, 's': 2}, 'source': 'Joyce 1982 (quandles); Jipsen: quandles',
           'ax': ['r(x,r(y,z)) = r(r(x,y),r(x,z))', 's(x,r(x,y)) = y', 'r(x,s(x,y)) = y', 'r(x,x) = x']},
    'Qg': {'sig': {'m': 2, 'l': 2, 'q': 2}, 'source': 'Evans 1949 (equational quasigroups); Jipsen: quasigroups',
           'ax': ['l(x,m(x,y)) = y', 'm(x,l(x,y)) = y', 'q(m(x,y),y) = x', 'm(q(x,y),y) = x']},
}
ORDER = list(ENTRIES)
VARS = 'xyzwuv'

# ---- terms: ('x'|'y') or (symbol, *args)


def show(t):
    return t if isinstance(t, str) else (t[0] if len(t) == 1 else f"{t[0]}({','.join(show(a) for a in t[1:])})")


def size(t): return 0 if isinstance(t, str) else 1 + sum(size(a) for a in t[1:])


def tvars(t): return {t} if isinstance(t, str) else set().union(*[tvars(a) for a in t[1:]]) if len(t) > 1 else set()


def terms(sig, max_size=3):
    by = {0: ['x', 'y']}
    for s in range(1, max_size + 1):
        out = []
        for f, ar in sig.items():
            if ar == 0 and s == 1: out.append((f,))
            if ar == 1: out += [(f, a) for a in by[s - 1]]
            if ar == 2:
                for i in range(s):
                    out += [(f, a, b) for a in by[i] for b in by[s - 1 - i]]
        by[s] = out
    return [t for s in by for t in by[s]]


def evalt(t, M, n):
    """Table of term t (in x, y) on model M ({symbol: table}), as an n x n array."""
    X, Y = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
    def go(u):
        if u == 'x': return X
        if u == 'y': return Y
        f = M[u[0]]
        if len(u) == 1: return np.full((n, n), int(f))
        if len(u) == 2: return f[go(u[1])]
        return f[go(u[1]), go(u[2])]
    return go(t)


# ---- Mace4 in an entry's signature

def models(entry, sizes=range(2, 7), per=200, secs=120):
    E = ENTRIES[entry]
    src = 'formulas(assumptions).\n' + '\n'.join(a + '.' for a in E['ax']) + '\nend_of_list.\n'
    out = []
    for n in sizes:
        r = subprocess.run(['mace4', '-n', str(n), '-N', str(n), '-m', str(per), '-t', str(secs), '-b', '500'],
                           input=src, capture_output=True, text=True, timeout=secs + 60)
        for block in r.stdout.split('interpretation(')[1:]:
            M = {}
            for m in re.finditer(r'function\((\w+)(\(([_,]*)\))?,\s*\[([\d,\s]+)\]\)', block):
                name, ar = m.group(1), (m.group(3).count('_') if m.group(2) else 0)
                v = np.array([int(x) for x in m.group(4).replace(',', ' ').split()], dtype=np.int64)
                M[name] = v[0] if ar == 0 else v if ar == 1 else v.reshape(n, n)
            if set(M) >= set(E['sig']): out.append((n, M))
    return out


# ---- TPTP in an entry's signature

def tptp_term(s):
    """An LADR-style term string with variables x..v -> TPTP with X..V."""
    return re.sub(r'\b([xyzwuv])\b', lambda m: m.group(1).upper(), s)


def fof(eq, name, role):
    L, R = (tptp_term(p.strip()) for p in eq.split('='))
    vs = sorted(set(re.findall(r'\b([XYZWUV])\b', L + ' ' + R)))
    q = f"! [{','.join(vs)}] : " if vs else ''
    return f'fof({name},{role},{q}({L} = {R})).'


def translate(law_tree, t1, t2):
    """A law of the table (tree over f, g and variables 0..5) with f := t1, g := t2, as an equation string."""
    def sub(t, env):
        if isinstance(t, str): return env[t]
        return (t[0],) + tuple(sub(a, env) for a in t[1:]) if len(t) > 1 else t
    def go(u):
        if u[0] == 'v': return VARS[u[1]]
        a, b = go(u[1]), go(u[2])
        return sub(t1 if u[0] == 'f' else t2, {'x': a, 'y': b})
    L, R = law_tree
    return f'{show(go(L))} = {show(go(R))}'


def prove(entry, goal, secs):
    from .provers import prove_e, prove_vampire
    src = '\n'.join(fof(a, f'a{k}', 'axiom') for k, a in enumerate(ENTRIES[entry]['ax'])) + '\n' + fof(goal, 'g', 'conjecture') + '\n'
    if prove_e([], src, processed_limit=1_000_000, cpu_limit=secs)['status'] == 'proved': return True
    return prove_vampire([], src, cpu_limit=secs)['status'] == 'proved'


def classes(entry, Ms, jobs):
    """Term classes up to equality in the entry: model groups, then E (10 s) for each member against its group's smallest."""
    T = [t for t in terms(ENTRIES[entry]['sig']) if tvars(t) == {'x', 'y'}]
    sig = {}
    for t in T:
        key = b''.join(evalt(t, M, n).astype(np.int8).tobytes() for n, M in Ms)
        sig.setdefault(key, []).append(t)
    reps = []
    jobs_ = []
    for grp in sig.values():
        grp.sort(key=lambda t: (size(t), show(t)))
        reps.append(grp[0])
        jobs_ += [(grp[0], u) for u in grp[1:]]
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(lambda p: prove(entry, f'{show(p[0])} = {show(p[1])}', 10), jobs_))
    extra = [u for (r, u), ok in zip(jobs_, res) if not ok]
    # every class must still depend on both variables in the models (a term equal to a projection is not binary)
    def binary(t):
        for n, M in Ms:
            V = evalt(t, M, n)
            if (V != V[:, :1]).any() and (V != V[:1, :]).any(): return True
        return False
    return [t for t in reps + extra if binary(t)], len(T), len(extra)


def _inst(tree, n, cache):
    """Instances of a law on n elements: one index array per variable (cached per law and size)."""
    key = (id(tree), n)
    if key not in cache:
        L, R = tree
        def nv(t): return t[1] + 1 if t[0] == 'v' else max(nv(t[1]), nv(t[2]))
        k = max(nv(L), nv(R))
        cache[key] = [a.ravel() for a in np.meshgrid(*[np.arange(n)] * k, indexing='ij')]
    return cache[key]


def _evb(t, X, F, Gs, B):
    """A tree over f (table F) and g (one table per batch row, Gs: B x n x n) on instances X: shape (N,) or (B, N)."""
    if t[0] == 'v': return X[t[1]]
    a, b = _evb(t[1], X, F, Gs, B), _evb(t[2], X, F, Gs, B)
    if t[0] == 'f': return F[a, b]
    return Gs[np.arange(B)[:, None], a, b]


def holds_batch(tree, F, Gs, n, cache):
    """For each row G of Gs: does the law hold in (F, G)? Same truth as law_vector(F, G, n)[law]."""
    X = _inst(tree, n, cache)
    step = max(1, 2_000_000 // len(X[0]))                   # rows per chunk: about 2M cells per intermediate array
    out = []
    for s in range(0, len(Gs), step):
        g = Gs[s:s + step]; B = len(g)
        eq = _evb(tree[0], X, F, g, B) == _evb(tree[1], X, F, g, B)
        out.append(np.full(B, bool(eq.all())) if eq.ndim == 1 else eq.all(axis=1))
    return np.concatenate(out) if out else np.zeros(0, dtype=bool)


def filter_pairs(C, Ms, targets, deadline):
    """Ordered pairs (t1, t2) of distinct classes with every law of a target true in every model: (target, t1, t2).
    For each t1, all t2 are tested at once, law by law, and only the target laws are evaluated (the first version called
    law_vector, all 71,369 laws, once per pair and model; same survivors, checked on G and AG)."""
    from .data import TREES
    tabs = [(n, np.stack([np.asarray(evalt(t, M, n), dtype=np.int64) for t in C])) for n, M in Ms]
    cache, surv, done = {}, [], 0
    for i1 in range(len(C)):
        if time.time() > deadline: break
        alive = {}
        for i in range(len(targets)):
            a = np.ones(len(C), dtype=bool); a[i1] = False
            alive[i] = a
        for n, TB in tabs:
            F = TB[i1]
            for i in list(alive):
                a = alive[i]
                for t in targets[i]['T']:
                    idx = np.flatnonzero(a)
                    if not len(idx): break
                    a[idx] = holds_batch(TREES[t], F, TB[idx], n, cache)
                if not a.any(): del alive[i]
            if not alive: break
        for i, a in alive.items():
            surv += [(i, C[i1], C[j]) for j in np.flatnonzero(a)]
        done += 1
    return surv, done


def run_entry(entry, targets, jobs, deadline):
    from .data import TREES
    t0 = time.time()
    Ms = models(entry)
    t_models = time.time() - t0
    C, n_terms, unproved = classes(entry, Ms, jobs)
    t_classes = time.time() - t0 - t_models
    print(f'  {entry}: {len(Ms)} models ({round(t_models)} s), {len(C)} classes ({round(t_classes)} s)', flush=True)
    pairs = len(C) * (len(C) - 1)
    surv, t1_done = filter_pairs(C, Ms, targets, deadline)
    t_filter = time.time() - t0 - t_models - t_classes
    print(f'  {entry}: filter {t1_done}/{len(C)} first terms, {len(surv)} survivors ({round(t_filter)} s)', flush=True)
    res = []
    def job(s):
        i, t1, t2 = s
        ok = all(prove(entry, translate(TREES[t], t1, t2), 60) for t in targets[i]['T'])
        return {'key': targets[i]['key'], 'entry': entry, 't1': show(t1), 't2': show(t2),
                'result': 'fragment' if ok else 'unknown'}
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(job, surv))
    return {'entry': entry, 'models': len(Ms), 'sizes': sorted({n for n, _ in Ms}), 'terms': n_terms,
            'classes': len(C), 'unproved_equal': unproved, 'pairs': pairs, 'filter_survivors': len(surv),
            'filter_first_terms_done': t1_done, 'filter_complete': t1_done == len(C),
            'secs_models': round(t_models), 'secs_classes': round(t_classes), 'secs_filter': round(t_filter),
            'results': res, 'secs': round(time.time() - t0)}


def targets():
    cands = json.load(open(data('check', 'candidates.json')))
    cal = json.load(open(data('calib_t3.json')))
    out = [{'key': c['key'], 'set': 'candidate', 'T': sorted(c['T'])} for c in cands]
    out += [{'key': f'random:{i}', 'set': 'random', 'T': sorted(c['T'])} for i, c in enumerate(cal) if c.get('kind') == 'null']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--entries', default=','.join(ORDER))
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--wall', type=int, default=28_800)
    ap.add_argument('--out', default='interp_r2.json', help='file name under check/')
    a = ap.parse_args()
    deadline = time.time() + a.wall
    tg = targets()
    path = data('check', a.out)
    out = json.load(open(path)) if path.exists() else {'entries': {}}
    for e in a.entries.split(','):
        if e in out['entries']: continue
        if time.time() > deadline: print(f'{e}: wall time reached, not run', flush=True); break
        r = run_entry(e, tg, a.jobs, deadline)
        out['entries'][e] = r
        json.dump(out, open(path, 'w'), indent=1)
        fr = [x for x in r['results'] if x['result'] == 'fragment']
        print(f"{e}: {r['models']} models on sizes {r['sizes']}, {r['classes']} term classes ({r['terms']} terms), "
              f"{r['pairs']} pairs, {r['filter_survivors']} survive the filter, {len(fr)} fragments proved, "
              f"{r['secs']} s", flush=True)
        for x in fr: print(f"   {x['key'][:12]}: · = {x['t1']}, ∘ = {x['t2']}", flush=True)


if __name__ == '__main__':
    main()
