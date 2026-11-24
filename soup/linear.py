"""Linear and affine two-operation models over finite rings: a countermodel family for open claims (24 Nov 2026).

The idea is parsimagma's (https://github.com/carlok/parsimagma, same author). Its structured algebraic sweep found
finite counterexamples on 9 to 32 elements that Vampire's finite model builder, Mace4 and grounded z3 all missed. It
did so by solving identities in a few coefficients instead of searching Cayley tables. The code here is new.

Family. Take a finite commutative ring R with q elements (Z/n, or a finite field GF(p^k)), use R itself as the
carrier, and set
    x · y = a x + b y + c,        x ∘ y = d x + e y + f,        a, ..., f in R
(the linear family has c = f = 0). A term evaluates to an affine form k_1 v_1 + ... + k_m v_m + k_0 with coefficients
in R. Two affine forms agree on every assignment iff their coefficients agree: put one variable to 1 and the others
to 0, then all to 0. So whether a law holds is decided exactly from the coefficients, without enumerating R^m. The
search enumerates the coefficients, q^4 tuples (linear) or q^6 (affine), vectorised with numpy.

soup.families.cyclic covers translation-invariant models (x · y = x + F(y - x)). Among linear models it contains
only those with a + b = 1, so this family adds new models.

Every model returned is re-checked on its Cayley tables. Each law of T is evaluated on every assignment when
q^m <= 200,000, and on 20,000 random ones otherwise. The goal is evaluated on an explicit failing assignment read off
the coefficients.

    python -m soup.linear claim --laws "x · (y · x) = y; ..." --goal "x · x = x" [--qmax 64] [--affine-qmax 16]
    python -m soup.linear sweep [--qmax 64] [--affine-qmax 16] [--budget 600] [--write]
        Every claim with status unknown or open in SOUP_DATA/results. Summary in SOUP_DATA/check/linear_sweep.json.
        With --write, a refuted claim's result file is rewritten (status 'refuted', certificate kind 'linear', field
        'linear_sweep'). The score is not recomputed.
"""
import argparse
import glob
import itertools
import json
import math
import time

import numpy as np

from .data import TREES

FULL_CHECK = 200_000
SAMPLES = 20_000


# ---- rings: elements 0..q-1, with 0 and 1 the ring's zero and one

class Ring:
    def __init__(self, name, add, mul):
        self.name = name
        self.add, self.mul = np.asarray(add, np.int16), np.asarray(mul, np.int16)
        self.q = len(self.add)


def zmod(n):
    r = np.arange(n)
    return Ring(f'Z/{n}', (r[:, None] + r[None, :]) % n, (r[:, None] * r[None, :]) % n)


def _pmul(u, v, p):
    """Product of polynomials over GF(p), coefficient lists with the lowest degree first."""
    out = [0] * (len(u) + len(v) - 1)
    for i, x in enumerate(u):
        for j, y in enumerate(v):
            out[i + j] = (out[i + j] + x * y) % p
    return out


def _pmod(u, m, p):
    """Remainder of u modulo the monic polynomial m over GF(p)."""
    u = list(u)
    while len(u) >= len(m):
        c = u[-1]
        if c:
            s = len(u) - len(m)
            for i, x in enumerate(m):
                u[s + i] = (u[s + i] - c * x) % p
        u.pop()
    return u


def _monic(p, d):
    for low in itertools.product(range(p), repeat=d):
        yield list(low) + [1]


