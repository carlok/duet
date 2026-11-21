"""v2: growing corpus, deterministic proof difficulty (z3 rlimit), countermodel and model search."""
import sys, time, pickle
sys.path.insert(0, '/home/claude/soup')
import numpy as np, z3
from soup import (LAWS, ORDER, PROBES, PM, LM, NL, NP, SIZES, TREES, NONDEG, unpack_probes, unpack_laws, nvars_tree)
from matrix import evaluate, postfix
from probes import NMAX

# ---- compiled law programs, for evaluating new structures against all laws
_prog, _lo, _mid, _hi, _nv = [], [], [], [], []
for L, R in TREES:
    _lo.append(len(_prog)); postfix(L, _prog); _mid.append(len(_prog)); postfix(R, _prog); _hi.append(len(_prog))
    _nv.append(max(nvars_tree(L), nvars_tree(R)))
_prog = np.array(_prog, np.int64); _lo, _mid, _hi, _nv = map(lambda a: np.array(a, np.int64), (_lo, _mid, _hi, _nv))

def law_vector(F, G, n):
    Fs = np.zeros((1, NMAX, NMAX), np.int64); Gs = np.zeros_like(Fs)
    Fs[0, :n, :n] = F; Gs[0, :n, :n] = G
    return evaluate(_prog, _lo, _mid, _hi, _nv, Fs, Gs, np.array([n], np.int64))[0].astype(bool)

def essbin(T, n):
    return any(T[x1, y] != T[x2, y] for y in range(n) for x1 in range(n) for x2 in range(n)) and \
           any(T[x, y1] != T[x, y2] for x in range(n) for y1 in range(n) for y2 in range(n))

class Corpus:
    """Base corpus (packed matrices) plus structures found during the search."""
    def __init__(self):
        self.extra = []          # (name, n, F, G, lawvec, nondeg)
        self.keys = set()
    def add(self, name, n, F, G):
        k = (n, F.tobytes(), G.tobytes())
        if k in self.keys: return False
        self.keys.add(k)
        self.extra.append((name, n, F, G, law_vector(F, G, n), essbin(F, n) and essbin(G, n) and not np.array_equal(F, G)))
        return True
    def sat(self, T):
        T = list(T)
        base = unpack_probes(np.bitwise_and.reduce(LM[T], axis=0))
        ext = np.array([e[4][T].all() for e in self.extra], bool)
        return base, ext
    def stats(self, T):
        base, ext = self.sat(T)
        nd = (base & NONDEG).any() or any(e[5] for e, s in zip(self.extra, ext) if s)
        sizes = set(SIZES[base]) | {e[1] for e, s in zip(self.extra, ext) if s}
        return int(base.sum() + ext.sum()), nd, sizes
    def implied(self, T):
        base, ext = self.sat(T)
        rows = PM[base]
        acc = np.bitwise_and.reduce(rows, axis=0) if rows.shape[0] else None
        acc = unpack_laws(acc) if acc is not None else None
        for e, s in zip(self.extra, ext):
            if s: acc = e[4].copy() if acc is None else acc & e[4]
        return acc
    def emergent(self, T):
        T = sorted(set(T)); imp = self.implied(T)
        if imp is None: return None
        union = np.zeros(NL, bool)
        for i in range(len(T)):
            si = self.implied([t for j, t in enumerate(T) if j != i])
            if si is not None: union |= si
        return np.flatnonzero(imp & ~union)

# ---- z3 helpers: deterministic budgets via rlimit
_S = z3.DeclareSort('S'); _f = z3.Function('f', _S, _S, _S); _g = z3.Function('g', _S, _S, _S)
def _zt(t, env, f=_f, g=_g): return env[t[1]] if t[0] == 'v' else (f if t[0] == 'f' else g)(_zt(t[1], env, f, g), _zt(t[2], env, f, g))
def _axiom(i, S, f, g):
    L, R = TREES[i]; k = max(nvars_tree(L), nvars_tree(R)); vs = [z3.Const(f'v{j}', S) for j in range(k)]
    body = _zt(L, vs, f, g) == _zt(R, vs, f, g)
    return z3.ForAll(vs, body) if vs else body
def prove(T, goal, rlimit=20_000_000):
    """Returns (status, effort). Each call gets a fresh z3 context, so effort counts this proof only."""
    ctx = z3.Context()
    S = z3.DeclareSort('S', ctx); f = z3.Function('f', S, S, S); g = z3.Function('g', S, S, S)
    s = z3.Solver(ctx=ctx); s.set('rlimit', rlimit)
    for t in T: s.add(_axiom(t, S, f, g))
    L, R = TREES[goal]; k = max(nvars_tree(L), nvars_tree(R)); cs = [z3.Const(f'c{j}', S) for j in range(k)]
    s.add(_zt(L, cs, f, g) != _zt(R, cs, f, g))
    r = s.check(); st = s.statistics()
    used = st.get_key_value('rlimit count') if 'rlimit count' in st.keys() else rlimit
    return ('proved' if r == z3.unsat else 'unknown'), int(used)

_SORTS = {}
def _sort(n):
    if n not in _SORTS: _SORTS[n] = z3.EnumSort(f'Dom{n}', [f'd{n}_{i}' for i in range(n)])
    return _SORTS[n]
import itertools as _it
def find_model(T, n, goal=None, nondeg=False, rlimit=30_000_000, avoid=()):
    """Finite model of T on n elements, axioms grounded over all tuples (Mace4-style, no quantifiers).
    Optionally violating goal, optionally non-degenerate; avoid = tables to exclude. Returns (F,G), None or 'unknown'."""
    S, el = _sort(n); f = z3.Function(f'f{n}', S, S, S); g = z3.Function(f'g{n}', S, S, S)
    s = z3.Solver(); s.set('rlimit', rlimit)
    for t in T:
        L, R = TREES[t]; k = max(nvars_tree(L), nvars_tree(R))
        for tup in _it.product(el, repeat=k):
            s.add(_zt(L, list(tup), f, g) == _zt(R, list(tup), f, g))
    if goal is not None:
        L, R = TREES[goal]; k = max(nvars_tree(L), nvars_tree(R))
        s.add(z3.Or([_zt(L, list(tup), f, g) != _zt(R, list(tup), f, g) for tup in _it.product(el, repeat=k)]))
    if nondeg:
        for op in (f, g):
            s.add(z3.Or([op(a, c) != op(b, c) for a in el for b in el for c in el if a is not b]))
            s.add(z3.Or([op(a, b) != op(a, c) for a in el for b in el for c in el if b is not c]))
        s.add(z3.Or([f(a, b) != g(a, b) for a in el for b in el]))
    for F0, G0 in avoid:
        s.add(z3.Or([f(el[x], el[y]) != el[int(F0[x, y])] for x in range(n) for y in range(n)] +
                    [g(el[x], el[y]) != el[int(G0[x, y])] for x in range(n) for y in range(n)]))
    r = s.check()
    if r == z3.unknown: return 'unknown'
    if r == z3.unsat: return None
    m = s.model(); pos = {str(e): i for i, e in enumerate(el)}
    F = np.array([[pos[str(m.eval(f(x, y)))] for y in el] for x in el]); G = np.array([[pos[str(m.eval(g(x, y)))] for y in el] for x in el])
    return F, G
