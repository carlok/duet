"""Growing corpus, z3 proof effort, finite model search.

Corpus: the base matrix (12,509 structures, memory-mapped) plus structures found during the search.
With a `store` directory the found structures are shared between processes through an append-only
directory of files `<n>_<hash>.npz`; each process calls `refresh()` to pick up what others found.
"""
import hashlib
import itertools
import os
import weakref
from collections import OrderedDict
from pathlib import Path

import numpy as np
import z3

from .data import LAWS, ORDER, PROBES, PM, LM, NL, NP, SIZES, TREES, NONDEG, unpack_laws, unpack_probes, nvars_tree, sat_base
from .matrix import evaluate_one, postfix
from .probes import NMAX

# ---- compiled law programs, for evaluating new structures against all laws
_prog, _lo, _mid, _hi, _nv = [], [], [], [], []
for _L, _R in TREES:
    _lo.append(len(_prog)); postfix(_L, _prog); _mid.append(len(_prog)); postfix(_R, _prog); _hi.append(len(_prog))
    _nv.append(max(nvars_tree(_L), nvars_tree(_R)))
_prog = np.array(_prog, np.int64)
_lo, _mid, _hi, _nv = (np.array(a, np.int64) for a in (_lo, _mid, _hi, _nv))
NLB = (NL + 7) // 8          # bytes per packed law vector


def law_vector(F, G, n):
    """Which of the NL laws hold in the structure (F, G) on n elements (bool vector)."""
    F = np.ascontiguousarray(F, np.int64); G = np.ascontiguousarray(G, np.int64)
    return evaluate_one(_prog, _lo, _mid, _hi, _nv, F, G, int(n)).astype(bool)


def essbin(T, n):
    return any(T[x1, y] != T[x2, y] for y in range(n) for x1 in range(n) for x2 in range(n)) and \
           any(T[x, y1] != T[x, y2] for x in range(n) for y1 in range(n) for y2 in range(n))


def is_nondeg(F, G, n):
    return essbin(F, n) and essbin(G, n) and not np.array_equal(F, G)


def structure_key(n, F, G):
    h = hashlib.sha1(bytes([n]) + np.asarray(F, np.int8).tobytes() + np.asarray(G, np.int8).tobytes())
    return f'{n}_{h.hexdigest()[:16]}'


def _bits_have(P, t):
    """Rows of a packed (structures x laws) matrix whose bit t is set."""
    return (P[:, t >> 3] & (128 >> (t & 7))) != 0


