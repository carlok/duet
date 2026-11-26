"""Search-side skip of parameter disguises (arm 'fusion5', after X10, 26 Nov 2026).

V6's screen (soup.hidden.hidden_param) marks a theory definitional when E proves that one operation is a term in the
other plus constant squares: x∘y = t(x, y, z·z, z∘z) for all z (or the same for x·y). It runs in the verifier, after
the search has spent archive cells and queue slots on the theory. In X10, 294 of the 578 verified theories were such
disguises, all of one shape (REPORT, "X10").

Across X6-X10 the screen proved 1,300 matches with 34 distinct terms, and in every one x and y occur exactly once.
TERMS are all such *linear parameter terms*: binary terms in one operation with 2 to 4 operations, whose leaves are x
once, y once and at least one of the squares z·z, z∘z (size as in hidden.param_terms, the squares counted as leaves).
There are 2,504 per direction: terms in · for ∘, and terms in ∘ for ·.

ParamSkip.check(T) has two steps.
1. Corpus: on every corpus structure satisfying T, one operation equals one of these terms in the other, for all x, y
   and z. A numba kernel stops at a term's first mismatch, so most of the 5,008 terms cost a few operations.
2. Confirmation, only when step 1 fires: Mace4 looks for a model of T on 2 to 5 elements in which the first matching
   term fails (2 s). A model found goes into the corpus (shared with every process, as the verifiers' models do), and
   step 1 runs again, at most 3 times. T is skipped only if a term still matches.
Step 1 alone over-approximates: a run's corpus lacks the models other runs found. On x10's corpus it would skip nine of
X4's candidates at funnel level 7, whose term V6's census refutes on 2 to 4 elements (notes/paramskip_check.out). A
skipped theory may still not imply the definition, when every countermodel has more than 5 elements. V6's screen in the
verifier stays as it was.
"""
import itertools
import subprocess

import numba as nb
import numpy as np

X, Y, CF, CG, OP = 0, 1, 2, 3, 4          # program codes: leaves x, y, z·z, z∘z; OP applies the term's operation


def _shapes(s):
    """Binary trees with s internal nodes, as postfix lists of 'L' (leaf) and 'O' (node)."""
    if s == 0: return [['L']]
    return [a + b + ['O'] for i in range(s) for a in _shapes(i) for b in _shapes(s - 1 - i)]


def _terms():
    progs = []
    for s in range(2, 5):
        for shape in _shapes(s):
            nl = s + 1
            for px, py in itertools.permutations(range(nl), 2):
                rest = [i for i in range(nl) if i not in (px, py)]
                for consts in itertools.product((CF, CG), repeat=len(rest)):
                    leaf = {px: X, py: Y, **dict(zip(rest, consts))}
                    k, prog = 0, []
                    for c in shape:
                        if c == 'L': prog.append(leaf[k]); k += 1
                        else: prog.append(OP)
                    progs.append(prog)
    return progs


def program_str(prog, op):
    st = []
    for c in prog:
        if c == OP: b, a = st.pop(), st.pop(); st.append(f'({a} {op} {b})')
        else: st.append(['x', 'y', 'z·z', 'z∘z'][c])
    return st[0]


_P = _terms()
L = max(len(p) for p in _P)
PROGS = np.full((2 * len(_P), L), -1, np.int8)
PLEN = np.zeros(2 * len(_P), np.int64)
DIRECTION = np.zeros(2 * len(_P), np.int8)      # 0: ∘ = a term in ·;  1: · = a term in ∘
for d in (0, 1):
    for i, p in enumerate(_P):
        PROGS[d * len(_P) + i, :len(p)] = p; PLEN[d * len(_P) + i] = len(p); DIRECTION[d * len(_P) + i] = d
NTERMS = len(PROGS)


def term_str(i):
    return ('x ∘ y = ' if DIRECTION[i] == 0 else 'x · y = ') + program_str(list(PROGS[i, :PLEN[i]]),
                                                                         '·' if DIRECTION[i] == 0 else '∘')


def term_tree(i):
    """Term i as a law (lhs, rhs) in the trees of soup.data: variables x, y, z = ('v', 0), ('v', 1), ('v', 2)."""
    d = DIRECTION[i]; op = 'f' if d == 0 else 'g'
    z = ('v', 2)
    leaves = {X: ('v', 0), Y: ('v', 1), CF: ('f', z, z), CG: ('g', z, z)}
    st = []
    for c in PROGS[i, :PLEN[i]]:
        if c == OP: b, a = st.pop(), st.pop(); st.append((op, a, b))
        else: st.append(leaves[int(c)])
    return ('g' if d == 0 else 'f', ('v', 0), ('v', 1)), st[0]