def irreducible(p, k):
    """The first monic irreducible polynomial of degree k over GF(p), in lexicographic order, by trial division."""
    for m in _monic(p, k):
        if m[0] == 0: continue
        if all(any(_pmod(m, g, p)) for d in range(1, k // 2 + 1) for g in _monic(p, d)):
            return m
    raise ValueError(f'no irreducible polynomial of degree {k} over GF({p})')


def gf(p, k):
    if k == 1:
        R = zmod(p); R.name = f'GF({p})'; return R
    m, q = irreducible(p, k), p ** k
    E = [[(x // p ** i) % p for i in range(k)] for x in range(q)]
    num = lambda u: sum(c * p ** i for i, c in enumerate((list(u) + [0] * k)[:k]))
    add = [[num([(s + t) % p for s, t in zip(E[x], E[y])]) for y in range(q)] for x in range(q)]
    mul = [[num(_pmod(_pmul(E[x], E[y], p), m, p)) for y in range(q)] for x in range(q)]
    return Ring(f'GF({q})', add, mul)


def _prime(n): return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def rings(qmax):
    """Z/n for every n and GF(q) for every prime power q, 2 <= q <= qmax, ordered by size (Z/p is GF(p))."""
    out = []
    for q in range(2, qmax + 1):
        out.append(gf(q, 1) if _prime(q) else zmod(q))
        for p in range(2, q):
            k = round(math.log(q, p)) if _prime(p) else 0
            if k >= 2 and p ** k == q: out.append(gf(p, k))
    return out


# ---- exact law test from coefficients

def _form(t, P, R):
    """Affine form of the term t: ({variable: coefficient}, constant), coefficients scalars or arrays over P."""
    if t[0] == 'v': return {t[1]: 1}, 0
    (s, ks), (u, ku) = _form(t[1], P, R), _form(t[2], P, R)
    a, b, c = (P['a'], P['b'], P['c']) if t[0] == 'f' else (P['d'], P['e'], P['f'])
    A, M = R.add, R.mul
    co = {v: A[M[a, s.get(v, 0)], M[b, u.get(v, 0)]] for v in set(s) | set(u)}
    return co, A[A[M[a, ks], M[b, ku]], c]


def holds(i, P, R, size):
    """Boolean array over the parameter tuples in P: does law i hold in the model?"""
    L, Rt = TREES[i]
    (cl, kl), (cr, kr) = _form(L, P, R), _form(Rt, P, R)
    ok = np.broadcast_to(np.asarray(kl) == np.asarray(kr), (size,)).copy()
    for v in set(cl) | set(cr):
        ok &= np.asarray(cl.get(v, 0)) == np.asarray(cr.get(v, 0))
    return ok


def search(T, goal, R, affine=False, chunk=1 << 20, deadline=None):
    """First coefficient tuple of the family over R that satisfies every law of T and fails goal; None if there is
    none; 'unknown' if the deadline (a time.time() value) passed first."""
    q, npar = R.q, 6 if affine else 4
    total = q ** npar
    for start in range(0, total, chunk):
        if deadline and time.time() > deadline: return 'unknown'
        idx = np.arange(start, min(start + chunk, total), dtype=np.int64)
        vals = []
        for _ in range(npar):
            vals.append((idx % q).astype(np.int16)); idx = idx // q
        P = dict(zip('abde', vals[:4]))
        P['c'], P['f'] = (vals[4], vals[5]) if affine else (0, 0)
        size = len(vals[0])
        for t in T:                      # keep only the tuples that pass each law before testing the next one
            m = holds(t, P, R, size)
            if not m.all():
                P = {k: (v[m] if np.ndim(v) else v) for k, v in P.items()}; size = int(m.sum())
            if not size: break
        if not size: continue
        m = ~holds(goal, P, R, size)
        if m.any():
            j = int(np.flatnonzero(m)[0])
            return {k: int(v[j]) if np.ndim(v) else int(v) for k, v in P.items()}
    return None


# ---- tables and the independent re-check

def tables(R, p):
    x = np.arange(R.q)
    A, M = R.add, R.mul
    F = A[A[M[p['a'], x][:, None], M[p['b'], x][None, :]], p['c']]
    G = A[A[M[p['d'], x][:, None], M[p['e'], x][None, :]], p['f']]
    return F, G


def _nv(t): return t[1] + 1 if t[0] == 'v' else max(_nv(t[1]), _nv(t[2]))


def law_k(i):
    L, R = TREES[i]; return max(_nv(L), _nv(R))


def _ev(t, env, F, G):
    if t[0] == 'v': return env[t[1]]
    a, b = _ev(t[1], env, F, G), _ev(t[2], env, F, G)
    return (F if t[0] == 'f' else G)[a, b]


def witness(goal, R, p):
    """An assignment (ring elements, one per variable) on which the goal fails, read off the coefficients."""
    P = {k: np.int16(v) for k, v in p.items()}
    L, Rt = TREES[goal]
    (cl, kl), (cr, kr) = _form(L, P, R), _form(Rt, P, R)
    k = law_k(goal)
    if int(np.asarray(kl)) != int(np.asarray(kr)): return [0] * k          # constants first: at 0 only they count
    for v in sorted(set(cl) | set(cr)):                                     # equal constants: v = 1 isolates k_v
        if int(np.asarray(cl.get(v, 0))) != int(np.asarray(cr.get(v, 0))):
            return [1 if i == v else 0 for i in range(k)]
    return None


def recheck(T, goal, R, p, seed=0):
    """Evaluate the tables directly. Raises AssertionError if the coefficient test and the tables disagree."""
    F, G = tables(R, p); q = R.q; rng = np.random.default_rng(seed); mode = 'all'
    for t in T:
        k = law_k(t)
        if q ** k <= FULL_CHECK:
            env = [a.ravel() for a in np.indices((q,) * k)]
        else:
            env = [rng.integers(0, q, SAMPLES) for _ in range(k)]; mode = f'sampled {SAMPLES}'
        L, Rt = TREES[t]
        assert np.array_equal(_ev(L, env, F, G), _ev(Rt, env, F, G)), f'law {t} fails on the tables'
    w = witness(goal, R, p)
    assert w is not None, 'the coefficients do not separate the goal'
    L, Rt = TREES[goal]
    env = [np.array([x]) for x in w]
    assert _ev(L, env, F, G)[0] != _ev(Rt, env, F, G)[0], 'the goal holds at the witness'
    return {'check': mode, 'witness': w, 'F': F.tolist(), 'G': G.tolist()}


def claim(T, goal, qmax=64, affine_qmax=16, budget=None):
    """Search the family ring by ring (by size; linear, then affine where q <= affine_qmax). Returns a record with
    status 'refuted' (model, tables, re-check), 'none' (no model in the family up to the bounds) or 'unknown'."""
    t0 = time.time(); deadline = t0 + budget if budget else None; unknown = False
    for R in rings(qmax):
        for affine in ([False, True] if R.q <= affine_qmax else [False]):
            r = search(T, goal, R, affine, deadline=deadline)
            if r == 'unknown': unknown = True; break
            if r:
                rec = recheck(T, goal, R, r)
                return {'status': 'refuted', 'ring': R.name, 'q': R.q, 'family': 'affine' if affine else 'linear',
                        'params': r, **rec, 'secs': round(time.time() - t0, 1)}
        if unknown: break
    return {'status': 'unknown' if unknown else 'none', 'qmax': qmax, 'affine_qmax': affine_qmax,
            'secs': round(time.time() - t0, 1)}


# ---- the pipeline step

def _job(args):
    path, i, T, idx, qmax, affine_qmax, budget = args
    return path, i, claim(T, idx, qmax, affine_qmax, budget)


def sweep(qmax, affine_qmax, budget, write, jobs=1):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from .paths import data, ensure
    from .stream.common import write_json
    files = {p: json.load(open(p)) for p in sorted(glob.glob(str(data('results', '*.json'))))}
    todo = [(p, i, r['T'], c['idx'], qmax, affine_qmax, budget) for p, r in files.items()
            for i, c in enumerate(r.get('claims', [])) if c.get('status') in ('unknown', 'open')]
    n_open = len(todo); out = []; hits = {}
    print(f'{n_open} open claims in {len({t[0] for t in todo})} results, {jobs} jobs', flush=True)
    with ProcessPoolExecutor(jobs) as ex:
        for fut in as_completed([ex.submit(_job, t) for t in todo]):
            path, i, rec = fut.result(); r = files[path]; c = r['claims'][i]
            row = {'key': r['key'], 'run': r.get('run'), 'law': c['law'], 'idx': c['idx'],
                   **{k: v for k, v in rec.items() if k not in ('F', 'G')}}
            out.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
            if rec['status'] == 'refuted': hits.setdefault(path, []).append((i, rec))
    for path, recs in hits.items() if write else ():
        r = json.load(open(path))            # re-read: write only the claims this sweep refuted
        for i, rec in recs:
            c = r['claims'][i]
            c['status'] = f"false (size {rec['q']}, {rec['family']} model over {rec['ring']})"   # the verify.py convention
            r['n_refuted'] = r.get('n_refuted', 0) + 1
            c['certificate'] = {'kind': 'linear', **{k: rec[k] for k in ('ring', 'q', 'family', 'params', 'check',
                                                                        'witness')}}
            c['linear_sweep'] = time.strftime('%Y-%m-%d %H:%M:%S')
            if c['law'] in r.get('open', []): r['open'].remove(c['law'])
        write_json(path, r)
    out.sort(key=lambda x: (x['key'], x['idx']))
    json.dump(out, open(ensure('check') / 'linear_sweep.json', 'w'), ensure_ascii=False, indent=1)
    ref = sum(1 for x in out if x['status'] == 'refuted')
    print(f'{n_open} open claims, {ref} refuted by a linear or affine model', flush=True)


def main():
    from .named import law_index
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['claim', 'sweep'])
    ap.add_argument('--laws'); ap.add_argument('--goal')
    ap.add_argument('--qmax', type=int, default=64); ap.add_argument('--affine-qmax', type=int, default=16)
    ap.add_argument('--budget', type=float, default=600); ap.add_argument('--write', action='store_true')
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    if a.cmd == 'sweep':
        sweep(a.qmax, a.affine_qmax, a.budget, a.write, a.jobs); return
    T = [law_index(s.strip().replace(' ', '')) for s in a.laws.split(';')]
    goal = law_index(a.goal.replace(' ', ''))
    if None in T or goal is None: raise SystemExit('a law is not in the enumeration (order <= 4)')
    rec = claim(T, goal, a.qmax, a.affine_qmax, a.budget)
    print(json.dumps({k: v for k, v in rec.items() if k not in ('F', 'G')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