class Corpus:
    """Base corpus (packed matrices) plus structures found during the search."""

    def __init__(self, store=None):
        self.store = Path(store) if store else None
        self.tables = []                      # (name, n, F, G)
        self.nd = np.zeros(0, bool)
        self.sz = np.zeros(0, np.int64)
        self.XP = np.zeros((0, NLB), np.uint8)  # packed law vectors of found structures
        self.keys = set()
        self._seen_files = set()
        self._cols = OrderedDict()            # law -> (rows covered, packed bits of column law of XP); see has()
        if self.store is not None:
            self.store.mkdir(parents=True, exist_ok=True)
            self.refresh()

    # compatibility with the first-session code: list of (name, n, F, G, ...)
    @property
    def extra(self): return self.tables

    def __len__(self): return len(self.tables)

    def _append(self, name, n, F, G, packed, nd):
        k = len(self.tables)
        if k == getattr(self, '_cap', 0):      # grow the buffers by doubling: appends stay O(1) amortised
            cap = max(64, 2 * k)
            buf = np.zeros((cap, NLB), np.uint8); buf[:k] = self.XP; self._buf = buf
            nd_, sz_ = np.zeros(cap, bool), np.zeros(cap, np.int64); nd_[:k] = self.nd; sz_[:k] = self.sz
            self._nd, self._sz, self._cap = nd_, sz_, cap
        self._buf[k] = packed; self._nd[k] = nd; self._sz[k] = n
        self.tables.append((name, n, F, G))
        self.XP, self.nd, self.sz = self._buf[:k + 1], self._nd[:k + 1], self._sz[:k + 1]

    def add(self, name, n, F, G):
        """Add a structure (deduplicated on its exact tables). Written to the store at once."""
        F = np.asarray(F, np.int64); G = np.asarray(G, np.int64)
        k = structure_key(n, F, G)
        if k in self.keys: return False
        self.keys.add(k)
        packed = np.packbits(law_vector(F, G, n))
        nd = is_nondeg(F, G, n)
        self._append(name, n, F, G, packed, nd)
        if self.store is not None:
            path = self.store / f'{k}.npz'
            self._seen_files.add(path.name)
            if not path.exists():
                tmp = self.store / f'.tmp-{k}-{os.getpid()}.npz'
                with open(tmp, 'wb') as fh:
                    np.savez(fh, n=np.int64(n), F=F.astype(np.int8), G=G.astype(np.int8), lawvec=packed,
                             nondeg=np.bool_(nd), name=np.str_(name))
                os.replace(tmp, path)
        return True

    def refresh(self):
        """Load structures other processes wrote since the last call. Returns how many were new."""
        if self.store is None: return 0
        new = 0
        for entry in sorted(os.listdir(self.store)):
            if entry.startswith('.') or not entry.endswith('.npz') or entry in self._seen_files: continue
            self._seen_files.add(entry)
            k = entry[:-4]
            if k in self.keys: continue
            try:
                z = np.load(self.store / entry)
                n = int(z['n']); F = z['F'].astype(np.int64); G = z['G'].astype(np.int64)
                packed = z['lawvec']; nd = bool(z['nondeg']); name = str(z['name'])
            except Exception:          # half-written by a crashed process: skip, retry never
                continue
            self.keys.add(k); self._append(name, n, F, G, packed, nd); new += 1
        return new

    COL_CACHE = 8192

    def has(self, t):
        """Packed bits (one per found structure) of the structures that satisfy law t: column t of XP.

        Cached by law, least recently used out first (COL_CACHE laws). Reading a column of XP touches one cache
        line per structure, since rows are 8.9 KB apart, and the searcher asks for the same few columns over and
        over: T's laws in stats, implied and offdiag_gain, an elite's laws in all its mutations, and the diagonal
        laws. On X9's corpus that read was 70% of the surrogate's time (25 Nov 2026, notes/profile_searcher.py).
        Rows never change once appended, so a cached column only has to be extended by the rows added since.
        Not thread-safe: the thread pools in dedupe, rediscover and taxonomy run E only, never the corpus."""
        t = int(t); n = len(self.tables)
        c = self._cols.get(t)
        if c is None:
            col = np.packbits(_bits_have(self.XP, t))
        elif c[0] == n:
            self._cols.move_to_end(t); return c[1]
        else:
            m, old = c
            col = np.packbits(np.concatenate([np.unpackbits(old, count=m).astype(bool), _bits_have(self.XP[m:], t)]))
        self._cols[t] = (n, col); self._cols.move_to_end(t)
        if len(self._cols) > self.COL_CACHE: self._cols.popitem(last=False)
        return col

    def sat(self, T):
        T = list(T)
        base = unpack_probes(sat_base(T))
        n = len(self.tables)
        if not T: return base, np.ones(n, bool)
        acc = self.has(T[0]).copy()
        for t in T[1:]: acc &= self.has(t)
        return base, np.unpackbits(acc, count=n).astype(bool)

    def stats(self, T):
        base, ext = self.sat(T)
        nd = bool((base & NONDEG).any() or (self.nd & ext).any())
        sizes = set(SIZES[base].tolist()) | set(self.sz[ext].tolist())
        return int(base.sum() + ext.sum()), nd, sizes

    def implied(self, T):
        """Laws true in every corpus structure satisfying T (bool vector), None if there is none."""
        base, ext = self.sat(T)
        rows = [PM[base], self.XP[ext]]
        rows = [r for r in rows if r.shape[0]]
        if not rows: return None
        acc = np.bitwise_and.reduce(rows[0], axis=0)
        if len(rows) > 1: acc &= np.bitwise_and.reduce(rows[1], axis=0)
        return unpack_laws(acc)

    def emergent(self, T):
        T = sorted(set(T)); imp = self.implied(T)
        if imp is None: return None
        union = np.zeros(NL, bool)
        for i in range(len(T)):
            si = self.implied([t for j, t in enumerate(T) if j != i])
            if si is not None: union |= si
        return np.flatnonzero(imp & ~union)


# ---- z3 bookkeeping: every context is registered so a stop request can interrupt a running check
_LIVE = weakref.WeakSet()
# Grounding size cap: more ground equations than this and the size is reported 'unknown' (not searched).
MAX_GROUND = int(os.environ.get('SOUP_MAX_GROUND', 60_000))


def new_context():
    ctx = z3.Context(); _LIVE.add(ctx); return ctx


def interrupt_all():
    """Called from a watcher thread on SIGTERM: running z3 checks return 'unknown' at once."""
    for ctx in list(_LIVE):
        try: ctx.interrupt()
        except Exception: pass


def set_memory_limit(mb):
    """Process-wide z3 memory cap; a check that exceeds it fails instead of growing without bound."""
    z3.set_param('memory_max_size', int(mb))


# ---- z3 proof effort: fresh context per proof, so rlimit count is this proof only
def _zt(t, env, f, g): return env[t[1]] if t[0] == 'v' else (f if t[0] == 'f' else g)(_zt(t[1], env, f, g), _zt(t[2], env, f, g))