def countermodel(T, i, max_n=5, secs=2):
    """A model (n, F, G) of the laws T in which term i fails, from Mace4 on 2..max_n elements, or None."""
    from .profile import _parse_models
    from .provers import PROVER_MB, ladr_input
    try:
        r = subprocess.run(['mace4', '-n', '2', '-N', str(max_n), '-m', '1', '-t', str(int(secs)), '-b', str(PROVER_MB)],
                           input=ladr_input(T, goal_tree=term_tree(i)), capture_output=True, text=True,
                           timeout=secs + 10)
    except subprocess.TimeoutExpired:
        return None
    ms = _parse_models(r.stdout)
    return ms[0] if ms else None


@nb.njit(cache=True)
def _match(progs, plen, direction, TF, TG, off, ns, models):
    """For each term: does it hold on every listed structure? Stops at the first mismatch."""
    out = np.zeros(progs.shape[0], np.bool_)
    stack = np.empty(16, np.int64)
    for t in range(progs.shape[0]):
        ok = True
        d = direction[t]
        for mi in range(models.shape[0]):
            k = models[mi]; n = ns[k]; o = off[k]
            for z in range(n):
                cf = TF[o + z * n + z]; cg = TG[o + z * n + z]
                for x in range(n):
                    for y in range(n):
                        sp = 0
                        for i in range(plen[t]):
                            c = progs[t, i]
                            if c == 0: stack[sp] = x
                            elif c == 1: stack[sp] = y
                            elif c == 2: stack[sp] = cf
                            elif c == 3: stack[sp] = cg
                            else:
                                b = stack[sp - 1]; a = stack[sp - 2]; sp -= 2
                                stack[sp] = TF[o + a * n + b] if d == 0 else TG[o + a * n + b]
                            sp += 1
                        tgt = TG[o + x * n + y] if d == 0 else TF[o + x * n + y]
                        if stack[0] != tgt:
                            ok = False; break
                    if not ok: break
                if not ok: break
            if not ok: break
        out[t] = ok
    return out


class ParamSkip:
    """The tables of the base probes and of a Corpus's found structures, flat, for _match."""

    def __init__(self, C, confirm=True, max_n=5, secs=2, rounds=3, cache=50_000):
        from .data import NP
        from .probes import build
        self.C = C
        self.confirm, self.max_n, self.secs, self.rounds, self.cache_max = confirm, max_n, secs, rounds, cache
        self.cache = {}
        self.fired = self.mace_calls = self.added = self.skipped = 0
        self.mace_secs = 0.0
        base = build()
        assert len(base) == NP, (len(base), NP)
        self.nb = len(base)
        self.TF = np.zeros(0, np.int64); self.TG = np.zeros(0, np.int64)
        self.off = np.zeros(0, np.int64); self.ns = np.zeros(0, np.int64)
        self._add([(n, F, G) for _, n, F, G in base])
        self.synced = 0
        self.sync()

    def _add(self, items):
        if not items: return
        start = len(self.TF)
        offs, k = [], start
        for n, F, G in items: offs.append(k); k += n * n
        self.TF = np.concatenate([self.TF] + [np.asarray(F, np.int64).ravel() for _, F, _ in items])
        self.TG = np.concatenate([self.TG] + [np.asarray(G, np.int64).ravel() for _, _, G in items])
        self.off = np.concatenate([self.off, np.array(offs, np.int64)])
        self.ns = np.concatenate([self.ns, np.array([n for n, _, _ in items], np.int64)])

    def sync(self):
        """Take in the found structures the Corpus gained since the last call."""
        new = self.C.tables[self.synced:]
        self._add([(n, F, G) for _, n, F, G in new]); self.synced += len(new)

    def models(self, T):
        if self.synced < len(self.C.tables): self.sync()
        base, ext = self.C.sat(T)
        idx = np.concatenate([np.flatnonzero(base), self.nb + np.flatnonzero(ext)]).astype(np.int64)
        return idx[np.argsort(-self.ns[idx], kind='stable')]   # large structures first: a wrong term fails early

    def matches(self, T):
        """Indices of the terms that hold on every corpus model of T (empty without models)."""
        idx = self.models(T)
        if not len(idx): return np.zeros(0, np.int64)
        return np.flatnonzero(_match(PROGS, PLEN, DIRECTION, self.TF, self.TG, self.off, self.ns, idx))

    def check(self, T, name='paramskip'):
        """Skip T? Step 1 on the corpus, then the Mace4 confirmation (module docstring). Cached per law set."""
        import time
        key = tuple(sorted(set(int(t) for t in T)))
        if key in self.cache: return self.cache[key]
        m = self.matches(key)
        if len(m): self.fired += 1
        k = 0
        while len(m) and self.confirm and k < self.rounds:
            t0 = time.time()
            cm = countermodel(list(key), int(m[0]), self.max_n, self.secs)
            self.mace_calls += 1; self.mace_secs += time.time() - t0
            if cm is None: break
            if self.C.add(name, *cm): self.added += 1
            m = self.matches(key); k += 1
        out = bool(len(m))
        self.skipped += out
        if len(self.cache) >= self.cache_max: self.cache.clear()
        self.cache[key] = out
        return out