def _axiom(i, S, f, g):
    L, R = TREES[i]; k = max(nvars_tree(L), nvars_tree(R)); vs = [z3.Const(f'v{j}', S) for j in range(k)]
    body = _zt(L, vs, f, g) == _zt(R, vs, f, g)
    return z3.ForAll(vs, body) if vs else body


def prove(T, goal, rlimit=20_000_000, secs=None):
    """Returns (status, effort). Each call gets a fresh z3 context, so effort counts this proof only.
    secs: a wall-time cap (z3's own timeout), off by default. z3 can run for hours without reaching its rlimit: two
    stage-a redundancy proofs in X12 ran 5.2 and 7.3 h at rlimit 10M (PREREGISTRATION.md, deviation 13)."""
    ctx = new_context()
    S = z3.DeclareSort('S', ctx); f = z3.Function('f', S, S, S); g = z3.Function('g', S, S, S)
    s = z3.Solver(ctx=ctx); s.set('rlimit', rlimit)
    if secs: s.set('timeout', int(secs * 1000))
    for t in T: s.add(_axiom(t, S, f, g))
    L, R = TREES[goal]; k = max(nvars_tree(L), nvars_tree(R)); cs = [z3.Const(f'c{j}', S) for j in range(k)]
    s.add(_zt(L, cs, f, g) != _zt(R, cs, f, g))
    try:
        r = s.check(); st = s.statistics()
    except z3.Z3Exception:            # memory cap hit
        return 'unknown', int(rlimit)
    used = st.get_key_value('rlimit count') if 'rlimit count' in st.keys() else rlimit
    return ('proved' if r == z3.unsat else 'unknown'), int(used)


def _nvars(i):
    L, R = TREES[i]; return max(nvars_tree(L), nvars_tree(R))


# ---- finite models: axioms grounded over all tuples (Mace4-style, no quantifiers)
class Grounding:
    """Theory T grounded over an n-element domain in its own z3 context. The ground equations are
    built once and reused by every query (model census, countermodels to different goals)."""

    def __init__(self, T, n):
        self.n = n; self.T = list(T)
        self.too_big = sum(n ** _nvars(t) for t in self.T) > MAX_GROUND
        self.ctx = new_context()
        self.S, self.el = z3.EnumSort(f'D{n}', [f'd{i}' for i in range(n)], ctx=self.ctx)
        self.f = z3.Function('f', self.S, self.S, self.S); self.g = z3.Function('g', self.S, self.S, self.S)
        self.pos = {str(e): i for i, e in enumerate(self.el)}
        self.ax = []
        if not self.too_big:
            for t in self.T: self.ax += self.ground(t)

    def ground(self, i):
        L, R = TREES[i]; k = max(nvars_tree(L), nvars_tree(R)); f, g = self.f, self.g
        return [_zt(L, list(tup), f, g) == _zt(R, list(tup), f, g) for tup in itertools.product(self.el, repeat=k)]

    def find(self, goal=None, nondeg=False, rlimit=30_000_000, avoid=()):
        """A model of T, optionally violating law `goal`, optionally non-degenerate, different from
        every table pair in `avoid`. Returns (F, G), None (no such model) or 'unknown' (budget)."""
        el, f, g, n = self.el, self.f, self.g, self.n
        if self.too_big or (goal is not None and n ** _nvars(goal) > MAX_GROUND): return 'unknown'
        s = z3.Solver(ctx=self.ctx); s.set('rlimit', rlimit)
        s.add(self.ax)
        if goal is not None:
            s.add(z3.Or([z3.Not(e) for e in self.ground(goal)]))
        if nondeg:
            for op in (f, g):
                s.add(z3.Or([op(a, c) != op(b, c) for a in el for b in el for c in el if a is not b]))
                s.add(z3.Or([op(a, b) != op(a, c) for a in el for b in el for c in el if b is not c]))
            s.add(z3.Or([f(a, b) != g(a, b) for a in el for b in el]))
        for F0, G0 in avoid:
            s.add(z3.Or([f(el[x], el[y]) != el[int(F0[x, y])] for x in range(n) for y in range(n)] +
                        [g(el[x], el[y]) != el[int(G0[x, y])] for x in range(n) for y in range(n)]))
        try: r = s.check()
        except z3.Z3Exception: return 'unknown'      # memory cap hit
        if r == z3.unknown: return 'unknown'
        if r == z3.unsat: return None
        m = s.model(); pos = self.pos
        F = np.array([[pos[str(m.eval(f(x, y)))] for y in el] for x in el])
        G = np.array([[pos[str(m.eval(g(x, y)))] for y in el] for x in el])
        return F, G


def find_model(T, n, goal=None, nondeg=False, rlimit=30_000_000, avoid=()):
    return Grounding(T, n).find(goal=goal, nondeg=nondeg, rlimit=rlimit, avoid=avoid)
